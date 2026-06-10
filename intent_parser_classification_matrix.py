"""Day98 parser classification matrix.

This module is deterministic, static-fixture-only, and report-only. It connects
Day96 parser prototype outcomes with Day97 unsupported-output hardening so a
reviewer can audit input sample -> classification -> reviewer action -> safety.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "parser-classification-matrix"
TITLE = "Parser Classification Matrix"
PHASE = "TRACEABILITY_HARDENED"
SCHEMA_VERSION = "day98.parser_classification_matrix.v1"
SOURCE_KIND = "day98_static_parser_traceability_sample"
PARSER_MODE = "classification_matrix_report_only"
REVIEWER_STATUS = "TRACEABILITY_READY"
REPORT_JSON = Path("reports") / "ai" / "day98_parser_classification_matrix.json"
REPORT_HTML = Path("reports") / "ai" / "day98_parser_classification_matrix.html"

CLASSIFICATION_ACTIONS = {
    "parsed_supported": "review_parsed_fields",
    "parsed_partial": "review_missing_fields",
    "unsupported_format": "reject_and_attach_sample",
    "unsupported_command_family": "reject_out_of_scope",
    "empty_output": "request_new_sample",
    "ambiguous_output": "manual_review_required",
    "parser_error_guarded": "reject_until_parser_fixed",
}

SUPPORTED_CLASSIFICATIONS = {"parsed_supported"}
CLASSIFICATIONS_REQUIRING_REASON = set(CLASSIFICATION_ACTIONS) - SUPPORTED_CLASSIFICATIONS
TRACE_STATUSES = {"TRACE_COMPLETE", "TRACE_REVIEW_REQUIRED"}
SAFETY_INVARIANTS = {
    "parser_output_is_not_executable",
    "unsupported_output_is_blocked",
    "unknown_output_requires_review",
    "parser_error_fails_closed",
    "reviewer_action_required_before_any_future_runtime_use",
}


@dataclass(frozen=True)
class ParserClassificationSample:
    case_id: str
    source_day: str
    input_label: str
    raw_output_sample: str
    parser_classification: str
    parsed_fields: Dict[str, Any]
    unsupported_reason: Optional[str]
    safety_invariant: str
    evidence_required: str
    trace_status: str

    def to_matrix_row(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "reviewer_action": CLASSIFICATION_ACTIONS[self.parser_classification],
            "executable_allowed": False,
            "fixture_origin": SOURCE_KIND,
            "parser_mode": PARSER_MODE,
            "no_live_command_execution": True,
            "no_external_runtime_state": True,
        }


def build_parser_classification_samples() -> List[Dict[str, Any]]:
    """Return static Day96/Day97 parser traceability samples."""
    samples = [
        ParserClassificationSample(
            case_id="D98-C01-day96-supported-identity",
            source_day="Day96",
            input_label="Day96 key-value identity simulated output",
            raw_output_sample="name: lab-router-simulated",
            parser_classification="parsed_supported",
            parsed_fields={"name": "lab-router-simulated"},
            unsupported_reason=None,
            safety_invariant="parser_output_is_not_executable",
            evidence_required="parsed_fields_and_source_fixture",
            trace_status="TRACE_COMPLETE",
        ),
        ParserClassificationSample(
            case_id="D98-C02-day96-supported-interface-lines",
            source_day="Day96",
            input_label="Day96 line-oriented interface simulated output",
            raw_output_sample="ether1 running\nether2 disabled\nbridge1 running",
            parser_classification="parsed_supported",
            parsed_fields={
                "records": [
                    {"interface": "ether1", "state": "running"},
                    {"interface": "ether2", "state": "disabled"},
                    {"interface": "bridge1", "state": "running"},
                ]
            },
            unsupported_reason=None,
            safety_invariant="parser_output_is_not_executable",
            evidence_required="parsed_fields_and_source_fixture",
            trace_status="TRACE_COMPLETE",
        ),
        ParserClassificationSample(
            case_id="D98-C03-day97-partial-headers-only",
            source_day="Day97",
            input_label="Header-only table output",
            raw_output_sample="NAME  STATE  COMMENT",
            parser_classification="parsed_partial",
            parsed_fields={"headers": ["NAME", "STATE", "COMMENT"], "rows": []},
            unsupported_reason="Table-like output has headers but no data rows.",
            safety_invariant="unknown_output_requires_review",
            evidence_required="raw_sample_and_missing_field_list",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
        ParserClassificationSample(
            case_id="D98-C04-day96-unsupported-type-format",
            source_day="Day96",
            input_label="Non-text simulated output type",
            raw_output_sample='["not", "text"]',
            parser_classification="unsupported_format",
            parsed_fields={},
            unsupported_reason="Parser accepts text samples only; structured list output is unsupported.",
            safety_invariant="unsupported_output_is_blocked",
            evidence_required="raw_sample_and_unsupported_reason",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
        ParserClassificationSample(
            case_id="D98-C05-day97-unsupported-command-family",
            source_day="Day97",
            input_label="Out-of-scope BGP neighbor output",
            raw_output_sample="peer address state\n198.51.100.1 established",
            parser_classification="unsupported_command_family",
            parsed_fields={},
            unsupported_reason="Command family is outside the reviewed Day96 parser surface.",
            safety_invariant="unsupported_output_is_blocked",
            evidence_required="raw_sample_command_family_and_rejection_note",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
        ParserClassificationSample(
            case_id="D98-C06-day97-empty-output",
            source_day="Day97",
            input_label="Empty output",
            raw_output_sample="",
            parser_classification="empty_output",
            parsed_fields={},
            unsupported_reason="Raw output is empty; parser must not infer device truth.",
            safety_invariant="unknown_output_requires_review",
            evidence_required="empty_sample_marker_and_fixture_origin",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
        ParserClassificationSample(
            case_id="D98-C07-day97-ambiguous-mixed-sections",
            source_day="Day97",
            input_label="Mixed supported identity and unsupported routing sections",
            raw_output_sample="name: lab-router-simulated\n/routing/bgp/peer print\npeer1 established",
            parser_classification="ambiguous_output",
            parsed_fields={"name": "lab-router-simulated"},
            unsupported_reason="Supported identity evidence is mixed with unsupported routing output.",
            safety_invariant="unknown_output_requires_review",
            evidence_required="raw_sample_parsed_subset_and_ambiguity_reason",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
        ParserClassificationSample(
            case_id="D98-C08-day97-parser-error-guarded",
            source_day="Day97",
            input_label="Malformed normalized adapter result",
            raw_output_sample="name: malformed-fixture",
            parser_classification="parser_error_guarded",
            parsed_fields={},
            unsupported_reason="Normalized result envelope is missing required parser schema fields.",
            safety_invariant="parser_error_fails_closed",
            evidence_required="raw_sample_schema_error_and_guarded_status",
            trace_status="TRACE_REVIEW_REQUIRED",
        ),
    ]
    return [sample.to_matrix_row() for sample in samples]


def build_parser_classification_matrix() -> Dict[str, Any]:
    rows = build_parser_classification_samples()
    summary = build_summary(rows)
    report = {
        "day": 98,
        "day_id": "Day98",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "reviewer_status": summary["reviewer_status"],
        "schema_version": SCHEMA_VERSION,
        "source_kind": SOURCE_KIND,
        "parser_mode": PARSER_MODE,
        "evidence_chain": {
            "from": "input sample",
            "through": [
                "parser classification",
                "parsed fields or unsupported reason",
                "reviewer action",
            ],
            "to": "safety invariant",
            "source_days": ["Day96", "Day97"],
        },
        "summary": summary,
        "matrix_rows": rows,
        "safety_invariants": build_safety_invariants(),
        "day96_context": {
            "task": "readonly-output-parser-prototype",
            "report_json": "reports/lab-summary/day96_readonly_output_parser_prototype.json",
            "relationship": "Day96 provides the parser-only supported and boundary parser outcomes.",
        },
        "day97_context": {
            "task": "parser-evidence-quality",
            "report_json": "reports/ai/day97_parser_evidence_quality_report.json",
            "relationship": "Day97 provides unsupported, ambiguous, empty, partial, and guarded error cases.",
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "no_real_device_access": True,
        "no_ssh": True,
        "no_live_execution": True,
        "no_routeros_execution": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
    }
    validation_errors = validate_parser_classification_matrix(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    classifications = [row["parser_classification"] for row in rows]
    trace_statuses = [row["trace_status"] for row in rows]
    unsupported_reason_count = sum(1 for row in rows if row.get("unsupported_reason"))
    reason_required_count = sum(
        1
        for row in rows
        if row["parser_classification"] in CLASSIFICATIONS_REQUIRING_REASON
    )
    executable_allowed_count = sum(1 for row in rows if row.get("executable_allowed") is not False)
    reviewer_action_missing_count = sum(1 for row in rows if not row.get("reviewer_action"))
    safety_invariant_missing_count = sum(1 for row in rows if not row.get("safety_invariant"))
    required_categories_present = set(CLASSIFICATION_ACTIONS).issubset(set(classifications))
    all_trace_statuses_valid = set(trace_statuses).issubset(TRACE_STATUSES)
    all_inputs_static = all(row.get("fixture_origin") == SOURCE_KIND for row in rows)
    unsupported_reasons_complete = unsupported_reason_count >= reason_required_count
    overall_status = (
        "PASS"
        if len(rows) >= len(CLASSIFICATION_ACTIONS)
        and required_categories_present
        and all_trace_statuses_valid
        and unsupported_reasons_complete
        and executable_allowed_count == 0
        and reviewer_action_missing_count == 0
        and safety_invariant_missing_count == 0
        and all_inputs_static
        else "FAIL"
    )
    return {
        "total_rows": len(rows),
        "classification_values": sorted(set(classifications)),
        "required_categories_present": required_categories_present,
        "trace_status_values": sorted(set(trace_statuses)),
        "all_trace_statuses_valid": all_trace_statuses_valid,
        "trace_complete_count": trace_statuses.count("TRACE_COMPLETE"),
        "trace_review_required_count": trace_statuses.count("TRACE_REVIEW_REQUIRED"),
        "unsupported_reason_count": unsupported_reason_count,
        "reason_required_count": reason_required_count,
        "unsupported_reasons_complete": unsupported_reasons_complete,
        "reviewer_action_missing_count": reviewer_action_missing_count,
        "safety_invariant_missing_count": safety_invariant_missing_count,
        "executable_allowed_count": executable_allowed_count,
        "all_inputs_static": all_inputs_static,
        "external_runtime_dependency_count": sum(
            1 for row in rows if row.get("no_external_runtime_state") is not True
        ),
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def build_safety_invariants() -> Dict[str, Any]:
    return {
        "parser_output_is_not_executable": True,
        "unsupported_output_is_blocked": True,
        "unknown_output_requires_review": True,
        "parser_error_fails_closed": True,
        "reviewer_action_required_before_any_future_runtime_use": True,
        "executable_allowed": False,
        "live_read_allowed": False,
        "ssh_allowed": False,
        "routeros_execution_allowed": False,
        "device_contact_allowed": False,
        "command_execution_allowed": False,
        "approval_unlock_supported": False,
        "dashboard_action_allowed": False,
        "external_runtime_state_required": False,
    }


def validate_parser_classification_matrix(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    rows = report.get("matrix_rows", [])

    if report.get("day") != 98:
        errors.append("day must be 98.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-classification-matrix.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    if summary.get("required_categories_present") is not True:
        errors.append("All Day98 parser classification categories must be represented.")
    if summary.get("executable_allowed_count") != 0:
        errors.append("No matrix row may allow execution.")
    if summary.get("external_runtime_dependency_count") != 0:
        errors.append("No matrix row may depend on external runtime state.")
    if summary.get("unsupported_reasons_complete") is not True:
        errors.append("Unsupported, ambiguous, partial, empty, and guarded rows need reasons.")

    for field in (
        "no_real_device_access",
        "no_ssh",
        "no_live_execution",
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
        "case_id",
        "source_day",
        "input_label",
        "raw_output_sample",
        "parser_classification",
        "parsed_fields",
        "unsupported_reason",
        "reviewer_action",
        "safety_invariant",
        "executable_allowed",
        "evidence_required",
        "trace_status",
    }
    for row in rows:
        missing = required_row_fields.difference(row)
        if missing:
            errors.append(f"{row.get('case_id', '<unknown>')} missing fields: {', '.join(sorted(missing))}.")
        case_id = row.get("case_id", "<unknown>")
        classification = row.get("parser_classification")
        if row.get("source_day") not in {"Day96", "Day97"}:
            errors.append(f"{case_id} source_day must be Day96 or Day97.")
        if classification not in CLASSIFICATION_ACTIONS:
            errors.append(f"{case_id} has unsupported parser_classification.")
        elif row.get("reviewer_action") != CLASSIFICATION_ACTIONS[classification]:
            errors.append(f"{case_id} reviewer_action does not match classification.")
        if classification in CLASSIFICATIONS_REQUIRING_REASON and not row.get("unsupported_reason"):
            errors.append(f"{case_id} must include unsupported_reason.")
        if classification in SUPPORTED_CLASSIFICATIONS and row.get("unsupported_reason") is not None:
            errors.append(f"{case_id} supported rows must use unsupported_reason None.")
        if not isinstance(row.get("parsed_fields"), dict):
            errors.append(f"{case_id} parsed_fields must be an object.")
        if not row.get("reviewer_action"):
            errors.append(f"{case_id} must include reviewer_action.")
        if row.get("safety_invariant") not in SAFETY_INVARIANTS:
            errors.append(f"{case_id} has an unknown safety_invariant.")
        if row.get("executable_allowed") is not False:
            errors.append(f"{case_id} executable_allowed must be false.")
        if not row.get("evidence_required"):
            errors.append(f"{case_id} must include evidence_required.")
        if row.get("trace_status") not in TRACE_STATUSES:
            errors.append(f"{case_id} has invalid trace_status.")
        if row.get("fixture_origin") != SOURCE_KIND:
            errors.append(f"{case_id} must be a Day98 static sample.")
        if row.get("no_live_command_execution") is not True:
            errors.append(f"{case_id} must declare no_live_command_execution true.")
        if row.get("no_external_runtime_state") is not True:
            errors.append(f"{case_id} must declare no_external_runtime_state true.")

    invariants = report.get("safety_invariants", {})
    for invariant in SAFETY_INVARIANTS:
        if invariants.get(invariant) is not True:
            errors.append(f"safety_invariants.{invariant} must be true.")
    for flag in (
        "executable_allowed",
        "live_read_allowed",
        "ssh_allowed",
        "routeros_execution_allowed",
        "device_contact_allowed",
        "command_execution_allowed",
        "approval_unlock_supported",
        "dashboard_action_allowed",
        "external_runtime_state_required",
    ):
        if invariants.get(flag) is not False:
            errors.append(f"safety_invariants.{flag} must be false.")
    return errors


def write_parser_classification_matrix_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_parser_classification_matrix()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_parser_classification_matrix_html(safe_report, html_path)
    return json_path, html_path


def write_parser_classification_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    matrix_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['case_id'])}</td>"
        f"<td>{html.escape(row['source_day'])}</td>"
        f"<td>{html.escape(row['input_label'])}</td>"
        f"<td><code>{html.escape(_preview(row['raw_output_sample']))}</code></td>"
        f"<td>{html.escape(row['parser_classification'])}</td>"
        f"<td><code>{html.escape(json.dumps(row['parsed_fields'], sort_keys=True))}</code></td>"
        f"<td>{html.escape(row['unsupported_reason'] or '')}</td>"
        f"<td>{html.escape(row['reviewer_action'])}</td>"
        f"<td>{html.escape(row['safety_invariant'])}</td>"
        f"<td>{html.escape(json.dumps(row['executable_allowed']))}</td>"
        f"<td>{html.escape(row['evidence_required'])}</td>"
        f"<td>{html.escape(row['trace_status'])}</td>"
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
  <h1>Day98 Parser Classification Matrix</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Scope:</strong> static Day96/Day97 parser samples only. The matrix connects input sample to parser classification, parsed fields or unsupported reason, reviewer action, and safety invariant. It does not execute, unlock, contact devices, read local configuration, or call external services.</p>
  <h2>Summary</h2>
  <p><strong>Total rows:</strong> {summary['total_rows']} | <strong>Trace complete:</strong> {summary['trace_complete_count']} | <strong>Review required:</strong> {summary['trace_review_required_count']} | <strong>Executable allowed count:</strong> {summary['executable_allowed_count']}</p>
  <p><strong>Classifications:</strong> <code>{html.escape(', '.join(summary['classification_values']))}</code></p>
  <h2>Traceability Matrix</h2>
  <table>
    <thead><tr><th>Case</th><th>Source</th><th>Input</th><th>Sample</th><th>Classification</th><th>Parsed Fields</th><th>Unsupported Reason</th><th>Reviewer Action</th><th>Safety Invariant</th><th>Executable</th><th>Evidence Required</th><th>Trace</th></tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Value</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
  <h2>Reviewer Evidence Chain</h2>
  <p><code>input sample -&gt; parser classification -&gt; parsed fields / unsupported reason -&gt; reviewer action -&gt; safety invariant</code></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def _preview(raw_output_sample: str) -> str:
    compact = " ".join(raw_output_sample.split())
    return compact[:140] if compact else "<empty>"
