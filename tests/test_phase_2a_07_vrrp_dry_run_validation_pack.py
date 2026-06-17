import json

import network_lab
import phase_2a_07_vrrp_dry_run_validation_pack as pack


def test_vrrp_mock_evidence_validation_detects_expected_outcomes():
    report = pack.build_phase_2a_07_vrrp_dry_run_validation_pack_report()

    assert report["phase"] == "2A-07"
    assert report["status"] == "PASS"
    assert report["summary"]["artifact_reference_groups_inspected"] == 6
    assert report["summary"]["mapped_job_candidates"] == 6
    assert report["summary"]["safe_job_candidates"] == 4
    assert report["summary"]["blocked_or_planning_only_job_candidates"] == 2
    assert report["summary"]["required_job_types_mapped"] == 6
    assert report["summary"]["vrrp_role_after_correction"] == "first_concrete_example_job"
    assert report["summary"]["vrrp_mock_records"] == 5
    assert report["summary"]["pass_records"] == 1
    assert report["summary"]["mismatch_records"] == 2
    assert report["summary"]["incomplete_records"] == 1
    assert report["summary"]["stale_records"] == 1
    assert report["summary"]["expected_outcomes_detected"] == 5
    assert report["next_phase_allowed"] is False
    assert report["phase_2b_authorized"] is False

    statuses = {
        validation["record_id"]: validation["validation_status"]
        for validation in report["vrrp_validation_pack"]["validations"]
    }
    assert statuses["VRRP-MOCK-VALID"] == "PASS"
    assert statuses["VRRP-MOCK-VIP-MISMATCH"] == "MISMATCH"
    assert statuses["VRRP-MOCK-MISSING-STANDBY"] == "INCOMPLETE"
    assert statuses["VRRP-MOCK-STALE"] == "STALE"
    assert statuses["VRRP-MOCK-INTERFACE-DOWN"] == "MISMATCH"

    for validation in report["vrrp_validation_pack"]["validations"]:
        assert validation["expected_outcome_matched"] is True
        proof = validation["non_execution_proof"]
        assert proof["subprocess_invoked"] is False
        assert proof["runner_invoked"] is False
        assert proof["adapter_invoked"] is False
        assert proof["broker_invoked"] is False
        assert proof["device_connection_attempted"] is False
        assert proof["command_payload_present"] is False
        assert proof["network_io_attempted"] is False


def test_day1_day160_artifact_patterns_map_to_required_jobs_with_vrrp_as_example():
    report = pack.build_phase_2a_07_vrrp_dry_run_validation_pack_report()
    mapping = report["artifact_to_jobs_mapping"]
    jobs = {job["job_type"]: job for job in mapping["job_candidates"]}

    assert mapping["artifact_references_inspected"] is True
    assert set(pack.REQUIRED_JOB_TYPES) == set(jobs)
    assert jobs["baseline_check"]["allowed_mode"] == "dry_run_mock_local_report_only"
    assert jobs["interface_status_check"]["allowed_mode"] == "dry_run_mock_local_report_only"
    assert jobs["wan_lan_check"]["allowed_mode"] == "dry_run_mock_local_report_only"
    assert jobs["vrrp_validation"]["allowed_mode"] == "dry_run_mock_local_report_only"
    assert jobs["vrrp_validation"]["vrrp_concrete_example"] is True
    assert jobs["vrrp_validation"]["candidate_status"] == "IMPLEMENTED_AS_LOCAL_MOCK_EXAMPLE"
    assert jobs["backup_config_plan"]["blocked_or_planning_only"] is True
    assert jobs["backup_config_plan"]["candidate_status"] == "BLOCKED_FROM_EXECUTION"
    assert jobs["blocked_config_change_request"]["blocked_or_planning_only"] is True
    assert jobs["blocked_config_change_request"]["candidate_status"] == "BLOCKED_NON_EXECUTING"

    for job in jobs.values():
        boundary = job["safety_boundary"]
        assert boundary["dry_run_only"] is True
        assert boundary["mock_only"] is True
        assert boundary["local_only"] is True
        assert boundary["report_only"] is True
        assert boundary["live_device_access_enabled"] is False
        assert boundary["ssh_enabled"] is False
        assert boundary["netconf_enabled"] is False
        assert boundary["restconf_enabled"] is False
        assert boundary["provider_api_model_enabled"] is False
        assert boundary["adapter_broker_runner_enabled"] is False
        assert boundary["secrets_enabled"] is False
        assert boundary["real_network_io_enabled"] is False
        assert boundary["config_change_enabled"] is False
        assert boundary["next_phase_allowed"] is False


