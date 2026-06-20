import copy
from pathlib import Path

import network_lab
import phase_2b_09_first_slice_implementation_plan_pack as plan_pack


DOC_PATH = Path("docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_09():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-09 First-Slice Implementation Plan Pack" not in agents_text
    assert "phase_2b_09_first_slice_implementation_plan_pack" not in agents_text


def test_phase_2b_09_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only" in text
    for section in (
        "## Purpose",
        "## Input Authorization",
        "## Scope Confirmation",
        "### Phase Goal",
        "### Example Job Types",
        "### Forbidden Scope",
        "### Existing Artifacts to Reference",
        "### Implementation Boundary",
        "## Phase Goal",
        "## First-Slice Planning Target",
        "## In-Scope Planning Content",
        "## Out-of-Scope List",
        "## File Impact Plan",
        "## Step Sequence",
        "## Testing Strategy",
        "## Evidence Strategy",
        "## Rollback and Stop Conditions",
        "## Acceptance Criteria",
        "## Boundary Proof Checklist",
        "## Final Verdict",
    ):
        assert section in text
    assert plan_pack.FINAL_VERDICT in text
    assert "No implementation is authorized by this artifact." in text


def test_phase_2b_09_references_phase_2b_08_as_gate_without_duplication():
    report = plan_pack.build_phase_2b_09_first_slice_implementation_plan_pack_report()
    text = _doc_text()

    assert report["input_authorization"]["phase_2b_08_verdict_referenced"] == "GO_TO_2B_09_PLANNING_ONLY"
    assert report["input_authorization"]["phase_2b_08_role"] == "Gate"
    assert report["input_authorization"]["phase_2b_09_role"] == "Plan"
    assert report["input_authorization"]["phase_2b_08_gate_duplicated"] is False
    assert report["input_authorization"]["phase_2b_08_gate_rerun"] is False
    assert "Phase 2B-08 = Gate." in text
    assert "Phase 2B-09 = Plan." in text
    assert "does not re-run, duplicate, or replace the full Phase 2B-08 gate decision" in text

    tampered = copy.deepcopy(report)
    tampered["input_authorization"]["phase_2b_08_gate_duplicated"] = True
    validation = plan_pack.validate_phase_2b_09_report(tampered)
    assert validation["valid"] is False
    assert "PHASE_2B_08_GATE_DUPLICATED" in validation["errors"]


def test_phase_2b_09_scope_is_phase_wide_and_examples_only():
    report = plan_pack.build_phase_2b_09_first_slice_implementation_plan_pack_report()
    text = _doc_text()

    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(plan_pack.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    for job_type in plan_pack.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "These job types are examples only." in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = plan_pack.validate_phase_2b_09_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_phase_2b_09_includes_required_plan_pack_content():
    report = plan_pack.build_phase_2b_09_first_slice_implementation_plan_pack_report()
    text = _doc_text()

    assert report["first_slice_planning_target"]["planning_level_only"] is True
    assert report["first_slice_planning_target"]["name"] == "local_static_job_definition_and_evidence_contract_slice"
    for key in (
        "documentation_only_files",
        "registry_reporting_metadata",
        "tests",
        "explicitly_forbidden_runtime_execution_files",
    ):
        assert key in report["file_impact_plan"]
    assert len(report["step_sequence"]) == len(plan_pack.STEP_SEQUENCE)
    assert all("stop_gate" in item for item in report["step_sequence"])
    assert set(report["testing_strategy"]) == set(plan_pack.TESTING_STRATEGY)
    assert set(report["evidence_strategy"]) == set(plan_pack.EVIDENCE_STRATEGY)
    assert set(report["rollback_stop_conditions"]) == set(plan_pack.ROLLBACK_STOP_CONDITIONS)
    assert set(report["acceptance_criteria"]) == set(plan_pack.ACCEPTANCE_CRITERIA)
    assert set(report["boundary_proof_checklist"]) == set(plan_pack.BOUNDARY_PROOF_CHECKLIST)
    for phrase in (
        "File impact plan",
        "Step sequence",
        "Test strategy",
        "Evidence strategy",
        "Rollback / stop conditions",
        "Acceptance criteria",
        "Boundary proof",
    ):
        assert phrase in text


def test_phase_2b_09_references_existing_artifacts():
    report = plan_pack.build_phase_2b_09_first_slice_implementation_plan_pack_report()
    text = _doc_text()

    for artifact in plan_pack.EXISTING_ARTIFACTS_REFERENCED:
        assert artifact in report["existing_artifacts_referenced"]
    for artifact in (
        "AGENTS.md",
        "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
        "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
        "network_lab.py",
        "network_lab_cli_dispatch.py",
        "network_lab_task_registry.py",
    ):
        assert artifact in text


def test_phase_2b_09_forbidden_capabilities_stay_disabled():
    report = plan_pack.build_phase_2b_09_first_slice_implementation_plan_pack_report()
    text = _doc_text()

    assert report["validation"]["valid"] is True
    for flag_name, expected in plan_pack.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": plan_pack.FINAL_VERDICT,
        "PHASE_2B_08_VERDICT_REFERENCED": plan_pack.PHASE_2B_08_VERDICT,
        "PHASE_2B_08_GATE_DUPLICATED": "NO",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    for phrase in (
        "No first-slice implementation is added.",
        "No runner, adapter, execution path",
        "No provider call, API call, model call",
        "No second safety matrix is created.",
    ):
        assert phrase in text

    tampered = copy.deepcopy(report)
    tampered["runner_added"] = True
    tampered["execution_path_added"] = True
    tampered["secrets_handling_added"] = True
    validation = plan_pack.validate_phase_2b_09_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:execution_path_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:secrets_handling_added" in validation["errors"]


def test_cli_writes_phase_2b_09_plan_pack_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-09 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-09 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", plan_pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "phase_2b_08_verdict_referenced: true" in output
    assert "phase_2b_08_gate_duplicated: false" in output
    assert "first_slice_implemented: false" in output
    assert "runner_added: false" in output
    assert "adapter_added: false" in output
    assert "execution_path_added: false" in output
    assert "ssh_netconf_restconf_live_device_touched: false" in output
    assert "provider_api_model_secrets_touched: false" in output
    assert f"[PASS] {plan_pack.FINAL_VERDICT}" in output
    assert (tmp_path / plan_pack.REPORT_JSON).exists()
    assert (tmp_path / plan_pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == plan_pack.TASK_NAME)

    assert task["task_id"] == "phase_2b_09_first_slice_implementation_plan_pack"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert plan_pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert plan_pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert plan_pack.DOC_PATH.as_posix() in task["report_paths"]
    assert plan_pack.FINAL_VERDICT in task["notes"]
    assert "PHASE_2B_08_VERDICT_REFERENCED" in task["notes"]
    assert "PHASE_2B_08_GATE_DUPLICATED_FALSE" in task["notes"]
    assert "FIRST_SLICE_IMPLEMENTED_FALSE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_FALSE" in task["notes"]

    assert network_lab.main(["--task", plan_pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only" in html
    assert "phase_2b_09_first_slice_implementation_plan_pack.json" in html
