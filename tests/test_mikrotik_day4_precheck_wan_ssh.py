import pytest

import mikrotik_day4_precheck_wan_ssh as precheck


def test_allowed_source_rejects_default_route(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "0.0.0.0/0")

    with pytest.raises(ValueError, match="not allowed"):
        precheck.get_allowed_source()


def test_allowed_source_accepts_single_pc(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "192.168.0.159/32")

    source, mode = precheck.get_allowed_source()

    assert source == "192.168.0.159/32"
    assert mode == "single Automation PC IP"


def test_allowed_source_accepts_home_lan_subnet(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "192.168.0.0/24")

    source, mode = precheck.get_allowed_source()

    assert source == "192.168.0.0/24"
    assert mode == "Home LAN subnet"


def test_parse_ssh_service_detail_enabled():
    output = '0 name="ssh" port=22 disabled=no address=""'

    service = precheck.parse_ssh_service(output)

    assert service["exists"] is True
    assert service["enabled"] is True


def test_parse_ssh_service_detail_disabled():
    output = '0 X name="ssh" port=22 disabled=yes address=""'

    service = precheck.parse_ssh_service(output)

    assert service["exists"] is True
    assert service["enabled"] is False


def test_parse_firewall_rule_matches_expected():
    output = (
        '0 chain=input action=accept protocol=tcp dst-port=22 '
        'src-address=192.168.0.159/32 in-interface-list=WAN disabled=no '
        'comment="Day4 allow SSH from automation source"'
    )

    rule = precheck.parse_firewall_rule(output)

    assert precheck.rule_matches(rule, "192.168.0.159/32") is True


def test_firewall_rule_matches_routeros_normalized_host_address():
    output = (
        '0 chain=input action=accept protocol=tcp dst-port=22 '
        'src-address=192.168.0.114 in-interface-list=WAN disabled=no '
        'comment="Day4 allow SSH from automation source"'
    )

    rule = precheck.parse_firewall_rule(output)

    assert precheck.rule_matches(rule, "192.168.0.114/32") is True


def test_parse_firewall_rule_detects_wrong_source():
    output = (
        '0 chain=input action=accept protocol=tcp dst-port=22 '
        'src-address=192.168.0.0/24 in-interface-list=WAN disabled=no '
        'comment="Day4 allow SSH from automation source"'
    )

    rule = precheck.parse_firewall_rule(output)

    assert precheck.rule_matches(rule, "192.168.0.159/32") is False


def test_firewall_header_only_output_is_not_existing_rule():
    output = "Flags: X - disabled, I - invalid; D - dynamic\nColumns: CHAIN, ACTION"

    rule = precheck.parse_firewall_rule(output)

    assert rule["exists"] is False
    assert precheck.rule_matches(rule, "192.168.0.114/32") is False


def test_build_report_warns_for_subnet_mode():
    report = precheck.build_report(
        device_name="Hex-s-2025-lab01",
        lan_management_ip="192.168.88.1",
        wan_dhcp_ip="192.168.0.200",
        allowed_source="192.168.0.0/24",
        allowed_source_mode="Home LAN subnet",
        ssh_service={"exists": True, "enabled": True, "action": "already enabled"},
        firewall_rule={
            "status": "already existed",
            "matches_expected": True,
            "moved_before_default_drop": True,
        },
        errors=[],
    )

    assert report["overall_result"] == "PASS"
    assert report["warnings"]
    assert "password" not in report
