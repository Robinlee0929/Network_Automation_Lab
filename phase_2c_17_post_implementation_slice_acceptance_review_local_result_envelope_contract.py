"""Phase 2C-17 local result envelope acceptance review.

This module creates deterministic, local, report-only acceptance evidence for
the Phase 2C-16 `local_result_envelope_contract` implementation slice. It
reviews existing Phase 2C evidence only. It does not continue implementation,
select another slice, start Phase 2C-18, or call runners, adapters, brokers,
schedulers, queues, workers, agent loops, shells, scripts, SSH, NETCONF,
RESTCONF, live devices, providers, APIs, models, or secret sources.
"""

from __future__ import annotations

import html
import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate import (
    AUTHORIZATION_RESULT as PHASE_2C_15_AUTHORIZATION_RESULT,
    DECISION_TARGET_ID as PHASE_2C_15_DECISION_TARGET_ID,
    DECISION_TARGET_SLICE as PHASE_2C_15_DECISION_TARGET_SLICE,
    FINAL_VERDICT as PHASE_2C_15_VERDICT,
    TASK_NAME as PHASE_2C_15_TASK_NAME,
)
from phase_2c_16_interview_mvp_local_result_envelope_contract import (
    FINAL_VERDICT as PHASE_2C_16_VERDICT,
    REPORT_HTML as PHASE_2C_16_REPORT_HTML,
    REPORT_JSON as PHASE_2C_16_REPORT_JSON,
    SELECTED_CANDIDATE_ID,
    SELECTED_NEXT_SLICE,
    TASK_NAME as PHASE_2C_16_TASK_NAME,
    build_phase_2c_16_interview_mvp_local_result_envelope_contract_report,
    validate_phase_2c_16_report,
)


PHASE = "2C-17"
TASK_NAME = "phase2c-17-post-implementation-slice-acceptance-review-local-result-envelope-contract"
TITLE = "Phase 2C-17 Post-Implementation Slice Acceptance Review - Local Result Envelope Contract"
MODE = "post_implementation_slice_acceptance_review_report_only"
SCOPE = "phase_2c_16_local_result_envelope_contract_acceptance_review"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_17_LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED"
NOT_ACCEPT_VERDICT = "PHASE_2C_17_LOCAL_RESULT_ENVELOPE_CONTRACT_NOT_ACCEPTED"
NEEDS_EVIDENCE_VERDICT = "PHASE_2C_17_NEEDS_EVIDENCE"
REPORT_JSON = Path("reports") / "lab-summary" / (
    "phase_2c_17_acceptance_review.json"
)
REPORT_HTML = Path("reports") / "lab-summary" / (
    "phase_2c_17_acceptance_review.html"
)
DOC_PATH = Path("docs") / "phase_2c" / (
    "phase_2c_17_post_implementation_slice_acceptance_review_"
    "local_result_envelope_contract.md"
)

ALLOWED_ACCEPTANCE_DECISIONS = ("ACCEPT", "NOT_ACCEPT", "NEEDS_EVIDENCE")

PHASE_GOAL = (
    "Review whether the completed Phase 2C-16 local_result_envelope_contract "
    "implementation is acceptable against Phase 2C-15 authorization evidence, "
    "existing project safety boundaries, Interview MVP scope, and report-only "
    "/ dry-run / mock-only expectations."
)

EXAMPLE_JOB_TYPES = (
    "local_static_job",
    "artifact_validation_job",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "baseline_check",
)

FORBIDDEN_SCOPE = (
    "new implementation slice",
    "Phase 2C-16 continuation",
    "Phase 2C-18 start",
    "next slice selection",
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
    "provider calls",
    "API calls",
    "model calls",
    "secrets handling",
    "real command execution",
    "config backup behavior",
    "config change behavior",
    "production execution path",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "AGENTS.md modification",
)

