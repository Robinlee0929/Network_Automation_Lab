import json

import cisco_topology_validation as cisco_validation
from parsers import cisco_parser


SHOW_VERSION = """
Cisco IOS Software, C2960C Software (C2960c405-UNIVERSALK9-M), Version 15.2(7)E9, RELEASE SOFTWARE (fc4)
cisco-switch uptime is 2 weeks, 3 days, 4 hours, 5 minutes
System serial number            : FOC1234X0YZ
Model number                    : WS-C2960CG-8TC-L
"""

SHOW_IP_INTERFACE_BRIEF = """
Interface              IP-Address      OK? Method Status                Protocol
Vlan1                  192.168.0.111   YES manual up                    up
GigabitEthernet0/1     unassigned      YES unset  up                    up
GigabitEthernet0/2     unassigned      YES unset  down                  down
"""

SHOW_INTERFACES_STATUS = """
Port      Name               Status       Vlan       Duplex  Speed Type
Gi0/1                        connected    1          a-full  a-100 10/100/1000BaseTX
Gi0/5     AP                 connected    1          a-full  a-100 10/100/1000BaseTX
Gi0/7     Camera             connected    1          a-full  a-100 10/100/1000BaseTX
Gi0/8     Uplink             connected    1          a-full  a-100 10/100/1000BaseTX
"""

SHOW_VLAN_BRIEF = """
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/5, Gi0/7, Gi0/8
1002 fddi-default                     act/unsup
"""

SHOW_MAC_ADDRESS_TABLE = """
          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
*  1    0011.2233.4455    DYNAMIC     Gi0/1
   1    aabb.ccdd.eeff    STATIC      CPU
Total Mac Addresses for this criterion: 2
"""

SHOW_STP_SUMMARY = """
Switch is in pvst mode
Root bridge for: none

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0001               0        0         0        4          4
"""


def sample_outputs():
    return {
        "show_version": SHOW_VERSION,
        "show_ip_interface_brief": SHOW_IP_INTERFACE_BRIEF,
        "show_interfaces_status": SHOW_INTERFACES_STATUS,
        "show_vlan_brief": SHOW_VLAN_BRIEF,
        "show_mac_address_table": SHOW_MAC_ADDRESS_TABLE,
        "show_spanning_tree_summary": SHOW_STP_SUMMARY,
    }


def sample_config(**overrides):
    config = {
        "device": {"vendor": "cisco", "platform": "ios"},
        "host": "192.168.0.111",
        "port": 22,
        "username": "admin",
        "password": "secret",
        "device_name": "cisco-switch",
        "device_type": "cisco_ios",
        "expected_model": "WS-C2960CG-8TC-L",
        "expected_management_ip": "192.168.0.111",
        "expected_connected_ports": ["Gi0/1", "Gi0/5", "Gi0/7", "Gi0/8"],
        "expected_vlan": 1,
        "expected_stp_mode": "pvst",
        "legacy_ssh": True,
    }
    config.update(overrides)
    return config


def test_cisco_parsers_extract_expected_fields():
    version = cisco_parser.parse_show_version(SHOW_VERSION)
    ip_interfaces = cisco_parser.parse_show_ip_interface_brief(SHOW_IP_INTERFACE_BRIEF)
    status = cisco_parser.parse_show_interfaces_status(SHOW_INTERFACES_STATUS)
    vlans = cisco_parser.parse_show_vlan_brief(SHOW_VLAN_BRIEF)
    mac_table = cisco_parser.parse_show_mac_address_table(SHOW_MAC_ADDRESS_TABLE)
    stp = cisco_parser.parse_show_spanning_tree_summary(SHOW_STP_SUMMARY)

    assert version["ios_version"] == "15.2(7)E9"
    assert version["model"] == "WS-C2960CG-8TC-L"
    assert ip_interfaces["Vlan1"]["ip_address"] == "192.168.0.111"
    assert ip_interfaces["Vlan1"]["status"] == "up"
    assert status["Gi0/5"]["status"] == "connected"
    assert vlans["1"]["status"] == "active"
    assert "Gi0/8" in vlans["1"]["ports"]
    assert mac_table["dynamic_count"] == 1
    assert stp["mode"] == "pvst"
    assert stp["vlan_blocking_ports"]["VLAN0001"] == 0


def test_parse_show_vlan_brief_includes_wrapped_ports():
    output = """
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/1, Gi0/2,
                                                Gi0/3, GigabitEthernet0/4
                                                Fa0/5
20   users                            active    Gi0/6
"""

    vlans = cisco_parser.parse_show_vlan_brief(output)

    assert vlans["1"]["ports"] == ["Gi0/1", "Gi0/2", "Gi0/3", "Gi0/4", "Fa0/5"]
    assert vlans["20"]["ports"] == ["Gi0/6"]


def test_parse_show_vlan_brief_ignores_orphan_and_malformed_continuations():
    output = """
                                                Gi0/99
1    default                          active    Gi0/1
                                                not-a-port
                                                Gi0/2
20   users                            active    Gi0/3
"""

    vlans = cisco_parser.parse_show_vlan_brief(output)

    assert vlans["1"]["ports"] == ["Gi0/1"]
    assert vlans["20"]["ports"] == ["Gi0/3"]


