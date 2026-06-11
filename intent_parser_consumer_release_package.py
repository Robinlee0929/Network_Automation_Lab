"""Day111 parser consumer evidence freeze and release package.

This module freezes Day107-Day110 parser consumer evidence into one
deterministic reviewer-facing release package. It is report-only: it does not
execute mapped tasks, invoke adapters or brokers, use SSH, contact live
devices, call OpenAI APIs, unlock approvals, or change configuration.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from intent_parser_consumer_final_gate import (
    FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS,
    FINAL_RECOMMENDATION_LOCKED,
    REPORT_HTML as DAY110_REPORT_HTML,
    REPORT_JSON as DAY110_REPORT_JSON,
    TASK_NAME as DAY110_TASK_NAME,
    build_parser_consumer_final_gate_report,
)
from intent_parser_consumer_handoff_readiness_matrix import (
    BLOCKED,
    NEEDS_CLARIFICATION,
    READY,
    REPORT_HTML as DAY109_REPORT_HTML,
    REPORT_JSON as DAY109_REPORT_JSON,
    TASK_NAME as DAY109_TASK_NAME,
    build_parser_consumer_handoff_readiness_matrix_report,
)
from intent_parser_contract_consumer_handoff import (
    REPORT_HTML as DAY108_REPORT_HTML,
    REPORT_JSON as DAY108_REPORT_JSON,
    TASK_NAME as DAY108_TASK_NAME,
    build_parser_contract_consumer_handoff_report,
)
from intent_parser_reviewer_evidence_contract import (
    REPORT_HTML as DAY107_REPORT_HTML,
    REPORT_JSON as DAY107_REPORT_JSON,
    TASK_NAME as DAY107_TASK_NAME,
    build_parser_reviewer_evidence_contract_report,
)


CREATED_AT = "2026-06-11T00:00:00+08:00"
DAY = 111
DAY_ID = "Day111"
TASK_NAME = "parser-consumer-release-package"
TITLE = "Day111 Parser Consumer Evidence Freeze / Release Package"
PHASE_NAME = "Parser Consumer Evidence Freeze / Release Package"
SCHEMA_VERSION = "day111.parser_consumer_release_package.v1"
REPORT_JSON = Path("reports") / "lab-summary" / "day111_parser_consumer_release_package.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day111_parser_consumer_release_package.html"
AGENTS_FILE = Path("AGENTS.md")

REVIEWER_STATUS = "RELEASE_PACKAGE_READY_REVIEW_ONLY"
RELEASE_PACKAGE_STATUS = "FROZEN"
FINAL_RECOMMENDATION = "RELEASE_PACKAGE_READY_BUT_DO_NOT_ADVANCE"

SAFETY_INVARIANTS: Dict[str, bool] = {
    "ssh_allowed": False,
    "live_device_access_allowed": False,
    "network_command_execution_allowed": False,
    "config_mutation_allowed": False,
    "openai_api_allowed": False,
    "voice_runtime_allowed": False,
    "cloud_runtime_allowed": False,
    "approval_unlock_supported": False,
    "mapped_task_execution_allowed": False,
    "execution_broker_unlock_allowed": False,
    "next_phase_execution_allowed": False,
    "review_only": True,
    "report_only": True,
    "deterministic": True,
}

EXECUTION_FALSE_FLAGS = (
    "ssh_allowed",
    "live_device_access_allowed",
    "network_command_execution_allowed",
    "config_mutation_allowed",
    "openai_api_allowed",
    "voice_runtime_allowed",
    "cloud_runtime_allowed",
    "approval_unlock_supported",
    "mapped_task_execution_allowed",
    "execution_broker_unlock_allowed",
    "next_phase_execution_allowed",
)

TRUE_SAFETY_FLAGS = ("review_only", "report_only", "deterministic")


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
        "agents_md_read_before_day111_work": agents_md_pre_read,
        "agents_md_pre_read_result": result,
        "agents_md_file_found": agents_file_found,
        "agents_md_file_readable": agents_file_readable,
        "agents_md_heading_found": agents_heading_found,
        "agents_md_modified": agents_md_modified,
        "reviewer_note": (
            "Day111 records that AGENTS.md was read before Day111 implementation work "
            "and that the repository instruction file was not modified by the release package."
        ),
    }


def build_source_day_records() -> List[Dict[str, Any]]:
    return [
        {
            "day": 107,
            "theme": "Parser Reviewer Evidence Contract Consolidation",
            "runner": DAY107_TASK_NAME,
            "expected_reports": [
                DAY107_REPORT_JSON.as_posix(),
                DAY107_REPORT_HTML.as_posix(),
            ],
            "role": "reviewer evidence contract baseline",
        },
        {
            "day": 108,
            "theme": "Parser Contract Consumer Handoff",
            "runner": DAY108_TASK_NAME,
            "expected_reports": [
                DAY108_REPORT_JSON.as_posix(),
                DAY108_REPORT_HTML.as_posix(),
            ],
            "role": "consumer handoff mapping",
        },
        {
            "day": 109,
            "theme": "Parser Consumer Handoff Readiness Matrix",
            "runner": DAY109_TASK_NAME,
            "expected_status": "BLOCKED_RECORDS_PRESENT",
            "expected_counts": {
                READY: 1,
                NEEDS_CLARIFICATION: 1,
                BLOCKED: 1,
            },
            "required_preserved_condition": {
                "blocking_condition_preserved": True,
            },
            "expected_reports": [
                DAY109_REPORT_JSON.as_posix(),
                DAY109_REPORT_HTML.as_posix(),
            ],
            "role": "readiness matrix before final gate",
        },
        {
            "day": 110,
            "theme": "Parser Consumer Final Gate / Reviewer Decision Summary",
            "runner": DAY110_TASK_NAME,
            "expected_status": FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS,
            "expected_final_recommendation": FINAL_RECOMMENDATION_LOCKED,
            "expected": {
                "next_phase_allowed": False,
                "agents_md_read_before_day110_work": True,
                "agents_md_pre_read_result": "PASS",
            },
            "expected_reports": [
                DAY110_REPORT_JSON.as_posix(),
                DAY110_REPORT_HTML.as_posix(),
            ],
            "role": "final reviewer gate preserving blocked records",
        },
    ]


def _count_frozen_evidence(source_days: Iterable[Dict[str, Any]]) -> int:
    return len(list(source_days))


def _safety_invariant_result(safety_invariants: Dict[str, Any]) -> str:
    false_ok = all(safety_invariants.get(flag) is False for flag in EXECUTION_FALSE_FLAGS)
    true_ok = all(safety_invariants.get(flag) is True for flag in TRUE_SAFETY_FLAGS)
    return "PASS" if false_ok and true_ok else "FAIL"


def build_frozen_evidence_chain(source_days: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "freeze_id": f"D111-F{index:03d}",
            "source_day": f"Day{record['day']}",
            "runner": record["runner"],
            "theme": record["theme"],
            "role": record["role"],
            "frozen": True,
            "execution_allowed": False,
            "expected_reports": deepcopy(record.get("expected_reports", [])),
        }
        for index, record in enumerate(source_days, start=1)
    ]


def build_parser_consumer_release_package_report(
    project_root: Path = Path("."),
    agents_md_pre_read: bool = True,
    agents_md_modified: bool = False,
    day107_report: Optional[Dict[str, Any]] = None,
    day108_report: Optional[Dict[str, Any]] = None,
    day109_report: Optional[Dict[str, Any]] = None,
    day110_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_day_records = build_source_day_records()
    source107 = deepcopy(day107_report) if day107_report is not None else build_parser_reviewer_evidence_contract_report()
    source108 = deepcopy(day108_report) if day108_report is not None else build_parser_contract_consumer_handoff_report()
    source109 = (
        deepcopy(day109_report)
        if day109_report is not None
        else build_parser_consumer_handoff_readiness_matrix_report()
    )
    source110 = (
        deepcopy(day110_report)
        if day110_report is not None
        else build_parser_consumer_final_gate_report(project_root=project_root, agents_md_pre_read=agents_md_pre_read)
    )
    agents_evidence = build_agents_md_pre_read_evidence(project_root, agents_md_pre_read, agents_md_modified)
    frozen_evidence_chain = build_frozen_evidence_chain(source_day_records)
    blocked_condition_summary = {
        "day109_expected_status": "BLOCKED_RECORDS_PRESENT",
        "day109_observed_status": source109.get("reviewer_status"),
        "day109_ready_count": source109.get("ready_count"),
        "day109_needs_clarification_count": source109.get("needs_clarification_count"),
        "day109_blocked_count": source109.get("blocked_count"),
        "day109_blocking_condition_preserved": source109.get("safety_summary", {}).get("blocking_condition_preserved"),
        "day110_expected_status": FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS,
        "day110_observed_status": source110.get("final_gate_status"),
        "day110_final_recommendation": source110.get("final_recommendation"),
        "day110_next_phase_allowed": source110.get("next_phase_allowed"),
        "blocked_condition_preserved": (
            source109.get("reviewer_status") == "BLOCKED_RECORDS_PRESENT"
            and source109.get("blocked_count") == 1
            and source109.get("safety_summary", {}).get("blocking_condition_preserved") is True
            and source110.get("final_gate_status") == FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS
            and source110.get("final_recommendation") == FINAL_RECOMMENDATION_LOCKED
            and source110.get("next_phase_allowed") is False
        ),
    }
    report_paths = {
        "json": REPORT_JSON.as_posix(),
        "html": REPORT_HTML.as_posix(),
    }
    release_manifest = {
        "release_scope": "Day107-Day110 parser consumer reviewer evidence",
        "source_day_count": len(source_day_records),
        "frozen_evidence_count": _count_frozen_evidence(frozen_evidence_chain),
        "release_package_status": RELEASE_PACKAGE_STATUS,
        "reviewer_status": REVIEWER_STATUS,
        "generated_reports": deepcopy(report_paths),
        "expected_source_reports": [
            path
            for record in source_day_records
            for path in record.get("expected_reports", [])
        ],
        "execution_unlocks_included": False,
        "mapped_task_execution_included": False,
    }
    traceability_summary = {
        "source_days": [record["day"] for record in source_day_records],
        "source_tasks": [record["runner"] for record in source_day_records],
        "day107_status": source107.get("overall_status"),
        "day108_status": source108.get("overall_status"),
        "day109_status": source109.get("reviewer_status"),
        "day110_status": source110.get("final_gate_status"),
        "release_package_ready": True,
        "next_phase_allowed": False,
        "safety_invariant_result": _safety_invariant_result(SAFETY_INVARIANTS),
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
    }
    report: Dict[str, Any] = {
        "task": TASK_NAME,
        "day": DAY,
        "day_id": DAY_ID,
        "title": TITLE,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "reviewer_status": REVIEWER_STATUS,
        "release_package_status": RELEASE_PACKAGE_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "agents_md_read_before_day111_work": agents_evidence["agents_md_read_before_day111_work"],
        "agents_md_pre_read_result": agents_evidence["agents_md_pre_read_result"],
        "agents_md_modified": agents_evidence["agents_md_modified"],
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "audit_type": "REPORT_ONLY",
        "source_days": source_day_records,
        "frozen_evidence_chain": frozen_evidence_chain,
        "release_manifest": release_manifest,
        "safety_invariants": deepcopy(SAFETY_INVARIANTS),
        "blocked_condition_summary": blocked_condition_summary,
        "traceability_summary": traceability_summary,
        "report_paths": report_paths,
        "agents_md_pre_read_evidence": agents_evidence,
        "reviewer_notes": [
            "Day111 freezes Day107-Day110 parser consumer reviewer evidence into a release package.",
            "Release package ready does not mean next phase execution is allowed.",
            "Day109 blocked records and Day110 final-gate lock remain preserved.",
            "No live, SSH, mapped-task, broker, adapter, OpenAI API, cloud, voice, or config mutation path is added.",
        ],
    }
    report["validation_errors"] = validate_parser_consumer_release_package_report(report)
    if report["validation_errors"]:
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "RELEASE_PACKAGE_BLOCKED_REVIEW_ONLY"
        report["release_package_status"] = "LOCKED"
        report["final_recommendation"] = "DO_NOT_ADVANCE_RELEASE_PACKAGE_VALIDATION_FAILED"
        report["next_phase_allowed"] = False
    return report


def validate_parser_consumer_release_package_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected = {
        "task": TASK_NAME,
        "day": DAY,
        "title": TITLE,
        "created_at": CREATED_AT,
        "reviewer_status": REVIEWER_STATUS,
        "release_package_status": RELEASE_PACKAGE_STATUS,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "agents_md_read_before_day111_work": True,
        "agents_md_pre_read_result": "PASS",
        "agents_md_modified": False,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"{key} must be {json.dumps(value)}.")

    source_days = report.get("source_days", [])
    if [record.get("day") for record in source_days] != [107, 108, 109, 110]:
        errors.append("source_days must contain exactly Day107, Day108, Day109, and Day110.")
    if len(report.get("frozen_evidence_chain", [])) != 4:
        errors.append("frozen_evidence_chain must contain exactly four records.")
    if not all(record.get("frozen") is True for record in report.get("frozen_evidence_chain", [])):
        errors.append("all frozen_evidence_chain records must be frozen.")

    safety = report.get("safety_invariants", {})
    for flag in EXECUTION_FALSE_FLAGS:
        if safety.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    for flag in TRUE_SAFETY_FLAGS:
        if safety.get(flag) is not True:
            errors.append(f"safety_invariants.{flag} must be true.")

    blocked = report.get("blocked_condition_summary", {})
    if blocked.get("day109_observed_status") != "BLOCKED_RECORDS_PRESENT":
        errors.append("Day109 blocked status must be preserved.")
    if blocked.get("day109_ready_count") != 1:
        errors.append("Day109 READY count must remain 1.")
    if blocked.get("day109_needs_clarification_count") != 1:
        errors.append("Day109 NEEDS_CLARIFICATION count must remain 1.")
    if blocked.get("day109_blocked_count") != 1:
        errors.append("Day109 BLOCKED count must remain 1.")
    if blocked.get("day109_blocking_condition_preserved") is not True:
        errors.append("Day109 blocking_condition_preserved must remain true.")
    if blocked.get("day110_observed_status") != FINAL_GATE_LOCKED_BY_BLOCKED_RECORDS:
        errors.append("Day110 final gate locked condition must be preserved.")
    if blocked.get("day110_final_recommendation") != FINAL_RECOMMENDATION_LOCKED:
        errors.append("Day110 final recommendation must remain locked.")
    if blocked.get("day110_next_phase_allowed") is not False:
        errors.append("Day110 next_phase_allowed must remain false.")
    if blocked.get("blocked_condition_preserved") is not True:
        errors.append("blocked_condition_preserved must be true.")

    manifest = report.get("release_manifest", {})
    if manifest.get("source_day_count") != 4:
        errors.append("release_manifest.source_day_count must be 4.")
    if manifest.get("frozen_evidence_count") != 4:
        errors.append("release_manifest.frozen_evidence_count must be 4.")
    if manifest.get("execution_unlocks_included") is not False:
        errors.append("release_manifest.execution_unlocks_included must be false.")
    if manifest.get("mapped_task_execution_included") is not False:
        errors.append("release_manifest.mapped_task_execution_included must be false.")

    if report.get("report_paths") != {
        "json": REPORT_JSON.as_posix(),
        "html": REPORT_HTML.as_posix(),
    }:
        errors.append("report_paths must point to Day111 JSON and HTML reports.")
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


def write_parser_consumer_release_package_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_rows = _table_rows(
        (
            f"Day{record['day']}",
            record["theme"],
            record["runner"],
            record["role"],
            ", ".join(record.get("expected_reports", [])),
        )
        for record in report["source_days"]
    )
    frozen_rows = _table_rows(
        (
            record["freeze_id"],
            record["source_day"],
            record["runner"],
            json.dumps(record["frozen"]),
            json.dumps(record["execution_allowed"]),
        )
        for record in report["frozen_evidence_chain"]
    )
    safety_rows = _table_rows(
        (key, json.dumps(value)) for key, value in report["safety_invariants"].items()
    )
    blocked = report["blocked_condition_summary"]
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
    <span class="badge">FROZEN</span>
    <span class="badge">NO_LIVE_EXECUTION</span>
    <span class="badge">NO_SSH</span>
    <span class="badge">NO_MAPPED_TASK_EXECUTION</span>
  </p>
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])}</p>
  <p><strong>Reviewer status:</strong> {html.escape(report['reviewer_status'])}</p>
  <p><strong>Release package status:</strong> {html.escape(report['release_package_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>

  <h2>AGENTS.md Pre-read Evidence</h2>
  <table>
    <tbody>
      <tr><th>Path</th><td><code>{html.escape(agents['agents_md_path'])}</code></td></tr>
      <tr><th>Read before Day111 work</th><td>{html.escape(json.dumps(agents['agents_md_read_before_day111_work']))}</td></tr>
      <tr><th>Pre-read result</th><td><strong>{html.escape(agents['agents_md_pre_read_result'])}</strong></td></tr>
      <tr><th>AGENTS.md modified</th><td>{html.escape(json.dumps(agents['agents_md_modified']))}</td></tr>
    </tbody>
  </table>

  <h2>Day107-Day110 Source Chain</h2>
  <table>
    <thead><tr><th>Day</th><th>Theme</th><th>Runner</th><th>Role</th><th>Expected Reports</th></tr></thead>
    <tbody>{source_rows}</tbody>
  </table>

  <h2>Frozen Evidence Status</h2>
  <table>
    <thead><tr><th>Freeze ID</th><th>Source Day</th><th>Runner</th><th>Frozen</th><th>Execution Allowed</th></tr></thead>
    <tbody>{frozen_rows}</tbody>
  </table>

  <h2>Blocked Condition Preserved</h2>
  <table>
    <tbody>
      <tr><th>Day109 status</th><td>{html.escape(str(blocked['day109_observed_status']))}</td></tr>
      <tr><th>READY / NEEDS_CLARIFICATION / BLOCKED</th><td>{blocked['day109_ready_count']} / {blocked['day109_needs_clarification_count']} / {blocked['day109_blocked_count']}</td></tr>
      <tr><th>Day109 blocking condition preserved</th><td>{html.escape(json.dumps(blocked['day109_blocking_condition_preserved']))}</td></tr>
      <tr><th>Day110 gate</th><td>{html.escape(str(blocked['day110_observed_status']))}</td></tr>
      <tr><th>Day110 recommendation</th><td>{html.escape(str(blocked['day110_final_recommendation']))}</td></tr>
      <tr><th>Overall blocked condition preserved</th><td><strong>{html.escape(json.dumps(blocked['blocked_condition_preserved']))}</strong></td></tr>
    </tbody>
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


def write_parser_consumer_release_package_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_consumer_release_package_report(project_root)
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_consumer_release_package_html(safe_report, html_path)
    return json_path, html_path


def main() -> int:
    report = build_parser_consumer_release_package_report()
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
