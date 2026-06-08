"""Day79 controlled read-only task contract and allowlist.

This module defines deterministic, mock-only, dry-run-only task eligibility
records for future read-only AI-requested task review. It never connects to
devices and never unlocks execution.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CREATED_AT = "2026-06-08T00:00:00Z"
TASK_NAME = "readonly-task-contract"
EXECUTION_MODE = "deterministic_mock_only_dry_run_only_readonly_contract"
REPORT_JSON = Path("reports") / "lab-summary" / "day79_readonly_task_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day79_readonly_task_contract.html"

READONLY_CONTRACT_READY = "READONLY_CONTRACT_READY"
BLOCKED_WRITE_ACTION = "BLOCKED_WRITE_ACTION"
BLOCKED_DESTRUCTIVE_ACTION = "BLOCKED_DESTRUCTIVE_ACTION"
UNKNOWN_TASK = "UNKNOWN_TASK"
NEEDS_MANUAL_CLASSIFICATION = "NEEDS_MANUAL_CLASSIFICATION"

READONLY_CANDIDATES = (
    "show_interface_status",
    "show_ip_address",
    "show_route_table",
    "show_wireguard_peer_status",
    "show_system_resource",
    "show_log_summary",
    "ping_readonly_probe",
    "iperf3_report_review",
)

BLOCKED_WRITE_ACTIONS = (
    "set_ip_address",
    "add_firewall_rule",
    "remove_firewall_rule",
    "enable_interface",
    "disable_interface",
    "create_wireguard_peer",
    "modify_vrrp_priority",
    "apply_config",
)

DESTRUCTIVE_ACTIONS = (
    "reset_configuration",
    "reboot_device",
    "factory_reset",
    "delete_interface",
    "remove_firewall_rules",
    "wipe_config",
)

UNKNOWN_MANUAL_CATEGORIES = (
    "unknown",
    "unsupported",
    "needs_manual_classification",
)

REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "scenario_id",
    "intent_id",
    "requested_task",
    "task_category",
    "readonly_eligible",
    "execution_candidate",
    "requires_human_approval",
    "allowed_command_refs",
    "blocked_command_patterns",
    "device_scope",
    "policy_reason",
    "safety_invariants",
    "contract_result",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "created_at",
)

RESULT_VALUES = {
    READONLY_CONTRACT_READY,
    BLOCKED_WRITE_ACTION,
    BLOCKED_DESTRUCTIVE_ACTION,
    UNKNOWN_TASK,
    NEEDS_MANUAL_CLASSIFICATION,
}

MOCK_SCENARIOS = (
    {
        "scenario_id": "day79-scenario-readonly-interface-status",
        "intent_id": "intent-show-interface-status",
        "requested_task": "show_interface_status",
        "device_scope": {
            "scope_type": "mock_lab_device_group",
            "devices": ("routeros-edge-01", "cisco-access-01"),
        },
    },
    {
        "scenario_id": "day79-scenario-blocked-write-firewall",
        "intent_id": "intent-add-firewall-rule",
        "requested_task": "add_firewall_rule",
        "device_scope": {
            "scope_type": "mock_router",
            "devices": ("routeros-edge-01",),
        },
    },
    {
        "scenario_id": "day79-scenario-destructive-factory-reset",
        "intent_id": "intent-factory-reset",
        "requested_task": "factory_reset",
        "device_scope": {
            "scope_type": "mock_router",
            "devices": ("routeros-edge-01",),
        },
    },
    {
        "scenario_id": "day79-scenario-unknown-task",
        "intent_id": "intent-do-something-unclear",
        "requested_task": "unknown",
        "device_scope": {
            "scope_type": "mock_unspecified_scope",
            "devices": (),
        },
    },
    {
        "scenario_id": "day79-scenario-manual-classification",
        "intent_id": "intent-review-custom-diagnostic",
        "requested_task": "needs_manual_classification",
        "device_scope": {
            "scope_type": "mock_unclassified_lab_scope",
            "devices": ("routeros-edge-01", "cisco-access-01"),
        },
    },
)


def _safe_scope(scope: Dict[str, Any]) -> Dict[str, Any]:
    safe = deepcopy(scope)
    devices = safe.get("devices", ())
    safe["devices"] = list(devices)
    safe["live_device_access"] = False
    safe["config_json_required"] = False
    return safe


def _allowed_refs(task: str) -> List[str]:
    if task not in READONLY_CANDIDATES:
        return []
    return [
        f"allowlist:{task}",
        "policy:readonly_candidate_only",
        "policy:mock_dry_run_contract_only",
    ]


def _blocked_patterns(task: str, result: str) -> List[str]:
    common_write_patterns = [
        "set ",
        "add ",
        "remove ",
        "enable ",
        "disable ",
        "apply ",
        "delete ",
        "reset ",
        "reboot ",
        "wipe ",
    ]
    if result == READONLY_CONTRACT_READY:
        return common_write_patterns
    return [task, *common_write_patterns]


def _classify_task(task: str) -> Dict[str, Any]:
    if task in READONLY_CANDIDATES:
        return {
            "task_category": task,
            "readonly_eligible": True,
            "execution_candidate": True,
            "requires_human_approval": False,
            "contract_result": READONLY_CONTRACT_READY,
            "policy_reason": (
                "Task is listed as a future read-only candidate, but Day79 only "
                "defines eligibility and keeps execution disabled."
            ),
        }
    if task in BLOCKED_WRITE_ACTIONS:
        return {
            "task_category": task,
            "readonly_eligible": False,
            "execution_candidate": False,
            "requires_human_approval": True,
            "contract_result": BLOCKED_WRITE_ACTION,
            "policy_reason": (
                "Task can change router, switch, firewall, VPN, VRRP, interface, "
                "route, or address state and is blocked by the read-only contract."
            ),
        }
    if task in DESTRUCTIVE_ACTIONS:
        return {
            "task_category": task,
            "readonly_eligible": False,
            "execution_candidate": False,
            "requires_human_approval": True,
            "contract_result": BLOCKED_DESTRUCTIVE_ACTION,
            "policy_reason": (
                "Task is destructive and always forbidden by the Day79 contract."
            ),
        }
    if task == "needs_manual_classification":
        return {
            "task_category": task,
            "readonly_eligible": False,
            "execution_candidate": False,
            "requires_human_approval": True,
            "contract_result": NEEDS_MANUAL_CLASSIFICATION,
            "policy_reason": (
                "Task cannot be safely categorized from the fixed allowlist and "
                "requires manual classification before any future consideration."
            ),
        }
    return {
        "task_category": "unknown",
        "readonly_eligible": False,
        "execution_candidate": False,
        "requires_human_approval": True,
        "contract_result": UNKNOWN_TASK,
        "policy_reason": (
            "Task is not in the read-only allowlist, blocked write list, or "
            "destructive list and is therefore unknown."
        ),
    }


def _safety_invariants() -> Dict[str, Any]:
    return {
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "deterministic": True,
        "mock_only": True,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "live_execution_used": False,
        "mapped_task_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }


def build_readonly_task_contract_records(
    scenarios: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic Day79 task contract records."""
    source_scenarios = deepcopy(scenarios) if scenarios is not None else deepcopy(list(MOCK_SCENARIOS))
    records: List[Dict[str, Any]] = []
    for index, scenario in enumerate(source_scenarios, start=1):
        task = str(scenario.get("requested_task", "unknown"))
        classification = _classify_task(task)
        result = classification["contract_result"]
        records.append(
            {
                "contract_id": f"day79-contract-{index:02d}",
                "scenario_id": str(scenario.get("scenario_id", "")),
                "intent_id": str(scenario.get("intent_id", "")),
                "requested_task": task,
                "task_category": classification["task_category"],
                "readonly_eligible": classification["readonly_eligible"],
                "execution_candidate": classification["execution_candidate"],
                "requires_human_approval": classification["requires_human_approval"],
                "allowed_command_refs": _allowed_refs(task),
                "blocked_command_patterns": _blocked_patterns(task, result),
                "device_scope": _safe_scope(scenario.get("device_scope", {})),
                "policy_reason": classification["policy_reason"],
                "safety_invariants": _safety_invariants(),
                "contract_result": result,
                "allowed_to_execute": False,
                "dry_run_only": True,
                "execution_unlock_supported": False,
                "created_at": CREATED_AT,
            }
        )
    return records


