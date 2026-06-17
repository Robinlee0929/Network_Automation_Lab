import json
from pathlib import Path

import network_lab
import phase_2a_08_jobs_catalog_ui_readiness_planning_pack as pack


def _jobs_by_type(report):
    return {entry["job_type"]: entry for entry in report["jobs_catalog"]}


def test_agents_md_status_is_recorded_and_file_was_not_modified_by_pack():
    report = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    agents_path = Path("AGENTS.md")

    assert agents_path.exists()
    assert "Phase 2A-08 Jobs Catalog" not in agents_path.read_text(encoding="utf-8")
    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }


def test_catalog_includes_all_required_job_types_and_is_not_vrrp_only():
    report = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    jobs = _jobs_by_type(report)

    assert report["phase"] == "2A-08"
    assert report["status"] == "PASS"
    assert report["summary"]["catalog_entries"] == 6
    assert set(jobs) == set(pack.REQUIRED_JOB_TYPES)
    assert len(jobs) > 1
    assert set(jobs) != {"vrrp_validation"}
    assert jobs["vrrp_validation"]["ui_card_summary"] == "Local mock VRRP evidence card."
    assert report["phase_2a_07_source"]["artifact_mapping_reused"] is True


def test_all_catalog_entries_are_planning_only_ui_ready_and_safety_locked():
    report = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()

    assert report["summary"]["planning_only_entries"] == 6
    assert report["summary"]["dry_run_entries"] == 5
    assert report["summary"]["blocked_entries"] == 1
    assert report["summary"]["ui_ready_entries"] == 6
    assert report["summary"]["executable_entries"] == 0
    assert report["summary"]["next_phase_allowed_count"] == 0

    for entry in report["jobs_catalog"]:
        for field in pack.UI_READY_FIELDS:
            assert field in entry
        assert entry["planning_only"] is True
        assert entry["next_phase_allowed"] is False
        assert entry["ui_card"]["ui_readiness_state"] == {
            "future_route": "/network/jobs",
            "can_be_consumed_by_future_ui": True,
            "executable_now": False,
        }
        assert set(entry["forbidden_capabilities_confirmed"]) == set(pack.FORBIDDEN_CAPABILITIES)
        assert all(value is False for value in entry["forbidden_capabilities_confirmed"].values())

    for flag_name, expected in pack.SAFETY_FLAGS.items():
        assert report[flag_name] is expected


def test_backup_plan_and_blocked_change_request_remain_non_executing():
    report = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    jobs = _jobs_by_type(report)
    backup = jobs["backup_config_plan"]
    blocked = jobs["blocked_config_change_request"]

    assert backup["supported_status"] == "planning_only"
    assert backup["dry_run"] is True
    assert backup["planning_only"] is True
    assert backup["requires_approval"] is True
    assert "Real backup" in backup["blocked_reason"]
    assert backup["forbidden_capabilities_confirmed"]["real_backup"] is False

    assert blocked["supported_status"] == "blocked"
    assert blocked["dry_run"] is False
    assert blocked["planning_only"] is True
    assert blocked["requires_approval"] is True
    assert "Configuration-changing jobs are blocked" in blocked["blocked_reason"]
    assert blocked["forbidden_capabilities_confirmed"]["config_change"] is False
    assert blocked["forbidden_capabilities_confirmed"]["command_execution"] is False


def test_validator_detects_scope_safety_and_ui_regressions():
    report = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    report["jobs_catalog"] = [entry for entry in report["jobs_catalog"] if entry["job_type"] == "vrrp_validation"]
    report["jobs_catalog"][0]["next_phase_allowed"] = True
    report["jobs_catalog"][0]["ui_card"]["ui_readiness_state"]["executable_now"] = True
    report["jobs_catalog"][0]["forbidden_capabilities_confirmed"]["ssh"] = True
    report["ssh_enabled"] = True

    validation = pack.validate_phase_2a_08_report(report)

    assert validation["valid"] is False
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]
    assert "SAFETY_FLAG_NOT_FALSE:ssh_enabled" in validation["errors"]
    assert any(error.startswith("NEXT_PHASE_ALLOWED_NOT_FALSE") for error in validation["errors"])
    assert any(error.startswith("FORBIDDEN_CAPABILITIES_ENABLED") for error in validation["errors"])
    assert any(error.startswith("UI_EXECUTABLE_NOW_NOT_FALSE") for error in validation["errors"])


def test_json_output_is_deterministic_and_ui_ready():
    report_a = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()
    report_b = pack.build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report()

    encoded_a = json.dumps(report_a, sort_keys=True, separators=(",", ":"))
    encoded_b = json.dumps(report_b, sort_keys=True, separators=(",", ":"))

    assert encoded_a == encoded_b
    assert report_a["validation"]["valid"] is True
    assert report_a["ui_schema"]["future_route"] == "/network/jobs"
    assert report_a["ui_schema"]["deterministic_json"] is True
    assert "status_badge" in report_a["jobs_catalog"][0]["ui_card"]
    assert "safety_lock_flags" in report_a["jobs_catalog"][0]["ui_card"]


def test_cli_writes_jobs_catalog_pack_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-08 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-08 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-08 Jobs Catalog / UI Readiness Planning Pack" in output
    assert "Task name: phase2a-08-jobs-catalog-ui-readiness-planning-pack" in output
    assert "Catalog entries: 6" in output
    assert "UI-ready entries: 6" in output
    assert "Executable entries: 0" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "broker_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "netconf_enabled: false" in output
    assert "restconf_enabled: false" in output
    assert "live_device_access_enabled: false" in output
    assert "provider_api_model_enabled: false" in output
    assert "secrets_enabled: false" in output
    assert "real_backup_enabled: false" in output
    assert "real_vrrp_test_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] PHASE_2A_08_JOBS_CATALOG_UI_READINESS_PLANNING_PACK_READY" in output
    assert (tmp_path / pack.REPORT_JSON).exists()
    assert (tmp_path / pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == pack.TASK_NAME)

    assert task["task_id"] == "phase_2a_08_jobs_catalog_ui_readiness_planning_pack"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert pack.DOC_PATH.as_posix() in task["report_paths"]
    assert "MULTI_JOB_SCOPE_CONFIRMED" in task["notes"]
    assert "JOBS_CATALOG_JSON_UI_READY" in task["notes"]
    assert "BLOCKED_CONFIG_CHANGE_REQUEST_BLOCKED" in task["notes"]
    assert "REAL_BACKUP_ENABLED_FALSE" in task["notes"]
    assert "NEXT_PHASE_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-08 Jobs Catalog / UI Readiness Planning Pack" in html
    assert "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json" in html
