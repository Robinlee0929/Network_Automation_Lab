import json

import mikrotik_day4_multi_device_baseline as day4
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
        "expected_wan_interface": "ether1",
        "expected_wan_mode": "dhcp",
        "expected_lan_ip_cidr": "192.168.88.1/24",
    }
    values.update(overrides)
    return Day2Config(**values)


OUTPUTS = {
    "identity": "name: Hex-s-2025-lab01",
    "package": "0 routeros 7.22.3",
    "routerboard": "current-firmware: 7.22.3\nupgrade-firmware: 7.22.3",
    "dhcp_client": "0 interface=ether1 status=bound address=10.0.0.10",
    "ip_address": "0 address=10.0.0.10/24 interface=ether1\n1 address=192.168.88.1/24 interface=bridge",
    "services": "0 X ftp 21\n1 ssh 22\n2 X telnet 23",
}


def test_evaluate_device_outputs_passes_all_required_checks():
    checks = day4.evaluate_device_outputs(make_config(), OUTPUTS, [])
    statuses = {check["name"]: check["result"] for check in checks}

    assert statuses["Device identity"] == "PASS"
    assert statuses["RouterOS version"] == "PASS"
    assert statuses["RouterBOARD current firmware"] == "PASS"
    assert statuses["RouterBOARD upgrade firmware"] == "PASS"
    assert statuses["WAN DHCP client status"] == "PASS"
    assert statuses["LAN bridge IP"] == "PASS"
    assert statuses["SSH service status"] == "PASS"


def test_evaluate_device_outputs_fails_lan_ip_mismatch():
    config = make_config(expected_lan_ip_cidr="192.168.89.1/24")
    checks = day4.evaluate_device_outputs(config, OUTPUTS, [])
    lan_check = [check for check in checks if check["name"] == "LAN bridge IP"][0]

    assert lan_check["expected"] == "192.168.89.1/24"
    assert lan_check["actual"] == "192.168.88.1/24"
    assert lan_check["result"] == "FAIL"


def test_build_device_report_fails_when_required_check_fails():
    checks = [
        day4.make_check("SSH connection", "authenticated", "authenticated", "PASS", "ok"),
        day4.make_check("LAN bridge IP", "192.168.89.1/24", "192.168.88.1/24", "FAIL", "mismatch"),
    ]

    report = day4.build_device_report(make_config(), checks, "2026-05-26T12:00:00")

    assert report["overall_result"] == "FAIL"


