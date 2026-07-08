import copy
from pathlib import Path

import network_lab
import phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review as readiness
from report_file_utils import path_exists, read_text_with_long_path


DOC_PATH = Path("docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_06():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-06 Implementation Entry Gate and First-Slice Readiness Review" not in agents_text
    assert "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review" not in agents_text


def test_phase_2b_06_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-06 Implementation Entry Gate and First-Slice Readiness Review" in text
    for section in (
        "## 1. Scope Confirmation",
        "## 2. Phase 2B-00 Through Phase 2B-05 Consolidation",
        "## 3. Implementation Entry Conditions",
        "## 4. First-Slice Readiness Definition",
        "## 5. Go / No-Go Verdict",
        "## 6. Explicit Non-Implementation Statement",
        "## 7. CLI / Report Integration",
    ):
        assert section in text
    assert "GO_TO_DEFINE_FIRST_SLICE_PLANNING_ONLY" in text


def test_phase_2b_06_scope_is_phase_wide_and_examples_only():
    report = readiness.build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    text = _doc_text()

    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(readiness.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    for job_type in readiness.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "These job types are examples only. They do not narrow Phase 2B-06" in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = readiness.validate_phase_2b_06_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_phase_2b_06_references_phase_2b_00_through_05_and_phase_2b_05_dedup_control():
    report = readiness.build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    text = _doc_text()

    phases = {item["phase"] for item in report["phase_2b_00_through_05_consolidation"]}
    assert phases == {
        "Phase 2B-00",
        "Phase 2B-00A",
        "Phase 2B-01",
        "Phase 2B-02",
        "Phase 2B-03",
        "Phase 2B-04",
        "Phase 2B-05",
    }
    for phrase in (
        "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "Phase 2B-03 scope confirmation before implementation",
        "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    ):
        assert phrase in text
    assert report["phase_2b_05_controls_safety_deduplication"] is True
    assert report["safety_matrix_policy"] == "do_not_create_second_safety_matrix"
    assert "Phase 2B-05 controls safety de-duplication" in text


def test_phase_2b_06_entry_conditions_and_first_slice_readiness_definition():
    report = readiness.build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    text = _doc_text()

    categories = {item["category"] for item in report["implementation_entry_conditions"]}
    assert categories == {item["category"] for item in readiness.ENTRY_CONDITIONS}
    assert all(item["status"] == "PASS" for item in report["implementation_entry_conditions"])
    for category in (
        "scope remains phase-wide",
        "safety gates are reused, not duplicated",
        "implementation slice is minimal and reversible",
        "no runner / adapter / execution is enabled during this task",
        "no provider / API / model calls are enabled",
        "no live-device access is introduced",
        "first slice has clear non-execution boundaries",
        "first slice has evidence and report expectations",
        "first slice has rollback / stop conditions",
        "first slice has explicit Go / No-Go criteria",
    ):
        assert category in categories
        assert category in text

    readiness_definition = report["first_slice_readiness_definition"]
    for field in (
        "purpose",
        "minimum_inputs",
        "minimum_outputs",
        "safety_preconditions",
        "non_execution_proof",
        "expected_report_evidence",
        "stop_conditions",
        "validation_expectations",
    ):
        assert field in readiness_definition
    assert "This section defines only what a future first implementation slice planning artifact is allowed to be" in text


def test_phase_2b_06_forbidden_scope_and_non_implementation_flags_stay_locked():
    report = readiness.build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()
    text = _doc_text()

    assert report["validation"]["valid"] is True
    assert report["second_safety_matrix_created"] is False
    assert report["first_slice_implemented"] is False
    assert report["runner_enabled"] is False
    assert report["adapter_enabled"] is False
    assert report["execution_path_implemented"] is False
    assert report["provider_api_model_calls_enabled"] is False
    assert report["provider_calls_enabled"] is False
    assert report["api_calls_enabled"] is False
    assert report["model_calls_enabled"] is False
    assert report["live_device_access_enabled"] is False
    for phrase in (
        "No runner implemented.",
        "No adapter implemented.",
        "No execution path implemented.",
        "No provider/API/model calls enabled.",
        "No live-device access enabled.",
        "No second safety matrix created.",
        "No Phase 2B implementation slice implemented.",
    ):
        assert phrase in text

    tampered = copy.deepcopy(report)
    tampered["second_safety_matrix_created"] = True
    tampered["provider_api_model_calls_enabled"] = True
    validation = readiness.validate_phase_2b_06_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:second_safety_matrix_created" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:provider_api_model_calls_enabled" in validation["errors"]


def test_phase_2b_06_machine_readable_verdict_is_planning_only():
    report = readiness.build_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review_report()

    assert report["go_no_go_verdict"] == readiness.FINAL_VERDICT
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": readiness.FINAL_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "FIRST_SLICE_DEFINITION_ALLOWED_NEXT_PLANNING_ONLY": "YES",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
        "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
        "LIVE_DEVICE_ACCESS_ENABLED": "NO",
    }
    assert "does not authorize implementation directly" in report["verdict_explanation"]


def test_cli_writes_phase_2b_06_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-06 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-06 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", readiness.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-06 Implementation Entry Gate and First-Slice Readiness Review" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "phase_2b_05_controls_safety_deduplication: true" in output
    assert "second_safety_matrix_created: false" in output
    assert "first_slice_implemented: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "execution_path_implemented: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert "live_device_access_enabled: false" in output
    assert f"[PASS] {readiness.FINAL_VERDICT}" in output
    assert path_exists(tmp_path / readiness.REPORT_JSON)
    assert path_exists(tmp_path / readiness.REPORT_HTML)


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == readiness.TASK_NAME)

    assert task["task_id"] == "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert readiness.REPORT_JSON.as_posix() in task["report_paths"]
    assert readiness.REPORT_HTML.as_posix() in task["report_paths"]
    assert readiness.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_06_IMPLEMENTATION_ENTRY_GATE_READY" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_FALSE" in task["notes"]
    assert "FIRST_SLICE_IMPLEMENTED_FALSE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE" in task["notes"]
    assert "PROVIDER_API_MODEL_CALLS_ENABLED_FALSE" in task["notes"]

    assert network_lab.main(["--task", readiness.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Phase 2B-06 Implementation Entry Gate and First-Slice Readiness Review" in html
    assert "phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.json" in html
