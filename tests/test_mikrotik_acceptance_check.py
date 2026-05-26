import json

import mikrotik_acceptance_check as acceptance
from mikrotik_day2_auto_setup import Day2Config


def make_config(**overrides):
    values = {
        "host": "192.168.88.1",
        "port": 22,
        "username": "admin",
        "password": "secret",
        "device_name": "Hex-s-2025-lab01",
        "target_routeros_version": "7.22.3",
        "enable_apply_config": False,
        "enable_backup": True,
        "enable_report": True,
        "timezone": "Asia/Taipei",
        "disable_services": ["ftp", "telnet"],
    }
    values.update(overrides)
    return Day2Config(**values)


BASE_OUTPUTS = {
    "identity": "name: Hex-s-2025-lab01",
    "interfaces": "0 R ether1\n1 R ether2\n",
    "bridge_ports": "0 bridge=bridge interface=ether2\n",
    "dhcp_client": "0 interface=ether1 disabled=false add-default-route=yes status=bound",
    "bridges": "0 R name=bridge",
    "ip_address": "0 address=192.168.88.1/24 interface=bridge",
    "services": "0 X ftp 21\n1 ssh 22\n2 X telnet 23\n3 www 80\n",
}


def status_for(results, name):
    return {result["name"]: result["status"] for result in results}[name]


def test_ether1_dhcp_client_enabled_should_pass():
    results = acceptance.evaluate_setup_acceptance(
        BASE_OUTPUTS,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "ether1 DHCP client exists") == "PASS"
    assert status_for(results, "ether1 DHCP client enabled") == "PASS"
    assert status_for(results, "ether1 DHCP add-default-route") == "PASS"


def test_ether1_dhcp_client_missing_should_fail():
    outputs = dict(BASE_OUTPUTS, dhcp_client="")
    results = acceptance.evaluate_setup_acceptance(
        outputs,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "ether1 DHCP client exists") == "FAIL"


def test_ether1_dhcp_client_disabled_should_fail():
    outputs = dict(
        BASE_OUTPUTS,
        dhcp_client="0 interface=ether1 disabled=true add-default-route=yes status=stopped",
    )
    results = acceptance.evaluate_setup_acceptance(
        outputs,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "ether1 DHCP client enabled") == "FAIL"


def test_ether1_inside_lan_bridge_should_fail():
    outputs = dict(BASE_OUTPUTS, bridge_ports="0 bridge=bridge interface=ether1")
    results = acceptance.evaluate_setup_acceptance(
        outputs,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "ether1 is not in LAN bridge") == "FAIL"


def test_ssh_enabled_should_pass():
    results = acceptance.evaluate_setup_acceptance(
        BASE_OUTPUTS,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "ssh service enabled") == "PASS"


def test_ftp_telnet_enabled_should_warn_but_www_is_not_required():
    outputs = dict(BASE_OUTPUTS, services="0 ftp 21\n1 ssh 22\n2 telnet 23\n3 www 80\n")
    results = acceptance.evaluate_setup_acceptance(
        outputs,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "unsafe services disabled") == "WARNING"


def test_expected_lan_ip_cidr_mismatch_should_fail():
    outputs = dict(BASE_OUTPUTS, ip_address="0 address=192.168.99.1/24 interface=bridge")
    results = acceptance.evaluate_setup_acceptance(
        outputs,
        "Hex-s-2025-lab01",
        make_config(),
    )

    assert status_for(results, "LAN bridge IP matches expected") == "FAIL"


def test_no_expected_config_uses_default_ether1_and_bridge_fallback(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.1",
                "username": "admin",
                "device_name": "Hex-s-2025-lab01",
            }
        ),
        encoding="utf-8",
    )

    config = acceptance.load_config(config_path)

    assert config.expected_wan_interface == "ether1"
    assert config.expected_wan_dhcp_client_required is True
    assert config.expected_lan_bridge == "bridge"
    assert config.expected_lan_ip_cidr == "192.168.88.1/24"
    assert config.required_disabled_services == ["ftp", "telnet"]
