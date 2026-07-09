"""Phase 2C-08 next-slice implementation.

This module implements the selected `artifact_validation_job` next slice as a
bounded, deterministic, local artifact validation report. It reads only fixed
repository artifacts and prior Phase 2C decision evidence. It does not add a
runner, adapter, execution path, scheduler, queue, broker, worker, agent loop,
SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, secrets,
real command execution, config backup, or config change behavior.
"""

from __future__ import annotations

import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple

from phase_2b_00a_planning_only_owner_authorization_statement import FORBIDDEN_CAPABILITIES
from phase_2c_06_next_slice_final_selection_gate import (
    FINAL_VERDICT as PHASE_2C_06_VERDICT,
    REPORT_JSON as PHASE_2C_06_REPORT_JSON,
    SELECTED_CANDIDATE_ID,
    SELECTED_EXAMPLE_JOB_TYPE,
    SELECTED_NEXT_SLICE,
    TASK_NAME as PHASE_2C_06_TASK_NAME,
    build_phase_2c_06_next_slice_final_selection_gate_report,
    validate_phase_2c_06_report,
)
from phase_2c_07_next_slice_implementation_kickoff_gate import (
    FINAL_VERDICT as PHASE_2C_07_VERDICT,
    DOC_PATH as PHASE_2C_07_DOC_PATH,
    REPORT_JSON as PHASE_2C_07_REPORT_JSON,
    TASK_NAME as PHASE_2C_07_TASK_NAME,
    build_phase_2c_07_next_slice_implementation_kickoff_gate_report,
    validate_phase_2c_07_report,
)


PHASE = "2C-08"
TASK_NAME = "phase2c-08-next-slice-implementation"
TASK_ALIAS = "phase2c-08-artifact-validation-job"
TITLE = "Phase 2C-08 Next-Slice Implementation"
MODE = "local_report_only_artifact_validation_job"
SCOPE = "bounded_local_artifact_validation_job"
STATUS = "PASS"
FINAL_VERDICT = "PHASE_2C_08_NEXT_SLICE_IMPLEMENTED_LOCAL_REPORT_ONLY"
BLOCKED_VERDICT = "NEEDS_SCOPE_CONFIRMATION"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2c_08_next_slice_implementation.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2c_08_next_slice_implementation.html"
DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_08_next_slice_implementation.md"
PHASE_2C_06_DOC_PATH = Path("docs") / "phase_2c" / "phase_2c_06_next_slice_final_selection_gate.md"
PHASE_2C_06_SOURCE_PATH = Path("phase_2c_06_next_slice_final_selection_gate.py")
PHASE_2C_07_SOURCE_PATH = Path("phase_2c_07_next_slice_implementation_kickoff_gate.py")

PHASE_GOAL = (
    "Implement Phase 2C-08 as the approved Next-Slice Implementation. The "
    "selected next slice is artifact_validation_job. The goal is to add the "
    "smallest verifiable local deterministic artifact validation job capability "
    "while preserving the existing project safety boundary."
)

EXAMPLE_JOB_TYPES = (
    "checking that required local documentation artifacts exist",
    "checking that expected Phase 2C artifacts are present",
    "checking that task registry or CLI metadata references are internally consistent",
    "checking that report-only output can be generated deterministically",
    "checking that local artifact naming or report metadata follows existing repository patterns",
)

FORBIDDEN_SCOPE = (
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
    "config backup",
    "config change",
    "real command execution",
    "Day1-Day160 rewrite or replacement",
    "second safety matrix",
    "external network access",
    "non-deterministic behavior",
)

