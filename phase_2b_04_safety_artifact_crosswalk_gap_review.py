"""Phase 2B-04 safety artifact crosswalk and gap review.

This module creates a deterministic, local, planning-only crosswalk over
existing safety artifacts. It maps coverage and gaps before any future Phase
2B implementation is considered. It does not create a new Day1-Day160 safety
matrix, does not duplicate prior artifacts, and does not enable a runner,
adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device
access, provider/API/model calls, secrets handling, frontend API integration,
real execution, backup, VRRP execution, device mutation, approval bypass, or
safety-gate behavior changes.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_02_safety_gate_design_planning_only import (
    build_phase_2b_02_safety_gate_design_planning_only_report,
)


PHASE = "2B-04"
TASK_NAME = "phase2b-04-safety-artifact-crosswalk-gap-review"
TITLE = "Phase 2B-04 Safety Artifact Crosswalk and Gap Review"
MODE = "planning_only_crosswalk_gap_review"
SCOPE = "phase_wide_phase_2b_safety_artifact_crosswalk_gap_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_04_PLANNING_ONLY_CROSSWALK_GAP_REVIEW_COMPLETE"
BLOCKED_VERDICT = "PHASE_2B_04_PLANNING_ONLY_CROSSWALK_GAP_REVIEW_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_04_safety_artifact_crosswalk_gap_review.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_04_safety_artifact_crosswalk_gap_review.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_04_safety_artifact_crosswalk_gap_review.md"

AUTHORIZED_SCOPE = (
    "documentation-only planning artifact",
    "crosswalk over existing safety artifacts",
    "gap review before future implementation",
    "static registry and report-index visibility",
    "tests proving planning-only behavior",
    "no new Day1-Day160 safety matrix",
)

IMPLEMENTATION_BOUNDARY = (
    "planning-only",
    "documentation-only",
    "report-only deterministic local artifact",
    "static crosswalk and gap review",
    "no safety gate behavior changes",
    "no executable workflow behavior",
    "no live-device hooks",
    "no provider/API/model integration",
    "no secrets or credentials handling",
    "no frontend API integration",
)

NON_DUPLICATION_STATEMENT = (
    "This is not a new Day1-Day160 safety matrix. It is a Phase 2B-04 "
    "crosswalk and gap review that references existing artifacts without "
    "re-implementing or duplicating them."
)

SAFETY_BOUNDARY_STATEMENT = (
    "No implementation, runner, adapter, execution path, live-device "
    "capability, provider/API/model call, secret handling, frontend API "
    "integration, or safety gate behavior change is authorized or enabled."
)

NEXT_STEP_RECOMMENDATION = (
    "Continue planning-only review or stop. Do not start Phase 2B "
    "implementation unless it is separately authorized by a future explicit "
    "owner-approved safety gate."
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "phase_2b_04_allowed_as_implementation": False,
    "implementation_started": False,
    "new_safety_matrix_created": False,
    "crosswalk_created": True,
    "gap_review_created": True,
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

COVERAGE_STATUS_CATEGORIES = (
    "COVERED",
    "PARTIALLY_COVERED",
    "MISSING_DEFERRED",
    "NOT_ALLOWED_CURRENT_PHASE",
)

CROSSWALK_ROWS = (
    {
        "artifact_source": "AGENTS.md",
        "phase_day": "Repository safety instructions",
        "safety_topic_covered": "Core safety rules, validation expectations, no live access, no secrets, and no execution for planning-only work.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "AGENTS.md",
        "notes": "Read before file changes for Phase 2B-04 and not modified.",
    },
    {
        "artifact_source": "Day1-Day40 portfolio, topology, dry-run, and VRRP safety artifacts",
        "phase_day": "Day1-Day40",
        "safety_topic_covered": "Offline review, report-only indexing, staged planning, read-only precheck, dry-run VRRP topology, and manual-observation evidence.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/roadmap/day35_vrrp_failover_validation_safety.md; docs/roadmap/day37_vrrp_report_regression_evidence_policy.md; docs/portfolio_evidence.md",
        "notes": "Existing artifacts remain referenced; Phase 2B-04 does not recreate their safety matrix.",
    },
    {
        "artifact_source": "Intent safety and policy artifacts",
        "phase_day": "Day57-Day60",
        "safety_topic_covered": "Intent mapping, safety review, policy matrix, and reviewer walkthrough without mapped task execution.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/ai/day57_intent_mapping_prototype.md; docs/ai/day59_intent_policy_matrix_reviewer_safety_explanation.md",
        "notes": "Useful as early reviewer-facing no-execution evidence.",
    },
    {
        "artifact_source": "Offline mock runtime and approval chain",
        "phase_day": "Day66-Day87",
        "safety_topic_covered": "Mock-only runtime, dry-run plans, approval envelopes, audit trails, locked safety gates, readonly task contracts, broker review queues, and phase gate review.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/roadmap/day66_offline_mock_runtime_skeleton.md; docs/roadmap/day77_runtime_safety_gate.md; docs/roadmap/day87_readonly_executor_phase_gate_review.md",
        "notes": "Documents reviewer-visible no-execution progression before any real adapter design.",
    },
    {
        "artifact_source": "Real adapter planning and parser hardening artifacts",
        "phase_day": "Day88-Day125",
        "safety_topic_covered": "Design-only real adapter boundary, implementation-entry planning, fake-adapter guardrails, parser evidence, safety boundary regression, invariant helpers, and thin CLI regression.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/ai/intent_real_adapter_safety_boundary_spec.md; docs/ai-intent/day123_safety_boundary_regression_matrix.md; docs/roadmap/day125_thin_cli_regression_gate.md",
        "notes": "Execution-adjacent planning exists, but Phase 2B-04 does not authorize any execution-adjacent implementation.",
    },
    {
        "artifact_source": "AI assistance disabled-provider and closure artifacts",
        "phase_day": "Day127-Day160",
        "safety_topic_covered": "Reviewer-only AI summary contracts, redaction, disabled provider boundaries, docs/report consistency, deferred risks, evidence freeze, safety regression, and phase gate review.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/ai-intent/day135_ai_provider_disabled_by_default_safety_regression.md; docs/ai/day159_v05_ai_assistance_safety_regression_matrix.md; docs/ai/day160_v05_ai_assistance_phase_gate_review.md",
        "notes": "Provider/API/model calls remain disabled and are cross-referenced rather than re-implemented.",
    },
    {
        "artifact_source": "Phase 2A read-only job runner framework",
        "phase_day": "Phase 2A-02",
        "safety_topic_covered": "No-execution framework baseline for read-only job planning.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "phase2a_readonly_job_runner_framework.py; docs/phase2a_readonly_job_runner_framework.md",
        "notes": "Referenced as a prior planning framework, not activated by Phase 2B-04.",
    },
    {
        "artifact_source": "Phase 2A dry-run job plan gate",
        "phase_day": "Phase 2A-03",
        "safety_topic_covered": "Dry-run job plan gate and no-execution proof before any job plan can advance.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "phase_2a_03_dry_run_job_plan_gate.py; docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
        "notes": "Confirms rejected or unsafe plans remain non-executing.",
    },
    {
        "artifact_source": "Phase 2A evidence ledger and result envelope",
        "phase_day": "Phase 2A-04 to Phase 2A-05",
        "safety_topic_covered": "Plan evidence ledger and dry-run result envelope traceability.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "phase_2a_04_plan_evidence_ledger.py; phase_2a_05_dry_run_result_envelope_renderer.py",
        "notes": "Provides reusable evidence structure for future planning, not execution.",
    },
    {
        "artifact_source": "Phase 2A negative regression and VRRP dry-run validation",
        "phase_day": "Phase 2A-06 to Phase 2A-07",
        "safety_topic_covered": "Negative regression coverage and VRRP dry-run validation as one example job type.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "phase_2a_06_negative_regression_matrix.py; phase_2a_07_vrrp_dry_run_validation_pack.py",
        "notes": "VRRP remains an example only and does not narrow Phase 2B scope.",
    },
    {
        "artifact_source": "Phase 2A UI readiness and closure artifacts",
        "phase_day": "Phase 2A-08 to Phase 2A-11",
        "safety_topic_covered": "Job catalog examples, mock-screen readiness, safe-boundary readiness, and final closure review.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py; phase_2a_11_phase_closure_final_readiness_review.py",
        "notes": "UI readiness remains mock/report-only and does not create frontend API integration.",
    },
    {
        "artifact_source": "Phase 2B authorization and planning artifacts",
        "phase_day": "Phase 2B-00, Phase 2B-00A, Phase 2B-01, Phase 2B-02",
        "safety_topic_covered": "Authorization scope gate, planning-only owner authorization, planning scope design, and safety gate design.",
        "coverage_status": "COVERED",
        "related_evidence_or_file_reference": "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md; docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md; docs/phase_2b/phase_2b_01_planning_scope_design_only.md; docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
        "notes": "Phase 2B is planning-only; implementation is still locked.",
    },
    {
        "artifact_source": "Phase 2B-03 planning artifact",
        "phase_day": "Phase 2B-03",
        "safety_topic_covered": "Phase 2B-03 artifact reference if present.",
        "coverage_status": "MISSING_DEFERRED",
        "related_evidence_or_file_reference": "No phase_2b_03_* source, docs, or tests found in current repository file listing.",
        "notes": "Absence is recorded as a planning gap, not a blocker for this crosswalk.",
    },
    {
        "artifact_source": "Forbidden capability inventory",
        "phase_day": "Phase-wide",
        "safety_topic_covered": "Runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live devices, providers/APIs/models, secrets, frontend APIs, backups, VRRP execution, mutation, approval bypass, and safety-gate weakening.",
        "coverage_status": "NOT_ALLOWED_CURRENT_PHASE",
        "related_evidence_or_file_reference": "phase_2b_00a_planning_only_owner_authorization_statement.py; phase_2b_02_safety_gate_design_planning_only.py",
        "notes": "All listed capabilities remain disabled and forbidden for Phase 2B-04.",
    },
    {
        "artifact_source": "Phase 2B-04 crosswalk and gap review",
        "phase_day": "Phase 2B-04",
        "safety_topic_covered": "Phase-wide planning crosswalk, gap review, non-duplication statement, and next-step recommendation.",
        "coverage_status": "PARTIALLY_COVERED",
        "related_evidence_or_file_reference": "phase_2b_04_safety_artifact_crosswalk_gap_review.py; docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
        "notes": "This task creates the missing consolidated crosswalk but does not close future implementation gaps.",
    },
)

GAP_REVIEW = {
    "already_covered": (
        "Repository AGENTS.md safety rules and validation expectations.",
        "Day1-Day160 reviewer-only, dry-run, mock-only, disabled-provider, safety-regression, closure, and phase-gate evidence.",
        "Phase 2A read-only, dry-run plan gate, evidence ledger, result envelope, negative regression, UI readiness, and closure readiness artifacts.",
        "Phase 2B-00, 00A, 01, and 02 planning-only authorization, scope, and safety gate artifacts.",
        "No-execution proof patterns for rejected, dry-run, mock-only, report-only, documentation-only, and design-only flows.",
    ),
    "partially_covered": (
        "A single phase-wide crosswalk existed only implicitly across prior artifacts before Phase 2B-04.",
        "Phase 2B-03 is not present in the current repository file listing and is therefore only recorded as missing/deferred.",
        "Future implementation authorization prerequisites are documented, but no implementation request has been authorized.",
    ),
    "missing_deferred": (
        "Any Phase 2B implementation authorization.",
        "Executable runner, adapter, broker, scheduler, queue worker, or live-device design implementation.",
        "Capability-specific negative tests for future implementation code that does not exist yet.",
        "Future owner-approved safety gate permitting any live-capable workflow.",
    ),
    "not_allowed_current_phase": (
        "SSH, NETCONF, RESTCONF, live device access, real execution, real backup, or real VRRP execution.",
        "Provider/API/model calls, external AI runtime, cloud execution, or secrets handling.",
        "Frontend API integration or executable safety enforcement behavior changes.",
        "Configuration-changing commands, reset, reboot, remove, disable, enable, mutation, approval bypass, or safety-gate weakening.",
    ),
}

COMPLETION_MARKERS = (
    "PHASE_2B_04_PLANNING_ONLY_CROSSWALK_GAP_REVIEW_COMPLETE",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "NEW_SAFETY_MATRIX_CREATED_FALSE",
    "CROSSWALK_CREATED_TRUE",
    "GAP_REVIEW_CREATED_TRUE",
    "IMPLEMENTATION_STARTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_ENABLED_FALSE",
    "PROVIDER_API_MODEL_CALLS_ENABLED_FALSE",
)


def _forbidden_capability_matrix() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_04": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _crosswalk_rows() -> Tuple[Dict[str, Any], ...]:
    return tuple(deepcopy(row) for row in CROSSWALK_ROWS)


def validate_phase_2b_04_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
        "phase_goal",
        "example_job_types",
        "forbidden_scope",
        "existing_artifacts_to_reference",
        "implementation_boundary",
    ):
        if field not in scope_confirmation:
            errors.append(f"SCOPE_CONFIRMATION_FIELD_MISSING:{field}")
    if scope_confirmation.get("status") != "PASS":
        errors.append("SCOPE_CONFIRMATION_NOT_PASS")
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
    if report.get("non_duplication_statement") != NON_DUPLICATION_STATEMENT:
        errors.append("NON_DUPLICATION_STATEMENT_MISMATCH")
    if report.get("safety_boundary_statement") != SAFETY_BOUNDARY_STATEMENT:
        errors.append("SAFETY_BOUNDARY_STATEMENT_MISMATCH")

    crosswalk = report.get("crosswalk", [])
    if not isinstance(crosswalk, Sequence) or isinstance(crosswalk, (str, bytes, bytearray)):
        errors.append("CROSSWALK_NOT_SEQUENCE")
        crosswalk = []
    required_fields = {
        "artifact_source",
        "phase_day",
        "safety_topic_covered",
        "coverage_status",
        "related_evidence_or_file_reference",
        "notes",
    }
    status_values = set()
    for item in crosswalk:
        if not isinstance(item, Mapping):
            errors.append("CROSSWALK_ITEM_NOT_OBJECT")
            continue
        missing = required_fields - set(item)
        if missing:
            errors.append(f"CROSSWALK_ITEM_FIELDS_MISSING:{','.join(sorted(missing))}")
        status_values.add(str(item.get("coverage_status")))
    if len(crosswalk) != len(CROSSWALK_ROWS):
        errors.append("CROSSWALK_ROW_COUNT_MISMATCH")
    if status_values != set(COVERAGE_STATUS_CATEGORIES):
        errors.append("CROSSWALK_COVERAGE_STATUS_SET_MISMATCH")

    gap_review = report.get("gap_review", {})
    if not isinstance(gap_review, Mapping):
        errors.append("GAP_REVIEW_NOT_OBJECT")
        gap_review = {}
    for key in ("already_covered", "partially_covered", "missing_deferred", "not_allowed_current_phase"):
        if not gap_review.get(key):
            errors.append(f"GAP_REVIEW_SECTION_MISSING:{key}")

    matrix = report.get("forbidden_capability_matrix", [])
    matrix_names = {str(item.get("capability")) for item in matrix if isinstance(item, Mapping)}
    if matrix_names != set(FORBIDDEN_CAPABILITIES):
        errors.append("FORBIDDEN_CAPABILITY_MATRIX_MISMATCH")
    for item in matrix if isinstance(matrix, Sequence) and not isinstance(matrix, (str, bytes, bytearray)) else ():
        if not isinstance(item, Mapping):
            errors.append("FORBIDDEN_CAPABILITY_ITEM_NOT_OBJECT")
            continue
        if item.get("enabled") is not False or item.get("allowed_by_phase_2b_04") is not False:
            errors.append(f"FORBIDDEN_CAPABILITY_ENABLED:{item.get('capability')}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "NEW_SAFETY_MATRIX_CREATED": "NO",
        "CROSSWALK_CREATED": "YES",
        "GAP_REVIEW_CREATED": "YES",
        "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
        "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "crosswalk_rows_checked": len(crosswalk),
        "coverage_statuses_checked": len(status_values),
        "forbidden_capabilities_checked": len(matrix_names),
        "gap_sections_checked": len(gap_review),
    }


def build_phase_2b_04_safety_artifact_crosswalk_gap_review_report() -> Dict[str, Any]:
    phase_2b_02 = build_phase_2b_02_safety_gate_design_planning_only_report()
    crosswalk = _crosswalk_rows()
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
            "status": "PASS",
            "phase_goal": "Phase-wide planning for safe future job execution readiness; review existing safety artifact coverage and gaps without enabling execution.",
            "example_job_types": list(REQUIRED_JOB_TYPES),
            "example_job_type_role": "examples_only_not_phase_scope",
            "forbidden_scope": list(FORBIDDEN_CAPABILITIES),
            "existing_artifacts_to_reference": [
                "Day1-Day160 safety, dry-run, reviewer-only, forbidden capability, and phase gate artifacts",
                "Phase 2A read-only, dry-run, mock-only, job spec validation, plan gate, evidence ledger, result envelope, negative regression, UI readiness, and closure artifacts",
                "Phase 2B-00, Phase 2B-00A, Phase 2B-01, Phase 2B-02, and Phase 2B-03 if present",
            ],
            "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "authorized_scope": list(AUTHORIZED_SCOPE),
        "implementation_boundary": list(IMPLEMENTATION_BOUNDARY),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "crosswalk": list(crosswalk),
        "gap_review": {key: list(value) for key, value in GAP_REVIEW.items()},
        "non_duplication_statement": NON_DUPLICATION_STATEMENT,
        "safety_boundary_statement": SAFETY_BOUNDARY_STATEMENT,
        "next_step_recommendation": NEXT_STEP_RECOMMENDATION,
        "forbidden_capability_matrix": list(_forbidden_capability_matrix()),
        "phase_2b_02_reference_status": phase_2b_02.get("status", "UNKNOWN"),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_PLANNING_ONLY_AUTHORIZED": "YES",
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "NEW_SAFETY_MATRIX_CREATED": "NO",
            "CROSSWALK_CREATED": "YES",
            "GAP_REVIEW_CREATED": "YES",
            "RUNNER_ADAPTER_EXECUTION_ENABLED": "NO",
            "PROVIDER_API_MODEL_CALLS_ENABLED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "new_safety_matrix_created": False,
            "crosswalk_created": True,
            "gap_review_created": True,
            "implementation_started": False,
            "runner_adapter_execution_enabled": False,
            "provider_api_model_calls_enabled": False,
            "crosswalk_rows_checked": len(crosswalk),
            "gap_sections_checked": len(GAP_REVIEW),
            "forbidden_capabilities_enabled": 0,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_04_report(report)
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


def _table_rows(values: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> str:
    return "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(str(item.get(field, '')))}</td>" for field in fields) + "</tr>"
        for item in values
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    gap_review = report["gap_review"]
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
  <p>{html.escape(str(report["non_duplication_statement"]))}</p>
  <p>{html.escape(str(report["safety_boundary_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Crosswalk</h2>
  <table>
    <thead><tr><th>Artifact / source</th><th>Phase/day</th><th>Safety topic covered</th><th>Coverage status</th><th>Related evidence or file reference</th><th>Notes</th></tr></thead>
    <tbody>{_table_rows(report["crosswalk"], ("artifact_source", "phase_day", "safety_topic_covered", "coverage_status", "related_evidence_or_file_reference", "notes"))}</tbody>
  </table>
  <h2>Gap Review</h2>
  <h3>Already Covered</h3><ul>{_list_items(gap_review["already_covered"])}</ul>
  <h3>Partially Covered</h3><ul>{_list_items(gap_review["partially_covered"])}</ul>
  <h3>Missing / Deferred</h3><ul>{_list_items(gap_review["missing_deferred"])}</ul>
  <h3>Not Allowed Current Phase</h3><ul>{_list_items(gap_review["not_allowed_current_phase"])}</ul>
  <h2>Forbidden Capabilities</h2>
  <table>
    <thead><tr><th>Capability</th><th>Enabled</th><th>Allowed by Phase 2B-04</th><th>Status</th></tr></thead>
    <tbody>{_table_rows(report["forbidden_capability_matrix"], ("capability", "enabled", "allowed_by_phase_2b_04", "status"))}</tbody>
  </table>
  <h2>Next Step</h2>
  <p>{html.escape(str(report["next_step_recommendation"]))}</p>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_04_safety_artifact_crosswalk_gap_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_04_safety_artifact_crosswalk_gap_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_04_safety_artifact_crosswalk_gap_review_report()
    json_path, html_path = write_phase_2b_04_safety_artifact_crosswalk_gap_review_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"scope_confirmation: {report['summary']['scope_confirmation']}")
    print(f"phase_goal_confirmed: {str(report['summary']['phase_goal_confirmed']).lower()}")
    print(
        "example_job_types_treated_as_examples_only: "
        f"{str(report['summary']['example_job_types_treated_as_examples_only']).lower()}"
    )
    print(f"forbidden_scope_preserved: {str(report['summary']['forbidden_scope_preserved']).lower()}")
    print(f"existing_artifacts_referenced: {str(report['summary']['existing_artifacts_referenced']).lower()}")
    print(
        "implementation_boundary_preserved: "
        f"{str(report['summary']['implementation_boundary_preserved']).lower()}"
    )
    print(f"new_safety_matrix_created: {str(report['new_safety_matrix_created']).lower()}")
    print(f"crosswalk_created: {str(report['crosswalk_created']).lower()}")
    print(f"gap_review_created: {str(report['gap_review_created']).lower()}")
    print(f"implementation_started: {str(report['implementation_started']).lower()}")
    print(f"runner_allowed: {str(report['runner_allowed']).lower()}")
    print(f"adapter_allowed: {str(report['adapter_allowed']).lower()}")
    print(f"execution_allowed: {str(report['execution_allowed']).lower()}")
    print(f"runner_enabled: {str(report['runner_enabled']).lower()}")
    print(f"adapter_enabled: {str(report['adapter_enabled']).lower()}")
    print(f"broker_enabled: {str(report['broker_enabled']).lower()}")
    print(f"scheduler_enabled: {str(report['scheduler_enabled']).lower()}")
    print(f"queue_worker_enabled: {str(report['queue_worker_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"netconf_enabled: {str(report['netconf_enabled']).lower()}")
    print(f"restconf_enabled: {str(report['restconf_enabled']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"provider_api_model_calls_enabled: {str(report['provider_api_model_calls_enabled']).lower()}")
    print(f"secrets_handling_enabled: {str(report['secrets_handling_enabled']).lower()}")
    print(f"frontend_api_integration_enabled: {str(report['frontend_api_integration_enabled']).lower()}")
    print(f"safety_gate_weakening_enabled: {str(report['safety_gate_weakening_enabled']).lower()}")
    print(f"Crosswalk rows checked: {report['summary']['crosswalk_rows_checked']}")
    print(f"Gap sections checked: {report['summary']['gap_sections_checked']}")
    print(f"Forbidden capabilities enabled: {report['summary']['forbidden_capabilities_enabled']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
