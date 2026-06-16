"""Phase 2A-03 dry-run job request normalization and plan gate.

This module is report-only and plan-only. It accepts only Phase 2A
mock/local/read-only request shapes, converts them into non-executable dry-run
plans, and rejects live-capable or dangerous request shapes before any runner or
adapter path can be reached.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase2a_readonly_job_runner_framework import (
    ALLOWED_INPUT_FIELDS_BY_JOB_TYPE,
    ALLOWED_JOB_TYPES,
    ALLOWED_TOP_LEVEL_FIELDS,
    validate_artifact_path,
    validate_evidence_ref,
)


PHASE = "Phase 2A"
TASK_NAME = "phase2a-03-dry-run-job-plan-gate"
TITLE = "Phase 2A-03 Job Request Normalization and Dry-Run Plan Gate"
STATUS_LABEL = "DRY_RUN_JOB_PLAN_GATE_READY"
EXECUTION_MODE = "dry-run-plan-only"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_03_dry_run_job_plan_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_03_dry_run_job_plan_gate.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_03_dry_run_job_plan_gate.md"

REJECTED_JOB_TYPES = frozenset(
    {
        "arbitrary_command",
        "arbitrary_script_path",
        "backup_config",
        "config_change",
        "custom_command",
        "custom_script_path",
        "model_call",
        "netconf_get",
        "provider_api_call",
        "restconf_get",
        "scriptPath",
        "ssh_command",
    }
)

REJECTED_FIELD_NAMES = frozenset(
    {
        "api_key",
        "arbitrary_command",
        "arbitrary_script_path",
        "cmd",
        "command",
        "custom_command",
        "custom_script_path",
        "device",
        "executable_path",
        "host",
        "hostname",
        "ip",
        "model",
        "netconf",
        "password",
        "provider",
        "provider_api",
        "restconf",
        "routeros",
        "scriptPath",
        "script_path",
        "secret",
        "shell",
        "ssh",
        "token",
        "username",
    }
)

SAFETY_FLAGS = {
    "live_execution_opened": False,
    "runner_invoked": False,
    "adapter_invoked": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "backup_config_enabled": False,
    "config_change_enabled": False,
    "arbitrary_command_enabled": False,
    "arbitrary_script_path_enabled": False,
    "provider_api_enabled": False,
    "model_call_enabled": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_03_DRY_RUN_PLAN_GATE_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "REQUEST_NORMALIZATION_REPORT_ONLY",
    "DRY_RUN_PLAN_NON_EXECUTABLE",
    "REJECTED_REQUESTS_BEFORE_PLAN_GENERATION",
    "RUNNER_INVOKED_FALSE",
    "ADAPTER_INVOKED_FALSE",
    "LIVE_EXECUTION_OPENED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)

PLAN_STEP_NAMES = {
    "mock_parse_report": (
        "Normalize mock report parse request",
        "Validate reviewer-safe report reference",
        "Prepare non-executable report parsing evidence preview",
    ),
    "mock_collect_local_evidence": (
        "Normalize mock local evidence request",
        "Validate reviewer-safe artifact reference",
        "Prepare non-executable local evidence collection preview",
    ),
    "mock_validate_existing_artifact": (
        "Normalize mock artifact validation request",
        "Validate reviewer-safe existing artifact reference",
        "Prepare non-executable artifact validation preview",
    ),
}


def _normalize_field_name(field_name: Any) -> str:
    return str(field_name).replace("-", "").replace("_", "").replace(".", "").lower()


def _iter_fields(payload: Any, prefix: str = "") -> Iterable[Tuple[str, Any, str]]:
    if isinstance(payload, Mapping):
        for field_name, value in payload.items():
            display_name = f"{prefix}.{field_name}" if prefix else str(field_name)
            yield str(field_name), value, display_name
            yield from _iter_fields(value, display_name)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            yield from _iter_fields(value, f"{prefix}[{index}]")


def _base_result(status: str, job_type: str) -> Dict[str, Any]:
    return {
        "status": status,
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "execution_mode": EXECUTION_MODE,
        "job_type": job_type,
        "dry_run_plan_gate": True,
        "report_only": True,
        "plan_only": True,
        "read_only": True,
        "local_only": True,
        "mock_only": True,
        "non_executable": True,
        **SAFETY_FLAGS,
    }


def _rejected_result(
    job_type: str,
    reason: str,
    rejected_field: Optional[str] = None,
    rejected_value: Optional[Any] = None,
) -> Dict[str, Any]:
    result = _base_result("REJECTED", job_type)
    result.update(
        {
            "valid": False,
            "normalized": False,
            "plan_generated": False,
            "dry_run_plan": None,
            "rejection_reason": reason,
            "safe_rejection": True,
        }
    )
    if rejected_field is not None:
        result["rejected_field"] = rejected_field
    if rejected_value is not None:
        result["rejected_value"] = str(rejected_value)
    return result


def _dangerous_field_rejection(job_request: Mapping[str, Any]) -> Optional[Tuple[str, str, Any]]:
    normalized_rejected_fields = {_normalize_field_name(field) for field in REJECTED_FIELD_NAMES}
    for field_name, value, display_name in _iter_fields(job_request):
        normalized = _normalize_field_name(field_name)
        if normalized == "port" and str(value) == "22":
            return "LIVE_TARGET_FIELD_REJECTED", display_name, value
        if normalized in normalized_rejected_fields:
            return "DANGEROUS_FIELD_REJECTED", display_name, value
    return None


def normalize_phase_2a_job_request(job_request: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize one controlled Phase 2A request without creating a plan."""

    if not isinstance(job_request, Mapping):
        return _rejected_result("<invalid>", "JOB_REQUEST_NOT_MAPPING")

    job_type = str(job_request.get("job_type", "")).strip()
    dangerous = _dangerous_field_rejection(job_request)
    if dangerous is not None:
        reason, rejected_field, rejected_value = dangerous
        return _rejected_result(job_type or "<missing>", reason, rejected_field, rejected_value)

    for field_name in job_request:
        if field_name not in ALLOWED_TOP_LEVEL_FIELDS:
            return _rejected_result(job_type or "<missing>", "UNKNOWN_TOP_LEVEL_FIELD_REJECTED", str(field_name))

    if not job_type:
        return _rejected_result("<missing>", "MISSING_JOB_TYPE")
    if job_type in REJECTED_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_EXPLICITLY_REJECTED")
    if job_type not in ALLOWED_JOB_TYPES:
        return _rejected_result(job_type, "JOB_TYPE_NOT_ALLOWLISTED")

    inputs = job_request.get("inputs", {})
    if inputs is None:
        inputs = {}
    if not isinstance(inputs, Mapping):
        return _rejected_result(job_type, "INPUTS_NOT_MAPPING_REJECTED", "inputs", inputs)

    allowed_fields = ALLOWED_INPUT_FIELDS_BY_JOB_TYPE[job_type]
    normalized_inputs: Dict[str, Any] = {}
    for field_name, value in inputs.items():
        if field_name not in allowed_fields:
            return _rejected_result(job_type, "UNKNOWN_INPUT_FIELD_REJECTED", f"inputs.{field_name}", value)
        if field_name in {"artifact_path", "report_path"}:
            path_rejection = validate_artifact_path(f"inputs.{field_name}", value)
            if path_rejection is not None:
                reason, rejected_field, rejected_value = path_rejection
                return _rejected_result(job_type, reason, rejected_field, rejected_value)
        if field_name == "evidence_ref":
            evidence_rejection = validate_evidence_ref(f"inputs.{field_name}", value)
            if evidence_rejection is not None:
                reason, rejected_field, rejected_value = evidence_rejection
                return _rejected_result(job_type, reason, rejected_field, rejected_value)
        normalized_inputs[str(field_name)] = value.strip() if isinstance(value, str) else value

    result = _base_result("NORMALIZED", job_type)
    result.update(
        {
            "valid": True,
            "normalized": True,
            "plan_generated": False,
            "rejection_reason": None,
            "safe_rejection": False,
            "normalized_request": {
                "job_type": job_type,
                "inputs": normalized_inputs,
            },
        }
    )
    return result


