import copy
from pathlib import Path

import network_lab
import phase_2c_03_next_slice_decision_gate_authorization_review as phase_2c_03


DOC_PATH = Path("docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_03():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-03 Next-Slice Decision Gate" not in agents_text
    assert "phase_2c_03_next_slice_decision_gate_authorization_review" not in agents_text


def test_phase_2c_03_markdown_artifact_exists_and_has_required_sections_and_labels():
    text = _doc_text()

    assert "# Phase 2C-03 Next-Slice Decision Gate / Authorization Review - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts Referenced",
        "## Implementation Boundary",
        "## Decision Criteria",
        "## Decision",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "LOCAL_STATIC_JOB_REVIEWED: YES",
        "PHASE_2C_02_REFERENCED: YES",
        "NEXT_SLICE_PLANNING_ALLOWED: YES",
        "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE: YES",
        "EXECUTION_PROVIDER_API_OPENED_FALSE: YES",
        "LIVE_DEVICE_ACCESS_OPENED_FALSE: YES",
        "REQUIRES_SEPARATE_USER_AUTHORIZATION_TRUE: YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE: NO",
    ):
        assert label in text
    assert phase_2c_03.FINAL_VERDICT in text


def test_phase_2c_03_allows_planning_only_from_phase_2c_02_input():
    report = phase_2c_03.build_phase_2c_03_next_slice_decision_gate_authorization_review_report()

    assert report["validation"]["valid"] is True
    assert report["authorization_decision"] == "ALLOW_NEXT_SLICE_PLANNING_ONLY"
    assert report["reviewed_completed_first_slice"] == "local_static_job"
    assert report["local_static_job_reviewed"] is True
    assert report["phase_2c_02_referenced"] is True
    assert report["phase_2c_02_acceptance_review_used_as_input"] is True
    assert report["phase_2c_02_acceptance_review_input"]["observed_verdict"] == "PHASE_2C_02_POST_FIRST_SLICE_ACCEPTED"
    assert report["phase_2c_02_acceptance_review_input"]["source_validation"]["valid"] is True
    assert report["next_slice_planning_allowed"] is True
    assert report["next_slice_implementation_allowed"] is False
    assert report["separate_user_authorization_required"] is True


def test_phase_2c_03_keeps_examples_broad_and_next_slice_unselected():
    report = phase_2c_03.build_phase_2c_03_next_slice_decision_gate_authorization_review_report()

    assert set(report["example_job_types"]) == set(phase_2c_03.EXAMPLE_JOB_TYPES)
    assert len(report["example_job_types"]) > 1
    assert "local_static_job" in report["example_job_types"]
    assert "baseline_check" in report["example_job_types"]
    assert "vrrp_validation" in report["example_job_types"]
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert report["scope_narrowed_to_one_example_job_type"] is False
    assert report["needs_scope_confirmation"] is False
    assert report["next_slice_selected"] is False
    assert report["next_slice_scaffolded"] is False
    assert report["next_slice_implemented"] is False


def test_phase_2c_03_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = phase_2c_03.build_phase_2c_03_next_slice_decision_gate_authorization_review_report()

    for flag_name, expected in phase_2c_03.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "next_slice_implementation_allowed",
        "execution_provider_api_opened",
        "live_device_access_opened",
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
        "shell_command_added",
        "custom_script_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "real_device_operation_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_03_rejects_tampered_authorization_or_execution_flags():
    report = phase_2c_03.build_phase_2c_03_next_slice_decision_gate_authorization_review_report()
    tampered = copy.deepcopy(report)
    tampered["authorization_decision"] = "ALLOW_IMPLEMENTATION"
    tampered["next_slice_implementation_allowed"] = True
    tampered["execution_provider_api_opened"] = True
    tampered["live_device_access_opened"] = True
    tampered["execution_opened"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["live_device_touched"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["next_slice_selected"] = True
    tampered["next_slice_scaffolded"] = True
    tampered["next_slice_implemented"] = True
    tampered["phase_2c_02_acceptance_review_input"]["observed_verdict"] = "TAMPERED"

    validation = phase_2c_03.validate_phase_2c_03_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "AUTHORIZATION_DECISION_MISMATCH" in validation["errors"]
    assert "PHASE_2C_02_VERDICT_MISMATCH" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_implementation_allowed" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_provider_api_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:live_device_access_opened" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_scaffolded" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_implemented" in validation["errors"]


def test_cli_writes_phase_2c_03_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-03 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-03 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_03.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-03 Next-Slice Decision Gate / Authorization Review - Planning Only" in output
    assert "Authorization decision: ALLOW_NEXT_SLICE_PLANNING_ONLY" in output
    assert "local_static_job_reviewed: true" in output
    assert "phase_2c_02_referenced: true" in output
    assert "next_slice_planning_allowed: true" in output
    assert "next_slice_implementation_allowed: false" in output
    assert "separate_user_authorization_required: true" in output
    assert "execution_provider_api_opened: false" in output
    assert "live_device_access_opened: false" in output
    assert "next_slice_selected: false" in output
    assert "next_slice_scaffolded: false" in output
    assert "next_slice_implemented: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert f"[PASS] {phase_2c_03.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_03.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_03.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_03(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_03.TASK_NAME)

    assert task["task_id"] == "phase_2c_03_next_slice_decision_gate_authorization_review"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_03.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_03.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_03.DOC_PATH.as_posix() in task["report_paths"]
    assert "LOCAL_STATIC_JOB_REVIEWED" in task["notes"]
    assert "PHASE_2C_02_REFERENCED" in task["notes"]
    assert "NEXT_SLICE_PLANNING_ALLOWED" in task["notes"]
    assert "NEXT_SLICE_IMPLEMENTATION_ALLOWED_FALSE" in task["notes"]
    assert "EXECUTION_PROVIDER_API_OPENED_FALSE" in task["notes"]
    assert "LIVE_DEVICE_ACCESS_OPENED_FALSE" in task["notes"]

    assert network_lab.main(["--task", phase_2c_03.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-03 Next-Slice Decision Gate / Authorization Review - Planning Only" in html
    assert "phase_2c_03_next_slice_decision_gate_authorization_review.json" in html
