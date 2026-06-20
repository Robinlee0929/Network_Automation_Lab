import copy
from pathlib import Path

import network_lab
import phase_2b_07_first_slice_definition_pack as definition_pack


DOC_PATH = Path("docs/phase_2b/phase_2b_07_first_slice_definition_pack.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_07():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-07 First-Slice Definition Pack" not in agents_text
    assert "phase_2b_07_first_slice_definition_pack" not in agents_text


def test_phase_2b_07_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-07 First-Slice Definition Pack" in text
    for section in (
        "## Purpose",
        "## Scope Confirmation",
        "## Relationship to Phase 2B-06",
        "## First Minimal Safe Slice Definition",
        "## In-Scope Boundaries",
        "## Out-of-Scope Boundaries",
        "## Existing Safety Gates That Remain Authoritative",
        "## Existing Artifacts Referenced",
        "## Example Job Types, Not Scope Reduction",
        "## Future Implementation Preconditions",
        "## Future Acceptance Criteria",
        "## Stop Conditions",
        "## Non-Duplication Statement",
        "## Final Verdict",
    ):
        assert section in text
    assert definition_pack.FINAL_VERDICT in text


def test_phase_2b_07_scope_is_phase_wide_and_examples_only():
    report = definition_pack.build_phase_2b_07_first_slice_definition_pack_report()
    text = _doc_text()

    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(definition_pack.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    for job_type in definition_pack.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "These job types are examples only." in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = definition_pack.validate_phase_2b_07_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_phase_2b_07_defines_first_slice_without_implementing_it():
    report = definition_pack.build_phase_2b_07_first_slice_definition_pack_report()
    text = _doc_text()

    assert report["first_minimal_safe_slice"]["name"] == "local_static_job_definition_and_evidence_contract_slice"
    assert "local_static_job_definition_and_evidence_contract_slice" in text
    assert report["first_slice_defined"] is True
    assert report["first_slice_implemented"] is False
    assert report["phase_2b_implementation_allowed"] is False
    assert report["phase_2b_implementation_started"] is False
    assert "This task does not implement the slice." in text

    tampered = copy.deepcopy(report)
    tampered["first_slice_implemented"] = True
    validation = definition_pack.validate_phase_2b_07_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:first_slice_implemented" in validation["errors"]


def test_phase_2b_07_references_existing_gates_without_recreating_or_rerunning():
    report = definition_pack.build_phase_2b_07_first_slice_definition_pack_report()
    text = _doc_text()

    assert report["phase_2b_06_relationship"]["referenced_verdict"] == definition_pack.PHASE_2B_06_VERDICT
    assert report["phase_2b_06_relationship"]["entry_gate_review_rerun"] is False
    assert report["entry_gate_review_rerun"] is False
    assert report["safety_gates_recreated"] is False
    assert report["second_safety_matrix_created"] is False
    assert "Phase 2B-05 remains authoritative for de-duplication" in text
    assert "It does not re-run the Phase 2B-06" in text
    assert "This is not a readiness review." in text

    gate_artifacts = {item["artifact"] for item in report["authoritative_safety_gates"]}
    for artifact in (
        "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
    ):
        assert artifact in gate_artifacts
        assert artifact in text


def test_phase_2b_07_forbidden_capabilities_stay_disabled():
    report = definition_pack.build_phase_2b_07_first_slice_definition_pack_report()

    assert report["validation"]["valid"] is True
    for flag_name, expected in definition_pack.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": definition_pack.FINAL_VERDICT,
        "PHASE_2B_06_VERDICT_REFERENCED": definition_pack.PHASE_2B_06_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_DEFINED": "YES",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "SAFETY_GATES_RECREATED": "NO",
        "ENTRY_GATE_REVIEW_RERUN": "NO",
        "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
        "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
        "LIVE_DEVICE_ACCESS_ENABLED": "NO",
    }

    tampered = copy.deepcopy(report)
    tampered["runner_enabled"] = True
    tampered["provider_api_model_calls_enabled"] = True
    validation = definition_pack.validate_phase_2b_07_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_enabled" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:provider_api_model_calls_enabled" in validation["errors"]


def test_cli_writes_phase_2b_07_definition_pack_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-07 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-07 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", definition_pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-07 First-Slice Definition Pack" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "safety_gates_recreated: false" in output
    assert "entry_gate_review_rerun: false" in output
    assert "first_slice_implemented: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "execution_path_implemented: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert "live_device_access_enabled: false" in output
    assert f"[PASS] {definition_pack.FINAL_VERDICT}" in output
    assert (tmp_path / definition_pack.REPORT_JSON).exists()
    assert (tmp_path / definition_pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == definition_pack.TASK_NAME)

    assert task["task_id"] == "phase_2b_07_first_slice_definition_pack"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert definition_pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert definition_pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert definition_pack.DOC_PATH.as_posix() in task["report_paths"]
    assert definition_pack.FINAL_VERDICT in task["notes"]
    assert "SAFETY_GATES_RECREATED_FALSE" in task["notes"]
    assert "ENTRY_GATE_REVIEW_RERUN_FALSE" in task["notes"]
    assert "FIRST_SLICE_IMPLEMENTED_FALSE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE" in task["notes"]

    assert network_lab.main(["--task", definition_pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-07 First-Slice Definition Pack" in html
    assert "phase_2b_07_first_slice_definition_pack.json" in html
