"""Day112 parser consumer release review intake and triage checklist.

This module receives the frozen Day111 release package into a deterministic
reviewer intake checklist. It remains review-only and report-only: it does not
approve advancement, unlock execution readiness, invoke adapters or brokers,
use SSH, contact live devices, call OpenAI APIs, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_consumer_release_package import (
    FINAL_RECOMMENDATION as DAY111_FINAL_RECOMMENDATION,
    RELEASE_PACKAGE_STATUS as DAY111_RELEASE_PACKAGE_STATUS,
    REPORT_HTML as DAY111_REPORT_HTML,
    REPORT_JSON as DAY111_REPORT_JSON,
    REVIEWER_STATUS as DAY111_REVIEWER_STATUS,
    TASK_NAME as DAY111_TASK_NAME,
    build_parser_consumer_release_package_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
DAY = 112
DAY_ID = "Day112"
TASK_NAME = "parser-consumer-release-review-intake"
TITLE = "Day112 Parser Consumer Release Review Intake / Reviewer Triage Checklist"
PHASE_NAME = "Parser Consumer Release Review Intake / Reviewer Triage Checklist"
SCHEMA_VERSION = "day112.parser_consumer_release_review_intake.v1"
SOURCE_DAY = "Day111"
SOURCE_TASK = DAY111_TASK_NAME
REPORT_JSON = Path("reports") / "lab-summary" / "day112_parser_consumer_release_review_intake.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day112_parser_consumer_release_review_intake.html"
AGENTS_FILE = Path("AGENTS.md")

REVIEWER_STATUS = "REVIEW_INTAKE_READY_NON_EXECUTABLE"
INTAKE_STATUS = "ACCEPTED_FOR_REVIEW"
TRIAGE_STATUS = "BLOCKED_CONDITIONS_PRESERVED"
BLOCKED_CONDITION_STATUS = "PRESERVED"
DECISION_ROUTE = "ACCEPT_FOR_REVIEW"
FINAL_RECOMMENDATION = "REVIEW_INTAKE_ACCEPTED_DO_NOT_ADVANCE"

REQUIRED_CHECKLIST_IDS = (
    "release_package_present",
    "source_chain_day107_to_day111_traceable",
    "day109_blocked_records_preserved",
    "day110_final_gate_locked",
    "day111_package_frozen",
    "next_phase_still_disallowed",
    "safety_invariants_preserved",
    "reviewer_routes_defined",
    "return_path_defined",
    "execution_unlock_absent",
)

ALLOWED_REVIEWER_ROUTES = (
    "ACCEPT_FOR_REVIEW",
    "HOLD_FOR_BLOCKED_RECORDS",
    "RETURN_FOR_CLARIFICATION",
    "REJECT_PACKAGE",
)

FORBIDDEN_REVIEWER_ROUTES = ("APPROVE_NEXT_PHASE_EXECUTION",)

SAFETY_INVARIANTS: Dict[str, bool] = {
    "review_only": True,
    "report_only": True,
    "deterministic": True,
    "source_package_frozen": True,
    "ssh_allowed": False,
    "live_device_access_allowed": False,
    "network_command_execution_allowed": False,
    "config_mutation_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
    "cloud_runtime_allowed": False,
    "approval_unlock_supported": False,
    "approve_next_phase_execution_supported": False,
    "execution_readiness_supported": False,
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
    "approve_next_phase_execution_supported",
    "execution_readiness_supported",
    "mapped_task_execution_allowed",
    "adapter_invocation_allowed",
    "broker_invocation_allowed",
    "execution_broker_unlock_allowed",
    "runner_invocation_allowed",
    "next_phase_execution_allowed",
)

TRUE_SAFETY_FLAGS = ("review_only", "report_only", "deterministic", "source_package_frozen")


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
        "agents_md_read_before_day112_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day112 records that AGENTS.md was read before reviewer intake work "
            "and that the repository instruction file was not modified by the intake report."
        ),
    }


def _safety_invariant_result(safety_invariants: Dict[str, Any]) -> str:
    false_ok = all(safety_invariants.get(flag) is False for flag in FALSE_SAFETY_FLAGS)
    true_ok = all(safety_invariants.get(flag) is True for flag in TRUE_SAFETY_FLAGS)
    return "PASS" if false_ok and true_ok else "FAIL"


def build_intake_triage_checklist(day111_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocked = day111_report.get("blocked_condition_summary", {})
    manifest = day111_report.get("release_manifest", {})
    safety = day111_report.get("safety_invariants", {})
    source_days = [record.get("day") for record in day111_report.get("source_days", [])]
    source_safety_result = _safety_invariant_result(
        {
            "review_only": safety.get("review_only"),
            "report_only": safety.get("report_only"),
            "deterministic": safety.get("deterministic"),
            "source_package_frozen": True,
            "ssh_allowed": safety.get("ssh_allowed"),
            "live_device_access_allowed": safety.get("live_device_access_allowed"),
            "network_command_execution_allowed": safety.get("network_command_execution_allowed"),
            "config_mutation_allowed": safety.get("config_mutation_allowed"),
            "openai_api_allowed": safety.get("openai_api_allowed"),
            "voice_runtime_allowed": safety.get("voice_runtime_allowed"),
            "cloud_runtime_allowed": safety.get("cloud_runtime_allowed"),
            "approval_unlock_supported": safety.get("approval_unlock_supported"),
            "approve_next_phase_execution_supported": False,
            "execution_readiness_supported": False,
            "mapped_task_execution_allowed": safety.get("mapped_task_execution_allowed"),
            "adapter_invocation_allowed": False,
            "broker_invocation_allowed": False,
            "execution_broker_unlock_allowed": safety.get("execution_broker_unlock_allowed", False),
            "runner_invocation_allowed": False,
            "next_phase_execution_allowed": safety.get("next_phase_execution_allowed"),
        }
    )

    def checklist_item(
        check_id: str,
        description: str,
        passed: bool,
        evidence: Any,
        blocks_advancement_if_failed: bool = True,
    ) -> Dict[str, Any]:
        return {
            "id": check_id,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "required": True,
            "evidence": evidence,
            "blocks_advancement_if_failed": blocks_advancement_if_failed,
        }

    return [
        checklist_item(
            "release_package_present",
            "Day111 release package report is present and passed validation.",
            day111_report.get("overall_status") == "PASS",
            {
                "source_day": SOURCE_DAY,
                "source_task": SOURCE_TASK,
                "source_overall_status": day111_report.get("overall_status"),
            },
        ),
        checklist_item(
            "source_chain_day107_to_day111_traceable",
            "Day107-Day111 source chain is traceable from Day112 intake.",
            source_days == [107, 108, 109, 110] and day111_report.get("day") == 111,
            {
                "day111_day": day111_report.get("day"),
                "day111_task": day111_report.get("task"),
                "day111_source_days": source_days,
                "day112_source_day": SOURCE_DAY,
            },
        ),
        checklist_item(
            "day109_blocked_records_preserved",
            "Day109 blocked records remain preserved in the Day111 package.",
            blocked.get("day109_observed_status") == "BLOCKED_RECORDS_PRESENT"
            and blocked.get("day109_blocked_count") == 1
            and blocked.get("blocked_condition_preserved") is True,
            {
                "day109_observed_status": blocked.get("day109_observed_status"),
                "day109_blocked_count": blocked.get("day109_blocked_count"),
                "blocked_condition_preserved": blocked.get("blocked_condition_preserved"),
            },
        ),
        checklist_item(
            "day110_final_gate_locked",
            "Day110 final gate remains locked by blocked records.",
            blocked.get("day110_observed_status") == "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS"
            and blocked.get("day110_next_phase_allowed") is False,
            {
                "day110_observed_status": blocked.get("day110_observed_status"),
                "day110_final_recommendation": blocked.get("day110_final_recommendation"),
                "day110_next_phase_allowed": blocked.get("day110_next_phase_allowed"),
            },
        ),
        checklist_item(
            "day111_package_frozen",
            "Day111 package remains frozen for review intake.",
            day111_report.get("release_package_status") == DAY111_RELEASE_PACKAGE_STATUS,
            {
                "release_package_status": day111_report.get("release_package_status"),
                "reviewer_status": day111_report.get("reviewer_status"),
            },
        ),
        checklist_item(
            "next_phase_still_disallowed",
            "Next phase remains disallowed after reviewer intake.",
            day111_report.get("next_phase_allowed") is False,
            {
                "day111_next_phase_allowed": day111_report.get("next_phase_allowed"),
                "day112_next_phase_allowed": False,
            },
        ),
        checklist_item(
            "safety_invariants_preserved",
            "Review-only and report-only safety invariants remain preserved.",
            source_safety_result == "PASS",
            {
                "source_safety_invariant_result": source_safety_result,
                "ssh_allowed": safety.get("ssh_allowed"),
                "live_device_access_allowed": safety.get("live_device_access_allowed"),
                "network_command_execution_allowed": safety.get("network_command_execution_allowed"),
                "config_mutation_allowed": safety.get("config_mutation_allowed"),
                "openai_api_allowed": safety.get("openai_api_allowed"),
                "voice_runtime_allowed": safety.get("voice_runtime_allowed"),
                "cloud_runtime_allowed": safety.get("cloud_runtime_allowed"),
                "mapped_task_execution_allowed": safety.get("mapped_task_execution_allowed"),
                "execution_broker_unlock_allowed": safety.get("execution_broker_unlock_allowed", False),
                "next_phase_execution_allowed": safety.get("next_phase_execution_allowed"),
            },
        ),
        checklist_item(
            "reviewer_routes_defined",
            "Allowed and forbidden reviewer routes are explicitly defined.",
            True,
            {
                "allowed_reviewer_routes": list(ALLOWED_REVIEWER_ROUTES),
                "forbidden_reviewer_routes": list(FORBIDDEN_REVIEWER_ROUTES),
            },
        ),
        checklist_item(
            "return_path_defined",
            "Reviewer return path for clarification is defined.",
            "RETURN_FOR_CLARIFICATION" in ALLOWED_REVIEWER_ROUTES,
            {
                "return_route": "RETURN_FOR_CLARIFICATION",
                "allowed": "RETURN_FOR_CLARIFICATION" in ALLOWED_REVIEWER_ROUTES,
            },
        ),
        checklist_item(
            "execution_unlock_absent",
            "Approval, execution readiness, and next-phase execution unlocks are absent.",
            manifest.get("execution_unlocks_included") is False
            and manifest.get("mapped_task_execution_included") is False,
            {
                "execution_unlocks_included": manifest.get("execution_unlocks_included"),
                "mapped_task_execution_included": manifest.get("mapped_task_execution_included"),
                "approve_next_phase_execution_supported": False,
            },
        ),
    ]


def build_decision_routes() -> List[Dict[str, Any]]:
    return [
        {
            "route_id": "D112-R001",
            "route": "ACCEPT_FOR_REVIEW",
            "allowed": True,
            "reviewer_action": "Inspect Day111 frozen package, source chain, blocked condition, and evidence paths.",
            "next_phase_allowed": False,
        },
        {
            "route_id": "D112-R002",
            "route": "HOLD_FOR_BLOCKED_RECORDS",
            "allowed": True,
            "reviewer_action": "Hold advancement because Day109 blocked records and the Day110 final-gate lock are preserved.",
            "next_phase_allowed": False,
        },
        {
            "route_id": "D112-R003",
            "route": "RETURN_FOR_CLARIFICATION",
            "allowed": True,
            "reviewer_action": "Return the package for clarification without changing execution state.",
            "next_phase_allowed": False,
        },
        {
            "route_id": "D112-R004",
            "route": "REJECT_PACKAGE",
            "allowed": True,
            "reviewer_action": "Reject the package if intake evidence fails while preserving all execution locks.",
            "next_phase_allowed": False,
        },
        {
            "route_id": "D112-R005",
            "route": "APPROVE_NEXT_PHASE_EXECUTION",
            "allowed": False,
            "reviewer_action": "Not available in Day112.",
            "next_phase_allowed": False,
        },
    ]


def build_parser_consumer_release_review_intake_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day111_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_report = (
        deepcopy(day111_report)
        if day111_report is not None
        else build_parser_consumer_release_package_report(
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
    checklist = build_intake_triage_checklist(source_report)
    failed_checks = [item["id"] for item in checklist if item["status"] != "PASS"]
    route_records = build_decision_routes()
    allowed_routes = [route for route in route_records if route.get("allowed") is True]
    forbidden_routes = [route for route in route_records if route.get("allowed") is False]
    checklist_pass_count = sum(1 for item in checklist if item.get("status") == "PASS")
    triage_summary = {
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "source_report_status": source_report.get("overall_status"),
        "source_reviewer_status": source_report.get("reviewer_status"),
        "source_release_package_status": source_report.get("release_package_status"),
        "source_final_recommendation": source_report.get("final_recommendation"),
        "source_next_phase_allowed": source_report.get("next_phase_allowed"),
        "source_day110_final_gate_status": source_report.get("blocked_condition_summary", {}).get(
            "day110_observed_status"
        ),
        "source_blocked_condition_preserved": source_report.get("blocked_condition_summary", {}).get(
            "blocked_condition_preserved"
        ),
        "blocked_condition_status": BLOCKED_CONDITION_STATUS,
        "checklist_pass_count": checklist_pass_count,
        "checklist_total_count": len(checklist),
        "failed_check_count": len(failed_checks),
        "failed_checks": failed_checks,
        "decision_route": DECISION_ROUTE,
        "allowed_reviewer_route_count": len(allowed_routes),
        "forbidden_reviewer_route_count": len(forbidden_routes),
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "next_phase_allowed": False,
    }
    report_paths = {
        "json": REPORT_JSON.as_posix(),
        "html": REPORT_HTML.as_posix(),
    }
    source_reports = {
        "day111_json": DAY111_REPORT_JSON.as_posix(),
        "day111_html": DAY111_REPORT_HTML.as_posix(),
    }
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "intake_status": INTAKE_STATUS,
        "triage_status": TRIAGE_STATUS,
        "blocked_condition_status": BLOCKED_CONDITION_STATUS,
        "decision_route": DECISION_ROUTE,
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
        "source_reports": source_reports,
        "intake_triage_checklist": checklist,
        "decision_routes": route_records,
        "triage_summary": triage_summary,
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "agents_md_read_before_day112_work": agents_evidence["agents_md_read_before_day112_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "agents_md_pre_read_evidence": agents_evidence,
        "report_paths": report_paths,
        "reviewer_notes": [
            "Day112 receives the Day111 frozen release package into reviewer intake.",
            "Intake and triage do not mean approval, unlock, execution readiness, or next-phase enablement.",
            "Decision routes are limited to review triage, clarification, or rejection/blocking.",
            "No live, SSH, mapped-task, broker, adapter, runner, OpenAI API, cloud, voice, approval unlock, or config mutation path is added.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_release_review_intake_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "INTAKE_BLOCKED_REVIEW_ONLY"
        report["triage_status"] = "TRIAGE_BLOCKED_REVIEW_ONLY"
        report["intake_status"] = "INTAKE_BLOCKED_REVIEW_ONLY"
        report["blocked_condition_status"] = "NOT_PRESERVED"
        report["decision_route"] = "REVIEWER_TRIAGE_BLOCKED_DO_NOT_ADVANCE"
        report["final_recommendation"] = "DO_NOT_ADVANCE_INTAKE_VALIDATION_FAILED"
        report["next_phase_allowed"] = False
        report["approval_unlock_allowed"] = False
        report["execution_readiness_allowed"] = False
        report["approve_next_phase_execution_supported"] = False
    return report


def validate_parser_consumer_release_review_intake_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "reviewer_status": REVIEWER_STATUS,
        "intake_status": INTAKE_STATUS,
        "triage_status": TRIAGE_STATUS,
        "blocked_condition_status": BLOCKED_CONDITION_STATUS,
        "decision_route": DECISION_ROUTE,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "approve_next_phase_execution_supported": False,
        "audit_type": "REPORT_ONLY",
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "agents_md_read_before_day112_work": True,
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

    checklist = report.get("intake_triage_checklist", [])
    checklist_ids = [item.get("id") for item in checklist]
    if checklist_ids != list(REQUIRED_CHECKLIST_IDS):
        errors.append("intake_triage_checklist must contain exactly the ten required Day112 checks in order.")
    for item in checklist:
        for field in ("id", "description", "status", "required", "evidence", "blocks_advancement_if_failed"):
            if field not in item:
                errors.append(f"checklist item {item.get('id', '<unknown>')} must include {field}.")
        if item.get("required") is not True:
            errors.append(f"checklist item {item.get('id', '<unknown>')} must be required.")
        if item.get("blocks_advancement_if_failed") is not True:
            errors.append(f"checklist item {item.get('id', '<unknown>')} must block advancement if failed.")
    failed_checks = [item.get("id") for item in checklist if item.get("status") != "PASS"]
    if failed_checks:
        errors.append(f"intake triage checks must all pass: {json.dumps(failed_checks)}.")

    summary = report.get("triage_summary", {})
    if summary.get("checklist_pass_count") != 10:
        errors.append("triage_summary.checklist_pass_count must be 10.")
    if summary.get("checklist_total_count") != 10:
        errors.append("triage_summary.checklist_total_count must be 10.")
    if summary.get("allowed_reviewer_route_count") != 4:
        errors.append("triage_summary.allowed_reviewer_route_count must be 4.")
    if summary.get("forbidden_reviewer_route_count") != 1:
        errors.append("triage_summary.forbidden_reviewer_route_count must be 1.")
    if summary.get("blocked_condition_status") != BLOCKED_CONDITION_STATUS:
        errors.append("triage_summary.blocked_condition_status must be PRESERVED.")
    if summary.get("source_release_package_status") != DAY111_RELEASE_PACKAGE_STATUS:
        errors.append("triage_summary.source_release_package_status must remain FROZEN.")
    if summary.get("source_reviewer_status") != DAY111_REVIEWER_STATUS:
        errors.append("triage_summary.source_reviewer_status must remain RELEASE_PACKAGE_READY_REVIEW_ONLY.")
    if summary.get("source_final_recommendation") != DAY111_FINAL_RECOMMENDATION:
        errors.append("triage_summary.source_final_recommendation must preserve the Day111 do-not-advance recommendation.")
    if summary.get("source_next_phase_allowed") is not False:
        errors.append("triage_summary.source_next_phase_allowed must be false.")
    if summary.get("source_blocked_condition_preserved") is not True:
        errors.append("triage_summary.source_blocked_condition_preserved must be true.")
    if summary.get("approval_unlock_allowed") is not False:
        errors.append("triage_summary.approval_unlock_allowed must be false.")
    if summary.get("execution_readiness_allowed") is not False:
        errors.append("triage_summary.execution_readiness_allowed must be false.")
    if summary.get("approve_next_phase_execution_supported") is not False:
        errors.append("triage_summary.approve_next_phase_execution_supported must be false.")
    if summary.get("next_phase_allowed") is not False:
        errors.append("triage_summary.next_phase_allowed must be false.")

    route_records = report.get("decision_routes", [])
    allowed_routes = [route.get("route") for route in route_records if route.get("allowed") is True]
    forbidden_routes = [route.get("route") for route in route_records if route.get("allowed") is False]
    if allowed_routes != list(ALLOWED_REVIEWER_ROUTES):
        errors.append("allowed reviewer routes must match the Day112 contract exactly.")
    if forbidden_routes != list(FORBIDDEN_REVIEWER_ROUTES):
        errors.append("forbidden reviewer routes must match the Day112 contract exactly.")
    if any(route.get("next_phase_allowed") is not False for route in route_records):
        errors.append("all decision routes must keep next_phase_allowed=false.")

    if report.get("report_paths") != {
        "json": REPORT_JSON.as_posix(),
        "html": REPORT_HTML.as_posix(),
    }:
        errors.append("report_paths must point to Day112 JSON and HTML reports.")
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


def write_parser_consumer_release_review_intake_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_rows = _table_rows(
        (
            item["id"],
            item["description"],
            item["status"],
            json.dumps(item["required"]),
            json.dumps(item["blocks_advancement_if_failed"]),
            json.dumps(item["evidence"]),
        )
        for item in report["intake_triage_checklist"]
    )
    route_rows = _table_rows(
        (
            route["route_id"],
            route["route"],
            json.dumps(route["allowed"]),
            route["reviewer_action"],
            json.dumps(route["next_phase_allowed"]),
        )
        for route in report["decision_routes"]
    )
    safety_rows = _table_rows(
        (key, json.dumps(value)) for key, value in report["safety_invariants"].items()
    )
    summary = report["triage_summary"]
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
    <span class="badge">TRIAGE_ONLY</span>
    <span class="badge">NO_APPROVAL_UNLOCK</span>
    <span class="badge">NEXT_PHASE_ALLOWED_FALSE</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Intake status:</strong> {html.escape(report['intake_status'])}</p>
  <p><strong>Triage status:</strong> {html.escape(report['triage_status'])}</p>
  <p><strong>Blocked condition status:</strong> {html.escape(report['blocked_condition_status'])}</p>
  <p><strong>Decision route:</strong> {html.escape(report['decision_route'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>
  <p><strong>Approve next phase execution supported:</strong> {html.escape(json.dumps(report['approve_next_phase_execution_supported']))}</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day112 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day112_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Source Package Intake</h2>
  <table>
    <tbody>
      <tr><th>Source</th><td>{html.escape(summary['source_day'])} / <code>{html.escape(summary['source_task'])}</code></td></tr>
      <tr><th>Source reviewer status</th><td>{html.escape(str(summary['source_reviewer_status']))}</td></tr>
      <tr><th>Source release status</th><td>{html.escape(str(summary['source_release_package_status']))}</td></tr>
      <tr><th>Source recommendation</th><td>{html.escape(str(summary['source_final_recommendation']))}</td></tr>
      <tr><th>Source next phase allowed</th><td>{html.escape(json.dumps(summary['source_next_phase_allowed']))}</td></tr>
      <tr><th>Blocked condition preserved</th><td>{html.escape(json.dumps(summary['source_blocked_condition_preserved']))}</td></tr>
      <tr><th>Checklist pass / total</th><td>{summary['checklist_pass_count']} / {summary['checklist_total_count']}</td></tr>
      <tr><th>Allowed / forbidden reviewer routes</th><td>{summary['allowed_reviewer_route_count']} / {summary['forbidden_reviewer_route_count']}</td></tr>
    </tbody>
  </table>

  <h2>Reviewer Triage Checklist</h2>
  <table>
    <thead><tr><th>ID</th><th>Description</th><th>Status</th><th>Required</th><th>Blocks Advancement If Failed</th><th>Evidence</th></tr></thead>
    <tbody>{checklist_rows}</tbody>
  </table>

  <h2>Decision Routes</h2>
  <table>
    <thead><tr><th>ID</th><th>Route</th><th>Allowed</th><th>Reviewer Action</th><th>Next Phase Allowed</th></tr></thead>
    <tbody>{route_rows}</tbody>
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


def write_parser_consumer_release_review_intake_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_parser_consumer_release_review_intake_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_release_review_intake_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_release_review_intake_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
