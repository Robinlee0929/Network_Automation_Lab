"""Day81 read-only broker review queue and decision state report.

This module transforms deterministic Day80 broker records into reviewer-facing
queue state records. It is offline, mock-only, report-only, and cannot unlock
execution.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_readonly_execution_broker import (
    MOCK_EXECUTION_REQUEST_PREPARED as DAY80_MOCK_EXECUTION_REQUEST_PREPARED,
    QUEUED_FOR_REVIEW as DAY80_QUEUED_FOR_REVIEW,
    REJECTED as DAY80_REJECTED,
    build_readonly_execution_broker_records,
)


CREATED_AT = "2026-06-08T00:00:00Z"
TASK_NAME = "broker-review-queue"
EXECUTION_MODE = "deterministic_mock_only_broker_review_queue"
REPORT_JSON = Path("reports") / "lab-summary" / "day81_broker_review_queue.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day81_broker_review_queue.html"

REJECTED_BY_BROKER = "REJECTED_BY_BROKER"
QUEUED_FOR_HUMAN_REVIEW = "QUEUED_FOR_HUMAN_REVIEW"
MOCK_EXECUTION_REQUEST_PREPARED = "MOCK_EXECUTION_REQUEST_PREPARED"
REVIEW_BLOCKED_BY_POLICY = "REVIEW_BLOCKED_BY_POLICY"
REVIEW_READY_NO_EXECUTION = "REVIEW_READY_NO_EXECUTION"

REVIEW_STATE_SEQUENCE = (
    REJECTED_BY_BROKER,
    QUEUED_FOR_HUMAN_REVIEW,
    MOCK_EXECUTION_REQUEST_PREPARED,
    REVIEW_BLOCKED_BY_POLICY,
    REVIEW_READY_NO_EXECUTION,
)
REVIEW_STATES = set(REVIEW_STATE_SEQUENCE)

REJECT = "REJECT"
HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
MOCK_ONLY = "MOCK_ONLY"
POLICY_BLOCKED = "POLICY_BLOCKED"
REVIEW_ONLY = "REVIEW_ONLY"

DECISION_STATE_SEQUENCE = (
    REJECT,
    HOLD_FOR_REVIEW,
    MOCK_ONLY,
    POLICY_BLOCKED,
    REVIEW_ONLY,
)
DECISION_STATES = set(DECISION_STATE_SEQUENCE)

REQUIRED_QUEUE_FIELDS = (
    "queue_id",
    "source_request_id",
    "requested_task",
    "requested_intent",
    "broker_status",
    "review_state",
    "decision_state",
    "review_required",
    "review_reason",
    "safety_boundary",
    "allowed_to_execute",
    "dry_run_only",
    "execution_unlock_supported",
    "device_connection_allowed",
    "ssh_allowed",
    "live_command_allowed",
    "mapped_task_execution_allowed",
    "dashboard_action_allowed",
    "final_recommendation",
    "evidence_chain",
    "report_only",
    "created_at",
)


def _safety_boundary() -> Dict[str, Any]:
    return {
        "review_only": True,
        "mock_only": True,
        "report_only": True,
        "deterministic": True,
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "device_connection_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "mapped_task_execution_allowed": False,
        "dashboard_action_allowed": False,
        "model_provider_api_used": False,
        "ai_sdk_dependency_used": False,
        "voice_integration_used": False,
        "config_json_read": False,
        "network_configuration_changed": False,
    }


def _state_for_broker_record(record: Dict[str, Any]) -> Tuple[str, str, str, str]:
    request_id = str(record.get("request_id", ""))
    broker_status = str(record.get("broker_status", ""))
    contract_result = str(record.get("contract_check_result", ""))

    if broker_status == DAY80_MOCK_EXECUTION_REQUEST_PREPARED:
        return (
            MOCK_EXECUTION_REQUEST_PREPARED,
            MOCK_ONLY,
            "Mock request data exists for reviewer inspection only.",
            "Review the mock request data object only; no execution approval is possible.",
        )
    if broker_status == DAY80_QUEUED_FOR_REVIEW and request_id.endswith("005"):
        return (
            REVIEW_READY_NO_EXECUTION,
            REVIEW_ONLY,
            "Ambiguous request is ready for reviewer reading without execution.",
            "Use as review-only evidence; do not execute or approve a task.",
        )
    if broker_status == DAY80_QUEUED_FOR_REVIEW:
        return (
            QUEUED_FOR_HUMAN_REVIEW,
            HOLD_FOR_REVIEW,
            "Broker requires human review before any future design step.",
            "Hold for reviewer interpretation only; no execution path is available.",
        )
    if broker_status == DAY80_REJECTED and contract_result == "BLOCKED_WRITE_ACTION":
        return (
            REVIEW_BLOCKED_BY_POLICY,
            POLICY_BLOCKED,
            "Request is blocked by policy because it implies a write or configuration change.",
            "Keep policy-blocked and report-only; do not execute.",
        )
    return (
        REJECTED_BY_BROKER,
        REJECT,
        "Broker rejected the request as unsupported or outside the read-only contract.",
        "Reject for execution; retain only the reviewer evidence record.",
    )


def build_broker_review_queue_records(
    broker_records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic Day81 queue records from Day80 broker records."""
    source_records = (
        deepcopy(broker_records)
        if broker_records is not None
        else build_readonly_execution_broker_records()
    )
    queue_records: List[Dict[str, Any]] = []
    for index, broker_record in enumerate(source_records, start=1):
        review_state, decision_state, review_reason, final_recommendation = _state_for_broker_record(
            broker_record
        )
        source_request_id = str(broker_record.get("request_id", f"day80-request-{index:03d}"))
        queue_records.append(
            {
                "queue_id": f"day81-queue-{index:03d}",
                "source_request_id": source_request_id,
                "requested_task": str(broker_record.get("requested_task", "unknown")),
                "requested_intent": str(broker_record.get("requested_intent", "")),
                "broker_status": str(broker_record.get("broker_status", "")),
                "review_state": review_state,
                "decision_state": decision_state,
                "review_required": True,
                "review_reason": review_reason,
                "safety_boundary": _safety_boundary(),
                "allowed_to_execute": False,
                "dry_run_only": True,
                "execution_unlock_supported": False,
                "device_connection_allowed": False,
                "ssh_allowed": False,
                "live_command_allowed": False,
                "mapped_task_execution_allowed": False,
                "dashboard_action_allowed": False,
                "final_recommendation": final_recommendation,
                "evidence_chain": [
                    "Day79 read-only task contract and allowlist reference",
                    "Day80 read-only execution broker skeleton record",
                    f"Day80 source request: {source_request_id}",
                    "Day81 broker review queue state assigned",
                    "Day81 decision state recorded for reviewer report only",
                ],
                "report_only": True,
                "created_at": CREATED_AT,
            }
        )
    return queue_records


