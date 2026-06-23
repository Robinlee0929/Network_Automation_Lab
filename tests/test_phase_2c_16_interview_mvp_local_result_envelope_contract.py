import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12
import phase_2c_16_interview_mvp_local_result_envelope_contract as phase_2c_16


DOC_PATH = Path("docs/phase_2c/phase_2c_16_interview_mvp_local_result_envelope_contract.md")
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


def test_agents_md_is_not_modified_for_phase_2c_16():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-16 Interview MVP Local Result Envelope Contract" not in agents_text
    assert "phase_2c_16_interview_mvp_local_result_envelope_contract" not in agents_text


def test_phase_2c_16_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-16 Interview MVP Local Result Envelope Contract" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Existing Artifacts Referenced",
        "## Implementation Boundary",
        "## Contract Shape",
        "## Non-Execution Statement",
        "## Validation Method",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "SELECTED_NEXT_SLICE: local_result_envelope_contract",
        "PHASE_GOAL_CONFIRMED: YES",
        "PHASE_2C_15_AUTHORIZATION_CONFIRMED: YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE: NO",
        "NEEDS_SCOPE_CONFIRMATION: NO",
        "CONTRACT_SHAPE_DEFINED: YES",
        "VALIDATOR_ADDED: YES",
        "SAMPLE_ENVELOPE_STATIC_FIXTURE_ONLY: YES",
        "LOCAL_ONLY: YES",
        "DETERMINISTIC: YES",
        "REPORT_ONLY_DRY_RUN_MOCK_ONLY: YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_ADDED: NO",
        "PRODUCTION_EXECUTION_PATH_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
        "NEXT_PHASE_STARTED: NO",
        "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO",
    ):
        assert label in text
    assert "STATIC_CONTRACT_EXAMPLE_NOT_LIVE_OUTPUT" in text
    assert phase_2c_16.FINAL_VERDICT in text


def test_local_result_envelope_contract_defines_report_only_shape():
    contract = phase_2c_16.build_local_result_envelope_contract()

    assert contract["contract_name"] == "local_result_envelope_contract"
    assert contract["schema_version"] == phase_2c_16.ENVELOPE_SCHEMA_VERSION
    assert contract["required_fields"] == list(phase_2c_16.REQUIRED_ENVELOPE_FIELDS)
    assert contract["allowed_result_statuses"] == list(phase_2c_16.ALLOWED_RESULT_STATUSES)
    assert contract["not_runtime_infrastructure"] is True
    assert contract["not_result_processing_infrastructure"] is True
    assert contract["sample_only_required"] is True


def test_sample_local_result_envelope_is_static_deterministic_and_valid():
    first = phase_2c_16.build_sample_local_result_envelope()
    second = phase_2c_16.build_sample_local_result_envelope()

    assert first == second
    assert first["contract_name"] == "local_result_envelope_contract"
    assert first["result_status"] == "REVIEW_ONLY"
    assert first["fixture_notice"] == "STATIC_CONTRACT_EXAMPLE_NOT_LIVE_OUTPUT"
    assert first["dry_run_mock_status"]["report_only"] is True
    assert first["dry_run_mock_status"]["dry_run_only"] is True
    assert first["dry_run_mock_status"]["mock_only"] is True
    assert first["dry_run_mock_status"]["live_device_observed"] is False
    assert first["report_only_evidence"][0]["not_live_output"] is True
    assert all(first[field] is None for field in phase_2c_16.NON_EXECUTABLE_FIELDS)
    assert phase_2c_16.validate_local_result_envelope(first)["valid"] is True


def test_phase_2c_16_report_validates_source_authorization_and_contract():
    report = phase_2c_16.build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(Path.cwd())

    assert report["validation"]["valid"] is True
    assert report["selected_candidate_id"] == "candidate-03"
    assert report["selected_next_slice"] == "local_result_envelope_contract"
    assert report["phase_2c_15_source_review"]["authorization_matches_phase_2c_16_target"] is True
    assert report["local_result_envelope_contract_implemented"] is True
    assert report["contract_shape_defined"] is True
    assert report["validator_added"] is True
    assert report["sample_envelope_static_fixture_only"] is True
    assert report["scope_narrowed_to_one_example"] is False
    assert report["needs_scope_confirmation"] is False


