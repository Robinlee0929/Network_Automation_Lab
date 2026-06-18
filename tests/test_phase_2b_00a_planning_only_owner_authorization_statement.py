import copy
from pathlib import Path

import network_lab
import phase_2b_00a_planning_only_owner_authorization_statement as auth


def test_agents_md_is_not_modified_for_phase_2b_00a():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-00A Planning-Only Owner Authorization Statement" not in agents_text
    assert "phase_2b_00a_planning_only_owner_authorization_statement" not in agents_text


def test_owner_authorization_statement_is_recorded_exactly():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    assert report["owner_authorization_statement"] == auth.OWNER_AUTHORIZATION_STATEMENT
    assert report["owner_authorization_recorded"] is True
    assert report["phase_2b_planning_only_authorized"] is True
    assert report["phase_2b_implementation_allowed"] is False
    assert report["phase_2b_01_allowed"] is False
    assert report["validation"]["valid"] is True


def test_machine_readable_verdict_records_planning_only_authorization():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    assert report["final_verdict"] == auth.FINAL_VERDICT
    assert report["machine_readable_verdict"] == {
        "FINAL_VERDICT": auth.FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "PHASE_2B_01_ALLOWED": "NO",
    }


def test_scope_confirmation_is_phase_wide_and_not_one_example():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    assert report["scope"] == auth.SCOPE
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(auth.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types"]) == 6
    assert set(report["example_job_types"]) != {"vrrp_validation"}

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = auth.validate_phase_2b_00a_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_authorized_scope_remains_planning_only():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    assert set(report["authorized_scope"]) == set(auth.AUTHORIZED_SCOPE)
    assert set(report["implementation_boundary"]) == set(auth.IMPLEMENTATION_BOUNDARY)
    for allowed in (
        "planning-only artifacts",
        "scope design",
        "readiness checklists",
        "safety boundary design",
        "static matrices",
    ):
        assert allowed in report["authorized_scope"]


def test_forbidden_capabilities_stay_disabled():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    matrix = {item["capability"]: item for item in report["forbidden_capability_matrix"]}
    assert set(matrix) == set(auth.FORBIDDEN_CAPABILITIES)
    assert all(item["enabled"] is False for item in matrix.values())
    assert all(item["allowed_by_phase_2b_00a"] is False for item in matrix.values())
    for flag_name, expected in auth.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["runner_enabled"] = True
    tampered["forbidden_capability_matrix"][0]["enabled"] = True
    validation = auth.validate_phase_2b_00a_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_MISMATCH:runner_enabled" in validation["errors"]
    assert any(error.startswith("FORBIDDEN_CAPABILITY_ENABLED:") for error in validation["errors"])


def test_traceability_references_phase_2b_00_and_prior_artifacts():
    report = auth.build_phase_2b_00a_planning_only_owner_authorization_statement_report()

    artifact_ids = {item["artifact_id"] for item in report["traceability_to_existing_artifacts"]}
    assert artifact_ids == set(auth.TRACEABILITY_ARTIFACT_IDS)
    assert "phase_2b_00_authorization_scope_gate_review" in artifact_ids
    assert "phase_2b_00_authorization_scope_gate_review_doc" in artifact_ids
    assert "phase_2b_00_authorization_scope_gate_review_test" in artifact_ids
    assert "next_phase_authorization_criteria_pack" in artifact_ids
    assert all(item["reviewed"] is True for item in report["traceability_to_existing_artifacts"])


def test_cli_writes_phase_2b_00a_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-00A must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-00A must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", auth.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-00A Planning-Only Owner Authorization Statement" in output
    assert "phase_2b_planning_only_authorized: true" in output
    assert "phase_2b_implementation_allowed: false" in output
    assert "phase_2b_01_allowed: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "broker_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert f"[PASS] {auth.FINAL_VERDICT}" in output
    assert (tmp_path / auth.REPORT_JSON).exists()
    assert (tmp_path / auth.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == auth.TASK_NAME)

    assert task["task_id"] == "phase_2b_00a_planning_only_owner_authorization_statement"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert auth.REPORT_JSON.as_posix() in task["report_paths"]
    assert auth.REPORT_HTML.as_posix() in task["report_paths"]
    assert auth.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_PLANNING_ONLY_AUTHORIZED_TRUE" in task["notes"]
    assert "PHASE_2B_IMPLEMENTATION_ALLOWED_FALSE" in task["notes"]
    assert "PHASE_2B_01_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", auth.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-00A Planning-Only Owner Authorization Statement" in html
    assert "phase_2b_00a_planning_only_owner_authorization_statement.json" in html
