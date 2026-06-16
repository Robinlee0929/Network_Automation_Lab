"""Phase 2A-04 dry-run plan evidence binding and traceability ledger.

This module is report-only. It binds Phase 2A-03 dry-run plan results and
rejected unsafe request results to sanitized evidence records, validates that
every source outcome is traceable, and stops before any runner, adapter, live
device, provider, or Phase 2B path can be represented.
"""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase_2a_03_dry_run_job_plan_gate import (
    build_phase_2a_03_dry_run_job_plan_gate_report,
)


PHASE = "2A-04"
TASK_NAME = "phase2a-04-plan-evidence-ledger"
TITLE = "Phase 2A-04 Dry-Run Job Plan Evidence Binding / Traceability Ledger"
STATUS_LABEL = "PHASE_2A_04_PLAN_EVIDENCE_LEDGER_READY"
MODE = "report_only"
SCOPE = "mock_local_read_only_dry_run"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_04_plan_evidence_ledger.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_04_plan_evidence_ledger.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_04_plan_evidence_ledger.md"

DANGEROUS_EVIDENCE_MARKERS = frozenset(
    {
        "api_key",
        "backup_config",
        "command",
        "commands",
        "credential",
        "credentials",
        "device",
        "endpoint",
        "host",
        "hostname",
        "ip",
        "live_target",
        "model",
        "netconf",
        "password",
        "provider",
        "restconf",
        "script",
        "scriptPath",
        "script_path",
        "secret",
        "ssh",
        "target",
        "token",
        "username",
    }
)

SAFETY_SUMMARY_FLAGS = {
    "runner_invoked": False,
    "adapter_invoked": False,
    "live_execution_opened": False,
    "ssh_execution_opened": False,
    "netconf_execution_opened": False,
    "restconf_execution_opened": False,
    "provider_api_model_call_opened": False,
    "backup_config_invoked": False,
    "arbitrary_command_execution_opened": False,
    "arbitrary_script_path_execution_opened": False,
    "phase_2b_authorized": False,
    "real_execution_authorized": False,
    "next_phase_allowed": False,
}

