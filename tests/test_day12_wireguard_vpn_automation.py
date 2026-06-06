import json
from pathlib import Path

import pytest

import mikrotik_day12_wireguard_vpn_automation as day12


CLIENT_CONFIG = """[Interface]
PrivateKey = super-secret-private-key
Address = 10.10.10.2/32
DNS = 192.168.88.1

[Peer]
PublicKey = router-public-key
AllowedIPs = 10.10.10.0/24,192.168.88.0/24
Endpoint = 192.168.0.199:13231
PersistentKeepalive = 25
"""


class FakeSshClient:
    def close(self):
        pass


def day12_config(expect_connected=True, run_iperf=False):
    return day12.Day12Config(
        device_name="Hex-s-2025-lab01",
        router_host="192.168.0.199",
        router_username="admin",
        router_password="router-secret-password",
        router_ssh_port=22,
        wg_interface="wg0",
        peer_name="pc-wg-day12",
        client_address="10.10.10.2/32",
        client_dns="192.168.88.1",
        client_endpoint_host="192.168.0.199",
        client_allowed_ips="10.10.10.0/24,192.168.88.0/24",
        client_keepalive=25,
        conf_filename="robin-laptop-day12.conf",
        wg_router_ip="10.10.10.1/24",
        lan_subnet="192.168.88.0/24",
        lan_gateway_ip="192.168.88.1",
        lan_host_ip="192.168.88.254",
        iperf_server_ip="192.168.88.254",
        iperf_port=5201,
        iperf_duration=40,
        iperf_omit=10,
        iperf_parallel=4,
        run_iperf=run_iperf,
        recreate_peer=False,
        apply_firewall_fixes=False,
        expect_connected=expect_connected,
        non_interactive=True,
    )