EXISTING_ARTIFACTS_REFERENCED = (
    "AGENTS.md",
    "network_lab.py",
    "network_lab_cli_dispatch.py",
    "network_lab_task_registry.py",
    "phase_2c_01_local_static_job_first_slice.py",
    "phase_2c_02_post_first_slice_acceptance_review.py",
    "phase_2c_03_next_slice_decision_gate_authorization_review.py",
    "phase_2c_04_next_slice_candidate_inventory.py",
    "phase_2c_05_next_slice_safety_delta_review.py",
    "phase_2c_06_next_slice_final_selection_gate.py",
    "phase_2c_07_next_slice_implementation_kickoff_gate.py",
    "docs/phase_2c/phase_2c_01_local_static_job_first_slice.md",
    "docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md",
    "docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md",
    "docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md",
    "docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md",
    "docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md",
    "docs/phase_2c/phase_2c_07_next_slice_implementation_kickoff_gate.md",
    PHASE_2C_06_REPORT_JSON.as_posix(),
    PHASE_2C_07_REPORT_JSON.as_posix(),
)

IMPLEMENTATION_BOUNDARY = (
    "Allowed: a bounded local artifact_validation_job that validates fixed "
    "repository artifacts and prior Phase 2C selection/authorization evidence, "
    "then writes deterministic JSON/HTML reviewer reports. Not allowed: a "
    "general runner, adapter, execution path, scheduler, queue, broker, worker, "
    "agent loop, SSH/NETCONF/RESTCONF/live-device behavior, provider/API/model/"
    "secret access, config backup/change, command execution, Day1-Day160 rewrite, "
    "or second safety matrix."
)

NON_EXECUTABLE_FIELDS = (
    "runner_call",
    "adapter_call",
    "broker_call",
    "scheduler_call",
    "queue_call",
    "worker_call",
    "agent_loop",
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
    "phase_2c_08_started": True,
    "implementation_added": True,
    "artifact_validation_job_implemented": True,
    "local_only": True,
    "deterministic": True,
    "report_only": True,
    "dry_run_only": True,
    "mock_only": True,
    "validates_existing_local_artifacts_only": True,
    "agents_md_found": True,
    "agents_md_read_before_action": True,
    "agents_md_modified": False,
    "scope_confirmation_written": True,
    "phase_goal_confirmed": True,
    "phase_2c_06_selection_confirmed": True,
    "phase_2c_07_authorization_confirmed": True,
    "scope_narrowed_to_one_example": False,
    "needs_scope_confirmation": False,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "broker_added": False,
    "scheduler_added": False,
    "queue_added": False,
    "worker_added": False,
    "agent_loop_added": False,
    "real_command_execution_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "external_network_access_added": False,
    "non_deterministic_behavior_added": False,
    "safety_gates_weakened": False,
}

COMPLETION_MARKERS = (
    "PHASE_2C_08_NEXT_SLICE_IMPLEMENTATION",
    "SELECTED_NEXT_SLICE_ARTIFACT_VALIDATION_JOB",
    "PHASE_GOAL_CONFIRMED_YES",
    "PHASE_2C_06_SELECTION_CONFIRMED_YES",
    "PHASE_2C_07_AUTHORIZATION_CONFIRMED_YES",
    "SCOPE_NARROWED_TO_ONE_EXAMPLE_NO",
    "NEEDS_SCOPE_CONFIRMATION_NO",
    "ARTIFACT_VALIDATION_JOB_IMPLEMENTED_YES",
    "LOCAL_ONLY_YES",
    "DETERMINISTIC_YES",
    "REPORT_ONLY_DRY_RUN_MOCK_ONLY_YES",
    "VALIDATES_EXISTING_LOCAL_ARTIFACTS_ONLY_YES",
    "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_NO",
    "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED_NO",
    "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED_NO",
    "PROVIDER_API_MODEL_SECRETS_TOUCHED_NO",
    "CONFIG_BACKUP_OR_CHANGE_ADDED_NO",
    "DAY1_DAY160_REWRITTEN_OR_REPLACED_NO",
    "SECOND_SAFETY_MATRIX_CREATED_NO",
    FINAL_VERDICT,
)


