import json

import pytest

import mikrotik_day2_auto_setup as day2


PACKAGE_OUTPUT = """
Columns: NAME, VERSION
# NAME      VERSION
0 routeros  7.22.3
"""


ROUTERBOARD_OUTPUT = """
       routerboard: yes
        board-name: hEX S
             model: E60iUGS
     serial-number: ABC123
     current-firmware: 7.22.3
     upgrade-firmware: 7.22.3
     factory-firmware: 7.16.2
"""


RESOURCE_OUTPUT = """
                   uptime: 1h2m3s
                  version: 7.22.3 (stable)
               build-time: 2026-05-20 09:11:22
         factory-software: 7.16.2
              free-memory: 178.0MiB
             total-memory: 256.0MiB
                      cpu: ARM64
                cpu-count: 4
        architecture-name: arm64
               board-name: hEX S
"""


def test_parse_package_version_from_routeros_table():
    assert day2.parse_package_version(PACKAGE_OUTPUT) == "7.22.3"


def test_parse_routerboard_firmware_fields():
    firmware = day2.parse_routerboard_firmware(ROUTERBOARD_OUTPUT)

    assert firmware["current-firmware"] == "7.22.3"
    assert firmware["upgrade-firmware"] == "7.22.3"
    assert firmware["factory-firmware"] == "7.16.2"


def test_parse_system_resource_fields():
    resource = day2.parse_system_resource(RESOURCE_OUTPUT)

    assert resource["version"] == "7.22.3 (stable)"
    assert resource["board-name"] == "hEX S"
    assert resource["architecture-name"] == "arm64"
    assert resource["cpu"] == "ARM64"
    assert resource["cpu-count"] == "4"
    assert resource["total-memory"] == "256.0MiB"
    assert resource["free-memory"] == "178.0MiB"
    assert resource["uptime"] == "1h2m3s"


def test_check_version_gate_passes_when_versions_match():
    result, package_latest = day2.check_version_gate("7.22.3", "7.22.3")

    assert result == "PASS"
    assert package_latest is True


def test_check_version_gate_warns_when_versions_differ():
    result, package_latest = day2.check_version_gate("7.22.2", "7.22.3")

    assert result == "WARNING"
    assert package_latest is False


def test_check_version_gate_fails_when_version_missing():
    result, package_latest = day2.check_version_gate("", "7.22.3")

    assert result == "FAIL"
    assert package_latest is False


def test_manual_update_steps_explain_version_mismatch_without_auto_upgrade():
    steps = day2.build_manual_update_steps("7.22.2", "7.22.3")
    text = "\n".join(steps)

    assert "7.22.2" in text
    assert "7.22.3" in text
    assert "/system package update check-for-updates" in text
    assert "run mikrotik_day2_auto_setup.py again in dry-run mode" in text
    assert "/system reboot" not in text


def test_load_config_reads_day2_fields(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
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
                "disable_services": ["ftp", "telnet", "www"],
            }
        ),
        encoding="utf-8",
    )

    config = day2.load_config(config_path)

    assert config.host == "192.168.88.1"
    assert config.port == 22
    assert config.username == "admin"
    assert config.password == "secret"
    assert config.device_name == "Hex-s-2025-lab01"
    assert config.target_routeros_version == "7.22.3"
    assert config.enable_apply_config is False
    assert config.enable_backup is True
    assert config.enable_report is True
    assert config.timezone == "Asia/Taipei"
    assert config.disable_services == ["ftp", "telnet", "www"]


def test_load_config_supports_legacy_host_keys(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "router_ip": "192.168.88.2",
                "ssh_port": 2222,
                "password": "secret",
            }
        ),
        encoding="utf-8",
    )

    config = day2.load_config(config_path)

    assert config.host == "192.168.88.2"
    assert config.port == 2222
    assert config.enable_apply_config is False


def test_make_empty_report_has_required_fields():
    config = day2.Day2Config(
        host="192.168.88.1",
        port=22,
        username="admin",
        password="secret",
        device_name="Hex-s-2025-lab01",
        target_routeros_version="7.22.3",
        enable_apply_config=False,
        enable_backup=True,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=["ftp"],
    )

    report = day2.make_empty_report(config)

    for field in day2.REPORT_FIELDS:
        assert field in report
    assert "password" not in report


def test_build_apply_commands_uses_config_and_does_not_disable_ssh():
    config = day2.Day2Config(
        host="192.168.88.1",
        port=22,
        username="admin",
        password="secret",
        device_name="Hex-s-2025-lab01",
        target_routeros_version="7.22.3",
        enable_apply_config=True,
        enable_backup=True,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=["ftp", "telnet", "www"],
    )

    commands = day2.build_apply_commands(config)

    assert '/system identity set name="Hex-s-2025-lab01"' in commands
    assert '/system clock set time-zone-name="Asia/Taipei"' in commands
    assert "/system ntp client set enabled=yes" in commands
    assert '/ip service disable [find name="ftp"]' in commands
    assert all('name="ssh"' not in command for command in commands)


def test_build_apply_commands_rejects_ssh_disable():
    config = day2.Day2Config(
        host="192.168.88.1",
        port=22,
        username="admin",
        password="secret",
        device_name="Hex-s-2025-lab01",
        target_routeros_version="7.22.3",
        enable_apply_config=True,
        enable_backup=True,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=["ssh"],
    )

    with pytest.raises(ValueError, match="ssh"):
        day2.build_apply_commands(config)


def test_build_text_report_omits_password_and_uses_plain_format(tmp_path):
    config = day2.Day2Config(
        host="192.168.88.1",
        port=22,
        username="admin",
        password="super-secret",
        device_name="Hex-s-2025-lab01",
        target_routeros_version="7.22.3",
        enable_apply_config=False,
        enable_backup=True,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=[],
    )
    report = day2.make_empty_report(config)
    report["commands_executed"] = ["/system resource print"]
    report["manual_update_steps"] = day2.build_manual_update_steps("7.22.2", "7.22.3")

    text_report = day2.build_text_report(
        report,
        tmp_path / "day2_auto_setup_report.json",
        tmp_path / "day2_auto_setup_report.txt",
    )

    assert "super-secret" not in text_report
    assert "MikroTik Day 2 Auto Setup" in text_report
    assert "Commands Executed" in text_report
    assert "Manual RouterOS Update Guidance" in text_report
    assert "/system package update check-for-updates" in text_report
    assert "/system resource print" in text_report
    assert "```" not in text_report


def test_write_reports_creates_json_and_txt(tmp_path, monkeypatch):
    monkeypatch.setattr(day2, "REPORT_DIR", tmp_path / "reports")
    config = day2.Day2Config(
        host="192.168.88.1",
        port=22,
        username="admin",
        password="super-secret",
        device_name="Hex-s-2025-lab01",
        target_routeros_version="7.22.3",
        enable_apply_config=False,
        enable_backup=True,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=[],
    )
    report = day2.make_empty_report(config)

    json_path, txt_path = day2.write_reports(report)

    assert json_path.name == "day2_auto_setup_report.json"
    assert txt_path.name == "day2_auto_setup_report.txt"
    assert json_path.exists()
    assert txt_path.exists()
