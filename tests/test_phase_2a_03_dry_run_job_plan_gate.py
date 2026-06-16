import json
from pathlib import Path

import network_lab
import phase_2a_03_dry_run_job_plan_gate as gate


SAFETY_FLAG_KEYS = tuple(gate.SAFETY_FLAGS.keys())


def assert_safety_flags_false(result):
    for flag_name in SAFETY_FLAG_KEYS:
        assert result[flag_name] is False


def assert_plan_non_executable(plan):
    assert plan["plan_type"] == "non_executable_dry_run_job_plan"
    assert plan["executable"] is False
    assert plan["plan_only"] is True
    assert plan["dry_run_only"] is True
    assert all(value is False for value in plan["non_executable_proof"].values())
    for step in plan["steps"]:
        assert step["operation"] == "semantic_review_step"
        assert step["executable"] is False
        assert step["runner_call"] is None
        assert step["adapter_call"] is None
        assert step["shell_command"] is None
        assert step["device_command"] is None
        assert step["script_path"] is None
        assert step["live_target"] is None


def test_allowed_mock_local_read_only_job_requests_normalize_successfully():
    cases = {
        "mock_parse_report": {"report_path": "reports/lab-summary/reviewer-safe.json"},
        "mock_collect_local_evidence": {"artifact_path": "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md"},
        "mock_validate_existing_artifact": {"artifact_path": "fixtures/day127_ai_reviewer_summary.example.json"},
    }

    for job_type, inputs in cases.items():
        result = gate.normalize_phase_2a_job_request({"job_type": job_type, "inputs": inputs})

        assert result["status"] == "NORMALIZED"
        assert result["job_type"] == job_type
        assert result["normalized_request"] == {"job_type": job_type, "inputs": inputs}
        assert result["plan_generated"] is False
        assert result["runner_invoked"] is False
        assert result["adapter_invoked"] is False
        assert_safety_flags_false(result)


def test_allowed_requests_produce_non_executable_dry_run_plans_only():
    result = gate.build_phase_2a_03_dry_run_job_plan(
        {
            "job_type": "mock_validate_existing_artifact",
            "inputs": {"artifact_path": "reports/lab-summary/reviewer-safe.json", "evidence_ref": "phase2a-03-safe"},
        }
    )

    assert result["status"] == "PLANNED"
    assert result["plan_generated"] is True
    assert result["dry_run_plan_non_executable"] is True
    assert result["runner_invoked"] is False
    assert result["adapter_invoked"] is False
    assert_safety_flags_false(result)

    plan = result["dry_run_plan"]
    assert plan["plan_id"] == "phase_2a_03::mock_validate_existing_artifact"
    assert plan["safe_artifact_references"] == {
        "artifact_path": "reports/lab-summary/reviewer-safe.json",
        "evidence_ref": "phase2a-03-safe",
    }
    assert_plan_non_executable(plan)

    payload = json.dumps(plan)
    for forbidden_value in ("show run", "/system", "backup_config", "scripts/run", "router01", "admin", "password"):
        assert forbidden_value not in payload


def test_rejected_job_types_are_rejected_before_plan_generation():
    expected = {
        "backup_config",
        "config_change",
        "ssh_command",
        "netconf_get",
        "restconf_get",
        "arbitrary_command",
        "custom_command",
        "scriptPath",
        "arbitrary_script_path",
        "provider_api_call",
        "model_call",
    }
    assert expected.issubset(gate.REJECTED_JOB_TYPES)

    for job_type in expected:
        result = gate.build_phase_2a_03_dry_run_job_plan({"job_type": job_type, "inputs": {}})

        assert result["status"] == "REJECTED"
        assert result["rejection_reason"] == "JOB_TYPE_EXPLICITLY_REJECTED"
        assert result["plan_generated"] is False
        assert result["dry_run_plan"] is None
        assert result["runner_invoked"] is False
        assert result["adapter_invoked"] is False
        assert_safety_flags_false(result)


