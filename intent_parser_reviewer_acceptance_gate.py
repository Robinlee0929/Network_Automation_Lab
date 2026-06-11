"""Day104 parser reviewer acceptance gate.

Day104 converts the Day103 matrix trace states into a reviewer-facing
acceptance decision. It is a gate report only; it does not add parser coverage
or enable any broker, adapter, SSH, live-device, or execution path.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_evidence_matrix import build_parser_evidence_matrix_report


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-reviewer-acceptance-gate"
TITLE = "Parser Reviewer Acceptance Gate / Matrix Decision Review"
PHASE = "PARSER_REVIEWER_ACCEPTANCE_GATE"
SCHEMA_VERSION = "day104.parser_reviewer_acceptance_gate.v1"
MODE = "REVIEW_GATE_ONLY"
DECISION_MODE = "ACCEPTANCE_DECISION_ONLY"
REVIEWER_STATUS = "REVIEW_GATE_READY"
REPORT_JSON = Path("reports") / "lab-summary" / "day104_parser_reviewer_acceptance_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day104_parser_reviewer_acceptance_gate.html"

TRACE_COMPLETE = "TRACE_COMPLETE"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
KNOWN_GAP = "KNOWN_GAP"
BLOCKED_BY_SAFETY_BOUNDARY = "BLOCKED_BY_SAFETY_BOUNDARY"
TRACE_STATUSES = {
    TRACE_COMPLETE,
    REVIEW_REQUIRED,
    KNOWN_GAP,
    BLOCKED_BY_SAFETY_BOUNDARY,
}

ACCEPTABLE_FOR_NEXT_STAGE = "ACCEPTABLE_FOR_NEXT_STAGE"
ACCEPTABLE_WITH_REVIEW_NOTES = "ACCEPTABLE_WITH_REVIEW_NOTES"
NOT_ACCEPTABLE_KNOWN_GAPS = "NOT_ACCEPTABLE_KNOWN_GAPS"
NOT_ACCEPTABLE_SAFETY_BLOCKED = "NOT_ACCEPTABLE_SAFETY_BLOCKED"

SAFETY_FLAGS = {
    "parser_capability_added": False,
    "execution_unlocked": False,
    "broker_handoff_enabled": False,
    "adapter_connected": False,
    "ssh_allowed": False,
    "live_device_access_allowed": False,
    "live_command_allowed": False,
    "config_change_allowed": False,
    "execution_allowed": False,
    "adapter_invocation_allowed": False,
    "broker_handoff_allowed": False,
    "live_access_allowed": False,
    "routeros_execution_allowed": False,
    "command_execution_allowed": False,
    "dashboard_action_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
}


def build_parser_reviewer_acceptance_gate_report(
    day103_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the Day104 reviewer acceptance gate report."""
    source_report = deepcopy(day103_report) if day103_report is not None else build_parser_evidence_matrix_report()
    matrix_rows = normalize_matrix_rows(source_report.get("matrix_rows", []))
    decision = decide_parser_acceptance(matrix_rows)
    summary = build_summary(matrix_rows, decision)
    report = {
        "day": 104,
        "day_id": "Day104",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": "PASS",
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "schema_version": SCHEMA_VERSION,
        "mode": MODE,
        "decision_mode": DECISION_MODE,
        "source_kind": "day103_matrix_decision_review",
        "source_day": source_report.get("day_id", "Day103"),
        "source_task": source_report.get("task"),
        "source_reports": source_report.get("reports", {}),
        "scope": {
            "review_gate_only": True,
            "acceptance_decision_only": True,
            "consumes_day103_matrix": True,
            "does_not_add_parser_capability": True,
            "does_not_expand_parser_coverage": True,
            "does_not_unlock_execution": True,
            "does_not_connect_broker_or_adapter": True,
            "does_not_use_ssh_or_live_devices": True,
        },
        **SAFETY_FLAGS,
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "acceptance_decision": decision["acceptance_decision"],
        "acceptance_reason": decision["acceptance_reason"],
        "matrix_state_counts": decision["matrix_state_counts"],
        "required_matrix_state_counts": decision["required_matrix_state_counts"],
        "blocking_findings": decision["blocking_findings"],
        "review_notes": decision["review_notes"],
        "next_stage_allowed": decision["next_stage_allowed"],
        "next_stage_conditions": decision["next_stage_conditions"],
        "summary": summary,
        "matrix_rows": matrix_rows,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_parser_reviewer_acceptance_gate_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def normalize_matrix_rows(rows: Any) -> List[Dict[str, Any]]:
    if not isinstance(rows, list):
        return []

    normalized = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            normalized.append(
                {
                    "row_id": f"D104-MALFORMED-{index:02d}",
                    "day": "UNKNOWN",
                    "trace_status": "MALFORMED",
                    "required": True,
                    "reviewer_note": "Matrix row is not an object.",
                }
            )
            continue

        copied = deepcopy(row)
        copied.setdefault("row_id", f"D104-R{index:02d}")
        copied.setdefault("day", "UNKNOWN")
        copied.setdefault("required", True)
        copied.setdefault("reviewer_note", "")
        if "trace_status" not in copied:
            copied["trace_status"] = "MALFORMED"
        normalized.append(copied)
    return normalized


def decide_parser_acceptance(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    matrix_rows = list(rows)
    required_rows = [row for row in matrix_rows if row.get("required", True) is not False]
    matrix_state_counts = count_trace_states(matrix_rows)
    required_counts = count_trace_states(required_rows)

    if not required_rows:
        return _decision(
            REVIEW_REQUIRED,
            "No required Day103 matrix rows were available for Day104 acceptance.",
            matrix_state_counts,
            required_counts,
            blocking_findings=[],
            review_notes=["Empty or non-list matrix requires reviewer inspection."],
            next_stage_allowed=False,
            next_stage_conditions=["Provide a valid Day103 matrix before acceptance can be decided."],
        )

    malformed_rows = [row for row in required_rows if row.get("trace_status") not in TRACE_STATUSES]
    if malformed_rows:
        return _decision(
            REVIEW_REQUIRED,
            "One or more required matrix rows are missing a valid Day103 trace status.",
            matrix_state_counts,
            required_counts,
            blocking_findings=build_findings(malformed_rows, "Malformed or missing trace status."),
            review_notes=["Reviewer must repair or regenerate the Day103 matrix before final acceptance."],
            next_stage_allowed=False,
            next_stage_conditions=["Regenerate Day103 matrix with valid trace statuses."],
        )

    safety_blocked = _rows_with_status(required_rows, BLOCKED_BY_SAFETY_BOUNDARY)
    if safety_blocked:
        return _decision(
            NOT_ACCEPTABLE_SAFETY_BLOCKED,
            "Safety boundary blocks dominate Day104 acceptance; next stage remains blocked.",
            matrix_state_counts,
            required_counts,
            blocking_findings=build_findings(safety_blocked, "Safety boundary block prevents next-stage acceptance."),
            review_notes=build_review_notes(required_rows),
            next_stage_allowed=False,
            next_stage_conditions=[
                "Resolve or explicitly sign off safety boundary blocks before any later readiness package.",
                "Broker handoff, adapter binding, SSH, live access, and execution remain disabled.",
            ],
        )

    known_gaps = _rows_with_status(required_rows, KNOWN_GAP)
    if known_gaps:
        return _decision(
            NOT_ACCEPTABLE_KNOWN_GAPS,
            "Known parser evidence gaps prevent next-stage acceptance.",
            matrix_state_counts,
            required_counts,
            blocking_findings=build_findings(known_gaps, "Known parser evidence gap requires closure."),
            review_notes=build_review_notes(required_rows),
            next_stage_allowed=False,
            next_stage_conditions=["Close or explicitly disposition known gaps before next-stage readiness."],
        )

    review_required = _rows_with_status(required_rows, REVIEW_REQUIRED)
    if review_required:
        return _decision(
            ACCEPTABLE_WITH_REVIEW_NOTES,
            "Evidence is traceable enough for reviewer discussion, but REVIEW_REQUIRED rows prevent full acceptance.",
            matrix_state_counts,
            required_counts,
            blocking_findings=[],
            review_notes=build_review_notes(review_required),
            next_stage_allowed=False,
            next_stage_conditions=["Manual reviewer sign-off is required before full next-stage acceptance."],
        )

    if all(row.get("trace_status") == TRACE_COMPLETE for row in required_rows):
        return _decision(
            ACCEPTABLE_FOR_NEXT_STAGE,
            "All required parser evidence rows are TRACE_COMPLETE with no review-required, known-gap, or safety-blocked rows.",
            matrix_state_counts,
            required_counts,
            blocking_findings=[],
            review_notes=[],
            next_stage_allowed=True,
            next_stage_conditions=["Proceed to the next reviewer package while preserving all execution safety flags."],
        )

    return _decision(
        REVIEW_REQUIRED,
        "Evidence is insufficient to make a final Day104 acceptance decision.",
        matrix_state_counts,
        required_counts,
        blocking_findings=[],
        review_notes=["Reviewer inspection is required."],
        next_stage_allowed=False,
        next_stage_conditions=["Review Day103 matrix state before moving forward."],
    )


def count_trace_states(rows: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts = {status: 0 for status in sorted(TRACE_STATUSES)}
    counts["MALFORMED"] = 0
    for row in rows:
        status = row.get("trace_status")
        if status in counts:
            counts[status] += 1
        else:
            counts["MALFORMED"] += 1
    return counts


def build_findings(rows: Iterable[Dict[str, Any]], reason: str) -> List[Dict[str, str]]:
    findings = []
    for row in rows:
        findings.append(
            {
                "row_id": str(row.get("row_id", "")),
                "day": str(row.get("day", "")),
                "trace_status": str(row.get("trace_status", "")),
                "reason": reason,
                "reviewer_note": str(row.get("reviewer_note", "")),
            }
        )
    return findings


def build_review_notes(rows: Iterable[Dict[str, Any]]) -> List[str]:
    notes = []
    for row in rows:
        if row.get("trace_status") == REVIEW_REQUIRED and row.get("reviewer_note"):
            notes.append(f"{row.get('day', 'UNKNOWN')}: {row['reviewer_note']}")
    return notes


def build_summary(rows: List[Dict[str, Any]], decision: Dict[str, Any]) -> Dict[str, Any]:
    required_rows = [row for row in rows if row.get("required", True) is not False]
    return {
        "total_rows": len(rows),
        "required_rows": len(required_rows),
        "optional_rows": len(rows) - len(required_rows),
        "acceptance_decision": decision["acceptance_decision"],
        "next_stage_allowed": decision["next_stage_allowed"],
        "blocking_finding_count": len(decision["blocking_findings"]),
        "review_note_count": len(decision["review_notes"]),
        "trace_complete_count": decision["required_matrix_state_counts"].get(TRACE_COMPLETE, 0),
        "review_required_count": decision["required_matrix_state_counts"].get(REVIEW_REQUIRED, 0),
        "known_gap_count": decision["required_matrix_state_counts"].get(KNOWN_GAP, 0),
        "blocked_by_safety_boundary_count": decision["required_matrix_state_counts"].get(
            BLOCKED_BY_SAFETY_BOUNDARY, 0
        ),
        "malformed_count": decision["required_matrix_state_counts"].get("MALFORMED", 0),
    }


def validate_parser_reviewer_acceptance_gate_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 104:
        errors.append("day must be 104.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("mode") != MODE:
        errors.append(f"mode must be {MODE}.")
    if report.get("decision_mode") != DECISION_MODE:
        errors.append(f"decision_mode must be {DECISION_MODE}.")
    if report.get("acceptance_decision") not in {
        ACCEPTABLE_FOR_NEXT_STAGE,
        ACCEPTABLE_WITH_REVIEW_NOTES,
        NOT_ACCEPTABLE_KNOWN_GAPS,
        NOT_ACCEPTABLE_SAFETY_BLOCKED,
        REVIEW_REQUIRED,
    }:
        errors.append("acceptance_decision is invalid.")
    for flag, expected_value in SAFETY_FLAGS.items():
        if report.get(flag) is not expected_value:
            errors.append(f"{flag} must be false.")
        if report.get("safety_flags", {}).get(flag) is not expected_value:
            errors.append(f"safety_flags.{flag} must be false.")
    if report.get("acceptance_decision") == ACCEPTABLE_FOR_NEXT_STAGE and report.get("next_stage_allowed") is not True:
        errors.append("ACCEPTABLE_FOR_NEXT_STAGE must allow the next stage.")
    if report.get("acceptance_decision") != ACCEPTABLE_FOR_NEXT_STAGE and report.get("next_stage_allowed") is not False:
        errors.append("Only ACCEPTABLE_FOR_NEXT_STAGE may set next_stage_allowed true.")
    if report.get("acceptance_decision") == NOT_ACCEPTABLE_SAFETY_BLOCKED:
        if report.get("required_matrix_state_counts", {}).get(BLOCKED_BY_SAFETY_BOUNDARY, 0) < 1:
            errors.append("Safety blocked decision requires at least one safety-blocked row.")
    if report.get("acceptance_decision") == NOT_ACCEPTABLE_KNOWN_GAPS:
        if report.get("required_matrix_state_counts", {}).get(KNOWN_GAP, 0) < 1:
            errors.append("Known gaps decision requires at least one known-gap row.")
    if report.get("summary", {}).get("total_rows") != len(report.get("matrix_rows", [])):
        errors.append("summary.total_rows must match matrix row count.")
    return errors


def write_parser_reviewer_acceptance_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_reviewer_acceptance_gate_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_reviewer_acceptance_gate_html(safe_report, html_path)
    return json_path, html_path


def write_parser_reviewer_acceptance_gate_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    blocking_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['row_id'])}</code></td>"
        f"<td>{html.escape(item['day'])}</td>"
        f"<td>{html.escape(item['trace_status'])}</td>"
        f"<td>{html.escape(item['reason'])}</td>"
        f"<td>{html.escape(item['reviewer_note'])}</td>"
        "</tr>"
        for item in report["blocking_findings"]
    )
    if not blocking_rows:
        blocking_rows = "<tr><td colspan=\"5\">No blocking findings.</td></tr>"

    matrix_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(str(row.get('row_id', '')))}</code></td>"
        f"<td>{html.escape(str(row.get('day', '')))}</td>"
        f"<td>{html.escape(str(row.get('trace_status', '')))}</td>"
        f"<td>{html.escape(str(row.get('required', True)))}</td>"
        f"<td>{html.escape(str(row.get('reviewer_note', '')))}</td>"
        "</tr>"
        for row in report["matrix_rows"]
    )
    flag_rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for name, value in report["safety_flags"].items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .decision {{ font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review</h1>
  <p><strong>Status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Mode:</strong> <code>{html.escape(report['mode'])}</code> / <code>{html.escape(report['decision_mode'])}</code></p>
  <p><strong>Acceptance decision:</strong> <span class="decision">{html.escape(report['acceptance_decision'])}</span></p>
  <p><strong>Reason:</strong> {html.escape(report['acceptance_reason'])}</p>
  <p><strong>Next stage allowed:</strong> {html.escape(json.dumps(report['next_stage_allowed']))}</p>
  <p><strong>Counts:</strong> trace_complete={summary['trace_complete_count']}, review_required={summary['review_required_count']}, known_gap={summary['known_gap_count']}, safety_blocked={summary['blocked_by_safety_boundary_count']}, malformed={summary['malformed_count']}</p>
  <p><strong>Day104 reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <p><strong>Scope:</strong> Day104 is a reviewer acceptance gate only. It does not add parser capability, parser fallback, broker handoff, adapter binding, SSH/read-only executor, live device preparation, command execution, or configuration change capability.</p>
  <h2>Blocking Findings</h2>
  <table>
    <thead><tr><th>Row</th><th>Day</th><th>Trace Status</th><th>Reason</th><th>Reviewer Note</th></tr></thead>
    <tbody>{blocking_rows}</tbody>
  </table>
  <h2>Matrix Rows</h2>
  <table>
    <thead><tr><th>Row</th><th>Day</th><th>Trace Status</th><th>Required</th><th>Reviewer Note</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <h2>Safety Flags</h2>
  <table>
    <thead><tr><th>Flag</th><th>Value</th></tr></thead>
    <tbody>{flag_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def _rows_with_status(rows: Iterable[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    return [row for row in rows if row.get("trace_status") == status]


def _decision(
    acceptance_decision: str,
    acceptance_reason: str,
    matrix_state_counts: Dict[str, int],
    required_matrix_state_counts: Dict[str, int],
    blocking_findings: List[Dict[str, str]],
    review_notes: List[str],
    next_stage_allowed: bool,
    next_stage_conditions: List[str],
) -> Dict[str, Any]:
    return {
        "acceptance_decision": acceptance_decision,
        "acceptance_reason": acceptance_reason,
        "matrix_state_counts": matrix_state_counts,
        "required_matrix_state_counts": required_matrix_state_counts,
        "blocking_findings": blocking_findings,
        "review_notes": review_notes,
        "next_stage_allowed": next_stage_allowed,
        "next_stage_conditions": next_stage_conditions,
    }
