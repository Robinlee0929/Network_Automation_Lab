import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12


DOC_PATH = Path("docs/phase_2c/phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md")


REFERENCE_TEXT = """# Actual Automation Integration Plan

## Stage 0: Mock-only / Dry-run Platform

It does not authorize live device access.

Default decision: NO-GO for real automation.
"""


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _materialize_reference(project_root: Path) -> None:
    path = project_root / phase_2c_12.REFERENCE_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REFERENCE_TEXT, encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_12():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory" not in agents_text
    assert "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory" not in agents_text


def test_phase_2c_12_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory" in text
    for section in (
        "## Phase 2C-12 Scope",
        "## Planning-Only Boundary",
        "## Interview MVP Candidate Inventory",
        "## Candidate Table",
        "## Explicit Non-Selection Statement",
        "## Explicit Non-Authorization Statement",
        "## Forbidden Scope Confirmation",
        "## Safety Inheritance Statement",
        "## Implementation Not Started Confirmation",
        "## Next Phase Boundary",
    ):
        assert section in text
    for label in (
        "CANDIDATE_INVENTORY_ONLY: YES",
        "CANDIDATE_ONLY_NOT_SELECTED_NOT_AUTHORIZED",
        "NO_SINGLE_SLICE_SELECTED",
        "NO_IMPLEMENTATION_AUTHORIZED",
        "NO_IMPLEMENTATION_STARTED",
        "SINGLE_CANDIDATE_SELECTED: NO",
        "IMPLEMENTATION_AUTHORIZED: NO",
        "IMPLEMENTATION_STARTED: NO",
        "PHASE_2C_13_STARTED: NO",
        "RUNNER_CODE_ADDED: NO",
        "ADAPTER_CODE_ADDED: NO",
        "RESULT_ENVELOPE_CODE_ADDED: NO",
        "REPORT_RENDERER_CODE_ADDED: NO",
        "DEMO_JOBS_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_12.FINAL_VERDICT in text


def test_phase_2c_12_builds_candidate_inventory_only_report():
    report = phase_2c_12.build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        Path.cwd()
    )

    assert report["validation"]["valid"] is True
    assert report["final_verdict"] == phase_2c_12.FINAL_VERDICT
    assert report["candidate_inventory_only"] is True
    assert report["single_slice_selected"] is False
    assert report["implementation_authorized"] is False
    assert report["implementation_started"] is False
    assert report["phase_2c_13_started"] is False
    assert report["phase_2c_11_input_review"]["observed_verdict"] == (
        "PHASE_2C_11_INTERVIEW_MVP_SCOPE_ARCHITECTURE_GATE_IMPLEMENTATION_LOCKED"
    )
    assert report["phase_2c_11_input_review"]["source_validation"]["valid"] is True


def test_phase_2c_12_candidates_are_unselected_and_unauthorized():
    report = phase_2c_12.build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        Path.cwd()
    )

    assert len(report["candidate_inventory"]) > 1
    assert all(
        candidate["current_decision_status"] == phase_2c_12.CANDIDATE_STATUS
        for candidate in report["candidate_inventory"]
    )
    assert all(candidate["selected"] is False for candidate in report["candidate_inventory"])
    assert all(candidate["authorized"] is False for candidate in report["candidate_inventory"])
    assert all(candidate["implementation_started"] is False for candidate in report["candidate_inventory"])
    assert "selected_candidate" not in report
    assert "authorized_candidate" not in report


def test_phase_2c_12_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_12.build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        Path.cwd()
    )

    for flag_name, expected in phase_2c_12.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "single_slice_selected",
        "implementation_authorized",
        "implementation_started",
        "phase_2c_13_started",
        "runner_code_added",
        "adapter_code_added",
        "result_envelope_code_added",
        "report_renderer_code_added",
        "demo_jobs_added",
        "execution_path_added",
        "queue_added",
        "scheduler_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_added",
        "config_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_12_rejects_tampered_selection_authorization_or_execution_flags():
    report = phase_2c_12.build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        Path.cwd()
    )
    tampered = copy.deepcopy(report)
    tampered["single_slice_selected"] = True
    tampered["implementation_authorized"] = True
    tampered["implementation_started"] = True
    tampered["phase_2c_13_started"] = True
    tampered["runner_code_added"] = True
    tampered["adapter_code_added"] = True
    tampered["result_envelope_code_added"] = True
    tampered["report_renderer_code_added"] = True
    tampered["demo_jobs_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["candidate_inventory"][0]["selected"] = True
    tampered["candidate_inventory"][0]["authorized"] = True
    tampered["candidate_inventory"][0]["implementation_started"] = True

    validation = phase_2c_12.validate_phase_2c_12_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "CANDIDATE_SELECTED" in validation["errors"]
    assert "CANDIDATE_AUTHORIZED" in validation["errors"]
    assert "CANDIDATE_IMPLEMENTATION_STARTED" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:single_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_code_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_code_added" in validation["errors"]


def test_cli_writes_phase_2c_12_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-12 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-12 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_12.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory" in output
    assert "candidate_count: 6" in output
    assert "candidate_inventory_only: true" in output
    assert "single_slice_selected: false" in output
    assert "implementation_authorized: false" in output
    assert "implementation_started: false" in output
    assert "phase_2c_13_started: false" in output
    assert "runner_code_added: false" in output
    assert "adapter_code_added: false" in output
    assert "result_envelope_code_added: false" in output
    assert "report_renderer_code_added: false" in output
    assert "demo_jobs_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_12.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_12.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_12.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_12(tmp_path):
    _materialize_reference(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_12.TASK_NAME)

    assert task["task_id"] == "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_12.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_12.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_12.DOC_PATH.as_posix() in task["report_paths"]
    assert "CANDIDATE_INVENTORY_ONLY_YES" in task["notes"]
    assert "NO_SINGLE_SLICE_SELECTED" in task["notes"]
    assert "NO_IMPLEMENTATION_AUTHORIZED" in task["notes"]
    assert "NO_IMPLEMENTATION_STARTED" in task["notes"]
    assert "PHASE_2C_13_STARTED_NO" in task["notes"]
    assert "RUNNER_CODE_ADDED_NO" in task["notes"]
    assert "ADAPTER_CODE_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_12.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-12 Interview MVP Implementation Slice Candidate Inventory" in html
    assert "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.json" in html
