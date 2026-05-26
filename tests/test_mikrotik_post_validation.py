import json
import json

import mikrotik_post_validation as day3


RESOURCE_OUTPUT = """
version: 7.22.3 (stable)
board-name: hEX S
"""

PACKAGE_OUTPUT = """
Columns: NAME, VERSION
0 routeros 7.22.3
"""

ROUTERBOARD_OUTPUT = """
current-firmware: 7.22.3
upgrade-firmware: 7.22.3
factory-firmware: 7.20.7
"""

DHCP_CLIENT_BOUND_OUTPUT = """
0 interface=ether1 status=bound address=10.0.0.10 dhcp-server=10.0.0.1
"""

IP_ADDRESS_OUTPUT = """
0 address=10.0.0.10/24 interface=ether1
1 address=192.168.88.1/24 interface=bridge
"""

ROUTE_OUTPUT = """
0 dst-address=0.0.0.0/0 gateway=10.0.0.1
"""

PING_OK_OUTPUT = """
sent=3 received=3 packet-loss=0%
"""

SERVICE_OUTPUT = """
Flags: X - disabled
0 X ftp 21
1   ssh 22
2 X telnet 23
3 X www 80
"""


def test_sanitize_path_name():
    assert day3.sanitize_path_name("Hex S 2025/lab02") == "Hex-S-2025-lab02"


def test_parse_ping_output():
    assert day3.parse_ping_output("sent=3 received=1 packet-loss=66%") is True
    assert day3.parse_ping_output("sent=3 received=0 packet-loss=100%") is False


def test_parse_wan_dhcp_client():
    parsed = day3.parse_wan_dhcp_client(DHCP_CLIENT_BOUND_OUTPUT)

    assert parsed["interface"] == "ether1"
    assert parsed["status"] == "bound"
    assert parsed["address"] == "10.0.0.10"


def test_parse_ip_addresses():
    addresses = day3.parse_ip_addresses(IP_ADDRESS_OUTPUT)

    assert {"address": "10.0.0.10/24", "interface": "ether1"} in addresses
    assert {"address": "192.168.88.1/24", "interface": "bridge"} in addresses


def test_parse_disabled_services():
    assert day3.parse_disabled_services(SERVICE_OUTPUT) == {
        "ftp": True,
        "telnet": True,
    }
    assert day3.parse_disabled_services(SERVICE_OUTPUT, ["www"]) == {"www": True}


def test_evaluate_results_all_core_checks_pass():
    outputs = {
        "resource": RESOURCE_OUTPUT,
        "package": PACKAGE_OUTPUT,
        "routerboard": ROUTERBOARD_OUTPUT,
        "dhcp_client": DHCP_CLIENT_BOUND_OUTPUT,
        "ip_address": IP_ADDRESS_OUTPUT,
        "route": ROUTE_OUTPUT,
        "ping_ip": PING_OK_OUTPUT,
        "ping_dns": PING_OK_OUTPUT,
        "service": SERVICE_OUTPUT,
    }

    results, metadata = day3.evaluate_results(outputs, "7.22.3")
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses["RouterOS version"] == "PASS"
    assert statuses["WAN DHCP client"] == "PASS"
    assert statuses["WAN IP address"] == "PASS"
    assert statuses["Default route"] == "PASS"
    assert statuses["Internet ping"] == "PASS"
    assert statuses["DNS ping"] == "PASS"
    assert statuses["LAN bridge IP"] == "PASS"
    assert statuses["Service hardening"] == "PASS"
    assert metadata["wan_ip"] == "10.0.0.10"
    assert metadata["lan_ip"] == "192.168.88.1/24"


def test_evaluate_results_ignores_open_www_when_ftp_telnet_disabled():
    outputs = {
        "resource": RESOURCE_OUTPUT,
        "package": "0 routeros 7.20.7",
        "routerboard": ROUTERBOARD_OUTPUT,
        "dhcp_client": DHCP_CLIENT_BOUND_OUTPUT,
        "ip_address": IP_ADDRESS_OUTPUT,
        "route": ROUTE_OUTPUT,
        "ping_ip": PING_OK_OUTPUT,
        "ping_dns": PING_OK_OUTPUT,
        "service": "0 X ftp 21\n1 X telnet 23\n2 www 80\n",
    }

    results, _metadata = day3.evaluate_results(outputs, "7.22.3")
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses["RouterOS version"] == "WARNING"
    assert statuses["Service hardening"] == "PASS"


