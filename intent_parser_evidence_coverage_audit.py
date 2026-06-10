"""Day99 parser evidence coverage and sample gap audit.

This module is deterministic, local-only, and report-only. It audits Day96,
Day97, and Day98 parser evidence coverage so Day100 can make a phase-gate
readiness decision without adding parser, adapter, broker, SSH, or live-device
capability.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_parser_classification_matrix import build_parser_classification_matrix
from intent_parser_evidence_quality import build_day97_parser_evidence_quality_report
from intent_readonly_output_parser_prototype import build_day96_parser_report


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "parser-evidence-coverage-audit"
TITLE = "Parser Evidence Coverage / Sample Gap Audit"
PHASE = "COVERAGE_AUDIT_READY"
SCHEMA_VERSION = "day99.parser_evidence_coverage_audit.v1"
SOURCE_KIND = "day99_static_day96_day98_report_audit"
AUDIT_MODE = "report_only_coverage_audit"
REVIEWER_STATUS = "COVERAGE_REVIEW_READY"
REPORT_JSON = Path("reports") / "ai" / "day99_parser_evidence_coverage_audit.json"
REPORT_HTML = Path("reports") / "ai" / "day99_parser_evidence_coverage_audit.html"

COVERAGE_STATUSES = {"COVERED", "UNDER_COVERED"}
READINESS_STATUSES = {"READY_FOR_DAY100", "REVIEW_IN_DAY100"}
REQUIRED_COVERAGE_AREAS = {
    "supported_key_value_parse",
    "supported_line_parse",
    "supported_table_parse",
    "unsupported_format",
    "unsupported_command_family",
    "empty_output",
    "malformed_input",
    "partial_output",
    "ambiguous_output",
    "degraded_duplicate_output",
    "encoding_anomaly",
    "parser_error_guarded",
    "classification_traceability",
}

RUNTIME_DISABLED_FLAGS = (
    "execution_allowed",
    "adapter_path_allowed",
    "broker_path_allowed",
    "ssh_allowed",
    "live_device_path_allowed",
    "routeros_execution_allowed",
    "command_execution_allowed",
    "config_json_read_allowed",
    "dashboard_action_allowed",
    "approval_unlock_supported",
    "openai_api_allowed",
    "voice_runtime_allowed",
)


@dataclass(frozen=True)
class CoverageAuditRow:
    coverage_area: str
    source_days: List[str]
    sample_refs: List[str]
    observed_count: int
    minimum_expected: int
    coverage_status: str
    gap_note: str
    day100_readiness: str

    def to_record(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "fixture_origin": SOURCE_KIND,
            "audit_mode": AUDIT_MODE,
            "report_only": True,
            "execution_allowed": False,
            "adapter_path_allowed": False,
            "broker_path_allowed": False,
            "ssh_allowed": False,
            "live_device_path_allowed": False,
        }


def build_parser_evidence_coverage_audit_report() -> Dict[str, Any]:
    day96_report = build_day96_parser_report()
    day97_report = build_day97_parser_evidence_quality_report()
    day98_report = build_parser_classification_matrix()
    rows = build_coverage_rows(day96_report, day97_report, day98_report)
    summary = build_summary(rows, day96_report, day97_report, day98_report)
    report = {
        "day": 99,
        "day_id": "Day99",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "schema_version": SCHEMA_VERSION,
        "source_kind": SOURCE_KIND,
        "audit_mode": AUDIT_MODE,
        "scope": {
            "report_only": True,
            "audited_days": ["Day96", "Day97", "Day98"],
            "purpose": "Audit parser sample coverage and gaps before Day100 phase-gate review.",
            "parser_capability_added": False,
            "allowed_under_covered_categories": True,
        },
        "source_reports": {
            "day96": {
                "task": day96_report["task"],
                "status": day96_report["overall_status"],
                "path": "reports/lab-summary/day96_readonly_output_parser_prototype.json",
            },
            "day97": {
                "task": day97_report["task"],
                "status": day97_report["overall_status"],
                "path": "reports/ai/day97_parser_evidence_quality_report.json",
            },
            "day98": {
                "task": day98_report["task"],
                "status": day98_report["overall_status"],
                "path": "reports/ai/day98_parser_classification_matrix.json",
            },
        },
        "summary": summary,
        "coverage_rows": rows,
        "sample_gap_register": build_sample_gap_register(rows),
        "phase_gate_readiness": {
            "next_day": "Day100",
            "recommended_name": "Parser Phase Gate Review / Readiness Decision",
            "ready_for_day100_review": summary["ready_for_day100_review"],
            "decision_boundary": "Day99 does not decide GO or expand parser behavior; it hands coverage evidence to Day100.",
            "blocking_gap_count": summary["blocking_gap_count"],
            "allowed_gap_status": "UNDER_COVERED",
        },
        "safety_invariants": build_safety_invariants(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_execution": True,
        "no_adapter_execution": True,
        "no_broker_execution": True,
        "no_routeros_execution": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
    }
    validation_errors = validate_parser_evidence_coverage_audit_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_coverage_rows(
    day96_report: Dict[str, Any],
    day97_report: Dict[str, Any],
    day98_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    day96_cases = day96_report.get("parser_cases", [])
    day97_cases = day97_report.get("scenario_cases", [])
    day98_rows = day98_report.get("matrix_rows", [])

    day96_parsed_cases = [
        case
        for case in day96_cases
        if case.get("parser_result", {}).get("parser_status") == "PARSED"
    ]
    day96_records = [
        record
        for case in day96_parsed_cases
        for record in case.get("parser_result", {}).get("parsed_records", [])
    ]
    day97_by_status = _group_ids(day97_cases, "parser_status")
    day98_by_classification = _group_ids(day98_rows, "parser_classification")

    rows = [
        _row(
            "supported_key_value_parse",
            ["Day96", "Day98"],
            _case_refs(
                day96_parsed_cases,
                lambda case: any(
                    record.get("record_type") == "key_value"
                    for record in case.get("parser_result", {}).get("parsed_records", [])
                ),
            )
            + day98_by_classification.get("parsed_supported", [])[:1],
            1,
            "READY_FOR_DAY100",
            "Key-value supported evidence exists, but Day100 should decide whether the sample family is broad enough.",
        ),
        _row(
            "supported_line_parse",
            ["Day96", "Day98"],
            _case_refs(
                day96_parsed_cases,
                lambda case: any(
                    record.get("record_type") == "text_line"
                    for record in case.get("parser_result", {}).get("parsed_records", [])
                ),
            )
            + day98_by_classification.get("parsed_supported", [])[1:2],
            1,
            "READY_FOR_DAY100",
            "Line-oriented supported evidence exists.",
        ),
        _row(
            "supported_table_parse",
            ["Day96"],
            [
                f"Day96:{record.get('record_type')}"
                for record in day96_records
                if record.get("record_type") == "table_row"
            ][:1],
            2,
            "REVIEW_IN_DAY100",
            "Table parsing has only prototype-level coverage and needs a Day100 readiness decision before expansion.",
        ),
        _row(
            "unsupported_format",
            ["Day96", "Day98"],
            _case_refs(
                day96_cases,
                lambda case: case.get("parser_result", {}).get("parser_status") == "UNSUPPORTED",
            )
            + day98_by_classification.get("unsupported_format", []),
            1,
            "READY_FOR_DAY100",
            "Unsupported non-text output is represented without fallback.",
        ),
        _row(
            "unsupported_command_family",
            ["Day97", "Day98"],
            day97_by_status.get("UNSUPPORTED_OUTPUT", [])
            + day98_by_classification.get("unsupported_command_family", []),
            1,
            "READY_FOR_DAY100",
            "Out-of-scope command-family evidence is represented and remains blocked.",
        ),
        _row(
            "empty_output",
            ["Day97", "Day98"],
            day97_by_status.get("EMPTY_OUTPUT", []) + day98_by_classification.get("empty_output", []),
            2,
            "READY_FOR_DAY100",
            "Empty and whitespace-only evidence are represented.",
        ),
        _row(
            "malformed_input",
            ["Day96", "Day97"],
            _case_refs(
                day96_cases,
                lambda case: case.get("parser_result", {}).get("parser_status") == "REVIEW_NEEDED",
            )
            + day97_by_status.get("MALFORMED_INPUT", []),
            3,
            "READY_FOR_DAY100",
            "Malformed, missing, and review-needed evidence cases are represented.",
        ),
        _row(
            "partial_output",
            ["Day97", "Day98"],
            day97_by_status.get("INCOMPLETE_OUTPUT", [])
            + day98_by_classification.get("parsed_partial", []),
            2,
            "READY_FOR_DAY100",
            "Partial evidence has enough samples for Day100 review.",
        ),
        _row(
            "ambiguous_output",
            ["Day97", "Day98"],
            day97_by_status.get("AMBIGUOUS_OUTPUT", [])
            + day98_by_classification.get("ambiguous_output", []),
            2,
            "READY_FOR_DAY100",
            "Ambiguous output and mixed sections are represented.",
        ),
        _row(
            "degraded_duplicate_output",
            ["Day97"],
            _case_refs(day97_cases, lambda case: "duplicate" in case.get("case_id", "")),
            2,
            "REVIEW_IN_DAY100",
            "Duplicate evidence is present once; Day100 should decide whether more degraded samples are required.",
        ),
        _row(
            "encoding_anomaly",
            ["Day97"],
            _case_refs(day97_cases, lambda case: "encoding" in case.get("case_id", "")),
            2,
            "REVIEW_IN_DAY100",
            "Encoding anomaly evidence is present once; keep as an explicit sample gap.",
        ),
        _row(
            "parser_error_guarded",
            ["Day98"],
            day98_by_classification.get("parser_error_guarded", []),
            1,
            "READY_FOR_DAY100",
            "Guarded parser-error traceability is represented.",
        ),
        _row(
            "classification_traceability",
            ["Day98"],
            [row.get("case_id", "") for row in day98_rows],
            7,
            "READY_FOR_DAY100",
            "All required Day98 classification categories are mapped to reviewer actions and safety invariants.",
        ),
    ]
    return rows


def build_summary(
    rows: List[Dict[str, Any]],
    day96_report: Dict[str, Any],
    day97_report: Dict[str, Any],
    day98_report: Dict[str, Any],
) -> Dict[str, Any]:
    coverage_statuses = [row["coverage_status"] for row in rows]
    required_areas_present = REQUIRED_COVERAGE_AREAS.issubset(
        {row["coverage_area"] for row in rows}
    )
    runtime_violation_count = sum(
        1
        for row in rows
        if row.get("execution_allowed") is not False
        or row.get("adapter_path_allowed") is not False
        or row.get("broker_path_allowed") is not False
        or row.get("ssh_allowed") is not False
        or row.get("live_device_path_allowed") is not False
    )
    source_report_fail_count = sum(
        1
        for report in (day96_report, day97_report, day98_report)
        if report.get("overall_status") != "PASS"
    )
    under_covered_count = coverage_statuses.count("UNDER_COVERED")
    blocking_gap_count = 0
    ready_for_day100_review = (
        required_areas_present
        and source_report_fail_count == 0
        and runtime_violation_count == 0
        and all(status in COVERAGE_STATUSES for status in coverage_statuses)
    )
    overall_status = "PASS" if ready_for_day100_review and blocking_gap_count == 0 else "FAIL"
    return {
        "total_coverage_rows": len(rows),
        "required_coverage_areas_present": required_areas_present,
        "coverage_status_values": sorted(set(coverage_statuses)),
        "covered_count": coverage_statuses.count("COVERED"),
        "under_covered_count": under_covered_count,
        "under_covered_allowed": True,
        "blocking_gap_count": blocking_gap_count,
        "source_report_fail_count": source_report_fail_count,
        "runtime_violation_count": runtime_violation_count,
        "ready_for_day100_review": ready_for_day100_review,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def build_sample_gap_register(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    gaps = []
    for row in rows:
        if row["coverage_status"] == "UNDER_COVERED":
            gaps.append(
                {
                    "coverage_area": row["coverage_area"],
                    "gap_status": "UNDER_COVERED",
                    "observed_count": row["observed_count"],
                    "minimum_expected": row["minimum_expected"],
                    "gap_note": row["gap_note"],
                    "blocking_day99": False,
                    "day100_decision_needed": True,
                }
            )
    return gaps


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "report_only": True,
        "static_report_audit_only": True,
        "parser_capability_added": False,
        "phase_gate_decision_made": False,
        **{flag: False for flag in RUNTIME_DISABLED_FLAGS},
    }


def validate_parser_evidence_coverage_audit_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    rows = report.get("coverage_rows", [])

    if report.get("day") != 99:
        errors.append("day must be 99.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-evidence-coverage-audit.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    if summary.get("required_coverage_areas_present") is not True:
        errors.append("All required Day99 coverage areas must be represented.")
    if summary.get("source_report_fail_count") != 0:
        errors.append("Day96, Day97, and Day98 source reports must pass.")
    if summary.get("runtime_violation_count") != 0:
        errors.append("Coverage rows must not enable execution, adapter, broker, SSH, or live-device paths.")
    if summary.get("blocking_gap_count") != 0:
        errors.append("Day99 may record under-covered categories but must not create blocking gaps.")
    if summary.get("under_covered_allowed") is not True:
        errors.append("UNDER_COVERED sample gaps must be allowed for Day99.")

    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_live_execution",
        "no_adapter_execution",
        "no_broker_execution",
        "no_routeros_execution",
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
        "coverage_area",
        "source_days",
        "sample_refs",
        "observed_count",
        "minimum_expected",
        "coverage_status",
        "gap_note",
        "day100_readiness",
        "fixture_origin",
        "audit_mode",
        "report_only",
        "execution_allowed",
        "adapter_path_allowed",
        "broker_path_allowed",
        "ssh_allowed",
        "live_device_path_allowed",
    }
    for row in rows:
        missing = required_row_fields.difference(row)
        if missing:
            errors.append(f"{row.get('coverage_area', '<unknown>')} missing fields: {', '.join(sorted(missing))}.")
        if row.get("coverage_area") not in REQUIRED_COVERAGE_AREAS:
            errors.append(f"{row.get('coverage_area')} is not a required coverage area.")
        if row.get("coverage_status") not in COVERAGE_STATUSES:
            errors.append(f"{row.get('coverage_area')} has invalid coverage_status.")
        if row.get("day100_readiness") not in READINESS_STATUSES:
            errors.append(f"{row.get('coverage_area')} has invalid day100_readiness.")
        if row.get("fixture_origin") != SOURCE_KIND:
            errors.append(f"{row.get('coverage_area')} must use Day99 report audit source kind.")
        if row.get("audit_mode") != AUDIT_MODE:
            errors.append(f"{row.get('coverage_area')} must use Day99 audit mode.")
        if row.get("report_only") is not True:
            errors.append(f"{row.get('coverage_area')} must be report-only.")
        if row.get("coverage_status") == "UNDER_COVERED" and not row.get("gap_note"):
            errors.append(f"{row.get('coverage_area')} under-covered rows need a gap note.")
        for flag in (
            "execution_allowed",
            "adapter_path_allowed",
            "broker_path_allowed",
            "ssh_allowed",
            "live_device_path_allowed",
        ):
            if row.get(flag) is not False:
                errors.append(f"{row.get('coverage_area')} {flag} must be false.")

    invariants = report.get("safety_invariants", {})
    if invariants.get("report_only") is not True:
        errors.append("safety_invariants.report_only must be true.")
    if invariants.get("static_report_audit_only") is not True:
        errors.append("safety_invariants.static_report_audit_only must be true.")
    if invariants.get("parser_capability_added") is not False:
        errors.append("safety_invariants.parser_capability_added must be false.")
    if invariants.get("phase_gate_decision_made") is not False:
        errors.append("safety_invariants.phase_gate_decision_made must be false.")
    for flag in RUNTIME_DISABLED_FLAGS:
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    return errors


def write_parser_evidence_coverage_audit_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_evidence_coverage_audit_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_evidence_coverage_audit_html(safe_report, html_path)
    return json_path, html_path


def write_parser_evidence_coverage_audit_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    coverage_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['coverage_area'])}</td>"
        f"<td>{html.escape(', '.join(row['source_days']))}</td>"
        f"<td>{html.escape(str(row['observed_count']))}</td>"
        f"<td>{html.escape(str(row['minimum_expected']))}</td>"
        f"<td>{html.escape(row['coverage_status'])}</td>"
        f"<td>{html.escape(row['day100_readiness'])}</td>"
        f"<td>{html.escape(row['gap_note'])}</td>"
        f"<td><code>{html.escape(', '.join(row['sample_refs'][:6]))}</code></td>"
        "</tr>"
        for row in report["coverage_rows"]
    )
    gap_rows = "".join(
        "<tr>"
        f"<td>{html.escape(gap['coverage_area'])}</td>"
        f"<td>{html.escape(gap['gap_status'])}</td>"
        f"<td>{html.escape(str(gap['observed_count']))}</td>"
        f"<td>{html.escape(str(gap['minimum_expected']))}</td>"
        f"<td>{html.escape(json.dumps(gap['blocking_day99']))}</td>"
        f"<td>{html.escape(gap['gap_note'])}</td>"
        "</tr>"
        for gap in report["sample_gap_register"]
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
  <h1>Day99 Parser Evidence Coverage / Sample Gap Audit</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Scope:</strong> report-only coverage audit across Day96, Day97, and Day98. UNDER_COVERED categories are allowed for Day99 and become Day100 review inputs. This audit does not add parser capability, execute commands, contact devices, use SSH, run adapters, run brokers, read configuration, or add dashboard actions.</p>
  <h2>Summary</h2>
  <p><strong>Total coverage rows:</strong> {summary['total_coverage_rows']} | <strong>Covered:</strong> {summary['covered_count']} | <strong>Under-covered:</strong> {summary['under_covered_count']} | <strong>Blocking gaps:</strong> {summary['blocking_gap_count']}</p>
  <p><strong>Ready for Day100 review:</strong> <code>{html.escape(json.dumps(summary['ready_for_day100_review']))}</code></p>
  <h2>Coverage Audit</h2>
  <table>
    <thead><tr><th>Coverage Area</th><th>Sources</th><th>Observed</th><th>Minimum</th><th>Status</th><th>Day100 Readiness</th><th>Gap Note</th><th>Sample Refs</th></tr></thead>
    <tbody>{coverage_rows}</tbody>
  </table>
  <h2>Sample Gap Audit</h2>
  <table>
    <thead><tr><th>Coverage Area</th><th>Gap Status</th><th>Observed</th><th>Minimum</th><th>Blocking Day99</th><th>Gap Note</th></tr></thead>
    <tbody>{gap_rows}</tbody>
  </table>
  <h2>Phase Gate Readiness</h2>
  <p>Next: <code>Day100 - Parser Phase Gate Review / Readiness Decision</code>. Day99 hands off coverage evidence only; it does not make a GO decision.</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def _row(
    coverage_area: str,
    source_days: List[str],
    sample_refs: List[str],
    minimum_expected: int,
    day100_readiness: str,
    gap_note: str,
) -> Dict[str, Any]:
    observed_count = len(sample_refs)
    coverage_status = "COVERED" if observed_count >= minimum_expected else "UNDER_COVERED"
    return CoverageAuditRow(
        coverage_area=coverage_area,
        source_days=source_days,
        sample_refs=sample_refs,
        observed_count=observed_count,
        minimum_expected=minimum_expected,
        coverage_status=coverage_status,
        gap_note=gap_note,
        day100_readiness=day100_readiness,
    ).to_record()


def _case_refs(cases: List[Dict[str, Any]], predicate: Any) -> List[str]:
    return [case["case_id"] for case in cases if predicate(case)]


def _group_ids(records: List[Dict[str, Any]], field: str) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for record in records:
        grouped.setdefault(record.get(field, "UNKNOWN"), []).append(record.get("case_id", "UNKNOWN"))
    return grouped