def run_day12_with_fake_state(
    tmp_path,
    monkeypatch,
    initial_peer,
    refreshed_peer=None,
    connectivity_ok=True,
    run_iperf=False,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(day12, "connect_ssh_with_auth_retry", lambda _config: FakeSshClient())
    monkeypatch.setattr(day12, "show_client_config", lambda _client, _peer_name: CLIENT_CONFIG)
    monkeypatch.setattr(day12.shutil, "which", lambda _name: "iperf3.exe")
    monkeypatch.setattr(
        day12,
        "run_allowlisted_write",
        lambda _client, command: pytest.fail(f"unexpected write command: {command}"),
    )

    peer_reads = [initial_peer, refreshed_peer if refreshed_peer is not None else initial_peer]

    def fake_read(_client, command):
        if command == "/interface/wireguard/print detail":
            return '0 name="wg0" listen-port=13231 disabled=no running=yes'
        if command == "/interface/wireguard/peers/print detail":
            return peer_reads.pop(0) if len(peer_reads) > 1 else peer_reads[0]
        if command == "/ip/address/print detail":
            return '0 address=10.10.10.1/24 interface="wg0" disabled=no'
        if command == "/ip/firewall/filter/print detail":
            return """
0 chain=input action=accept protocol=udp in-interface-list=WAN dst-port=13231 disabled=no
1 chain=forward action=accept src-address=10.10.10.0/24 dst-address=192.168.88.0/24 disabled=no
"""
        raise AssertionError(f"unexpected read command: {command}")

    def fake_subprocess(command, timeout):
        if command and command[0] == "ping":
            return connectivity_ok, "Reply from target" if connectivity_ok else "Request timed out", ""
        if command and command[0] == "powershell":
            return True, "True\r\n" if connectivity_ok else "False\r\n", ""
        raise AssertionError(f"unexpected subprocess command: {command}")

    def fake_iperf(_command, timeout, progress_label, progress_seconds):
        if connectivity_ok:
            return True, "[SUM] 0.00-40.00 sec 959 MBytes 201 Mbits/sec receiver", ""
        return False, "", ""

    monkeypatch.setattr(day12, "run_allowlisted_read", fake_read)
    monkeypatch.setattr(day12, "run_subprocess", fake_subprocess)
    monkeypatch.setattr(day12, "run_subprocess_with_countdown", fake_iperf)

    report, json_path, html_path = day12.run(day12_config(expect_connected=True, run_iperf=run_iperf))
    return report, json_path, html_path


def base_checks():
    return {
        "wg_interface_exists": "PASS",
        "wg_interface_running": "PASS",
        "wg_interface_ip_exists": "PASS",
        "peer_exists": "PASS",
        "peer_allowed_address": "PASS",
        "client_config_generated": "PASS",
        "config_file_written": "PASS",
        "private_key_redacted_in_report": "PASS",
        "firewall_udp_input_allow": "PASS",
        "firewall_forward_vpn_to_lan": "PASS",
        "handshake_seen": "PASS",
        "peer_rx_tx_nonzero": "PASS",
        "ping_lan_gateway": "PASS",
        "ping_lan_host": "PASS",
        "tcp_5201_reachable": "PASS",
        "iperf_forward": "PASS",
        "iperf_reverse": "PASS",
    }


def test_valid_conf_filename_accepted():
    assert day12.validate_conf_filename("robin-laptop-day12.conf") == "robin-laptop-day12.conf"


@pytest.mark.parametrize("filename", ["client.txt", "../client.conf", "dir/client.conf", "C:\\tmp\\client.conf", "bad name.conf"])
def test_invalid_conf_filename_rejected(filename):
    with pytest.raises(ValueError):
        day12.validate_conf_filename(filename)


def test_export_path_always_under_exports_wireguard(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = day12.build_export_path("client.conf")

    assert path == Path("exports") / "wireguard" / "client.conf"
    assert path.parent.exists()


def test_private_key_redacted_in_report_data():
    sanitized = day12.sanitize_client_config_for_report(CLIENT_CONFIG)

    assert "PrivateKey = REDACTED" in sanitized
    assert "super-secret-private-key" not in sanitized
    assert day12.private_key_leaked({"config": sanitized}) is False


def test_private_key_redaction_handles_routeros_padded_output():
    config = "   PrivateKey = super-secret-private-key\r\n"
    sanitized = day12.sanitize_client_config_for_report(config)

    assert "PrivateKey = REDACTED" in sanitized
    assert "super-secret-private-key" not in sanitized
    assert day12.private_key_leaked(sanitized) is False


def test_private_key_leak_detection_fails_if_report_contains_real_private_key():
    checks = base_checks()
    result, _warnings, errors = day12.evaluate_day12_result(
        checks,
        run_iperf=True,
        report_data={"config": CLIENT_CONFIG},
    )

    assert result == "FAIL"
    assert "PrivateKey leaked" in errors[0]


def test_redact_private_keys_recurses_before_report_write():
    report = {
        "config": CLIENT_CONFIG,
        "nested": [
            {"summary": "PrivateKey=another-secret"},
            "PrivateKey = REDACTED",
        ],
    }

    redacted = day12.redact_private_keys(report)

    assert day12.private_key_leaked(redacted) is False
    assert "super-secret-private-key" not in json.dumps(redacted)
    assert "another-secret" not in json.dumps(redacted)


def test_write_reports_redacts_private_key_before_disk_write(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = {
        "device_name": "Hex-s-2025-lab01",
        "overall_result": "PASS",
        "wireguard_summary": {"raw": CLIENT_CONFIG},
        "checks": dict(base_checks()),
        "warnings": [],
        "errors": [],
        "suggestions": [],
        "sanitized_client_config_summary": CLIENT_CONFIG,
    }

    json_path, html_path = day12.write_reports(report)
    json_text = json_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    saved = json.loads(json_text)

    assert "super-secret-private-key" not in json_text
    assert "super-secret-private-key" not in html_text
    assert saved["overall_result"] == "FAIL"
    assert saved["checks"]["private_key_redacted_in_report"] == "FAIL"
    assert any("PrivateKey leaked" in error for error in saved["errors"])


def test_html_report_uses_wireguard_title_without_day_label():
    html_report = day12.build_html_report(
        {
            "device_name": "Hex-s-2025-lab01",
            "overall_result": "PASS",
            "wireguard_summary": {},
            "checks": {},
            "warnings": [],
            "errors": [],
            "suggestions": [],
            "sanitized_client_config_summary": "",
        }
    )

    assert "<title>WireGuard VPN Automation</title>" in html_report
    assert "<h1>WireGuard VPN Automation</h1>" in html_report
    assert "Day12" not in html_report


def test_html_report_shows_config_path_without_rendering_conf_content():
    html_report = day12.build_html_report(
        {
            "device_name": "Hex-s-2025-lab01",
            "overall_result": "PASS",
            "wireguard_summary": {
                "interface_name": "wg0",
                "listen_port": 13231,
                "client_address": "10.10.10.2/32",
                "client_dns": "192.168.88.1",
                "client_endpoint_host": "192.168.0.199",
                "exported_config_path": "exports/wireguard/robin-laptop-day12.conf",
            },
            "checks": {},
            "warnings": [],
            "errors": [],
            "suggestions": [],
            "sanitized_client_config_summary": CLIENT_CONFIG,
        }
    )

    assert "exports/wireguard/robin-laptop-day12.conf" in html_report
    assert "Sanitized Client Config Summary" not in html_report
    for forbidden in (
        "[Interface]",
        "[Peer]",
        "PrivateKey",
        "PublicKey",
        "AllowedIPs",
        "Endpoint",
        "PersistentKeepalive",
        "Address",
        "DNS",
        "ListenPort",
    ):
        assert forbidden not in html_report


def test_show_client_config_output_parsed_correctly():
    parsed = day12.parse_wireguard_client_config(CLIENT_CONFIG)

    assert parsed["valid"] is True
    assert parsed["interface"]["Address"] == "10.10.10.2/32"
    assert parsed["peer"]["Endpoint"] == "192.168.0.199:13231"


def test_endpoint_host_should_not_duplicate_port():
    assert day12.endpoint_host_only("192.168.0.199:13231") == "192.168.0.199"


def test_peer_add_command_uses_private_key_auto_and_host_only_endpoint():
    command = day12.build_peer_add_command(
        "wg0",
        "pc-wg-day12",
        "10.10.10.2/32",
        "192.168.88.1",
        "192.168.0.199:13231",
        "10.10.10.0/24,192.168.88.0/24",
        25,
    )

    assert "private-key=auto" in command
    assert 'client-endpoint="192.168.0.199"' in command
    assert "192.168.0.199:13231" not in command


def test_peer_add_command_uses_allowlisted_fields_only():
    command = day12.build_peer_add_command(
        "wg0",
        "pc-wg-day12",
        "10.10.10.2/32",
        "192.168.88.1",
        "192.168.0.199",
        "10.10.10.0/24,192.168.88.0/24",
        25,
    )

    for unsafe in ("reboot", "reset", "/export", "password=", "show-client-config"):
        assert unsafe not in command
    assert command.startswith("/interface/wireguard/peers/add ")


def test_firewall_udp_rule_detection_before_drop_rule():
    output = """
0 chain=input action=accept protocol=udp in-interface-list=WAN dst-port=13231 disabled=no
1 chain=input action=drop in-interface-list=!LAN
"""

    assert day12.detect_firewall_udp_allow_before_drop(output, 13231)["found"] is True


def test_firewall_udp_rule_after_drop_is_not_valid():
    output = """
0 chain=input action=drop in-interface-list=!LAN
1 chain=input action=accept protocol=udp in-interface-list=WAN dst-port=13231 disabled=no
"""

    assert day12.detect_firewall_udp_allow_before_drop(output, 13231)["found"] is False


def test_firewall_udp_detection_ignores_drop_invalid_before_wireguard_rule():
    output = """
1 ;;; defconf: accept established,related,untracked chain=input action=accept connection-state=established,related,untracked
2 ;;; defconf: drop invalid chain=input action=drop connection-state=invalid
6 ;;; day12 allow wireguard udp chain=input action=accept protocol=udp in-interface-list=WAN dst-port=13231
7 ;;; defconf: drop all not coming from LAN chain=input action=drop in-interface-list=!LAN
"""

    result = day12.detect_firewall_udp_allow_before_drop(output, 13231)

    assert result["found"] is True
    assert result["accept_index"] < result["drop_index"]


def test_forward_vpn_to_lan_rule_detection():
    output = "0 chain=forward action=accept src-address=10.10.10.0/24 dst-address=192.168.88.0/24 disabled=no"

    assert day12.detect_forward_vpn_to_lan_rule(output, "10.10.10.0/24", "192.168.88.0/24")["found"] is True


def test_peer_handshake_parser_handles_last_and_latest_variants():
    latest = '0 name="pc-wg-day12" latest-handshake=1m30s rx=1KiB tx=2KiB'
    last = '0 name="pc-wg-day12" last-handshake=2m rx=1KiB tx=2KiB'

    assert day12.parse_wireguard_peer_detail(latest, "pc-wg-day12")["handshake_seen"] is True
    assert day12.parse_wireguard_peer_detail(last, "pc-wg-day12")["handshake_seen"] is True


def test_peer_rx_tx_parser_handles_kib_values():
    peer = day12.parse_wireguard_peer_detail('0 name="pc-wg-day12" rx=1KiB tx=2KiB', "pc-wg-day12")

    assert peer["rx_bytes"] == 1024
    assert peer["tx_bytes"] == 2048
    assert peer["rx_tx_nonzero"] is True


def test_iperf3_sum_mbps_parser_for_forward_direction():
    output = "[SUM]   0.00-40.00  sec   959 MBytes   201 Mbits/sec  receiver"

    assert day12.parse_iperf3_summary_mbps(output) == 201


def test_iperf3_sum_mbps_parser_for_reverse_direction():
    output = "[SUM]   0.00-40.00  sec  1.27 GBytes   272 Mbits/sec  receiver"

    assert day12.parse_iperf3_summary_mbps(output) == 272


def test_result_logic_pass_when_both_iperf_directions_exceed_threshold():
    result, warnings, errors = day12.evaluate_day12_result(base_checks(), run_iperf=True, expect_connected=True)

    assert result == "PASS"
    assert warnings == []
    assert errors == []


def test_result_logic_pass_when_iperf_disabled_and_checks_are_clean():
    result, warnings, errors = day12.evaluate_day12_result(base_checks(), run_iperf=False)

    assert result == "PASS"
    assert warnings == []
    assert errors == []


def test_skip_connectivity_checks_do_not_warn_before_config_import():
    checks = base_checks()
    checks["ping_lan_gateway"] = "SKIP"
    checks["ping_lan_host"] = "SKIP"
    checks["tcp_5201_reachable"] = "SKIP"
    checks["iperf_forward"] = "SKIP"
    checks["iperf_reverse"] = "SKIP"
    result, warnings, errors = day12.evaluate_day12_result(checks, run_iperf=False)

    assert result == "PASS"
    assert warnings == []
    assert errors == []


def test_existing_peer_is_reused_when_recreate_peer_not_provided():
    peer = day12.parse_wireguard_peer_detail('0 name="pc-wg-day12" allowed-address=10.10.10.2/32', "pc-wg-day12")

    assert peer["exists"] is True
    assert day12.build_peer_remove_command("other") != day12.build_peer_remove_command("pc-wg-day12")


def test_existing_peer_is_not_removed_in_default_mode(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    args = day12.parse_args(
        [
            "--device-name",
            "test-device",
            "--router-host",
            "192.0.2.10",
            "--router-username",
            "test-admin",
            "--non-interactive",
        ]
    )
    config = day12.build_config_from_args(args)

    assert not (tmp_path / "config.json").exists()
    assert config.device_name == "test-device"
    assert config.router_host == "192.0.2.10"
    assert config.router_username == "test-admin"
    assert config.recreate_peer is False


def test_existing_peer_default_mode_does_not_execute_remove_command(tmp_path, monkeypatch):
    peer = '0 name="pc-wg-day12" allowed-address=10.10.10.2/32 last-handshake=16s rx=1KiB tx=2KiB'

    report, _json_path, _html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer=peer,
        connectivity_ok=True,
    )

    assert report["checks"]["peer_exists"] == "PASS"
    assert report["wireguard_summary"]["initial_peer_state"]["exists"] is True
    assert report["suggestions"] == []


def test_day12_config_file_loads_repeated_values_without_password(tmp_path, monkeypatch):
    config_path = tmp_path / "Set_WireguardVPN_config.json"
    config_path.write_text(
        json.dumps(
            {
                "device_name": "Hex-s-2025-lab01",
                "router_host": "192.168.0.199",
                "router_username": "admin",
                "router_ssh_port": 2222,
                "wg_interface": "wg0",
                "peer_name": "pc-wg-day12",
                "client_address": "10.10.10.2/32",
                "client_dns": "192.168.88.1",
                "client_endpoint_host": "192.168.0.199",
                "client_allowed_ips": "10.10.10.0/24,192.168.88.0/24",
                "client_keepalive": 25,
                "conf_filename": "robin-laptop-day12.conf",
                "wg_router_ip": "10.10.10.1/24",
                "lan_subnet": "192.168.88.0/24",
                "lan_gateway_ip": "192.168.88.1",
                "lan_host_ip": "192.168.88.254",
                "iperf_server_ip": "192.168.88.254",
                "iperf_port": 5201,
                "iperf_duration": 40,
                "iperf_omit": 10,
                "iperf_parallel": 4,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(day12, "load_default_router_config", lambda: {"password": "secret"})

    args = day12.parse_args(["--config", str(config_path), "--non-interactive"])
    config = day12.build_config_from_args(args)
    saved = day12.day12_config_to_saved_dict(config)

    assert config.router_host == "192.168.0.199"
    assert config.router_ssh_port == 2222
    assert config.conf_filename == "robin-laptop-day12.conf"
    assert config.wg_router_ip == "10.10.10.1/24"
    assert config.lan_subnet == "192.168.88.0/24"
    assert "router_password" not in saved
    assert "password" not in json.dumps(saved)


def test_day12_cli_accepts_lab02_wireguard_router_ip_and_lan_subnet(monkeypatch):
    monkeypatch.setattr(day12, "load_default_router_config", lambda: {"password": "secret"})

    args = day12.parse_args(
        [
            "--device-name",
            "Hex-s-2025-lab02",
            "--router-host",
            "192.168.0.113",
            "--router-username",
            "admin",
            "--client-address",
            "10.10.20.2/32",
            "--client-allowed-ips",
            "10.10.20.0/24,192.168.89.0/24",
            "--wg-router-ip",
            "10.10.20.1/24",
            "--lan-subnet",
            "192.168.89.0/24",
            "--lan-gateway-ip",
            "192.168.89.1",
            "--lan-host-ip",
            "192.168.89.200",
            "--non-interactive",
        ]
    )
    config = day12.build_config_from_args(args)
    report = day12.make_initial_report(config)

    assert config.wg_router_ip == "10.10.20.1/24"
    assert config.lan_subnet == "192.168.89.0/24"
    assert config.lan_gateway_ip == "192.168.89.1"
    assert report["wireguard_summary"]["interface_ip"] == "10.10.20.1/24"


def test_cli_values_override_day12_config_file(tmp_path, monkeypatch):
    config_path = tmp_path / "Set_WireguardVPN_config.json"
    config_path.write_text(
        json.dumps(
            {
                "device_name": "Hex-s-2025-lab01",
                "router_host": "192.168.0.199",
                "router_username": "admin",
                "conf_filename": "from-config.conf",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(day12, "load_default_router_config", lambda: {"password": "secret"})

    args = day12.parse_args(
        [
            "--config",
            str(config_path),
            "--router-host",
            "192.168.88.1",
            "--conf-filename",
            "from-cli.conf",
            "--non-interactive",
        ]
    )
    config = day12.build_config_from_args(args)

    assert config.router_host == "192.168.88.1"
    assert config.conf_filename == "from-cli.conf"


def test_missing_handshake_is_warn_in_default_mode():
    checks = base_checks()
    checks["handshake_seen"] = "WARN"
    result, warnings, errors = day12.evaluate_day12_result(checks, run_iperf=False)

    assert result == "WARN"
    assert any("handshake" in warning for warning in warnings)
    assert errors == []


def test_missing_handshake_is_fail_in_expect_connected_mode():
    checks = base_checks()
    checks["handshake_seen"] = "FAIL"
    checks["ping_lan_gateway"] = "FAIL"
    checks["ping_lan_host"] = "FAIL"
    checks["tcp_5201_reachable"] = "FAIL"
    checks["iperf_forward"] = "SKIP"
    checks["iperf_reverse"] = "SKIP"
    result, _warnings, errors = day12.evaluate_day12_result(checks, expect_connected=True)

    assert result == "FAIL"
    assert any("handshake" in error for error in errors)


def test_initial_missing_handshake_with_later_ping_and_tcp_pass_does_not_fail_summary(tmp_path, monkeypatch):
    initial_peer = '0 name="pc-wg-day12" allowed-address=10.10.10.2/32 rx=1KiB tx=2KiB'

    report, json_path, html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer=initial_peer,
        connectivity_ok=True,
        run_iperf=True,
    )

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8")
    assert report["overall_result"] != "FAIL"
    assert report["checks"]["initial_handshake_seen"] == "WARN"
    assert report["checks"]["post_connectivity_handshake_seen"] == "WARN"
    assert report["checks"]["final_vpn_connectivity"] == "PASS"
    assert report["checks"]["ping_lan_gateway"] == "PASS"
    assert report["checks"]["ping_lan_host"] == "PASS"
    assert report["checks"]["tcp_5201_reachable"] == "PASS"
    assert report["checks"]["iperf_forward"] == "PASS"
    assert report["checks"]["iperf_reverse"] == "PASS"
    assert "initial_peer_state" in report["wireguard_summary"]
    assert "post_connectivity_peer_state" in report["wireguard_summary"]
    for secret in ("super-secret-private-key", "router-secret-password"):
        assert secret not in json.dumps(saved)
        assert secret not in html


def test_initial_missing_handshake_then_refreshed_peer_handshake_passes_summary(tmp_path, monkeypatch):
    initial_peer = '0 name="pc-wg-day12" allowed-address=10.10.10.2/32 rx=1KiB tx=2KiB'
    refreshed_peer = '0 name="pc-wg-day12" allowed-address=10.10.10.2/32 last-handshake=16s rx=2KiB tx=4KiB'

    report, _json_path, _html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer=initial_peer,
        refreshed_peer=refreshed_peer,
        connectivity_ok=True,
    )

    assert report["overall_result"] == "PASS"
    assert report["checks"]["initial_handshake_seen"] == "WARN"
    assert report["checks"]["post_connectivity_handshake_seen"] == "PASS"
    assert report["checks"]["handshake_seen"] == "PASS"
    assert report["wireguard_summary"]["post_connectivity_peer_state"]["latest_handshake"] == "16s"


def test_peer_missing_still_fails_with_connectivity_checks(tmp_path, monkeypatch):
    report, _json_path, _html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer="",
        connectivity_ok=True,
    )

    assert report["overall_result"] == "FAIL"
    assert report["checks"]["peer_exists"] == "FAIL"
    assert any("peer is missing" in error for error in report["errors"])


def test_allowed_address_mismatch_still_fails(tmp_path, monkeypatch):
    peer = '0 name="pc-wg-day12" allowed-address=10.10.10.99/32 last-handshake=16s rx=1KiB tx=2KiB'

    report, _json_path, _html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer=peer,
        connectivity_ok=True,
    )

    assert report["overall_result"] == "FAIL"
    assert report["checks"]["peer_allowed_address"] == "FAIL"


def test_connectivity_fail_with_no_handshake_still_fails(tmp_path, monkeypatch):
    peer = '0 name="pc-wg-day12" allowed-address=10.10.10.2/32 rx=0 tx=0'

    report, _json_path, _html_path = run_day12_with_fake_state(
        tmp_path,
        monkeypatch,
        initial_peer=peer,
        connectivity_ok=False,
    )

    assert report["overall_result"] == "FAIL"
    assert report["checks"]["handshake_seen"] == "FAIL"
    assert report["checks"]["peer_rx_tx_nonzero"] == "FAIL"
    assert report["checks"]["final_vpn_connectivity"] == "FAIL"
    assert any("handshake" in error for error in report["errors"])


def test_tcp_5201_failure_is_warn_in_default_mode():
    checks = base_checks()
    checks["tcp_5201_reachable"] = "WARN"
    result, warnings, errors = day12.evaluate_day12_result(checks, run_iperf=False)

    assert result == "WARN"
    assert any("TCP 5201" in warning for warning in warnings)
    assert errors == []


def test_tcp_5201_failure_is_fail_in_run_iperf_mode():
    checks = base_checks()
    checks["tcp_5201_reachable"] = "FAIL"
    result, _warnings, errors = day12.evaluate_day12_result(checks, run_iperf=True)

    assert result == "FAIL"
    assert any("TCP 5201" in error for error in errors)


def test_subprocess_command_builders_use_list_arguments_and_not_shell_strings():
    commands = [
        day12.build_ping_command("192.168.88.1"),
        day12.build_tcp_test_command("192.168.88.254", 5201),
        day12.build_iperf_command("192.168.88.254", 40, 10, 4),
        day12.build_iperf_command("192.168.88.254", 40, 10, 4, reverse=True),
    ]

    assert all(isinstance(command, list) for command in commands)
    assert all(all(isinstance(part, str) for part in command) for command in commands)
    assert commands[-1][-1] == "-R"
    assert "-InformationLevel Quiet" in " ".join(commands[1])


def test_run_subprocess_uses_shell_false(monkeypatch):
    captured = {}

    class Completed:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(command, capture_output, text, timeout, shell):
        captured["command"] = command
        captured["shell"] = shell
        return Completed()

    monkeypatch.setattr(day12.subprocess, "run", fake_run)
    ok, stdout, stderr = day12.run_subprocess(["ping", "-n", "1", "192.168.88.1"], timeout=5)

    assert ok is True
    assert stdout == "ok"
    assert stderr == ""
    assert captured["command"] == ["ping", "-n", "1", "192.168.88.1"]
    assert captured["shell"] is False


def test_run_subprocess_with_countdown_uses_safe_runner(monkeypatch):
    captured = {}

    def fake_run(command, timeout):
        captured["command"] = command
        captured["timeout"] = timeout
        return True, "done", ""

    monkeypatch.setattr(day12, "run_subprocess", fake_run)

    ok, stdout, stderr = day12.run_subprocess_with_countdown(
        ["iperf3", "-c", "192.168.88.254"],
        timeout=5,
        progress_label="iperf3 test",
        progress_seconds=0,
    )

    assert ok is True
    assert stdout == "done"
    assert stderr == ""
    assert captured == {"command": ["iperf3", "-c", "192.168.88.254"], "timeout": 5}


def test_tcp_5201_check_accepts_quiet_true_output(monkeypatch):
    def fake_run(_command, timeout):
        assert timeout == 45
        return True, "True\r\n", ""

    monkeypatch.setattr(day12, "run_subprocess", fake_run)

    assert day12.run_tcp_5201_check(day12.build_tcp_test_command("192.168.88.254", 5201), True) == "PASS"


def test_tcp_5201_check_fails_quiet_false_output(monkeypatch):
    def fake_run(_command, timeout):
        assert timeout == 45
        return True, "False\r\n", ""

    monkeypatch.setattr(day12, "run_subprocess", fake_run)

    assert day12.run_tcp_5201_check(day12.build_tcp_test_command("192.168.88.254", 5201), True) == "FAIL"


def test_ssh_failure_result_logic_is_fail_for_missing_export():
    checks = base_checks()
    checks["client_config_generated"] = "FAIL"
    checks["config_file_written"] = "FAIL"

    result, _warnings, errors = day12.evaluate_day12_result(checks, run_iperf=False)

    assert result == "FAIL"
    assert any("client config export failed" in error for error in errors)
