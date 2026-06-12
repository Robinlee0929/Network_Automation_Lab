"""Day117 deferred action traceability review.

This module builds a static follow-up ownership matrix on top of the Day116
deferred action register. It is reviewer-only and non-advancing: it does not
resolve items, generate readiness, invoke brokers or runners, access adapters,
use SSH, contact live devices, or execute commands.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_reviewer_deferred_action_register import (
    FALSE_QUEUE_FLAGS,
    REPORT_JSON as DAY116_REPORT_JSON,
    TASK_NAME as DAY116_TASK_NAME,
    build_reviewer_deferred_action_register_report,
)


CREATED_AT = "2026-06-12T00:00:00+08:00"
DAY = 117
DAY_ID = "Day117"
TASK_NAME = "deferred-action-traceability-review"
TITLE = "Day117 Deferred Action Traceability Review / Follow-up Ownership Matrix"
PHASE_NAME = "Deferred Action Traceability Review / Follow-up Ownership Matrix"
SCHEMA_VERSION = "day117.deferred_action_traceability_review.v1"
SOURCE_DAY = "Day116"
EXPECTED_DEFERRED_ITEM_COUNT = 7
STATUS_READY = "DEFERRED_ACTION_TRACEABILITY_REVIEW_READY"
STATUS_COUNT_MISMATCH = "DEFERRED_ITEM_COUNT_MISMATCH_REVIEW_REQUIRED"
STATUS_SAFETY_VIOLATION = "SAFETY_INVARIANT_VIOLATION_REVIEW_REQUIRED"
FINAL_RECOMMENDATION = "REVIEW_ONLY_NON_ADVANCING"
MATRIX_SCOPE = "DAY116_DEFERRED_ACTION_TRACEABILITY_ONLY"
AUDIT_TYPE = "REVIEWER_ONLY_REPORT_ONLY_NON_ADVANCING"
REPORT_JSON = Path("reports") / "lab-summary" / "day117_deferred_action_traceability_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day117_deferred_action_traceability_review.html"

OWNER_BY_SOURCE_STATUS = {
    "BLOCKED": "evidence_owner",
    "HOLD": "release_reviewer",
    "DO_NOT_ADVANCE": "reviewer",
}

FOLLOW_UP_BY_SOURCE_STATUS = {
    "BLOCKED": "evidence_gap_review",
    "HOLD": "release_hold_review",
    "DO_NOT_ADVANCE": "traceability_follow_up",
}

OWNER_BY_ITEM_ID = {
    "D116-D112-DO-NOT-ADVANCE": "release_reviewer",
    "D116-D113-HOLD-FOR-BLOCKED-RECORDS": "reviewer",
    "D116-D115-TRIAGE-CLOSURE-DO-NOT-ADVANCE": "safety_gate_owner",
}

FOLLOW_UP_BY_ITEM_ID = {
    "D116-D112-DO-NOT-ADVANCE": "consumer_contract_review",
    "D116-D113-HOLD-FOR-BLOCKED-RECORDS": "release_hold_review",
    "D116-D115-TRIAGE-CLOSURE-DO-NOT-ADVANCE": "safety_boundary_review",
}

ALLOWED_OWNER_ROLES = {
    "reviewer",
    "parser_contract_owner",
    "evidence_owner",
    "safety_gate_owner",
    "documentation_owner",
    "release_reviewer",
}

ALLOWED_FOLLOW_UP_TYPES = {
    "evidence_gap_review",
    "policy_clarification",
    "traceability_follow_up",
    "safety_boundary_review",
    "documentation_alignment",
    "release_hold_review",
    "consumer_contract_review",
}


def _bool_false_summary() -> Dict[str, bool]:
    return {flag: False for flag in FALSE_QUEUE_FLAGS}


def _matrix_item(day116_item: Dict[str, Any], review_sequence: int) -> Dict[str, Any]:
    item_id = day116_item["item_id"]
    source_status = day116_item.get("source_status", "")
    owner_role = OWNER_BY_ITEM_ID.get(item_id, OWNER_BY_SOURCE_STATUS.get(source_status, "reviewer"))
    follow_up_type = FOLLOW_UP_BY_ITEM_ID.get(
        item_id,
        FOLLOW_UP_BY_SOURCE_STATUS.get(source_status, "traceability_follow_up"),
    )
    deferred_summary = (
        f"{source_status} item from Day{day116_item['origin_day']} remains deferred: "
        f"{day116_item['deferred_reason']}"
    )
    blocking_reason = (
        f"Day116 preserved {source_status} without approval, readiness, or execution unlock; "
        f"the item requires reviewer evidence before any future separately approved task may reconsider it."
    )
    required_evidence = (
        f"Review {day116_item['source_artifact']} field {day116_item['source_field']} and preserve "
        f"Day116 item {item_id} with execution, broker, runner, adapter, SSH, live access, readiness, "
        f"and next-stage flags all false."
    )
    closure_condition = (
        "A future explicitly approved review-only task records sufficient evidence and keeps this Day117 "
        "matrix item non-executing; Day117 itself does not close or unblock the item."
    )
    result = {
        "deferred_id": item_id,
        "source_day": SOURCE_DAY,
        "source_artifact": DAY116_REPORT_JSON.as_posix(),
        "source_item_artifact": day116_item["source_artifact"],
        "source_item_field": day116_item["source_field"],
        "source_item_status": source_status,
        "deferred_summary": deferred_summary,
        "owner_role": owner_role,
        "follow_up_type": follow_up_type,
        "blocking_reason": blocking_reason,
        "review_sequence": review_sequence,
        "required_evidence": required_evidence,
        "closure_condition": closure_condition,
        "status": "DEFERRED_FOLLOW_UP_REVIEW_ONLY",
        **_bool_false_summary(),
    }
    return result


def build_follow_up_ownership_matrix(day116_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    queue = deepcopy(day116_report.get("deferred_action_queue", []))
    return [_matrix_item(item, index) for index, item in enumerate(queue, start=1)]


def build_matrix_summary(matrix: List[Dict[str, Any]], validation_errors: List[str]) -> Dict[str, Any]:
    unsafe_flag_count = sum(
        1
        for item in matrix
        for flag in FALSE_QUEUE_FLAGS
        if item.get(flag) is not False
    )
    sequence_values = [item.get("review_sequence") for item in matrix]
    if len(matrix) != EXPECTED_DEFERRED_ITEM_COUNT:
        status = STATUS_COUNT_MISMATCH
    elif unsafe_flag_count:
        status = STATUS_SAFETY_VIOLATION
    elif validation_errors:
        status = "DEFERRED_ACTION_TRACEABILITY_REVIEW_FAILED"
    else:
        status = STATUS_READY
    return {
        "status": status,
        "matrix_scope": MATRIX_SCOPE,
        "source_task": DAY116_TASK_NAME,
        "source_artifact": DAY116_REPORT_JSON.as_posix(),
        "total_deferred_items_reviewed": len(matrix),
        "expected_deferred_item_count": EXPECTED_DEFERRED_ITEM_COUNT,
        "ownership_matrix_status": "RECORDED" if not validation_errors else "REVIEW_REQUIRED",
        "traceability_status": "TRACEABLE_TO_DAY116" if len(matrix) == EXPECTED_DEFERRED_ITEM_COUNT else "COUNT_MISMATCH",
        "review_sequence_count": len(set(sequence_values)),
        "unsafe_flag_count": unsafe_flag_count,
        "final_recommendation": FINAL_RECOMMENDATION,
        **_bool_false_summary(),
    }


def build_deferred_action_traceability_review_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day116_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_day116 = (
        deepcopy(day116_report)
        if day116_report is not None
        else build_reviewer_deferred_action_register_report(
            project_root=project_root,
            agents_md_pre_read=agents_md_pre_read,
            agents_md_modified=agents_md_modified,
        )
    )
    matrix = build_follow_up_ownership_matrix(source_day116)
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "status": STATUS_READY,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "matrix_scope": MATRIX_SCOPE,
        "source_day": SOURCE_DAY,
        "source_task": DAY116_TASK_NAME,
        "source_artifact": DAY116_REPORT_JSON.as_posix(),
        "source_day116_status": source_day116.get("status"),
        "source_day116_deferred_item_count": len(source_day116.get("deferred_action_queue", [])),
        "follow_up_ownership_matrix": matrix,
        "final_recommendation": FINAL_RECOMMENDATION,
        "agents_md_read_before_day117_work": agents_md_pre_read,
        "agents_md_modified": agents_md_modified,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day117 adds ownership and evidence traceability fields to the Day116 deferred queue only.",
            "Day117 does not resolve, unblock, approve, release, or advance any Day116 deferred item.",
            "Day117 does not enter broker, runner, adapter, SSH, live access, or command execution paths.",
            "Day117 does not generate readiness or next-stage approval.",
        ],
        **_bool_false_summary(),
    }
    report["validation_errors"] = validate_deferred_action_traceability_review_report(report)
    report["matrix_summary"] = build_matrix_summary(matrix, report["validation_errors"])
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["status"] = report["matrix_summary"]["status"]
    return report


def validate_deferred_action_traceability_review_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "status": STATUS_READY,
        "matrix_scope": MATRIX_SCOPE,
        "source_day": SOURCE_DAY,
        "source_task": DAY116_TASK_NAME,
        "source_artifact": DAY116_REPORT_JSON.as_posix(),
        "final_recommendation": FINAL_RECOMMENDATION,
        "agents_md_read_before_day117_work": True,
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    for flag in FALSE_QUEUE_FLAGS:
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")

    matrix = report.get("follow_up_ownership_matrix", [])
    if len(matrix) != EXPECTED_DEFERRED_ITEM_COUNT:
        errors.append(
            "follow_up_ownership_matrix must contain exactly "
            f"{EXPECTED_DEFERRED_ITEM_COUNT} Day116 deferred items."
        )

    sequence_values = [item.get("review_sequence") for item in matrix]
    if sequence_values != list(range(1, len(matrix) + 1)):
        errors.append("review_sequence must be deterministic and cover 1 through the matrix length.")
    if len(matrix) == EXPECTED_DEFERRED_ITEM_COUNT and sequence_values != list(
        range(1, EXPECTED_DEFERRED_ITEM_COUNT + 1)
    ):
        errors.append("review_sequence must cover 1 through 7.")

    seen_ids = set()
    for item in matrix:
        deferred_id = item.get("deferred_id", "<unknown>")
        if deferred_id in seen_ids:
            errors.append(f"deferred item {deferred_id} must not be duplicated.")
        seen_ids.add(deferred_id)
        for field in (
            "deferred_id",
            "source_day",
            "source_artifact",
            "deferred_summary",
            "owner_role",
            "follow_up_type",
            "blocking_reason",
            "review_sequence",
            "required_evidence",
            "closure_condition",
            "status",
        ):
            if not item.get(field):
                errors.append(f"deferred item {deferred_id} must include {field}.")
        if item.get("source_day") != SOURCE_DAY:
            errors.append(f"deferred item {deferred_id}.source_day must be {SOURCE_DAY}.")
        if item.get("source_artifact") != DAY116_REPORT_JSON.as_posix():
            errors.append(f"deferred item {deferred_id}.source_artifact must point to Day116 JSON.")
        if item.get("owner_role") not in ALLOWED_OWNER_ROLES:
            errors.append(f"deferred item {deferred_id}.owner_role must use the controlled role vocabulary.")
        if item.get("follow_up_type") not in ALLOWED_FOLLOW_UP_TYPES:
            errors.append(f"deferred item {deferred_id}.follow_up_type must use the controlled follow-up vocabulary.")
        if item.get("status") != "DEFERRED_FOLLOW_UP_REVIEW_ONLY":
            errors.append(f"deferred item {deferred_id}.status must remain review-only.")
        for flag in FALSE_QUEUE_FLAGS:
            if item.get(flag) is not False:
                errors.append(f"deferred item {deferred_id}.{flag} must be false.")

    summary = report.get("matrix_summary", {})
    if summary:
        expected_summary = {
            "matrix_scope": MATRIX_SCOPE,
            "source_task": DAY116_TASK_NAME,
            "source_artifact": DAY116_REPORT_JSON.as_posix(),
            "total_deferred_items_reviewed": len(matrix),
            "expected_deferred_item_count": EXPECTED_DEFERRED_ITEM_COUNT,
            "review_sequence_count": len(set(sequence_values)),
            "unsafe_flag_count": 0,
            "final_recommendation": FINAL_RECOMMENDATION,
        }
        for key, value in expected_summary.items():
            if summary.get(key) != value:
                errors.append(f"matrix_summary.{key} must be {json.dumps(value)}.")
        for flag in FALSE_QUEUE_FLAGS:
            if summary.get(flag) is not False:
                errors.append(f"matrix_summary.{flag} must be false.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day117 JSON and HTML reports.")
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


def write_deferred_action_traceability_review_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["matrix_summary"]
    summary_rows = _table_rows(
        (key, json.dumps(value) if isinstance(value, bool) else value)
        for key, value in summary.items()
    )
    matrix_rows = _table_rows(
        (
            item["review_sequence"],
            item["deferred_id"],
            item["owner_role"],
            item["follow_up_type"],
            item["blocking_reason"],
            item["required_evidence"],
            item["closure_condition"],
            json.dumps(item["execution_allowed"]),
            json.dumps(item["broker_allowed"]),
            json.dumps(item["runner_allowed"]),
            json.dumps(item["adapter_allowed"]),
            json.dumps(item["ssh_allowed"]),
            json.dumps(item["live_access_allowed"]),
            json.dumps(item["readiness_generated"]),
            json.dumps(item["next_stage_allowed"]),
        )
        for item in report["follow_up_ownership_matrix"]
    )
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
    <span class="badge">NON_ADVANCING</span>
    <span class="badge">NO_EXECUTION_UNLOCK</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Status:</strong> {html.escape(report['status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p>Day117 adds owner, follow-up type, blocking reason, review sequence, and evidence requirements to Day116 deferred items only.</p>

  <h2>Matrix Summary</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>

  <h2>Follow-up Ownership Matrix</h2>
  <table>
    <thead><tr><th>Seq</th><th>Deferred ID</th><th>Owner Role</th><th>Follow-up Type</th><th>Blocking Reason</th><th>Required Evidence</th><th>Closure Condition</th><th>Execution</th><th>Broker</th><th>Runner</th><th>Adapter</th><th>SSH</th><th>Live</th><th>Readiness</th><th>Next Stage</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_deferred_action_traceability_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_deferred_action_traceability_review_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_deferred_action_traceability_review_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_deferred_action_traceability_review_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
