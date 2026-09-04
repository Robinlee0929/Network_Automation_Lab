"""Offline contracts for one future Stage-2 VRRP read-only observation.

This module contains immutable request and normalized-evidence data only.  It
does not resolve any reference, authorize execution, parse device output, or
provide a transport/runtime boundary.  Importing and using it performs no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import re
from typing import Final
import unicodedata


STAGE2_VRRP_CONTRACT_SCHEMA_VERSION: Final = "1.0"
VRRP_OBSERVATION_OPERATION_ID: Final = "mikrotik.vrrp_status"
VRRP_COMMAND_POLICY_VERSION: Final = "policy.stage2.vrrp-readonly.v1"

MAX_REFERENCE_LENGTH: Final = 160
MAX_INSTANCE_NAME_UTF8_BYTES: Final = 128
MAX_VRRP_RECORDS: Final = 32
MAX_DURATION_MS: Final = 60_000
MAX_RAW_OUTPUT_BYTES: Final = 65_536
MAX_REQUEST_CANONICAL_BYTES: Final = 2_048
MAX_EVIDENCE_CANONICAL_BYTES: Final = 32_768

ALLOWED_VRRP_VERSIONS: Final = frozenset({2, 3})
ALLOWED_VRRP_ROLES: Final = frozenset(
    {"MASTER", "BACKUP", "FAILURE", "UNKNOWN"}
)

_REFERENCE_PATTERN: Final = re.compile(
    r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$"
)
_LOWER_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_REQUEST_FIELDS: Final = frozenset(
    {
        "schema_version",
        "operation_id",
        "run_id",
        "target_ref",
        "credential_ref",
        "authorization_ref",
        "read_only",
    }
)
_EVIDENCE_FIELDS: Final = frozenset(
    {
        "schema_version",
        "operation_id",
        "run_id",
        "target_ref",
        "authorization_ref",
        "command_policy_version",
        "attempt_count",
        "retry_count",
        "duration_ms",
        "raw_output_byte_count",
        "raw_output_sha256",
        "records",
    }
)
_RECORD_FIELDS: Final = frozenset(
    {
        "instance_name",
        "vrid",
        "priority",
        "interval_ms",
        "version",
        "running",
        "role",
        "disabled",
        "invalid",
    }
)
_FORBIDDEN_CREDENTIAL_REFERENCE_TOKENS: Final = frozenset(
    {
        "apikey",
        "password",
        "passphrase",
        "passwd",
        "privatekey",
        "pwd",
        "secret",
        "token",
        "username",
    }
)


class Stage2VrrpContractFailure(Enum):
    """Bounded contract failures that never retain rejected input."""

    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_EVIDENCE = "INVALID_EVIDENCE"


class Stage2VrrpContractError(ValueError):
    """Sanitized error for invalid S2-RO-01 contract data."""

    def __init__(self, code: Stage2VrrpContractFailure) -> None:
        if type(code) is not Stage2VrrpContractFailure:
            raise TypeError("contract error requires a bounded category")
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2VrrpObservationRequest:
    """One inert request for the fixed future read-only VRRP operation."""

    schema_version: str
    operation_id: str
    run_id: str
    target_ref: str
    credential_ref: str
    authorization_ref: str
    read_only: bool

    def __post_init__(self) -> None:
        if (
            self.schema_version != STAGE2_VRRP_CONTRACT_SCHEMA_VERSION
            or self.operation_id != VRRP_OBSERVATION_OPERATION_ID
            or not _is_reference(self.run_id, "run")
            or not _is_reference(self.target_ref, "target")
            or not _is_reference(self.credential_ref, "credential")
            or _credential_reference_looks_like_material(self.credential_ref)
            or not _is_reference(self.authorization_ref, "authorization")
            or self.read_only is not True
        ):
            _fail(Stage2VrrpContractFailure.INVALID_REQUEST)

    def __repr__(self) -> str:
        return "Stage2VrrpObservationRequest(<offline-read-only>)"

    __str__ = __repr__

    @property
    def execution_authorized(self) -> bool:
        """Contract validity is never execution authority."""

        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "operation_id": self.operation_id,
            "run_id": self.run_id,
            "target_ref": self.target_ref,
            "credential_ref": self.credential_ref,
            "authorization_ref": self.authorization_ref,
            "read_only": self.read_only,
        }

    def to_canonical_bytes(self) -> bytes:
        return _canonical_json_bytes(
            self.to_dict(),
            MAX_REQUEST_CANONICAL_BYTES,
            Stage2VrrpContractFailure.INVALID_REQUEST,
        )


@dataclass(frozen=True, slots=True, repr=False)
class NormalizedVrrpRecord:
    """Bounded reviewer evidence for one observed VRRP instance."""

    instance_name: str
    vrid: int
    priority: int
    interval_ms: int
    version: int
    running: bool
    role: str
    disabled: bool
    invalid: bool

    def __post_init__(self) -> None:
        if (
            not _is_normalized_display_text(self.instance_name)
            or type(self.vrid) is not int
            or not 1 <= self.vrid <= 255
            or type(self.priority) is not int
            or not 0 <= self.priority <= 255
            or type(self.interval_ms) is not int
            or not 1 <= self.interval_ms <= 255_000
            or type(self.version) is not int
            or self.version not in ALLOWED_VRRP_VERSIONS
            or type(self.running) is not bool
            or type(self.role) is not str
            or self.role not in ALLOWED_VRRP_ROLES
            or type(self.disabled) is not bool
            or type(self.invalid) is not bool
        ):
            _fail(Stage2VrrpContractFailure.INVALID_EVIDENCE)

    def __repr__(self) -> str:
        return "NormalizedVrrpRecord(<bounded>)"

    __str__ = __repr__

    def to_dict(self) -> dict[str, object]:
        return {
            "instance_name": self.instance_name,
            "vrid": self.vrid,
            "priority": self.priority,
            "interval_ms": self.interval_ms,
            "version": self.version,
            "running": self.running,
            "role": self.role,
            "disabled": self.disabled,
            "invalid": self.invalid,
        }


@dataclass(frozen=True, slots=True, repr=False)
class Stage2VrrpObservationEvidence:
    """Successful normalized evidence only; raw device output is excluded."""

    schema_version: str
    operation_id: str
    run_id: str
    target_ref: str
    authorization_ref: str
    command_policy_version: str
    attempt_count: int
    retry_count: int
    duration_ms: int
    raw_output_byte_count: int
    raw_output_sha256: str
    records: tuple[NormalizedVrrpRecord, ...]

    def __post_init__(self) -> None:
        if (
            self.schema_version != STAGE2_VRRP_CONTRACT_SCHEMA_VERSION
            or self.operation_id != VRRP_OBSERVATION_OPERATION_ID
            or not _is_reference(self.run_id, "run")
            or not _is_reference(self.target_ref, "target")
            or not _is_reference(self.authorization_ref, "authorization")
            or self.command_policy_version != VRRP_COMMAND_POLICY_VERSION
            or type(self.attempt_count) is not int
            or self.attempt_count != 1
            or type(self.retry_count) is not int
            or self.retry_count != 0
            or type(self.duration_ms) is not int
            or not 1 <= self.duration_ms <= MAX_DURATION_MS
            or type(self.raw_output_byte_count) is not int
            or not 0 <= self.raw_output_byte_count <= MAX_RAW_OUTPUT_BYTES
            or type(self.raw_output_sha256) is not str
            or not _LOWER_SHA256_PATTERN.fullmatch(self.raw_output_sha256)
            or type(self.records) is not tuple
            or len(self.records) > MAX_VRRP_RECORDS
            or any(type(record) is not NormalizedVrrpRecord for record in self.records)
        ):
            _fail(Stage2VrrpContractFailure.INVALID_EVIDENCE)

    def __repr__(self) -> str:
        return "Stage2VrrpObservationEvidence(<normalized-no-raw-output>)"

    __str__ = __repr__

    @property
    def execution_authorized(self) -> bool:
        """Evidence records an observation and grants no further authority."""

        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "operation_id": self.operation_id,
            "run_id": self.run_id,
            "target_ref": self.target_ref,
            "authorization_ref": self.authorization_ref,
            "command_policy_version": self.command_policy_version,
            "attempt_count": self.attempt_count,
            "retry_count": self.retry_count,
            "duration_ms": self.duration_ms,
            "raw_output_byte_count": self.raw_output_byte_count,
            "raw_output_sha256": self.raw_output_sha256,
            "records": [record.to_dict() for record in self.records],
        }

    def to_canonical_bytes(self) -> bytes:
        return _canonical_json_bytes(
            self.to_dict(),
            MAX_EVIDENCE_CANONICAL_BYTES,
            Stage2VrrpContractFailure.INVALID_EVIDENCE,
        )


def parse_stage2_vrrp_observation_request(
    raw_data: object,
) -> Stage2VrrpObservationRequest:
    """Parse one exact plain request record with no coercion or defaults."""

    if type(raw_data) is not dict or raw_data.keys() != _REQUEST_FIELDS:
        _fail(Stage2VrrpContractFailure.INVALID_REQUEST)
    return Stage2VrrpObservationRequest(
        schema_version=raw_data["schema_version"],
        operation_id=raw_data["operation_id"],
        run_id=raw_data["run_id"],
        target_ref=raw_data["target_ref"],
        credential_ref=raw_data["credential_ref"],
        authorization_ref=raw_data["authorization_ref"],
        read_only=raw_data["read_only"],
    )


def parse_stage2_vrrp_observation_evidence(
    raw_data: object,
) -> Stage2VrrpObservationEvidence:
    """Parse one exact successful evidence record with no raw-output field."""

    if type(raw_data) is not dict or raw_data.keys() != _EVIDENCE_FIELDS:
        _fail(Stage2VrrpContractFailure.INVALID_EVIDENCE)
    raw_records = raw_data["records"]
    if type(raw_records) is not list or len(raw_records) > MAX_VRRP_RECORDS:
        _fail(Stage2VrrpContractFailure.INVALID_EVIDENCE)
    records = tuple(_parse_record(record) for record in raw_records)
    return Stage2VrrpObservationEvidence(
        schema_version=raw_data["schema_version"],
        operation_id=raw_data["operation_id"],
        run_id=raw_data["run_id"],
        target_ref=raw_data["target_ref"],
        authorization_ref=raw_data["authorization_ref"],
        command_policy_version=raw_data["command_policy_version"],
        attempt_count=raw_data["attempt_count"],
        retry_count=raw_data["retry_count"],
        duration_ms=raw_data["duration_ms"],
        raw_output_byte_count=raw_data["raw_output_byte_count"],
        raw_output_sha256=raw_data["raw_output_sha256"],
        records=records,
    )


def parse_stage2_vrrp_request_canonical_json(
    raw_json: bytes,
) -> Stage2VrrpObservationRequest:
    """Parse byte-exact canonical request JSON and reject duplicates."""

    return parse_stage2_vrrp_observation_request(
        _decode_canonical_json(
            raw_json,
            MAX_REQUEST_CANONICAL_BYTES,
            Stage2VrrpContractFailure.INVALID_REQUEST,
        )
    )


def parse_stage2_vrrp_evidence_canonical_json(
    raw_json: bytes,
) -> Stage2VrrpObservationEvidence:
    """Parse byte-exact canonical evidence JSON and reject duplicates."""

    return parse_stage2_vrrp_observation_evidence(
        _decode_canonical_json(
            raw_json,
            MAX_EVIDENCE_CANONICAL_BYTES,
            Stage2VrrpContractFailure.INVALID_EVIDENCE,
        )
    )


def _parse_record(raw_data: object) -> NormalizedVrrpRecord:
    if type(raw_data) is not dict or raw_data.keys() != _RECORD_FIELDS:
        _fail(Stage2VrrpContractFailure.INVALID_EVIDENCE)
    return NormalizedVrrpRecord(
        instance_name=raw_data["instance_name"],
        vrid=raw_data["vrid"],
        priority=raw_data["priority"],
        interval_ms=raw_data["interval_ms"],
        version=raw_data["version"],
        running=raw_data["running"],
        role=raw_data["role"],
        disabled=raw_data["disabled"],
        invalid=raw_data["invalid"],
    )


def _is_reference(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= MAX_REFERENCE_LENGTH
        and value.isascii()
        and value.startswith(f"{prefix}.")
        and _REFERENCE_PATTERN.fullmatch(value) is not None
    )


def _credential_reference_looks_like_material(value: str) -> bool:
    compacted = re.sub(r"[._-]+", "", value)
    return any(
        token in compacted for token in _FORBIDDEN_CREDENTIAL_REFERENCE_TOKENS
    )


def _is_normalized_display_text(value: object) -> bool:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or value != unicodedata.normalize("NFC", value)
        or any(unicodedata.category(character).startswith("C") for character in value)
    ):
        return False
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return False
    return len(encoded) <= MAX_INSTANCE_NAME_UTF8_BYTES


def _canonical_json_bytes(
    value: dict[str, object],
    maximum: int,
    failure: Stage2VrrpContractFailure,
) -> bytes:
    try:
        encoded = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8", errors="strict")
    except (OverflowError, RecursionError, TypeError, ValueError, UnicodeEncodeError):
        _fail(failure)
    if not 1 <= len(encoded) <= maximum:
        _fail(failure)
    return encoded


def _decode_canonical_json(
    raw_json: object,
    maximum: int,
    failure: Stage2VrrpContractFailure,
) -> dict[str, object]:
    if (
        type(raw_json) is not bytes
        or not 1 <= len(raw_json) <= maximum
        or raw_json.startswith(b"\xef\xbb\xbf")
    ):
        _fail(failure)
    try:
        text = raw_json.decode("utf-8", errors="strict")
        parsed = json.loads(
            text,
            object_pairs_hook=lambda pairs: _unique_object(pairs, failure),
            parse_constant=lambda _: _fail(failure),
        )
    except Stage2VrrpContractError:
        raise
    except Exception:
        _fail(failure)
    if type(parsed) is not dict:
        _fail(failure)
    if _canonical_json_bytes(parsed, maximum, failure) != raw_json:
        _fail(failure)
    return parsed


def _unique_object(
    pairs: list[tuple[str, object]],
    failure: Stage2VrrpContractFailure,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            _fail(failure)
        result[key] = value
    return result


def _fail(code: Stage2VrrpContractFailure) -> None:
    raise Stage2VrrpContractError(code)


__all__ = (
    "ALLOWED_VRRP_ROLES",
    "ALLOWED_VRRP_VERSIONS",
    "MAX_DURATION_MS",
    "MAX_EVIDENCE_CANONICAL_BYTES",
    "MAX_INSTANCE_NAME_UTF8_BYTES",
    "MAX_RAW_OUTPUT_BYTES",
    "MAX_REFERENCE_LENGTH",
    "MAX_REQUEST_CANONICAL_BYTES",
    "MAX_VRRP_RECORDS",
    "NormalizedVrrpRecord",
    "STAGE2_VRRP_CONTRACT_SCHEMA_VERSION",
    "Stage2VrrpContractError",
    "Stage2VrrpContractFailure",
    "Stage2VrrpObservationEvidence",
    "Stage2VrrpObservationRequest",
    "VRRP_COMMAND_POLICY_VERSION",
    "VRRP_OBSERVATION_OPERATION_ID",
    "parse_stage2_vrrp_evidence_canonical_json",
    "parse_stage2_vrrp_observation_evidence",
    "parse_stage2_vrrp_observation_request",
    "parse_stage2_vrrp_request_canonical_json",
)
