"""Day96 read-only output parser prototype.

This module is deterministic and parser-only. It accepts Day95 normalized fake
adapter result objects and parses only their simulated output payloads.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_adapter_result_normalization import (
    RESULT_KIND as DAY95_RESULT_KIND,
    SCHEMA_VERSION as DAY95_SCHEMA_VERSION,
    run_adapter_result_normalization,
)


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "readonly-output-parser-prototype"
TITLE = "Read-only Output Parser Prototype"
PHASE = "PARSER_PROTOTYPE_READY"
SCHEMA_VERSION = "day96.readonly_output_parser.v1"
SOURCE_KIND = "fake_adapter_simulated_output"
PARSER_MODE = "parser_only"
REPORT_JSON = Path("reports") / "lab-summary" / "day96_readonly_output_parser_prototype.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day96_readonly_output_parser_prototype.html"


def parse_normalized_fake_adapter_result(normalized_result: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a Day95 normalized fake adapter result without any live fallback."""
    parsed = _base_parser_record(normalized_result)

    if not isinstance(normalized_result, dict):
        parsed["parser_status"] = "REVIEW_NEEDED"
        parsed["warnings"].append("Malformed normalized result: input is not an object.")
        return parsed

    validation_warnings = _validate_day95_fake_result_envelope(normalized_result)
    if validation_warnings:
        parsed["parser_status"] = "REVIEW_NEEDED"
        parsed["warnings"].extend(validation_warnings)
        return parsed

    payload = normalized_result.get("result_payload", {})
    if "simulated_output" not in payload:
        parsed["parser_status"] = "REVIEW_NEEDED"
        parsed["warnings"].append("Missing simulated_output in Day95 result_payload.")
        return parsed

    simulated_output = payload.get("simulated_output")
    if not isinstance(simulated_output, str):
        parsed["parser_status"] = "UNSUPPORTED"
        parsed["warnings"].append("Unsupported simulated_output type; parser accepts text only.")
        parsed["unsupported_sections"].append(
            {
                "section": "result_payload.simulated_output",
                "reason": f"Unsupported type: {type(simulated_output).__name__}",
            }
        )
        return parsed

    lines = [line.strip() for line in simulated_output.splitlines() if line.strip()]
    if not lines:
        parsed["parser_status"] = "REVIEW_NEEDED"
        parsed["warnings"].append("Missing or empty simulated_output text.")
        return parsed

    parsed["parsed_records"] = _parse_text_lines(lines)
    parsed["parser_status"] = "PARSED" if parsed["parsed_records"] else "REVIEW_NEEDED"
    if parsed["parser_status"] == "REVIEW_NEEDED":
        parsed["warnings"].append("No supported parser records were extracted from simulated output.")
    return parsed


def build_day96_parser_report() -> Dict[str, Any]:
    day95_report = run_adapter_result_normalization()
    day95_results = deepcopy(day95_report["normalized_result_records"])
    parser_cases = [
        _build_case_record(
            case_id=f"D96-C{index:02d}-day95-{result['scenario_id']}",
            description="Day95 normalized fake adapter result",
            normalized_result=result,
        )
        for index, result in enumerate(day95_results, start=1)
    ]
    parser_cases.extend(_build_boundary_parser_cases(day95_results[0] if day95_results else {}))

    summary = _build_parser_summary(parser_cases)
    report = {
        "day": 96,
        "day_id": "Day96",
        "task": TASK_NAME,
        "title": TITLE,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": summary["overall_status"],
        "overall_status": summary["overall_status"],
        "schema_version": SCHEMA_VERSION,
        "safety_boundary": _build_safety_boundary(),
        "parser_contract": {
            "input_schema": DAY95_SCHEMA_VERSION,
            "input_result_kind": DAY95_RESULT_KIND,
            "source_kind": SOURCE_KIND,
            "parser_mode": PARSER_MODE,
            "no_live_fallback": True,
            "unsupported_behavior": "REVIEW_NEEDED_OR_UNSUPPORTED",
        },
        "parser_cases": parser_cases,
        "parsed_records_summary": summary,
        "unsupported_cases": [
            case for case in parser_cases if case["parser_result"]["parser_status"] == "UNSUPPORTED"
        ],
        "warnings": [
            warning
            for case in parser_cases
            for warning in case["parser_result"].get("warnings", [])
        ],
        "evidence": {
            "day95_normalized_fake_adapter_results_used": len(day95_results),
            "all_inputs_fake_only_simulated_outputs": True,
            "live_read_enabled": False,
            "ssh_enabled": False,
            "routeros_enabled": False,
            "device_access_enabled": False,
            "adapter_fallback_enabled": False,
            "runner_live_path_enabled": False,
            "dashboard_action_allowed": False,
            "no_config_json_read": True,
        },
        "no_real_device_access": True,
        "no_ssh": True,
        "no_routeros": True,
        "no_live_read": True,
        "no_config_json_read": True,
        "dashboard_read_only": True,
        "dashboard_action_allowed": False,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
    }
    validation_errors = validate_day96_parser_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["parsed_records_summary"]["overall_status"] = "FAIL"
    return report


