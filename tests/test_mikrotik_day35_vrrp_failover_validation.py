import json
from types import SimpleNamespace

import pytest

import mikrotik_day35_vrrp_failover_validation as day35
from mikrotik_day2_auto_setup import Day2Config


def profile(**overrides):
    values = {
        "shared_lan_subnet": "192.168.88.0/24",
        "lab01_lan_ip": "192.168.88.2",
        "lab02_lan_ip": "192.168.88.3",
        "vrrp_virtual_ip": "192.168.88.99",
        "automation_pc_lan_ip": "192.168.88.100",
        "lan_server_ip": "192.168.88.254",
        "windows_default_route": "192.168.0.114",
        "vrid": 88,
        "virtual_mac": "00:00:5E:00:01:58",
        "lab01_priority": 150,
        "lab02_priority": 100,
        "lab01_state_before_failover": "MASTER",
        "lab02_state_before_failover": "BACKUP",
        "devices": [
            {"name": "Hex-s-2025-lab01", "role": "primary"},
            {"name": "Hex-s-2025-lab02", "role": "backup"},
        ],
    }
    values.update(overrides)
    return values


def make_config(name="Hex-s-2025-lab01"):
    return Day2Config(
        host="192.168.88.2",
        port=22,
        username="admin",
        password="secret",
        device_name=name,
        target_routeros_version="7.22.3",
        enable_apply_config=False,
        enable_backup=False,
        enable_report=True,
        timezone="Asia/Taipei",
        disable_services=[],
    )


def device(role, state, reachable=True, output=""):
    name = "Hex-s-2025-lab01" if role == "primary" else "Hex-s-2025-lab02"
    config = make_config(name)
    return day35.build_device_observation(
        config,
        role,
        reachable,
        {
            "identity": f"name: {name}",
            "vrrp": f"0 interface=vrrp-lan state={state.lower()} priority=150 vrid=88 virtual-mac-address=00:00:5E:00:01:58",
            "ip_addresses": "0 address=192.168.88.99/32 interface=vrrp-lan",
            "firewall_nat": output,
        },
        [],
        list(day35.READONLY_COMMANDS.values()),
    )


def pings(ok=True):
    status = "PASS" if ok else "FAIL"
    return [
        {"label": "lab01_lan_ip", "reachable": ok, "status": status},
        {"label": "lab02_lan_ip", "reachable": ok, "status": status},
        {"label": "vrrp_virtual_ip", "reachable": ok, "status": status},
        {"label": "lan_server_ip", "reachable": ok, "status": status},
    ]


def test_safety_guard_allows_required_readonly_commands():
    for command in day35.READONLY_COMMANDS.values():
        day35.assert_readonly_observation_command(command)


@pytest.mark.parametrize(
    "command",
    [
        "/interface disable ether2",
        "/interface enable ether2",
        "/ip firewall nat add chain=srcnat action=masquerade",
        "/ip firewall filter set 0 disabled=no",
        "/ip address add address=192.168.88.99/32 interface=vrrp-lan",
        "/ip address set 0 address=192.168.88.99/32",
        "/interface vrrp set 0 priority=200",
        "/interface vrrp set 0 vrid=99",
        "/system reboot",
        "/system reset-configuration",
    ],
)
def test_safety_guard_blocks_destructive_day35_commands(command):
    with pytest.raises(ValueError):
        day35.assert_readonly_observation_command(command)


def test_collect_outputs_fails_before_command_runner_when_command_list_contains_unsafe_command(monkeypatch):
    commands = dict(day35.READONLY_COMMANDS)
    commands["unsafe"] = "/interface vrrp set 0 priority=1"
    calls = []
    monkeypatch.setattr(day35, "READONLY_COMMANDS", commands)

    with pytest.raises(ValueError):
        day35.collect_readonly_outputs(object(), command_runner=lambda _client, command: calls.append(command) or "")

    assert calls == []


def test_validate_profile_contains_day35_expected_topology():
    topology = day35.validate_profile(profile())

    assert topology["lab01_lan_ip"] == "192.168.88.2"
    assert topology["lab02_lan_ip"] == "192.168.88.3"
    assert topology["vrrp_virtual_ip"] == "192.168.88.99"
    assert topology["automation_pc_lan_ip"] == "192.168.88.100"
    assert topology["lan_server_ip"] == "192.168.88.254"
    assert topology["vrid"] == 88
    assert topology["virtual_mac"] == "00:00:5E:00:01:58"


def test_build_ping_command_uses_source_specific_windows_ping_shape(monkeypatch):
    monkeypatch.setattr(day35.os, "name", "nt")

    command = day35.build_ping_command("192.168.88.100", "192.168.88.99")

    assert command[:3] == ["ping", "-S", "192.168.88.100"]
    assert "192.168.88.99" in command


