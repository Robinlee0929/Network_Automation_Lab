"""DL-01 inert Dual-Lab VRRP contracts; validity never authorizes execution.

The minimal query carries schema, caller-supplied query identity, fixed operation,
and fixed order. Its target scope is always Lab1 and Lab2. The aggregate adds
exactly those two tagged results. No runtime bundles or authority are accepted.

The five Dual-Lab failure identifiers were specified by the Owner clarification;
the other six preserve S2-RO-11 spellings without importing its live entrypoint.
"""

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
from functools import wraps as _wraps
import json as _json
import re as _re

from validation_framework import stage2_vrrp_readonly_contract as _stage2


_SCHEMA = "dual-lab-vrrp-query.v1"
_OPERATION = _stage2.VRRP_OBSERVATION_OPERATION_ID
_ORDER = "LAB1_THEN_LAB2"
_LAB1 = "target.mikrotik.lab01"
_LAB2 = "target.mikrotik.lab02"
_QUERY_FIELDS = frozenset({"schema_version", "query_id", "operation_id", "execution_order"})
_AGGREGATE_FIELDS = _QUERY_FIELDS | {"lab1", "lab2"}
_SUCCESS_FIELDS = frozenset({"status", "target_ref", "evidence"})
_FAILURE_FIELDS = frozenset({"status", "target_ref", "failure_category"})
# Same bounded lowercase dotted logical-reference grammar as S2-RO-01.
_QUERY_ID = _re.compile(r"query\.[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*")
_MAX_QUERY_BYTES = _stage2.MAX_REQUEST_CANONICAL_BYTES
_MAX_RESULT_BYTES = _stage2.MAX_EVIDENCE_CANONICAL_BYTES + 1_024
_MAX_AGGREGATE_BYTES = 2 * _MAX_RESULT_BYTES + _MAX_QUERY_BYTES


class FailureCategory(_Enum):
    """Exact Owner-approved target failure vocabulary; no exception details.

    PREFLIGHT_TARGET_BUNDLE_INVALID covers non-authorization bundle structure
    and fixed-target bindings, excluding a missing persistent startup binding.
    PREFLIGHT_AUTHORIZATION_INVALID covers unusable authorization before entry.
    PREFLIGHT_AUTHORIZATION_NOT_DISTINCT covers shared/colliding authorization
    references or IDs; neither target may rely on the duplicated identity.
    PREFLIGHT_STARTUP_BINDING_UNAVAILABLE covers unavailable accepted startup
    reconstruction, never discovery or substitution of another configuration.
    CANONICAL_EVIDENCE_VALIDATION_FAILED covers rejected candidate evidence.
    These are data labels only: this module performs none of those operations.
    """

    PREFLIGHT_TARGET_BUNDLE_INVALID = "PREFLIGHT_TARGET_BUNDLE_INVALID"
    PREFLIGHT_AUTHORIZATION_INVALID = "PREFLIGHT_AUTHORIZATION_INVALID"
    PREFLIGHT_AUTHORIZATION_NOT_DISTINCT = "PREFLIGHT_AUTHORIZATION_NOT_DISTINCT"
    PREFLIGHT_STARTUP_BINDING_UNAVAILABLE = "PREFLIGHT_STARTUP_BINDING_UNAVAILABLE"
    CANONICAL_EVIDENCE_VALIDATION_FAILED = "CANONICAL_EVIDENCE_VALIDATION_FAILED"
    INVALID_REQUEST_INPUT = "INVALID_REQUEST_INPUT"
    INVALID_AUTHORIZATION_INPUT = "INVALID_AUTHORIZATION_INPUT"
    INVALID_TRUSTED_CONFIGURATION = "INVALID_TRUSTED_CONFIGURATION"
    TRUSTED_RUNTIME_FAILED = "TRUSTED_RUNTIME_FAILED"
    OUTPUT_RENDER_FAILED = "OUTPUT_RENDER_FAILED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"


class DualLabContractError(ValueError):
    """Rejected contract input, never a TargetResult or an aggregate."""

    def __init__(self):
        super().__init__("invalid Dual-Lab contract")


