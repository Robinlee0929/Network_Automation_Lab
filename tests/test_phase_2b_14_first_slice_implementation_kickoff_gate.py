import copy
from pathlib import Path

import network_lab
import phase_2b_14_first_slice_implementation_kickoff_gate as gate


DOC_PATH = Path("docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_14():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-14 First-Slice Implementation Kickoff Gate" not in agents_text
    assert "phase_2b_14_first_slice_implementation_kickoff_gate" not in agents_text


def test_phase_2b_14_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-14 First-Slice Implementation Kickoff Gate" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Authorization Gate Decision",
        "## Non-Implementation Statement",
        "## Final Verdict",
    ):
        assert section in text
    assert gate.FINAL_VERDICT in text
    assert "This artifact is an authorization kickoff gate only." in text


def test_phase_2b_14_scope_confirmation_is_written_and_not_narrowed():
    report = gate.build_phase_2b_14_first_slice_implementation_kickoff_gate_report()
    text = _doc_text()

    assert report["scope_confirmation_written"] is True
    assert report["phase_goal_separated"] is True
    assert report["example_job_types_separated"] is True
    assert report["forbidden_scope_separated"] is True
    assert report["existing_artifacts_referenced"] is True
    assert report["implementation_boundary_separated"] is True
    assert report["scope_narrowed_to_single_example"] is False
    assert report["needs_scope_confirmation"] is False
    assert set(report["example_job_types"]) == set(gate.EXAMPLE_JOB_TYPES)
    assert len(report["example_job_types"]) > 1
    assert "SCOPE_CONFIRMATION_WRITTEN: YES" in text
    assert "SCOPE_NARROWED_TO_SINGLE_EXAMPLE: NO" in text
    assert "NEEDS_SCOPE_CONFIRMATION: NO" in text


def test_phase_2b_14_references_selected_slice_without_implementing_it():
    report = gate.build_phase_2b_14_first_slice_implementation_kickoff_gate_report()
    text = _doc_text()

    assert report["phase_2b_13_selected_future_first_slice"] is True
    assert report["phase_2b_13_verdict_referenced"] == "PHASE_2B_13_FIRST_SLICE_SELECTED_PLANNING_ONLY"
    assert report["selected_future_first_slice"]["implementation_status"] == "NOT_IMPLEMENTED"
    assert report["selected_first_slice_is_first_target_only"] is True
    assert report["broader_phase_scope_reduced_to_first_slice"] is False
    assert report["first_slice_implemented"] is False
    assert report["local_static_job_implemented"] is False
    assert "`local_static_job` does not redefine the whole phase" in text
    assert "Later implementation still requires explicit user authorization: YES." in text


def test_phase_2b_14_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = gate.build_phase_2b_14_first_slice_implementation_kickoff_gate_report()

    assert report["validation"]["valid"] is True
    for flag_name, expected in gate.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "first_slice_implemented",
        "local_static_job_implemented",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "live_device_access_added",
        "provider_calls_added",
        "api_calls_added",
        "model_calls_added",
        "secrets_handling_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "custom_command_execution_added",
        "custom_script_execution_added",
        "real_device_operation_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2b_14_rejects_tampered_scope_or_execution_flags():
    report = gate.build_phase_2b_14_first_slice_implementation_kickoff_gate_report()
    tampered = copy.deepcopy(report)
    tampered["scope_narrowed_to_single_example"] = True
    tampered["needs_scope_confirmation"] = True
    tampered["first_slice_implemented"] = True
    tampered["local_static_job_implemented"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_touched"] = True
    tampered["api_calls_added"] = True
    tampered["secrets_handling_added"] = True

    validation = gate.validate_phase_2b_14_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:scope_narrowed_to_single_example" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:first_slice_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:local_static_job_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:api_calls_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_14_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-14 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-14 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-14 First-Slice Implementation Kickoff Gate" in output
    assert "scope_confirmation_written: true" in output
    assert "phase_goal_separated: true" in output
    assert "example_job_types_separated: true" in output
    assert "forbidden_scope_separated: true" in output
    assert "existing_artifacts_referenced: true" in output
    assert "implementation_boundary_separated: true" in output
    assert "scope_narrowed_to_single_example: false" in output
    assert "needs_scope_confirmation: false" in output
    assert "first_slice_implemented: false" in output
    assert "local_static_job_implemented: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {gate.FINAL_VERDICT}" in output
    assert (tmp_path / gate.REPORT_JSON).exists()
    assert (tmp_path / gate.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2b_14(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == gate.TASK_NAME)

    assert task["task_id"] == "phase_2b_14_first_slice_implementation_kickoff_gate"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert gate.REPORT_JSON.as_posix() in task["report_paths"]
    assert gate.REPORT_HTML.as_posix() in task["report_paths"]
    assert gate.DOC_PATH.as_posix() in task["report_paths"]
    assert "SCOPE_CONFIRMATION_WRITTEN_YES" in task["notes"]
    assert "SCOPE_NARROWED_TO_SINGLE_EXAMPLE_NO" in task["notes"]
    assert "FIRST_SLICE_IMPLEMENTED_NO" in task["notes"]
    assert "LOCAL_STATIC_JOB_IMPLEMENTED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-14 First-Slice Implementation Kickoff Gate" in html
    assert "phase_2b_14_first_slice_implementation_kickoff_gate.json" in html
