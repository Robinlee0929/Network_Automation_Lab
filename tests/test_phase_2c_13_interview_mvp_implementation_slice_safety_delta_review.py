import copy
from pathlib import Path

import network_lab
import phase_2c_12_interview_mvp_implementation_slice_candidate_inventory as phase_2c_12
import phase_2c_13_interview_mvp_implementation_slice_safety_delta_review as phase_2c_13


DOC_PATH = Path("docs/phase_2c/phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.md")


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


def test_agents_md_is_not_modified_for_phase_2c_13():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2C-13 Interview MVP Implementation Slice Safety Delta Review" not in agents_text
    assert "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review" not in agents_text


def test_phase_2c_13_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2C-13 Interview MVP Implementation Slice Safety Delta Review - Planning Only" in text
    for section in (
        "## Scope Confirmation",
        "## Phase Goal",
        "## Candidate Source",
        "## Example Job Types",
        "## Safety Matrix Rule",
        "## Safety Delta Review Criteria",
        "## Candidate Safety Delta Reviews",
        "## Safety Decision Output",
        "## Forbidden Scope Confirmation",
        "## Existing Artifacts Referenced",
        "## Implementation Boundary",
        "## Non-Execution Statement",
        "## Final Verdict",
    ):
        assert section in text
    for label in (
        "CANDIDATE_SOURCE_PHASE_2C_12_ONLY: YES",
        "NO_NEW_CANDIDATES_INVENTED: YES",
        "SAFETY_DELTA_REVIEW_ONLY: YES",
        "UNIQUE_SLICE_SELECTED: NO",
        "IMPLEMENTATION_AUTHORIZED: NO",
        "IMPLEMENTATION_STARTED: NO",
        "SECOND_SAFETY_MATRIX_CREATED: NO",
        "NEXT_PHASE_STARTED: NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED: NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED: NO",
        "CONFIG_BACKUP_CHANGE_ADDED: NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED: NO",
    ):
        assert label in text
    assert "The existing safety matrix remains the single source of truth" in text
    assert phase_2c_13.FINAL_VERDICT in text


def test_phase_2c_13_builds_safety_delta_review_only_report():
    report = phase_2c_13.build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        Path.cwd()
    )

    assert report["validation"]["valid"] is True
    assert report["review_decision"] == "SAFETY_DELTA_REVIEW_ONLY"
    assert report["phase_2c_12_source_review"]["observed_verdict"] == phase_2c_12.FINAL_VERDICT
    assert report["phase_2c_12_source_review"]["source_validation"]["valid"] is True
    assert report["candidate_source_phase_2c_12_only"] is True
    assert report["no_new_candidates_invented"] is True
    assert report["safety_delta_review_only"] is True
    assert report["unique_slice_selected"] is False
    assert report["implementation_authorized"] is False
    assert report["implementation_started"] is False
    assert report["second_safety_matrix_created"] is False


def test_phase_2c_13_uses_only_phase_2c_12_candidate_inventory():
    report = phase_2c_13.build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        Path.cwd()
    )

    source_ids = {candidate["candidate_id"] for candidate in phase_2c_12.CANDIDATE_INVENTORY}
    observed_ids = {candidate["candidate_id"] for candidate in report["candidate_safety_delta_reviews"]}

    assert observed_ids == source_ids
    assert report["phase_2c_12_source_review"]["candidate_ids"] == [
        candidate["candidate_id"] for candidate in phase_2c_12.CANDIDATE_INVENTORY
    ]
    assert "selected_candidate" not in report
    assert "authorized_candidate" not in report


