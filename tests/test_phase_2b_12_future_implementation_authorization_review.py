import copy
from pathlib import Path

import network_lab
import phase_2b_12_future_implementation_authorization_review as review


DOC_PATH = Path("docs/phase_2b/phase_2b_12_future_implementation_authorization_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_12():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-12 Future Implementation Authorization Review" not in agents_text
    assert "phase_2b_12_future_implementation_authorization_review" not in agents_text


def test_phase_2b_12_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-12 Future Implementation Authorization Review - Planning Only" in text
    for section in (
        "## Purpose",
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Forbidden Scope",
        "## Existing Artifacts Referenced",
        "## Future Implementation Authorization Status",
        "## Missing Conditions Before Implementation",
        "## Scope Drift Risk Review",
        "## Planning-Only Boundary",
        "## Decision",
        "## Non-Authorization Statement",
    ):
        assert section in text
    assert review.FINAL_VERDICT in text
    assert "No implementation is authorized by this artifact." in text


def test_phase_2b_12_references_previous_phase_2b_chain_without_inventing_phase_2b_03():
    report = review.build_phase_2b_12_future_implementation_authorization_review_report()
    text = _doc_text()

    for artifact in (
        "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
        "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
        "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
        "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
        "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
        "docs/phase_2b/phase_2b_11_project_consolidation_and_implementation_entry_map.md",
    ):
        assert artifact in report["existing_artifacts_referenced"]
        assert artifact in text
    assert report["phase_2b_11_verdict_referenced"] == review.PHASE_2B_11_VERDICT
    assert "no concrete source, documentation, or test path was found" in text
    assert "does not invent" not in text.lower()


def test_phase_2b_12_authorization_status_and_missing_conditions_are_explicit():
    report = review.build_phase_2b_12_future_implementation_authorization_review_report()
    text = _doc_text()

    assert report["future_implementation_authorized"] is False
    assert report["phase_2b_remains_planning_only"] is True
    assert report["authorization_review"]["future_implementation_currently_allowed"] == "NO"
    assert report["authorization_review"]["phase_2b_must_remain_planning_only"] == "YES"
    assert report["missing_conditions_listed"] is True
    for condition in review.MISSING_CONDITIONS_BEFORE_IMPLEMENTATION:
        assert condition in text
    assert "Future implementation is not yet authorized." in text
    assert "Any future implementation must require explicit written authorization." in text


def test_phase_2b_12_scope_is_phase_wide_and_examples_only():
    report = review.build_phase_2b_12_future_implementation_authorization_review_report()
    text = _doc_text()

    assert set(report["example_job_types"]) == set(review.REQUIRED_JOB_TYPES)
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert report["example_job_types_treated_as_examples_only"] is True
    assert report["task_wording_narrows_phase_to_one_example"] is False
    for job_type in review.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "representative examples only" in text
    assert "does not select any one of them as an implementation target" in text


def test_phase_2b_12_forbidden_scope_and_no_execution_flags_stay_disabled():
    report = review.build_phase_2b_12_future_implementation_authorization_review_report()

    assert report["validation"]["valid"] is True
    for flag_name, expected in review.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    for flag_name in (
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_worker_added",
        "ssh_touched",
        "netconf_touched",
        "restconf_touched",
        "live_device_access_added",
        "real_device_inventory_access_added",
        "provider_calls_added",
        "api_calls_added",
        "model_calls_added",
        "secrets_handling_added",
        "frontend_api_integration_added",
        "production_workflow_added",
        "real_backup_execution_added",
        "real_configuration_change_added",
        "real_vrrp_execution_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "first_slice_implemented",
    ):
        assert report[flag_name] is False


def test_phase_2b_12_scope_drift_requires_scope_confirmation():
    report = review.build_phase_2b_12_future_implementation_authorization_review_report()
    tampered = copy.deepcopy(report)
    tampered["future_implementation_authorized"] = True
    tampered["task_wording_narrows_phase_to_one_example"] = True
    tampered["first_slice_implemented"] = True
    tampered["runner_added"] = True
    tampered["ssh_touched"] = True
    tampered["secrets_handling_added"] = True

    validation = review.validate_phase_2b_12_report(tampered)

    assert validation["valid"] is False
    assert "NEEDS_SCOPE_CONFIRMATION" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:future_implementation_authorized" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:task_wording_narrows_phase_to_one_example" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:first_slice_implemented" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_12_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-12 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-12 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", review.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-12 Future Implementation Authorization Review - Planning Only" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "future_implementation_authorized_by_this_task: false" in output
    assert "phase_2b_remains_planning_only: true" in output
    assert "missing_conditions_listed: true" in output
    assert "scope_drift_risk_reviewed: true" in output
    assert "needs_scope_confirmation_behavior_included: true" in output
    assert "day1_day160_rewritten_or_replaced: false" in output
    assert "second_safety_matrix_created: false" in output
    assert "first_slice_implemented: false" in output
    assert "runner_adapter_execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {review.FINAL_VERDICT}" in output
    assert (tmp_path / review.REPORT_JSON).exists()
    assert (tmp_path / review.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == review.TASK_NAME)

    assert task["task_id"] == "phase_2b_12_future_implementation_authorization_review"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert review.REPORT_JSON.as_posix() in task["report_paths"]
    assert review.REPORT_HTML.as_posix() in task["report_paths"]
    assert review.DOC_PATH.as_posix() in task["report_paths"]
    assert "FUTURE_IMPLEMENTATION_AUTHORIZED_FALSE" in task["notes"]
    assert "PHASE_2B_REMAINS_PLANNING_ONLY" in task["notes"]
    assert "MISSING_CONDITIONS_LISTED" in task["notes"]
    assert "SCOPE_DRIFT_RISK_REVIEWED" in task["notes"]
    assert "NEEDS_SCOPE_CONFIRMATION_BEHAVIOR_INCLUDED" in task["notes"]

    assert network_lab.main(["--task", review.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-12 Future Implementation Authorization Review - Planning Only" in html
    assert "phase_2b_12_future_implementation_authorization_review.json" in html
