"""Day80 read-only execution broker skeleton.

This module builds deterministic, mock-only broker records for future
read-only request review. It does not connect to devices, run commands, or
unlock execution.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_readonly_task_contract import (
    NEEDS_MANUAL_CLASSIFICATION,
    READONLY_CONTRACT_READY,
    build_readonly_task_contract_records,
)


CREATED_AT = "2026-06-08T00:00:00Z"
TASK_NAME = "readonly-execution-broker"
EXECUTION_MODE = "deterministic_mock_only_readonly_broker_skeleton"
REPORT_JSON = Path("reports") / "lab-summary" / "day80_readonly_execution_broker.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day80_readonly_execution_broker.html"

RECEIVED = "RECEIVED"
REJECTED = "REJECTED"
QUEUED_FOR_REVIEW = "QUEUED_FOR_REVIEW"
MOCK_EXECUTION_REQUEST_PREPARED = "MOCK_EXECUTION_REQUEST_PREPARED"

BROKER_STATUSES = {
    RECEIVED,
    REJECTED,
    QUEUED_FOR_REVIEW,
    MOCK_EXECUTION_REQUEST_PREPARED,
}

REQUIRED_BROKER_FIELDS = (
    "request_id",
    "requested_task",
    "requested_intent",
    "contract_check_result",
    "allowlist_result",
    "broker_status",
    "rejection_reason",
    "mock_execution_request",
    "evidence_chain",
    "safety_invariants",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "device_connection_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "created_at",
)

MOCK_BROKER_REQUESTS = (
    {
        "request_id": "day80-request-001",
        "requested_task": "show_interface_status",
        "requested_intent": "Show interface status for the lab devices.",
        "readonly_scope": "mock_lab_device_group",
        "requires_manual_review": False,
        "expected_report_path": "reports/lab-summary/day81_mock_interface_status.json",
    },
    {
        "request_id": "day80-request-002",
        "requested_task": "show_log_summary",
        "requested_intent": "Review the recent lab device log summary before any future read-only collection.",
        "readonly_scope": "mock_router_log_summary",
        "requires_manual_review": True,
        "expected_report_path": "reports/lab-summary/day81_mock_log_summary.json",
    },
    {
        "request_id": "day80-request-003",
        "requested_task": "show_bgp_neighbors",
        "requested_intent": "Show BGP neighbors for this lab.",
        "readonly_scope": "unsupported_protocol_scope",
        "requires_manual_review": False,
        "expected_report_path": "reports/lab-summary/day81_unsupported_bgp_neighbors.json",
    },
    {
        "request_id": "day80-request-004",
        "requested_task": "add_firewall_rule",
        "requested_intent": "Add a firewall rule to allow a test flow.",
        "readonly_scope": "mock_router_firewall",
        "requires_manual_review": True,
        "expected_report_path": "reports/lab-summary/day81_blocked_firewall_change.json",
    },
    {
        "request_id": "day80-request-005",
        "requested_task": "needs_manual_classification",
        "requested_intent": "Please check whether the lab is healthy and fix anything suspicious.",
        "readonly_scope": "ambiguous_natural_language_scope",
        "requires_manual_review": True,
        "expected_report_path": "reports/lab-summary/day81_ambiguous_health_check.json",
    },
)


def _safety_invariants() -> Dict[str, Any]:
    return {
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "device_connection_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "deterministic": True,
        "mock_only": True,
        "model_provider_api_used": False,
        "ai_sdk_dependency_used": False,
        "device_access_used": False,
        "live_execution_used": False,
        "mapped_task_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }


def build_broker_request_records(
    requests: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic Day80 broker input request records."""
    source_requests = deepcopy(requests) if requests is not None else deepcopy(list(MOCK_BROKER_REQUESTS))
    records: List[Dict[str, Any]] = []
    for index, request in enumerate(source_requests, start=1):
        records.append(
            {
                "request_id": str(request.get("request_id", f"day80-request-{index:03d}")),
                "requested_task": str(request.get("requested_task", "unknown")),
                "requested_intent": str(request.get("requested_intent", "")),
                "readonly_scope": str(request.get("readonly_scope", "mock_unspecified_scope")),
                "requires_manual_review": bool(request.get("requires_manual_review", True)),
                "expected_report_path": str(request.get("expected_report_path", "")),
                "received_status": RECEIVED,
                "allowed_to_execute": False,
                "dry_run_only": True,
                "execution_unlock_supported": False,
                "device_connection_allowed": False,
                "ssh_allowed": False,
                "live_command_allowed": False,
                "created_at": CREATED_AT,
            }
        )
    return records