def test_load_day4_device_configs_reads_two_profiles(tmp_path, monkeypatch):
    monkeypatch.setattr(day4, "REPORT_ROOT", tmp_path / "reports")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.254",
                "username": "admin",
                "password": "",
                "device_name": "Hex-s-2025-lab01",
                "devices": {
                    "Hex-s-2025-lab01": {
                        "host": "192.168.88.1",
                        "ssh_port": 22,
                        "username": "admin",
                        "password": "",
                        "expected": {
                            "wan_interface": "ether1",
                            "wan_mode": "dhcp",
                            "expected_lan_bridge_ip": "192.168.88.1/24",
                        },
                    },
                    "Hex-s-2025-lab02": {
                        "host": "192.168.89.1",
                        "ssh_port": 22,
                        "username": "admin",
                        "password": "",
                        "expected": {
                            "wan_interface": "ether1",
                            "wan_mode": "dhcp",
                            "expected_lan_bridge_ip": "192.168.89.1/24",
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    configs = day4.load_day4_device_configs(config_path)
    by_name = {config.device_name: config for config in configs}

    assert by_name["Hex-s-2025-lab01"].host == "192.168.88.1"
    assert by_name["Hex-s-2025-lab01"].expected_lan_ip_cidr == "192.168.88.1/24"
    assert by_name["Hex-s-2025-lab02"].host == "192.168.89.1"
    assert by_name["Hex-s-2025-lab02"].expected_lan_ip_cidr == "192.168.89.1/24"


def test_load_day4_device_configs_prefers_day4_wan_hosts(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.254",
                "username": "admin",
                "password": "",
                "device_name": "Hex-s-2025-lab01",
                "devices": {
                    "Hex-s-2025-lab01": {
                        "host": "192.168.88.1",
                        "day4_host": "192.168.0.199",
                        "expected": {
                            "expected_lan_bridge_ip": "192.168.88.1/24",
                        },
                    },
                    "Hex-s-2025-lab02": {
                        "host": "192.168.89.1",
                        "day4": {
                            "wan_host": "192.168.0.113",
                            "ssh_port": 2222,
                        },
                        "expected": {
                            "expected_lan_bridge_ip": "192.168.89.1/24",
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    configs = day4.load_day4_device_configs(config_path)
    by_name = {config.device_name: config for config in configs}

    assert by_name["Hex-s-2025-lab01"].host == "192.168.0.199"
    assert by_name["Hex-s-2025-lab01"].port == 22
    assert by_name["Hex-s-2025-lab02"].host == "192.168.0.113"
    assert by_name["Hex-s-2025-lab02"].port == 2222


def test_load_day4_device_configs_uses_precheck_wan_ip_when_no_day4_host(
    tmp_path,
    monkeypatch,
):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.254",
                "username": "admin",
                "password": "",
                "device_name": "Hex-s-2025-lab01",
                "devices": {
                    "Hex-s-2025-lab01": {
                        "host": "192.168.88.1",
                        "expected": {
                            "expected_lan_bridge_ip": "192.168.88.1/24",
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    report_dir = tmp_path / "reports" / "Hex-s-2025-lab01"
    report_dir.mkdir(parents=True)
    (report_dir / "day4_precheck_wan_ssh.json").write_text(
        json.dumps({"wan_dhcp_ip": "192.168.0.199/24"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(day4, "REPORT_ROOT", tmp_path / "reports")

    configs = day4.load_day4_device_configs(config_path)

    assert configs[0].host == "192.168.0.199"


def test_day4_profile_host_wins_over_precheck_report(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.254",
                "username": "admin",
                "password": "",
                "device_name": "Hex-s-2025-lab01",
                "devices": {
                    "Hex-s-2025-lab01": {
                        "host": "192.168.88.1",
                        "day4_host": "192.168.0.200",
                        "expected": {
                            "expected_lan_bridge_ip": "192.168.88.1/24",
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    report_dir = tmp_path / "reports" / "Hex-s-2025-lab01"
    report_dir.mkdir(parents=True)
    (report_dir / "day4_precheck_wan_ssh.json").write_text(
        json.dumps({"wan_dhcp_ip": "192.168.0.199/24"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(day4, "REPORT_ROOT", tmp_path / "reports")

    configs = day4.load_day4_device_configs(config_path)

    assert configs[0].host == "192.168.0.200"


def test_prompt_device_host_overrides_default(monkeypatch):
    config = make_config(host="192.168.0.199")
    monkeypatch.setattr("builtins.input", lambda _prompt: "192.168.0.113")

    day4.prompt_device_host(config)

    assert config.host == "192.168.0.113"


def test_prompt_device_host_keeps_default_on_enter(monkeypatch):
    config = make_config(host="192.168.0.199")
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    day4.prompt_device_host(config)

    assert config.host == "192.168.0.199"


def test_write_device_and_summary_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(day4, "REPORT_ROOT", tmp_path)
    report = day4.build_device_report(
        make_config(),
        [
            day4.make_check(
                "SSH connection",
                "authenticated",
                "authenticated",
                "PASS",
                "ok",
            )
        ],
        "2026-05-26T12:00:00",
    )

    json_path, txt_path, html_path = day4.write_device_report(report)
    summary = day4.build_summary_report([report])
    summary_json, summary_txt, summary_html = day4.write_summary_report(summary)

    assert json_path == tmp_path / "Hex-s-2025-lab01" / "day4_baseline_validation.json"
    assert txt_path.exists()
    assert html_path == tmp_path / "Hex-s-2025-lab01" / "day4_baseline_validation.html"
    assert html_path.exists()
    assert summary_json == tmp_path / "day4_summary_report.json"
    assert summary_txt.exists()
    assert summary_html == tmp_path / "day4_summary_report.html"
    assert summary_html.exists()
