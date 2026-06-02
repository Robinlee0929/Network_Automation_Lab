import json

import pytest

import mikrotik_day13_multi_router_wireguard_validation as day13


def valid_profile():
    return {
        "topology_name": "Day13 Multi-router WireGuard Client-to-Site Validation",
        "vpn_type": "client_to_site",
        "devices": [
            {
                "enabled": True,
                "device_name": "Hex-s-2025-lab01",
                "router_host": "192.168.0.199",
                "client_endpoint_host": "192.168.0.199",
                "lan_subnet": "192.168.88.0/24",
                "lan_gateway": "192.168.88.1",
                "lan_host_ip": "192.168.88.254",
                "iperf_server_ip": "192.168.88.254",
                "wireguard_subnet": "10.10.10.0/24",
                "wireguard_router_ip": "10.10.10.1/24",
                "wireguard_client_ip": "10.10.10.2/32",
                "peer_name": "pc-wg-lab01",
                "export_conf_name": "robin-laptop-lab01.conf",
            },
            {
                "enabled": True,
                "device_name": "Hex-s-2025-lab02",
                "router_host": "192.168.0.113",
                "client_endpoint_host": "192.168.0.113",
                "lan_subnet": "192.168.89.0/24",
                "lan_gateway": "192.168.89.1",
                "lan_host_ip": "192.168.89.200",
                "iperf_server_ip": "192.168.89.200",
                "lan_host_validation": {
                    "enabled": True,
                    "lan_host_ip": "192.168.89.200",
                    "expected_gateway": "192.168.89.1",
                    "wireguard_client_subnet": "10.10.20.0/24",
                },
                "wireguard_subnet": "10.10.20.0/24",
                "wireguard_router_ip": "10.10.20.1/24",
                "wireguard_client_ip": "10.10.20.2/32",
                "peer_name": "pc-wg-lab02",
                "export_conf_name": "robin-laptop-lab02.conf",
            },
        ],
    }


def test_valid_lab01_lab02_client_to_site_profile_passes_static_validation():
    report = day13.validate_profile(valid_profile())

    assert report["overall_result"] == "PASS"
    assert report["vpn_type"] == "client_to_site"
    assert [device["result"] for device in report["devices"]] == ["PASS", "PASS"]


def test_device_name_filter_only_validates_one_enabled_device():
    report = day13.validate_profile(valid_profile(), device_name="Hex-s-2025-lab02")

    assert report["overall_result"] == "PASS"
    assert [device["device_name"] for device in report["devices"]] == ["Hex-s-2025-lab02"]


def test_device_name_filter_fails_for_unknown_enabled_device():
    report = day13.validate_profile(valid_profile(), device_name="Hex-s-2025-lab99")

    assert report["overall_result"] == "FAIL"
    assert any("Enabled device profile was not found" in error for error in report["errors"])


def test_vpn_type_must_be_client_to_site():
    profile = valid_profile()
    profile["vpn_type"] = "site_to_site"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("vpn_type must be client_to_site" in error for error in report["errors"])


def test_overlapping_wireguard_subnets_fail():
    profile = valid_profile()
    profile["devices"][1]["wireguard_subnet"] = "10.10.10.0/24"
    profile["devices"][1]["wireguard_router_ip"] = "10.10.10.1/24"
    profile["devices"][1]["wireguard_client_ip"] = "10.10.10.3/32"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("WireGuard subnet overlap" in error for error in report["errors"])


def test_overlapping_lan_subnets_fail():
    profile = valid_profile()
    profile["devices"][1]["lan_subnet"] = "192.168.88.128/25"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("LAN subnet overlap" in error for error in report["errors"])


def test_duplicate_client_wireguard_ip_fails():
    profile = valid_profile()
    profile["devices"][1]["wireguard_subnet"] = "10.10.10.0/24"
    profile["devices"][1]["wireguard_router_ip"] = "10.10.10.3/24"
    profile["devices"][1]["wireguard_client_ip"] = "10.10.10.2/32"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("Duplicate client WireGuard IP" in error for error in report["errors"])


