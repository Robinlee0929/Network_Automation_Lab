import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12
import phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate as phase_2c_15


DOC_PATH = Path("docs/phase_2c/phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.md")


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


def test_agents_md_is_not_modified_for_phase_2c_15():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-15 Interview MVP Implementation Slice Kickoff Authorization Gate" not in agents_text
    assert "phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate" not in agents_text


def test_phase_2c_15_markdown_artifact_exists_and_is_authorization_gate_only():
    text = _doc_text()

    assert "# Phase 2C-15 Interview MVP Implementation Slice Kickoff Authorization Gate - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Decision Target",
        "## Authorization Question",
        "## Authorization Result",
        "## Decision Rationale",
        "## Safety Baseline Compatibility",
        "## Example Job Types",
        "## Existing Artifacts Referenced",
        "## Future Implementation Boundary",
        "## Forbidden Scope Confirmation",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "AUTHORIZATION_GATE_ONLY: YES",
        "DECISION_TARGET: candidate-03 / local_result_envelope_contract",
        "AUTHORIZATION_RESULT: AUTHORIZED",
        "FUTURE_PHASE_IMPLEMENTATION_AUTHORIZED: YES",
        "PHASE_2C_15_IMPLEMENTS_SLICE: NO",
        "LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED: NO",
        "RESULT_ENVELOPE_RUNTIME_ADDED: NO",
        "IMPLEMENTATION_STARTED: NO",
        "NEXT_PHASE_STARTED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
        "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO",
    ):
        assert label in text
    assert "This authorizes only a later phase" in text
    assert phase_2c_15.FINAL_VERDICT in text


def test_phase_2c_15_builds_authorization_gate_only_report():
    report = phase_2c_15.build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
        Path.cwd()
    )

    assert report["validation"]["valid"] is True
    assert report["authorization_decision"] == "KICKOFF_AUTHORIZATION_GATE_ONLY"
    assert report["authorization_question"] == phase_2c_15.AUTHORIZATION_QUESTION
    assert report["authorization_result"] == "AUTHORIZED"
    assert report["decision_target_id"] == "candidate-03"
    assert report["decision_target_slice"] == "local_result_envelope_contract"
    assert report["phase_2c_14_source_review"]["selected_candidate_matches_decision_target"] is True
    assert report["future_phase_implementation_authorized"] is True
    assert report["phase_2c_15_implements_slice"] is False
    assert report["local_result_envelope_contract_implemented"] is False
    assert report["result_envelope_runtime_added"] is False
    assert report["implementation_started"] is False
    assert report["next_phase_started"] is False


def test_phase_2c_15_no_execution_flags_stay_disabled():
    report = phase_2c_15.build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
        Path.cwd()
    )

    for flag_name, expected in phase_2c_15.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "phase_2c_15_implements_slice",
        "local_result_envelope_contract_implemented",
        "result_envelope_runtime_added",
        "implementation_started",
        "next_phase_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "extra_slice_selected_or_implemented",
    ):
        assert report[flag_name] is False


def test_phase_2c_15_rejects_tampered_implementation_or_next_phase_start():
    report = phase_2c_15.build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
        Path.cwd()
    )
    tampered = copy.deepcopy(report)
    tampered["authorization_result"] = "NOT_AUTHORIZED"
    tampered["decision_target_slice"] = "different_slice"
    tampered["phase_2c_15_implements_slice"] = True
    tampered["local_result_envelope_contract_implemented"] = True
    tampered["result_envelope_runtime_added"] = True
    tampered["implementation_started"] = True
    tampered["next_phase_started"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["queue_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["second_safety_matrix_created"] = True

    validation = phase_2c_15.validate_phase_2c_15_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "AUTHORIZATION_RESULT_MISMATCH" in validation["errors"]
    assert "DECISION_TARGET_SLICE_MISMATCH" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_15_implements_slice" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:local_result_envelope_contract_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:result_envelope_runtime_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_phase_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_15_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-15 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-15 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_15.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-15 Interview MVP Implementation Slice Kickoff Authorization Gate - Planning Only" in output
    assert "Authorization decision: KICKOFF_AUTHORIZATION_GATE_ONLY" in output
    assert "authorization_gate_only: true" in output
    assert "decision_target: candidate-03 / local_result_envelope_contract" in output
    assert "authorization_result: AUTHORIZED" in output
    assert "future_phase_implementation_authorized: true" in output
    assert "phase_2c_15_implements_slice: false" in output
    assert "local_result_envelope_contract_implemented: false" in output
    assert "result_envelope_runtime_added: false" in output
    assert "implementation_started: false" in output
    assert "next_phase_started: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "queue_scheduler_worker_ai_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_15.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_15.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_15.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_15(tmp_path):
    _materialize_reference(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_15.TASK_NAME)

    assert task["task_id"] == "phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_15.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_15.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_15.DOC_PATH.as_posix() in task["report_paths"]
    assert "AUTHORIZATION_GATE_ONLY_YES" in task["notes"]
    assert "DECISION_TARGET_CANDIDATE_03_LOCAL_RESULT_ENVELOPE_CONTRACT" in task["notes"]
    assert "AUTHORIZATION_RESULT_AUTHORIZED" in task["notes"]
    assert "FUTURE_PHASE_IMPLEMENTATION_AUTHORIZED_YES" in task["notes"]
    assert "LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED_NO" in task["notes"]
    assert "RESULT_ENVELOPE_RUNTIME_ADDED_NO" in task["notes"]
    assert "NEXT_PHASE_STARTED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_15.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-15 Interview MVP Implementation Slice Kickoff Authorization Gate - Planning Only" in html
    assert phase_2c_15.REPORT_JSON.name in html