def _contract_record_for_request(request: Dict[str, Any]) -> Dict[str, Any]:
    scenarios = [
        {
            "scenario_id": f"day80-contract-check-{request['request_id']}",
            "intent_id": request["request_id"],
            "requested_task": request["requested_task"],
            "device_scope": {
                "scope_type": request["readonly_scope"],
                "devices": (),
            },
        }
    ]
    return build_readonly_task_contract_records(scenarios)[0]


def _allowlist_result(contract_record: Dict[str, Any]) -> str:
    if contract_record["contract_result"] == READONLY_CONTRACT_READY:
        return "ALLOWLIST_MATCH_READONLY_CANDIDATE"
    if contract_record["contract_result"] == NEEDS_MANUAL_CLASSIFICATION:
        return "ALLOWLIST_REVIEW_REQUIRED"
    return "ALLOWLIST_REJECTED"


def _rejection_reason(contract_record: Dict[str, Any]) -> Optional[str]:
    if contract_record["contract_result"] == READONLY_CONTRACT_READY:
        return None
    return str(contract_record["policy_reason"])


def _mock_execution_request(
    request: Dict[str, Any],
    contract_record: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if contract_record["contract_result"] != READONLY_CONTRACT_READY:
        return None
    if request["requires_manual_review"]:
        return None
    return {
        "mock_request_id": f"mock-{request['request_id']}",
        "task_name": request["requested_task"],
        "readonly_scope": request["readonly_scope"],
        "expected_report_path": request["expected_report_path"],
        "requires_manual_review": False,
        "execution_mode": "MOCK_ONLY",
        "live_execution": False,
        "data_object_only": True,
        "runnable_entrypoint": None,
    }


def _broker_status(
    request: Dict[str, Any],
    contract_record: Dict[str, Any],
) -> str:
    if contract_record["contract_result"] != READONLY_CONTRACT_READY:
        if contract_record["contract_result"] == NEEDS_MANUAL_CLASSIFICATION:
            return QUEUED_FOR_REVIEW
        return REJECTED
    if request["requires_manual_review"]:
        return QUEUED_FOR_REVIEW
    return MOCK_EXECUTION_REQUEST_PREPARED


def build_readonly_execution_broker_records(
    requests: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic Day80 broker decision records."""
    broker_requests = build_broker_request_records(requests)
    records: List[Dict[str, Any]] = []
    for request in broker_requests:
        contract_record = _contract_record_for_request(request)
        status = _broker_status(request, contract_record)
        evidence_chain = [
            "Day79 read-only task contract / allowlist",
            "Day80 broker request received",
            "Day80 contract check completed",
            "Day80 broker decision recorded",
            "Day80 review evidence produced",
        ]
        if status == MOCK_EXECUTION_REQUEST_PREPARED:
            evidence_chain.append("Mock execution request data object prepared")
        elif status == QUEUED_FOR_REVIEW:
            evidence_chain.append("Manual review queue record prepared")
        else:
            evidence_chain.append("Unsafe or unsupported request rejected")

        records.append(
            {
                "request_id": request["request_id"],
                "requested_task": request["requested_task"],
                "requested_intent": request["requested_intent"],
                "contract_check_result": contract_record["contract_result"],
                "contract_record_ref": contract_record["contract_id"],
                "allowlist_result": _allowlist_result(contract_record),
                "broker_status": status,
                "rejection_reason": _rejection_reason(contract_record) if status == REJECTED else None,
                "mock_execution_request": _mock_execution_request(request, contract_record),
                "evidence_chain": evidence_chain,
                "safety_invariants": _safety_invariants(),
                "allowed_to_execute": False,
                "dry_run_only": True,
                "execution_unlock_supported": False,
                "device_connection_allowed": False,
                "ssh_allowed": False,
                "live_command_allowed": False,
                "created_at": CREATED_AT,
            }
        )
    return records


def validate_readonly_execution_broker_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day80 broker records."""
    errors: List[str] = []
    if not records:
        errors.append("no read-only execution broker records were produced.")
        return errors

    for record in records:
        request_id = str(record.get("request_id", "<missing>"))
        for field in REQUIRED_BROKER_FIELDS:
            if field not in record:
                errors.append(f"{request_id} missing required field: {field}.")
        if record.get("broker_status") not in BROKER_STATUSES:
            errors.append(f"{request_id} has unknown broker_status.")
        for field, expected in (
            ("allowed_to_execute", False),
            ("dry_run_only", True),
            ("execution_unlock_supported", False),
            ("device_connection_allowed", False),
            ("ssh_allowed", False),
            ("live_command_allowed", False),
        ):
            if record.get(field) is not expected:
                errors.append(f"{request_id} {field} must be {str(expected).lower()}.")
            invariants = record.get("safety_invariants", {})
            if invariants.get(field) is not expected:
                errors.append(f"{request_id} invariant {field} must be {str(expected).lower()}.")
        if record.get("broker_status") == REJECTED and not record.get("rejection_reason"):
            errors.append(f"{request_id} rejected records must include rejection_reason.")
        if record.get("broker_status") != MOCK_EXECUTION_REQUEST_PREPARED:
            if record.get("mock_execution_request") is not None:
                errors.append(f"{request_id} only prepared mock records may include mock_execution_request.")
        else:
            mock_request = record.get("mock_execution_request")
            if not isinstance(mock_request, dict):
                errors.append(f"{request_id} prepared records must include mock_execution_request data.")
            elif mock_request.get("execution_mode") != "MOCK_ONLY" or mock_request.get("live_execution") is not False:
                errors.append(f"{request_id} mock_execution_request must stay MOCK_ONLY and non-live.")
    return errors


def build_readonly_execution_broker_report() -> Dict[str, Any]:
    """Build the Day80 read-only execution broker skeleton report."""
    records = build_readonly_execution_broker_records()
    validation_errors = validate_readonly_execution_broker_records(records)
    disabled_keys = {
        "model_provider_api_used",
        "ai_sdk_dependency_used",
        "device_access_used",
        "live_execution_used",
        "mapped_task_executed",
        "config_json_read",
        "dashboard_action_surface_added",
        "network_configuration_changed",
    }
    safety_invariants = {
        "allowed_to_execute_always_false": all(record["allowed_to_execute"] is False for record in records),
        "dry_run_only_always_true": all(record["dry_run_only"] is True for record in records),
        "execution_unlock_supported_always_false": all(
            record["execution_unlock_supported"] is False for record in records
        ),
        "device_connection_allowed_always_false": all(
            record["device_connection_allowed"] is False for record in records
        ),
        "ssh_allowed_always_false": all(record["ssh_allowed"] is False for record in records),
        "live_command_allowed_always_false": all(record["live_command_allowed"] is False for record in records),
        "broker_results_do_not_unlock_execution": True,
        "deterministic": True,
        "mock_only": True,
        "model_provider_api_used": False,
        "ai_sdk_dependency_used": False,
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
        "day": "Day80",
        "title": "Day80 Read-only Execution Broker Skeleton",
        "task_name": TASK_NAME,
        "execution_mode": EXECUTION_MODE,
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "summary": {
            "broker_record_count": len(records),
            "broker_statuses": sorted({record["broker_status"] for record in records}),
            "broker_status_counts": {
                status: sum(1 for record in records if record["broker_status"] == status)
                for status in sorted(BROKER_STATUSES)
            },
            "allowed_to_execute_values": sorted({record["allowed_to_execute"] for record in records}),
            "dry_run_only_values": sorted({record["dry_run_only"] for record in records}),
            "execution_unlock_supported_values": sorted(
                {record["execution_unlock_supported"] for record in records}
            ),
            "device_connection_allowed_values": sorted(
                {record["device_connection_allowed"] for record in records}
            ),
            "ssh_allowed_values": sorted({record["ssh_allowed"] for record in records}),
            "live_command_allowed_values": sorted({record["live_command_allowed"] for record in records}),
        },
        "broker_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Deterministic fixed mock data only.",
            "Broker skeleton and review evidence only.",
            "No model-provider API.",
            "No AI SDK dependency.",
            "No SSH.",
            "No device access.",
            "No live command execution.",
            "No mapped task execution.",
            "No config.json dependency.",
            "No approval unlock.",
            "No dashboard action surface.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": [
            "docs/ai/intent_readonly_execution_broker.md",
            "docs/roadmap/day80_readonly_execution_broker_skeleton.md",
            "docs/ai/intent_readonly_task_contract.md",
            REPORT_JSON.as_posix(),
            REPORT_HTML.as_posix(),
        ],
        "final_safety_statement": (
            "Day80 receives fixed mock read-only task requests, validates them against "
            "the Day79 contract, rejects unsafe requests, queues review-only requests, "
            "or prepares mock execution request data while keeping execution disabled."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _record_rows(records: List[Dict[str, Any]]) -> str:
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record['request_id']))}</td>"
            f"<td>{html.escape(str(record['requested_task']))}</td>"
            f"<td>{html.escape(str(record['contract_check_result']))}</td>"
            f"<td>{html.escape(str(record['allowlist_result']))}</td>"
            f"<td>{html.escape(str(record['broker_status']))}</td>"
            f"<td>{html.escape(str(record['allowed_to_execute']))}</td>"
            f"<td>{html.escape(str(record['dry_run_only']))}</td>"
            f"<td>{html.escape(str(record['execution_unlock_supported']))}</td>"
            f"<td>{html.escape(str(record['ssh_allowed']))}</td>"
            f"<td>{html.escape(str(record['live_command_allowed']))}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_readonly_execution_broker_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static HTML reviewer report."""
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
  <p><strong>Overall status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['reviewer_status'])}</p>
  <p><strong>Safety:</strong> deterministic mock-only broker skeleton; no execution is unlocked.</p>
  <h2>Summary</h2>
  <table>
    <tbody>
      <tr><th>Broker records</th><td>{summary['broker_record_count']}</td></tr>
      <tr><th>Broker statuses</th><td>{html.escape(str(summary['broker_statuses']))}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(summary['allowed_to_execute_values']))}</td></tr>
      <tr><th>Dry-run-only values</th><td>{html.escape(str(summary['dry_run_only_values']))}</td></tr>
      <tr><th>Execution unlock supported values</th><td>{html.escape(str(summary['execution_unlock_supported_values']))}</td></tr>
      <tr><th>SSH allowed values</th><td>{html.escape(str(summary['ssh_allowed_values']))}</td></tr>
      <tr><th>Live command allowed values</th><td>{html.escape(str(summary['live_command_allowed_values']))}</td></tr>
    </tbody>
  </table>
  <h2>Broker Records</h2>
  <table>
    <thead>
      <tr><th>Request ID</th><th>Task</th><th>Contract result</th><th>Allowlist result</th><th>Broker status</th><th>Allowed?</th><th>Dry-run only?</th><th>Unlock supported?</th><th>SSH allowed?</th><th>Live command allowed?</th></tr>
    </thead>
    <tbody>{_record_rows(report['broker_records'])}</tbody>
  </table>
  <h2>Safety Boundary</h2>
  <ul>{_html_list(report['safety_boundary'])}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_readonly_execution_broker_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day80 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_readonly_execution_broker_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_readonly_execution_broker_html(safe_report, html_path)
    return json_path, html_path