def test_unsafe_vrrp_requests_are_rejected_redacted_and_non_executing():
    report = pack.build_phase_2a_07_vrrp_dry_run_validation_pack_report()

    assert report["summary"]["unsafe_requests_rejected"] == len(pack.UNSAFE_REQUEST_SPECS)
    assert report["summary"]["unsafe_requests_redacted"] == len(pack.UNSAFE_REQUEST_SPECS)
    assert report["summary"]["runner_invoked_count"] == 0
    assert report["summary"]["adapter_invoked_count"] == 0
    assert report["summary"]["broker_invoked_count"] == 0
    assert report["summary"]["live_execution_opened_count"] == 0
    assert report["summary"]["next_phase_allowed_count"] == 0

    for case in report["negative_regression_matrix"]:
        assert case["passed"] is True
        assert case["actual"]["status"] == "REJECTED"
        assert case["actual"]["values_redacted"] is True
        assert case["actual"]["raw_values_included"] is False
        assert case["actual"]["runner_invoked"] is False
        assert case["actual"]["adapter_invoked"] is False
        assert case["actual"]["broker_invoked"] is False
        assert case["actual"]["live_execution_opened"] is False
        assert case["actual"]["next_phase_allowed"] is False

    payload = json.dumps(report, sort_keys=True)
    for literal in pack.RAW_UNSAFE_LITERALS:
        assert literal not in payload


def test_validator_fails_if_safety_boundary_or_detection_is_weakened():
    report = pack.build_phase_2a_07_vrrp_dry_run_validation_pack_report()
    report["ssh_enabled"] = True
    report["vrrp_validation_pack"]["validations"][0]["expected_outcome_matched"] = False
    report["artifact_to_jobs_mapping"]["job_candidates"][0]["safety_boundary"]["ssh_enabled"] = True

    validation = pack.validate_phase_2a_07_report(report)

    assert validation["valid"] is False
    assert "SAFETY_FLAG_NOT_FALSE:ssh_enabled" in validation["errors"]
    assert any(error.startswith("VRRP_EXPECTED_OUTCOME_NOT_DETECTED") for error in validation["errors"])
    assert any(error.startswith("JOB_SAFETY_BOUNDARY_FAILED") for error in validation["errors"])


def test_cli_writes_vrrp_validation_pack_without_execution_paths(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-07 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-07 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-07 Day1-Day160 Artifact-to-Jobs Dry-Run Validation Pack" in output
    assert "Task name: phase2a-07-vrrp-dry-run-validation-pack" in output
    assert "Artifact reference groups inspected: 6" in output
    assert "Mapped job candidates: 6" in output
    assert "Safe job candidates: 4" in output
    assert "Blocked/planning-only job candidates: 2" in output
    assert "Required job types mapped: 6" in output
    assert "VRRP role after correction: first_concrete_example_job" in output
    assert "VRRP mock records: 5" in output
    assert "Expected outcomes detected: 5" in output
    assert "Unsafe requests rejected: 9" in output
    assert "Unsafe requests redacted: 9" in output
    assert "runner_invoked_count: 0" in output
    assert "adapter_invoked_count: 0" in output
    assert "broker_invoked_count: 0" in output
    assert "live_execution_opened_count: 0" in output
    assert "real_vrrp_test_performed: false" in output
    assert "live_device_access_enabled: false" in output
    assert "ssh_enabled: false" in output
    assert "provider_api_model_enabled: false" in output
    assert "adapter_broker_runner_enabled: false" in output
    assert "config_change_enabled: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] PHASE_2A_07_ARTIFACT_TO_JOBS_DRY_RUN_VALIDATION_PACK_READY" in output
    assert (tmp_path / pack.REPORT_JSON).exists()
    assert (tmp_path / pack.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == pack.TASK_NAME)

    assert task["task_id"] == "phase_2a_07_vrrp_dry_run_validation_pack"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert pack.REPORT_JSON.as_posix() in task["report_paths"]
    assert pack.REPORT_HTML.as_posix() in task["report_paths"]
    assert pack.DOC_PATH.as_posix() in task["report_paths"]
    assert pack.FIXTURE_PATH.as_posix() in task["report_paths"]
    assert "DAY1_DAY160_ARTIFACT_REFERENCES_INSPECTED" in task["notes"]
    assert "ARTIFACT_PATTERNS_MAPPED_TO_JOB_CANDIDATES" in task["notes"]
    assert "VRRP_VALIDATION_RETAINED_AS_FIRST_CONCRETE_EXAMPLE_JOB" in task["notes"]
    assert "VRRP_MOCK_EVIDENCE_ONLY" in task["notes"]
    assert "UNSAFE_VRRP_REQUESTS_REJECTED" in task["notes"]
    assert "NEXT_PHASE_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", pack.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-07 Day1-Day160 Artifact-to-Jobs Dry-Run Validation Pack" in html
    assert "phase_2a_07_vrrp_dry_run_validation_pack.json" in html
