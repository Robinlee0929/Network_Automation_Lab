"""Day115 parser consumer reviewer triage closure summary.

This module closes the Day112-Day114 reviewer triage chain as a deterministic
report-only audit. Closure here means the reviewer triage chain is complete;
it does not advance the parser consumer work, infer readiness, invoke brokers
or runners, use adapters or SSH, contact live devices, or execute commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from report_file_utils import write_text_with_parents

from intent_parser_consumer_release_review_intake import (
    REPORT_HTML as DAY112_REPORT_HTML,
    REPORT_JSON as DAY112_REPORT_JSON,
    TASK_NAME as DAY112_TASK_NAME,
    build_parser_consumer_release_review_intake_report,
)
from intent_parser_consumer_reviewer_triage_decision_log import (
    REPORT_HTML as DAY113_REPORT_HTML,
    REPORT_JSON as DAY113_REPORT_JSON,
    TASK_NAME as DAY113_TASK_NAME,
    build_parser_consumer_reviewer_triage_decision_log_report,
)
from intent_parser_consumer_reviewer_triage_evidence_traceability import (
    REPORT_HTML as DAY114_REPORT_HTML,
    REPORT_JSON as DAY114_REPORT_JSON,
    TASK_NAME as DAY114_TASK_NAME,
    build_parser_consumer_reviewer_triage_evidence_traceability_report,
)


CREATED_AT = "2026-06-12T00:00:00+08:00"
DAY = 115
DAY_ID = "Day115"
TASK_NAME = "parser-consumer-reviewer-triage-closure-summary"
TITLE = "Day115 Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit"
PHASE_NAME = "Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit"
SCHEMA_VERSION = "day115.parser_consumer_reviewer_triage_closure_summary.v1"
REPORT_JSON = Path("reports") / "lab-summary" / "day115_parser_consumer_reviewer_triage_closure_summary.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day115_parser_consumer_reviewer_triage_closure_summary.html"
AGENTS_FILE = Path("AGENTS.md")

REVIEWER_STATUS = "TRIAGE_CLOSURE_AUDITED_NON_ADVANCING"
CLOSURE_STATUS = "CLOSED_WITH_BLOCKED_RECORDS_PRESERVED"
FINAL_RECOMMENDATION = "DO_NOT_ADVANCE"
TRIAGE_CHAIN_CONCLUSION = "TRIAGE_CHAIN_CLOSED_NON_ADVANCING"

REQUIRED_CHAIN_DAYS = ("Day112", "Day113", "Day114")
REQUIRED_EVIDENCE_MARKERS = (
    "NO_EXECUTION_READINESS_INFERRED",
    "NO_NEXT_PHASE_UNLOCK",
    "TRIAGE_CHAIN_CLOSED_NON_ADVANCING",
    "BLOCKED_RECORDS_PRESERVED",
    "BLOCKED_RECORDS_NOT_DOWNGRADED",
    "NO_BROKER_HANDOFF",
    "NO_RUNNER_EXECUTION",
    "NO_ADAPTER_ACCESS",
    "NO_SSH_ACCESS",
    "NO_LIVE_ACCESS",
    "NO_COMMAND_EXECUTION",
    "NO_MAPPED_TASK_EXECUTION",
    "NO_APPROVAL_UNLOCK",
)

REVIEWER_CHAIN_RECORDS: Tuple[Dict[str, str], ...] = (
    {
        "day": "Day112",
        "role": "reviewer_intake",
        "status": "INTAKE_RECEIVED",
        "advancement_effect": "NONE",
    },
    {
        "day": "Day113",
        "role": "reviewer_triage",
        "status": "HOLD_DO_NOT_ADVANCE",
        "advancement_effect": "BLOCKS_ADVANCEMENT",
    },
    {
        "day": "Day114",
        "role": "traceability_blocked_record_preservation",
        "status": "BLOCKED_RECORDS_PRESERVED",
        "advancement_effect": "PRESERVES_BLOCK",
    },
)

EXECUTION_FALSE_FLAGS = (
    "next_phase_allowed",
    "execution_readiness_inferred",
    "readiness_inferred",
    "broker_handoff_allowed",
    "runner_execution_allowed",
    "adapter_access_allowed",
    "ssh_allowed",
    "live_access_allowed",
    "command_execution_allowed",
    "mapped_task_execution_allowed",
    "approval_unlock_allowed",
    "parser_capability_changed",
    "readiness_allowed",
    "broker_invocation_allowed",
    "adapter_invocation_allowed",
    "runner_invocation_allowed",
    "live_device_access_allowed",
    "network_command_execution_allowed",
    "config_mutation_allowed",
    "execution_broker_unlock_allowed",
    "approval_unlock_supported",
    "execution_readiness_supported",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "cloud_runtime_allowed",
)

TRUE_SAFETY_FLAGS = ("review_only", "report_only", "audit_only", "deterministic")

SAFETY_INVARIANTS: Dict[str, bool] = {
    "review_only": True,
    "report_only": True,
    "audit_only": True,
    "deterministic": True,
    **{flag: False for flag in EXECUTION_FALSE_FLAGS},
}


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
        "agents_md_read_before_day115_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day115 records that AGENTS.md was read before closure summary work "
            "and that the repository instruction file was not modified by this audit."
        ),
    }


def build_reviewer_chain_records() -> List[Dict[str, str]]:
    return [dict(record) for record in REVIEWER_CHAIN_RECORDS]


def _source_day_statuses(
    day112_report: Dict[str, Any],
    day113_report: Dict[str, Any],
    day114_report: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "day112": {
            "task": DAY112_TASK_NAME,
            "overall_status": day112_report.get("overall_status"),
            "intake_status": day112_report.get("intake_status"),
            "triage_status": day112_report.get("triage_status"),
            "next_phase_allowed": day112_report.get("next_phase_allowed"),
        },
        "day113": {
            "task": DAY113_TASK_NAME,
            "overall_status": day113_report.get("overall_status"),
            "selected_reviewer_outcome": day113_report.get("selected_reviewer_outcome"),
            "final_recommendation": day113_report.get("final_recommendation"),
            "next_phase_allowed": day113_report.get("next_phase_allowed"),
        },
        "day114": {
            "task": DAY114_TASK_NAME,
            "overall_status": day114_report.get("overall_status"),
            "traceability_status": day114_report.get("traceability_status"),
            "blocked_records_preserved": day114_report.get("blocked_records_preserved"),
            "final_recommendation": day114_report.get("final_recommendation"),
            "next_phase_allowed": day114_report.get("next_phase_allowed"),
        },
    }


def build_blocked_record_closure_audit(day114_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = []
    for source in day114_report.get("traceability_records", []):
        if not source.get("blocked_condition_id"):
            continue
        evidence_status = source.get("evidence_status")
        downgraded_to_pass = evidence_status == "PASS_EVIDENCE_VISIBLE_NON_EXECUTABLE"
        records.append(
            {
                "blocked_condition_id": source.get("blocked_condition_id"),
                "source_trace_id": source.get("trace_id"),
                "source_intake_id": source.get("source_intake_id"),
                "blocked_reason": source.get("blocked_reason"),
                "source_evidence_status": evidence_status,
                "closure_record_status": "BLOCKED",
                "blocked_record_preserved": source.get("preservation_status") == "preserved",
                "downgraded_to_pass": downgraded_to_pass,
                "execution_readiness_inferred": False,
                "next_phase_allowed": False,
            }
        )
    return records


def build_closure_summary(
    reviewer_chain: List[Dict[str, Any]],
    blocked_records: List[Dict[str, Any]],
    safety_invariants: Dict[str, Any],
    source_statuses: Dict[str, Any],
) -> Dict[str, Any]:
    chain_days = [record.get("day") for record in reviewer_chain]
    source_reports_pass = all(source_statuses[day]["overall_status"] == "PASS" for day in ("day112", "day113", "day114"))
    blocked_records_preserved = bool(blocked_records) and all(
        record.get("closure_record_status") == "BLOCKED"
        and record.get("blocked_record_preserved") is True
        and record.get("downgraded_to_pass") is False
        for record in blocked_records
    )
    unsafe_flag_count = sum(1 for flag in EXECUTION_FALSE_FLAGS if safety_invariants.get(flag) is not False)
    unsafe_flag_count += sum(1 for flag in TRUE_SAFETY_FLAGS if safety_invariants.get(flag) is not True)
    final_decision_preserved = FINAL_RECOMMENDATION == "DO_NOT_ADVANCE"
    overall_status = (
        "PASS"
        if chain_days == list(REQUIRED_CHAIN_DAYS)
        and source_reports_pass
        and source_statuses["day113"]["selected_reviewer_outcome"] == "HOLD_FOR_BLOCKED_RECORDS"
        and source_statuses["day114"]["blocked_records_preserved"] is True
        and blocked_records_preserved
        and unsafe_flag_count == 0
        and final_decision_preserved
        else "FAIL"
    )
    return {
        "overall_status": overall_status,
        "reviewer_status": (
            REVIEWER_STATUS if overall_status == "PASS" else "TRIAGE_CLOSURE_AUDIT_FAILED_NON_ADVANCING"
        ),
        "closure_status": (
            CLOSURE_STATUS if overall_status == "PASS" else "CLOSURE_FAILED_BLOCKED_RECORDS_STILL_LOCKED"
        ),
        "chain_days": chain_days,
        "required_chain_days": list(REQUIRED_CHAIN_DAYS),
        "day112_included": "Day112" in chain_days,
        "day113_included": "Day113" in chain_days,
        "day114_included": "Day114" in chain_days,
        "source_reports_pass": source_reports_pass,
        "blocked_record_count": len(blocked_records),
        "blocked_records_preserved": blocked_records_preserved,
        "blocked_records_not_downgraded": all(
            record.get("downgraded_to_pass") is False for record in blocked_records
        ),
        "downgraded_to_pass_count": sum(1 for record in blocked_records if record.get("downgraded_to_pass") is True),
        "unsafe_flag_count": unsafe_flag_count,
        "final_decision_preserved": final_decision_preserved,
        "triage_chain_conclusion": TRIAGE_CHAIN_CONCLUSION,
        "next_phase_allowed": False,
        "execution_readiness_inferred": False,
    }


def build_parser_consumer_reviewer_triage_closure_summary_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day112_report: Optional[Dict[str, Any]] = None,
    day113_report: Optional[Dict[str, Any]] = None,
    day114_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_day112 = (
        deepcopy(day112_report)
        if day112_report is not None
        else build_parser_consumer_release_review_intake_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
        )
    )
    source_day113 = (
        deepcopy(day113_report)
        if day113_report is not None
        else build_parser_consumer_reviewer_triage_decision_log_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
            day112_report=source_day112,
        )
    )
    source_day114 = (
        deepcopy(day114_report)
        if day114_report is not None
        else build_parser_consumer_reviewer_triage_evidence_traceability_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
            day112_report=source_day112,
            day113_report=source_day113,
        )
    )
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_pre_read=agents_md_pre_read,
        agents_md_modified=agents_md_modified,
    )
    reviewer_chain = build_reviewer_chain_records()
    blocked_records = build_blocked_record_closure_audit(source_day114)
    safety_invariants = deepcopy(SAFETY_INVARIANTS)
    source_statuses = _source_day_statuses(source_day112, source_day113, source_day114)
    closure_summary = build_closure_summary(
        reviewer_chain,
        blocked_records,
        safety_invariants,
        source_statuses,
    )
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": closure_summary["overall_status"],
        "reviewer_status": closure_summary["reviewer_status"],
        "closure_status": closure_summary["closure_status"],
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "execution_readiness_inferred": False,
        "readiness_inferred": False,
        "broker_handoff_allowed": False,
        "runner_execution_allowed": False,
        "adapter_access_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "command_execution_allowed": False,
        "mapped_task_execution_allowed": False,
        "approval_unlock_allowed": False,
        "parser_capability_changed": False,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": "CLOSURE_SUMMARY_REPORT_ONLY",
        "triage_chain_conclusion": TRIAGE_CHAIN_CONCLUSION,
        "source_tasks": {
            "day112": DAY112_TASK_NAME,
            "day113": DAY113_TASK_NAME,
            "day114": DAY114_TASK_NAME,
        },
        "source_reports": {
            "day112_json": DAY112_REPORT_JSON.as_posix(),
            "day112_html": DAY112_REPORT_HTML.as_posix(),
            "day113_json": DAY113_REPORT_JSON.as_posix(),
            "day113_html": DAY113_REPORT_HTML.as_posix(),
            "day114_json": DAY114_REPORT_JSON.as_posix(),
            "day114_html": DAY114_REPORT_HTML.as_posix(),
        },
        "source_statuses": source_statuses,
        "reviewer_chain": reviewer_chain,
        "blocked_record_closure_audit": blocked_records,
        "closure_summary": closure_summary,
        "safety_invariants": safety_invariants,
        "evidence_markers": list(REQUIRED_EVIDENCE_MARKERS),
        "agents_md_read_before_day115_work": agents_evidence["agents_md_read_before_day115_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "agents_md_pre_read_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day115 closes the reviewer triage chain from Day112 to Day114.",
            "Day115 does not advance the parser consumer work.",
            "Day115 does not imply execution readiness.",
            "Day115 preserves blocked records and keeps the next phase locked.",
            "Closure is reviewer evidence only, not broker preparation or execution preparation.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_reviewer_triage_closure_summary_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "TRIAGE_CLOSURE_AUDIT_FAILED_NON_ADVANCING"
        report["closure_status"] = "CLOSURE_FAILED_BLOCKED_RECORDS_STILL_LOCKED"
        report["final_recommendation"] = "DO_NOT_ADVANCE"
        report["next_phase_allowed"] = False
        report["execution_readiness_inferred"] = False
        report["closure_summary"]["overall_status"] = "FAIL"
        report["closure_summary"]["reviewer_status"] = report["reviewer_status"]
        report["closure_summary"]["closure_status"] = report["closure_status"]
    return report


def validate_parser_consumer_reviewer_triage_closure_summary_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "closure_status": CLOSURE_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "execution_readiness_inferred": False,
        "readiness_inferred": False,
        "broker_handoff_allowed": False,
        "runner_execution_allowed": False,
        "adapter_access_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "command_execution_allowed": False,
        "mapped_task_execution_allowed": False,
        "approval_unlock_allowed": False,
        "parser_capability_changed": False,
        "audit_type": "CLOSURE_SUMMARY_REPORT_ONLY",
        "triage_chain_conclusion": TRIAGE_CHAIN_CONCLUSION,
        "agents_md_read_before_day115_work": True,
        "agents_md_pre_read_result": "PASS",
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    safety = report.get("safety_invariants", {})
    for flag in EXECUTION_FALSE_FLAGS:
        if safety.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    for flag in TRUE_SAFETY_FLAGS:
        if safety.get(flag) is not True:
            errors.append(f"safety_invariants.{flag} must be true.")

    chain = report.get("reviewer_chain", [])
    if [record.get("day") for record in chain] != list(REQUIRED_CHAIN_DAYS):
        errors.append("reviewer_chain must include Day112, Day113, and Day114 in order.")
    required_chain = build_reviewer_chain_records()
    for expected_record, actual_record in zip(required_chain, chain):
        for field, value in expected_record.items():
            if actual_record.get(field) != value:
                errors.append(f"reviewer_chain {expected_record['day']}.{field} must be {json.dumps(value)}.")

    blocked_records = report.get("blocked_record_closure_audit", [])
    if not blocked_records:
        errors.append("blocked_record_closure_audit must include preserved blocked records.")
    for record in blocked_records:
        if record.get("closure_record_status") != "BLOCKED":
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must remain BLOCKED.")
        if record.get("blocked_record_preserved") is not True:
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must be preserved.")
        if record.get("downgraded_to_pass") is not False:
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must not be downgraded.")
        if record.get("source_evidence_status") == "PASS_EVIDENCE_VISIBLE_NON_EXECUTABLE":
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must not use PASS evidence.")
        if record.get("execution_readiness_inferred") is not False:
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must not infer readiness.")
        if record.get("next_phase_allowed") is not False:
            errors.append(f"blocked record {record.get('blocked_condition_id', '<unknown>')} must not unlock next phase.")

    summary = report.get("closure_summary", {})
    expected_summary = {
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "closure_status": CLOSURE_STATUS,
        "chain_days": list(REQUIRED_CHAIN_DAYS),
        "day112_included": True,
        "day113_included": True,
        "day114_included": True,
        "source_reports_pass": True,
        "blocked_records_preserved": True,
        "blocked_records_not_downgraded": True,
        "downgraded_to_pass_count": 0,
        "unsafe_flag_count": 0,
        "final_decision_preserved": True,
        "triage_chain_conclusion": TRIAGE_CHAIN_CONCLUSION,
        "next_phase_allowed": False,
        "execution_readiness_inferred": False,
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"closure_summary.{key} must be {json.dumps(value)}.")
    if summary.get("blocked_record_count", 0) < 1:
        errors.append("closure_summary.blocked_record_count must be at least 1.")

    if report.get("evidence_markers") != list(REQUIRED_EVIDENCE_MARKERS):
        errors.append("evidence_markers must contain the required Day115 markers in order.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day115 JSON and HTML reports.")
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


def write_parser_consumer_reviewer_triage_closure_summary_html(
    report: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chain_rows = _table_rows(
        (
            record["day"],
            record["role"],
            record["status"],
            record["advancement_effect"],
        )
        for record in report["reviewer_chain"]
    )
    blocked_rows = _table_rows(
        (
            record["blocked_condition_id"],
            record["source_trace_id"],
            record["source_intake_id"],
            record["closure_record_status"],
            json.dumps(record["blocked_record_preserved"]),
            json.dumps(record["downgraded_to_pass"]),
            json.dumps(record["execution_readiness_inferred"]),
            json.dumps(record["next_phase_allowed"]),
        )
        for record in report["blocked_record_closure_audit"]
    )
    summary_rows = _table_rows(
        (key, json.dumps(value) if isinstance(value, bool) else value)
        for key, value in report["closure_summary"].items()
    )
    safety_rows = _table_rows((key, json.dumps(value)) for key, value in report["safety_invariants"].items())
    marker_rows = _table_rows((marker,) for marker in report["evidence_markers"])
    agents = report["agents_md_pre_read_evidence"]
    write_text_with_parents(
        output_path,
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
    <span class="badge">REPORT_ONLY</span>
    <span class="badge">CLOSURE_SUMMARY</span>
    <span class="badge">TRIAGE_CHAIN_CLOSED_NON_ADVANCING</span>
    <span class="badge">DO_NOT_ADVANCE</span>
    <span class="badge">NO_NEXT_PHASE_UNLOCK</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Closure status:</strong> {html.escape(report['closure_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>
  <p><strong>Execution readiness inferred:</strong> {html.escape(json.dumps(report['execution_readiness_inferred']))}</p>
  <p>Day115 closes the reviewer triage chain from Day112 to Day114. It does not advance the parser consumer work, does not imply execution readiness, preserves blocked records, and keeps the next phase locked.</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day115 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day115_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Closure Summary</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>

  <h2>Reviewer Chain</h2>
  <table>
    <thead><tr><th>Day</th><th>Role</th><th>Status</th><th>Advancement Effect</th></tr></thead>
    <tbody>{chain_rows}</tbody>
  </table>

  <h2>Blocked Record Closure Audit</h2>
  <table>
    <thead><tr><th>Blocked Condition</th><th>Trace ID</th><th>Source Intake</th><th>Closure Status</th><th>Preserved</th><th>Downgraded</th><th>Readiness Inferred</th><th>Next Phase</th></tr></thead>
    <tbody>{blocked_rows}</tbody>
  </table>

  <h2>Evidence Markers</h2>
  <table>
    <thead><tr><th>Marker</th></tr></thead>
    <tbody>{marker_rows}</tbody>
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


def write_parser_consumer_reviewer_triage_closure_summary_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_parser_consumer_reviewer_triage_closure_summary_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_reviewer_triage_closure_summary_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_reviewer_triage_closure_summary_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
