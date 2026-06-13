"""Day119 reviewer evidence intake outcome ledger.

This module records static, reviewer-facing intake outcomes for the Day118
evidence checklist. It is evidence-only and review-only: it does not accept,
sign off, release safety boundaries, invoke adapters or brokers, use SSH, or
change parser/runtime capabilities.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_deferred_action_review_sequence_runbook import (
    REPORT_JSON as DAY118_REPORT_JSON,
    TASK_NAME as DAY118_TASK_NAME,
    build_deferred_action_review_sequence_runbook_report,
)


CREATED_AT = "2026-06-13T00:00:00+08:00"
DAY = 119
DAY_ID = "Day119"
TASK_NAME = "reviewer-evidence-intake-outcome-ledger"
TASK_ALIAS = "deferred-evidence-collection-log"
TITLE = "Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log"
FULL_TITLE = f"Day119 {TITLE}"
PHASE_NAME = TITLE
SCHEMA_VERSION = "day119.reviewer_evidence_intake_outcome_ledger.v1"
SOURCE_DAY = 118
EXPECTED_SOURCE_RECORD_COUNT = 7
OVERALL_STATUS = "INTAKE_LEDGER_READY"
STATUS_SOURCE_COUNT_MISMATCH = "DAY118_SOURCE_RECORD_COUNT_MISMATCH_REVIEW_REQUIRED"
STATUS_SOURCE_ALIGNMENT_MISMATCH = "DAY118_SOURCE_ALIGNMENT_MISMATCH_REVIEW_REQUIRED"
STATUS_SAFETY_VIOLATION = "SAFETY_INVARIANT_VIOLATION_REVIEW_REQUIRED"
FINAL_RECOMMENDATION = "REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION"
AUDIT_TYPE = "REVIEWER_EVIDENCE_INTAKE_LOG_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day119_reviewer_evidence_intake_outcome_ledger.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day119_reviewer_evidence_intake_outcome_ledger.html"

ALLOWED_INTAKE_STATUSES = {
    "RECEIVED",
    "PARTIAL",
    "MISSING",
    "DEFERRED",
    "REJECTED",
    "NEEDS_CLARIFICATION",
}

ALLOWED_GAP_STATUSES = {
    "NO_GAP",
    "OPEN_GAP",
    "DEFERRED_GAP",
    "SAFETY_BLOCKED_GAP",
    "CLARIFICATION_REQUIRED",
}

SUMMARY_FALSE_FLAGS = (
    "acceptance_decision_made",
    "reviewer_signoff_made",
    "safety_boundary_released",
    "allowed_to_execute",
    "ssh_allowed",
    "live_command_allowed",
    "adapter_invocation_allowed",
    "broker_handoff_allowed",
    "parser_capability_changed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "live_device_access_allowed",
    "config_mutation_allowed",
)

ROW_FALSE_FLAGS = (
    "acceptance_decision_made",
    "reviewer_signoff_made",
    "safety_boundary_released",
    "allowed_to_execute",
    "ssh_allowed",
    "live_command_allowed",
    "adapter_invocation_allowed",
    "broker_handoff_allowed",
    "parser_capability_changed",
)

OUTCOME_BY_SEQUENCE = {
    1: {
        "intake_status": "RECEIVED",
        "gap_status": "NO_GAP",
        "deferred_reason": "No remaining evidence gap for intake logging; acceptance is still out of scope.",
        "follow_up_action": "Preserve the received static evidence with the Day118 requirement link.",
        "reviewer_note": "Evidence was logged for reviewer visibility only.",
        "safety_boundary_impact": "No safety boundary impact; no execution capability is changed.",
        "blocked_by_safety_boundary": False,
    },
    2: {
        "intake_status": "PARTIAL",
        "gap_status": "OPEN_GAP",
        "deferred_reason": "Evidence addresses the owner and follow-up type but lacks a complete reviewer note.",
        "follow_up_action": "Request a complete static reviewer note tied to the Day118 checklist row.",
        "reviewer_note": "Partial evidence remains useful for traceability but cannot close the gap.",
        "safety_boundary_impact": "No safety boundary impact; open evidence gaps do not unlock execution.",
        "blocked_by_safety_boundary": False,
    },
    3: {
        "intake_status": "MISSING",
        "gap_status": "OPEN_GAP",
        "deferred_reason": "No reviewer-visible evidence was provided for the Day118 expectation.",
        "follow_up_action": "Collect a deterministic report excerpt or documentation reference.",
        "reviewer_note": "Missing evidence remains deferred until separately supplied and reviewed.",
        "safety_boundary_impact": "No safety boundary impact; missing evidence keeps the item blocked from advancement.",
        "blocked_by_safety_boundary": False,
    },
    4: {
        "intake_status": "DEFERRED",
        "gap_status": "DEFERRED_GAP",
        "deferred_reason": "Evidence collection depends on a future reviewer pass outside Day119.",
        "follow_up_action": "Carry the item forward in the deferred evidence collection queue.",
        "reviewer_note": "Day119 records the deferral only and does not close the follow-up.",
        "safety_boundary_impact": "No boundary release; the item remains review-only and non-advancing.",
        "blocked_by_safety_boundary": False,
    },
    5: {
        "intake_status": "NEEDS_CLARIFICATION",
        "gap_status": "CLARIFICATION_REQUIRED",
        "deferred_reason": "Evidence is ambiguous or not clearly tied to the Day118 expected item.",
        "follow_up_action": "Ask the owner to clarify the evidence reference and expected closure condition.",
        "reviewer_note": "Clarification is required before this can be treated as received evidence.",
        "safety_boundary_impact": "Clarification does not alter any locked execution or safety flag.",
        "blocked_by_safety_boundary": False,
    },
    6: {
        "intake_status": "REJECTED",
        "gap_status": "SAFETY_BLOCKED_GAP",
        "deferred_reason": "Submitted evidence implies readiness or execution unlock, which Day119 cannot accept.",
        "follow_up_action": "Reject the unsafe framing and request report-only evidence language.",
        "reviewer_note": "Rejected intake protects the safety boundary and preserves no-execution proof.",
        "safety_boundary_impact": "Safety boundary remains locked; unsafe evidence cannot be used for acceptance.",
        "blocked_by_safety_boundary": True,
    },
    7: {
        "intake_status": "DEFERRED",
        "gap_status": "SAFETY_BLOCKED_GAP",
        "deferred_reason": "Evidence depends on a future approved safety review and cannot be collected by Day119.",
        "follow_up_action": "Keep the evidence item deferred until a separate safety gate review is approved.",
        "reviewer_note": "Deferred collection is recorded without sign-off or boundary release.",
        "safety_boundary_impact": "Safety boundary remains locked; no live, SSH, adapter, or broker path is opened.",
        "blocked_by_safety_boundary": True,
    },
}


def _false_summary_flags() -> Dict[str, bool]:
    return {flag: False for flag in SUMMARY_FALSE_FLAGS}


def _false_row_flags() -> Dict[str, bool]:
    return {flag: False for flag in ROW_FALSE_FLAGS}


def _list_to_sentence(values: Iterable[Any]) -> str:
    return "; ".join(str(value) for value in values)


def build_evidence_intake_outcome_ledger(day118_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    checklist = deepcopy(day118_report.get("evidence_intake_checklist", []))
    ledger: List[Dict[str, Any]] = []
    for index, source_item in enumerate(checklist, start=1):
        review_sequence = source_item.get("review_sequence", index)
        outcome = OUTCOME_BY_SEQUENCE.get(review_sequence, OUTCOME_BY_SEQUENCE[index])
        evidence_id = f"D119-EVIDENCE-{index:03d}"
        requirement_id = f"DAY118-CHECKLIST-{index:03d}"
        ledger.append(
            {
                "evidence_id": evidence_id,
                "day118_requirement_id": requirement_id,
                "evidence_name": f"Day118 evidence intake item for {source_item.get('deferred_action_id', evidence_id)}",
                "expected_from": source_item.get("owner", "Day118 reviewer evidence owner"),
                "intake_status": outcome["intake_status"],
                "gap_status": outcome["gap_status"],
                "deferred_reason": outcome["deferred_reason"],
                "follow_up_action": outcome["follow_up_action"],
                "reviewer_note": outcome["reviewer_note"],
                "safety_boundary_impact": outcome["safety_boundary_impact"],
                "acceptance_impact": "No acceptance decision is made; Day119 remains evidence intake logging only.",
                "blocked_by_safety_boundary": outcome["blocked_by_safety_boundary"],
                "source_day": SOURCE_DAY,
                "source_task": DAY118_TASK_NAME,
                "source_artifact": DAY118_REPORT_JSON.as_posix(),
                "source_review_sequence": review_sequence,
                "source_deferred_action_id": source_item.get("deferred_action_id", ""),
                "source_completion_state": source_item.get("completion_state", ""),
                "day118_required_evidence": deepcopy(source_item.get("required_evidence", [])),
                "day118_reject_or_defer_if": deepcopy(source_item.get("reject_or_defer_if", [])),
                **_false_row_flags(),
            }
        )
    return ledger


def validate_reviewer_evidence_intake_outcome_ledger_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "source_day": SOURCE_DAY,
        "overall_status": OVERALL_STATUS,
        "status": OVERALL_STATUS,
        "source_record_count": EXPECTED_SOURCE_RECORD_COUNT,
        "ledger_record_count": EXPECTED_SOURCE_RECORD_COUNT,
        "final_recommendation": FINAL_RECOMMENDATION,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    for flag in SUMMARY_FALSE_FLAGS:
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")
        if report.get("safety_invariants", {}).get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")

    source_records = report.get("source_day118_checklist", [])
    ledger = report.get("evidence_intake_outcome_ledger", [])
    if len(source_records) != EXPECTED_SOURCE_RECORD_COUNT:
        errors.append("source_day118_checklist must contain exactly 7 records.")
    if len(ledger) != EXPECTED_SOURCE_RECORD_COUNT:
        errors.append("evidence_intake_outcome_ledger must contain exactly 7 records.")
    if report.get("source_record_count") != len(source_records):
        errors.append("source_record_count must match source_day118_checklist length.")
    if report.get("ledger_record_count") != len(ledger):
        errors.append("ledger_record_count must match evidence_intake_outcome_ledger length.")

    source_sequence = [item.get("review_sequence") for item in source_records]
    ledger_sequence = [item.get("source_review_sequence") for item in ledger]
    if source_sequence != list(range(1, EXPECTED_SOURCE_RECORD_COUNT + 1)):
        errors.append("Day118 source review_sequence must be 1..7.")
    if ledger_sequence != source_sequence:
        errors.append("Day119 ledger source_review_sequence must align to Day118 source review_sequence.")

    required_fields = (
        "evidence_id",
        "day118_requirement_id",
        "evidence_name",
        "expected_from",
        "intake_status",
        "gap_status",
        "deferred_reason",
        "follow_up_action",
        "reviewer_note",
        "safety_boundary_impact",
        "acceptance_impact",
    )
    for item in ledger:
        evidence_id = item.get("evidence_id", "<unknown>")
        for field in required_fields:
            if not item.get(field):
                errors.append(f"ledger item {evidence_id} must include {field}.")
        if item.get("intake_status") not in ALLOWED_INTAKE_STATUSES:
            errors.append(f"ledger item {evidence_id}.intake_status is not allowed.")
        if item.get("gap_status") not in ALLOWED_GAP_STATUSES:
            errors.append(f"ledger item {evidence_id}.gap_status is not allowed.")
        for flag in ROW_FALSE_FLAGS:
            if item.get(flag) is not False:
                errors.append(f"ledger item {evidence_id}.{flag} must be false.")

    if not any(
        item.get("gap_status") in {"OPEN_GAP", "DEFERRED_GAP", "SAFETY_BLOCKED_GAP", "CLARIFICATION_REQUIRED"}
        for item in ledger
    ):
        errors.append("ledger must preserve at least one open, deferred, safety-blocked, or clarification gap.")
    if not any(item.get("blocked_by_safety_boundary") is True for item in ledger):
        errors.append("ledger must include at least one safety-boundary-blocked evidence item.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day119 JSON and HTML reports.")
    return errors


def _derive_status(errors: List[str]) -> str:
    if not errors:
        return OVERALL_STATUS
    if any("exactly 7" in error for error in errors):
        return STATUS_SOURCE_COUNT_MISMATCH
    if any("align" in error or "1..7" in error for error in errors):
        return STATUS_SOURCE_ALIGNMENT_MISMATCH
    if any("must be false" in error for error in errors):
        return STATUS_SAFETY_VIOLATION
    return "DAY119_INTAKE_LEDGER_REVIEW_REQUIRED"


def build_reviewer_evidence_intake_outcome_ledger_report(
    project_root: Path = Path("."),
    day118_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_day118 = (
        deepcopy(day118_report)
        if day118_report is not None
        else build_deferred_action_review_sequence_runbook_report(project_root=project_root)
    )
    source_records = deepcopy(source_day118.get("evidence_intake_checklist", []))
    ledger = build_evidence_intake_outcome_ledger(source_day118)
    summary_flags = _false_summary_flags()
    gap_status_counts: Dict[str, int] = {}
    intake_status_counts: Dict[str, int] = {}
    for item in ledger:
        intake_status_counts[item["intake_status"]] = intake_status_counts.get(item["intake_status"], 0) + 1
        gap_status_counts[item["gap_status"]] = gap_status_counts.get(item["gap_status"], 0) + 1

    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "task_alias": TASK_ALIAS,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "created_at": CREATED_AT,
        "overall_status": OVERALL_STATUS,
        "status": OVERALL_STATUS,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "source_day": SOURCE_DAY,
        "source_task": DAY118_TASK_NAME,
        "source_artifact": DAY118_REPORT_JSON.as_posix(),
        "source_record_count": len(source_records),
        "ledger_record_count": len(ledger),
        "source_day118_checklist": source_records,
        "evidence_intake_outcome_ledger": ledger,
        "intake_status_counts": intake_status_counts,
        "gap_status_counts": gap_status_counts,
        "open_or_deferred_gap_count": sum(
            1
            for item in ledger
            if item["gap_status"] in {"OPEN_GAP", "DEFERRED_GAP", "SAFETY_BLOCKED_GAP", "CLARIFICATION_REQUIRED"}
        ),
        "safety_blocked_gap_count": sum(1 for item in ledger if item["gap_status"] == "SAFETY_BLOCKED_GAP"),
        "received_no_gap_count": sum(
            1 for item in ledger if item["intake_status"] == "RECEIVED" and item["gap_status"] == "NO_GAP"
        ),
        "final_recommendation": FINAL_RECOMMENDATION,
        "reviewer_notes": [
            "Day119 records evidence intake outcomes for the seven Day118 expected evidence items.",
            "Day119 does not judge acceptance, make reviewer sign-off, or close the safety review.",
            "Deferred evidence remains deferred until separately reviewed in a future day.",
            "Rejected or safety-blocked evidence cannot unlock execution or change parser/runtime capability.",
        ],
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "safety_invariants": summary_flags,
        **summary_flags,
    }
    report["validation_errors"] = validate_reviewer_evidence_intake_outcome_ledger_report(report)
    report["status"] = _derive_status(report["validation_errors"])
    if report["validation_errors"]:
        report["overall_status"] = report["status"]
    return report


def _cell_text(value: Any) -> str:
    if isinstance(value, list):
        return _list_to_sentence(value)
    if isinstance(value, bool):
        return json.dumps(value)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]], empty_columns: int = 0) -> str:
    rendered = [
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    ]
    if rendered:
        return "".join(rendered)
    if empty_columns:
        return "<tr>" + "".join("<td>none</td>" for _ in range(empty_columns)) + "</tr>"
    return ""


def write_reviewer_evidence_intake_outcome_ledger_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_rows = _table_rows(
        (
            item["evidence_id"],
            item["day118_requirement_id"],
            item["source_deferred_action_id"],
            item["expected_from"],
            item["intake_status"],
            item["gap_status"],
            item["deferred_reason"],
            item["follow_up_action"],
            item["blocked_by_safety_boundary"],
            item["acceptance_impact"],
        )
        for item in report["evidence_intake_outcome_ledger"]
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(FULL_TITLE)}</title>
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
  <h1>{html.escape(FULL_TITLE)}</h1>
  <p>
    <span class="badge">REVIEW_ONLY</span>
    <span class="badge">EVIDENCE_INTAKE_LOG</span>
    <span class="badge">NO_ACCEPTANCE</span>
    <span class="badge">NO_EXECUTION_UNLOCK</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p>Day119 records evidence intake outcomes for Day118 expected evidence items only.</p>

  <h2>Ledger</h2>
  <table>
    <thead><tr><th>Evidence ID</th><th>Day118 Requirement</th><th>Deferred Action</th><th>Expected From</th><th>Intake Status</th><th>Gap Status</th><th>Deferred Reason</th><th>Follow-up</th><th>Safety Blocked</th><th>Acceptance Impact</th></tr></thead>
    <tbody>{ledger_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_reviewer_evidence_intake_outcome_ledger_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_reviewer_evidence_intake_outcome_ledger_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_reviewer_evidence_intake_outcome_ledger_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_reviewer_evidence_intake_outcome_ledger_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == OVERALL_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
