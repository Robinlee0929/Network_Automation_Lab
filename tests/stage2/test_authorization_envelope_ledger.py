"""Synthetic offline S2-RO-05 evidence. No production ledger or credentials."""

import ast
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import multiprocessing
from pathlib import Path
import sqlite3

import pytest

from validation_framework import stage2_authorization_envelope_ledger as m
from validation_framework.stage2_vrrp_readonly_contract import Stage2VrrpObservationRequest
from validation_framework.stage2_mikrotik_target_registry import parse_stage2_fixed_target_registry
from validation_framework.stage2_mikrotik_credential_resolver import build_stage2_fixed_credential_resolver


AUTH_ID = "12345678-1234-4234-8234-123456789abc"
INSTANCE = "22345678-1234-4234-8234-123456789abc"
DDL = (
    "CREATE TABLE ledger_metadata (schema_version TEXT NOT NULL PRIMARY KEY COLLATE BINARY, ledger_instance_id TEXT NOT NULL COLLATE BINARY) STRICT",
    "CREATE TABLE consumed_authorizations (authorization_id TEXT NOT NULL PRIMARY KEY COLLATE BINARY, envelope_sha256 TEXT NOT NULL COLLATE BINARY, consumed_at INTEGER NOT NULL) STRICT, WITHOUT ROWID",
)


def inputs():
    request = Stage2VrrpObservationRequest("1.0", "mikrotik.vrrp_status", "run.demo",
        "target.mikrotik.lab01", "credential.mikrotik.lab01", "authorization.demo", True)
    envelope = m.Stage2AuthorizationEnvelope("1.0", AUTH_ID, request.operation_id,
        hashlib.sha256(request.to_canonical_bytes()).hexdigest(), request.authorization_ref,
        request.target_ref, request.credential_ref, 1000, 1300, 1)
    registry = parse_stage2_fixed_target_registry(dict(target_ref=request.target_ref,
        address="192.0.2.10", port=22, transport="SSH", declared_lab_only=True))
    binding = build_stage2_fixed_credential_resolver().resolve(request.credential_ref)
    return envelope, request, registry, binding


def provision(path, ddl=DDL, metadata=True):
    with sqlite3.connect(path) as connection:
        for statement in ddl:
            connection.execute(statement)
        if metadata:
            connection.execute("INSERT INTO ledger_metadata VALUES (?, ?)", ("1.0", INSTANCE))


def configuration(path):
    return m.Stage2ReplayLedgerConfiguration(path, INSTANCE, (Path(__file__).resolve().parents[2],))


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / "ledger.db"
    provision(path)
    return m.Stage2ReplayLedger(configuration(path))


def consume(ledger, args=None, **kwargs):
    return ledger.consume(*(inputs() if args is None else args), utc_now=kwargs.get("clock", lambda: 1100))


