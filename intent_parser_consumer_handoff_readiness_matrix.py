"""Day109 parser consumer handoff readiness matrix.

This module converts Day108 parser contract consumer handoff records into a
reviewer-facing readiness matrix. It is deterministic and report-only: it does
not execute commands, call adapters or brokers, use SSH, contact live devices,
call OpenAI APIs, unlock approvals, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_contract_consumer_handoff import (
    BLOCKED_UNSAFE_OR_UNSUPPORTED,
    NEEDS_REVIEWER_CLARIFICATION,
    READY_FOR_REVIEW_HANDOFF,
    REPORT_JSON as DAY108_REPORT_JSON,
    TASK_NAME as DAY108_TASK_NAME,
    build_parser_contract_consumer_handoff_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
TASK_NAME = "parser-consumer-handoff-readiness-matrix"
TITLE = "Day109 Parser Consumer Handoff Readiness Matrix"
SOURCE_DAY = "Day108"
SOURCE_TASK = DAY108_TASK_NAME
SCHEMA_VERSION = "day109.parser_consumer_handoff_readiness_matrix.v1"
REPORT_JSON = Path("reports") / "lab-summary" / "day109_parser_consumer_handoff_readiness_matrix.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day109_parser_consumer_handoff_readiness_matrix.html"

READY = "READY"
NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
BLOCKED = "BLOCKED"
READINESS_STATUSES = (READY, NEEDS_CLARIFICATION, BLOCKED)

SAFETY_FLAG_FIELDS = (
    "unsafe_flag",
    "live_flag",
    "ssh_flag",
    "write_flag",
    "command_execution_flag",
    "mapped_task_execution_flag",
)

SAFETY_INVARIANTS: Dict[str, Any] = {
    "review_only": True,
    "no_live_execution": True,
    "no_ssh": True,
    "no_write": True,
    "no_command_execution": True,
    "no_mapped_task_execution": True,
    "openai_api_used": False,
    "external_api_used": False,
}


@dataclass(frozen=True)
class ParserConsumerReadinessRow:
    record_id: str
    consumer_name: str
    source_day: str
    handoff_status: str
    readiness_status: str
    blocking_reasons: Tuple[str, ...]
    clarification_items: Tuple[str, ...]
    required_consumer_actions: Tuple[str, ...]
    unsafe_flag: bool
    live_flag: bool
    ssh_flag: bool
    write_flag: bool
    command_execution_flag: bool
    mapped_task_execution_flag: bool
    evidence_refs: Tuple[str, ...]


def _tuple_of_strings(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),) if str(value).strip() else ()


def _record_bool(record: Dict[str, Any], direct_field: str, safety_fields: Tuple[str, ...]) -> bool:
    if direct_field in record:
        return record.get(direct_field) is True
    safety_flags = record.get("safety_flags", {})
    if isinstance(safety_flags, dict):
        return any(safety_flags.get(field) is True for field in safety_fields)
    return False


def _consumer_name(record: Dict[str, Any]) -> str:
    if "consumer_name" in record:
        return str(record.get("consumer_name") or "")
    if "consumer_identity" in record:
        return str(record.get("consumer_identity") or "")
    return "parser_contract_consumer"


def _required_actions(record: Dict[str, Any]) -> Tuple[str, ...]:
    if "required_consumer_actions" in record:
        return _tuple_of_strings(record.get("required_consumer_actions"))
    return _tuple_of_strings(record.get("next_stage_recommendation"))


def _evidence_refs(record: Dict[str, Any]) -> Tuple[str, ...]:
    if "evidence_refs" in record:
        return _tuple_of_strings(record.get("evidence_refs"))
    if "evidence_reference" in record:
        return _tuple_of_strings(record.get("evidence_reference"))

    refs = [DAY108_REPORT_JSON.as_posix()]
    if record.get("handoff_id"):
        refs.append(f"handoff:{record['handoff_id']}")
    if record.get("evidence_status"):
        refs.append(f"evidence_status:{record['evidence_status']}")
    return tuple(refs)


def _handoff_status(record: Dict[str, Any]) -> str:
    return str(
        record.get("handoff_status")
        or record.get("reviewer_decision")
        or record.get("evidence_status")
        or "UNKNOWN"
    )


def _record_marked_blocked_or_unsafe(record: Dict[str, Any], handoff_status: str) -> bool:
    markers = (
        handoff_status,
        str(record.get("reviewer_decision", "")),
        str(record.get("evidence_status", "")),
        str(record.get("handoff_ready", "")),
    )
    marker_text = " ".join(markers).upper()
    return (
        BLOCKED_UNSAFE_OR_UNSUPPORTED in marker_text
        or "BLOCKED" in marker_text
        or "REJECTED" in marker_text
        or "UNSAFE" in marker_text
        or record.get("deliverable") is False
    )


def build_readiness_row_from_handoff_record(record: Dict[str, Any]) -> ParserConsumerReadinessRow:
    source = deepcopy(record)
    record_id = str(source.get("record_id") or source.get("handoff_id") or source.get("intent_id") or "")
    consumer_name = _consumer_name(source)
    handoff_status = _handoff_status(source)
    required_actions = _required_actions(source)
    evidence_refs = _evidence_refs(source)
    flags = {
        "unsafe_flag": _record_bool(source, "unsafe_flag", ("unsafe_requested", "unsafe_flag")),
        "live_flag": _record_bool(source, "live_flag", ("live_execution_requested", "live_flag")),
        "ssh_flag": _record_bool(source, "ssh_flag", ("ssh_requested", "ssh_flag")),
        "write_flag": _record_bool(
            source,
            "write_flag",
            ("write_or_config_change_requested", "write_requested", "write_flag"),
        ),
        "command_execution_flag": _record_bool(
            source,
            "command_execution_flag",
            ("command_execution_requested", "command_execution_flag"),
        ),
        "mapped_task_execution_flag": _record_bool(
            source,
            "mapped_task_execution_flag",
            ("mapped_task_execution_requested", "mapped_task_execution_flag"),
        ),
    }

    blocking_reasons: List[str] = []
    if flags["unsafe_flag"]:
        blocking_reasons.append("UNSAFE_FLAG_SET")
    if flags["live_flag"]:
        blocking_reasons.append("LIVE_FLAG_SET")
    if flags["ssh_flag"]:
        blocking_reasons.append("SSH_FLAG_SET")
    if flags["write_flag"]:
        blocking_reasons.append("WRITE_FLAG_SET")
    if flags["command_execution_flag"]:
        blocking_reasons.append("COMMAND_EXECUTION_FLAG_SET")
    if flags["mapped_task_execution_flag"]:
        blocking_reasons.append("MAPPED_TASK_EXECUTION_FLAG_SET")
    if not record_id:
        blocking_reasons.append("MISSING_RECORD_ID")
    if not consumer_name:
        blocking_reasons.append("MISSING_CONSUMER_IDENTITY")
    if not evidence_refs:
        blocking_reasons.append("MISSING_HANDOFF_EVIDENCE")
    if _record_marked_blocked_or_unsafe(source, handoff_status):
        blocking_reasons.append("RECORD_MARKED_BLOCKED_OR_UNSAFE")

    clarification_items: List[str] = []
    if not blocking_reasons:
        if not required_actions:
            clarification_items.append("MISSING_REQUIRED_CONSUMER_ACTIONS")
        if handoff_status == NEEDS_REVIEWER_CLARIFICATION or source.get("reviewer_decision") == NEEDS_REVIEWER_CLARIFICATION:
            clarification_items.append("HANDOFF_STATUS_NEEDS_REVIEWER_CLARIFICATION")
        if source.get("handoff_ready") is False:
            clarification_items.append("HANDOFF_NOT_READY_FOR_CONSUMER")

    if blocking_reasons:
        readiness_status = BLOCKED
        clarification_items = []
    elif clarification_items:
        readiness_status = NEEDS_CLARIFICATION
    else:
        readiness_status = READY

    return ParserConsumerReadinessRow(
        record_id=record_id,
        consumer_name=consumer_name,
        source_day=SOURCE_DAY,
        handoff_status=handoff_status,
        readiness_status=readiness_status,
        blocking_reasons=tuple(sorted(set(blocking_reasons))),
        clarification_items=tuple(sorted(set(clarification_items))),
        required_consumer_actions=required_actions,
        unsafe_flag=flags["unsafe_flag"],
        live_flag=flags["live_flag"],
        ssh_flag=flags["ssh_flag"],
        write_flag=flags["write_flag"],
        command_execution_flag=flags["command_execution_flag"],
        mapped_task_execution_flag=flags["mapped_task_execution_flag"],
        evidence_refs=evidence_refs,
    )


def build_readiness_rows_from_handoff_records(
    handoff_records: Iterable[Dict[str, Any]],
) -> List[ParserConsumerReadinessRow]:
    return [build_readiness_row_from_handoff_record(record) for record in deepcopy(list(handoff_records))]


def _row_to_report_dict(row: ParserConsumerReadinessRow) -> Dict[str, Any]:
    data = asdict(row)
    for field in (
        "blocking_reasons",
        "clarification_items",
        "required_consumer_actions",
        "evidence_refs",
    ):
        data[field] = list(data[field])
    return data


def build_default_day108_handoff_records() -> List[Dict[str, Any]]:
    return build_parser_contract_consumer_handoff_report()["handoff_records"]


def _safety_summary(rows: Iterable[ParserConsumerReadinessRow]) -> Dict[str, Any]:
    row_list = list(rows)
    summary = {
        f"{field}_count": sum(1 for row in row_list if getattr(row, field) is True)
        for field in SAFETY_FLAG_FIELDS
    }
    summary["blocking_condition_preserved"] = all(
        row.readiness_status == BLOCKED and row.blocking_reasons
        for row in row_list
        if any(getattr(row, field) is True for field in SAFETY_FLAG_FIELDS)
    )
    return summary


def _reviewer_status(rows: List[ParserConsumerReadinessRow], safety_summary: Dict[str, Any]) -> str:
    if any(safety_summary[f"{field}_count"] > 0 for field in SAFETY_FLAG_FIELDS):
        return "BLOCKED_RECORDS_PRESENT"
    if any(row.readiness_status == BLOCKED for row in rows):
        return "BLOCKED_RECORDS_PRESENT"
    if any(row.readiness_status == NEEDS_CLARIFICATION for row in rows):
        return "NEEDS_REVIEW"
    return "READY_FOR_REVIEW"


def validate_readiness_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 109:
        errors.append("day must be 109.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("overall_status") != "PASS":
        errors.append("overall_status must remain PASS for deterministic matrix generation.")
    if report.get("safety_summary", {}).get("blocking_condition_preserved") is not True:
        errors.append("blocking_condition_preserved must be true.")

    for index, row in enumerate(report.get("readiness_matrix", []), start=1):
        status = row.get("readiness_status")
        if status not in READINESS_STATUSES:
            errors.append(f"readiness_matrix[{index}] has invalid readiness_status.")
        if status == BLOCKED and not row.get("blocking_reasons"):
            errors.append(f"readiness_matrix[{index}] BLOCKED row lacks blocking_reasons.")
        if status == NEEDS_CLARIFICATION and not row.get("clarification_items"):
            errors.append(f"readiness_matrix[{index}] NEEDS_CLARIFICATION row lacks clarification_items.")
        if status == READY and (row.get("blocking_reasons") or row.get("clarification_items")):
            errors.append(f"readiness_matrix[{index}] READY row has blockers or clarification items.")
        if any(row.get(field) is True for field in SAFETY_FLAG_FIELDS) and status != BLOCKED:
            errors.append(f"readiness_matrix[{index}] safety flag row is not BLOCKED.")
    return errors


def build_parser_consumer_handoff_readiness_matrix_report(
    handoff_records: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    rows = build_readiness_rows_from_handoff_records(
        handoff_records if handoff_records is not None else build_default_day108_handoff_records()
    )
    matrix = [_row_to_report_dict(row) for row in rows]
    safety_summary = _safety_summary(rows)
    report = {
        "day": 109,
        "day_id": "Day109",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "schema_version": SCHEMA_VERSION,
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "overall_status": "PASS",
        "reviewer_status": _reviewer_status(rows, safety_summary),
        "total_records": len(rows),
        "ready_count": sum(1 for row in rows if row.readiness_status == READY),
        "needs_clarification_count": sum(1 for row in rows if row.readiness_status == NEEDS_CLARIFICATION),
        "blocked_count": sum(1 for row in rows if row.readiness_status == BLOCKED),
        "safety_summary": safety_summary,
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "readiness_matrix": matrix,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    report["validation_errors"] = validate_readiness_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
    return report


def write_parser_consumer_handoff_readiness_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_consumer_handoff_readiness_matrix_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_handoff_readiness_matrix_html(safe_report, html_path)
    return json_path, html_path


def write_parser_consumer_handoff_readiness_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(key)}</code></td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for key, value in {
            "overall_status": report["overall_status"],
            "reviewer_status": report["reviewer_status"],
            "total_records": report["total_records"],
            "ready_count": report["ready_count"],
            "needs_clarification_count": report["needs_clarification_count"],
            "blocked_count": report["blocked_count"],
            **report["safety_summary"],
        }.items()
    )
    matrix_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(row['record_id'])}</code></td>"
        f"<td>{html.escape(row['consumer_name'])}</td>"
        f"<td>{html.escape(row['handoff_status'])}</td>"
        f"<td><strong>{html.escape(row['readiness_status'])}</strong></td>"
        f"<td>{html.escape(', '.join(row['blocking_reasons']) or 'none')}</td>"
        f"<td>{html.escape(', '.join(row['clarification_items']) or 'none')}</td>"
        f"<td>{html.escape(', '.join(row['required_consumer_actions']) or 'none')}</td>"
        f"<td>{html.escape(json.dumps({field: row[field] for field in SAFETY_FLAG_FIELDS}, sort_keys=True))}</td>"
        f"<td>{html.escape(', '.join(row['evidence_refs']) or 'none')}</td>"
        "</tr>"
        for row in report["readiness_matrix"]
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
    <span class="badge">REVIEW_ONLY</span>
    <span class="badge">NO_LIVE_EXECUTION</span>
    <span class="badge">NO_SSH</span>
    <span class="badge">NO_WRITE</span>
  </p>
  <p><strong>Source:</strong> {html.escape(report['source_day'])} / <code>{html.escape(report['source_task'])}</code></p>
  <p><strong>Status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <h2>Summary</h2>
  <table>
    <thead><tr><th>Field</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>
  <h2>Readiness Status Counts</h2>
  <table>
    <thead><tr><th>READY</th><th>NEEDS_CLARIFICATION</th><th>BLOCKED</th></tr></thead>
    <tbody><tr><td>{report['ready_count']}</td><td>{report['needs_clarification_count']}</td><td>{report['blocked_count']}</td></tr></tbody>
  </table>
  <h2>Per-record Readiness Matrix</h2>
  <table>
    <thead><tr><th>Record</th><th>Consumer</th><th>Handoff Status</th><th>Readiness</th><th>Blocking Reason</th><th>Clarification Items</th><th>Required Consumer Actions</th><th>Safety Flags</th><th>Evidence Refs</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> int:
    report = build_parser_consumer_handoff_readiness_matrix_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
