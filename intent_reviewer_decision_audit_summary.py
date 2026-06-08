"""Day82 reviewer decision audit summary and queue evidence export.

This module converts deterministic Day81 broker review queue records into a
reviewer-facing audit summary. It is offline, mock-only, review-only, and cannot
unlock execution.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_broker_review_queue import build_broker_review_queue_report


CREATED_AT = "2026-06-08T00:00:00Z"
TASK_NAME = "reviewer-decision-audit-summary"
TITLE = "Reviewer Decision Audit Summary / Queue Evidence Export"
STATUS = "REVIEW_READY"
EXECUTION_MODE = "deterministic_mock_only_reviewer_decision_audit_summary"
REPORT_JSON = Path("reports") / "lab-summary" / "day82_reviewer_decision_audit_summary.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day82_reviewer_decision_audit_summary.html"

REQUIRED_TOP_LEVEL_FIELDS = (
    "day",
    "title",
    "status",
    "review_scope",
    "source_chain",
    "decision_summary",
    "evidence_exports",
    "safety_invariants",
    "traceability_map",
    "reviewer_notes",
    "reports",
)

REQUIRED_EXECUTION_FLAGS = (
    ("allowed_to_execute", False),
    ("dry_run_only", True),
    ("execution_unlock_supported", False),
    ("device_connection_allowed", False),
    ("ssh_allowed", False),
    ("live_command_allowed", False),
    ("network_change_allowed", False),
    ("ai_runtime_allowed", False),
    ("dashboard_action_allowed", False),
)


def _safety_flags() -> Dict[str, Any]:
    return {
        "allowed_to_execute": False,
        "dry_run_only": True,
        "execution_unlock_supported": False,
        "device_connection_allowed": False,
        "ssh_allowed": False,
        "live_command_allowed": False,
        "network_change_allowed": False,
        "ai_runtime_allowed": False,
        "dashboard_action_allowed": False,
        "mapped_task_execution_allowed": False,
        "model_provider_api_used": False,
        "ai_sdk_dependency_used": False,
        "voice_integration_used": False,
        "config_json_read": False,
        "live_execution_used": False,
        "mapped_task_executed": False,
        "dashboard_action_surface_added": False,
    }


def _count_by(records: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    values = sorted({str(record.get(field, "")) for record in records})
    return {value: sum(1 for record in records if str(record.get(field, "")) == value) for value in values}


def build_queue_evidence_exports(
    queue_records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build deterministic reviewer evidence exports from Day81 queue records."""
    source_records = (
        deepcopy(queue_records)
        if queue_records is not None
        else deepcopy(build_broker_review_queue_report()["queue_records"])
    )
    exports: List[Dict[str, Any]] = []
    for index, record in enumerate(source_records, start=1):
        safety_flags = _safety_flags()
        exports.append(
            {
                "export_id": f"day82-evidence-export-{index:03d}",
                "source_day": "Day81",
                "source_queue_id": str(record.get("queue_id", f"day81-queue-{index:03d}")),
                "source_request_id": str(record.get("source_request_id", "")),
                "requested_task": str(record.get("requested_task", "")),
                "requested_intent": str(record.get("requested_intent", "")),
                "broker_status": str(record.get("broker_status", "")),
                "review_state": str(record.get("review_state", "")),
                "decision_state": str(record.get("decision_state", "")),
                "review_required": bool(record.get("review_required", True)),
                "review_reason": str(record.get("review_reason", "")),
                "final_recommendation": str(record.get("final_recommendation", "")),
                "safety_invariants": safety_flags,
                "allowed_to_execute": False,
                "dry_run_only": True,
                "execution_unlock_supported": False,
                "device_connection_allowed": False,
                "ssh_allowed": False,
                "live_command_allowed": False,
                "network_change_allowed": False,
                "ai_runtime_allowed": False,
                "dashboard_action_allowed": False,
                "evidence_chain": [
                    "Day79 Read-only Task Contract",
                    "Day80 Read-only Execution Broker Skeleton",
                    "Day81 Broker Review Queue & Decision State Report",
                    f"Day81 source queue record: {record.get('queue_id', '')}",
                    "Day82 Reviewer Decision Audit Summary / Queue Evidence Export",
                ],
                "reviewer_export_purpose": (
                    "Summarize the Day81 queue decision and safety evidence for "
                    "human audit only; no execution approval is possible."
                ),
                "created_at": CREATED_AT,
            }
        )
    return exports