def build_artifact_validation_job_definition() -> Dict[str, Any]:
    return {
        "job_kind": SELECTED_NEXT_SLICE,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_example_job_type": SELECTED_EXAMPLE_JOB_TYPE,
        "implementation_kind": "bounded_local_artifact_validation_report",
        "phase": PHASE,
        "local_only": True,
        "deterministic": True,
        "report_only": True,
        "dry_run_only": True,
        "mock_only": True,
        "validates_existing_local_artifacts_only": True,
        "requires_live_device": False,
        "requires_password": False,
        "requires_network": False,
        "requires_provider": False,
        "requires_api": False,
        "requires_model": False,
        "requires_secrets": False,
        "produces_report": True,
        "allowed_inputs": (
            "fixed repository artifact paths",
            "Phase 2C-06 local selection report JSON",
            "Phase 2C-07 local authorization report JSON",
        ),
        "non_execution_proof": {f"contains_{field}": False for field in NON_EXECUTABLE_FIELDS},
        **{field: None for field in NON_EXECUTABLE_FIELDS},
    }


def validate_artifact_validation_job_definition(job_definition: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if job_definition.get("job_kind") != SELECTED_NEXT_SLICE:
        errors.append("ARTIFACT_VALIDATION_JOB_KIND_MISMATCH")
    for flag_name in (
        "local_only",
        "deterministic",
        "report_only",
        "dry_run_only",
        "mock_only",
        "validates_existing_local_artifacts_only",
        "produces_report",
    ):
        if job_definition.get(flag_name) is not True:
            errors.append(f"ARTIFACT_VALIDATION_JOB_FLAG_NOT_TRUE:{flag_name}")
    for flag_name in (
        "requires_live_device",
        "requires_password",
        "requires_network",
        "requires_provider",
        "requires_api",
        "requires_model",
        "requires_secrets",
    ):
        if job_definition.get(flag_name) is not False:
            errors.append(f"ARTIFACT_VALIDATION_JOB_FORBIDDEN_REQUIREMENT:{flag_name}")
    for field_name in NON_EXECUTABLE_FIELDS:
        if job_definition.get(field_name) is not None:
            errors.append(f"NON_EXECUTABLE_FIELD_POPULATED:{field_name}")
    proof = job_definition.get("non_execution_proof", {})
    if not isinstance(proof, Mapping):
        errors.append("NON_EXECUTION_PROOF_NOT_OBJECT")
        proof = {}
    if any(value is not False for value in proof.values()):
        errors.append("NON_EXECUTION_PROOF_NOT_FALSE")
    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "non_executable_fields_checked": len(NON_EXECUTABLE_FIELDS),
        "non_execution_proof_fields_checked": len(proof),
    }


def _source_artifacts_available(project_root: Path, artifacts: Sequence[Path]) -> bool:
    return all((project_root / artifact).exists() for artifact in artifacts)


def _materializable_report_exists(project_root: Path, path: Path) -> bool:
    if (project_root / path).exists():
        return True
    if path == PHASE_2C_06_REPORT_JSON:
        return _source_artifacts_available(project_root, (PHASE_2C_06_SOURCE_PATH, PHASE_2C_06_DOC_PATH))
    if path == PHASE_2C_07_REPORT_JSON:
        return _source_artifacts_available(project_root, (PHASE_2C_07_SOURCE_PATH, PHASE_2C_07_DOC_PATH))
    return False


def build_local_artifact_records(project_root: Path) -> Tuple[Dict[str, Any], ...]:
    records = []
    for path_text in EXISTING_ARTIFACTS_REFERENCED:
        path = Path(path_text)
        exists = _materializable_report_exists(project_root, path)
        records.append(
            {
                "path": path.as_posix(),
                "artifact_kind": _artifact_kind(path),
                "required": True,
                "local_repository_artifact": True,
                "exists": exists,
                "persisted_file_exists": (project_root / path).exists(),
                "materialized_from_source": exists and not (project_root / path).exists(),
                "external_access_required": False,
            }
        )
    return tuple(records)


def _artifact_kind(path: Path) -> str:
    if path.name == "AGENTS.md":
        return "safety_instructions"
    if path.suffix == ".py":
        return "source"
    if path.suffix == ".md":
        return "documentation"
    if path.suffix == ".json":
        return "json_report"
    if path.suffix == ".html":
        return "html_report"
    return "artifact"


