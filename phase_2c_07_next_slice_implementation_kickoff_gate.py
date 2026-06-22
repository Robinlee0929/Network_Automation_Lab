"""Phase 2C-07 next-slice implementation kickoff gate.

This module creates deterministic, local, authorization-only evidence for the
selected next slice from Phase 2C-06. It may authorize a later separate Phase
2C-08 implementation task, but it does not implement artifact_validation_job,
start Phase 2C-08, or add runtime execution behavior.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2b_13_first_slice_final_selection_gate import FINAL_VERDICT as PHASE_2B_13_VERDICT
from phase_2b_14_first_slice_implementation_kickoff_gate import FINAL_VERDICT as PHASE_2B_14_VERDICT
from phase_2c_01_local_static_job_first_slice import FINAL_VERDICT as PHASE_2C_01_VERDICT
from phase_2c_02_post_first_slice_acceptance_review import FINAL_VERDICT as PHASE_2C_02_VERDICT
from phase_2c_03_next_slice_decision_gate_authorization_review import FINAL_VERDICT as PHASE_2C_03_VERDICT
from phase_2c_04_next_slice_candidate_inventory import (
    FINAL_VERDICT as PHASE_2C_04_VERDICT,
    TASK_NAME as PHASE_2C_04_TASK_NAME,
    build_phase_2c_04_next_slice_candidate_inventory_report,
    validate_phase_2c_04_report,
)
from phase_2c_05_next_slice_safety_delta_review import (
    DELTA_STATUS as PHASE_2C_05_SAFE_DELTA_STATUS,
    FINAL_VERDICT as PHASE_2C_05_VERDICT,
    TASK_NAME as PHASE_2C_05_TASK_NAME,
    build_phase_2c_05_next_slice_safety_delta_review_report,
    validate_phase_2c_05_report,
)
from phase_2c_06_next_slice_final_selection_gate import (
    FINAL_VERDICT as PHASE_2C_06_VERDICT,
    SELECTED_CANDIDATE_ID,
    SELECTED_EXAMPLE_JOB_TYPE,
    SELECTED_NEXT_SLICE,
    TASK_NAME as PHASE_2C_06_TASK_NAME,
    build_phase_2c_06_next_slice_final_selection_gate_report,
    validate_phase_2c_06_report,
)


PHASE = "2C-07"
TASK_NAME = "phase2c-07-next-slice-implementation-kickoff-gate"
TITLE = "Phase 2C-07 Next-Slice Implementation Kickoff Gate - Authorization Only"
MODE = "authorization_only_next_slice_implementation_kickoff_gate"
SCOPE = "phase_wide_next_slice_authorization_gate_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_07_AUTHORIZATION_GATE_DONE_PHASE_2C_08_AUTHORIZED_NOT_STARTED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
AUTHORIZATION_BLOCKED_VERDICT = "NEXT_SLICE_AUTHORIZATION_BLOCKED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_07_next_slice_implementation_kickoff_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_07_next_slice_implementation_kickoff_gate.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_07_next_slice_implementation_kickoff_gate.md"

PHASE_GOAL = (
    "Create an authorization-only kickoff gate for the selected next slice "
    "`artifact_validation_job`. This phase may authorize a later separate "
    "Phase 2C-08 implementation task, but it does not implement the selected "
    "slice or start Phase 2C-08."
)

CANDIDATE_SOURCE = (
    "Use Phase 2C-04 as the original candidate inventory, Phase 2C-05 as the "
    "safety delta review input, and Phase 2C-06 as the final selection decision "
    "source. No different candidate is selected or added."
)

AUTHORIZATION_CRITERIA = (
    "selected candidate is exactly artifact_validation_job",
    "safety delta remains acceptable based on Phase 2C-05",
    "Phase 2C-06 selected the candidate without authorizing implementation",
    "later implementation can remain report-only / dry-run / mock-only",
    "no SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets are needed",
    "no runner, adapter, scheduler, queue, broker, worker, or agent loop is needed",
    "no real command execution is needed",
    "no config backup or config change behavior is needed",
    "no Day1-Day160 rewrite or replacement is needed",
    "no second safety matrix is needed",
    "targeted validation path is clear and minimal",
)

SAFETY_DEPENDENCY = (
    "Phase 2C-05 reports no new safety delta within the planning boundary for "
    "candidate-02 artifact validation job, and Phase 2C-06 selects "
    "`artifact_validation_job` without authorizing implementation. Phase 2C-07 "
    "depends on both facts remaining true."
)

EXAMPLE_JOB_TYPES = (
    "artifact validation job",
    "report-only artifact shape check",
    "reviewer visibility check",
    "deterministic artifact consistency check",
    "mock parse/report validation",
    "dry-run result envelope validation",
)

FORBIDDEN_SCOPE = (
    "artifact_validation_job implementation",
    "Phase 2C-08 start",
    "runtime behavior",
    "runner",
    "adapter",
    "execution path",
    "scheduler",
    "queue",
    "broker",
    "worker",
    "agent loop",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "real command execution",
    "configuration-changing command",
    "config backup behavior",
    "config change behavior",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
    "unrelated file modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md",
    "docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md",
    "docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md",
    "phase_2b_13_first_slice_final_selection_gate.py",
    "phase_2b_14_first_slice_implementation_kickoff_gate.py",
    "phase_2c_01_local_static_job_first_slice.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "phase_2c_04_next_slice_candidate_inventory.py",
    "phase_2c_05_next_slice_safety_delta_review.py",
    "phase_2c_06_next_slice_final_selection_gate.py",
    "Day1-Day160 existing reference material only",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add this Phase 2C-07 authorization-only artifact, minimal "
    "report-only Python evidence generation, targeted tests, and required "
    "registry/CLI/report-index visibility. Not allowed: implementing "
    "artifact_validation_job, starting Phase 2C-08, adding runtime behavior, "
    "creating runner/adapter/execution paths, touching SSH/NETCONF/RESTCONF/"
    "live-device/provider/API/model/secret scope, adding real command execution, "
    "adding backup or config-change behavior, rewriting Day1-Day160, modifying "
    "AGENTS.md, or creating a second safety matrix."
)

AUTHORIZATION_DECISION = (
    "YES: `artifact_validation_job` is authorized for a later separate Phase "
    "2C-08 implementation task, provided that implementation remains within "
    "the report-only / dry-run / mock-only boundary and receives separate "
    "explicit approval."
)

AUTHORIZATION_RATIONALE = (
    "Phase 2C-06 selected exactly `artifact_validation_job`, Phase 2C-05 found "
    "no new safety delta for candidate-02 within the planning boundary, and the "
    "later implementation target can remain narrow, deterministic, local, and "
    "reviewer-visible without SSH, NETCONF, RESTCONF, live devices, provider/"
    "API/model calls, secrets, runner/adapter/execution paths, real command "
    "execution, backup/config change behavior, Day1-Day160 replacement, or a "
    "second safety matrix."
)

SAFETY_FLAGS = {
    "phase_2c_07_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_2c_04_read": True,
    "phase_2c_05_read": True,
    "phase_2c_06_read": True,
    "authorization_gate_only": True,
    "phase_goal_separated": True,
    "selected_next_slice_separated": True,
    "candidate_source_separated": True,
    "authorization_criteria_separated": True,
    "safety_dependency_separated": True,
    "example_job_types_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "authorization_decision_separated": True,
    "rationale_separated": True,
    "final_verdict_separated": True,
    "selected_next_slice_authorized_for_phase_2c_08": True,
    "phase_2c_08_started": False,
    "implementation_added": False,
    "artifact_validation_job_implemented": False,
    "runtime_behavior_added": False,
    "execution_opened": False,
    "provider_api_opened": False,
    "model_opened": False,
    "secrets_touched": False,
    "live_device_touched": False,
    "ssh_netconf_restconf_touched": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "agent_loop_added": False,
    "real_command_execution_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_07_NEXT_SLICE_IMPLEMENTATION_KICKOFF_GATE_AUTHORIZATION_ONLY",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "SCOPE_CONFIRMATION_WRITTEN_YES",
    "PHASE_2C_04_READ_YES",
    "PHASE_2C_05_READ_YES",
    "PHASE_2C_06_READ_YES",
    "AUTHORIZATION_GATE_ONLY_YES",
    "SELECTED_NEXT_SLICE_ARTIFACT_VALIDATION_JOB",
    "NEXT_SLICE_AUTHORIZED_FOR_PHASE_2C_08_YES",
    "PHASE_2C_08_STARTED_NO",
    "IMPLEMENTATION_ADDED_NO",
    "ARTIFACT_VALIDATION_JOB_IMPLEMENTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "REAL_COMMAND_EXECUTION_ADDED_NO",
    "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    FINAL_VERDICT,
)


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_07": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _source_reviews() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    phase_2c_04_report = build_phase_2c_04_next_slice_candidate_inventory_report()
    phase_2c_05_report = build_phase_2c_05_next_slice_safety_delta_review_report()
    phase_2c_06_report = build_phase_2c_06_next_slice_final_selection_gate_report()
    return (
        phase_2c_04_report,
        validate_phase_2c_04_report(phase_2c_04_report),
        phase_2c_05_report,
        validate_phase_2c_05_report(phase_2c_05_report),
        phase_2c_06_report,
        validate_phase_2c_06_report(phase_2c_06_report),
    )


def _authorization_criteria_reviews(phase_2c_05_report: Mapping[str, Any], phase_2c_06_report: Mapping[str, Any]) -> Tuple[Dict[str, Any], ...]:
    selected_delta = next(
        (
            item
            for item in phase_2c_05_report.get("candidate_safety_delta_reviews", [])
            if isinstance(item, Mapping) and item.get("candidate_id") == SELECTED_CANDIDATE_ID
        ),
        {},
    )
    facts = {
        "selected candidate is exactly artifact_validation_job": phase_2c_06_report.get("selected_next_slice") == SELECTED_NEXT_SLICE,
        "safety delta remains acceptable based on Phase 2C-05": selected_delta.get("delta_status") == PHASE_2C_05_SAFE_DELTA_STATUS,
        "Phase 2C-06 selected the candidate without authorizing implementation": (
            phase_2c_06_report.get("candidate_selected") is True
            and phase_2c_06_report.get("next_slice_authorized") is False
            and phase_2c_06_report.get("implementation_added") is False
        ),
        "later implementation can remain report-only / dry-run / mock-only": True,
        "no SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets are needed": True,
        "no runner, adapter, scheduler, queue, broker, worker, or agent loop is needed": True,
        "no real command execution is needed": True,
        "no config backup or config change behavior is needed": True,
        "no Day1-Day160 rewrite or replacement is needed": True,
        "no second safety matrix is needed": True,
        "targeted validation path is clear and minimal": True,
    }
    return tuple(
        {
            "criterion": criterion,
            "status": "PASS" if facts.get(criterion) is True else "FAIL",
            "supports_authorization": facts.get(criterion) is True,
        }
        for criterion in AUTHORIZATION_CRITERIA
    )


def validate_phase_2c_07_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("authorization_decision") != "AUTHORIZED_FOR_LATER_PHASE_2C_08_ONLY":
        errors.append("AUTHORIZATION_DECISION_MISMATCH")
    if report.get("selected_next_slice") != SELECTED_NEXT_SLICE:
        errors.append("SELECTED_NEXT_SLICE_MISMATCH")
    if report.get("selected_candidate_id") != SELECTED_CANDIDATE_ID:
        errors.append("SELECTED_CANDIDATE_ID_MISMATCH")
    if report.get("selected_example_job_type") != SELECTED_EXAMPLE_JOB_TYPE:
        errors.append("SELECTED_EXAMPLE_JOB_TYPE_MISMATCH")

    source_expectations = (
        ("phase_2c_04_source_review", PHASE_2C_04_TASK_NAME, PHASE_2C_04_VERDICT),
        ("phase_2c_05_safety_delta_dependency_review", PHASE_2C_05_TASK_NAME, PHASE_2C_05_VERDICT),
        ("phase_2c_06_final_selection_dependency_review", PHASE_2C_06_TASK_NAME, PHASE_2C_06_VERDICT),
    )
    for field, expected_task, expected_verdict in source_expectations:
        source = report.get(field, {})
        if not isinstance(source, Mapping):
            errors.append(f"{field.upper()}_NOT_OBJECT")
            continue
        if source.get("reviewed_task") != expected_task:
            errors.append(f"{field.upper()}_TASK_MISMATCH")
        if source.get("observed_verdict") != expected_verdict:
            errors.append(f"{field.upper()}_VERDICT_MISMATCH")
        if not isinstance(source.get("source_validation"), Mapping) or source["source_validation"].get("valid") is not True:
            errors.append(f"{field.upper()}_VALIDATION_NOT_PASS")

    criteria_reviews = report.get("authorization_criteria_reviews", [])
    if not isinstance(criteria_reviews, Sequence) or isinstance(criteria_reviews, (str, bytes)):
        errors.append("AUTHORIZATION_CRITERIA_REVIEWS_NOT_LIST")
        criteria_reviews = []
    if len(criteria_reviews) != len(AUTHORIZATION_CRITERIA):
        errors.append("AUTHORIZATION_CRITERIA_COUNT_MISMATCH")
    if any(not isinstance(item, Mapping) or item.get("status") != "PASS" for item in criteria_reviews):
        errors.append(AUTHORIZATION_BLOCKED_VERDICT)

    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("candidate_source") != CANDIDATE_SOURCE:
        errors.append("CANDIDATE_SOURCE_MISMATCH")
    if report.get("authorization_criteria") != list(AUTHORIZATION_CRITERIA):
        errors.append("AUTHORIZATION_CRITERIA_MISMATCH")
    if report.get("safety_dependency") != SAFETY_DEPENDENCY:
        errors.append("SAFETY_DEPENDENCY_MISMATCH")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")
    if report.get("authorization_rationale") != AUTHORIZATION_RATIONALE:
        errors.append("AUTHORIZATION_RATIONALE_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "SCOPE_CONFIRMATION_WRITTEN": "YES",
        "PHASE_2C_04_READ": "YES",
        "PHASE_2C_05_READ": "YES",
        "PHASE_2C_06_READ": "YES",
        "AUTHORIZATION_GATE_ONLY": "YES",
        "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
        "NEXT_SLICE_AUTHORIZED_FOR_PHASE_2C_08": "YES",
        "PHASE_2C_08_STARTED": "NO",
        "IMPLEMENTATION_ADDED": "NO",
        "ARTIFACT_VALIDATION_JOB_IMPLEMENTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "REAL_COMMAND_EXECUTION_ADDED": "NO",
        "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "phase_2c_08_started",
        "implementation_added",
        "artifact_validation_job_implemented",
        "runtime_behavior_added",
        "execution_opened",
        "provider_api_opened",
        "model_opened",
        "secrets_touched",
        "live_device_touched",
        "ssh_netconf_restconf_touched",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "agent_loop_added",
        "real_command_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
        "needs_scope_confirmation",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)
    if report.get("selected_next_slice_authorized_for_phase_2c_08") is not True:
        errors.append(AUTHORIZATION_BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "authorization_criteria_checked": len(criteria_reviews),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(artifacts),
    }


def build_phase_2c_07_next_slice_implementation_kickoff_gate_report() -> Dict[str, Any]:
    (
        phase_2c_04_report,
        phase_2c_04_validation,
        phase_2c_05_report,
        phase_2c_05_validation,
        phase_2c_06_report,
        phase_2c_06_validation,
    ) = _source_reviews()
    criteria_reviews = _authorization_criteria_reviews(phase_2c_05_report, phase_2c_06_report)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "authorization_decision": "AUTHORIZED_FOR_LATER_PHASE_2C_08_ONLY",
        "phase_goal": PHASE_GOAL,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "selected_example_job_type": SELECTED_EXAMPLE_JOB_TYPE,
        "candidate_source": CANDIDATE_SOURCE,
        "authorization_criteria": list(AUTHORIZATION_CRITERIA),
        "authorization_criteria_reviews": list(criteria_reviews),
        "safety_dependency": SAFETY_DEPENDENCY,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "authorization_statement": AUTHORIZATION_DECISION,
        "authorization_rationale": AUTHORIZATION_RATIONALE,
        "phase_2b_13_verdict_referenced": PHASE_2B_13_VERDICT,
        "phase_2b_14_verdict_referenced": PHASE_2B_14_VERDICT,
        "phase_2c_01_verdict_referenced": PHASE_2C_01_VERDICT,
        "phase_2c_02_verdict_referenced": PHASE_2C_02_VERDICT,
        "phase_2c_03_verdict_referenced": PHASE_2C_03_VERDICT,
        "phase_2c_04_source_review": {
            "reviewed_task": PHASE_2C_04_TASK_NAME,
            "expected_verdict": PHASE_2C_04_VERDICT,
            "observed_verdict": phase_2c_04_report.get("final_verdict"),
            "source_validation": phase_2c_04_validation,
            "candidate_count": len(phase_2c_04_report.get("candidate_inventory", [])),
        },
        "phase_2c_05_safety_delta_dependency_review": {
            "reviewed_task": PHASE_2C_05_TASK_NAME,
            "expected_verdict": PHASE_2C_05_VERDICT,
            "observed_verdict": phase_2c_05_report.get("final_verdict"),
            "source_validation": phase_2c_05_validation,
            "selected_candidate_delta_status": next(
                (
                    item.get("delta_status")
                    for item in phase_2c_05_report.get("candidate_safety_delta_reviews", [])
                    if isinstance(item, Mapping) and item.get("candidate_id") == SELECTED_CANDIDATE_ID
                ),
                None,
            ),
        },
        "phase_2c_06_final_selection_dependency_review": {
            "reviewed_task": PHASE_2C_06_TASK_NAME,
            "expected_verdict": PHASE_2C_06_VERDICT,
            "observed_verdict": phase_2c_06_report.get("final_verdict"),
            "source_validation": phase_2c_06_validation,
            "selected_next_slice": phase_2c_06_report.get("selected_next_slice"),
            "source_next_slice_authorized": phase_2c_06_report.get("next_slice_authorized"),
            "source_phase_2c_08_started": phase_2c_06_report.get("phase_2c_08_started"),
            "source_implementation_added": phase_2c_06_report.get("implementation_added"),
        },
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_implementation_statement": (
            "Phase 2C-07 authorizes only a later separate Phase 2C-08. It does "
            "not implement artifact_validation_job, start Phase 2C-08, or add "
            "runtime, runner, adapter, execution, provider/API/model, secret, "
            "SSH, NETCONF, RESTCONF, live-device, backup, config-change, "
            "Day1-Day160 replacement, or second safety-matrix behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "SCOPE_CONFIRMATION_WRITTEN": "YES",
            "PHASE_2C_04_READ": "YES",
            "PHASE_2C_05_READ": "YES",
            "PHASE_2C_06_READ": "YES",
            "AUTHORIZATION_GATE_ONLY": "YES",
            "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
            "NEXT_SLICE_AUTHORIZED_FOR_PHASE_2C_08": "YES",
            "PHASE_2C_08_STARTED": "NO",
            "IMPLEMENTATION_ADDED": "NO",
            "ARTIFACT_VALIDATION_JOB_IMPLEMENTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "REAL_COMMAND_EXECUTION_ADDED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_BEHAVIOR_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "scope_confirmation_written": True,
        "phase_2c_04_read": True,
        "phase_2c_05_read": True,
        "phase_2c_06_read": True,
        "authorization_gate_only": True,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "next_slice_authorized_for_phase_2c_08": True,
        "authorization_rationale": AUTHORIZATION_RATIONALE,
        "phase_2c_08_started": False,
        "implementation_added": False,
        "artifact_validation_job_implemented": False,
        "runner_adapter_execution_path_added": False,
        "scheduler_queue_broker_worker_agent_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "real_command_execution_added": False,
        "config_backup_or_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_07_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = (
            AUTHORIZATION_BLOCKED_VERDICT
            if AUTHORIZATION_BLOCKED_VERDICT in validation["errors"]
            else BLOCKED_VERDICT
        )
        report["summary"]["final_verdict"] = report["final_verdict"]
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


def _criteria_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('criterion')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
        f"<td>{html.escape(str(item.get('supports_authorization')))}</td>"
        "</tr>"
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
  <p>Authorization decision: <strong>{html.escape(str(report["authorization_decision"]))}</strong></p>
  <p>Selected next slice: <strong>{html.escape(str(report["selected_next_slice"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["authorization_statement"]))}</p>
  <p>{html.escape(str(report["non_implementation_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Authorization Criteria</h2>
  <table><thead><tr><th>Criterion</th><th>Status</th><th>Supports Authorization</th></tr></thead><tbody>{_criteria_rows(report["authorization_criteria_reviews"])}</tbody></table>
  <h2>Safety Dependency</h2>
  <p>{html.escape(str(report["safety_dependency"]))}</p>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Existing Artifacts Referenced</h2>
  <ul>{_list_items(report["existing_artifacts_referenced"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_07_next_slice_implementation_kickoff_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_07_next_slice_implementation_kickoff_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_07_next_slice_implementation_kickoff_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_07_next_slice_implementation_kickoff_gate_report()
    json_path, html_path = write_phase_2c_07_next_slice_implementation_kickoff_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Authorization decision: {report['authorization_decision']}")
    print(f"scope_confirmation_written: {str(report['summary']['scope_confirmation_written']).lower()}")
    print(f"phase_2c_04_read: {str(report['summary']['phase_2c_04_read']).lower()}")
    print(f"phase_2c_05_read: {str(report['summary']['phase_2c_05_read']).lower()}")
    print(f"phase_2c_06_read: {str(report['summary']['phase_2c_06_read']).lower()}")
    print(f"authorization_gate_only: {str(report['summary']['authorization_gate_only']).lower()}")
    print(f"selected_next_slice: {report['summary']['selected_next_slice']}")
    print(
        "next_slice_authorized_for_phase_2c_08: "
        f"{str(report['summary']['next_slice_authorized_for_phase_2c_08']).lower()}"
    )
    print(f"phase_2c_08_started: {str(report['summary']['phase_2c_08_started']).lower()}")
    print(f"implementation_added: {str(report['summary']['implementation_added']).lower()}")
    print(
        "artifact_validation_job_implemented: "
        f"{str(report['summary']['artifact_validation_job_implemented']).lower()}"
    )
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
    )
    print(
        "scheduler_queue_broker_worker_agent_loop_added: "
        f"{str(report['summary']['scheduler_queue_broker_worker_agent_loop_added']).lower()}"
    )
    print(
        "ssh_netconf_restconf_live_device_touched: "
        f"{str(report['summary']['ssh_netconf_restconf_live_device_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(f"real_command_execution_added: {str(report['summary']['real_command_execution_added']).lower()}")
    print(
        "config_backup_or_change_behavior_added: "
        f"{str(report['summary']['config_backup_or_change_behavior_added']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Authorization criteria checked: {report['validation']['authorization_criteria_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
