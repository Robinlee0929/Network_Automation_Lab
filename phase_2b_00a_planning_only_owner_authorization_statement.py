"""Phase 2B-00A planning-only owner authorization statement.

This module records a deterministic, local, review-only owner authorization
statement for Phase 2B planning-only scope work. It does not authorize Phase
2B implementation, Phase 2B-01, a runner, adapter, broker, scheduler, queue
worker, SSH, NETCONF, RESTCONF, live device access, provider/API/model calls,
secrets handling, frontend API integration, real backup, real VRRP execution,
device mutation, approval bypass, or safety-gate weakening.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00_authorization_scope_gate_review import (
    FORBIDDEN_CAPABILITIES,
    REQUIRED_ARTIFACT_IDS as PHASE_2B_00_REQUIRED_ARTIFACT_IDS,
    build_phase_2b_00_authorization_scope_gate_review_report,
)


PHASE = "2B-00A"
TASK_NAME = "phase2b-00a-planning-only-owner-authorization-statement"
TITLE = "Phase 2B-00A Planning-Only Owner Authorization Statement"
MODE = "review_only_planning_only_owner_authorization"
SCOPE = "phase_wide_phase_2b_planning_only_scope_authorization"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_00A_PLANNING_ONLY_OWNER_AUTHORIZATION_RECORDED"
BLOCKED_VERDICT = "PHASE_2B_00A_PLANNING_ONLY_OWNER_AUTHORIZATION_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_00a_planning_only_owner_authorization_statement.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_00a_planning_only_owner_authorization_statement.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_00a_planning_only_owner_authorization_statement.md"

OWNER_AUTHORIZATION_STATEMENT = """I authorize Phase 2B planning-only scope work.

This authorization permits review-only, documentation-only, readiness-only, and specification-only artifacts for Phase 2B scope design.

This authorization does not permit Phase 2B implementation.

This authorization does not permit Phase 2B-01.

