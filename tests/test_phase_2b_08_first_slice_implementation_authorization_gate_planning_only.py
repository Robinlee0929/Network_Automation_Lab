import copy
from pathlib import Path

import network_lab
import phase_2b_08_first_slice_implementation_authorization_gate_planning_only as gate
from report_file_utils import path_exists, read_text_with_long_path


DOC_PATH = Path("docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md")


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_agents_md_is_not_modified_for_phase_2b_08():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-08 First-Slice Implementation Authorization Gate" not in agents_text
    assert "phase_2b_08_first_slice_implementation_authorization_gate_planning_only" not in agents_text


def test_phase_2b_08_markdown_artifact_exists_and_has_required_sections():
    text = _doc_text()

    assert "# Phase 2B-08 First-Slice Implementation Authorization Gate - Planning Only" in text
    for section in (
        "## Purpose",
        "## Planning-Only Status",
        "## Scope Confirmation",
        "## Phase Goal",
        "## Example Job Types",
        "## Existing Artifacts Reviewed",
        "## Phase 2B-07 First-Slice Clarity Check",
        "## Boundary Compliance Check",
        "## Safety Gate Reuse Check",
        "## Authorization Condition Checklist",
        "## GO / NO-GO Verdict Model",
        "## Recommended Next Step",
        "## Explicit Non-Goals",
        "## Evidence Summary",
        "## Final Verdict",
    ):
        assert section in text
    assert gate.FINAL_VERDICT in text
    assert gate.RECOMMENDED_NEXT_STEP in text
    assert "This verdict does not authorize implementation directly." in text


def test_phase_2b_08_scope_is_phase_wide_and_examples_only():
    report = gate.build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    text = _doc_text()

    assert report["scope_confirmation"]["status"] == "PASS"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(gate.REQUIRED_JOB_TYPES)
    assert set(report["example_job_types"]) != {"vrrp_validation"}
    for job_type in gate.REQUIRED_JOB_TYPES:
        assert f"`{job_type}`" in text
    assert "These job types are examples only." in text
    assert "NEEDS_SCOPE_CONFIRMATION" in text

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = gate.validate_phase_2b_08_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_phase_2b_08_references_existing_artifacts_and_phase_2b_07_verdict():
    report = gate.build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    text = _doc_text()

    assert report["phase_2b_06_verdict_referenced"] == gate.PHASE_2B_06_VERDICT
    assert report["phase_2b_07_verdict_referenced"] == gate.PHASE_2B_07_VERDICT
    assert report["phase_2b_07_first_slice"]["name"] == "local_static_job_definition_and_evidence_contract_slice"
    assert report["phase_2b_07_verdict_referenced"] in text
    assert "local_static_job_definition_and_evidence_contract_slice" in text

    artifact_paths = {item["artifact"] for item in report["existing_artifacts_reviewed"]}
    for artifact in (
        "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
        "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    ):
        assert artifact in artifact_paths
        assert artifact in text


def test_phase_2b_08_authorization_checks_pass_without_implementation():
    report = gate.build_phase_2b_08_first_slice_implementation_authorization_gate_report()

    assert report["validation"]["valid"] is True
    assert all(item["status"] == "PASS" for item in report["phase_2b_07_first_slice_clarity_check"])
    assert all(item["status"] == "PASS" for item in report["boundary_compliance_check"])
    assert all(item["status"] == "PASS" for item in report["safety_gate_reuse_check"])
    assert all(item["status"] == "PASS" for item in report["authorization_condition_checklist"])
    assert report["summary"]["phase_2b_07_clarity_check"] == "PASS"
    assert report["summary"]["boundary_compliance_check"] == "PASS"
    assert report["summary"]["safety_gate_reuse_check"] == "PASS"
    assert report["recommended_next_step"] == gate.RECOMMENDED_NEXT_STEP
    assert report["final_verdict"] == gate.FINAL_VERDICT

    tampered = copy.deepcopy(report)
    tampered["authorization_condition_checklist"][0]["status"] = "FAIL"
    validation = gate.validate_phase_2b_08_report(tampered)
    assert validation["valid"] is False
    assert "AUTHORIZATION_CONDITION_CHECKLIST_NOT_PASS" in validation["errors"]


def test_phase_2b_08_forbidden_capabilities_stay_disabled():
    report = gate.build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    text = _doc_text()

    for flag_name, expected in gate.SAFETY_FLAGS.items():
        assert report[flag_name] is expected
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": gate.FINAL_VERDICT,
        "PHASE_2B_06_VERDICT_REFERENCED": gate.PHASE_2B_06_VERDICT,
        "PHASE_2B_07_VERDICT_REFERENCED": gate.PHASE_2B_07_VERDICT,
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "DIRECT_IMPLEMENTATION_AUTHORIZED": "NO",
        "NEXT_STEP": gate.RECOMMENDED_NEXT_STEP,
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "LIVE_DEVICE_ACCESS_ADDED": "NO",
        "PROVIDER_API_MODEL_CALLS_ADDED": "NO",
        "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    for phrase in (
        "First slice implemented: NO.",
        "Runner added: NO.",
        "Adapter added: NO.",
        "Execution path added: NO.",
        "SSH, NETCONF, or RESTCONF touched: NO.",
        "Live-device access added: NO.",
        "Provider, API, or model calls added: NO.",
        "Secrets handling added: NO.",
        "Second safety matrix created: NO.",
    ):
        assert phrase in text

    tampered = copy.deepcopy(report)
    tampered["runner_added"] = True
    tampered["ssh_touched"] = True
    tampered["safety_gates_rebuilt"] = True
    validation = gate.validate_phase_2b_08_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_added" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:ssh_touched" in validation["errors"]
    assert "SAFETY_FLAG_MISMATCH:safety_gates_rebuilt" in validation["errors"]


