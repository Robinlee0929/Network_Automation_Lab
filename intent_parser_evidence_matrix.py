"""Day103 parser evidence matrix and gap traceability.

This module integrates Day96-Day102 parser evidence into one static reviewer
matrix. It reads deterministic local report builders only; it does not add
parser behavior or any execution path.
"""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_parser_classification_matrix import build_parser_classification_matrix
from intent_parser_evidence_closure_plan import build_parser_evidence_closure_plan_report
from intent_parser_evidence_coverage_audit import build_parser_evidence_coverage_audit_report
from intent_parser_evidence_quality import build_day97_parser_evidence_quality_report
from intent_parser_fixture_expansion import build_parser_fixture_expansion_report
from intent_parser_phase_gate_review import build_parser_phase_gate_review_report
from intent_readonly_output_parser_prototype import build_day96_parser_report


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-evidence-matrix-gap-traceability"
TITLE = "Parser Evidence Matrix / Gap Traceability"
PHASE = "PARSER_EVIDENCE_MATRIX_READY"
SCHEMA_VERSION = "day103.parser_evidence_matrix.v1"
SOURCE_KIND = "day103_static_day96_day102_evidence_integration"
REVIEW_MODE = "read_only_evidence_matrix_report_only"
REVIEWER_STATUS = "MATRIX_READY"
REPORT_JSON = Path("reports") / "ai" / "day103_parser_evidence_matrix_gap_traceability.json"
REPORT_HTML = Path("reports") / "ai" / "day103_parser_evidence_matrix_gap_traceability.html"

EXPECTED_DAYS = ["Day96", "Day97", "Day98", "Day99", "Day100", "Day101", "Day102"]
TRACE_STATUSES = {
    "TRACE_COMPLETE",
    "REVIEW_REQUIRED",
    "KNOWN_GAP",
    "BLOCKED_BY_SAFETY_BOUNDARY",
}
SAFETY_BOUNDARY_REQUIREMENTS = (
    "no_ssh",
    "no_live_device_access",
    "no_routeros_command_execution",
    "no_config_mutation",
    "no_adapter_invocation",
    "no_executor_invocation",
    "no_broker_handoff",
    "no_dashboard_post_action_endpoint",
    "no_openai_api",
    "no_voice_runtime",
    "no_external_integration",
    "no_execution_unlock",
)
DISABLED_COUNTER_FLAGS = (
    "execution_allowed",
    "adapter_invocation_allowed",
    "broker_handoff_allowed",
    "live_access_allowed",
    "ssh_allowed",
    "parser_capability_added",
)


