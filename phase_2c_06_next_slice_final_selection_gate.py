"""Phase 2C-06 next-slice final selection gate.

This module creates deterministic, local, planning-only evidence that selects
exactly one next-slice candidate from Phase 2C-04 using the Phase 2C-05 safety
delta review as required input. It does not authorize, scaffold, implement, or
execute the selected slice.
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
    SAFETY_DELTA_FIELDS,
    TASK_NAME as PHASE_2C_05_TASK_NAME,
    build_phase_2c_05_next_slice_safety_delta_review_report,
    validate_phase_2c_05_report,
)


PHASE = "2C-06"
TASK_NAME = "phase2c-06-next-slice-final-selection-gate"
TITLE = "Phase 2C-06 Next-Slice Final Selection Gate - Planning Only"
MODE = "planning_only_next_slice_final_selection_gate"
SCOPE = "phase_wide_final_selection_gate_only"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_06_FINAL_SELECTION_GATE_DONE_IMPLEMENTATION_LOCKED"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
NO_SAFE_SELECTION_VERDICT = "NO_SAFE_NEXT_SLICE_SELECTED"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_06_next_slice_final_selection_gate.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_06_next_slice_final_selection_gate.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_06_next_slice_final_selection_gate.md"

SELECTED_CANDIDATE_ID = "candidate-02"
SELECTED_NEXT_SLICE = "artifact_validation_job"
SELECTED_EXAMPLE_JOB_TYPE = "artifact validation job"
SELECTED_SLICE_DISPLAY_NAME = "Artifact Validation Job"

PHASE_GOAL = (
    "Select exactly one next-slice candidate from the Phase 2C-04 candidate "
    "inventory, using the Phase 2C-05 safety delta review as the required "
    "safety input. This final selection gate does not authorize Phase 2C-07, "
    "Phase 2C-08, implementation, scaffolding, runtime behavior, or execution."
)

CANDIDATE_SOURCE = (
    "Candidate items come only from Phase 2C-04 Next-Slice Candidate "
    "Inventory. Safety input comes only from Phase 2C-05 Next-Slice Safety "
    "Delta Review. No unrelated new candidates are added."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job continuation",
    "artifact validation job",
    "report-only evidence collection job",
    "dry-run result rendering job",
    "mock parse/report job",
    "candidate UI display contract follow-up",
    "candidate safety regression follow-up",
)

SELECTION_CRITERIA = (
    "lowest safety delta",
    "smallest implementation boundary",
    "strongest alignment with existing report-only / dry-run / mock-only constraints",
    "no need for SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets",
    "no need for runner, adapter, scheduler, queue, broker, worker, or agent loop",
    "no Day1-Day160 rewrite or replacement",
    "no second safety matrix",
    "clear targeted validation path",
    "ability to remain minimal and verifiable in a later implementation phase",
)

SAFETY_DELTA_DEPENDENCY = (
    "Phase 2C-05 reports no new safety delta within the planning boundary for "
    "all Phase 2C-04 candidates. The selected candidate must retain that "
    "status and must not require expanded forbidden scope."
)

FORBIDDEN_SCOPE = (
    "implementation authorization",
    "Phase 2C-07 start",
    "Phase 2C-08 start",
    "selected candidate implementation",
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
    "phase_2b_13_first_slice_final_selection_gate.py",
    "phase_2b_14_first_slice_implementation_kickoff_gate.py",
    "phase_2c_01_local_static_job_first_slice.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "phase_2c_04_next_slice_candidate_inventory.py",
    "phase_2c_05_next_slice_safety_delta_review.py",
    "Day1-Day160 existing reference material only",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: add the Phase 2C-06 planning-only final selection artifact, "
    "minimal report-only Python evidence generation, targeted tests, and "
    "registry/CLI/report-index visibility. Not allowed: authorizing or "
    "starting Phase 2C-07/2C-08, implementing the selected candidate, creating "
    "a runner/adapter/execution path, touching SSH/NETCONF/RESTCONF/live-device/"
    "provider/API/model/secret scope, adding backup or config-change behavior, "
    "rewriting Day1-Day160, modifying AGENTS.md, or creating a second safety "
    "matrix."
)

SELECTION_RATIONALE = (
    "candidate-02 is selected because artifact validation can remain a narrow, "
    "deterministic, report-only follow-up over existing artifact shape and "
    "reviewer visibility. Phase 2C-05 records no new safety delta for it, and "
    "it avoids expanded runtime, runner, adapter, scheduler, broker, live-device, "
    "provider/API/model, secret, Day1-Day160 replacement, and second safety "
    "matrix scope."
)

SAFETY_FLAGS = {
    "phase_2c_06_artifact_created": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_2c_04_read": True,
    "phase_2c_05_read": True,
    "final_selection_gate_only": True,
    "phase_goal_separated": True,
    "candidate_source_separated": True,
    "example_job_types_separated": True,
    "selection_criteria_separated": True,
    "safety_delta_dependency_separated": True,
    "forbidden_scope_separated": True,
    "existing_artifacts_to_reference_separated": True,
    "implementation_boundary_separated": True,
    "selected_next_slice_separated": True,
    "rationale_separated": True,
    "final_verdict_separated": True,
    "candidate_selected": True,
    "next_slice_authorized": False,
    "phase_2c_07_started": False,
    "phase_2c_08_started": False,
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
    "agent_loop_added": False,
    "shell_command_added": False,
    "custom_script_execution_added": False,
    "config_backup_execution_added": False,
    "config_change_execution_added": False,
    "real_device_operation_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
    "scope_narrowed_to_one_example_before_review": False,
    "needs_scope_confirmation": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_06_NEXT_SLICE_FINAL_SELECTION_GATE_PLANNING_ONLY",
    "FINAL_SELECTION_GATE_ONLY_YES",
    "PHASE_2C_04_READ_YES",
    "PHASE_2C_05_READ_YES",
    "CANDIDATE_SELECTED_YES",
    f"SELECTED_NEXT_SLICE_{SELECTED_NEXT_SLICE.upper()}",
    "NEXT_SLICE_AUTHORIZED_NO",
    "PHASE_2C_07_STARTED_NO",
    "PHASE_2C_08_STARTED_NO",
    "IMPLEMENTATION_ADDED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
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
            "allowed_by_phase_2c_06": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def _source_reviews() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    phase_2c_04_report = build_phase_2c_04_next_slice_candidate_inventory_report()
    phase_2c_05_report = build_phase_2c_05_next_slice_safety_delta_review_report()
    return (
        phase_2c_04_report,
        validate_phase_2c_04_report(phase_2c_04_report),
        phase_2c_05_report,
        validate_phase_2c_05_report(phase_2c_05_report),
    )


def _candidate_selection_reviews(
    phase_2c_04_report: Mapping[str, Any],
    phase_2c_05_report: Mapping[str, Any],
) -> Tuple[Dict[str, Any], ...]:
    delta_by_candidate = {
        item.get("candidate_id"): item
        for item in phase_2c_05_report.get("candidate_safety_delta_reviews", [])
        if isinstance(item, Mapping)
    }
    reviews = []
    for candidate in phase_2c_04_report.get("candidate_inventory", []):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = candidate.get("candidate_id")
        delta_review = delta_by_candidate.get(candidate_id, {})
        selected = candidate_id == SELECTED_CANDIDATE_ID
        reviews.append(
            {
                "candidate_id": candidate_id,
                "example_job_type": candidate.get("example_job_type"),
                "source_inventory_status": candidate.get("inventory_status"),
                "phase_2c_05_delta_status": delta_review.get("delta_status"),
                "selected": selected,
                "selection_status": "SELECTED_NEXT_SLICE" if selected else "NOT_SELECTED",
                "selection_reason": SELECTION_RATIONALE if selected else "Not selected in this gate.",
                "requires_expanded_forbidden_scope": False,
            }
        )
    return tuple(reviews)


def validate_phase_2c_06_report(report: Mapping[str, Any]) -> Dict[str, Any]:
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

    source_04 = report.get("phase_2c_04_source_review", {})
    source_05 = report.get("phase_2c_05_safety_delta_dependency_review", {})
    if not isinstance(source_04, Mapping):
        errors.append("PHASE_2C_04_SOURCE_NOT_OBJECT")
        source_04 = {}
    if not isinstance(source_05, Mapping):
        errors.append("PHASE_2C_05_SOURCE_NOT_OBJECT")
        source_05 = {}
    if source_04.get("reviewed_task") != PHASE_2C_04_TASK_NAME:
        errors.append("PHASE_2C_04_TASK_MISMATCH")
    if source_04.get("observed_verdict") != PHASE_2C_04_VERDICT:
        errors.append("PHASE_2C_04_VERDICT_MISMATCH")
    if not isinstance(source_04.get("source_validation"), Mapping) or source_04["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_04_VALIDATION_NOT_PASS")
    if source_05.get("reviewed_task") != PHASE_2C_05_TASK_NAME:
        errors.append("PHASE_2C_05_TASK_MISMATCH")
    if source_05.get("observed_verdict") != PHASE_2C_05_VERDICT:
        errors.append("PHASE_2C_05_VERDICT_MISMATCH")
    if not isinstance(source_05.get("source_validation"), Mapping) or source_05["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_05_VALIDATION_NOT_PASS")

    candidate_reviews = report.get("candidate_selection_reviews", [])
    if not isinstance(candidate_reviews, Sequence) or isinstance(candidate_reviews, (str, bytes)):
        errors.append("CANDIDATE_SELECTION_REVIEWS_NOT_LIST")
        candidate_reviews = []
    selected_reviews = [
        item for item in candidate_reviews if isinstance(item, Mapping) and item.get("selected") is True
    ]
    if len(selected_reviews) != 1:
        errors.append("SELECTED_CANDIDATE_COUNT_MISMATCH")
    else:
        selected = selected_reviews[0]
        if selected.get("candidate_id") != SELECTED_CANDIDATE_ID:
            errors.append("SELECTED_CANDIDATE_ID_MISMATCH")
        if selected.get("example_job_type") != SELECTED_EXAMPLE_JOB_TYPE:
            errors.append("SELECTED_EXAMPLE_JOB_TYPE_MISMATCH")
        if selected.get("phase_2c_05_delta_status") != PHASE_2C_05_SAFE_DELTA_STATUS:
            errors.append(NO_SAFE_SELECTION_VERDICT)
        if selected.get("requires_expanded_forbidden_scope") is not False:
            errors.append("SELECTED_CANDIDATE_EXPANDS_FORBIDDEN_SCOPE")

    if report.get("selected_next_slice") != SELECTED_NEXT_SLICE:
        errors.append("SELECTED_NEXT_SLICE_MISMATCH")
    if report.get("selected_candidate_id") != SELECTED_CANDIDATE_ID:
        errors.append("SELECTED_CANDIDATE_ID_FIELD_MISMATCH")
    if report.get("candidate_source") != CANDIDATE_SOURCE:
        errors.append("CANDIDATE_SOURCE_MISMATCH")
    if report.get("selection_criteria") != list(SELECTION_CRITERIA):
        errors.append("SELECTION_CRITERIA_MISMATCH")
    if report.get("safety_delta_dependency") != SAFETY_DELTA_DEPENDENCY:
        errors.append("SAFETY_DELTA_DEPENDENCY_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    artifacts = set(report.get("existing_artifacts_referenced", []))
    for artifact in EXISTING_ARTIFACTS_REFERENCED:
        if artifact not in artifacts:
            errors.append(f"EXISTING_ARTIFACT_MISSING:{artifact}")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "FINAL_SELECTION_GATE_ONLY": "YES",
        "PHASE_2C_04_READ": "YES",
        "PHASE_2C_05_READ": "YES",
        "CANDIDATE_SELECTED": "YES",
        "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
        "NEXT_SLICE_AUTHORIZED": "NO",
        "PHASE_2C_07_STARTED": "NO",
        "PHASE_2C_08_STARTED": "NO",
        "IMPLEMENTATION_ADDED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "next_slice_authorized",
        "phase_2c_07_started",
        "phase_2c_08_started",
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
        "agent_loop_added",
        "shell_command_added",
        "custom_script_execution_added",
        "config_backup_execution_added",
        "config_change_execution_added",
        "real_device_operation_added",
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
        "existing_artifacts_checked": len(artifacts),
        "selected_candidate_count": len(selected_reviews),
    }


def build_phase_2c_06_next_slice_final_selection_gate_report() -> Dict[str, Any]:
    phase_2c_04_report, phase_2c_04_validation, phase_2c_05_report, phase_2c_05_validation = _source_reviews()
    candidate_selection_reviews = _candidate_selection_reviews(phase_2c_04_report, phase_2c_05_report)
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
        "selected_example_job_type": SELECTED_EXAMPLE_JOB_TYPE,
        "selection_rationale": SELECTION_RATIONALE,
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
            "source_candidate_selected": phase_2c_04_report.get("candidate_selected"),
            "source_next_slice_authorized": phase_2c_04_report.get("next_slice_authorized"),
        },
        "phase_2c_05_safety_delta_dependency_review": {
            "reviewed_task": PHASE_2C_05_TASK_NAME,
            "expected_verdict": PHASE_2C_05_VERDICT,
            "observed_verdict": phase_2c_05_report.get("final_verdict"),
            "source_validation": phase_2c_05_validation,
            "selected_candidate_delta_status": selected_review["phase_2c_05_delta_status"],
            "all_candidates_safe_within_planning_boundary": all(
                item.get("phase_2c_05_delta_status") == PHASE_2C_05_SAFE_DELTA_STATUS
                for item in candidate_selection_reviews
            ),
        },
        "candidate_selection_reviews": list(deepcopy(candidate_selection_reviews)),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "selection_statement": (
            "Phase 2C-06 selects exactly one next-slice candidate for future "
            "consideration only. Selection is not implementation authorization."
        ),
        "non_execution_statement": (
            "This task opens no runtime implementation, runner, adapter, "
            "scheduler, queue, broker, worker, agent loop, execution path, SSH, "
            "NETCONF, RESTCONF, live-device access, provider/API/model calls, "
            "secrets, backup behavior, config-change behavior, Phase 2C-07 "
            "start, Phase 2C-08 start, Day1-Day160 rewrite, or second safety "
            "matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "FINAL_SELECTION_GATE_ONLY": "YES",
            "PHASE_2C_04_READ": "YES",
            "PHASE_2C_05_READ": "YES",
            "CANDIDATE_SELECTED": "YES",
            "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
            "NEXT_SLICE_AUTHORIZED": "NO",
            "PHASE_2C_07_STARTED": "NO",
            "PHASE_2C_08_STARTED": "NO",
            "IMPLEMENTATION_ADDED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "final_selection_gate_only": True,
        "phase_2c_04_read": True,
        "phase_2c_05_read": True,
        "candidate_count": len(candidate_selection_reviews),
        "candidate_selected": True,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "selection_rationale": SELECTION_RATIONALE,
        "next_slice_authorized": False,
        "phase_2c_07_started": False,
        "phase_2c_08_started": False,
        "implementation_added": False,
        "runner_adapter_execution_path_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_06_report(report)
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
        f"<td>{html.escape(str(item.get('example_job_type')))}</td>"
        f"<td>{html.escape(str(item.get('phase_2c_05_delta_status')))}</td>"
        f"<td>{html.escape(str(item.get('selected')))}</td>"
        f"<td>{html.escape(str(item.get('selection_status')))}</td>"
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
  <p>Selection decision: <strong>{html.escape(str(report["selection_decision"]))}</strong></p>
  <p>Selected next slice: <strong>{html.escape(str(report["selected_next_slice"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["selection_statement"]))}</p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Safety Delta Dependency</h2>
  <table><tbody>{_dict_rows(report["phase_2c_05_safety_delta_dependency_review"])}</tbody></table>
  <h2>Candidate Selection Reviews</h2>
  <table><thead><tr><th>Candidate</th><th>Example Job Type</th><th>Phase 2C-05 Delta</th><th>Selected</th><th>Status</th></tr></thead><tbody>{_selection_rows(report["candidate_selection_reviews"])}</tbody></table>
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


def write_phase_2c_06_next_slice_final_selection_gate_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_06_next_slice_final_selection_gate_report()
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_06_next_slice_final_selection_gate(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_06_next_slice_final_selection_gate_report()
    json_path, html_path = write_phase_2c_06_next_slice_final_selection_gate_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"Selection decision: {report['selection_decision']}")
    print(f"phase_2c_04_read: {str(report['summary']['phase_2c_04_read']).lower()}")
    print(f"phase_2c_05_read: {str(report['summary']['phase_2c_05_read']).lower()}")
    print(f"final_selection_gate_only: {str(report['summary']['final_selection_gate_only']).lower()}")
    print(f"candidate_count: {report['summary']['candidate_count']}")
    print(f"candidate_selected: {str(report['summary']['candidate_selected']).lower()}")
    print(f"selected_candidate_id: {report['summary']['selected_candidate_id']}")
    print(f"selected_next_slice: {report['summary']['selected_next_slice']}")
    print(f"next_slice_authorized: {str(report['summary']['next_slice_authorized']).lower()}")
    print(f"phase_2c_07_started: {str(report['summary']['phase_2c_07_started']).lower()}")
    print(f"phase_2c_08_started: {str(report['summary']['phase_2c_08_started']).lower()}")
    print(f"implementation_added: {str(report['summary']['implementation_added']).lower()}")
    print(
        "runner_adapter_execution_path_added: "
        f"{str(report['summary']['runner_adapter_execution_path_added']).lower()}"
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
