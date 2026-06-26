"""Phase 2F-10 non-executing local adapter evidence binding.

This module binds already-existing local adapter evidence metadata into a
deterministic review record. It is local-only and evidence-binding-only: it
does not instantiate adapters, call runners, execute commands, read device
state, collect live evidence, use transports, load secrets, call providers,
or perform config backup/change behavior.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Sequence, Tuple


PHASE = "2F-10"
TASK_NAME = "phase2f-10-non-executing-local-adapter-evidence-binding"
TITLE = "Phase 2F-10 Non-Executing Local Adapter Evidence Binding"
MODE = "implementation_local_deterministic_non_executing_evidence_binding_only"
AUTHORIZED_SCOPE = "non_executing_local_adapter_evidence_binding"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
FINAL_VERDICT = "PHASE_2F_10_NON_EXECUTING_LOCAL_ADAPTER_EVIDENCE_BINDING_READY"
DOC_PATH = "docs/phase_2f/phase_2f_10_non_executing_local_adapter_evidence_binding.md"

PHASE_2F_06_CONTRACT_REFERENCE = "non_executing_local_adapter_contract_skeleton"

ALLOWED_SOURCE_KINDS = (
    "local_adapter_evidence_fixture",
    "local_adapter_evidence_metadata",
)

ALLOWED_REVIEWER_STATUSES = (
    "REVIEW_ONLY",
    "EVIDENCE_BOUND",
)

REQUIRED_METADATA_FIELDS = (
    "binding_id",
    "phase",
    "source_kind",
    "adapter_contract_reference",
    "evidence_reference",
    "reviewer_status",
    "safety_boundary",
    "metadata",
)

REQUIRED_EVIDENCE_REFERENCE_FIELDS = (
    "evidence_id",
    "evidence_kind",
    "evidence_status",
)

REQUIRED_SAFETY_BOUNDARY_VALUES = {
    "non_executing": True,
    "local_only": True,
    "deterministic": True,
    "evidence_binding_only": True,
    "report_only": True,
    "dry_run_safe": True,
    "mock_only": True,
    "no_live_network": True,
    "no_command_execution": True,
    "no_ssh_netconf_restconf": True,
    "runner_attached": False,
    "execution_path_attached": False,
    "adapter_instantiated": False,
    "live_device_touched": False,
    "provider_api_model_used": False,
    "secrets_used": False,
    "config_backup_change_added": False,
}

FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "agent_loop",
        "api",
        "api_call",
        "api_client",
        "backup_command",
        "broker",
        "change_command",
        "command",
        "command_allowlist",
        "config_backup",
        "config_change",
        "credential",
        "credential_ref",
        "device",
        "device_command",
        "device_inventory",
        "enable",
        "execute",
        "execution",
        "execution_path",
        "http_client",
        "inventory",
        "live_device",
        "live_evidence",
        "live_target",
        "model",
        "model_client",
        "netconf",
        "provider",
        "queue",
        "reboot",
        "remove",
        "reset",
        "restconf",
        "router",
        "rpc_allowlist",
        "runner",
        "scheduler",
        "secret",
        "secret_ref",
        "ssh",
        "ssh_target",
        "token",
        "transport",
        "worker",
    }
)


@dataclass(frozen=True)
class LocalAdapterEvidenceBinding:
    """Deterministic evidence binding record for local reviewer metadata."""

    binding_name: str
    phase: str
    authorized_scope: str
    binding_id: str
    source_kind: str
    adapter_contract_reference: str
    evidence_id: str
    evidence_kind: str
    evidence_status: str
    reviewer_status: str
    evidence_digest: str
    local_only: bool
    deterministic: bool
    non_executing: bool
    evidence_binding_only: bool
    report_only: bool
    dry_run_safe: bool
    mock_only: bool
    no_live_network: bool
    no_command_execution: bool
    no_ssh_netconf_restconf: bool
    runner_attached: bool
    execution_path_attached: bool
    adapter_instantiated: bool
    live_device_touched: bool
    provider_api_model_used: bool
    secrets_used: bool
    config_backup_change_added: bool
    safety_markers: Tuple[str, ...]


@dataclass(frozen=True)
class LocalAdapterEvidenceBindingValidationResult:
    """Pure local validation result for evidence binding metadata."""

    passed: bool
    status: str
    errors: Tuple[str, ...]
    checks: Tuple[Mapping[str, Any], ...]
    non_executing: bool
    local_only: bool
    deterministic: bool
    evidence_binding_only: bool
    runner_reached: bool
    execution_path_reached: bool
    adapter_instantiated: bool
    external_access_attempted: bool
    secrets_accessed: bool
    live_device_touched: bool


def build_sample_local_adapter_evidence_metadata() -> Dict[str, Any]:
    """Return a deterministic local metadata payload for evidence binding."""

    return {
        "binding_id": "phase-2f-10-local-adapter-evidence-binding",
        "phase": PHASE,
        "source_kind": "local_adapter_evidence_fixture",
        "adapter_contract_reference": PHASE_2F_06_CONTRACT_REFERENCE,
        "evidence_reference": {
            "evidence_id": "phase-2f-06-contract-skeleton-local-metadata",
            "evidence_kind": "local_contract_fixture_metadata",
            "evidence_status": "REVIEW_ONLY",
        },
        "reviewer_status": "EVIDENCE_BOUND",
        "safety_boundary": dict(REQUIRED_SAFETY_BOUNDARY_VALUES),
        "metadata": {
            "review_target": PHASE_2F_06_CONTRACT_REFERENCE,
            "already_existing_local_metadata": True,
            "collects_live_evidence": False,
            "requires_runtime": False,
        },
    }


def bind_local_adapter_evidence(
    metadata: Mapping[str, Any],
) -> LocalAdapterEvidenceBinding:
    """Bind local evidence metadata into a deterministic no-execution record."""

    validation = validate_local_adapter_evidence_metadata(metadata)
    if not validation.passed:
        raise ValueError(";".join(validation.errors))

    evidence_reference = metadata["evidence_reference"]
    return LocalAdapterEvidenceBinding(
        binding_name=AUTHORIZED_SCOPE,
        phase=PHASE,
        authorized_scope=AUTHORIZED_SCOPE,
        binding_id=str(metadata["binding_id"]),
        source_kind=str(metadata["source_kind"]),
        adapter_contract_reference=str(metadata["adapter_contract_reference"]),
        evidence_id=str(evidence_reference["evidence_id"]),
        evidence_kind=str(evidence_reference["evidence_kind"]),
        evidence_status=str(evidence_reference["evidence_status"]),
        reviewer_status=str(metadata["reviewer_status"]),
        evidence_digest=_stable_digest(metadata),
        local_only=True,
        deterministic=True,
        non_executing=True,
        evidence_binding_only=True,
        report_only=True,
        dry_run_safe=True,
        mock_only=True,
        no_live_network=True,
        no_command_execution=True,
        no_ssh_netconf_restconf=True,
        runner_attached=False,
        execution_path_attached=False,
        adapter_instantiated=False,
        live_device_touched=False,
        provider_api_model_used=False,
        secrets_used=False,
        config_backup_change_added=False,
        safety_markers=(
            "NON_EXECUTING",
            "LOCAL_ONLY",
            "EVIDENCE_BINDING_ONLY",
            "NO_LIVE_NETWORK",
            "NO_COMMAND_EXECUTION",
            "NO_SSH_NETCONF_RESTCONF",
            "NO_RUNNER_ATTACHMENT",
            "NO_ADAPTER_INSTANTIATION",
        ),
    )


def validate_local_adapter_evidence_metadata(
    metadata: Mapping[str, Any],
) -> LocalAdapterEvidenceBindingValidationResult:
    """Validate local evidence metadata without invoking execution behavior."""

    errors = []
    checks = []

    if not isinstance(metadata, Mapping):
        return _result(
            errors=("METADATA_NOT_OBJECT",),
            checks=(_check("metadata is mapping", False),),
        )

    missing = [field for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if missing:
        errors.extend(f"REQUIRED_METADATA_FIELD_MISSING:{field}" for field in missing)
    checks.append(_check("required metadata fields present", not missing))

    forbidden_keys = _find_forbidden_keys(metadata)
    if forbidden_keys:
        errors.extend(f"FORBIDDEN_METADATA_KEY:{key}" for key in forbidden_keys)
    checks.append(_check("forbidden live and execution keys absent", not forbidden_keys))

    if metadata.get("phase") != PHASE:
        errors.append("METADATA_PHASE_MISMATCH")
    checks.append(_check("metadata phase marker", metadata.get("phase") == PHASE))

    if metadata.get("source_kind") not in ALLOWED_SOURCE_KINDS:
        errors.append("METADATA_SOURCE_KIND_NOT_LOCAL_EVIDENCE")
    checks.append(
        _check(
            "metadata source kind is local evidence",
            metadata.get("source_kind") in ALLOWED_SOURCE_KINDS,
        )
    )

    if metadata.get("adapter_contract_reference") != PHASE_2F_06_CONTRACT_REFERENCE:
        errors.append("ADAPTER_CONTRACT_REFERENCE_MISMATCH")
    checks.append(
        _check(
            "adapter contract reference is Phase 2F-06 local skeleton",
            metadata.get("adapter_contract_reference") == PHASE_2F_06_CONTRACT_REFERENCE,
        )
    )

    if metadata.get("reviewer_status") not in ALLOWED_REVIEWER_STATUSES:
        errors.append("REVIEWER_STATUS_NOT_REVIEW_ONLY")
    checks.append(
        _check(
            "reviewer status is non-executing",
            metadata.get("reviewer_status") in ALLOWED_REVIEWER_STATUSES,
        )
    )

    evidence_errors = _validate_evidence_reference(metadata.get("evidence_reference"))
    errors.extend(evidence_errors)
    checks.append(_check("evidence reference is local review metadata", not evidence_errors))

    boundary_errors = _validate_safety_boundary(metadata.get("safety_boundary"))
    errors.extend(boundary_errors)
    checks.append(_check("safety boundary is evidence-binding-only", not boundary_errors))

    if not isinstance(metadata.get("metadata"), Mapping):
        errors.append("LOCAL_METADATA_PAYLOAD_NOT_OBJECT")
    checks.append(_check("local metadata payload is object", isinstance(metadata.get("metadata"), Mapping)))

    return _result(errors=tuple(errors), checks=tuple(checks))


def build_phase_2f_10_evidence_binding_summary() -> Dict[str, Any]:
    """Build a deterministic local summary without writing files or running tasks."""

    metadata = build_sample_local_adapter_evidence_metadata()
    binding = bind_local_adapter_evidence(metadata)
    return {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "authorized_scope": AUTHORIZED_SCOPE,
        "final_verdict": FINAL_VERDICT,
        "metadata_validation": asdict(validate_local_adapter_evidence_metadata(metadata)),
        "binding": asdict(binding),
        "non_execution_statement": (
            "Phase 2F-10 binds already-existing local adapter evidence metadata "
            "into a deterministic reviewer record only. It is not wired to a "
            "runner or execution path, does not instantiate adapters, and cannot "
            "contact live devices, providers, APIs, models, secrets, SSH, "
            "NETCONF, RESTCONF, transports, or configuration backup/change "
            "behavior."
        ),
        "forbidden_scope_status": {
            "read_only_lab_adapter_created": False,
            "runner_connected": False,
            "executable_job_registered": False,
            "ssh_added_or_used": False,
            "netconf_added_or_used": False,
            "restconf_added_or_used": False,
            "live_device_touched": False,
            "provider_api_model_added_or_used": False,
            "secrets_used": False,
            "config_backup_or_change_added": False,
            "scheduler_queue_worker_agent_loop_added": False,
            "day1_day160_rewritten": False,
            "second_safety_matrix_created": False,
            "next_phase_started": False,
            "extra_slice_selected_or_implemented": False,
        },
    }


def _validate_evidence_reference(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("EVIDENCE_REFERENCE_NOT_OBJECT",)
    errors = []
    missing = [field for field in REQUIRED_EVIDENCE_REFERENCE_FIELDS if field not in value]
    errors.extend(f"EVIDENCE_REFERENCE_FIELD_MISSING:{field}" for field in missing)
    if value.get("evidence_status") != "REVIEW_ONLY":
        errors.append("EVIDENCE_STATUS_NOT_REVIEW_ONLY")
    if value.get("evidence_kind") not in {
        "local_contract_fixture_metadata",
        "local_adapter_evidence_metadata",
    }:
        errors.append("EVIDENCE_KIND_NOT_LOCAL_METADATA")
    return tuple(errors)


def _validate_safety_boundary(value: Any) -> Tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ("SAFETY_BOUNDARY_NOT_OBJECT",)
    errors = []
    for key, expected in REQUIRED_SAFETY_BOUNDARY_VALUES.items():
        if value.get(key) is not expected:
            errors.append(f"SAFETY_BOUNDARY_VALUE_MISMATCH:{key}")
    unsupported = [key for key in value if key not in REQUIRED_SAFETY_BOUNDARY_VALUES]
    errors.extend(f"SAFETY_BOUNDARY_UNSUPPORTED_FIELD:{key}" for key in unsupported)
    return tuple(errors)


def _stable_digest(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _find_forbidden_keys(value: Any, prefix: str = "$") -> Tuple[str, ...]:
    found = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            normalized = key_text.strip().lower().replace("-", "_").replace(" ", "_")
            path = f"{prefix}.{key_text}"
            if normalized in FORBIDDEN_METADATA_KEYS:
                found.append(path)
            found.extend(_find_forbidden_keys(item, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            found.extend(_find_forbidden_keys(item, f"{prefix}[{index}]"))
    return tuple(found)


def _check(name: str, passed: bool) -> Dict[str, Any]:
    return {"check": name, "status": STATUS_PASS if passed else STATUS_FAIL, "passed": passed}


def _result(
    errors: Sequence[str],
    checks: Sequence[Mapping[str, Any]],
) -> LocalAdapterEvidenceBindingValidationResult:
    return LocalAdapterEvidenceBindingValidationResult(
        passed=not errors,
        status=STATUS_PASS if not errors else STATUS_FAIL,
        errors=tuple(errors),
        checks=tuple(dict(check) for check in checks),
        non_executing=True,
        local_only=True,
        deterministic=True,
        evidence_binding_only=True,
        runner_reached=False,
        execution_path_reached=False,
        adapter_instantiated=False,
        external_access_attempted=False,
        secrets_accessed=False,
        live_device_touched=False,
    )