def _traceability_map() -> List[Dict[str, Any]]:
    return [
        {
            "day": "Day79",
            "artifact": "Day79 Read-only Task Contract",
            "role": "Defines read-only candidates, blocked write actions, destructive actions, unknown tasks, and manual classification boundaries.",
            "evidence_refs": [
                "docs/ai/intent_readonly_task_contract.md",
                "docs/roadmap/day79_readonly_task_contract.md",
                "reports/lab-summary/day79_readonly_task_contract.json",
                "reports/lab-summary/day79_readonly_task_contract.html",
            ],
        },
        {
            "day": "Day80",
            "artifact": "Day80 Read-only Execution Broker Skeleton",
            "role": "Transforms fixed mock requests into rejected, queued-for-review, or mock request data records without execution.",
            "evidence_refs": [
                "docs/ai/intent_readonly_execution_broker.md",
                "docs/roadmap/day80_readonly_execution_broker_skeleton.md",
                "reports/lab-summary/day80_readonly_execution_broker.json",
                "reports/lab-summary/day80_readonly_execution_broker.html",
            ],
        },
        {
            "day": "Day81",
            "artifact": "Day81 Broker Review Queue & Decision State Report",
            "role": "Assigns reviewer-facing queue states and decision states to Day80 broker records.",
            "evidence_refs": [
                "docs/ai/intent_broker_review_queue.md",
                "docs/roadmap/day81_broker_review_queue.md",
                "reports/lab-summary/day81_broker_review_queue.json",
                "reports/lab-summary/day81_broker_review_queue.html",
            ],
        },
        {
            "day": "Day82",
            "artifact": TITLE,
            "role": "Summarizes Day81 reviewer decisions and exports queue evidence for audit review only.",
            "evidence_refs": [
                "docs/ai/intent_reviewer_decision_audit_summary.md",
                "docs/roadmap/day82_reviewer_decision_audit_summary.md",
                REPORT_JSON.as_posix(),
                REPORT_HTML.as_posix(),
            ],
        },
    ]


def build_reviewer_decision_audit_summary_report() -> Dict[str, Any]:
    """Build the deterministic Day82 reviewer decision audit summary."""
    day81_report = build_broker_review_queue_report()
    queue_records = deepcopy(day81_report["queue_records"])
    evidence_exports = build_queue_evidence_exports(queue_records)
    validation_errors = validate_reviewer_decision_audit_summary_exports(evidence_exports)

    safety_invariants = _safety_flags()
    safety_invariants.update(
        {
            "day81_queue_record_count": len(queue_records),
            "day82_evidence_export_count": len(evidence_exports),
            "all_day82_records_preserve_required_flags": not validation_errors,
            "review_only": True,
            "mock_only": True,
            "deterministic": True,
            "report_only": True,
            "approval_unlock_supported": False,
            "execution_endpoint_added": False,
            "dashboard_post_route_added": False,
            "validation_errors": validation_errors,
        }
    )

    overall_status = "PASS" if not validation_errors else "FAIL"
    return {
        "day": "Day82",
        "title": TITLE,
        "status": STATUS if overall_status == "PASS" else "REVIEW_REQUIRED",
        "task_name": TASK_NAME,
        "execution_mode": EXECUTION_MODE,
        "overall_status": overall_status,
        "created_at": CREATED_AT,
        "review_scope": {
            "scope_type": "reviewer_decision_audit_summary",
            "source_report": "Day81 broker review queue and decision state records",
            "source_queue_records": len(queue_records),
            "day82_behavior": "summarize_and_export_review_evidence_only",
            "not_a_duplicate_of_day81": (
                "Day81 creates queue and decision state records. Day82 summarizes "
                "those records, exports evidence, proves invariants, and maps the "
                "Day79-Day82 audit chain."
            ),
        },
        "source_chain": [
            "Day79 Read-only Task Contract",
            "Day80 Read-only Execution Broker Skeleton",
            "Day81 Broker Review Queue & Decision State Report",
            "Day82 Reviewer Decision Audit Summary / Queue Evidence Export",
        ],
        "decision_summary": {
            "queue_record_count": len(queue_records),
            "evidence_export_count": len(evidence_exports),
            "broker_status_counts": _count_by(queue_records, "broker_status"),
            "review_state_counts": _count_by(queue_records, "review_state"),
            "decision_state_counts": _count_by(queue_records, "decision_state"),
            "allowed_to_execute_values": sorted({item["allowed_to_execute"] for item in evidence_exports}),
            "dry_run_only_values": sorted({item["dry_run_only"] for item in evidence_exports}),
            "execution_unlock_supported_values": sorted(
                {item["execution_unlock_supported"] for item in evidence_exports}
            ),
            "device_connection_allowed_values": sorted(
                {item["device_connection_allowed"] for item in evidence_exports}
            ),
            "ssh_allowed_values": sorted({item["ssh_allowed"] for item in evidence_exports}),
            "live_command_allowed_values": sorted({item["live_command_allowed"] for item in evidence_exports}),
            "network_change_allowed_values": sorted(
                {item["network_change_allowed"] for item in evidence_exports}
            ),
            "ai_runtime_allowed_values": sorted({item["ai_runtime_allowed"] for item in evidence_exports}),
            "dashboard_action_allowed_values": sorted(
                {item["dashboard_action_allowed"] for item in evidence_exports}
            ),
        },
        "evidence_exports": evidence_exports,
        "safety_invariants": safety_invariants,
        "traceability_map": _traceability_map(),
        "reviewer_notes": [
            "Day82 is an audit/evidence export layer only.",
            "Day82 consumes deterministic Day81 queue records and does not create another queue.",
            "No Day82 field can approve, unlock, or trigger execution.",
            "The dashboard remains static and read-only with no form, POST route, or action endpoint.",
            "The runner does not require config.json and does not execute mapped tasks.",
        ],
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
            "source_day81_json": "reports/lab-summary/day81_broker_review_queue.json",
            "source_day81_html": "reports/lab-summary/day81_broker_review_queue.html",
        },
    }


