import json

import pytest

import mikrotik_day33_vrrp_topology_dry_run as day33


def profile(**overrides):
    values = {
        "shared_lan_subnet": "192.168.88.0/24",
        "virtual_gateway_ip": "192.168.88.99/32",
        "parent_interface": "bridge",
        "vrrp_interface_name": "vrrp-lan",
        "vrid": 88,
        "primary_priority": 150,
        "backup_priority": 100,
        "devices": [
            {"name": "Hex-s-2025-lab01", "role": "primary", "lan_bridge_ip": "192.168.88.2/24"},
            {"name": "Hex-s-2025-lab02", "role": "backup", "lan_bridge_ip": "192.168.88.3/24"},
        ],
    }
    values.update(overrides)
    return values


def test_build_report_generates_primary_and_backup_preview_commands():
    report = day33.build_report(profile(), day33.DEFAULT_PROFILE)

    assert report["day"] == "Day33"
    assert report["safety_mode"] == "safe_dry_run"
    assert report["execution_status"] == "DRY-RUN ONLY - NOT EXECUTED"
    assert report["safety_guardrails"]["no_ssh_connection"] == "PASS"
    assert report["safety_guardrails"]["not_executed"] == "PASS"
    assert report["devices"][0]["execution_allowed"] is False
    assert report["devices"][0]["execution_status"] == "DRY-RUN ONLY - NOT EXECUTED"
    assert report["topology"]["virtual_gateway_cidr"] == "192.168.88.99/32"
    assert report["topology"]["primary_lan_bridge_ip"] == "192.168.88.2/24"
    assert report["topology"]["backup_lan_bridge_ip"] == "192.168.88.3/24"
    assert report["devices"][0]["configuration_preview_commands"] == [
        "/interface vrrp add name=vrrp-lan interface=bridge vrid=88 priority=150 preemption-mode=yes",
        "/ip address add address=192.168.88.99/32 interface=vrrp-lan",
    ]
    assert report["devices"][1]["configuration_preview_commands"][0].endswith("priority=100 preemption-mode=yes")
    assert report["devices"][1]["configuration_preview_commands"][1] == (
        "/ip address add address=192.168.88.99/32 interface=vrrp-lan"
    )


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"virtual_gateway_ip": "192.168.89.254"}, "virtual_gateway_ip"),
        ({"virtual_gateway_ip": "192.168.88.99/24"}, "192.168.88.99/32"),
        (
            {"devices": [
                {"name": "Hex-s-2025-lab01", "role": "primary", "lan_bridge_ip": "192.168.88.99/24"},
                {"name": "Hex-s-2025-lab02", "role": "backup", "lan_bridge_ip": "192.168.88.3/24"},
            ]},
            "physical LAN bridge IP",
        ),
        ({"primary_priority": 90, "backup_priority": 100}, "primary_priority"),
        ({"primary_priority": 120}, "primary_priority"),
        ({"backup_priority": 90}, "backup_priority"),
        ({"vrid": 33}, "vrid"),
        ({"devices": [{"name": "Hex-s-2025-lab01", "role": "primary"}]}, "primary and backup"),
    ],
)
def test_validate_profile_rejects_invalid_topology(overrides, message):
    with pytest.raises(ValueError, match=message):
        day33.validate_profile(profile(**overrides))


@pytest.mark.parametrize(
    "command",
    [
        "/interface remove 0",
        "/interface disable ether2",
        "/system reboot",
        "/system reset-configuration",
        "interface vrrp add name=vrrp-lan",
    ],
)
def test_preview_guard_blocks_destructive_or_malformed_commands(command):
    with pytest.raises(ValueError):
        day33.assert_preview_command_safe(command)


def test_run_writes_json_html_and_txt_reports(tmp_path):
    profile_path = tmp_path / "day33_profile.json"
    profile_path.write_text(json.dumps(profile()), encoding="utf-8")

    report, paths = day33.run(profile_path, tmp_path / "lab-summary")

    assert report["overall_status"] == "PASS"
    assert all(path.exists() for path in paths)
    assert paths[0].name == "day33_vrrp_topology_dry_run.json"
    data = json.loads(paths[0].read_text(encoding="utf-8"))
    assert data["devices"][0]["configuration_preview_commands"][0] == (
        "/interface vrrp add name=vrrp-lan interface=bridge vrid=88 priority=150 preemption-mode=yes"
    )
    text_report = paths[2].read_text(encoding="utf-8")
    assert "DRY-RUN ONLY" in text_report
    assert "NOT EXECUTED" in text_report
