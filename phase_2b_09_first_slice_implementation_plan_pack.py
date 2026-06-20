"""Phase 2B-09 first-slice implementation plan pack.

This module creates deterministic, local, planning-only report artifacts for a
future first implementation slice plan. It starts from the Phase 2B-08
GO_TO_2B_09_PLANNING_ONLY verdict and does not implement the slice, duplicate
the gate decision, rebuild safety gates, create a second safety matrix, or
enable runners, adapters, execution, SSH, NETCONF, RESTCONF, live-device access,
provider/API/model calls, secrets handling, frontend integration, backup,
validation, command execution, or real network operations.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_08_first_slice_implementation_authorization_gate_planning_only import (
    FINAL_VERDICT as PHASE_2B_08_VERDICT,
)


PHASE = "2B-09"
TASK_NAME = "phase2b-09-first-slice-implementation-plan-pack-planning-only"
TITLE = "Phase 2B-09 First-Slice Implementation Plan Pack - Planning Only"
MODE = "planning_only_first_slice_implementation_plan_pack"
SCOPE = "phase_wide_phase_2b_first_slice_implementation_plan_pack_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_09_PLANNING_ONLY_DONE"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_09_first_slice_implementation_plan_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_09_first_slice_implementation_plan_pack.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_09_first_slice_implementation_plan_pack.md"

PHASE_GOAL = (
    "Plan how a future smallest safe first implementation slice should be "
    "prepared, sequenced, constrained, tested, reviewed, stopped, and rolled "
    "back while keeping this task planning-only."
)

INPUT_AUTHORIZATION = {
    "phase_2b_08_verdict_referenced": PHASE_2B_08_VERDICT,
    "phase_2b_08_role": "Gate",
    "phase_2b_09_role": "Plan",
    "phase_2b_08_gate_duplicated": False,
    "phase_2b_08_gate_rerun": False,
}

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
    "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
    "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
    "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
    "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
    "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
    "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "existing Phase 2B planning artifact tests",
)

FORBIDDEN_SCOPE = (
    "implementation",
    "first-slice implementation",
    "runner creation",
    "adapter creation",
    "execution path creation",
    "scheduler creation",
    "queue worker creation",
    "broker creation",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "real network operation",
    "real backup",
    "real config change",
    "provider call",
    "API call",
    "model call",
    "secrets handling",
    "frontend API integration",
    "new safety matrix duplication",
    "rewriting existing safety gates",
)

FIRST_SLICE_PLANNING_TARGET = {
    "name": "local_static_job_definition_and_evidence_contract_slice",
    "planning_level_only": True,
    "description": (
        "A future, separately authorized implementation may remain limited to "
        "local static job-definition and reviewer-evidence contract structures "
        "for the Phase 2B job lifecycle."
    ),
    "may_define": (
        "static job metadata fields",
        "static reviewer-evidence fields",
        "static no-execution flags",
        "report-index visibility expectations",
        "validation tests proving forbidden capabilities remain absent",
    ),
    "must_not_create": (
        "code that executes work",
        "runner",
        "adapter",
        "broker",
        "scheduler",
        "queue worker",
        "execution engine",
        "network client",
        "provider client",
        "secrets path",
        "frontend API integration",
        "live-device behavior",
    ),
}

IN_SCOPE_PLANNING_CONTENT = (
    "file impact plan",
    "step sequence",
    "test strategy",
    "evidence strategy",
    "rollback / stop conditions",
    "acceptance criteria",
    "boundary proof",
)

FILE_IMPACT_PLAN = {
    "documentation_only_files": (
        "docs/phase_2b/",
        "docs/phase_2a/ references where relevant",
        "reviewer-facing evidence notes",
    ),
    "registry_reporting_metadata": (
        "task catalog metadata",
        "report-index metadata",
        "CLI report task exposure",
    ),
    "tests": (
        "Phase 2B planning artifact tests",
        "report-index visibility tests",
        "negative boundary tests",
    ),
    "explicitly_forbidden_runtime_execution_files": (
        "runner, adapter, broker, scheduler, queue worker, or execution engine files",
        "network client files",
        "SSH, NETCONF, or RESTCONF integration files",
        "provider/API/model integration files",
        "secrets or credential handling files",
        "frontend API integration routes",
        "files that trigger real backup, validation, command execution, or config change",
    ),
}

STEP_SEQUENCE = (
    {
        "step": "Confirm future task authorization and scope.",
        "stop_gate": "Stop with NEEDS_SCOPE_CONFIRMATION if scope narrows to one example job type or implementation is not explicitly authorized.",
    },
    {
        "step": "Re-read existing safety artifacts and AGENTS.md.",
        "stop_gate": "Stop if any future task would rebuild, replace, duplicate, or weaken existing safety gates.",
    },
    {
        "step": "Draft static contract fields only.",
        "stop_gate": "Stop if a field implies runner dispatch, adapter invocation, queue processing, device access, provider access, secrets access, or frontend API integration.",
    },
    {
        "step": "Add deterministic local metadata exposure only.",
        "stop_gate": "Stop if exposure would create production execution behavior or call a runtime path.",
    },
    {
        "step": "Add negative tests before any future behavior wiring.",
        "stop_gate": "Stop if tests cannot prove rejected, planning-only, report-only, dry-run-only, and mock-only flows reach no execution path.",
    },
    {
        "step": "Run targeted validation and report-index validation.",
        "stop_gate": "Stop on failing safety, scope, report visibility, or no-execution proof.",
    },
    {
        "step": "Require reviewer approval before any future execution-related change.",
        "stop_gate": "Stop unless the reviewer explicitly approves the next separate change.",
    },
)

TESTING_STRATEGY = (
    "prove the future artifact or static contract exists",
    "prove work remains local, deterministic, and planning/report-only unless separately authorized",
    "prove no implementation is authorized by Phase 2B-09",
    "prove example job types remain examples only",
    "prove the phase is not narrowed to one job type",
    "prove Phase 2B-08 is referenced as the input gate and the full decision is not duplicated",
    "prove forbidden capability paths remain absent",
    "prove report-index and registry metadata remain visible where consistent with repository patterns",
    "prove rejected scenarios reach no adapter, broker, runner, or execution path",
)

EVIDENCE_STRATEGY = (
    "machine-readable no-execution flags",
    "static artifact references",
    "report-index visibility",
    "targeted negative-test output",
    "validation output for python -m pytest",
    "validation output for python network_lab.py --task report-index",
    "clear distinction between 2B-08 = Gate and 2B-09 = Plan",
    "explicit note that Phase 2B-08 was referenced, not duplicated",
)

ROLLBACK_STOP_CONDITIONS = (
    "scope narrows to only VRRP, only baseline, only backup, only one job type, or only one device scenario",
    "implementation begins without a separate explicit future authorization",
    "runner, adapter, broker, scheduler, queue worker, background worker, or execution path appears",
    "SSH, NETCONF, RESTCONF, live-device access, provider/API/model call, secrets handling, frontend API integration, real backup, real validation, real command execution, or real config change appears",
    "a second safety matrix is created",
    "existing safety gates are rewritten, rebuilt, replaced, or weakened",
    "Phase 2B-08 is re-run, duplicated, or converted into a new gate",
    "examples stop being examples only",
    "report-index or registry metadata becomes execution-capable",
    "no-execution proof is missing, ambiguous, or weakened",
)

ACCEPTANCE_CRITERIA = (
    "task remains planning-only",
    "no first-slice implementation is added",
    "no runner, adapter, execution path, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live-device access, provider/API/model call, secrets handling, frontend API integration, real backup, real validation, real command execution, or config change is added",
    "example job types remain examples only",
    f"Phase 2B-08 verdict {PHASE_2B_08_VERDICT} is referenced as the input gate",
    "the full Phase 2B-08 gate decision is not duplicated",
    "existing safety gates are referenced and remain authoritative",
    "no second safety matrix is created",
    "future file impact remains separated into documentation-only files, registry/reporting metadata, tests, and explicitly forbidden runtime/execution files",
    "future step sequence includes mandatory stop gates and reviewer approval before any future execution-related change",
    "boundary proof is reviewer-visible and machine-readable",
)

BOUNDARY_PROOF_CHECKLIST = (
    "AGENTS.md found, read before changes, and not modified",
    "scope confirmation recorded with phase goal, example job types, forbidden scope, existing artifacts, and implementation boundary",
    f"{PHASE_2B_08_VERDICT} referenced from Phase 2B-08",
    "2B-08 = Gate and 2B-09 = Plan distinction preserved",
    "Phase 2B-08 gate decision not duplicated",
    "no first-slice implementation added",
    "no runner, adapter, execution path, broker, scheduler, queue worker, or background worker added",
    "no SSH, NETCONF, RESTCONF, live-device access, real network operation, real backup, real validation, real command execution, or real config change added",
    "no provider call, API call, model call, external AI runtime, secrets handling, or frontend API integration added",
    "existing safety gates referenced, not rebuilt, replaced, duplicated, or weakened",
    "no second safety matrix created",
    "example job types remain examples only",
    "report-index and task-registry exposure remain planning-only and non-executing",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
    "phase_2b_09_plan_pack_created": True,
    "phase_2b_08_verdict_referenced": True,
    "phase_2b_08_gate_duplicated": False,
    "phase_2b_08_gate_rerun": False,
    "direct_implementation_authorized": False,
    "first_slice_implemented": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_worker_added": False,
    "background_worker_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "real_device_access_added": False,
    "real_network_operation_added": False,
    "real_backup_added": False,
    "real_config_change_added": False,
    "real_validation_added": False,
    "real_command_execution_added": False,
    "provider_api_model_calls_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "secrets_handling_added": False,
    "frontend_api_integration_added": False,
    "safety_gates_rebuilt": False,
    "safety_gates_replaced": False,
    "safety_gates_rewritten": False,
    "safety_gates_weakened": False,
    "second_safety_matrix_created": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_09_FIRST_SLICE_IMPLEMENTATION_PLAN_PACK_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "PHASE_2B_08_VERDICT_REFERENCED",
    "PHASE_2B_08_GATE_DUPLICATED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_FALSE",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_FALSE",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_FALSE",
    "SAFETY_GATES_REBUILT_OR_REPLACED_FALSE",
    "SECOND_SAFETY_MATRIX_CREATED_FALSE",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_09": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_09_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    input_authorization = report.get("input_authorization", {})
    if not isinstance(input_authorization, Mapping):
        errors.append("INPUT_AUTHORIZATION_NOT_OBJECT")
        input_authorization = {}
    if input_authorization.get("phase_2b_08_verdict_referenced") != PHASE_2B_08_VERDICT:
        errors.append("PHASE_2B_08_VERDICT_NOT_REFERENCED")
    if input_authorization.get("phase_2b_08_gate_duplicated") is not False:
        errors.append("PHASE_2B_08_GATE_DUPLICATED")
    if input_authorization.get("phase_2b_08_gate_rerun") is not False:
        errors.append("PHASE_2B_08_GATE_RERUN")

    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if set(report.get("in_scope_planning_content", [])) != set(IN_SCOPE_PLANNING_CONTENT):
        errors.append("IN_SCOPE_PLANNING_CONTENT_MISMATCH")
    if set(report.get("testing_strategy", [])) != set(TESTING_STRATEGY):
        errors.append("TESTING_STRATEGY_MISMATCH")
    if set(report.get("evidence_strategy", [])) != set(EVIDENCE_STRATEGY):
        errors.append("EVIDENCE_STRATEGY_MISMATCH")
    if set(report.get("rollback_stop_conditions", [])) != set(ROLLBACK_STOP_CONDITIONS):
        errors.append("ROLLBACK_STOP_CONDITIONS_MISMATCH")
    if set(report.get("acceptance_criteria", [])) != set(ACCEPTANCE_CRITERIA):
        errors.append("ACCEPTANCE_CRITERIA_MISMATCH")
    if set(report.get("boundary_proof_checklist", [])) != set(BOUNDARY_PROOF_CHECKLIST):
        errors.append("BOUNDARY_PROOF_CHECKLIST_MISMATCH")

    file_impact_plan = report.get("file_impact_plan", {})
    if not isinstance(file_impact_plan, Mapping):
        errors.append("FILE_IMPACT_PLAN_NOT_OBJECT")
        file_impact_plan = {}
    for category in (
        "documentation_only_files",
        "registry_reporting_metadata",
        "tests",
        "explicitly_forbidden_runtime_execution_files",
    ):
        if category not in file_impact_plan:
            errors.append(f"FILE_IMPACT_PLAN_MISSING:{category}")

    if len(report.get("step_sequence", [])) != len(STEP_SEQUENCE):
        errors.append("STEP_SEQUENCE_COUNT_MISMATCH")
    if any("stop_gate" not in item for item in report.get("step_sequence", []) if isinstance(item, Mapping)):
        errors.append("STEP_SEQUENCE_STOP_GATE_MISSING")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    target = report.get("first_slice_planning_target", {})
    if not isinstance(target, Mapping):
        errors.append("FIRST_SLICE_PLANNING_TARGET_NOT_OBJECT")
        target = {}
    if target.get("planning_level_only") is not True:
        errors.append("FIRST_SLICE_PLANNING_TARGET_NOT_PLANNING_ONLY")
    if target.get("name") == "vrrp_validation":
        errors.append("FIRST_SLICE_NARROWED_TO_VRRP")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PHASE_2B_08_VERDICT_REFERENCED": PHASE_2B_08_VERDICT,
        "PHASE_2B_08_GATE_DUPLICATED": "NO",
        "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(artifacts),
        "file_impact_categories_checked": len(file_impact_plan),
        "step_sequence_steps_checked": len(report.get("step_sequence", [])),
        "testing_strategy_items_checked": len(report.get("testing_strategy", [])),
        "acceptance_criteria_checked": len(report.get("acceptance_criteria", [])),
        "boundary_proof_items_checked": len(report.get("boundary_proof_checklist", [])),
    }


def build_phase_2b_09_first_slice_implementation_plan_pack_report() -> Dict[str, Any]:
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
            "phase_goal": PHASE_GOAL,
            "example_job_types": list(REQUIRED_JOB_TYPES),
            "example_job_type_role": "examples_only_not_phase_scope",
            "forbidden_scope": list(FORBIDDEN_SCOPE),
            "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
            "implementation_boundary": list(FORBIDDEN_SCOPE) + list(IN_SCOPE_PLANNING_CONTENT),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "input_authorization": deepcopy(INPUT_AUTHORIZATION),
        "first_slice_planning_target": deepcopy(FIRST_SLICE_PLANNING_TARGET),
        "in_scope_planning_content": list(IN_SCOPE_PLANNING_CONTENT),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "file_impact_plan": deepcopy(FILE_IMPACT_PLAN),
        "step_sequence": list(deepcopy(STEP_SEQUENCE)),
        "testing_strategy": list(TESTING_STRATEGY),
        "evidence_strategy": list(EVIDENCE_STRATEGY),
        "rollback_stop_conditions": list(ROLLBACK_STOP_CONDITIONS),
        "acceptance_criteria": list(ACCEPTANCE_CRITERIA),
        "boundary_proof_checklist": list(BOUNDARY_PROOF_CHECKLIST),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_duplication_statement": (
            "Phase 2B-09 references the Phase 2B-08 GO_TO_2B_09_PLANNING_ONLY "
            "verdict as the input gate and does not duplicate, re-run, or replace "
            "the Phase 2B-08 gate decision."
        ),
        "non_implementation_statement": (
            "This task is planning-only. It does not implement the first slice, "
            "authorize implementation, create runtime behavior, create mock code "
            "that looks like a runner or adapter, or enable live or provider access."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PHASE_2B_08_VERDICT_REFERENCED": PHASE_2B_08_VERDICT,
            "PHASE_2B_08_GATE_DUPLICATED": "NO",
            "PHASE_2B_IMPLEMENTATION_ALLOWED": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "SAFETY_GATES_REBUILT_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "phase_2b_08_verdict_referenced": True,
            "phase_2b_08_gate_duplicated": False,
            "first_slice_implemented": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "safety_gates_rebuilt_or_replaced": False,
            "second_safety_matrix_created": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_09_report(report)
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
  <p>{html.escape(str(report["non_implementation_statement"]))}</p>
  <p>{html.escape(str(report["non_duplication_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Input Authorization</h2>
  <table><tbody>{_dict_rows(report["input_authorization"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>First-Slice Planning Target</h2>
  <table><tbody>{_dict_rows(report["first_slice_planning_target"])}</tbody></table>
  <h2>File Impact Plan</h2>
  <table><tbody>{_dict_rows(report["file_impact_plan"])}</tbody></table>
  <h2>Step Sequence</h2>
  <table>
    <thead><tr><th>Step</th><th>Stop Gate</th></tr></thead>
    <tbody>{_table_rows(report["step_sequence"], ("step", "stop_gate"))}</tbody>
  </table>
  <h2>Testing Strategy</h2>
  <ul>{_list_items(report["testing_strategy"])}</ul>
  <h2>Evidence Strategy</h2>
  <ul>{_list_items(report["evidence_strategy"])}</ul>
  <h2>Rollback / Stop Conditions</h2>
  <ul>{_list_items(report["rollback_stop_conditions"])}</ul>
  <h2>Acceptance Criteria</h2>
  <ul>{_list_items(report["acceptance_criteria"])}</ul>
  <h2>Boundary Proof Checklist</h2>
  <ul>{_list_items(report["boundary_proof_checklist"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2b_09_first_slice_implementation_plan_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_09_first_slice_implementation_plan_pack_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_09_first_slice_implementation_plan_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_09_first_slice_implementation_plan_pack_report()
    json_path, html_path = write_phase_2b_09_first_slice_implementation_plan_pack_reports(project_root, report)
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
    print(f"phase_2b_08_verdict_referenced: {str(report['summary']['phase_2b_08_verdict_referenced']).lower()}")
    print(f"phase_2b_08_gate_duplicated: {str(report['summary']['phase_2b_08_gate_duplicated']).lower()}")
    print(f"first_slice_implemented: {str(report['first_slice_implemented']).lower()}")
    print(f"runner_added: {str(report['runner_added']).lower()}")
    print(f"adapter_added: {str(report['adapter_added']).lower()}")
    print(f"execution_path_added: {str(report['execution_path_added']).lower()}")
    print(
        "ssh_netconf_restconf_live_device_touched: "
        f"{str(report['summary']['ssh_netconf_restconf_live_device_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(f"safety_gates_rebuilt_or_replaced: {str(report['summary']['safety_gates_rebuilt_or_replaced']).lower()}")
    print(f"second_safety_matrix_created: {str(report['second_safety_matrix_created']).lower()}")
    print(f"File impact categories checked: {report['validation']['file_impact_categories_checked']}")
    print(f"Step sequence steps checked: {report['validation']['step_sequence_steps_checked']}")
    print(f"Testing strategy items checked: {report['validation']['testing_strategy_items_checked']}")
    print(f"Acceptance criteria checked: {report['validation']['acceptance_criteria_checked']}")
    print(f"Boundary proof items checked: {report['validation']['boundary_proof_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