def build_parser_evidence_matrix_report() -> Dict[str, Any]:
    """Build a deterministic Day103 evidence matrix from Day96-Day102 reports."""
    source_reports = build_source_reports()
    rows = build_matrix_rows(source_reports)
    summary = build_summary(rows)
    report = {
        "day": 103,
        "day_id": "Day103",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "schema_version": SCHEMA_VERSION,
        "source_kind": SOURCE_KIND,
        "review_mode": REVIEW_MODE,
        "scope": {
            "report_only": True,
            "read_only_evidence_integration": True,
            "covered_days": EXPECTED_DAYS,
            "does_not_add_parser_capability": True,
            "does_not_unlock_execution": True,
        },
        "reviewer_question": (
            "Can a reviewer trace each Day96-Day102 parser gap to static evidence, "
            "expected decision, actual result, report path, and safety boundary?"
        ),
        "source_reports": source_report_index(source_reports),
        "summary": summary,
        "matrix_rows": rows,
        "safety_invariants": build_safety_invariants(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "parser_capability_added": False,
        "execution_allowed": False,
        "adapter_invocation_allowed": False,
        "broker_handoff_allowed": False,
        "live_access_allowed": False,
        "ssh_allowed": False,
        "execution_unlock_supported": False,
        "broker_handoff_remains_blocked": True,
        "day104_gate_required_separately": True,
    }
    validation_errors = validate_parser_evidence_matrix_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_source_reports() -> Dict[str, Dict[str, Any]]:
    day96 = build_day96_parser_report()
    day97 = build_day97_parser_evidence_quality_report()
    day98 = build_parser_classification_matrix()
    day99 = build_parser_evidence_coverage_audit_report()
    day100 = build_parser_phase_gate_review_report(day99)
    day101 = build_parser_evidence_closure_plan_report(day100)
    day102 = build_parser_fixture_expansion_report()
    return {
        "Day96": day96,
        "Day97": day97,
        "Day98": day98,
        "Day99": day99,
        "Day100": day100,
        "Day101": day101,
        "Day102": day102,
    }


def source_report_index(source_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {
        day: {
            "task": report.get("task"),
            "title": report.get("title"),
            "overall_status": report.get("overall_status"),
            "reviewer_status": report.get("reviewer_status", report.get("phase")),
            "report_json_path": report.get("reports", {}).get("json"),
            "report_html_path": report.get("reports", {}).get("html"),
        }
        for day, report in source_reports.items()
    }


def build_matrix_rows(source_reports: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    day99_summary = source_reports["Day99"].get("summary", {})
    day100_summary = source_reports["Day100"].get("summary", {})
    day101_summary = source_reports["Day101"].get("summary", {})
    day102_summary = source_reports["Day102"].get("summary", {})

    specs = [
        {
            "day": "Day96",
            "evidence_source": "intent_readonly_output_parser_prototype.build_day96_parser_report",
            "parser_gap": "Prototype can parse normalized fake adapter simulated output only.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day96"], "parser_cases", "case_id"),
            "fixture_category": "prototype_supported_fake_output",
            "expected_decision": "PASS / PARSER_PROTOTYPE_READY",
            "trace_status": "TRACE_COMPLETE",
            "reviewer_note": "Day96 proves a parser-only prototype against Day95 fake output without live fallback.",
        },
        {
            "day": "Day97",
            "evidence_source": "intent_parser_evidence_quality.build_day97_parser_evidence_quality_report",
            "parser_gap": "Unsupported, empty, malformed, incomplete, ambiguous, and degraded output must fail closed as evidence.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day97"], "scenario_cases", "case_id"),
            "fixture_category": "unsupported_output_hardening",
            "expected_decision": "PASS / HARDENED",
            "trace_status": "TRACE_COMPLETE",
            "reviewer_note": "Day97 records unsupported output as parser evidence quality, not an execution failure.",
        },
        {
            "day": "Day98",
            "evidence_source": "intent_parser_classification_matrix.build_parser_classification_matrix",
            "parser_gap": "Parser classifications need reviewer actions and sample-to-decision traceability.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day98"], "matrix_rows", "case_id"),
            "fixture_category": "classification_traceability",
            "expected_decision": "PASS / TRACEABILITY_READY",
            "trace_status": "TRACE_COMPLETE",
            "reviewer_note": "Day98 links Day96 and Day97 cases to classifications, reviewer actions, and non-executable safety invariants.",
        },
        {
            "day": "Day99",
            "evidence_source": "intent_parser_evidence_coverage_audit.build_parser_evidence_coverage_audit_report",
            "parser_gap": "Coverage gaps must be visible before the Day100 phase gate.",
            "fixture_or_evidence_id": _gap_refs(source_reports["Day99"]),
            "fixture_category": "coverage_sample_gap_audit",
            "expected_decision": "PASS / COVERAGE_REVIEW_READY with UNDER_COVERED gaps preserved",
            "trace_status": "KNOWN_GAP" if day99_summary.get("under_covered_count", 0) else "TRACE_COMPLETE",
            "reviewer_note": (
                f"Day99 keeps {day99_summary.get('under_covered_count', 0)} UNDER_COVERED rows as non-blocking "
                "Day100 review inputs."
            ),
        },
        {
            "day": "Day100",
            "evidence_source": "intent_parser_phase_gate_review.build_parser_phase_gate_review_report",
            "parser_gap": "Phase-gate decisions must separate review-only evidence from any broker or execution boundary.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day100"], "decision_rows", "evidence_area"),
            "fixture_category": "phase_gate_readiness_decision",
            "expected_decision": "PASS / PHASE_GATE_REVIEW_READY with broker boundary blocked",
            "trace_status": (
                "REVIEW_REQUIRED"
                if day100_summary.get("under_covered_count", 0) or day100_summary.get("review_only_count", 0)
                else "TRACE_COMPLETE"
            ),
            "reviewer_note": (
                f"Day100 final readiness is {day100_summary.get('final_readiness_decision')}; "
                "broker, executor, adapter, SSH, and live access remain disabled."
            ),
        },
        {
            "day": "Day101",
            "evidence_source": "intent_parser_evidence_closure_plan.build_parser_evidence_closure_plan_report",
            "parser_gap": "UNDER_COVERED and REVIEW_ONLY findings need a closure sequence before any later gate.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day101"], "closure_items", "category"),
            "fixture_category": "evidence_closure_plan",
            "expected_decision": "PASS / EVIDENCE_CLOSURE_PLAN_READY; Day102 -> Day103 -> Day104 -> Day105",
            "trace_status": "REVIEW_REQUIRED",
            "reviewer_note": (
                f"Day101 schedules {', '.join(day101_summary.get('recommended_next_days', []))}; "
                "broker handoff remains blocked."
            ),
        },
        {
            "day": "Day102",
            "evidence_source": "intent_parser_fixture_expansion.build_parser_fixture_expansion_report",
            "parser_gap": "Fixture expansion must prove positive, negative, malformed, ambiguous, and unsafe cases without adding parser capability.",
            "fixture_or_evidence_id": _case_refs(source_reports["Day102"], "fixture_cases", "case_id"),
            "fixture_category": "fixture_expansion_boundary",
            "expected_decision": "PASS / FIXTURE_EXPANSION_READY",
            "trace_status": (
                "BLOCKED_BY_SAFETY_BOUNDARY"
                if day102_summary.get("unsafe_blocked_count", 0)
                else "TRACE_COMPLETE"
            ),
            "reviewer_note": (
                f"Day102 adds {day102_summary.get('total_fixtures', 0)} static fixtures only; "
                f"unsafe_blocked_count={day102_summary.get('unsafe_blocked_count', 0)}."
            ),
        },
    ]

    rows = []
    for index, spec in enumerate(specs, start=1):
        report = source_reports[spec["day"]]
        reports = report.get("reports", {})
        row = {
            "row_id": f"D103-R{index:02d}-{spec['day'].lower()}",
            **spec,
            "actual_result": _actual_result(report),
            "report_json_path": str(reports.get("json", "")),
            "report_html_path": str(reports.get("html", "")),
            "safety_boundary": build_row_safety_boundary(),
            "parser_capability_added": False,
            "execution_allowed": False,
            "adapter_invocation_allowed": False,
            "broker_handoff_allowed": False,
            "live_access_allowed": False,
            "ssh_allowed": False,
        }
        rows.append(row)
    return rows


