"""Day85 mock adapter fixture and evidence binding report.

This module creates deterministic mock adapter records that conform to the
Day84 read-only executor adapter contract. It is fixture-only: no SSH, device
access, live command execution, AI API, approval unlock, or execution unlock is
introduced.
"""

from copy import deepcopy
import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from intent_readonly_executor_adapter_contract import (
    CONTRACT_VERSION as DAY84_CONTRACT_VERSION,
    validate_adapter_request_shape,
    validate_adapter_response_shape,
)


CREATED_AT = "2026-06-09T00:00:00Z"
TASK_NAME = "mock-adapter-evidence-binding"
TITLE = "Day85 Mock Adapter + Evidence Binding"
ADAPTER_FIXTURE_ID = "day85.mock_adapter_fixture.v1"
CONTRACT_REFERENCE = "Day84 Read-only Executor Adapter Interface Contract"
REPORT_JSON = Path("reports") / "lab-summary" / "day85_mock_adapter_evidence_binding.json"
REPORT_HTML = Path("reports") / "lab-summary" / "day85_mock_adapter_evidence_binding.html"

COMPATIBLE_ADAPTER_TYPES = {
    "mock adapter",
    "replay adapter",
    "evidence-only adapter",
}

BLOCKED_ADAPTER_TYPES = {
    "ssh adapter",
    "live command adapter",
    "AI executor adapter",
    "approval unlock adapter",
}

REQUIRED_ADAPTER_RECORD_FIELDS = (
    "adapter_id",
    "adapter_type",
    "request_id",
    "contract_id",
    "contract_reference",
    "evidence_reference",
    "compatible_with_day84_contract",
    "allowed_to_execute",
    "ssh_allowed",
    "device_access_allowed",
    "live_command_allowed",
    "approval_unlock_supported",
    "execution_unlock_supported",
    "decision",
    "decision_reason",
    "traceability",
)


def adapter_safety_flags() -> Dict[str, bool]:
    """Return the locked Day85 mock-adapter safety flags."""
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
        "real_executor_present": False,
        "runnable_entrypoint_present": False,
        "runtime_transport_present": False,
        "subprocess_allowed": False,
        "config_json_required": False,
        "network_change_allowed": False,
        "mapped_task_execution_allowed": False,
        "dashboard_action_allowed": False,
    }


def _decision_for_adapter(adapter_type: str) -> Tuple[bool, str, str]:
    if adapter_type in COMPATIBLE_ADAPTER_TYPES:
        return (
            True,
            "COMPATIBLE_REVIEW_ONLY",
            "Adapter type matches the Day84 read-only contract fixture and remains non-executing.",
        )
    return (
        False,
        "BLOCKED",
        "Adapter type implies execution, unlock, SSH, live command, or AI executor capability.",
    )


def build_mock_adapter_request(request_id: str = "day85-mock-request-001") -> Dict[str, Any]:
    """Build a deterministic request that conforms to the Day84 request shape."""
    flags = adapter_safety_flags()
    return {
        "request_id": request_id,
        "contract_version": DAY84_CONTRACT_VERSION,
        "requested_task": "show_interface_status",
        "request_source": "Day85 deterministic mock adapter fixture",
        "target_scope": {
            "scope_type": "mock_fixture_target_reference_only",
            "target_ref": "day85_mock_lab_device_group",
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
                "device_group_ref": "day85_mock_lab_device_group",
                "include_admin_state": True,
            },
            "command_text": None,
            "raw_device_command": None,
        },
        "safety_flags": flags,
        "evidence_refs": [
            CONTRACT_REFERENCE,
            "docs/ai/intent_readonly_executor_adapter_contract.md",
            "docs/ai/intent_mock_adapter_evidence_binding.md",
            "Day85 deterministic adapter fixture request",
        ],
    }


