import json

import mikrotik_day34_vrrp_staged_apply_plan as day34


def profile(**overrides):
    values = {
        "shared_lan_subnet": "192.168.88.0/24",
        "virtual_gateway_ip": "192.168.88.99/32",
        "parent_interface": "bridge",
        "vrrp_interface_name": "vrrp-lan",
        "vrid": 88,
        "primary_priority": 150,
        "backup_priority": 100,
        "required_evidence": [
            "reports/lab-summary/day32_vrrp_readonly_precheck.json",
            "reports/lab-summary/day33_vrrp_topology_dry_run.json",
        ],
        "devices": [
            {"name": "Hex-s-2025-lab01", "role": "primary", "lan_bridge_ip": "192.168.88.2/24"},
            {"name": "Hex-s-2025-lab02", "role": "backup", "lan_bridge_ip": "192.168.88.3/24"},
        ],
    }
    values.update(overrides)
    return values


def test_build_report_blocks_apply_when_required_evidence_is_missing(tmp_path):
    report = day34.build_report(profile(), day34.DEFAULT_PROFILE, tmp_path)

    assert report["day"] == "Day34"
    assert report["safety_mode"] == "blocked_guarded_live_plan"
    assert report["execution_status"] == "BLOCKED - PLAN ONLY - NOT EXECUTED"
    assert report["overall_status"] == "BLOCKED"
    assert report["safety_gate"]["live_execution"] == "BLOCKED"
    assert report["safety_gate"]["manual_operator_confirmation"] == "BLOCKED"
    assert report["stages"][0]["status"] == "BLOCKED"
    assert all(stage["execution_allowed"] is False for stage in report["stages"])


def test_build_report_orders_backup_before_primary_when_evidence_exists(tmp_path):
    for path in day34.REQUIRED_EVIDENCE:
        full_path = tmp_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("{}", encoding="utf-8")

    report = day34.build_report(profile(), day34.DEFAULT_PROFILE, tmp_path)

    assert report["overall_status"] == "PASS"
    assert report["stages"][0]["status"] == "PASS"
    assert report["stages"][1]["device"]["device_name"] == "Hex-s-2025-lab02"
    assert report["stages"][1]["device"]["planned_apply_commands"][0].endswith("priority=100 preemption-mode=yes")
    assert report["stages"][2]["device"]["device_name"] == "Hex-s-2025-lab01"
    assert report["stages"][2]["device"]["planned_apply_commands"][0].endswith("priority=150 preemption-mode=yes")
    assert report["stages"][1]["device"]["rollback_preview_commands"]


def test_run_writes_json_html_and_txt_reports(tmp_path):
    profile_path = tmp_path / "day34_profile.json"
    profile_path.write_text(json.dumps(profile()), encoding="utf-8")

    report, paths = day34.run(profile_path, tmp_path / "lab-summary", tmp_path)

    assert report["overall_status"] == "BLOCKED"
    assert all(path.exists() for path in paths)
    assert paths[0].name == "day34_vrrp_staged_apply_plan.json"
    data = json.loads(paths[0].read_text(encoding="utf-8"))
    assert data["execution_status"] == "BLOCKED - PLAN ONLY - NOT EXECUTED"
    assert "Safety Gate" in paths[1].read_text(encoding="utf-8")
    assert "PLAN ONLY" in paths[2].read_text(encoding="utf-8")
