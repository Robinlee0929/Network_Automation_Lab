import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12
import phase_2c_16_interview_mvp_local_result_envelope_contract as phase_2c_16
import phase_2c_17_post_implementation_slice_acceptance_review_local_result_envelope_contract as phase_2c_17


DOC_PATH = Path(
    "docs/phase_2c/"
    "phase_2c_17_post_implementation_slice_acceptance_review_"
    "local_result_envelope_contract.md"
)
REFERENCE_TEXT = """# Actual Automation Integration Plan

## Stage 0: Mock-only / Dry-run Platform

It does not authorize live device access.

Default decision: NO-GO for real automation.
"""


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _write_placeholder(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"fixture for {path.as_posix()}\n", encoding="utf-8")


def _materialize_reference(project_root: Path) -> None:
    path = project_root / phase_2c_12.REFERENCE_DOC
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REFERENCE_TEXT, encoding="utf-8")


def _materialize_phase_2c_16_evidence(project_root: Path) -> None:
    _materialize_reference(project_root)
    phase_2c_16.write_phase_2c_16_interview_mvp_local_result_envelope_contract_reports(project_root)

    for artifact in phase_2c_17.EXISTING_ARTIFACTS_REVIEWED:
        path = project_root / artifact
        if not path.exists():
            _write_placeholder(path)


def test_agents_md_is_not_modified_for_phase_2c_17():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-17 Post-Implementation Slice Acceptance Review" not in agents_text
    assert "phase_2c_17_post_implementation_slice_acceptance_review" not in agents_text


def test_phase_2c_17_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-17 Post-Implementation Slice Acceptance Review - Local Result Envelope Contract" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Acceptance Review Scope",
        "## Acceptance Criteria",
        "## Existing Artifacts Reviewed",
        "## Report-Only / Dry-Run / Mock-Only Behavior",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "AGENTS.md_FOUND: YES",
        "AGENTS.md_READ_BEFORE_ACTION: YES",
        "AGENTS.md_MODIFIED: NO",
        "REQUIRED_REFERENCE_DOCUMENTS_READ: YES",
        "SCOPE_CONFIRMED_IN_WRITING: YES",
        "NEEDS_SCOPE_CONFIRMATION: NO",
        "PHASE_2C_16_CONTINUED: NO",
        "NEXT_SLICE_SELECTED: NO",
        "NEXT_IMPLEMENTATION_STARTED: NO",
        "PHASE_2C_15_AUTHORIZATION_CONFIRMED: YES",
        "PHASE_2C_16_VALIDATION_PASSED: YES",
        "PHASE_2C_16_EVIDENCE_FOUND: YES",
        "LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED: YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED: NO",
        "PRODUCTION_EXECUTION_PATH_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_17.FINAL_VERDICT in text


def test_phase_2c_17_accepts_phase_2c_16_local_result_envelope_contract():
    report = phase_2c_17.build_phase_2c_17_post_implementation_slice_acceptance_review_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["acceptance_decision"] == "ACCEPT"
    assert report["phase_2c_15_authorization_confirmed"] is True
    assert report["phase_2c_16_evidence_found"] is True
    assert report["phase_2c_16_validation_passed"] is True
    assert report["phase_2c_16_within_authorized_boundary"] is True
    assert report["phase_2c_16_forbidden_execution_paths_avoided"] is True
    assert report["local_result_envelope_contract_local_bounded_interview_mvp_suitable"] is True
    assert report["local_result_envelope_contract_accepted"] == "YES"
    assert all(check["status"] == "PASS" for check in report["acceptance_checks"])


def test_phase_2c_17_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_17.build_phase_2c_17_post_implementation_slice_acceptance_review_report(Path.cwd())

    for flag_name, expected in phase_2c_17.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "phase_2c_16_source_task_rerun",
        "phase_2c_16_implementation_modified",
        "local_result_envelope_contract_modified",
        "phase_2c_16_continued",
        "next_slice_selected",
        "next_implementation_started",
        "phase_2c_18_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_17_rejects_tampered_acceptance_and_execution_flags():
    report = phase_2c_17.build_phase_2c_17_post_implementation_slice_acceptance_review_report(Path.cwd())
    tampered = copy.deepcopy(report)
    tampered["acceptance_decision"] = "ACCEPT"
    tampered["phase_2c_15_authorization_confirmed"] = False
    tampered["phase_2c_16_evidence_found"] = False
    tampered["phase_2c_16_validation_passed"] = False
    tampered["phase_2c_16_continued"] = True
    tampered["next_slice_selected"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["worker_added"] = True
    tampered["ai_loop_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["config_backup_change_behavior_added"] = True
    tampered["production_execution_path_added"] = True
    tampered["day1_day160_rewritten_or_replaced"] = True
    tampered["second_safety_matrix_created"] = True

    validation = phase_2c_17.validate_phase_2c_17_report(tampered)

    assert validation["valid"] is False
    assert "PHASE_2C_17_FORBIDDEN_SCOPE_OPENED" in validation["errors"]
    assert "ACCEPT_DECISION_WITHOUT_REQUIRED_EVIDENCE" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_16_continued" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:worker_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ai_loop_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_17_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_phase_2c_16_evidence(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-17 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-17 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_17.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-17 Post-Implementation Slice Acceptance Review - Local Result Envelope Contract" in output
    assert "acceptance_decision: ACCEPT" in output
    assert "phase_2c_15_authorization_confirmed: true" in output
    assert "phase_2c_16_evidence_found: true" in output
    assert "phase_2c_16_validation_passed: true" in output
    assert "local_result_envelope_contract_accepted: YES" in output
    assert "phase_2c_16_continued: false" in output
    assert "next_slice_selected: false" in output
    assert "next_implementation_started: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "queue_scheduler_worker_ai_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "config_backup_change_behavior_added: false" in output
    assert "production_execution_path_added: false" in output
    assert f"[PASS] {phase_2c_17.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_17.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_17.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_17(tmp_path):
    _materialize_phase_2c_16_evidence(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_17.TASK_NAME)

    assert task["task_id"] == "phase_2c_17_post_implementation_slice_acceptance_review_local_result_envelope_contract"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_17.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_17.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_17.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2C_17_POST_IMPLEMENTATION_SLICE_ACCEPTANCE_REVIEW_REPORT_ONLY" in task["notes"]
    assert "LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED_YES" in task["notes"]
    assert "PHASE_2C_16_CONTINUED_NO" in task["notes"]
    assert "NEXT_SLICE_SELECTED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_17.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-17 Post-Implementation Slice Acceptance Review" in html
    assert "phase_2c_17_acceptance_review.json" in html
