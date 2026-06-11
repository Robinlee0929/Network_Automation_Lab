"""Day113 parser consumer reviewer triage decision log.

This module records the reviewer triage outcome for the Day112 intake package.
It is deterministic, review-only, and report-only: it does not approve
advancement, unlock execution readiness, invoke adapters or brokers, use SSH,
contact live devices, call OpenAI APIs, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_consumer_release_review_intake import (
    DECISION_ROUTE as DAY112_DECISION_ROUTE,
    INTAKE_STATUS as DAY112_INTAKE_STATUS,
    REPORT_HTML as DAY112_REPORT_HTML,
    REPORT_JSON as DAY112_REPORT_JSON,
    REVIEWER_STATUS as DAY112_REVIEWER_STATUS,
    TASK_NAME as DAY112_TASK_NAME,
    TRIAGE_STATUS as DAY112_TRIAGE_STATUS,
    build_parser_consumer_release_review_intake_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
DAY = 113
DAY_ID = "Day113"
TASK_NAME = "parser-consumer-reviewer-triage-decision-log"
TITLE = "Day113 Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit"
PHASE_NAME = "Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit"
SCHEMA_VERSION = "day113.parser_consumer_reviewer_triage_decision_log.v1"
SOURCE_DAY = "Day112"
SOURCE_TASK = DAY112_TASK_NAME
REPORT_JSON = Path("reports") / "lab-summary" / "day113_parser_consumer_reviewer_triage_decision_log.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day113_parser_consumer_reviewer_triage_decision_log.html"
AGENTS_FILE = Path("AGENTS.md")

REVIEWER_STATUS = "TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE"
OUTCOME_AUDIT_STATUS = "INTAKE_OUTCOME_AUDITED"
TRIAGE_OUTCOME_STATUS = "HOLD_LOGGED_BLOCKED_CONDITIONS_PRESERVED"
SELECTED_REVIEWER_OUTCOME = "HOLD_FOR_BLOCKED_RECORDS"
FINAL_RECOMMENDATION = "TRIAGE_OUTCOME_LOGGED_DO_NOT_ADVANCE"

REQUIRED_AUDIT_CHECK_IDS = (
    "source_day112_intake_passed",
    "source_day112_intake_status_accepted",
    "source_day112_triage_preserved_blockers",
    "source_day112_checklist_complete",
    "selected_outcome_is_allowed_day112_route",
    "selected_outcome_preserves_next_phase_block",
    "approval_and_execution_unlock_absent",
    "safety_invariants_preserved",
    "outcome_log_has_required_entries",
)

REQUIRED_LOG_STAGES = (
    "source_intake_received",
    "intake_outcome_confirmed",
    "blocked_condition_reviewed",
    "triage_outcome_selected",
    "advancement_decision_recorded",
)

SAFETY_INVARIANTS: Dict[str, bool] = {
    "review_only": True,
    "report_only": True,
    "deterministic": True,
    "source_intake_frozen": True,
    "ssh_allowed": False,
    "live_device_access_allowed": False,
    "network_command_execution_allowed": False,
    "config_mutation_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
    "cloud_runtime_allowed": False,
    "approval_unlock_supported": False,
    "execution_readiness_supported": False,
    "approve_next_phase_execution_supported": False,
    "mapped_task_execution_allowed": False,
    "adapter_invocation_allowed": False,
    "broker_invocation_allowed": False,
    "execution_broker_unlock_allowed": False,
    "runner_invocation_allowed": False,
    "next_phase_execution_allowed": False,
}

FALSE_SAFETY_FLAGS = (
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
)

TRUE_SAFETY_FLAGS = ("review_only", "report_only", "deterministic", "source_intake_frozen")


def build_agents_md_pre_read_evidence(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
) -> Dict[str, Any]:
    agents_path = Path(project_root) / AGENTS_FILE
    agents_file_found = agents_path.is_file()
    agents_file_readable = False
    agents_heading_found = False
    if agents_file_found:
        text = agents_path.read_text(encoding="utf-8")
        agents_file_readable = True
        agents_heading_found = "AGENTS.md" in text.splitlines()[0:3] or "# AGENTS.md" in text

    result = "PASS" if agents_md_pre_read and agents_file_found and agents_file_readable else "FAIL"
    return {
        "agents_md_expected": True,
        "agents_md_path": AGENTS_FILE.as_posix(),
        "agents_md_read_before_day113_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day113 records that AGENTS.md was read before triage outcome work "
            "and that the repository instruction file was not modified by the outcome audit."
        ),
    }


def _safety_invariant_result(safety_invariants: Dict[str, Any]) -> str:
    false_ok = all(safety_invariants.get(flag) is False for flag in FALSE_SAFETY_FLAGS)
    true_ok = all(safety_invariants.get(flag) is True for flag in TRUE_SAFETY_FLAGS)
    return "PASS" if false_ok and true_ok else "FAIL"


def build_triage_outcome_log(day112_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    summary = day112_report.get("triage_summary", {})
    return [
        {
            "entry_id": "D113-L001",
            "stage": "source_intake_received",
            "outcome": "DAY112_INTAKE_PACKAGE_RECEIVED",
            "source_field": "reviewer_status",
            "source_value": day112_report.get("reviewer_status"),
            "reviewer_visible_result": "Day112 intake package is available for outcome audit.",
            "next_phase_allowed": False,
        },
        {
            "entry_id": "D113-L002",
            "stage": "intake_outcome_confirmed",
            "outcome": "INTAKE_ACCEPTED_FOR_REVIEW",
            "source_field": "intake_status",
            "source_value": day112_report.get("intake_status"),
            "reviewer_visible_result": "The intake result is recorded without approving advancement.",
            "next_phase_allowed": False,
        },
        {
            "entry_id": "D113-L003",
            "stage": "blocked_condition_reviewed",
            "outcome": "BLOCKED_CONDITIONS_PRESERVED",
            "source_field": "blocked_condition_status",
            "source_value": day112_report.get("blocked_condition_status"),
            "reviewer_visible_result": "Day109 blocked records and the Day110 lock remain preserved.",
            "next_phase_allowed": False,
        },
        {
            "entry_id": "D113-L004",
            "stage": "triage_outcome_selected",
            "outcome": SELECTED_REVIEWER_OUTCOME,
            "source_field": "decision_routes",
            "source_value": summary.get("allowed_reviewer_route_count"),
            "reviewer_visible_result": "Reviewer triage outcome is to hold the package for blocked records.",
            "next_phase_allowed": False,
        },
        {
            "entry_id": "D113-L005",
            "stage": "advancement_decision_recorded",
            "outcome": FINAL_RECOMMENDATION,
            "source_field": "next_phase_allowed",
            "source_value": day112_report.get("next_phase_allowed"),
            "reviewer_visible_result": "Outcome audit records do-not-advance and no execution unlock.",
            "next_phase_allowed": False,
        },
    ]


def build_outcome_audit_checks(
    day112_report: Dict[str, Any],
    outcome_log: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    summary = day112_report.get("triage_summary", {})
    safety = day112_report.get("safety_invariants", {})
    allowed_routes = [
        route.get("route")
        for route in day112_report.get("decision_routes", [])
        if route.get("allowed") is True
    ]
    selected_route_records = [
        route
        for route in day112_report.get("decision_routes", [])
        if route.get("route") == SELECTED_REVIEWER_OUTCOME
    ]
    log_stages = [entry.get("stage") for entry in outcome_log]

    def audit_check(
        check_id: str,
        description: str,
        passed: bool,
        evidence: Any,
    ) -> Dict[str, Any]:
        return {
            "id": check_id,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "required": True,
            "evidence": evidence,
            "blocks_advancement_if_failed": True,
        }

    return [
        audit_check(
            "source_day112_intake_passed",
            "Day112 intake report passed validation.",
            day112_report.get("overall_status") == "PASS",
            {"source_overall_status": day112_report.get("overall_status")},
        ),
        audit_check(
            "source_day112_intake_status_accepted",
            "Day112 intake status is accepted for review.",
            day112_report.get("reviewer_status") == DAY112_REVIEWER_STATUS
            and day112_report.get("intake_status") == DAY112_INTAKE_STATUS,
            {
                "source_reviewer_status": day112_report.get("reviewer_status"),
                "source_intake_status": day112_report.get("intake_status"),
            },
        ),
        audit_check(
            "source_day112_triage_preserved_blockers",
            "Day112 preserved blocked conditions and did not advance.",
            day112_report.get("triage_status") == DAY112_TRIAGE_STATUS
            and day112_report.get("blocked_condition_status") == "PRESERVED"
            and summary.get("source_blocked_condition_preserved") is True,
            {
                "source_triage_status": day112_report.get("triage_status"),
                "source_blocked_condition_status": day112_report.get("blocked_condition_status"),
                "source_blocked_condition_preserved": summary.get("source_blocked_condition_preserved"),
            },
        ),
        audit_check(
            "source_day112_checklist_complete",
            "Day112 checklist passed all 10 required intake checks.",
            summary.get("checklist_pass_count") == 10
            and summary.get("checklist_total_count") == 10
            and summary.get("failed_check_count") == 0,
            {
                "checklist_pass_count": summary.get("checklist_pass_count"),
                "checklist_total_count": summary.get("checklist_total_count"),
                "failed_check_count": summary.get("failed_check_count"),
            },
        ),
        audit_check(
            "selected_outcome_is_allowed_day112_route",
            "Selected Day113 outcome is an allowed Day112 reviewer route.",
            SELECTED_REVIEWER_OUTCOME in allowed_routes
            and bool(selected_route_records)
            and selected_route_records[0].get("next_phase_allowed") is False,
            {
                "selected_reviewer_outcome": SELECTED_REVIEWER_OUTCOME,
                "allowed_day112_routes": allowed_routes,
                "selected_route_next_phase_allowed": (
                    selected_route_records[0].get("next_phase_allowed") if selected_route_records else None
                ),
            },
        ),
        audit_check(
            "selected_outcome_preserves_next_phase_block",
            "Selected triage outcome keeps next phase blocked.",
            day112_report.get("next_phase_allowed") is False,
            {
                "source_next_phase_allowed": day112_report.get("next_phase_allowed"),
                "day113_next_phase_allowed": False,
            },
        ),
        audit_check(
            "approval_and_execution_unlock_absent",
            "Approval unlock and execution readiness remain absent.",
            day112_report.get("approval_unlock_allowed") is False
            and day112_report.get("execution_readiness_allowed") is False
            and day112_report.get("approve_next_phase_execution_supported") is False,
            {
                "source_approval_unlock_allowed": day112_report.get("approval_unlock_allowed"),
                "source_execution_readiness_allowed": day112_report.get("execution_readiness_allowed"),
                "source_approve_next_phase_execution_supported": day112_report.get(
                    "approve_next_phase_execution_supported"
                ),
            },
        ),
        audit_check(
            "safety_invariants_preserved",
            "Day113 safety invariants remain review-only, report-only, and non-executable.",
            _safety_invariant_result(SAFETY_INVARIANTS) == "PASS"
            and safety.get("ssh_allowed") is False
            and safety.get("live_device_access_allowed") is False
            and safety.get("next_phase_execution_allowed") is False,
            {
                "day113_safety_invariant_result": _safety_invariant_result(SAFETY_INVARIANTS),
                "source_ssh_allowed": safety.get("ssh_allowed"),
                "source_live_device_access_allowed": safety.get("live_device_access_allowed"),
                "source_next_phase_execution_allowed": safety.get("next_phase_execution_allowed"),
            },
        ),
        audit_check(
            "outcome_log_has_required_entries",
            "Outcome log has exactly the required Day113 stages.",
            log_stages == list(REQUIRED_LOG_STAGES),
            {"log_stages": log_stages, "required_log_stages": list(REQUIRED_LOG_STAGES)},
        ),
    ]


def build_parser_consumer_reviewer_triage_decision_log_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day112_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_report = (
        deepcopy(day112_report)
        if day112_report is not None
        else build_parser_consumer_release_review_intake_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
        )
    )
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_pre_read=agents_md_pre_read,
        agents_md_modified=agents_md_modified,
    )
    outcome_log = build_triage_outcome_log(source_report)
    audit_checks = build_outcome_audit_checks(source_report, outcome_log)
    failed_checks = [item["id"] for item in audit_checks if item["status"] != "PASS"]
    summary = {
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "source_reviewer_status": source_report.get("reviewer_status"),
        "source_intake_status": source_report.get("intake_status"),
        "source_triage_status": source_report.get("triage_status"),
        "source_decision_route": source_report.get("decision_route"),
        "source_next_phase_allowed": source_report.get("next_phase_allowed"),
        "source_blocked_condition_status": source_report.get("blocked_condition_status"),
        "source_checklist_pass_count": source_report.get("triage_summary", {}).get("checklist_pass_count"),
        "source_checklist_total_count": source_report.get("triage_summary", {}).get("checklist_total_count"),
        "selected_reviewer_outcome": SELECTED_REVIEWER_OUTCOME,
        "outcome_log_entry_count": len(outcome_log),
        "audit_check_pass_count": sum(1 for item in audit_checks if item.get("status") == "PASS"),
        "audit_check_total_count": len(audit_checks),
        "failed_check_count": len(failed_checks),
        "failed_checks": failed_checks,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "next_phase_allowed": False,
    }
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "outcome_audit_status": OUTCOME_AUDIT_STATUS,
        "triage_outcome_status": TRIAGE_OUTCOME_STATUS,
        "selected_reviewer_outcome": SELECTED_REVIEWER_OUTCOME,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": "REPORT_ONLY",
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "source_reports": {
            "day112_json": DAY112_REPORT_JSON.as_posix(),
            "day112_html": DAY112_REPORT_HTML.as_posix(),
        },
        "triage_outcome_log": outcome_log,
        "outcome_audit_checks": audit_checks,
        "outcome_summary": summary,
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "agents_md_read_before_day113_work": agents_evidence["agents_md_read_before_day113_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "agents_md_pre_read_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day113 records the reviewer triage outcome for the Day112 intake package.",
            "The selected outcome is HOLD_FOR_BLOCKED_RECORDS because Day112 preserved blocked conditions.",
            "Outcome logging does not mean approval, execution readiness, or next-phase enablement.",
            "No live, SSH, mapped-task, broker, adapter, runner, OpenAI API, cloud, voice, approval unlock, or config mutation path is added.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_reviewer_triage_decision_log_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "TRIAGE_OUTCOME_BLOCKED_REVIEW_ONLY"
        report["outcome_audit_status"] = "OUTCOME_AUDIT_FAILED_REVIEW_ONLY"
        report["triage_outcome_status"] = "TRIAGE_OUTCOME_NOT_ACCEPTED"
        report["selected_reviewer_outcome"] = "REVIEWER_TRIAGE_BLOCKED_DO_NOT_ADVANCE"
        report["final_recommendation"] = "DO_NOT_ADVANCE_OUTCOME_AUDIT_FAILED"
        report["next_phase_allowed"] = False
        report["approval_unlock_allowed"] = False
        report["execution_readiness_allowed"] = False
        report["approve_next_phase_execution_supported"] = False
    return report


def validate_parser_consumer_reviewer_triage_decision_log_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "reviewer_status": REVIEWER_STATUS,
        "outcome_audit_status": OUTCOME_AUDIT_STATUS,
        "triage_outcome_status": TRIAGE_OUTCOME_STATUS,
        "selected_reviewer_outcome": SELECTED_REVIEWER_OUTCOME,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "audit_type": "REPORT_ONLY",
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "agents_md_read_before_day113_work": True,
        "agents_md_pre_read_result": "PASS",
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    safety = report.get("safety_invariants", {})
    for flag in FALSE_SAFETY_FLAGS:
        if safety.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    for flag in TRUE_SAFETY_FLAGS:
        if safety.get(flag) is not True:
            errors.append(f"safety_invariants.{flag} must be true.")

    outcome_log = report.get("triage_outcome_log", [])
    log_stages = [entry.get("stage") for entry in outcome_log]
    if log_stages != list(REQUIRED_LOG_STAGES):
        errors.append("triage_outcome_log must contain exactly the five required Day113 stages in order.")
    if len(outcome_log) != 5:
        errors.append("triage_outcome_log must contain exactly five entries.")
    for entry in outcome_log:
        for field in (
            "entry_id",
            "stage",
            "outcome",
            "source_field",
            "source_value",
            "reviewer_visible_result",
            "next_phase_allowed",
        ):
            if field not in entry:
                errors.append(f"outcome log entry {entry.get('entry_id', '<unknown>')} must include {field}.")
        if entry.get("next_phase_allowed") is not False:
            errors.append(f"outcome log entry {entry.get('entry_id', '<unknown>')} must keep next_phase_allowed=false.")

    checks = report.get("outcome_audit_checks", [])
    check_ids = [item.get("id") for item in checks]
    if check_ids != list(REQUIRED_AUDIT_CHECK_IDS):
        errors.append("outcome_audit_checks must contain exactly the nine required Day113 checks in order.")
    for item in checks:
        for field in ("id", "description", "status", "required", "evidence", "blocks_advancement_if_failed"):
            if field not in item:
                errors.append(f"outcome audit check {item.get('id', '<unknown>')} must include {field}.")
        if item.get("required") is not True:
            errors.append(f"outcome audit check {item.get('id', '<unknown>')} must be required.")
        if item.get("blocks_advancement_if_failed") is not True:
            errors.append(f"outcome audit check {item.get('id', '<unknown>')} must block advancement if failed.")
    failed_checks = [item.get("id") for item in checks if item.get("status") != "PASS"]
    if failed_checks:
        errors.append(f"outcome audit checks must all pass: {json.dumps(failed_checks)}.")

    summary = report.get("outcome_summary", {})
    if summary.get("source_reviewer_status") != DAY112_REVIEWER_STATUS:
        errors.append("outcome_summary.source_reviewer_status must match Day112 reviewer status.")
    if summary.get("source_intake_status") != DAY112_INTAKE_STATUS:
        errors.append("outcome_summary.source_intake_status must match Day112 intake status.")
    if summary.get("source_triage_status") != DAY112_TRIAGE_STATUS:
        errors.append("outcome_summary.source_triage_status must match Day112 triage status.")
    if summary.get("source_decision_route") != DAY112_DECISION_ROUTE:
        errors.append("outcome_summary.source_decision_route must match Day112 decision route.")
    if summary.get("source_next_phase_allowed") is not False:
        errors.append("outcome_summary.source_next_phase_allowed must be false.")
    if summary.get("source_blocked_condition_status") != "PRESERVED":
        errors.append("outcome_summary.source_blocked_condition_status must be PRESERVED.")
    if summary.get("source_checklist_pass_count") != 10:
        errors.append("outcome_summary.source_checklist_pass_count must be 10.")
    if summary.get("source_checklist_total_count") != 10:
        errors.append("outcome_summary.source_checklist_total_count must be 10.")
    if summary.get("selected_reviewer_outcome") != SELECTED_REVIEWER_OUTCOME:
        errors.append("outcome_summary.selected_reviewer_outcome must be HOLD_FOR_BLOCKED_RECORDS.")
    if summary.get("outcome_log_entry_count") != 5:
        errors.append("outcome_summary.outcome_log_entry_count must be 5.")
    if summary.get("audit_check_pass_count") != 9:
        errors.append("outcome_summary.audit_check_pass_count must be 9.")
    if summary.get("audit_check_total_count") != 9:
        errors.append("outcome_summary.audit_check_total_count must be 9.")
    if summary.get("failed_check_count") != 0:
        errors.append("outcome_summary.failed_check_count must be 0.")
    for field in (
        "approval_unlock_allowed",
        "execution_readiness_allowed",
        "approve_next_phase_execution_supported",
        "next_phase_allowed",
    ):
        if summary.get(field) is not False:
            errors.append(f"outcome_summary.{field} must be false.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day113 JSON and HTML reports.")
    return errors


def _table_rows(rows: Iterable[Iterable[Any]], empty_columns: int = 0) -> str:
    rendered = [
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    ]
    if rendered:
        return "".join(rendered)
    if empty_columns:
        return "<tr>" + "".join("<td>none</td>" for _ in range(empty_columns)) + "</tr>"
    return ""


def write_parser_consumer_reviewer_triage_decision_log_html(
    report: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_rows = _table_rows(
        (
            entry["entry_id"],
            entry["stage"],
            entry["outcome"],
            entry["source_field"],
            json.dumps(entry["source_value"]),
            entry["reviewer_visible_result"],
            json.dumps(entry["next_phase_allowed"]),
        )
        for entry in report["triage_outcome_log"]
    )
    check_rows = _table_rows(
        (
            item["id"],
            item["description"],
            item["status"],
            json.dumps(item["required"]),
            json.dumps(item["blocks_advancement_if_failed"]),
            json.dumps(item["evidence"]),
        )
        for item in report["outcome_audit_checks"]
    )
    safety_rows = _table_rows(
        (key, json.dumps(value)) for key, value in report["safety_invariants"].items()
    )
    summary = report["outcome_summary"]
    agents = report["agents_md_pre_read_evidence"]
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(TITLE)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .badge {{ display: inline-block; margin-right: 0.5rem; padding: 0.2rem 0.45rem; border: 1px solid #85929e; }}
  </style>
</head>
<body>
  <h1>{html.escape(TITLE)}</h1>
  <p>
    <span class="badge">REVIEW_ONLY</span>
    <span class="badge">REPORT_ONLY</span>
    <span class="badge">OUTCOME_AUDIT</span>
    <span class="badge">NO_APPROVAL_UNLOCK</span>
    <span class="badge">NEXT_PHASE_ALLOWED_FALSE</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Outcome audit status:</strong> {html.escape(report['outcome_audit_status'])}</p>
  <p><strong>Triage outcome status:</strong> {html.escape(report['triage_outcome_status'])}</p>
  <p><strong>Selected reviewer outcome:</strong> {html.escape(report['selected_reviewer_outcome'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day113 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day113_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Outcome Summary</h2>
  <table>
    <tbody>
      <tr><th>Source</th><td>{html.escape(summary['source_day'])} / <code>{html.escape(summary['source_task'])}</code></td></tr>
      <tr><th>Source reviewer status</th><td>{html.escape(str(summary['source_reviewer_status']))}</td></tr>
      <tr><th>Source intake status</th><td>{html.escape(str(summary['source_intake_status']))}</td></tr>
      <tr><th>Source triage status</th><td>{html.escape(str(summary['source_triage_status']))}</td></tr>
      <tr><th>Selected reviewer outcome</th><td>{html.escape(summary['selected_reviewer_outcome'])}</td></tr>
      <tr><th>Source next phase allowed</th><td>{html.escape(json.dumps(summary['source_next_phase_allowed']))}</td></tr>
      <tr><th>Outcome log entries</th><td>{summary['outcome_log_entry_count']}</td></tr>
      <tr><th>Audit pass / total</th><td>{summary['audit_check_pass_count']} / {summary['audit_check_total_count']}</td></tr>
    </tbody>
  </table>

  <h2>Triage Outcome Log</h2>
  <table>
    <thead><tr><th>ID</th><th>Stage</th><th>Outcome</th><th>Source Field</th><th>Source Value</th><th>Reviewer Result</th><th>Next Phase Allowed</th></tr></thead>
    <tbody>{log_rows}</tbody>
  </table>

  <h2>Outcome Audit Checks</h2>
  <table>
    <thead><tr><th>ID</th><th>Description</th><th>Status</th><th>Required</th><th>Blocks Advancement If Failed</th><th>Evidence</th></tr></thead>
    <tbody>{check_rows}</tbody>
  </table>

  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Value</th></tr></thead>
    <tbody>{safety_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_parser_consumer_reviewer_triage_decision_log_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_parser_consumer_reviewer_triage_decision_log_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_reviewer_triage_decision_log_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_reviewer_triage_decision_log_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
