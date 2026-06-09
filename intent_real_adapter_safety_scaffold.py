"""Day91 real adapter safety scaffold.

This module creates deterministic scaffold evidence after the Day90
CONDITIONAL_GO. It proves dangerous actions are structurally denied before any
real adapter, transport, SSH, RouterOS API, socket, subprocess device
operation, credential use, or live-read path exists.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "real-adapter-safety-scaffold"
TITLE = "Real Adapter Safety Scaffold"
STATUS = "SCAFFOLD_ONLY"
OVERALL_DECISION = "PASS"
REPORT_JSON = Path("reports") / "lab-summary" / "day91_real_adapter_safety_scaffold.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day91_real_adapter_safety_scaffold.html"

DANGEROUS_ACTION_CATEGORIES = (
    ("configuration_write", "configuration write"),
    ("firewall_change", "firewall change"),
    ("route_change", "route change"),
    ("interface_state_change", "interface disable/enable"),
    ("vrrp_modification", "VRRP modification"),
    ("wireguard_peer_modification", "WireGuard peer modification"),
    ("reboot", "reboot"),
    ("reset_configuration", "reset configuration"),
    ("raw_command_execution", "raw command execution"),
    ("device_file_transfer", "file upload/download to device"),
    ("credential_export", "credential export"),
    ("arbitrary_command_passthrough", "arbitrary command passthrough"),
)

READ_ONLY_CANDIDATE_CATEGORIES = (
    ("system_identity_read", "system identity read"),
    ("interface_print_read", "interface print/read"),
    ("ip_address_print_read", "IP address print/read"),
    ("route_print_read", "route print/read"),
    ("firewall_print_read", "firewall print/read"),
    ("log_read", "log read"),
    ("wireguard_peer_print_read", "WireGuard peer print/read"),
)

BLOCKED_CAPABILITIES = (
    "real adapter implementation",
    "SSH client",
    "RouterOS API client",
    "socket transport",
    "subprocess device operation",
    "live-read path",
    "credential loading",
    "real device contact",
    "raw command runner",
    "dashboard execution control",
    "approval unlock",
    "execution unlock",
)

REQUIRED_INVARIANTS = {
    "fail_closed_default": True,
    "live_read_allowed": False,
    "write_allowed": False,
    "raw_command_allowed": False,
    "credential_required": False,
    "transport_required": False,
    "real_device_contact_allowed": False,
}


def build_dangerous_actions() -> List[Dict[str, Any]]:
    """Return deterministic default-deny dangerous action records."""
    return [
        {
            "id": action_id,
            "category": category,
            "decision": "DENY",
            "allowed": False,
            "denied_by_default": True,
            "reason": "Dangerous live or device-modifying action is outside Day91 scaffold scope.",
            "proof_state": "STRUCTURALLY_BLOCKED",
        }
        for action_id, category in DANGEROUS_ACTION_CATEGORIES
    ]


def build_read_only_candidates() -> List[Dict[str, Any]]:
    """Return future read-only candidates without executable behavior."""
    return [
        {
            "id": candidate_id,
            "category": category,
            "execution_state": "NOT_EXECUTABLE",
            "guard_state": "PENDING_GUARD",
            "scope_state": "FUTURE_ONLY",
            "allowed_to_execute": False,
            "live_read_allowed": False,
            "reason": "Listed only for Day92+ guard design; no Day91 code path can execute or live-read it.",
        }
        for candidate_id, category in READ_ONLY_CANDIDATE_CATEGORIES
    ]


def build_fail_closed_decision_model() -> Dict[str, Any]:
    return {
        "default_decision": "DENY",
        "unknown_action_decision": "DENY",
        "missing_guard_decision": "DENY",
        "read_only_without_guard_decision": "DENY",
        "dangerous_action_decision": "DENY",
        "live_read_without_future_review_decision": "DENY",
        "fallback_to_execution": False,
        "operator_message": "Day91 stops at scaffold evidence; executable guards start no earlier than Day92.",
    }


def build_blocked_imports_or_capabilities() -> List[Dict[str, Any]]:
    return [
        {
            "capability": capability,
            "present": False,
            "allowed": False,
            "decision": "BLOCKED",
            "scope": "SCAFFOLD_ONLY",
        }
        for capability in BLOCKED_CAPABILITIES
    ]


def build_evidence_chain() -> List[Dict[str, Any]]:
    return [
        {
            "day": "Day90",
            "title": "Real Adapter Implementation Plan",
            "evidence": "Day90 produced CONDITIONAL_GO only, not GO.",
            "decision": "CONDITIONAL_GO",
            "effect": "Day91 may create only safety scaffold evidence.",
        },
        {
            "day": "Day91",
            "title": TITLE,
            "evidence": "Dangerous actions are denied before any read-only path exists.",
            "decision": "SCAFFOLD_ONLY",
            "effect": "No real adapter, live-read, transport, credential, or executable guard is added.",
        },
    ]


def build_next_required_days() -> List[Dict[str, str]]:
    return [
        {
            "day": "Day92",
            "title": "Executable Guards",
            "required_proof": "Guard functions reject dangerous actions and still keep live-read blocked.",
        },
        {
            "day": "Day93",
            "title": "Fake Transport Full Path",
            "required_proof": "Non-live fake transport can pass guarded read-only candidates without device contact.",
        },
        {
            "day": "Day94",
            "title": "Runner Dry-run Wiring",
            "required_proof": "Runner wiring remains dry-run and cannot reach live transport.",
        },
        {
            "day": "Day95",
            "title": "Regression Lock",
            "required_proof": "Safety tests lock no-write, no-raw-command, no-credential, and no-live-read behavior.",
        },
        {
            "day": "Day96",
            "title": "Live-read Review",
            "required_proof": "Only after prior proof can limited live-read entry be reviewed, not automatically enabled.",
        },
    ]


def validate_day91_real_adapter_safety_scaffold(report: Dict[str, Any]) -> List[str]:
    """Return validation errors for the Day91 scaffold report."""
    errors: List[str] = []
    if report.get("day") != 91:
        errors.append("day must be 91.")
    if report.get("day_id") != "Day91":
        errors.append("day_id must be Day91.")
    if report.get("title") != TITLE:
        errors.append("title must match Day91.")
    if report.get("status") != STATUS:
        errors.append("status must be SCAFFOLD_ONLY.")
    if report.get("overall_decision") != OVERALL_DECISION:
        errors.append("overall_decision must be PASS.")
    if report.get("day90_gate", {}).get("decision") != "CONDITIONAL_GO":
        errors.append("day90_gate decision must be CONDITIONAL_GO.")

    invariants = report.get("invariants", {})
    for field, expected in REQUIRED_INVARIANTS.items():
        if invariants.get(field) is not expected:
            errors.append(f"invariant {field} must be {json.dumps(expected)}.")

    for item in report.get("dangerous_actions", []):
        if item.get("allowed") is not False or item.get("decision") != "DENY":
            errors.append(f"dangerous action {item.get('id')} must be denied.")
        if item.get("denied_by_default") is not True:
            errors.append(f"dangerous action {item.get('id')} must be denied by default.")

    for item in report.get("read_only_candidates", []):
        if item.get("execution_state") != "NOT_EXECUTABLE":
            errors.append(f"read-only candidate {item.get('id')} must be NOT_EXECUTABLE.")
        if item.get("guard_state") != "PENDING_GUARD":
            errors.append(f"read-only candidate {item.get('id')} must be PENDING_GUARD.")
        if item.get("scope_state") != "FUTURE_ONLY":
            errors.append(f"read-only candidate {item.get('id')} must be FUTURE_ONLY.")
        if item.get("allowed_to_execute") is not False or item.get("live_read_allowed") is not False:
            errors.append(f"read-only candidate {item.get('id')} must not execute or live-read.")

    if any(item.get("present") is not False for item in report.get("blocked_imports_or_capabilities", [])):
        errors.append("blocked imports or capabilities must not be present.")
    if [item.get("day") for item in report.get("next_required_days", [])] != [
        "Day92",
        "Day93",
        "Day94",
        "Day95",
        "Day96",
    ]:
        errors.append("next_required_days must be Day92 through Day96.")
    return errors


def build_day91_real_adapter_safety_scaffold() -> Dict[str, Any]:
    """Build the deterministic Day91 real adapter safety scaffold report."""
    report: Dict[str, Any] = {
        "day": 91,
        "day_id": "Day91",
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "status": STATUS,
        "phase": STATUS,
        "overall_decision": OVERALL_DECISION,
        "day90_gate": {
            "decision": "CONDITIONAL_GO",
            "is_go": False,
            "is_conditional_go": True,
            "day91_scope_allowed": "safety scaffold and evidence chain only",
        },
        "scope_statement": (
            "Day91 proves dangerous actions are structurally denied before any "
            "real adapter, live-read, transport, credential, or executable guard exists."
        ),
        "dangerous_actions": build_dangerous_actions(),
        "read_only_candidates": build_read_only_candidates(),
        "fail_closed_decision_model": build_fail_closed_decision_model(),
        "invariants": dict(REQUIRED_INVARIANTS),
        "blocked_imports_or_capabilities": build_blocked_imports_or_capabilities(),
        "evidence_chain": build_evidence_chain(),
        "next_required_days": build_next_required_days(),
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day91 adds scaffold-only safety evidence. It adds no live device access, "
            "SSH, RouterOS API, socket, subprocess device operation, credential use, "
            "real adapter implementation, executable guard, or live-read path."
        ),
    }
    validation_errors = validate_day91_real_adapter_safety_scaffold(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_decision"] = "FAIL"
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _action_rows(items: List[Dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item['id']))}</td>"
        f"<td>{html.escape(str(item['category']))}</td>"
        f"<td>{html.escape(str(item.get('decision') or item.get('execution_state')))}</td>"
        f"<td>{html.escape(json.dumps(item.get('allowed', item.get('allowed_to_execute'))))}</td>"
        "</tr>"
        for item in items
    )


def write_day91_real_adapter_safety_scaffold_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write the static Day91 scaffold reviewer HTML report."""
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
  <p><strong>Result:</strong> {html.escape(report['overall_decision'])} / {html.escape(report['status'])}</p>
  <p><strong>Day90 gate:</strong> {html.escape(report['day90_gate']['decision'])} only</p>
  <p><strong>Safety:</strong> scaffold-only; dangerous actions denied, read-only candidates future-only, live-read not allowed.</p>
  <h2>Safety Invariants</h2>
  <table><tbody>{''.join('<tr><th>' + html.escape(key) + '</th><td>' + html.escape(json.dumps(value)) + '</td></tr>' for key, value in report['invariants'].items())}</tbody></table>
  <h2>Dangerous Actions</h2>
  <table><thead><tr><th>ID</th><th>Category</th><th>Decision</th><th>Allowed</th></tr></thead><tbody>{_action_rows(report['dangerous_actions'])}</tbody></table>
  <h2>Read-only Candidates</h2>
  <table><thead><tr><th>ID</th><th>Category</th><th>Execution state</th><th>Allowed</th></tr></thead><tbody>{_action_rows(report['read_only_candidates'])}</tbody></table>
  <h2>Blocked Capabilities</h2>
  <ul>{_html_list([item['capability'] for item in report['blocked_imports_or_capabilities']])}</ul>
  <h2>Evidence Chain</h2>
  <ul>{_html_list([item['day'] + ': ' + item['evidence'] for item in report['evidence_chain']])}</ul>
  <h2>Next Required Days</h2>
  <ul>{_html_list([item['day'] + ' - ' + item['required_proof'] for item in report['next_required_days']])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_day91_real_adapter_safety_scaffold_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day91 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_day91_real_adapter_safety_scaffold()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day91_real_adapter_safety_scaffold_html(safe_report, html_path)
    return json_path, html_path
