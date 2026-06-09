"""Day84 read-only executor adapter interface contract.

This module defines the future read-only executor adapter boundary only. It
validates deterministic contract objects and writes reviewer evidence, but it
does not implement an executor, connect to devices, or run commands.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "readonly-executor-adapter-contract"
TITLE = "Day84 Read-only Executor Adapter Interface Contract"
CONTRACT_VERSION = "day84.readonly_executor_adapter_contract.v1"
CONTRACT_STATE = "LOCKED_REVIEW_ONLY_CONTRACT"
EXECUTION_MODE = "deterministic_contract_only_readonly_executor_adapter_boundary"
REPORT_JSON = Path("reports") / "lab-summary" / "day84_readonly_executor_adapter_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day84_readonly_executor_adapter_contract.html"

REQUIRED_TRUE_FLAGS = (
    "read_only_only",
    "dry_run_only",
)

REQUIRED_FALSE_FLAGS = (
    "allowed_to_execute",
    "ssh_allowed",
    "device_access_allowed",
    "live_command_allowed",
    "approval_unlock_supported",
    "execution_unlock_supported",
    "ai_api_allowed",
    "adapter_implementation_present",
)

ADDITIONAL_FALSE_FLAGS = (
    "device_connection_allowed",
    "live_execution_allowed",
    "mapped_task_execution_allowed",
    "dashboard_action_allowed",
    "network_change_allowed",
    "real_executor_present",
    "runnable_entrypoint_present",
    "runtime_transport_present",
    "subprocess_allowed",
    "config_json_required",
)

REQUIRED_REQUEST_FIELDS = (
    "request_id",
    "contract_version",
    "requested_task",
    "request_source",
    "target_scope",
    "input_payload",
    "safety_flags",
    "evidence_refs",
)

REQUIRED_RESPONSE_FIELDS = (
    "response_id",
    "request_id",
    "contract_version",
    "response_status",
    "output_contract",
    "execution_result",
    "commands_executed",
    "device_session",
    "safety_flags",
    "evidence_refs",
)

REQUIRED_CAPABILITY_FIELDS = (
    "capability_id",
    "contract_version",
    "adapter_family",
    "capability_kind",
    "supported_request_shapes",
    "supported_response_shapes",
    "supported_transports",
    "runnable_entrypoint",
    "implementation_module",
    "safety_flags",
    "blocked_runtime_surfaces",
)

REQUIRED_EVIDENCE_FIELDS = (
    "evidence_id",
    "contract_version",
    "source_days",
    "reference_paths",
    "review_purpose",
    "review_only",
    "safety_flags",
)

FORBIDDEN_TRANSPORTS = {
    "ssh",
    "paramiko",
    "netmiko",
    "scrapli",
    "socket",
    "telnet",
    "http_device_api",
    "routeros_api",
    "subprocess",
}


def adapter_safety_flags() -> Dict[str, bool]:
    """Return the locked Day84 adapter-boundary safety flags."""
    return {
        "read_only_only": True,
        "dry_run_only": True,
        "allowed_to_execute": False,
        "ssh_allowed": False,
        "device_access_allowed": False,
        "live_command_allowed": False,
        "approval_unlock_supported": False,
        "execution_unlock_supported": False,
        "ai_api_allowed": False,
        "adapter_implementation_present": False,
        "device_connection_allowed": False,
        "live_execution_allowed": False,
        "mapped_task_execution_allowed": False,
        "dashboard_action_allowed": False,
        "network_change_allowed": False,
        "real_executor_present": False,
        "runnable_entrypoint_present": False,
        "runtime_transport_present": False,
        "subprocess_allowed": False,
        "config_json_required": False,
    }


def build_adapter_request_shape() -> Dict[str, Any]:
    """Build the deterministic future adapter request contract shape."""
    return {
        "request_id": "day84-adapter-request-001",
        "contract_version": CONTRACT_VERSION,
        "requested_task": "show_interface_status",
        "request_source": "Day80 mock broker request data reference",
        "target_scope": {
            "scope_type": "future_adapter_target_reference_only",
            "target_ref": "mock_lab_device_group",
            "target_address": None,
            "credentials_ref": None,
            "live_device_identifier": None,
        },
        "input_payload": {
            "operation_id": "readonly_interface_status_snapshot",
            "parameters_schema": {
                "device_group_ref": "string",
                "include_admin_state": "boolean",
            },
            "example_parameters": {
                "device_group_ref": "mock_lab_device_group",
                "include_admin_state": True,
            },
            "command_text": None,
            "raw_device_command": None,
        },
        "safety_flags": adapter_safety_flags(),
        "evidence_refs": [
            "Day79 read-only task contract",
            "Day80 read-only execution broker skeleton",
            "Day83 read-only executor readiness gate",
            "Day84 adapter request shape fixture",
        ],
    }


def build_adapter_response_shape() -> Dict[str, Any]:
    """Build the deterministic future adapter response contract shape."""
    return {
        "response_id": "day84-adapter-response-001",
        "request_id": "day84-adapter-request-001",
        "contract_version": CONTRACT_VERSION,
        "response_status": "CONTRACT_ONLY_RESPONSE_EXAMPLE",
        "output_contract": {
            "output_kind": "structured_readonly_snapshot_placeholder",
            "records_schema": [
                {"field": "device_ref", "type": "string"},
                {"field": "interface_ref", "type": "string"},
                {"field": "observed_state", "type": "string"},
            ],
            "example_records": [],
            "fixture_only": True,
        },
        "execution_result": None,
        "commands_executed": [],
        "device_session": None,
        "safety_flags": adapter_safety_flags(),
        "evidence_refs": [
            "Day84 adapter response shape fixture",
            "No execution result is present because no executor exists",
        ],
    }


def build_adapter_capability_declaration_shape() -> Dict[str, Any]:
    """Build the deterministic future adapter capability declaration shape."""
    return {
        "capability_id": "day84-readonly-adapter-capability-contract-only",
        "contract_version": CONTRACT_VERSION,
        "adapter_family": "future_readonly_executor_adapter",
        "capability_kind": "interface_contract_only",
        "supported_request_shapes": [
            "adapter_request_shape.v1",
        ],
        "supported_response_shapes": [
            "adapter_response_shape.v1",
        ],
        "supported_transports": [
            "none_contract_only",
        ],
        "runnable_entrypoint": None,
        "implementation_module": None,
        "safety_flags": adapter_safety_flags(),
        "blocked_runtime_surfaces": [
            "ssh",
            "device_access",
            "live_command_execution",
            "subprocess_execution",
            "approval_unlock",
            "execution_unlock",
            "ai_api",
            "dashboard_action",
            "network_configuration_change",
        ],
    }


def build_adapter_evidence_reference_shape() -> Dict[str, Any]:
    """Build the deterministic reviewer evidence/reference shape."""
    return {
        "evidence_id": "day84-adapter-contract-evidence-001",
        "contract_version": CONTRACT_VERSION,
        "source_days": ["Day79", "Day80", "Day81", "Day82", "Day83", "Day84"],
        "reference_paths": [
            "docs/ai/intent_readonly_task_contract.md",
            "docs/ai/intent_readonly_execution_broker.md",
            "docs/ai/intent_broker_review_queue.md",
            "docs/ai/intent_reviewer_decision_audit_summary.md",
            "docs/ai/readonly_executor_readiness_gate.md",
            "docs/ai/intent_readonly_executor_adapter_contract.md",
            REPORT_JSON.as_posix(),
            REPORT_HTML.as_posix(),
        ],
        "review_purpose": (
            "Show the future read-only executor adapter input/output boundary "
            "without implementing an executor."
        ),
        "review_only": True,
        "safety_flags": adapter_safety_flags(),
    }


def build_validation_result_shape(validation_errors: Optional[List[str]] = None) -> Dict[str, Any]:
    """Build the deterministic validation result contract shape."""
    errors = list(validation_errors or [])
    return {
        "validation_id": "day84-adapter-contract-validation-001",
        "contract_version": CONTRACT_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "validation_scope": "contract_shapes_and_locked_safety_flags_only",
        "validation_errors": errors,
        "review_only": True,
        "safety_flags": adapter_safety_flags(),
    }


def build_adapter_contract_fixtures() -> Dict[str, Any]:
    """Build deterministic Day84 example fixtures for reviewer inspection."""
    return {
        "adapter_request_shape": build_adapter_request_shape(),
        "adapter_response_shape": build_adapter_response_shape(),
        "adapter_capability_declaration_shape": build_adapter_capability_declaration_shape(),
        "adapter_evidence_reference_shape": build_adapter_evidence_reference_shape(),
    }


def _validate_safety_flags(flags: Dict[str, Any], context: str) -> List[str]:
    errors: List[str] = []
    if not isinstance(flags, dict):
        return [f"{context} safety_flags must be an object."]
    for field in REQUIRED_TRUE_FLAGS:
        if flags.get(field) is not True:
            errors.append(f"{context} safety_flags {field} must be true.")
    for field in REQUIRED_FALSE_FLAGS + ADDITIONAL_FALSE_FLAGS:
        if flags.get(field) is not False:
            errors.append(f"{context} safety_flags {field} must be false.")
    return errors


def validate_adapter_request_shape(request: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for a Day84 request shape."""
    errors: List[str] = []
    for field in REQUIRED_REQUEST_FIELDS:
        if field not in request:
            errors.append(f"request missing required field: {field}.")
    errors.extend(_validate_safety_flags(request.get("safety_flags", {}), "request"))
    target_scope = request.get("target_scope", {})
    if target_scope.get("target_address") is not None:
        errors.append("request target_scope target_address must stay null.")
    if target_scope.get("credentials_ref") is not None:
        errors.append("request target_scope credentials_ref must stay null.")
    input_payload = request.get("input_payload", {})
    if input_payload.get("command_text") is not None:
        errors.append("request input_payload command_text must stay null.")
    if input_payload.get("raw_device_command") is not None:
        errors.append("request input_payload raw_device_command must stay null.")
    return errors


