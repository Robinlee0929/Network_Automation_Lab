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
    "arbitrary_command_allowed",
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
    assert result["execution_mode"] == "mock-local-read-only-framework"
    assert result["read_only"] is True
    assert result["local_only"] is True
    assert result["mock_only"] is True
    for flag in SAFETY_FLAG_KEYS:
        assert result[flag] is False


def test_allowed_mock_local_read_only_jobs_pass():
    for job_type in phase2a.ALLOWED_JOB_TYPES:
        result = phase2a.run_readonly_job({"job_type": job_type, "artifact_id": "reviewer-safe-id"})

        assert result["status"] == "PASS"
        assert result["job_type"] == job_type
        assert result["rejection_reason"] is None
        assert result["mock_result_recorded"] is True
        assert result["result_record"]["record_type"] == "deterministic_mock_local_evidence"
        assert_phase2a_safety_flags(result)


def test_rejected_job_types_fail_safely_without_execution_capabilities():
    for job_type in phase2a.REJECTED_JOB_TYPES:
        result = phase2a.run_readonly_job({"job_type": job_type})

        assert result["status"] == "REJECTED"
        assert result["job_type"] == job_type
        assert result["rejection_reason"] == "JOB_TYPE_EXPLICITLY_REJECTED"
        assert result["safe_rejection"] is True
        assert result["mock_result_recorded"] is False
        assert_phase2a_safety_flags(result)


def test_arbitrary_command_fields_are_rejected():
    result = phase2a.run_readonly_job({"job_type": "mock_parse_report", "command": "/system print"})

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "ARBITRARY_COMMAND_FIELD_REJECTED"
    assert result["rejected_field"] == "command"
    assert_phase2a_safety_flags(result)


def test_arbitrary_script_path_fields_are_rejected():
    result = phase2a.run_readonly_job(
        {"job_type": "mock_collect_local_evidence", "scriptPath": "scripts/run_anything.py"}
    )

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "ARBITRARY_SCRIPT_PATH_FIELD_REJECTED"
    assert result["rejected_field"] == "scriptPath"
    assert_phase2a_safety_flags(result)


def test_live_device_fields_are_rejected():
    result = phase2a.run_readonly_job({"job_type": "mock_parse_report", "device": "router01"})

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "LIVE_DEVICE_FIELD_REJECTED"
    assert result["rejected_field"] == "device"
    assert_phase2a_safety_flags(result)


def test_ssh_fields_are_rejected():
    result = phase2a.run_readonly_job({"job_type": "mock_parse_report", "ssh_host": "192.0.2.1"})

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "SSH_FIELD_REJECTED"
    assert result["rejected_field"] == "ssh_host"
    assert_phase2a_safety_flags(result)


def test_netconf_and_restconf_fields_are_rejected():
    netconf = phase2a.run_readonly_job({"job_type": "mock_parse_report", "netconf": True})
    restconf = phase2a.run_readonly_job({"job_type": "mock_parse_report", "restconf_url": "https://example.test"})

    assert netconf["status"] == "REJECTED"
    assert netconf["rejection_reason"] == "NETCONF_RESTCONF_FIELD_REJECTED"
    assert restconf["status"] == "REJECTED"
    assert restconf["rejection_reason"] == "NETCONF_RESTCONF_FIELD_REJECTED"
    assert_phase2a_safety_flags(netconf)
    assert_phase2a_safety_flags(restconf)


def test_backup_config_is_not_run_and_config_change_is_not_enabled():
    backup = phase2a.run_readonly_job({"job_type": "backup_config"})
    config_change = phase2a.run_readonly_job({"job_type": "config_change"})

    assert backup["status"] == "REJECTED"
    assert backup["backup_config_run_allowed"] is False
    assert backup["live_execution_allowed"] is False
    assert config_change["status"] == "REJECTED"
    assert config_change["config_change_allowed"] is False
    assert config_change["live_execution_allowed"] is False


