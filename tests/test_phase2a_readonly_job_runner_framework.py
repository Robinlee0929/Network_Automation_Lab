import json
from pathlib import Path

import network_lab
import phase2a_readonly_job_runner_framework as phase2a


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SAFETY_FLAG_KEYS = (
    "live_device_access",
    "ssh_enabled",
    "netconf_enabled",
    "restconf_enabled",
    "routeros_enabled",
    "arbitrary_command_allowed",
    "arbitrary_shell_allowed",
    "arbitrary_script_path_allowed",
    "config_change_allowed",
    "backup_config_run_allowed",
    "provider_allowed",
    "api_call_allowed",
    "external_api_call_allowed",
    "model_call_allowed",
    "adapter_invocation_allowed",
    "broker_invocation_allowed",
    "live_execution_allowed",
)


def assert_phase2a_safety_flags(result):
    assert result["phase"] == "Phase 2A"
    assert result["execution_mode"] == "mock-local-review-only-validator"
    assert result["read_only"] is True
    assert result["local_only"] is True
    assert result["mock_only"] is True
    assert result["review_only"] is True
    assert result["next_phase_allowed"] is False
    assert result["allowlist_schema_primary"] is True
    assert result["denylist_evidence_only"] is True
    for flag in SAFETY_FLAG_KEYS:
        assert result[flag] is False


def test_allowed_mock_local_read_only_jobs_pass_after_validation():
    cases = {
        "mock_parse_report": {"report_path": "reports/lab-summary/reviewer-safe.json"},
        "mock_collect_local_evidence": {"artifact_path": "docs/phase2a_readonly_job_runner_framework.md"},
        "mock_validate_existing_artifact": {"artifact_path": "fixtures/day127_ai_reviewer_summary.example.json"},
    }
    for job_type, inputs in cases.items():
        result = phase2a.run_readonly_job({"job_type": job_type, "inputs": inputs})

        assert result["status"] == "PASS"
        assert result["job_type"] == job_type
        assert result["rejection_reason"] is None
        assert result["runner_invoked"] is True
        assert result["mock_result_recorded"] is True
        assert result["result_record"]["record_type"] == "deterministic_mock_local_review_only_evidence"
        assert_phase2a_safety_flags(result)


def test_forbidden_job_types_fail_safely_before_runner_invocation():
    for job_type in phase2a.FORBIDDEN_JOB_TYPES:
        result = phase2a.run_readonly_job({"job_type": job_type, "inputs": {}})

        assert result["status"] == "REJECTED"
        assert result["job_type"] == job_type
        assert result["rejection_reason"] == "JOB_TYPE_EXPLICITLY_FORBIDDEN"
        assert result["safe_rejection"] is True
        assert result["mock_result_recorded"] is False
        assert result["runner_invoked"] is False
        assert_phase2a_safety_flags(result)


def test_unknown_job_type_is_not_allowlisted():
    result = phase2a.run_readonly_job({"job_type": "show_inventory", "inputs": {}})

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "JOB_TYPE_NOT_ALLOWLISTED"
    assert result["runner_invoked"] is False
    assert_phase2a_safety_flags(result)


def test_unknown_top_level_fields_are_rejected():
    result = phase2a.run_readonly_job(
        {
            "job_type": "mock_parse_report",
            "inputs": {"report_path": "reports/lab-summary/reviewer-safe.json"},
            "metadata": {"reviewer": "local"},
        }
    )

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "UNKNOWN_TOP_LEVEL_FIELD_REJECTED"
    assert result["rejected_field"] == "metadata"
    assert result["runner_invoked"] is False
    assert_phase2a_safety_flags(result)


def test_unknown_input_fields_are_rejected_per_job_type():
    result = phase2a.run_readonly_job(
        {"job_type": "mock_parse_report", "inputs": {"artifact_path": "reports/lab-summary/reviewer-safe.json"}}
    )

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "UNKNOWN_INPUT_FIELD_REJECTED"
    assert result["rejected_field"] == "inputs.artifact_path"
    assert result["runner_invoked"] is False
    assert_phase2a_safety_flags(result)


def test_arbitrary_command_fields_are_rejected_before_unknown_field_fallback():
    for field in ("command", "cmd", "shell"):
        result = phase2a.run_readonly_job({"job_type": "mock_parse_report", "inputs": {field: "/system print"}})

        assert result["status"] == "REJECTED"
        assert result["rejection_reason"] == "ARBITRARY_COMMAND_FIELD_REJECTED"
        assert result["rejected_field"] == f"inputs.{field}"
        assert result["runner_invoked"] is False
        assert_phase2a_safety_flags(result)


