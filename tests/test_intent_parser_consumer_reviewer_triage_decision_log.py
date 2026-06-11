import ast
import json
from copy import deepcopy
from pathlib import Path

import intent_parser_consumer_reviewer_triage_decision_log as day113
import network_lab


FORBIDDEN_IMPORTS = {
    "paramiko",
    "netmiko",
    "scrapli",
    "routeros_api",
    "openai",
    "requests",
    "httpx",
    "socket",
    "subprocess",
    "time",
    "datetime",
    "random",
    "uuid",
}


SAFE_AGENTS_TEXT = """# AGENTS.md

## Project

This repository is a Network Automation Lab for safe reviewer-visible validation.

## Core Safety Rules

- Do not perform live device access.
- Do not use SSH or real network-device commands.
- Do not execute configuration-changing commands.
- Preserve safety gates and no-execution proof.
- Report-only work remains report-only.
"""


def write_agents(project_root: Path) -> Path:
    path = project_root / "AGENTS.md"
    path.write_text(SAFE_AGENTS_TEXT, encoding="utf-8")
    return path


def test_day113_default_report_records_triage_outcome_for_day112_intake(tmp_path):
    write_agents(tmp_path)

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)

    assert report["overall_status"] == "PASS"
    assert report["reviewer_status"] == "TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE"
    assert report["outcome_audit_status"] == "INTAKE_OUTCOME_AUDITED"
    assert report["triage_outcome_status"] == "HOLD_LOGGED_BLOCKED_CONDITIONS_PRESERVED"
    assert report["selected_reviewer_outcome"] == "HOLD_FOR_BLOCKED_RECORDS"
    assert report["final_recommendation"] == "TRIAGE_OUTCOME_LOGGED_DO_NOT_ADVANCE"
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["approve_next_phase_execution_supported"] is False
    assert report["next_phase_allowed"] is False
    assert report["validation_errors"] == []

    summary = report["outcome_summary"]
    assert summary["source_day"] == "Day112"
    assert summary["source_task"] == "parser-consumer-release-review-intake"
    assert summary["source_reviewer_status"] == "REVIEW_INTAKE_READY_NON_EXECUTABLE"
    assert summary["source_intake_status"] == "ACCEPTED_FOR_REVIEW"
    assert summary["source_triage_status"] == "BLOCKED_CONDITIONS_PRESERVED"
    assert summary["source_decision_route"] == "ACCEPT_FOR_REVIEW"
    assert summary["source_next_phase_allowed"] is False
    assert summary["source_blocked_condition_status"] == "PRESERVED"
    assert summary["selected_reviewer_outcome"] == "HOLD_FOR_BLOCKED_RECORDS"


def test_day113_outcome_log_is_ordered_non_executable_and_reviewer_visible(tmp_path):
    write_agents(tmp_path)

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)
    log = report["triage_outcome_log"]

    assert [entry["stage"] for entry in log] == list(day113.REQUIRED_LOG_STAGES)
    assert len(log) == 5
    assert report["outcome_summary"]["outcome_log_entry_count"] == 5
    assert all(entry["next_phase_allowed"] is False for entry in log)
    assert log[3]["outcome"] == "HOLD_FOR_BLOCKED_RECORDS"
    assert log[4]["outcome"] == "TRIAGE_OUTCOME_LOGGED_DO_NOT_ADVANCE"
    for entry in log:
        assert set(entry) == {
            "entry_id",
            "stage",
            "outcome",
            "source_field",
            "source_value",
            "reviewer_visible_result",
            "next_phase_allowed",
        }


def test_day113_outcome_audit_checks_all_pass_and_block_advancement_if_failed(tmp_path):
    write_agents(tmp_path)

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)
    checks = report["outcome_audit_checks"]

    assert [item["id"] for item in checks] == list(day113.REQUIRED_AUDIT_CHECK_IDS)
    assert len(checks) == 9
    assert report["outcome_summary"]["audit_check_pass_count"] == 9
    assert report["outcome_summary"]["audit_check_total_count"] == 9
    assert report["outcome_summary"]["failed_check_count"] == 0
    assert all(item["status"] == "PASS" for item in checks)
    assert all(item["required"] is True for item in checks)
    assert all(item["blocks_advancement_if_failed"] is True for item in checks)


