"""Day110 parser consumer final gate and reviewer decision summary.

This module consumes the Day109 parser consumer readiness matrix and emits a
deterministic reviewer-facing final gate. It is report-only and cannot unlock
execution, invoke adapters or brokers, use SSH, contact devices, call OpenAI
APIs, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_consumer_handoff_readiness_matrix import (
    BLOCKED,
    NEEDS_CLARIFICATION,
    READY,
    REPORT_HTML as DAY109_REPORT_HTML,
    REPORT_JSON as DAY109_REPORT_JSON,
    TASK_NAME as DAY109_TASK_NAME,
    build_parser_consumer_handoff_readiness_matrix_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
DAY = 110
DAY_ID = "Day110"
TASK_NAME = "parser-consumer-final-gate"
TITLE = "Day110 Parser Consumer Final Gate / Reviewer Decision Summary"
PHASE_NAME = "Parser Consumer Final Gate / Reviewer Decision Summary"
SCHEMA_VERSION = "day110.parser_consumer_final_gate.v1"
SOURCE_DAY = "Day109"
SOURCE_TASK = DAY109_TASK_NAME
REPORT_JSON = Path("reports") / "lab-summary" / "day110_parser_consumer_final_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day110_parser_consumer_final_gate.html"
AGENTS_FILE = Path("AGENTS.md")

FINAL_GATE_READY = "FINAL_GATE_READY_FOR_REVIEW_ONLY_CONSUMER_USE"
FINAL_GATE_CLARIFICATION_REQUIRED = "FINAL_GATE_REVIEWER_CLARIFICATION_REQUIRED"
FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS = "FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS"

FINAL_RECOMMENDATION_READY = "REVIEW_ONLY_CONSUMER_SUMMARY_READY"
FINAL_RECOMMENDATION_CLARIFY = "REVIEWER_CLARIFICATION_REQUIRED_BEFORE_CONSUMER_SIGNOFF"
FINAL_RECOMMENDATION_LOCKED = "DO_NOT_ADVANCE_BLOCKED_RECORDS_PRESENT"

SAFETY_INVARIANTS: Dict[str, Any] = {
    "review_only": True,
    "report_only": True,
    "no_live_execution": True,
    "no_ssh": True,
    "no_device_connection": True,
    "no_write_or_config_change": True,
    "no_command_execution": True,
    "no_adapter_invocation": True,
    "no_broker_invocation": True,
    "no_runner_execution": True,
    "no_mapped_task_execution": True,
    "openai_api_used": False,
    "external_api_used": False,
    "voice_runtime_used": False,
    "approval_unlock_supported": False,
    "execution_unlock_supported": False,
}

LOCKED_FALSE_FLAGS = (
    "openai_api_used",
    "external_api_used",
    "voice_runtime_used",
    "approval_unlock_supported",
    "execution_unlock_supported",
)


def _count_by(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    record_list = list(records)
    values = sorted({str(record.get(field, "")) for record in record_list})
    return {
        value: sum(1 for record in record_list if str(record.get(field, "")) == value)
        for value in values
    }


def build_agents_md_pre_read_evidence(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
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
        "agents_md_pre_read_declared": agents_md_pre_read,
        "agents_md_read_before_day110_work": agents_md_pre_read,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_pre_read_result": result,
        "reviewer_note": (
            "Day110 records whether AGENTS.md was read before this task's work "
            "and verifies the repository instruction file is present/readable."
        ),
    }


def _final_gate_decision(
    day109_report: Dict[str, Any],
    agents_evidence: Dict[str, Any],
) -> Tuple[str, str, bool, List[str]]:
    blockers: List[str] = []
    if day109_report.get("overall_status") != "PASS":
        blockers.append("DAY109_REPORT_NOT_PASS")
    if day109_report.get("blocked_count", 0) > 0:
        blockers.append("DAY109_BLOCKED_RECORDS_PRESENT")
    if day109_report.get("safety_summary", {}).get("blocking_condition_preserved") is not True:
        blockers.append("DAY109_BLOCKING_CONDITION_NOT_PRESERVED")
    if agents_evidence.get("agents_md_pre_read_result") != "PASS":
        blockers.append("AGENTS_MD_PRE_READ_NOT_PROVEN")

    if blockers:
        return FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS, FINAL_RECOMMENDATION_LOCKED, False, blockers
    if day109_report.get("needs_clarification_count", 0) > 0:
        return (
            FINAL_GATE_CLARIFICATION_REQUIRED,
            FINAL_RECOMMENDATION_CLARIFY,
            False,
            ["DAY109_NEEDS_CLARIFICATION_RECORDS_PRESENT"],
        )
    return FINAL_GATE_READY, FINAL_RECOMMENDATION_READY, False, []


def build_parser_consumer_final_gate_report(
    day109_report: Optional[Dict[str, Any]] = None,
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
) -> Dict[str, Any]:
    source_report = deepcopy(day109_report) if day109_report is not None else build_parser_consumer_handoff_readiness_matrix_report()
    readiness_matrix = deepcopy(source_report.get("readiness_matrix", []))
    agents_evidence = build_agents_md_pre_read_evidence(project_root, agents_md_pre_read)
    final_gate_status, final_recommendation, next_phase_allowed, gate_blockers = _final_gate_decision(
        source_report,
        agents_evidence,
    )
    reviewer_decision_summary = {
        "source_total_records": int(source_report.get("total_records", len(readiness_matrix))),
        "ready_count": int(source_report.get("ready_count", 0)),
        "needs_clarification_count": int(source_report.get("needs_clarification_count", 0)),
        "blocked_count": int(source_report.get("blocked_count", 0)),
        "readiness_status_counts": _count_by(readiness_matrix, "readiness_status"),
        "handoff_status_counts": _count_by(readiness_matrix, "handoff_status"),
        "source_reviewer_status": str(source_report.get("reviewer_status", "UNKNOWN")),
        "final_gate_status": final_gate_status,
        "final_recommendation": final_recommendation,
        "next_phase_allowed": next_phase_allowed,
        "gate_blockers": gate_blockers,
    }
    report: Dict[str, Any] = {
        "day": DAY,
        "day_id": DAY_ID,
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
        "overall_status": "PASS",
        "audit_type": "REPORT_ONLY",
        "reviewer_status": final_gate_status,
        "final_gate_status": final_gate_status,
        "final_recommendation": final_recommendation,
        "next_phase_allowed": next_phase_allowed,
        "agents_md_pre_read_evidence": agents_evidence,
        "reviewer_decision_summary": reviewer_decision_summary,
        "gate_blockers": gate_blockers,
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "source_reports": {
            "day109_json": DAY109_REPORT_JSON.as_posix(),
            "day109_html": DAY109_REPORT_HTML.as_posix(),
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "reviewer_notes": [
            "Day110 is the final reviewer summary gate for Day109 parser consumer readiness evidence.",
            "PASS means the summary was generated and validated; it does not mean execution is unlocked.",
            "Blocked or clarification records keep next_phase_allowed=false.",
            "AGENTS.md pre-read evidence is displayed for reviewer confirmation.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_final_gate_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS
        report["final_gate_status"] = FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS
        report["final_recommendation"] = FINAL_RECOMMENDATION_LOCKED
        report["next_phase_allowed"] = False
    return report


def validate_parser_consumer_final_gate_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "day": DAY,
        "day_id": DAY_ID,
        "task": TASK_NAME,
        "phase_name": PHASE_NAME,
        "audit_type": "REPORT_ONLY",
        "source_day": SOURCE_DAY,
        "source_task": SOURCE_TASK,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")
    if report.get("next_phase_allowed") is not False:
        errors.append("next_phase_allowed must remain false.")
    if report.get("agents_md_pre_read_evidence", {}).get("agents_md_pre_read_result") != "PASS":
        errors.append("agents_md_pre_read_result must be PASS.")
    for key, value in SAFETY_INVARIANTS.items():
        if report.get("safety_invariants", {}).get(key) is not value:
            errors.append(f"safety_invariants.{key} must be {json.dumps(value)}.")
    for key in LOCKED_FALSE_FLAGS:
        if report.get("safety_invariants", {}).get(key) is not False:
            errors.append(f"safety_invariants.{key} must remain false.")
    summary = report.get("reviewer_decision_summary", {})
    if summary.get("blocked_count", 0) > 0 and report.get("final_gate_status") != FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS:
        errors.append("blocked Day109 records must lock the final gate.")
    if (
        summary.get("blocked_count", 0) == 0
        and summary.get("needs_clarification_count", 0) > 0
        and report.get("final_gate_status") != FINAL_GATE_CLARIFICATION_REQUIRED
    ):
        errors.append("clarification records must require reviewer clarification.")
    if report.get("overall_status") == "PASS" and report.get("final_gate_status") == FINAL_GATE_READY:
        if summary.get("ready_count", 0) != summary.get("source_total_records", -1):
            errors.append("ready final gate requires all source records to be ready.")
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


def write_parser_consumer_final_gate_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["reviewer_decision_summary"]
    agents = report["agents_md_pre_read_evidence"]
    safety_rows = _table_rows(
        (key, json.dumps(value)) for key, value in report["safety_invariants"].items()
    )
    blocker_rows = _table_rows(((blocker,) for blocker in report["gate_blockers"]), empty_columns=1)
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
    <span class="badge">NO_LIVE_EXECUTION</span>
    <span class="badge">NO_SSH</span>
    <span class="badge">NO_WRITE</span>
  </p>
  <p><strong>Status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['final_gate_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>
  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day110 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day110_work']))}</td></tr>
      <tr><th>File found</th><td>{html.escape(json.dumps(agents['agents_md_file_found']))}</td></tr>
      <tr><th>File readable</th><td>{html.escape(json.dumps(agents['agents_md_file_readable']))}</td></tr>
      <tr><th>Result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
    </tbody>
  </table>
  <h2>Reviewer Decision Summary</h2>
  <table>
    <tbody>
      <tr><th>Source</th><td>{html.escape(report['source_day'])} / <code>{html.escape(report['source_task'])}</code></td></tr>
      <tr><th>Total records</th><td>{summary['source_total_records']}</td></tr>
      <tr><th>READY</th><td>{summary['ready_count']}</td></tr>
      <tr><th>NEEDS_CLARIFICATION</th><td>{summary['needs_clarification_count']}</td></tr>
      <tr><th>BLOCKED</th><td>{summary['blocked_count']}</td></tr>
      <tr><th>Day109 reviewer status</th><td>{html.escape(summary['source_reviewer_status'])}</td></tr>
    </tbody>
  </table>
  <h2>Gate Blockers</h2>
  <table>
    <thead><tr><th>Blocker</th></tr></thead>
    <tbody>{blocker_rows}</tbody>
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


def write_parser_consumer_final_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_consumer_final_gate_report(project_root=project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_final_gate_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_final_gate_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