def test_duplicate_router_wireguard_ip_fails():
    profile = valid_profile()
    profile["devices"][1]["wireguard_subnet"] = "10.10.10.0/24"
    profile["devices"][1]["wireguard_router_ip"] = "10.10.10.1/24"
    profile["devices"][1]["wireguard_client_ip"] = "10.10.10.3/32"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("Duplicate router WireGuard IP" in error for error in report["errors"])


def test_missing_required_device_field_fails():
    profile = valid_profile()
    del profile["devices"][0]["peer_name"]

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("Missing required field: peer_name" in error for device in report["devices"] for error in device["errors"])


@pytest.mark.parametrize("field_name", ["password", "PrivateKey"])
def test_profile_with_password_or_private_key_field_fails(field_name):
    profile = valid_profile()
    profile["devices"][0][field_name] = "secret"

    report = day13.validate_profile(profile)

    assert report["overall_result"] == "FAIL"
    assert any("must not contain password or PrivateKey fields" in error for error in report["errors"])


def test_aggregate_result_pass_when_all_devices_pass():
    assert day13.aggregate_result([{"result": "PASS"}, {"result": "PASS"}]) == "PASS"


def test_aggregate_result_fail_when_any_device_fails():
    assert day13.aggregate_result([{"result": "PASS"}, {"result": "FAIL"}]) == "FAIL"


def test_lan_host_validation_disabled_is_skipped():
    validation = day13.build_lan_host_validation_config(valid_profile()["devices"][0])
    result = day13.evaluate_lan_host_ping(validation, "", "PASS", "Hex-s-2025-lab01")

    assert validation["enabled"] is False
    assert result["router_to_lan_host_ping"] == "SKIP"
    assert result["lan_host_diagnosis"] == "LAN host validation disabled"


def test_router_ping_to_lan_host_pass():
    validation = day13.build_lan_host_validation_config(valid_profile()["devices"][1])
    output = "sent=4 received=4 packet-loss=0% min-rtt=1ms avg-rtt=1ms max-rtt=2ms"
    result = day13.evaluate_lan_host_ping(validation, output, "PASS", "Hex-s-2025-lab02")

    assert result["router_to_lan_host_ping"] == "PASS"
    assert result["router_to_lan_host_reachability"] == "PASS"
    assert result["lan_host_diagnosis"] == "Router can reach LAN host"
    assert result["remediation_commands"] == []


def test_router_ping_to_lan_host_fail_reports_causes_and_remediation():
    validation = day13.build_lan_host_validation_config(valid_profile()["devices"][1])
    output = "sent=4 received=0 packet-loss=100%"
    result = day13.evaluate_lan_host_ping(validation, output, "PASS", "Hex-s-2025-lab02")

    assert result["router_to_lan_host_ping"] == "FAIL"
    assert result["router_to_lan_host_reachability"] == "FAIL"
    assert result["lan_host_diagnosis"] == "Tunnel OK, LAN host unreachable"
    assert any("Windows Firewall" in cause for cause in result["likely_causes"])
    assert any("192.168.89.200" in item for item in result["remediation_commands"])
    assert any("New-NetFirewallRule" in item for item in result["remediation_commands"])
    assert any("192.168.89.1,10.10.20.0/24" in item for item in result["remediation_commands"])


def test_tunnel_pass_but_lan_host_fail_updates_device_summary():
    device = day13.validate_profile(valid_profile())["devices"][1]
    device["wireguard_tunnel_status"] = "PASS"
    device["router_gateway_reachability"] = "PASS"
    validation = device["lan_host_validation"]
    result = day13.evaluate_lan_host_ping(
        validation,
        "sent=4 received=0 packet-loss=100%",
        device["router_gateway_reachability"],
        device["device_name"],
    )
    day13.apply_lan_host_result(device, result)

    assert device["wireguard_tunnel_status"] == "PASS"
    assert device["router_to_lan_host_ping"] == "FAIL"
    assert device["lan_host_diagnosis"] == "Tunnel OK, LAN host unreachable"
    assert any("Router cannot ping LAN host" in warning for warning in device["warnings"])


