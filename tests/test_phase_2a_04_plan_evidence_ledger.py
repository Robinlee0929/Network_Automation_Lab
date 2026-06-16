import json

import network_lab
import phase_2a_03_dry_run_job_plan_gate as phase_2a_03
import phase_2a_04_plan_evidence_ledger as ledger


def _phase_2a_03_sources():
    report = phase_2a_03.build_phase_2a_03_dry_run_job_plan_gate_report()
    return report["allowed_request_results"], report["rejected_request_results"]


def _assert_record_flags_false(record):
    assert record["runner_invoked"] is False
    assert record["adapter_invoked"] is False
    assert record["live_execution_opened"] is False
    assert record["next_phase_allowed"] is False


def test_accepted_phase_2a_03_dry_run_plans_bind_to_evidence_records():
    accepted, rejected = _phase_2a_03_sources()
    traceability = ledger.build_phase_2a_04_plan_evidence_ledger(accepted, rejected)

    accepted_records = traceability["accepted_evidence_records"]
    assert len(accepted_records) == len(accepted)
    assert {record["source_plan_id"] for record in accepted_records} == {
        result["dry_run_plan"]["plan_id"] for result in accepted
    }
    for record in accepted_records:
        assert record["evidence_id"].startswith("PHASE_2A_04_EVIDENCE_")
        assert record["accepted_or_rejected"] == "accepted"
        assert record["rejection_reason"] is None
        assert record["safe_artifact_references"]
        assert record["non_executable_proof"]["report_only_record"] is True
        assert record["non_executable_proof"]["execution_payload_present"] is False
        _assert_record_flags_false(record)


def test_rejected_unsafe_phase_2a_03_requests_bind_to_sanitized_no_plan_records():
    accepted, rejected = _phase_2a_03_sources()
    traceability = ledger.build_phase_2a_04_plan_evidence_ledger(accepted, rejected)

    rejected_records = traceability["rejected_evidence_records"]
    assert len(rejected_records) == len(rejected)
    assert all(record["source_plan_id"].startswith("REJECTED_NO_PLAN_") for record in rejected_records)
    assert all(record["accepted_or_rejected"] == "rejected" for record in rejected_records)
    assert all(record["safe_artifact_references"] == {} for record in rejected_records)
    assert any(record["source_job_type"].startswith("rejected_job_type_ref_") for record in rejected_records)
    for record in rejected_records:
        assert record["rejection_reason"]
        assert record["non_executable_proof"]["phase_2a_03_result_bound"] is True
        _assert_record_flags_false(record)

    payload = json.dumps(rejected_records)
    for unsafe_value in ("ssh_command", "backup_config", "scripts/run_anything.py", "port 22"):
        assert unsafe_value not in payload


def test_missing_evidence_causes_validation_and_report_failure():
    accepted, rejected = _phase_2a_03_sources()
    traceability = ledger.build_phase_2a_04_plan_evidence_ledger(accepted, rejected)
    traceability["records"] = traceability["records"][1:]

    validation = ledger.validate_phase_2a_04_evidence_binding(traceability, accepted, rejected)

    assert validation["valid"] is False
    assert validation["status"] == "FAIL"
    assert any(error.startswith("MISSING_ACCEPTED_EVIDENCE") for error in validation["errors"])


def test_executable_looking_evidence_keys_are_rejected():
    accepted, rejected = _phase_2a_03_sources()
    traceability = ledger.build_phase_2a_04_plan_evidence_ledger(accepted, rejected)
    traceability["records"][0]["device_command"] = "redacted"

    validation = ledger.validate_phase_2a_04_evidence_binding(traceability, accepted, rejected)

    assert validation["valid"] is False
    assert "UNSAFE_EVIDENCE_KEY:device_command" in validation["errors"]


def test_executable_looking_evidence_values_are_rejected():
    accepted, rejected = _phase_2a_03_sources()
    traceability = ledger.build_phase_2a_04_plan_evidence_ledger(accepted, rejected)
    traceability["records"][0]["safe_note"] = "run backup_config later"

    validation = ledger.validate_phase_2a_04_evidence_binding(traceability, accepted, rejected)

    assert validation["valid"] is False
    assert "UNSAFE_EVIDENCE_VALUE:safe_note" in validation["errors"]


