import copy
from pathlib import Path

import network_lab
import phase_2b_04_safety_artifact_crosswalk_gap_review as crosswalk


def test_agents_md_is_not_modified_for_phase_2b_04():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-04 Safety Artifact Crosswalk and Gap Review" not in agents_text
    assert "phase_2b_04_safety_artifact_crosswalk_gap_review" not in agents_text


def test_phase_2b_04_report_has_required_crosswalk_and_gap_fields():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    assert report["phase"] == "2B-04"
    assert report["task"] == crosswalk.TASK_NAME
    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    for field in (
        "scope_confirmation",
        "crosswalk",
        "gap_review",
        "non_duplication_statement",
        "safety_boundary_statement",
        "next_step_recommendation",
        "forbidden_capability_matrix",
        "machine_readable_verdict",
    ):
        assert field in report


def test_scope_confirmation_is_phase_wide_and_not_one_example():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    assert report["scope"] == crosswalk.SCOPE
    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(crosswalk.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types"]) == 6
    assert set(report["example_job_types"]) != {"vrrp_validation"}

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = crosswalk.validate_phase_2b_04_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_crosswalk_rows_have_required_columns_and_reference_expected_artifacts():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    rows = report["crosswalk"]
    required_fields = {
        "artifact_source",
        "phase_day",
        "safety_topic_covered",
        "coverage_status",
        "related_evidence_or_file_reference",
        "notes",
    }
    assert len(rows) == len(crosswalk.CROSSWALK_ROWS)
    assert all(required_fields <= set(row) for row in rows)
    assert {row["coverage_status"] for row in rows} == set(crosswalk.COVERAGE_STATUS_CATEGORIES)

    references = " ".join(row["related_evidence_or_file_reference"] for row in rows)
    assert "AGENTS.md" in references
    assert "phase_2a_03_dry_run_job_plan_gate.py" in references
    assert "phase_2a_11_phase_closure_final_readiness_review.py" in references
    assert "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md" in references
    assert "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md" in references
    assert "No phase_2b_03_*" in references

    tampered = copy.deepcopy(report)
    tampered["crosswalk"][0].pop("coverage_status")
    validation = crosswalk.validate_phase_2b_04_report(tampered)
    assert validation["valid"] is False
    assert any(error.startswith("CROSSWALK_ITEM_FIELDS_MISSING:") for error in validation["errors"])


def test_gap_review_contains_required_sections_and_non_duplication_lock():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    assert set(report["gap_review"]) == {
        "already_covered",
        "partially_covered",
        "missing_deferred",
        "not_allowed_current_phase",
    }
    assert report["gap_review"]["already_covered"]
    assert report["gap_review"]["partially_covered"]
    assert report["gap_review"]["missing_deferred"]
    assert report["gap_review"]["not_allowed_current_phase"]
    assert report["new_safety_matrix_created"] is False
    assert report["non_duplication_statement"] == crosswalk.NON_DUPLICATION_STATEMENT

    tampered = copy.deepcopy(report)
    tampered["new_safety_matrix_created"] = True
    validation = crosswalk.validate_phase_2b_04_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:new_safety_matrix_created" in validation["errors"]


def test_forbidden_capabilities_stay_disabled_and_not_allowed():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    matrix = {item["capability"]: item for item in report["forbidden_capability_matrix"]}
    assert set(matrix) == set(crosswalk.FORBIDDEN_CAPABILITIES)
    assert all(item["enabled"] is False for item in matrix.values())
    assert all(item["allowed_by_phase_2b_04"] is False for item in matrix.values())
    for flag_name, expected in crosswalk.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["provider_api_model_calls_enabled"] = True
    tampered["forbidden_capability_matrix"][0]["allowed_by_phase_2b_04"] = True
    validation = crosswalk.validate_phase_2b_04_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:provider_api_model_calls_enabled" in validation["errors"]
    assert any(error.startswith("FORBIDDEN_CAPABILITY_ENABLED:") for error in validation["errors"])


def test_machine_readable_verdict_matches_required_phase_2b_04_lock():
    report = crosswalk.build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()

    assert report["final_verdict"] == crosswalk.FINAL_VERDICT
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": crosswalk.FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "NEW_SAFETY_MATRIX_CREATED": "NO",
        "CROSSWALK_CREATED": "YES",
        "GAP_REVIEW_CREATED": "YES",
        "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
        "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
    }
    assert report["implementation_started"] is False
    assert report["runner_enabled"] is False
    assert report["adapter_enabled"] is False
    assert report["execution_allowed"] is False


def test_cli_writes_phase_2b_04_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-04 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-04 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", crosswalk.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-04 Safety Artifact Crosswalk and Gap Review" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "new_safety_matrix_created: false" in output
    assert "crosswalk_created: true" in output
    assert "gap_review_created: true" in output
    assert "implementation_started: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert f"[PASS] {crosswalk.FINAL_VERDICT}" in output
    assert (tmp_path / crosswalk.REPORT_JSON).exists()
    assert (tmp_path / crosswalk.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == crosswalk.TASK_NAME)

    assert task["task_id"] == "phase_2b_04_safety_artifact_crosswalk_gap_review"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert crosswalk.REPORT_JSON.as_posix() in task["report_paths"]
    assert crosswalk.REPORT_HTML.as_posix() in task["report_paths"]
    assert crosswalk.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_04_PLANNING_ONLY_CROSSWALK_GAP_REVIEW_COMPLETE" in task["notes"]
    assert "NEW_SAFETY_MATRIX_CREATED_FALSE" in task["notes"]
    assert "CROSSWALK_CREATED_TRUE" in task["notes"]
    assert "GAP_REVIEW_CREATED_TRUE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE" in task["notes"]

    assert network_lab.main(["--task", crosswalk.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-04 Safety Artifact Crosswalk and Gap Review" in html
    assert "phase_2b_04_safety_artifact_crosswalk_gap_review.json" in html
