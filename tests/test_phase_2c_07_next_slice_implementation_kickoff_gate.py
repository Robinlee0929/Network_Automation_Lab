import copy
from pathlib import Path

import network_lab
import phase_2c_07_next_slice_implementation_kickoff_gate as phase_2c_07


DOC_PATH = Path("docs/phase_2c/phase_2c_07_next_slice_implementation_kickoff_gate.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_07():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-07 Next-Slice Implementation Kickoff Gate" not in agents_text
    assert "phase_2c_07_next_slice_implementation_kickoff_gate" not in agents_text


def test_phase_2c_07_markdown_artifact_exists_and_has_required_separation():
    text = _doc_text()

    assert "# Phase 2C-07 Next-Slice Implementation Kickoff Gate - Authorization Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Selected Next Slice",
        "## Candidate Source",
        "## Authorization Criteria",
        "## Safety Dependency",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Authorization Decision",
        "## Rationale",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "SCOPE_CONFIRMATION_WRITTEN: YES",
        "PHASE_2C_04_READ: YES",
        "PHASE_2C_05_READ: YES",
        "PHASE_2C_06_READ: YES",
        "AUTHORIZATION_GATE_ONLY: YES",
        "SELECTED_NEXT_SLICE: artifact_validation_job",
        "NEXT_SLICE_AUTHORIZED_FOR_PHASE_2C_08: YES",
        "PHASE_2C_08_STARTED: NO",
        "IMPLEMENTATION_ADDED: NO",
        "ARTIFACT_VALIDATION_JOB_IMPLEMENTED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "REAL_COMMAND_EXECUTION_ADDED: NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_07.FINAL_VERDICT in text


def test_phase_2c_07_builds_authorization_only_report():
    report = phase_2c_07.build_phase_2c_07_next_slice_implementation_kickoff_gate_report()

    assert report["validation"]["valid"] is True
    assert report["authorization_decision"] == "AUTHORIZED_FOR_LATER_PHASE_2C_08_ONLY"
    assert report["selected_next_slice"] == "artifact_validation_job"
    assert report["selected_candidate_id"] == "candidate-02"
    assert report["phase_2c_04_source_review"]["observed_verdict"] == (
        "PHASE_2C_04_CANDIDATE_INVENTORY_DONE_NEXT_SLICE_LOCKED"
    )
    assert report["phase_2c_05_safety_delta_dependency_review"]["observed_verdict"] == (
        "PHASE_2C_05_SAFETY_DELTA_REVIEW_DONE_NEXT_SLICE_LOCKED"
    )
    assert report["phase_2c_06_final_selection_dependency_review"]["observed_verdict"] == (
        "PHASE_2C_06_FINAL_SELECTION_GATE_DONE_IMPLEMENTATION_LOCKED"
    )
    assert report["phase_2c_04_source_review"]["source_validation"]["valid"] is True
    assert report["phase_2c_05_safety_delta_dependency_review"]["source_validation"]["valid"] is True
    assert report["phase_2c_06_final_selection_dependency_review"]["source_validation"]["valid"] is True
    assert report["authorization_gate_only"] is True
    assert report["selected_next_slice_authorized_for_phase_2c_08"] is True
    assert report["phase_2c_08_started"] is False
    assert report["implementation_added"] is False
    assert report["artifact_validation_job_implemented"] is False


def test_phase_2c_07_authorization_criteria_all_pass_without_implementation():
    report = phase_2c_07.build_phase_2c_07_next_slice_implementation_kickoff_gate_report()

    assert len(report["authorization_criteria_reviews"]) == len(phase_2c_07.AUTHORIZATION_CRITERIA)
    assert all(item["status"] == "PASS" for item in report["authorization_criteria_reviews"])
    assert all(item["supports_authorization"] is True for item in report["authorization_criteria_reviews"])
    assert report["phase_2c_05_safety_delta_dependency_review"]["selected_candidate_delta_status"] == (
        phase_2c_07.PHASE_2C_05_SAFE_DELTA_STATUS
    )
    assert report["phase_2c_06_final_selection_dependency_review"]["selected_next_slice"] == "artifact_validation_job"
    assert report["phase_2c_06_final_selection_dependency_review"]["source_next_slice_authorized"] is False
    assert report["phase_2c_06_final_selection_dependency_review"]["source_phase_2c_08_started"] is False
    assert report["phase_2c_06_final_selection_dependency_review"]["source_implementation_added"] is False


def test_phase_2c_07_no_execution_flags_stay_disabled():
    report = phase_2c_07.build_phase_2c_07_next_slice_implementation_kickoff_gate_report()

    for flag_name, expected in phase_2c_07.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "phase_2c_08_started",
        "implementation_added",
        "artifact_validation_job_implemented",
        "runtime_behavior_added",
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
        "agent_loop_added",
        "real_command_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_07_rejects_tampered_implementation_or_unsafe_authorization():
    report = phase_2c_07.build_phase_2c_07_next_slice_implementation_kickoff_gate_report()
    tampered = copy.deepcopy(report)
    tampered["authorization_decision"] = "IMPLEMENT_ARTIFACT_VALIDATION_JOB"
    tampered["selected_next_slice"] = "different_candidate"
    tampered["selected_next_slice_authorized_for_phase_2c_08"] = False
    tampered["phase_2c_08_started"] = True
    tampered["implementation_added"] = True
    tampered["artifact_validation_job_implemented"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["worker_added"] = True
    tampered["agent_loop_added"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["provider_api_opened"] = True
    tampered["real_command_execution_added"] = True
    tampered["config_change_execution_added"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["authorization_criteria_reviews"][0]["status"] = "FAIL"

    validation = phase_2c_07.validate_phase_2c_07_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "NEXT_SLICE_AUTHORIZATION_BLOCKED" in validation["errors"]
    assert "AUTHORIZATION_DECISION_MISMATCH" in validation["errors"]
    assert "SELECTED_NEXT_SLICE_MISMATCH" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:selected_next_slice_authorized_for_phase_2c_08" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_08_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:artifact_validation_job_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_07_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-07 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-07 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_07.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-07 Next-Slice Implementation Kickoff Gate - Authorization Only" in output
    assert "Authorization decision: AUTHORIZED_FOR_LATER_PHASE_2C_08_ONLY" in output
    assert "phase_2c_04_read: true" in output
    assert "phase_2c_05_read: true" in output
    assert "phase_2c_06_read: true" in output
    assert "authorization_gate_only: true" in output
    assert "selected_next_slice: artifact_validation_job" in output
    assert "next_slice_authorized_for_phase_2c_08: true" in output
    assert "phase_2c_08_started: false" in output
    assert "implementation_added: false" in output
    assert "artifact_validation_job_implemented: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "scheduler_queue_broker_worker_agent_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "real_command_execution_added: false" in output
    assert "config_backup_or_change_behavior_added: false" in output
    assert f"[PASS] {phase_2c_07.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_07.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_07.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_07(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_07.TASK_NAME)

    assert task["task_id"] == "phase_2c_07_next_slice_implementation_kickoff_gate"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_07.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_07.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_07.DOC_PATH.as_posix() in task["report_paths"]
    assert "AUTHORIZATION_GATE_ONLY_YES" in task["notes"]
    assert "SELECTED_NEXT_SLICE_ARTIFACT_VALIDATION_JOB" in task["notes"]
    assert "NEXT_SLICE_AUTHORIZED_FOR_PHASE_2C_08_YES" in task["notes"]
    assert "PHASE_2C_08_STARTED_NO" in task["notes"]
    assert "IMPLEMENTATION_ADDED_NO" in task["notes"]
    assert "ARTIFACT_VALIDATION_JOB_IMPLEMENTED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_07.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-07 Next-Slice Implementation Kickoff Gate - Authorization Only" in html
    assert "phase_2c_07_next_slice_implementation_kickoff_gate.json" in html
