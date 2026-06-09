"""Day83 read-only executor readiness gate.

This module performs a deterministic, offline, review-only preflight over the
Day79-Day82 safety evidence chain. It does not execute commands, connect to
devices, or unlock any future executor behavior.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_broker_review_queue import build_broker_review_queue_report
from intent_readonly_execution_broker import build_readonly_execution_broker_report
from intent_readonly_task_contract import build_readonly_task_contract_report
from intent_reviewer_decision_audit_summary import (
    build_reviewer_decision_audit_summary_report,
    validate_reviewer_decision_audit_summary_report,
)


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "readonly-executor-readiness-gate"
TITLE = "Day83 Read-only Executor Readiness Gate / Controlled Runner Preflight"
READINESS_REVIEW_READY = "READINESS_REVIEW_READY"
READINESS_REVIEW_REQUIRED = "READINESS_REVIEW_REQUIRED"
EXECUTION_MODE = "deterministic_offline_review_only_readiness_gate"
REPORT_JSON = Path("reports") / "lab-summary" / "day83_readonly_executor_readiness_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day83_readonly_executor_readiness_gate.html"

REQUIRED_FALSE_FLAGS = (
    "executor_allowed",
    "live_execution_allowed",
    "ssh_allowed",
    "device_access_allowed",
    "ai_runtime_allowed",
    "dashboard_action_allowed",
    "mapped_task_execution_allowed",
    "approval_unlock_allowed",
    "execution_unlock_supported",
)


def _false_gate_flags() -> Dict[str, bool]:
    return {
        "executor_allowed": False,
        "live_execution_allowed": False,
        "ssh_allowed": False,
        "device_access_allowed": False,
        "ai_runtime_allowed": False,
        "dashboard_action_allowed": False,
        "mapped_task_execution_allowed": False,
        "approval_unlock_allowed": False,
        "execution_unlock_supported": False,
    }


def _pass_check(check_id: str, title: str, evidence_refs: List[str]) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "title": title,
        "status": "PASS",
        "evidence_refs": evidence_refs,
    }


def _fail_check(check_id: str, title: str, message: str, evidence_refs: List[str]) -> Dict[str, Any]:
    return {
        "check_id": check_id,
        "title": title,
        "status": "FAIL",
        "message": message,
        "evidence_refs": evidence_refs,
    }


def _has_only_values(records: List[Dict[str, Any]], field: str, expected: Any) -> bool:
    return all(record.get(field) is expected for record in records)


def _has_only_boundary_values(records: List[Dict[str, Any]], field: str, expected: Any) -> bool:
    return all(record.get("safety_boundary", {}).get(field) is expected for record in records)


def _has_only_invariant_values(records: List[Dict[str, Any]], field: str, expected: Any) -> bool:
    return all(record.get("safety_invariants", {}).get(field) is expected for record in records)


def build_readiness_checks(
    day79_report: Dict[str, Any],
    day80_report: Dict[str, Any],
    day81_report: Dict[str, Any],
    day82_report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Build deterministic Day83 readiness validation checks."""
    checks: List[Dict[str, Any]] = []

    allowlist = day79_report.get("allowlist", {})
    if (
        day79_report.get("overall_status") == "PASS"
        and allowlist.get("readonly_candidates")
        and allowlist.get("blocked_write_actions")
        and allowlist.get("destructive_actions")
    ):
        checks.append(
            _pass_check(
                "day79-contract-policy-present",
                "Day79 contract exposes read-only allowlist and blocked action policy.",
                ["Day79", "intent_readonly_task_contract"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day79-contract-policy-present",
                "Day79 contract exposes read-only allowlist and blocked action policy.",
                "Day79 contract policy evidence is missing or incomplete.",
                ["Day79", "intent_readonly_task_contract"],
            )
        )

    broker_records = day80_report.get("broker_records", [])
    if (
        day80_report.get("overall_status") == "PASS"
        and broker_records
        and _has_only_values(broker_records, "allowed_to_execute", False)
        and _has_only_values(broker_records, "ssh_allowed", False)
        and _has_only_values(broker_records, "live_command_allowed", False)
        and _has_only_values(broker_records, "device_connection_allowed", False)
        and _has_only_values(broker_records, "execution_unlock_supported", False)
    ):
        checks.append(
            _pass_check(
                "day80-broker-non-executing",
                "Day80 broker remains non-executing.",
                ["Day80", "intent_readonly_execution_broker"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day80-broker-non-executing",
                "Day80 broker remains non-executing.",
                "Day80 broker evidence contains missing records or an enabled execution flag.",
                ["Day80", "intent_readonly_execution_broker"],
            )
        )

    queue_records = day81_report.get("queue_records", [])
    queue_has_states = all(
        record.get("review_state") and record.get("decision_state") for record in queue_records
    )
    if day81_report.get("overall_status") == "PASS" and queue_records and queue_has_states:
        checks.append(
            _pass_check(
                "day81-queue-review-decision-state",
                "Day81 queue records include review state and decision state.",
                ["Day81", "intent_broker_review_queue"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day81-queue-review-decision-state",
                "Day81 queue records include review state and decision state.",
                "Day81 queue records are missing review_state or decision_state evidence.",
                ["Day81", "intent_broker_review_queue"],
            )
        )

    day82_validation_errors = validate_reviewer_decision_audit_summary_report(day82_report)
    traceability_text = json.dumps(day82_report.get("traceability_map", []), sort_keys=True)
    if (
        day82_report.get("overall_status") == "PASS"
        and not day82_validation_errors
        and all(day in traceability_text for day in ("Day79", "Day80", "Day81", "Day82"))
    ):
        checks.append(
            _pass_check(
                "day82-audit-traceability",
                "Day82 audit evidence is traceable across Day79-Day82.",
                ["Day82", "intent_reviewer_decision_audit_summary"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day82-audit-traceability",
                "Day82 audit evidence is traceable across Day79-Day82.",
                "Day82 audit traceability evidence is missing or invalid.",
                ["Day82", "intent_reviewer_decision_audit_summary"],
            )
        )

    no_queue_live_flags = (
        queue_records
        and _has_only_values(queue_records, "allowed_to_execute", False)
        and _has_only_values(queue_records, "ssh_allowed", False)
        and _has_only_values(queue_records, "live_command_allowed", False)
        and _has_only_values(queue_records, "device_connection_allowed", False)
        and _has_only_values(queue_records, "mapped_task_execution_allowed", False)
        and _has_only_values(queue_records, "dashboard_action_allowed", False)
        and _has_only_boundary_values(queue_records, "allowed_to_execute", False)
        and _has_only_boundary_values(queue_records, "ssh_allowed", False)
        and _has_only_boundary_values(queue_records, "live_command_allowed", False)
    )
    if no_queue_live_flags:
        checks.append(
            _pass_check(
                "day81-no-live-queue-flags",
                "No Day81 queue item has live execution flags enabled.",
                ["Day81 queue_records", "Day81 safety_boundary"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day81-no-live-queue-flags",
                "No Day81 queue item has live execution flags enabled.",
                "One or more Day81 queue records expose a live/device/action flag.",
                ["Day81 queue_records", "Day81 safety_boundary"],
            )
        )

    evidence_exports = day82_report.get("evidence_exports", [])
    no_live_capability = (
        evidence_exports
        and _has_only_values(evidence_exports, "ssh_allowed", False)
        and _has_only_values(evidence_exports, "device_connection_allowed", False)
        and _has_only_values(evidence_exports, "live_command_allowed", False)
        and _has_only_values(evidence_exports, "network_change_allowed", False)
        and _has_only_values(evidence_exports, "ai_runtime_allowed", False)
        and _has_only_values(evidence_exports, "dashboard_action_allowed", False)
        and _has_only_invariant_values(evidence_exports, "ssh_allowed", False)
        and _has_only_invariant_values(evidence_exports, "device_connection_allowed", False)
        and _has_only_invariant_values(evidence_exports, "live_command_allowed", False)
    )
    if no_live_capability:
        checks.append(
            _pass_check(
                "day82-no-ssh-device-live-capability",
                "No SSH, device, live command, AI runtime, network change, or dashboard action capability is enabled.",
                ["Day82 evidence_exports", "Day82 safety_invariants"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "day82-no-ssh-device-live-capability",
                "No SSH, device, live command, AI runtime, network change, or dashboard action capability is enabled.",
                "One or more Day82 evidence exports expose a forbidden capability.",
                ["Day82 evidence_exports", "Day82 safety_invariants"],
            )
        )

    readonly_candidate_records = [
        record
        for record in day79_report.get("contract_records", [])
        if record.get("readonly_eligible") is True and record.get("execution_candidate") is True
    ]
    readonly_candidate_only = (
        bool(readonly_candidate_records)
        and _has_only_values(readonly_candidate_records, "allowed_to_execute", False)
        and _has_only_values(readonly_candidate_records, "dry_run_only", True)
        and _has_only_values(readonly_candidate_records, "execution_unlock_supported", False)
    )
    if readonly_candidate_only:
        checks.append(
            _pass_check(
                "candidate-status-readonly-only",
                "Candidate status is read-only-only and does not unlock execution.",
                ["Day79 contract_records", "Day83 gate flags"],
            )
        )
    else:
        checks.append(
            _fail_check(
                "candidate-status-readonly-only",
                "Candidate status is read-only-only and does not unlock execution.",
                "Read-only candidate records are missing or imply execution permission.",
                ["Day79 contract_records", "Day83 gate flags"],
            )
        )

    return checks


def validate_readonly_executor_readiness_gate_report(report: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for the Day83 readiness gate."""
    errors: List[str] = []
    for field in REQUIRED_FALSE_FLAGS:
        if report.get(field) is not False:
            errors.append(f"{field} must be false.")
        if report.get("safety_invariants", {}).get(field) is not False:
            errors.append(f"safety_invariants {field} must be false.")
    if report.get("readonly_executor_candidate") is not True:
        errors.append("readonly_executor_candidate must be true for review-ready evidence.")
    if report.get("candidate_scope", {}).get("candidate_means_execution_allowed") is not False:
        errors.append("candidate status must not mean execution is allowed.")
    if report.get("candidate_scope", {}).get("future_adapter_design_review_only") is not True:
        errors.append("candidate status must only support future adapter design review.")
    checks = report.get("readiness_checks", [])
    if not checks:
        errors.append("readiness_checks must not be empty.")
    for check in checks:
        if check.get("status") != "PASS":
            errors.append(f"{check.get('check_id', '<missing>')} did not pass.")
    traceability_text = json.dumps(report.get("evidence_chain", []), sort_keys=True)
    for day in ("Day79", "Day80", "Day81", "Day82", "Day83"):
        if day not in traceability_text:
            errors.append(f"evidence_chain must include {day}.")
    if report.get("overall_status") == "PASS" and report.get("readiness_state") != READINESS_REVIEW_READY:
        errors.append("PASS reports must have readiness_state READINESS_REVIEW_READY.")
    if report.get("executor_allowed") is not False and report.get("readonly_executor_candidate") is True:
        errors.append("readonly_executor_candidate must never imply executor_allowed.")
    return errors


def build_readonly_executor_readiness_gate_report() -> Dict[str, Any]:
    """Build the deterministic Day83 readiness gate report."""
    day79_report = build_readonly_task_contract_report()
    day80_report = build_readonly_execution_broker_report()
    day81_report = build_broker_review_queue_report()
    day82_report = build_reviewer_decision_audit_summary_report()
    readiness_checks = build_readiness_checks(day79_report, day80_report, day81_report, day82_report)
    checks_pass = all(check.get("status") == "PASS" for check in readiness_checks)
    gate_flags = _false_gate_flags()
    safety_invariants = {
        **gate_flags,
        "readonly_executor_candidate": True,
        "review_only": True,
        "deterministic": True,
        "offline_only": True,
        "report_only": True,
        "source_reports_required": False,
        "optional_local_reports_missing_break_tests": False,
        "openai_api_used": False,
        "ai_sdk_dependency_used": False,
        "voice_integration_used": False,
        "config_json_read": False,
        "network_configuration_changed": False,
        "routeros_command_path_added": False,
        "external_command_execution_added": False,
        "dashboard_post_route_added": False,
        "html_contains_execution_controls": False,
    }
    report: Dict[str, Any] = {
        "day": "Day83",
        "title": TITLE,
        "task_name": TASK_NAME,
        "execution_mode": EXECUTION_MODE,
        "created_at": CREATED_AT,
        "overall_status": "PASS" if checks_pass else "FAIL",
        "readiness_state": READINESS_REVIEW_READY if checks_pass else READINESS_REVIEW_REQUIRED,
        "readonly_executor_candidate": True,
        **gate_flags,
        "candidate_scope": {
            "candidate_meaning": (
                "The request may be considered for future read-only executor adapter design."
            ),
            "candidate_does_not_mean": (
                "The request may run, connect to devices, open SSH, call an AI runtime, "
                "execute mapped tasks, use dashboard actions, or unlock approval/execution."
            ),
            "candidate_means_execution_allowed": False,
            "future_adapter_design_review_only": True,
        },
        "summary": {
            "readiness_check_count": len(readiness_checks),
            "readiness_checks_passed": sum(1 for check in readiness_checks if check.get("status") == "PASS"),
            "source_days": ["Day79", "Day80", "Day81", "Day82"],
            "day79_contract_records": day79_report.get("summary", {}).get("contract_record_count"),
            "day80_broker_records": day80_report.get("summary", {}).get("broker_record_count"),
            "day81_queue_records": day81_report.get("summary", {}).get("queue_record_count"),
            "day82_evidence_exports": day82_report.get("decision_summary", {}).get("evidence_export_count"),
            "executor_allowed_values": [False],
            "readonly_executor_candidate_values": [True],
            "live_execution_allowed_values": [False],
            "ssh_allowed_values": [False],
            "device_access_allowed_values": [False],
            "ai_runtime_allowed_values": [False],
            "dashboard_action_allowed_values": [False],
            "mapped_task_execution_allowed_values": [False],
            "approval_unlock_allowed_values": [False],
            "execution_unlock_supported_values": [False],
        },
        "readiness_checks": readiness_checks,
        "evidence_chain": [
            "Day79 Read-only Task Contract: allowlist, blocked writes, destructive actions, manual classification.",
            "Day80 Read-only Execution Broker Skeleton: non-executing broker records and mock request data only.",
            "Day81 Broker Review Queue & Decision State Report: review_state and decision_state evidence.",
            "Day82 Reviewer Decision Audit Summary / Queue Evidence Export: traceable audit exports.",
            "Day83 Read-only Executor Readiness Gate: candidate-readiness decision only.",
        ],
        "source_evidence": {
            "day79": {
                "overall_status": day79_report.get("overall_status"),
                "reviewer_status": day79_report.get("reviewer_status"),
                "allowlist_keys": sorted(day79_report.get("allowlist", {}).keys()),
            },
            "day80": {
                "overall_status": day80_report.get("overall_status"),
                "reviewer_status": day80_report.get("reviewer_status"),
                "broker_statuses": day80_report.get("summary", {}).get("broker_statuses", []),
            },
            "day81": {
                "overall_status": day81_report.get("overall_status"),
                "reviewer_status": day81_report.get("reviewer_status"),
                "review_states": day81_report.get("summary", {}).get("review_states", []),
                "decision_states": day81_report.get("summary", {}).get("decision_states", []),
            },
            "day82": {
                "overall_status": day82_report.get("overall_status"),
                "status": day82_report.get("status"),
                "traceability_days": [
                    item.get("day") for item in day82_report.get("traceability_map", [])
                ],
            },
        },
        "safety_invariants": safety_invariants,
        "report_file_policy": {
            "uses_in_memory_day79_day82_builders": True,
            "requires_existing_local_day79_day82_report_files": False,
            "missing_optional_local_reports_break_day83": False,
            "day83_reports_required": [REPORT_JSON.as_posix(), REPORT_HTML.as_posix()],
        },
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "final_safety_statement": (
            "Day83 marks the evidence chain as ready for future read-only executor "
            "adapter design review only. It is not an executor and cannot execute, "
            "connect, unlock, approve, or trigger any live behavior."
        ),
    }
    validation_errors = validate_readonly_executor_readiness_gate_report(report)
    report["validation_errors"] = validation_errors
    if validation_errors:
        report["overall_status"] = "FAIL"
        report["readiness_state"] = READINESS_REVIEW_REQUIRED
    return report


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _bool_text(value: Any) -> str:
    return json.dumps(value)


def _check_rows(checks: List[Dict[str, Any]]) -> str:
    rows = []
    for check in checks:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(check['check_id']))}</td>"
            f"<td>{html.escape(str(check['title']))}</td>"
            f"<td>{html.escape(str(check['status']))}</td>"
            f"<td>{html.escape(', '.join(str(item) for item in check.get('evidence_refs', [])))}</td>"
            "</tr>"
        )
    return "".join(rows)


def write_readonly_executor_readiness_gate_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static reviewer-facing HTML report."""
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
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['readiness_state'])}</p>
  <p><strong>Safety:</strong> offline, deterministic, review-only readiness gate. It is not an executor.</p>
  <h2>Gate Decision</h2>
  <table>
    <tbody>
      <tr><th>Executor allowed</th><td>{_bool_text(report['executor_allowed'])}</td></tr>
      <tr><th>Read-only executor candidate</th><td>{_bool_text(report['readonly_executor_candidate'])}</td></tr>
      <tr><th>Live execution allowed</th><td>{_bool_text(report['live_execution_allowed'])}</td></tr>
      <tr><th>SSH allowed</th><td>{_bool_text(report['ssh_allowed'])}</td></tr>
      <tr><th>Device access allowed</th><td>{_bool_text(report['device_access_allowed'])}</td></tr>
      <tr><th>AI runtime allowed</th><td>{_bool_text(report['ai_runtime_allowed'])}</td></tr>
      <tr><th>Dashboard action allowed</th><td>{_bool_text(report['dashboard_action_allowed'])}</td></tr>
      <tr><th>Mapped task execution allowed</th><td>{_bool_text(report['mapped_task_execution_allowed'])}</td></tr>
      <tr><th>Approval unlock allowed</th><td>{_bool_text(report['approval_unlock_allowed'])}</td></tr>
      <tr><th>Execution unlock supported</th><td>{_bool_text(report['execution_unlock_supported'])}</td></tr>
    </tbody>
  </table>
  <h2>Readiness Checks</h2>
  <table>
    <thead><tr><th>Check ID</th><th>Title</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_check_rows(report['readiness_checks'])}</tbody>
  </table>
  <h2>Candidate Scope</h2>
  <p>{html.escape(report['candidate_scope']['candidate_meaning'])}</p>
  <p>{html.escape(report['candidate_scope']['candidate_does_not_mean'])}</p>
  <h2>Evidence Chain</h2>
  <ul>{_html_list(report['evidence_chain'])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_readonly_executor_readiness_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day83 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_readonly_executor_readiness_gate_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_readonly_executor_readiness_gate_html(safe_report, html_path)
    return json_path, html_path
