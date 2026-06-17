import json
from pathlib import Path

import network_lab
import phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack as pack


def _rows_by_type(report):
    rows = report["mock_screen_data"]["job_list_populated"]["rows"]
    return {row["job_type"]: row for row in rows}


def test_agents_md_status_is_recorded_and_file_was_not_modified_by_pack():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    agents_path = Path("AGENTS.md")

    assert agents_path.exists()
    assert "Phase 2A-09 Jobs UI Display Contract" not in agents_path.read_text(encoding="utf-8")
    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }


def test_phase_2a_09_artifacts_and_phase_2a_08_source_are_present():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()

    assert report["phase"] == "2A-09"
    assert report["status"] == "PASS"
    assert report["phase_2a_08_source"]["source_artifact_found"] is True
    assert report["phase_2a_08_source"]["source_job_count"] == 6
    assert set(report["phase_2a_08_source"]["source_job_types"]) == set(pack.PHASE_2A_08_REQUIRED_JOB_TYPES)
    assert "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py" in report["existing_artifacts_referenced"]


def test_job_list_contract_includes_required_display_fields():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    contract = report["job_list_view_contract"]

    assert contract["future_route"] == "/network/jobs"
    assert set(pack.JOB_LIST_REQUIRED_FIELDS).issubset(contract["required_fields"])
    assert contract["row_behavior"]["rows_are_display_only"] is True
    assert contract["row_behavior"]["row_must_not_execute"] is True


def test_job_detail_contract_includes_capability_and_safety_display_fields():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    contract = report["job_detail_view_contract"]

    assert set(pack.JOB_DETAIL_REQUIRED_FIELDS).issubset(contract["required_fields"])
    assert contract["detail_behavior"]["show_can_and_cannot_do_sections"] is True
    assert contract["detail_behavior"]["show_no_execution_proof"] is True
    assert contract["detail_behavior"]["show_no_live_device_proof"] is True
    assert contract["detail_behavior"]["show_no_ssh_netconf_restconf_proof"] is True

    for detail in report["mock_screen_data"]["job_detail_examples"]:
        assert detail["what_this_job_can_do"]
        assert detail["what_this_job_cannot_do"]
        assert detail["no_execution_proof"]["executable_now"] is False
        assert detail["no_execution_proof"]["runner_invoked"] is False
        assert detail["no_live_device_proof"]["live_device_access_enabled"] is False
        assert detail["no_ssh_netconf_restconf_proof"] == {
            "ssh_enabled": False,
            "netconf_enabled": False,
            "restconf_enabled": False,
        }


def test_badge_rules_include_all_required_badge_types_and_never_allow_execution():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()

    assert set(pack.REQUIRED_BADGE_TYPES).issubset(report["badge_rules"])
    for badge_type in pack.REQUIRED_BADGE_TYPES:
        assert report["badge_rules"][badge_type]["executable_allowed"] is False


def test_empty_state_exists_and_does_not_suggest_execution():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    empty_states = report["empty_state_contract"]

    assert set(empty_states) == {"no_catalog_exists", "catalog_exists_zero_jobs", "no_displayable_jobs"}
    for state in empty_states.values():
        assert state["must_not_suggest_execution"] is True
        action = state["primary_action_label"].lower()
        assert not any(word in action for word in pack.FORBIDDEN_EMPTY_ACTION_WORDS)


def test_error_state_exists_and_blocks_executable_interpretation():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    error_states = report["error_state_contract"]

    assert set(error_states) == {
        "malformed_json",
        "required_fields_missing",
        "unknown_status",
        "forbidden_execution_fields",
        "unsafe_capability",
    }
    assert all(state["blocks_executable_interpretation"] is True for state in error_states.values())
    assert all("blocked" in state["badges"] for state in error_states.values())


def test_mock_screen_data_includes_multiple_job_types_not_one_example():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    rows = _rows_by_type(report)

    assert len(rows) == 6
    assert set(rows) == set(pack.PHASE_2A_08_REQUIRED_JOB_TYPES)
    assert set(rows) != {"vrrp_validation"}
    assert rows["vrrp_validation"]["display_status"] == "planning-only"
    assert rows["backup_config_plan"]["display_status"] == "approval-required"
    assert rows["blocked_config_change_request"]["display_status"] == "blocked"