def test_day113_safety_invariants_remain_review_only_report_only_and_non_executable(tmp_path):
    write_agents(tmp_path)

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)
    safety = report["safety_invariants"]

    for field in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "approval_unlock_supported",
        "execution_readiness_supported",
        "approve_next_phase_execution_supported",
        "mapped_task_execution_allowed",
        "adapter_invocation_allowed",
        "broker_invocation_allowed",
        "execution_broker_unlock_allowed",
        "runner_invocation_allowed",
        "next_phase_execution_allowed",
    ):
        assert safety[field] is False
    assert safety["review_only"] is True
    assert safety["report_only"] is True
    assert safety["deterministic"] is True
    assert safety["source_intake_frozen"] is True


def test_day113_agents_pre_read_evidence_is_visible_and_agents_unmodified(tmp_path):
    write_agents(tmp_path)

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)

    assert report["agents_md_read_before_day113_work"] is True
    assert report["agents_md_pre_read_result"] == "PASS"
    assert report["agents_md_modified"] is False
    assert report["agents_md_pre_read_evidence"]["agents_md_file_found"] is True
    assert report["agents_md_pre_read_evidence"]["agents_md_file_readable"] is True


def test_day113_fails_closed_if_day112_source_unlocks_next_phase(tmp_path):
    write_agents(tmp_path)
    source = day113.build_parser_consumer_reviewer_triage_decision_log_report(
        project_root=tmp_path
    )["outcome_summary"]
    day112_source = {
        "overall_status": "PASS",
        "reviewer_status": "REVIEW_INTAKE_READY_NON_EXECUTABLE",
        "intake_status": "ACCEPTED_FOR_REVIEW",
        "triage_status": "BLOCKED_CONDITIONS_PRESERVED",
        "blocked_condition_status": "PRESERVED",
        "decision_route": "ACCEPT_FOR_REVIEW",
        "next_phase_allowed": True,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "triage_summary": {
            "source_blocked_condition_preserved": True,
            "checklist_pass_count": 10,
            "checklist_total_count": 10,
            "failed_check_count": 0,
            "allowed_reviewer_route_count": 4,
        },
        "decision_routes": [
            {"route": "HOLD_FOR_BLOCKED_RECORDS", "allowed": True, "next_phase_allowed": False}
        ],
        "safety_invariants": {
            "ssh_allowed": False,
            "live_device_access_allowed": False,
            "next_phase_execution_allowed": False,
        },
    }

    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(
        project_root=tmp_path,
        day112_report=day112_source,
    )

    assert source["source_task"] == "parser-consumer-release-review-intake"
    assert report["overall_status"] == "FAIL"
    assert report["next_phase_allowed"] is False
    assert report["approval_unlock_allowed"] is False
    assert report["execution_readiness_allowed"] is False
    assert report["approve_next_phase_execution_supported"] is False
    assert "outcome audit checks must all pass" in " ".join(report["validation_errors"])
    assert "outcome_summary.source_next_phase_allowed must be false." in report["validation_errors"]


def test_day113_writer_outputs_json_and_html_outcome_audit(tmp_path):
    write_agents(tmp_path)
    report = day113.build_parser_consumer_reviewer_triage_decision_log_report(project_root=tmp_path)

    json_path, html_path = day113.write_parser_consumer_reviewer_triage_decision_log_reports(
        tmp_path, report
    )

    assert json_path == tmp_path / "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.json"
    assert html_path == tmp_path / "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.html"
    assert json.loads(json_path.read_text(encoding="utf-8")) == report
    html = html_path.read_text(encoding="utf-8")
    assert "Day113 Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit" in html
    assert "Triage Outcome Log" in html
    assert "Outcome Audit Checks" in html
    assert "HOLD_FOR_BLOCKED_RECORDS" in html
    assert "NEXT_PHASE_ALLOWED_FALSE" in html
    assert "AGENTS.md Pre-read Evidence" in html