def validate_adapter_response_shape(response: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for a Day84 response shape."""
    errors: List[str] = []
    for field in REQUIRED_RESPONSE_FIELDS:
        if field not in response:
            errors.append(f"response missing required field: {field}.")
    errors.extend(_validate_safety_flags(response.get("safety_flags", {}), "response"))
    if response.get("execution_result") is not None:
        errors.append("response execution_result must stay null.")
    if response.get("commands_executed") != []:
        errors.append("response commands_executed must stay empty.")
    if response.get("device_session") is not None:
        errors.append("response device_session must stay null.")
    return errors


def validate_adapter_capability_declaration(declaration: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for a capability declaration."""
    errors: List[str] = []
    for field in REQUIRED_CAPABILITY_FIELDS:
        if field not in declaration:
            errors.append(f"capability declaration missing required field: {field}.")
    errors.extend(_validate_safety_flags(declaration.get("safety_flags", {}), "capability"))
    transports = {str(item).lower() for item in declaration.get("supported_transports", [])}
    forbidden = sorted(transports.intersection(FORBIDDEN_TRANSPORTS))
    if forbidden:
        errors.append("capability declaration contains forbidden transports: " + ", ".join(forbidden) + ".")
    if declaration.get("runnable_entrypoint") is not None:
        errors.append("capability declaration runnable_entrypoint must stay null.")
    if declaration.get("implementation_module") is not None:
        errors.append("capability declaration implementation_module must stay null.")
    if declaration.get("capability_kind") != "interface_contract_only":
        errors.append("capability declaration capability_kind must be interface_contract_only.")
    return errors


def validate_adapter_evidence_reference_shape(evidence: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for a Day84 evidence shape."""
    errors: List[str] = []
    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in evidence:
            errors.append(f"evidence missing required field: {field}.")
    errors.extend(_validate_safety_flags(evidence.get("safety_flags", {}), "evidence"))
    if evidence.get("review_only") is not True:
        errors.append("evidence review_only must be true.")
    evidence_text = json.dumps(evidence.get("source_days", []), sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82", "Day83", "Day84"):
        if day not in evidence_text:
            errors.append(f"evidence source_days must include {day}.")
    return errors


def validate_adapter_contract_fixtures(fixtures: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for all Day84 fixtures."""
    errors: List[str] = []
    errors.extend(validate_adapter_request_shape(fixtures.get("adapter_request_shape", {})))
    errors.extend(validate_adapter_response_shape(fixtures.get("adapter_response_shape", {})))
    errors.extend(
        validate_adapter_capability_declaration(
            fixtures.get("adapter_capability_declaration_shape", {})
        )
    )
    errors.extend(
        validate_adapter_evidence_reference_shape(
            fixtures.get("adapter_evidence_reference_shape", {})
        )
    )
    return errors


def build_readonly_executor_adapter_contract_report() -> Dict[str, Any]:
    """Build the Day84 contract-only adapter boundary report."""
    fixtures = build_adapter_contract_fixtures()
    validation_errors = validate_adapter_contract_fixtures(fixtures)
    validation_result_shape = build_validation_result_shape(validation_errors)
    flags = adapter_safety_flags()
    safety_invariants = {
        **flags,
        "contract_only_boundary": True,
        "review_only": True,
        "deterministic": True,
        "offline_only": True,
        "report_only": True,
        "request_shape_present": True,
        "response_shape_present": True,
        "capability_declaration_shape_present": True,
        "evidence_reference_shape_present": True,
        "validation_result_shape_present": True,
        "runner_writes_reports_only": True,
        "html_contains_execution_controls": False,
        "dashboard_post_route_added": False,
    }
    overall_status = "PASS" if not validation_errors else "FAIL"
    return {
        "day": "Day84",
        "title": TITLE,
        "task_name": TASK_NAME,
        "contract_version": CONTRACT_VERSION,
        "contract_state": CONTRACT_STATE,
        "execution_mode": EXECUTION_MODE,
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "adapter_boundary": {
            "boundary_type": "contract_only_boundary",
            "defines_future_adapter_contract": True,
            "implements_executor": False,
            "implements_adapter": False,
            "can_connect_to_devices": False,
            "can_execute_commands": False,
            "can_unlock_approval_or_execution": False,
        },
        "summary": {
            "request_shape_count": 1,
            "response_shape_count": 1,
            "capability_declaration_count": 1,
            "evidence_reference_count": 1,
            "validation_result_count": 1,
            "read_only_only_values": [flags["read_only_only"]],
            "dry_run_only_values": [flags["dry_run_only"]],
            "allowed_to_execute_values": [flags["allowed_to_execute"]],
            "ssh_allowed_values": [flags["ssh_allowed"]],
            "device_access_allowed_values": [flags["device_access_allowed"]],
            "live_command_allowed_values": [flags["live_command_allowed"]],
            "approval_unlock_supported_values": [flags["approval_unlock_supported"]],
            "execution_unlock_supported_values": [flags["execution_unlock_supported"]],
            "ai_api_allowed_values": [flags["ai_api_allowed"]],
            "adapter_implementation_present_values": [flags["adapter_implementation_present"]],
        },
        "adapter_request_shape": fixtures["adapter_request_shape"],
        "adapter_response_shape": fixtures["adapter_response_shape"],
        "adapter_capability_declaration_shape": fixtures["adapter_capability_declaration_shape"],
        "adapter_evidence_reference_shape": fixtures["adapter_evidence_reference_shape"],
        "adapter_safety_flags": flags,
        "validation_result_shape": validation_result_shape,
        "example_fixtures": fixtures,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "traceability_map": [
            {
                "day": "Day79",
                "role": "Defines read-only task contract and blocked action policy.",
                "artifact": "intent_readonly_task_contract",
            },
            {
                "day": "Day80",
                "role": "Defines a non-executing broker skeleton and mock request data.",
                "artifact": "intent_readonly_execution_broker",
            },
            {
                "day": "Day81",
                "role": "Defines review queue and decision state evidence.",
                "artifact": "intent_broker_review_queue",
            },
            {
                "day": "Day82",
                "role": "Exports reviewer decision audit evidence.",
                "artifact": "intent_reviewer_decision_audit_summary",
            },
            {
                "day": "Day83",
                "role": "Marks future adapter design readiness without enabling execution.",
                "artifact": "intent_readonly_executor_readiness_gate",
            },
            {
                "day": "Day84",
                "role": "Defines the read-only executor adapter interface contract only.",
                "artifact": "intent_readonly_executor_adapter_contract",
            },
        ],
        "safety_boundary": [
            "Contract-only adapter boundary.",
            "No executor implementation.",
            "No adapter implementation.",
            "No SSH.",
            "No device access.",
            "No live command execution.",
            "No subprocess execution.",
            "No OpenAI API or AI SDK runtime.",
            "No approval unlock.",
            "No execution unlock.",
            "No dashboard form, POST route, button, or action endpoint.",
            "No mapped task execution.",
            "No network configuration change.",
        ],
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "evidence_links_or_doc_refs": [
            "docs/ai/intent_readonly_executor_adapter_contract.md",
            "docs/roadmap/day84_readonly_executor_adapter_interface_contract.md",
            REPORT_JSON.as_posix(),
            REPORT_HTML.as_posix(),
        ],
        "final_safety_statement": (
            "Day84 defines the read-only executor adapter input/output contract "
            "only. It keeps execution, SSH, device access, AI API usage, approval "
            "unlock, execution unlock, dashboard action surfaces, and real adapter "
            "implementation locked off."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _flag_rows(flags: Dict[str, Any]) -> str:
    return "".join(
        "<tr>"
        f"<th>{html.escape(str(key))}</th>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for key, value in flags.items()
    )


def write_readonly_executor_adapter_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static reviewer-facing HTML report."""
    summary = report["summary"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>{html.escape(report['title'])}</h1>
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <p><strong>State:</strong> {html.escape(report['contract_state'])}</p>
  <p><strong>Safety:</strong> contract-only boundary; no executor or adapter implementation is present.</p>
  <h2>Contract Summary</h2>
  <table>
    <tbody>
      <tr><th>Request shapes</th><td>{summary['request_shape_count']}</td></tr>
      <tr><th>Response shapes</th><td>{summary['response_shape_count']}</td></tr>
      <tr><th>Capability declarations</th><td>{summary['capability_declaration_count']}</td></tr>
      <tr><th>Evidence references</th><td>{summary['evidence_reference_count']}</td></tr>
      <tr><th>Read-only-only values</th><td>{html.escape(str(summary['read_only_only_values']))}</td></tr>
      <tr><th>Dry-run-only values</th><td>{html.escape(str(summary['dry_run_only_values']))}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(summary['allowed_to_execute_values']))}</td></tr>
      <tr><th>SSH allowed values</th><td>{html.escape(str(summary['ssh_allowed_values']))}</td></tr>
      <tr><th>Device access allowed values</th><td>{html.escape(str(summary['device_access_allowed_values']))}</td></tr>
      <tr><th>Live command allowed values</th><td>{html.escape(str(summary['live_command_allowed_values']))}</td></tr>
      <tr><th>Adapter implementation present values</th><td>{html.escape(str(summary['adapter_implementation_present_values']))}</td></tr>
    </tbody>
  </table>
  <h2>Safety Flags</h2>
  <table><tbody>{_flag_rows(report['adapter_safety_flags'])}</tbody></table>
  <h2>Capability Declaration</h2>
  <table>
    <tbody>
      <tr><th>Capability ID</th><td>{html.escape(report['adapter_capability_declaration_shape']['capability_id'])}</td></tr>
      <tr><th>Capability kind</th><td>{html.escape(report['adapter_capability_declaration_shape']['capability_kind'])}</td></tr>
      <tr><th>Supported transports</th><td>{html.escape(str(report['adapter_capability_declaration_shape']['supported_transports']))}</td></tr>
      <tr><th>Runnable entrypoint</th><td>{html.escape(json.dumps(report['adapter_capability_declaration_shape']['runnable_entrypoint']))}</td></tr>
      <tr><th>Implementation module</th><td>{html.escape(json.dumps(report['adapter_capability_declaration_shape']['implementation_module']))}</td></tr>
    </tbody>
  </table>
  <h2>Safety Boundary</h2>
  <ul>{_html_list(report['safety_boundary'])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_readonly_executor_adapter_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day84 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_readonly_executor_adapter_contract_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_readonly_executor_adapter_contract_html(safe_report, html_path)
    return json_path, html_path