def test_evaluate_results_warns_for_open_required_service():
    outputs = {
        "resource": RESOURCE_OUTPUT,
        "package": "0 routeros 7.22.3",
        "routerboard": ROUTERBOARD_OUTPUT,
        "dhcp_client": DHCP_CLIENT_BOUND_OUTPUT,
        "ip_address": IP_ADDRESS_OUTPUT,
        "route": ROUTE_OUTPUT,
        "ping_ip": PING_OK_OUTPUT,
        "ping_dns": PING_OK_OUTPUT,
        "service": "0 ftp 21\n1 X telnet 23\n2 www 80\n",
    }

    results, _metadata = day3.evaluate_results(outputs, "7.22.3")
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses["Service hardening"] == "WARNING"


def test_lab02_post_validation_uses_expected_lan_ip():
    outputs = {
        "resource": RESOURCE_OUTPUT,
        "package": PACKAGE_OUTPUT,
        "routerboard": ROUTERBOARD_OUTPUT,
        "dhcp_client": DHCP_CLIENT_BOUND_OUTPUT,
        "ip_address": (
            "0 address=10.0.0.10/24 interface=ether1\n"
            "1 address=192.168.89.1/24 interface=bridge\n"
        ),
        "route": ROUTE_OUTPUT,
        "ping_ip": PING_OK_OUTPUT,
        "ping_dns": PING_OK_OUTPUT,
        "service": SERVICE_OUTPUT,
    }

    results, metadata = day3.evaluate_results(
        outputs,
        "7.22.3",
        expected_lan_ip_cidr="192.168.89.1/24",
    )
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses["LAN bridge IP"] == "PASS"
    assert metadata["lan_ip"] == "192.168.89.1/24"


def test_lab02_post_validation_fails_lab01_lan_ip():
    outputs = {
        "resource": RESOURCE_OUTPUT,
        "package": PACKAGE_OUTPUT,
        "routerboard": ROUTERBOARD_OUTPUT,
        "dhcp_client": DHCP_CLIENT_BOUND_OUTPUT,
        "ip_address": IP_ADDRESS_OUTPUT,
        "route": ROUTE_OUTPUT,
        "ping_ip": PING_OK_OUTPUT,
        "ping_dns": PING_OK_OUTPUT,
        "service": SERVICE_OUTPUT,
    }

    results, _metadata = day3.evaluate_results(
        outputs,
        "7.22.3",
        expected_lan_ip_cidr="192.168.89.1/24",
    )
    statuses = {result["name"]: result["status"] for result in results}

    assert statuses["LAN bridge IP"] == "FAIL"


def test_write_reports_uses_device_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(day3, "REPORT_ROOT", tmp_path)
    report = {
        "device_name": "Hex S 2025/lab02",
        "host": "192.168.88.2",
        "routeros_version": "7.22.3",
        "wan_ip": "10.0.0.10",
        "lan_ip": "192.168.88.1/24",
        "summary": {"pass": 1, "fail": 0, "warning": 0, "skip": 0},
        "test_results": [
            {
                "name": "Internet ping",
                "status": "PASS",
                "reason": "ok",
                "command": "/ping 8.8.8.8 count=3",
                "raw_output": "sent=3 received=3 packet-loss=0%",
            }
        ],
        "failed_items": [],
        "warning_items": [],
        "raw_commands": {},
    }

    json_path, txt_path = day3.write_reports(report)

    assert json_path == tmp_path / "Hex-S-2025-lab02" / "day3_test_report.json"
    assert txt_path.exists()
    written = json.loads(json_path.read_text(encoding="utf-8"))
    assert written["device_name"] == "Hex S 2025/lab02"