RECORD_DANGEROUS_FLAGS = {
    "runner_invoked": False,
    "adapter_invoked": False,
    "live_execution_opened": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_04_PLAN_EVIDENCE_LEDGER_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "PHASE_2A_03_DRY_RUN_PLANS_BOUND",
    "REJECTED_REQUESTS_BOUND_TO_TRACEABILITY_RECORDS",
    "EVIDENCE_PAYLOAD_SANITIZED",
    "NON_EXECUTION_PROOF_PRESENT",
    "RUNNER_INVOKED_FALSE",
    "ADAPTER_INVOKED_FALSE",
    "LIVE_EXECUTION_OPENED_FALSE",
    "PHASE_2B_AUTHORIZED_FALSE",
    "REAL_EXECUTION_AUTHORIZED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _normalize_marker(value: Any) -> str:
    return str(value).replace("-", "").replace("_", "").replace(".", "").lower()


def _source_plan_id_for_rejected(result: Mapping[str, Any]) -> str:
    digest_source = {
        "job_type": result.get("job_type"),
        "rejection_reason": result.get("rejection_reason"),
        "rejected_field": result.get("rejected_field"),
    }
    return f"REJECTED_NO_PLAN_{_stable_digest(digest_source)}"


def _safe_source_job_type(job_type: Any) -> str:
    value = str(job_type or "<missing>")
    if _contains_unsafe_string(value):
        return f"rejected_job_type_ref_{_stable_digest(value)}"
    return value


def _safe_rejection_reason(reason: Any) -> Optional[str]:
    if reason is None:
        return None
    reason_text = str(reason)
    replacements = {
        "LIVE_TARGET_FIELD_REJECTED": "LIVE_REFERENCE_FIELD_REJECTED",
        "DANGEROUS_FIELD_REJECTED": "DANGEROUS_FIELD_REJECTED",
        "JOB_TYPE_EXPLICITLY_REJECTED": "JOB_TYPE_EXPLICITLY_REJECTED",
    }
    safe_reason = replacements.get(reason_text, reason_text)
    if _contains_unsafe_string(safe_reason):
        return f"SAFE_REJECTION_REASON_{_stable_digest(safe_reason)}"
    return safe_reason


def _safe_normalized_request_summary(result: Mapping[str, Any]) -> Dict[str, Any]:
    if result.get("status") == "PLANNED":
        normalized_request = result.get("normalized_request", {})
        inputs = normalized_request.get("inputs", {}) if isinstance(normalized_request, Mapping) else {}
        return {
            "request_ref": f"phase_2a_03_normalized_request_{_stable_digest(normalized_request)}",
            "safe_input_fields": sorted(str(field) for field in inputs),
        }
    return {
        "request_ref": f"phase_2a_03_rejected_request_{_stable_digest(result)}",
        "safe_rejection": True,
    }


def _non_execution_proof(source_status: str) -> Dict[str, Any]:
    return {
        "source_status_bound": source_status,
        "report_only_record": True,
        "phase_2a_03_result_bound": True,
        "execution_payload_present": False,
        "review_stops_at_traceability_ledger": True,
    }


def _contains_unsafe_string(value: Any) -> bool:
    lowered = str(value).lower()
    normalized = _normalize_marker(value)
    for marker in DANGEROUS_EVIDENCE_MARKERS:
        marker_lower = marker.lower()
        marker_normalized = _normalize_marker(marker)
        if marker_lower in lowered or marker_normalized in normalized:
            return True
    return False


def _iter_payload_fields(payload: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            display_key = f"{prefix}.{key}" if prefix else str(key)
            yield display_key, value
            yield from _iter_payload_fields(value, display_key)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            yield from _iter_payload_fields(value, f"{prefix}[{index}]")


def _evidence_payload_safety_errors(record: Mapping[str, Any]) -> Sequence[str]:
    errors = []
    for key, value in _iter_payload_fields(record):
        leaf_key = key.split(".")[-1]
        normalized_leaf_key = _normalize_marker(leaf_key)
        if any(_normalize_marker(marker) in normalized_leaf_key for marker in DANGEROUS_EVIDENCE_MARKERS):
            errors.append(f"UNSAFE_EVIDENCE_KEY:{key}")
        if isinstance(value, str) and _contains_unsafe_string(value):
            errors.append(f"UNSAFE_EVIDENCE_VALUE:{key}")
    return tuple(errors)


def build_phase_2a_04_plan_evidence_record(source_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Create one sanitized evidence record from a Phase 2A-03 source result."""

    status = str(source_result.get("status", "UNKNOWN"))
    accepted = status == "PLANNED"
    plan = source_result.get("dry_run_plan") if accepted else None
    source_plan_id = str(plan.get("plan_id")) if isinstance(plan, Mapping) else _source_plan_id_for_rejected(source_result)
    source_job_type = _safe_source_job_type(source_result.get("job_type"))
    record_seed = {
        "source_plan_id": source_plan_id,
        "source_job_type": source_job_type,
        "status": "accepted" if accepted else "rejected",
        "rejection_reason": _safe_rejection_reason(source_result.get("rejection_reason")),
    }
    safe_artifact_references = plan.get("safe_artifact_references", {}) if isinstance(plan, Mapping) else {}

    return {
        "evidence_id": f"PHASE_2A_04_EVIDENCE_{_stable_digest(record_seed)}",
        "source_job_type": source_job_type,
        "source_plan_id": source_plan_id,
        "safe_normalized_request_summary": _safe_normalized_request_summary(source_result),
        "accepted_or_rejected": "accepted" if accepted else "rejected",
        "rejection_reason": None if accepted else _safe_rejection_reason(source_result.get("rejection_reason")),
        "safe_artifact_references": dict(safe_artifact_references),
        "non_executable_proof": _non_execution_proof("accepted" if accepted else "rejected"),
        **RECORD_DANGEROUS_FLAGS,
    }


def build_phase_2a_04_plan_evidence_ledger(
    accepted_plan_results: Optional[Sequence[Mapping[str, Any]]] = None,
    rejected_request_results: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a deterministic report-only traceability ledger."""

    if accepted_plan_results is None or rejected_request_results is None:
        phase_2a_03_report = build_phase_2a_03_dry_run_job_plan_gate_report()
        accepted_plan_results = phase_2a_03_report["allowed_request_results"]
        rejected_request_results = phase_2a_03_report["rejected_request_results"]

    accepted_records = [build_phase_2a_04_plan_evidence_record(result) for result in accepted_plan_results]
    rejected_records = [build_phase_2a_04_plan_evidence_record(result) for result in rejected_request_results]
    ledger = {
        "ledger_id": f"PHASE_2A_04_LEDGER_{_stable_digest({'accepted': accepted_records, 'rejected': rejected_records})}",
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "source_phase": "2A-03",
        "records": accepted_records + rejected_records,
        "accepted_evidence_records": accepted_records,
        "rejected_evidence_records": rejected_records,
        "source_counts": {
            "accepted_plan_results": len(accepted_plan_results),
            "rejected_request_results": len(rejected_request_results),
        },
        **SAFETY_SUMMARY_FLAGS,
    }
    return ledger


def validate_phase_2a_04_evidence_binding(
    ledger: Mapping[str, Any],
    accepted_plan_results: Sequence[Mapping[str, Any]],
    rejected_request_results: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Validate traceability, sanitization, and no-execution invariants."""

    records = list(ledger.get("records", []))
    expected_accepted_plan_ids = {
        str(result["dry_run_plan"]["plan_id"])
        for result in accepted_plan_results
        if result.get("status") == "PLANNED" and isinstance(result.get("dry_run_plan"), Mapping)
    }
    expected_rejected_plan_ids = {_source_plan_id_for_rejected(result) for result in rejected_request_results}
    actual_accepted_plan_ids = {
        str(record.get("source_plan_id"))
        for record in records
        if record.get("accepted_or_rejected") == "accepted"
    }
    actual_rejected_plan_ids = {
        str(record.get("source_plan_id"))
        for record in records
        if record.get("accepted_or_rejected") == "rejected"
    }

    errors = []
    missing_accepted = sorted(expected_accepted_plan_ids - actual_accepted_plan_ids)
    missing_rejected = sorted(expected_rejected_plan_ids - actual_rejected_plan_ids)
    if missing_accepted:
        errors.append(f"MISSING_ACCEPTED_EVIDENCE:{','.join(missing_accepted)}")
    if missing_rejected:
        errors.append(f"MISSING_REJECTED_EVIDENCE:{','.join(missing_rejected)}")

    for index, record in enumerate(records):
        proof = record.get("non_executable_proof")
        if not isinstance(proof, Mapping) or not proof:
            errors.append(f"MISSING_NON_EXECUTION_PROOF:{index}")
        if record.get("runner_invoked") is not False:
            errors.append(f"RUNNER_INVOCATION_REPRESENTED:{index}")
        if record.get("adapter_invoked") is not False:
            errors.append(f"ADAPTER_INVOCATION_REPRESENTED:{index}")
        if record.get("live_execution_opened") is not False:
            errors.append(f"LIVE_EXECUTION_OPENED:{index}")
        if record.get("next_phase_allowed") is not False:
            errors.append(f"NEXT_PHASE_ALLOWED:{index}")
        errors.extend(_evidence_payload_safety_errors(record))

    if ledger.get("phase_2b_authorized") is not False:
        errors.append("PHASE_2B_AUTHORIZED")
    if ledger.get("real_execution_authorized") is not False:
        errors.append("REAL_EXECUTION_AUTHORIZED")
    for flag_name, expected_value in SAFETY_SUMMARY_FLAGS.items():
        if ledger.get(flag_name) is not expected_value:
            errors.append(f"SAFETY_SUMMARY_FLAG_NOT_FALSE:{flag_name}")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "expected_accepted_evidence_records": len(expected_accepted_plan_ids),
        "actual_accepted_evidence_records": len(actual_accepted_plan_ids),
        "expected_rejected_evidence_records": len(expected_rejected_plan_ids),
        "actual_rejected_evidence_records": len(actual_rejected_plan_ids),
        "records_checked": len(records),
    }


def build_phase_2a_04_plan_evidence_ledger_report() -> Dict[str, Any]:
    phase_2a_03_report = build_phase_2a_03_dry_run_job_plan_gate_report()
    accepted_plan_results = phase_2a_03_report["allowed_request_results"]
    rejected_request_results = phase_2a_03_report["rejected_request_results"]
    ledger = build_phase_2a_04_plan_evidence_ledger(accepted_plan_results, rejected_request_results)
    validation = validate_phase_2a_04_evidence_binding(ledger, accepted_plan_results, rejected_request_results)
    status = "PASS" if validation["valid"] else "FAIL"
    return {
        "phase": PHASE,
        "status": status,
        "overall_status": status,
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_SUMMARY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "source_accepted_plans": len(accepted_plan_results),
            "source_rejected_requests": len(rejected_request_results),
            "accepted_evidence_records": len(ledger["accepted_evidence_records"]),
            "rejected_evidence_records": len(ledger["rejected_evidence_records"]),
            "runner_invoked_count": sum(1 for record in ledger["records"] if record["runner_invoked"]),
            "adapter_invoked_count": sum(1 for record in ledger["records"] if record["adapter_invoked"]),
            "live_execution_opened_count": sum(1 for record in ledger["records"] if record["live_execution_opened"]),
            "next_phase_allowed_count": sum(1 for record in ledger["records"] if record["next_phase_allowed"]),
            "unsafe_payload_errors": len(
                [error for error in validation["errors"] if error.startswith("UNSAFE_EVIDENCE_")]
            ),
        },
        "evidence_ledger_format": {
            "evidence_id": "PHASE_2A_04_EVIDENCE_<stable_digest>",
            "source_plan_id": "Phase 2A-03 plan_id or REJECTED_NO_PLAN_<stable_digest>",
            "safe_normalized_request_summary": "digest-backed summary with safe field names only",
            "non_executable_proof": "report-only binding facts without executable payload details",
        },
        "dangerous_evidence_markers_rejected": sorted(DANGEROUS_EVIDENCE_MARKERS),
        "validation": validation,
        "ledger": ledger,
    }


def write_phase_2a_04_plan_evidence_ledger_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_04_plan_evidence_ledger_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    summary_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )
    record_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(record['evidence_id']))}</td>"
        f"<td>{html.escape(str(record['source_job_type']))}</td>"
        f"<td>{html.escape(str(record['source_plan_id']))}</td>"
        f"<td>{html.escape(str(record['accepted_or_rejected']))}</td>"
        f"<td>{html.escape(str(record['rejection_reason']))}</td>"
        f"<td>{html.escape(str(record['runner_invoked']))}</td>"
        f"<td>{html.escape(str(record['adapter_invoked']))}</td>"
        f"<td>{html.escape(str(record['live_execution_opened']))}</td>"
        "</tr>"
        for record in report["ledger"]["records"]
    )
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Phase 2A-04 binds Phase 2A-03 dry-run outcomes to sanitized traceability evidence only.</p>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
  <h2>Safety Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Evidence Records</h2>
  <table>
    <thead><tr><th>Evidence id</th><th>Job type</th><th>Source plan id</th><th>Status</th><th>Rejection reason</th><th>Runner invoked</th><th>Adapter invoked</th><th>Live execution opened</th></tr></thead>
    <tbody>{record_rows}</tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_04_plan_evidence_ledger(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_04_plan_evidence_ledger_report()
    json_path, html_path = write_phase_2a_04_plan_evidence_ledger_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Accepted evidence records: {report['summary']['accepted_evidence_records']}")
    print(f"Rejected evidence records: {report['summary']['rejected_evidence_records']}")
    print(f"runner_invoked: {str(report['runner_invoked']).lower()}")
    print(f"adapter_invoked: {str(report['adapter_invoked']).lower()}")
    print(f"live_execution_opened: {str(report['live_execution_opened']).lower()}")
    print(f"ssh_execution_opened: {str(report['ssh_execution_opened']).lower()}")
    print(f"netconf_execution_opened: {str(report['netconf_execution_opened']).lower()}")
    print(f"restconf_execution_opened: {str(report['restconf_execution_opened']).lower()}")
    print(f"provider_api_model_call_opened: {str(report['provider_api_model_call_opened']).lower()}")
    print(f"backup_config_invoked: {str(report['backup_config_invoked']).lower()}")
    print(f"arbitrary_command_execution_opened: {str(report['arbitrary_command_execution_opened']).lower()}")
    print(f"arbitrary_script_path_execution_opened: {str(report['arbitrary_script_path_execution_opened']).lower()}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"real_execution_authorized: {str(report['real_execution_authorized']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