This authorization does not permit runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device access, provider/API/model calls, secrets handling, frontend API integration, real execution, real backup, real VRRP execution, device mutation, approval bypass, or safety-gate weakening."""

AUTHORIZED_SCOPE = (
    "planning-only artifacts",
    "scope design",
    "readiness checklists",
    "safety boundary design",
    "approval gate design documents",
    "mock-only architecture planning",
    "local-only design notes",
    "static matrices",
    "traceability references",
    "tests proving implementation remains forbidden",
    "CLI/report-index metadata only",
)

IMPLEMENTATION_BOUNDARY = (
    "review-only owner authorization record",
    "documentation-only",
    "readiness-only",
    "specification-only",
    "static criteria only",
    "local deterministic report generation",
    "tests proving implementation remains forbidden",
    "CLI registry/report-index metadata only",
)

SAFETY_FLAGS = {
    "owner_authorization_recorded": True,
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "phase_2b_01_allowed": False,
    "implementation_allowed": False,
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

TRACEABILITY_ARTIFACT_IDS = (
    "AGENTS.md",
    "phase_2b_00_authorization_scope_gate_review",
    "phase_2b_00_authorization_scope_gate_review_doc",
    "phase_2b_00_authorization_scope_gate_review_test",
    "next_phase_authorization_criteria_pack",
    *PHASE_2B_00_REQUIRED_ARTIFACT_IDS,
)

TRACEABILITY_ARTIFACTS = (
    {
        "artifact_id": "AGENTS.md",
        "source": "AGENTS.md",
        "relevance": "Repository safety and validation instructions.",
    },
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review",
        "source": "phase_2b_00_authorization_scope_gate_review.py",
        "relevance": "Prior Phase 2B-00 authorization/scope gate review.",
    },
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review_doc",
        "source": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "relevance": "Prior Phase 2B-00 reviewer-facing decision record.",
    },
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review_test",
        "source": "tests/test_phase_2b_00_authorization_scope_gate_review.py",
        "relevance": "Prior Phase 2B-00 negative safety tests.",
    },
    {
        "artifact_id": "next_phase_authorization_criteria_pack",
        "source": "docs/phase_2a/next_phase_authorization_criteria_pack.md",
        "relevance": "Human authorization format and stop conditions.",
    },
    {
        "artifact_id": "phase2a_readonly_job_runner_framework",
        "source": "phase2a_readonly_job_runner_framework.py",
        "relevance": "Phase 2A-02 validator and no-execution baseline.",
    },
    {
        "artifact_id": "phase_2a_03_dry_run_job_plan_gate",
        "source": "phase_2a_03_dry_run_job_plan_gate.py",
        "relevance": "Dry-run plan gate and non-execution proof.",
    },
    {
        "artifact_id": "phase_2a_04_plan_evidence_ledger",
        "source": "phase_2a_04_plan_evidence_ledger.py",
        "relevance": "Plan evidence and traceability ledger.",
    },
    {
        "artifact_id": "phase_2a_05_dry_run_result_envelope_renderer",
        "source": "phase_2a_05_dry_run_result_envelope_renderer.py",
        "relevance": "Dry-run result envelope format.",
    },
    {
        "artifact_id": "phase_2a_06_negative_regression_matrix",
        "source": "phase_2a_06_negative_regression_matrix.py",
        "relevance": "Negative regression safety lock.",
    },
    {
        "artifact_id": "phase_2a_07_vrrp_dry_run_validation_pack",
        "source": "phase_2a_07_vrrp_dry_run_validation_pack.py",
        "relevance": "Artifact-to-jobs dry-run validation pack.",
    },
    {
        "artifact_id": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
        "source": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
        "relevance": "Phase-wide example job catalog.",
    },
    {
        "artifact_id": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
        "source": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
        "relevance": "Mock display contract without frontend API integration.",
    },
    {
        "artifact_id": "phase_2a_10_safe_boundary_implementation_readiness_artifact",
        "source": "phase_2a_10_safe_boundary_implementation_readiness_artifact.py",
        "relevance": "Safe-boundary readiness while Phase 2B remained disabled.",
    },
    {
        "artifact_id": "phase_2a_11_phase_closure_final_readiness_review",
        "source": "phase_2a_11_phase_closure_final_readiness_review.py",
        "relevance": "Phase 2A closure review.",
    },
)

STOP_CONDITIONS = (
    "Any work attempts to implement Phase 2B rather than plan or specify it.",
    "Any task attempts to create or authorize Phase 2B-01.",
    "Any forbidden capability is enabled or implied as partially enabled.",
    "Scope narrows to one example job type.",
    "Rejected scenarios can reach a runner, adapter, broker, or execution path.",
    "A future artifact changes implementation_allowed or phase_2b_01_allowed to true without a separate explicit gate.",
)

COMPLETION_MARKERS = (
    "PHASE_2B_00A_PLANNING_ONLY_OWNER_AUTHORIZATION_RECORDED",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "OWNER_AUTHORIZATION_STATEMENT_RECORDED_EXACTLY",
    "PHASE_2B_PLANNING_ONLY_AUTHORIZED_TRUE",
    "PHASE_2B_IMPLEMENTATION_ALLOWED_FALSE",
    "PHASE_2B_01_ALLOWED_FALSE",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_CAPABILITIES_ENABLED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)


def _forbidden_capability_matrix() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_00a": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _traceability_rows() -> Tuple[Dict[str, Any], ...]:
    phase_2b_00 = build_phase_2b_00_authorization_scope_gate_review_report()
    status_by_id = {
        "phase_2b_00_authorization_scope_gate_review": phase_2b_00.get("status", "UNKNOWN"),
        "next_phase_authorization_criteria_pack": "CRITERIA_ONLY",
        "AGENTS.md": "READ_BEFORE_CHANGES",
    }
    return tuple(
        {
            **deepcopy(artifact),
            "reviewed": True,
            "source_status": status_by_id.get(str(artifact["artifact_id"]), "REFERENCED"),
        }
        for artifact in TRACEABILITY_ARTIFACTS
    )


def validate_phase_2b_00a_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []

    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("owner_authorization_statement") != OWNER_AUTHORIZATION_STATEMENT:
        errors.append("OWNER_AUTHORIZATION_STATEMENT_MISMATCH")

    scope_confirmation = report.get("scope_confirmation", {})
    if not isinstance(scope_confirmation, Mapping):
        errors.append("SCOPE_CONFIRMATION_NOT_OBJECT")
        scope_confirmation = {}
    for field in (
        "PHASE_GOAL",
        "AUTHORIZED_SCOPE",
        "EXAMPLE_JOB_TYPES",
        "FORBIDDEN_SCOPE",
        "EXISTING_ARTIFACTS_TO_REFERENCE",
        "IMPLEMENTATION_BOUNDARY",
    ):
        if field not in scope_confirmation:
            errors.append(f"SCOPE_CONFIRMATION_FIELD_MISSING:{field}")
    if scope_confirmation.get("scope_narrowed_to_one_example") is not False:
        errors.append("SCOPE_NARROWED_TO_ONE_EXAMPLE")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1 or example_job_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    if set(report.get("authorized_scope", [])) != set(AUTHORIZED_SCOPE):
        errors.append("AUTHORIZED_SCOPE_MISMATCH")
    if set(report.get("implementation_boundary", [])) != set(IMPLEMENTATION_BOUNDARY):
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    matrix = report.get("forbidden_capability_matrix", [])
    matrix_names = {str(item.get("capability")) for item in matrix if isinstance(item, Mapping)}
    if matrix_names != set(FORBIDDEN_CAPABILITIES):
        errors.append("FORBIDDEN_CAPABILITY_MATRIX_MISMATCH")
    for item in matrix if isinstance(matrix, Sequence) else ():
        if not isinstance(item, Mapping):
            errors.append("FORBIDDEN_CAPABILITY_ITEM_NOT_OBJECT")
            continue
        if item.get("enabled") is not False or item.get("allowed_by_phase_2b_00a") is not False:
            errors.append(f"FORBIDDEN_CAPABILITY_ENABLED:{item.get('capability')}")

    traceability = report.get("traceability_to_existing_artifacts", [])
    trace_ids = {str(item.get("artifact_id")) for item in traceability if isinstance(item, Mapping)}
    if trace_ids != set(TRACEABILITY_ARTIFACT_IDS):
        errors.append("TRACEABILITY_ARTIFACT_SET_MISMATCH")
    if any(item.get("reviewed") is not True for item in traceability if isinstance(item, Mapping)):
        errors.append("TRACEABILITY_NOT_FULLY_REVIEWED")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    verdict = report.get("machine_readable_verdict", {})
    if not isinstance(verdict, Mapping):
        errors.append("MACHINE_READABLE_VERDICT_NOT_OBJECT")
        verdict = {}
    if verdict.get("FINAL_VERDICT") != FINAL_VERDICT:
        errors.append("MACHINE_VERDICT_MISMATCH")
    if verdict.get("PHASE_2B_PLANNING_ONLY_AUTHORIZED") != "YES":
        errors.append("MACHINE_PLANNING_ONLY_AUTHORIZED_NOT_YES")
    if verdict.get("PHASE_2B_IMPLEMENTATION_ALLOWED") != "NO":
        errors.append("MACHINE_IMPLEMENTATION_ALLOWED_NOT_NO")
    if verdict.get("PHASE_2B_01_ALLOWED") != "NO":
        errors.append("MACHINE_PHASE_2B_01_ALLOWED_NOT_NO")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "forbidden_capabilities_checked": len(matrix_names),
        "traceability_artifacts_checked": len(trace_ids),
    }


def build_phase_2b_00a_planning_only_owner_authorization_statement_report() -> Dict[str, Any]:
    traceability = _traceability_rows()
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "owner_authorization_statement": OWNER_AUTHORIZATION_STATEMENT,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_changes": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "PHASE_GOAL": (
                "Move Phase 2B from not authorized to limited planning-only scope authorization, "
                "without authorizing implementation or Phase 2B-01."
            ),
            "AUTHORIZED_SCOPE": list(AUTHORIZED_SCOPE),
            "EXAMPLE_JOB_TYPES": list(REQUIRED_JOB_TYPES),
            "FORBIDDEN_SCOPE": list(FORBIDDEN_CAPABILITIES),
            "EXISTING_ARTIFACTS_TO_REFERENCE": list(TRACEABILITY_ARTIFACT_IDS),
            "IMPLEMENTATION_BOUNDARY": list(IMPLEMENTATION_BOUNDARY),
            "scope_narrowed_to_one_example": False,
        },
        "authorized_scope": list(AUTHORIZED_SCOPE),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "forbidden_capability_matrix": list(_forbidden_capability_matrix()),
        "traceability_to_existing_artifacts": list(traceability),
        "stop_conditions": list(STOP_CONDITIONS),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "PHASE_2B_01_ALLOWED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "owner_authorization_recorded": True,
            "phase_2b_planning_only_authorized": True,
            "phase_2b_implementation_allowed": False,
            "phase_2b_01_allowed": False,
            "example_job_types_checked": len(REQUIRED_JOB_TYPES),
            "forbidden_capabilities_enabled": 0,
            "traceability_artifacts_checked": len(traceability),
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_00a_report(report)
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


def _forbidden_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['capability']))}</td>"
        f"<td>{html.escape(str(item['enabled']))}</td>"
        f"<td>{html.escape(str(item['allowed_by_phase_2b_00a']))}</td>"
        f"<td>{html.escape(str(item['status']))}</td>"
        "</tr>"
        for item in report["forbidden_capability_matrix"]
    )


def _traceability_rows_html(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['artifact_id']))}</td>"
        f"<td>{html.escape(str(item['source']))}</td>"
        f"<td>{html.escape(str(item['source_status']))}</td>"
        f"<td>{html.escape(str(item['reviewed']))}</td>"
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
    pre {{ white-space: pre-wrap; background: #f4f6f8; padding: 1rem; border: 1px solid #cbd5e1; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: <strong>{html.escape(str(report["status"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <h2>Owner Authorization Statement</h2>
  <pre>{html.escape(str(report["owner_authorization_statement"]))}</pre>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Authorized Scope</h2>
  <ul>{_list_items(report["authorized_scope"])}</ul>
  <h2>Forbidden Capabilities</h2>
  <table>
    <thead><tr><th>Capability</th><th>Enabled</th><th>Allowed by 00A</th><th>Status</th></tr></thead>
    <tbody>{_forbidden_rows(report)}</tbody>
  </table>
  <h2>Traceability</h2>
  <table>
    <thead><tr><th>Artifact</th><th>Source</th><th>Status</th><th>Reviewed</th></tr></thead>
    <tbody>{_traceability_rows_html(report)}</tbody>
  </table>
  <h2>Stop Conditions</h2>
  <ul>{_list_items(report["stop_conditions"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_00a_planning_only_owner_authorization_statement_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_00a_planning_only_owner_authorization_statement_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_00a_planning_only_owner_authorization_statement(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_00a_planning_only_owner_authorization_statement_report()
    json_path, html_path = write_phase_2b_00a_planning_only_owner_authorization_statement_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Owner authorization recorded: {str(report['owner_authorization_recorded']).lower()}")
    print(f"phase_2b_planning_only_authorized: {str(report['phase_2b_planning_only_authorized']).lower()}")
    print(f"phase_2b_implementation_allowed: {str(report['phase_2b_implementation_allowed']).lower()}")
    print(f"phase_2b_01_allowed: {str(report['phase_2b_01_allowed']).lower()}")
    print(f"Example job types checked: {report['summary']['example_job_types_checked']}")
    print(f"Forbidden capabilities enabled: {report['summary']['forbidden_capabilities_enabled']}")
    print(f"Traceability artifacts checked: {report['summary']['traceability_artifacts_checked']}")
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
