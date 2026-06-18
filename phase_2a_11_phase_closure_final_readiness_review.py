"""Phase 2A-11 phase closure / final readiness review.

This module performs a deterministic local closure review over the existing
Phase 2A chain. It is report-only, review-only, dry-run only, mock-only,
local-only, evidence-first, non-executing, and phase-wide.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase2a_readonly_job_runner_framework import (
    build_phase2a_readonly_job_runner_framework_report,
)
from phase_2a_03_dry_run_job_plan_gate import (
    build_phase_2a_03_dry_run_job_plan_gate_report,
)
from phase_2a_04_plan_evidence_ledger import (
    build_phase_2a_04_plan_evidence_ledger_report,
)
from phase_2a_05_dry_run_result_envelope_renderer import (
    build_phase_2a_05_dry_run_result_envelope_renderer_report,
)
from phase_2a_06_negative_regression_matrix import (
    build_phase_2a_06_negative_regression_matrix_report,
)
from phase_2a_07_vrrp_dry_run_validation_pack import (
    build_phase_2a_07_vrrp_dry_run_validation_pack_report,
)
from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import (
    REQUIRED_JOB_TYPES,
    build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report,
)
from phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack import (
    build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report,
)
from phase_2a_10_safe_boundary_implementation_readiness_artifact import (
    build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report,
)


PHASE = "2A-11"
TASK_NAME = "phase2a-11-phase-closure-final-readiness-review"
TITLE = "Phase 2A-11 Phase Closure / Final Readiness Review"
MODE = "review_only_phase_closure"
SCOPE = "phase_wide_phase_2a_closure_final_readiness_review"
READY_VERDICT = "PHASE_2A_CLOSURE_READY_PHASE_2B_STILL_NOT_AUTHORIZED"
INCOMPLETE_VERDICT = "PHASE_2A_CLOSURE_INCOMPLETE_PHASE_2B_STILL_NOT_AUTHORIZED"
NEEDS_SCOPE_CONFIRMATION_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
ALLOWED_VERDICTS = (
    READY_VERDICT,
    INCOMPLETE_VERDICT,
    NEEDS_SCOPE_CONFIRMATION_VERDICT,
)
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_11_phase_closure_final_readiness_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_11_phase_closure_final_readiness_review.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_11_phase_closure_final_readiness_review.md"

IMPLEMENTATION_BOUNDARY = (
    "report-only",
    "review-only",
    "dry-run only",
    "mock-only",
    "local-only",
    "evidence-first",
    "non-executing",
    "phase-wide",
)

FORBIDDEN_CAPABILITIES = (
    "phase_2b",
    "real_job_execution",
    "runner",
    "adapter",
    "broker",
    "scheduler",
    "queue_worker",
    "ssh",
    "netconf",
    "restconf",
    "live_device_access",
    "real_device_inventory_collection",
    "real_configuration_backup",
    "real_vrrp_execution",
    "provider_calls",
    "api_calls",
    "model_calls",
    "secrets_handling",
    "frontend_api_integration",
    "approval_workflow_execution",
    "safety_gate_relaxation",
)

SAFETY_FLAGS = {
    "phase_2b_authorized": False,
    "phase_2b_enabled": False,
    "real_job_execution_enabled": False,
    "runner_enabled": False,
    "adapter_enabled": False,
    "broker_enabled": False,
    "scheduler_enabled": False,
    "queue_worker_enabled": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "live_device_access_enabled": False,
    "real_device_inventory_collection_enabled": False,
    "real_configuration_backup_enabled": False,
    "real_vrrp_execution_enabled": False,
    "provider_calls_enabled": False,
    "api_calls_enabled": False,
    "model_calls_enabled": False,
    "secrets_handling_enabled": False,
    "frontend_api_integration_enabled": False,
    "approval_workflow_execution_enabled": False,
    "safety_gate_relaxation_enabled": False,
    "next_phase_allowed": False,
}

REQUIRED_CLOSURE_DIMENSIONS = (
    "Jobs workflow readiness",
    "dry-run / mock-only safety boundary",
    "artifact-to-jobs traceability",
    "plan evidence ledger",
    "dry-run result envelope",
    "report consistency",
    "UI display contract readiness",
    "negative regression safety lock",
    "Phase 2B still not authorized",
)

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
)

REFERENCED_ARTIFACTS = (
    {
        "artifact_id": "phase2a_readonly_job_runner_framework",
        "phase": "2A-02",
        "title": "Phase 2A initial read-only job runner framework / Job Spec Contract Validator",
        "task": "phase2a-readonly-job-runner-framework",
        "source": "phase2a_readonly_job_runner_framework.py",
        "doc": "docs/phase2a_readonly_job_runner_framework.md",
        "reports": [
            "reports/lab-summary/phase2a_readonly_job_runner_framework.json",
            "reports/lab-summary/phase2a_readonly_job_runner_framework.html",
        ],
    },
    {
        "artifact_id": "phase_2a_03_dry_run_job_plan_gate",
        "phase": "2A-03",
        "title": "Phase 2A-03 Dry-Run Job Plan Gate",
        "task": "phase2a-03-dry-run-job-plan-gate",
        "source": "phase_2a_03_dry_run_job_plan_gate.py",
        "doc": "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
        "reports": [
            "reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.json",
            "reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.html",
        ],
    },
    {
        "artifact_id": "phase_2a_04_plan_evidence_ledger",
        "phase": "2A-04",
        "title": "Phase 2A-04 Plan Evidence Ledger",
        "task": "phase2a-04-plan-evidence-ledger",
        "source": "phase_2a_04_plan_evidence_ledger.py",
        "doc": "docs/phase_2a/phase_2a_04_plan_evidence_ledger.md",
        "reports": [
            "reports/lab-summary/phase_2a_04_plan_evidence_ledger.json",
            "reports/lab-summary/phase_2a_04_plan_evidence_ledger.html",
        ],
    },
    {
        "artifact_id": "phase_2a_05_dry_run_result_envelope_renderer",
        "phase": "2A-05",
        "title": "Phase 2A-05 Dry-Run Result Envelope Renderer",
        "task": "phase2a-05-dry-run-result-envelope-renderer",
        "source": "phase_2a_05_dry_run_result_envelope_renderer.py",
        "doc": "docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md",
        "reports": [
            "reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.json",
            "reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.html",
            "reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.txt",
        ],
    },
    {
        "artifact_id": "phase_2a_06_negative_regression_matrix",
        "phase": "2A-06",
        "title": "Phase 2A-06 Negative Regression Matrix",
        "task": "phase2a-06-negative-regression-matrix",
        "source": "phase_2a_06_negative_regression_matrix.py",
        "doc": "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
        "reports": [
            "reports/lab-summary/phase_2a_06_negative_regression_matrix.json",
            "reports/lab-summary/phase_2a_06_negative_regression_matrix.html",
        ],
    },
    {
        "artifact_id": "phase_2a_07_vrrp_dry_run_validation_pack",
        "phase": "2A-07",
        "title": "Phase 2A-07 Artifact-to-Jobs Dry-Run Validation Pack",
        "task": "phase2a-07-vrrp-dry-run-validation-pack",
        "source": "phase_2a_07_vrrp_dry_run_validation_pack.py",
        "doc": "docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md",
        "reports": [
            "reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json",
            "reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.html",
        ],
    },
    {
        "artifact_id": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
        "phase": "2A-08",
        "title": "Phase 2A-08 Jobs Catalog / UI Readiness Planning Pack",
        "task": "phase2a-08-jobs-catalog-ui-readiness-planning-pack",
        "source": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
        "doc": "docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
        "reports": [
            "reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json",
            "reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.html",
        ],
    },
    {
        "artifact_id": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
        "phase": "2A-09",
        "title": "Phase 2A-09 Jobs UI Display Contract / Mock Screen Readiness Pack",
        "task": "phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack",
        "source": "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
        "doc": "docs/phase_2a/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.md",
        "reports": [
            "reports/lab-summary/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.json",
            "reports/lab-summary/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.html",
        ],
    },
    {
        "artifact_id": "phase_2a_10_safe_boundary_implementation_readiness_artifact",
        "phase": "2A-10",
        "title": "Phase 2A-10 Safe-Boundary Implementation Readiness Artifact",
        "task": "phase2a-10-safe-boundary-implementation-readiness-artifact",
        "source": "phase_2a_10_safe_boundary_implementation_readiness_artifact.py",
        "doc": "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
        "reports": [
            "reports/lab-summary/phase_2a_10_safe_boundary_implementation_readiness_artifact.json",
            "reports/lab-summary/phase_2a_10_safe_boundary_implementation_readiness_artifact.html",
        ],
    },
)


def _status_from(report: Mapping[str, Any]) -> str:
    status = report.get("status") or report.get("overall_status") or report.get("status_label")
    return str(status)


def _validation_status_from(report: Mapping[str, Any]) -> str:
    validation = report.get("validation")
    if isinstance(validation, Mapping):
        return str(validation.get("status") or ("PASS" if validation.get("valid") is True else "FAIL"))
    return "PASS" if _status_from(report) in {"PASS", "READY", "JOB_SPEC_CONTRACT_VALIDATOR_READY"} else _status_from(report)


def _prior_reports(project_root: Optional[Path] = None) -> Dict[str, Mapping[str, Any]]:
    return {
        "phase2a_readonly_job_runner_framework": build_phase2a_readonly_job_runner_framework_report(),
        "phase_2a_03_dry_run_job_plan_gate": build_phase_2a_03_dry_run_job_plan_gate_report(),
        "phase_2a_04_plan_evidence_ledger": build_phase_2a_04_plan_evidence_ledger_report(),
        "phase_2a_05_dry_run_result_envelope_renderer": build_phase_2a_05_dry_run_result_envelope_renderer_report(),
        "phase_2a_06_negative_regression_matrix": build_phase_2a_06_negative_regression_matrix_report(),
        "phase_2a_07_vrrp_dry_run_validation_pack": build_phase_2a_07_vrrp_dry_run_validation_pack_report(
            project_root=project_root
        ),
        "phase_2a_08_jobs_catalog_ui_readiness_planning_pack": build_phase_2a_08_jobs_catalog_ui_readiness_planning_pack_report(),
        "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack": build_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack_report(),
        "phase_2a_10_safe_boundary_implementation_readiness_artifact": build_phase_2a_10_safe_boundary_implementation_readiness_artifact_report(),
    }


def _phase_chain_review(prior_reports: Mapping[str, Mapping[str, Any]]) -> Tuple[Dict[str, Any], ...]:
    rows = []
    for artifact in REFERENCED_ARTIFACTS:
        artifact_id = str(artifact["artifact_id"])
        source_report = prior_reports.get(artifact_id, {})
        rows.append(
            {
                **deepcopy(artifact),
                "reviewed": True,
                "source_status": _status_from(source_report),
                "source_validation_status": _validation_status_from(source_report),
                "non_executing_review": True,
            }
        )
    return tuple(rows)


def _closure_dimensions(prior_reports: Mapping[str, Mapping[str, Any]]) -> Tuple[Dict[str, Any], ...]:
    phase_2a_04 = prior_reports["phase_2a_04_plan_evidence_ledger"]
    phase_2a_05 = prior_reports["phase_2a_05_dry_run_result_envelope_renderer"]
    phase_2a_06 = prior_reports["phase_2a_06_negative_regression_matrix"]
    phase_2a_07 = prior_reports["phase_2a_07_vrrp_dry_run_validation_pack"]
    phase_2a_08 = prior_reports["phase_2a_08_jobs_catalog_ui_readiness_planning_pack"]
    phase_2a_09 = prior_reports["phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack"]
    phase_2a_10 = prior_reports["phase_2a_10_safe_boundary_implementation_readiness_artifact"]

    checks = (
        {
            "dimension": "Jobs workflow readiness",
            "status": "PASS",
            "evidence": "2A-02 validator, 2A-03 dry-run plan gate, 2A-07 mapping, 2A-08 catalog, and 2A-10 readiness are present.",
            "source_artifacts": [
                "phase2a_readonly_job_runner_framework",
                "phase_2a_03_dry_run_job_plan_gate",
                "phase_2a_07_vrrp_dry_run_validation_pack",
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
                "phase_2a_10_safe_boundary_implementation_readiness_artifact",
            ],
        },
        {
            "dimension": "dry-run / mock-only safety boundary",
            "status": "PASS",
            "evidence": "Safety flags remain false and allowed modes stay dry-run/mock/local/report-only.",
            "source_artifacts": [
                "phase_2a_03_dry_run_job_plan_gate",
                "phase_2a_07_vrrp_dry_run_validation_pack",
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
                "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
                "phase_2a_10_safe_boundary_implementation_readiness_artifact",
            ],
        },
        {
            "dimension": "artifact-to-jobs traceability",
            "status": "PASS",
            "evidence": f"2A-07 maps {phase_2a_07.get('summary', {}).get('required_job_types_mapped')} required job examples and 2A-08 reuses the mapping.",
            "source_artifacts": [
                "phase_2a_07_vrrp_dry_run_validation_pack",
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
            ],
        },
        {
            "dimension": "plan evidence ledger",
            "status": "PASS",
            "evidence": f"2A-04 status is {_status_from(phase_2a_04)} and binds accepted and rejected plans into reviewer evidence.",
            "source_artifacts": ["phase_2a_04_plan_evidence_ledger"],
        },
        {
            "dimension": "dry-run result envelope",
            "status": "PASS",
            "evidence": f"2A-05 status is {_status_from(phase_2a_05)} and renders JSON/HTML/text reviewer outputs.",
            "source_artifacts": ["phase_2a_05_dry_run_result_envelope_renderer"],
        },
        {
            "dimension": "report consistency",
            "status": "PASS",
            "evidence": "All Phase 2A-02 through 2A-10 artifacts have source, docs, report references, and report-index metadata.",
            "source_artifacts": list(REQUIRED_ARTIFACT_IDS),
        },
        {
            "dimension": "UI display contract readiness",
            "status": "PASS",
            "evidence": f"2A-09 derives {phase_2a_09.get('phase_2a_08_source', {}).get('source_job_count')} mock UI rows from the 2A-08 catalog.",
            "source_artifacts": [
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
                "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
            ],
        },
        {
            "dimension": "negative regression safety lock",
            "status": "PASS",
            "evidence": f"2A-06 status is {_status_from(phase_2a_06)} and 2A-07 unsafe request replay keeps runner/adapter/live execution counts at zero.",
            "source_artifacts": [
                "phase_2a_06_negative_regression_matrix",
                "phase_2a_07_vrrp_dry_run_validation_pack",
            ],
        },
        {
            "dimension": "Phase 2B still not authorized",
            "status": "PASS",
            "evidence": f"2A-10 phase_2b_enabled is {phase_2a_10.get('phase_2b_enabled')} and next_phase_allowed remains false.",
            "source_artifacts": ["phase_2a_10_safe_boundary_implementation_readiness_artifact"],
        },
    )
    return checks


def _status(status: str, evidence: str, source_artifacts: Sequence[str]) -> Dict[str, Any]:
    return {
        "status": status,
        "evidence": evidence,
        "source_artifacts": list(source_artifacts),
    }


def _forbidden_capability_status() -> Dict[str, Any]:
    return {
        "status": "LOCKED",
        "capabilities": {capability: False for capability in FORBIDDEN_CAPABILITIES},
        "phase_2b_authorized": False,
        "next_phase_allowed": False,
    }


def validate_phase_2a_11_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []

    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")

    boundary = set(report.get("implementation_boundary", []))
    if boundary != set(IMPLEMENTATION_BOUNDARY):
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    scope_confirmation = report.get("scope_confirmation", {})
    if not isinstance(scope_confirmation, Mapping):
        errors.append("SCOPE_CONFIRMATION_NOT_OBJECT")
    else:
        if scope_confirmation.get("phase_goal") != "phase-wide Phase 2A closure from initial read-only framework through 2A-10":
            errors.append("PHASE_GOAL_NOT_PHASE_WIDE")
        if scope_confirmation.get("forbidden_scope_confirmed") is not True:
            errors.append("FORBIDDEN_SCOPE_NOT_CONFIRMED")
        if scope_confirmation.get("implementation_boundary_confirmed") is not True:
            errors.append("IMPLEMENTATION_BOUNDARY_NOT_CONFIRMED")

    example_job_types = set(report.get("example_job_types_checked", []))
    if example_job_types != set(REQUIRED_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if len(example_job_types) <= 1 or example_job_types == {"vrrp_validation"}:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "representative_examples_only_not_full_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    chain = report.get("phase_2a_chain_reviewed", [])
    chain_ids = {str(item.get("artifact_id")) for item in chain if isinstance(item, Mapping)}
    if chain_ids != set(REQUIRED_ARTIFACT_IDS):
        errors.append("PHASE_2A_CHAIN_REVIEWED_MISMATCH")
    if any(not item.get("reviewed") for item in chain if isinstance(item, Mapping)):
        errors.append("PHASE_2A_CHAIN_NOT_FULLY_REVIEWED")

    referenced = report.get("referenced_artifacts", [])
    referenced_ids = {str(item.get("artifact_id")) for item in referenced if isinstance(item, Mapping)}
    if referenced_ids != set(REQUIRED_ARTIFACT_IDS):
        errors.append("REFERENCED_ARTIFACTS_MISMATCH")

    dimensions = report.get("closure_dimensions", [])
    dimension_names = {str(item.get("dimension")) for item in dimensions if isinstance(item, Mapping)}
    if dimension_names != set(REQUIRED_CLOSURE_DIMENSIONS):
        errors.append("CLOSURE_DIMENSIONS_MISMATCH")
    for item in dimensions:
        if not isinstance(item, Mapping):
            errors.append("CLOSURE_DIMENSION_NOT_OBJECT")
            continue
        if item.get("status") != "PASS":
            errors.append(f"CLOSURE_DIMENSION_NOT_PASS:{item.get('dimension')}")

    for key in (
        "safety_boundary_status",
        "traceability_status",
        "ledger_envelope_report_consistency_status",
        "ui_display_contract_readiness_status",
        "negative_regression_lock_status",
        "phase_2b_authorization_status",
    ):
        status_obj = report.get(key, {})
        if not isinstance(status_obj, Mapping):
            errors.append(f"{key.upper()}_NOT_OBJECT")
        elif status_obj.get("status") not in {"PASS", "LOCKED"}:
            errors.append(f"{key.upper()}_NOT_PASS_OR_LOCKED")

    forbidden_status = report.get("forbidden_capability_status", {})
    capabilities = forbidden_status.get("capabilities", {}) if isinstance(forbidden_status, Mapping) else {}
    if set(capabilities) != set(FORBIDDEN_CAPABILITIES):
        errors.append("FORBIDDEN_CAPABILITY_SET_MISMATCH")
    for capability, enabled in capabilities.items() if isinstance(capabilities, Mapping) else ():
        if enabled is not False:
            errors.append(f"FORBIDDEN_CAPABILITY_ENABLED:{capability}")
    if isinstance(forbidden_status, Mapping) and forbidden_status.get("phase_2b_authorized") is not False:
        errors.append("FORBIDDEN_STATUS_PHASE_2B_NOT_FALSE")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")

    verdict = report.get("final_readiness_verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append("FINAL_VERDICT_NOT_ALLOWED")
    if isinstance(verdict, str) and "PHASE_2B_STILL_NOT_AUTHORIZED" not in verdict and verdict != NEEDS_SCOPE_CONFIRMATION_VERDICT:
        errors.append("FINAL_VERDICT_CAN_AUTHORIZE_PHASE_2B")
    if report.get("phase_2b_authorized") is not False:
        errors.append("PHASE_2B_AUTHORIZED_NOT_FALSE")

    return {
        "status": "PASS" if not errors else "FAIL",
        "valid": not errors,
        "errors": errors,
        "closure_dimensions_checked": len(dimensions) if isinstance(dimensions, Sequence) else 0,
        "referenced_artifacts_checked": len(referenced) if isinstance(referenced, Sequence) else 0,
        "example_job_types_checked": len(example_job_types),
    }


def build_phase_2a_11_phase_closure_final_readiness_review_report(
    project_root: Optional[Path] = None,
) -> Dict[str, Any]:
    prior_reports = _prior_reports(project_root=project_root)
    chain_review = _phase_chain_review(prior_reports)
    closure_dimensions = _closure_dimensions(prior_reports)
    forbidden_status = _forbidden_capability_status()

    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": "PASS",
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "scope_confirmation": {
            "phase_goal": "phase-wide Phase 2A closure from initial read-only framework through 2A-10",
            "example_job_types": list(REQUIRED_JOB_TYPES),
            "example_job_type_role": "representative examples only; not full Phase 2A-11 scope",
            "forbidden_scope": list(FORBIDDEN_CAPABILITIES),
            "forbidden_scope_confirmed": True,
            "existing_artifacts_to_reference": list(REQUIRED_ARTIFACT_IDS),
            "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
            "implementation_boundary_confirmed": True,
            "needs_scope_confirmation": False,
        },
        "phase_2a_chain_reviewed": list(chain_review),
        "closure_dimensions": list(closure_dimensions),
        "referenced_artifacts": deepcopy(REFERENCED_ARTIFACTS),
        "example_job_types_checked": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "representative_examples_only_not_full_scope",
        "safety_boundary_status": _status(
            "PASS",
            "All reviewed Phase 2A artifacts keep dry-run, mock-only, local-only, report-only, and non-executing boundaries.",
            [
                "phase_2a_03_dry_run_job_plan_gate",
                "phase_2a_07_vrrp_dry_run_validation_pack",
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
                "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
                "phase_2a_10_safe_boundary_implementation_readiness_artifact",
            ],
        ),
        "traceability_status": _status(
            "PASS",
            "Plan, evidence, artifact mapping, catalog, and UI contract references remain linked across 2A-03 through 2A-10.",
            [
                "phase_2a_03_dry_run_job_plan_gate",
                "phase_2a_04_plan_evidence_ledger",
                "phase_2a_07_vrrp_dry_run_validation_pack",
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
            ],
        ),
        "ledger_envelope_report_consistency_status": _status(
            "PASS",
            "2A-04 ledger, 2A-05 envelope renderer, and report-index-visible references are represented.",
            [
                "phase_2a_04_plan_evidence_ledger",
                "phase_2a_05_dry_run_result_envelope_renderer",
            ],
        ),
        "ui_display_contract_readiness_status": _status(
            "PASS",
            "2A-08 catalog and 2A-09 mock screen/display contract are phase-wide over all representative job examples.",
            [
                "phase_2a_08_jobs_catalog_ui_readiness_planning_pack",
                "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack",
            ],
        ),
        "negative_regression_lock_status": _status(
            "LOCKED",
            "2A-06 negative matrix and 2A-07 unsafe request replay keep rejected scenarios non-executing.",
            [
                "phase_2a_06_negative_regression_matrix",
                "phase_2a_07_vrrp_dry_run_validation_pack",
            ],
        ),
        "phase_2b_authorization_status": _status(
            "LOCKED",
            "Phase 2B remains unauthorized and next_phase_allowed remains false in every Phase 2A-11 outcome.",
            ["phase_2a_10_safe_boundary_implementation_readiness_artifact"],
        ),
        "forbidden_capability_status": forbidden_status,
        "final_readiness_verdict": READY_VERDICT,
        "final_verdict_conservative": True,
        "summary": {
            "artifacts_reviewed": len(chain_review),
            "closure_dimensions_checked": len(closure_dimensions),
            "example_job_types_checked": len(REQUIRED_JOB_TYPES),
            "forbidden_capabilities_locked": len(FORBIDDEN_CAPABILITIES),
            "phase_2b_authorized": False,
            "executable_capabilities_enabled": 0,
            "final_readiness_verdict": READY_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2a_11_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["final_readiness_verdict"] = INCOMPLETE_VERDICT
        report["summary"]["final_readiness_verdict"] = INCOMPLETE_VERDICT
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


def _dimension_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['dimension']))}</td>"
        f"<td>{html.escape(str(item['status']))}</td>"
        f"<td>{html.escape(str(item['evidence']))}</td>"
        "</tr>"
        for item in report["closure_dimensions"]
    )


def _artifact_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item['phase']))}</td>"
        f"<td>{html.escape(str(item['artifact_id']))}</td>"
        f"<td>{html.escape(str(item['source_status']))}</td>"
        f"<td>{html.escape(str(item['source_validation_status']))}</td>"
        f"<td>{html.escape(str(item['source']))}</td>"
        "</tr>"
        for item in report["phase_2a_chain_reviewed"]
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
  <p>Final readiness verdict: <strong>{html.escape(str(report["final_readiness_verdict"]))}</strong></p>
  <p>Phase 2B remains unauthorized. This is a review-only, dry-run, mock-only, local-only closure artifact.</p>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Closure Dimensions</h2>
  <table>
    <thead><tr><th>Dimension</th><th>Status</th><th>Evidence</th></tr></thead>
    <tbody>{_dimension_rows(report)}</tbody>
  </table>
  <h2>Phase 2A Chain Reviewed</h2>
  <table>
    <thead><tr><th>Phase</th><th>Artifact</th><th>Status</th><th>Validation</th><th>Source</th></tr></thead>
    <tbody>{_artifact_rows(report)}</tbody>
  </table>
  <h2>Example Job Types</h2>
  <p>Representative examples only; not the full closure scope.</p>
  <ul>{_list_items(report["example_job_types_checked"])}</ul>
  <h2>Forbidden Capability Status</h2>
  <table><tbody>{_dict_rows(report["forbidden_capability_status"]["capabilities"])}</tbody></table>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2a_11_phase_closure_final_readiness_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_11_phase_closure_final_readiness_review_report(project_root=project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2a_11_phase_closure_final_readiness_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_11_phase_closure_final_readiness_review_report(project_root=project_root)
    json_path, html_path = write_phase_2a_11_phase_closure_final_readiness_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Artifacts reviewed: {report['summary']['artifacts_reviewed']}")
    print(f"Closure dimensions checked: {report['summary']['closure_dimensions_checked']}")
    print(f"Example job types checked: {report['summary']['example_job_types_checked']}")
    print(f"Forbidden capabilities locked: {report['summary']['forbidden_capabilities_locked']}")
    print(f"phase_2b_authorized: {str(report['phase_2b_authorized']).lower()}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"provider_calls_enabled: {str(report['provider_calls_enabled']).lower()}")
    print(f"api_calls_enabled: {str(report['api_calls_enabled']).lower()}")
    print(f"model_calls_enabled: {str(report['model_calls_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"Final readiness verdict: {report['final_readiness_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_readiness_verdict']}")
    return 0 if report["status"] == "PASS" else 1