def test_provider_api_model_call_flags_are_not_opened():
    result = phase2a.run_readonly_job({"job_type": "mock_validate_existing_artifact", "provider": "openai"})

    assert result["status"] == "REJECTED"
    assert result["rejection_reason"] == "PROVIDER_API_MODEL_FIELD_REJECTED"
    assert result["provider_allowed"] is False
    assert result["api_call_allowed"] is False
    assert result["external_api_call_allowed"] is False
    assert result["model_call_allowed"] is False
    assert_phase2a_safety_flags(result)


def test_report_has_only_phase2a_completion_markers_and_no_forbidden_ready_labels():
    report = phase2a.build_phase2a_readonly_job_runner_framework_report()

    assert report["overall_status"] == "PASS"
    assert report["phase_status"] == "PHASE_2A_STARTED"
    assert report["status_label"] == "READ_ONLY_JOB_RUNNER_FRAMEWORK_SCAFFOLD_READY"
    assert report["read_only"] is True
    assert report["local_only"] is True
    assert report["mock_only"] is True
    assert report["summary"]["allowed_jobs"] == 3
    assert report["summary"]["rejected_jobs"] == len(phase2a.REJECTED_JOB_TYPES)
    assert report["summary"]["provider_api_model_open_count"] == 0
    assert report["summary"]["backup_config_run_allowed_count"] == 0
    assert report["summary"]["config_change_allowed_count"] == 0
    assert report["completion_markers"] == [
        "PHASE_2A_STARTED",
        "READ_ONLY_JOB_RUNNER_FRAMEWORK_SCAFFOLD_READY",
        "MOCK_ONLY_TRUE",
        "LOCAL_ONLY_TRUE",
        "LIVE_DEVICE_ACCESS_FALSE",
        "SSH_ENABLED_FALSE",
        "ARBITRARY_COMMAND_ALLOWED_FALSE",
        "ARBITRARY_SCRIPT_PATH_ALLOWED_FALSE",
        "BACKUP_CONFIG_RUN_ALLOWED_FALSE",
        "CONFIG_CHANGE_ALLOWED_FALSE",
    ]

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


def test_phase2a_cli_writes_reviewer_visible_reports_without_profile_or_subprocess(
    tmp_path, capsys, monkeypatch
):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A scaffold must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A scaffold must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "phase2a-readonly-job-runner-framework"], project_root=tmp_path)
    output = capsys.readouterr().out

    json_path = tmp_path / "reports/lab-summary/phase2a_readonly_job_runner_framework.json"
    html_path = tmp_path / "reports/lab-summary/phase2a_readonly_job_runner_framework.html"
    assert exit_code == 0
    assert "Phase 2A Read-only Job Runner Framework" in output
    assert "Task name: phase2a-readonly-job-runner-framework" in output
    assert "read_only: true" in output
    assert "local_only: true" in output
    assert "mock_only: true" in output
    assert "live_device_access: false" in output
    assert "ssh_enabled: false" in output
    assert "arbitrary_command_allowed: false" in output
    assert "arbitrary_script_path_allowed: false" in output
    assert "backup_config_run_allowed: false" in output
    assert "config_change_allowed: false" in output
    assert "[PASS] READ_ONLY_JOB_RUNNER_FRAMEWORK_SCAFFOLD_READY" in output
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
    assert "LIVE_DEVICE_ACCESS_FALSE" in task["notes"]
    assert "SSH_ENABLED_FALSE" in task["notes"]
    assert "BACKUP_CONFIG_RUN_ALLOWED_FALSE" in task["notes"]
    assert "CONFIG_CHANGE_ALLOWED_FALSE" in task["notes"]

    assert network_lab.main(["--task", "phase2a-readonly-job-runner-framework"], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A Read-only Job Runner Framework" in html
    assert "phase2a_readonly_job_runner_framework.json" in html
    assert "Mock/local read-only job runner framework" in html