def validate_broker_review_queue_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day81 queue records."""
    errors: List[str] = []
    if len(records) != 5:
        errors.append("exactly 5 broker review queue records must be produced.")

    expected_queue_ids = [f"day81-queue-{index:03d}" for index in range(1, 6)]
    if [record.get("queue_id") for record in records] != expected_queue_ids:
        errors.append("queue_id values must be stable day81-queue-001 through day81-queue-005.")

    for record in records:
        queue_id = str(record.get("queue_id", "<missing>"))
        for field in REQUIRED_QUEUE_FIELDS:
            if field not in record:
                errors.append(f"{queue_id} missing required field: {field}.")
        if record.get("review_state") not in REVIEW_STATES:
            errors.append(f"{queue_id} has unknown review_state.")
        if record.get("decision_state") not in DECISION_STATES:
            errors.append(f"{queue_id} has unknown decision_state.")
        for field, expected in (
            ("allowed_to_execute", False),
            ("dry_run_only", True),
            ("execution_unlock_supported", False),
            ("device_connection_allowed", False),
            ("ssh_allowed", False),
            ("live_command_allowed", False),
            ("mapped_task_execution_allowed", False),
            ("dashboard_action_allowed", False),
            ("report_only", True),
        ):
            if record.get(field) is not expected:
                errors.append(f"{queue_id} {field} must be {str(expected).lower()}.")
            boundary = record.get("safety_boundary", {})
            if boundary.get(field) is not expected:
                errors.append(f"{queue_id} safety_boundary {field} must be {str(expected).lower()}.")
        recommendation = str(record.get("final_recommendation", "")).lower()
        if "approve execution" in recommendation or "allowed to execute" in recommendation:
            errors.append(f"{queue_id} final_recommendation must not imply execution approval.")
        evidence_text = " ".join(str(item) for item in record.get("evidence_chain", []))
        if "Day79" not in evidence_text or "Day80" not in evidence_text:
            errors.append(f"{queue_id} evidence_chain must reference Day79 and Day80.")
    return errors


def _ordered_present(values: List[str], ordered_values: Tuple[str, ...]) -> List[str]:
    seen = set(values)
    return [value for value in ordered_values if value in seen]


def build_broker_review_queue_report() -> Dict[str, Any]:
    """Build the Day81 broker review queue and decision state report."""
    records = build_broker_review_queue_records()
    validation_errors = validate_broker_review_queue_records(records)
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
        "mapped_task_execution_allowed_always_false": all(
            record["mapped_task_execution_allowed"] is False for record in records
        ),
        "dashboard_action_allowed_always_false": all(
            record["dashboard_action_allowed"] is False for record in records
        ),
        "report_only_always_true": all(record["report_only"] is True for record in records),
        "broker_queue_does_not_unlock_execution": True,
        "deterministic": True,
        "mock_only": True,
        "model_provider_api_used": False,
        "ai_sdk_dependency_used": False,
        "voice_integration_used": False,
        "device_access_used": False,
        "live_execution_used": False,
        "mapped_task_executed": False,
        "config_json_read": False,
        "dashboard_action_surface_added": False,
        "network_configuration_changed": False,
    }
    disabled_keys = {
        "model_provider_api_used",
        "ai_sdk_dependency_used",
        "voice_integration_used",
        "device_access_used",
        "live_execution_used",
        "mapped_task_executed",
        "config_json_read",
        "dashboard_action_surface_added",
        "network_configuration_changed",
    }
    overall_status = "PASS" if not validation_errors and all(
        value is False if key in disabled_keys else value is True
        for key, value in safety_invariants.items()
    ) else "FAIL"
    return {
        "day": "Day81",
        "title": "Day81 Read-only Broker Review Queue & Decision State Report",
        "task_name": TASK_NAME,
        "execution_mode": EXECUTION_MODE,
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "created_at": CREATED_AT,
        "summary": {
            "queue_record_count": len(records),
            "broker_statuses": sorted({record["broker_status"] for record in records}),
            "review_states": _ordered_present(
                [record["review_state"] for record in records],
                REVIEW_STATE_SEQUENCE,
            ),
            "decision_states": _ordered_present(
                [record["decision_state"] for record in records],
                DECISION_STATE_SEQUENCE,
            ),
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
            "mapped_task_execution_allowed_values": sorted(
                {record["mapped_task_execution_allowed"] for record in records}
            ),
            "dashboard_action_allowed_values": sorted(
                {record["dashboard_action_allowed"] for record in records}
            ),
            "report_only_values": sorted({record["report_only"] for record in records}),
        },
        "queue_records": records,
        "validation_errors": validation_errors,
        "safety_invariants": safety_invariants,
        "safety_boundary": [
            "Deterministic fixed mock data only.",
            "Broker review queue and decision state report only.",
            "No request is allowed to execute.",
            "No model-provider API.",
            "No AI SDK dependency.",
            "No voice integration.",
            "No SSH.",
            "No device access.",
            "No live command execution.",
            "No mapped task execution.",
            "No config.json dependency.",
            "No approval unlock.",
            "No dashboard form or action endpoint.",
            "No router, switch, firewall, VPN, VRRP, or network configuration change.",
        ],
        "evidence_links_or_doc_refs": [
            "docs/ai/intent_broker_review_queue.md",
            "docs/roadmap/day81_broker_review_queue.md",
            "docs/ai/intent_readonly_task_contract.md",
            "docs/ai/intent_readonly_execution_broker.md",
            REPORT_JSON.as_posix(),
            REPORT_HTML.as_posix(),
        ],
        "final_safety_statement": (
            "Day81 transforms Day80 mock broker records into reviewer-facing queue "
            "and decision state records. No request is allowed to execute."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _record_rows(records: List[Dict[str, Any]]) -> str:
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record['queue_id']))}</td>"
            f"<td>{html.escape(str(record['source_request_id']))}</td>"
            f"<td>{html.escape(str(record['requested_task']))}</td>"
            f"<td>{html.escape(str(record['broker_status']))}</td>"
            f"<td>{html.escape(str(record['review_state']))}</td>"
            f"<td>{html.escape(str(record['decision_state']))}</td>"
            f"<td>{html.escape(str(record['allowed_to_execute']))}</td>"
            f"<td>{html.escape(str(record['dry_run_only']))}</td>"
            f"<td>{html.escape(str(record['execution_unlock_supported']))}</td>"
            f"<td>{html.escape(str(record['ssh_allowed']))}</td>"
            f"<td>{html.escape(str(record['live_command_allowed']))}</td>"
            f"<td>{html.escape(str(record['mapped_task_execution_allowed']))}</td>"
            f"<td>{html.escape(str(record['dashboard_action_allowed']))}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_broker_review_queue_html(report: Dict[str, Any], output_path: Path) -> None:
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
  <p><strong>Safety:</strong> no request is allowed to execute; this report is static, read-only, mock-only, dry-run-only, and report-only.</p>
  <h2>Summary</h2>
  <table>
    <tbody>
      <tr><th>Queue records</th><td>{summary['queue_record_count']}</td></tr>
      <tr><th>Broker statuses</th><td>{html.escape(str(summary['broker_statuses']))}</td></tr>
      <tr><th>Review states</th><td>{html.escape(str(summary['review_states']))}</td></tr>
      <tr><th>Decision states</th><td>{html.escape(str(summary['decision_states']))}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(summary['allowed_to_execute_values']))}</td></tr>
      <tr><th>Dry-run-only values</th><td>{html.escape(str(summary['dry_run_only_values']))}</td></tr>
      <tr><th>Execution unlock supported values</th><td>{html.escape(str(summary['execution_unlock_supported_values']))}</td></tr>
      <tr><th>Device connection allowed values</th><td>{html.escape(str(summary['device_connection_allowed_values']))}</td></tr>
      <tr><th>SSH allowed values</th><td>{html.escape(str(summary['ssh_allowed_values']))}</td></tr>
      <tr><th>Live command allowed values</th><td>{html.escape(str(summary['live_command_allowed_values']))}</td></tr>
      <tr><th>Mapped task execution allowed values</th><td>{html.escape(str(summary['mapped_task_execution_allowed_values']))}</td></tr>
      <tr><th>Dashboard action allowed values</th><td>{html.escape(str(summary['dashboard_action_allowed_values']))}</td></tr>
    </tbody>
  </table>
  <h2>Queue Records</h2>
  <table>
    <thead>
      <tr><th>Queue ID</th><th>Source request</th><th>Task</th><th>Broker status</th><th>Review state</th><th>Decision state</th><th>Allowed?</th><th>Dry-run?</th><th>Unlock?</th><th>SSH?</th><th>Live command?</th><th>Mapped task?</th><th>Dashboard action?</th></tr>
    </thead>
    <tbody>{_record_rows(report['queue_records'])}</tbody>
  </table>
  <h2>Evidence Chain</h2>
  <ul>{_html_list(report['queue_records'][0]['evidence_chain'])}</ul>
  <h2>Safety Boundary</h2>
  <ul>{_html_list(report['safety_boundary'])}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_broker_review_queue_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day81 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_broker_review_queue_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_broker_review_queue_html(safe_report, html_path)
    return json_path, html_path