def test_dangerous_fields_are_rejected_before_plan_generation():
    fields = {
        "host",
        "hostname",
        "ip",
        "username",
        "password",
        "secret",
        "token",
        "command",
        "cmd",
        "custom_command",
        "scriptPath",
        "arbitrary_script_path",
        "provider_api",
        "model",
        "netconf",
        "restconf",
        "ssh",
    }

    for field_name in fields:
        result = gate.build_phase_2a_03_dry_run_job_plan(
            {"job_type": "mock_parse_report", "inputs": {field_name: "unsafe"}}
        )

        assert result["status"] == "REJECTED"
        assert result["rejection_reason"] == "DANGEROUS_FIELD_REJECTED"
        assert result["rejected_field"] == f"inputs.{field_name}"
        assert result["plan_generated"] is False
        assert result["runner_invoked"] is False
        assert result["adapter_invoked"] is False
        assert_safety_flags_false(result)

    port = gate.build_phase_2a_03_dry_run_job_plan({"job_type": "mock_parse_report", "inputs": {"port": 22}})
    assert port["status"] == "REJECTED"
    assert port["rejection_reason"] == "LIVE_TARGET_FIELD_REJECTED"
    assert port["runner_invoked"] is False


def test_rejected_requests_do_not_invoke_runner_or_adapter_and_all_flags_stay_false():
    report = gate.build_phase_2a_03_dry_run_job_plan_gate_report()

    assert report["overall_status"] == "PASS"
    assert report["summary"]["unsafe_requests"] > 0
    assert report["summary"]["unsafe_requests_with_plan_generated"] == 0
    assert report["summary"]["runner_invoked_count"] == 0
    assert report["summary"]["adapter_invoked_count"] == 0
    assert report["summary"]["all_safety_flags_false"] is True
    for result in report["rejected_request_results"]:
        assert result["status"] == "REJECTED"
        assert result["plan_generated"] is False
        assert result["runner_invoked"] is False
        assert result["adapter_invoked"] is False
        assert_safety_flags_false(result)


def test_report_status_pass_requires_unsafe_rejections_and_agents_metadata():
    report = gate.build_phase_2a_03_dry_run_job_plan_gate_report()

    assert report["overall_status"] == "PASS"
    assert report["status_label"] == "DRY_RUN_JOB_PLAN_GATE_READY"
    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }
    assert report["phase_2b_authorized"] is False
    assert report["real_execution_authorized"] is False
    assert report["live_execution_opened"] is False
    assert report["runner_invoked"] is False
    assert report["adapter_invoked"] is False
    assert "AGENTS_MD_FOUND_AND_READ" in report["completion_markers"]
    assert "AGENTS_MD_NOT_MODIFIED" in report["completion_markers"]
    assert_safety_flags_false(report)


def test_cli_writes_fixed_report_only_gate_without_profile_runner_adapter_or_subprocess(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-03 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-03 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-03 Job Request Normalization and Dry-Run Plan Gate" in output
    assert "Task name: phase2a-03-dry-run-job-plan-gate" in output
    assert "runner_invoked: false" in output
    assert "adapter_invoked: false" in output
    assert "live_execution_opened: false" in output
    assert "next_phase_allowed: false" in output
    assert "phase_2b_authorized: false" in output
    assert "real_execution_authorized: false" in output
    assert "[PASS] DRY_RUN_JOB_PLAN_GATE_READY" in output
    assert (tmp_path / gate.REPORT_JSON).exists()
    assert (tmp_path / gate.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == gate.TASK_NAME)

    assert task["task_id"] == "phase_2a_03_dry_run_job_plan_gate"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert gate.REPORT_JSON.as_posix() in task["report_paths"]
    assert gate.REPORT_HTML.as_posix() in task["report_paths"]
    assert gate.DOC_PATH.as_posix() in task["report_paths"]
    assert "DRY_RUN_PLAN_NON_EXECUTABLE" in task["notes"]
    assert "RUNNER_INVOKED_FALSE" in task["notes"]
    assert "ADAPTER_INVOKED_FALSE" in task["notes"]
    assert "LIVE_EXECUTION_OPENED_FALSE" in task["notes"]

    assert network_lab.main(["--task", gate.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-03 Job Request Normalization and Dry-Run Plan Gate" in html
    assert "phase_2a_03_dry_run_job_plan_gate.json" in html