def test_mock_screen_data_includes_allowed_blocked_planning_and_approval_examples():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    statuses = {
        row["display_status"]
        for row in report["mock_screen_data"]["job_list_populated"]["rows"]
    }

    assert {"allowed", "blocked", "planning-only", "approval-required"}.issubset(statuses)
    assert report["summary"]["allowed_examples"] >= 1
    assert report["summary"]["blocked_examples"] >= 1
    assert report["summary"]["planning_only_examples"] >= 1
    assert report["summary"]["approval_required_examples"] >= 1
    assert report["summary"]["executable_examples"] == 0


def test_safety_display_includes_no_ssh_no_runner_no_live_device_and_protocol_locks():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    safety = report["safety_display_contract"]

    for line in (
        "no SSH",
        "no runner",
        "no live device",
        "no NETCONF",
        "no RESTCONF",
        "dry-run only",
        "planning/mock/local only",
        "not Phase 2B",
    ):
        assert line in safety["required_banner_lines"]

    assert safety["display_flags"]["no_ssh"] is True
    assert safety["display_flags"]["no_runner"] is True
    assert safety["display_flags"]["no_live_device"] is True
    assert safety["display_flags"]["no_netconf"] is True
    assert safety["display_flags"]["no_restconf"] is True


def test_forbidden_strings_or_executable_capability_indicators_are_rejected_or_absent():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    assert report["validation"]["valid"] is True

    tampered = json.loads(json.dumps(report))
    tampered["mock_screen_data"]["job_list_populated"]["rows"][0]["command"] = "blocked-placeholder"
    validation = pack.validate_phase_2a_09_report(tampered)
    assert validation["valid"] is False
    assert any(error.startswith("FORBIDDEN_EXECUTION_FIELDS_PRESENT_IN_MOCK") for error in validation["errors"])

    tampered = json.loads(json.dumps(report))
    tampered["runner_introduced"] = True
    tampered["safety_display_contract"]["display_flags"]["no_runner"] = False
    validation = pack.validate_phase_2a_09_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_NOT_FALSE:runner_introduced" in validation["errors"]
    assert "SAFETY_DISPLAY_FLAG_MISSING:no_runner" in validation["errors"]


def test_no_phase_2b_runner_adapter_protocol_live_backup_or_vrrp_execution_introduced():
    report = pack.build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()

    for flag_name in (
        "phase_2b_introduced",
        "runner_introduced",
        "adapter_introduced",
        "ssh_introduced",
        "netconf_introduced",
        "restconf_introduced",
        "live_device_introduced",
        "real_backup_introduced",
        "real_vrrp_execution_introduced",
        "real_frontend_api_integration_introduced",
    ):
        assert report[flag_name] is False


def test_cli_writes_jobs_ui_display_contract_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-09 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-09 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-09 Jobs UI Display Contract / Mock Screen Readiness Pack" in output
    assert "Task name: phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack" in output
    assert "Source catalog jobs: 6" in output
    assert "Mock list rows: 6" in output
    assert "Executable examples: 0" in output
    assert "runner_introduced: false" in output
    assert "adapter_introduced: false" in output
    assert "ssh_introduced: false" in output
    assert "netconf_introduced: false" in output
    assert "restconf_introduced: false" in output
    assert "live_device_introduced: false" in output
    assert "real_backup_introduced: false" in output
    assert "real_vrrp_execution_introduced: false" in output
    assert "real_frontend_api_integration_introduced: false" in output
    assert "[PASS] PHASE_2A_09_JOBS_UI_DISPLAY_CONTRACT_MOCK_SCREEN_READINESS_PACK_READY" in output
    assert (tmp_path / pack.REPORT_JSON).exists()
    assert (tmp_path / pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == pack.TASK_NAME)

    assert task["task_id"] == "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert pack.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2A_08_JOBS_CATALOG_REFERENCED" in task["notes"]
    assert "JOB_LIST_VIEW_CONTRACT_DEFINED" in task["notes"]
    assert "JOB_DETAIL_VIEW_CONTRACT_DEFINED" in task["notes"]
    assert "REAL_FRONTEND_API_INTEGRATION_INTRODUCED_FALSE" in task["notes"]
    assert "PHASE_2B_INTRODUCED_FALSE" in task["notes"]

    assert network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-09 Jobs UI Display Contract / Mock Screen Readiness Pack" in html
    assert "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.json" in html
