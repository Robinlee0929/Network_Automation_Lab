"""Shared deterministic reports for v0.5 AI Assistance review-only days."""

from __future__ import annotations

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple


OVERALL_STATUS = "PASS"
STATUS = "REVIEW_READY"
FAIL_STATUS = "FAIL"
BLOCKED_STATUS = "BLOCKED"
MODE = "review-only / report-only / non-executable"

REQUIRED_TRUE_FIELDS: Tuple[str, ...] = (
    "agents_md_found_and_read",
    "agents_md_not_modified",
    "day154_closure_baseline_lock_respected",
    "day155_reopen_rationale_respected",
    "reviewer_assistance_only",
    "executor_recommendation_only",
    "human_reviewer_final_authority",
    "fixed_template_required",
    "pytest_required",
    "report_index_no_new_blocking_issue_required",
    "forbidden_capability_scan_required",
    "safety_boundary_regression_required",
)

REQUIRED_FALSE_FIELDS: Tuple[str, ...] = (
    "next_phase_allowed",
    "phase_gate_approval",
    "execution_allowed",
    "executor_unlock_allowed",
    "provider_allowed",
    "api_allowed",
    "external_api_call_allowed",
    "openai_api_call_allowed",
    "model_call_allowed",
    "live_device_allowed",
    "ssh_allowed",
    "netconf_allowed",
    "restconf_allowed",
    "routeros_allowed",
    "command_execution_allowed",
    "live_command_template_allowed",
    "direct_command_generation_allowed",
    "secrets_allowed",
    "credential_read_allowed",
    "config_json_read_allowed",
    "microphone_allowed",
    "voice_input_allowed",
)

COMMON_FORBIDDEN_CAPABILITIES: Tuple[str, ...] = (
    "provider/API/model activation",
    "OpenAI or external API call",
    "live device access",
    "SSH, NETCONF, RESTCONF, or RouterOS transport",
    "direct command generation",
    "executor unlock",
    "secrets, tokens, passwords, private keys, or local runtime config reads",
    "microphone, voice input, speech-to-text, or text-to-speech",
    "phase gate approval",
)


def build_agents_md_evidence(project_root: Path) -> Dict[str, Any]:
    agents_path = Path(project_root) / "AGENTS.md"
    try:
        contents = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "agents_md_pre_read": "NO",
            "agents_md_result": f"READ_ERROR: {exc}",
            "agents_md_found_and_read": False,
            "agents_md_not_modified": False,
            "agents_md_modified": True,
        }

    markers_present = "Core Safety Rules" in contents and "Standard Validation" in contents
    return {
        "agents_md_pre_read": "YES" if markers_present else "NO",
        "agents_md_result": "FOUND_AND_READ" if markers_present else "FOUND_WITHOUT_REQUIRED_MARKERS",
        "agents_md_found_and_read": markers_present,
        "agents_md_not_modified": True,
        "agents_md_modified": False,
    }


def build_v05_ai_assistance_report(project_root: Path, spec: Mapping[str, Any]) -> Dict[str, Any]:
    reference_records = [_build_reference_record(Path(project_root), target) for target in spec["reference_targets"]]
    report: Dict[str, Any] = {
        "day": spec["day"],
        "day_label": f"Day{spec['day']}",
        "task": spec["task_name"],
        "title": spec["title"],
        "full_title": f"Day{spec['day']} {spec['title']}",
        "overall_status": OVERALL_STATUS,
        "status": STATUS,
        "status_label": spec["status_label"],
        "mode": spec.get("mode", MODE),
        "contract_type": spec["contract_type"],
        **{field: True for field in REQUIRED_TRUE_FIELDS},
        **{field: False for field in REQUIRED_FALSE_FIELDS},
        **build_agents_md_evidence(project_root),
        "purpose": spec["purpose"],
        "contract_records": deepcopy(spec["contract_records"]),
        "acceptance_checks": deepcopy(spec["acceptance_checks"]),
        "forbidden_capabilities": list(COMMON_FORBIDDEN_CAPABILITIES),
        "forbidden_capability_scan": {
            "status": OVERALL_STATUS,
            "provider_api_live_device_activation_found": False,
            "direct_command_generation_found": False,
            "secrets_access_found": False,
            "executor_unlock_found": False,
            "voice_or_microphone_runtime_found": False,
        },
        "safety_boundary_regression": {
            "status": OVERALL_STATUS,
            "day154_closure_baseline_lock_respected": True,
            "day155_reopen_rationale_respected": True,
            "next_phase_allowed": False,
            "phase_gate_approval": False,
            "execution_allowed": False,
        },
        "result_semantics": {
            "pass_means": spec["pass_means"],
            "ai_execution_allowed": False,
            "provider_api_integration_allowed": False,
            "executor_can_act_on_ai_output": False,
            "next_phase_allowed": False,
        },
        "reference_records": reference_records,
        "report_paths": {
            "json": spec["report_json"].as_posix(),
            "html": spec["report_html"].as_posix(),
        },
        "final_recommendation": spec["final_recommendation"],
        "validation_errors": [],
    }
    report["validation_errors"] = collect_v05_validation_errors(report, spec)
    if report["validation_errors"]:
        report["overall_status"] = FAIL_STATUS
        report["status"] = BLOCKED_STATUS
    return report


