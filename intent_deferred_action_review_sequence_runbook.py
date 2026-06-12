"""Day118 deferred action review sequence runbook.

This module converts the Day117 follow-up ownership matrix into a static
reviewer evidence intake checklist. It is review-only and non-advancing: it
does not generate readiness, unlock execution, invoke brokers or runners,
access adapters, use SSH, contact live devices, or execute mapped tasks.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_deferred_action_traceability_review import (
    REPORT_JSON as DAY117_REPORT_JSON,
    TASK_NAME as DAY117_TASK_NAME,
    build_deferred_action_traceability_review_report,
)


CREATED_AT = "2026-06-12T00:00:00+08:00"
DAY = 118
DAY_ID = "Day118"
TASK_NAME = "deferred-action-review-sequence-runbook"
TITLE = "Deferred Action Review Sequence Runbook / Evidence Intake Checklist"
FULL_TITLE = f"Day118 {TITLE}"
PHASE_NAME = TITLE
SCHEMA_VERSION = "day118.deferred_action_review_sequence_runbook.v1"
SOURCE_DAY = 117
EXPECTED_SOURCE_RECORD_COUNT = 7
REVIEWER_STATUS = "INTAKE_CHECKLIST_READY_REVIEW_ONLY"
STATUS_COUNT_MISMATCH = "DAY117_SOURCE_RECORD_COUNT_MISMATCH_REVIEW_REQUIRED"
STATUS_SEQUENCE_MISMATCH = "DAY117_REVIEW_SEQUENCE_MISMATCH_REVIEW_REQUIRED"
STATUS_SAFETY_VIOLATION = "SAFETY_INVARIANT_VIOLATION_REVIEW_REQUIRED"
FINAL_RECOMMENDATION = "REVIEW_ONLY_NON_ADVANCING"
AUDIT_TYPE = "REVIEWER_ONLY_REPORT_ONLY_NON_ADVANCING"
REPORT_JSON = Path("reports") / "lab-summary" / "day118_deferred_action_review_sequence_runbook.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day118_deferred_action_review_sequence_runbook.html"

AGGREGATE_FALSE_FLAGS = (
    "execution_unlock_supported",
    "next_stage_allowed",
    "readiness_transition_allowed",
    "broker_allowed",
    "runner_allowed",
    "adapter_allowed",
    "ssh_allowed",
    "live_access_allowed",
    "mapped_task_execution_allowed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "device_access_allowed",
)

RECORD_FALSE_FLAGS = (
    "advances_stage",
    "unlocks_execution",
    "allows_live_access",
    "allows_ssh",
    "allows_broker",
    "allows_adapter",
    "allows_mapped_task_execution",
)


def _aggregate_false_flags() -> Dict[str, bool]:
    return {flag: False for flag in AGGREGATE_FALSE_FLAGS}


def _record_false_flags() -> Dict[str, bool]:
    return {flag: False for flag in RECORD_FALSE_FLAGS}


def _list_to_sentence(values: Iterable[Any]) -> str:
    return "; ".join(str(value) for value in values)


def build_evidence_intake_checklist(day117_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    source_matrix = deepcopy(day117_report.get("follow_up_ownership_matrix", []))
    checklist: List[Dict[str, Any]] = []
    for source_item in source_matrix:
        deferred_action_id = source_item.get("deferred_id", "")
        owner = source_item.get("owner_role", "")
        follow_up_type = source_item.get("follow_up_type", "")
        blocking_reason = source_item.get("blocking_reason", "")
        review_sequence = source_item.get("review_sequence")
        source_required_evidence = source_item.get("required_evidence", "")
        closure_condition = source_item.get("closure_condition", "")
        source_status = source_item.get("source_item_status", "")

        checklist.append(
            {
                "review_sequence": review_sequence,
                "deferred_action_id": deferred_action_id,
                "owner": owner,
                "follow_up_type": follow_up_type,
                "blocking_reason": blocking_reason,
                "source_day": SOURCE_DAY,
                "source_task": DAY117_TASK_NAME,
                "source_artifact": DAY117_REPORT_JSON.as_posix(),
                "source_deferred_id": deferred_action_id,
                "source_review_sequence": review_sequence,
                "source_status": source_status,
                "evidence_intake_question": (
                    f"What reviewer-visible evidence does {owner} provide for "
                    f"{deferred_action_id} so the {follow_up_type} follow-up can be reviewed "
                    "without changing its deferred, non-advancing state?"
                ),
                "required_evidence": [
                    f"Day117 source row for {deferred_action_id} with review_sequence {review_sequence}.",
                    f"Owner-provided evidence addressing: {source_required_evidence}",
                    "Reviewer note confirming evidence intake only and no readiness, execution, broker, runner, adapter, SSH, live access, or mapped task unlock.",
                ],
                "acceptable_evidence_examples": [
                    "Static reviewer note, report excerpt, or traceability annotation that can be inspected offline.",
                    "Documentation link or deterministic report reference that preserves the Day117 deferred action ID and sequence.",
                    "Reviewer comment stating evidence collected while final recommendation remains REVIEW_ONLY_NON_ADVANCING.",
                ],
                "reject_or_defer_if": [
                    "Evidence is missing, ambiguous, not tied to the Day117 deferred action ID, or not tied to the deterministic review sequence.",
                    "Evidence proposes READY, approval, next-stage transition, execution unlock, live access, SSH, broker, runner, adapter, or mapped task execution.",
                    "Evidence changes the Day117 blocking reason, owner, follow-up type, closure condition, or deferred/non-advancing conclusion.",
                ],
                "reviewer_checkpoints": [
                    f"Confirm source Day117 deferred_action_id={deferred_action_id} and review_sequence={review_sequence}.",
                    f"Confirm owner={owner}, follow_up_type={follow_up_type}, and blocking_reason are preserved.",
                    "Confirm collected evidence remains reviewer-facing, static, and report-only.",
                    "Confirm completion can only remain PENDING_EVIDENCE_REVIEW or later evidence-collected review state, never READY.",
                ],
                "source_required_evidence": source_required_evidence,
                "source_closure_condition": closure_condition,
                "completion_state": "PENDING_EVIDENCE_REVIEW",
                **_record_false_flags(),
            }
        )
    return checklist


def build_review_sequence_runbook() -> List[Dict[str, Any]]:
    return [
        {
            "section": "Pre-intake checks",
            "steps": [
                "Confirm the Day117 source artifact exists and is the source for this Day118 checklist.",
                "Confirm Day117 exposes exactly 7 deferred ownership matrix records.",
                "Confirm review_sequence is deterministic and equals 1..7.",
                "Confirm no readiness transition, next-stage approval, or execution unlock is present.",
            ],
        },
        {
            "section": "Per-record evidence intake",
            "steps": [
                "Process records in review_sequence order from 1 through 7.",
                "Collect reviewer-visible evidence only; do not mark any item READY.",
                "If evidence is incomplete, keep the item deferred and PENDING_EVIDENCE_REVIEW.",
                "If evidence is sufficient, record only that evidence was collected; do not advance stage or unlock execution.",
            ],
        },
        {
            "section": "Post-intake reviewer decision",
            "steps": [
                "Reviewer may produce follow-up review notes or recommendations only.",
                "Do not automatically transition into readiness or next-stage work.",
                "Do not invoke broker, runner, adapter, SSH, live device access, or mapped task execution.",
            ],
        },
        {
            "section": "Stop conditions",
            "steps": [
                "Stop if the source record count is not exactly 7.",
                "Stop if review_sequence is missing, duplicated, or not continuous from 1 through 7.",
                "Stop if any execution, broker, runner, adapter, SSH, live access, mapped task, or external AI flag is true.",
                "Stop if any readiness, next-stage, or execution-unlock flag is true.",
                "Stop if Day117 source records cannot be aligned to the checklist records.",
            ],
        },
    ]


def validate_deferred_action_review_sequence_runbook_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "source_day": SOURCE_DAY,
        "source_record_count": EXPECTED_SOURCE_RECORD_COUNT,
        "checklist_record_count": EXPECTED_SOURCE_RECORD_COUNT,
        "reviewer_status": REVIEWER_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_stage_allowed": False,
        "readiness_transition_allowed": False,
        "execution_unlock_supported": False,
        "review_only": True,
        "non_advancing": True,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    for flag in AGGREGATE_FALSE_FLAGS:
        if report.get(flag) is not False:
            errors.append(f"{flag} must be false.")
        if report.get("safety_invariants", {}).get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")

    source_records = report.get("source_day117_records", [])
    checklist = report.get("evidence_intake_checklist", [])
    if len(source_records) != EXPECTED_SOURCE_RECORD_COUNT:
        errors.append("source_day117_records must contain exactly 7 records.")
    if len(checklist) != EXPECTED_SOURCE_RECORD_COUNT:
        errors.append("evidence_intake_checklist must contain exactly 7 records.")
    if report.get("source_record_count") != len(source_records):
        errors.append("source_record_count must match source_day117_records length.")
    if report.get("checklist_record_count") != len(checklist):
        errors.append("checklist_record_count must match evidence_intake_checklist length.")

    source_sequence = [item.get("review_sequence") for item in source_records]
    checklist_sequence = [item.get("review_sequence") for item in checklist]
    if source_sequence != list(range(1, EXPECTED_SOURCE_RECORD_COUNT + 1)):
        errors.append("Day117 source review_sequence must be 1..7.")
    if checklist_sequence != list(range(1, EXPECTED_SOURCE_RECORD_COUNT + 1)):
        errors.append("Day118 checklist review_sequence must be 1..7.")

    source_ids = [item.get("deferred_id") for item in source_records]
    checklist_ids = [item.get("deferred_action_id") for item in checklist]
    if source_ids != checklist_ids:
        errors.append("Day118 checklist deferred_action_id values must align to Day117 deferred_id values.")

    for item in checklist:
        deferred_action_id = item.get("deferred_action_id", "<unknown>")
        for field in (
            "review_sequence",
            "deferred_action_id",
            "owner",
            "follow_up_type",
            "blocking_reason",
            "evidence_intake_question",
            "required_evidence",
            "acceptable_evidence_examples",
            "reject_or_defer_if",
            "reviewer_checkpoints",
            "completion_state",
        ):
            if not item.get(field):
                errors.append(f"checklist item {deferred_action_id} must include {field}.")
        if item.get("completion_state") != "PENDING_EVIDENCE_REVIEW":
            errors.append(f"checklist item {deferred_action_id}.completion_state must remain PENDING_EVIDENCE_REVIEW.")
        for field in ("required_evidence", "acceptable_evidence_examples", "reject_or_defer_if", "reviewer_checkpoints"):
            if not isinstance(item.get(field), list) or not item.get(field):
                errors.append(f"checklist item {deferred_action_id}.{field} must be a non-empty list.")
        for flag in RECORD_FALSE_FLAGS:
            if item.get(flag) is not False:
                errors.append(f"checklist item {deferred_action_id}.{flag} must be false.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day118 JSON and HTML reports.")
    return errors


def _derive_status(errors: List[str]) -> str:
    if not errors:
        return REVIEWER_STATUS
    if any("exactly 7" in error for error in errors):
        return STATUS_COUNT_MISMATCH
    if any("review_sequence" in error or "1..7" in error for error in errors):
        return STATUS_SEQUENCE_MISMATCH
    if any("must be false" in error for error in errors):
        return STATUS_SAFETY_VIOLATION
    return "DAY118_INTAKE_CHECKLIST_REVIEW_REQUIRED"


def build_deferred_action_review_sequence_runbook_report(
    project_root: Path = Path("."),
    day117_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_day117 = (
        deepcopy(day117_report)
        if day117_report is not None
        else build_deferred_action_traceability_review_report(project_root=project_root)
    )
    source_records = deepcopy(source_day117.get("follow_up_ownership_matrix", []))
    checklist = build_evidence_intake_checklist(source_day117)
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "full_title": FULL_TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "status": REVIEWER_STATUS,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": AUDIT_TYPE,
        "source_day": SOURCE_DAY,
        "source_task": DAY117_TASK_NAME,
        "source_artifact": DAY117_REPORT_JSON.as_posix(),
        "source_record_count": len(source_records),
        "checklist_record_count": len(checklist),
        "source_day117_records": source_records,
        "evidence_intake_checklist": checklist,
        "review_sequence_runbook": build_review_sequence_runbook(),
        "reviewer_status_summary": {
            "source_record_count": len(source_records),
            "checklist_record_count": len(checklist),
            "review_sequence": [item.get("review_sequence") for item in checklist],
            "completion_state_values": sorted({item.get("completion_state") for item in checklist}),
            "final_recommendation": FINAL_RECOMMENDATION,
        },
        "stop_conditions": [
            "record count is not exactly 7",
            "review_sequence is not continuous 1..7",
            "any execution flag is true",
            "any readiness or next-stage allowed flag is true",
            "Day117 source cannot be aligned",
        ],
        "final_recommendation": FINAL_RECOMMENDATION,
        "review_only": True,
        "non_advancing": True,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "reviewer_notes": [
            "Day118 is a reviewer evidence intake checklist derived from the seven Day117 ownership matrix records.",
            "Day118 does not change the Day117 deferred or non-advancing conclusion.",
            "Day118 does not represent readiness and does not unlock execution.",
            "Day118 does not allow live device access, SSH, broker, runner, adapter, or mapped task execution.",
        ],
        "safety_invariants": _aggregate_false_flags(),
        **_aggregate_false_flags(),
    }
    report["validation_errors"] = validate_deferred_action_review_sequence_runbook_report(report)
    report["status"] = _derive_status(report["validation_errors"])
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = report["status"]
    return report


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


def _cell_text(value: Any) -> str:
    if isinstance(value, list):
        return _list_to_sentence(value)
    if isinstance(value, bool):
        return json.dumps(value)
    return str(value)


def write_deferred_action_review_sequence_runbook_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    runbook_rows = _table_rows(
        (section["section"], section["steps"])
        for section in report["review_sequence_runbook"]
    )
    checklist_rows = _table_rows(
        (
            item["review_sequence"],
            item["deferred_action_id"],
            item["owner"],
            item["follow_up_type"],
            item["blocking_reason"],
            item["evidence_intake_question"],
            item["required_evidence"],
            item["reject_or_defer_if"],
            item["completion_state"],
            (
                "advances_stage=false; unlocks_execution=false; allows_live_access=false; "
                "allows_ssh=false; allows_broker=false; allows_adapter=false; "
                "allows_mapped_task_execution=false"
            ),
        )
        for item in report["evidence_intake_checklist"]
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
    <span class="badge">REPORT_ONLY</span>
    <span class="badge">NON_ADVANCING</span>
    <span class="badge">NO_EXECUTION_UNLOCK</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p>Day118 converts the seven Day117 deferred ownership matrix records into reviewer evidence intake questions only.</p>

  <h2>Runbook</h2>
  <table>
    <thead><tr><th>Section</th><th>Steps</th></tr></thead>
    <tbody>{runbook_rows}</tbody>
  </table>

  <h2>Evidence Intake Checklist</h2>
  <table>
    <thead><tr><th>Review Sequence</th><th>Deferred Action ID</th><th>Owner</th><th>Follow-up Type</th><th>Blocking Reason</th><th>Evidence Intake Question</th><th>Required Evidence</th><th>Reject / Defer If</th><th>Completion State</th><th>Safety Flags Summary</th></tr></thead>
    <tbody>{checklist_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_deferred_action_review_sequence_runbook_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_deferred_action_review_sequence_runbook_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_deferred_action_review_sequence_runbook_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_deferred_action_review_sequence_runbook_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