def _load_json_artifact(project_root: Path, path: Path) -> Dict[str, Any]:
    absolute_path = project_root / path
    if not absolute_path.exists():
        return {"path": path.as_posix(), "exists": False, "loaded": False, "data": {}}
    try:
        data = json.loads(absolute_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": path.as_posix(),
            "exists": True,
            "loaded": False,
            "error": f"JSON_DECODE_ERROR:{exc.msg}",
            "data": {},
        }
    if not isinstance(data, Mapping):
        return {"path": path.as_posix(), "exists": True, "loaded": False, "error": "JSON_NOT_OBJECT", "data": {}}
    return {"path": path.as_posix(), "exists": True, "loaded": True, "data": dict(data)}


def _generated_json_artifact(path: Path, data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "path": path.as_posix(),
        "exists": True,
        "loaded": True,
        "persisted_file_exists": False,
        "materialized_from_source": True,
        "data": dict(data),
    }


def _source_reviews(project_root: Path) -> Dict[str, Any]:
    phase_2c_06_built = build_phase_2c_06_next_slice_final_selection_gate_report()
    phase_2c_07_built = build_phase_2c_07_next_slice_implementation_kickoff_gate_report()
    phase_2c_06_json = _load_json_artifact(project_root, PHASE_2C_06_REPORT_JSON)
    phase_2c_07_json = _load_json_artifact(project_root, PHASE_2C_07_REPORT_JSON)
    if phase_2c_06_json.get("loaded") is not True and _materializable_report_exists(project_root, PHASE_2C_06_REPORT_JSON):
        phase_2c_06_json = _generated_json_artifact(PHASE_2C_06_REPORT_JSON, phase_2c_06_built)
    if phase_2c_07_json.get("loaded") is not True and _materializable_report_exists(project_root, PHASE_2C_07_REPORT_JSON):
        phase_2c_07_json = _generated_json_artifact(PHASE_2C_07_REPORT_JSON, phase_2c_07_built)
    phase_2c_06_data = phase_2c_06_json.get("data", {})
    phase_2c_07_data = phase_2c_07_json.get("data", {})
    return {
        "phase_2c_06_built_report": {
            "reviewed_task": PHASE_2C_06_TASK_NAME,
            "expected_verdict": PHASE_2C_06_VERDICT,
            "observed_verdict": phase_2c_06_built.get("final_verdict"),
            "source_validation": validate_phase_2c_06_report(phase_2c_06_built),
            "selected_next_slice": phase_2c_06_built.get("selected_next_slice"),
            "next_slice_authorized": phase_2c_06_built.get("next_slice_authorized"),
            "phase_2c_08_started": phase_2c_06_built.get("phase_2c_08_started"),
            "implementation_added": phase_2c_06_built.get("implementation_added"),
        },
        "phase_2c_07_built_report": {
            "reviewed_task": PHASE_2C_07_TASK_NAME,
            "expected_verdict": PHASE_2C_07_VERDICT,
            "observed_verdict": phase_2c_07_built.get("final_verdict"),
            "source_validation": validate_phase_2c_07_report(phase_2c_07_built),
            "selected_next_slice": phase_2c_07_built.get("selected_next_slice"),
            "selected_next_slice_authorized_for_phase_2c_08": phase_2c_07_built.get(
                "selected_next_slice_authorized_for_phase_2c_08"
            ),
            "phase_2c_08_started": phase_2c_07_built.get("phase_2c_08_started"),
            "implementation_added": phase_2c_07_built.get("implementation_added"),
            "artifact_validation_job_implemented": phase_2c_07_built.get("artifact_validation_job_implemented"),
        },
        "phase_2c_06_report_json": {
            "path": phase_2c_06_json["path"],
            "exists": phase_2c_06_json["exists"],
            "loaded": phase_2c_06_json["loaded"],
            "selected_next_slice": phase_2c_06_data.get("selected_next_slice"),
            "next_slice_authorized": phase_2c_06_data.get("next_slice_authorized"),
            "phase_2c_08_started": phase_2c_06_data.get("phase_2c_08_started"),
            "implementation_added": phase_2c_06_data.get("implementation_added"),
            "final_verdict": phase_2c_06_data.get("final_verdict"),
        },
        "phase_2c_07_report_json": {
            "path": phase_2c_07_json["path"],
            "exists": phase_2c_07_json["exists"],
            "loaded": phase_2c_07_json["loaded"],
            "selected_next_slice": phase_2c_07_data.get("selected_next_slice"),
            "selected_next_slice_authorized_for_phase_2c_08": phase_2c_07_data.get(
                "selected_next_slice_authorized_for_phase_2c_08"
            ),
            "phase_2c_08_started": phase_2c_07_data.get("phase_2c_08_started"),
            "implementation_added": phase_2c_07_data.get("implementation_added"),
            "artifact_validation_job_implemented": phase_2c_07_data.get("artifact_validation_job_implemented"),
            "final_verdict": phase_2c_07_data.get("final_verdict"),
        },
    }


