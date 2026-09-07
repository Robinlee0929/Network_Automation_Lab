"""Immutable offline command policy for one future Stage-2 VRRP observation.

The public resolver accepts only the exact S2-RO-01 request type and returns
one fixed, non-authorizing command specification. It performs no I/O and has
no transport, credential, parser, runtime, or command-execution capability.
"""

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpObservationRequest as _Stage2VrrpObservationRequest,
    VRRP_COMMAND_POLICY_VERSION as _SOURCE_POLICY_VERSION,
    VRRP_OBSERVATION_OPERATION_ID as _SOURCE_OPERATION_ID,
)


_SCHEMA_VERSION = "s2-ro-08.command-policy.v1"
_OPERATION_ID = "mikrotik.vrrp_status"
_COMMAND_POLICY_VERSION = "policy.stage2.vrrp-readonly.v1"
_COMMAND_TEXT = "/interface/vrrp/print"
_POLICY_BINDINGS = (
    (_OPERATION_ID, _COMMAND_POLICY_VERSION, _COMMAND_TEXT),
)


class Stage2VrrpCommandPolicyFailure(_Enum):
    """Bounded failures that never retain rejected request or policy data."""

    INVALID_REQUEST = "INVALID_REQUEST"
    UNKNOWN_REQUEST = "UNKNOWN_REQUEST"
    INVALID_POLICY = "INVALID_POLICY"


class Stage2VrrpCommandPolicyError(ValueError):
    """Sanitized failure for S2-RO-08 request or policy rejection."""

    def __init__(self, code: Stage2VrrpCommandPolicyFailure) -> None:
        if type(code) is not Stage2VrrpCommandPolicyFailure:
            raise TypeError("command policy error requires a bounded category")
        self.code = code
        super().__init__(code.value)


def _fail(code: Stage2VrrpCommandPolicyFailure) -> None:
    raise Stage2VrrpCommandPolicyError(code) from None


def _validated_request(request: object) -> None:
    if type(request) is not _Stage2VrrpObservationRequest:
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_REQUEST)

    failed = False
    try:
        values = (
            request.schema_version,
            request.operation_id,
            request.run_id,
            request.target_ref,
            request.credential_ref,
            request.authorization_ref,
            request.read_only,
        )
    except Exception:
        failed = True
        values = ()
    if failed or len(values) != 7:
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_REQUEST)

    string_values = values[:-1]
    if any(type(value) is not str for value in string_values):
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_REQUEST)
    if request.operation_id != _OPERATION_ID:
        _fail(Stage2VrrpCommandPolicyFailure.UNKNOWN_REQUEST)
    if type(request.read_only) is not bool or request.read_only is not True:
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_REQUEST)

    try:
        _Stage2VrrpObservationRequest.__post_init__(request)
    except Exception:
        failed = True
    if failed:
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_REQUEST)


def _validated_policy() -> tuple[str, str, str]:
    expected = ((_OPERATION_ID, _COMMAND_POLICY_VERSION, _COMMAND_TEXT),)
    if (
        type(_SOURCE_OPERATION_ID) is not str
        or _SOURCE_OPERATION_ID != _OPERATION_ID
        or type(_SOURCE_POLICY_VERSION) is not str
        or _SOURCE_POLICY_VERSION != _COMMAND_POLICY_VERSION
        or type(_POLICY_BINDINGS) is not tuple
        or _POLICY_BINDINGS != expected
        or any(type(binding) is not tuple for binding in _POLICY_BINDINGS)
        or any(type(value) is not str for binding in _POLICY_BINDINGS for value in binding)
    ):
        _fail(Stage2VrrpCommandPolicyFailure.INVALID_POLICY)
    return _POLICY_BINDINGS[0]


@_dataclass(frozen=True, slots=True, init=False, repr=False)
class Stage2VrrpReadOnlyCommandSpecification:
    """One resolver-issued command description without execution authority."""

    schema_version: str
    operation_id: str
    command_policy_version: str
    command_text: str
    read_only: bool
    execution_authorized: bool

    def __new__(cls, *args, **kwargs):
        raise TypeError("command specifications are resolver-issued only")

    def __init__(self, *args, **kwargs):
        raise TypeError("command specifications are resolver-issued only")

    def __init_subclass__(cls, **kwargs):
        raise TypeError("command specifications cannot be subclassed")

    def __copy__(self):
        raise TypeError("command specifications cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("command specifications cannot be copied")

    def __getstate__(self):
        raise TypeError("command specifications cannot be reconstructed")

    def __setstate__(self, state):
        raise TypeError("command specifications cannot be reconstructed")

    def __reduce__(self):
        raise TypeError("command specifications cannot be reconstructed")

    def __reduce_ex__(self, protocol):
        raise TypeError("command specifications cannot be reconstructed")

    def __repr__(self) -> str:
        return "Stage2VrrpReadOnlyCommandSpecification(<offline-policy-only>)"

    __str__ = __repr__


def resolve_stage2_vrrp_readonly_command(
    request: _Stage2VrrpObservationRequest,
) -> Stage2VrrpReadOnlyCommandSpecification:
    """Resolve one exact S2-RO-01 request without I/O, fallback, or execution."""

    _validated_request(request)
    operation_id, policy_version, command_text = _validated_policy()
    result = object.__new__(Stage2VrrpReadOnlyCommandSpecification)
    for name, value in (
        ("schema_version", _SCHEMA_VERSION),
        ("operation_id", operation_id),
        ("command_policy_version", policy_version),
        ("command_text", command_text),
        ("read_only", True),
        ("execution_authorized", False),
    ):
        object.__setattr__(result, name, value)
    return result


__all__ = (
    "Stage2VrrpCommandPolicyError",
    "Stage2VrrpCommandPolicyFailure",
    "Stage2VrrpReadOnlyCommandSpecification",
    "resolve_stage2_vrrp_readonly_command",
)
