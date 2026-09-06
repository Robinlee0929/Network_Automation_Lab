"""Offline envelope data and durable single consumption, never execution authority.

Replay resistance assumes the same trusted non-rolled-back persistent history.
No independent anti-rollback anchor or Owner authenticity verification exists.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import stat
import time
from uuid import UUID

from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpObservationRequest, VRRP_OBSERVATION_OPERATION_ID,
    parse_stage2_vrrp_observation_request,
)
from validation_framework.stage2_mikrotik_target_registry import (
    Stage2FixedTargetRegistry, STAGE2_FIXED_TARGET_REF,
)
from validation_framework.stage2_mikrotik_credential_resolver import (
    Stage2CredentialBinding, STAGE2_FIXED_CREDENTIAL_REF,
    build_stage2_fixed_credential_resolver,
)


SCHEMA_VERSION = "1.0"
MAX_CANONICAL_ENVELOPE_BYTES = 2048
MAX_UNIX_SECONDS = 253402300799
MAX_VALIDITY_SECONDS = 300
MAX_LEDGER_RECORDS = 100_000
MAX_LEDGER_BYTES = 64 * 1024 * 1024
OWNER_PAYLOAD_DOMAIN = b"Network_Automation_Lab/S2-RO-05/authorization-envelope/v1\x00"
_REFERENCE = re.compile(r"authorization\.[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*")
_DIGEST = re.compile(r"[0-9a-f]{64}")
_SCHEMA = (
    "CREATE TABLE ledger_metadata (schema_version TEXT NOT NULL PRIMARY KEY COLLATE BINARY, "
    "ledger_instance_id TEXT NOT NULL COLLATE BINARY) STRICT",
    "CREATE TABLE consumed_authorizations (authorization_id TEXT NOT NULL PRIMARY KEY COLLATE BINARY, "
    "envelope_sha256 TEXT NOT NULL COLLATE BINARY, consumed_at INTEGER NOT NULL) STRICT, WITHOUT ROWID",
)


class Stage2AuthorizationFailure(Enum):
    INVALID_ENVELOPE = "INVALID_ENVELOPE"
    INVALID_BINDING = "INVALID_BINDING"
    INVALID_CLOCK = "INVALID_CLOCK"
    NOT_YET_VALID = "NOT_YET_VALID"
    EXPIRED = "EXPIRED"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    INVALID_LEDGER = "INVALID_LEDGER"
    LEDGER_UNAVAILABLE = "LEDGER_UNAVAILABLE"
    REPLAY = "REPLAY"
    COMMIT_UNCERTAIN = "COMMIT_UNCERTAIN"
    CAPACITY_EXCEEDED = "CAPACITY_EXCEEDED"


class Stage2AuthorizationError(ValueError):
    def __init__(self, code: Stage2AuthorizationFailure):
        if type(code) is not Stage2AuthorizationFailure:
            raise TypeError("bounded authorization category required")
        self.code = code
        super().__init__(code.value)


def _fail(code):
    raise Stage2AuthorizationError(code) from None


def _uuid(value):
    if type(value) is not str or len(value) != 36:
        return False
    try:
        parsed = UUID(value)
        return parsed.version == 4 and str(parsed) == value
    except ValueError:
        return False


def _digest(value):
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _seconds(value):
    return type(value) is int and 0 <= value <= MAX_UNIX_SECONDS


@dataclass(frozen=True, slots=True, repr=False)
class Stage2AuthorizationEnvelope:
    schema_version: str
    authorization_id: str
    operation_id: str
    request_sha256: str
    authorization_ref: str
    target_ref: str
    credential_ref: str
    issued_at: int
    expires_at: int
    max_attempts: int

    def __post_init__(self):
        exact = ((self.schema_version, SCHEMA_VERSION),
                 (self.operation_id, VRRP_OBSERVATION_OPERATION_ID),
                 (self.target_ref, STAGE2_FIXED_TARGET_REF),
                 (self.credential_ref, STAGE2_FIXED_CREDENTIAL_REF))
        if (any(type(value) is not str or value != expected for value, expected in exact)
                or not _uuid(self.authorization_id) or not _digest(self.request_sha256)
                or type(self.authorization_ref) is not str
                or not 1 <= len(self.authorization_ref) <= 160
                or _REFERENCE.fullmatch(self.authorization_ref) is None
                or not _seconds(self.issued_at) or not _seconds(self.expires_at)
                or not 1 <= self.expires_at - self.issued_at <= MAX_VALIDITY_SECONDS
                or type(self.max_attempts) is not int or self.max_attempts != 1):
            _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)

    def __repr__(self):
        return "Stage2AuthorizationEnvelope(<untrusted-offline-data>)"

    __str__ = __repr__

    @property
    def execution_authorized(self):
        return False

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def to_canonical_bytes(self):
        self.__post_init__()
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
        result[key] = value
    return result


def parse_stage2_authorization_envelope(raw):
    if type(raw) is not bytes or not 1 <= len(raw) <= MAX_CANONICAL_ENVELOPE_BYTES:
        _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
    error = False
    try:
        record = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs)
        expected = {field.name for field in fields(Stage2AuthorizationEnvelope)}
        if type(record) is not dict or record.keys() != expected:
            _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
        envelope = Stage2AuthorizationEnvelope(**record)
        if envelope.to_canonical_bytes() != raw:
            _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
    except Exception:
        error = True
    if error:
        _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
    return envelope


def _current(envelope, now):
    if not _seconds(now):
        _fail(Stage2AuthorizationFailure.INVALID_CLOCK)
    if now < envelope.issued_at:
        _fail(Stage2AuthorizationFailure.NOT_YET_VALID)
    if now >= envelope.expires_at:
        _fail(Stage2AuthorizationFailure.EXPIRED)


def validate_stage2_authorization_binding(envelope, request, registry, credential_binding, *, now):
    invalid = False
    try:
        if (type(envelope) is not Stage2AuthorizationEnvelope
                or type(request) is not Stage2VrrpObservationRequest
                or type(registry) is not Stage2FixedTargetRegistry
                or type(credential_binding) is not Stage2CredentialBinding):
            _fail(Stage2AuthorizationFailure.INVALID_BINDING)
        envelope.__post_init__()
        validated_request = parse_stage2_vrrp_observation_request(request.to_dict())
        endpoint = registry.lookup(validated_request.target_ref)
        endpoint.__post_init__()
        expected_binding = build_stage2_fixed_credential_resolver().resolve(request.credential_ref)
        if (credential_binding != expected_binding
                or envelope.operation_id != request.operation_id
                or envelope.authorization_ref != request.authorization_ref
                or envelope.target_ref != endpoint.target_ref
                or envelope.credential_ref != credential_binding.credential_ref
                or envelope.request_sha256 != hashlib.sha256(request.to_canonical_bytes()).hexdigest()):
            _fail(Stage2AuthorizationFailure.INVALID_BINDING)
    except Exception:
        invalid = True
    if invalid:
        _fail(Stage2AuthorizationFailure.INVALID_BINDING)
    _current(envelope, now)


def owner_verification_payload(envelope):
    if type(envelope) is not Stage2AuthorizationEnvelope:
        _fail(Stage2AuthorizationFailure.INVALID_ENVELOPE)
    return OWNER_PAYLOAD_DOMAIN + envelope.to_canonical_bytes()


@dataclass(frozen=True, slots=True, repr=False)
class Stage2ReplayLedgerConfiguration:
    database_path: Path
    expected_ledger_instance_id: str
    excluded_roots: tuple[Path, ...]

    def __post_init__(self):
        if (not _local_path(self.database_path)
                or not _uuid(self.expected_ledger_instance_id)
                or type(self.excluded_roots) is not tuple or not self.excluded_roots
                or len(self.excluded_roots) > 32
                or any(not _local_path(root) for root in self.excluded_roots)):
            _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)

    def __repr__(self):
        return "Stage2ReplayLedgerConfiguration(<trusted-redacted>)"

    __str__ = __repr__


def _local_path(path):
    return (type(path) is type(Path()) and path.is_absolute()
            and len(str(path)) <= 1024 and not str(path).startswith(("\\\\", "//"))
            and ".." not in path.parts
            and all(ord(char) >= 32 for char in str(path))
            and ":" not in str(path)[len(path.drive):])


def _path_identity(configuration):
    path = configuration.database_path
    roots = (*configuration.excluded_roots, Path(__file__).resolve().parent.parent)
    if any(path.resolve().is_relative_to(root.resolve()) for root in roots):
        _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
    for entry in (path, *path.parents):
        info = entry.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
        if entry != path and not stat.S_ISDIR(info.st_mode):
            _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
    if info.st_size > MAX_LEDGER_BYTES:
        _fail(Stage2AuthorizationFailure.CAPACITY_EXCEEDED)
    for suffix in ("-journal", "-wal", "-shm"):
        sidecar = path.with_name(path.name + suffix)
        try:
            extra = sidecar.lstat()
        except FileNotFoundError:
            continue
        if (not stat.S_ISREG(extra.st_mode) or extra.st_nlink != 1
                or getattr(extra, "st_file_attributes", 0) & 0x400):
            _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
    return info.st_dev, info.st_ino


@dataclass(frozen=True, slots=True, repr=False)
class Stage2ConsumptionRecord:
    authorization_id: str
    envelope_sha256: str
    consumed_at: int

    def __post_init__(self):
        if not _uuid(self.authorization_id) or not _digest(self.envelope_sha256) or not _seconds(self.consumed_at):
            _fail(Stage2AuthorizationFailure.INVALID_LEDGER)

    def __repr__(self):
        return "Stage2ConsumptionRecord(<spent-not-execution-authority>)"

    __str__ = __repr__

    @property
    def execution_authorized(self):
        return False


def _schema_tokens(sql):
    # Deliberately allow only whitespace/case and one terminal semicolon variation.
    if type(sql) is not str or len(sql) > 1024:
        return None
    text = sql.strip().removesuffix(";")
    tokens = re.findall(r"[A-Za-z_][A-Za-z_0-9]*|[(),]", text)
    if re.sub(r"[A-Za-z_][A-Za-z_0-9]*|[(),]|\s+", "", text):
        return None
    return tuple(token.upper() for token in tokens)


def _validate_ledger(connection, configuration):
    rows = connection.execute(
        "SELECT type, name, sql FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*'"
    ).fetchmany(4)
    expected = {
        ("table", "ledger_metadata"): _schema_tokens(_SCHEMA[0]),
        ("table", "consumed_authorizations"): _schema_tokens(_SCHEMA[1]),
    }
    if (any(value is None for value in expected.values()) or len(rows) != 2
            or {(kind, name): _schema_tokens(sql) for kind, name, sql in rows} != expected):
        _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
    if connection.execute("PRAGMA integrity_check").fetchmany(2) != [("ok",)]:
        _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
    if connection.execute("SELECT schema_version, ledger_instance_id FROM ledger_metadata").fetchmany(2) != [
        (SCHEMA_VERSION, configuration.expected_ledger_instance_id)
    ]:
        _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
    count = connection.execute("SELECT count(*) FROM consumed_authorizations").fetchone()[0]
    if count >= MAX_LEDGER_RECORDS:
        _fail(Stage2AuthorizationFailure.CAPACITY_EXCEEDED)
    for row in connection.execute("SELECT authorization_id, envelope_sha256, consumed_at FROM consumed_authorizations"):
        Stage2ConsumptionRecord(*row)


def _now(clock):
    failed = False
    try:
        value = clock()
    except Exception:
        failed = True
    if failed or not _seconds(value):
        _fail(Stage2AuthorizationFailure.INVALID_CLOCK)
    return value


def _system_now():
    return time.time_ns() // 1_000_000_000


class Stage2ReplayLedger:
    """Local I/O only; consumption does not authenticate the Owner or execute."""

    __slots__ = ("_configuration",)

    def __init__(self, configuration):
        if type(configuration) is not Stage2ReplayLedgerConfiguration:
            _fail(Stage2AuthorizationFailure.INVALID_CONFIGURATION)
        configuration.__post_init__()
        self._configuration = configuration

    def __repr__(self):
        return "Stage2ReplayLedger(<pre-provisioned-offline>)"

    __str__ = __repr__

    def consume(self, envelope, request, registry, credential_binding, *, utc_now=_system_now):
        validate_stage2_authorization_binding(
            envelope, request, registry, credential_binding, now=_now(utc_now))
        connection = None
        failure = None
        result = None
        try:
            identity = _path_identity(self._configuration)
            connection = sqlite3.connect(
                self._configuration.database_path.as_uri() + "?mode=rw",
                uri=True, timeout=0, isolation_level=None)
            connection.execute("PRAGMA synchronous=EXTRA")
            connection.execute("PRAGMA trusted_schema=OFF")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN IMMEDIATE")
            required = {"journal_mode": ("delete",), "synchronous": (3,),
                        "busy_timeout": (0,), "locking_mode": ("normal",),
                        "trusted_schema": (0,), "foreign_keys": (1,)}
            for setting, expected in required.items():
                if connection.execute("PRAGMA " + setting).fetchone() != expected:
                    _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
            _validate_ledger(connection, self._configuration)
            consumed_at = _now(utc_now)
            _current(envelope, consumed_at)
            result = Stage2ConsumptionRecord(envelope.authorization_id,
                hashlib.sha256(envelope.to_canonical_bytes()).hexdigest(), consumed_at)
            try:
                connection.execute(
                    "INSERT INTO consumed_authorizations (authorization_id, envelope_sha256, consumed_at) VALUES (?, ?, ?)",
                    (result.authorization_id, result.envelope_sha256, result.consumed_at))
            except sqlite3.IntegrityError:
                _fail(Stage2AuthorizationFailure.REPLAY)
            page_size = connection.execute("PRAGMA page_size").fetchone()[0]
            page_count = connection.execute("PRAGMA page_count").fetchone()[0]
            if page_size * page_count > MAX_LEDGER_BYTES:
                _fail(Stage2AuthorizationFailure.CAPACITY_EXCEEDED)
            if _path_identity(self._configuration) != identity:
                _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
            try:
                connection.commit()
            except Exception:
                _fail(Stage2AuthorizationFailure.COMMIT_UNCERTAIN)
            _current(envelope, _now(utc_now))
            if _path_identity(self._configuration) != identity:
                _fail(Stage2AuthorizationFailure.INVALID_LEDGER)
        except Stage2AuthorizationError as error:
            failure = error.code
        except Exception:
            failure = Stage2AuthorizationFailure.LEDGER_UNAVAILABLE
        finally:
            if connection is not None:
                try:
                    if connection.in_transaction:
                        connection.rollback()
                except Exception:
                    failure = failure or Stage2AuthorizationFailure.LEDGER_UNAVAILABLE
                try:
                    connection.close()
                except Exception:
                    failure = failure or Stage2AuthorizationFailure.LEDGER_UNAVAILABLE
        if failure is not None:
            _fail(failure)
        return result


__all__ = (
    "Stage2AuthorizationEnvelope", "Stage2ReplayLedgerConfiguration",
    "Stage2ReplayLedger", "Stage2ConsumptionRecord", "Stage2AuthorizationError",
    "Stage2AuthorizationFailure", "parse_stage2_authorization_envelope",
    "validate_stage2_authorization_binding", "owner_verification_payload",
)
