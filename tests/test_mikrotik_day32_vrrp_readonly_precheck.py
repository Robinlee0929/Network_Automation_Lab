import json

import pytest

import mikrotik_day32_vrrp_readonly_precheck as day32
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
        "enable_backup": False,
        "enable_report": True,
        "timezone": "Asia/Taipei",
        "disable_services": [],
    }
    values.update(overrides)
    return Day2Config(**values)


def test_safety_guard_allows_readonly_commands():
    for command in [
        "/system identity print",
        "/interface vrrp print detail",
        "/ip address print detail",
        "/export terse",
    ]:
        day32.assert_readonly_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "/interface vrrp add interface=bridge vrid=1",
        "/interface vrrp set 0 priority=120",
        "/interface vrrp remove 0",
        "/interface disable ether2",
        "/interface enable ether2",
        "/system reboot",
        "/system reset-configuration",
    ],
)
def test_safety_guard_blocks_dangerous_commands(command):
    with pytest.raises(ValueError):
        day32.assert_readonly_command(command)


def test_parse_vrrp_summary_keeps_vrid_separate_from_virtual_ip():
    summary = day32.parse_vrrp_summary(
        "0 interface=bridge state=master priority=120 vrid=1",
        "",
    )

    assert summary["configured"] is True
    assert summary["vrid"] == "1"
    assert summary["virtual_ip"] == ""


def test_parse_vrrp_summary_reads_virtual_address_without_using_vrid():
    summary = day32.parse_vrrp_summary(
        "0 interface=bridge state=master priority=120 vrid=1 virtual-address=192.168.88.254",
        "",
    )

    assert summary["configured"] is True
    assert summary["vrid"] == "1"
    assert summary["virtual_ip"] == "192.168.88.254"


def test_write_reports_creates_json_html_and_txt(tmp_path):
    outputs = {
        "identity": "name: Hex-s-2025-lab01",
        "resource": "version: 7.22.3 board-name: hEX S",
        "vrrp": "",
        "ip_addresses": "0 address=192.168.88.1/24 interface=bridge",
        "routes": "0 dst-address=0.0.0.0/0 gateway=192.168.0.1",
        "bridges": "0 name=bridge protocol-mode=rstp",
        "bridge_ports": "0 interface=ether2 bridge=bridge",
    }
    device = day32.build_device_entry(
        make_config(),
        True,
        outputs,
        [],
        list(day32.READONLY_COMMANDS.values()),
    )
    report = day32.build_report([device])

    json_path, html_path, txt_path = day32.write_reports(report, tmp_path)

    assert json_path.exists()
    assert html_path.exists()
    assert txt_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["day"] == "Day32"
    assert data["safety_mode"] == "read-only"
    assert data["allowed_operations"] == day32.ALLOWED_OPERATIONS
    assert data["forbidden_operations"] == day32.FORBIDDEN_OPERATIONS
    assert data["devices"][0]["vrrp_configured"] is False
    assert day32.VRRP_NOT_CONFIGURED_NOTE in data["devices"][0]["notes"]


def test_collect_outputs_fails_fast_when_command_list_contains_unsafe_command(monkeypatch):
    commands = dict(day32.READONLY_COMMANDS)
    commands["unsafe"] = "/interface vrrp add interface=bridge"
    monkeypatch.setattr(day32, "READONLY_COMMANDS", commands)

    with pytest.raises(ValueError):
        day32.collect_readonly_outputs(object(), command_runner=lambda _client, _command: "")


def test_run_can_generate_reports_without_real_credentials(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    profile_path = tmp_path / "day32_profile.json"
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
                        "username": "admin",
                        "password": "",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    profile_path.write_text(
        json.dumps({"devices": [{"name": "Hex-s-2025-lab01", "role": "primary_candidate"}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        day32,
        "run_device_precheck",
        lambda config: day32.build_device_entry(
            config,
            True,
            {
                "identity": "name: Hex-s-2025-lab01",
                "resource": "version: 7.22.3",
                "vrrp": "0 interface=bridge state=master priority=120",
                "ip_addresses": "0 address=192.168.88.1/24 interface=bridge",
                "routes": "",
                "bridges": "",
                "bridge_ports": "",
            },
            [],
            list(day32.READONLY_COMMANDS.values()),
        ),
    )

    report, paths = day32.run(config_path, profile_path, tmp_path / "lab-summary")

    assert report["overall_status"] == "PASS"
    assert all(path.exists() for path in paths)
    assert paths[0].name == "day32_vrrp_readonly_precheck.json"