def validate_reviewer_decision_audit_summary_exports(exports: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for Day82 evidence exports."""
    errors: List[str] = []
    if len(exports) != 5:
        errors.append("exactly 5 Day82 evidence exports must be produced from Day81 queue records.")

    expected_export_ids = [f"day82-evidence-export-{index:03d}" for index in range(1, 6)]
    if [record.get("export_id") for record in exports] != expected_export_ids:
        errors.append("export_id values must be stable day82-evidence-export-001 through 005.")

    for record in exports:
        export_id = str(record.get("export_id", "<missing>"))
        for field, expected in REQUIRED_EXECUTION_FLAGS:
            if record.get(field) is not expected:
                errors.append(f"{export_id} {field} must be {str(expected).lower()}.")
            invariants = record.get("safety_invariants", {})
            if invariants.get(field) is not expected:
                errors.append(f"{export_id} safety_invariants {field} must be {str(expected).lower()}.")
        evidence_text = " ".join(str(item) for item in record.get("evidence_chain", []))
        for day in ("Day79", "Day80", "Day81", "Day82"):
            if day not in evidence_text:
                errors.append(f"{export_id} evidence_chain must reference {day}.")
        recommendation = str(record.get("final_recommendation", "")).lower()
        if "approve execution" in recommendation or "allowed to execute" in recommendation:
            errors.append(f"{export_id} final_recommendation must not imply execution approval.")
    return errors


def validate_reviewer_decision_audit_summary_report(report: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for the Day82 report."""
    errors: List[str] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in report:
            errors.append(f"report missing required top-level field: {field}.")
    errors.extend(validate_reviewer_decision_audit_summary_exports(report.get("evidence_exports", [])))
    traceability_text = json.dumps(report.get("traceability_map", []), sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82"):
        if day not in traceability_text:
            errors.append(f"traceability_map must include {day}.")
    for field, expected in REQUIRED_EXECUTION_FLAGS:
        if report.get("safety_invariants", {}).get(field) is not expected:
            errors.append(f"safety_invariants {field} must be {str(expected).lower()}.")
    return errors


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _traceability_rows(items: List[Dict[str, Any]]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item['day']))}</td>"
            f"<td>{html.escape(str(item['artifact']))}</td>"
            f"<td>{html.escape(str(item['role']))}</td>"
            f"<td><ul>{_html_list(item['evidence_refs'])}</ul></td>"
            "</tr>"
        )
    return "".join(rows)