def test_arbitrary_script_path_fields_are_rejected_before_runner_invocation():
    for field in ("scriptPath", "script_path", "custom_script_path", "executable_path"):
        result = phase2a.run_readonly_job(
            {"job_type": "mock_collect_local_evidence", "inputs": {field: "scripts/run_anything.py"}}
        )

        assert result["status"] == "REJECTED"
        assert result["rejection_reason"] == "ARBITRARY_SCRIPT_PATH_FIELD_REJECTED"
        assert result["rejected_field"] == f"inputs.{field}"
        assert result["runner_invoked"] is False
        assert_phase2a_safety_flags(result)


def test_live_device_ssh_netconf_restconf_provider_model_fields_are_rejected():
    field_groups = [
        ("host", "LIVE_DEVICE_FIELD_REJECTED"),
        ("ip", "LIVE_DEVICE_FIELD_REJECTED"),
        ("device", "LIVE_DEVICE_FIELD_REJECTED"),
        ("routeros", "LIVE_DEVICE_FIELD_REJECTED"),
        ("ssh", "SSH_FIELD_REJECTED"),
        ("username", "SSH_FIELD_REJECTED"),
        ("password", "SSH_FIELD_REJECTED"),
        ("netconf", "NETCONF_RESTCONF_FIELD_REJECTED"),
        ("restconf", "NETCONF_RESTCONF_FIELD_REJECTED"),
        ("api_key", "PROVIDER_API_MODEL_FIELD_REJECTED"),
        ("provider", "PROVIDER_API_MODEL_FIELD_REJECTED"),
        ("model", "PROVIDER_API_MODEL_FIELD_REJECTED"),
    ]
    for field, expected_reason in field_groups:
        result = phase2a.run_readonly_job({"job_type": "mock_parse_report", "inputs": {field: "unsafe"}})

        assert result["status"] == "REJECTED"
        assert result["rejection_reason"] == expected_reason
        assert result["runner_invoked"] is False
        assert_phase2a_safety_flags(result)

    port = phase2a.run_readonly_job({"job_type": "mock_parse_report", "inputs": {"port": 22}})
    assert port["status"] == "REJECTED"
    assert port["rejection_reason"] == "SSH_FIELD_REJECTED"
    assert port["runner_invoked"] is False


def test_safe_artifact_paths_are_allowed_but_executable_or_unsafe_paths_are_rejected():
    safe = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/lab-summary/safe.json"}}
    )
    absolute = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "C:/Users/example/safe.json"}}
    )
    traversal = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/../config.json"}}
    )
    outside = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "config/example.json"}}
    )
    secret = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/secrets/api_key.json"}}
    )
    script = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"artifact_path": "reports/lab-summary/run.py"}}
    )
    evidence_ref_script = phase2a.run_readonly_job(
        {"job_type": "mock_validate_existing_artifact", "inputs": {"evidence_ref": "run.py"}}
    )

    assert safe["status"] == "PASS"
    assert safe["runner_invoked"] is True
    assert absolute["rejection_reason"] == "ARTIFACT_PATH_ABSOLUTE_REJECTED"
    assert traversal["rejection_reason"] == "ARTIFACT_PATH_TRAVERSAL_REJECTED"
    assert outside["rejection_reason"] == "ARTIFACT_PATH_OUTSIDE_APPROVED_DIR_REJECTED"
    assert secret["rejection_reason"] == "ARTIFACT_PATH_SECRET_LIKE_REJECTED"
    assert script["rejection_reason"] == "ARTIFACT_PATH_EXECUTABLE_OR_SCRIPT_REJECTED"
    assert evidence_ref_script["rejection_reason"] == "EVIDENCE_REF_EXECUTABLE_OR_SCRIPT_REJECTED"
    for rejected in (absolute, traversal, outside, secret, script, evidence_ref_script):
        assert rejected["status"] == "REJECTED"
        assert rejected["runner_invoked"] is False
        assert_phase2a_safety_flags(rejected)


def test_negative_input_matrix_covers_required_cases_and_rejected_specs_skip_runner():
    matrix = phase2a.build_negative_input_matrix()

    assert len(matrix) == 18
    assert [case["case_id"] for case in matrix] == [f"M{index:02d}" for index in range(1, 19)]
    assert all(case["passed"] is True for case in matrix)
    rejected_cases = [case for case in matrix if case["expected_status"] == "REJECTED"]
    assert rejected_cases
    assert all(case["runner_invoked"] is False for case in rejected_cases)