def test_day113_module_has_no_live_external_or_nondeterministic_imports():
    tree = ast.parse(Path(day113.__file__).read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert not (FORBIDDEN_IMPORTS & imports)


def test_day113_runner_task_is_registered_and_report_only():
    task = next(task for task in network_lab.list_tasks() if task["id"] == "parser-consumer-reviewer-triage-decision-log")

    assert task["task_id"] == "day113_parser_consumer_reviewer_triage_decision_log"
    assert task["day"] == "Day113"
    assert task["safety_level"] == "report-only"
    assert task["execution_mode"] == "report-only"
    assert task["requires_live_device"] is False
    assert task["requires_password"] is False
    assert "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.json" in task["report_paths"]
    assert "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.html" in task["report_paths"]
    assert "docs/ai-intent/day113_parser_consumer_reviewer_triage_decision_log.md" in task["report_paths"]
    assert "docs/ai-intent/reviewer/day113_parser_consumer_reviewer_triage_decision_log.md" in task["report_paths"]
    assert "docs/roadmap/day113_parser_consumer_reviewer_triage_decision_log.md" in task["report_paths"]
    assert "agents_md_read_before_day113_work" in task["notes"]
    assert "reviewer_status=TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE" in task["notes"]
    assert "outcome_audit_status=INTAKE_OUTCOME_AUDITED" in task["notes"]
    assert "triage_outcome_status=HOLD_LOGGED_BLOCKED_CONDITIONS_PRESERVED" in task["notes"]
    assert "selected_reviewer_outcome=HOLD_FOR_BLOCKED_RECORDS" in task["notes"]
    assert "outcome_log_entry_count=5" in task["notes"]
    assert "audit_check_pass_count=9" in task["notes"]
    assert "audit_check_total_count=9" in task["notes"]
    assert "approve_next_phase_execution_supported=false" in task["notes"]
    assert "approval_unlock_allowed=false" in task["notes"]
    assert "execution_readiness_allowed=false" in task["notes"]
    assert "next_phase_allowed=false" in task["notes"]


def test_day113_runner_writes_reports_without_live_access(tmp_path, capsys, monkeypatch):
    write_agents(tmp_path)

    def fail_run(*_args, **_kwargs):
        raise AssertionError("Day113 triage decision log must not execute subprocess")

    def fail_load(_path):
        raise AssertionError("Day113 triage decision log must not load profile or config data")

    monkeypatch.setattr(network_lab.subprocess, "run", fail_run)
    monkeypatch.setattr(network_lab, "load_lab_runner_profile", fail_load)

    exit_code = network_lab.main(["--task", "parser-consumer-reviewer-triage-decision-log"], project_root=tmp_path)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Day113 Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit" in output
    assert "Task name: parser-consumer-reviewer-triage-decision-log" in output
    assert "overall_status: PASS" in output
    assert "reviewer_status: TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE" in output
    assert "outcome_audit_status: INTAKE_OUTCOME_AUDITED" in output
    assert "triage_outcome_status: HOLD_LOGGED_BLOCKED_CONDITIONS_PRESERVED" in output
    assert "selected_reviewer_outcome: HOLD_FOR_BLOCKED_RECORDS" in output
    assert "final_recommendation: TRIAGE_OUTCOME_LOGGED_DO_NOT_ADVANCE" in output
    assert "approval_unlock_allowed: false" in output
    assert "execution_readiness_allowed: false" in output
    assert "approve_next_phase_execution_supported: false" in output
    assert "next_phase_allowed: false" in output
    assert "source_intake_status: ACCEPTED_FOR_REVIEW" in output
    assert "source_triage_status: BLOCKED_CONDITIONS_PRESERVED" in output
    assert "source_blocked_condition_status: PRESERVED" in output
    assert "outcome_log_entry_count: 5" in output
    assert "audit_check_pass_count: 9" in output
    assert "audit_check_total_count: 9" in output
    assert "failed_check_count: 0" in output
    assert "JSON report: reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.json" in output
    assert "HTML report: reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.html" in output
    assert (tmp_path / "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.json").exists()
    assert (tmp_path / "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.html").exists()


def test_day113_report_index_visibility_includes_triage_outcome_audit(tmp_path):
    write_agents(tmp_path)
    assert network_lab.main(["--task", "parser-consumer-reviewer-triage-decision-log"], project_root=tmp_path) == 0

    exit_code = network_lab.main(["--report-index"], project_root=tmp_path)

    assert exit_code == 0
    html = (tmp_path / "reports/report_index.html").read_text(encoding="utf-8")
    assert "Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit" in html
    assert "triage outcome" in html
    assert "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.json" in html
    assert "reports/lab-summary/day113_parser_consumer_reviewer_triage_decision_log.html" in html