def _reject():
    try:
        raise DualLabContractError() from None
    except DualLabContractError as error:
        error.__context__ = None
        raise


def _checked(function):
    """Discard child errors before raising the fixed public rejection."""
    @_wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            pass
        args = kwargs = None
        _reject()
    return checked


def _exact(value, expected):
    if type(value) is not str or value != expected:
        _reject()


def _identity(value):
    _exact(value.schema_version, _SCHEMA)
    _exact(value.operation_id, _OPERATION)
    _exact(value.execution_order, _ORDER)
    if (type(value.query_id) is not str
            or not 1 <= len(value.query_id) <= _stage2.MAX_REFERENCE_LENGTH
            or _QUERY_ID.fullmatch(value.query_id) is None):
        _reject()
    return {name: getattr(value, name) for name in _QUERY_FIELDS}


def _target(value):
    if type(value) is not str or value not in (_LAB1, _LAB2):
        _reject()


def _evidence(value, target_ref):
    if type(value) is not _stage2.Stage2VrrpObservationEvidence:
        _reject()
    # Revalidate even exact-type objects altered after construction. Reparse
    # also detaches mutable source data without defining a second evidence schema.
    parsed = _stage2.parse_stage2_vrrp_evidence_canonical_json(value.to_canonical_bytes())
    if parsed.target_ref != target_ref:
        _reject()
    return parsed


class _Canonical:
    __slots__ = ()

    def __repr__(self):
        return f"{type(self).__name__}(<inert-contract>)"

    __str__ = __repr__

    @property
    def execution_authorized(self):
        return False

    @_checked
    def to_canonical_bytes(self):
        if type(self) is DualLabVrrpQuery:
            maximum, parser = _MAX_QUERY_BYTES, parse_query_canonical_json
        elif type(self) is DualLabVrrpAggregate:
            maximum, parser = _MAX_AGGREGATE_BYTES, parse_aggregate_canonical_json
        elif type(self) in (TargetSuccess, TargetFailure):
            maximum, parser = _MAX_RESULT_BYTES, parse_target_result_canonical_json
        else:
            _reject()
        encoded = _encode(self.to_dict(), maximum)
        parser(encoded)
        return encoded


@_dataclass(frozen=True, slots=True, repr=False)
class DualLabVrrpQuery(_Canonical):
    """Logical query for the fixed pair, with no invocation or authority data."""

    schema_version: str
    query_id: str
    operation_id: str
    execution_order: str

    @_checked
    def __post_init__(self):
        _identity(self)

    @_checked
    def to_dict(self):
        return _identity(self)


@_dataclass(frozen=True, slots=True, repr=False)
class TargetSuccess(_Canonical):
    """Exactly one fixed target's canonical S2-RO-01 evidence."""

    status: str
    target_ref: str
    evidence: _stage2.Stage2VrrpObservationEvidence

    @_checked
    def __post_init__(self):
        _exact(self.status, "SUCCESS")
        _target(self.target_ref)
        object.__setattr__(self, "evidence", _evidence(self.evidence, self.target_ref))

    @_checked
    def to_dict(self):
        _exact(self.status, "SUCCESS")
        _target(self.target_ref)
        return {"status": self.status, "target_ref": self.target_ref,
                "evidence": _evidence(self.evidence, self.target_ref).to_dict()}


@_dataclass(frozen=True, slots=True, repr=False)
class TargetFailure(_Canonical):
    """A bounded target outcome only, never a top-level validation error."""

    status: str
    target_ref: str
    failure_category: FailureCategory

    @_checked
    def __post_init__(self):
        _exact(self.status, "FAILURE")
        _target(self.target_ref)
        if type(self.failure_category) is not FailureCategory:
            _reject()

    @_checked
    def to_dict(self):
        self.__post_init__()
        return {"status": self.status, "target_ref": self.target_ref,
                "failure_category": self.failure_category.value}


TargetResult = TargetSuccess | TargetFailure