def build_mock_adapter_response(
    adapter_id: str,
    adapter_type: str,
    request_id: str,
    evidence_reference: str,
) -> Dict[str, Any]:
    """Build a deterministic response that conforms to the Day84 response shape."""
    compatible, decision, decision_reason = _decision_for_adapter(adapter_type)
    mock_records = []
    if compatible:
        mock_records = [
            {
                "device_ref": "mock-lab-device-01",
                "interface_ref": "ether1",
                "observed_state": "up",
                "source": "deterministic_fixture",
            },
            {
                "device_ref": "mock-lab-device-01",
                "interface_ref": "ether2",
                "observed_state": "administratively_down",
                "source": "deterministic_fixture",
            },
        ]

    return {
        "response_id": f"{adapter_id}-response-001",
        "request_id": request_id,
        "contract_version": DAY84_CONTRACT_VERSION,
        "response_status": decision,
        "output_contract": {
            "output_kind": "structured_readonly_snapshot_fixture",
            "records_schema": [
                {"field": "device_ref", "type": "string"},
                {"field": "interface_ref", "type": "string"},
                {"field": "observed_state", "type": "string"},
            ],
            "example_records": mock_records,
            "fixture_only": True,
            "adapter_type": adapter_type,
            "evidence_reference": evidence_reference,
            "decision_reason": decision_reason,
        },
        "execution_result": None,
        "commands_executed": [],
        "device_session": None,
        "safety_flags": adapter_safety_flags(),
        "evidence_refs": [
            CONTRACT_REFERENCE,
            evidence_reference,
            "Day85 response is bound to request, adapter, contract, and evidence.",
        ],
    }


def build_adapter_record(adapter_type: str, index: int) -> Dict[str, Any]:
    """Build a reviewer-facing adapter record with evidence binding."""
    adapter_slug = adapter_type.lower().replace(" ", "-")
    adapter_id = f"day85-{adapter_slug}"
    request_id = f"day85-request-{index:03d}"
    evidence_reference = f"day85-evidence-{index:03d}-{adapter_slug}"
    compatible, decision, decision_reason = _decision_for_adapter(adapter_type)
    response = build_mock_adapter_response(
        adapter_id=adapter_id,
        adapter_type=adapter_type,
        request_id=request_id,
        evidence_reference=evidence_reference,
    )
    return {
        "adapter_id": adapter_id,
        "adapter_type": adapter_type,
        "request_id": request_id,
        "contract_id": DAY84_CONTRACT_VERSION,
        "contract_reference": CONTRACT_REFERENCE,
        "evidence_reference": evidence_reference,
        "compatible_with_day84_contract": compatible,
        "allowed_to_execute": False,
        "ssh_allowed": False,
        "device_access_allowed": False,
        "live_command_allowed": False,
        "approval_unlock_supported": False,
        "execution_unlock_supported": False,
        "decision": decision,
        "decision_reason": decision_reason,
        "mock_response": response,
        "traceability": {
            "original_request": request_id,
            "day84_contract": DAY84_CONTRACT_VERSION,
            "adapter_fixture": ADAPTER_FIXTURE_ID,
            "adapter_id": adapter_id,
            "evidence_reference": evidence_reference,
            "reviewer_decision": decision,
            "response_id": response["response_id"],
        },
    }


def build_adapter_records() -> List[Dict[str, Any]]:
    """Build deterministic compatible and blocked adapter records."""
    adapter_types = [
        "mock adapter",
        "replay adapter",
        "evidence-only adapter",
        "ssh adapter",
        "live command adapter",
        "AI executor adapter",
        "approval unlock adapter",
    ]
    return [build_adapter_record(adapter_type, index + 1) for index, adapter_type in enumerate(adapter_types)]


