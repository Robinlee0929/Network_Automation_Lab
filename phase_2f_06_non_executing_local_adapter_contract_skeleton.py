"""Phase 2F-06 non-executing local adapter contract skeleton.

This module defines local contract-only data shapes and validation helpers for
the first Phase 2F adapter slice. It does not contact devices, use transports,
load secrets, invoke runners, register CLI tasks, call providers/APIs/models,
perform config backup/change behavior, or open any execution path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Sequence, Tuple


PHASE = "2F-06"
TASK_NAME = "phase2f-06-non-executing-local-adapter-contract-skeleton"
TITLE = "Phase 2F-06 Non-Executing Local Adapter Contract Skeleton"
MODE = "implementation_local_deterministic_non_executing_contract_only"
AUTHORIZED_SCOPE = "non_executing_local_adapter_contract_skeleton"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
FINAL_VERDICT = "PHASE_2F_06_NON_EXECUTING_LOCAL_ADAPTER_CONTRACT_SKELETON_READY"
DOC_PATH = "docs/phase_2f/phase_2f_06_non_executing_local_adapter_contract_skeleton.md"

ALLOWED_REQUESTED_CAPABILITIES = (
    "contract_metadata_review",
    "contract_shape_validation",
)

REQUIRED_REQUEST_FIELDS = (
    "request_id",
    "contract_name",
    "phase",
    "requested_capability",
    "source_kind",
    "safety_boundary",
    "payload",
)

REQUIRED_SAFETY_BOUNDARY_VALUES = {
    "non_executing": True,
    "local_only": True,
    "deterministic": True,
    "contract_only": True,
    "report_only": True,
    "dry_run_safe": True,
    "mock_only": True,
    "supports_execution": False,
    "wired_to_runner": False,
    "wired_to_execution_path": False,
    "connected_to_live_device": False,
    "connected_to_provider_api_model_secrets": False,
    "capable_of_config_backup_change": False,
}

FORBIDDEN_REQUEST_KEYS = frozenset(
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
class AdapterCapabilityDeclaration:
    """Static capability declaration for contract review only."""

    name: str
    description: str
    local_only: bool
    deterministic: bool
    contract_only: bool
    supports_execution: bool
    supports_live_device: bool
    supports_provider_api_model: bool
    supports_secrets: bool
    supports_config_backup: bool
    supports_config_change: bool


@dataclass(frozen=True)
class LocalAdapterContract:
    """Static local contract metadata with explicit non-execution markers."""

    contract_name: str
    phase: str
    authorized_scope: str
    status: str
    local_only: bool
    deterministic: bool
    non_executing: bool
    contract_only: bool
    report_only: bool
    dry_run_safe: bool
    mock_only: bool
    wired_to_runner: bool
    wired_to_execution_path: bool
    connected_to_live_device: bool
    connected_to_provider_api_model_secrets: bool
    capable_of_config_backup_change: bool
    capabilities: Tuple[AdapterCapabilityDeclaration, ...]


@dataclass(frozen=True)
class AdapterContractValidationResult:
    """Deterministic local validation result for contract-only checks."""

    passed: bool
    status: str
    errors: Tuple[str, ...]
    checks: Tuple[Mapping[str, Any], ...]
    non_executing: bool
    local_only: bool
    deterministic: bool
    runner_reached: bool
    execution_path_reached: bool
    external_access_attempted: bool
    secrets_accessed: bool


def build_local_adapter_contract() -> LocalAdapterContract:
    """Return the static Phase 2F-06 local adapter contract skeleton."""

    capabilities = tuple(
        AdapterCapabilityDeclaration(
            name=name,
            description="Local contract-only review capability; no adapter invocation is possible.",
            local_only=True,
            deterministic=True,
            contract_only=True,
            supports_execution=False,
            supports_live_device=False,
            supports_provider_api_model=False,
            supports_secrets=False,
            supports_config_backup=False,
            supports_config_change=False,
        )
        for name in ALLOWED_REQUESTED_CAPABILITIES
    )
    return LocalAdapterContract(
        contract_name=AUTHORIZED_SCOPE,
        phase=PHASE,
        authorized_scope=AUTHORIZED_SCOPE,
        status="READY_CONTRACT_ONLY",
        local_only=True,
        deterministic=True,
        non_executing=True,
        contract_only=True,
        report_only=True,
        dry_run_safe=True,
        mock_only=True,
        wired_to_runner=False,
        wired_to_execution_path=False,
        connected_to_live_device=False,
        connected_to_provider_api_model_secrets=False,
        capable_of_config_backup_change=False,
        capabilities=capabilities,
    )


def build_sample_adapter_contract_request() -> Dict[str, Any]:
    """Return a deterministic request shape for local contract validation."""

    return {
        "request_id": "phase-2f-06-static-contract-request",
        "contract_name": AUTHORIZED_SCOPE,
        "phase": PHASE,
        "requested_capability": "contract_shape_validation",
        "source_kind": "static_contract_fixture",
        "safety_boundary": dict(REQUIRED_SAFETY_BOUNDARY_VALUES),
        "payload": {
            "review_target": "local_contract_shape_only",
            "no_runtime_input": True,
        },
    }


def build_phase_2f_06_contract_summary() -> Dict[str, Any]:
    """Build a deterministic local summary without writing files or running tasks."""

    contract = build_local_adapter_contract()
    request = build_sample_adapter_contract_request()
    return {
        "phase": PHASE,
        "task": TASK_NAME,
        "title": TITLE,
        "mode": MODE,
        "authorized_scope": AUTHORIZED_SCOPE,
        "final_verdict": FINAL_VERDICT,
        "contract": _contract_to_dict(contract),
        "sample_request": request,
        "contract_validation": asdict(validate_local_adapter_contract(contract)),
        "request_validation": asdict(validate_adapter_contract_request(request)),
        "non_execution_statement": (
            "Phase 2F-06 defines local adapter contract metadata, capability "
            "declarations, and request validation only. It is not wired to a "
            "runner or execution path and cannot contact live devices, "
            "providers, APIs, models, secrets, transports, or configuration "
            "backup/change behavior."
        ),
        "forbidden_scope_status": {
            "runner_integration_touched": False,
            "adapter_execution_wiring_touched": False,
            "scheduler_queue_worker_agent_loop_touched": False,
            "live_device_touched": False,
            "ssh_netconf_restconf_touched": False,
            "provider_api_model_secrets_touched": False,
            "config_backup_change_touched": False,
            "production_execution_path_touched": False,
            "day1_day160_rewritten_or_replaced": False,
            "second_safety_matrix_created": False,
            "next_phase_started": False,
            "extra_slice_selected_or_implemented": False,
        },
    }


def validate_local_adapter_contract(
    contract: LocalAdapterContract,
) -> AdapterContractValidationResult:
    """Validate static contract metadata without side effects."""

    errors = []
    checks = []

    expected_flags = {
        "local_only": True,
        "deterministic": True,
        "non_executing": True,
        "contract_only": True,
        "report_only": True,
        "dry_run_safe": True,
        "mock_only": True,
        "wired_to_runner": False,
        "wired_to_execution_path": False,
        "connected_to_live_device": False,
        "connected_to_provider_api_model_secrets": False,
        "capable_of_config_backup_change": False,
    }

    if contract.contract_name != AUTHORIZED_SCOPE:
        errors.append("CONTRACT_NAME_MISMATCH")
    checks.append(_check("authorized scope name", contract.contract_name == AUTHORIZED_SCOPE))

    if contract.phase != PHASE:
        errors.append("PHASE_MISMATCH")
    checks.append(_check("phase marker", contract.phase == PHASE))

    for flag_name, expected in expected_flags.items():
        if getattr(contract, flag_name) is not expected:
            errors.append(f"CONTRACT_FLAG_MISMATCH:{flag_name}")
    checks.append(
        _check(
            "non-executing contract flags",
            all(getattr(contract, flag_name) is expected for flag_name, expected in expected_flags.items()),
        )
    )

    capability_errors = _validate_capability_declarations(contract.capabilities)
    errors.extend(capability_errors)
    checks.append(_check("capabilities are contract-only", not capability_errors))

    return _result(errors=tuple(errors), checks=tuple(checks))


def validate_adapter_contract_request(
    request: Mapping[str, Any],
) -> AdapterContractValidationResult:
    """Validate a local request shape without invoking any adapter behavior."""

    errors = []
    checks = []

    if not isinstance(request, Mapping):
        return _result(
            errors=("REQUEST_NOT_OBJECT",),
            checks=(_check("request is mapping", False),),
        )

    missing = [field for field in REQUIRED_REQUEST_FIELDS if field not in request]
    if missing:
        errors.extend(f"REQUIRED_REQUEST_FIELD_MISSING:{field}" for field in missing)
    checks.append(_check("required request fields present", not missing))

    forbidden_keys = _find_forbidden_keys(request)
    if forbidden_keys:
        errors.extend(f"FORBIDDEN_REQUEST_KEY:{key}" for key in forbidden_keys)
    checks.append(_check("forbidden live and execution keys absent", not forbidden_keys))

    if request.get("contract_name") != AUTHORIZED_SCOPE:
        errors.append("REQUEST_CONTRACT_NAME_MISMATCH")
    checks.append(_check("request contract name", request.get("contract_name") == AUTHORIZED_SCOPE))

    if request.get("phase") != PHASE:
        errors.append("REQUEST_PHASE_MISMATCH")
    checks.append(_check("request phase marker", request.get("phase") == PHASE))

    if request.get("requested_capability") not in ALLOWED_REQUESTED_CAPABILITIES:
        errors.append("REQUESTED_CAPABILITY_NOT_CONTRACT_ONLY")
    checks.append(
        _check(
            "requested capability is contract-only",
            request.get("requested_capability") in ALLOWED_REQUESTED_CAPABILITIES,
        )
    )

    if request.get("source_kind") != "static_contract_fixture":
        errors.append("REQUEST_SOURCE_KIND_NOT_STATIC_CONTRACT_FIXTURE")
    checks.append(
        _check(
            "request source kind is static fixture",
            request.get("source_kind") == "static_contract_fixture",
        )
    )

    boundary_errors = _validate_safety_boundary(request.get("safety_boundary"))
    errors.extend(boundary_errors)
    checks.append(_check("request safety boundary is non-executing", not boundary_errors))

    if not isinstance(request.get("payload"), Mapping):
        errors.append("REQUEST_PAYLOAD_NOT_OBJECT")
    checks.append(_check("request payload is local object", isinstance(request.get("payload"), Mapping)))

    return _result(errors=tuple(errors), checks=tuple(checks))


def _validate_capability_declarations(
    capabilities: Sequence[AdapterCapabilityDeclaration],
) -> Tuple[str, ...]:
    errors = []
    if not capabilities:
        return ("CAPABILITIES_MISSING",)
    observed_names = tuple(capability.name for capability in capabilities)
    if observed_names != ALLOWED_REQUESTED_CAPABILITIES:
        errors.append("CAPABILITY_NAMES_MISMATCH")
    for capability in capabilities:
        if capability.local_only is not True:
            errors.append(f"CAPABILITY_NOT_LOCAL_ONLY:{capability.name}")
        if capability.deterministic is not True:
            errors.append(f"CAPABILITY_NOT_DETERMINISTIC:{capability.name}")
        if capability.contract_only is not True:
            errors.append(f"CAPABILITY_NOT_CONTRACT_ONLY:{capability.name}")
        for field in (
            "supports_execution",
            "supports_live_device",
            "supports_provider_api_model",
            "supports_secrets",
            "supports_config_backup",
            "supports_config_change",
        ):
            if getattr(capability, field) is not False:
                errors.append(f"CAPABILITY_FORBIDDEN_FLAG_ENABLED:{capability.name}:{field}")
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


def _find_forbidden_keys(value: Any, prefix: str = "$") -> Tuple[str, ...]:
    found = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            normalized = key_text.strip().lower().replace("-", "_").replace(" ", "_")
            path = f"{prefix}.{key_text}"
            if normalized in FORBIDDEN_REQUEST_KEYS:
                found.append(path)
            found.extend(_find_forbidden_keys(item, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            found.extend(_find_forbidden_keys(item, f"{prefix}[{index}]"))
    return tuple(found)


def _contract_to_dict(contract: LocalAdapterContract) -> Dict[str, Any]:
    data = asdict(contract)
    data["capabilities"] = [asdict(capability) for capability in contract.capabilities]
    return data


def _check(name: str, passed: bool) -> Dict[str, Any]:
    return {"check": name, "status": STATUS_PASS if passed else STATUS_FAIL, "passed": passed}


def _result(
    errors: Sequence[str],
    checks: Sequence[Mapping[str, Any]],
) -> AdapterContractValidationResult:
    return AdapterContractValidationResult(
        passed=not errors,
        status=STATUS_PASS if not errors else STATUS_FAIL,
        errors=tuple(errors),
        checks=tuple(dict(check) for check in checks),
        non_executing=True,
        local_only=True,
        deterministic=True,
        runner_reached=False,
        execution_path_reached=False,
        external_access_attempted=False,
        secrets_accessed=False,
    )