def write_day96_parser_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_day96_parser_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day96_parser_html(safe_report, html_path)
    return json_path, html_path


def validate_day96_parser_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    summary = report.get("parsed_records_summary", {})
    safety = report.get("safety_boundary", {})
    evidence = report.get("evidence", {})

    if report.get("day") != 96:
        errors.append("day must be 96.")
    if report.get("task") != TASK_NAME:
        errors.append("task must be readonly-output-parser-prototype.")
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}.")
    if summary.get("parsed_case_count", 0) < 2:
        errors.append("At least two Day95 parser cases must parse successfully.")
    if summary.get("live_fallback_attempts") != 0:
        errors.append("live_fallback_attempts must be 0.")
    if summary.get("device_access_attempts") != 0:
        errors.append("device_access_attempts must be 0.")
    for field in (
        "live_read_enabled",
        "ssh_enabled",
        "routeros_enabled",
        "device_access_enabled",
        "adapter_fallback_enabled",
        "runner_live_path_enabled",
        "dashboard_action_allowed",
    ):
        if safety.get(field) is not False:
            errors.append(f"safety_boundary.{field} must be false.")
        if evidence.get(field) is not False:
            errors.append(f"evidence.{field} must be false.")
    if safety.get("source_kind") != SOURCE_KIND:
        errors.append("safety_boundary.source_kind must be fake_adapter_simulated_output.")
    if safety.get("parser_mode") != PARSER_MODE:
        errors.append("safety_boundary.parser_mode must be parser_only.")
    if evidence.get("all_inputs_fake_only_simulated_outputs") is not True:
        errors.append("all_inputs_fake_only_simulated_outputs must be true.")
    if evidence.get("no_config_json_read") is not True:
        errors.append("no_config_json_read must be true.")

    for case in report.get("parser_cases", []):
        parser_result = case.get("parser_result", {})
        if parser_result.get("source_kind") != SOURCE_KIND:
            errors.append(f"{case.get('case_id')} has wrong source_kind.")
        if parser_result.get("parser_mode") != PARSER_MODE:
            errors.append(f"{case.get('case_id')} has wrong parser_mode.")
        for field in (
            "live_read_enabled",
            "ssh_enabled",
            "routeros_enabled",
            "device_access_enabled",
        ):
            if parser_result.get(field) is not False:
                errors.append(f"{case.get('case_id')} {field} must be false.")
        if parser_result.get("live_fallback_attempted") is not False:
            errors.append(f"{case.get('case_id')} must not attempt live fallback.")
    return errors