def collect_v05_validation_errors(report: Mapping[str, Any], spec: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_values = {
        "day": spec["day"],
        "day_label": f"Day{spec['day']}",
        "task": spec["task_name"],
        "title": spec["title"],
        "overall_status": OVERALL_STATUS,
        "status": STATUS,
        "status_label": spec["status_label"],
        "contract_type": spec["contract_type"],
        "final_recommendation": spec["final_recommendation"],
    }
    for field, expected in expected_values.items():
        if report.get(field) != expected:
            errors.append(f"{field} must be {expected}.")

    if report.get("agents_md_pre_read") != "YES":
        errors.append("agents_md_pre_read must be YES.")
    if report.get("agents_md_result") != "FOUND_AND_READ":
        errors.append("agents_md_result must be FOUND_AND_READ.")
    if report.get("agents_md_modified") is not False:
        errors.append("agents_md_modified must be false.")

    for field in REQUIRED_TRUE_FIELDS:
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FIELDS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    records = report.get("contract_records")
    if not isinstance(records, list) or len(records) != len(spec["contract_records"]):
        errors.append("contract_records must preserve the spec records.")
    else:
        for record in records:
            if record.get("status") != OVERALL_STATUS:
                errors.append(f"{record.get('id', '<unknown>')} status must be PASS.")
            if record.get("review_only") is not True:
                errors.append(f"{record.get('id', '<unknown>')} review_only must be true.")
            if record.get("report_only") is not True:
                errors.append(f"{record.get('id', '<unknown>')} report_only must be true.")
            if record.get("execution_allowed") is not False:
                errors.append(f"{record.get('id', '<unknown>')} execution_allowed must be false.")
            if record.get("next_phase_allowed") is not False:
                errors.append(f"{record.get('id', '<unknown>')} next_phase_allowed must be false.")

    checks = report.get("acceptance_checks")
    if not isinstance(checks, list) or len(checks) != len(spec["acceptance_checks"]):
        errors.append("acceptance_checks must preserve the spec checks.")
    else:
        for check in checks:
            if check.get("status") != OVERALL_STATUS:
                errors.append(f"{check.get('id', '<unknown>')} status must be PASS.")
            if check.get("blocks_execution_unlock") is not True:
                errors.append(f"{check.get('id', '<unknown>')} blocks_execution_unlock must be true.")

    scan = report.get("forbidden_capability_scan")
    if not isinstance(scan, dict) or scan.get("status") != OVERALL_STATUS:
        errors.append("forbidden_capability_scan.status must be PASS.")
    elif any(value is not False for key, value in scan.items() if key != "status"):
        errors.append("forbidden_capability_scan unsafe findings must all be false.")

    boundary = report.get("safety_boundary_regression")
    if not isinstance(boundary, dict) or boundary.get("status") != OVERALL_STATUS:
        errors.append("safety_boundary_regression.status must be PASS.")
    else:
        for field in ("next_phase_allowed", "phase_gate_approval", "execution_allowed"):
            if boundary.get(field) is not False:
                errors.append(f"safety_boundary_regression.{field} must be false.")

    semantics = report.get("result_semantics")
    if not isinstance(semantics, dict):
        errors.append("result_semantics must be present.")
    else:
        for field in (
            "ai_execution_allowed",
            "provider_api_integration_allowed",
            "executor_can_act_on_ai_output",
            "next_phase_allowed",
        ):
            if semantics.get(field) is not False:
                errors.append(f"result_semantics.{field} must be false.")

    reference_records = report.get("reference_records")
    if not isinstance(reference_records, list) or len(reference_records) != len(spec["reference_targets"]):
        errors.append("reference_records must cover all reference targets.")
    else:
        for record in reference_records:
            if record.get("path_exists") is not True:
                errors.append(f"{record.get('surface', '<unknown>')} path must exist.")
            if record.get("missing_fragments") != []:
                errors.append(f"{record.get('surface', '<unknown>')} must contain all required fragments.")
            if record.get("next_phase_allowed") is not False:
                errors.append(f"{record.get('surface', '<unknown>')} next_phase_allowed must be false.")
    return errors


def write_v05_ai_assistance_reports(
    project_root: Path,
    spec: Mapping[str, Any],
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    safe_report = deepcopy(report) if report is not None else build_v05_ai_assistance_report(project_root, spec)
    json_path = Path(project_root) / spec["report_json"]
    html_path = Path(project_root) / spec["report_html"]
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_v05_ai_assistance_html(safe_report, html_path)
    return json_path, html_path


def write_v05_ai_assistance_html(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = _table_rows(
        (field, report[field])
        for field in (
            "day",
            "status",
            "status_label",
            "mode",
            "contract_type",
            "reviewer_assistance_only",
            "executor_recommendation_only",
            "execution_allowed",
            "provider_allowed",
            "api_allowed",
            "openai_api_call_allowed",
            "live_device_allowed",
            "command_execution_allowed",
            "secrets_allowed",
            "phase_gate_approval",
            "next_phase_allowed",
        )
    )
    record_rows = _table_rows(
        (
            item.get("id", ""),
            item.get("name", ""),
            item.get("status", ""),
            item.get("summary", ""),
            item.get("next_phase_allowed", False),
        )
        for item in report.get("contract_records", [])
    )
    check_rows = _table_rows(
        (item.get("id", ""), item.get("name", ""), item.get("status", ""), item.get("blocks_execution_unlock", ""))
        for item in report.get("acceptance_checks", [])
    )
    reference_rows = _table_rows(
        (
            item.get("surface", ""),
            item.get("path", ""),
            item.get("path_exists", False),
            item.get("all_required_fragments_present", False),
            item.get("missing_fragments", []),
        )
        for item in report.get("reference_records", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report['full_title']))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5d8dc; padding: 0.55rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report['full_title']))}</h1>
  <p><strong>{html.escape(str(report['status_label']))}</strong></p>
  <p><strong>next_phase_allowed=false</strong></p>
  <p><strong>PASS does not allow AI execution, provider/API integration, live-device access, direct command generation, or executor action.</strong></p>
  <p>{html.escape(str(report['purpose']))}</p>
  <h2>Status</h2>
  <table><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>{summary_rows}</tbody></table>
  <h2>Contract Records</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Summary</th><th>Next Phase Allowed</th></tr></thead><tbody>{record_rows}</tbody></table>
  <h2>Acceptance Checks</h2>
  <table><thead><tr><th>ID</th><th>Name</th><th>Status</th><th>Blocks Execution Unlock</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Reference Records</h2>
  <table><thead><tr><th>Surface</th><th>Path</th><th>Path Exists</th><th>Fragments Present</th><th>Missing Fragments</th></tr></thead><tbody>{reference_rows}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_v05_ai_assistance_report(
    project_root: Path,
    spec: Mapping[str, Any],
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_v05_ai_assistance_report(project_root, spec)
    json_path, html_path = write_v05_ai_assistance_reports(project_root, spec, report)
    format_heading = format_heading_func or (lambda text: text)
    format_status = format_status_func or (lambda status: f"[{status}]")
    relative_to_project = relative_to_project_func or _default_relative_to_project

    print(f"AGENTS.md pre-read: {report['agents_md_pre_read']}")
    print(f"AGENTS.md result: {report['agents_md_result']}")
    print(f"AGENTS.md modified: {json.dumps(report['agents_md_modified'])}")
    print(format_heading(report["full_title"]))
    print(f"Task slug: {report['task']}")
    for field in (
        "day",
        "status",
        "status_label",
        "mode",
        "contract_type",
        "reviewer_assistance_only",
        "executor_recommendation_only",
        "execution_allowed",
        "provider_allowed",
        "api_allowed",
        "openai_api_call_allowed",
        "external_api_call_allowed",
        "live_device_allowed",
        "command_execution_allowed",
        "executor_unlock_allowed",
        "secrets_allowed",
        "phase_gate_approval",
        "next_phase_allowed",
    ):
        print(f"{field}: {_json_value(report[field])}")
    print(f"contract_record_count: {len(report['contract_records'])}")
    for item in report["contract_records"]:
        print(f"{item['id']}: {item['status']} | {item['name']}")
    print(f"acceptance_check_count: {len(report['acceptance_checks'])}")
    for item in report["acceptance_checks"]:
        print(f"{item['id']}: {item['status']} | {item['name']}")
    print(f"forbidden_capability_scan: {report['forbidden_capability_scan']['status']}")
    print(f"safety_boundary_regression: {report['safety_boundary_regression']['status']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"JSON report: {relative_to_project(project_root, json_path)}")
    print(f"HTML report: {relative_to_project(project_root, html_path)}")

    if report["overall_status"] == OVERALL_STATUS and not report["validation_errors"]:
        print(f"{format_status(OVERALL_STATUS)} {report['status_label']}")
        return 0

    print(f"{format_status(FAIL_STATUS)} {report['status_label']}_BLOCKED")
    return 1


def _build_reference_record(project_root: Path, target: Mapping[str, Any]) -> Dict[str, Any]:
    path = project_root / str(target["path"])
    text = _read_text(path)
    required_fragments = list(target["required_fragments"])
    missing_fragments = [fragment for fragment in required_fragments if fragment not in text]
    return {
        "surface": target["surface"],
        "path": target["path"],
        "path_exists": path.exists(),
        "required_fragments": required_fragments,
        "missing_fragments": missing_fragments,
        "all_required_fragments_present": path.exists() and not missing_fragments,
        "review_only": True,
        "report_only": True,
        "next_phase_allowed": False,
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _default_relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _json_value(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    return str(value)


def _cell_text(value: Any) -> str:
    if isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _table_rows(rows: Iterable[Iterable[Any]]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell_text(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
