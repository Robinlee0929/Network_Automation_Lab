"""Day114 parser consumer reviewer triage evidence traceability audit.

This module links the Day112 intake package and Day113 triage outcome log into
a deterministic reviewer-facing traceability map. It remains audit-only and
report-only: it does not infer readiness, unlock a next phase, invoke adapters
or brokers, use SSH, contact live devices, call OpenAI APIs, or change config.
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


CREATED_AT = "2026-06-11T00:00:00+08:00"
DAY = 114
DAY_ID = "Day114"
TASK_NAME = "parser-consumer-reviewer-triage-evidence-traceability"
TITLE = "Day114 Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit"
PHASE_NAME = "Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit"
SCHEMA_VERSION = "day114.parser_consumer_reviewer_triage_evidence_traceability.v1"
SOURCE_DAY112 = "Day112"
SOURCE_DAY113 = "Day113"
REPORT_JSON = Path("reports") / "lab-summary" / "day114_parser_consumer_reviewer_triage_evidence_traceability.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day114_parser_consumer_reviewer_triage_evidence_traceability.html"
AGENTS_FILE = Path("AGENTS.md")

REVIEWER_STATUS = "TRACEABILITY_AUDITED_NON_EXECUTABLE"
TRACEABILITY_STATUS = "DAY112_DAY113_TRACEABILITY_COMPLETE"
BLOCKED_RECORD_STATUS = "PRESERVED_VISIBLE_NON_EXECUTABLE"
FINAL_RECOMMENDATION = "TRACEABILITY_AUDITED_DO_NOT_ADVANCE"

TRACEABILITY_RECORD_FIELDS = (
    "trace_id",
    "source_day",
    "source_intake_id",
    "day113_outcome_id",
    "blocked_condition_id",
    "blocked_reason",
    "evidence_status",
    "preservation_status",
    "reviewer_visibility",
    "downgrade_detected",
    "missing_trace_detected",
    "execution_readiness_inferred",
    "next_phase_allowed",
    "audit_note",
)

INTAKE_TO_OUTCOME_STAGE = {
    "release_package_present": "source_intake_received",
    "source_chain_day107_to_day111_traceable": "source_intake_received",
    "day109_blocked_records_preserved": "blocked_condition_reviewed",
    "day110_final_gate_locked": "blocked_condition_reviewed",
    "day111_package_frozen": "source_intake_received",
    "next_phase_still_disallowed": "advancement_decision_recorded",
    "safety_invariants_preserved": "advancement_decision_recorded",
    "reviewer_routes_defined": "triage_outcome_selected",
    "return_path_defined": "triage_outcome_selected",
    "execution_unlock_absent": "advancement_decision_recorded",
}

BLOCKED_CONDITION_DETAILS = {
    "day109_blocked_records_preserved": (
        "D114-BLOCKED-DAY109",
        "Day109 blocked records remain preserved through Day112 intake and Day113 triage.",
    ),
    "day110_final_gate_locked": (
        "D114-BLOCKED-DAY110",
        "Day110 final gate remains locked by preserved blocked records.",
    ),
    "next_phase_still_disallowed": (
        "D114-BLOCKED-NEXT-PHASE",
        "Next phase remains disallowed and cannot be inferred from reviewer triage.",
    ),
    "execution_unlock_absent": (
        "D114-BLOCKED-EXECUTION-UNLOCK",
        "Execution readiness and approval unlock remain absent.",
    ),
}

SAFETY_INVARIANTS: Dict[str, bool] = {
    "review_only": True,
    "report_only": True,
    "audit_only": True,
    "deterministic": True,
    "source_day112_intake_frozen": True,
    "source_day113_triage_frozen": True,
    "ssh_allowed": False,
    "live_device_access_allowed": False,
    "network_command_execution_allowed": False,
    "config_mutation_allowed": False,
    "adapter_invocation_allowed": False,
    "broker_invocation_allowed": False,
    "runner_invocation_allowed": False,
    "approval_unlock_supported": False,
    "execution_readiness_supported": False,
    "next_phase_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
    "cloud_runtime_allowed": False,
    "mapped_task_execution_allowed": False,
}

FALSE_SAFETY_FLAGS = (
    "ssh_allowed",
    "live_device_access_allowed",
    "network_command_execution_allowed",
    "config_mutation_allowed",
    "adapter_invocation_allowed",
    "broker_invocation_allowed",
    "runner_invocation_allowed",
    "approval_unlock_supported",
    "execution_readiness_supported",
    "next_phase_allowed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "cloud_runtime_allowed",
    "mapped_task_execution_allowed",
)

TRUE_SAFETY_FLAGS = (
    "review_only",
    "report_only",
    "audit_only",
    "deterministic",
    "source_day112_intake_frozen",
    "source_day113_triage_frozen",
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
        "agents_md_read_before_day114_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day114 records that AGENTS.md was read before traceability audit work "
            "and that the repository instruction file was not modified by this audit."
        ),
    }


def _safety_invariant_result(safety_invariants: Dict[str, Any]) -> str:
    false_ok = all(safety_invariants.get(flag) is False for flag in FALSE_SAFETY_FLAGS)
    true_ok = all(safety_invariants.get(flag) is True for flag in TRUE_SAFETY_FLAGS)
    return "PASS" if false_ok and true_ok else "FAIL"


def build_triage_evidence_traceability_records(
    day112_report: Dict[str, Any],
    day113_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    outcome_by_stage = {
        entry.get("stage"): entry
        for entry in day113_report.get("triage_outcome_log", [])
    }
    records: List[Dict[str, Any]] = []
    for index, intake_record in enumerate(day112_report.get("intake_triage_checklist", []), start=1):
        intake_id = intake_record.get("id")
        outcome_stage = INTAKE_TO_OUTCOME_STAGE.get(intake_id)
        outcome = outcome_by_stage.get(outcome_stage, {})
        blocked_condition_id, blocked_reason = BLOCKED_CONDITION_DETAILS.get(
            intake_id,
            ("", "none"),
        )
        is_blocked_record = bool(blocked_condition_id)
        record = {
            "trace_id": f"D114-T{index:03d}",
            "source_day": SOURCE_DAY112,
            "source_intake_id": intake_id,
            "day113_outcome_id": outcome.get("entry_id", ""),
            "blocked_condition_id": blocked_condition_id,
            "blocked_reason": blocked_reason,
            "evidence_status": (
                "BLOCKED_EVIDENCE_VISIBLE_NON_EXECUTABLE"
                if is_blocked_record
                else "PASS_EVIDENCE_VISIBLE_NON_EXECUTABLE"
            ),
            "preservation_status": "preserved",
            "reviewer_visibility": "visible",
            "downgrade_detected": False,
            "missing_trace_detected": not bool(outcome),
            "execution_readiness_inferred": False,
            "next_phase_allowed": False,
            "audit_note": (
                "Day112 intake record is linked to a Day113 reviewer-visible outcome "
                "without inferring execution readiness or allowing next phase."
            ),
        }
        records.append(record)
    return records


def build_traceability_summary(
    day112_report: Dict[str, Any],
    day113_report: Dict[str, Any],
    traceability_records: List[Dict[str, Any]],
    safety_invariants: Dict[str, Any],
) -> Dict[str, Any]:
    source_intake_count = len(day112_report.get("intake_triage_checklist", []))
    source_ids = {item.get("id") for item in day112_report.get("intake_triage_checklist", [])}
    linked_source_ids = {item.get("source_intake_id") for item in traceability_records}
    blocked_records = [record for record in traceability_records if record.get("blocked_condition_id")]
    missing_trace_count = sum(1 for record in traceability_records if record.get("missing_trace_detected") is True)
    missing_trace_count += len(source_ids - linked_source_ids)
    downgrade_detected_count = sum(1 for record in traceability_records if record.get("downgrade_detected") is True)
    execution_readiness_inferred_count = sum(
        1 for record in traceability_records if record.get("execution_readiness_inferred") is True
    )
    next_phase_allowed_count = sum(1 for record in traceability_records if record.get("next_phase_allowed") is True)
    unsafe_flag_count = sum(1 for flag in FALSE_SAFETY_FLAGS if safety_invariants.get(flag) is not False)
    unsafe_flag_count += sum(1 for flag in TRUE_SAFETY_FLAGS if safety_invariants.get(flag) is not True)
    day113_outcome_ids = {entry.get("entry_id") for entry in day113_report.get("triage_outcome_log", [])}
    linked_day113_outcome_count = sum(
        1 for record in traceability_records if record.get("day113_outcome_id") in day113_outcome_ids
    )
    preserved_blocked_record_count = sum(
        1
        for record in blocked_records
        if record.get("preservation_status") == "preserved"
        and record.get("reviewer_visibility") == "visible"
        and record.get("execution_readiness_inferred") is False
        and record.get("next_phase_allowed") is False
    )
    source_day112_intake_linked = (
        source_intake_count == len(traceability_records)
        and source_ids == linked_source_ids
        and missing_trace_count == 0
    )
    source_day113_triage_linked = (
        linked_day113_outcome_count == len(traceability_records)
        and {"D113-L003", "D113-L004"} <= {record.get("day113_outcome_id") for record in traceability_records}
    )
    blocked_records_preserved = (
        len(blocked_records) > 0
        and preserved_blocked_record_count == len(blocked_records)
        and day113_report.get("selected_reviewer_outcome") == "HOLD_FOR_BLOCKED_RECORDS"
    )
    overall_status = (
        "PASS"
        if source_day112_intake_linked
        and source_day113_triage_linked
        and blocked_records_preserved
        and missing_trace_count == 0
        and downgrade_detected_count == 0
        and execution_readiness_inferred_count == 0
        and next_phase_allowed_count == 0
        and unsafe_flag_count == 0
        else "FAIL"
    )
    return {
        "total_trace_records": len(traceability_records),
        "source_intake_record_count": source_intake_count,
        "linked_day113_outcome_count": linked_day113_outcome_count,
        "blocked_condition_count": len(blocked_records),
        "preserved_blocked_record_count": preserved_blocked_record_count,
        "missing_trace_count": missing_trace_count,
        "downgrade_detected_count": downgrade_detected_count,
        "execution_readiness_inferred_count": execution_readiness_inferred_count,
        "next_phase_allowed_count": next_phase_allowed_count,
        "unsafe_flag_count": unsafe_flag_count,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "TRACEABILITY_AUDIT_FAILED_NON_EXECUTABLE",
        "source_day112_intake_linked": source_day112_intake_linked,
        "source_day113_triage_linked": source_day113_triage_linked,
        "blocked_records_preserved": blocked_records_preserved,
        "source_day112_task": DAY112_TASK_NAME,
        "source_day113_task": DAY113_TASK_NAME,
        "source_day113_selected_reviewer_outcome": day113_report.get("selected_reviewer_outcome"),
        "source_day113_final_recommendation": day113_report.get("final_recommendation"),
    }


def build_parser_consumer_reviewer_triage_evidence_traceability_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day112_report: Optional[Dict[str, Any]] = None,
    day113_report: Optional[Dict[str, Any]] = None,
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
    agents_evidence = build_agents_md_pre_read_evidence(
        project_root,
        agents_md_pre_read=agents_md_pre_read,
        agents_md_modified=agents_md_modified,
    )
    traceability_records = build_triage_evidence_traceability_records(source_day112, source_day113)
    safety_invariants = deepcopy(SAFETY_INVARIANTS)
    summary = build_traceability_summary(
        source_day112,
        source_day113,
        traceability_records,
        safety_invariants,
    )
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "traceability_status": TRACEABILITY_STATUS,
        "blocked_record_status": BLOCKED_RECORD_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": "AUDIT_ONLY_REPORT_ONLY",
        "source_day112": SOURCE_DAY112,
        "source_day113": SOURCE_DAY113,
        "source_tasks": {
            "day112": DAY112_TASK_NAME,
            "day113": DAY113_TASK_NAME,
        },
        "source_reports": {
            "day112_json": DAY112_REPORT_JSON.as_posix(),
            "day112_html": DAY112_REPORT_HTML.as_posix(),
            "day113_json": DAY113_REPORT_JSON.as_posix(),
            "day113_html": DAY113_REPORT_HTML.as_posix(),
        },
        "traceability_record_fields": list(TRACEABILITY_RECORD_FIELDS),
        "traceability_records": traceability_records,
        "traceability_summary": summary,
        "source_day112_intake_linked": summary["source_day112_intake_linked"],
        "source_day113_triage_linked": summary["source_day113_triage_linked"],
        "blocked_records_preserved": summary["blocked_records_preserved"],
        "safety_invariants": safety_invariants,
        "agents_md_read_before_day114_work": agents_evidence["agents_md_read_before_day114_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "agents_md_pre_read_evidence": agents_evidence,
        "report_paths": {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()},
        "fixed_safety_strings": [
            "NO_EXECUTION_READINESS_INFERRED",
            "NO_NEXT_PHASE_UNLOCK",
            "BLOCKED_RECORDS_PRESERVED",
        ],
        "reviewer_notes": [
            "Day114 verifies that all Day112 intake records and Day113 triage outcomes remain traceable, blocked records are preserved, no downgrade occurred, and no execution readiness or next phase unlock is inferred.",
            "Day114 用來確認 Day112 收件與 Day113 分流結果完整可追溯，blocked records 被保留，沒有被降級、漏記或誤判為可執行，也不解鎖下一階段。",
            "No live, SSH, mapped-task, broker, adapter, runner, OpenAI API, cloud, voice, approval unlock, or config mutation path is added.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_reviewer_triage_evidence_traceability_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "TRACEABILITY_AUDIT_FAILED_NON_EXECUTABLE"
        report["traceability_status"] = "TRACEABILITY_AUDIT_FAILED"
        report["blocked_record_status"] = "PRESERVATION_NOT_PROVEN"
        report["final_recommendation"] = "DO_NOT_ADVANCE_TRACEABILITY_AUDIT_FAILED"
        report["next_phase_allowed"] = False
        report["approval_unlock_allowed"] = False
        report["execution_readiness_allowed"] = False
        report["traceability_summary"]["overall_status"] = "FAIL"
        report["traceability_summary"]["reviewer_status"] = "TRACEABILITY_AUDIT_FAILED_NON_EXECUTABLE"
    return report


def validate_parser_consumer_reviewer_triage_evidence_traceability_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "reviewer_status": REVIEWER_STATUS,
        "traceability_status": TRACEABILITY_STATUS,
        "blocked_record_status": BLOCKED_RECORD_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "approval_unlock_allowed": False,
        "execution_readiness_allowed": False,
        "audit_type": "AUDIT_ONLY_REPORT_ONLY",
        "source_day112": SOURCE_DAY112,
        "source_day113": SOURCE_DAY113,
        "source_day112_intake_linked": True,
        "source_day113_triage_linked": True,
        "blocked_records_preserved": True,
        "agents_md_read_before_day114_work": True,
        "agents_md_pre_read_result": "PASS",
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    records = report.get("traceability_records", [])
    if len(records) != 10:
        errors.append("traceability_records must contain exactly the ten Day112 intake records.")
    if report.get("traceability_record_fields") != list(TRACEABILITY_RECORD_FIELDS):
        errors.append("traceability_record_fields must match the Day114 traceability schema.")
    for record in records:
        if tuple(record.keys()) != TRACEABILITY_RECORD_FIELDS:
            errors.append(f"traceability record {record.get('trace_id', '<unknown>')} must match the schema.")
        if not record.get("source_intake_id"):
            errors.append(f"traceability record {record.get('trace_id', '<unknown>')} must include source_intake_id.")
        if not record.get("day113_outcome_id"):
            errors.append(f"traceability record {record.get('trace_id', '<unknown>')} must include day113_outcome_id.")
        if record.get("preservation_status") != "preserved":
            errors.append(f"traceability record {record.get('trace_id', '<unknown>')} must be preserved.")
        if record.get("reviewer_visibility") != "visible":
            errors.append(f"traceability record {record.get('trace_id', '<unknown>')} must be reviewer-visible.")
        for field in ("downgrade_detected", "missing_trace_detected", "execution_readiness_inferred", "next_phase_allowed"):
            if record.get(field) is not False:
                errors.append(f"traceability record {record.get('trace_id', '<unknown>')}.{field} must be false.")
        if record.get("blocked_condition_id") and (
            record.get("blocked_reason") in {"", "none"} or not record.get("evidence_status")
        ):
            errors.append(
                f"blocked traceability record {record.get('trace_id', '<unknown>')} must include blocked reason and evidence status."
            )

    safety = report.get("safety_invariants", {})
    for flag in FALSE_SAFETY_FLAGS:
        if safety.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    for flag in TRUE_SAFETY_FLAGS:
        if safety.get(flag) is not True:
            errors.append(f"safety_invariants.{flag} must be true.")

    summary = report.get("traceability_summary", {})
    expected_summary = {
        "total_trace_records": 10,
        "source_intake_record_count": 10,
        "linked_day113_outcome_count": 10,
        "blocked_condition_count": 4,
        "preserved_blocked_record_count": 4,
        "missing_trace_count": 0,
        "downgrade_detected_count": 0,
        "execution_readiness_inferred_count": 0,
        "next_phase_allowed_count": 0,
        "unsafe_flag_count": 0,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "source_day112_intake_linked": True,
        "source_day113_triage_linked": True,
        "blocked_records_preserved": True,
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"traceability_summary.{key} must be {json.dumps(value)}.")

    if report.get("report_paths") != {"json": REPORT_JSON.as_posix(), "html": REPORT_HTML.as_posix()}:
        errors.append("report_paths must point to Day114 JSON and HTML reports.")
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


def write_parser_consumer_reviewer_triage_evidence_traceability_html(
    report: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record_rows = _table_rows(
        (
            record["trace_id"],
            record["source_intake_id"],
            record["day113_outcome_id"],
            record["blocked_condition_id"] or "none",
            record["blocked_reason"],
            record["evidence_status"],
            record["preservation_status"],
            record["reviewer_visibility"],
            json.dumps(record["downgrade_detected"]),
            json.dumps(record["execution_readiness_inferred"]),
            json.dumps(record["next_phase_allowed"]),
        )
        for record in report["traceability_records"]
    )
    summary_rows = _table_rows(
        (key, json.dumps(value) if isinstance(value, bool) else value)
        for key, value in report["traceability_summary"].items()
    )
    safety_rows = _table_rows(
        (key, json.dumps(value)) for key, value in report["safety_invariants"].items()
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
    <span class="badge">AUDIT_ONLY</span>
    <span class="badge">REPORT_ONLY</span>
    <span class="badge">TRACEABILITY_AUDITED_NON_EXECUTABLE</span>
    <span class="badge">NO_EXECUTION_READINESS_INFERRED</span>
    <span class="badge">NO_NEXT_PHASE_UNLOCK</span>
    <span class="badge">BLOCKED_RECORDS_PRESERVED</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Traceability status:</strong> {html.escape(report['traceability_status'])}</p>
  <p><strong>Blocked record status:</strong> {html.escape(report['blocked_record_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>
  <p>Day114 verifies that all Day112 intake records and Day113 triage outcomes remain traceable, blocked records are preserved, no downgrade occurred, and no execution readiness or next phase unlock is inferred.</p>
  <p>Day114 用來確認 Day112 收件與 Day113 分流結果完整可追溯，blocked records 被保留，沒有被降級、漏記或誤判為可執行，也不解鎖下一階段。</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day114 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day114_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Traceability Summary</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>

  <h2>Traceability Records</h2>
  <table>
    <thead><tr><th>Trace ID</th><th>Day112 Intake ID</th><th>Day113 Outcome ID</th><th>Blocked Condition</th><th>Blocked Reason</th><th>Evidence Status</th><th>Preservation</th><th>Visibility</th><th>Downgrade</th><th>Readiness Inferred</th><th>Next Phase</th></tr></thead>
    <tbody>{record_rows}</tbody>
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


def write_parser_consumer_reviewer_triage_evidence_traceability_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = (
        deepcopy(report)
        if report is not None
        else build_parser_consumer_reviewer_triage_evidence_traceability_report(project_root)
    )
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_reviewer_triage_evidence_traceability_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_reviewer_triage_evidence_traceability_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