def _actual_result(report: Dict[str, Any]) -> str:
    reviewer_status = report.get("reviewer_status") or report.get("phase") or report.get("status") or "UNKNOWN"
    return f"{report.get('overall_status', report.get('status', 'UNKNOWN'))} / {reviewer_status}"


def _case_refs(report: Dict[str, Any], collection_name: str, field_name: str) -> str:
    collection = report.get(collection_name, [])
    values = [str(item.get(field_name)) for item in collection if item.get(field_name)]
    if not values:
        return "source-report-summary"
    if len(values) <= 4:
        return ", ".join(values)
    return f"{', '.join(values[:4])}, ... ({len(values)} total)"


def _gap_refs(day99_report: Dict[str, Any]) -> str:
    gaps = day99_report.get("sample_gap_register", [])
    if not gaps:
        return _case_refs(day99_report, "coverage_rows", "coverage_area")
    values = [gap["coverage_area"] for gap in gaps]
    return f"{', '.join(values[:4])}, ... ({len(values)} known gaps)" if len(values) > 4 else ", ".join(values)


def build_row_safety_boundary() -> Dict[str, Any]:
    boundary = {name: True for name in SAFETY_BOUNDARY_REQUIREMENTS}
    boundary.update(
        {
            "execution_allowed": False,
            "adapter_invocation_allowed": False,
            "broker_handoff_allowed": False,
            "live_access_allowed": False,
            "ssh_allowed": False,
            "parser_capability_added": False,
        }
    )
    return boundary


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "report_only": True,
        "read_only_evidence_integration": True,
        "no_config_json_read": True,
        "no_network_calls": True,
        "no_subprocess_execution": True,
        "no_openai_api": True,
        "no_voice_runtime": True,
        "no_dashboard_action_endpoint": True,
        **{flag: False for flag in DISABLED_COUNTER_FLAGS},
        "executor_invocation_allowed": False,
        "routeros_execution_allowed": False,
        "config_mutation_allowed": False,
        "external_integration_allowed": False,
        "execution_unlock_supported": False,
    }


