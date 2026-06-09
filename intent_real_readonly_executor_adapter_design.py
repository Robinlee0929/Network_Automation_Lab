"""Day88 real read-only executor adapter design draft.

This module defines the future real read-only adapter boundary as deterministic
design evidence only. It does not implement transport, connect to devices, or
run live commands.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "readonly-executor-adapter-design"
TITLE = "Real Read-only Executor Adapter Design Draft"
PHASE_STATE = "DESIGN_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day88_real_readonly_executor_adapter_design.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day88_real_readonly_executor_adapter_design.html"

ALLOWLIST_COMMANDS = (
    "/system/resource/print",
    "/system/identity/print",
    "/interface/print",
    "/ip/address/print",
    "/ip/route/print",
    "/interface/vrrp/print",
)

FORBIDDEN_MUTATION_TOKENS = (
    "add",
    "set",
    "remove",
    "enable",
    "disable",
    "reboot",
    "reset-configuration",
    "import",
    "export",
    "password",
    "secret",
    "certificate",
    "user",
    "tool",
    "fetch",
    "script",
    "scheduler",
)

ERROR_CODES = (
    "POLICY_DENIED",
    "COMMAND_NOT_ALLOWLISTED",
    "MUTATION_TOKEN_DETECTED",
    "TIMEOUT",
    "CONNECTION_UNAVAILABLE",
    "AUTH_UNAVAILABLE",
    "ADAPTER_NOT_IMPLEMENTED",
    "OUTPUT_REDACTION_REQUIRED",
    "UNKNOWN_ERROR",
)

REQUIRED_FALSE_FLAGS = (
    "execution_supported",
    "ssh_supported",
    "routeros_connection_supported",
    "live_command_supported",
    "execution_unlock_supported",
    "dashboard_execute_button_supported",
)


@dataclass(frozen=True)
class ReadOnlyCommandSpec:
    spec_id: str
    platform_family: str
    raw_command_example: str
    normalized_command: str
    read_only_rationale: str
    requires_reviewer_approval_envelope: bool
    execution_enabled: bool


@dataclass(frozen=True)
class ReadOnlyTimeoutPolicy:
    default_timeout_seconds: int
    max_timeout_seconds: int
    retry_supported: bool
    retry_count: int
    timeout_result_status: str
    rationale: str


def normalize_command(command: str) -> str:
    """Normalize a future command string for design-time allowlist matching."""
    return " ".join(command.strip().lower().split())


def build_safety_boundary() -> Dict[str, Any]:
    return {
        "execution_supported": False,
        "ssh_supported": False,
        "routeros_connection_supported": False,
        "live_command_supported": False,
        "execution_unlock_supported": False,
        "dashboard_execute_button_supported": False,
        "adapter_implementation_present": False,
        "transport_implementation_present": False,
        "local_process_execution_supported": False,
        "config_json_required": False,
        "statements": [
            "Day88 does not unlock real read-only execution.",
            "Day88 only defines the contract for a future adapter.",
            "Day88 remains DESIGN_ONLY and cannot be changed by reviewer approval.",
        ],
    }


def build_command_specs() -> List[Dict[str, Any]]:
    return [
        asdict(
            ReadOnlyCommandSpec(
                spec_id=f"readonly-routeros-command-{index:02d}",
                platform_family="routeros_future_design_reference",
                raw_command_example=command,
                normalized_command=normalize_command(command),
                read_only_rationale="Inspection command listed for future design review only.",
                requires_reviewer_approval_envelope=True,
                execution_enabled=False,
            )
        )
        for index, command in enumerate(ALLOWLIST_COMMANDS, start=1)
    ]


def build_command_allowlist_design() -> Dict[str, Any]:
    return {
        "policy_type": "positive_allowlist",
        "blacklist_based": False,
        "allowlist_enforced_before_adapter_call": True,
        "normalization_required": True,
        "deny_by_default": True,
        "dashboard_direct_command_input_supported": False,
        "reviewer_approval_envelope_required_for_future_use": True,
        "execution_enabled": False,
        "commands": build_command_specs(),
        "normalized_commands": [normalize_command(command) for command in ALLOWLIST_COMMANDS],
        "matching_rules": [
            "Normalize command text before comparison.",
            "Only exact normalized commands listed in the positive allowlist may pass policy review.",
            "Any unlisted command is denied.",
            "Any command containing a mutation token is denied even when a prefix appears read-only.",
            "No dashboard surface may accept arbitrary command text for adapter use.",
        ],
        "sensitive_exclusions": [
            {
                "command": "export",
                "allowed": False,
                "reason": "May disclose sensitive configuration and secrets.",
            }
        ],
    }


def build_forbidden_command_policy() -> Dict[str, Any]:
    return {
        "mutation_token_policy": "deny_if_present_after_normalization",
        "tokens": list(FORBIDDEN_MUTATION_TOKENS),
        "case_sensitive": False,
        "deny_result": "MUTATION_TOKEN_DETECTED",
        "unknown_command_result": "COMMAND_NOT_ALLOWLISTED",
        "policy_decision_shape": {
            "name": "ReadOnlyPolicyDecision",
            "fields": [
                "request_id",
                "command_spec_id",
                "normalized_command",
                "allowed",
                "decision_code",
                "decision_reason",
                "reviewer_approval_envelope_id",
            ],
        },
    }


def build_adapter_design() -> Dict[str, Any]:
    return {
        "adapter_name": "future_real_readonly_routeros_adapter",
        "adapter_state": "NOT_IMPLEMENTED",
        "design_scope": "contract_and_boundary_draft_only",
        "transport_layer": "not_defined_in_day88",
        "connects_to_devices": False,
        "runs_commands": False,
        "concepts": [
            {
                "name": "ReadOnlyAdapterRequest",
                "purpose": "Carries a reviewed command spec reference, target alias, correlation id, and safety flags.",
                "required_fields": [
                    "request_id",
                    "device_alias",
                    "command_spec_id",
                    "normalized_command",
                    "reviewer_approval_envelope_id",
                    "timeout_policy",
                    "correlation_id",
                ],
            },
            {
                "name": "ReadOnlyAdapterResponse",
                "purpose": "Returns policy, timing, evidence, and error records without exposing raw sensitive output.",
                "required_fields": [
                    "request_id",
                    "adapter_name",
                    "status",
                    "policy_decision",
                    "evidence_record",
                    "error_record",
                    "timeout_applied",
                ],
            },
            {
                "name": "ReadOnlyCommandSpec",
                "purpose": "Defines one explicit read-only command candidate and review requirements.",
                "required_fields": list(ReadOnlyCommandSpec.__dataclass_fields__),
            },
            {
                "name": "ReadOnlyEvidenceRecord",
                "purpose": "Defines audit evidence fields for future adapter observations.",
            },
            {
                "name": "ReadOnlyErrorRecord",
                "purpose": "Defines stable error codes and reviewer-facing messages.",
            },
            {
                "name": "ReadOnlyTimeoutPolicy",
                "purpose": "Defines bounded timing behavior with no initial retries.",
                "required_fields": list(ReadOnlyTimeoutPolicy.__dataclass_fields__),
            },
            {
                "name": "ReadOnlyPolicyDecision",
                "purpose": "Records allow/deny result before any future adapter boundary.",
            },
        ],
    }


def build_evidence_contract() -> Dict[str, Any]:
    fields = [
        "request_id",
        "adapter_name",
        "device_alias",
        "command_spec_id",
        "normalized_command",
        "policy_decision",
        "started_at",
        "completed_at",
        "duration_ms",
        "stdout_digest",
        "stderr_digest",
        "raw_output_redacted",
        "redaction_applied",
        "timeout_applied",
        "error_code",
        "error_message",
        "correlation_id",
    ]
    return {
        "name": "ReadOnlyEvidenceRecord",
        "required_fields": fields,
        "stdout_collection_state": "NOT_COLLECTED_DESIGN_ONLY",
        "raw_output_policy": "not_collected_in_day88_example_only",
        "example_record": {
            "request_id": "day88-design-request-example",
            "adapter_name": "future_real_readonly_routeros_adapter",
            "device_alias": "example-device-alias-only",
            "command_spec_id": "readonly-routeros-command-01",
            "normalized_command": "/system/resource/print",
            "policy_decision": "DESIGN_ONLY_NOT_EVALUATED",
            "started_at": None,
            "completed_at": None,
            "duration_ms": None,
            "stdout_digest": None,
            "stderr_digest": None,
            "raw_output_redacted": "NOT_COLLECTED_DESIGN_ONLY_EXAMPLE_ONLY",
            "redaction_applied": False,
            "timeout_applied": False,
            "error_code": "ADAPTER_NOT_IMPLEMENTED",
            "error_message": "Day88 defines the evidence schema only; no device output was collected.",
            "correlation_id": "day88-design-correlation-example",
        },
    }


def build_error_contract() -> Dict[str, Any]:
    return {
        "name": "ReadOnlyErrorRecord",
        "codes": list(ERROR_CODES),
        "day88_current_error_code": "ADAPTER_NOT_IMPLEMENTED",
        "day88_current_state": "DESIGN_ONLY",
        "fields": [
            "error_code",
            "error_message",
            "policy_decision",
            "retryable",
            "safe_to_display",
            "correlation_id",
        ],
        "classification": {
            "POLICY_DENIED": "Policy stopped the request before adapter boundary.",
            "COMMAND_NOT_ALLOWLISTED": "Command was not present in the positive allowlist.",
            "MUTATION_TOKEN_DETECTED": "Command contained a forbidden mutation token.",
            "TIMEOUT": "Future adapter exceeded the bounded timeout policy.",
            "CONNECTION_UNAVAILABLE": "Future transport could not reach the device.",
            "AUTH_UNAVAILABLE": "Future credential or auth context was unavailable.",
            "ADAPTER_NOT_IMPLEMENTED": "Day88 design draft has no real adapter implementation.",
            "OUTPUT_REDACTION_REQUIRED": "Future output must be redacted before evidence storage.",
            "UNKNOWN_ERROR": "Unexpected future adapter error bucket.",
        },
    }


def build_timeout_contract() -> Dict[str, Any]:
    return asdict(
        ReadOnlyTimeoutPolicy(
            default_timeout_seconds=10,
            max_timeout_seconds=30,
            retry_supported=False,
            retry_count=0,
            timeout_result_status="TIMEOUT",
            rationale=(
                "Initial real read-only adapter design avoids retries so repeated "
                "device observation cannot disturb lab state."
            ),
        )
    )


def build_future_implementation_checklist() -> List[Dict[str, Any]]:
    return [
        {"item": "Write Day89 Real Adapter Safety Boundary Spec", "required_before_implementation": True},
        {"item": "Keep adapter disabled until a later explicit implementation gate", "required_before_implementation": True},
        {"item": "Validate positive allowlist and mutation token denial before any transport boundary", "required_before_implementation": True},
        {"item": "Require reviewer approval envelope for every future adapter request", "required_before_implementation": True},
        {"item": "Add output redaction and digest-only evidence storage before raw output handling", "required_before_implementation": True},
        {"item": "Add deterministic timeout handling with retry_supported=false for first implementation", "required_before_implementation": True},
        {"item": "Prove dashboard remains report-view only", "required_before_implementation": True},
    ]


def validate_real_readonly_executor_adapter_design(report: Dict[str, Any]) -> List[str]:
    """Return validation errors for the Day88 design-only report."""
    errors: List[str] = []
    if report.get("overall_status") != "PASS":
        errors.append("overall_status must be PASS.")
    if report.get("phase_state") != PHASE_STATE:
        errors.append("phase_state must be DESIGN_ONLY.")
    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
        if report.get("safety_boundary", {}).get(field) is not False:
            errors.append(f"safety_boundary {field} must be false.")
    allowlist = report.get("command_allowlist_design", {})
    if allowlist.get("policy_type") != "positive_allowlist":
        errors.append("command allowlist must be a positive_allowlist.")
    if allowlist.get("blacklist_based") is not False:
        errors.append("command allowlist must not be blacklist based.")
    if "export" in allowlist.get("normalized_commands", []):
        errors.append("export must not be allowlisted.")
    tokens = set(report.get("forbidden_command_policy", {}).get("tokens", []))
    for token in FORBIDDEN_MUTATION_TOKENS:
        if token not in tokens:
            errors.append(f"forbidden command policy missing token: {token}.")
    if "ADAPTER_NOT_IMPLEMENTED" not in report.get("error_contract", {}).get("codes", []):
        errors.append("error contract must include ADAPTER_NOT_IMPLEMENTED.")
    if report.get("timeout_contract", {}).get("retry_supported") is not False:
        errors.append("timeout retry_supported must be false.")
    evidence = report.get("evidence_contract", {})
    if evidence.get("stdout_collection_state") != "NOT_COLLECTED_DESIGN_ONLY":
        errors.append("evidence contract must not claim true stdout collection.")
    if evidence.get("example_record", {}).get("stdout_digest") is not None:
        errors.append("Day88 evidence example stdout_digest must stay null.")
    return errors


def build_real_readonly_executor_adapter_design_report() -> Dict[str, Any]:
    """Build the deterministic Day88 design-only adapter draft report."""
    safety_boundary = build_safety_boundary()
    report: Dict[str, Any] = {
        "day": 88,
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "overall_status": "PASS",
        "phase_state": PHASE_STATE,
        "execution_supported": False,
        "ssh_supported": False,
        "routeros_connection_supported": False,
        "live_command_supported": False,
        "dashboard_execute_button_supported": False,
        "execution_unlock_supported": False,
        "adapter_design": build_adapter_design(),
        "command_allowlist_design": build_command_allowlist_design(),
        "forbidden_command_policy": build_forbidden_command_policy(),
        "evidence_contract": build_evidence_contract(),
        "error_contract": build_error_contract(),
        "timeout_contract": build_timeout_contract(),
        "safety_boundary": safety_boundary,
        "future_implementation_checklist": build_future_implementation_checklist(),
        "day87_transition": {
            "day87_redone": False,
            "source_gate": "Day87 Read-only Executor Phase Gate Review",
            "day88_entry_state": "PASS / DESIGN_ONLY",
        },
        "day89_handoff": "Real Adapter Safety Boundary Spec",
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day88 does not unlock real read-only execution. Day88 only defines "
            "the contract for a future adapter."
        ),
    }
    validation_errors = validate_real_readonly_executor_adapter_design(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_status"] = "FAIL"
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _flag_rows(flags: Dict[str, Any]) -> str:
    return "".join(
        "<tr>"
        f"<th>{html.escape(str(key))}</th>"
        f"<td>{html.escape(json.dumps(value))}</td>"
        "</tr>"
        for key, value in flags.items()
        if isinstance(value, bool)
    )


def write_real_readonly_executor_adapter_design_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write the static Day88 reviewer HTML report."""
    allowlist = report["command_allowlist_design"]
    timeout = report["timeout_contract"]
    evidence = report["evidence_contract"]
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
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['phase_state'])}</p>
  <p><strong>Safety:</strong> design draft only; no adapter implementation, transport, device connection, or live command support.</p>
  <h2>Safety Boundary</h2>
  <table><tbody>{_flag_rows(report['safety_boundary'])}</tbody></table>
  <ul>{_html_list(report['safety_boundary']['statements'])}</ul>
  <h2>Positive Allowlist Design</h2>
  <table>
    <tbody>
      <tr><th>Policy type</th><td>{html.escape(allowlist['policy_type'])}</td></tr>
      <tr><th>Normalize first</th><td>{html.escape(json.dumps(allowlist['normalization_required']))}</td></tr>
      <tr><th>Deny by default</th><td>{html.escape(json.dumps(allowlist['deny_by_default']))}</td></tr>
      <tr><th>Allowed examples</th><td>{html.escape(', '.join(allowlist['normalized_commands']))}</td></tr>
      <tr><th>Forbidden tokens</th><td>{html.escape(', '.join(report['forbidden_command_policy']['tokens']))}</td></tr>
    </tbody>
  </table>
  <h2>Evidence Contract</h2>
  <p><strong>Collection state:</strong> {html.escape(evidence['stdout_collection_state'])}</p>
  <p><strong>Required fields:</strong> {html.escape(', '.join(evidence['required_fields']))}</p>
  <h2>Error And Timeout Contract</h2>
  <p><strong>Current Day88 state:</strong> {html.escape(report['error_contract']['day88_current_error_code'])} / {html.escape(report['error_contract']['day88_current_state'])}</p>
  <table>
    <tbody>
      <tr><th>Default timeout seconds</th><td>{timeout['default_timeout_seconds']}</td></tr>
      <tr><th>Max timeout seconds</th><td>{timeout['max_timeout_seconds']}</td></tr>
      <tr><th>Retry supported</th><td>{html.escape(json.dumps(timeout['retry_supported']))}</td></tr>
      <tr><th>Retry count</th><td>{timeout['retry_count']}</td></tr>
      <tr><th>Timeout result status</th><td>{html.escape(timeout['timeout_result_status'])}</td></tr>
    </tbody>
  </table>
  <h2>Future Checklist</h2>
  <ul>{_html_list([item['item'] for item in report['future_implementation_checklist']])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_real_readonly_executor_adapter_design_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day88 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_real_readonly_executor_adapter_design_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_real_readonly_executor_adapter_design_html(safe_report, html_path)
    return json_path, html_path
