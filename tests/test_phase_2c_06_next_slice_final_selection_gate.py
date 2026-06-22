import copy
from pathlib import Path

import network_lab
import phase_2c_06_next_slice_final_selection_gate as phase_2c_06


DOC_PATH = Path("docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_06():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-06 Next-Slice Final Selection Gate" not in agents_text
    assert "phase_2c_06_next_slice_final_selection_gate" not in agents_text


def test_phase_2c_06_markdown_artifact_exists_and_has_required_separation():
    text = _doc_text()

    assert "# Phase 2C-06 Next-Slice Final Selection Gate - Planning Only" in text
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
        "PHASE_2C_04_READ: YES",
        "PHASE_2C_05_READ: YES",
        "CANDIDATE_SELECTED: YES",
        "SELECTED_NEXT_SLICE: artifact_validation_job",
        "NEXT_SLICE_AUTHORIZED: NO",
        "PHASE_2C_07_STARTED: NO",
        "PHASE_2C_08_STARTED: NO",
        "IMPLEMENTATION_ADDED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
    ):
        assert label in text
    assert phase_2c_06.FINAL_VERDICT in text


def test_phase_2c_06_builds_final_selection_gate_only_report():
    report = phase_2c_06.build_phase_2c_06_next_slice_final_selection_gate_report()

    assert report["validation"]["valid"] is True
    assert report["selection_decision"] == "FINAL_SELECTION_GATE_ONLY"
    assert report["phase_2c_04_source_review"]["observed_verdict"] == (
        "PHASE_2C_04_CANDIDATE_INVENTORY_DONE_NEXT_SLICE_LOCKED"
    )
    assert report["phase_2c_05_safety_delta_dependency_review"]["observed_verdict"] == (
        "PHASE_2C_05_SAFETY_DELTA_REVIEW_DONE_NEXT_SLICE_LOCKED"
    )
    assert report["phase_2c_04_source_review"]["source_validation"]["valid"] is True
    assert report["phase_2c_05_safety_delta_dependency_review"]["source_validation"]["valid"] is True
    assert report["final_selection_gate_only"] is True
    assert report["phase_2c_04_read"] is True
    assert report["phase_2c_05_read"] is True
    assert report["candidate_selected"] is True
    assert report["selected_candidate_id"] == phase_2c_06.SELECTED_CANDIDATE_ID
    assert report["selected_next_slice"] == phase_2c_06.SELECTED_NEXT_SLICE
    assert report["next_slice_authorized"] is False
    assert report["phase_2c_07_started"] is False
    assert report["phase_2c_08_started"] is False
    assert report["implementation_added"] is False


def test_phase_2c_06_selects_exactly_one_safe_candidate_without_authorization():
    report = phase_2c_06.build_phase_2c_06_next_slice_final_selection_gate_report()

    selected = [candidate for candidate in report["candidate_selection_reviews"] if candidate["selected"] is True]

    assert len(selected) == 1
    assert selected[0]["candidate_id"] == "candidate-02"
    assert selected[0]["example_job_type"] == "artifact validation job"
    assert selected[0]["phase_2c_05_delta_status"] == phase_2c_06.PHASE_2C_05_SAFE_DELTA_STATUS
    assert selected[0]["requires_expanded_forbidden_scope"] is False
    assert report["phase_2c_05_safety_delta_dependency_review"]["all_candidates_safe_within_planning_boundary"] is True
    assert report["next_slice_authorized"] is False
    assert report["phase_2c_07_started"] is False
    assert report["phase_2c_08_started"] is False


def test_phase_2c_06_no_execution_flags_stay_disabled():
    report = phase_2c_06.build_phase_2c_06_next_slice_final_selection_gate_report()

    for flag_name, expected in phase_2c_06.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "next_slice_authorized",
        "phase_2c_07_started",
        "phase_2c_08_started",
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
        "agent_loop_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_06_rejects_tampered_authorization_implementation_or_unsafe_selection():
    report = phase_2c_06.build_phase_2c_06_next_slice_final_selection_gate_report()
    tampered = copy.deepcopy(report)
    tampered["selection_decision"] = "IMPLEMENT_SELECTED_SLICE"
    tampered["next_slice_authorized"] = True
    tampered["phase_2c_07_started"] = True
    tampered["phase_2c_08_started"] = True
    tampered["implementation_added"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["candidate_selection_reviews"][1]["phase_2c_05_delta_status"] = "UNACCEPTABLE_NEW_SAFETY_DELTA"

    validation = phase_2c_06.validate_phase_2c_06_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SELECTION_DECISION_MISMATCH" in validation["errors"]
    assert "NO_SAFE_NEXT_SLICE_SELECTED" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_07_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_08_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_06_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-06 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-06 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_06.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-06 Next-Slice Final Selection Gate - Planning Only" in output
    assert "Selection decision: FINAL_SELECTION_GATE_ONLY" in output
    assert "phase_2c_04_read: true" in output
    assert "phase_2c_05_read: true" in output
    assert "final_selection_gate_only: true" in output
    assert "candidate_selected: true" in output
    assert "selected_candidate_id: candidate-02" in output
    assert "selected_next_slice: artifact_validation_job" in output
    assert "next_slice_authorized: false" in output
    assert "phase_2c_07_started: false" in output
    assert "phase_2c_08_started: false" in output
    assert "implementation_added: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_06.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_06.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_06.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_06(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_06.TASK_NAME)

    assert task["task_id"] == "phase_2c_06_next_slice_final_selection_gate"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_06.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_06.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_06.DOC_PATH.as_posix() in task["report_paths"]
    assert "FINAL_SELECTION_GATE_ONLY_YES" in task["notes"]
    assert "CANDIDATE_SELECTED_YES" in task["notes"]
    assert "SELECTED_NEXT_SLICE_ARTIFACT_VALIDATION_JOB" in task["notes"]
    assert "NEXT_SLICE_AUTHORIZED_NO" in task["notes"]
    assert "PHASE_2C_07_STARTED_NO" in task["notes"]
    assert "PHASE_2C_08_STARTED_NO" in task["notes"]
    assert "IMPLEMENTATION_ADDED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_06.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-06 Next-Slice Final Selection Gate - Planning Only" in html
    assert "phase_2c_06_next_slice_final_selection_gate.json" in html
