import copy
from pathlib import Path

import network_lab
import phase_2b_01_planning_scope_design_only as scope


def test_agents_md_is_not_modified_for_phase_2b_01():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-01 Planning Scope Design Only" not in agents_text
    assert "phase_2b_01_planning_scope_design_only" not in agents_text


def test_phase_2b_01_report_has_required_planning_scope_fields():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    assert report["phase"] == "2B-01"
    assert report["task"] == scope.TASK_NAME
    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    for field in (
        "authorized_scope",
        "implementation_prohibition",
        "forbidden_capability_matrix",
        "conceptual_architecture_boundaries",
        "safety_gate_design_requirements",
        "future_implementation_prerequisites",
        "stop_conditions",
        "traceability_to_existing_artifacts",
        "machine_readable_verdict",
    ):
        assert field in report


def test_machine_readable_verdict_matches_required_phase_2b_01_lock():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    assert report["final_verdict"] == scope.FINAL_VERDICT
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": scope.FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "RUNNER_ALLOWED": "NO",
        "ADAPTER_ALLOWED": "NO",
        "EXECUTION_ALLOWED": "NO",
    }
    assert report["phase_2b_planning_only_authorized"] is True
    assert report["phase_2b_implementation_allowed"] is False
    assert report["phase_2b_01_allowed_as_implementation"] is False
    assert report["runner_allowed"] is False
    assert report["adapter_allowed"] is False
    assert report["execution_allowed"] is False


def test_scope_confirmation_is_phase_wide_and_not_one_example():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    assert report["scope"] == scope.SCOPE
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(scope.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types"]) == 6
    assert set(report["example_job_types"]) != {"vrrp_validation"}

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = scope.validate_phase_2b_01_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_authorized_scope_and_conceptual_boundaries_remain_non_executing():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    assert set(report["authorized_scope"]) == set(scope.AUTHORIZED_SCOPE)
    assert set(report["implementation_boundary"]) == set(scope.IMPLEMENTATION_BOUNDARY)
    assert set(report["planning_artifacts_allowed"]) == set(scope.PLANNING_ARTIFACTS_ALLOWED)
    assert all(item["allowed_now"] == "concept_only" for item in report["conceptual_architecture_boundaries"])
    assert all(item["executable"] is False for item in report["conceptual_architecture_boundaries"])
    assert all(item["implementation_allowed"] is False for item in report["conceptual_architecture_boundaries"])

    tampered = copy.deepcopy(report)
    tampered["conceptual_architecture_boundaries"][0]["executable"] = True
    validation = scope.validate_phase_2b_01_report(tampered)
    assert validation["valid"] is False
    assert "CONCEPT_EXECUTABLE:mock runner concept" in validation["errors"]


def test_forbidden_capabilities_stay_disabled_and_not_allowed():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    matrix = {item["capability"]: item for item in report["forbidden_capability_matrix"]}
    assert set(matrix) == set(scope.FORBIDDEN_CAPABILITIES)
    assert all(item["enabled"] is False for item in matrix.values())
    assert all(item["allowed_by_phase_2b_01"] is False for item in matrix.values())
    for flag_name, expected in scope.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["execution_allowed"] = True
    tampered["forbidden_capability_matrix"][0]["allowed_by_phase_2b_01"] = True
    validation = scope.validate_phase_2b_01_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:execution_allowed" in validation["errors"]
    assert any(error.startswith("FORBIDDEN_CAPABILITY_ENABLED:") for error in validation["errors"])


def test_traceability_references_phase_2b_00_00a_and_phase_2a_artifacts():
    report = scope.build_phase_2b_01_planning_scope_design_only_report()

    artifact_ids = {item["artifact_id"] for item in report["traceability_to_existing_artifacts"]}
    assert artifact_ids == set(scope.TRACEABILITY_ARTIFACT_IDS)
    assert "phase_2b_00_authorization_scope_gate_review" in artifact_ids
    assert "phase_2b_00a_planning_only_owner_authorization_statement" in artifact_ids
    assert "phase_2a_11_phase_closure_final_readiness_review" in artifact_ids
    assert "next_phase_authorization_criteria_pack" in artifact_ids
    assert all(item["reviewed"] is True for item in report["traceability_to_existing_artifacts"])


def test_cli_writes_phase_2b_01_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-01 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-01 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", scope.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-01 Planning Scope Design Only" in output
    assert "phase_2b_planning_only_authorized: true" in output
    assert "phase_2b_implementation_allowed: false" in output
    assert "phase_2b_01_allowed_as_implementation: false" in output
    assert "runner_allowed: false" in output
    assert "adapter_allowed: false" in output
    assert "execution_allowed: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "broker_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert f"[PASS] {scope.FINAL_VERDICT}" in output
    assert (tmp_path / scope.REPORT_JSON).exists()
    assert (tmp_path / scope.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == scope.TASK_NAME)

    assert task["task_id"] == "phase_2b_01_planning_scope_design_only"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert scope.REPORT_JSON.as_posix() in task["report_paths"]
    assert scope.REPORT_HTML.as_posix() in task["report_paths"]
    assert scope.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_01_PLANNING_SCOPE_DESIGN_ONLY" in task["notes"]
    assert "PHASE_2B_IMPLEMENTATION_ALLOWED_FALSE" in task["notes"]
    assert "RUNNER_ALLOWED_FALSE" in task["notes"]
    assert "ADAPTER_ALLOWED_FALSE" in task["notes"]
    assert "EXECUTION_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", scope.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-01 Planning Scope Design Only" in html
    assert "phase_2b_01_planning_scope_design_only.json" in html