def test_final_report_pass_requires_all_sources_traceable_and_dangerous_flags_false():
    report = ledger.build_phase_2a_04_plan_evidence_ledger_report()

    assert report["phase"] == "2A-04"
    assert report["status"] == "PASS"
    assert report["mode"] == "report_only"
    assert report["scope"] == "mock_local_read_only_dry_run"
    assert report["runner_invoked"] is False
    assert report["adapter_invoked"] is False
    assert report["live_execution_opened"] is False
    assert report["ssh_execution_opened"] is False
    assert report["netconf_execution_opened"] is False
    assert report["restconf_execution_opened"] is False
    assert report["provider_api_model_call_opened"] is False
    assert report["backup_config_invoked"] is False
    assert report["arbitrary_command_execution_opened"] is False
    assert report["arbitrary_script_path_execution_opened"] is False
    assert report["phase_2b_authorized"] is False
    assert report["real_execution_authorized"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation"]["valid"] is True
    assert report["summary"]["runner_invoked_count"] == 0
    assert report["summary"]["adapter_invoked_count"] == 0
    assert report["summary"]["live_execution_opened_count"] == 0
    assert report["summary"]["next_phase_allowed_count"] == 0
    assert report["agents_md_pre_read"] == {
        "required": True,
        "found": True,
        "read": True,
        "modified": False,
        "path": "AGENTS.md",
    }
    assert "AGENTS_MD_FOUND_AND_READ" in report["completion_markers"]
    assert "PHASE_2B_AUTHORIZED_FALSE" in report["completion_markers"]


def test_cli_writes_report_only_ledger_without_runner_adapter_or_profile(tmp_path, capsys, monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("Phase 2A-04 must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Phase 2A-04 must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", ledger.TASK_NAME], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Phase 2A-04 Dry-Run Job Plan Evidence Binding / Traceability Ledger" in output
    assert "Task name: phase2a-04-plan-evidence-ledger" in output
    assert "runner_invoked: false" in output
    assert "adapter_invoked: false" in output
    assert "live_execution_opened: false" in output
    assert "phase_2b_authorized: false" in output
    assert "real_execution_authorized: false" in output
    assert "next_phase_allowed: false" in output
    assert "[PASS] PHASE_2A_04_PLAN_EVIDENCE_LEDGER_READY" in output
    assert (tmp_path / ledger.REPORT_JSON).exists()
    assert (tmp_path / ledger.REPORT_HTML).exists()


def test_task_catalog_and_report_index_visibility(tmp_path):
    task = next(task for task in network_lab.list_tasks() if task["id"] == ledger.TASK_NAME)

    assert task["task_id"] == "phase_2a_04_plan_evidence_ledger"
    assert task["day"] == "Phase 2A"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert ledger.REPORT_JSON.as_posix() in task["report_paths"]
    assert ledger.REPORT_HTML.as_posix() in task["report_paths"]
    assert ledger.DOC_PATH.as_posix() in task["report_paths"]
    assert "PHASE_2A_03_DRY_RUN_PLANS_BOUND" in task["notes"]
    assert "REJECTED_REQUESTS_BOUND_TO_TRACEABILITY_RECORDS" in task["notes"]
    assert "RUNNER_INVOKED_FALSE" in task["notes"]
    assert "ADAPTER_INVOKED_FALSE" in task["notes"]
    assert "LIVE_EXECUTION_OPENED_FALSE" in task["notes"]

    assert network_lab.main(["--task", ledger.TASK_NAME], project_root=tmp_path) == 0
    assert network_lab.main(["--report-index"], project_root=tmp_path) == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Phase 2A-04 Dry-Run Job Plan Evidence Binding / Traceability Ledger" in html
    assert "phase_2a_04_plan_evidence_ledger.json" in html
