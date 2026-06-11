"""Day100 parser phase gate review and readiness decision.

This module is deterministic, local-only, and report-only. It grades the
Day96-Day99 parser evidence into reviewer readiness decisions without opening
broker, executor, adapter, SSH, or live-access paths.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_parser_evidence_coverage_audit import build_parser_evidence_coverage_audit_report


CREATED_AT = "2026-06-11T00:00:00Z"
TASK_NAME = "parser-phase-gate-review"
TITLE = "Parser Phase Gate Review / Readiness Decision"
PHASE = "PARSER_PHASE_GATE_REVIEW"
SCHEMA_VERSION = "day100.parser_phase_gate_review.v1"
SOURCE_KIND = "day100_static_day96_day99_phase_gate_review"
REVIEW_MODE = "readiness_decision_report_only"
REVIEWER_STATUS = "PHASE_GATE_REVIEW_READY"
REPORT_JSON = Path("reports") / "ai" / "day100_parser_phase_gate_review.json"
REPORT_HTML = Path("reports") / "ai" / "day100_parser_phase_gate_review.html"

READINESS_DECISIONS = {
    "ADVANCE_READY",
    "REVIEW_ONLY",
    "UNDER_COVERED",
    "BLOCKED",
}
NEXT_ACTIONS = {
    "ADVANCE_READY": "advance_to_next_design_review_no_execution",
    "REVIEW_ONLY": "keep_as_reviewer_evidence_not_broker_boundary",
    "UNDER_COVERED": "add_static_tests_or_fixtures_before_advancing",
    "BLOCKED": "stop_until_safety_semantic_coverage_or_boundary_issue_is_fixed",
}
REVIEW_ONLY_AREAS = {
    "unsupported_format",
    "unsupported_command_family",
    "empty_output",
    "malformed_input",
    "partial_output",
    "ambiguous_output",
    "parser_error_guarded",
}
ADVANCE_READY_AREAS = {
    "supported_key_value_parse",
    "supported_line_parse",
    "classification_traceability",
}
RUNTIME_DISABLED_FLAGS = (
    "broker_boundary_allowed",
    "execution_allowed",
    "adapter_invocation_allowed",
    "executor_invocation_allowed",
    "ssh_allowed",
    "live_access_allowed",
    "live_read_allowed",
    "live_device_path_allowed",
    "routeros_execution_allowed",
    "command_execution_allowed",
    "dashboard_action_allowed",
    "approval_unlock_supported",
    "openai_api_allowed",
    "voice_runtime_allowed",
)


@dataclass(frozen=True)
class PhaseGateDecisionRow:
    evidence_area: str
    source_days: List[str]
    sample_refs: List[str]
    coverage_status: str
    observed_count: int
    minimum_expected: int
    readiness_decision: str
    decision_reason: str

    def to_record(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "next_action": NEXT_ACTIONS[self.readiness_decision],
            "fixture_origin": SOURCE_KIND,
            "review_mode": REVIEW_MODE,
            "review_data_only": True,
            "broker_boundary_allowed": False,
            "execution_allowed": False,
            "adapter_invocation_allowed": False,
            "executor_invocation_allowed": False,
            "ssh_allowed": False,
            "live_access_allowed": False,
        }


def build_parser_phase_gate_review_report(
    day99_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_report = deepcopy(day99_report) if day99_report is not None else build_parser_evidence_coverage_audit_report()
    decision_rows = build_phase_gate_decision_rows(source_report)
    summary = build_summary(decision_rows, source_report)
    report = {
        "day": 100,
        "day_id": "Day100",
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
            "reviewed_days": ["Day96", "Day97", "Day98", "Day99"],
            "purpose": "Grade parser evidence into phase-gate readiness decisions without granting execution authority.",
            "parser_output_is_authorization": False,
            "broker_boundary_opened": False,
            "executor_opened": False,
        },
        "source_reports": {
            "day96": source_report.get("source_reports", {}).get("day96", {}),
            "day97": source_report.get("source_reports", {}).get("day97", {}),
            "day98": source_report.get("source_reports", {}).get("day98", {}),
            "day99": {
                "task": source_report.get("task"),
                "status": source_report.get("overall_status"),
                "path": "reports/ai/day99_parser_evidence_coverage_audit.json",
            },
        },
        "summary": summary,
        "decision_rows": decision_rows,
        "phase_gate_decision": {
            "final_readiness_decision": summary["final_readiness_decision"],
            "broker_boundary_allowed": False,
            "execution_allowed": False,
            "adapter_invocation_allowed": False,
            "executor_invocation_allowed": False,
            "ssh_allowed": False,
            "live_access_allowed": False,
            "parser_outputs_are_review_data_only": True,
            "decision_note": (
                "Day100 grades parser evidence only. It does not authorize broker entry, "
                "executor use, adapter invocation, SSH, live access, or command execution."
            ),
        },
        "classification_policy": {
            "ADVANCE_READY": "May proceed to the next design review stage, but remains non-executable.",
            "REVIEW_ONLY": "Reviewer evidence only and cannot cross into the broker boundary.",
            "UNDER_COVERED": "Concept may remain, but static tests or fixtures must be added before advancement.",
            "BLOCKED": "Safety, semantic, coverage, or boundary issue must block the parser phase.",
        },
        "safety_invariants": build_safety_invariants(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "no_broker_boundary": True,
        "no_executor": True,
        "no_adapter_invocation": True,
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_access": True,
        "no_live_execution": True,
        "no_routeros_execution": True,
        "no_command_execution": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
    }
    validation_errors = validate_parser_phase_gate_review_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_phase_gate_decision_rows(day99_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    source_summary = day99_report.get("summary", {})
    source_blocked = (
        day99_report.get("overall_status") != "PASS"
        or source_summary.get("source_report_fail_count", 0) != 0
        or source_summary.get("runtime_violation_count", 0) != 0
        or bool(day99_report.get("validation_errors"))
    )
    rows = []
    for coverage_row in day99_report.get("coverage_rows", []):
        decision, reason = classify_coverage_row(coverage_row, source_blocked)
        rows.append(
            PhaseGateDecisionRow(
                evidence_area=coverage_row.get("coverage_area", "unknown"),
                source_days=list(coverage_row.get("source_days", [])),
                sample_refs=list(coverage_row.get("sample_refs", [])),
                coverage_status=coverage_row.get("coverage_status", "UNKNOWN"),
                observed_count=int(coverage_row.get("observed_count", 0)),
                minimum_expected=int(coverage_row.get("minimum_expected", 0)),
                readiness_decision=decision,
                decision_reason=reason,
            ).to_record()
        )
    return rows


def classify_coverage_row(row: Dict[str, Any], source_blocked: bool = False) -> Tuple[str, str]:
    area = row.get("coverage_area", "unknown")
    if source_blocked:
        return "BLOCKED", "A source report, validation, or safety invariant failed before Day100."
    if any(row.get(flag) is not False for flag in (
        "execution_allowed",
        "adapter_path_allowed",
        "broker_path_allowed",
        "ssh_allowed",
        "live_device_path_allowed",
    )):
        return "BLOCKED", "The source row attempted to enable execution, adapter, broker, SSH, or live-device access."
    if row.get("coverage_status") == "UNDER_COVERED":
        return "UNDER_COVERED", "Evidence exists, but the observed static samples are below the Day99 minimum."
    if area in REVIEW_ONLY_AREAS:
        return "REVIEW_ONLY", "The area is useful reviewer evidence but must not enter the broker boundary."
    if area in ADVANCE_READY_AREAS and row.get("coverage_status") == "COVERED":
        return "ADVANCE_READY", "Static parser evidence is covered enough for the next design review stage only."
    return "REVIEW_ONLY", "No execution authority is implied; keep this parser evidence in reviewer-only scope."


def build_summary(rows: List[Dict[str, Any]], day99_report: Dict[str, Any]) -> Dict[str, Any]:
    decisions = [row["readiness_decision"] for row in rows]
    decision_counts = {decision: decisions.count(decision) for decision in sorted(READINESS_DECISIONS)}
    safety_violation_count = sum(
        1
        for row in rows
        if row.get("broker_boundary_allowed") is not False
        or row.get("execution_allowed") is not False
        or row.get("adapter_invocation_allowed") is not False
        or row.get("executor_invocation_allowed") is not False
        or row.get("ssh_allowed") is not False
        or row.get("live_access_allowed") is not False
    )
    source_summary = day99_report.get("summary", {})
    source_report_fail_count = int(source_summary.get("source_report_fail_count", 0))
    source_runtime_violation_count = int(source_summary.get("runtime_violation_count", 0))
    source_validation_error_count = len(day99_report.get("validation_errors", []))
    final_readiness_decision = choose_final_readiness_decision(decisions)
    overall_status = (
        "PASS"
        if rows
        and safety_violation_count == 0
        and source_report_fail_count == 0
        and source_runtime_violation_count == 0
        and source_validation_error_count == 0
        and day99_report.get("overall_status") == "PASS"
        else "FAIL"
    )
    return {
        "total_decision_rows": len(rows),
        "readiness_decision_values": sorted(set(decisions)),
        "decision_counts": decision_counts,
        "advance_ready_count": decision_counts["ADVANCE_READY"],
        "review_only_count": decision_counts["REVIEW_ONLY"],
        "under_covered_count": decision_counts["UNDER_COVERED"],
        "blocked_count": decision_counts["BLOCKED"],
        "final_readiness_decision": final_readiness_decision,
        "source_day99_status": day99_report.get("overall_status"),
        "source_report_fail_count": source_report_fail_count,
        "source_runtime_violation_count": source_runtime_violation_count,
        "source_validation_error_count": source_validation_error_count,
        "safety_violation_count": safety_violation_count,
        "broker_boundary_allowed": False,
        "execution_allowed": False,
        "adapter_invocation_allowed": False,
        "executor_invocation_allowed": False,
        "ssh_allowed": False,
        "live_access_allowed": False,
        "parser_outputs_are_review_data_only": True,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def choose_final_readiness_decision(decisions: List[str]) -> str:
    if "BLOCKED" in decisions:
        return "BLOCKED"
    if "UNDER_COVERED" in decisions:
        return "UNDER_COVERED"
    if decisions and set(decisions).issubset({"ADVANCE_READY", "REVIEW_ONLY"}):
        return "ADVANCE_READY"
    return "REVIEW_ONLY"


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "report_only": True,
        "static_phase_gate_review_only": True,
        "parser_output_is_authorization": False,
        "parser_capability_added": False,
        "broker_opened": False,
        "executor_opened": False,
        **{flag: False for flag in RUNTIME_DISABLED_FLAGS},
    }


def validate_parser_phase_gate_review_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    rows = report.get("decision_rows", [])

    if report.get("day") != 100:
        errors.append("day must be 100.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-phase-gate-review.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    if summary.get("safety_violation_count") != 0:
        errors.append("Day100 decision rows must not enable broker, executor, adapter, SSH, live access, or execution.")
    if summary.get("source_report_fail_count") != 0:
        errors.append("Day96-Day98 source reports must pass before Day100 can grade readiness.")
    if summary.get("source_runtime_violation_count") != 0:
        errors.append("Day99 source runtime violation count must be zero.")
    if summary.get("source_validation_error_count") != 0:
        errors.append("Day99 source validation errors must be zero.")

    for field in (
        "no_broker_boundary",
        "no_executor",
        "no_adapter_invocation",
        "no_real_device_access",
        "no_ssh",
        "no_live_access",
        "no_live_execution",
        "no_routeros_execution",
        "no_command_execution",
        "no_config_json_read",
        "no_openai_api",
        "no_ai_sdk_runtime",
        "no_voice",
        "dashboard_read_only",
    ):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    if report.get("dashboard_action_allowed") is not False:
        errors.append("dashboard_action_allowed must be false.")

    required_row_fields = {
        "evidence_area",
        "source_days",
        "sample_refs",
        "coverage_status",
        "observed_count",
        "minimum_expected",
        "readiness_decision",
        "decision_reason",
        "next_action",
        "fixture_origin",
        "review_mode",
        "review_data_only",
        "broker_boundary_allowed",
        "execution_allowed",
        "adapter_invocation_allowed",
        "executor_invocation_allowed",
        "ssh_allowed",
        "live_access_allowed",
    }
    for row in rows:
        missing = required_row_fields.difference(row)
        if missing:
            errors.append(f"{row.get('evidence_area', '<unknown>')} missing fields: {', '.join(sorted(missing))}.")
        decision = row.get("readiness_decision")
        if decision not in READINESS_DECISIONS:
            errors.append(f"{row.get('evidence_area', '<unknown>')} has invalid readiness_decision.")
        elif row.get("next_action") != NEXT_ACTIONS[decision]:
            errors.append(f"{row.get('evidence_area', '<unknown>')} next_action does not match readiness_decision.")
        if row.get("fixture_origin") != SOURCE_KIND:
            errors.append(f"{row.get('evidence_area', '<unknown>')} must use Day100 source kind.")
        if row.get("review_mode") != REVIEW_MODE:
            errors.append(f"{row.get('evidence_area', '<unknown>')} must use Day100 review mode.")
        if row.get("review_data_only") is not True:
            errors.append(f"{row.get('evidence_area', '<unknown>')} must be review data only.")
        for flag in (
            "broker_boundary_allowed",
            "execution_allowed",
            "adapter_invocation_allowed",
            "executor_invocation_allowed",
            "ssh_allowed",
            "live_access_allowed",
        ):
            if row.get(flag) is not False:
                errors.append(f"{row.get('evidence_area', '<unknown>')} {flag} must be false.")

    invariants = report.get("safety_invariants", {})
    if invariants.get("report_only") is not True:
        errors.append("safety_invariants.report_only must be true.")
    if invariants.get("static_phase_gate_review_only") is not True:
        errors.append("safety_invariants.static_phase_gate_review_only must be true.")
    if invariants.get("parser_output_is_authorization") is not False:
        errors.append("safety_invariants.parser_output_is_authorization must be false.")
    if invariants.get("parser_capability_added") is not False:
        errors.append("safety_invariants.parser_capability_added must be false.")
    if invariants.get("broker_opened") is not False:
        errors.append("safety_invariants.broker_opened must be false.")
    if invariants.get("executor_opened") is not False:
        errors.append("safety_invariants.executor_opened must be false.")
    for flag in RUNTIME_DISABLED_FLAGS:
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    return errors


def write_parser_phase_gate_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_phase_gate_review_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_phase_gate_review_html(safe_report, html_path)
    return json_path, html_path


def write_parser_phase_gate_review_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    decision_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['evidence_area'])}</td>"
        f"<td>{html.escape(', '.join(row['source_days']))}</td>"
        f"<td>{html.escape(str(row['observed_count']))}</td>"
        f"<td>{html.escape(str(row['minimum_expected']))}</td>"
        f"<td>{html.escape(row['coverage_status'])}</td>"
        f"<td>{html.escape(row['readiness_decision'])}</td>"
        f"<td>{html.escape(row['next_action'])}</td>"
        f"<td>{html.escape(row['decision_reason'])}</td>"
        "</tr>"
        for row in report["decision_rows"]
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
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 22px; }}
    th, td {{ border: 1px solid #d6dee9; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f7; }}
    .pass {{ color: #116329; font-weight: bold; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>Day100 Parser Phase Gate Review / Readiness Decision</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Final readiness decision:</strong> <code>{html.escape(summary['final_readiness_decision'])}</code></p>
  <p><strong>Scope:</strong> Day100 grades Day96-Day99 parser evidence only. Parser outputs are review data, not execution authorization. Broker boundary, executor, adapter invocation, SSH, and live access remain disabled.</p>
  <h2>Summary</h2>
  <p><strong>Rows:</strong> {summary['total_decision_rows']} | <strong>Advance ready:</strong> {summary['advance_ready_count']} | <strong>Review only:</strong> {summary['review_only_count']} | <strong>Under-covered:</strong> {summary['under_covered_count']} | <strong>Blocked:</strong> {summary['blocked_count']}</p>
  <p><strong>Safety locks:</strong> <code>broker_boundary_allowed=false</code>, <code>execution_allowed=false</code>, <code>adapter_invocation_allowed=false</code>, <code>ssh_allowed=false</code>, <code>live_access_allowed=false</code></p>
  <h2>Readiness Decisions</h2>
  <table>
    <thead><tr><th>Evidence Area</th><th>Sources</th><th>Observed</th><th>Minimum</th><th>Coverage</th><th>Decision</th><th>Next Action</th><th>Reason</th></tr></thead>
    <tbody>{decision_rows}</tbody>
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