def test_phase_2c_13_safety_delta_fields_and_no_execution_flags_stay_disabled():
    report = phase_2c_13.build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        Path.cwd()
    )

    for flag_name, expected in phase_2c_13.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for candidate in report["candidate_safety_delta_reviews"]:
        for field in phase_2c_13.SAFETY_DELTA_FIELDS:
            assert candidate[field] is False
        assert candidate["candidate_selected"] is False
        assert candidate["candidate_authorized"] is False
        assert candidate["implementation_started"] is False
    for flag_name in (
        "unique_slice_selected",
        "implementation_authorized",
        "implementation_started",
        "phase_2c_14_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "queue_added",
        "scheduler_added",
        "worker_added",
        "ai_loop_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    ):
        assert report[flag_name] is False


def test_phase_2c_13_rejects_tampered_selection_authorization_or_safety_delta():
    report = phase_2c_13.build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        Path.cwd()
    )
    tampered = copy.deepcopy(report)
    tampered["review_decision"] = "SELECT_UNIQUE_SLICE"
    tampered["unique_slice_selected"] = True
    tampered["implementation_authorized"] = True
    tampered["implementation_started"] = True
    tampered["runner_added"] = True
    tampered["adapter_added"] = True
    tampered["execution_path_added"] = True
    tampered["queue_added"] = True
    tampered["ssh_netconf_restconf_live_device_touched"] = True
    tampered["provider_api_model_secrets_touched"] = True
    tampered["second_safety_matrix_created"] = True
    tampered["candidate_safety_delta_reviews"][0]["candidate_selected"] = True
    tampered["candidate_safety_delta_reviews"][0]["candidate_authorized"] = True
    tampered["candidate_safety_delta_reviews"][0]["would_require_live_device_access"] = True

    validation = phase_2c_13.validate_phase_2c_13_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "REVIEW_DECISION_MISMATCH" in validation["errors"]
    assert "CANDIDATE_SELECTED:candidate-01" in validation["errors"]
    assert "CANDIDATE_AUTHORIZED:candidate-01" in validation["errors"]
    assert "SAFETY_DELTA_FIELD_TRUE:candidate-01:would_require_live_device_access" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:unique_slice_selected" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:implementation_started" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:adapter_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]


def test_cli_writes_phase_2c_13_without_execution_paths(tmp_path, capsys, monkeypatch):
    _materialize_reference(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2C-13 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2C-13 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", phase_2c_13.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2C-13 Interview MVP Implementation Slice Safety Delta Review - Planning Only" in output
    assert "candidate_source_phase_2c_12_only: true" in output
    assert "no_new_candidates_invented: true" in output
    assert "safety_delta_review_only: true" in output
    assert "candidate_count: 6" in output
    assert "unique_slice_selected: false" in output
    assert "implementation_authorized: false" in output
    assert "implementation_started: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "queue_scheduler_worker_ai_loop_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert "second_safety_matrix_created: false" in output
    assert "next_phase_started: false" in output
    assert f"[PASS] {phase_2c_13.FINAL_VERDICT}" in output
    assert (tmp_path / phase_2c_13.REPORT_JSON).exists()
    assert (tmp_path / phase_2c_13.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility_for_phase_2c_13(tmp_path):
    _materialize_reference(tmp_path)
    task = next(task for task in network_lab.list_tasks() if task["id"] == phase_2c_13.TASK_NAME)

    assert task["task_id"] == "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review"
    assert task["day"] == "Phase 2C"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert phase_2c_13.REPORT_JSON.as_posix() in task["report_paths"]
    assert phase_2c_13.REPORT_HTML.as_posix() in task["report_paths"]
    assert phase_2c_13.DOC_PATH.as_posix() in task["report_paths"]
    assert "CANDIDATE_SOURCE_PHASE_2C_12_ONLY_YES" in task["notes"]
    assert "NO_NEW_CANDIDATES_INVENTED_YES" in task["notes"]
    assert "UNIQUE_SLICE_SELECTED_NO" in task["notes"]
    assert "IMPLEMENTATION_AUTHORIZED_NO" in task["notes"]
    assert "IMPLEMENTATION_STARTED_NO" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_NO" in task["notes"]

    assert network_lab.main(["--task", phase_2c_13.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2C-13 Interview MVP Implementation Slice Safety Delta Review - Planning Only" in html
    assert "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.json" in html