def build_compatibility_matrix(records: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Build the internal Day85/Day86 validation matrix for adapter outcomes."""
    source_records = records if records is not None else build_adapter_records()
    return [
        {
            "adapter_type": record["adapter_type"],
            "expected_result": "compatible"
            if record["adapter_type"] in COMPATIBLE_ADAPTER_TYPES
            else "blocked",
            "validation_scope": "internal_day85_day86_validation",
            "standalone_topic": False,
            "compatible_with_day84_contract": record["compatible_with_day84_contract"],
            "allowed_to_execute": record["allowed_to_execute"],
            "ssh_allowed": record["ssh_allowed"],
            "live_command_allowed": record["live_command_allowed"],
            "approval_unlock_supported": record["approval_unlock_supported"],
            "execution_unlock_supported": record["execution_unlock_supported"],
            "reviewer_decision": record["decision"],
            "evidence_reference": record["evidence_reference"],
        }
        for record in source_records
    ]


def validate_adapter_record(record: Dict[str, Any]) -> List[str]:
    """Return reviewer-visible validation errors for one Day85 adapter record."""
    errors: List[str] = []
    for field in REQUIRED_ADAPTER_RECORD_FIELDS:
        if field not in record:
            errors.append(f"adapter record missing required field: {field}.")

    adapter_type = str(record.get("adapter_type", ""))
    expected_compatible = adapter_type in COMPATIBLE_ADAPTER_TYPES
    if record.get("compatible_with_day84_contract") is not expected_compatible:
        errors.append(f"{adapter_type} compatibility result is incorrect.")

    response = record.get("mock_response", {})
    request = build_mock_adapter_request(str(record.get("request_id", "")))
    errors.extend(validate_adapter_request_shape(request))
    errors.extend(validate_adapter_response_shape(response))

    false_fields = (
        "allowed_to_execute",
        "ssh_allowed",
        "device_access_allowed",
        "live_command_allowed",
        "approval_unlock_supported",
        "execution_unlock_supported",
    )
    for field in false_fields:
        if record.get(field) is not False:
            errors.append(f"{adapter_type} {field} must be false.")
        if response.get("safety_flags", {}).get(field) is not False:
            errors.append(f"{adapter_type} response safety_flags {field} must be false.")

    if adapter_type in BLOCKED_ADAPTER_TYPES and record.get("decision") not in {"BLOCKED", "REJECTED"}:
        errors.append(f"{adapter_type} reviewer decision must be blocked or rejected.")
    if adapter_type in COMPATIBLE_ADAPTER_TYPES and record.get("decision") != "COMPATIBLE_REVIEW_ONLY":
        errors.append(f"{adapter_type} reviewer decision must be compatible review-only.")

    traceability = record.get("traceability", {})
    expected_trace_fields = {
        "original_request": record.get("request_id"),
        "day84_contract": DAY84_CONTRACT_VERSION,
        "adapter_fixture": ADAPTER_FIXTURE_ID,
        "adapter_id": record.get("adapter_id"),
        "evidence_reference": record.get("evidence_reference"),
        "response_id": response.get("response_id"),
    }
    for field, expected_value in expected_trace_fields.items():
        if traceability.get(field) != expected_value:
            errors.append(f"{adapter_type} traceability {field} is not bound correctly.")

    evidence_refs_text = json.dumps(response.get("evidence_refs", []), sort_keys=True)
    if str(record.get("evidence_reference", "")) not in evidence_refs_text:
        errors.append(f"{adapter_type} response is missing evidence reference.")
    if str(record.get("request_id", "")) != response.get("request_id"):
        errors.append(f"{adapter_type} response request_id does not match adapter record.")
    if response.get("contract_version") != DAY84_CONTRACT_VERSION:
        errors.append(f"{adapter_type} response contract_version does not match Day84 contract.")
    return errors


def validate_adapter_records(records: List[Dict[str, Any]]) -> List[str]:
    """Return reviewer-visible validation errors for all adapter records."""
    errors: List[str] = []
    for record in records:
        errors.extend(validate_adapter_record(record))
    return errors


def build_mock_adapter_evidence_binding_report() -> Dict[str, Any]:
    """Build the Day85 mock adapter evidence binding report."""
    adapter_records = build_adapter_records()
    validation_errors = validate_adapter_records(adapter_records)
    compatibility_matrix = build_compatibility_matrix(adapter_records)
    overall_status = "PASS" if not validation_errors else "FAIL"
    blocked_records = [
        record for record in adapter_records if record["adapter_type"] in BLOCKED_ADAPTER_TYPES
    ]
    flags = adapter_safety_flags()
    evidence_bindings = [
        {
            "request_id": record["request_id"],
            "adapter_id": record["adapter_id"],
            "contract_reference": record["contract_reference"],
            "evidence_reference": record["evidence_reference"],
            "safety_decision": record["decision"],
            "response_id": record["mock_response"]["response_id"],
            "traceability_complete": validate_adapter_record(record) == [],
        }
        for record in adapter_records
    ]
    blocked_adapter_checks = [
        {
            "adapter_type": record["adapter_type"],
            "allowed_to_execute": record["allowed_to_execute"],
            "ssh_allowed": record["ssh_allowed"],
            "live_command_allowed": record["live_command_allowed"],
            "approval_unlock_supported": record["approval_unlock_supported"],
            "execution_unlock_supported": record["execution_unlock_supported"],
            "reviewer_decision": record["decision"],
            "evidence_trail_generated": bool(record["evidence_reference"]),
        }
        for record in blocked_records
    ]
    return {
        "day": "Day85",
        "title": TITLE,
        "task_name": TASK_NAME,
        "created_at": CREATED_AT,
        "overall_status": overall_status,
        "review_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "scope": [
            "deterministic mock adapter fixture",
            "Day84 interface contract conformance",
            "evidence binding for every adapter response",
            "reviewer-facing JSON and HTML reports",
            "Compatibility Matrix as internal validation only",
        ],
        "non_goals": [
            "SSH",
            "device access",
            "live command execution",
            "real executor implementation",
            "AI API or OpenAI SDK usage",
            "approval unlock",
            "execution unlock",
            "dashboard execution control",
            "mapped task execution",
        ],
        "contract_reference": {
            "contract_id": DAY84_CONTRACT_VERSION,
            "title": CONTRACT_REFERENCE,
            "doc_path": "docs/ai/intent_readonly_executor_adapter_contract.md",
            "roadmap_path": "docs/roadmap/day84_readonly_executor_adapter_interface_contract.md",
        },
        "adapter_fixture": {
            "adapter_fixture_id": ADAPTER_FIXTURE_ID,
            "fixture_only": True,
            "deterministic": True,
            "mock_only": True,
            "implements_real_executor": False,
        },
        "adapter_records": adapter_records,
        "compatibility_matrix": compatibility_matrix,
        "evidence_bindings": evidence_bindings,
        "blocked_adapter_checks": blocked_adapter_checks,
        "safety_invariants": {
            **flags,
            "mock_only": True,
            "review_only": True,
            "report_only": True,
            "deterministic": True,
            "offline_only": True,
            "compatibility_matrix_is_internal_validation": True,
            "compatibility_matrix_is_standalone_topic": False,
            "json_report_written": True,
            "html_report_written": True,
            "html_contains_execution_controls": False,
            "post_endpoint_added": False,
        },
        "traceability_summary": {
            "adapter_record_count": len(adapter_records),
            "evidence_binding_count": len(evidence_bindings),
            "compatible_adapter_count": len(
                [record for record in adapter_records if record["compatible_with_day84_contract"]]
            ),
            "blocked_adapter_count": len(blocked_records),
            "all_responses_bound_to_request": all(
                record["mock_response"]["request_id"] == record["request_id"]
                for record in adapter_records
            ),
            "all_responses_bound_to_day84_contract": all(
                record["mock_response"]["contract_version"] == DAY84_CONTRACT_VERSION
                for record in adapter_records
            ),
            "all_responses_bound_to_evidence": all(
                record["evidence_reference"] in json.dumps(record["mock_response"]["evidence_refs"])
                for record in adapter_records
            ),
            "all_blocked_adapters_generate_evidence": all(
                bool(record["evidence_reference"]) for record in blocked_records
            ),
            "validation_errors": validation_errors,
        },
        "final_recommendation": "REVIEW_ONLY",
        "reports": {
            "json": REPORT_JSON.as_posix(),
            "html": REPORT_HTML.as_posix(),
        },
        "validation_errors": validation_errors,
        "final_safety_statement": (
            "Day85 remains Mock Adapter + Evidence Binding. The Compatibility "
            "Matrix is included only as internal validation data and report "
            "evidence; it is not promoted to an independent topic."
        ),
    }


def _html_list(items: List[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _adapter_rows(records: List[Dict[str, Any]]) -> str:
    rows = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td>{html.escape(record['adapter_type'])}</td>"
            f"<td>{html.escape(str(record['compatible_with_day84_contract']))}</td>"
            f"<td>{html.escape(str(record['allowed_to_execute']))}</td>"
            f"<td>{html.escape(record['decision'])}</td>"
            f"<td><code>{html.escape(record['evidence_reference'])}</code></td>"
            "</tr>"
        )
    return "".join(rows)


def _matrix_rows(rows: List[Dict[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(row['adapter_type'])}</td>"
        f"<td>{html.escape(row['expected_result'])}</td>"
        f"<td>{html.escape(str(row['allowed_to_execute']))}</td>"
        f"<td>{html.escape(str(row['ssh_allowed']))}</td>"
        f"<td>{html.escape(str(row['live_command_allowed']))}</td>"
        f"<td>{html.escape(row['reviewer_decision'])}</td>"
        "</tr>"
        for row in rows
    )


def write_mock_adapter_evidence_binding_html(report: Dict[str, Any], output_path: Path) -> None:
    """Write a deterministic static reviewer-facing HTML report."""
    summary = report["traceability_summary"]
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
  <p><strong>Result:</strong> {html.escape(report['overall_status'])} / {html.escape(report['review_status'])}</p>
  <p><strong>Final recommendation:</strong> {html.escape(report['final_recommendation'])}</p>
  <p><strong>Safety:</strong> mock-only, evidence-bound, read-only, report-only, and non-executing.</p>
  <h2>Traceability Summary</h2>
  <table>
    <tbody>
      <tr><th>Adapter records</th><td>{summary['adapter_record_count']}</td></tr>
      <tr><th>Evidence bindings</th><td>{summary['evidence_binding_count']}</td></tr>
      <tr><th>Compatible adapters</th><td>{summary['compatible_adapter_count']}</td></tr>
      <tr><th>Blocked adapters</th><td>{summary['blocked_adapter_count']}</td></tr>
      <tr><th>Responses bound to request</th><td>{html.escape(str(summary['all_responses_bound_to_request']))}</td></tr>
      <tr><th>Responses bound to Day84 contract</th><td>{html.escape(str(summary['all_responses_bound_to_day84_contract']))}</td></tr>
      <tr><th>Responses bound to evidence</th><td>{html.escape(str(summary['all_responses_bound_to_evidence']))}</td></tr>
    </tbody>
  </table>
  <h2>Adapter Records</h2>
  <table>
    <thead><tr><th>Adapter type</th><th>Day84 compatible</th><th>Allowed to execute</th><th>Decision</th><th>Evidence</th></tr></thead>
    <tbody>{_adapter_rows(report['adapter_records'])}</tbody>
  </table>
  <h2>Compatibility Matrix Internal Validation</h2>
  <p>This matrix is validation evidence inside Day85/Day86 scope only. It is not a standalone Day85 topic.</p>
  <table>
    <thead><tr><th>Adapter type</th><th>Expected result</th><th>Allowed to execute</th><th>SSH allowed</th><th>Live command allowed</th><th>Reviewer decision</th></tr></thead>
    <tbody>{_matrix_rows(report['compatibility_matrix'])}</tbody>
  </table>
  <h2>Non Goals</h2>
  <ul>{_html_list(report['non_goals'])}</ul>
  <h2>Final Safety Statement</h2>
  <p>{html.escape(report['final_safety_statement'])}</p>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_mock_adapter_evidence_binding_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    """Write Day85 JSON and HTML reports and return their paths."""
    safe_report = deepcopy(report) if report is not None else build_mock_adapter_evidence_binding_report()
    json_path = Path(project_root) / REPORT_JSON
    html_path = Path(project_root) / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(safe_report, indent=2), encoding="utf-8")
    write_mock_adapter_evidence_binding_html(safe_report, html_path)
    return json_path, html_path
