import copy
from pathlib import Path

import network_lab
import phase_2a_11_phase_closure_final_readiness_review as pack


def test_agents_md_is_not_modified_for_phase_2a_11():
    agents_text = (Path.cwd() / "AGENTS.md").read_text(encoding="utf-8")

    assert "Phase 2A-11 Phase Closure / Final Readiness Review" not in agents_text
    assert "phase_2a_11_phase_closure_final_readiness_review" not in agents_text


def test_phase_2a_11_report_has_required_structured_closure_fields():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert report["phase"] == "2A-11"
    assert report["task"] == pack.TASK_NAME
    assert report["status"] == "PASS"
    assert report["validation"]["valid"] is True
    for field in (
        "phase_2a_chain_reviewed",
        "closure_dimensions",
        "referenced_artifacts",
        "example_job_types_checked",
        "safety_boundary_status",
        "traceability_status",
        "ledger_envelope_report_consistency_status",
        "ui_display_contract_readiness_status",
        "negative_regression_lock_status",
        "phase_2b_authorization_status",
        "forbidden_capability_status",
        "final_readiness_verdict",
    ):
        assert field in report


def test_phase_2a_11_is_phase_wide_and_not_narrowed_to_one_example_job():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert report["scope"] == "phase_wide_phase_2a_closure_final_readiness_review"
    assert report["scope_confirmation"]["needs_scope_confirmation"] is False
    assert report["example_job_type_role"] == "representative_examples_only_not_full_scope"
    assert set(report["example_job_types_checked"]) == set(pack.REQUIRED_JOB_TYPES)
    assert len(report["example_job_types_checked"]) == 6
    assert set(report["example_job_types_checked"]) != {"vrrp_validation"}
    assert len(report["phase_2a_chain_reviewed"]) == len(pack.REQUIRED_ARTIFACT_IDS)


def test_example_job_types_remain_examples_only():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert report["scope_confirmation"]["example_job_type_role"] == (
        "representative examples only; not full Phase 2A-11 scope"
    )
    assert "vrrp_validation" in report["example_job_types_checked"]
    assert "backup_config_plan" in report["example_job_types_checked"]
    assert "baseline_check" in report["example_job_types_checked"]
    validation = pack.validate_phase_2a_11_report(report)
    assert validation["valid"] is True

    narrowed = copy.deepcopy(report)
    narrowed["example_job_types_checked"] = ["vrrp_validation"]
    narrowed_validation = pack.validate_phase_2a_11_report(narrowed)
    assert narrowed_validation["valid"] is False
    assert "EXAMPLE_JOB_TYPE_SET_MISMATCH" in narrowed_validation["errors"]
    assert "PHASE_SCOPE_NARROWED_TO_SINGLE_JOB" in narrowed_validation["errors"]


def test_forbidden_capabilities_are_disabled_and_phase_2b_remains_unauthorized():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()
    forbidden = report["forbidden_capability_status"]

    assert forbidden["status"] == "LOCKED"
    assert forbidden["phase_2b_authorized"] is False
    assert forbidden["next_phase_allowed"] is False
    assert set(forbidden["capabilities"]) == set(pack.FORBIDDEN_CAPABILITIES)
    assert all(value is False for value in forbidden["capabilities"].values())
    for flag_name, expected in pack.SAFETY_FLAGS.items():
        assert report[flag_name] is expected


def test_closure_dimensions_are_all_checked():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()
    dimensions = {item["dimension"]: item for item in report["closure_dimensions"]}

    assert set(dimensions) == set(pack.REQUIRED_CLOSURE_DIMENSIONS)
    assert all(item["status"] == "PASS" for item in dimensions.values())
    assert dimensions["Jobs workflow readiness"]["source_artifacts"]
    assert dimensions["Phase 2B still not authorized"]["status"] == "PASS"


def test_ledger_envelope_report_ui_and_negative_lock_are_represented():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert report["ledger_envelope_report_consistency_status"]["status"] == "PASS"
    assert "phase_2a_04_plan_evidence_ledger" in report["ledger_envelope_report_consistency_status"]["source_artifacts"]
    assert "phase_2a_05_dry_run_result_envelope_renderer" in report["ledger_envelope_report_consistency_status"]["source_artifacts"]
    assert report["ui_display_contract_readiness_status"]["status"] == "PASS"
    assert "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack" in report[
        "ui_display_contract_readiness_status"
    ]["source_artifacts"]
    assert report["negative_regression_lock_status"]["status"] == "LOCKED"
    assert "phase_2a_06_negative_regression_matrix" in report["negative_regression_lock_status"]["source_artifacts"]


def test_final_verdict_never_authorizes_phase_2b_even_when_incomplete():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert report["final_readiness_verdict"] == pack.READY_VERDICT
    assert "PHASE_2B_STILL_NOT_AUTHORIZED" in report["final_readiness_verdict"]
    assert report["phase_2b_authorized"] is False

    tampered = copy.deepcopy(report)
    tampered["phase_2b_authorized"] = True
    validation = pack.validate_phase_2a_11_report(tampered)
    assert validation["valid"] is False
    assert "SAFETY_FLAG_NOT_FALSE:phase_2b_authorized" in validation["errors"]
    assert "PHASE_2B_AUTHORIZED_NOT_FALSE" in validation["errors"]


def test_artifact_is_report_only_dry_run_mock_local_and_non_executing():
    report = pack.build_phase_2a_11_phase_closure_final_readiness_review_report()

    assert set(report["implementation_boundary"]) == set(pack.IMPLEMENTATION_BOUNDARY)
    for required in ("report-only", "review-only", "dry-run only", "mock-only", "local-only", "non-executing"):
        assert required in report["implementation_boundary"]
    assert report["summary"]["executable_capabilities_enabled"] == 0
    assert report["real_job_execution_enabled"] is False
    assert report["live_device_access_enabled"] is False


def test_cli_writes_phase_2a_11_review_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-11 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-11 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-11 Phase Closure / Final Readiness Review" in output
    assert "Task name: phase2a-11-phase-closure-final-readiness-review" in output
    assert "Artifacts reviewed: 9" in output
    assert "Closure dimensions checked: 9" in output
    assert "Example job types checked: 6" in output
    assert "Forbidden capabilities locked: 21" in output
    assert "phase_2b_authorized: false" in output
    assert "runner_enabled: false" in output
    assert "adapter_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_calls_enabled: false" in output
    assert "api_calls_enabled: false" in output
    assert "model_calls_enabled: false" in output
    assert "live_device_access_enabled: false" in output
    assert f"Final readiness verdict: {pack.READY_VERDICT}" in output
    assert f"[PASS] {pack.READY_VERDICT}" in output
    assert (tmp_path / pack.REPORT_JSON).exists()
    assert (tmp_path / pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == pack.TASK_NAME)

    assert task["task_id"] == "phase_2a_11_phase_closure_final_readiness_review"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert pack.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_WIDE_SCOPE_CONFIRMED" in task["notes"]
    assert "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY" in task["notes"]
    assert "CLOSURE_DIMENSIONS_CHECKED" in task["notes"]
    assert "UI_DISPLAY_CONTRACT_READINESS_REPRESENTED" in task["notes"]
    assert "NEGATIVE_REGRESSION_LOCK_REPRESENTED" in task["notes"]
    assert "PHASE_2B_AUTHORIZED_FALSE" in task["notes"]

    assert network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-11 Phase Closure / Final Readiness Review" in html
    assert "phase_2a_11_phase_closure_final_readiness_review.json" in html