EXISTING_ARTIFACTS_REVIEWED = (
    "AGENTS.md",
    "docs/automation_readiness/actual_automation_integration_plan.md",
    "docs/phase_2c/phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.md",
    "docs/phase_2c/phase_2c_16_interview_mvp_local_result_envelope_contract.md",
    "phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.py",
    "phase_2c_16_interview_mvp_local_result_envelope_contract.py",
    "tests/test_phase_2c_16_interview_mvp_local_result_envelope_contract.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    PHASE_2C_16_REPORT_JSON.as_posix(),
    PHASE_2C_16_REPORT_HTML.as_posix(),
)

ACCEPTANCE_REVIEW_QUESTIONS = (
    "Was local_result_envelope_contract authorized by Phase 2C-15?",
    "Does the Phase 2C-16 report validate?",
    "Does Phase 2C-16 define a local bounded result envelope contract?",
    "Does the contract remain general across example job types rather than one narrow fixture?",
    "Does Phase 2C-16 avoid forbidden execution paths and live-capable behavior?",
    "Is Phase 2C-16 acceptable, not acceptable, or missing enough evidence?",
)

SAFETY_FLAGS = {
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "required_reference_documents_read": True,
    "scope_confirmed_in_writing": True,
    "needs_scope_confirmation": False,
    "acceptance_review_created": True,
    "report_only_artifact_created": True,
    "phase_2c_16_source_task_rerun": False,
    "phase_2c_16_implementation_modified": False,
    "local_result_envelope_contract_modified": False,
    "phase_2c_16_continued": False,
    "next_slice_selected": False,
    "next_implementation_started": False,
    "phase_2c_18_started": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "ai_loop_added": False,
    "real_command_execution_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_17_POST_IMPLEMENTATION_SLICE_ACCEPTANCE_REVIEW_REPORT_ONLY",
    "AGENTS_MD_FOUND_YES",
    "AGENTS_MD_READ_BEFORE_ACTION_YES",
    "AGENTS_MD_MODIFIED_NO",
    "REQUIRED_REFERENCE_DOCUMENTS_READ_YES",
    "SCOPE_CONFIRMED_IN_WRITING_YES",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "PHASE_2C_15_AUTHORIZATION_CONFIRMED_YES",
    "PHASE_2C_16_VALIDATION_PASSED_YES",
    "PHASE_2C_16_EVIDENCE_FOUND_YES",
    "LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED_YES",
    "REPORT_ONLY_ARTIFACT_CREATED_YES",
    "PHASE_2C_16_CONTINUED_NO",
    "NEXT_SLICE_SELECTED_NO",
    "NEXT_IMPLEMENTATION_STARTED_NO",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED_NO",
    "PRODUCTION_EXECUTION_PATH_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def _artifact_record(project_root: Path, path_text: str) -> Dict[str, Any]:
    path = Path(path_text)
    return {
        "path": path.as_posix(),
        "exists": (project_root / path).exists(),
        "local_repository_artifact": True,
        "external_access_required": False,
    }


def _phase_2c_16_source_review(project_root: Path) -> Dict[str, Any]:
    source_report = build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(project_root)
    source_validation = validate_phase_2c_16_report(source_report)
    source_15 = source_report.get("phase_2c_15_source_review", {})
    if not isinstance(source_15, Mapping):
        source_15 = {}
    contract = source_report.get("local_result_envelope_contract", {})
    if not isinstance(contract, Mapping):
        contract = {}
    envelope_validation = source_validation.get("envelope_validation", {})
    if not isinstance(envelope_validation, Mapping):
        envelope_validation = {}
    return {
        "reviewed_task": PHASE_2C_16_TASK_NAME,
        "expected_verdict": PHASE_2C_16_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "selected_candidate_id": source_report.get("selected_candidate_id"),
        "selected_next_slice": source_report.get("selected_next_slice"),
        "local_result_envelope_contract_implemented": source_report.get(
            "local_result_envelope_contract_implemented"
        ),
        "contract_shape_defined": source_report.get("contract_shape_defined"),
        "validator_added": source_report.get("validator_added"),
        "sample_envelope_static_fixture_only": source_report.get("sample_envelope_static_fixture_only"),
        "contract_not_runtime_infrastructure": contract.get("not_runtime_infrastructure"),
        "contract_not_result_processing_infrastructure": contract.get(
            "not_result_processing_infrastructure"
        ),
        "envelope_validation": envelope_validation,
        "phase_2c_15_source_review": {
            "reviewed_task": source_15.get("reviewed_task"),
            "expected_verdict": PHASE_2C_15_VERDICT,
            "observed_verdict": source_15.get("observed_verdict"),
            "authorization_result": source_15.get("authorization_result"),
            "decision_target_id": source_15.get("decision_target_id"),
            "decision_target_slice": source_15.get("decision_target_slice"),
            "authorization_matches_phase_2c_16_target": source_15.get(
                "authorization_matches_phase_2c_16_target"
            ),
        },
        "source_report_snapshot": {
            "status": source_report.get("status"),
            "overall_status": source_report.get("overall_status"),
            "scope_narrowed_to_one_example": source_report.get("scope_narrowed_to_one_example"),
            "needs_scope_confirmation": source_report.get("needs_scope_confirmation"),
            "local_only": source_report.get("local_only"),
            "deterministic": source_report.get("deterministic"),
            "report_only": source_report.get("report_only"),
            "dry_run_only": source_report.get("dry_run_only"),
            "mock_only": source_report.get("mock_only"),
            "runner_added": source_report.get("runner_added"),
            "adapter_added": source_report.get("adapter_added"),
            "execution_path_added": source_report.get("execution_path_added"),
            "broker_added": source_report.get("broker_added"),
            "scheduler_added": source_report.get("scheduler_added"),
            "queue_added": source_report.get("queue_added"),
            "worker_added": source_report.get("worker_added"),
            "ai_loop_added": source_report.get("ai_loop_added"),
            "ssh_netconf_restconf_live_device_touched": source_report.get(
                "ssh_netconf_restconf_live_device_touched"
            ),
            "provider_api_model_secrets_touched": source_report.get(
                "provider_api_model_secrets_touched"
            ),
            "config_backup_or_change_behavior_added": source_report.get(
                "config_backup_or_change_behavior_added"
            ),
            "production_execution_path_added": source_report.get("production_execution_path_added"),
            "day1_day160_rewritten_or_replaced": source_report.get(
                "day1_day160_rewritten_or_replaced"
            ),
            "second_safety_matrix_created": source_report.get("second_safety_matrix_created"),
            "next_phase_started": source_report.get("next_phase_started"),
            "extra_slice_selected_or_implemented": source_report.get(
                "extra_slice_selected_or_implemented"
            ),
        },
    }


def _phase_2c_16_acceptance_facts(source_review: Mapping[str, Any]) -> Dict[str, bool]:
    validation = source_review.get("source_validation", {})
    if not isinstance(validation, Mapping):
        validation = {}
    source_15 = source_review.get("phase_2c_15_source_review", {})
    if not isinstance(source_15, Mapping):
        source_15 = {}
    snapshot = source_review.get("source_report_snapshot", {})
    if not isinstance(snapshot, Mapping):
        snapshot = {}
    return {
        "phase_2c_15_authorization_confirmed": (
            source_15.get("reviewed_task") == PHASE_2C_15_TASK_NAME
            and source_15.get("observed_verdict") == PHASE_2C_15_VERDICT
            and source_15.get("authorization_result") == PHASE_2C_15_AUTHORIZATION_RESULT
            and source_15.get("decision_target_id") == PHASE_2C_15_DECISION_TARGET_ID
            and source_15.get("decision_target_slice") == PHASE_2C_15_DECISION_TARGET_SLICE
            and source_15.get("authorization_matches_phase_2c_16_target") is True
        ),
        "phase_2c_16_validation_passed": validation.get("valid") is True,
        "selected_next_slice_matches": source_review.get("selected_next_slice") == SELECTED_NEXT_SLICE,
        "final_verdict_matches": source_review.get("observed_verdict") == PHASE_2C_16_VERDICT,
        "local_result_envelope_contract_implemented": source_review.get(
            "local_result_envelope_contract_implemented"
        )
        is True,
        "contract_shape_defined": source_review.get("contract_shape_defined") is True,
        "validator_added": source_review.get("validator_added") is True,
        "sample_envelope_static_fixture_only": source_review.get(
            "sample_envelope_static_fixture_only"
        )
        is True,
        "contract_not_runtime_infrastructure": source_review.get(
            "contract_not_runtime_infrastructure"
        )
        is True,
        "contract_not_result_processing_infrastructure": source_review.get(
            "contract_not_result_processing_infrastructure"
        )
        is True,
        "scope_not_narrowed_to_one_example": snapshot.get("scope_narrowed_to_one_example") is False,
        "local_only": snapshot.get("local_only") is True,
        "deterministic": snapshot.get("deterministic") is True,
        "report_only_dry_run_mock_only": (
            snapshot.get("report_only") is True
            and snapshot.get("dry_run_only") is True
            and snapshot.get("mock_only") is True
        ),
        "runner_adapter_execution_path_added": (
            snapshot.get("runner_added") is False
            and snapshot.get("adapter_added") is False
            and snapshot.get("execution_path_added") is False
        ),
        "queue_scheduler_worker_ai_loop_added": (
            snapshot.get("broker_added") is False
            and snapshot.get("scheduler_added") is False
            and snapshot.get("queue_added") is False
            and snapshot.get("worker_added") is False
            and snapshot.get("ai_loop_added") is False
        ),
        "ssh_netconf_restconf_live_device_touched": (
            snapshot.get("ssh_netconf_restconf_live_device_touched") is False
        ),
        "provider_api_model_secrets_touched": (
            snapshot.get("provider_api_model_secrets_touched") is False
        ),
        "config_backup_change_behavior_added": (
            snapshot.get("config_backup_or_change_behavior_added") is False
        ),
        "production_execution_path_added": snapshot.get("production_execution_path_added") is False,
        "day1_day160_rewritten_or_replaced": (
            snapshot.get("day1_day160_rewritten_or_replaced") is False
        ),
        "second_safety_matrix_created": snapshot.get("second_safety_matrix_created") is False,
        "next_phase_started": snapshot.get("next_phase_started") is False,
        "extra_slice_selected_or_implemented": (
            snapshot.get("extra_slice_selected_or_implemented") is False
        ),
    }


def _acceptance_decision(phase_2c_16_evidence_found: bool, acceptance_facts: Mapping[str, bool]) -> str:
    if phase_2c_16_evidence_found is not True:
        return "NEEDS_EVIDENCE"
    if all(acceptance_facts.values()):
        return "ACCEPT"
    return "NOT_ACCEPT"


def _acceptance_checks(
    phase_2c_16_evidence_found: bool,
    acceptance_facts: Mapping[str, bool],
    acceptance_decision: str,
) -> Tuple[Dict[str, Any], ...]:
    checks = (
        ("Phase 2C-16 evidence is available for review", phase_2c_16_evidence_found),
        ("Phase 2C-15 authorized local_result_envelope_contract", acceptance_facts.get("phase_2c_15_authorization_confirmed") is True),
        ("Phase 2C-16 validation passed", acceptance_facts.get("phase_2c_16_validation_passed") is True),
        ("Phase 2C-16 selected slice matches local_result_envelope_contract", acceptance_facts.get("selected_next_slice_matches") is True),
        ("Phase 2C-16 implemented the local result envelope contract", acceptance_facts.get("local_result_envelope_contract_implemented") is True),
        ("Phase 2C-16 defined contract shape and validator", (
            acceptance_facts.get("contract_shape_defined") is True
            and acceptance_facts.get("validator_added") is True
        )),
        ("Phase 2C-16 kept sample envelope static fixture only", acceptance_facts.get("sample_envelope_static_fixture_only") is True),
        ("Phase 2C-16 did not create runtime or processing infrastructure", (
            acceptance_facts.get("contract_not_runtime_infrastructure") is True
            and acceptance_facts.get("contract_not_result_processing_infrastructure") is True
        )),
        ("Phase 2C-16 remained general and not tied to one example", acceptance_facts.get("scope_not_narrowed_to_one_example") is True),
        ("Phase 2C-16 stayed local and deterministic", (
            acceptance_facts.get("local_only") is True
            and acceptance_facts.get("deterministic") is True
        )),
        ("Phase 2C-16 stayed report-only / dry-run / mock-only", acceptance_facts.get("report_only_dry_run_mock_only") is True),
        ("Phase 2C-16 avoided runner / adapter / execution path", acceptance_facts.get("runner_adapter_execution_path_added") is True),
        ("Phase 2C-16 avoided queue / scheduler / worker / AI loop", acceptance_facts.get("queue_scheduler_worker_ai_loop_added") is True),
        ("Phase 2C-16 avoided SSH / NETCONF / RESTCONF / live devices", acceptance_facts.get("ssh_netconf_restconf_live_device_touched") is True),
        ("Phase 2C-16 avoided provider / API / model / secrets", acceptance_facts.get("provider_api_model_secrets_touched") is True),
        ("Phase 2C-16 avoided config backup / config change behavior", acceptance_facts.get("config_backup_change_behavior_added") is True),
        ("Phase 2C-16 avoided production execution path", acceptance_facts.get("production_execution_path_added") is True),
        ("Day1-Day160 was not rewritten or replaced", acceptance_facts.get("day1_day160_rewritten_or_replaced") is True),
        ("No second safety matrix was created", acceptance_facts.get("second_safety_matrix_created") is True),
        ("Phase 2C-17 does not continue 2C-16", True),
        ("Phase 2C-17 does not select the next slice or start Phase 2C-18", True),
    )
    return tuple(
        {
            "check": name,
            "passed": passed is True,
            "status": "PASS"
            if passed is True
            else ("NEEDS_EVIDENCE" if acceptance_decision == "NEEDS_EVIDENCE" else "FAIL"),
        }
        for name, passed in checks
    )


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_17": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_17_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("acceptance_decision") not in ALLOWED_ACCEPTANCE_DECISIONS:
        errors.append("ACCEPTANCE_DECISION_INVALID")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    blocked_flags = (
        "needs_scope_confirmation",
        "agents_md_modified",
        "phase_2c_16_source_task_rerun",
        "phase_2c_16_implementation_modified",
        "local_result_envelope_contract_modified",
        "phase_2c_16_continued",
        "next_slice_selected",
        "next_implementation_started",
        "phase_2c_18_started",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append("PHASE_2C_17_FORBIDDEN_SCOPE_OPENED")

    expected_verdict = {
        "FINAL_VERDICT": report.get("final_verdict"),
        "ACCEPTANCE_DECISION": report.get("acceptance_decision"),
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "REQUIRED_REFERENCE_DOCUMENTS_READ": "YES",
        "SCOPE_CONFIRMED_IN_WRITING": "YES",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "PHASE_2C_15_AUTHORIZATION_CONFIRMED": "YES"
        if report.get("phase_2c_15_authorization_confirmed")
        else "NO",
        "PHASE_2C_16_VALIDATION_PASSED": "YES" if report.get("phase_2c_16_validation_passed") else "NO",
        "PHASE_2C_16_EVIDENCE_FOUND": "YES" if report.get("phase_2c_16_evidence_found") else "NO",
        "LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED": report.get(
            "local_result_envelope_contract_accepted"
        ),
        "REPORT_ONLY_ARTIFACT_CREATED": "YES",
        "PHASE_2C_16_CONTINUED": "NO",
        "NEXT_SLICE_SELECTED": "NO",
        "NEXT_IMPLEMENTATION_STARTED": "NO",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED": "NO",
        "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    if report.get("acceptance_decision") == "ACCEPT":
        required_accept_flags = (
            "phase_2c_15_authorization_confirmed",
            "phase_2c_16_evidence_found",
            "phase_2c_16_validation_passed",
            "phase_2c_16_within_authorized_boundary",
            "phase_2c_16_forbidden_execution_paths_avoided",
            "local_result_envelope_contract_local_bounded_interview_mvp_suitable",
        )
        if any(report.get(flag) is not True for flag in required_accept_flags):
            errors.append("ACCEPT_DECISION_WITHOUT_REQUIRED_EVIDENCE")
        if any(check.get("status") != "PASS" for check in report.get("acceptance_checks", [])):
            errors.append("ACCEPTANCE_CHECK_NOT_PASS")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "acceptance_checks_reviewed": len(report.get("acceptance_checks", [])),
        "existing_artifacts_reviewed": len(report.get("existing_artifacts_reviewed", [])),
        "forbidden_scope_items_checked": len(report.get("forbidden_scope", [])),
    }


def build_phase_2c_17_post_implementation_slice_acceptance_review_report(project_root: Path) -> Dict[str, Any]:
    source_review = _phase_2c_16_source_review(project_root)
    acceptance_facts = _phase_2c_16_acceptance_facts(source_review)
    phase_2c_16_evidence_found = source_review.get("reviewed_task") == PHASE_2C_16_TASK_NAME
    acceptance_decision = _acceptance_decision(phase_2c_16_evidence_found, acceptance_facts)
    final_verdict = {
        "ACCEPT": FINAL_VERDICT,
        "NOT_ACCEPT": NOT_ACCEPT_VERDICT,
        "NEEDS_EVIDENCE": NEEDS_EVIDENCE_VERDICT,
    }[acceptance_decision]
    local_result_envelope_contract_accepted = {
        "ACCEPT": "YES",
        "NOT_ACCEPT": "NO",
        "NEEDS_EVIDENCE": "NEEDS_EVIDENCE",
    }[acceptance_decision]
    phase_2c_16_within_authorized_boundary = (
        acceptance_facts.get("phase_2c_15_authorization_confirmed") is True
        and acceptance_facts.get("phase_2c_16_validation_passed") is True
        and acceptance_facts.get("selected_next_slice_matches") is True
        and acceptance_facts.get("local_result_envelope_contract_implemented") is True
        and acceptance_facts.get("contract_shape_defined") is True
        and acceptance_facts.get("validator_added") is True
        and acceptance_facts.get("sample_envelope_static_fixture_only") is True
        and acceptance_facts.get("scope_not_narrowed_to_one_example") is True
        and acceptance_facts.get("local_only") is True
        and acceptance_facts.get("deterministic") is True
        and acceptance_facts.get("report_only_dry_run_mock_only") is True
    )
    phase_2c_16_forbidden_execution_paths_avoided = (
        acceptance_facts.get("runner_adapter_execution_path_added") is True
        and acceptance_facts.get("queue_scheduler_worker_ai_loop_added") is True
        and acceptance_facts.get("ssh_netconf_restconf_live_device_touched") is True
        and acceptance_facts.get("provider_api_model_secrets_touched") is True
        and acceptance_facts.get("config_backup_change_behavior_added") is True
        and acceptance_facts.get("production_execution_path_added") is True
        and acceptance_facts.get("day1_day160_rewritten_or_replaced") is True
        and acceptance_facts.get("second_safety_matrix_created") is True
        and acceptance_facts.get("next_phase_started") is True
        and acceptance_facts.get("extra_slice_selected_or_implemented") is True
    )
    local_result_envelope_contract_local_bounded_interview_mvp_suitable = (
        phase_2c_16_within_authorized_boundary
        and acceptance_facts.get("contract_not_runtime_infrastructure") is True
        and acceptance_facts.get("contract_not_result_processing_infrastructure") is True
        and phase_2c_16_forbidden_execution_paths_avoided
    )

    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": final_verdict,
        "acceptance_decision": acceptance_decision,
        "phase_goal": PHASE_GOAL,
        "acceptance_review_questions": list(ACCEPTANCE_REVIEW_QUESTIONS),
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "reference_examples_only_not_phase_2c_17_implementation_targets",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_reviewed": list(EXISTING_ARTIFACTS_REVIEWED),
        "artifact_records": [_artifact_record(project_root, path) for path in EXISTING_ARTIFACTS_REVIEWED],
        "source_evidence_review": source_review,
        "phase_2c_16_acceptance_facts": dict(acceptance_facts),
        "phase_2c_15_authorization_confirmed": acceptance_facts.get(
            "phase_2c_15_authorization_confirmed"
        )
        is True,
        "phase_2c_16_evidence_found": phase_2c_16_evidence_found,
        "phase_2c_16_validation_passed": acceptance_facts.get("phase_2c_16_validation_passed") is True,
        "phase_2c_16_within_authorized_boundary": phase_2c_16_within_authorized_boundary,
        "phase_2c_16_forbidden_execution_paths_avoided": phase_2c_16_forbidden_execution_paths_avoided,
        "local_result_envelope_contract_local_bounded_interview_mvp_suitable": (
            local_result_envelope_contract_local_bounded_interview_mvp_suitable
        ),
        "local_result_envelope_contract_accepted": local_result_envelope_contract_accepted,
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "non_execution_statement": (
            "Phase 2C-17 is a report-only acceptance review of existing Phase "
            "2C-16 local_result_envelope_contract evidence. It does not "
            "continue Phase 2C-16, select a next slice, start Phase 2C-18, "
            "modify the contract, or add runner, adapter, execution, "
            "live-device, provider/API/model, secret, backup, "
            "configuration-change, production, Day1-Day160 replacement, or "
            "second-safety-matrix behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": final_verdict,
            "ACCEPTANCE_DECISION": acceptance_decision,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "REQUIRED_REFERENCE_DOCUMENTS_READ": "YES",
            "SCOPE_CONFIRMED_IN_WRITING": "YES",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "PHASE_2C_15_AUTHORIZATION_CONFIRMED": "YES"
            if acceptance_facts.get("phase_2c_15_authorization_confirmed")
            else "NO",
            "PHASE_2C_16_VALIDATION_PASSED": "YES"
            if acceptance_facts.get("phase_2c_16_validation_passed")
            else "NO",
            "PHASE_2C_16_EVIDENCE_FOUND": "YES" if phase_2c_16_evidence_found else "NO",
            "LOCAL_RESULT_ENVELOPE_CONTRACT_ACCEPTED": local_result_envelope_contract_accepted,
            "REPORT_ONLY_ARTIFACT_CREATED": "YES",
            "PHASE_2C_16_CONTINUED": "NO",
            "NEXT_SLICE_SELECTED": "NO",
            "NEXT_IMPLEMENTATION_STARTED": "NO",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED": "NO",
            "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["acceptance_checks"] = list(
        _acceptance_checks(phase_2c_16_evidence_found, acceptance_facts, acceptance_decision)
    )
    report["summary"] = {
        "acceptance_decision": acceptance_decision,
        "phase_2c_15_authorization_confirmed": report["phase_2c_15_authorization_confirmed"],
        "phase_2c_16_evidence_found": phase_2c_16_evidence_found,
        "phase_2c_16_validation_passed": report["phase_2c_16_validation_passed"],
        "phase_2c_16_within_authorized_boundary": phase_2c_16_within_authorized_boundary,
        "phase_2c_16_forbidden_execution_paths_avoided": phase_2c_16_forbidden_execution_paths_avoided,
        "local_result_envelope_contract_local_bounded_interview_mvp_suitable": (
            local_result_envelope_contract_local_bounded_interview_mvp_suitable
        ),
        "local_result_envelope_contract_accepted": local_result_envelope_contract_accepted,
        "report_only_artifact_created": True,
        "phase_2c_16_continued": False,
        "next_slice_selected": False,
        "next_implementation_started": False,
        "runner_adapter_execution_path_added": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_change_behavior_added": False,
        "production_execution_path_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": final_verdict,
    }
    validation = validate_phase_2c_17_report(report)
    report["validation"] = validation
    if not validation["valid"]:
        report["status"] = "FAIL"
        report["overall_status"] = "FAIL"
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


def _check_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('check')))}</td>"
        f"<td>{html.escape(str(item.get('status')))}</td>"
        f"<td>{html.escape(str(item.get('passed')))}</td>"
        "</tr>"
        for item in values
    )