def validate_readonly_task_contract_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day79 contract records."""
    errors: List[str] = []
    if not records:
        errors.append("no read-only task contract records were produced.")
        return errors

    for record in records:
        contract_id = str(record.get("contract_id", "<missing>"))
        for field in REQUIRED_CONTRACT_FIELDS:
            if field not in record:
                errors.append(f"{contract_id} missing required field: {field}.")
        if record.get("allowed_to_execute") is not False:
            errors.append(f"{contract_id} allowed_to_execute must be false.")
        if record.get("dry_run_only") is not True:
            errors.append(f"{contract_id} dry_run_only must be true.")
        if record.get("execution_unlock_supported") is not False:
            errors.append(f"{contract_id} execution_unlock_supported must be false.")
        if record.get("contract_result") not in RESULT_VALUES:
            errors.append(f"{contract_id} has unknown contract_result.")
        invariants = record.get("safety_invariants", {})
        if invariants.get("allowed_to_execute") is not False:
            errors.append(f"{contract_id} invariant allowed_to_execute must be false.")
        if invariants.get("dry_run_only") is not True:
            errors.append(f"{contract_id} invariant dry_run_only must be true.")
        if invariants.get("execution_unlock_supported") is not False:
            errors.append(
                f"{contract_id} invariant execution_unlock_supported must be false."
            )
        if record.get("readonly_eligible") is True and record.get("execution_candidate") is not True:
            errors.append(f"{contract_id} read-only eligible records must be candidates.")
        if record.get("contract_result") != READONLY_CONTRACT_READY:
            if record.get("readonly_eligible") is not False:
                errors.append(f"{contract_id} blocked or unknown records must not be read-only eligible.")
            if record.get("execution_candidate") is not False:
                errors.append(f"{contract_id} blocked or unknown records must not be candidates.")
    return errors


def build_readonly_task_contract_report() -> Dict[str, Any]:
    """Build the Day79 controlled read-only task contract report."""
    records = build_readonly_task_contract_records()
    validation_errors = validate_readonly_task_contract_records(records)
    result_counts = {
        result: sum(1 for record in records if record.get("contract_result") == result)
        for result in sorted(RESULT_VALUES)
    }
    disabled_keys = {
        "openai_api_used",
        "ai_sdk_dependency_used",
        "ssh_used",
        "device_access_used",
        "live_execution_used",
        "mapped_task_executed",
        "config_json_read",
        "dashboard_action_surface_added",
        "network_configuration_changed",
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(
            record.get("allowed_to_execute") is False for record in records
        ),
        "dry_run_only_always_true": all(record.get("dry_run_only") is True for record in records),
        "execution_unlock_supported_always_false": all(
            record.get("execution_unlock_supported") is False for record in records
        ),
        "readonly_eligible_has_no_execution_permission": all(
            record.get("allowed_to_execute") is False
            for record in records
            if record.get("readonly_eligible") is True
        ),
        "deterministic": True,
        "mock_only": True,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "ssh_used": False,
        "device_access_used": False,
        "live_execution_used": False,
        "mapped_task_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in disabled_keys else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day79",
        "title": "Day79 Controlled Read-only Task Contract & Allowlist",
        "task_name": TASK_NAME,
        "execution_mode": EXECUTION_MODE,
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "summary": {
            "contract_record_count": len(records),
            "contract_result_counts": result_counts,
            "readonly_eligible_values": sorted(
                {record.get("readonly_eligible") for record in records}
            ),
            "execution_candidate_values": sorted(
                {record.get("execution_candidate") for record in records}
            ),
            "allowed_to_execute_values": sorted(
                {record.get("allowed_to_execute") for record in records}
            ),
            "dry_run_only_values": sorted({record.get("dry_run_only") for record in records}),
            "execution_unlock_supported_values": sorted(
                {record.get("execution_unlock_supported") for record in records}
            ),
        },
        "allowlist": {
            "readonly_candidates": list(READONLY_CANDIDATES),
            "blocked_write_actions": list(BLOCKED_WRITE_ACTIONS),
            "destructive_actions": list(DESTRUCTIVE_ACTIONS),
            "unknown_manual_categories": list(UNKNOWN_MANUAL_CATEGORIES),
        },
        "contract_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Deterministic fixed mock data only.",
            "Dry-run-only contract report.",
            "No OpenAI API.",
            "No AI SDK dependency.",
            "No SSH.",
            "No device access.",
            "No live execution.",
            "No mapped task execution.",
            "No config.json dependency.",
            "No approval unlock.",
            "No dashboard action surface.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": [
            "docs/ai/intent_readonly_task_contract.md",
            "docs/roadmap/day79_readonly_task_contract.md",
            REPORT_JSON.as_posix(),
            REPORT_HTML.as_posix(),
        ],
        "final_safety_statement": (
            "Day79 defines a read-only task allowlist and blocked task taxonomy only. "
            "Read-only eligibility is not permission to run anything: every record keeps "
            "allowed_to_execute=false, dry_run_only=true, and "
            "execution_unlock_supported=false."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _record_rows(records: List[Dict[str, Any]]) -> str:
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record['contract_id']))}</td>"
            f"<td>{html.escape(str(record['requested_task']))}</td>"
            f"<td>{html.escape(str(record['contract_result']))}</td>"
            f"<td>{html.escape(str(record['readonly_eligible']))}</td>"
            f"<td>{html.escape(str(record['execution_candidate']))}</td>"
            f"<td>{html.escape(str(record['allowed_to_execute']))}</td>"
            f"<td>{html.escape(str(record['dry_run_only']))}</td>"
            f"<td>{html.escape(str(record['execution_unlock_supported']))}</td>"
            f"<td>{html.escape(str(record['policy_reason']))}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_readonly_task_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static HTML reviewer report."""
    summary = report["summary"]
    allowlist = report["allowlist"]
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
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Safety:</strong> deterministic mock-only / dry-run-only task eligibility contract.</p>
  <h2>Summary</h2>
  <table>
    <tbody>
      <tr><th>Contract records</th><td>{summary['contract_record_count']}</td></tr>
      <tr><th>Read-only eligible values</th><td>{html.escape(str(summary['readonly_eligible_values']))}</td></tr>
      <tr><th>Execution candidate values</th><td>{html.escape(str(summary['execution_candidate_values']))}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(summary['allowed_to_execute_values']))}</td></tr>
      <tr><th>Dry-run-only values</th><td>{html.escape(str(summary['dry_run_only_values']))}</td></tr>
      <tr><th>Execution unlock supported values</th><td>{html.escape(str(summary['execution_unlock_supported_values']))}</td></tr>
    </tbody>
  </table>
  <h2>Contract Records</h2>
  <table>
    <thead>
      <tr><th>Contract ID</th><th>Task</th><th>Result</th><th>Read-only eligible?</th><th>Candidate?</th><th>Allowed?</th><th>Dry-run only?</th><th>Unlock supported?</th><th>Policy reason</th></tr>
    </thead>
    <tbody>{_record_rows(report['contract_records'])}</tbody>
  </table>
  <h2>Allowlist and Blocks</h2>
  <h3>Read-only candidates</h3>
  <ul>{_html_list(allowlist['readonly_candidates'])}</ul>
  <h3>Blocked write actions</h3>
  <ul>{_html_list(allowlist['blocked_write_actions'])}</ul>
  <h3>Destructive actions</h3>
  <ul>{_html_list(allowlist['destructive_actions'])}</ul>
  <h3>Unknown / manual classification</h3>
  <ul>{_html_list(allowlist['unknown_manual_categories'])}</ul>
  <h2>Safety Boundary</h2>
  <ul>{_html_list(report['safety_boundary'])}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_readonly_task_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day79 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_readonly_task_contract_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_readonly_task_contract_html(safe_report, html_path)
    return json_path, html_path
