import copy
from pathlib import Path

import network_lab
import phase_2c_11_interview_mvp_scope_architecture_gate as phase_2c_11


DOC_PATH = Path("docs/phase_2c/phase_2c_11_interview_mvp_scope_architecture_gate.md")


REFERENCE_TEXT = """# Actual Automation Integration Plan

## Stage 0: Mock-only / Dry-run Platform

It does not authorize live device access.

Default decision: NO-GO for real automation.
"""


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _materialize_reference(project_root: Path) -> None:
    path = project_root / phase_2c_11.REFERENCE_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REFERENCE_TEXT, encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_11():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-11 Interview MVP Scope" not in agents_text
    assert "phase_2c_11_interview_mvp_scope_architecture_gate" not in agents_text


def test_phase_2c_11_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-11 Interview MVP Scope + Architecture Authorization Gate - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Interview MVP Definition",
        "## Safe Dry-Run Platform Scope",
        "## Safe Runner Architecture Boundary",
        "## Mock Adapter Boundary",
        "## Result Envelope Boundary",
        "## Demo Jobs Candidate List",
        "## Forbidden Scope Confirmation",
        "## Required Reference Document Confirmation",
        "## Existing Artifacts Reviewed",
        "## Next Implementation Candidates",
        "## Authorization Status",
        "## Implementation Boundary",
        "## Non-Execution Statement",
        "## Explicit Implementation Not Started Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "AGENTS.md_FOUND: YES",
        "AGENTS.md_READ_BEFORE_ACTION: YES",
        "AGENTS.md_MODIFIED: NO",
        "REQUIRED_REFERENCE_DOCUMENT_FOUND: YES",
        "REQUIRED_REFERENCE_DOCUMENT_READ_BEFORE_SCOPE_CONFIRMATION: YES",
        "INTERVIEW_MVP_DEFINITION_PRESENT: YES",
        "SAFE_DRY_RUN_PLATFORM_SCOPE_DEFINED: YES",
        "RUNNER_ARCHITECTURE_BOUNDARY_DEFINED: YES",
        "MOCK_ADAPTER_BOUNDARY_DEFINED: YES",
        "RESULT_ENVELOPE_BOUNDARY_DEFINED: YES",
        "DEMO_JOB_CANDIDATES_EXAMPLES_ONLY: YES",
        "DEMO_JOB_CANDIDATES_SELECTED_OR_IMPLEMENTED: NO",
        "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED: YES",
        "IMPLEMENTATION_AUTHORIZED: NO",
        "IMPLEMENTATION_STARTED: NO",
        "PHASE_2C_12_STARTED: NO",
        "RUNNER_ADAPTER_RESULT_ENVELOPE_REPORT_RENDERER_DEMO_JOBS_ADDED: NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO",
        "LIVE_DEVICE_SSH_NETCONF_RESTCONF_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED: NO",
        "PRODUCTION_EXECUTION_PATH_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
        "PHASE_2C_10_MODIFIED: NO",
    ):
        assert label in text
    for job_type in phase_2c_11.EXAMPLE_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert phase_2c_11.FINAL_VERDICT in text


def test_phase_2c_11_builds_planning_only_architecture_gate_report():
    report = phase_2c_11.build_phase_2c_11_interview_mvp_scope_architecture_gate_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["final_verdict"] == phase_2c_11.FINAL_VERDICT
    assert report["required_reference_document_found"] is True
    assert report["required_reference_document_read_before_scope_confirmation"] is True
    assert report["interview_mvp_defined"] is True
    assert report["safe_dry_run_platform_scope_defined"] is True
    assert report["runner_architecture_boundary_defined"] is True
    assert report["mock_adapter_boundary_defined"] is True
    assert report["result_envelope_boundary_defined"] is True
    assert report["later_implementation_planning_authorized"] is True
    assert report["implementation_authorized"] is False
    assert report["implementation_started"] is False
    assert report["phase_2c_12_started"] is False


def test_phase_2c_11_blocks_when_required_reference_document_is_missing(tmp_path):
    report = phase_2c_11.build_phase_2c_11_interview_mvp_scope_architecture_gate_report(tmp_path)

    assert report["status"] == "FAIL"
    assert report["validation"]["valid"] is False
    assert phase_2c_11.REFERENCE_MISSING_VERDICT in report["validation"]["errors"]
    assert report["required_reference_document_found"] is False
    assert report["required_reference_document_read_before_scope_confirmation"] is False
    assert report["final_verdict"] == phase_2c_11.REFERENCE_MISSING_VERDICT