def test_report_status_pass_when_baseline_failover_and_recovery_match():
    prof = profile()
    topology = day35.validate_profile(prof)
    phases = [
        day35.build_phase("baseline", "Baseline", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
        day35.build_phase("failover", "Failover", topology, [device("primary", ""), device("backup", "MASTER")], pings()),
        day35.build_phase("recovery", "Recovery", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
    ]

    report = day35.build_report(prof, day35.DEFAULT_PROFILE, phases)

    assert report["overall_status"] == "PASS"
    assert report["safety_mode"] == "controlled_failover_observation"


def test_report_status_pass_with_notes_when_recovery_preemption_differs():
    prof = profile()
    topology = day35.validate_profile(prof)
    phases = [
        day35.build_phase("baseline", "Baseline", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
        day35.build_phase("failover", "Failover", topology, [device("primary", ""), device("backup", "MASTER")], pings()),
        day35.build_phase("recovery", "Recovery", topology, [device("primary", "BACKUP"), device("backup", "MASTER")], pings()),
    ]

    report = day35.build_report(prof, day35.DEFAULT_PROFILE, phases)

    assert report["overall_status"] == "PASS_WITH_NOTES"
    recovery_checks = phases[2]["checks"]
    assert recovery_checks["lab01_preemption_back_to_master_observed"] == "PASS_WITH_NOTES"


def test_report_status_fails_when_lab02_does_not_become_master():
    prof = profile()
    topology = day35.validate_profile(prof)
    phases = [
        day35.build_phase("baseline", "Baseline", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
        day35.build_phase("failover", "Failover", topology, [device("primary", ""), device("backup", "BACKUP")], pings()),
        day35.build_phase("recovery", "Recovery", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
    ]

    report = day35.build_report(prof, day35.DEFAULT_PROFILE, phases)

    assert report["overall_status"] == "FAIL"
    assert phases[1]["checks"]["lab02_master_after_failover"] == "FAIL"


def test_write_reports_redacts_sensitive_command_output(tmp_path):
    prof = profile(notes=["password=do-not-keep"])
    topology = day35.validate_profile(prof)
    sensitive_output = "private-key=abc123 password: hunter2"
    phases = [
        day35.build_phase("baseline", "Baseline", topology, [device("primary", "MASTER", output=sensitive_output), device("backup", "BACKUP")], pings()),
        day35.build_phase("failover", "Failover", topology, [device("primary", ""), device("backup", "MASTER")], pings()),
        day35.build_phase("recovery", "Recovery", topology, [device("primary", "MASTER"), device("backup", "BACKUP")], pings()),
    ]
    report = day35.build_report(prof, day35.DEFAULT_PROFILE, phases)

    json_path, html_path, txt_path = day35.write_reports(report, tmp_path)

    report_text = json_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    txt = txt_path.read_text(encoding="utf-8")
    assert "abc123" not in report_text
    assert "hunter2" not in report_text
    assert "do-not-keep" not in report_text
    assert "abc123" not in html
    assert "hunter2" not in txt
    assert "<REDACTED>" in report_text


def test_run_can_generate_reports_with_fakes_without_destructive_commands(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    profile_path = tmp_path / "day35_profile.json"
    config_path.write_text(
        json.dumps(
            {
                "host": "192.168.88.2",
                "username": "admin",
                "password": "",
                "device_name": "Hex-s-2025-lab01",
                "devices": {
                    "Hex-s-2025-lab01": {"host": "192.168.88.2", "username": "admin", "password": ""},
                    "Hex-s-2025-lab02": {"host": "192.168.88.3", "username": "admin", "password": ""},
                },
            }
        ),
        encoding="utf-8",
    )
    profile_path.write_text(json.dumps(profile()), encoding="utf-8")
    phase_states = iter(
        [
            [device("primary", "MASTER"), device("backup", "BACKUP")],
            [device("primary", ""), device("backup", "MASTER")],
            [device("primary", "MASTER"), device("backup", "BACKUP")],
        ]
    )
    monkeypatch.setattr(day35, "collect_router_observations", lambda *_args, **_kwargs: next(phase_states))

    def fake_ping(command):
        assert "-S" in command or "-I" in command
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    report, paths = day35.run(
        config_path,
        profile_path,
        tmp_path / "lab-summary",
        input_func=lambda _prompt: "",
        ping_runner=fake_ping,
    )

    assert report["overall_status"] == "PASS"
    assert all(path.exists() for path in paths)
    assert all(
        not any(keyword in command for keyword in (" disable ", " enable ", " reboot", " reset", " set ", " remove "))
        for command in report["readonly_commands"]
    )
