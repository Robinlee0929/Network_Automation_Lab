"""Day97 parser evidence quality hardening.

This module is deterministic, local-only, and parser-only. It defines static
fake output cases that exercise unsupported, incomplete, malformed, ambiguous,
and degraded parser evidence after the Day96 prototype.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "parser-evidence-quality"
TITLE = "Parser Evidence Quality"
PHASE = "HARDENED"
SCHEMA_VERSION = "day97.parser_evidence_quality.v1"
SOURCE_KIND = "day97_static_fake_parser_case"
PARSER_MODE = "parser_only_evidence_quality"
REVIEWER_STATUS = "HARDENED"
REPORT_JSON = Path("reports") / "ai" / "day97_parser_evidence_quality_report.json"
REPORT_HTML = Path("reports") / "ai" / "day97_parser_evidence_quality_report.html"

SAFETY_FLAG_NAMES = (
    "live_read_allowed",
    "ssh_allowed",
    "write_allowed",
    "command_execution_allowed",
    "raw_command_allowed",
    "device_contact_allowed",
    "approval_unlock_supported",
    "mapped_task_execution_allowed",
)

PARSER_STATUSES = {
    "PARSED",
    "UNSUPPORTED_OUTPUT",
    "INCOMPLETE_OUTPUT",
    "MALFORMED_INPUT",
    "EMPTY_OUTPUT",
    "AMBIGUOUS_OUTPUT",
}

EVIDENCE_QUALITY_VALUES = {"HIGH", "MEDIUM", "LOW", "NOT_APPLICABLE"}


@dataclass(frozen=True)
class ParserEvidenceCase:
    case_id: str
    case_name: str
    input_source: str
    command_family: str
    raw_output: Optional[str]
    parser_status: str
    unsupported_reason: str
    evidence_quality: str
    reviewer_action: str
    parser_supported: bool = False

    def to_record(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "fixture_origin": SOURCE_KIND,
            "is_static_fake_case": True,
            "raw_output_present": isinstance(self.raw_output, str) and bool(self.raw_output),
            "raw_output_preview": _preview_raw_output(self.raw_output),
            "failed_execution_classification": False,
            "execution_classification": "NOT_FAILED_EXECUTION",
            "safety_flags": build_safety_flags(),
        }


def build_day97_parser_evidence_cases() -> List[Dict[str, Any]]:
    """Return static fake parser evidence cases for unsupported output hardening."""
    cases = [
        ParserEvidenceCase(
            case_id="D97-C01-empty-output",
            case_name="Empty output",
            input_source="day97_static_fake_output",
            command_family="readonly_identity",
            raw_output="",
            parser_status="EMPTY_OUTPUT",
            unsupported_reason="Raw output is empty; parser must not infer device truth.",
            evidence_quality="NOT_APPLICABLE",
            reviewer_action="Confirm the upstream fake fixture is intentionally empty.",
        ),
        ParserEvidenceCase(
            case_id="D97-C02-whitespace-only-output",
            case_name="Whitespace-only output",
            input_source="day97_static_fake_output",
            command_family="readonly_interfaces",
            raw_output=" \n\t \n",
            parser_status="EMPTY_OUTPUT",
            unsupported_reason="Raw output contains only whitespace and has no evidence body.",
            evidence_quality="NOT_APPLICABLE",
            reviewer_action="Treat as no parser evidence; do not retry through live transport.",
        ),
        ParserEvidenceCase(
            case_id="D97-C03-unsupported-command-family",
            case_name="Unsupported command family",
            input_source="day97_static_fake_output",
            command_family="readonly_bgp_neighbors",
            raw_output="peer address state\n198.51.100.1 established",
            parser_status="UNSUPPORTED_OUTPUT",
            unsupported_reason="Command family is outside the Day96 supported parser surface.",
            evidence_quality="LOW",
            reviewer_action="Mark unsupported until a reviewed parser contract exists.",
        ),
        ParserEvidenceCase(
            case_id="D97-C04-unknown-adapter-source",
            case_name="Unknown adapter source",
            input_source="unknown_adapter_source",
            command_family="readonly_identity",
            raw_output="name: lab-router-simulated",
            parser_status="MALFORMED_INPUT",
            unsupported_reason="Input source is not a reviewed fake adapter or Day97 static fixture source.",
            evidence_quality="LOW",
            reviewer_action="Reject source provenance and request a normalized fake fixture.",
        ),
        ParserEvidenceCase(
            case_id="D97-C05-malformed-normalized-adapter-result",
            case_name="Malformed normalized adapter result",
            input_source="malformed_normalized_adapter_result",
            command_family="UNKNOWN",
            raw_output="name: malformed-fixture",
            parser_status="MALFORMED_INPUT",
            unsupported_reason="Normalized result envelope is missing required Day95/Day96 schema fields.",
            evidence_quality="LOW",
            reviewer_action="Hold for schema repair; do not classify as execution failure.",
        ),
        ParserEvidenceCase(
            case_id="D97-C06-missing-raw-output",
            case_name="Missing raw_output",
            input_source="day97_static_fake_output",
            command_family="readonly_identity",
            raw_output=None,
            parser_status="MALFORMED_INPUT",
            unsupported_reason="raw_output field is absent from the parser evidence case.",
            evidence_quality="NOT_APPLICABLE",
            reviewer_action="Reject the case shape and request raw evidence text.",
        ),
        ParserEvidenceCase(
            case_id="D97-C07-missing-command-family",
            case_name="Missing command",
            input_source="day97_static_fake_output",
            command_family="",
            raw_output="name: lab-router-simulated",
            parser_status="MALFORMED_INPUT",
            unsupported_reason="Command family is missing, so parser context is not reviewable.",
            evidence_quality="LOW",
            reviewer_action="Request a normalized command family before parsing.",
        ),
        ParserEvidenceCase(
            case_id="D97-C08-partial-output-headers-only",
            case_name="Partial output with only headers",
            input_source="day97_static_fake_output",
            command_family="readonly_interfaces",
            raw_output="NAME  STATE  COMMENT",
            parser_status="INCOMPLETE_OUTPUT",
            unsupported_reason="Table-like output has headers but no data rows.",
            evidence_quality="LOW",
            reviewer_action="Treat as incomplete evidence and ask for a complete fake fixture.",
        ),
        ParserEvidenceCase(
            case_id="D97-C09-mixed-supported-and-unsupported-sections",
            case_name="Mixed supported and unsupported sections",
            input_source="day97_static_fake_output",
            command_family="readonly_identity+unsupported_routing",
            raw_output="name: lab-router-simulated\n/routing/bgp/peer print\npeer1 established",
            parser_status="AMBIGUOUS_OUTPUT",
            unsupported_reason="Supported identity evidence is mixed with unsupported routing output.",
            evidence_quality="MEDIUM",
            reviewer_action="Split the fixture into reviewed command families before accepting evidence.",
            parser_supported=True,
        ),
        ParserEvidenceCase(
            case_id="D97-C10-supported-shape-missing-required-fields",
            case_name="Supported-looking output missing required fields",
            input_source="day97_static_fake_output",
            command_family="readonly_identity",
            raw_output="name:\nuptime:",
            parser_status="INCOMPLETE_OUTPUT",
            unsupported_reason="Output resembles key-value identity data but required values are empty.",
            evidence_quality="LOW",
            reviewer_action="Do not invent missing values; request complete fake evidence.",
        ),
        ParserEvidenceCase(
            case_id="D97-C11-unexpected-encoding-characters",
            case_name="Unexpected encoding-like characters",
            input_source="day97_static_fake_output",
            command_family="readonly_identity",
            raw_output="name: lab-router-\\ufffd\\ufffd\nstatus: running",
            parser_status="AMBIGUOUS_OUTPUT",
            unsupported_reason="Output includes replacement-character text that may corrupt field meaning.",
            evidence_quality="MEDIUM",
            reviewer_action="Preserve raw text and request clean fixture encoding.",
        ),
        ParserEvidenceCase(
            case_id="D97-C12-repeated-duplicate-lines",
            case_name="Repeated duplicate lines",
            input_source="day97_static_fake_output",
            command_family="readonly_interfaces",
            raw_output="ether1 running\nether1 running\nether1 running",
            parser_status="PARSED",
            unsupported_reason="Duplicate evidence lines reduce confidence even when the shape is parseable.",
            evidence_quality="MEDIUM",
            reviewer_action="Accept only as degraded parser evidence and review fixture generation.",
            parser_supported=True,
        ),
        ParserEvidenceCase(
            case_id="D97-C13-contradictory-parser-hints",
            case_name="Contradictory parser hints",
            input_source="day97_static_fake_output",
            command_family="readonly_identity",
            raw_output="# parser_hint: readonly_identity\n# parser_hint: readonly_interfaces\nname: lab-router",
            parser_status="AMBIGUOUS_OUTPUT",
            unsupported_reason="Parser hints disagree about the command family.",
            evidence_quality="LOW",
            reviewer_action="Require one reviewed command-family hint before accepting output.",
        ),
        ParserEvidenceCase(
            case_id="D97-C14-unsupported-not-failed-execution",
            case_name="Unsupported output, not failed execution",
            input_source="day97_static_fake_output",
            command_family="unsupported_cli_error_text",
            raw_output="% Unrecognized command output fixture only\nsyntax error near token",
            parser_status="UNSUPPORTED_OUTPUT",
            unsupported_reason="Unsupported text must remain parser unsupported evidence, not FAILED_EXECUTION.",
            evidence_quality="LOW",
            reviewer_action="Classify as unsupported parser output; do not infer that a command ran or failed.",
        ),
    ]
    return [case.to_record() for case in cases]


def build_day97_parser_evidence_quality_report() -> Dict[str, Any]:
    cases = build_day97_parser_evidence_cases()
    summary = build_day97_summary(cases)
    report = {
        "day": 97,
        "day_id": "Day97",
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
        "day96_context": {
            "task": "readonly-output-parser-prototype",
            "report_json": "reports/lab-summary/day96_readonly_output_parser_prototype.json",
            "report_html": "reports/lab-summary/day96_readonly_output_parser_prototype.html",
            "relationship": "Day97 hardens evidence classification after the Day96 parser prototype.",
        },
        "summary": summary,
        "scenario_cases": cases,
        "safety_invariants": build_safety_invariants(),
        "unsupported_output_policy": {
            "unsupported_is_not_failed_execution": True,
            "no_live_retry": True,
            "no_adapter_fallback": True,
            "reviewer_facing_only": True,
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
    validation_errors = validate_day97_parser_evidence_quality_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["summary"]["overall_status"] = "FAIL"
        report["summary"]["reviewer_status"] = "REVIEW_REQUIRED"
        report["reviewer_status"] = "REVIEW_REQUIRED"
    return report


def build_day97_summary(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    unsafe_flag_count = sum(
        1
        for case in cases
        for flag_value in case.get("safety_flags", {}).values()
        if flag_value is not False
    )
    parser_statuses = [case["parser_status"] for case in cases]
    evidence_quality_values = [case["evidence_quality"] for case in cases]
    unsupported_degraded_count = sum(
        1
        for case in cases
        if case["parser_status"] != "PARSED" or case["evidence_quality"] != "HIGH"
    )
    failed_execution_count = sum(
        1
        for case in cases
        if case.get("parser_status") == "FAILED_EXECUTION"
        or case.get("failed_execution_classification") is not False
    )
    required_statuses_present = {
        "UNSUPPORTED_OUTPUT",
        "INCOMPLETE_OUTPUT",
        "MALFORMED_INPUT",
        "EMPTY_OUTPUT",
        "AMBIGUOUS_OUTPUT",
    }.issubset(set(parser_statuses))
    overall_status = (
        "PASS"
        if len(cases) >= 14
        and unsupported_degraded_count >= 13
        and unsafe_flag_count == 0
        and failed_execution_count == 0
        and required_statuses_present
        and all(case.get("is_static_fake_case") is True for case in cases)
        else "FAIL"
    )
    return {
        "total_cases": len(cases),
        "parser_supported_count": sum(1 for case in cases if case["parser_supported"] is True),
        "unsupported_degraded_count": unsupported_degraded_count,
        "unsafe_flag_count": unsafe_flag_count,
        "failed_execution_count": failed_execution_count,
        "empty_output_count": parser_statuses.count("EMPTY_OUTPUT"),
        "malformed_input_count": parser_statuses.count("MALFORMED_INPUT"),
        "incomplete_output_count": parser_statuses.count("INCOMPLETE_OUTPUT"),
        "unsupported_output_count": parser_statuses.count("UNSUPPORTED_OUTPUT"),
        "ambiguous_output_count": parser_statuses.count("AMBIGUOUS_OUTPUT"),
        "parsed_degraded_count": sum(
            1
            for case in cases
            if case["parser_status"] == "PARSED" and case["evidence_quality"] != "HIGH"
        ),
        "parser_status_values": sorted(set(parser_statuses)),
        "evidence_quality_values": sorted(set(evidence_quality_values)),
        "required_statuses_present": required_statuses_present,
        "safety_flags_all_false": unsafe_flag_count == 0,
        "overall_status": overall_status,
        "reviewer_status": REVIEWER_STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
    }


def validate_day97_parser_evidence_quality_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("summary", {})
    cases = report.get("scenario_cases", [])

    if report.get("day") != 97:
        errors.append("day must be 97.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be parser-evidence-quality.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if report.get("phase") != PHASE:
        errors.append(f"phase must be {PHASE}.")
    if summary.get("total_cases", 0) < 14:
        errors.append("At least 14 Day97 parser evidence cases are required.")
    if summary.get("unsafe_flag_count") != 0:
        errors.append("unsafe_flag_count must be 0.")
    if summary.get("failed_execution_count") != 0:
        errors.append("failed_execution_count must be 0.")
    if summary.get("required_statuses_present") is not True:
        errors.append("Required parser evidence statuses are missing.")

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

    for invariant, value in report.get("safety_invariants", {}).items():
        if invariant in SAFETY_FLAG_NAMES and value is not False:
            errors.append(f"safety_invariants.{invariant} must be false.")

    required_case_fields = {
        "case_id",
        "case_name",
        "input_source",
        "command_family",
        "raw_output_present",
        "parser_supported",
        "parser_status",
        "unsupported_reason",
        "evidence_quality",
        "reviewer_action",
        "safety_flags",
    }
    for case in cases:
        missing = required_case_fields.difference(case)
        if missing:
            errors.append(f"{case.get('case_id', '<unknown>')} missing fields: {', '.join(sorted(missing))}.")
        if case.get("fixture_origin") != SOURCE_KIND:
            errors.append(f"{case.get('case_id')} must be a Day97 static fake parser case.")
        if case.get("is_static_fake_case") is not True:
            errors.append(f"{case.get('case_id')} must be marked static fake.")
        if case.get("parser_status") not in PARSER_STATUSES:
            errors.append(f"{case.get('case_id')} has unsupported parser_status.")
        if case.get("evidence_quality") not in EVIDENCE_QUALITY_VALUES:
            errors.append(f"{case.get('case_id')} has unsupported evidence_quality.")
        if not case.get("unsupported_reason"):
            errors.append(f"{case.get('case_id')} must include unsupported_reason.")
        if not case.get("reviewer_action"):
            errors.append(f"{case.get('case_id')} must include reviewer_action.")
        if case.get("failed_execution_classification") is not False:
            errors.append(f"{case.get('case_id')} must not be a failed execution classification.")
        safety_flags = case.get("safety_flags", {})
        for flag_name in SAFETY_FLAG_NAMES:
            if safety_flags.get(flag_name) is not False:
                errors.append(f"{case.get('case_id')} safety_flags.{flag_name} must be false.")
    return errors


def write_day97_parser_evidence_quality_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day97_parser_evidence_quality_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day97_parser_evidence_quality_html(safe_report, html_path)
    return json_path, html_path


def write_day97_parser_evidence_quality_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    case_rows = "".join(
        "<tr>"
        f"<td>{html.escape(case['case_id'])}</td>"
        f"<td>{html.escape(case['case_name'])}</td>"
        f"<td>{html.escape(case['input_source'])}</td>"
        f"<td>{html.escape(case['command_family'] or 'MISSING')}</td>"
        f"<td>{html.escape(json.dumps(case['raw_output_present']))}</td>"
        f"<td>{html.escape(json.dumps(case['parser_supported']))}</td>"
        f"<td>{html.escape(case['parser_status'])}</td>"
        f"<td>{html.escape(case['unsupported_reason'])}</td>"
        f"<td>{html.escape(case['evidence_quality'])}</td>"
        f"<td>{html.escape(case['reviewer_action'])}</td>"
        "</tr>"
        for case in report["scenario_cases"]
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
  <h1>Day97 Parser Evidence Quality</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Scope:</strong> parser-only static fake cases for unsupported, incomplete, malformed, ambiguous, empty, and degraded output. Unsupported parser output is not failed execution.</p>
  <h2>Summary</h2>
  <p><strong>Total cases:</strong> {summary['total_cases']} | <strong>Parser supported:</strong> {summary['parser_supported_count']} | <strong>Unsupported/degraded:</strong> {summary['unsupported_degraded_count']} | <strong>Unsafe flags:</strong> {summary['unsafe_flag_count']}</p>
  <p><strong>Overall status:</strong> <code>{html.escape(summary['overall_status'])}</code> | <strong>Reviewer status:</strong> <code>{html.escape(summary['reviewer_status'])}</code></p>
  <h2>Scenario Table</h2>
  <table>
    <thead><tr><th>Case</th><th>Name</th><th>Input source</th><th>Command family</th><th>Raw output</th><th>Parser supported</th><th>Status</th><th>Unsupported reason</th><th>Evidence quality</th><th>Reviewer action</th></tr></thead>
    <tbody>{case_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table>
    <thead><tr><th>Invariant</th><th>Value</th></tr></thead>
    <tbody>{invariant_rows}</tbody>
  </table>
  <h2>Day96 Context</h2>
  <p>Day97 follows the Day96 read-only output parser prototype and hardens unsupported output evidence quality. Related Day96 report paths: <code>reports/lab-summary/day96_readonly_output_parser_prototype.json</code> and <code>reports/lab-summary/day96_readonly_output_parser_prototype.html</code>.</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_safety_flags() -> Dict[str, bool]:
    return {flag_name: False for flag_name in SAFETY_FLAG_NAMES}


def build_safety_invariants() -> Dict[str, Any]:
    return {
        **build_safety_flags(),
        "fake_only": True,
        "static_fixture_only": True,
        "parser_only": True,
        "report_only": True,
        "no_config_json_read": True,
        "no_openai_api": True,
        "no_ai_sdk_runtime": True,
        "no_voice_runtime": True,
        "no_dashboard_post_route": True,
        "unsupported_output_is_not_failed_execution": True,
    }


def _preview_raw_output(raw_output: Optional[str]) -> str:
    if raw_output is None:
        return "<missing>"
    compact = " ".join(raw_output.split())
    if not compact:
        return "<empty>"
    return compact[:120]