def test_lan_host_fail_remediation_appears_in_html_report():
    report = day13.validate_profile(valid_profile())
    device = report["devices"][1]
    result = day13.evaluate_lan_host_ping(
        device["lan_host_validation"],
        "sent=4 received=0 packet-loss=100%",
        "PASS",
        device["device_name"],
    )
    day13.apply_lan_host_result(device, result)
    html_report = day13.build_html_report(report)

    assert "Tunnel OK, LAN host unreachable" in html_report
    assert "New-NetFirewallRule" in html_report
    assert "192.168.89.1,10.10.20.0/24" in html_report
    assert "<pre><code>" in html_report


def test_html_report_uses_summary_overview_and_device_cards():
    report = day13.validate_profile(valid_profile())
    html_report = day13.build_html_report(report)

    assert '<section class="summary">' in html_report
    assert "Device Overview" in html_report
    assert "Per-Device Diagnosis" in html_report
    assert '<section class="card">' in html_report
    assert "Connectivity Checklist" in html_report
    assert "Likely Causes" in html_report
    assert "Remediation Commands" in html_report
    assert "Device count" in html_report
    assert "<th>WireGuard tunnel status</th>" not in html_report


def test_aggregate_html_does_not_contain_private_key_or_conf_like_content():
    report = day13.validate_profile(valid_profile())
    html_report = day13.build_html_report(report)

    for forbidden in day13.CONF_CONTENT_TOKENS:
        assert forbidden not in html_report


def test_exported_config_path_may_be_shown():
    report = day13.validate_profile(valid_profile())
    html_report = day13.build_html_report(report)

    assert "exports\\wireguard\\robin-laptop-lab01.conf" in html_report or "exports/wireguard/robin-laptop-lab01.conf" in html_report