def _write_text_with_windows_long_path_fallback(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_path.write_text(content, encoding="utf-8")
        return
    except FileNotFoundError:
        if os.name != "nt":
            raise

    resolved = output_path.resolve()
    path_text = str(resolved)
    if path_text.startswith("\\\\?\\"):
        extended_path = Path(path_text)
    elif path_text.startswith("\\\\"):
        extended_path = Path("\\\\?\\UNC\\" + path_text[2:])
    else:
        extended_path = Path("\\\\?\\" + path_text)
    extended_path.write_text(content, encoding="utf-8")


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    _write_text_with_windows_long_path_fallback(
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
  <p>Acceptance decision: <strong>{html.escape(str(report["acceptance_decision"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Acceptance Checks</h2>
  <table><thead><tr><th>Check</th><th>Status</th><th>Passed</th></tr></thead><tbody>{_check_rows(report["acceptance_checks"])}</tbody></table>
  <h2>Phase 2C-16 Acceptance Facts</h2>
  <table><tbody>{_dict_rows(report["phase_2c_16_acceptance_facts"])}</tbody></table>
  <h2>Existing Artifacts Reviewed</h2>
  <ul>{_list_items(report["existing_artifacts_reviewed"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
    )


def write_phase_2c_17_post_implementation_slice_acceptance_review_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_17_post_implementation_slice_acceptance_review_report(
        project_root
    )
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    _write_text_with_windows_long_path_fallback(
        json_path,
        json.dumps(report_data, indent=2, sort_keys=True),
    )
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_17_post_implementation_slice_acceptance_review(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_17_post_implementation_slice_acceptance_review_report(project_root)
    json_path, html_path = write_phase_2c_17_post_implementation_slice_acceptance_review_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"acceptance_decision: {report['summary']['acceptance_decision']}")
    print(
        "phase_2c_15_authorization_confirmed: "
        f"{str(report['summary']['phase_2c_15_authorization_confirmed']).lower()}"
    )
    print(f"phase_2c_16_evidence_found: {str(report['summary']['phase_2c_16_evidence_found']).lower()}")
    print(
        "phase_2c_16_validation_passed: "
        f"{str(report['summary']['phase_2c_16_validation_passed']).lower()}"
    )
    print(
        "phase_2c_16_within_authorized_boundary: "
        f"{str(report['summary']['phase_2c_16_within_authorized_boundary']).lower()}"
    )
    print(
        "phase_2c_16_forbidden_execution_paths_avoided: "
        f"{str(report['summary']['phase_2c_16_forbidden_execution_paths_avoided']).lower()}"
    )
    print(
        "local_result_envelope_contract_local_bounded_interview_mvp_suitable: "
        f"{str(report['summary']['local_result_envelope_contract_local_bounded_interview_mvp_suitable']).lower()}"
    )
    print(
        "local_result_envelope_contract_accepted: "
        f"{report['summary']['local_result_envelope_contract_accepted']}"
    )
    print(f"report_only_artifact_created: {str(report['summary']['report_only_artifact_created']).lower()}")
    print(f"phase_2c_16_continued: {str(report['summary']['phase_2c_16_continued']).lower()}")
    print(f"next_slice_selected: {str(report['summary']['next_slice_selected']).lower()}")
    print(f"next_implementation_started: {str(report['summary']['next_implementation_started']).lower()}")
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
        "config_backup_change_behavior_added: "
        f"{str(report['summary']['config_backup_change_behavior_added']).lower()}"
    )
    print(
        "production_execution_path_added: "
        f"{str(report['summary']['production_execution_path_added']).lower()}"
    )
    print(
        "day1_day160_rewritten_or_replaced: "
        f"{str(report['summary']['day1_day160_rewritten_or_replaced']).lower()}"
    )
    print(f"second_safety_matrix_created: {str(report['summary']['second_safety_matrix_created']).lower()}")
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