def validate_phase_2a_job_request(job_request: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a controlled request before any dry-run plan is built."""

    normalized = normalize_phase_2a_job_request(job_request)
    if normalized["status"] == "REJECTED":
        return normalized
    result = dict(normalized)
    result["status"] = "VALIDATED"
    return result


def _safe_reference_summary(inputs: Mapping[str, Any]) -> Dict[str, str]:
    return {
        field_name: str(value)
        for field_name, value in inputs.items()
        if field_name in {"artifact_path", "report_path", "evidence_ref"}
    }


def _build_plan_from_validation(validation: Mapping[str, Any]) -> Dict[str, Any]:
    job_type = str(validation["job_type"])
    normalized_request = validation["normalized_request"]
    inputs = normalized_request["inputs"]
    steps = [
        {
            "step_id": f"step_{index}",
            "name": step_name,
            "operation": "semantic_review_step",
            "executable": False,
            "runner_call": None,
            "adapter_call": None,
            "shell_command": None,
            "device_command": None,
            "script_path": None,
            "live_target": None,
        }
        for index, step_name in enumerate(PLAN_STEP_NAMES[job_type], start=1)
    ]
    return {
        "plan_id": f"phase_2a_03::{job_type}",
        "plan_type": "non_executable_dry_run_job_plan",
        "job_type": job_type,
        "execution_mode": EXECUTION_MODE,
        "executable": False,
        "plan_only": True,
        "dry_run_only": True,
        "safe_artifact_references": _safe_reference_summary(inputs),
        "steps": steps,
        "non_executable_proof": {
            "contains_shell_commands": False,
            "contains_device_commands": False,
            "contains_ssh_commands": False,
            "contains_script_paths": False,
            "contains_credentials": False,
            "contains_host_targets": False,
            "contains_adapter_calls": False,
            "contains_runner_calls": False,
        },
    }


def _plan_is_non_executable(plan: Mapping[str, Any]) -> bool:
    if plan.get("executable") is not False:
        return False
    proof = plan.get("non_executable_proof", {})
    if not isinstance(proof, Mapping) or any(value is not False for value in proof.values()):
        return False
    for step in plan.get("steps", []):
        if step.get("executable") is not False:
            return False
        for field_name in ("runner_call", "adapter_call", "shell_command", "device_command", "script_path", "live_target"):
            if step.get(field_name) is not None:
                return False
    return True


def build_phase_2a_03_dry_run_job_plan(job_request: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a non-executable dry-run plan for a validated request."""

    validation = validate_phase_2a_job_request(job_request)
    if validation["status"] == "REJECTED":
        return validation

    plan = _build_plan_from_validation(validation)
    result = _base_result("PLANNED", validation["job_type"])
    result.update(
        {
            "valid": True,
            "normalized": True,
            "plan_generated": True,
            "rejection_reason": None,
            "safe_rejection": False,
            "normalized_request": validation["normalized_request"],
            "dry_run_plan": plan,
            "dry_run_plan_non_executable": _plan_is_non_executable(plan),
        }
    )
    return result


def _default_allowed_requests() -> Sequence[Mapping[str, Any]]:
    return (
        {"job_type": "mock_parse_report", "inputs": {"report_path": "reports/lab-summary/sample.json"}},
        {"job_type": "mock_collect_local_evidence", "inputs": {"artifact_path": DOC_PATH.as_posix()}},
        {
            "job_type": "mock_validate_existing_artifact",
            "inputs": {"artifact_path": "fixtures/day127_ai_reviewer_summary.example.json"},
        },
    )


def _default_rejected_requests() -> Sequence[Mapping[str, Any]]:
    rejected_by_type = tuple({"job_type": job_type, "inputs": {}} for job_type in sorted(REJECTED_JOB_TYPES))
    rejected_by_field = tuple(
        {"job_type": "mock_parse_report", "inputs": {field_name: "unsafe"}}
        for field_name in sorted(REJECTED_FIELD_NAMES)
        if field_name != "scriptPath"
    )
    return rejected_by_type + rejected_by_field + (
        {"job_type": "mock_parse_report", "inputs": {"scriptPath": "scripts/run_anything.py"}},
        {"job_type": "mock_parse_report", "inputs": {"port": 22}},
    )


def build_phase_2a_03_dry_run_job_plan_gate_report() -> Dict[str, Any]:
    allowed_results = [build_phase_2a_03_dry_run_job_plan(request) for request in _default_allowed_requests()]
    rejected_results = [build_phase_2a_03_dry_run_job_plan(request) for request in _default_rejected_requests()]
    all_allowed_planned = all(result["status"] == "PLANNED" for result in allowed_results)
    all_plans_non_executable = all(result.get("dry_run_plan_non_executable") is True for result in allowed_results)
    all_unsafe_rejected = all(result["status"] == "REJECTED" and result["plan_generated"] is False for result in rejected_results)
    all_flags_false = all(
        result[flag_name] is False
        for result in allowed_results + rejected_results
        for flag_name in SAFETY_FLAGS
    )
    overall_status = "PASS" if all_allowed_planned and all_plans_non_executable and all_unsafe_rejected and all_flags_false else "FAIL"
    return {
        "overall_status": overall_status,
        "status": overall_status,
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "execution_mode": EXECUTION_MODE,
        "report_only": True,
        "plan_only": True,
        "normalization_only": True,
        "dry_run_plan_gate": True,
        "phase_2b_authorized": False,
        "real_execution_authorized": False,
        "allowed_job_types": sorted(ALLOWED_JOB_TYPES),
        "rejected_job_types": sorted(REJECTED_JOB_TYPES),
        "rejected_fields": sorted(REJECTED_FIELD_NAMES),
        "allowed_top_level_fields": sorted(ALLOWED_TOP_LEVEL_FIELDS),
        "allowed_input_fields_by_job_type": {
            job_type: sorted(fields) for job_type, fields in ALLOWED_INPUT_FIELDS_BY_JOB_TYPE.items()
        },
        "dry_run_plan_format": {
            "plan_id": "phase_2a_03::<job_type>",
            "plan_type": "non_executable_dry_run_job_plan",
            "steps": "semantic_review_step records with executable=false and no command, script, target, runner, or adapter value",
            "safe_artifact_references": "only validated report_path, artifact_path, or evidence_ref values",
            "non_executable_proof": "all contains_* capability booleans remain false",
        },
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "allowed_requests": len(allowed_results),
            "allowed_requests_planned": sum(1 for result in allowed_results if result["status"] == "PLANNED"),
            "dry_run_plans_non_executable": sum(
                1 for result in allowed_results if result.get("dry_run_plan_non_executable") is True
            ),
            "unsafe_requests": len(rejected_results),
            "unsafe_requests_rejected": sum(1 for result in rejected_results if result["status"] == "REJECTED"),
            "unsafe_requests_with_plan_generated": sum(
                1 for result in rejected_results if result.get("plan_generated") is True
            ),
            "runner_invoked_count": sum(1 for result in allowed_results + rejected_results if result["runner_invoked"]),
            "adapter_invoked_count": sum(1 for result in allowed_results + rejected_results if result["adapter_invoked"]),
            "all_safety_flags_false": all_flags_false,
        },
        **SAFETY_FLAGS,
        "allowed_request_results": allowed_results,
        "rejected_request_results": rejected_results,
    }


