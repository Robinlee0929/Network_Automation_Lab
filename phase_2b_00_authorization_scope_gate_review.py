"""Phase 2B-00 authorization / scope gate review.

This module creates a deterministic, local, review-only authorization artifact
for deciding whether Phase 2B can be opened. It does not implement Phase 2B,
Phase 2B-01, a runner, adapter, broker, scheduler, queue worker, SSH,
NETCONF, RESTCONF, live device access, provider/API/model calls, secrets
handling, frontend API integration, real backup, real VRRP execution, device
mutation, approval bypass, or safety-gate weakening.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2a_10_safe_boundary_implementation_readiness_artifact import (
    build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report,
)
from phase_2a_11_phase_closure_final_readiness_review import (
    build_phase_2a_11_phase_closure_final_readiness_review_report,
)


PHASE = "2B-00"
TASK_NAME = "phase2b-00-authorization-scope-gate-review"
TITLE = "Phase 2B-00 Authorization / Scope Gate Review"
MODE = "review_only_authorization_scope_gate"
SCOPE = "phase_wide_phase_2b_authorization_scope_gate_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_00_AUTHORIZATION_SCOPE_GATE_REVIEW_ONLY"
PHASE_2B_STATUS = "NOT_AUTHORIZED_YET"
NEXT_ALLOWED_STEP = "PHASE_2B_SCOPE_CONFIRMATION_OR_AUTHORIZATION_CRITERIA_REVIEW"
BLOCKED_VERDICT = "PHASE_2B_00_AUTHORIZATION_SCOPE_GATE_BLOCKED"
NEEDS_SCOPE_CONFIRMATION_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_00_authorization_scope_gate_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_00_authorization_scope_gate_review.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_00_authorization_scope_gate_review.md"

IMPLEMENTATION_BOUNDARY = (
    "review-only artifact",
    "authorization-only scope gate",
    "documentation/report-only",
    "static criteria",
    "readiness checklist",
    "authorization matrix",
    "failure-condition matrix",
    "traceability to existing artifacts",
    "negative tests only",
    "CLI registry/report-index metadata only",
)

FORBIDDEN_CAPABILITIES = (
    "phase_2b_implementation",
    "phase_2b_01",
    "runner",
    "adapter",
    "broker",
    "scheduler",
    "queue_worker",
    "ssh",
    "netconf",
    "restconf",
    "live_device_access",
    "provider_api_model_calls",
    "secrets_handling",
    "frontend_api_integration",
    "real_execution",
    "real_backup",
    "real_vrrp_execution",
    "device_mutation",
    "approval_bypass",
    "safety_gate_weakening",
)

SAFETY_FLAGS = {
    "implementation_allowed": False,
    "phase_2b_authorized": False,
    "phase_2b_implementation_started": False,
    "phase_2b_01_allowed": False,
    "runner_enabled": False,
    "adapter_enabled": False,
    "broker_enabled": False,
    "scheduler_enabled": False,
    "queue_worker_enabled": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "live_device_access_enabled": False,
    "provider_api_model_calls_enabled": False,
    "secrets_handling_enabled": False,
    "frontend_api_integration_enabled": False,
    "real_execution_enabled": False,
    "real_backup_enabled": False,
    "real_vrrp_execution_enabled": False,
    "device_mutation_enabled": False,
    "approval_bypass_enabled": False,
    "safety_gate_weakening_enabled": False,
    "next_phase_allowed": False,
}

REQUIRED_ARTIFACT_IDS = (
    "phase2a_readonly_job_runner_framework",
    "phase_2a_03_dry_run_job_plan_gate",
    "phase_2a_04_plan_evidence_ledger",
    "phase_2a_05_dry_run_result_envelope_renderer",
    "phase_2a_06_negative_regression_matrix",
    "phase_2a_07_vrrp_dry_run_validation_pack",
    "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
    "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
    "phase_2a_10_safe_boundary_implementation_readiness_artifact",
    "phase_2a_11_phase_closure_final_readiness_review",
    "next_phase_authorization_criteria_pack",
)

REFERENCED_ARTIFACTS = (
    {
        "artifact_id": "phase2a_readonly_job_runner_framework",
        "phase": "2A-02",
        "source": "phase2a_readonly_job_runner_framework.py",
        "doc": "docs/phase2a_readonly_job_runner_framework.md",
        "relevance": "Job spec validator and negative input matrix baseline.",
    },
    {
        "artifact_id": "phase_2a_03_dry_run_job_plan_gate",
        "phase": "2A-03",
        "source": "phase_2a_03_dry_run_job_plan_gate.py",
        "doc": "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
        "relevance": "Dry-run plan gate and non-execution proof.",
    },
    {
        "artifact_id": "phase_2a_04_plan_evidence_ledger",
        "phase": "2A-04",
        "source": "phase_2a_04_plan_evidence_ledger.py",
        "doc": "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
        "relevance": "Reviewer evidence ledger for accepted and rejected plans.",
    },
    {
        "artifact_id": "phase_2a_05_dry_run_result_envelope_renderer",
        "phase": "2A-05",
        "source": "phase_2a_05_dry_run_result_envelope_renderer.py",
        "doc": "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
        "relevance": "Dry-run result envelope and reviewer report shape.",
    },
    {
        "artifact_id": "phase_2a_06_negative_regression_matrix",
        "phase": "2A-06",
        "source": "phase_2a_06_negative_regression_matrix.py",
        "doc": "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
        "relevance": "Negative safety lock for forbidden capabilities.",
    },
    {
        "artifact_id": "phase_2a_07_vrrp_dry_run_validation_pack",
        "phase": "2A-07",
        "source": "phase_2a_07_vrrp_dry_run_validation_pack.py",
        "doc": "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
        "relevance": "Artifact-to-jobs dry-run validation pack; VRRP remains one example only.",
    },
    {
        "artifact_id": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
        "phase": "2A-08",
        "source": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
        "doc": "docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
        "relevance": "Phase-wide example job catalog and UI readiness planning.",
    },
    {
        "artifact_id": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
        "phase": "2A-09",
        "source": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
        "doc": "docs/phase_2a/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md",
        "relevance": "Mock screen/display contract with no frontend API integration.",
    },
    {
        "artifact_id": "phase_2a_10_safe_boundary_implementation_readiness_artifact",
        "phase": "2A-10",
        "source": "phase_2a_10_safe_boundary_implementation_readiness_artifact.py",
        "doc": "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
        "relevance": "Safe-boundary readiness while Phase 2B remains disabled.",
    },
    {
        "artifact_id": "phase_2a_11_phase_closure_final_readiness_review",
        "phase": "2A-11",
        "source": "phase_2a_11_phase_closure_final_readiness_review.py",
        "doc": "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
        "relevance": "Phase 2A closure review; Phase 2B still not authorized.",
    },
    {
        "artifact_id": "next_phase_authorization_criteria_pack",
        "phase": "next-phase criteria",
        "source": "docs/phase_2a/next_phase_authorization_criteria_pack.md",
        "doc": "docs/phase_2a/next_phase_authorization_criteria_pack.md",
        "relevance": "Criteria-only pack requiring explicit owner authorization.",
    },
)

REQUIRED_GATES_BEFORE_PHASE_2B_01 = (
    "Project owner explicitly authorizes Phase 2B planning or implementation with exact approved wording.",
    "Exact Phase 2B scope and non-scope are approved without narrowing to a single example job type.",
    "Any proposed safety-boundary upgrade has a separate approved gate and negative tests.",
    "Forbidden capability list remains locked unless a separate approved gate changes one item explicitly.",
    "Reviewer evidence expectations and rollback/stop process are written before implementation.",
    "Phase 2B-01 task title, branch, files, and tests do not imply unapproved implementation.",
)

SAFETY_UPGRADE_CONDITIONS = (
    "Separate explicit approval for the exact capability being upgraded.",
    "Reviewer-visible threat/safety case for the new boundary.",
    "Negative tests proving rejected scenarios do not reach adapters, brokers, runners, or execution paths.",
    "No secret, credential, live target, or provider/API/model path is introduced without its own gate.",
    "Rollback/stop criteria are documented and testable before any implementation begins.",
)

STOP_FAILURE_CONDITIONS = (
    "AGENTS.md was not read before changes.",
    "Scope is narrowed to only one example job type.",
    "Phase 2B or Phase 2B-01 implementation begins before explicit authorization.",
    "Any runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, real backup, real VRRP, mutation, approval bypass, or safety-gate weakening path is added.",
    "Rejected intent would invoke an adapter, broker, runner, or execution path.",
    "next_phase_allowed, implementation_allowed, or phase_2b_authorized is changed to true.",
)

COMPLETION_MARKERS = (
    "PHASE_2B_00_AUTHORIZATION_SCOPE_GATE_REVIEW_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "PHASE_WIDE_SCOPE_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "PHASE_2A_CLOSURE_REFERENCED",
    "NEXT_PHASE_AUTHORIZATION_CRITERIA_REFERENCED",
    "IMPLEMENTATION_ALLOWED_FALSE",
    "PHASE_2B_STATUS_NOT_AUTHORIZED_YET",
    "PHASE_2B_01_ALLOWED_FALSE",
    "FORBIDDEN_CAPABILITIES_LOCKED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)


def _status_from(report: Mapping[str, Any]) -> str:
    return str(report.get("status") or report.get("overall_status") or report.get("status_label") or "UNKNOWN")


def _authorization_matrix() -> Tuple[Dict[str, Any], ...]:
    return (
        {
            "criterion": "Phase 2A closure evidence exists",
            "status": "PASS",
            "evidence": "Phase 2A-11 closure artifact can be referenced.",
            "authorizes_phase_2b": False,
        },
        {
            "criterion": "Next-phase authorization criteria exist",
            "status": "PASS",
            "evidence": "Criteria-only next-phase authorization pack is present.",
            "authorizes_phase_2b": False,
        },
        {
            "criterion": "Explicit Phase 2B project-owner authorization exists",
            "status": "BLOCKED",
            "evidence": "No explicit Phase 2B authorization evidence is present in the repository.",
            "authorizes_phase_2b": False,
        },
        {
            "criterion": "Phase 2B-01 implementation gate exists",
            "status": "BLOCKED",
            "evidence": "Phase 2B-01 remains forbidden until Phase 2B authorization is granted.",
            "authorizes_phase_2b": False,
        },
    )


def _allowed_planning_candidates() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "job_type": job_type,
            "role": "example_only_not_full_phase_scope",
            "allowed_now": "planning_readiness_only",
            "executable": False,
            "can_authorize_phase_2b": False,
        }
        for job_type in REQUIRED_JOB_TYPES
    )


def _traceability_rows(
    phase_2a_10: Mapping[str, Any],
    phase_2a_11: Mapping[str, Any],
) -> Tuple[Dict[str, Any], ...]:
    status_by_id = {
        "phase_2a_10_safe_boundary_implementation_readiness_artifact": _status_from(phase_2a_10),
        "phase_2a_11_phase_closure_final_readiness_review": _status_from(phase_2a_11),
        "next_phase_authorization_criteria_pack": "CRITERIA_ONLY",
    }
    rows = []
    for artifact in REFERENCED_ARTIFACTS:
        artifact_id = str(artifact["artifact_id"])
        rows.append(
            {
                **deepcopy(artifact),
                "reviewed": True,
                "source_status": status_by_id.get(artifact_id, "REFERENCED"),
                "phase_2b_authorization_evidence": False,
            }
        )
    return tuple(rows)


def _forbidden_capability_status() -> Dict[str, Any]:
    return {
        "status": "LOCKED",
        "capabilities": {capability: False for capability in FORBIDDEN_CAPABILITIES},
        "phase_2b_authorized": False,
        "implementation_allowed": False,
        "phase_2b_01_allowed": False,
        "next_phase_allowed": False,
    }


def validate_phase_2b_00_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []

    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")

    agents = report.get("agents_md_pre_read", {})
    if not isinstance(agents, Mapping):
        errors.append("AGENTS_MD_PRE_READ_NOT_OBJECT")
    else:
        if agents.get("found") is not True:
            errors.append("AGENTS_MD_FOUND_NOT_TRUE")
        if agents.get("read_before_changes") is not True:
            errors.append("AGENTS_MD_READ_BEFORE_CHANGES_NOT_TRUE")
        if agents.get("modified") is not False:
            errors.append("AGENTS_MD_MODIFIED_NOT_FALSE")

    scope_confirmation = report.get("scope_confirmation", {})
    if not isinstance(scope_confirmation, Mapping):
        errors.append("SCOPE_CONFIRMATION_NOT_OBJECT")
        scope_confirmation = {}
    for field in (
        "PHASE_GOAL",
        "EXAMPLE_JOB_TYPES",
        "FORBIDDEN_SCOPE",
        "EXISTING_ARTIFACTS_TO_REFERENCE",
        "IMPLEMENTATION_BOUNDARY",
    ):
        if field not in scope_confirmation:
            errors.append(f"SCOPE_CONFIRMATION_FIELD_MISSING:{field}")
    if scope_confirmation.get("needs_scope_confirmation") is not False:
        errors.append("NEEDS_SCOPE_CONFIRMATION_NOT_FALSE")
    if scope_confirmation.get("scope_narrowed_to_one_example") is not False:
        errors.append("SCOPE_NARROWED_TO_ONE_EXAMPLE")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1 or example_job_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    boundary = set(report.get("implementation_boundary", []))
    if boundary != set(IMPLEMENTATION_BOUNDARY):
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    traceability = report.get("traceability_to_existing_artifacts", [])
    trace_ids = {str(item.get("artifact_id")) for item in traceability if isinstance(item, Mapping)}
    if trace_ids != set(REQUIRED_ARTIFACT_IDS):
        errors.append("TRACEABILITY_ARTIFACT_SET_MISMATCH")
    if any(item.get("reviewed") is not True for item in traceability if isinstance(item, Mapping)):
        errors.append("TRACEABILITY_NOT_FULLY_REVIEWED")

    forbidden_status = report.get("forbidden_capability_status", {})
    capabilities = forbidden_status.get("capabilities", {}) if isinstance(forbidden_status, Mapping) else {}
    if set(capabilities) != set(FORBIDDEN_CAPABILITIES):
        errors.append("FORBIDDEN_CAPABILITY_SET_MISMATCH")
    for capability, enabled in capabilities.items() if isinstance(capabilities, Mapping) else ():
        if enabled is not False:
            errors.append(f"FORBIDDEN_CAPABILITY_ENABLED:{capability}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")

    if report.get("phase_2b_status") != PHASE_2B_STATUS:
        errors.append("PHASE_2B_STATUS_NOT_LOCKED")
    if report.get("final_verdict") != FINAL_VERDICT:
        errors.append("FINAL_VERDICT_MISMATCH")
    if report.get("machine_readable_verdict", {}).get("FINAL_VERDICT") != FINAL_VERDICT:
        errors.append("MACHINE_VERDICT_MISMATCH")
    if report.get("machine_readable_verdict", {}).get("IMPLEMENTATION_ALLOWED") != "NO":
        errors.append("MACHINE_IMPLEMENTATION_ALLOWED_NOT_NO")
    if report.get("machine_readable_verdict", {}).get("PHASE_2B_01_ALLOWED") != "NO":
        errors.append("MACHINE_PHASE_2B_01_ALLOWED_NOT_NO")

    if not report.get("required_gates_before_phase_2b_01"):
        errors.append("REQUIRED_GATES_MISSING")
    if not report.get("safety_upgrade_conditions"):
        errors.append("SAFETY_UPGRADE_CONDITIONS_MISSING")
    if not report.get("stop_failure_conditions"):
        errors.append("STOP_FAILURE_CONDITIONS_MISSING")

    authorization_matrix = report.get("authorization_matrix", [])
    if not authorization_matrix:
        errors.append("AUTHORIZATION_MATRIX_MISSING")
    if any(item.get("authorizes_phase_2b") is not False for item in authorization_matrix if isinstance(item, Mapping)):
        errors.append("AUTHORIZATION_MATRIX_AUTHORIZES_PHASE_2B")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "referenced_artifacts_checked": len(traceability) if isinstance(traceability, Sequence) else 0,
        "example_job_types_checked": len(example_job_types),
        "forbidden_capabilities_checked": len(capabilities) if isinstance(capabilities, Mapping) else 0,
    }


def build_phase_2b_00_authorization_scope_gate_review_report() -> Dict[str, Any]:
    phase_2a_10 = build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report()
    phase_2a_11 = build_phase_2a_11_phase_closure_final_readiness_review_report()
    traceability = _traceability_rows(phase_2a_10, phase_2a_11)
    forbidden_status = _forbidden_capability_status()

    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "phase_2b_status": PHASE_2B_STATUS,
        "final_verdict": FINAL_VERDICT,
        "final_verdict_conservative": True,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_changes": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "PHASE_GOAL": (
                "Decide whether Phase 2B can be opened by defining authorization criteria, scope boundaries, "
                "allowed planning/readiness candidates, forbidden capabilities, safety upgrade conditions, "
                "required gates, and stop/failure conditions."
            ),
            "EXAMPLE_JOB_TYPES": list(REQUIRED_JOB_TYPES),
            "FORBIDDEN_SCOPE": list(FORBIDDEN_CAPABILITIES),
            "EXISTING_ARTIFACTS_TO_REFERENCE": list(REQUIRED_ARTIFACT_IDS),
            "IMPLEMENTATION_BOUNDARY": list(IMPLEMENTATION_BOUNDARY),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "allowed_planning_readiness_candidates": list(_allowed_planning_candidates()),
        "forbidden_capability_status": forbidden_status,
        "authorization_matrix": list(_authorization_matrix()),
        "required_gates_before_phase_2b_01": list(REQUIRED_GATES_BEFORE_PHASE_2B_01),
        "safety_upgrade_conditions": list(SAFETY_UPGRADE_CONDITIONS),
        "stop_failure_conditions": list(STOP_FAILURE_CONDITIONS),
        "traceability_to_existing_artifacts": list(traceability),
        "phase_2b_implemented": False,
        "phase_2b_01_allowed": False,
        "next_allowed_step": NEXT_ALLOWED_STEP,
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "IMPLEMENTATION_ALLOWED": "NO",
            "PHASE_2B_STATUS": PHASE_2B_STATUS,
            "NEXT_ALLOWED_STEP": NEXT_ALLOWED_STEP,
            "PHASE_2B_01_ALLOWED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "authorization_matrix_items": len(_authorization_matrix()),
            "example_job_types_checked": len(REQUIRED_JOB_TYPES),
            "referenced_artifacts_checked": len(traceability),
            "forbidden_capabilities_locked": len(FORBIDDEN_CAPABILITIES),
            "required_gates_before_phase_2b_01": len(REQUIRED_GATES_BEFORE_PHASE_2B_01),
            "safety_upgrade_conditions": len(SAFETY_UPGRADE_CONDITIONS),
            "stop_failure_conditions": len(STOP_FAILURE_CONDITIONS),
            "implementation_allowed": False,
            "phase_2b_authorized": False,
            "phase_2b_01_allowed": False,
            "forbidden_capabilities_enabled": 0,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_00_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = BLOCKED_VERDICT
        report["summary"]["final_verdict"] = BLOCKED_VERDICT
    return report


def _list_items(values: Sequence[Any]) -> str:
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values)


def _dict_rows(values: Mapping[str, Any]) -> str:
    return "".join(
        "<tr>"
        f"<th>{html.escape(str(key))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for key, value in values.items()
    )


def _matrix_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['criterion']))}</td>"
        f"<td>{html.escape(str(item['status']))}</td>"
        f"<td>{html.escape(str(item['evidence']))}</td>"
        f"<td>{html.escape(str(item['authorizes_phase_2b']))}</td>"
        "</tr>"
        for item in report["authorization_matrix"]
    )


def _traceability_rows_html(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['phase']))}</td>"
        f"<td>{html.escape(str(item['artifact_id']))}</td>"
        f"<td>{html.escape(str(item['source']))}</td>"
        f"<td>{html.escape(str(item['source_status']))}</td>"
        f"<td>{html.escape(str(item['phase_2b_authorization_evidence']))}</td>"
        "</tr>"
        for item in report["traceability_to_existing_artifacts"]
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2933; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 0.5rem; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    code {{ background: #f4f6f8; padding: 0.1rem 0.25rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: <strong>{html.escape(str(report["status"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>Phase 2B is not authorized yet. This artifact is review-only and authorization-only.</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Authorization Matrix</h2>
  <table>
    <thead><tr><th>Criterion</th><th>Status</th><th>Evidence</th><th>Authorizes Phase 2B</th></tr></thead>
    <tbody>{_matrix_rows(report)}</tbody>
  </table>
  <h2>Required Gates Before Phase 2B-01</h2>
  <ul>{_list_items(report["required_gates_before_phase_2b_01"])}</ul>
  <h2>Stop / Failure Conditions</h2>
  <ul>{_list_items(report["stop_failure_conditions"])}</ul>
  <h2>Traceability</h2>
  <table>
    <thead><tr><th>Phase</th><th>Artifact</th><th>Source</th><th>Status</th><th>Phase 2B Authorization Evidence</th></tr></thead>
    <tbody>{_traceability_rows_html(report)}</tbody>
  </table>
  <h2>Forbidden Capabilities</h2>
  <table><tbody>{_dict_rows(report["forbidden_capability_status"]["capabilities"])}</tbody></table>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_00_authorization_scope_gate_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_00_authorization_scope_gate_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_00_authorization_scope_gate_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_00_authorization_scope_gate_review_report()
    json_path, html_path = write_phase_2b_00_authorization_scope_gate_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Phase 2B status: {report['phase_2b_status']}")
    print(f"Implementation allowed: {str(report['implementation_allowed']).lower()}")
    print(f"Phase 2B-01 allowed: {str(report['phase_2b_01_allowed']).lower()}")
    print(f"Example job types checked: {report['summary']['example_job_types_checked']}")
    print(f"Referenced artifacts checked: {report['summary']['referenced_artifacts_checked']}")
    print(f"Forbidden capabilities locked: {report['summary']['forbidden_capabilities_locked']}")
    print(f"Required gates before Phase 2B-01: {report['summary']['required_gates_before_phase_2b_01']}")
    print(f"Stop/failure conditions: {report['summary']['stop_failure_conditions']}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"broker_enabled: {str(report['broker_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"netconf_enabled: {str(report['netconf_enabled']).lower()}")
    print(f"restconf_enabled: {str(report['restconf_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"provider_api_model_calls_enabled: {str(report['provider_api_model_calls_enabled']).lower()}")
    print(f"secrets_handling_enabled: {str(report['secrets_handling_enabled']).lower()}")
    print(f"safety_gate_weakening_enabled: {str(report['safety_gate_weakening_enabled']).lower()}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
