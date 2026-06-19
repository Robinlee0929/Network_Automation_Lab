import copy
from pathlib import Path

import network_lab
import phase_2b_02_safety_gate_design_planning_only as safety


def test_agents_md_is_not_modified_for_phase_2b_02():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-02 Safety Gate Design Planning Only" not in agents_text
    assert "phase_2b_02_safety_gate_design_planning_only" not in agents_text


def test_phase_2b_02_report_has_required_safety_gate_fields():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    assert report["phase"] == "2B-02"
    assert report["task"] == safety.TASK_NAME
    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    for field in (
        "authorized_scope",
        "implementation_prohibition",
        "forbidden_capability_matrix",
        "safety_gate_designs",
        "required_gates_before_future_implementation",
        "required_evidence_before_future_implementation",
        "approval_gate_design_boundaries",
        "failure_condition_matrix",
        "stop_conditions",
        "traceability_to_existing_artifacts",
        "machine_readable_verdict",
    ):
        assert field in report


def test_machine_readable_verdict_matches_required_phase_2b_02_lock():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    assert report["final_verdict"] == safety.FINAL_VERDICT
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": safety.FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "RUNNER_ALLOWED": "NO",
        "ADAPTER_ALLOWED": "NO",
        "EXECUTION_ALLOWED": "NO",
    }
    assert report["phase_2b_planning_only_authorized"] is True
    assert report["phase_2b_implementation_allowed"] is False
    assert report["phase_2b_02_allowed_as_implementation"] is False
    assert report["runner_allowed"] is False
    assert report["adapter_allowed"] is False
    assert report["execution_allowed"] is False


def test_scope_confirmation_is_phase_wide_and_not_one_example():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    assert report["scope"] == safety.SCOPE
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(safety.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types"]) == 6
    assert set(report["example_job_types"]) != {"vrrp_validation"}

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = safety.validate_phase_2b_02_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_required_safety_gate_categories_are_defined_and_non_executing():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    assert set(report["safety_gate_categories"]) == set(safety.SAFETY_GATE_CATEGORIES)
    gate_rows = {item["gate"]: item for item in report["safety_gate_designs"]}
    assert set(gate_rows) == set(safety.SAFETY_GATE_CATEGORIES)
    assert all(item["required_before_future_implementation"] is True for item in gate_rows.values())
    assert all(item["implementation_effect_now"] == "none_planning_only" for item in gate_rows.values())
    assert all(item["stop_on_fail"] is True for item in gate_rows.values())

    tampered = copy.deepcopy(report)
    tampered["safety_gate_designs"][0]["implementation_effect_now"] = "authorizes_runner"
    validation = safety.validate_phase_2b_02_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_GATE_HAS_IMPLEMENTATION_EFFECT:owner authorization gate" in validation["errors"]


def test_forbidden_capabilities_stay_disabled_and_not_allowed():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    matrix = {item["capability"]: item for item in report["forbidden_capability_matrix"]}
    assert set(matrix) == set(safety.FORBIDDEN_CAPABILITIES)
    assert all(item["enabled"] is False for item in matrix.values())
    assert all(item["allowed_by_phase_2b_02"] is False for item in matrix.values())
    for flag_name, expected in safety.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["runner_allowed"] = True
    tampered["forbidden_capability_matrix"][0]["allowed_by_phase_2b_02"] = True
    validation = safety.validate_phase_2b_02_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_allowed" in validation["errors"]
    assert any(error.startswith("FORBIDDEN_CAPABILITY_ENABLED:") for error in validation["errors"])


def test_failure_and_stop_conditions_block_before_execution():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    assert report["stop_conditions"] == list(safety.STOP_CONDITIONS)
    assert len(report["failure_condition_matrix"]) == len(safety.STOP_CONDITIONS)
    assert all(item["severity"] == "STOP" for item in report["failure_condition_matrix"])
    assert all(item["authorized_response"] == "BLOCKED_NOT_AUTHORIZED" for item in report["failure_condition_matrix"])
    assert all(item["execution_reached"] is False for item in report["failure_condition_matrix"])

    tampered = copy.deepcopy(report)
    tampered["failure_condition_matrix"][0]["execution_reached"] = True
    validation = safety.validate_phase_2b_02_report(tampered)
    assert validation["valid"] is False
    assert any(error.startswith("FAILURE_CONDITION_REACHES_EXECUTION:") for error in validation["errors"])


def test_traceability_references_phase_2b_00_00a_01_and_phase_2a_artifacts():
    report = safety.build_phase_2b_02_safety_gate_design_planning_only_report()

    artifact_ids = {item["artifact_id"] for item in report["traceability_to_existing_artifacts"]}
    assert artifact_ids == set(safety.TRACEABILITY_ARTIFACT_IDS)
    assert "phase_2b_00_authorization_scope_gate_review" in artifact_ids
    assert "phase_2b_00a_planning_only_owner_authorization_statement" in artifact_ids
    assert "phase_2b_01_planning_scope_design_only" in artifact_ids
    assert "phase_2a_11_phase_closure_final_readiness_review" in artifact_ids
    assert "next_phase_authorization_criteria_pack" in artifact_ids
    assert all(item["reviewed"] is True for item in report["traceability_to_existing_artifacts"])


def test_cli_writes_phase_2b_02_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-02 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-02 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", safety.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-02 Safety Gate Design Planning Only" in output
    assert "phase_2b_planning_only_authorized: true" in output
    assert "phase_2b_implementation_allowed: false" in output
    assert "phase_2b_02_allowed_as_implementation: false" in output
    assert "runner_allowed: false" in output
    assert "adapter_allowed: false" in output
    assert "execution_allowed: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "broker_enabled: false" in output
    assert "scheduler_enabled: false" in output
    assert "queue_worker_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert "secrets_handling_enabled: false" in output
    assert f"[PASS] {safety.FINAL_VERDICT}" in output
    assert (tmp_path / safety.REPORT_JSON).exists()
    assert (tmp_path / safety.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == safety.TASK_NAME)

    assert task["task_id"] == "phase_2b_02_safety_gate_design_planning_only"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert safety.REPORT_JSON.as_posix() in task["report_paths"]
    assert safety.REPORT_HTML.as_posix() in task["report_paths"]
    assert safety.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_02_SAFETY_GATE_DESIGN_PLANNING_ONLY" in task["notes"]
    assert "PHASE_2B_IMPLEMENTATION_ALLOWED_FALSE" in task["notes"]
    assert "RUNNER_ALLOWED_FALSE" in task["notes"]
    assert "ADAPTER_ALLOWED_FALSE" in task["notes"]
    assert "EXECUTION_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", safety.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-02 Safety Gate Design Planning Only" in html
    assert "phase_2b_02_safety_gate_design_planning_only.json" in html
