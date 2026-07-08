"""Phase 2B-10 Day1-Day160 reference mapping for a future first slice.

This module creates deterministic, local, planning-only report artifacts that
map future first-slice planning concerns back to existing Day1-Day160, Phase 2A,
and Phase 2B controls. It does not create a second safety matrix, rewrite
existing controls, authorize implementation, or enable runners, adapters,
execution paths, SSH, NETCONF, RESTCONF, live-device access, provider/API/model
calls, secrets handling, frontend integration, backups, validation, command
execution, or real network operations.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents
from phase_2a_08_jobs_catalog_ui_readiness_planning_pack import REQUIRED_JOB_TYPES
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_09_first_slice_implementation_plan_pack import FINAL_VERDICT as PHASE_2B_09_VERDICT


PHASE = "2B-10"
TASK_NAME = "phase2b-10-day1-day160-reference-mapping-for-future-first-slice-planning-only"
TITLE = "Phase 2B-10 Day1-Day160 Reference Mapping for Future First Slice - Planning Only"
MODE = "planning_only_day1_day160_reference_mapping"
SCOPE = "phase_wide_day1_day160_reference_mapping_for_future_first_slice_planning_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2B_10_DAY1_DAY160_REFERENCE_MAPPING_PLANNING_ONLY_DONE"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.html"
DOC_PATH = Path("docs") / "phase_2b" / "phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md"

PHASE_GOAL = (
    "Create a Day1-Day160 reference mapping for a future first implementation "
    "slice, proving that future planning inherits existing controls by "
    "reference only without copying, rebuilding, replacing, or creating a "
    "second safety matrix."
)

REQUIRED_PHASE_2B_REFERENCES = (
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
    "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2b/phase_2b_00_authorization_scope_gate_review.md",
    "docs/phase_2b/phase_2b_00a_planning_only_owner_authorization_statement.md",
    "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
    "docs/phase_2b/phase_2b_02_safety_gate_design_planning_only.md",
    "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    *REQUIRED_PHASE_2B_REFERENCES,
    "docs/phase_2b/phase_2b_07_first_slice_definition_pack.md",
    "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md",
    "docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
    "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md",
    "docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
    "docs/roadmap/day35_vrrp_failover_validation_safety.md",
    "docs/roadmap/day59_intent_policy_matrix_reviewer_safety_explanation.md",
    "docs/ai/intent_runtime_safety_gate.md",
    "docs/ai/day159_v05_ai_assistance_safety_regression_matrix.md",
    "docs/ai/day160_v05_ai_assistance_phase_gate_review.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "existing Phase 2B planning artifact tests",
)

FORBIDDEN_SCOPE = (
    "implementation",
    "first-slice implementation",
    "new readiness gate duplication",
    "new authorization gate duplication",
    "new implementation plan duplication",
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
    "new safety matrix",
    "second safety matrix",
    "rewriting Day1-Day160 controls",
    "replacing Day1-Day160 controls",
    "copying Day1-Day160 safety matrix into Phase 2B",
)

ALLOWED_REFERENCE_BEHAVIOR = (
    "cite",
    "link",
    "summarize narrowly",
    "inherit",
    "verify consistency",
)

FORBIDDEN_REFERENCE_BEHAVIOR = (
    "copy wholesale",
    "rewrite",
    "replace",
    "create parallel safety gate",
    "create new matrix",
)

REFERENCE_MAPPING_TABLE = (
    {
        "future_first_slice_concern": "Repository-wide no-live and no-execution boundary",
        "existing_control_or_artifact_to_reference": "AGENTS.md",
        "allowed_use": "Cite as the authoritative repository safety operating contract.",
        "forbidden_use": "Do not restate it as a new Phase 2B safety matrix or override its rules.",
        "reviewer_evidence_expected": "Artifact notes AGENTS.md was found, read before changes, and not modified.",
    },
    {
        "future_first_slice_concern": "Phase-wide scope and examples-only job handling",
        "existing_control_or_artifact_to_reference": "docs/phase_2b/phase_2b_01_planning_scope_design_only.md",
        "allowed_use": "Inherit the examples-only boundary for baseline, interface, WAN/LAN, VRRP, backup-plan, and blocked-change examples.",
        "forbidden_use": "Do not narrow Phase 2B-10 or a future first slice to one job type.",
        "reviewer_evidence_expected": "Scope confirmation shows multiple example job types and NEEDS_SCOPE_CONFIRMATION stop behavior.",
    },
    {
        "future_first_slice_concern": "Day1-Day160 safety de-duplication",
        "existing_control_or_artifact_to_reference": "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
        "allowed_use": "Reference the existing de-duplication acceptance criteria and authoritative control list.",
        "forbidden_use": "Do not copy the full control list into a second matrix or redesign Day1-Day160 controls.",
        "reviewer_evidence_expected": "Mapping rows cite Phase 2B-05 as the de-duplication source, not a duplicated table.",
    },
    {
        "future_first_slice_concern": "Implementation entry and first-slice readiness boundary",
        "existing_control_or_artifact_to_reference": "docs/phase_2b/phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review.md",
        "allowed_use": "Cite the readiness review boundary when checking consistency.",
        "forbidden_use": "Do not re-run readiness, re-decide readiness, or convert 2B-10 into an entry gate.",
        "reviewer_evidence_expected": "Artifact states Phase 2B-10 does not duplicate Phase 2B-06.",
    },
    {
        "future_first_slice_concern": "First-slice authorization status",
        "existing_control_or_artifact_to_reference": "docs/phase_2b/phase_2b_08_first_slice_implementation_authorization_gate_planning_only.md",
        "allowed_use": "Reference the authorization gate boundary and its planning-only outcome.",
        "forbidden_use": "Do not re-run authorization or treat this mapping as implementation authorization.",
        "reviewer_evidence_expected": "Machine-readable verdict states implementation authorization remains NO.",
    },
    {
        "future_first_slice_concern": "Future first-slice plan pack alignment",
        "existing_control_or_artifact_to_reference": "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
        "allowed_use": "Reference the plan pack as the existing planning artifact to keep aligned.",
        "forbidden_use": "Do not rewrite, replace, or implement the Phase 2B-09 plan.",
        "reviewer_evidence_expected": "Artifact states 2B-09 is referenced, not reimplemented.",
    },
    {
        "future_first_slice_concern": "Dry-run plan rejection and unsafe input handling",
        "existing_control_or_artifact_to_reference": "docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md; docs/phase_2a/phase_2a_06_negative_regression_matrix.md",
        "allowed_use": "Cite existing rejection and negative-regression evidence for unsafe requests.",
        "forbidden_use": "Do not create a parallel rejection framework or new execution path.",
        "reviewer_evidence_expected": "Boundary proof keeps rejected and unsafe scenarios non-executing.",
    },
    {
        "future_first_slice_concern": "Phase 2A closure and handoff controls",
        "existing_control_or_artifact_to_reference": "docs/phase_2a/phase_2a_10_safe_boundary_implementation_readiness_artifact.md; docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md",
        "allowed_use": "Inherit Phase 2A safe-boundary and closure context.",
        "forbidden_use": "Do not reopen Phase 2A closure or turn readiness evidence into authorization.",
        "reviewer_evidence_expected": "Mapping distinguishes inherited prior-phase evidence from new implementation permission.",
    },
    {
        "future_first_slice_concern": "Locked runtime, provider/API/model, secret, and live-device controls",
        "existing_control_or_artifact_to_reference": "docs/ai/intent_runtime_safety_gate.md; docs/ai/day159_v05_ai_assistance_safety_regression_matrix.md; docs/ai/day160_v05_ai_assistance_phase_gate_review.md",
        "allowed_use": "Reference disabled runtime and phase-gate review evidence for consistency checks.",
        "forbidden_use": "Do not add provider/API/model calls, secrets handling, SSH, live-device access, or runtime unlocks.",
        "reviewer_evidence_expected": "No-execution flags remain false for provider/API/model/secrets and live-device paths.",
    },
    {
        "future_first_slice_concern": "VRRP and other concrete job examples",
        "existing_control_or_artifact_to_reference": "docs/roadmap/day35_vrrp_failover_validation_safety.md; docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md",
        "allowed_use": "Use concrete job artifacts only as examples of mapping behavior.",
        "forbidden_use": "Do not make VRRP, baseline, backup, or any single job type the whole phase.",
        "reviewer_evidence_expected": "Example job types remain examples only and the scope remains phase-wide.",
    },
)

FUTURE_REVIEWER_CHECKLIST = (
    "Day1-Day160 controls are referenced.",
    "No second safety matrix is created.",
    "No execution path is created.",
    "Examples remain examples only.",
    "Phase 2B-09 plan is referenced, not reimplemented.",
)

ACCEPTANCE_CRITERIA = (
    "planning-only status is explicit",
    "Day1-Day160 controls are used by reference only",
    "no new safety matrix is created",
    "no runner, adapter, execution path, provider/API/model call, secrets, SSH, NETCONF, RESTCONF, or live-device access is added",
    "examples remain examples only",
    "Phase 2B-05 is referenced without duplicating its role",
    "Phase 2B-06 is referenced without duplicating its role",
    "Phase 2B-08 is referenced without duplicating its role",
    "Phase 2B-09 is referenced without duplicating its role",
)

BOUNDARY_PROOF_CHECKLIST = (
    "AGENTS.md found, read before changes, and not modified",
    "scope confirmation recorded with phase goal, example job types, forbidden scope, existing artifacts, and implementation boundary",
    "Day1-Day160 controls referenced, not rewritten or replaced",
    "reference mapping table present",
    "allowed reference behavior limited to cite, link, summarize narrowly, inherit, and verify consistency",
    "forbidden reference behavior blocks wholesale copy, rewrite, replacement, parallel safety gate, and new matrix creation",
    "no Phase 2B-05, Phase 2B-06, Phase 2B-08, or Phase 2B-09 role duplication",
    "no first-slice implementation added",
    "no runner, adapter, execution path, broker, scheduler, queue worker, or background worker added",
    "no SSH, NETCONF, RESTCONF, live-device access, real network operation, real backup, real validation, command execution, or config change added",
    "no provider call, API call, model call, external AI runtime, secrets handling, or frontend API integration added",
)

SAFETY_FLAGS = {
    "phase_2b_planning_only_authorized": True,
    "phase_2b_10_reference_mapping_created": True,
    "phase_2b_implementation_allowed": False,
    "phase_2b_implementation_started": False,
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
    "day1_day160_rewritten_or_replaced": False,
    "day1_day160_safety_matrix_copied": False,
    "second_safety_matrix_created": False,
    "new_safety_matrix_created": False,
    "phase_2b_05_duplicated": False,
    "phase_2b_06_duplicated": False,
    "phase_2b_08_duplicated": False,
    "phase_2b_09_duplicated": False,
    "readiness_gate_duplicated": False,
    "authorization_gate_duplicated": False,
    "implementation_plan_duplicated": False,
}

COMPLETION_MARKERS = (
    "PHASE_2B_10_DAY1_DAY160_REFERENCE_MAPPING_PLANNING_ONLY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "SCOPE_CONFIRMATION_PASS",
    "PHASE_GOAL_CONFIRMED",
    "EXAMPLE_JOB_TYPES_TREATED_AS_EXAMPLES_ONLY",
    "FORBIDDEN_SCOPE_PRESERVED",
    "EXISTING_ARTIFACTS_REFERENCED",
    "IMPLEMENTATION_BOUNDARY_PRESERVED",
    "DAY1_DAY160_REFERENCED",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_FALSE",
    "SECOND_SAFETY_MATRIX_CREATED_FALSE",
    "PHASE_2B_05_DUPLICATED_FALSE",
    "PHASE_2B_06_DUPLICATED_FALSE",
    "PHASE_2B_08_DUPLICATED_FALSE",
    "PHASE_2B_09_DUPLICATED_FALSE",
    "FIRST_SLICE_IMPLEMENTED_FALSE",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_FALSE",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_FALSE",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_FALSE",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2b_10": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2b_10_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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
    if len(example_job_types) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_JOB")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")
    for artifact in REQUIRED_PHASE_2B_REFERENCES:
        if artifact not in artifacts:
            errors.append(f"REQUIRED_PHASE_2B_REFERENCE_MISSING:{artifact}")

    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if tuple(report.get("allowed_reference_behavior", [])) != ALLOWED_REFERENCE_BEHAVIOR:
        errors.append("ALLOWED_REFERENCE_BEHAVIOR_MISMATCH")
    if tuple(report.get("forbidden_reference_behavior", [])) != FORBIDDEN_REFERENCE_BEHAVIOR:
        errors.append("FORBIDDEN_REFERENCE_BEHAVIOR_MISMATCH")

    mapping = report.get("reference_mapping_table", [])
    required_mapping_fields = {
        "future_first_slice_concern",
        "existing_control_or_artifact_to_reference",
        "allowed_use",
        "forbidden_use",
        "reviewer_evidence_expected",
    }
    if not isinstance(mapping, Sequence) or isinstance(mapping, (str, bytes)) or not mapping:
        errors.append("REFERENCE_MAPPING_TABLE_MISSING")
    else:
        for index, row in enumerate(mapping):
            if not isinstance(row, Mapping):
                errors.append(f"REFERENCE_MAPPING_ROW_NOT_OBJECT:{index}")
                continue
            missing_fields = required_mapping_fields.difference(row)
            for field in sorted(missing_fields):
                errors.append(f"REFERENCE_MAPPING_FIELD_MISSING:{index}:{field}")

    if set(report.get("future_first_slice_reviewer_checklist", [])) != set(FUTURE_REVIEWER_CHECKLIST):
        errors.append("FUTURE_REVIEWER_CHECKLIST_MISMATCH")
    if set(report.get("acceptance_criteria", [])) != set(ACCEPTANCE_CRITERIA):
        errors.append("ACCEPTANCE_CRITERIA_MISMATCH")
    if set(report.get("boundary_proof_checklist", [])) != set(BOUNDARY_PROOF_CHECKLIST):
        errors.append("BOUNDARY_PROOF_CHECKLIST_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "PLANNING_ONLY": "YES",
        "DAY1_DAY160_REFERENCED": "YES",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "PHASE_2B_05_DUPLICATED": "NO",
        "PHASE_2B_06_DUPLICATED": "NO",
        "PHASE_2B_08_DUPLICATED": "NO",
        "PHASE_2B_09_DUPLICATED": "NO",
        "FIRST_SLICE_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(artifacts),
        "reference_mapping_rows_checked": len(mapping) if isinstance(mapping, Sequence) else 0,
        "acceptance_criteria_checked": len(report.get("acceptance_criteria", [])),
        "boundary_proof_items_checked": len(report.get("boundary_proof_checklist", [])),
    }


def build_phase_2b_10_day1_day160_reference_mapping_report() -> Dict[str, Any]:
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
            "implementation_boundary": (
                "planning artifact exposure and validation only; no implementation logic, mock runner code, "
                "adapter placeholders, execution paths, network clients, provider clients, secrets paths, "
                "frontend API integration, or production behavior changes"
            ),
            "needs_scope_confirmation": False,
            "scope_narrowed_to_one_example": False,
        },
        "phase_goal": PHASE_GOAL,
        "input_context": {
            "phase_2b_05_role": "Day1-Day160 safety de-duplication acceptance criteria",
            "phase_2b_06_role": "implementation entry gate and first-slice readiness review",
            "phase_2b_08_role": "first-slice implementation authorization gate",
            "phase_2b_09_role": "first-slice implementation plan pack",
            "phase_2b_09_verdict_referenced": PHASE_2B_09_VERDICT,
            "phase_2b_10_role": "reference mapping only",
            "does_not_duplicate_prior_roles": True,
        },
        "reference_mapping_table": list(deepcopy(REFERENCE_MAPPING_TABLE)),
        "de_duplication_proof": {
            "creates_second_safety_matrix": False,
            "day1_day160_controls_remain_authoritative": True,
            "reference_only_usage": True,
            "statement": (
                "Phase 2B-10 maps future first-slice concerns to existing controls only. "
                "It does not copy, rebuild, replace, or create a parallel Day1-Day160 safety matrix."
            ),
        },
        "allowed_reference_behavior": list(ALLOWED_REFERENCE_BEHAVIOR),
        "forbidden_reference_behavior": list(FORBIDDEN_REFERENCE_BEHAVIOR),
        "future_first_slice_reviewer_checklist": list(FUTURE_REVIEWER_CHECKLIST),
        "out_of_scope": list(FORBIDDEN_SCOPE),
        "acceptance_criteria": list(ACCEPTANCE_CRITERIA),
        "boundary_proof_checklist": list(BOUNDARY_PROOF_CHECKLIST),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "example_job_types": list(REQUIRED_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_duplication_statement": (
            "Phase 2B-10 does not duplicate Phase 2B-05, Phase 2B-06, Phase 2B-08, or Phase 2B-09. "
            "It only maps future planning concerns back to those artifacts and existing Day1-Day160 controls."
        ),
        "non_implementation_statement": (
            "This task is planning-only. It does not authorize implementation, implement the first slice, "
            "create runtime behavior, create mock code that looks like a runner or adapter, or enable live, "
            "provider, API, model, or secrets access."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "PLANNING_ONLY": "YES",
            "DAY1_DAY160_REFERENCED": "YES",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "PHASE_2B_05_DUPLICATED": "NO",
            "PHASE_2B_06_DUPLICATED": "NO",
            "PHASE_2B_08_DUPLICATED": "NO",
            "PHASE_2B_09_DUPLICATED": "NO",
            "FIRST_SLICE_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "scope_confirmation": "PASS",
            "phase_goal_confirmed": True,
            "example_job_types_treated_as_examples_only": True,
            "forbidden_scope_preserved": True,
            "existing_artifacts_referenced": True,
            "implementation_boundary_preserved": True,
            "day1_day160_referenced": True,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "phase_2b_05_duplicated": False,
            "phase_2b_06_duplicated": False,
            "phase_2b_08_duplicated": False,
            "phase_2b_09_duplicated": False,
            "first_slice_implemented": False,
            "runner_adapter_execution_path_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "final_verdict": FINAL_VERDICT,
        },
        **SAFETY_FLAGS,
    }
    validation = validate_phase_2b_10_report(report)
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
    write_text_with_parents(
        output_path,
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
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Input Context</h2>
  <table><tbody>{_dict_rows(report["input_context"])}</tbody></table>
  <h2>Reference Mapping Table</h2>
  <table>
    <thead><tr><th>Future first-slice concern</th><th>Existing control or artifact to reference</th><th>Allowed use</th><th>Forbidden use</th><th>Reviewer evidence expected</th></tr></thead>
    <tbody>{_table_rows(report["reference_mapping_table"], ("future_first_slice_concern", "existing_control_or_artifact_to_reference", "allowed_use", "forbidden_use", "reviewer_evidence_expected"))}</tbody>
  </table>
  <h2>Allowed Reference Behavior</h2>
  <ul>{_list_items(report["allowed_reference_behavior"])}</ul>
  <h2>Forbidden Reference Behavior</h2>
  <ul>{_list_items(report["forbidden_reference_behavior"])}</ul>
  <h2>Future First-Slice Reviewer Checklist</h2>
  <ul>{_list_items(report["future_first_slice_reviewer_checklist"])}</ul>
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


def write_phase_2b_10_day1_day160_reference_mapping_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2b_10_day1_day160_reference_mapping_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2b_10_day1_day160_reference_mapping(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2b_10_day1_day160_reference_mapping_report()
    json_path, html_path = write_phase_2b_10_day1_day160_reference_mapping_reports(project_root, report)
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
    print(f"day1_day160_referenced: {str(report['summary']['day1_day160_referenced']).lower()}")
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"phase_2b_05_duplicated: {str(report['summary']['phase_2b_05_duplicated']).lower()}")
    print(f"phase_2b_06_duplicated: {str(report['summary']['phase_2b_06_duplicated']).lower()}")
    print(f"phase_2b_08_duplicated: {str(report['summary']['phase_2b_08_duplicated']).lower()}")
    print(f"phase_2b_09_duplicated: {str(report['summary']['phase_2b_09_duplicated']).lower()}")
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
    print(f"Reference mapping rows checked: {report['validation']['reference_mapping_rows_checked']}")
    print(f"Acceptance criteria checked: {report['validation']['acceptance_criteria_checked']}")
    print(f"Boundary proof items checked: {report['validation']['boundary_proof_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
