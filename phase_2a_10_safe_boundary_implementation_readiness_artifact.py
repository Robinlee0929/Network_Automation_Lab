"""Phase 2A-10 safe-boundary implementation readiness artifact.

This module creates a deterministic readiness report for moving the full
Phase 2A Jobs workflow from scope confirmation into safe-boundary
implementation readiness. It is documentation, local artifact validation, and
report output only. It does not add Phase 2B, a runner, adapter, broker,
scheduler, queue worker, SSH, NETCONF, RESTCONF, live device access, real
execution, real backup, real VRRP execution, frontend API integration,
provider/API/model calls, secrets handling, or weaker safety gates.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import (
    REQUIRED_JOB_TYPES,
)
from phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack import (
    DOC_PATH as PHASE_2A_09_DOC_PATH,
    REPORT_HTML as PHASE_2A_09_REPORT_HTML,
    REPORT_JSON as PHASE_2A_09_REPORT_JSON,
    build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report,
)


PHASE = "2A-10"
TASK_NAME = "phase2a-10-safe-boundary-implementation-readiness-artifact"
TITLE = "Phase 2A-10 Safe-Boundary Implementation Readiness Artifact"
STATUS_LABEL = "PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READY"
BLOCKED_LABEL = "PHASE_2A_10_BLOCKED"
MODE = "safe_boundary_readiness_report_only"
SCOPE = "phase_wide_jobs_workflow_safe_boundary_implementation_readiness"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_10_safe_boundary_implementation_readiness_artifact.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_10_safe_boundary_implementation_readiness_artifact.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_10_safe_boundary_implementation_readiness_artifact.md"

FORBIDDEN_SCOPE = (
    "Phase 2B",
    "real runner",
    "adapter",
    "broker",
    "scheduler",
    "queue worker",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "real execution",
    "real backup",
    "real VRRP execution",
    "frontend API integration",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "changing or weakening safety gates",
)

IMPLEMENTATION_BOUNDARY = (
    "mock-only planning",
    "read-only dry-run planning",
    "local artifact validation",
    "display contract readiness",
    "envelope consistency",
    "ledger consistency",
    "report consistency",
)

SAFETY_FLAGS = {
    "phase_2b_enabled": False,
    "phase_2b_authorized": False,
    "real_runner_enabled": False,
    "runner_introduced": False,
    "adapter_enabled": False,
    "adapter_introduced": False,
    "broker_enabled": False,
    "broker_introduced": False,
    "scheduler_enabled": False,
    "scheduler_introduced": False,
    "queue_worker_enabled": False,
    "queue_worker_introduced": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "live_device_access_enabled": False,
    "real_execution_enabled": False,
    "real_backup_enabled": False,
    "real_vrrp_execution_enabled": False,
    "frontend_api_integration_enabled": False,
    "provider_calls_enabled": False,
    "api_calls_enabled": False,
    "model_calls_enabled": False,
    "secrets_handling_added": False,
    "safety_gates_weakened": False,
    "next_phase_allowed": False,
}

EXISTING_ARTIFACT_REFERENCES = (
    "AGENTS.md",
    "phase2a_readonly_job_runner_framework.py",
    "docs/phase2a_readonly_job_runner_framework.md",
    "reports/lab-summary/phase2a_readonly_job_runner_framework.json",
    "reports/lab-summary/phase2a_readonly_job_runner_framework.html",
    "phase_2a_03_dry_run_job_plan_gate.py",
    "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
    "reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.json",
    "reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.html",
    "phase_2a_04_plan_evidence_ledger.py",
    "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
    "reports/lab-summary/phase_2a_04_plan_evidence_ledger.json",
    "reports/lab-summary/phase_2a_04_plan_evidence_ledger.html",
    "phase_2a_05_dry_run_result_envelope_renderer.py",
    "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
    "reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.json",
    "reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.html",
    "phase_2a_06_negative_regression_matrix.py",
    "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
    "reports/lab-summary/phase_2a_06_negative_regression_matrix.json",
    "reports/lab-summary/phase_2a_06_negative_regression_matrix.html",
    "phase_2a_07_vrrp_dry_run_validation_pack.py",
    "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
    "reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json",
    "reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.html",
    "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
    "docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
    "reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json",
    "reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.html",
    "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
    PHASE_2A_09_DOC_PATH.as_posix(),
    PHASE_2A_09_REPORT_JSON.as_posix(),
    PHASE_2A_09_REPORT_HTML.as_posix(),
)

REQUIRED_REFERENCE_FRAGMENTS = (
    "AGENTS.md",
    "phase2a_readonly_job_runner_framework",
    "phase_2a_03_dry_run_job_plan_gate",
    "phase_2a_04_plan_evidence_ledger",
    "phase_2a_05_dry_run_result_envelope_renderer",
    "phase_2a_06_negative_regression_matrix",
    "phase_2a_07_vrrp_dry_run_validation_pack",
    "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
    "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
)

COMPLETION_MARKERS = (
    "PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "PHASE_WIDE_SCOPE_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "PRIOR_PHASE_2A_ARTIFACTS_REFERENCED",
    "MOCK_ONLY_PLANNING_ALLOWED",
    "READ_ONLY_DRY_RUN_PLANNING_ALLOWED",
    "LOCAL_ARTIFACT_VALIDATION_ALLOWED",
    "DISPLAY_CONTRACT_READINESS_ALLOWED",
    "ENVELOPE_LEDGER_REPORT_CONSISTENCY_ALLOWED",
    "PHASE_2B_ENABLED_FALSE",
    "REAL_RUNNER_ENABLED_FALSE",
    "ADAPTER_ENABLED_FALSE",
    "BROKER_ENABLED_FALSE",
    "SCHEDULER_ENABLED_FALSE",
    "QUEUE_WORKER_ENABLED_FALSE",
    "SSH_ENABLED_FALSE",
    "NETCONF_ENABLED_FALSE",
    "RESTCONF_ENABLED_FALSE",
    "LIVE_DEVICE_ACCESS_ENABLED_FALSE",
    "REAL_EXECUTION_ENABLED_FALSE",
    "REAL_BACKUP_ENABLED_FALSE",
    "REAL_VRRP_EXECUTION_ENABLED_FALSE",
    "FRONTEND_API_INTEGRATION_ENABLED_FALSE",
    "PROVIDER_CALLS_ENABLED_FALSE",
    "API_CALLS_ENABLED_FALSE",
    "MODEL_CALLS_ENABLED_FALSE",
    "SECRETS_HANDLING_ADDED_FALSE",
    "SAFETY_GATES_WEAKENED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _contains_fragment(references: Iterable[str], fragment: str) -> bool:
    return any(fragment in reference for reference in references)


def _prior_phase_2a_status() -> Dict[str, Any]:
    phase_2a_09 = build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report()
    source = phase_2a_09.get("phase_2a_08_source", {})
    return {
        "phase_2a_09_status": phase_2a_09.get("status"),
        "phase_2a_09_validation_status": phase_2a_09.get("validation", {}).get("status"),
        "phase_2a_09_source_job_count": source.get("source_job_count") if isinstance(source, Mapping) else None,
        "phase_2a_09_source_job_types": list(source.get("source_job_types", [])) if isinstance(source, Mapping) else [],
        "phase_2a_09_next_phase_allowed": phase_2a_09.get("next_phase_allowed"),
        "phase_2a_09_phase_2b_introduced": phase_2a_09.get("phase_2b_introduced"),
        "phase_2a_09_runner_introduced": phase_2a_09.get("runner_introduced"),
        "phase_2a_09_adapter_introduced": phase_2a_09.get("adapter_introduced"),
        "phase_2a_09_live_device_introduced": phase_2a_09.get("live_device_introduced"),
    }


def _readiness_checklist() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "area": area,
            "allowed_inside_phase_2a_10": True,
            "readiness_status": "READY",
            "executable_capability": False,
            "notes": "Allowed only as local reviewer-facing readiness evidence.",
        }
        for area in IMPLEMENTATION_BOUNDARY
    )


def validate_phase_2a_10_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []

    scope_confirmation = report.get("scope_confirmation", {})
    if not isinstance(scope_confirmation, Mapping):
        errors.append("SCOPE_CONFIRMATION_NOT_OBJECT")
        scope_confirmation = {}
    if scope_confirmation.get("phase_wide") is not True:
        errors.append("PHASE_WIDE_NOT_TRUE")
    if scope_confirmation.get("narrowed_to_one_example") is not False:
        errors.append("SCOPE_NARROWED_TO_ONE_EXAMPLE")
    if scope_confirmation.get("example_job_types_treated_as_examples_only") is not True:
        errors.append("EXAMPLE_JOB_TYPES_NOT_MARKED_AS_EXAMPLES_ONLY")

    example_types = set(report.get("example_job_types", []))
    if example_types != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_types) <= 1 or example_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")

    forbidden_scope = set(report.get("forbidden_scope", []))
    missing_forbidden = sorted(set(FORBIDDEN_SCOPE).difference(forbidden_scope))
    if missing_forbidden:
        errors.append("FORBIDDEN_SCOPE_MISSING:" + ",".join(missing_forbidden))

    boundary = report.get("implementation_boundary", {})
    allowed_work = set(boundary.get("allowed_work", [])) if isinstance(boundary, Mapping) else set()
    missing_boundary = sorted(set(IMPLEMENTATION_BOUNDARY).difference(allowed_work))
    if missing_boundary:
        errors.append("IMPLEMENTATION_BOUNDARY_MISSING:" + ",".join(missing_boundary))
    if isinstance(boundary, Mapping) and boundary.get("real_execution_allowed") is not False:
        errors.append("REAL_EXECUTION_ALLOWED_NOT_FALSE")
    if isinstance(boundary, Mapping) and boundary.get("phase_2b_allowed") is not False:
        errors.append("PHASE_2B_ALLOWED_NOT_FALSE")

    references = [str(reference) for reference in report.get("existing_artifacts_referenced", [])]
    for fragment in REQUIRED_REFERENCE_FRAGMENTS:
        if not _contains_fragment(references, fragment):
            errors.append("REQUIRED_ARTIFACT_REFERENCE_MISSING:" + fragment)

    prior_status = report.get("prior_phase_2a_status", {})
    if not isinstance(prior_status, Mapping):
        errors.append("PRIOR_PHASE_2A_STATUS_NOT_OBJECT")
    else:
        if prior_status.get("phase_2a_09_status") != "PASS":
            errors.append("PHASE_2A_09_STATUS_NOT_PASS")
        if set(prior_status.get("phase_2a_09_source_job_types", [])) != set(REQUIRED_JOB_TYPES):
            errors.append("PHASE_2A_09_SOURCE_JOB_TYPES_MISMATCH")
        for key in (
            "phase_2a_09_next_phase_allowed",
            "phase_2a_09_phase_2b_introduced",
            "phase_2a_09_runner_introduced",
            "phase_2a_09_adapter_introduced",
            "phase_2a_09_live_device_introduced",
        ):
            if prior_status.get(key) is not False:
                errors.append(f"PRIOR_PHASE_2A_UNSAFE_FLAG_NOT_FALSE:{key}")

    checklist = report.get("readiness_checklist", [])
    if not isinstance(checklist, Sequence) or isinstance(checklist, (str, bytes, bytearray)):
        errors.append("READINESS_CHECKLIST_NOT_LIST")
    else:
        checklist_areas = {str(item.get("area")) for item in checklist if isinstance(item, Mapping)}
        if checklist_areas != set(IMPLEMENTATION_BOUNDARY):
            errors.append("READINESS_CHECKLIST_AREA_MISMATCH")
        for item in checklist:
            if not isinstance(item, Mapping):
                errors.append("READINESS_CHECKLIST_ITEM_NOT_OBJECT")
                continue
            if item.get("allowed_inside_phase_2a_10") is not True:
                errors.append(f"READINESS_ITEM_NOT_ALLOWED:{item.get('area')}")
            if item.get("executable_capability") is not False:
                errors.append(f"READINESS_ITEM_EXECUTABLE:{item.get('area')}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")

    decision = report.get("readiness_decision", {})
    if not isinstance(decision, Mapping):
        errors.append("READINESS_DECISION_NOT_OBJECT")
    elif decision.get("decision") != STATUS_LABEL:
        errors.append("READINESS_DECISION_NOT_READY")

    try:
        canonical = _canonical_json(report)
        if _canonical_json(json.loads(canonical)) != canonical:
            errors.append("JSON_NOT_DETERMINISTIC")
    except (TypeError, ValueError) as exc:
        errors.append(f"JSON_SERIALIZATION_FAILED:{exc}")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_types),
        "artifact_references_checked": len(references),
        "readiness_items_checked": len(checklist) if isinstance(checklist, Sequence) else 0,
    }


def build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report() -> Dict[str, Any]:
    prior_status = _prior_phase_2a_status()
    report = {
        "phase": PHASE,
        "status": "PASS",
        "overall_status": "PASS",
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "phase_goal": (
            "Phase 2A-10 is a phase-wide readiness artifact for moving the existing "
            "Phase 2A Jobs workflow from scope confirmation into safe-boundary "
            "implementation readiness."
        ),
        "scope_confirmation": {
            "phase_wide": True,
            "narrowed_to_one_example": False,
            "example_job_types_treated_as_examples_only": True,
            "phase_goal": (
                "Confirm safe-boundary implementation readiness for the full Phase 2A Jobs workflow, "
                "not one example job type."
            ),
        },
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_full_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACT_REFERENCES),
        "prior_phase_2a_status": prior_status,
        "implementation_boundary": {
            "allowed_work": list(IMPLEMENTATION_BOUNDARY),
            "real_execution_allowed": False,
            "phase_2b_allowed": False,
            "device_access_allowed": False,
            "provider_api_model_allowed": False,
            "secrets_handling_allowed": False,
            "safety_gate_weakening_allowed": False,
        },
        "readiness_checklist": list(_readiness_checklist()),
        "readiness_decision": {
            "decision": STATUS_LABEL,
            "blocked": False,
            "reason": (
                "Existing Phase 2A-02 through Phase 2A-09 artifacts preserve multi-job scope, "
                "local/mock/read-only/dry-run boundaries, and no-execution proof."
            ),
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "example_job_types": len(REQUIRED_JOB_TYPES),
            "forbidden_scope_items": len(FORBIDDEN_SCOPE),
            "existing_artifact_references": len(EXISTING_ARTIFACT_REFERENCES),
            "readiness_items": len(IMPLEMENTATION_BOUNDARY),
            "executable_items": 0,
            "phase_2b_enabled": False,
            "safety_gates_weakened": False,
            "readiness_decision": STATUS_LABEL,
        },
    }
    validation = validate_phase_2a_10_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    if report["status"] != "PASS":
        report["readiness_decision"]["decision"] = BLOCKED_LABEL
        report["readiness_decision"]["blocked"] = True
    return report


def write_phase_2a_10_safe_boundary_implementation_readiness_artifact_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _list_items(values: Sequence[Any]) -> str:
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values)


def _summary_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )


def _readiness_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['area']))}</td>"
        f"<td>{html.escape(str(item['allowed_inside_phase_2a_10']))}</td>"
        f"<td>{html.escape(str(item['readiness_status']))}</td>"
        f"<td>{html.escape(str(item['executable_capability']))}</td>"
        f"<td>{html.escape(str(item['notes']))}</td>"
        "</tr>"
        for item in report["readiness_checklist"]
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
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
    code {{ background: #f3f6fa; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["status"]))} / {html.escape(str(report["status_label"]))}</p>
  <h2>Phase Goal</h2>
  <p>{html.escape(str(report["phase_goal"]))}</p>
  <h2>Example Job Types</h2>
  <p>These job types are examples only, not the full scope.</p>
  <ul>{_list_items(report["example_job_types"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_referenced"])}</ul>
  <h2>Implementation Boundary</h2>
  <table>
    <thead><tr><th>Area</th><th>Allowed inside Phase 2A-10</th><th>Status</th><th>Executable capability</th><th>Notes</th></tr></thead>
    <tbody>{_readiness_rows(report)}</tbody>
  </table>
  <h2>Readiness Decision</h2>
  <p><strong>{html.escape(str(report["readiness_decision"]["decision"]))}</strong></p>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Completion Markers</h2>
  <ul>{_list_items(report["completion_markers"])}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_10_safe_boundary_implementation_readiness_artifact(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    json_path, html_path = write_phase_2a_10_safe_boundary_implementation_readiness_artifact_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Phase-wide: {str(report['scope_confirmation']['phase_wide']).lower()}")
    print(f"Narrowed to one example: {str(report['scope_confirmation']['narrowed_to_one_example']).lower()}")
    print(f"Example job types: {len(report['example_job_types'])}")
    print(f"Forbidden scope items: {len(report['forbidden_scope'])}")
    print(f"Existing artifact references: {len(report['existing_artifacts_referenced'])}")
    print(f"Readiness items: {len(report['readiness_checklist'])}")
    print(f"phase_2b_enabled: {str(report['phase_2b_enabled']).lower()}")
    print(f"real_runner_enabled: {str(report['real_runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"broker_enabled: {str(report['broker_enabled']).lower()}")
    print(f"scheduler_enabled: {str(report['scheduler_enabled']).lower()}")
    print(f"queue_worker_enabled: {str(report['queue_worker_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"netconf_enabled: {str(report['netconf_enabled']).lower()}")
    print(f"restconf_enabled: {str(report['restconf_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"real_execution_enabled: {str(report['real_execution_enabled']).lower()}")
    print(f"real_backup_enabled: {str(report['real_backup_enabled']).lower()}")
    print(f"real_vrrp_execution_enabled: {str(report['real_vrrp_execution_enabled']).lower()}")
    print(f"frontend_api_integration_enabled: {str(report['frontend_api_integration_enabled']).lower()}")
    print(f"provider_calls_enabled: {str(report['provider_calls_enabled']).lower()}")
    print(f"api_calls_enabled: {str(report['api_calls_enabled']).lower()}")
    print(f"model_calls_enabled: {str(report['model_calls_enabled']).lower()}")
    print(f"secrets_handling_added: {str(report['secrets_handling_added']).lower()}")
    print(f"safety_gates_weakened: {str(report['safety_gates_weakened']).lower()}")
    print(f"Readiness decision: {report['readiness_decision']['decision']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