def write_day96_parser_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report["parsed_records_summary"]
    case_rows = "".join(
        "<tr>"
        f"<td>{html.escape(case['case_id'])}</td>"
        f"<td>{html.escape(case['description'])}</td>"
        f"<td>{html.escape(case['parser_result']['input_scenario_id'])}</td>"
        f"<td>{html.escape(case['parser_result']['parser_status'])}</td>"
        f"<td>{len(case['parser_result']['parsed_records'])}</td>"
        f"<td>{html.escape('; '.join(case['parser_result']['warnings']))}</td>"
        "</tr>"
        for case in report["parser_cases"]
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
  <h1>Day96 Read-only Output Parser Prototype</h1>
  <p><strong>Status:</strong> <span class="{html.escape(report['status'].lower())}">{html.escape(report['status'])}</span> / {html.escape(report['phase'])}</p>
  <p><strong>Safety boundary:</strong> parser-only over Day95 normalized fake adapter simulated output. No RouterOS, no SSH, no live-read, no device access, no adapter fallback, no runner live path, no dashboard action.</p>
  <h2>Parser Summary</h2>
  <p><strong>Total cases:</strong> {summary['total_cases']} | <strong>Parsed:</strong> {summary['parsed_case_count']} | <strong>Review needed:</strong> {summary['review_needed_case_count']} | <strong>Unsupported:</strong> {summary['unsupported_case_count']}</p>
  <p><strong>Parsed records:</strong> {summary['parsed_record_count']} | <strong>Live fallback attempts:</strong> {summary['live_fallback_attempts']} | <strong>Device access attempts:</strong> {summary['device_access_attempts']}</p>
  <h2>Parser Cases</h2>
  <table>
    <thead><tr><th>Case</th><th>Description</th><th>Scenario</th><th>Status</th><th>Records</th><th>Warnings</th></tr></thead>
    <tbody>{case_rows}</tbody>
  </table>
  <h2>Evidence</h2>
  <p>All inputs are fake-only simulated outputs from Day95 normalized fake adapter results or local malformed boundary probes. Unsupported or malformed input returns REVIEW_NEEDED or UNSUPPORTED without live recovery.</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def _base_parser_record(normalized_result: Any) -> Dict[str, Any]:
    scenario_id = normalized_result.get("scenario_id", "UNKNOWN") if isinstance(normalized_result, dict) else "UNKNOWN"
    command_family = (
        normalized_result.get("result_payload", {}).get("command_family", "UNKNOWN")
        if isinstance(normalized_result, dict)
        else "UNKNOWN"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "input_schema_version": (
            normalized_result.get("schema_version") if isinstance(normalized_result, dict) else None
        ),
        "input_scenario_id": scenario_id,
        "command_family": command_family,
        "source_kind": SOURCE_KIND,
        "parser_mode": PARSER_MODE,
        "live_read_enabled": False,
        "ssh_enabled": False,
        "routeros_enabled": False,
        "device_access_enabled": False,
        "live_fallback_attempted": False,
        "adapter_fallback_attempted": False,
        "runner_live_path_attempted": False,
        "parser_status": "REVIEW_NEEDED",
        "parsed_records": [],
        "warnings": [],
        "unsupported_sections": [],
        "not_verified_device_truth": True,
    }


def _validate_day95_fake_result_envelope(normalized_result: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    if normalized_result.get("schema_version") != DAY95_SCHEMA_VERSION:
        warnings.append("Malformed normalized result: schema_version is not Day95.")
    if normalized_result.get("result_kind") != DAY95_RESULT_KIND:
        warnings.append("Malformed normalized result: result_kind is not normalized_fake_adapter_result.")
    if normalized_result.get("adapter_type") != "fake":
        warnings.append("Malformed normalized result: adapter_type must be fake.")
    if normalized_result.get("guard_decision") != "ALLOW":
        warnings.append("Malformed normalized result: guard_decision must be ALLOW.")
    if normalized_result.get("adapter_invoked") is not True:
        warnings.append("Malformed normalized result: adapter_invoked must be true for Day95 allowed records.")
    if not isinstance(normalized_result.get("result_payload"), dict):
        warnings.append("Malformed normalized result: result_payload must be an object.")

    safety = normalized_result.get("safety", {})
    if not isinstance(safety, dict):
        warnings.append("Malformed normalized result: safety must be an object.")
    else:
        for field in (
            "real_adapter_result_present",
            "live_execution_result_present",
            "ssh_used",
            "device_access_used",
            "execution_unlocked",
        ):
            if safety.get(field) is not False:
                warnings.append(f"Malformed normalized result: safety.{field} must be false.")
    return warnings


def _parse_text_lines(lines: List[str]) -> List[Dict[str, Any]]:
    if _looks_like_table(lines):
        return _parse_table_lines(lines)
    if all(_looks_like_key_value(line) for line in lines):
        return [_parse_key_value_line(line, index) for index, line in enumerate(lines, start=1)]
    return [
        {
            "record_type": "text_line",
            "line_number": index,
            "text": line,
        }
        for index, line in enumerate(lines, start=1)
    ]


def _looks_like_key_value(line: str) -> bool:
    if ":" in line:
        key, value = line.split(":", 1)
        return bool(key.strip() and value.strip())
    if "=" in line:
        key, value = line.split("=", 1)
        return bool(key.strip() and value.strip())
    return False


def _parse_key_value_line(line: str, line_number: int) -> Dict[str, Any]:
    separator = ":" if ":" in line else "="
    key, value = line.split(separator, 1)
    return {
        "record_type": "key_value",
        "line_number": line_number,
        "key": key.strip(),
        "value": value.strip(),
    }


def _looks_like_table(lines: List[str]) -> bool:
    if len(lines) < 2:
        return False
    if "|" in lines[0]:
        return all("|" in line for line in lines[:2])
    return len(_split_table_row(lines[0])) >= 2 and len(_split_table_row(lines[1])) >= 2


def _parse_table_lines(lines: List[str]) -> List[Dict[str, Any]]:
    headers = _split_table_row(lines[0])
    records: List[Dict[str, Any]] = []
    for line_number, line in enumerate(lines[1:], start=2):
        values = _split_table_row(line)
        if len(values) != len(headers):
            records.append(
                {
                    "record_type": "table_row_unaligned",
                    "line_number": line_number,
                    "raw": line,
                }
            )
            continue
        records.append(
            {
                "record_type": "table_row",
                "line_number": line_number,
                "fields": dict(zip(headers, values)),
            }
        )
    return records


def _split_table_row(line: str) -> List[str]:
    if "|" in line:
        return [part.strip() for part in line.strip("|").split("|") if part.strip()]
    parts: List[str] = []
    current = ""
    previous_space = False
    split_ready = False
    for char in line:
        if char.isspace():
            if previous_space:
                split_ready = True
            previous_space = True
            if not split_ready:
                current += char
            continue
        if split_ready:
            if current.strip():
                parts.append(current.strip())
            current = char
            split_ready = False
            previous_space = False
            continue
        previous_space = False
        current += char
    if current.strip():
        parts.append(current.strip())
    return parts


def _build_case_record(
    case_id: str,
    description: str,
    normalized_result: Any,
) -> Dict[str, Any]:
    parser_result = parse_normalized_fake_adapter_result(normalized_result)
    return {
        "case_id": case_id,
        "description": description,
        "input_source": "day95_normalized_fake_adapter_result",
        "parser_result": parser_result,
    }


def _build_boundary_parser_cases(example_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    missing_output = deepcopy(example_result)
    if isinstance(missing_output.get("result_payload"), dict):
        missing_output["result_payload"].pop("simulated_output", None)

    unsupported_output = deepcopy(example_result)
    if isinstance(unsupported_output.get("result_payload"), dict):
        unsupported_output["result_payload"]["simulated_output"] = ["not", "text"]

    return [
        _build_case_record(
            "D96-C90-missing-simulated-output",
            "Missing simulated output is held for review",
            missing_output,
        ),
        _build_case_record(
            "D96-C91-malformed-normalized-result",
            "Malformed normalized result is held for review",
            {"result_payload": {"simulated_output": "name: malformed-fixture"}},
        ),
        _build_case_record(
            "D96-C92-unsupported-simulated-output-type",
            "Unsupported simulated output type is rejected without fallback",
            unsupported_output,
        ),
    ]


def _build_parser_summary(parser_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = [case["parser_result"]["parser_status"] for case in parser_cases]
    parsed_record_count = sum(
        len(case["parser_result"]["parsed_records"]) for case in parser_cases
    )
    live_fallback_attempts = sum(
        1 for case in parser_cases if case["parser_result"]["live_fallback_attempted"]
    )
    adapter_fallback_attempts = sum(
        1 for case in parser_cases if case["parser_result"]["adapter_fallback_attempted"]
    )
    device_access_attempts = sum(
        1 for case in parser_cases if case["parser_result"]["device_access_enabled"]
    )
    overall_status = (
        "PASS"
        if statuses.count("PARSED") >= 2
        and statuses.count("REVIEW_NEEDED") >= 2
        and statuses.count("UNSUPPORTED") >= 1
        and live_fallback_attempts == 0
        and adapter_fallback_attempts == 0
        and device_access_attempts == 0
        else "FAIL"
    )
    return {
        "overall_status": overall_status,
        "total_cases": len(parser_cases),
        "parsed_case_count": statuses.count("PARSED"),
        "review_needed_case_count": statuses.count("REVIEW_NEEDED"),
        "unsupported_case_count": statuses.count("UNSUPPORTED"),
        "parsed_record_count": parsed_record_count,
        "live_fallback_attempts": live_fallback_attempts,
        "adapter_fallback_attempts": adapter_fallback_attempts,
        "device_access_attempts": device_access_attempts,
        "parser_status_values": sorted(set(statuses)),
    }


def _build_safety_boundary() -> Dict[str, Any]:
    return {
        "source_kind": SOURCE_KIND,
        "parser_mode": PARSER_MODE,
        "live_read_enabled": False,
        "ssh_enabled": False,
        "routeros_enabled": False,
        "device_access_enabled": False,
        "adapter_fallback_enabled": False,
        "runner_live_path_enabled": False,
        "dashboard_action_allowed": False,
        "config_json_read": False,
    }
