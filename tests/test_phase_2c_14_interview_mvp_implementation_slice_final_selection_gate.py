import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12
import phase_2c_14_interview_mvp_implementation_slice_final_selection_gate as phase_2c_14
from report_file_utils import path_exists, read_text_with_long_path, write_text_with_parents


DOC_PATH = Path("docs/phase_2c/phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.md")


REFERENCE_TEXT = """# Actual Automation Integration Plan

## Stage 0: Mock-only / Dry-run Platform

It does not authorize live device access.

Default decision: NO-GO for real automation.
"""


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _materialize_reference(project_root: Path) -> None:
    path = project_root / phase_2c_12.REFERENCE_DOC
    write_text_with_parents(path, REFERENCE_TEXT, encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_14():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-14 Interview MVP Implementation Slice Final Selection Gate" not in agents_text
    assert "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate" not in agents_text


def test_phase_2c_14_markdown_artifact_exists_and_has_required_separation():
    text = _doc_text()

    assert "# Phase 2C-14 Interview MVP Implementation Slice Final Selection Gate - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Candidate Source",
        "## Example Job Types",
        "## Selection Criteria",
        "## Safety Delta Dependency",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Selected Next Slice",
        "## Rationale",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "FINAL_SELECTION_GATE_ONLY: YES",
        "PHASE_2C_12_READ: YES",
        "PHASE_2C_13_READ: YES",
        "CANDIDATE_SELECTED: YES",
        "SELECTED_NEXT_SLICE: local_result_envelope_contract",
        "IMPLEMENTATION_AUTHORIZED: NO",
        "IMPLEMENTATION_STARTED: NO",
        "PHASE_2C_15_STARTED: NO",
        "IMPLEMENTATION_ADDED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_14.FINAL_VERDICT in text


def test_phase_2c_14_builds_final_selection_gate_only_report():
    report = phase_2c_14.build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
        Path.cwd()
    )

    assert report["validation"]["valid"] is True
    assert report["selection_decision"] == "FINAL_SELECTION_GATE_ONLY"
    assert report["phase_2c_12_source_review"]["observed_verdict"] == phase_2c_12.FINAL_VERDICT
    assert report["phase_2c_12_source_review"]["source_validation"]["valid"] is True
    assert report["phase_2c_13_safety_delta_dependency_review"]["source_validation"]["valid"] is True
    assert report["final_selection_gate_only"] is True
    assert report["phase_2c_12_read"] is True
    assert report["phase_2c_13_read"] is True
    assert report["candidate_selected"] is True
    assert report["selected_candidate_id"] == phase_2c_14.SELECTED_CANDIDATE_ID
    assert report["selected_next_slice"] == phase_2c_14.SELECTED_NEXT_SLICE
    assert report["implementation_authorized"] is False
    assert report["implementation_started"] is False
    assert report["phase_2c_15_started"] is False
    assert report["implementation_added"] is False


def test_phase_2c_14_selects_exactly_one_safer_candidate_without_authorization():
    report = phase_2c_14.build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
        Path.cwd()
    )

    selected = [candidate for candidate in report["candidate_selection_reviews"] if candidate["selected"] is True]

    assert len(selected) == 1
    assert selected[0]["candidate_id"] == "candidate-03"
    assert selected[0]["candidate_name"] == "local_result_envelope_contract"
    assert selected[0]["phase_2c_13_delta_status"] == phase_2c_14.PHASE_2C_13_SAFE_DELTA_STATUS
    assert selected[0]["source_runner_adapter_execution_risk"] is False
    assert selected[0]["source_live_device_provider_secrets_risk"] is False
    assert selected[0]["requires_expanded_forbidden_scope"] is False
    assert report["phase_2c_13_safety_delta_dependency_review"]["all_candidates_safe_within_planning_boundary"] is True
    assert report["implementation_authorized"] is False
    assert report["implementation_started"] is False
    assert report["phase_2c_15_started"] is False


def test_phase_2c_14_no_execution_flags_stay_disabled():
    report = phase_2c_14.build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
        Path.cwd()
    )

    for flag_name, expected in phase_2c_14.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "implementation_authorized",
        "implementation_started",
        "phase_2c_15_started",
        "implementation_added",
        "runtime_implementation_added",
        "execution_opened",
        "provider_api_opened",
        "model_opened",
        "secrets_touched",
        "live_device_touched",
        "ssh_netconf_restconf_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_14_rejects_tampered_authorization_implementation_or_unsafe_selection():
    report = phase_2c_14.build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
        Path.cwd()
    )
    tampered = copy.deepcopy(report)
    tampered["selection_decision"] = "IMPLEMENT_SELECTED_SLICE"
    tampered["implementation_authorized"] = True
    tampered["implementation_started"] = True
    tampered["phase_2c_15_started"] = True
    tampered["implementation_added"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["queue_added"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["candidate_selection_reviews"][2]["phase_2c_13_delta_status"] = "UNACCEPTABLE_NEW_SAFETY_DELTA"
    tampered["candidate_selection_reviews"][2]["source_runner_adapter_execution_risk"] = True

    validation = phase_2c_14.validate_phase_2c_14_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SELECTION_DECISION_MISMATCH" in validation["errors"]
    assert "NO_SAFE_INTERVIEW_MVP_SLICE_SELECTED" in validation["errors"]
    assert "SELECTED_CANDIDATE_RUNNER_ADAPTER_RISK" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_15_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_14_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-14 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-14 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_14.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-14 Interview MVP Implementation Slice Final Selection Gate - Planning Only" in output
    assert "Selection decision: FINAL_SELECTION_GATE_ONLY" in output
    assert "phase_2c_12_read: true" in output
    assert "phase_2c_13_read: true" in output
    assert "final_selection_gate_only: true" in output
    assert "candidate_selected: true" in output
    assert "selected_candidate_id: candidate-03" in output
    assert "selected_next_slice: local_result_envelope_contract" in output
    assert "implementation_authorized: false" in output
    assert "implementation_started: false" in output
    assert "phase_2c_15_started: false" in output
    assert "implementation_added: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "queue_scheduler_worker_ai_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_14.FINAL_VERDICT}" in output
    assert path_exists(tmp_path / phase_2c_14.REPORT_JSON)
    assert path_exists(tmp_path / phase_2c_14.REPORT_HTML)


def test_task_catalog_and_report_index_visibility_for_phase_2c_14(tmp_path):
    _materialize_reference(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_14.TASK_NAME)

    assert task["task_id"] == "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_14.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_14.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_14.DOC_PATH.as_posix() in task["report_paths"]
    assert "FINAL_SELECTION_GATE_ONLY_YES" in task["notes"]
    assert "CANDIDATE_SELECTED_YES" in task["notes"]
    assert "SELECTED_NEXT_SLICE_LOCAL_RESULT_ENVELOPE_CONTRACT" in task["notes"]
    assert "IMPLEMENTATION_AUTHORIZED_NO" in task["notes"]
    assert "IMPLEMENTATION_STARTED_NO" in task["notes"]
    assert "PHASE_2C_15_STARTED_NO" in task["notes"]
    assert "IMPLEMENTATION_ADDED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_14.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Phase 2C-14 Interview MVP Implementation Slice Final Selection Gate - Planning Only" in html
    assert "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.json" in html