@_dataclass(frozen=True, slots=True, repr=False)
class DualLabVrrpAggregate(_Canonical):
    """Two independent observations; order metadata is not an execution path."""

    schema_version: str
    query_id: str
    operation_id: str
    execution_order: str
    lab1: TargetResult
    lab2: TargetResult

    @_checked
    def __post_init__(self):
        _identity(self)
        _result_dict(self.lab1, _LAB1)
        _result_dict(self.lab2, _LAB2)

    @_checked
    def to_dict(self):
        return {**_identity(self), "lab1": _result_dict(self.lab1, _LAB1),
                "lab2": _result_dict(self.lab2, _LAB2)}


def _result_dict(value, target_ref):
    if type(value) not in (TargetSuccess, TargetFailure):
        _reject()
    _exact(value.target_ref, target_ref)
    return value.to_dict()


def _fields(raw, expected):
    if type(raw) is not dict or raw.keys() != expected:
        _reject()


@_checked
def parse_query(raw: object) -> DualLabVrrpQuery:
    """Parse exactly four query fields; the target pair is implicit and fixed."""
    _fields(raw, _QUERY_FIELDS)
    return DualLabVrrpQuery(**raw)


@_checked
def parse_target_result(raw: object) -> TargetResult:
    """Parse one exact tagged variant; malformed evidence is rejected."""
    if type(raw) is not dict or type(raw.get("status")) is not str:
        _reject()
    if raw["status"] == "SUCCESS":
        _fields(raw, _SUCCESS_FIELDS)
        return TargetSuccess(raw["status"], raw["target_ref"],
                             _stage2.parse_stage2_vrrp_observation_evidence(raw["evidence"]))
    if raw["status"] == "FAILURE":
        _fields(raw, _FAILURE_FIELDS)
        if type(raw["failure_category"]) is not str:
            _reject()
        return TargetFailure(raw["status"], raw["target_ref"], FailureCategory(raw["failure_category"]))
    _reject()


@_checked
def parse_aggregate(raw: object) -> DualLabVrrpAggregate:
    """Reject invalid aggregate input without manufacturing target failures."""
    _fields(raw, _AGGREGATE_FIELDS)
    query = parse_query({key: raw[key] for key in _QUERY_FIELDS})
    return DualLabVrrpAggregate(**query.to_dict(), lab1=parse_target_result(raw["lab1"]),
                               lab2=parse_target_result(raw["lab2"]))


def _encode(raw, maximum):
    encoded = _json.dumps(raw, allow_nan=False, ensure_ascii=False,
                          separators=(",", ":"), sort_keys=True).encode("utf-8", errors="strict")
    if not 1 <= len(encoded) <= maximum:
        _reject()
    return encoded


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _reject()
        result[key] = value
    return result


def _decode(raw, maximum):
    if (type(raw) is not bytes or not 1 <= len(raw) <= maximum
            or raw.startswith(b"\xef\xbb\xbf")):
        _reject()
    parsed = _json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_unique,
                         parse_constant=lambda _: _reject())
    if type(parsed) is not dict or _encode(parsed, maximum) != raw:
        _reject()
    return parsed


@_checked
def parse_query_canonical_json(raw: bytes) -> DualLabVrrpQuery:
    return parse_query(_decode(raw, _MAX_QUERY_BYTES))


@_checked
def parse_target_result_canonical_json(raw: bytes) -> TargetResult:
    return parse_target_result(_decode(raw, _MAX_RESULT_BYTES))


@_checked
def parse_aggregate_canonical_json(raw: bytes) -> DualLabVrrpAggregate:
    return parse_aggregate(_decode(raw, _MAX_AGGREGATE_BYTES))


__all__ = (
    "FailureCategory", "DualLabContractError", "DualLabVrrpQuery",
    "TargetSuccess", "TargetFailure", "TargetResult", "DualLabVrrpAggregate",
    "parse_query", "parse_target_result", "parse_aggregate",
    "parse_query_canonical_json", "parse_target_result_canonical_json",
    "parse_aggregate_canonical_json",
)
