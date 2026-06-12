"""Day116 reviewer deferred action register.

This module records a static follow-up queue for blocked, held, and
do-not-advance records from Day112 through Day115. It is reviewer-only and
report-only: it does not resolve queue items, unlock execution, invoke brokers
or runners, access adapters, use SSH, contact live devices, or execute commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

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
from intent_parser_consumer_reviewer_triage_closure_summary import (
    REPORT_HTML as DAY115_REPORT_HTML,
    REPORT_JSON as DAY115_REPORT_JSON,
    TASK_NAME as DAY115_TASK_NAME,
    build_parser_consumer_reviewer_triage_closure_summary_report,
)


CREATED_AT = "2026-06-12T00:00:00+08:00"
DAY = 116
DAY_ID = "Day116"
TASK_NAME = "reviewer-deferred-action-register"
TITLE = "Day116 Reviewer Deferred Action Register / Blocked Follow-up Queue"
PHASE_NAME = "Reviewer Deferred Action Register / Blocked Follow-up Queue"
SCHEMA_VERSION = "day116.reviewer_deferred_action_register.v1"
DAY_RANGE = "Day112-Day115"
REGISTER_SCOPE = "REVIEWER_DEFERRED_ACTIONS_ONLY"
REGISTER_STATUS = "DEFERRED_ACTION_REGISTER_RECORDED"
FOLLOW_UP_QUEUE_STATUS = "FOLLOW_UP_QUEUE_RECORDED"
AUDIT_TYPE = "REVIEWER_ONLY_REPORT_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day116_reviewer_deferred_action_register.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day116_reviewer_deferred_action_register.html"
AGENTS_FILE = Path("AGENTS.md")

FALSE_QUEUE_FLAGS = (
    "execution_allowed",
    "broker_allowed",
    "runner_allowed",
    "adapter_allowed",
    "ssh_allowed",
    "live_access_allowed",
    "readiness_generated",
    "next_stage_allowed",
)

ZERO_SUMMARY_COUNTS = (
    "readiness_generated_count",
    "execution_unlock_count",
    "broker_handoff_count",
    "runner_handoff_count",
    "adapter_handoff_count",
    "ssh_access_count",
    "live_access_count",
)

FORBIDDEN_STATUS_TERMS = ("READY", "READINESS")

SOURCE_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {
        "day": "Day112",
        "task": DAY112_TASK_NAME,
        "json": DAY112_REPORT_JSON.as_posix(),
        "html": DAY112_REPORT_HTML.as_posix(),
        "module": "intent_parser_consumer_release_review_intake.py",
        "doc": "docs/ai-intent/day112_parser_consumer_release_review_intake.md",
        "roadmap": "docs/roadmap/day112_parser_consumer_release_review_intake.md",
    },
    {
        "day": "Day113",
        "task": DAY113_TASK_NAME,
        "json": DAY113_REPORT_JSON.as_posix(),
        "html": DAY113_REPORT_HTML.as_posix(),
        "module": "intent_parser_consumer_reviewer_triage_decision_log.py",
        "doc": "docs/ai-intent/day113_parser_consumer_reviewer_triage_decision_log.md",
        "roadmap": "docs/roadmap/day113_parser_consumer_reviewer_triage_decision_log.md",
    },
    {
        "day": "Day114",
        "task": DAY114_TASK_NAME,
        "json": DAY114_REPORT_JSON.as_posix(),
        "html": DAY114_REPORT_HTML.as_posix(),
        "module": "intent_parser_consumer_reviewer_triage_evidence_traceability.py",
        "doc": "docs/ai-intent/day114_parser_consumer_reviewer_triage_evidence_traceability.md",
        "roadmap": "docs/roadmap/day114_parser_consumer_reviewer_triage_evidence_traceability.md",
    },
    {
        "day": "Day115",
        "task": DAY115_TASK_NAME,
        "json": DAY115_REPORT_JSON.as_posix(),
        "html": DAY115_REPORT_HTML.as_posix(),
        "module": "intent_parser_consumer_reviewer_triage_closure_summary.py",
        "doc": "docs/ai-intent/day115_parser_consumer_reviewer_triage_closure_summary.md",
        "roadmap": "docs/roadmap/day115_parser_consumer_reviewer_triage_closure_summary.md",
    },
)


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
        "agents_md_read_before_day116_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day116 records that AGENTS.md was read before deferred action register work "
            "and that the repository instruction file was not modified by this report."
        ),
    }


def _queue_item(
    item_id: str,
    origin_day: int,
    origin_task: str,
    source_status: str,
    deferred_reason: str,
    required_follow_up: str,
    source_artifact: str,
    source_field: str,
    source_value: Any,
) -> Dict[str, Any]:
    return {
        "item_id": item_id,
        "origin_day": origin_day,
        "origin_task": origin_task,
        "source_status": source_status,
        "deferred_reason": deferred_reason,
        "required_follow_up": required_follow_up,
        "review_owner": "REVIEWER",
        "execution_allowed": False,
        "broker_allowed": False,
        "runner_allowed": False,
        "adapter_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "readiness_generated": False,
        "next_stage_allowed": False,
        "source_artifact": source_artifact,
        "source_field": source_field,
        "source_value": source_value,
        "trace_note": "SOURCE_REVIEWED_DEFERRED_ITEM_FOUND",
    }


def build_deferred_action_queue(
    day112_report: Dict[str, Any],
    day113_report: Dict[str, Any],
    day114_report: Dict[str, Any],
    day115_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    queue: List[Dict[str, Any]] = []
    if day112_report.get("final_recommendation") == "REVIEW_INTAKE_ACCEPTED_DO_NOT_ADVANCE":
        queue.append(
            _queue_item(
                item_id="D116-D112-DO-NOT-ADVANCE",
                origin_day=112,
                origin_task=DAY112_TASK_NAME,
                source_status="DO_NOT_ADVANCE",
                deferred_reason="Day112 accepted the package for reviewer intake while preserving blocked conditions.",
                required_follow_up="Reviewer must keep the intake package in deferred review until blocked records are addressed by a future approved task.",
                source_artifact=DAY112_REPORT_JSON.as_posix(),
                source_field="final_recommendation",
                source_value=day112_report.get("final_recommendation"),
            )
        )
    if day113_report.get("selected_reviewer_outcome") == "HOLD_FOR_BLOCKED_RECORDS":
        queue.append(
            _queue_item(
                item_id="D116-D113-HOLD-FOR-BLOCKED-RECORDS",
                origin_day=113,
                origin_task=DAY113_TASK_NAME,
                source_status="HOLD",
                deferred_reason="Day113 selected HOLD_FOR_BLOCKED_RECORDS as the reviewer triage outcome.",
                required_follow_up="Reviewer must leave the package on hold and track the blocked records without advancing them.",
                source_artifact=DAY113_REPORT_JSON.as_posix(),
                source_field="selected_reviewer_outcome",
                source_value=day113_report.get("selected_reviewer_outcome"),
            )
        )
    for record in day114_report.get("traceability_records", []):
        if record.get("blocked_condition_id"):
            queue.append(
                _queue_item(
                    item_id=f"D116-D114-{record['blocked_condition_id']}",
                    origin_day=114,
                    origin_task=DAY114_TASK_NAME,
                    source_status="BLOCKED",
                    deferred_reason=record.get("blocked_reason", ""),
                    required_follow_up="Reviewer must keep this blocked condition visible in the follow-up queue without resolving, approving, or advancing it.",
                    source_artifact=DAY114_REPORT_JSON.as_posix(),
                    source_field=f"traceability_records.{record.get('trace_id')}.blocked_condition_id",
                    source_value=record.get("blocked_condition_id"),
                )
            )
    if day115_report.get("final_recommendation") == "DO_NOT_ADVANCE":
        queue.append(
            _queue_item(
                item_id="D116-D115-TRIAGE-CLOSURE-DO-NOT-ADVANCE",
                origin_day=115,
                origin_task=DAY115_TASK_NAME,
                source_status="DO_NOT_ADVANCE",
                deferred_reason="Day115 closed the reviewer triage chain as non-advancing with blocked records preserved.",
                required_follow_up="Reviewer must carry the closed non-advancement decision forward as a deferred queue item only.",
                source_artifact=DAY115_REPORT_JSON.as_posix(),
                source_field="final_recommendation",
                source_value=day115_report.get("final_recommendation"),
            )
        )
    return queue


def build_source_trace_notes(queue: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    origin_days = {item["origin_day"] for item in queue}
    notes = []
    for artifact in SOURCE_ARTIFACTS:
        day_number = int(artifact["day"].replace("Day", ""))
        notes.append(
            {
                "trace_id": f"D116-SOURCE-{day_number}",
                "source_day": artifact["day"],
                "source_task": artifact["task"],
                "source_artifacts": {
                    "json": artifact["json"],
                    "html": artifact["html"],
                    "module": artifact["module"],
                    "doc": artifact["doc"],
                    "roadmap": artifact["roadmap"],
                },
                "trace_status": (
                    "SOURCE_REVIEWED_DEFERRED_ITEM_FOUND"
                    if day_number in origin_days
                    else "SOURCE_REVIEWED_NO_DEFERRED_ITEM_FOUND"
                ),
                "execution_allowed": False,
                "broker_allowed": False,
                "runner_allowed": False,
                "adapter_allowed": False,
                "ssh_allowed": False,
                "live_access_allowed": False,
                "readiness_generated": False,
                "next_stage_allowed": False,
            }
        )
    return notes


def build_register_summary(queue: List[Dict[str, Any]], trace_notes: List[Dict[str, Any]]) -> Dict[str, Any]:
    blocked_count = sum(1 for item in queue if item.get("source_status") == "BLOCKED")
    hold_count = sum(1 for item in queue if item.get("source_status") == "HOLD")
    do_not_advance_count = sum(1 for item in queue if item.get("source_status") == "DO_NOT_ADVANCE")
    return {
        "status": REGISTER_STATUS,
        "day_range": DAY_RANGE,
        "register_scope": REGISTER_SCOPE,
        "source_days_reviewed": len({note["source_day"] for note in trace_notes}),
        "source_artifacts_reviewed": len(trace_notes),
        "deferred_item_count": len(queue),
        "blocked_count": blocked_count,
        "hold_count": hold_count,
        "do_not_advance_count": do_not_advance_count,
        "readiness_generated_count": 0,
        "execution_unlock_count": 0,
        "broker_handoff_count": 0,
        "runner_handoff_count": 0,
        "adapter_handoff_count": 0,
        "ssh_access_count": 0,
        "live_access_count": 0,
        "execution_allowed": False,
        "broker_allowed": False,
        "runner_allowed": False,
        "adapter_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "readiness_generated": False,
        "next_stage_allowed": False,
    }


def build_reviewer_deferred_action_register_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day112_report: Optional[Dict[str, Any]] = None,
    day113_report: Optional[Dict[str, Any]] = None,
    day114_report: Optional[Dict[str, Any]] = None,
    day115_report: Optional[Dict[str, Any]] = None,
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
    source_day115 = (
        deepcopy(day115_report)
        if day115_report is not None
        else build_parser_consumer_reviewer_triage_closure_summary_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
            day112_report=source_day112,
            day113_report=source_day113,
            day114_report=source_day114,
        )
    )
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_pre_read=agents_md_pre_read,
        agents_md_modified=agents_md_modified,
    )
    queue = build_deferred_action_queue(source_day112, source_day113, source_day114, source_day115)
    trace_notes = build_source_trace_notes(queue)
    summary = build_register_summary(queue, trace_notes)
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "status": REGISTER_STATUS,
        "follow_up_queue_status": FOLLOW_UP_QUEUE_STATUS,
        "day_range": DAY_RANGE,
        "register_scope": REGISTER_SCOPE,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "source_tasks": {
            "day112": DAY112_TASK_NAME,
            "day113": DAY113_TASK_NAME,
            "day114": DAY114_TASK_NAME,
            "day115": DAY115_TASK_NAME,
        },
        "source_reports": {
            "day112_json": DAY112_REPORT_JSON.as_posix(),
            "day112_html": DAY112_REPORT_HTML.as_posix(),
            "day113_json": DAY113_REPORT_JSON.as_posix(),
            "day113_html": DAY113_REPORT_HTML.as_posix(),
            "day114_json": DAY114_REPORT_JSON.as_posix(),
            "day114_html": DAY114_REPORT_HTML.as_posix(),
            "day115_json": DAY115_REPORT_JSON.as_posix(),
            "day115_html": DAY115_REPORT_HTML.as_posix(),
        },
        "source_artifacts": [dict(artifact) for artifact in SOURCE_ARTIFACTS],
        "deferred_action_queue": queue,
        "source_trace_notes": trace_notes,
        "register_summary": summary,
        "execution_allowed": False,
        "broker_allowed": False,
        "runner_allowed": False,
        "adapter_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "readiness_generated": False,
        "next_stage_allowed": False,
        "agents_md_read_before_day116_work": agents_evidence["agents_md_read_before_day116_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "agents_md_pre_read_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day116 records a reviewer-only deferred follow-up queue for Day112-Day115.",
            "Day116 does not resolve, approve, release, or advance any queued item.",
            "Day116 does not enter broker, runner, adapter, SSH, live access, or command execution paths.",
            "Day116 is a follow-up queue, not an approval gate.",
        ],
    }
    report["validation_errors"] = validate_reviewer_deferred_action_register_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["status"] = "DEFERRED_ACTION_REGISTER_FAILED_REVIEW_ONLY"
        report["follow_up_queue_status"] = "FOLLOW_UP_QUEUE_FAILED_REVIEW_ONLY"
        report["execution_allowed"] = False
        report["broker_allowed"] = False
        report["runner_allowed"] = False
        report["adapter_allowed"] = False
        report["ssh_allowed"] = False
        report["live_access_allowed"] = False
        report["readiness_generated"] = False
        report["next_stage_allowed"] = False
    return report


def validate_reviewer_deferred_action_register_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "status": REGISTER_STATUS,
        "follow_up_queue_status": FOLLOW_UP_QUEUE_STATUS,
        "day_range": DAY_RANGE,
        "register_scope": REGISTER_SCOPE,
        "audit_type": AUDIT_TYPE,
        "agents_md_read_before_day116_work": True,
        "agents_md_pre_read_result": "PASS",
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    for status_field in ("status", "follow_up_queue_status"):
        status_value = str(report.get(status_field, ""))
        if any(term in status_value.upper() for term in FORBIDDEN_STATUS_TERMS):
            errors.append(f"{status_field} must not use readiness wording.")

    for flag in FALSE_QUEUE_FLAGS:
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")

    queue = report.get("deferred_action_queue", [])
    if len(queue) < 1:
        errors.append("deferred_action_queue must include at least one queue item.")
    for item in queue:
        for field in (
            "item_id",
            "origin_day",
            "origin_task",
            "source_status",
            "deferred_reason",
            "required_follow_up",
            "review_owner",
            "source_artifact",
            "source_field",
            "source_value",
            "trace_note",
        ):
            if field not in item:
                errors.append(f"queue item {item.get('item_id', '<unknown>')} must include {field}.")
        if item.get("origin_day") not in {112, 113, 114, 115}:
            errors.append(f"queue item {item.get('item_id', '<unknown>')} must originate from Day112-Day115.")
        if item.get("source_status") not in {"BLOCKED", "HOLD", "DO_NOT_ADVANCE", "NOT_ACCEPTABLE_SAFETY_BLOCKED"}:
            errors.append(f"queue item {item.get('item_id', '<unknown>')} has unsupported source_status.")
        if item.get("review_owner") != "REVIEWER":
            errors.append(f"queue item {item.get('item_id', '<unknown>')} must keep review_owner REVIEWER.")
        for flag in FALSE_QUEUE_FLAGS:
            if item.get(flag) is not False:
                errors.append(f"queue item {item.get('item_id', '<unknown>')}.{flag} must be false.")

    notes = report.get("source_trace_notes", [])
    if [note.get("source_day") for note in notes] != ["Day112", "Day113", "Day114", "Day115"]:
        errors.append("source_trace_notes must cover Day112 through Day115 in order.")
    for note in notes:
        for field in ("trace_id", "source_day", "source_task", "source_artifacts", "trace_status"):
            if field not in note:
                errors.append(f"trace note {note.get('trace_id', '<unknown>')} must include {field}.")
        for flag in FALSE_QUEUE_FLAGS:
            if note.get(flag) is not False:
                errors.append(f"trace note {note.get('trace_id', '<unknown>')}.{flag} must be false.")

    summary = report.get("register_summary", {})
    expected_summary = {
        "status": REGISTER_STATUS,
        "day_range": DAY_RANGE,
        "register_scope": REGISTER_SCOPE,
        "source_days_reviewed": 4,
        "source_artifacts_reviewed": 4,
        "deferred_item_count": len(queue),
        "blocked_count": sum(1 for item in queue if item.get("source_status") == "BLOCKED"),
        "hold_count": sum(1 for item in queue if item.get("source_status") == "HOLD"),
        "do_not_advance_count": sum(1 for item in queue if item.get("source_status") == "DO_NOT_ADVANCE"),
        "execution_allowed": False,
        "broker_allowed": False,
        "runner_allowed": False,
        "adapter_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "readiness_generated": False,
        "next_stage_allowed": False,
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"register_summary.{key} must be {json.dumps(value)}.")
    for count_name in ZERO_SUMMARY_COUNTS:
        if summary.get(count_name) != 0:
            errors.append(f"register_summary.{count_name} must be 0.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day116 JSON and HTML reports.")
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


def write_reviewer_deferred_action_register_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (key, json.dumps(value) if isinstance(value, bool) else value)
        for key, value in report["register_summary"].items()
    )
    queue_rows = _table_rows(
        (
            item["item_id"],
            f"Day{item['origin_day']}",
            item["source_status"],
            item["deferred_reason"],
            item["required_follow_up"],
            json.dumps(item["execution_allowed"]),
            json.dumps(item["broker_allowed"]),
            json.dumps(item["runner_allowed"]),
            json.dumps(item["adapter_allowed"]),
            json.dumps(item["ssh_allowed"]),
            json.dumps(item["live_access_allowed"]),
            json.dumps(item["next_stage_allowed"]),
            item["source_artifact"],
            item["source_field"],
        )
        for item in report["deferred_action_queue"]
    )
    trace_rows = _table_rows(
        (
            note["trace_id"],
            note["source_day"],
            note["source_task"],
            note["trace_status"],
            json.dumps(note["execution_allowed"]),
            json.dumps(note["broker_allowed"]),
            json.dumps(note["runner_allowed"]),
            json.dumps(note["adapter_allowed"]),
            json.dumps(note["ssh_allowed"]),
            json.dumps(note["live_access_allowed"]),
        )
        for note in report["source_trace_notes"]
    )
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
    <span class="badge">REVIEWER_ONLY</span>
    <span class="badge">REPORT_ONLY</span>
    <span class="badge">DEFERRED_ACTION_REGISTER_RECORDED</span>
    <span class="badge">FOLLOW_UP_QUEUE_RECORDED</span>
    <span class="badge">NO_EXECUTION_UNLOCK</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Status:</strong> {html.escape(report['status'])}</p>
  <p><strong>Follow-up queue status:</strong> {html.escape(report['follow_up_queue_status'])}</p>
  <p><strong>Day range:</strong> {html.escape(report['day_range'])}</p>
  <p><strong>Register scope:</strong> {html.escape(report['register_scope'])}</p>
  <p>Day116 records a reviewer-only deferred follow-up queue. It does not resolve, approve, release, or advance any item.</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day116 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day116_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Register Summary</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>

  <h2>Deferred Follow-up Queue</h2>
  <table>
    <thead><tr><th>ID</th><th>Origin</th><th>Source Status</th><th>Deferred Reason</th><th>Required Follow-up</th><th>Execution</th><th>Broker</th><th>Runner</th><th>Adapter</th><th>SSH</th><th>Live Access</th><th>Next Stage</th><th>Source Artifact</th><th>Source Field</th></tr></thead>
    <tbody>{queue_rows}</tbody>
  </table>

  <h2>Source Trace Notes</h2>
  <table>
    <thead><tr><th>Trace ID</th><th>Source Day</th><th>Source Task</th><th>Trace Status</th><th>Execution</th><th>Broker</th><th>Runner</th><th>Adapter</th><th>SSH</th><th>Live Access</th></tr></thead>
    <tbody>{trace_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_reviewer_deferred_action_register_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_reviewer_deferred_action_register_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_reviewer_deferred_action_register_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_reviewer_deferred_action_register_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