def _evidence_rows(records: List[Dict[str, Any]]) -> str:
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(record['export_id']))}</td>"
            f"<td>{html.escape(str(record['source_queue_id']))}</td>"
            f"<td>{html.escape(str(record['requested_task']))}</td>"
            f"<td>{html.escape(str(record['review_state']))}</td>"
            f"<td>{html.escape(str(record['decision_state']))}</td>"
            f"<td>{html.escape(str(record['allowed_to_execute']))}</td>"
            f"<td>{html.escape(str(record['dry_run_only']))}</td>"
            f"<td>{html.escape(str(record['execution_unlock_supported']))}</td>"
            f"<td>{html.escape(str(record['device_connection_allowed']))}</td>"
            f"<td>{html.escape(str(record['ssh_allowed']))}</td>"
            f"<td>{html.escape(str(record['live_command_allowed']))}</td>"
            f"<td>{html.escape(str(record['network_change_allowed']))}</td>"
            f"<td>{html.escape(str(record['ai_runtime_allowed']))}</td>"
            f"<td>{html.escape(str(record['dashboard_action_allowed']))}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_reviewer_decision_audit_summary_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static HTML reviewer audit report."""
    summary = report["decision_summary"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day82 {html.escape(report['title'])}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    code {{ background: #eef2f6; padding: 1px 4px; border-radius: 3px; }}
  </style>
</head>
<body>
  <h1>Day82 {html.escape(report['title'])}</h1>
  <p><strong>Status:</strong> {html.escape(report['overall_status'])} / {html.escape(report['status'])}</p>
  <p><strong>Safety:</strong> review-only, mock/deterministic, no live execution, no SSH/device access, no OpenAI API or AI SDK runtime, and no dashboard action endpoint.</p>
  <h2>Decision Summary</h2>
  <table>
    <tbody>
      <tr><th>Queue records</th><td>{summary['queue_record_count']}</td></tr>
      <tr><th>Evidence exports</th><td>{summary['evidence_export_count']}</td></tr>
      <tr><th>Broker status counts</th><td>{html.escape(str(summary['broker_status_counts']))}</td></tr>
      <tr><th>Review state counts</th><td>{html.escape(str(summary['review_state_counts']))}</td></tr>
      <tr><th>Decision state counts</th><td>{html.escape(str(summary['decision_state_counts']))}</td></tr>
      <tr><th>Allowed to execute values</th><td>{html.escape(str(summary['allowed_to_execute_values']))}</td></tr>
      <tr><th>Dry-run-only values</th><td>{html.escape(str(summary['dry_run_only_values']))}</td></tr>
      <tr><th>Execution unlock supported values</th><td>{html.escape(str(summary['execution_unlock_supported_values']))}</td></tr>
      <tr><th>Device connection allowed values</th><td>{html.escape(str(summary['device_connection_allowed_values']))}</td></tr>
      <tr><th>SSH allowed values</th><td>{html.escape(str(summary['ssh_allowed_values']))}</td></tr>
      <tr><th>Live command allowed values</th><td>{html.escape(str(summary['live_command_allowed_values']))}</td></tr>
      <tr><th>Network change allowed values</th><td>{html.escape(str(summary['network_change_allowed_values']))}</td></tr>
      <tr><th>AI runtime allowed values</th><td>{html.escape(str(summary['ai_runtime_allowed_values']))}</td></tr>
      <tr><th>Dashboard action allowed values</th><td>{html.escape(str(summary['dashboard_action_allowed_values']))}</td></tr>
    </tbody>
  </table>
  <h2>Evidence Exports</h2>
  <table>
    <thead>
      <tr><th>Export ID</th><th>Queue ID</th><th>Task</th><th>Review state</th><th>Decision state</th><th>Allowed?</th><th>Dry-run?</th><th>Unlock?</th><th>Device?</th><th>SSH?</th><th>Live command?</th><th>Network change?</th><th>AI runtime?</th><th>Dashboard action?</th></tr>
    </thead>
    <tbody>{_evidence_rows(report['evidence_exports'])}</tbody>
  </table>
  <h2>Traceability Map</h2>
  <table>
    <thead><tr><th>Day</th><th>Artifact</th><th>Role</th><th>Evidence</th></tr></thead>
    <tbody>{_traceability_rows(report['traceability_map'])}</tbody>
  </table>
  <h2>Reviewer Notes</h2>
  <ul>{_html_list(report['reviewer_notes'])}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_reviewer_decision_audit_summary_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day82 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_reviewer_decision_audit_summary_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_reviewer_decision_audit_summary_html(safe_report, html_path)
    return json_path, html_path
