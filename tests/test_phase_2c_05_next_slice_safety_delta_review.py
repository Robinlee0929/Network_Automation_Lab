import copy
from pathlib import Path

import network_lab
import phase_2c_05_next_slice_safety_delta_review as phase_2c_05


DOC_PATH = Path("docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2c_05():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-05 Next-Slice Safety Delta Review" not in agents_text
    assert "phase_2c_05_next_slice_safety_delta_review" not in agents_text


def test_phase_2c_05_markdown_artifact_exists_and_has_required_separation():
    text = _doc_text()

    assert "# Phase 2C-05 Next-Slice Safety Delta Review - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Candidate Source",
        "## Example Job Types",
        "## Safety Delta Review Criteria",
        "## Forbidden Scope",
        "## Existing Artifacts To Reference",
        "## Implementation Boundary",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "PHASE_2C_04_READ: YES",
        "SAFETY_DELTA_REVIEW_ONLY: YES",
        "CANDIDATE_SELECTED: NO",
        "NEXT_SLICE_AUTHORIZED: NO",
        "PHASE_2C_06_STARTED: NO",
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
    assert phase_2c_05.FINAL_VERDICT in text


def test_phase_2c_05_builds_safety_delta_review_only_report():
    report = phase_2c_05.build_phase_2c_05_next_slice_safety_delta_review_report()

    assert report["validation"]["valid"] is True
    assert report["review_decision"] == "SAFETY_DELTA_REVIEW_ONLY"
    assert report["phase_2c_04_source_review"]["observed_verdict"] == (
        "PHASE_2C_04_CANDIDATE_INVENTORY_DONE_NEXT_SLICE_LOCKED"
    )
    assert report["phase_2c_04_source_review"]["source_validation"]["valid"] is True
    assert report["phase_2c_04_read"] is True
    assert report["safety_delta_review_only"] is True
    assert report["candidate_selected"] is False
    assert report["next_slice_authorized"] is False
    assert report["phase_2c_06_started"] is False
    assert report["phase_2c_07_started"] is False
    assert report["phase_2c_08_started"] is False
    assert report["implementation_added"] is False


def test_phase_2c_05_reviews_phase_2c_04_candidates_without_selection_or_authorization():
    report = phase_2c_05.build_phase_2c_05_next_slice_safety_delta_review_report()

    assert report["example_job_types"] == list(phase_2c_05.EXAMPLE_JOB_TYPES)
    assert len(report["candidate_safety_delta_reviews"]) == len(phase_2c_05.EXAMPLE_JOB_TYPES)
    assert {
        candidate["example_job_type"] for candidate in report["candidate_safety_delta_reviews"]
    } == set(phase_2c_05.EXAMPLE_JOB_TYPES)
    assert all(
        candidate["delta_status"] == phase_2c_05.DELTA_STATUS
        for candidate in report["candidate_safety_delta_reviews"]
    )
    assert all(candidate["candidate_selected"] is False for candidate in report["candidate_safety_delta_reviews"])
    assert "selected_candidate" not in report
    assert "authorized_candidate" not in report


def test_phase_2c_05_safety_delta_fields_and_no_execution_flags_stay_disabled():
    report = phase_2c_05.build_phase_2c_05_next_slice_safety_delta_review_report()

    for flag_name, expected in phase_2c_05.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for candidate in report["candidate_safety_delta_reviews"]:
        for field in phase_2c_05.SAFETY_DELTA_FIELDS:
            assert candidate[field] is False
    for flag_name in (
        "candidate_selected",
        "next_slice_authorized",
        "phase_2c_06_started",
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


def test_phase_2c_05_rejects_tampered_selection_authorization_or_safety_delta():
    report = phase_2c_05.build_phase_2c_05_next_slice_safety_delta_review_report()
    tampered = copy.deepcopy(report)
    tampered["review_decision"] = "SELECT_NEXT_SLICE"
    tampered["candidate_selected"] = True
    tampered["next_slice_authorized"] = True
    tampered["phase_2c_06_started"] = True
    tampered["implementation_added"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["ssh_netconf_restconf_touched"] = True
    tampered["provider_api_opened"] = True
    tampered["model_opened"] = True
    tampered["secrets_touched"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["candidate_safety_delta_reviews"][0]["candidate_selected"] = True
    tampered["candidate_safety_delta_reviews"][0]["new_runtime_execution_behavior"] = True

    validation = phase_2c_05.validate_phase_2c_05_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "REVIEW_DECISION_MISMATCH" in validation["errors"]
    assert "CANDIDATE_SELECTED:candidate-01" in validation["errors"]
    assert "SAFETY_DELTA_FIELD_TRUE:candidate-01:new_runtime_execution_behavior" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:candidate_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:next_slice_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:phase_2c_06_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_05_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-05 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-05 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_05.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-05 Next-Slice Safety Delta Review - Planning Only" in output
    assert "Review decision: SAFETY_DELTA_REVIEW_ONLY" in output
    assert "phase_2c_04_read: true" in output
    assert "safety_delta_review_only: true" in output
    assert "candidate_count: 7" in output
    assert "candidate_selected: false" in output
    assert "next_slice_authorized: false" in output
    assert "phase_2c_06_started: false" in output
    assert "phase_2c_07_started: false" in output
    assert "phase_2c_08_started: false" in output
    assert "implementation_added: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {phase_2c_05.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_05.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_05.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_05(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_05.TASK_NAME)

    assert task["task_id"] == "phase_2c_05_next_slice_safety_delta_review"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_05.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_05.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_05.DOC_PATH.as_posix() in task["report_paths"]
    assert "SAFETY_DELTA_REVIEW_ONLY_YES" in task["notes"]
    assert "CANDIDATE_SELECTED_NO" in task["notes"]
    assert "NEXT_SLICE_AUTHORIZED_NO" in task["notes"]
    assert "PHASE_2C_06_STARTED_NO" in task["notes"]
    assert "IMPLEMENTATION_ADDED_NO" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_05.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-05 Next-Slice Safety Delta Review - Planning Only" in html
    assert "phase_2c_05_next_slice_safety_delta_review.json" in html