def test_phase_2c_16_report_output_is_deterministic():
    first = phase_2c_16.build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(Path.cwd())
    second = phase_2c_16.build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(Path.cwd())

    assert first == second


def test_phase_2c_16_no_forbidden_scope_flags_are_added():
    report = phase_2c_16.build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(Path.cwd())

    for flag_name, expected in phase_2c_16.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "provider_api_model_secrets_touched",
        "ssh_netconf_restconf_live_device_touched",
        "real_command_execution_added",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "next_phase_started",
        "extra_slice_selected_or_implemented",
    ):
        assert report[flag_name] is False


def test_phase_2c_16_rejects_tampered_execution_or_live_output_claims():
    report = phase_2c_16.build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(Path.cwd())
    tampered = copy.deepcopy(report)
    envelope = tampered["sample_local_result_envelope"]
    envelope["fixture_notice"] = "LIVE_OUTPUT"
    envelope["dry_run_mock_status"]["live_device_observed"] = True
    envelope["report_only_evidence"][0]["not_live_output"] = False
    envelope["forbidden_scope_metadata"]["runner_added"] = True
    envelope["non_execution_proof"]["runtime_result_consumed"] = True
    envelope["shell_command"] = "echo unsafe"
    tampered["runner_added"] = True
    tampered["execution_path_added"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["next_phase_started"] = True

    validation = phase_2c_16.validate_phase_2c_16_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "LOCAL_RESULT_ENVELOPE:FIXTURE_NOTICE_MISSING" in validation["errors"]
    assert "LOCAL_RESULT_ENVELOPE:LIVE_DEVICE_OBSERVED_NOT_FALSE" in validation["errors"]
    assert "LOCAL_RESULT_ENVELOPE:REPORT_ONLY_EVIDENCE_NOT_LIVE_OUTPUT_FLAG_MISSING:0" in validation["errors"]
    assert "LOCAL_RESULT_ENVELOPE:NON_EXECUTABLE_FIELD_POPULATED:shell_command" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:provider_api_model_secrets_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_phase_started" in validation["errors"]


def test_cli_writes_phase_2c_16_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-16 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-16 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_16.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-16 Interview MVP Local Result Envelope Contract" in output
    assert "selected_next_slice: local_result_envelope_contract" in output
    assert "phase_goal_confirmed: true" in output
    assert "phase_2c_15_authorization_confirmed: true" in output
    assert "scope_narrowed_to_one_example: false" in output
    assert "needs_scope_confirmation: false" in output
    assert "contract_shape_defined: true" in output
    assert "validator_added: true" in output
    assert "sample_envelope_static_fixture_only: true" in output
    assert "local_only: true" in output
    assert "deterministic: true" in output
    assert "report_only_dry_run_mock_only: true" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "queue_scheduler_worker_ai_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "config_backup_or_change_behavior_added: false" in output
    assert "production_execution_path_added: false" in output
    assert "next_phase_started: false" in output
    assert "extra_slice_selected_or_implemented: false" in output
    assert f"[PASS] {phase_2c_16.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_16.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_16.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_16(tmp_path):
    _materialize_reference(tmp_path)

    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_16.TASK_NAME)

    assert task["task_id"] == "phase_2c_16_interview_mvp_local_result_envelope_contract"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_16.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_16.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_16.DOC_PATH.as_posix() in task["report_paths"]
    assert "CONTRACT_SHAPE_DEFINED_YES" in task["notes"]
    assert "VALIDATOR_ADDED_YES" in task["notes"]
    assert "SAMPLE_ENVELOPE_STATIC_FIXTURE_ONLY_YES" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]
    assert "NEXT_PHASE_STARTED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_16.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-16 Interview MVP Local Result Envelope Contract" in html
    assert "phase_2c_16_interview_mvp_local_result_envelope_contract.json" in html