def test_aggregate_report_write_rejects_conf_content(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = day13.validate_profile(valid_profile())
    report["devices"][0]["warnings"].append("[Interface]")

    with pytest.raises(ValueError):
        day13.write_aggregate_reports(report)


def test_aggregate_report_write_creates_timestamped_summary_copy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = day13.build_report(valid_profile())
    report["timestamp"] = "2026-06-02T01:02:03"

    json_path, html_path, summary_json_path, summary_html_path = day13.write_aggregate_reports(report)

    assert json_path == day13.REPORT_JSON_PATH
    assert html_path == day13.REPORT_HTML_PATH
    assert json_path.exists()
    assert html_path.exists()
    assert summary_json_path == day13.SUMMARY_REPORT_DIR / (
        f"{day13.SUMMARY_REPORT_STEM}_20260602_010203.json"
    )
    assert summary_html_path == day13.SUMMARY_REPORT_DIR / (
        f"{day13.SUMMARY_REPORT_STEM}_20260602_010203.html"
    )
    assert summary_json_path.exists()
    assert summary_html_path.exists()
    assert summary_json_path.read_text(encoding="utf-8") == json_path.read_text(encoding="utf-8")
    assert summary_html_path.read_text(encoding="utf-8") == html_path.read_text(encoding="utf-8")


def test_profile_file_loads_without_passwords_or_conf_content():
    profile = day13.load_profile()
    serialized = json.dumps(profile)

    assert "password" not in serialized.lower()
    assert "privatekey" not in serialized.lower()
    assert len(profile["devices"]) == 5
    assert profile["devices"][2]["template"] is True
    assert day13.validate_profile(profile)["overall_result"] == "PASS"


def test_console_output_lists_static_checks_and_devices():
    report = day13.build_report(valid_profile())
    output = day13.build_console_output(
        report,
        day13.REPORT_JSON_PATH,
        day13.REPORT_HTML_PATH,
    )

    assert "Mode: Static profile validation" in output
    assert "[PASS] vpn_type is client_to_site" in output
    assert "[PASS] WireGuard subnets do not overlap" in output
    assert "[PASS] LAN subnets do not overlap" in output
    assert "Hex-s-2025-lab01" in output
    assert "Hex-s-2025-lab02" in output
    assert "Expected export path:" in output
    assert "Exported config path:" not in output


def test_console_output_lists_timestamped_summary_paths():
    report = day13.build_report(valid_profile())
    output = day13.build_console_output(
        report,
        day13.REPORT_JSON_PATH,
        day13.REPORT_HTML_PATH,
        day13.SUMMARY_REPORT_DIR / "day13_example.json",
        day13.SUMMARY_REPORT_DIR / "day13_example.html",
    )

    assert "Summary JSON report: summary\\day13_example.json" in output or "Summary JSON report: summary/day13_example.json" in output
    assert "Summary HTML report: summary\\day13_example.html" in output or "Summary HTML report: summary/day13_example.html" in output


def test_console_output_uses_ansi_colors_by_default(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    report = day13.build_report(valid_profile())
    output = day13.build_console_output(
        report,
        day13.REPORT_JSON_PATH,
        day13.REPORT_HTML_PATH,
    )

    assert "\033[" in output
    assert "\033[32;1m[PASS]\033[0m" in output


def test_console_output_does_not_print_private_key_or_conf_like_content():
    report = day13.build_report(valid_profile())
    output = day13.build_console_output(
        report,
        day13.REPORT_JSON_PATH,
        day13.REPORT_HTML_PATH,
    )

    forbidden_tokens = [
        token
        for token in day13.CONF_CONTENT_TOKENS
        if token not in {"PrivateKey"}
    ]
    for forbidden in forbidden_tokens:
        assert forbidden not in output
    assert "PrivateKey" not in output
    assert "exports" in output
    assert ".conf" in output


def test_lab02_setup_guidance_prints_manual_commands_without_conf_content():
    device = valid_profile()["devices"][1]
    output = day13.build_lab_setup_guidance(
        device,
        endpoint_host="lab02.example.net",
        router_host="192.168.0.202",
    )

    assert "Day13 semi-automatic setup guidance: Hex-s-2025-lab02" in output
    assert "[SKIP] No router changes were applied by this script." in output
    assert "Client config private key will be generated by private-key=auto" in output
    assert "/interface/wireguard/add" in output
    assert '/ip/address/add address="10.10.20.1/24"' in output
    assert "/interface/wireguard/peers/add" in output
    assert "private-key=auto" in output
    assert '/ip/firewall/filter/move [find comment="day13 allow wireguard udp"] destination=6' in output
    assert "pc-wg-lab02" in output
    assert "lab02.example.net" in output
    assert "python mikrotik_day12_wireguard_vpn_automation.py" in output
    assert "--router-host 192.168.0.202" in output
    assert "--wg-router-ip 10.10.20.1/24" in output
    assert "--lan-subnet 192.168.89.0/24" in output
    assert "--lan-host-ip 192.168.89.200" in output
    assert "--iperf-server-ip 192.168.89.200" in output
    assert "robin-laptop-lab02.conf" in output
    assert "Verify these RouterOS states before running Day12 export:" in output
    assert "/ip/firewall/filter/print" in output
    assert "day13 allow wireguard udp is before defconf drop all not coming from LAN" in output
    assert "/ip/address/print where interface=wg0" in output
    assert "Expect: 10.10.20.1/24 on wg0." in output
    assert "ping 192.168.89.1" in output
    assert "ping 192.168.89.200" in output
    assert "Verify the LAN host side if LAN gateway works but LAN host ping fails:" in output
    assert "LAN host IP should be 192.168.89.200." in output
    assert "LAN host default gateway should be 192.168.89.1." in output
    assert "Windows Firewall on the LAN host should allow ICMP Echo Request." in output
    assert "add a route back to 10.10.20.0/24 via 192.168.89.1" in output
    assert "/interface/wireguard/peers/print detail" in output
    assert "Expect: allowed-address=10.10.20.2/32." in output
    assert "Expect: client-allowed-address=10.10.20.0/24,192.168.89.0/24." in output
    assert "PrivateKey" not in output
    assert "[Interface]" not in output
    assert "[Peer]" not in output
