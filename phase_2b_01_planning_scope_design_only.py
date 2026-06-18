"""Phase 2B-01 planning scope design only.

This module creates a deterministic, local, planning-only Phase 2B artifact.
It defines what Phase 2B should design and what remains forbidden. It does not
implement Phase 2B, a runner, adapter, broker, scheduler, queue worker, SSH,
NETCONF, RESTCONF, live device access, provider/API/model calls, secrets
handling, frontend API integration, execution, backup, VRRP execution, device
mutation, approval bypass, or safety-gate weakening.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00_authorization_scope_gate_review import (
    build_phase_2b_00_authorization_scope_gate_review_report,
)
from phase_2b_00a_planning_only_owner_authorization_statement import (
    FORBIDDEN_CAPABILITIES,
    build_phase_2b_00a_planning_only_owner_authorization_statement_report,
)


PHASE = "2B-01"
TASK_NAME = "phase2b-01-planning-scope-design-only"
TITLE = "Phase 2B-01 Planning Scope Design Only"
MODE = "planning_only_scope_design_only"
SCOPE = "phase_wide_phase_2b_planning_scope_design_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_01_PLANNING_SCOPE_DESIGN_ONLY"
BLOCKED_VERDICT = "PHASE_2B_01_PLANNING_SCOPE_DESIGN_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_01_planning_scope_design_only.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_01_planning_scope_design_only.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_01_planning_scope_design_only.md"

AUTHORIZED_SCOPE = (
    "planning-only artifact",
    "scope design",
    "readiness design",
    "mock-only architecture planning",
    "local-only queue concept documentation",
    "approval gate design documentation",
    "safety boundary matrix",
    "forbidden capability matrix",
    "implementation prerequisite checklist",
    "traceability to Phase 2B-00 and Phase 2B-00A",
    "tests proving no implementation is authorized",
    "CLI/report-index metadata only",
)

IMPLEMENTATION_BOUNDARY = (
    "deterministic report builder",
    "reviewer-facing documentation",
    "static JSON/HTML evidence",
    "conceptual architecture records only",
    "negative safety tests",
    "CLI/report-index visibility metadata",
    "no executable workflow behavior",
    "no live-device hooks",
    "no provider/API/model integration",
    "no credential or secrets handling",
    "no frontend integration",
)

PLANNING_ARTIFACTS_ALLOWED = (
    "Phase 2B planning goal",
    "authorized planning-only scope",
    "explicit implementation prohibition",
    "forbidden capabilities matrix",
    "conceptual architecture boundaries",
    "safety gate design requirements",
    "future implementation prerequisites",
    "stop conditions",
    "traceability matrix",
    "machine-readable verdict",
)

CONCEPTUAL_ARCHITECTURE_BOUNDARIES = (
    {
        "concept": "mock runner concept",
        "allowed_now": "concept_only",
        "executable": False,
        "implementation_allowed": False,
        "boundary": "May describe future mock-only behavior; must not create a runner or runner entry point.",
    },
    {
        "concept": "local queue concept",
        "allowed_now": "concept_only",
        "executable": False,
        "implementation_allowed": False,
        "boundary": "May describe local queue lifecycle states; must not create scheduler, worker, broker, or queue runtime.",
    },
    {
        "concept": "approval gate concept",
        "allowed_now": "concept_only",
        "executable": False,
        "implementation_allowed": False,
        "boundary": "May define future approval evidence requirements; must not unlock execution or bypass review.",
    },
    {
        "concept": "dry-run execution envelope concept",
        "allowed_now": "concept_only",
        "executable": False,
        "implementation_allowed": False,
        "boundary": "May describe future dry-run envelope fields; must not execute commands or invoke adapters.",
    },
    {
        "concept": "read-only result lifecycle concept",
        "allowed_now": "concept_only",
        "executable": False,
        "implementation_allowed": False,
        "boundary": "May specify reviewer-visible result states; must not collect live data or call devices.",
    },
)

SAFETY_GATE_DESIGN_REQUIREMENTS = (
    "A future implementation gate must name the exact capability being requested.",
    "A future implementation gate must keep all unapproved forbidden capabilities locked false.",
    "Rejected scenarios must prove they do not reach adapters, brokers, runners, workers, or execution paths.",
    "Any live-device, SSH, NETCONF, RESTCONF, provider/API/model, secret, frontend API, backup, or VRRP execution path requires separate explicit approval.",
    "Reviewer evidence must include a no-execution proof and machine-readable PASS/WARN/FAIL/BLOCKED/LOCKED status fields.",
    "Approval cannot be inferred from Phase 2B-00, Phase 2B-00A, or this Phase 2B-01 planning artifact.",
)

FUTURE_IMPLEMENTATION_PREREQUISITES = (
    "Explicit owner authorization for Phase 2B implementation using approved wording.",
    "Approved scope and non-scope that do not narrow Phase 2B to only one example job type.",
    "Dedicated safety gate for each proposed capability upgrade.",
    "Threat/safety review for any execution-adjacent design.",
    "Negative tests showing blocked inputs do not reach execution paths.",
    "Reviewer-visible rollback and stop process.",
    "Secret-handling policy and public-documentation review before any credential-adjacent work.",
    "Validation plan that does not require live devices unless separately approved.",
)

STOP_CONDITIONS = (
    "AGENTS.md was not read before changes.",
    "Scope is narrowed to only one example job type.",
    "The task attempts to implement Phase 2B rather than design planning scope.",
    "The task authorizes Phase 2B implementation or Phase 2B-01 as implementation.",
    "Any runner, adapter, broker, scheduler, queue worker, execution, SSH, NETCONF, RESTCONF, live-device, provider/API/model, secret, frontend API, backup, VRRP execution, device mutation, approval bypass, or safety-gate weakening path is added.",
    "Rejected scenarios can reach an adapter, broker, runner, worker, or execution path.",
    "A future artifact changes implementation, runner, adapter, or execution permission to allowed without a separate explicit gate.",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_01_allowed_as_implementation": False,
    "phase_2b_implementation_started": False,
    "implementation_allowed": False,
    "runner_allowed": False,
    "adapter_allowed": False,
    "execution_allowed": False,
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
    "phase_2b_00a_planning_only_owner_authorization_statement",
    "phase_2b_00a_planning_only_owner_authorization_statement_doc",
    "phase_2b_00a_planning_only_owner_authorization_statement_test",
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

TRACEABILITY_ARTIFACTS = (
    {"artifact_id": "AGENTS.md", "source": "AGENTS.md", "relevance": "Repository safety and validation instructions."},
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review",
        "source": "phase_2b_00_authorization_scope_gate_review.py",
        "relevance": "Phase 2B-00 authorization and scope gate baseline.",
    },
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review_doc",
        "source": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
        "relevance": "Reviewer-facing Phase 2B-00 decision record.",
    },
    {
        "artifact_id": "phase_2b_00_authorization_scope_gate_review_test",
        "source": "tests/test_phase_2b_00_authorization_scope_gate_review.py",
        "relevance": "Negative tests for the Phase 2B-00 boundary.",
    },
    {
        "artifact_id": "phase_2b_00a_planning_only_owner_authorization_statement",
        "source": "phase_2b_00a_planning_only_owner_authorization_statement.py",
        "relevance": "Owner authorization for Phase 2B planning-only work.",
    },
    {
        "artifact_id": "phase_2b_00a_planning_only_owner_authorization_statement_doc",
        "source": "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
        "relevance": "Reviewer-facing Phase 2B planning-only authorization record.",
    },
    {
        "artifact_id": "phase_2b_00a_planning_only_owner_authorization_statement_test",
        "source": "tests/test_phase_2b_00a_planning_only_owner_authorization_statement.py",
        "relevance": "Negative tests proving planning-only authorization does not permit implementation.",
    },
    {
        "artifact_id": "phase2a_readonly_job_runner_framework",
        "source": "phase2a_readonly_job_runner_framework.py",
        "doc": "docs/phase2a_readonly_job_runner_framework.md",
        "relevance": "Phase 2A-02 no-execution validator baseline.",
    },
    {
        "artifact_id": "phase_2a_03_dry_run_job_plan_gate",
        "source": "phase_2a_03_dry_run_job_plan_gate.py",
        "doc": "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
        "relevance": "Dry-run job plan gate and no-execution proof.",
    },
    {
        "artifact_id": "phase_2a_04_plan_evidence_ledger",
        "source": "phase_2a_04_plan_evidence_ledger.py",
        "doc": "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
        "relevance": "Plan evidence traceability ledger.",
    },
    {
        "artifact_id": "phase_2a_05_dry_run_result_envelope_renderer",
        "source": "phase_2a_05_dry_run_result_envelope_renderer.py",
        "doc": "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
        "relevance": "Dry-run result envelope shape.",
    },
    {
        "artifact_id": "phase_2a_06_negative_regression_matrix",
        "source": "phase_2a_06_negative_regression_matrix.py",
        "doc": "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
        "relevance": "Negative safety regression matrix.",
    },
    {
        "artifact_id": "phase_2a_07_vrrp_dry_run_validation_pack",
        "source": "phase_2a_07_vrrp_dry_run_validation_pack.py",
        "doc": "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
        "relevance": "VRRP dry-run example; still only one example job type.",
    },
    {
        "artifact_id": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
        "source": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
        "doc": "docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
        "relevance": "Required multi-job example catalog.",
    },
    {
        "artifact_id": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
        "source": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
        "doc": "docs/phase_2a/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md",
        "relevance": "Mock screen readiness without frontend API integration.",
    },
    {
        "artifact_id": "phase_2a_10_safe_boundary_implementation_readiness_artifact",
        "source": "phase_2a_10_safe_boundary_implementation_readiness_artifact.py",
        "doc": "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
        "relevance": "Safe-boundary implementation readiness while implementation remains locked.",
    },
    {
        "artifact_id": "phase_2a_11_phase_closure_final_readiness_review",
        "source": "phase_2a_11_phase_closure_final_readiness_review.py",
        "doc": "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
        "relevance": "Phase 2A closure readiness review.",
    },
    {
        "artifact_id": "next_phase_authorization_criteria_pack",
        "source": "docs/phase_2a/next_phase_authorization_criteria_pack.md",
        "doc": "docs/phase_2a/next_phase_authorization_criteria_pack.md",
        "relevance": "Authorization criteria and stop conditions for future phase work.",
    },
)

COMPLETION_MARKERS = (
    "PHASE_2B_01_PLANNING_SCOPE_DESIGN_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "PHASE_2B_PLANNING_ONLY_AUTHORIZED_TRUE",
    "PHASE_2B_IMPLEMENTATION_ALLOWED_FALSE",
    "PHASE_2B_01_ALLOWED_AS_IMPLEMENTATION_FALSE",
    "RUNNER_ALLOWED_FALSE",
    "ADAPTER_ALLOWED_FALSE",
    "EXECUTION_ALLOWED_FALSE",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_CAPABILITIES_ENABLED_FALSE",
    "CONCEPTUAL_ARCHITECTURE_ONLY",
    "FUTURE_IMPLEMENTATION_REQUIRES_SEPARATE_GATE",
)


def _forbidden_capability_matrix() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_01": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _traceability_rows() -> Tuple[Dict[str, Any], ...]:
    phase_2b_00 = build_phase_2b_00_authorization_scope_gate_review_report()
    phase_2b_00a = build_phase_2b_00a_planning_only_owner_authorization_statement_report()
    status_by_id = {
        "AGENTS.md": "READ_BEFORE_CHANGES",
        "phase_2b_00_authorization_scope_gate_review": phase_2b_00.get("status", "UNKNOWN"),
        "phase_2b_00a_planning_only_owner_authorization_statement": phase_2b_00a.get("status", "UNKNOWN"),
        "next_phase_authorization_criteria_pack": "CRITERIA_ONLY",
    }
    return tuple(
        {
            **deepcopy(artifact),
            "reviewed": True,
            "source_status": status_by_id.get(str(artifact["artifact_id"]), "REFERENCED"),
        }
        for artifact in TRACEABILITY_ARTIFACTS
    )


def validate_phase_2b_01_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []

    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
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
        "AUTHORIZED_SCOPE",
        "EXAMPLE_JOB_TYPES",
        "FORBIDDEN_SCOPE",
        "EXISTING_ARTIFACTS_TO_REFERENCE",
        "IMPLEMENTATION_BOUNDARY",
        "STOP_CONDITIONS",
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

    if set(report.get("authorized_scope", [])) != set(AUTHORIZED_SCOPE):
        errors.append("AUTHORIZED_SCOPE_MISMATCH")
    if set(report.get("implementation_boundary", [])) != set(IMPLEMENTATION_BOUNDARY):
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")
    if set(report.get("planning_artifacts_allowed", [])) != set(PLANNING_ARTIFACTS_ALLOWED):
        errors.append("PLANNING_ARTIFACTS_ALLOWED_MISMATCH")

    concepts = report.get("conceptual_architecture_boundaries", [])
    if not isinstance(concepts, Sequence) or isinstance(concepts, (str, bytes, bytearray)):
        errors.append("CONCEPTUAL_ARCHITECTURE_NOT_LIST")
        concepts = []
    if len(concepts) != len(CONCEPTUAL_ARCHITECTURE_BOUNDARIES):
        errors.append("CONCEPTUAL_ARCHITECTURE_COUNT_MISMATCH")
    for item in concepts:
        if not isinstance(item, Mapping):
            errors.append("CONCEPTUAL_ARCHITECTURE_ITEM_NOT_OBJECT")
            continue
        if item.get("allowed_now") != "concept_only":
            errors.append(f"CONCEPT_NOT_CONCEPT_ONLY:{item.get('concept')}")
        if item.get("executable") is not False:
            errors.append(f"CONCEPT_EXECUTABLE:{item.get('concept')}")
        if item.get("implementation_allowed") is not False:
            errors.append(f"CONCEPT_IMPLEMENTATION_ALLOWED:{item.get('concept')}")

    matrix = report.get("forbidden_capability_matrix", [])
    matrix_names = {str(item.get("capability")) for item in matrix if isinstance(item, Mapping)}
    if matrix_names != set(FORBIDDEN_CAPABILITIES):
        errors.append("FORBIDDEN_CAPABILITY_MATRIX_MISMATCH")
    for item in matrix if isinstance(matrix, Sequence) else ():
        if not isinstance(item, Mapping):
            errors.append("FORBIDDEN_CAPABILITY_ITEM_NOT_OBJECT")
            continue
        if item.get("enabled") is not False or item.get("allowed_by_phase_2b_01") is not False:
            errors.append(f"FORBIDDEN_CAPABILITY_ENABLED:{item.get('capability')}")

    traceability = report.get("traceability_to_existing_artifacts", [])
    trace_ids = {str(item.get("artifact_id")) for item in traceability if isinstance(item, Mapping)}
    if trace_ids != set(TRACEABILITY_ARTIFACT_IDS):
        errors.append("TRACEABILITY_ARTIFACT_SET_MISMATCH")
    if any(item.get("reviewed") is not True for item in traceability if isinstance(item, Mapping)):
        errors.append("TRACEABILITY_NOT_FULLY_REVIEWED")

    for field_name in (
        "safety_gate_design_requirements",
        "future_implementation_prerequisites",
        "stop_conditions",
    ):
        if not report.get(field_name):
            errors.append(f"{field_name.upper()}_MISSING")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    verdict = report.get("machine_readable_verdict", {})
    if not isinstance(verdict, Mapping):
        errors.append("MACHINE_READABLE_VERDICT_NOT_OBJECT")
        verdict = {}
    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "RUNNER_ALLOWED": "NO",
        "ADAPTER_ALLOWED": "NO",
        "EXECUTION_ALLOWED": "NO",
    }
    if verdict != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "forbidden_capabilities_checked": len(matrix_names),
        "traceability_artifacts_checked": len(trace_ids),
        "conceptual_boundaries_checked": len(concepts),
    }


def build_phase_2b_01_planning_scope_design_only_report() -> Dict[str, Any]:
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
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_changes": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": {
            "PHASE_GOAL": (
                "Define what Phase 2B is intended to design while keeping implementation, "
                "execution, adapters, runners, brokers, live-device access, providers/APIs/models, "
                "secrets, frontend integration, backup, VRRP execution, mutation, approval bypass, "
                "and safety-gate weakening forbidden."
            ),
            "AUTHORIZED_SCOPE": list(AUTHORIZED_SCOPE),
            "EXAMPLE_JOB_TYPES": list(REQUIRED_JOB_TYPES),
            "FORBIDDEN_SCOPE": list(FORBIDDEN_CAPABILITIES),
            "EXISTING_ARTIFACTS_TO_REFERENCE": list(TRACEABILITY_ARTIFACT_IDS),
            "IMPLEMENTATION_BOUNDARY": list(IMPLEMENTATION_BOUNDARY),
            "STOP_CONDITIONS": list(STOP_CONDITIONS),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "authorized_scope": list(AUTHORIZED_SCOPE),
        "planning_artifacts_allowed": list(PLANNING_ARTIFACTS_ALLOWED),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "implementation_prohibition": {
            "phase_2b_implementation_allowed": False,
            "phase_2b_01_allowed_as_implementation": False,
            "runner_allowed": False,
            "adapter_allowed": False,
            "execution_allowed": False,
        },
        "forbidden_capability_matrix": list(_forbidden_capability_matrix()),
        "conceptual_architecture_boundaries": [deepcopy(item) for item in CONCEPTUAL_ARCHITECTURE_BOUNDARIES],
        "safety_gate_design_requirements": list(SAFETY_GATE_DESIGN_REQUIREMENTS),
        "future_implementation_prerequisites": list(FUTURE_IMPLEMENTATION_PREREQUISITES),
        "stop_conditions": list(STOP_CONDITIONS),
        "traceability_to_existing_artifacts": list(traceability),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "RUNNER_ALLOWED": "NO",
            "ADAPTER_ALLOWED": "NO",
            "EXECUTION_ALLOWED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "phase_2b_planning_only_authorized": True,
            "phase_2b_implementation_allowed": False,
            "phase_2b_01_allowed_as_implementation": False,
            "runner_allowed": False,
            "adapter_allowed": False,
            "execution_allowed": False,
            "example_job_types_checked": len(REQUIRED_JOB_TYPES),
            "forbidden_capabilities_enabled": 0,
            "conceptual_architecture_boundaries": len(CONCEPTUAL_ARCHITECTURE_BOUNDARIES),
            "traceability_artifacts_checked": len(traceability),
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_01_report(report)
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
        f"<td>{html.escape(str(item['allowed_by_phase_2b_01']))}</td>"
        f"<td>{html.escape(str(item['status']))}</td>"
        "</tr>"
        for item in report["forbidden_capability_matrix"]
    )


def _concept_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['concept']))}</td>"
        f"<td>{html.escape(str(item['allowed_now']))}</td>"
        f"<td>{html.escape(str(item['executable']))}</td>"
        f"<td>{html.escape(str(item['implementation_allowed']))}</td>"
        f"<td>{html.escape(str(item['boundary']))}</td>"
        "</tr>"
        for item in report["conceptual_architecture_boundaries"]
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
    code {{ background: #f4f6f8; padding: 0.1rem 0.25rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: <strong>{html.escape(str(report["status"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>This artifact is planning and scope design only. It does not authorize implementation or execution.</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Authorized Scope</h2>
  <ul>{_list_items(report["authorized_scope"])}</ul>
  <h2>Conceptual Architecture Boundaries</h2>
  <table>
    <thead><tr><th>Concept</th><th>Allowed now</th><th>Executable</th><th>Implementation allowed</th><th>Boundary</th></tr></thead>
    <tbody>{_concept_rows(report)}</tbody>
  </table>
  <h2>Forbidden Capabilities</h2>
  <table>
    <thead><tr><th>Capability</th><th>Enabled</th><th>Allowed by Phase 2B-01</th><th>Status</th></tr></thead>
    <tbody>{_forbidden_rows(report)}</tbody>
  </table>
  <h2>Safety Gate Design Requirements</h2>
  <ul>{_list_items(report["safety_gate_design_requirements"])}</ul>
  <h2>Future Implementation Prerequisites</h2>
  <ul>{_list_items(report["future_implementation_prerequisites"])}</ul>
  <h2>Stop Conditions</h2>
  <ul>{_list_items(report["stop_conditions"])}</ul>
  <h2>Traceability</h2>
  <table>
    <thead><tr><th>Artifact</th><th>Source</th><th>Status</th><th>Reviewed</th></tr></thead>
    <tbody>{_traceability_rows_html(report)}</tbody>
  </table>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_01_planning_scope_design_only_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_01_planning_scope_design_only_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_01_planning_scope_design_only(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_01_planning_scope_design_only_report()
    json_path, html_path = write_phase_2b_01_planning_scope_design_only_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"phase_2b_planning_only_authorized: {str(report['phase_2b_planning_only_authorized']).lower()}")
    print(f"phase_2b_implementation_allowed: {str(report['phase_2b_implementation_allowed']).lower()}")
    print(f"phase_2b_01_allowed_as_implementation: {str(report['phase_2b_01_allowed_as_implementation']).lower()}")
    print(f"runner_allowed: {str(report['runner_allowed']).lower()}")
    print(f"adapter_allowed: {str(report['adapter_allowed']).lower()}")
    print(f"execution_allowed: {str(report['execution_allowed']).lower()}")
    print(f"Example job types checked: {report['summary']['example_job_types_checked']}")
    print(f"Forbidden capabilities enabled: {report['summary']['forbidden_capabilities_enabled']}")
    print(f"Conceptual architecture boundaries: {report['summary']['conceptual_architecture_boundaries']}")
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