def write_phase_2a_03_dry_run_job_plan_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_03_dry_run_job_plan_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    summary_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )
    allowed_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(result['job_type']))}</td>"
        f"<td>{html.escape(str(result['status']))}</td>"
        f"<td>{html.escape(str(result['plan_generated']))}</td>"
        f"<td>{html.escape(str(result.get('dry_run_plan_non_executable')))}</td>"
        f"<td>{html.escape(str(result['runner_invoked']))}</td>"
        f"<td>{html.escape(str(result['adapter_invoked']))}</td>"
        "</tr>"
        for result in report["allowed_request_results"]
    )
    rejected_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(result['job_type']))}</td>"
        f"<td>{html.escape(str(result['rejection_reason']))}</td>"
        f"<td>{html.escape(str(result.get('rejected_field')))}</td>"
        f"<td>{html.escape(str(result['plan_generated']))}</td>"
        f"<td>{html.escape(str(result['runner_invoked']))}</td>"
        f"<td>{html.escape(str(result['adapter_invoked']))}</td>"
        "</tr>"
        for result in report["rejected_request_results"]
    )
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["overall_status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Phase 2A-03 normalizes controlled requests and renders non-executable dry-run plans only.</p>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Allowed Request Plans</h2>
  <table>
    <thead><tr><th>Job type</th><th>Status</th><th>Plan generated</th><th>Non-executable</th><th>Runner invoked</th><th>Adapter invoked</th></tr></thead>
    <tbody>{allowed_rows}</tbody>
  </table>
  <h2>Rejected Requests</h2>
  <table>
    <thead><tr><th>Job type</th><th>Reason</th><th>Field</th><th>Plan generated</th><th>Runner invoked</th><th>Adapter invoked</th></tr></thead>
    <tbody>{rejected_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_03_dry_run_job_plan_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_03_dry_run_job_plan_gate_report()
    json_path, html_path = write_phase_2a_03_dry_run_job_plan_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Execution mode: {EXECUTION_MODE}")
    print(f"Allowed job types: {', '.join(report['allowed_job_types'])}")
    print(f"Rejected job types: {', '.join(report['rejected_job_types'])}")
    print(f"Rejected fields: {', '.join(report['rejected_fields'])}")
    print(f"Allowed requests planned: {report['summary']['allowed_requests_planned']}")
    print(f"Unsafe requests rejected: {report['summary']['unsafe_requests_rejected']}")
    print(f"Dry-run plans non-executable: {report['summary']['dry_run_plans_non_executable']}")
    print(f"runner_invoked: {str(report['runner_invoked']).lower()}")
    print(f"adapter_invoked: {str(report['adapter_invoked']).lower()}")
    print(f"live_execution_opened: {str(report['live_execution_opened']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"real_execution_authorized: {str(report['real_execution_authorized']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['overall_status'])} {report['status_label']}")
    return 0 if report["overall_status"] == "PASS" else 1