def build_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    trace_statuses = [row["trace_status"] for row in rows]
    day_values = sorted({row["day"] for row in rows}, key=lambda day: EXPECTED_DAYS.index(day))
    safety_violation_count = sum(
        1
        for row in rows
        if any(row.get(flag) is not False for flag in DISABLED_COUNTER_FLAGS)
        or not all(row.get("safety_boundary", {}).get(name) is True for name in SAFETY_BOUNDARY_REQUIREMENTS)
    )
    counts = {status: trace_statuses.count(status) for status in sorted(TRACE_STATUSES)}
    execution_allowed_count = sum(1 for row in rows if row["execution_allowed"] is True)
    adapter_invocation_allowed_count = sum(1 for row in rows if row["adapter_invocation_allowed"] is True)
    broker_handoff_allowed_count = sum(1 for row in rows if row["broker_handoff_allowed"] is True)
    live_access_allowed_count = sum(1 for row in rows if row["live_access_allowed"] is True)
    parser_capability_added_count = sum(1 for row in rows if row["parser_capability_added"] is True)
    ssh_allowed_count = sum(1 for row in rows if row["ssh_allowed"] is True)
    overall_status = (
        "PASS"
        if rows
        and day_values == EXPECTED_DAYS
        and safety_violation_count == 0
        and execution_allowed_count == 0
        and adapter_invocation_allowed_count == 0
        and broker_handoff_allowed_count == 0
        and live_access_allowed_count == 0
        and parser_capability_added_count == 0
        and ssh_allowed_count == 0
        else "FAIL"
    )
    return {
        "total_rows": len(rows),
        "total_days_covered": len(day_values),
        "days_covered": day_values,
        "trace_status_values": sorted(set(trace_statuses)),
        "trace_complete_count": counts["TRACE_COMPLETE"],
        "review_required_count": counts["REVIEW_REQUIRED"],
        "known_gap_count": counts["KNOWN_GAP"],
        "blocked_by_safety_boundary_count": counts["BLOCKED_BY_SAFETY_BOUNDARY"],
        "execution_allowed_count": execution_allowed_count,
        "adapter_invocation_allowed_count": adapter_invocation_allowed_count,
        "broker_handoff_allowed_count": broker_handoff_allowed_count,
        "live_access_allowed_count": live_access_allowed_count,
        "ssh_allowed_count": ssh_allowed_count,
        "parser_capability_added_count": parser_capability_added_count,
        "safety_violation_count": safety_violation_count,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def validate_parser_evidence_matrix_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    rows = report.get("matrix_rows", [])
    summary = report.get("summary", {})

    if report.get("day") != 103:
        errors.append("day must be 103.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-evidence-matrix-gap-traceability.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if summary.get("days_covered") != EXPECTED_DAYS:
        errors.append("Day103 matrix must cover Day96 through Day102.")
    if summary.get("total_rows") != len(rows):
        errors.append("summary.total_rows must match matrix row count.")
    if summary.get("trace_complete_count", 0) < 1:
        errors.append("At least one row must be TRACE_COMPLETE.")
    if summary.get("review_required_count", 0) + summary.get("known_gap_count", 0) < 1:
        errors.append("At least one row must preserve REVIEW_REQUIRED or KNOWN_GAP evidence.")

    for field in (
        "execution_allowed_count",
        "adapter_invocation_allowed_count",
        "broker_handoff_allowed_count",
        "live_access_allowed_count",
        "parser_capability_added_count",
        "ssh_allowed_count",
        "safety_violation_count",
    ):
        if summary.get(field) != 0:
            errors.append(f"summary.{field} must be zero.")

    required_row_fields = (
        "day",
        "evidence_source",
        "parser_gap",
        "fixture_or_evidence_id",
        "fixture_category",
        "expected_decision",
        "actual_result",
        "trace_status",
        "report_json_path",
        "report_html_path",
        "safety_boundary",
        "reviewer_note",
    )
    for row in rows:
        for field in required_row_fields:
            if field not in row:
                errors.append(f"{row.get('row_id', '<unknown>')} missing {field}.")
        if row.get("trace_status") not in TRACE_STATUSES:
            errors.append(f"{row.get('row_id')} has invalid trace_status.")
        if not str(row.get("report_json_path", "")).startswith("reports/"):
            errors.append(f"{row.get('row_id')} report_json_path must use reports/ convention.")
        if not str(row.get("report_json_path", "")).endswith(".json"):
            errors.append(f"{row.get('row_id')} report_json_path must be a JSON path.")
        if not str(row.get("report_html_path", "")).startswith("reports/"):
            errors.append(f"{row.get('row_id')} report_html_path must use reports/ convention.")
        if not str(row.get("report_html_path", "")).endswith(".html"):
            errors.append(f"{row.get('row_id')} report_html_path must be an HTML path.")
        for flag in DISABLED_COUNTER_FLAGS:
            if row.get(flag) is not False:
                errors.append(f"{row.get('row_id')} {flag} must be false.")
        boundary = row.get("safety_boundary", {})
        for name in SAFETY_BOUNDARY_REQUIREMENTS:
            if boundary.get(name) is not True:
                errors.append(f"{row.get('row_id')} safety_boundary.{name} must be true.")
        for flag in DISABLED_COUNTER_FLAGS:
            if boundary.get(flag) is not False:
                errors.append(f"{row.get('row_id')} safety_boundary.{flag} must be false.")

    for field in DISABLED_COUNTER_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
    invariants = report.get("safety_invariants", {})
    for field in ("report_only", "read_only_evidence_integration", "no_config_json_read", "no_network_calls"):
        if invariants.get(field) is not True:
            errors.append(f"safety_invariants.{field} must be true.")
    for field in DISABLED_COUNTER_FLAGS:
        if invariants.get(field) is not False:
            errors.append(f"safety_invariants.{field} must be false.")
    return errors


def write_parser_evidence_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_evidence_matrix_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_evidence_matrix_html(safe_report, html_path)
    return json_path, html_path


def write_parser_evidence_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    matrix_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['day'])}</td>"
        f"<td>{html.escape(row['parser_gap'])}</td>"
        f"<td><code>{html.escape(row['fixture_or_evidence_id'])}</code></td>"
        f"<td>{html.escape(row['expected_decision'])}</td>"
        f"<td>{html.escape(row['actual_result'])}</td>"
        f"<td>{html.escape(row['trace_status'])}</td>"
        f"<td><code>{html.escape(row['report_json_path'])}</code><br><code>{html.escape(row['report_html_path'])}</code></td>"
        f"<td>{html.escape(row['reviewer_note'])}</td>"
        "</tr>"
        for row in report["matrix_rows"]
    )
    boundary_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['day'])}</td>"
        f"<td><code>{html.escape(json.dumps(row['safety_boundary'], sort_keys=True))}</code></td>"
        "</tr>"
        for row in report["matrix_rows"]
    )
    invariant_rows = "".join(
        "<tr>"
        f"<td>{html.escape(name)}</td>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for name, value in report["safety_invariants"].items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day103 Parser Evidence Matrix / Gap Traceability</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; vertical-align: top; }}
    th {{ background: #eef2f6; text-align: left; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
    .pass {{ color: #116329; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Day103 Parser Evidence Matrix / Gap Traceability</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Reviewer question:</strong> {html.escape(report['reviewer_question'])}</p>
  <p><strong>Scope:</strong> Day103 integrates Day96-Day102 parser evidence only. It does not add parser capability, execution capability, broker handoff, adapter invocation, SSH, live device access, dashboard actions, OpenAI API usage, voice runtime, or external integrations.</p>
  <h2>Summary</h2>
  <p><strong>Total rows:</strong> {summary['total_rows']} | <strong>Days covered:</strong> {summary['total_days_covered']} | <strong>Trace complete:</strong> {summary['trace_complete_count']} | <strong>Review required:</strong> {summary['review_required_count']} | <strong>Known gaps:</strong> {summary['known_gap_count']} | <strong>Boundary blocked:</strong> {summary['blocked_by_safety_boundary_count']}</p>
  <p><strong>Execution counters:</strong> <code>execution_allowed_count={summary['execution_allowed_count']}</code>, <code>adapter_invocation_allowed_count={summary['adapter_invocation_allowed_count']}</code>, <code>broker_handoff_allowed_count={summary['broker_handoff_allowed_count']}</code>, <code>live_access_allowed_count={summary['live_access_allowed_count']}</code>, <code>parser_capability_added_count={summary['parser_capability_added_count']}</code></p>
  <p><strong>Day103 reports:</strong> <code>{html.escape(report['reports']['json'])}</code> and <code>{html.escape(report['reports']['html'])}</code></p>
  <h2>Traceability Matrix</h2>
  <table>
    <thead><tr><th>Day</th><th>Gap</th><th>Fixture / Evidence</th><th>Expected Decision</th><th>Actual Result</th><th>Trace Status</th><th>Reports</th><th>Reviewer Note</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <h2>Safety Boundary</h2>
  <table>
    <thead><tr><th>Day</th><th>Boundary</th></tr></thead>
    <tbody>{boundary_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Value</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )
