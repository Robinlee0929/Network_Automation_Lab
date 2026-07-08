"""Phase 2C-16 Interview MVP local result envelope contract.

This module defines a deterministic, local, report-only contract for Interview
MVP result envelopes. It validates shape and safety metadata only. It does not
create a runner, adapter, scheduler, queue, worker, AI loop, provider/API/model
integration, live device path, SSH/NETCONF/RESTCONF path, config backup/change
behavior, or production execution path.
"""

from __future__ import annotations

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from report_file_utils import write_text_with_parents

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate import (
    AUTHORIZATION_RESULT as PHASE_2C_15_AUTHORIZATION_RESULT,
    DECISION_TARGET_ID as PHASE_2C_15_DECISION_TARGET_ID,
    DECISION_TARGET_SLICE as PHASE_2C_15_DECISION_TARGET_SLICE,
    FINAL_VERDICT as PHASE_2C_15_VERDICT,
    TASK_NAME as PHASE_2C_15_TASK_NAME,
    build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report,
    validate_phase_2c_15_report,
)


PHASE = "2C-16"
TASK_NAME = "phase2c-16-interview-mvp-local-result-envelope-contract"
TITLE = "Phase 2C-16 Interview MVP Local Result Envelope Contract"
MODE = "local_result_envelope_contract_report_only"
SCOPE = "local_deterministic_report_only_result_envelope_contract"
STATUS = "PASS"
SELECTED_CANDIDATE_ID = "candidate-03"
SELECTED_NEXT_SLICE = "local_result_envelope_contract"
FINAL_VERDICT = "PHASE_2C_16_LOCAL_RESULT_ENVELOPE_CONTRACT_IMPLEMENTED_REPORT_ONLY"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_16_interview_mvp_local_result_envelope_contract.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_16_interview_mvp_local_result_envelope_contract.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_16_interview_mvp_local_result_envelope_contract.md"

ENVELOPE_SCHEMA_VERSION = "phase2c.local-result-envelope.v1"
ALLOWED_RESULT_STATUSES = ("PASS", "WARN", "FAIL", "BLOCKED", "REVIEW_ONLY", "LOCKED")
ALLOWED_EVIDENCE_STATUSES = ("PRESENT", "MISSING", "NOT_APPLICABLE")

PHASE_GOAL = (
    "Implement the Phase 2C-15 authorized candidate-03 / "
    "local_result_envelope_contract as a local, deterministic, report-only "
    "contract for Interview MVP result envelope shape and validation evidence."
)

EXAMPLE_JOB_TYPES = (
    "local static report result",
    "local artifact validation result",
    "future mock-only Interview MVP local result",
)

FORBIDDEN_SCOPE = (
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
    "Phase 2C-17 start",
    "extra slice selection or implementation",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "docs/phase_2c/phase_2c_11_interview_mvp_scope_architecture_gate.md",
    "docs/phase_2c/phase_2c_12_interview_mvp_implementation_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_13_interview_mvp_implementation_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_14_interview_mvp_implementation_slice_final_selection_gate.md",
    "docs/phase_2c/phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.md",
    "phase_2a_05_dry_run_result_envelope_renderer.py",
    "phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate.py",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "reports/report_index.html",
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: define and validate a local deterministic result envelope "
    "contract with a static sample envelope, reviewer-visible evidence, "
    "warnings, status fields, and forbidden-scope metadata. Not allowed: "
    "runtime serialization infrastructure, result processing infrastructure, "
    "runner, adapter, scheduler, queue, broker, worker, AI loop, live-device "
    "access, SSH, NETCONF, RESTCONF, provider/API/model/secret access, command "
    "execution, config backup/change behavior, production execution, "
    "Day1-Day160 rewrite, second safety matrix, Phase 2C-17, or extra slices."
)

REQUIRED_ENVELOPE_FIELDS = (
    "schema_version",
    "envelope_id",
    "contract_name",
    "phase",
    "local_task_identity",
    "dry_run_mock_status",
    "result_status",
    "report_only_evidence",
    "warnings",
    "forbidden_scope_metadata",
    "non_execution_proof",
    "fixture_notice",
)

NON_EXECUTABLE_FIELDS = (
    "runner_call",
    "adapter_call",
    "broker_call",
    "scheduler_call",
    "queue_call",
    "worker_call",
    "ai_loop",
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
    "config_backup_action",
    "config_change_action",
)

SAFETY_FLAGS = {
    "phase_2c_16_started": True,
    "local_result_envelope_contract_implemented": True,
    "contract_shape_defined": True,
    "validator_added": True,
    "sample_envelope_static_fixture_only": True,
    "local_only": True,
    "deterministic": True,
    "report_only": True,
    "dry_run_only": True,
    "mock_only": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_goal_confirmed": True,
    "phase_2c_15_authorization_confirmed": True,
    "scope_narrowed_to_one_example": False,
    "needs_scope_confirmation": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "ai_loop_added": False,
    "provider_api_model_secrets_touched": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "real_command_execution_added": False,
    "config_backup_or_change_behavior_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "next_phase_started": False,
    "extra_slice_selected_or_implemented": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_16_LOCAL_RESULT_ENVELOPE_CONTRACT",
    "SELECTED_NEXT_SLICE_LOCAL_RESULT_ENVELOPE_CONTRACT",
    "PHASE_GOAL_CONFIRMED_YES",
    "PHASE_2C_15_AUTHORIZATION_CONFIRMED_YES",
    "SCOPE_NARROWED_TO_ONE_EXAMPLE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "CONTRACT_SHAPE_DEFINED_YES",
    "VALIDATOR_ADDED_YES",
    "SAMPLE_ENVELOPE_STATIC_FIXTURE_ONLY_YES",
    "LOCAL_ONLY_YES",
    "DETERMINISTIC_YES",
    "REPORT_ONLY_DRY_RUN_MOCK_ONLY_YES",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_CHANGE_ADDED_NO",
    "PRODUCTION_EXECUTION_PATH_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    "NEXT_PHASE_STARTED_NO",
    "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED_NO",
    FINAL_VERDICT,
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def build_local_result_envelope_contract() -> Dict[str, Any]:
    return {
        "contract_name": SELECTED_NEXT_SLICE,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "contract_status": "READY_REPORT_ONLY",
        "required_fields": list(REQUIRED_ENVELOPE_FIELDS),
        "allowed_result_statuses": list(ALLOWED_RESULT_STATUSES),
        "allowed_evidence_statuses": list(ALLOWED_EVIDENCE_STATUSES),
        "field_contract": {
            "local_task_identity": {
                "required_keys": ["task_id", "task_label", "phase", "source_kind"],
                "purpose": "Identify a local mock/report-only task without implying live execution.",
            },
            "dry_run_mock_status": {
                "required_keys": ["report_only", "dry_run_only", "mock_only", "local_only", "deterministic"],
                "purpose": "Preserve the non-executing safety baseline in every envelope.",
            },
            "result_status": {
                "allowed_values": list(ALLOWED_RESULT_STATUSES),
                "purpose": "Expose reviewer-visible status without executing or normalizing runtime output.",
            },
            "report_only_evidence": {
                "required_keys": ["evidence_id", "status", "path", "description", "source"],
                "purpose": "Bind local reviewer evidence to an envelope without claiming live observations.",
            },
            "forbidden_scope_metadata": {
                "required_keys": [
                    "runner_added",
                    "adapter_added",
                    "execution_path_added",
                    "ssh_netconf_restconf_live_device_touched",
                    "provider_api_model_secrets_touched",
                    "config_backup_or_change_behavior_added",
                    "production_execution_path_added",
                ],
                "purpose": "Make forbidden scope explicit and machine-checkable.",
            },
        },
        "non_executable_fields": list(NON_EXECUTABLE_FIELDS),
        "not_runtime_infrastructure": True,
        "not_result_processing_infrastructure": True,
        "sample_only_required": True,
        "safety_baseline": "report-only / dry-run / mock-only",
    }


def build_sample_local_result_envelope() -> Dict[str, Any]:
    seed = {
        "phase": PHASE,
        "task": TASK_NAME,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "result_status": "REVIEW_ONLY",
    }
    envelope = {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "envelope_id": f"PHASE_2C_16_LOCAL_RESULT_ENVELOPE_{_stable_digest(seed)}",
        "contract_name": SELECTED_NEXT_SLICE,
        "phase": PHASE,
        "local_task_identity": {
            "task_id": "interview-mvp-local-result-envelope-contract-sample",
            "task_label": "Interview MVP local result envelope contract sample",
            "phase": PHASE,
            "source_kind": "static_contract_fixture",
            "example_job_type": "contract_shape_only_not_job_execution",
        },
        "dry_run_mock_status": {
            "report_only": True,
            "dry_run_only": True,
            "mock_only": True,
            "local_only": True,
            "deterministic": True,
            "live_device_observed": False,
        },
        "result_status": "REVIEW_ONLY",
        "report_only_evidence": [
            {
                "evidence_id": "PHASE_2C_16_STATIC_CONTRACT_SAMPLE",
                "status": "PRESENT",
                "path": REPORT_JSON.as_posix(),
                "description": "Static local contract sample generated for reviewer evidence only.",
                "source": "deterministic_contract_fixture",
                "not_live_output": True,
            }
        ],
        "warnings": [
            {
                "warning_id": "STATIC_SAMPLE_NOT_RUNTIME_RESULT",
                "status": "WARN",
                "message": "This envelope is a static contract example and must not be treated as live execution output.",
            }
        ],
        "forbidden_scope_metadata": {
            "runner_added": False,
            "adapter_added": False,
            "execution_path_added": False,
            "broker_added": False,
            "scheduler_added": False,
            "queue_added": False,
            "worker_added": False,
            "ai_loop_added": False,
            "ssh_netconf_restconf_live_device_touched": False,
            "provider_api_model_secrets_touched": False,
            "config_backup_or_change_behavior_added": False,
            "production_execution_path_added": False,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "next_phase_started": False,
            "extra_slice_selected_or_implemented": False,
        },
        "non_execution_proof": {
            "fixture_only": True,
            "schema_contract_only": True,
            "runtime_result_consumed": False,
            "live_output_claimed": False,
            "contains_execution_payload": False,
            **{f"contains_{field}": False for field in NON_EXECUTABLE_FIELDS},
        },
        "fixture_notice": "STATIC_CONTRACT_EXAMPLE_NOT_LIVE_OUTPUT",
        **{field: None for field in NON_EXECUTABLE_FIELDS},
    }
    return envelope


def validate_local_result_envelope(envelope: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in envelope:
            errors.append(f"REQUIRED_ENVELOPE_FIELD_MISSING:{field}")
    if envelope.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
        errors.append("SCHEMA_VERSION_MISMATCH")
    if envelope.get("contract_name") != SELECTED_NEXT_SLICE:
        errors.append("CONTRACT_NAME_MISMATCH")
    if envelope.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if envelope.get("result_status") not in ALLOWED_RESULT_STATUSES:
        errors.append("RESULT_STATUS_NOT_ALLOWED")
    if envelope.get("fixture_notice") != "STATIC_CONTRACT_EXAMPLE_NOT_LIVE_OUTPUT":
        errors.append("FIXTURE_NOTICE_MISSING")

    local_task_identity = envelope.get("local_task_identity", {})
    if not isinstance(local_task_identity, Mapping):
        errors.append("LOCAL_TASK_IDENTITY_NOT_OBJECT")
        local_task_identity = {}
    for key in ("task_id", "task_label", "phase", "source_kind"):
        if key not in local_task_identity:
            errors.append(f"LOCAL_TASK_IDENTITY_FIELD_MISSING:{key}")
    if local_task_identity.get("source_kind") != "static_contract_fixture":
        errors.append("LOCAL_TASK_IDENTITY_SOURCE_KIND_NOT_STATIC_FIXTURE")

    dry_run_mock_status = envelope.get("dry_run_mock_status", {})
    if not isinstance(dry_run_mock_status, Mapping):
        errors.append("DRY_RUN_MOCK_STATUS_NOT_OBJECT")
        dry_run_mock_status = {}
    for flag_name in ("report_only", "dry_run_only", "mock_only", "local_only", "deterministic"):
        if dry_run_mock_status.get(flag_name) is not True:
            errors.append(f"DRY_RUN_MOCK_STATUS_FLAG_NOT_TRUE:{flag_name}")
    if dry_run_mock_status.get("live_device_observed") is not False:
        errors.append("LIVE_DEVICE_OBSERVED_NOT_FALSE")

    evidence_items = envelope.get("report_only_evidence", [])
    if not isinstance(evidence_items, Sequence) or isinstance(evidence_items, (str, bytes)):
        errors.append("REPORT_ONLY_EVIDENCE_NOT_LIST")
        evidence_items = []
    if not evidence_items:
        errors.append("REPORT_ONLY_EVIDENCE_EMPTY")
    for index, item in enumerate(evidence_items):
        if not isinstance(item, Mapping):
            errors.append(f"REPORT_ONLY_EVIDENCE_ITEM_NOT_OBJECT:{index}")
            continue
        if item.get("status") not in ALLOWED_EVIDENCE_STATUSES:
            errors.append(f"REPORT_ONLY_EVIDENCE_STATUS_NOT_ALLOWED:{index}")
        if item.get("not_live_output") is not True:
            errors.append(f"REPORT_ONLY_EVIDENCE_NOT_LIVE_OUTPUT_FLAG_MISSING:{index}")
        for key in ("evidence_id", "path", "description", "source"):
            if key not in item:
                errors.append(f"REPORT_ONLY_EVIDENCE_FIELD_MISSING:{index}:{key}")

    warnings = envelope.get("warnings", [])
    if not isinstance(warnings, Sequence) or isinstance(warnings, (str, bytes)):
        errors.append("WARNINGS_NOT_LIST")
    elif not warnings:
        errors.append("WARNINGS_EMPTY_STATIC_SAMPLE_NOTICE_REQUIRED")

    forbidden_metadata = envelope.get("forbidden_scope_metadata", {})
    if not isinstance(forbidden_metadata, Mapping):
        errors.append("FORBIDDEN_SCOPE_METADATA_NOT_OBJECT")
        forbidden_metadata = {}
    if any(value is not False for value in forbidden_metadata.values()):
        errors.append(BLOCKED_VERDICT)

    proof = envelope.get("non_execution_proof", {})
    if not isinstance(proof, Mapping):
        errors.append("NON_EXECUTION_PROOF_NOT_OBJECT")
        proof = {}
    if proof.get("fixture_only") is not True:
        errors.append("NON_EXECUTION_PROOF_FIXTURE_ONLY_NOT_TRUE")
    if proof.get("schema_contract_only") is not True:
        errors.append("NON_EXECUTION_PROOF_SCHEMA_CONTRACT_ONLY_NOT_TRUE")
    for key in ("runtime_result_consumed", "live_output_claimed", "contains_execution_payload"):
        if proof.get(key) is not False:
            errors.append(f"NON_EXECUTION_PROOF_NOT_FALSE:{key}")
    for field in NON_EXECUTABLE_FIELDS:
        if envelope.get(field) is not None:
            errors.append(f"NON_EXECUTABLE_FIELD_POPULATED:{field}")
        if proof.get(f"contains_{field}") is not False:
            errors.append(f"NON_EXECUTION_PROOF_FIELD_NOT_FALSE:contains_{field}")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "required_fields_checked": len(REQUIRED_ENVELOPE_FIELDS),
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
        "evidence_items_checked": len(evidence_items),
    }


def _phase_2c_15_source_review(project_root: Path) -> Dict[str, Any]:
    source_report = build_phase_2c_15_interview_mvp_implementation_slice_kickoff_authorization_gate_report(
        project_root
    )
    source_validation = validate_phase_2c_15_report(source_report)
    return {
        "reviewed_task": PHASE_2C_15_TASK_NAME,
        "expected_verdict": PHASE_2C_15_VERDICT,
        "observed_verdict": source_report.get("final_verdict"),
        "source_validation": source_validation,
        "authorization_result": source_report.get("authorization_result"),
        "decision_target_id": source_report.get("decision_target_id"),
        "decision_target_slice": source_report.get("decision_target_slice"),
        "future_phase_implementation_authorized": source_report.get("future_phase_implementation_authorized"),
        "phase_2c_15_implements_slice": source_report.get("phase_2c_15_implements_slice"),
        "local_result_envelope_contract_implemented": source_report.get(
            "local_result_envelope_contract_implemented"
        ),
        "authorization_matches_phase_2c_16_target": (
            source_report.get("authorization_result") == PHASE_2C_15_AUTHORIZATION_RESULT
            and source_report.get("decision_target_id") == PHASE_2C_15_DECISION_TARGET_ID
            and source_report.get("decision_target_slice") == PHASE_2C_15_DECISION_TARGET_SLICE
        ),
    }


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_16": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_16_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("selected_candidate_id") != SELECTED_CANDIDATE_ID:
        errors.append("SELECTED_CANDIDATE_ID_MISMATCH")
    if report.get("selected_next_slice") != SELECTED_NEXT_SLICE:
        errors.append("SELECTED_NEXT_SLICE_MISMATCH")
    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if set(report.get("existing_artifacts_referenced", [])) != set(EXISTING_ARTIFACTS_REFERENCED):
        errors.append("EXISTING_ARTIFACTS_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    contract = report.get("local_result_envelope_contract", {})
    if not isinstance(contract, Mapping):
        errors.append("LOCAL_RESULT_ENVELOPE_CONTRACT_NOT_OBJECT")
        contract = {}
    if contract.get("contract_name") != SELECTED_NEXT_SLICE:
        errors.append("LOCAL_RESULT_ENVELOPE_CONTRACT_NAME_MISMATCH")
    if contract.get("required_fields") != list(REQUIRED_ENVELOPE_FIELDS):
        errors.append("LOCAL_RESULT_ENVELOPE_REQUIRED_FIELDS_MISMATCH")
    if contract.get("not_runtime_infrastructure") is not True:
        errors.append("LOCAL_RESULT_ENVELOPE_RUNTIME_INFRASTRUCTURE_NOT_BLOCKED")
    if contract.get("not_result_processing_infrastructure") is not True:
        errors.append("LOCAL_RESULT_ENVELOPE_PROCESSING_INFRASTRUCTURE_NOT_BLOCKED")

    envelope_validation = validate_local_result_envelope(report.get("sample_local_result_envelope", {}))
    if envelope_validation["valid"] is not True:
        errors.extend(f"LOCAL_RESULT_ENVELOPE:{error}" for error in envelope_validation["errors"])

    source_15 = report.get("phase_2c_15_source_review", {})
    if not isinstance(source_15, Mapping):
        errors.append("PHASE_2C_15_SOURCE_NOT_OBJECT")
        source_15 = {}
    if source_15.get("reviewed_task") != PHASE_2C_15_TASK_NAME:
        errors.append("PHASE_2C_15_TASK_MISMATCH")
    if source_15.get("observed_verdict") != PHASE_2C_15_VERDICT:
        errors.append("PHASE_2C_15_VERDICT_MISMATCH")
    if not isinstance(source_15.get("source_validation"), Mapping) or source_15["source_validation"].get("valid") is not True:
        errors.append("PHASE_2C_15_VALIDATION_NOT_PASS")
    if source_15.get("authorization_result") != "AUTHORIZED":
        errors.append("PHASE_2C_15_AUTHORIZATION_NOT_AUTHORIZED")
    if source_15.get("decision_target_id") != SELECTED_CANDIDATE_ID:
        errors.append("PHASE_2C_15_DECISION_TARGET_ID_MISMATCH")
    if source_15.get("decision_target_slice") != SELECTED_NEXT_SLICE:
        errors.append("PHASE_2C_15_DECISION_TARGET_SLICE_MISMATCH")
    if source_15.get("authorization_matches_phase_2c_16_target") is not True:
        errors.append("PHASE_2C_15_AUTHORIZATION_DOES_NOT_MATCH_PHASE_2C_16")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
        "PHASE_GOAL_CONFIRMED": "YES",
        "PHASE_2C_15_AUTHORIZATION_CONFIRMED": "YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "CONTRACT_SHAPE_DEFINED": "YES",
        "VALIDATOR_ADDED": "YES",
        "SAMPLE_ENVELOPE_STATIC_FIXTURE_ONLY": "YES",
        "LOCAL_ONLY": "YES",
        "DETERMINISTIC": "YES",
        "REPORT_ONLY_DRY_RUN_MOCK_ONLY": "YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_CHANGE_ADDED": "NO",
        "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
        "NEXT_PHASE_STARTED": "NO",
        "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED": "NO",
    }
    if report.get("machine_readable_verdict") != expected_verdict:
        errors.append("MACHINE_READABLE_VERDICT_MISMATCH")

    blocked_flags = (
        "scope_narrowed_to_one_example",
        "needs_scope_confirmation",
        "runner_added",
        "adapter_added",
        "execution_path_added",
        "broker_added",
        "scheduler_added",
        "queue_added",
        "worker_added",
        "ai_loop_added",
        "provider_api_model_secrets_touched",
        "ssh_netconf_restconf_live_device_touched",
        "real_command_execution_added",
        "config_backup_or_change_behavior_added",
        "production_execution_path_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "next_phase_started",
        "extra_slice_selected_or_implemented",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "envelope_validation": envelope_validation,
        "required_envelope_fields_checked": len(REQUIRED_ENVELOPE_FIELDS),
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
    }


def build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(
    project_root: Path,
) -> Dict[str, Any]:
    contract = build_local_result_envelope_contract()
    sample_envelope = build_sample_local_result_envelope()
    source_review = _phase_2c_15_source_review(project_root)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_not_implemented_as_jobs",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "local_result_envelope_contract": contract,
        "sample_local_result_envelope": deepcopy(sample_envelope),
        "phase_2c_15_source_review": source_review,
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "validation_method": (
            "The validator checks a static local envelope shape, allowed status "
            "values, report-only evidence markers, warnings, forbidden-scope "
            "metadata, and null non-executable fields. It consumes no runtime "
            "or live device output."
        ),
        "non_execution_statement": (
            "Phase 2C-16 defines and validates only a local deterministic "
            "result envelope contract and static sample. It does not add "
            "runner, adapter, scheduler, queue, broker, worker, AI loop, "
            "execution path, SSH, NETCONF, RESTCONF, live-device access, "
            "provider/API/model/secret access, config backup/change behavior, "
            "production execution, Day1-Day160 replacement, second safety "
            "matrix, next phase, or extra slice behavior."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
            "PHASE_GOAL_CONFIRMED": "YES",
            "PHASE_2C_15_AUTHORIZATION_CONFIRMED": "YES",
            "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "CONTRACT_SHAPE_DEFINED": "YES",
            "VALIDATOR_ADDED": "YES",
            "SAMPLE_ENVELOPE_STATIC_FIXTURE_ONLY": "YES",
            "LOCAL_ONLY": "YES",
            "DETERMINISTIC": "YES",
            "REPORT_ONLY_DRY_RUN_MOCK_ONLY": "YES",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "QUEUE_SCHEDULER_WORKER_AI_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_CHANGE_ADDED": "NO",
            "PRODUCTION_EXECUTION_PATH_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEXT_PHASE_STARTED": "NO",
            "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "phase_goal_confirmed": True,
        "phase_2c_15_authorization_confirmed": True,
        "scope_narrowed_to_one_example": False,
        "needs_scope_confirmation": False,
        "contract_shape_defined": True,
        "validator_added": True,
        "sample_envelope_static_fixture_only": True,
        "sample_envelope_id": sample_envelope["envelope_id"],
        "allowed_result_status_count": len(ALLOWED_RESULT_STATUSES),
        "required_envelope_fields_checked": len(REQUIRED_ENVELOPE_FIELDS),
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
        "local_only": True,
        "deterministic": True,
        "report_only_dry_run_mock_only": True,
        "runner_adapter_execution_path_added": False,
        "queue_scheduler_worker_ai_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_behavior_added": False,
        "production_execution_path_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "next_phase_started": False,
        "extra_slice_selected_or_implemented": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_16_report(report)
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
  <p>Selected next slice: <strong>{html.escape(str(report["selected_next_slice"]))}</strong></p>
  <p>Sample envelope id: <strong>{html.escape(str(report["summary"]["sample_envelope_id"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Contract</h2>
  <table><tbody>{_dict_rows(report["local_result_envelope_contract"])}</tbody></table>
  <h2>Sample Envelope</h2>
  <table><tbody>{_dict_rows(report["sample_local_result_envelope"])}</tbody></table>
  <h2>Phase 2C-15 Source Review</h2>
  <table><tbody>{_dict_rows(report["phase_2c_15_source_review"])}</tbody></table>
  <h2>Example Job Types</h2>
  <ul>{_list_items(report["example_job_types"])}</ul>
  <h2>Forbidden Scope</h2>
  <ul>{_list_items(report["forbidden_scope"])}</ul>
  <h2>Summary</h2>
  <table><tbody>{_dict_rows(report["summary"])}</tbody></table>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_phase_2c_16_interview_mvp_local_result_envelope_contract_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_with_parents(json_path, json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_16_interview_mvp_local_result_envelope_contract(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_16_interview_mvp_local_result_envelope_contract_report(project_root)
    json_path, html_path = write_phase_2c_16_interview_mvp_local_result_envelope_contract_reports(
        project_root,
        report,
    )
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Mode: {MODE}")
    print(f"selected_next_slice: {report['summary']['selected_next_slice']}")
    print(f"phase_goal_confirmed: {str(report['summary']['phase_goal_confirmed']).lower()}")
    print(
        "phase_2c_15_authorization_confirmed: "
        f"{str(report['summary']['phase_2c_15_authorization_confirmed']).lower()}"
    )
    print(f"scope_narrowed_to_one_example: {str(report['summary']['scope_narrowed_to_one_example']).lower()}")
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(f"contract_shape_defined: {str(report['summary']['contract_shape_defined']).lower()}")
    print(f"validator_added: {str(report['summary']['validator_added']).lower()}")
    print(
        "sample_envelope_static_fixture_only: "
        f"{str(report['summary']['sample_envelope_static_fixture_only']).lower()}"
    )
    print(f"sample_envelope_id: {report['summary']['sample_envelope_id']}")
    print(f"local_only: {str(report['summary']['local_only']).lower()}")
    print(f"deterministic: {str(report['summary']['deterministic']).lower()}")
    print(
        "report_only_dry_run_mock_only: "
        f"{str(report['summary']['report_only_dry_run_mock_only']).lower()}"
    )
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
        "production_execution_path_added: "
        f"{str(report['summary']['production_execution_path_added']).lower()}"
    )
    print(f"next_phase_started: {str(report['summary']['next_phase_started']).lower()}")
    print(
        "extra_slice_selected_or_implemented: "
        f"{str(report['summary']['extra_slice_selected_or_implemented']).lower()}"
    )
    print(f"Final verdict: {report['final_verdict']}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['final_verdict']}")
    return 0 if report["status"] == "PASS" else 1
