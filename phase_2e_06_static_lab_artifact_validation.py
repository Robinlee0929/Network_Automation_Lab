"""Phase 2E-06 static lab artifact validation.

This module validates only caller-provided static lab artifact envelopes. It
does not read devices, execute commands, invoke runners, call adapters, contact
networks, use providers/APIs/models, or load secrets.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


PHASE = "2E-06"
TASK_NAME = "phase2e-06-static-lab-artifact-validation"
TITLE = "Phase 2E-06 Static Lab Artifact Validation Implementation"
MODE = "implementation_slice_local_deterministic_static_artifact_only_report_only_dry_run_mock_only"
SCOPE = "static_lab_artifact_validation"
STATUS = "PASS"
FAIL_STATUS = "FAIL"
FINAL_VERDICT = "PHASE_2E_06_STATIC_LAB_ARTIFACT_VALIDATION_IMPLEMENTED"
DOC_PATH = "docs/phase_2e/phase_2e_06_static_lab_artifact_validation_implementation.md"

REQUIRED_FIELDS = (
    "artifact_id",
    "artifact_type",
    "source_path",
    "static_evidence_kind",
    "collected_state",
    "reviewer_summary",
    "safety_boundary",
    "content",
)

OPTIONAL_FIELDS = (
    "provenance",
    "notes",
)

ALLOWED_ARTIFACT_TYPES = (
    "static_lab_report",
    "mock_lab_export",
    "reviewer_evidence",
)

ALLOWED_STATIC_EVIDENCE_KINDS = (
    "already_collected_local_artifact",
    "committed_mock_fixture",
    "reviewer_documentation",
)

REQUIRED_BOUNDARY_VALUES = {
    "local_only": True,
    "static_only": True,
    "deterministic": True,
    "report_only": True,
    "dry_run_only": True,
    "mock_only": True,
    "requires_live_device": False,
    "requires_network": False,
    "requires_credentials": False,
    "requires_external_api": False,
    "execution_allowed": False,
}

FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "adapter",
        "adapter_call",
        "agent_loop",
        "api",
        "api_call",
        "api_url",
        "backup_command",
        "broker",
        "broker_call",
        "change_command",
        "command",
        "config_backup",
        "config_backup_action",
        "config_change",
        "config_change_action",
        "credential",
        "credential_ref",
        "device_command",
        "execute",
        "execution_engine",
        "execution_path",
        "live_network",
        "live_target",
        "model",
        "model_call",
        "netconf",
        "netconf_target",
        "provider",
        "provider_call",
        "queue",
        "queue_call",
        "restconf",
        "restconf_target",
        "runner",
        "runner_call",
        "scheduler",
        "scheduler_call",
        "secret",
        "secret_ref",
        "shell_command",
        "ssh",
        "ssh_target",
        "token",
        "token_ref",
        "worker",
        "worker_call",
    }
)

SAFETY_FLAGS = {
    "implementation_added": True,
    "static_lab_artifact_validation_implemented": True,
    "local_only": True,
    "deterministic": True,
    "static_artifact_only": True,
    "report_only": True,
    "dry_run_only": True,
    "mock_only": True,
    "runner_added": False,
    "adapter_added": False,
    "execution_path_added": False,
    "scheduler_queue_broker_worker_agent_loop_added": False,
    "ssh_netconf_restconf_live_device_touched": False,
    "provider_api_model_secrets_touched": False,
    "config_backup_or_change_added": False,
    "production_execution_path_added": False,
    "day1_day160_rewritten_or_replaced": False,
    "second_safety_matrix_created": False,
    "next_phase_started": False,
    "extra_slice_selected_or_implemented": False,
}

VALID_STATIC_LAB_ARTIFACT = {
    "artifact_id": "phase-2e-05-authorization-doc",
    "artifact_type": "reviewer_evidence",
    "source_path": "docs/phase_2e/phase_2e_05_static_lab_artifact_validation_kickoff_gate_authorization_gate.md",
    "static_evidence_kind": "reviewer_documentation",
    "collected_state": "already_collected",
    "reviewer_summary": "Phase 2E-05 authorization gate evidence for the static lab artifact validation slice.",
    "safety_boundary": deepcopy(REQUIRED_BOUNDARY_VALUES),
    "content": {
        "status": "PASS",
        "evidence_markers": (
            "AUTHORIZED_FOR_NEXT_IMPLEMENTATION_SLICE: YES",
            "AUTHORIZED_FUTURE_SLICE: `Static lab artifact validation`",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED_OR_MODIFIED: NO",
        ),
    },
    "provenance": {
        "kind": "repository_documentation",
        "refresh_performed": False,
        "external_access_required": False,
    },
}


def build_valid_static_lab_artifact_fixture() -> Dict[str, Any]:
    """Return a deterministic valid static lab artifact envelope."""

    return deepcopy(VALID_STATIC_LAB_ARTIFACT)


def validate_static_lab_artifact(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one static lab artifact envelope without side effects."""

    errors = []
    checks = []

    if not isinstance(artifact, Mapping):
        return _result(
            artifact_id="<not-mapping>",
            errors=("ARTIFACT_NOT_OBJECT",),
            checks=({"check": "artifact is mapping", "status": FAIL_STATUS, "passed": False},),
        )

    artifact_id = str(artifact.get("artifact_id", "<missing>"))

    missing_fields = [field for field in REQUIRED_FIELDS if field not in artifact]
    if missing_fields:
        errors.extend(f"REQUIRED_FIELD_MISSING:{field}" for field in missing_fields)
    checks.append(_check("required fields present", not missing_fields))

    unsupported_fields = [
        field for field in artifact if field not in REQUIRED_FIELDS and field not in OPTIONAL_FIELDS
    ]
    if unsupported_fields:
        errors.extend(f"UNSUPPORTED_FIELD:{field}" for field in unsupported_fields)
    checks.append(_check("unsupported fields absent", not unsupported_fields))

    forbidden_fields = _find_forbidden_fields(artifact)
    if forbidden_fields:
        errors.extend(f"FORBIDDEN_FIELD_PRESENT:{field}" for field in forbidden_fields)
    checks.append(_check("live and execution fields absent", not forbidden_fields))

    if artifact.get("artifact_type") not in ALLOWED_ARTIFACT_TYPES:
        errors.append("UNSUPPORTED_ARTIFACT_TYPE")
    checks.append(_check("artifact type supported", artifact.get("artifact_type") in ALLOWED_ARTIFACT_TYPES))

    if artifact.get("static_evidence_kind") not in ALLOWED_STATIC_EVIDENCE_KINDS:
        errors.append("UNSUPPORTED_STATIC_EVIDENCE_KIND")
    checks.append(
        _check(
            "static evidence kind supported",
            artifact.get("static_evidence_kind") in ALLOWED_STATIC_EVIDENCE_KINDS,
        )
    )

    if artifact.get("collected_state") != "already_collected":
        errors.append("COLLECTED_STATE_NOT_ALREADY_COLLECTED")
    checks.append(_check("artifact is already collected", artifact.get("collected_state") == "already_collected"))

    source_path = artifact.get("source_path")
    local_path = isinstance(source_path, str) and _is_safe_relative_local_path(source_path)
    if not local_path:
        errors.append("SOURCE_PATH_NOT_SAFE_LOCAL_RELATIVE_PATH")
    checks.append(_check("source path is safe local relative path", local_path))

    boundary_errors = _validate_safety_boundary(artifact.get("safety_boundary"))
    errors.extend(boundary_errors)
    checks.append(_check("safety boundary is report-only dry-run mock-only", not boundary_errors))

    content = artifact.get("content")
    if not isinstance(content, Mapping):
        errors.append("CONTENT_NOT_OBJECT")
    checks.append(_check("content is structured object", isinstance(content, Mapping)))

    reviewer_summary = artifact.get("reviewer_summary")
    if not isinstance(reviewer_summary, str) or not reviewer_summary.strip():
        errors.append("REVIEWER_SUMMARY_MISSING")
    checks.append(
        _check(
            "reviewer summary present",
            isinstance(reviewer_summary, str) and bool(reviewer_summary.strip()),
        )
    )

    return _result(artifact_id=artifact_id, errors=tuple(errors), checks=tuple(checks))


