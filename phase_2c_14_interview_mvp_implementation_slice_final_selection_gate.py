"""Phase 2C-14 Interview MVP implementation slice final selection gate.

This module creates deterministic, local, planning-only evidence that selects
exactly one next Interview MVP implementation slice from Phase 2C-12 using the
Phase 2C-13 safety delta review as the required decision basis. It does not
authorize, scaffold, implement, execute, or prepare execution for the selected
slice.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents
from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_12_interview_mvp_implementation_slice_candidate_inventory import (
    CANDIDATE_INVENTORY as PHASE_2C_12_CANDIDATE_INVENTORY,
    FINAL_VERDICT as PHASE_2C_12_VERDICT,
    TASK_NAME as PHASE_2C_12_TASK_NAME,
    build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report,
    validate_phase_2c_12_report,
)
from phase_2c_13_interview_mvp_implementation_slice_safety_delta_review import (
    DELTA_STATUS as PHASE_2C_13_SAFE_DELTA_STATUS,
    FINAL_VERDICT as PHASE_2C_13_VERDICT,
    TASK_NAME as PHASE_2C_13_TASK_NAME,
    build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report,
    validate_phase_2c_13_report,
)


PHASE = "2C-14"
TASK_NAME = "phase2c-14-interview-mvp-implementation-slice-final-selection-gate"
TITLE = "Phase 2C-14 Interview MVP Implementation Slice Final Selection Gate - Planning Only"
MODE = "planning_only_interview_mvp_final_selection_gate"
SCOPE = "interview_mvp_implementation_slice_final_selection_gate_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_14_INTERVIEW_MVP_FINAL_SELECTION_GATE_DONE_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
NO_SAFE_SELECTION_VERDICT = "NO_SAFE_INTERVIEW_MVP_SLICE_SELECTED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.md"

SELECTED_CANDIDATE_ID = "candidate-03"
SELECTED_NEXT_SLICE = "local_result_envelope_contract"
SELECTED_SLICE_DISPLAY_NAME = "Local Result Envelope Contract"

PHASE_GOAL = (
    "Select exactly one next Interview MVP implementation slice from the "
    "Phase 2C-12 candidate inventory, using the Phase 2C-13 safety delta "
    "review as the decision basis. This phase is planning-only and does not "
    "authorize or start implementation."
)

CANDIDATE_SOURCE = (
    "Candidate items come only from Phase 2C-12 Interview MVP Implementation "
    "Slice Candidate Inventory. Safety input comes only from Phase 2C-13 "
    "Interview MVP Implementation Slice Safety Delta Review. No unrelated new "
    "candidates are added."
)

EXAMPLE_JOB_TYPES = (
    "interview MVP candidate inventory",
    "interview MVP safety-delta-reviewed slice",
    "report-only candidate artifact",
    "mock-only validation candidate",
    "Phase 2C-12 listed candidate slices only",
)

SELECTION_CRITERIA = (
    "lowest safety delta",
    "smallest implementation boundary",
    "strongest reviewer-visible evidence value for an Interview MVP",
    "no runner, adapter, execution path, scheduler, queue, worker, or AI loop required",
    "no SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets required",
    "no config backup or config change behavior required",
    "no Day1-Day160 rewrite or replacement",
    "no second safety matrix",
    "clear later validation path that can remain local, deterministic, and mock-only",
)

SAFETY_DELTA_DEPENDENCY = (
    "Phase 2C-13 reports no new safety delta within the planning boundary for "
    "all Phase 2C-12 candidates. The selected candidate must retain that "
    "status and must not require expanded forbidden scope."
)

FORBIDDEN_SCOPE = (
    "implementation authorization",
    "Phase 2C-15 start",
    "selected slice implementation",
    "candidate implementation logic",
    "runner",
    "adapter",
    "execution path",
    "scheduler",
    "queue",
    "broker",
    "worker",
    "AI agent loop",
    "SSH",
    "NETCONF",
    "RESTCONF",
    "live device access",
    "provider integration",
    "API integration",
    "model integration",
    "secrets handling",
    "real command execution",
    "config backup behavior",
    "config change behavior",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
    "unrelated file modification",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/automation_readiness/actual_automation_integration_plan.md",
    "docs/phase_2c/phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md",
    "phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.py",
    "phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.py",
    "phase_2c_06_next_slice_final_selection_gate.py",
    "tests/test_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.py",
    "tests/test_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.py",
    "tests/test_phase_2c_06_next_slice_final_selection_gate.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add Phase 2C-14 planning-only final selection evidence, minimal "
    "deterministic report-only generation, targeted tests, and existing-pattern "
    "registry/CLI/report-index visibility. Not allowed: authorizing "
    "implementation, starting Phase 2C-15, implementing the selected slice, "
    "adding runner, adapter, execution path, scheduler, queue, broker, worker, "
    "AI loop, SSH, NETCONF, RESTCONF, live device access, provider/API/model "
    "integration, secrets, config backup, config change, production execution, "
    "Day1-Day160 replacement, AGENTS.md modification, or a second safety matrix."
)

SELECTION_RATIONALE = (
    "candidate-03 is selected because local_result_envelope_contract can remain "
    "a narrow, deterministic, mock-only planning output that improves "
    "reviewer-visible PASS/WARN/FAIL/BLOCKED evidence without opening runner, "
    "adapter, execution, live-device, provider/API/model, secret, backup, "
    "config-change, Day1-Day160 replacement, or second-safety-matrix scope. "
    "It is safer than candidates 01, 02, 05, and 06 because those carry "
    "runner/adapter/execution or live-device/provider/secrets risk if "
    "broadened. It is more appropriate than candidate-04 because an envelope "
    "contract defines the evidence shape a later report can display, while "
    "report visibility alone is only navigation."
)

SAFETY_FLAGS = {
    "phase_2c_14_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_2c_12_read": True,
    "phase_2c_13_read": True,
    "final_selection_gate_only": True,
    "phase_goal_separated": True,
    "example_job_types_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "selected_next_slice_separated": True,
    "rationale_separated": True,
    "candidate_selected": True,
    "implementation_authorized": False,
    "implementation_started": False,
    "phase_2c_15_started": False,
    "implementation_added": False,
    "runtime_implementation_added": False,
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
    "ai_loop_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "scope_narrowed_to_one_example_before_review": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_14_INTERVIEW_MVP_IMPLEMENTATION_SLICE_FINAL_SELECTION_GATE_PLANNING_ONLY",
    "FINAL_SELECTION_GATE_ONLY_YES",
    "PHASE_2C_12_READ_YES",
    "PHASE_2C_13_READ_YES",
    "CANDIDATE_SELECTED_YES",
    f"SELECTED_NEXT_SLICE_{SELECTED_NEXT_SLICE.upper()}",
    "IMPLEMENTATION_AUTHORIZED_NO",
    "IMPLEMENTATION_STARTED_NO",
    "PHASE_2C_15_STARTED_NO",
    "IMPLEMENTATION_ADDED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_ADDED_NO",
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
            "allowed_by_phase_2c_14": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _source_reviews(project_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    phase_2c_12_report = build_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory_report(
        project_root
    )
    phase_2c_13_report = build_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review_report(
        project_root
    )
    return (
        phase_2c_12_report,
        validate_phase_2c_12_report(phase_2c_12_report),
        phase_2c_13_report,
        validate_phase_2c_13_report(phase_2c_13_report),
    )


def _candidate_delta_by_id(phase_2c_13_report: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    return {
        item.get("candidate_id"): item
        for item in phase_2c_13_report.get("candidate_safety_delta_reviews", [])
        if isinstance(item, Mapping)
    }


def _selection_reason(candidate: Mapping[str, Any], selected: bool) -> str:
    if selected:
        return SELECTION_RATIONALE
    if candidate.get("opens_runner_adapter_execution_risk") or candidate.get("touches_live_device_provider_secrets_risk"):
        return "Not selected because the source inventory records higher risk if broadened."
    return "Not selected because candidate-03 provides a stronger evidence-contract basis for a later MVP slice."


def _candidate_selection_reviews(
    phase_2c_12_report: Mapping[str, Any],
    phase_2c_13_report: Mapping[str, Any],
) -> Tuple[Dict[str, Any], ...]:
    delta_by_candidate = _candidate_delta_by_id(phase_2c_13_report)
    reviews = []
    for candidate in phase_2c_12_report.get("candidate_inventory", []):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = candidate.get("candidate_id")
        delta_review = delta_by_candidate.get(candidate_id, {})
        selected = candidate_id == SELECTED_CANDIDATE_ID
        reviews.append(
            {
                "candidate_id": candidate_id,
                "candidate_name": candidate.get("candidate_name"),
                "source_decision_status": candidate.get("current_decision_status"),
                "phase_2c_13_delta_status": delta_review.get("delta_status"),
                "source_runner_adapter_execution_risk": candidate.get("opens_runner_adapter_execution_risk"),
                "source_live_device_provider_secrets_risk": candidate.get("touches_live_device_provider_secrets_risk"),
                "selected": selected,
                "selection_status": "SELECTED_NEXT_SLICE" if selected else "NOT_SELECTED",
                "selection_reason": _selection_reason(candidate, selected),
                "requires_expanded_forbidden_scope": False,
                "implementation_authorized": False,
                "implementation_started": False,
            }
        )
    return tuple(reviews)


def validate_phase_2c_14_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("selection_decision") != "FINAL_SELECTION_GATE_ONLY":
        errors.append("SELECTION_DECISION_MISMATCH")
    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("candidate_source") != CANDIDATE_SOURCE:
        errors.append("CANDIDATE_SOURCE_MISMATCH")

    source_12 = report.get("phase_2c_12_source_review", {})
    source_13 = report.get("phase_2c_13_safety_delta_dependency_review", {})
    if not isinstance(source_12, Mapping):
        errors.append("PHASE_2C_12_SOURCE_NOT_OBJECT")
        source_12 = {}
    if not isinstance(source_13, Mapping):
        errors.append("PHASE_2C_13_SOURCE_NOT_OBJECT")
        source_13 = {}
    if source_12.get("reviewed_task") != PHASE_2C_12_TASK_NAME:
        errors.append("PHASE_2C_12_TASK_MISMATCH")
    if source_12.get("observed_verdict") != PHASE_2C_12_VERDICT:
        errors.append("PHASE_2C_12_VERDICT_MISMATCH")
    if not isinstance(source_12.get("source_validation"), Mapping) or source_12["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_12_VALIDATION_NOT_PASS")
    if source_13.get("reviewed_task") != PHASE_2C_13_TASK_NAME:
        errors.append("PHASE_2C_13_TASK_MISMATCH")
    if source_13.get("observed_verdict") != PHASE_2C_13_VERDICT:
        errors.append("PHASE_2C_13_VERDICT_MISMATCH")
    if not isinstance(source_13.get("source_validation"), Mapping) or source_13["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_13_VALIDATION_NOT_PASS")

    candidate_reviews = report.get("candidate_selection_reviews", [])
    if not isinstance(candidate_reviews, Sequence) or isinstance(candidate_reviews, (str, bytes)):
        errors.append("CANDIDATE_SELECTION_REVIEWS_NOT_LIST")
        candidate_reviews = []
    expected_ids = {candidate["candidate_id"] for candidate in PHASE_2C_12_CANDIDATE_INVENTORY}
    observed_ids = {item.get("candidate_id") for item in candidate_reviews if isinstance(item, Mapping)}
    if observed_ids != expected_ids:
        errors.append("CANDIDATE_ID_SET_MISMATCH")
    selected_reviews = [
        item for item in candidate_reviews if isinstance(item, Mapping) and item.get("selected") is True
    ]
    if len(selected_reviews) != 1:
        errors.append("SELECTED_CANDIDATE_COUNT_MISMATCH")
    else:
        selected = selected_reviews[0]
        if selected.get("candidate_id") != SELECTED_CANDIDATE_ID:
            errors.append("SELECTED_CANDIDATE_ID_MISMATCH")
        if selected.get("candidate_name") != SELECTED_NEXT_SLICE:
            errors.append("SELECTED_NEXT_SLICE_NAME_MISMATCH")
        if selected.get("phase_2c_13_delta_status") != PHASE_2C_13_SAFE_DELTA_STATUS:
            errors.append(NO_SAFE_SELECTION_VERDICT)
        if selected.get("requires_expanded_forbidden_scope") is not False:
            errors.append("SELECTED_CANDIDATE_EXPANDS_FORBIDDEN_SCOPE")
        if selected.get("source_runner_adapter_execution_risk") is not False:
            errors.append("SELECTED_CANDIDATE_RUNNER_ADAPTER_RISK")
        if selected.get("source_live_device_provider_secrets_risk") is not False:
            errors.append("SELECTED_CANDIDATE_LIVE_PROVIDER_SECRET_RISK")
        if selected.get("implementation_authorized") is not False:
            errors.append("SELECTED_CANDIDATE_AUTHORIZED")
        if selected.get("implementation_started") is not False:
            errors.append("SELECTED_CANDIDATE_IMPLEMENTATION_STARTED")

    if report.get("selected_next_slice") != SELECTED_NEXT_SLICE:
        errors.append("SELECTED_NEXT_SLICE_MISMATCH")
    if report.get("selected_candidate_id") != SELECTED_CANDIDATE_ID:
        errors.append("SELECTED_CANDIDATE_ID_FIELD_MISMATCH")
    if report.get("selection_criteria") != list(SELECTION_CRITERIA):
        errors.append("SELECTION_CRITERIA_MISMATCH")
    if report.get("safety_delta_dependency") != SAFETY_DELTA_DEPENDENCY:
        errors.append("SAFETY_DELTA_DEPENDENCY_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in set(report.get("existing_artifacts_referenced", [])):
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "FINAL_SELECTION_GATE_ONLY": "YES",
        "PHASE_2C_12_READ": "YES",
        "PHASE_2C_13_READ": "YES",
        "CANDIDATE_SELECTED": "YES",
        "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
        "IMPLEMENTATION_AUTHORIZED": "NO",
        "IMPLEMENTATION_STARTED": "NO",
        "PHASE_2C_15_STARTED": "NO",
        "IMPLEMENTATION_ADDED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "implementation_authorized",
        "implementation_started",
        "phase_2c_15_started",
        "implementation_added",
        "runtime_implementation_added",
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
        "ai_loop_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
        "scope_narrowed_to_one_example_before_review",
        "needs_scope_confirmation",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)
    if report.get("candidate_selected") is not True:
        errors.append("CANDIDATE_NOT_SELECTED")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "candidate_selection_reviews_checked": len(candidate_reviews),
        "selection_criteria_checked": len(report.get("selection_criteria", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
        "existing_artifacts_checked": len(report.get("existing_artifacts_referenced", [])),
        "selected_candidate_count": len(selected_reviews),
    }


def build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
    project_root: Path,
) -> Dict[str, Any]:
    phase_2c_12_report, phase_2c_12_validation, phase_2c_13_report, phase_2c_13_validation = _source_reviews(
        project_root
    )
    candidate_selection_reviews = _candidate_selection_reviews(phase_2c_12_report, phase_2c_13_report)
    selected_review = next(item for item in candidate_selection_reviews if item["selected"] is True)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "selection_decision": "FINAL_SELECTION_GATE_ONLY",
        "phase_goal": PHASE_GOAL,
        "candidate_source": CANDIDATE_SOURCE,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "selection_criteria": list(SELECTION_CRITERIA),
        "safety_delta_dependency": SAFETY_DELTA_DEPENDENCY,
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "selected_slice_display_name": SELECTED_SLICE_DISPLAY_NAME,
        "selection_rationale": SELECTION_RATIONALE,
        "phase_2c_12_source_review": {
            "reviewed_task": PHASE_2C_12_TASK_NAME,
            "expected_verdict": PHASE_2C_12_VERDICT,
            "observed_verdict": phase_2c_12_report.get("final_verdict"),
            "source_validation": phase_2c_12_validation,
            "candidate_count": len(phase_2c_12_report.get("candidate_inventory", [])),
            "source_single_slice_selected": phase_2c_12_report.get("single_slice_selected"),
            "source_implementation_authorized": phase_2c_12_report.get("implementation_authorized"),
            "source_implementation_started": phase_2c_12_report.get("implementation_started"),
        },
        "phase_2c_13_safety_delta_dependency_review": {
            "reviewed_task": PHASE_2C_13_TASK_NAME,
            "expected_verdict": PHASE_2C_13_VERDICT,
            "observed_verdict": phase_2c_13_report.get("final_verdict"),
            "source_validation": phase_2c_13_validation,
            "selected_candidate_delta_status": selected_review["phase_2c_13_delta_status"],
            "all_candidates_safe_within_planning_boundary": all(
                item.get("phase_2c_13_delta_status") == PHASE_2C_13_SAFE_DELTA_STATUS
                for item in candidate_selection_reviews
            ),
        },
        "candidate_selection_reviews": list(deepcopy(candidate_selection_reviews)),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "selection_statement": (
            "Phase 2C-14 selects exactly one next Interview MVP implementation "
            "slice for future consideration only. Selection is not "
            "implementation authorization."
        ),
        "non_execution_statement": (
            "This task opens no implementation, runtime behavior, runner, "
            "adapter, scheduler, queue, broker, worker, AI loop, execution "
            "path, SSH, NETCONF, RESTCONF, live-device access, "
            "provider/API/model calls, secrets, backup behavior, config-change "
            "behavior, Phase 2C-15 start, Day1-Day160 rewrite, or second safety "
            "matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "FINAL_SELECTION_GATE_ONLY": "YES",
            "PHASE_2C_12_READ": "YES",
            "PHASE_2C_13_READ": "YES",
            "CANDIDATE_SELECTED": "YES",
            "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
            "IMPLEMENTATION_AUTHORIZED": "NO",
            "IMPLEMENTATION_STARTED": "NO",
            "PHASE_2C_15_STARTED": "NO",
            "IMPLEMENTATION_ADDED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "final_selection_gate_only": True,
        "phase_2c_12_read": True,
        "phase_2c_13_read": True,
        "candidate_count": len(candidate_selection_reviews),
        "candidate_selected": True,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "selection_rationale": SELECTION_RATIONALE,
        "implementation_authorized": False,
        "implementation_started": False,
        "phase_2c_15_started": False,
        "implementation_added": False,
        "runner_adapter_execution_path_added": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_14_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
        report["final_verdict"] = (
            NO_SAFE_SELECTION_VERDICT if NO_SAFE_SELECTION_VERDICT in validation["errors"] else BLOCKED_VERDICT
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


def _selection_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('candidate_id')))}</td>"
        f"<td>{html.escape(str(item.get('candidate_name')))}</td>"
        f"<td>{html.escape(str(item.get('phase_2c_13_delta_status')))}</td>"
        f"<td>{html.escape(str(item.get('selected')))}</td>"
        f"<td>{html.escape(str(item.get('selection_status')))}</td>"
        "</tr>"
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
  <p>Selection decision: <strong>{html.escape(str(report["selection_decision"]))}</strong></p>
  <p>Selected next slice: <strong>{html.escape(str(report["selected_next_slice"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["selection_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Safety Delta Dependency</h2>
  <table><tbody>{_dict_rows(report["phase_2c_13_safety_delta_dependency_review"])}</tbody></table>
  <h2>Candidate Selection Reviews</h2>
  <table><thead><tr><th>Candidate</th><th>Name</th><th>Phase 2C-13 Delta</th><th>Selected</th><th>Status</th></tr></thead><tbody>{_selection_rows(report["candidate_selection_reviews"])}</tbody></table>
  <h2>Selection Criteria</h2>
  <ul>{_list_items(report["selection_criteria"])}</ul>
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


def write_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(
        project_root
    )
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_report(project_root)
    json_path, html_path = write_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Selection decision: {report['selection_decision']}")
    print(f"phase_2c_12_read: {str(report['summary']['phase_2c_12_read']).lower()}")
    print(f"phase_2c_13_read: {str(report['summary']['phase_2c_13_read']).lower()}")
    print(f"final_selection_gate_only: {str(report['summary']['final_selection_gate_only']).lower()}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"candidate_selected: {str(report['summary']['candidate_selected']).lower()}")
    print(f"selected_candidate_id: {report['summary']['selected_candidate_id']}")
    print(f"selected_next_slice: {report['summary']['selected_next_slice']}")
    print(f"implementation_authorized: {str(report['summary']['implementation_authorized']).lower()}")
    print(f"implementation_started: {str(report['summary']['implementation_started']).lower()}")
    print(f"phase_2c_15_started: {str(report['summary']['phase_2c_15_started']).lower()}")
    print(f"implementation_added: {str(report['summary']['implementation_added']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
    )
    print(
        "queue_scheduler_worker_ai_loop_added: "
        f"{str(report['summary']['queue_scheduler_worker_ai_loop_added']).lower()}"
    )
    print(
        "ssh_netconf_restconf_live_device_touched: "
        f"{str(report['summary']['ssh_netconf_restconf_live_device_touched']).lower()}"
    )
    print(
        "provider_api_model_secrets_touched: "
        f"{str(report['summary']['provider_api_model_secrets_touched']).lower()}"
    )
    print(
        "config_backup_or_change_behavior_added: "
        f"{str(report['summary']['config_backup_or_change_behavior_added']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Candidate selection reviews checked: {report['validation']['candidate_selection_reviews_checked']}")
    print(f"Selection criteria checked: {report['validation']['selection_criteria_checked']}")
    print(f"Forbidden scope items checked: {report['validation']['forbidden_scope_items_checked']}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
