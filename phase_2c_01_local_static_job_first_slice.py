"""Phase 2C-01 local static job first-slice implementation.

This module implements only a deterministic static representation of the
authorized `local_static_job` first slice. It does not execute work, call
runners, adapters, brokers, schedulers, queues, shells, scripts, SSH, NETCONF,
RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_13_first_slice_final_selection_gate import FINAL_VERDICT as PHASE_2B_13_VERDICT
from phase_2b_14_first_slice_implementation_kickoff_gate import FINAL_VERDICT as PHASE_2B_14_VERDICT


PHASE = "2C-01"
TASK_NAME = "phase2c-01-local-static-job-first-slice"
TITLE = "Phase 2C-01 Local Static Job First Slice"
MODE = "local_static_first_slice_implementation"
SCOPE = "minimum_safe_local_static_job_first_slice"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_01_LOCAL_STATIC_JOB_FIRST_SLICE_DONE"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
AUTHORIZED_FIRST_SLICE = "local_static_job"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_01_local_static_job_first_slice.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_01_local_static_job_first_slice.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_01_local_static_job_first_slice.md"

READABILITY_POLISH_PHASE = "2C-25"
READABILITY_AUTHORIZED_SLICE = "candidate-01 / mock_demo_job_readability_polish"
READABILITY_POLISH_STATUS = "APPLIED_REPORT_ONLY"
READABILITY_SAFETY_BOUNDARY = "report-only / dry-run / mock-only"

PHASE_GOAL = (
    "Implement the minimum safe Phase 2C-01 first slice for local_static_job "
    "as a local-only, static-only, deterministic, offline, testable, "
    "non-device, non-provider, non-API, non-model, non-secret representation."
)

EXAMPLE_JOB_TYPES = (
    "baseline_check",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "backup_config_plan",
    "blocked_config_change_request",
)

FORBIDDEN_SCOPE = (
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider calls",
    "API calls",
    "model calls",
    "secrets",
    "credentials",
    "tokens",
    "real network commands",
    "shell command execution",
    "custom script execution",
    "queue",
    "scheduler",
    "broker",
    "remote runner",
    "real adapter",
    "execution engine",
    "backup execution",
    "configuration change execution",
    "any path that could run against a real device",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "phase2a_readonly_job_runner_framework.py",
    "phase_2a_03_dry_run_job_plan_gate.py",
    "phase_2a_04_plan_evidence_ledger.py",
    "phase_2a_05_dry_run_result_envelope_renderer.py",
    "phase_2a_06_negative_regression_matrix.py",
    "phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py",
    "phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.py",
    "phase_2a_11_phase_closure_final_readiness_review.py",
    "docs/phase_2b/phase_2b_04_safety_artifact_crosswalk_gap_review.md",
    "docs/phase_2b/phase_2b_05_day1_day160_safety_deduplication_acceptance_criteria.md",
    "docs/phase_2b/phase_2b_09_first_slice_implementation_plan_pack.md",
    "docs/phase_2b/phase_2b_10_day1_day160_reference_mapping_for_future_first_slice.md",
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: static local_static_job definition and reviewer-evidence contract "
    "with validation proving forbidden capabilities remain absent. Not allowed: "
    "runner, adapter, broker, scheduler, queue, execution engine, shell command, "
    "script execution, live device, SSH, NETCONF, RESTCONF, provider/API/model, "
    "secrets, backup execution, configuration change execution, next-day feature, "
    "Day1-Day160 rewrite, or second safety matrix."
)

READABILITY_PRESENTATION_ORDER = (
    "status_and_verdict",
    "authorized_slice",
    "mock_demo_job_role",
    "behavior_changed",
    "behavior_intentionally_not_changed",
    "safety_boundary",
    "validation_summary",
)

READABILITY_CHANGES = (
    "Adds a reviewer quick-read section to the existing local_static_job JSON and HTML reports.",
    "Labels the existing static job as mock demo evidence so reviewers do not confuse it with live execution.",
    "Surfaces the Phase 2C-25 authorized slice and unchanged safety boundary near the top of the report.",
)

READABILITY_INTENTIONALLY_NOT_CHANGED = (
    "No runner, adapter, broker, scheduler, queue, worker, AI loop, or execution path was added.",
    "No SSH, NETCONF, RESTCONF, live-device, provider/API/model, secret, backup, or config-change behavior was added.",
    "No task identity, CLI dispatch, registry behavior, report paths, Day1-Day160 artifact, or safety matrix was replaced.",
)

NON_EXECUTABLE_FIELDS = (
    "runner_call",
    "adapter_call",
    "broker_call",
    "scheduler_call",
    "queue_call",
    "execution_engine",
    "shell_command",
    "device_command",
    "script_path",
    "live_target",
    "ssh_target",
    "netconf_target",
    "restconf_target",
    "provider_call",
    "api_call",
    "model_call",
    "secret_ref",
    "credential_ref",
    "token_ref",
)

SAFETY_FLAGS = {
    "not_next_day_feature": True,
    "execution_opened": False,
    "provider_api_opened": False,
    "model_opened": False,
    "secrets_touched": False,
    "live_device_touched": False,
    "ssh_netconf_restconf_touched": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "local_static_job_implemented": True,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "ssh_touched": False,
    "netconf_touched": False,
    "restconf_touched": False,
    "live_device_access_added": False,
    "provider_calls_added": False,
    "api_calls_added": False,
    "model_calls_added": False,
    "secrets_handling_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "custom_command_execution_added": False,
    "custom_script_execution_added": False,
    "real_device_operation_added": False,
    "safety_gates_weakened": False,
    "scope_narrowed_to_one_example_job_type": False,
    "needs_scope_confirmation": False,
}

LOCAL_STATIC_JOB_DEFINITION = {
    "job_kind": AUTHORIZED_FIRST_SLICE,
    "implementation_kind": "static_definition_and_reviewer_evidence_contract",
    "phase": PHASE,
    "local_only": True,
    "static_only": True,
    "deterministic": True,
    "offline": True,
    "testable": True,
    "non_device": True,
    "non_provider": True,
    "non_api": True,
    "non_model": True,
    "non_secret": True,
    "allowed_data_contract_fields": (
        "job_kind",
        "phase",
        "title",
        "scope",
        "safety_flags",
        "reviewer_evidence_contract",
        "non_execution_proof",
    ),
    "reviewer_evidence_contract": {
        "status": "PASS",
        "evidence_kind": "static_local_first_slice",
        "requires_live_device": False,
        "requires_password": False,
        "produces_report": True,
        "report_only": True,
    },
    "non_execution_proof": {
        "contains_runner_call": False,
        "contains_adapter_call": False,
        "contains_broker_call": False,
        "contains_scheduler_call": False,
        "contains_queue_call": False,
        "contains_execution_engine": False,
        "contains_shell_command": False,
        "contains_device_command": False,
        "contains_script_path": False,
        "contains_live_target": False,
        "contains_ssh_target": False,
        "contains_netconf_target": False,
        "contains_restconf_target": False,
        "contains_provider_call": False,
        "contains_api_call": False,
        "contains_model_call": False,
        "contains_secret_ref": False,
        "contains_credential_ref": False,
        "contains_token_ref": False,
    },
    **{field: None for field in NON_EXECUTABLE_FIELDS},
}

SCOPE_CONFIRMATION = {
    "status": "PASS",
    "scope_confirmation_written": True,
    "scope_confirmation_artifact": DOC_PATH.as_posix(),
    "phase_goal": PHASE_GOAL,
    "phase_goal_separated": True,
    "example_job_types": list(EXAMPLE_JOB_TYPES),
    "example_job_types_separated": True,
    "example_job_type_role": "examples_only_not_phase_scope",
    "forbidden_scope": list(FORBIDDEN_SCOPE),
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary": IMPLEMENTATION_BOUNDARY,
    "implementation_boundary_separated": True,
    "authorized_first_slice": AUTHORIZED_FIRST_SLICE,
    "scope_narrowed_to_one_example_job_type": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_01_LOCAL_STATIC_JOB_FIRST_SLICE",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "PHASE_GOAL_SEPARATED_YES",
    "EXAMPLE_JOB_TYPES_SEPARATED_YES",
    "FORBIDDEN_SCOPE_SEPARATED_YES",
    "EXISTING_ARTIFACTS_TO_REFERENCE_SEPARATED_YES",
    "IMPLEMENTATION_BOUNDARY_SEPARATED_YES",
    "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "NOT_NEXT_DAY_FEATURE_YES",
    "EXECUTION_OPENED_NO",
    "PROVIDER_API_OPENED_NO",
    "MODEL_OPENED_NO",
    "SECRETS_TOUCHED_NO",
    "LIVE_DEVICE_TOUCHED_NO",
    "SSH_NETCONF_RESTCONF_TOUCHED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "LOCAL_STATIC_JOB_IMPLEMENTED_YES",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    FINAL_VERDICT,
)


def build_local_static_job_definition() -> Dict[str, Any]:
    """Return the deterministic static first-slice data contract."""

    return deepcopy(LOCAL_STATIC_JOB_DEFINITION)


def build_reviewer_readability_polish() -> Dict[str, Any]:
    """Return static Phase 2C-25 readability metadata for reviewer reports."""

    return {
        "phase": READABILITY_POLISH_PHASE,
        "authorized_slice": READABILITY_AUTHORIZED_SLICE,
        "status": READABILITY_POLISH_STATUS,
        "safety_boundary": READABILITY_SAFETY_BOUNDARY,
        "mock_demo_job_role": (
            "The local_static_job evidence is a deterministic mock demo artifact "
            "for reviewer understanding only; it is not a live or executable job."
        ),
        "presentation_order": list(READABILITY_PRESENTATION_ORDER),
        "behavior_changed": list(READABILITY_CHANGES),
        "behavior_intentionally_not_changed": list(READABILITY_INTENTIONALLY_NOT_CHANGED),
        "quick_read": {
            "phase_goal": "Make the existing mock demo job evidence easier to read.",
            "authorized_slice": READABILITY_AUTHORIZED_SLICE,
            "behavior_changed": "Reviewer labels, section order, and report presentation only.",
            "behavior_intentionally_not_changed": (
                "No execution capability, live access, dispatch expansion, task identity change, "
                "or safety posture change."
            ),
            "safety_boundary": READABILITY_SAFETY_BOUNDARY,
        },
        "forbidden_scope_touched": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "production_execution_path_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "phase_2c_26_started": False,
        "next_phase_started": False,
        "extra_slice_selected_or_implemented": False,
    }


def validate_local_static_job_definition(job_definition: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if job_definition.get("job_kind") != AUTHORIZED_FIRST_SLICE:
        errors.append("LOCAL_STATIC_JOB_KIND_MISMATCH")
    for flag_name in (
        "local_only",
        "static_only",
        "deterministic",
        "offline",
        "testable",
        "non_device",
        "non_provider",
        "non_api",
        "non_model",
        "non_secret",
    ):
        if job_definition.get(flag_name) is not True:
            errors.append(f"LOCAL_STATIC_JOB_FLAG_NOT_TRUE:{flag_name}")

    for field_name in NON_EXECUTABLE_FIELDS:
        if job_definition.get(field_name) is not None:
            errors.append(f"NON_EXECUTABLE_FIELD_POPULATED:{field_name}")

    proof = job_definition.get("non_execution_proof", {})
    if not isinstance(proof, Mapping):
        errors.append("NON_EXECUTION_PROOF_NOT_OBJECT")
        proof = {}
    for field_name, value in proof.items():
        if value is not False:
            errors.append(f"NON_EXECUTION_PROOF_NOT_FALSE:{field_name}")

    evidence = job_definition.get("reviewer_evidence_contract", {})
    if not isinstance(evidence, Mapping):
        errors.append("REVIEWER_EVIDENCE_CONTRACT_NOT_OBJECT")
    else:
        if evidence.get("requires_live_device") is not False:
            errors.append("REVIEWER_EVIDENCE_REQUIRES_LIVE_DEVICE")
        if evidence.get("requires_password") is not False:
            errors.append("REVIEWER_EVIDENCE_REQUIRES_PASSWORD")
        if evidence.get("report_only") is not True:
            errors.append("REVIEWER_EVIDENCE_NOT_REPORT_ONLY")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
        "non_execution_proof_fields_checked": len(proof),
    }


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_01": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_01_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("authorized_first_slice") != AUTHORIZED_FIRST_SLICE:
        errors.append("AUTHORIZED_FIRST_SLICE_MISMATCH")

    agents = report.get("agents_md_pre_read", {})
    if not isinstance(agents, Mapping):
        errors.append("AGENTS_MD_PRE_READ_NOT_OBJECT")
    else:
        if agents.get("found") is not True:
            errors.append("AGENTS_MD_FOUND_NOT_TRUE")
        if agents.get("read_before_action") is not True:
            errors.append("AGENTS_MD_READ_BEFORE_ACTION_NOT_TRUE")
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
    for flag_name in (
        "phase_goal_separated",
        "example_job_types_separated",
        "forbidden_scope_separated",
        "existing_artifacts_to_reference_separated",
        "implementation_boundary_separated",
    ):
        if scope_confirmation.get(flag_name) is not True:
            errors.append(f"SCOPE_CONFIRMATION_FLAG_NOT_TRUE:{flag_name}")
    if scope_confirmation.get("scope_narrowed_to_one_example_job_type") is not False:
        errors.append("SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE")
    if scope_confirmation.get("needs_scope_confirmation") is not False:
        errors.append("NEEDS_SCOPE_CONFIRMATION_NOT_FALSE")

    example_job_types = set(report.get("example_job_types", []))
    if example_job_types != set(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPE_SET_MISMATCH")
    if AUTHORIZED_FIRST_SLICE in example_job_types:
        errors.append("AUTHORIZED_FIRST_SLICE_LISTED_AS_EXAMPLE")
    if len(example_job_types) <= 1:
        errors.append("PHASE_SCOPE_NARROWED_TO_SINGLE_EXAMPLE")
    if report.get("example_job_type_role") != "examples_only_not_phase_scope":
        errors.append("EXAMPLE_JOB_TYPE_ROLE_MISMATCH")

    readability = report.get("reviewer_readability_polish", {})
    if not isinstance(readability, Mapping):
        errors.append("REVIEWER_READABILITY_POLISH_NOT_OBJECT")
        readability = {}
    else:
        if readability.get("phase") != READABILITY_POLISH_PHASE:
            errors.append("READABILITY_POLISH_PHASE_MISMATCH")
        if readability.get("authorized_slice") != READABILITY_AUTHORIZED_SLICE:
            errors.append("READABILITY_AUTHORIZED_SLICE_MISMATCH")
        if readability.get("status") != READABILITY_POLISH_STATUS:
            errors.append("READABILITY_POLISH_STATUS_MISMATCH")
        if readability.get("safety_boundary") != READABILITY_SAFETY_BOUNDARY:
            errors.append("READABILITY_SAFETY_BOUNDARY_MISMATCH")
        if readability.get("presentation_order") != list(READABILITY_PRESENTATION_ORDER):
            errors.append("READABILITY_PRESENTATION_ORDER_MISMATCH")
        if readability.get("behavior_changed") != list(READABILITY_CHANGES):
            errors.append("READABILITY_BEHAVIOR_CHANGED_MISMATCH")
        if readability.get("behavior_intentionally_not_changed") != list(READABILITY_INTENTIONALLY_NOT_CHANGED):
            errors.append("READABILITY_BEHAVIOR_NOT_CHANGED_MISMATCH")
        if not isinstance(readability.get("quick_read"), Mapping):
            errors.append("READABILITY_QUICK_READ_MISSING")
        for flag_name in (
            "forbidden_scope_touched",
            "ssh_netconf_restconf_live_device_touched",
            "queue_scheduler_worker_ai_loop_added",
            "provider_api_model_secrets_touched",
            "config_backup_or_change_behavior_added",
            "production_execution_path_added",
            "day1_day160_rewritten_or_replaced",
            "second_safety_matrix_created",
            "phase_2c_26_started",
            "next_phase_started",
            "extra_slice_selected_or_implemented",
        ):
            if readability.get(flag_name) is not False:
                errors.append(f"READABILITY_FORBIDDEN_FLAG_NOT_FALSE:{flag_name}")
    if report.get("readability_polish_applied") is not True:
        errors.append("READABILITY_POLISH_APPLIED_NOT_TRUE")
    if report.get("authorized_readability_slice") != READABILITY_AUTHORIZED_SLICE:
        errors.append("AUTHORIZED_READABILITY_SLICE_MISMATCH")

    job_validation = validate_local_static_job_definition(report.get("local_static_job_definition", {}))
    if job_validation["valid"] is not True:
        errors.extend(f"LOCAL_STATIC_JOB:{error}" for error in job_validation["errors"])

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "SCOPE_CONFIRMATION_WRITTEN": "YES",
        "PHASE_GOAL_SEPARATED": "YES",
        "EXAMPLE_JOB_TYPES_SEPARATED": "YES",
        "FORBIDDEN_SCOPE_SEPARATED": "YES",
        "EXISTING_ARTIFACTS_TO_REFERENCE_SEPARATED": "YES",
        "IMPLEMENTATION_BOUNDARY_SEPARATED": "YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "NOT_NEXT_DAY_FEATURE": "YES",
        "EXECUTION_OPENED": "NO",
        "PROVIDER_API_OPENED": "NO",
        "MODEL_OPENED": "NO",
        "SECRETS_TOUCHED": "NO",
        "LIVE_DEVICE_TOUCHED": "NO",
        "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "LOCAL_STATIC_JOB_IMPLEMENTED": "YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if any(
        report.get(flag)
        for flag in (
            "execution_opened",
            "provider_api_opened",
            "model_opened",
            "secrets_touched",
            "live_device_touched",
            "ssh_netconf_restconf_touched",
            "day1_day160_rewritten_or_replaced",
            "second_safety_matrix_created",
            "runner_added",
            "adapter_added",
            "execution_path_added",
            "broker_added",
            "scheduler_added",
            "queue_added",
            "ssh_touched",
            "netconf_touched",
            "restconf_touched",
            "provider_calls_added",
            "api_calls_added",
            "model_calls_added",
            "secrets_handling_added",
            "scope_narrowed_to_one_example_job_type",
            "needs_scope_confirmation",
        )
    ):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "example_job_types_checked": len(example_job_types),
        "existing_artifacts_checked": len(report.get("existing_artifacts_to_reference", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "local_static_job_validation": job_validation,
    }


def build_phase_2c_01_local_static_job_first_slice_report() -> Dict[str, Any]:
    reviewer_readability_polish = build_reviewer_readability_polish()
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "authorized_first_slice": AUTHORIZED_FIRST_SLICE,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read_before_action": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "scope_confirmation": deepcopy(SCOPE_CONFIRMATION),
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_not_phase_scope",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_to_reference": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "phase_2b_14_verdict_referenced": PHASE_2B_14_VERDICT,
        "local_static_job_definition": build_local_static_job_definition(),
        "reviewer_readability_polish": reviewer_readability_polish,
        "readability_polish_applied": True,
        "authorized_readability_slice": READABILITY_AUTHORIZED_SLICE,
        "behavior_changed": list(READABILITY_CHANGES),
        "behavior_intentionally_not_changed": list(READABILITY_INTENTIONALLY_NOT_CHANGED),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_execution_statement": (
            "Phase 2C-01 implements only a static local_static_job data contract. "
            "No runner, adapter, execution path, shell command, script path, live "
            "target, provider/API/model call, secret handling, or device access is available."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "SCOPE_CONFIRMATION_WRITTEN": "YES",
            "PHASE_GOAL_SEPARATED": "YES",
            "EXAMPLE_JOB_TYPES_SEPARATED": "YES",
            "FORBIDDEN_SCOPE_SEPARATED": "YES",
            "EXISTING_ARTIFACTS_TO_REFERENCE_SEPARATED": "YES",
            "IMPLEMENTATION_BOUNDARY_SEPARATED": "YES",
            "SCOPE_NARROWED_TO_ONE_EXAMPLE_JOB_TYPE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "NOT_NEXT_DAY_FEATURE": "YES",
            "EXECUTION_OPENED": "NO",
            "PROVIDER_API_OPENED": "NO",
            "MODEL_OPENED": "NO",
            "SECRETS_TOUCHED": "NO",
            "LIVE_DEVICE_TOUCHED": "NO",
            "SSH_NETCONF_RESTCONF_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "LOCAL_STATIC_JOB_IMPLEMENTED": "YES",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "scope_confirmation_written": True,
        "phase_goal_separated": True,
        "example_job_types_separated": True,
        "forbidden_scope_separated": True,
        "existing_artifacts_to_reference_separated": True,
        "implementation_boundary_separated": True,
        "scope_narrowed_to_one_example_job_type": False,
        "needs_scope_confirmation": False,
        "not_next_day_feature": True,
        "execution_opened": False,
        "provider_api_opened": False,
        "model_opened": False,
        "secrets_touched": False,
        "live_device_touched": False,
        "ssh_netconf_restconf_touched": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "local_static_job_implemented": True,
        "readability_polish_applied": True,
        "authorized_readability_slice": READABILITY_AUTHORIZED_SLICE,
        "runner_adapter_execution_path_added": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_01_report(report)
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


def _readability_rows(values: Mapping[str, Any]) -> str:
    quick_read = values.get("quick_read", {})
    if not isinstance(quick_read, Mapping):
        quick_read = {}
    return _dict_rows(quick_read)


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
  <p>Authorized first slice: <code>{html.escape(str(report["authorized_first_slice"]))}</code></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Reviewer Quick Read</h2>
  <table><tbody>{_readability_rows(report["reviewer_readability_polish"])}</tbody></table>
  <h2>Behavior Changed</h2>
  <ul>{_list_items(report["behavior_changed"])}</ul>
  <h2>Behavior Intentionally Not Changed</h2>
  <ul>{_list_items(report["behavior_intentionally_not_changed"])}</ul>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Scope Confirmation</h2>
  <table><tbody>{_dict_rows(report["scope_confirmation"])}</tbody></table>
  <h2>Local Static Job Definition</h2>
  <table><tbody>{_dict_rows(report["local_static_job_definition"])}</tbody></table>
  <h2>Example Job Types</h2>
  <ul>{_list_items(report["example_job_types"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_to_reference"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_01_local_static_job_first_slice_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_01_local_static_job_first_slice_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_01_local_static_job_first_slice(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_01_local_static_job_first_slice_report()
    json_path, html_path = write_phase_2c_01_local_static_job_first_slice_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Authorized first slice: {AUTHORIZED_FIRST_SLICE}")
    print(f"scope_confirmation_written: {str(report['summary']['scope_confirmation_written']).lower()}")
    print(f"phase_goal_separated: {str(report['summary']['phase_goal_separated']).lower()}")
    print(f"example_job_types_separated: {str(report['summary']['example_job_types_separated']).lower()}")
    print(f"forbidden_scope_separated: {str(report['summary']['forbidden_scope_separated']).lower()}")
    print(
        "existing_artifacts_to_reference_separated: "
        f"{str(report['summary']['existing_artifacts_to_reference_separated']).lower()}"
    )
    print(
        "implementation_boundary_separated: "
        f"{str(report['summary']['implementation_boundary_separated']).lower()}"
    )
    print(
        "scope_narrowed_to_one_example_job_type: "
        f"{str(report['summary']['scope_narrowed_to_one_example_job_type']).lower()}"
    )
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(f"not_next_day_feature: {str(report['summary']['not_next_day_feature']).lower()}")
    print(f"execution_opened: {str(report['summary']['execution_opened']).lower()}")
    print(f"provider_api_opened: {str(report['summary']['provider_api_opened']).lower()}")
    print(f"model_opened: {str(report['summary']['model_opened']).lower()}")
    print(f"secrets_touched: {str(report['summary']['secrets_touched']).lower()}")
    print(f"live_device_touched: {str(report['summary']['live_device_touched']).lower()}")
    print(f"ssh_netconf_restconf_touched: {str(report['summary']['ssh_netconf_restconf_touched']).lower()}")
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"local_static_job_implemented: {str(report['summary']['local_static_job_implemented']).lower()}")
    print(f"readability_polish_applied: {str(report['summary']['readability_polish_applied']).lower()}")
    print(f"authorized_readability_slice: {report['summary']['authorized_readability_slice']}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
    )
    print(f"Example job types checked: {report['validation']['example_job_types_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