def test_phase_2c_11_demo_jobs_are_examples_only():
    report = phase_2c_11.build_phase_2c_11_interview_mvp_scope_architecture_gate_report(Path.cwd())

    assert report["example_job_types"] == list(phase_2c_11.EXAMPLE_JOB_TYPES)
    assert [candidate["job_type"] for candidate in report["demo_job_candidates"]] == list(
        phase_2c_11.EXAMPLE_JOB_TYPES
    )
    for candidate in report["demo_job_candidates"]:
        assert candidate["candidate_only"] is True
        assert candidate["selected"] is False
        assert candidate["implemented"] is False
        assert candidate["execution_capable"] is False
        assert candidate["requires_live_device"] is False


def test_phase_2c_11_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_11.build_phase_2c_11_interview_mvp_scope_architecture_gate_report(Path.cwd())

    for flag_name, expected in phase_2c_11.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "implementation_authorized",
        "implementation_started",
        "phase_2c_12_started",
        "runner_added",
        "adapter_added",
        "result_envelope_added",
        "report_renderer_added",
        "demo_jobs_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "phase_2c_10_modified",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_11_rejects_tampered_implementation_or_execution_flags():
    report = phase_2c_11.build_phase_2c_11_interview_mvp_scope_architecture_gate_report(Path.cwd())
    tampered = copy.deepcopy(report)
    tampered["demo_job_candidates"][0]["selected"] = True
    tampered["demo_job_candidates"][0]["implemented"] = True
    tampered["implementation_authorized"] = True
    tampered["implementation_started"] = True
    tampered["phase_2c_12_started"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["result_envelope_added"] = True
    tampered["report_renderer_added"] = True
    tampered["demo_jobs_added"] = True
    tampered["execution_path_added"] = True
    tampered["queue_added"] = True
    tampered["worker_added"] = True
    tampered["agent_loop_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["config_backup_or_change_behavior_added"] = True
    tampered["production_execution_path_added"] = True
    tampered["phase_2c_10_modified"] = True

    validation = phase_2c_11.validate_phase_2c_11_report(tampered)

    assert validation["valid"] is False
    assert "DEMO_JOB_CANDIDATE_IMPLEMENTED_OR_SELECTED" in validation["errors"]
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_12_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:result_envelope_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:report_renderer_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:demo_jobs_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:agent_loop_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_10_modified" in validation["errors"]


def test_cli_writes_phase_2c_11_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-11 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-11 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_11.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-11 Interview MVP Scope + Architecture Authorization Gate - Planning Only" in output
    assert "required_reference_document_found: true" in output
    assert "required_reference_document_read_before_scope_confirmation: true" in output
    assert "interview_mvp_defined: true" in output
    assert "safe_dry_run_platform_scope_defined: true" in output
    assert "runner_architecture_boundary_defined: true" in output
    assert "mock_adapter_boundary_defined: true" in output
    assert "result_envelope_boundary_defined: true" in output
    assert "later_implementation_planning_authorized: true" in output
    assert "implementation_authorized: false" in output
    assert "implementation_started: false" in output
    assert "phase_2c_12_started: false" in output
    assert "runner_adapter_result_envelope_report_renderer_demo_jobs_added: false" in output
    assert "scheduler_queue_broker_worker_agent_loop_added: false" in output
    assert "live_device_ssh_netconf_restconf_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "config_backup_or_change_behavior_added: false" in output
    assert "production_execution_path_added: false" in output
    assert "phase_2c_10_modified: false" in output
    assert f"[PASS] {phase_2c_11.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_11.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_11.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_11(tmp_path):
    _materialize_reference(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_11.TASK_NAME)

    assert task["task_id"] == "phase_2c_11_interview_mvp_scope_architecture_gate"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_11.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_11.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_11.DOC_PATH.as_posix() in task["report_paths"]
    assert "REQUIRED_REFERENCE_DOCUMENT_FOUND_YES" in task["notes"]
    assert "LATER_IMPLEMENTATION_PLANNING_AUTHORIZED_YES" in task["notes"]
    assert "IMPLEMENTATION_AUTHORIZED_NO" in task["notes"]
    assert "PHASE_2C_12_STARTED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_RESULT_ENVELOPE_REPORT_RENDERER_DEMO_JOBS_ADDED_NO" in task["notes"]
    assert "PHASE_2C_10_MODIFIED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_11.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-11 Interview MVP Scope + Architecture Authorization Gate - Planning Only" in html
    assert "phase_2c_11_interview_mvp_scope_architecture_gate.json" in html