def test_parse_show_vlan_brief_preserves_single_line_output():
    vlans = cisco_parser.parse_show_vlan_brief(SHOW_VLAN_BRIEF)

    assert vlans["1"] == {
        "vlan_id": "1",
        "name": "default",
        "status": "active",
        "ports": ["Gi0/1", "Gi0/5", "Gi0/7", "Gi0/8"],
    }
    assert vlans["1002"]["ports"] == []


def test_evaluate_topology_passes_expected_profile():
    checks, parsed = cisco_validation.evaluate_topology(sample_config(), sample_outputs())
    statuses = {check["name"]: check["result"] for check in checks}

    assert statuses["show version readable"] == "PASS"
    assert statuses["Switch model"] == "PASS"
    assert statuses["IOS version parsed"] == "PASS"
    assert statuses["Vlan1 management IP"] == "PASS"
    assert statuses["Expected ports connected"] == "PASS"
    assert statuses["VLAN 1 active"] == "PASS"
    assert statuses["Dynamic MAC learned"] == "PASS"
    assert statuses["VLAN0001 blocking ports"] == "PASS"
    assert parsed["show_version"]["model"] == "WS-C2960CG-8TC-L"


def test_evaluate_topology_fails_port_and_management_ip_mismatch():
    outputs = sample_outputs()
    outputs["show_ip_interface_brief"] = outputs["show_ip_interface_brief"].replace(
        "192.168.0.111", "192.168.0.112"
    )
    outputs["show_interfaces_status"] = outputs["show_interfaces_status"].replace(
        "Gi0/8     Uplink             connected", "Gi0/8     Uplink             notconnect"
    )

    checks, _parsed = cisco_validation.evaluate_topology(sample_config(), outputs)
    statuses = {check["name"]: check["result"] for check in checks}

    assert statuses["Vlan1 management IP"] == "FAIL"
    assert statuses["Expected ports connected"] == "FAIL"
    assert cisco_validation.overall_result(checks) == "FAIL"


def test_resolve_config_path_prefers_cisco_config(tmp_path, monkeypatch):
    monkeypatch.setattr(cisco_validation, "CISCO_CONFIG_PATH", tmp_path / "config.cisco.json")
    monkeypatch.setattr(
        cisco_validation,
        "CISCO_EXAMPLE_CONFIG_PATH",
        tmp_path / "config.cisco.example.json",
    )
    cisco_validation.CISCO_CONFIG_PATH.write_text(json.dumps(sample_config()), encoding="utf-8")
    cisco_validation.CISCO_EXAMPLE_CONFIG_PATH.write_text(json.dumps(sample_config()), encoding="utf-8")

    assert cisco_validation.resolve_config_path() == cisco_validation.CISCO_CONFIG_PATH


def test_resolve_config_path_falls_back_to_cisco_example(tmp_path, monkeypatch):
    monkeypatch.setattr(cisco_validation, "CISCO_CONFIG_PATH", tmp_path / "config.cisco.json")
    monkeypatch.setattr(
        cisco_validation,
        "CISCO_EXAMPLE_CONFIG_PATH",
        tmp_path / "config.cisco.example.json",
    )
    cisco_validation.CISCO_EXAMPLE_CONFIG_PATH.write_text(json.dumps(sample_config()), encoding="utf-8")

    assert cisco_validation.resolve_config_path() == cisco_validation.CISCO_EXAMPLE_CONFIG_PATH


def test_prompt_switch_host_keeps_config_host_on_enter(monkeypatch):
    config = sample_config()
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    cisco_validation.prompt_switch_host(config, interactive=True)

    assert config["host"] == "192.168.0.111"
    assert config["expected_management_ip"] == "192.168.0.111"


def test_prompt_switch_host_updates_host_and_matching_expected_ip(monkeypatch):
    config = sample_config()
    monkeypatch.setattr("builtins.input", lambda _prompt: "192.168.0.222")

    cisco_validation.prompt_switch_host(config, interactive=True)

    assert config["host"] == "192.168.0.222"
    assert config["expected_management_ip"] == "192.168.0.222"


def test_prompt_switch_host_preserves_explicit_expected_ip(monkeypatch):
    config = sample_config(expected_management_ip="192.168.0.250")
    monkeypatch.setattr("builtins.input", lambda _prompt: "192.168.0.222")

    cisco_validation.prompt_switch_host(config, interactive=True)

    assert config["host"] == "192.168.0.222"
    assert config["expected_management_ip"] == "192.168.0.250"


def test_write_json_and_html_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(cisco_validation, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(cisco_validation, "REPORT_JSON", tmp_path / "switch_topology_report.json")
    monkeypatch.setattr(cisco_validation, "REPORT_HTML", tmp_path / "switch_topology_report.html")
    checks, parsed = cisco_validation.evaluate_topology(sample_config(), sample_outputs())
    checks.append(
        cisco_validation.make_check(
            "SSH login",
            "authenticated",
            "authenticated",
            "PASS",
            "SSH login succeeded.",
        )
    )
    checks.append(
        cisco_validation.make_check(
            "Report generation",
            "JSON and HTML report files",
            "pending",
            "PASS",
            "Reports generated.",
        )
    )
    report = cisco_validation.build_report(
        sample_config(),
        checks,
        parsed,
        sample_outputs(),
        "2026-05-27T12:00:00",
    )

    json_path, html_path = cisco_validation.write_reports(report)

    assert json_path.exists()
    assert html_path.exists()
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["overall_result"] == "PASS"
    assert "Cisco Switch Topology Validation" in html_path.read_text(encoding="utf-8")
