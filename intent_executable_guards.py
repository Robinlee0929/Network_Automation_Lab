"""Day92 executable guard layer for future real adapter requests.

This module turns the Day91 static scaffold into deterministic executable
guards. It evaluates simulated request objects only: no SSH, no sockets, no
RouterOS commands, no subprocess device operations, and no real adapter.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-10T00:00:00Z"
TASK_NAME = "real-adapter-executable-guards"
TITLE = "Real Adapter Executable Guards"
STATUS = "PASS"
PHASE = "GUARD_ENFORCED"
SAFETY_LEVEL = "offline_deterministic_guard"
REPORT_JSON = Path("reports") / "lab-summary" / "day92_real_adapter_executable_guards_report.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day92_real_adapter_executable_guards_report.html"

ALLOW = "ALLOW"
REJECT = "REJECT"

SAFE_READ_ONLY_ACTIONS: Dict[str, Dict[str, str]] = {
    "collect_interface_status": {
        "category": "interface_status_read",
        "result_key": "interfaces",
    },
    "read_route_summary": {
        "category": "route_summary_read",
        "result_key": "routes",
    },
    "read_wireguard_peer_status": {
        "category": "wireguard_peer_status_read",
        "result_key": "wireguard_peers",
    },
    "read_system_resource_summary": {
        "category": "system_resource_read",
        "result_key": "system_resources",
    },
    "read_only_precheck_summary": {
        "category": "read_only_precheck",
        "result_key": "precheck",
    },
}

DANGEROUS_ACTION_RULES = (
    ("reboot_device", "deny_reboot_device", "reboot", ("reboot", "restart device")),
    ("reset_configuration", "deny_reset_configuration", "reset_configuration", ("reset configuration", "factory reset")),
    ("disable_interface", "deny_disable_interface", "interface_state_change", ("disable interface",)),
    ("enable_interface", "deny_enable_interface", "interface_state_change", ("enable interface",)),
    ("add_firewall_rule", "deny_add_firewall_rule", "firewall_change", ("add firewall", "firewall add")),
    ("remove_firewall_rule", "deny_remove_firewall_rule", "firewall_change", ("remove firewall", "delete firewall")),
    ("change_ip_address", "deny_change_ip_address", "ip_address_change", ("change ip", "set address")),
    ("modify_route", "deny_modify_route", "route_change", ("modify route", "set route")),
    ("modify_wireguard_peer", "deny_modify_wireguard", "wireguard_modification", ("modify wireguard", "set wireguard")),
    ("modify_vrrp", "deny_modify_vrrp", "vrrp_modification", ("modify vrrp", "set vrrp")),
    ("run_arbitrary_command", "deny_arbitrary_command", "arbitrary_command", ("run command", "arbitrary command")),
    ("export_secret", "deny_secret_export", "credential_export", ("export secret", "private key", "show password")),
)

MUTATION_VERBS = (
    "write",
    "apply",
    "configure",
    "set",
    "add",
    "remove",
    "delete",
    "enable",
    "disable",
)

SECRET_MARKERS = (
    "password",
    "token",
    "private key",
    "privatekey",
    "preshared key",
    "presharedkey",
    "secret",
)


@dataclass(frozen=True)
class GuardRequest:
    """A simulated request object evaluated by the Day92 guard."""

    request_id: str
    action: str
    intent: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GuardDecision:
    """Structured guard decision returned before any executor is reachable."""

    request_id: str
    decision: str
    allowed: bool
    reason_code: str
    reason: str
    matched_rule_name: str
    evidence: List[str]
    blocked_action_category: Optional[str]
    adapter_invocation_allowed: bool

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutableGuard:
    """Fail-closed executable guard for simulated future adapter requests."""

    def evaluate(self, request: GuardRequest) -> GuardDecision:
        text = _normalized_request_text(request)

        secret_hit = _find_secret_marker(text)
        if secret_hit:
            return _reject(
                request,
                "SECRET_MATERIAL_DETECTED",
                f"Request contains sensitive marker '{secret_hit}' and is rejected before any executor can be reached.",
                "deny_secret_material",
                "credential_or_secret_material",
                [
                    "Day92 rejects request objects containing password/token/private key/secret markers.",
                    "Rejected request has adapter_invocation_allowed=false.",
                ],
            )

        for action_id, rule_name, category, phrases in DANGEROUS_ACTION_RULES:
            if request.action == action_id or any(phrase in text for phrase in phrases):
                return _reject(
                    request,
                    "DANGEROUS_ACTION_REJECTED",
                    f"Dangerous action category '{category}' is outside Day92 guard scope.",
                    rule_name,
                    category,
                    [
                        f"Matched dangerous action rule {rule_name}.",
                        "Day91 dangerous actions remain denied by executable guard.",
                        "Rejected request has adapter_invocation_allowed=false.",
                    ],
                )

        mutation_verb = _find_mutation_verb(text)
        if mutation_verb:
            return _reject(
                request,
                "MUTATION_VERB_REJECTED",
                f"Mutation verb '{mutation_verb}' is not allowed in Day92 simulated guard requests.",
                "deny_mutation_verbs",
                "configuration_mutation_request",
                [
                    "Matched Day92 mutation verb deny rule.",
                    "Write/apply/configure/set/add/remove/delete/enable/disable verbs fail closed.",
                    "Rejected request has adapter_invocation_allowed=false.",
                ],
            )

        safe = SAFE_READ_ONLY_ACTIONS.get(request.action)
        if safe:
            return GuardDecision(
                request_id=request.request_id,
                decision=ALLOW,
                allowed=True,
                reason_code="READ_ONLY_ACTION_ALLOWED",
                reason="Simulated read-only request matched the Day92 positive allowlist.",
                matched_rule_name="allow_read_only_simulated_request",
                evidence=[
                    f"Matched read-only category {safe['category']}.",
                    "Request is simulated and deterministic.",
                    "No secret markers or mutation verbs were present.",
                ],
                blocked_action_category=None,
                adapter_invocation_allowed=True,
            )

        return _reject(
            request,
            "UNKNOWN_ACTION_REJECTED",
            "Unknown or ambiguous request did not match the Day92 positive allowlist.",
            "deny_unknown_action",
            "unknown_or_ambiguous_request",
            [
                "Day92 fail-closed default rejected the request.",
                "Only explicitly allowlisted read-only simulated requests may proceed.",
                "Rejected request has adapter_invocation_allowed=false.",
            ],
        )


def execute_guarded_request(
    request: GuardRequest,
    executor: Callable[[GuardRequest], Dict[str, Any]],
    guard: Optional[ExecutableGuard] = None,
) -> Dict[str, Any]:
    """Evaluate a request and call the executor only after an ALLOW decision."""
    active_guard = guard or ExecutableGuard()
    decision = active_guard.evaluate(request)
    if not decision.allowed:
        return {
            "request": request.to_record(),
            "guard_decision": decision.to_record(),
            "executor_invoked": False,
            "result": None,
        }
    return {
        "request": request.to_record(),
        "guard_decision": decision.to_record(),
        "executor_invoked": True,
        "result": executor(request),
    }


def build_guard_scenarios() -> List[GuardRequest]:
    """Return deterministic Day92 simulated request scenarios."""
    safe = [
        GuardRequest("day92-safe-001", "collect_interface_status", "Collect interface status", {"scope": "simulated"}),
        GuardRequest("day92-safe-002", "read_route_summary", "Read route summary", {"scope": "simulated"}),
        GuardRequest(
            "day92-safe-003",
            "read_wireguard_peer_status",
            "Read WireGuard peer status",
            {"redaction": "enabled"},
        ),
        GuardRequest("day92-safe-004", "read_system_resource_summary", "Read system resource summary", {}),
        GuardRequest("day92-safe-005", "read_only_precheck_summary", "Read-only precheck summary", {}),
    ]
    dangerous = [
        GuardRequest("day92-deny-001", "reboot_device", "Reboot device", {}),
        GuardRequest("day92-deny-002", "reset_configuration", "Reset configuration", {}),
        GuardRequest("day92-deny-003", "disable_interface", "Disable interface ether1", {"interface": "ether1"}),
        GuardRequest("day92-deny-004", "enable_interface", "Enable interface ether1", {"interface": "ether1"}),
        GuardRequest("day92-deny-005", "add_firewall_rule", "Add firewall rule", {}),
        GuardRequest("day92-deny-006", "remove_firewall_rule", "Remove firewall rule", {}),
        GuardRequest("day92-deny-007", "change_ip_address", "Change IP address", {"address": "192.0.2.10/24"}),
        GuardRequest("day92-deny-008", "modify_route", "Modify route", {"gateway": "192.0.2.1"}),
        GuardRequest("day92-deny-009", "modify_wireguard_peer", "Modify WireGuard peer/interface", {}),
        GuardRequest("day92-deny-010", "modify_vrrp", "Modify VRRP", {}),
        GuardRequest("day92-deny-011", "run_arbitrary_command", "Run arbitrary command", {"command": "/system reboot"}),
        GuardRequest("day92-deny-012", "export_secret", "Export or expose private key", {}),
        GuardRequest("day92-deny-013", "collect_interface_status", "Collect status", {"password": "REDACTED"}),
        GuardRequest("day92-deny-014", "read_route_summary", "Apply route read change", {"verb": "apply"}),
        GuardRequest("day92-deny-015", "unknown_action", "Unknown action", {}),
    ]
    return safe + dangerous


def deterministic_read_only_executor(request: GuardRequest) -> Dict[str, Any]:
    """Return offline deterministic data for allowlisted simulated requests."""
    fixtures: Dict[str, Dict[str, Any]] = {
        "collect_interface_status": {
            "interfaces": [
                {"name": "ether1", "running": True, "disabled": False},
                {"name": "bridge-lan", "running": True, "disabled": False},
            ]
        },
        "read_route_summary": {
            "routes": [
                {"dst": "0.0.0.0/0", "gateway": "198.51.100.1", "active": True},
                {"dst": "192.0.2.0/24", "gateway": "bridge-lan", "active": True},
            ]
        },
        "read_wireguard_peer_status": {
            "wireguard_peers": [
                {
                    "name": "peer-lab-client",
                    "latest_handshake": "2026-06-10T00:00:00Z",
                    "private_key": "REDACTED",
                }
            ]
        },
        "read_system_resource_summary": {
            "system_resources": {"cpu_load_percent": 7, "free_memory_mib": 384, "uptime": "1d02:03:04"}
        },
        "read_only_precheck_summary": {
            "precheck": {"interfaces_seen": 2, "routes_seen": 2, "wireguard_peers_seen": 1, "safe": True}
        },
    }
    return deepcopy(fixtures[request.action])


def run_day92_guard_scenarios() -> List[Dict[str, Any]]:
    """Run deterministic guard scenarios using only the offline fake executor."""
    guard = ExecutableGuard()
    return [
        execute_guarded_request(request, deterministic_read_only_executor, guard)
        for request in build_guard_scenarios()
    ]


def build_day92_real_adapter_executable_guards_report() -> Dict[str, Any]:
    """Build the deterministic Day92 executable guard report."""
    scenarios = run_day92_guard_scenarios()
    allowed = [item for item in scenarios if item["guard_decision"]["decision"] == ALLOW]
    rejected = [item for item in scenarios if item["guard_decision"]["decision"] == REJECT]
    rejected_adapter_invocations = sum(1 for item in rejected if item["executor_invoked"])
    report: Dict[str, Any] = {
        "day": 92,
        "day_id": "Day92",
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "status": STATUS,
        "phase": PHASE,
        "safety_level": SAFETY_LEVEL,
        "no_real_device_access": True,
        "no_ssh": True,
        "no_subprocess": True,
        "no_socket": True,
        "no_real_adapter": True,
        "adapter_implementation_added": False,
        "total_scenarios": len(scenarios),
        "allowed_scenarios": len(allowed),
        "rejected_scenarios": len(rejected),
        "rejected_adapter_invocations": rejected_adapter_invocations,
        "adapter_invoked_for_rejected": rejected_adapter_invocations,
        "scenario_results": scenarios,
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day92 implements executable request guards only. Rejected simulated "
            "requests return structured evidence and cannot reach an executor; "
            "no real adapter, SSH, socket, subprocess, RouterOS command, or live "
            "device access is added."
        ),
    }
    validation_errors = validate_day92_real_adapter_executable_guards_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["status"] = "FAIL"
    return report


def validate_day92_real_adapter_executable_guards_report(report: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if report.get("day") != 92:
        errors.append("day must be 92.")
    if report.get("title") != TITLE:
        errors.append("title must match Day92.")
    if report.get("phase") != PHASE:
        errors.append("phase must be GUARD_ENFORCED.")
    for field in ("no_real_device_access", "no_ssh", "no_subprocess", "no_socket", "no_real_adapter"):
        if report.get(field) is not True:
            errors.append(f"{field} must be true.")
    if report.get("adapter_implementation_added") is not False:
        errors.append("adapter_implementation_added must be false.")
    if report.get("total_scenarios") != len(report.get("scenario_results", [])):
        errors.append("total_scenarios must match scenario_results length.")
    if report.get("allowed_scenarios", 0) < len(SAFE_READ_ONLY_ACTIONS):
        errors.append("allowed_scenarios must cover all safe read-only examples.")
    if report.get("rejected_scenarios", 0) < len(DANGEROUS_ACTION_RULES):
        errors.append("rejected_scenarios must cover dangerous examples.")
    if report.get("rejected_adapter_invocations") != 0:
        errors.append("rejected_adapter_invocations must be 0.")

    for scenario in report.get("scenario_results", []):
        decision = scenario.get("guard_decision", {})
        if decision.get("decision") == REJECT:
            if scenario.get("executor_invoked") is not False:
                errors.append(f"rejected request {decision.get('request_id')} invoked executor.")
            if decision.get("adapter_invocation_allowed") is not False:
                errors.append(f"rejected request {decision.get('request_id')} allowed adapter invocation.")
            if not decision.get("reason_code") or not decision.get("matched_rule_name"):
                errors.append(f"rejected request {decision.get('request_id')} lacks reason evidence.")
        elif decision.get("decision") == ALLOW:
            if scenario.get("executor_invoked") is not True:
                errors.append(f"allowed request {decision.get('request_id')} did not invoke executor.")
            if _contains_unredacted_secret(scenario.get("result")):
                errors.append(f"allowed request {decision.get('request_id')} exposed a secret.")
        else:
            errors.append("scenario has invalid guard decision.")
    return errors


def write_day92_real_adapter_executable_guards_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write the Day92 reviewer HTML report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(item['request']['request_id'])}</td>"
        f"<td>{html.escape(item['request']['action'])}</td>"
        f"<td>{html.escape(item['guard_decision']['decision'])}</td>"
        f"<td>{html.escape(item['guard_decision']['reason_code'])}</td>"
        f"<td>{html.escape(item['guard_decision']['matched_rule_name'])}</td>"
        f"<td>{html.escape(str(item['guard_decision']['blocked_action_category']))}</td>"
        f"<td>{html.escape('; '.join(item['guard_decision']['evidence']))}</td>"
        f"<td>{html.escape(json.dumps(item['executor_invoked']))}</td>"
        "</tr>"
        for item in report["scenario_results"]
    )
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
  <p><strong>Safety level:</strong> {html.escape(report['safety_level'])}</p>
  <p><strong>Total scenarios:</strong> {report['total_scenarios']}</p>
  <p><strong>Allowed:</strong> {report['allowed_scenarios']} | <strong>Rejected:</strong> {report['rejected_scenarios']} | <strong>Rejected adapter invocations:</strong> {report['rejected_adapter_invocations']}</p>
  <p><strong>Boundary:</strong> no real device access, no SSH, no subprocess, no socket, no real adapter.</p>
  <h2>Scenario Evidence</h2>
  <table>
    <thead><tr><th>Request</th><th>Action</th><th>Decision</th><th>Reason code</th><th>Matched rule</th><th>Blocked category</th><th>Evidence</th><th>Executor invoked</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_day92_real_adapter_executable_guards_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day92 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_day92_real_adapter_executable_guards_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_day92_real_adapter_executable_guards_html(safe_report, html_path)
    return json_path, html_path


def _reject(
    request: GuardRequest,
    reason_code: str,
    reason: str,
    matched_rule_name: str,
    blocked_action_category: str,
    evidence: List[str],
) -> GuardDecision:
    return GuardDecision(
        request_id=request.request_id,
        decision=REJECT,
        allowed=False,
        reason_code=reason_code,
        reason=reason,
        matched_rule_name=matched_rule_name,
        evidence=evidence,
        blocked_action_category=blocked_action_category,
        adapter_invocation_allowed=False,
    )


def _normalized_request_text(request: GuardRequest) -> str:
    raw = json.dumps(request.to_record(), sort_keys=True).lower().replace("_", " ")
    return "".join(character if character.isalnum() else " " for character in raw)


def _find_secret_marker(text: str) -> Optional[str]:
    for marker in SECRET_MARKERS:
        if marker in text:
            return marker
    return None


def _find_mutation_verb(text: str) -> Optional[str]:
    padded = f" {text} "
    for verb in MUTATION_VERBS:
        if f" {verb} " in padded:
            return verb
    return None


def _contains_unredacted_secret(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in SECRET_MARKERS) and "redacted" not in lowered
    if isinstance(value, dict):
        for key, item in value.items():
            lowered_key = str(key).lower().replace("_", " ")
            if any(marker in lowered_key for marker in SECRET_MARKERS) and item != "REDACTED":
                return True
            if _contains_unredacted_secret(item):
                return True
        return False
    if isinstance(value, list):
        return any(_contains_unredacted_secret(item) for item in value)
    return False
