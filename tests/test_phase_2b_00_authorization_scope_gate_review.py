import copy
from pathlib import Path

import network_lab
import phase_2b_00_authorization_scope_gate_review as gate


def test_agents_md_is_not_modified_for_phase_2b_00():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2B-00 Authorization / Scope Gate Review" not in agents_text
    assert "phase_2b_00_authorization_scope_gate_review" not in agents_text


def test_phase_2b_00_report_has_required_authorization_fields():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()

    assert report["phase"] == "2B-00"
    assert report["task"] == gate.TASK_NAME
    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    for field in (
        "phase_2b_status",
        "scope_confirmation",
        "authorization_matrix",
        "allowed_planning_readiness_candidates",
        "forbidden_capability_status",
        "safety_upgrade_conditions",
        "required_gates_before_phase_2b_01",
        "stop_failure_conditions",
        "traceability_to_existing_artifacts",
        "machine_readable_verdict",
    ):
        assert field in report


def test_scope_confirmation_is_phase_wide_and_not_narrowed_to_one_example():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()

    assert report["scope"] == gate.SCOPE
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["scope_confirmation"]["scope_narrowed_to_one_example"] is False
    assert report["example_job_type_role"] == "examples_only_not_phase_scope"
    assert set(report["example_job_types"]) == set(gate.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types"]) == 6
    assert set(report["example_job_types"]) != {"vrrp_validation"}

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types"] = ["vrrp_validation"]
    validation = gate.validate_phase_2b_00_report(narrowed)
    assert validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in validation["errors"]


def test_machine_readable_verdict_keeps_phase_2b_not_authorized():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()
    verdict = report["machine_readable_verdict"]

    assert report["final_verdict"] == gate.FINAL_VERDICT
    assert verdict == {
        "FINAL_VERDICT": gate.FINAL_VERDICT,
        "IMPLEMENTATION_ALLOWED": "NO",
        "PHASE_2B_STATUS": "NOT_AUTHORIZED_YET",
        "NEXT_ALLOWED_STEP": gate.NEXT_ALLOWED_STEP,
        "PHASE_2B_01_ALLOWED": "NO",
    }
    assert report["implementation_allowed"] is False
    assert report["phase_2b_authorized"] is False
    assert report["phase_2b_01_allowed"] is False


def test_forbidden_capabilities_are_locked_false():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()
    forbidden = report["forbidden_capability_status"]

    assert forbidden["status"] == "LOCKED"
    assert set(forbidden["capabilities"]) == set(gate.FORBIDDEN_CAPABILITIES)
    assert all(value is False for value in forbidden["capabilities"].values())
    for flag_name, expected in gate.SAFETY_FLAGS.items():
        assert report[flag_name] is expected

    tampered = copy.deepcopy(report)
    tampered["ssh_enabled"] = True
    tampered["forbidden_capability_status"]["capabilities"]["ssh"] = True
    validation = gate.validate_phase_2b_00_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_NOT_FALSE:ssh_enabled" in validation["errors"]
    assert "FORBIDDEN_CAPABILITY_ENABLED:ssh" in validation["errors"]


def test_traceability_references_phase_2a_and_next_phase_criteria():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()

    artifact_ids = {item["artifact_id"] for item in report["traceability_to_existing_artifacts"]}
    assert artifact_ids == set(gate.REQUIRED_ARTIFACT_IDS)
    assert "phase_2a_11_phase_closure_final_readiness_review" in artifact_ids
    assert "next_phase_authorization_criteria_pack" in artifact_ids
    assert all(item["reviewed"] is True for item in report["traceability_to_existing_artifacts"])
    assert all(item["phase_2b_authorization_evidence"] is False for item in report["traceability_to_existing_artifacts"])


def test_authorization_matrix_does_not_authorize_phase_2b():
    report = gate.build_phase_2b_00_authorization_scope_gate_review_report()

    assert any(item["status"] == "BLOCKED" for item in report["authorization_matrix"])
    assert all(item["authorizes_phase_2b"] is False for item in report["authorization_matrix"])
    assert report["phase_2b_implemented"] is False
    assert report["next_allowed_step"] == gate.NEXT_ALLOWED_STEP


def test_cli_writes_phase_2b_00_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2B-00 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2B-00 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2B-00 Authorization / Scope Gate Review" in output
    assert "Implementation allowed: false" in output
    assert "Phase 2B-01 allowed: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "broker_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_api_model_calls_enabled: false" in output
    assert f"[PASS] {gate.FINAL_VERDICT}" in output
    assert (tmp_path / gate.REPORT_JSON).exists()
    assert (tmp_path / gate.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == gate.TASK_NAME)

    assert task["task_id"] == "phase_2b_00_authorization_scope_gate_review"
    assert task["day"] == "Phase 2B"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert gate.REPORT_JSON.as_posix() in task["report_paths"]
    assert gate.REPORT_HTML.as_posix() in task["report_paths"]
    assert gate.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2B_STATUS_NOT_AUTHORIZED_YET" in task["notes"]
    assert "PHASE_2B_01_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2B-00 Authorization / Scope Gate Review" in html
    assert "phase_2b_00_authorization_scope_gate_review.json" in html