def encode(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode()


def test_roundtrip_payload_and_immutable_aliases():
    envelope = inputs()[0]
    source = bytearray(envelope.to_canonical_bytes())
    parsed = m.parse_stage2_authorization_envelope(bytes(source))
    source[:] = b"changed"
    exported = parsed.to_dict()
    exported["authorization_id"] = "changed"
    assert parsed == envelope
    assert parsed.to_canonical_bytes() == envelope.to_canonical_bytes()
    with pytest.raises(FrozenInstanceError):
        parsed.issued_at = 0
    assert not parsed.execution_authorized
    assert m.owner_verification_payload(parsed) == (
        b"Network_Automation_Lab/S2-RO-05/authorization-envelope/v1\x00" + envelope.to_canonical_bytes())


@pytest.mark.parametrize("field", list(inputs()[0].to_dict()))
def test_missing_each_field(field):
    record = inputs()[0].to_dict()
    del record[field]
    with pytest.raises(m.Stage2AuthorizationError):
        m.parse_stage2_authorization_envelope(encode(record))


@pytest.mark.parametrize("field,value", [
    ("schema_version", "2.0"), ("schema_version", 1),
    ("authorization_id", AUTH_ID.upper()), ("authorization_id", "{" + AUTH_ID + "}"),
    ("authorization_id", "12345678-1234-1234-8234-123456789abc"),
    ("authorization_id", " " + AUTH_ID), ("authorization_id", "x" * 500),
    ("operation_id", "other"), ("target_ref", "target.other"),
    ("credential_ref", "credential.other"), ("authorization_ref", "authorization.é"),
    ("authorization_ref", "authorization." + "a" * 160), ("authorization_ref", "authorization.a/b"),
    ("request_sha256", "A" * 64), ("request_sha256", "0" * 63),
    ("issued_at", True), ("issued_at", 1000.0), ("issued_at", -1),
    ("expires_at", "1300"), ("expires_at", 1301), ("expires_at", 1000),
    ("expires_at", 999), ("expires_at", m.MAX_UNIX_SECONDS + 1),
    ("max_attempts", 0), ("max_attempts", 2), ("max_attempts", True),
])
def test_invalid_fields(field, value):
    record = inputs()[0].to_dict()
    record[field] = value
    with pytest.raises(m.Stage2AuthorizationError):
        m.parse_stage2_authorization_envelope(encode(record))


@pytest.mark.parametrize("raw", [b"", b"\xff", b"{}", b"[]", b"null", b"x" * 2049,
    b'{"schema_version":"1.0","schema_version":"1.0"}',
    b'{' + b'"x":[' * 200 + b'}', bytearray(b"{}"), "{}"])
def test_invalid_bytes(raw):
    with pytest.raises(m.Stage2AuthorizationError):
        m.parse_stage2_authorization_envelope(raw)


@pytest.mark.parametrize("variant", ["newline", "space", "pretty", "bom", "escape", "extra", "nan"])
def test_noncanonical(variant):
    env = inputs()[0]
    raw = env.to_canonical_bytes()
    if variant == "newline": raw += b"\n"
    if variant == "space": raw = b" " + raw
    if variant == "pretty": raw = json.dumps(env.to_dict(), indent=2).encode()
    if variant == "bom": raw = b"\xef\xbb\xbf" + raw
    if variant == "escape": raw = raw.replace(b"authorization.demo", b"authorization.\\u0064emo")
    if variant == "extra": raw = encode(dict(env.to_dict(), extra=1))
    if variant == "nan": raw = raw.replace(b'"issued_at":1000', b'"issued_at":NaN')
    with pytest.raises(m.Stage2AuthorizationError):
        m.parse_stage2_authorization_envelope(raw)


@pytest.mark.parametrize("now,code", [(999, "NOT_YET_VALID"), (1300, "EXPIRED"),
    (1400, "EXPIRED"), (True, "INVALID_CLOCK"), (1100.0, "INVALID_CLOCK"), (-1, "INVALID_CLOCK")])
def test_time_rejection(now, code):
    with pytest.raises(m.Stage2AuthorizationError, match=code):
        m.validate_stage2_authorization_binding(*inputs(), now=now)


@pytest.mark.parametrize("now", [1000, 1299])
def test_time_inclusive_exclusive(now):
    assert m.validate_stage2_authorization_binding(*inputs(), now=now) is None


@pytest.mark.parametrize("change", ["digest", "authorization", "run", "target", "credential", "binding", "registry"])
def test_binding_failure_before_io(change, ledger, monkeypatch):
    args = list(inputs())
    if change == "digest": args[0] = replace(args[0], request_sha256="0" * 64)
    if change == "authorization": args[0] = replace(args[0], authorization_ref="authorization.other")
    if change == "run": args[1] = replace(args[1], run_id="run.other")
    if change == "target": args[1] = replace(args[1], target_ref="target.other")
    if change == "credential": args[1] = replace(args[1], credential_ref="credential.other")
    if change == "binding": args[3] = object()
    if change == "registry": args[2] = object()
    def forbidden(*a, **k):
        pytest.fail("rejected binding reached filesystem")
    monkeypatch.setattr(m, "_path_identity", forbidden)
    with pytest.raises(m.Stage2AuthorizationError, match="INVALID_BINDING"):
        consume(ledger, args)


def test_first_replay_changed_envelope_restart_and_record(ledger):
    result = consume(ledger)
    assert not result.execution_authorized
    assert result.consumed_at == 1100
    assert result.envelope_sha256 == hashlib.sha256(inputs()[0].to_canonical_bytes()).hexdigest()
    for candidate in (ledger, m.Stage2ReplayLedger(ledger._configuration)):
        with pytest.raises(m.Stage2AuthorizationError, match="REPLAY"):
            consume(candidate)
    args = list(inputs())
    args[0] = replace(args[0], issued_at=1001)
    with pytest.raises(m.Stage2AuthorizationError, match="REPLAY"):
        consume(ledger, args)
    with sqlite3.connect(ledger._configuration.database_path) as db:
        assert db.execute("SELECT * FROM consumed_authorizations").fetchall() == [
            (AUTH_ID, result.envelope_sha256, 1100)]


def test_missing_and_wrong_object(tmp_path):
    for path in (tmp_path / "missing.db", tmp_path):
        with pytest.raises(m.Stage2AuthorizationError):
            consume(m.Stage2ReplayLedger(configuration(path)))
    assert not (tmp_path / "missing.db").exists()


@pytest.mark.parametrize("mutation", ["version", "instance", "metadata", "duplicate_metadata", "row", "trigger", "index", "extra_table", "sqlite_prefix"])
def test_invalid_ledger(ledger, mutation):
    sql = {
        "version": "UPDATE ledger_metadata SET schema_version='2.0'",
        "instance": "UPDATE ledger_metadata SET ledger_instance_id='wrong'",
        "metadata": "DELETE FROM ledger_metadata",
        "duplicate_metadata": "INSERT INTO ledger_metadata VALUES ('2.0', 'wrong')",
        "row": "INSERT INTO consumed_authorizations VALUES ('bad', 'bad', -1)",
        "trigger": "CREATE TRIGGER bad AFTER INSERT ON consumed_authorizations BEGIN DELETE FROM consumed_authorizations; END",
        "index": "CREATE INDEX extra ON consumed_authorizations(consumed_at)",
        "extra_table": "CREATE TABLE extra(x TEXT)",
        "sqlite_prefix": "CREATE TABLE sqliteXextra(x TEXT)",
    }[mutation]
    with sqlite3.connect(ledger._configuration.database_path) as db:
        db.execute(sql)
    with pytest.raises(m.Stage2AuthorizationError, match="INVALID_LEDGER"):
        consume(ledger)


@pytest.mark.parametrize("alteration", ["column", "nullable", "replace", "ignore", "nocase", "not_strict", "rowid"])
def test_schema_exact(tmp_path, alteration):
    ddl = list(DDL)
    substitutions = {
        "column": ("consumed_at INTEGER NOT NULL", "consumed_at INTEGER NOT NULL, extra TEXT"),
        "nullable": ("authorization_id TEXT NOT NULL", "authorization_id TEXT"),
        "replace": ("PRIMARY KEY COLLATE", "PRIMARY KEY ON CONFLICT REPLACE COLLATE"),
        "ignore": ("PRIMARY KEY COLLATE", "PRIMARY KEY ON CONFLICT IGNORE COLLATE"),
        "nocase": ("BINARY", "NOCASE"), "not_strict": ("STRICT, WITHOUT ROWID", "WITHOUT ROWID"),
        "rowid": ("STRICT, WITHOUT ROWID", "STRICT"),
    }
    ddl[1] = ddl[1].replace(*substitutions[alteration])
    path = tmp_path / "bad.db"
    provision(path, ddl)
    with pytest.raises(m.Stage2AuthorizationError):
        consume(m.Stage2ReplayLedger(configuration(path)))


@pytest.mark.parametrize("content", [b"", b"not sqlite", b"SQLite format 3\x00partial"])
def test_corrupt_partial_no_repair(tmp_path, content):
    path = tmp_path / "bad.db"
    path.write_bytes(content)
    with pytest.raises(m.Stage2AuthorizationError):
        consume(m.Stage2ReplayLedger(configuration(path)))
    assert path.read_bytes() == content


def test_busy_no_retry(ledger):
    with sqlite3.connect(ledger._configuration.database_path) as db:
        db.execute("BEGIN IMMEDIATE")
        with pytest.raises(m.Stage2AuthorizationError):
            consume(ledger)
    assert consume(ledger)


@pytest.mark.parametrize("phase", ["open", "insert", "commit_before", "commit_after", "close"])
def test_faults_never_success_or_retry(ledger, monkeypatch, phase):
    original = sqlite3.connect
    calls = []
    class FaultConnection:
        def __init__(self, connection): self.connection = connection
        def __getattr__(self, name): return getattr(self.connection, name)
        def execute(self, sql, *args):
            if phase == "insert" and sql.startswith("INSERT"):
                raise OSError("sensitive SQL detail")
            return self.connection.execute(sql, *args)
        def commit(self):
            if phase == "commit_before": raise OSError("private path")
            self.connection.commit()
            if phase == "commit_after": raise OSError("unknown durable result")
        def close(self):
            self.connection.close()
            if phase == "close": raise OSError("cleanup detail")
    def connect(*args, **kwargs):
        calls.append(1)
        if phase == "open": raise OSError("private path")
        return FaultConnection(original(*args, **kwargs))
    monkeypatch.setattr(m.sqlite3, "connect", connect)
    with pytest.raises(m.Stage2AuthorizationError) as exc:
        consume(ledger)
    assert len(calls) == 1
    assert str(exc.value) == exc.value.code.value
    assert exc.value.__context__ is None
    monkeypatch.setattr(m.sqlite3, "connect", original)
    if phase in ("commit_after", "close"):
        with pytest.raises(m.Stage2AuthorizationError, match="REPLAY"):
            consume(ledger)


def test_expired_after_commit_is_spent(ledger):
    clock = iter([1100, 1100, 1300])
    with pytest.raises(m.Stage2AuthorizationError, match="EXPIRED"):
        consume(ledger, clock=lambda: next(clock))
    with pytest.raises(m.Stage2AuthorizationError, match="REPLAY"):
        consume(ledger)


@pytest.mark.parametrize("setting", ["journal_mode", "synchronous", "busy_timeout", "trusted_schema", "foreign_keys", "locking_mode"])
def test_effective_setting_mismatch_rejects(ledger, monkeypatch, setting):
    original = sqlite3.connect
    class WrongSetting:
        def __init__(self, db): self.db = db
        def __getattr__(self, key): return getattr(self.db, key)
        def execute(self, sql, *args):
            if sql == "PRAGMA " + setting:
                class Row:
                    def fetchone(self): return ("wrong",)
                return Row()
            return self.db.execute(sql, *args)
    monkeypatch.setattr(m.sqlite3, "connect", lambda *a, **k: WrongSetting(original(*a, **k)))
    with pytest.raises(m.Stage2AuthorizationError, match="INVALID_LEDGER"):
        consume(ledger)


def test_capacity_without_pruning(ledger, monkeypatch):
    consume(ledger)
    monkeypatch.setattr(m, "MAX_LEDGER_RECORDS", 1)
    with pytest.raises(m.Stage2AuthorizationError, match="CAPACITY_EXCEEDED"):
        consume(ledger)
    with sqlite3.connect(ledger._configuration.database_path) as db:
        assert db.execute("SELECT count(*) FROM consumed_authorizations").fetchone() == (1,)


def test_size_capacity(ledger, monkeypatch):
    monkeypatch.setattr(m, "MAX_LEDGER_BYTES", 1)
    with pytest.raises(m.Stage2AuthorizationError, match="CAPACITY_EXCEEDED"):
        consume(ledger)


def test_configuration_and_consumption_record_bounds(tmp_path):
    for path in (Path("relative.db"), tmp_path / ".." / "bad.db"):
        with pytest.raises(m.Stage2AuthorizationError):
            configuration(path)
    with pytest.raises(m.Stage2AuthorizationError):
        m.Stage2ReplayLedgerConfiguration(tmp_path / "x", INSTANCE, [])
    for timestamp in (-1, True, 1.5, m.MAX_UNIX_SECONDS + 1):
        with pytest.raises(m.Stage2AuthorizationError):
            m.Stage2ConsumptionRecord(AUTH_ID, "0" * 64, timestamp)


def test_clock_exception_and_preinsert_expiry(ledger):
    def broken(): raise OSError("private clock detail")
    with pytest.raises(m.Stage2AuthorizationError, match="INVALID_CLOCK"):
        consume(ledger, clock=broken)
    clock = iter([1100, 1300])
    with pytest.raises(m.Stage2AuthorizationError, match="EXPIRED"):
        consume(ledger, clock=lambda: next(clock))
    assert consume(ledger)


def _process_consume(path, start, output):
    start.wait(10)
    try:
        consume(m.Stage2ReplayLedger(configuration(Path(path))))
        output.send("success")
    except m.Stage2AuthorizationError as error:
        output.send(error.code.value)
    finally:
        output.close()


def test_competing_processes_and_process_restart(ledger):
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    readers, processes = [], []
    for _ in range(2):
        read, write = context.Pipe(duplex=False)
        process = context.Process(target=_process_consume,
            args=(str(ledger._configuration.database_path), start, write))
        process.start()
        write.close()
        readers.append(read)
        processes.append(process)
    start.set()
    try:
        results = []
        for reader in readers:
            assert reader.poll(20)
            results.append(reader.recv())
        assert results.count("success") == 1
        assert set(results) <= {"success", "REPLAY", "LEDGER_UNAVAILABLE"}
    finally:
        for process in processes:
            process.join(20)
            if process.is_alive(): process.terminate(); process.join()
        for reader in readers: reader.close()
    read, write = context.Pipe(duplex=False)
    process = context.Process(target=_process_consume,
        args=(str(ledger._configuration.database_path), start, write))
    process.start()
    write.close()
    try:
        assert read.poll(20)
        assert read.recv() == "REPLAY"
    finally:
        process.join(20)
        if process.is_alive(): process.terminate(); process.join()
        read.close()


def test_no_forbidden_capabilities_or_reset():
    tree = ast.parse(Path(m.__file__).read_text(encoding="utf-8"))
    imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert not imports & {"socket", "dns", "paramiko", "subprocess", "ctypes", "requests"}
    assert not set(dir(m.Stage2ReplayLedger)) & {"reset", "unconsume", "delete", "retry", "enumerate"}
    for item in (*inputs()[::3],):
        assert AUTH_ID not in repr(item)


def test_valid_snapshot_rollback_is_explicitly_not_protected(ledger):
    path = ledger._configuration.database_path
    historical = path.read_bytes()
    consume(ledger)
    # Synthetic threat-model demonstration, never a production recovery action.
    path.write_bytes(historical)
    assert consume(ledger)
    doc = Path(__file__).resolve().parents[2] / "docs/automation_readiness/stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md"
    assert "VALID_SNAPSHOT_ROLLBACK_PROTECTION = OUT_OF_SCOPE" in doc.read_text(encoding="utf-8")