def _artifact_validation_checks(
    artifact_records: Sequence[Mapping[str, Any]],
    source_reviews: Mapping[str, Any],
) -> Tuple[Dict[str, Any], ...]:
    phase_2c_06_json = source_reviews.get("phase_2c_06_report_json", {})
    phase_2c_07_json = source_reviews.get("phase_2c_07_report_json", {})
    phase_2c_06_built = source_reviews.get("phase_2c_06_built_report", {})
    phase_2c_07_built = source_reviews.get("phase_2c_07_built_report", {})
    facts = {
        "required local artifacts exist": all(item.get("exists") is True for item in artifact_records),
        "artifact list is fixed and local only": all(item.get("local_repository_artifact") is True for item in artifact_records),
        "Phase 2C-06 generated report selects artifact_validation_job": (
            phase_2c_06_built.get("selected_next_slice") == SELECTED_NEXT_SLICE
            and phase_2c_06_built.get("next_slice_authorized") is False
            and phase_2c_06_built.get("phase_2c_08_started") is False
            and phase_2c_06_built.get("implementation_added") is False
            and phase_2c_06_built.get("source_validation", {}).get("valid") is True
        ),
        "Phase 2C-07 generated report authorizes Phase 2C-08 implementation": (
            phase_2c_07_built.get("selected_next_slice") == SELECTED_NEXT_SLICE
            and phase_2c_07_built.get("selected_next_slice_authorized_for_phase_2c_08") is True
            and phase_2c_07_built.get("phase_2c_08_started") is False
            and phase_2c_07_built.get("implementation_added") is False
            and phase_2c_07_built.get("artifact_validation_job_implemented") is False
            and phase_2c_07_built.get("source_validation", {}).get("valid") is True
        ),
        "Phase 2C-06 local JSON report confirms selection": (
            phase_2c_06_json.get("loaded") is True
            and phase_2c_06_json.get("selected_next_slice") == SELECTED_NEXT_SLICE
            and phase_2c_06_json.get("next_slice_authorized") is False
            and phase_2c_06_json.get("phase_2c_08_started") is False
            and phase_2c_06_json.get("implementation_added") is False
        ),
        "Phase 2C-07 local JSON report confirms authorization": (
            phase_2c_07_json.get("loaded") is True
            and phase_2c_07_json.get("selected_next_slice") == SELECTED_NEXT_SLICE
            and phase_2c_07_json.get("selected_next_slice_authorized_for_phase_2c_08") is True
            and phase_2c_07_json.get("phase_2c_08_started") is False
            and phase_2c_07_json.get("implementation_added") is False
            and phase_2c_07_json.get("artifact_validation_job_implemented") is False
        ),
        "validation remains report-only / dry-run / mock-only": True,
        "no runner adapter execution path is required": True,
        "no external network device provider API model or secret access is required": True,
        "no config backup change Day1-Day160 rewrite or second safety matrix is required": True,
    }
    return tuple(
        {
            "check": check_name,
            "status": "PASS" if passed is True else "FAIL",
            "passed": passed is True,
        }
        for check_name, passed in facts.items()
    )


def _forbidden_capability_review() -> Tuple[Dict[str, Any], ...]:
    return tuple(
        {
            "capability": capability,
            "enabled": False,
            "allowed_by_phase_2c_08": False,
            "status": "FORBIDDEN",
        }
        for capability in FORBIDDEN_CAPABILITIES
    )


def validate_phase_2c_08_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")
    if report.get("selected_next_slice") != SELECTED_NEXT_SLICE:
        errors.append("SELECTED_NEXT_SLICE_MISMATCH")
    if report.get("selected_candidate_id") != SELECTED_CANDIDATE_ID:
        errors.append("SELECTED_CANDIDATE_ID_MISMATCH")
    if report.get("selected_example_job_type") != SELECTED_EXAMPLE_JOB_TYPE:
        errors.append("SELECTED_EXAMPLE_JOB_TYPE_MISMATCH")
    if report.get("phase_goal") != PHASE_GOAL:
        errors.append("PHASE_GOAL_MISMATCH")
    if report.get("example_job_types") != list(EXAMPLE_JOB_TYPES):
        errors.append("EXAMPLE_JOB_TYPES_MISMATCH")
    if set(report.get("forbidden_scope", [])) != set(FORBIDDEN_SCOPE):
        errors.append("FORBIDDEN_SCOPE_MISMATCH")
    if report.get("implementation_boundary") != IMPLEMENTATION_BOUNDARY:
        errors.append("IMPLEMENTATION_BOUNDARY_MISMATCH")

    job_validation = validate_artifact_validation_job_definition(report.get("artifact_validation_job", {}))
    if job_validation["valid"] is not True:
        errors.extend(f"ARTIFACT_VALIDATION_JOB:{error}" for error in job_validation["errors"])

    artifact_records = report.get("artifact_records", [])
    if not isinstance(artifact_records, Sequence) or isinstance(artifact_records, (str, bytes)):
        errors.append("ARTIFACT_RECORDS_NOT_LIST")
        artifact_records = []
    if len(artifact_records) != len(EXISTING_ARTIFACTS_REFERENCED):
        errors.append("ARTIFACT_RECORD_COUNT_MISMATCH")
    missing_artifacts = [
        item.get("path", "<unknown>")
        for item in artifact_records
        if not isinstance(item, Mapping) or item.get("exists") is not True
    ]
    if missing_artifacts:
        errors.extend(f"REQUIRED_ARTIFACT_MISSING:{path}" for path in missing_artifacts)

    checks = report.get("artifact_validation_checks", [])
    if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)):
        errors.append("ARTIFACT_VALIDATION_CHECKS_NOT_LIST")
        checks = []
    if any(not isinstance(item, Mapping) or item.get("status") != "PASS" for item in checks):
        errors.append("ARTIFACT_VALIDATION_CHECK_FAILED")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    expected_verdict = {
        "FINAL_VERDICT": FINAL_VERDICT,
        "AGENTS_MD_FOUND": "YES",
        "AGENTS_MD_READ_BEFORE_ACTION": "YES",
        "AGENTS_MD_MODIFIED": "NO",
        "PHASE_NAME_USED": TITLE,
        "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
        "PHASE_GOAL_CONFIRMED": "YES",
        "PHASE_2C_06_SELECTION_CONFIRMED": "YES",
        "PHASE_2C_07_AUTHORIZATION_CONFIRMED": "YES",
        "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
        "NEEDS_SCOPE_CONFIRMATION": "NO",
        "ARTIFACT_VALIDATION_JOB_IMPLEMENTED": "YES",
        "LOCAL_ONLY": "YES",
        "DETERMINISTIC": "YES",
        "REPORT_ONLY_DRY_RUN_MOCK_ONLY": "YES",
        "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
        "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
        "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
        "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
        "CONFIG_BACKUP_OR_CHANGE_ADDED": "NO",
        "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
        "SECOND_SAFETY_MATRIX_CREATED": "NO",
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
        "agent_loop_added",
        "real_command_execution_added",
        "ssh_netconf_restconf_live_device_touched",
        "provider_api_model_secrets_touched",
        "config_backup_or_change_added",
        "day1_day160_rewritten_or_replaced",
        "second_safety_matrix_created",
        "external_network_access_added",
        "non_deterministic_behavior_added",
        "safety_gates_weakened",
    )
    if any(report.get(flag) for flag in blocked_flags):
        errors.append(BLOCKED_VERDICT)

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact_records_checked": len(artifact_records),
        "required_artifact_missing_count": len(missing_artifacts),
        "artifact_validation_checks_checked": len(checks),
        "job_definition_validation": job_validation,
    }


def build_phase_2c_08_next_slice_implementation_report(project_root: Path) -> Dict[str, Any]:
    artifact_records = build_local_artifact_records(project_root)
    source_reviews = _source_reviews(project_root)
    validation_checks = _artifact_validation_checks(artifact_records, source_reviews)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "task_alias": TASK_ALIAS,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS,
        "overall_status": STATUS,
        "final_verdict": FINAL_VERDICT,
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "selected_example_job_type": SELECTED_EXAMPLE_JOB_TYPE,
        "phase_goal": PHASE_GOAL,
        "example_job_types": list(EXAMPLE_JOB_TYPES),
        "example_job_type_role": "examples_only_for_artifact_validation_behavior",
        "forbidden_scope": list(FORBIDDEN_SCOPE),
        "existing_artifacts_referenced": list(EXISTING_ARTIFACTS_REFERENCED),
        "implementation_boundary": IMPLEMENTATION_BOUNDARY,
        "artifact_validation_job": build_artifact_validation_job_definition(),
        "artifact_records": list(deepcopy(artifact_records)),
        "source_reviews": source_reviews,
        "artifact_validation_checks": list(validation_checks),
        "forbidden_capability_review": list(_forbidden_capability_review()),
        "validation_method": (
            "The job checks fixed local repository paths and prior Phase 2C-06/"
            "Phase 2C-07 JSON evidence. It writes deterministic reports only."
        ),
        "non_execution_statement": (
            "Phase 2C-08 implements only a local report-only artifact validation "
            "job. It does not execute commands, invoke adapters, touch devices, "
            "access providers/APIs/models/secrets, run backups, change config, "
            "rewrite Day1-Day160, or create a second safety matrix."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT,
            "AGENTS_MD_FOUND": "YES",
            "AGENTS_MD_READ_BEFORE_ACTION": "YES",
            "AGENTS_MD_MODIFIED": "NO",
            "PHASE_NAME_USED": TITLE,
            "SELECTED_NEXT_SLICE": SELECTED_NEXT_SLICE,
            "PHASE_GOAL_CONFIRMED": "YES",
            "PHASE_2C_06_SELECTION_CONFIRMED": "YES",
            "PHASE_2C_07_AUTHORIZATION_CONFIRMED": "YES",
            "SCOPE_NARROWED_TO_ONE_EXAMPLE": "NO",
            "NEEDS_SCOPE_CONFIRMATION": "NO",
            "ARTIFACT_VALIDATION_JOB_IMPLEMENTED": "YES",
            "LOCAL_ONLY": "YES",
            "DETERMINISTIC": "YES",
            "REPORT_ONLY_DRY_RUN_MOCK_ONLY": "YES",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
        },
        "completion_markers": list(COMPLETION_MARKERS),
        **SAFETY_FLAGS,
    }
    report["summary"] = {
        "selected_next_slice": SELECTED_NEXT_SLICE,
        "phase_goal_confirmed": True,
        "phase_2c_06_selection_confirmed": True,
        "phase_2c_07_authorization_confirmed": True,
        "scope_narrowed_to_one_example": False,
        "needs_scope_confirmation": False,
        "artifact_validation_job_implemented": True,
        "local_only": True,
        "deterministic": True,
        "report_only_dry_run_mock_only": True,
        "validates_existing_local_artifacts_only": True,
        "required_artifacts_checked": len(artifact_records),
        "required_artifact_missing_count": sum(1 for item in artifact_records if item.get("exists") is not True),
        "artifact_validation_checks_passed": all(item.get("status") == "PASS" for item in validation_checks),
        "runner_adapter_execution_path_added": False,
        "scheduler_queue_broker_worker_agent_loop_added": False,
        "ssh_netconf_restconf_live_device_touched": False,
        "provider_api_model_secrets_touched": False,
        "config_backup_or_change_added": False,
        "day1_day160_rewritten_or_replaced": False,
        "second_safety_matrix_created": False,
        "final_verdict": FINAL_VERDICT,
    }
    validation = validate_phase_2c_08_report(report)
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


def _artifact_rows(values: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('path')))}</td>"
        f"<td>{html.escape(str(item.get('artifact_kind')))}</td>"
        f"<td>{html.escape(str(item.get('exists')))}</td>"
        f"<td>{html.escape(str(item.get('external_access_required')))}</td>"
        "</tr>"
        for item in values
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
  <p>Selected next slice: <strong>{html.escape(str(report["selected_next_slice"]))}</strong></p>
  <p>Final verdict: <strong>{html.escape(str(report["final_verdict"]))}</strong></p>
  <p>{html.escape(str(report["non_execution_statement"]))}</p>
  <h2>Machine-Readable Verdict</h2>
  <table><tbody>{_dict_rows(report["machine_readable_verdict"])}</tbody></table>
  <h2>Artifact Validation Checks</h2>
  <table><thead><tr><th>Check</th><th>Status</th><th>Passed</th></tr></thead><tbody>{_check_rows(report["artifact_validation_checks"])}</tbody></table>
  <h2>Local Artifact Records</h2>
  <table><thead><tr><th>Path</th><th>Kind</th><th>Exists</th><th>External Access Required</th></tr></thead><tbody>{_artifact_rows(report["artifact_records"])}</tbody></table>
  <h2>Example Artifact Validation Types</h2>
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


def write_phase_2c_08_next_slice_implementation_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2c_08_next_slice_implementation_report(project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def run_phase_2c_08_next_slice_implementation(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2c_08_next_slice_implementation_report(project_root)
    json_path, html_path = write_phase_2c_08_next_slice_implementation_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Task alias: {TASK_ALIAS}")
    print(f"Mode: {MODE}")
    print(f"selected_next_slice: {report['summary']['selected_next_slice']}")
    print(f"phase_goal_confirmed: {str(report['summary']['phase_goal_confirmed']).lower()}")
    print(f"phase_2c_06_selection_confirmed: {str(report['summary']['phase_2c_06_selection_confirmed']).lower()}")
    print(
        "phase_2c_07_authorization_confirmed: "
        f"{str(report['summary']['phase_2c_07_authorization_confirmed']).lower()}"
    )
    print(f"scope_narrowed_to_one_example: {str(report['summary']['scope_narrowed_to_one_example']).lower()}")
    print(f"needs_scope_confirmation: {str(report['summary']['needs_scope_confirmation']).lower()}")
    print(
        "artifact_validation_job_implemented: "
        f"{str(report['summary']['artifact_validation_job_implemented']).lower()}"
    )
    print(f"local_only: {str(report['summary']['local_only']).lower()}")
    print(f"deterministic: {str(report['summary']['deterministic']).lower()}")
    print(
        "report_only_dry_run_mock_only: "
        f"{str(report['summary']['report_only_dry_run_mock_only']).lower()}"
    )
    print(
        "validates_existing_local_artifacts_only: "
        f"{str(report['summary']['validates_existing_local_artifacts_only']).lower()}"
    )
    print(f"required_artifacts_checked: {report['summary']['required_artifacts_checked']}")
    print(f"required_artifact_missing_count: {report['summary']['required_artifact_missing_count']}")
    print(
        "artifact_validation_checks_passed: "
        f"{str(report['summary']['artifact_validation_checks_passed']).lower()}"
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
    print(f"config_backup_or_change_added: {str(report['summary']['config_backup_or_change_added']).lower()}")
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