def build_phase_2e_06_static_lab_artifact_validation_report(
    artifacts: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a deterministic report-only validation object."""

    artifact_inputs = tuple(artifacts) if artifacts is not None else (build_valid_static_lab_artifact_fixture(),)
    results = [validate_static_lab_artifact(artifact) for artifact in artifact_inputs]
    all_passed = all(result["passed"] is True for result in results)
    report = {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "scope": SCOPE,
        "status": STATUS if all_passed else FAIL_STATUS,
        "final_verdict": FINAL_VERDICT if all_passed else "PHASE_2E_06_STATIC_LAB_ARTIFACT_VALIDATION_FAILED",
        "allowed_artifact_types": list(ALLOWED_ARTIFACT_TYPES),
        "allowed_static_evidence_kinds": list(ALLOWED_STATIC_EVIDENCE_KINDS),
        "required_fields": list(REQUIRED_FIELDS),
        "optional_fields": list(OPTIONAL_FIELDS),
        "forbidden_field_names": sorted(FORBIDDEN_FIELD_NAMES),
        "artifact_validation_results": results,
        "summary": {
            "artifacts_checked": len(results),
            "artifacts_passed": sum(1 for result in results if result["passed"] is True),
            "artifacts_failed": sum(1 for result in results if result["passed"] is not True),
            "report_only_dry_run_mock_only_boundary_visible": True,
            "local_deterministic_static_artifact_only": True,
            "external_system_calls_performed": False,
            "runner_adapter_execution_path_reached": False,
            "final_verdict": FINAL_VERDICT if all_passed else "PHASE_2E_06_STATIC_LAB_ARTIFACT_VALIDATION_FAILED",
        },
        "non_execution_statement": (
            "Phase 2E-06 validates caller-provided static artifact envelopes only. "
            "It does not collect evidence, refresh artifacts, contact devices, invoke "
            "runners or adapters, execute commands, call providers/APIs/models, use "
            "secrets, run backups, or change configuration."
        ),
        "machine_readable_verdict": {
            "FINAL_VERDICT": FINAL_VERDICT if all_passed else "PHASE_2E_06_STATIC_LAB_ARTIFACT_VALIDATION_FAILED",
            "STATIC_LAB_ARTIFACT_VALIDATION_IMPLEMENTED": "YES",
            "LOCAL_ONLY": "YES",
            "DETERMINISTIC": "YES",
            "STATIC_ARTIFACT_ONLY": "YES",
            "REPORT_ONLY_DRY_RUN_MOCK_ONLY": "YES",
            "RUNNER_ADAPTER_EXECUTION_PATH_ADDED": "NO",
            "SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED": "NO",
            "SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED": "NO",
            "PROVIDER_API_MODEL_SECRETS_TOUCHED": "NO",
            "CONFIG_BACKUP_OR_CHANGE_ADDED": "NO",
            "DAY1_DAY160_REWRITTEN_OR_REPLACED": "NO",
            "SECOND_SAFETY_MATRIX_CREATED": "NO",
            "NEXT_PHASE_STARTED": "NO",
            "EXTRA_SLICE_SELECTED_OR_IMPLEMENTED": "NO",
        },
        **SAFETY_FLAGS,
    }
    report["validation"] = validate_phase_2e_06_report(report)
    return report


def validate_phase_2e_06_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    if report.get("phase") != PHASE:
        errors.append("PHASE_MISMATCH")
    if report.get("task") != TASK_NAME:
        errors.append("TASK_NAME_MISMATCH")
    if report.get("mode") != MODE:
        errors.append("MODE_MISMATCH")
    if report.get("scope") != SCOPE:
        errors.append("SCOPE_MISMATCH")

    results = report.get("artifact_validation_results", [])
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        errors.append("ARTIFACT_VALIDATION_RESULTS_NOT_LIST")
        results = []
    if any(not isinstance(result, Mapping) or result.get("status") != STATUS for result in results):
        errors.append("ARTIFACT_VALIDATION_RESULT_FAILED")

    summary = report.get("summary", {})
    if not isinstance(summary, Mapping):
        errors.append("SUMMARY_NOT_OBJECT")
        summary = {}
    if summary.get("report_only_dry_run_mock_only_boundary_visible") is not True:
        errors.append("REPORT_ONLY_DRY_RUN_MOCK_ONLY_BOUNDARY_NOT_VISIBLE")
    if summary.get("external_system_calls_performed") is not False:
        errors.append("EXTERNAL_SYSTEM_CALLS_PERFORMED")
    if summary.get("runner_adapter_execution_path_reached") is not False:
        errors.append("RUNNER_ADAPTER_EXECUTION_PATH_REACHED")

    for flag_name, expected in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected:
            errors.append(f"SAFETY_FLAG_MISMATCH:{flag_name}")

    if any(report.get(flag_name) for flag_name, expected in SAFETY_FLAGS.items() if expected is False):
        errors.append("FORBIDDEN_SCOPE_TOUCHED")

    return {
        "valid": not errors,
        "status": STATUS if not errors else FAIL_STATUS,
        "errors": errors,
        "artifact_validation_results_checked": len(results),
    }


def _validate_safety_boundary(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("SAFETY_BOUNDARY_NOT_OBJECT",)
    errors = []
    for field, expected in REQUIRED_BOUNDARY_VALUES.items():
        if value.get(field) is not expected:
            errors.append(f"SAFETY_BOUNDARY_VALUE_MISMATCH:{field}")
    unsupported = [field for field in value if field not in REQUIRED_BOUNDARY_VALUES]
    errors.extend(f"SAFETY_BOUNDARY_UNSUPPORTED_FIELD:{field}" for field in unsupported)
    return tuple(errors)


def _find_forbidden_fields(value: Any, prefix: str = "$") -> Tuple[str, ...]:
    found = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower().replace("-", "_").replace(" ", "_")
            path = f"{prefix}.{key_text}"
            if normalized_key in FORBIDDEN_FIELD_NAMES:
                found.append(path)
            found.extend(_find_forbidden_fields(item, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            found.extend(_find_forbidden_fields(item, f"{prefix}[{index}]"))
    return tuple(found)


def _is_safe_relative_local_path(path_text: str) -> bool:
    normalized = path_text.replace("\\", "/")
    if not normalized.strip():
        return False
    if "://" in normalized or normalized.startswith("/") or normalized.startswith("~"):
        return False
    if PureWindowsPath(path_text).is_absolute() or PurePosixPath(normalized).is_absolute():
        return False
    parts = PurePosixPath(normalized).parts
    return ".." not in parts


def _check(name: str, passed: bool) -> Dict[str, Any]:
    return {"check": name, "status": STATUS if passed else FAIL_STATUS, "passed": passed}


def _result(
    artifact_id: str,
    errors: Sequence[str],
    checks: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    passed = not errors
    return {
        "artifact_id": artifact_id,
        "passed": passed,
        "status": STATUS if passed else FAIL_STATUS,
        "errors": list(errors),
        "checks": [dict(check) for check in checks],
        "report_only": True,
        "dry_run_only": True,
        "mock_only": True,
        "external_access_attempted": False,
        "runner_invoked": False,
        "adapter_invoked": False,
        "execution_path_reached": False,
    }