def test_phase_2b_08_final_verdict_goes_only_to_2b_09_planning():
    report = gate.build_phase_2b_08_first_slice_implementation_authorization_gate_report()
    text = _doc_text()

    assert report["final_verdict"] == "GO_TO_2B_09_PLANNING_ONLY"
    assert report["go_no_go_verdict_model"]["GO"] == "GO_TO_2B_09_PLANNING_ONLY"
    assert report["machine_readable_verdict"]["DIRECT_IMPLEMENTATION_AUTHORIZED"] == "NO"
    assert "The repository may proceed only to `Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only`." in text
    assert "This is not approval to implement." in text


def test_cli_writes_phase_2b_08_gate_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-08 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-08 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-08 First-Slice Implementation Authorization Gate - Planning Only" in output
    assert "scope_confirmation: PASS" in output
    assert "phase_goal_confirmed: true" in output
    assert "example_job_types_treated_as_examples_only: true" in output
    assert "phase_2b_07_clarity_check: PASS" in output
    assert "boundary_compliance_check: PASS" in output
    assert "safety_gate_reuse_check: PASS" in output
    assert "first_slice_implemented: false" in output
    assert "runner_added: false" in output
    assert "adapter_added: false" in output
    assert "execution_path_added: false" in output
    assert "ssh_netconf_restconf_touched: false" in output
    assert "live_device_access_added: false" in output
    assert "provider_api_model_calls_added: false" in output
    assert f"[PASS] {gate.FINAL_VERDICT}" in output
    assert path_exists(tmp_path / gate.REPORT_JSON)
    assert path_exists(tmp_path / gate.REPORT_HTML)


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == gate.TASK_NAME)

    assert task["task_id"] == "phase_2b_08_first_slice_implementation_authorization_gate_planning_only"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "planning-only"
    assert task["execution_mode"] == "planning-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert gate.REPORT_JSON.as_posix() in task["report_paths"]
    assert gate.REPORT_HTML.as_posix() in task["report_paths"]
    assert gate.DOC_PATH.as_posix() in task["report_paths"]
    assert gate.FINAL_VERDICT in task["notes"]
    assert "FIRST_SLICE_IMPLEMENTED_FALSE" in task["notes"]
    assert "RUNNER_ADAPTER_EXECUTION_ADDED_FALSE" in task["notes"]
    assert "SSH_NETCONF_RESTCONF_TOUCHED_FALSE" in task["notes"]
    assert "SECOND_SAFETY_MATRIX_CREATED_FALSE" in task["notes"]

    assert network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = read_text_with_long_path(tmp_path / "reports/report_index.html", encoding="utf-8")
    assert "Phase 2B-08 First-Slice Implementation Authorization Gate - Planning Only" in html
    assert "phase_2b_08_first_slice_implementation_authorization_gate_planning_only.json" in html
