"""Day105 parser acceptance closure / safety-blocked exit summary.

Day105 is a closure package for Day96-Day104 parser evidence. It summarizes
existing reports only and deliberately does not add parser recognition,
execution, adapter, SSH, live-device, OpenAI, voice, or configuration behavior.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_parser_evidence_matrix import build_parser_evidence_matrix_report, build_source_reports
from intent_parser_reviewer_acceptance_gate import build_parser_reviewer_acceptance_gate_report


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-acceptance-closure"
TITLE = "Day105 Parser Acceptance Closure / Safety-Blocked Exit Summary"
PHASE_NAME = "Parser Acceptance Closure / Safety-Blocked Exit Summary"
SCHEMA_VERSION = "day105.parser_acceptance_closure.v1"
CLOSURE_TYPE = "SUMMARY_ONLY"
FINAL_RECOMMENDATION = "SAFETY_BLOCKED_REVIEW_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day105_parser_acceptance_closure.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day105_parser_acceptance_closure.html"
COVERED_DAYS = [96, 97, 98, 99, 100, 101, 102, 103, 104]
COVERED_DAY_IDS = [f"Day{day}" for day in COVERED_DAYS]

EXECUTION_FLAGS = {
    "execution_allowed": False,
    "live_device_access_allowed": False,
    "ssh_allowed": False,
    "config_change_allowed": False,
    "mapped_task_execution_allowed": False,
    "openai_api_allowed": False,
    "voice_input_allowed": False,
}

STATIC_SAFETY_FLAGS = {
    "parser_capability_added": False,
    "capability_added": False,
    "adapter_invocation_allowed": False,
    "broker_handoff_allowed": False,
    "next_phase_allowed": False,
    "execution_unlocked": False,
}


def build_parser_acceptance_closure_report(
    source_day104_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the Day105 closure report from deterministic local evidence."""
    source_reports = build_source_reports()
    day103_report = build_parser_evidence_matrix_report()
    day104_report = (
        deepcopy(source_day104_report)
        if source_day104_report is not None
        else build_parser_reviewer_acceptance_gate_report(day103_report)
    )
    source_reports["Day103"] = day103_report
    source_reports["Day104"] = day104_report

    covered_day_summaries = build_covered_day_summaries(source_reports)
    report = {
        "day": 105,
        "day_id": "Day105",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase_name": PHASE_NAME,
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "overall_status": "PASS",
        "reviewer_status": "CLOSURE_READY_REVIEW_ONLY",
        "closure_type": CLOSURE_TYPE,
        "covered_days": COVERED_DAYS,
        "covered_day_ids": COVERED_DAY_IDS,
        "covered_day_summaries": covered_day_summaries,
        "capability_added": False,
        "parser_capability_added": False,
        "safety_blocked": True,
        "final_recommendation": FINAL_RECOMMENDATION,
        "next_phase_allowed": False,
        "execution_flags": deepcopy(EXECUTION_FLAGS),
        **EXECUTION_FLAGS,
        **STATIC_SAFETY_FLAGS,
        "closure_summary": build_closure_summary(covered_day_summaries, day104_report),
        "safety_blocking_reasons": build_safety_blocking_reasons(),
        "next_phase_entry_conditions": build_next_phase_entry_conditions(),
        "evidence_references": build_evidence_references(covered_day_summaries),
        "read_only_evidence_proofs": build_read_only_evidence_proofs(day103_report, day104_report),
        "source_decisions": {
            "day103_reviewer_status": day103_report.get("reviewer_status"),
            "day104_acceptance_decision": day104_report.get("acceptance_decision"),
            "day104_next_stage_allowed": day104_report.get("next_stage_allowed"),
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_parser_acceptance_closure_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["reviewer_status"] = "CLOSURE_REVIEW_REQUIRED"
    return report


def build_covered_day_summaries(source_reports: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for day in COVERED_DAY_IDS:
        report = source_reports.get(day, {})
        reports = report.get("reports", {})
        summaries.append(
            {
                "day": day,
                "day_number": int(day.replace("Day", "")),
                "title": str(report.get("title") or fallback_day_title(day)),
                "task": str(report.get("task") or report.get("task_name") or ""),
                "overall_status": str(report.get("overall_status") or report.get("status") or "UNKNOWN"),
                "reviewer_status": str(
                    report.get("reviewer_status")
                    or report.get("phase")
                    or report.get("acceptance_decision")
                    or "UNKNOWN"
                ),
                "report_json_path": str(reports.get("json", "")),
                "report_html_path": str(reports.get("html", "")),
                "summary_only_note": day_summary_note(day),
            }
        )
    return summaries


def fallback_day_title(day: str) -> str:
    titles = {
        "Day96": "Read-only Output Parser Prototype",
        "Day97": "Parser Evidence Quality",
        "Day98": "Parser Classification Matrix",
        "Day99": "Parser Evidence Coverage / Sample Gap Audit",
        "Day100": "Parser Phase Gate Review / Readiness Decision",
        "Day101": "Parser Evidence Closure Plan",
        "Day102": "Parser Fixture Expansion",
        "Day103": "Parser Evidence Matrix / Gap Traceability",
        "Day104": "Parser Reviewer Acceptance Gate / Matrix Decision Review",
    }
    return titles[day]


def day_summary_note(day: str) -> str:
    notes = {
        "Day96": "Established parser-only handling for normalized fake adapter output.",
        "Day97": "Hardened unsupported and malformed output evidence as fail-closed review material.",
        "Day98": "Mapped parser classifications to reviewer actions and safety invariants.",
        "Day99": "Audited parser coverage and kept sample gaps visible for review.",
        "Day100": "Separated parser evidence readiness from broker or execution readiness.",
        "Day101": "Planned closure work while keeping broker handoff and execution blocked.",
        "Day102": "Expanded static fixtures as evidence without changing parser behavior.",
        "Day103": "Collected Day96-Day102 evidence into a gap traceability matrix.",
        "Day104": "Converted the matrix into a reviewer acceptance gate with safety blocks preserved.",
    }
    return notes[day]


def build_closure_summary(
    covered_day_summaries: List[Dict[str, Any]],
    day104_report: Dict[str, Any],
) -> List[Dict[str, str]]:
    return [
        {
            "summary_id": "D105-S01",
            "statement": "Day96-Day104 parser evidence is now packaged for reviewer inspection.",
        },
        {
            "summary_id": "D105-S02",
            "statement": (
                "The covered days show parser evidence quality, coverage, traceability, "
                "fixture expansion, and reviewer gate decisions."
            ),
        },
        {
            "summary_id": "D105-S03",
            "statement": (
                f"Day104 decision remains {day104_report.get('acceptance_decision')}; "
                "Day105 does not reinterpret that decision as permission to execute."
            ),
        },
        {
            "summary_id": "D105-S04",
            "statement": (
                f"Covered source reports: {', '.join(item['day'] for item in covered_day_summaries)}."
            ),
        },
    ]


def build_safety_blocking_reasons() -> List[Dict[str, str]]:
    reasons = [
        "Parser evidence is strong enough for review, but not sufficient for live execution.",
        "Output parsing does not prove safe remediation.",
        "Read-only observation is different from device mutation.",
        "No adapter execution unlock exists.",
        "No human approval envelope has granted execution.",
        "No rollback or recovery path has been validated for live changes.",
        "No real-device command mutation is allowed by the current safety boundary.",
        "Reviewer acceptance is for evidence quality only, not execution permission.",
    ]
    return [
        {"reason_id": f"D105-B{index:02d}", "reason": reason}
        for index, reason in enumerate(reasons, start=1)
    ]


def build_next_phase_entry_conditions() -> List[Dict[str, Any]]:
    conditions = [
        "Explicit human approval is required.",
        "A separate branch and separate phase gate are required.",
        "No automatic execution unlock is allowed.",
        "Read-only scope remains the default.",
        "The adapter boundary remains guarded.",
        "All live-capable paths must be blocked by tests.",
        "A rollback and recovery plan must be documented before any future live mutation discussion.",
        "Test evidence must prove rejected scenarios do not invoke an adapter.",
        "The dashboard remains read-only.",
        "Reports remain evidence-only.",
    ]
    return [
        {
            "condition_id": f"D105-C{index:02d}",
            "condition": condition,
            "satisfied_for_day105": False,
        }
        for index, condition in enumerate(conditions, start=1)
    ]


def build_evidence_references(covered_day_summaries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    references = []
    for item in covered_day_summaries:
        references.append(
            {
                "day": str(item["day"]),
                "title": str(item["title"]),
                "task": str(item["task"]),
                "report_json_path": str(item["report_json_path"]),
                "report_html_path": str(item["report_html_path"]),
            }
        )
    return references


def build_read_only_evidence_proofs(
    day103_report: Dict[str, Any],
    day104_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        {
            "proof_id": "D105-P01",
            "source": "Day103 safety_invariants",
            "evidence": day103_report.get("safety_invariants", {}),
        },
        {
            "proof_id": "D105-P02",
            "source": "Day104 safety_flags",
            "evidence": day104_report.get("safety_flags", {}),
        },
        {
            "proof_id": "D105-P03",
            "source": "Day105 execution_flags",
            "evidence": deepcopy(EXECUTION_FLAGS),
        },
    ]


def validate_parser_acceptance_closure_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 105:
        errors.append("day must be 105.")
    if report.get("task") != TASK_NAME:
        errors.append(f"task must be {TASK_NAME}.")
    if report.get("phase_name") != PHASE_NAME:
        errors.append(f"phase_name must be {PHASE_NAME}.")
    if report.get("closure_type") != CLOSURE_TYPE:
        errors.append(f"closure_type must be {CLOSURE_TYPE}.")
    if report.get("covered_days") != COVERED_DAYS:
        errors.append("covered_days must be exactly Day96 through Day104.")
    if report.get("final_recommendation") != FINAL_RECOMMENDATION:
        errors.append(f"final_recommendation must be {FINAL_RECOMMENDATION}.")
    if report.get("safety_blocked") is not True:
        errors.append("safety_blocked must be true.")
    for flag, expected in {**EXECUTION_FLAGS, **STATIC_SAFETY_FLAGS}.items():
        if report.get(flag) is not expected:
            errors.append(f"{flag} must be {json.dumps(expected)}.")
    for flag, expected in EXECUTION_FLAGS.items():
        if report.get("execution_flags", {}).get(flag) is not expected:
            errors.append(f"execution_flags.{flag} must be false.")
    if len(report.get("covered_day_summaries", [])) != len(COVERED_DAYS):
        errors.append("covered_day_summaries must include Day96 through Day104.")
    if not report.get("closure_summary"):
        errors.append("closure_summary must be non-empty.")
    if not report.get("safety_blocking_reasons"):
        errors.append("safety_blocking_reasons must be non-empty.")
    if not report.get("next_phase_entry_conditions"):
        errors.append("next_phase_entry_conditions must be non-empty.")
    if not report.get("evidence_references"):
        errors.append("evidence_references must be non-empty.")
    return errors


def write_parser_acceptance_closure_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_acceptance_closure_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_acceptance_closure_html(safe_report, html_path)
    return json_path, html_path


def write_parser_acceptance_closure_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    day_rows = "".join(
        "<tr>"
        f"<td>{html.escape(item['day'])}</td>"
        f"<td>{html.escape(item['title'])}</td>"
        f"<td>{html.escape(item['overall_status'])} / {html.escape(item['reviewer_status'])}</td>"
        f"<td>{html.escape(item['summary_only_note'])}</td>"
        f"<td><code>{html.escape(item['report_json_path'])}</code><br><code>{html.escape(item['report_html_path'])}</code></td>"
        "</tr>"
        for item in report["covered_day_summaries"]
    )
    reason_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['reason_id'])}</code></td>"
        f"<td>{html.escape(item['reason'])}</td>"
        "</tr>"
        for item in report["safety_blocking_reasons"]
    )
    condition_rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['condition_id'])}</code></td>"
        f"<td>{html.escape(item['condition'])}</td>"
        f"<td>{html.escape(json.dumps(item['satisfied_for_day105']))}</td>"
        "</tr>"
        for item in report["next_phase_entry_conditions"]
    )
    flag_rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for name, value in report["execution_flags"].items()
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
    .blocked {{ color: #8a1f11; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>{html.escape(TITLE)}</h1>
  <p><strong>Phase:</strong> {html.escape(report['phase_name'])}</p>
  <p><strong>Status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Closure type:</strong> <code>{html.escape(report['closure_type'])}</code></p>
  <p><strong>Final recommendation:</strong> <span class="blocked">{html.escape(report['final_recommendation'])}</span></p>
  <p><strong>Next phase allowed:</strong> {html.escape(json.dumps(report['next_phase_allowed']))}</p>
  <p><strong>Day105 reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <p><strong>Scope:</strong> Day105 summarizes Day96-Day104 parser evidence for reviewer inspection only. It adds no parser capability and grants no live-device, command, adapter, API, voice, or configuration permission.</p>
  <h2>Covered Days</h2>
  <table>
    <thead><tr><th>Day</th><th>Title</th><th>Status</th><th>Day105 Summary</th><th>Reports</th></tr></thead>
    <tbody>{day_rows}</tbody>
  </table>
  <h2>Safety-blocked Reasons</h2>
  <table>
    <thead><tr><th>ID</th><th>Reason</th></tr></thead>
    <tbody>{reason_rows}</tbody>
  </table>
  <h2>Next-phase Entry Conditions</h2>
  <table>
    <thead><tr><th>ID</th><th>Condition</th><th>Satisfied for Day105</th></tr></thead>
    <tbody>{condition_rows}</tbody>
  </table>
  <h2>Execution Flags</h2>
  <table>
    <thead><tr><th>Flag</th><th>Value</th></tr></thead>
    <tbody>{flag_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )
