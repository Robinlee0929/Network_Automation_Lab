"""Day89 real adapter safety boundary spec.

This module locks the pre-implementation safety boundary for a future real
read-only adapter. It is deterministic design evidence only: no SSH, RouterOS
transport, device connection, command execution, or adapter implementation is
provided here.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "real-adapter-safety-boundary-spec"
TITLE = "Real Adapter Safety Boundary Spec"
PHASE = "DESIGN_ONLY"
REPORT_JSON = Path("reports") / "lab-summary" / "day89_real_adapter_safety_boundary_spec.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day89_real_adapter_safety_boundary_spec.html"

BLOCKED_CAPABILITIES = (
    "configuration changes",
    "firewall changes",
    "interface disable/enable",
    "reboot/reset",
    "package install/update",
    "password/secret export",
    "arbitrary command execution",
    "write-mode SSH sessions",
    "command shell escape",
    "file upload to devices",
    "destructive RouterOS commands",
    "fallback to non-allowlisted commands",
)

ALLOWED_CAPABILITIES = (
    "load static safety boundary spec",
    "validate a future read-only command against allowlist metadata",
    "classify a candidate command as allowed/blocked",
    "produce evidence-only reports",
    "preserve deterministic output",
    "no network side effects",
)

REQUIRED_INVARIANTS = (
    "default deny",
    "no command may run unless allowlisted",
    "no command may mutate device state",
    "no secret-bearing output may be stored unredacted",
    "every future live read-only run must produce evidence",
    "every future live read-only run must be reviewer-gated",
    "adapter errors must fail closed",
    "design-only reports must not imply live readiness",
)

FUTURE_ENTRY_CONDITIONS = (
    "Day89 safety boundary report is PASS and reviewed.",
    "A positive read-only command allowlist exists with command identity, rationale, expected output class, and redaction policy.",
    "Reviewer approval envelope is required for every future live read-only request.",
    "Future implementation remains read-only, allowlisted, evidence-producing, and fail-closed.",
    "No arbitrary command input surface is exposed in runner or dashboard.",
    "Tests prove no write, destructive, shell escape, upload, or fallback command can cross the adapter boundary.",
)

REQUIRED_FALSE_FLAGS = (
    "implementation_allowed",
    "live_device_access_allowed",
    "ssh_allowed",
    "config_change_allowed",
    "command_execution_allowed",
)


def build_future_allowed_behavior() -> Dict[str, Any]:
    return {
        "scope": "future read-only evidence collection only",
        "allowed_only_after_future_gate": True,
        "transport_implementation_in_day89": False,
        "adapter_implementation_in_day89": False,
        "behaviors": [
            {
                "behavior": "read-only command classification",
                "day89_status": "SPEC_ONLY",
                "future_requirement": "Classify only commands present in reviewed allowlist metadata.",
            },
            {
                "behavior": "evidence collection",
                "day89_status": "SPEC_ONLY",
                "future_requirement": "Collect evidence only after reviewer gate, redaction policy, and fail-closed handling exist.",
            },
            {
                "behavior": "report writing",
                "day89_status": "ALLOWED",
                "future_requirement": "Reports remain deterministic and reviewer-visible.",
            },
        ],
    }


def build_blocked_behavior() -> List[Dict[str, Any]]:
    return [
        {
            "capability": capability,
            "allowed": False,
            "decision": "BLOCKED",
            "reason": "Outside the Day89 pre-implementation safety boundary.",
        }
        for capability in BLOCKED_CAPABILITIES
    ]


def build_reviewer_gate_behavior() -> Dict[str, Any]:
    return {
        "reviewer_decision_required": True,
        "gate_position": "before any future live read-only adapter request",
        "approval_is_execution_unlock": False,
        "approval_scope": "single reviewed allowlisted read-only evidence request only",
        "required_fields": [
            "reviewer_id_or_alias",
            "approval_envelope_id",
            "target_device_alias",
            "allowlist_command_id",
            "normalized_command",
            "risk_classification",
            "evidence_required",
            "redaction_required",
            "expires_at",
        ],
        "fail_closed_conditions": [
            "missing approval envelope",
            "expired approval envelope",
            "command mismatch",
            "target mismatch",
            "allowlist metadata mismatch",
            "redaction policy missing",
        ],
    }


def build_evidence_requirements() -> Dict[str, Any]:
    return {
        "evidence_required_for_future_live_readonly": True,
        "day89_collects_device_evidence": False,
        "required_future_fields": [
            "request_id",
            "approval_envelope_id",
            "adapter_name",
            "target_device_alias",
            "allowlist_command_id",
            "normalized_command",
            "policy_decision",
            "started_at",
            "completed_at",
            "duration_ms",
            "stdout_digest",
            "stderr_digest",
            "redaction_applied",
            "error_code",
            "correlation_id",
        ],
        "storage_policy": "redacted output or digest-only evidence; never unredacted secret-bearing output",
    }


def build_failure_handling() -> Dict[str, Any]:
    return {
        "default_result": "DENY",
        "adapter_errors_fail_closed": True,
        "fallback_to_non_allowlisted_commands": False,
        "retry_policy_day89": "not implemented",
        "future_error_classes": [
            "COMMAND_NOT_ALLOWLISTED",
            "MUTATION_OR_WRITE_TOKEN_DETECTED",
            "REVIEWER_GATE_MISSING",
            "REDACTION_POLICY_MISSING",
            "TRANSPORT_UNAVAILABLE",
            "TIMEOUT",
            "ADAPTER_NOT_IMPLEMENTED",
        ],
        "operator_message": "Failure must stop before command execution and produce reviewer-visible evidence.",
    }


def build_redaction_requirements() -> Dict[str, Any]:
    return {
        "redaction_required": True,
        "store_unredacted_secret_output": False,
        "secret_markers": [
            "password",
            "secret",
            "private-key",
            "private_key",
            "token",
            "certificate",
            "preshared-key",
        ],
        "future_policy": "Secret-bearing output must be rejected or redacted before evidence storage.",
    }


def build_audit_report_requirements() -> Dict[str, Any]:
    return {
        "audit_required": True,
        "deterministic_design_report_required": True,
        "dashboard_visibility": "static read-only report visibility only",
        "live_action_button_allowed": False,
        "post_route_allowed": False,
        "command_input_control_allowed": False,
        "required_report_outputs": [REPORT_JSON.as_posix(), REPORT_HTML.as_posix()],
    }


def validate_real_adapter_safety_boundary_spec(report: Dict[str, Any]) -> List[str]:
    """Return validation errors for the Day89 safety boundary report."""
    errors: List[str] = []
    if report.get("day") != 89:
        errors.append("day must be 89.")
    if report.get("title") != TITLE:
        errors.append("title must match Day89.")
    if report.get("phase") != PHASE:
        errors.append("phase must be DESIGN_ONLY.")
    if report.get("status") != "PASS":
        errors.append("status must be PASS.")
    if report.get("safety_boundary_locked") is not True:
        errors.append("safety_boundary_locked must be true.")
    if report.get("reviewer_decision_required") is not True:
        errors.append("reviewer_decision_required must be true.")
    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")

    blocked = {item.get("capability") for item in report.get("blocked_capabilities", [])}
    for capability in BLOCKED_CAPABILITIES:
        if capability not in blocked:
            errors.append(f"blocked capability missing: {capability}.")

    allowed = {item.get("capability") for item in report.get("allowed_capabilities", [])}
    for capability in ALLOWED_CAPABILITIES:
        if capability not in allowed:
            errors.append(f"allowed capability missing: {capability}.")
    if any("implementation" in str(item).lower() and "no network side effects" not in str(item).lower() for item in allowed):
        errors.append("allowed capabilities must not include live implementation.")

    invariants = set(report.get("required_invariants", []))
    for invariant in REQUIRED_INVARIANTS:
        if invariant not in invariants:
            errors.append(f"required invariant missing: {invariant}.")

    audit = report.get("audit_report_requirements", {})
    if audit.get("live_action_button_allowed") is not False:
        errors.append("live action button must remain blocked.")
    if audit.get("post_route_allowed") is not False:
        errors.append("dashboard POST route must remain blocked.")
    return errors


def build_real_adapter_safety_boundary_spec_report() -> Dict[str, Any]:
    """Build the deterministic Day89 safety boundary report."""
    report: Dict[str, Any] = {
        "day": 89,
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "phase": PHASE,
        "status": "PASS",
        "implementation_allowed": False,
        "live_device_access_allowed": False,
        "ssh_allowed": False,
        "config_change_allowed": False,
        "command_execution_allowed": False,
        "command_execution_exception": "Future read-only allowlist commands may be documented later, but Day89 executes none.",
        "safety_boundary_locked": True,
        "adapter_scope": "read-only evidence collection only",
        "reviewer_decision_required": True,
        "blocked_capabilities": build_blocked_behavior(),
        "allowed_capabilities": [
            {
                "capability": capability,
                "allowed": True,
                "scope": "SPEC_ONLY",
            }
            for capability in ALLOWED_CAPABILITIES
        ],
        "required_invariants": list(REQUIRED_INVARIANTS),
        "future_entry_conditions": list(FUTURE_ENTRY_CONDITIONS),
        "future_allowed_behavior": build_future_allowed_behavior(),
        "reviewer_gate_behavior": build_reviewer_gate_behavior(),
        "evidence_requirements": build_evidence_requirements(),
        "failure_handling": build_failure_handling(),
        "redaction_requirements": build_redaction_requirements(),
        "audit_report_requirements": build_audit_report_requirements(),
        "day88_handoff": {
            "source": "Real Read-only Executor Adapter Design Draft",
            "day88_redone": False,
            "day89_boundary": "Pre-implementation safety boundary lock.",
        },
        "day90_entry_note": (
            "Day90 may plan implementation only if the Day89 boundary remains "
            "satisfied; any future adapter must remain read-only, allowlisted, "
            "reviewer-gated, evidence-producing, and fail-closed."
        ),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day89 locks the safety boundary before any real adapter implementation. "
            "It does not implement SSH, RouterOS connection, live read-only commands, "
            "arbitrary command execution, or device configuration changes."
        ),
    }
    validation_errors = validate_real_adapter_safety_boundary_spec(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _capability_rows(items: List[Dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item['capability']))}</td>"
        f"<td>{html.escape(json.dumps(item['allowed']))}</td>"
        f"<td>{html.escape(str(item.get('scope') or item.get('decision') or ''))}</td>"
        "</tr>"
        for item in items
    )


def write_real_adapter_safety_boundary_spec_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write the static Day89 reviewer HTML report."""
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
  <p><strong>Result:</strong> {html.escape(report['status'])} / {html.escape(report['phase'])}</p>
  <p><strong>Boundary locked:</strong> {html.escape(json.dumps(report['safety_boundary_locked']))}</p>
  <p><strong>Safety:</strong> pre-implementation boundary only; no SSH, RouterOS connection, live command execution, or device changes.</p>
  <h2>Locked Flags</h2>
  <table>
    <tbody>
      <tr><th>Implementation allowed</th><td>{html.escape(json.dumps(report['implementation_allowed']))}</td></tr>
      <tr><th>Live device access allowed</th><td>{html.escape(json.dumps(report['live_device_access_allowed']))}</td></tr>
      <tr><th>SSH allowed</th><td>{html.escape(json.dumps(report['ssh_allowed']))}</td></tr>
      <tr><th>Config change allowed</th><td>{html.escape(json.dumps(report['config_change_allowed']))}</td></tr>
      <tr><th>Command execution allowed</th><td>{html.escape(json.dumps(report['command_execution_allowed']))}</td></tr>
      <tr><th>Reviewer decision required</th><td>{html.escape(json.dumps(report['reviewer_decision_required']))}</td></tr>
    </tbody>
  </table>
  <h2>Allowed Spec-Level Capabilities</h2>
  <table><thead><tr><th>Capability</th><th>Allowed</th><th>Scope</th></tr></thead><tbody>{_capability_rows(report['allowed_capabilities'])}</tbody></table>
  <h2>Blocked Capabilities</h2>
  <table><thead><tr><th>Capability</th><th>Allowed</th><th>Decision</th></tr></thead><tbody>{_capability_rows(report['blocked_capabilities'])}</tbody></table>
  <h2>Required Invariants</h2>
  <ul>{_html_list(report['required_invariants'])}</ul>
  <h2>Future Entry Conditions</h2>
  <ul>{_html_list(report['future_entry_conditions'])}</ul>
  <h2>Evidence And Failure Handling</h2>
  <p><strong>Evidence required:</strong> {html.escape(json.dumps(report['evidence_requirements']['evidence_required_for_future_live_readonly']))}</p>
  <p><strong>Day89 collects device evidence:</strong> {html.escape(json.dumps(report['evidence_requirements']['day89_collects_device_evidence']))}</p>
  <p><strong>Adapter errors fail closed:</strong> {html.escape(json.dumps(report['failure_handling']['adapter_errors_fail_closed']))}</p>
  <h2>Redaction And Audit</h2>
  <p>{html.escape(report['redaction_requirements']['future_policy'])}</p>
  <p><strong>Dashboard visibility:</strong> {html.escape(report['audit_report_requirements']['dashboard_visibility'])}</p>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_real_adapter_safety_boundary_spec_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day89 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_real_adapter_safety_boundary_spec_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_real_adapter_safety_boundary_spec_html(safe_report, html_path)
    return json_path, html_path