def test_report_has_contract_validator_evidence_and_no_forbidden_ready_labels():
    report = phase2a.build_phase2a_readonly_job_runner_framework_report()

    assert report["overall_status"] == "PASS"
    assert report["phase_status"] == "PHASE_2A_STARTED"
    assert report["status_label"] == "JOB_SPEC_CONTRACT_VALIDATOR_READY"
    assert report["validator_contract_only"] is True
    assert report["allowlist_schema_primary"] is True
    assert report["denylist_evidence_only"] is True
    assert report["next_phase_allowed"] is False
    assert report["summary"]["allowed_jobs"] == 3
    assert report["summary"]["rejected_jobs"] == len(phase2a.FORBIDDEN_JOB_TYPES)
    assert report["summary"]["negative_matrix_cases"] == 18
    assert report["summary"]["negative_matrix_failed"] == 0
    assert report["summary"]["all_rejections_runner_invoked_false"] is True
    assert report["summary"]["provider_api_model_open_count"] == 0
    assert report["summary"]["backup_config_run_allowed_count"] == 0
    assert report["summary"]["config_change_allowed_count"] == 0
    assert report["allowed_top_level_fields"] == ["inputs", "job_type"]
    assert report["path_safety_rules"]["artifact_style_fields"] == ["artifact_path", "evidence_ref", "report_path"]
    assert report["path_safety_rules"]["path_validated_fields"] == ["artifact_path", "report_path"]
    assert report["path_safety_rules"]["approved_repo_local_roots"] == ["reports", "docs", "fixtures", "summary"]
    assert report["path_safety_rules"]["evidence_ref_rejects_path_traversal_secrets_and_scripts"] is True
    assert "ALLOWLIST_SCHEMA_PRIMARY_TRUE" in report["completion_markers"]
    assert "DENYLIST_EVIDENCE_ONLY_TRUE" in report["completion_markers"]
    assert "RUNNER_INVOKED_FALSE_FOR_REJECTIONS_TRUE" in report["completion_markers"]
    assert "NEXT_PHASE_ALLOWED_FALSE" in report["completion_markers"]

    payload = json.dumps(report)
    for forbidden in (
        "RUNNER" + "_ENABLED",
        "LIVE" + "_READY",
        "SSH" + "_READY",
        "BACKUP" + "_READY",
        "CONFIG_CHANGE" + "_READY",
        "EXECUTION" + "_UNLOCKED",
    ):
        assert forbidden not in payload


def test_phase2a_cli_writes_reviewer_visible_reports_without_profile_or_subprocess(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A validator must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A validator must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "phase2a-readonly-job-runner-framework"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/phase2a_readonly_job_runner_framework.json"
    html_path = tmp_path / "reports/lab-summary/phase2a_readonly_job_runner_framework.html"
    assert exit_code == 0
    assert "Phase 2A-02 Job Spec Contract Validator + Negative Input Matrix" in output
    assert "Task name: phase2a-readonly-job-runner-framework" in output
    assert "Allowlist schema primary: true" in output
    assert "Denylist evidence only: true" in output
    assert "Negative matrix cases: 18" in output
    assert "Rejected specs runner_invoked=false: true" in output
    assert "read_only: true" in output
    assert "local_only: true" in output
    assert "mock_only: true" in output
    assert "next_phase_allowed: false" in output
    assert "live_device_access: false" in output
    assert "ssh_enabled: false" in output
    assert "netconf_enabled: false" in output
    assert "restconf_enabled: false" in output
    assert "arbitrary_command_allowed: false" in output
    assert "arbitrary_shell_allowed: false" in output
    assert "arbitrary_script_path_allowed: false" in output
    assert "backup_config_run_allowed: false" in output
    assert "config_change_allowed: false" in output
    assert "[PASS] JOB_SPEC_CONTRACT_VALIDATOR_READY" in output
    assert json_path.exists()
    assert html_path.exists()
    assert not (tmp_path / "config.json").exists()


def test_phase2a_task_catalog_and_report_index_visibility(tmp_path, capsys):
    task = next(task for task in network_lab.list_tasks() if task["id"] == "phase2a-readonly-job-runner-framework")

    assert task["task_id"] == "phase2a_readonly_job_runner_framework"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/phase2a_readonly_job_runner_framework.json" in task["report_paths"]
    assert "docs/phase2a_readonly_job_runner_framework.md" in task["report_paths"]
    assert "ALLOWLIST_SCHEMA_PRIMARY_TRUE" in task["notes"]
    assert "DENYLIST_EVIDENCE_ONLY_TRUE" in task["notes"]
    assert "RUNNER_INVOKED_FALSE_FOR_REJECTIONS_TRUE" in task["notes"]
    assert "NEXT_PHASE_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", "phase2a-readonly-job-runner-framework"], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-02 Job Spec Contract Validator + Negative Input Matrix" in html
    assert "phase2a_readonly_job_runner_framework.json" in html
    assert "Job spec contract validator and negative input matrix" in html
