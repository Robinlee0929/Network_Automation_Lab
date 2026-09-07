"""Synthetic host trust only: no real file source, DLL, key, secret or network."""

import ast
import base64
import builtins
import copy
import ctypes
import dataclasses
import hashlib
import importlib
import inspect
import json
import pickle
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest

from validation_framework import stage2_known_host_snapshot as subject
from validation_framework.stage2_mikrotik_target_registry import Stage2FixedTargetEndpoint


F = subject.Stage2KnownHostFailure
PATH = r"c:\synthetic-owner\host-trust.json"
IDENTITY = "win32-fileid-v1:0123456789abcdef:000102030405060708090a0b0c0d0e0f"
OTHER_ID = "win32-fileid-v1:0123456789abcdef:100102030405060708090a0b0c0d0e0f"
PREFIX = b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20"
BLOB = PREFIX + bytes(range(32))


def endpoint(address="192.0.2.17"):
    return Stage2FixedTargetEndpoint("target.mikrotik.lab01", address, 22, "SSH", True)


def record(**changes):
    value = dict(schema_version="s2-ro-07.known-host.v1", target_ref="target.mikrotik.lab01",
                 address="192.0.2.17", port=22, host_key_algorithm="ssh-ed25519",
                 host_key_base64=base64.b64encode(BLOB).decode("ascii"))
    value.update(changes)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


RAW = canonical(record())


def configuration(raw=RAW, **changes):
    values = dict(expected_path=PATH, expected_file_identity=IDENTITY,
                  expected_file_sha256=hashlib.sha256(raw).hexdigest(), expected_endpoint=endpoint())
    values.update(changes)
    return subject.Stage2KnownHostSourceConfiguration(**values)


def assert_failure(code, operation):
    with pytest.raises(subject.Stage2KnownHostError) as caught:
        operation()
    error = caught.value
    assert error.code is code
    assert error.args == (code.value,)
    assert str(error) == code.value
    assert error.__context__ is None
    assert error.__cause__ is None
    assert PATH not in repr(error)
    return error


@pytest.fixture(autouse=True)
def no_execution(monkeypatch):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append("forbidden boundary")
        raise AssertionError("real native/network/execution boundary forbidden")

    monkeypatch.setattr(ctypes, "WinDLL", forbidden, raising=False)
    for name in ("socket", "create_connection", "getaddrinfo", "gethostbyname", "gethostbyaddr"):
        monkeypatch.setattr(socket, name, forbidden)
    for name in ("Popen", "run", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, forbidden)
    # Guard imports even if an optional provider is already installed/cached.
    original_import = builtins.__import__
    blocked = ("paramiko", "ncclient", "requests", "win32cred", "keyring",
               "validation_framework.stage2_owner_verifier",
               "validation_framework.stage2_authorization_envelope_ledger",
               "validation_framework.stage2_mikrotik_credential_resolver",
               "validation_framework.stage2_windows_credential_backend")

    def guarded_import(name, *args, **kwargs):
        if any(name == prefix or name.startswith(prefix + ".") for prefix in blocked):
            return forbidden(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    # Catch calls through already-imported module references as well.
    for module_name, attributes in (
        ("paramiko", ("SSHClient", "Transport", "HostKeys", "AutoAddPolicy")),
        ("validation_framework.stage2_owner_verifier", ("Stage2OwnerVerifier",)),
        ("validation_framework.stage2_authorization_envelope_ledger", ("Stage2ReplayLedger",)),
        ("validation_framework.stage2_mikrotik_credential_resolver", ("Stage2FixedCredentialResolver",)),
        ("validation_framework.stage2_windows_credential_backend", (
            "Stage2WindowsCredentialBackend", "Stage2CtypesWindowsCredentialApi")),
    ):
        module = sys.modules.get(module_name)
        if module is not None:
            for name in attributes:
                if hasattr(module, name):
                    monkeypatch.setattr(module, name, forbidden)
    yield calls
    assert calls == []


class FakeNative:
    def __init__(self, raw=RAW, *, step=2048, identity=IDENTITY, metadata=(1, 0), fail=None,
                 close_fail=False, open_result=73, read_result=None):
        self.raw = raw
        self.step = step
        self.file_identity = identity
        self.file_metadata = metadata
        self.fail = fail
        self.close_fail = close_fail
        self.open_result = open_result
        self.read_result = read_result
        self.events = []
        self.offset = 0

    def event(self, operation, *args):
        self.events.append((operation, *args))
        if self.fail == operation:
            raise OSError("private rejected path/key/native detail")

    def open_source(self, path):
        self.event("open", path)
        return self.open_result

    def metadata(self, handle):
        self.event("metadata", handle)
        return self.file_metadata

    def identity(self, handle):
        self.event("identity", handle)
        return self.file_identity

    def read(self, handle, maximum):
        self.event("read", handle, maximum)
        if self.read_result is not None:
            return self.read_result
        chunk = self.raw[self.offset:self.offset + min(maximum, self.step)]
        self.offset += len(chunk)
        return chunk

    def close(self, handle):
        self.event("close", handle)
        if self.close_fail:
            raise OSError("private close detail")


def install(monkeypatch, fake):
    monkeypatch.setattr(subject, "_sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(subject, "_Win32KnownHostNative", lambda: fake)
    return fake


def acquire(monkeypatch, raw=RAW, **options):
    fake = install(monkeypatch, FakeNative(raw, **options))
    result = subject.acquire_stage2_known_host_snapshot(configuration(raw))
    return result, fake


def test_exact_public_surface():
    assert set(subject.__all__) == {
        "Stage2KnownHostSourceConfiguration", "Stage2KnownHostSnapshot", "Stage2KnownHostFailure",
        "Stage2KnownHostError", "acquire_stage2_known_host_snapshot"}
    assert {name for name in vars(subject) if not name.startswith("_")} == set(subject.__all__)
    assert tuple(inspect.signature(subject.acquire_stage2_known_host_snapshot).parameters) == ("configuration",)
    assert [f.name for f in dataclasses.fields(subject.Stage2KnownHostSourceConfiguration)] == [
        "expected_path", "expected_file_identity", "expected_file_sha256", "expected_endpoint"]


def test_success_same_handle_order_and_no_execution_authority(monkeypatch):
    result, fake = acquire(monkeypatch)
    assert fake.events == [("open", PATH), ("metadata", 73), ("identity", 73),
                           ("read", 73, 2048), ("read", 73, 2049 - len(RAW)), ("close", 73)]
    assert type(result) is subject.Stage2KnownHostSnapshot
    assert result.schema_version == "s2-ro-07.known-host.v1"
    assert (result.target_ref, result.address, result.port) == (endpoint().target_ref, endpoint().address, 22)
    assert result.host_key_algorithm == "ssh-ed25519"
    assert result.host_key_blob == BLOB
    assert type(result.host_key_blob) is bytes
    assert result.source_file_identity == IDENTITY
    assert result.source_artifact_sha256 == hashlib.sha256(RAW).hexdigest()
    assert result.execution_authorized is False


@pytest.mark.parametrize("value", [None, True, 12, b"c:\\x", [], {}, r"relative\file", r"c:file",
    "c:\\", "c:\\x" + "a" * 1021, r"C:\file", r"c:/file", r"\\server\share\file",
    r"\\?\c:\file", r"\\.\pipe\file", r"c:\a:stream", r"c:\a\..\b", r"c:\.\b",
    r"c:\a\\b", "c:\\a.\\b", "c:\\a \\b", "c:\\b.", "c:\\b ", "c:\\a\nb",
    "c:\\a\x00b", r"c:\a?b", r"c:\a*b", 'c:\\a"b', r"c:\a<b", r"c:\a>b", r"c:\a|b",
    r"c:\con", r"c:\aux.txt", r"c:\prn\file", r"c:\nul", r"c:\com1.log", r"c:\lpt9",
    r"c:\com¹", r"c:\lpt².json", r"c:\conin$", r"c:\conout$", r"c:\con .json",
    "c:\\conın$", "c:\\e\u0301.json"])
def test_invalid_path_before_native(value):
    assert_failure(F.INVALID_CONFIGURATION, lambda: configuration(expected_path=value))


@pytest.mark.parametrize("path", [r"c:\x", PATH, r"d:\synthetic\com10.json", r"c:\synthetic\console",
                                   "c:\\é.json", "c:\\" + "a" * 1021])
def test_canonical_path_acceptance_is_syntax_only(path):
    assert configuration(expected_path=path).expected_path == path


@pytest.mark.parametrize("field,value", [
    ("expected_file_identity", None), ("expected_file_identity", IDENTITY.upper()),
    ("expected_file_identity", IDENTITY + "\n"), ("expected_file_identity", IDENTITY[:-1]),
    ("expected_file_identity", "win32-fileid-v1:" + "0" * 17 + ":" + "0" * 32),
    ("expected_file_identity", IDENTITY.encode()), ("expected_file_identity", 1),
    ("expected_file_sha256", None), ("expected_file_sha256", "A" * 64),
    ("expected_file_sha256", "g" * 64), ("expected_file_sha256", "0" * 63),
    ("expected_file_sha256", "0" * 65), ("expected_file_sha256", "0" * 64 + "\n"),
    ("expected_file_sha256", b"0" * 64), ("expected_file_sha256", True),
])
def test_invalid_pin_before_native(field, value):
    assert_failure(F.INVALID_CONFIGURATION, lambda: configuration(**{field: value}))


@pytest.mark.parametrize("field", ["expected_path", "expected_file_identity", "expected_file_sha256"])
def test_scalar_subclasses_rejected(field):
    class Text(str):
        pass
    assert_failure(F.INVALID_CONFIGURATION,
                   lambda: configuration(**{field: Text(getattr(configuration(), field))}))


@pytest.mark.parametrize("value", [None, {}, True, "target.mikrotik.lab01", object()])
def test_invalid_endpoint(value):
    assert_failure(F.INVALID_TARGET, lambda: configuration(expected_endpoint=value))


def test_endpoint_lookalike_subclass_and_uninitialized():
    class EndpointChild(Stage2FixedTargetEndpoint):
        pass
    variants = [SimpleNamespace(**dataclasses.asdict(endpoint())),
                EndpointChild("target.mikrotik.lab01", "192.0.2.17", 22, "SSH", True),
                object.__new__(Stage2FixedTargetEndpoint)]
    for value in variants:
        assert_failure(F.INVALID_TARGET, lambda: configuration(expected_endpoint=value))


def test_configuration_substitution_rejected_before_attribute_access():
    accesses = []

    class Lookalike:
        @property
        def expected_endpoint(self):
            accesses.append("endpoint")
            return endpoint()

    class Child(subject.Stage2KnownHostSourceConfiguration):
        @property
        def expected_endpoint(self):
            accesses.append("subclass endpoint")
            return endpoint()

    for value in (None, {}, Lookalike(), object.__new__(Child),
                  object.__new__(subject.Stage2KnownHostSourceConfiguration)):
        assert_failure(F.INVALID_CONFIGURATION, lambda: subject.acquire_stage2_known_host_snapshot(value))
    assert accesses == []


def test_configuration_immutable_and_no_override(monkeypatch):
    config = configuration()
    for field in dataclasses.fields(config):
        with pytest.raises((AttributeError, TypeError)):
            setattr(config, field.name, "replacement")
    assert not hasattr(config, "__dict__")
    fake = install(monkeypatch, FakeNative())
    monkeypatch.setenv("KNOWN_HOSTS", "request-selected")
    monkeypatch.setenv("STAGE2_KNOWN_HOST_PATH", "request-selected")
    with pytest.raises(TypeError):
        subject.acquire_stage2_known_host_snapshot(config, expected_path="request-selected")
    subject.acquire_stage2_known_host_snapshot(config)
    assert fake.events[0] == ("open", PATH)


def test_unsupported_platform_before_dll(monkeypatch):
    monkeypatch.setattr(subject, "_sys", SimpleNamespace(platform="linux"))
    assert_failure(F.PLATFORM_UNSUPPORTED, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    with pytest.raises(OSError):
        subject._Win32KnownHostNative()


def test_import_safe_under_native_and_network_sentinels(monkeypatch):
    # Reload a separate module name so existing exact classes are not replaced.
    spec = importlib.util.spec_from_file_location("_synthetic_s2ro07_import", subject.__file__)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    assert module.__all__ == subject.__all__


@pytest.mark.parametrize("operation,code", [("open", F.SOURCE_UNAVAILABLE),
    ("metadata", F.SOURCE_UNAVAILABLE), ("identity", F.SOURCE_UNAVAILABLE),
    ("read", F.SOURCE_READ_FAILED), ("close", F.SOURCE_CLOSE_FAILED)])
@pytest.mark.parametrize("close_fail", [False, True])
def test_native_failures_sanitized_close_once_original_wins(monkeypatch, operation, code, close_fail):
    fake = install(monkeypatch, FakeNative(fail=operation, close_fail=close_fail))
    assert_failure(code, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert sum(e[0] == "open" for e in fake.events) == 1
    assert sum(e[0] == "close" for e in fake.events) == (operation != "open")


@pytest.mark.parametrize("metadata,code", [((0, 0), F.SOURCE_TYPE_REJECTED),
    ((2, 0), F.SOURCE_TYPE_REJECTED), ((3, 0), F.SOURCE_TYPE_REJECTED),
    ((1, 0x10), F.SOURCE_TYPE_REJECTED), ((1, 0x400), F.SOURCE_REPARSE_REJECTED),
    ((1, 0x410), F.SOURCE_TYPE_REJECTED), (None, F.SOURCE_TYPE_REJECTED),
    ([1, 0], F.SOURCE_TYPE_REJECTED), ((True, 0), F.SOURCE_TYPE_REJECTED),
    ((1, False), F.SOURCE_TYPE_REJECTED), ((1, -1), F.SOURCE_TYPE_REJECTED),
    ((1, 2**32), F.SOURCE_TYPE_REJECTED), ((1,), F.SOURCE_TYPE_REJECTED)])
def test_type_and_reparse_rejection_precedes_identity_and_read(monkeypatch, metadata, code):
    fake = install(monkeypatch, FakeNative(metadata=metadata))
    assert_failure(code, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert [e[0] for e in fake.events] == ["open", "metadata", "close"]


@pytest.mark.parametrize("identity", [OTHER_ID, None, True, IDENTITY.upper(), IDENTITY.encode()])
def test_wrong_identity_prevents_read(monkeypatch, identity):
    fake = install(monkeypatch, FakeNative(identity=identity))
    assert_failure(F.SOURCE_IDENTITY_MISMATCH, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert [e[0] for e in fake.events] == ["open", "metadata", "identity", "close"]


@pytest.mark.parametrize("handle", [None, 0, -1, 0xffffffff, 0xffffffffffffffff, True, "73"])
def test_invalid_handle_never_used(monkeypatch, handle):
    fake = install(monkeypatch, FakeNative(open_result=handle))
    assert_failure(F.SOURCE_UNAVAILABLE, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert fake.events == [("open", PATH)]


@pytest.mark.parametrize("step", [1, 3, 17, 2048])
def test_short_reads_accumulated_through_eof(monkeypatch, step):
    result, fake = acquire(monkeypatch, step=step)
    assert result.host_key_blob == BLOB
    assert fake.offset == len(RAW)
    assert fake.events[-1] == ("close", 73)
    assert sum(e[0] == "read" for e in fake.events) == (len(RAW) + step - 1) // step + 1


@pytest.mark.parametrize("raw", [b"", RAW[:-1], RAW[:20], RAW.replace(b"192.0.2.17", b"192.0.2.18")])
def test_changed_or_truncated_source_hash_rejected_before_parse(monkeypatch, raw):
    fake = install(monkeypatch, FakeNative(raw))
    monkeypatch.setattr(subject, "_parse", lambda *args: pytest.fail("hash mismatch reached parser"))
    assert_failure(F.SOURCE_HASH_MISMATCH, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert fake.events[-1] == ("close", 73)


@pytest.mark.parametrize("step", [1, 31, 2048])
def test_exact_2048_reader_boundary_and_eof_probe(step):
    fake = FakeNative(b"x" * 2048, step=step)
    assert subject._read_bounded(fake, 73) == b"x" * 2048
    assert fake.events[-1] == ("read", 73, 1)


@pytest.mark.parametrize("size", [2049, 4096])
def test_overflow_byte_rejected_with_single_close(monkeypatch, size):
    fake = install(monkeypatch, FakeNative(b"x" * size))
    assert_failure(F.SOURCE_TOO_LARGE, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert fake.events[-2:] == [("read", 73, 1), ("close", 73)]
    assert fake.offset == 2049


@pytest.mark.parametrize("bad", [b"x" * 2049, bytearray(b"x"), "x", True, 1, []])
def test_invalid_facade_read_result(monkeypatch, bad):
    fake = install(monkeypatch, FakeNative(read_result=bad))
    assert_failure(F.SOURCE_READ_FAILED, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert fake.events[-1] == ("close", 73)


MALFORMED = [b"", b"\xff", b"\xef\xbb\xbf" + RAW, b"\x00" + RAW, RAW + b"\x00",
    b" " + RAW, RAW + b" ", RAW + b"\n", RAW + b"\r\n", b"[]", b"null", b"true", b"22",
    b"{}", RAW + RAW, b"# comment\n" + RAW, b"// comment\n" + RAW,
    RAW.replace(b'"port":22', b'"port":22,"port":22'),
    json.dumps(record()).encode(), RAW.replace(b'"address"', b'"\\u0061ddress"'),
    RAW.replace(b"192.0.2.17", b"192.0.2.\\u0031\\u0037"),
    RAW.replace(b'"port":22', b'"port":22.0'),
    RAW.replace(b'"port":22', b'"port":2.2e1'),
    RAW.replace(b'"port":22', b'"port":NaN'),
    RAW.replace(b'"port":22', b'"port":Infinity'),
    canonical(record(extra="unknown")), canonical(record(port=True)), canonical(record(port="22")),
    canonical(record(address={"nested": "192.0.2.17"})), canonical([record()]),
    canonical(record(address="é")), canonical(record(host_key_base64=["nested"])),
    b"[" * 1100 + b"]" * 900]


@pytest.mark.parametrize("raw", MALFORMED)
def test_malformed_canonical_source_with_matching_hash(monkeypatch, raw):
    fake = install(monkeypatch, FakeNative(raw))
    assert_failure(F.MALFORMED_SNAPSHOT, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))
    assert fake.events[-1] == ("close", 73)


@pytest.mark.parametrize("field", sorted(record()))
def test_every_missing_field_rejected(monkeypatch, field):
    value = record()
    del value[field]
    raw = canonical(value)
    install(monkeypatch, FakeNative(raw))
    assert_failure(F.MALFORMED_SNAPSHOT, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))


@pytest.mark.parametrize("field", sorted(record()))
@pytest.mark.parametrize("value", [None, {}, []])
def test_every_field_exact_scalar_type(monkeypatch, field, value):
    raw = canonical(record(**{field: value}))
    install(monkeypatch, FakeNative(raw))
    assert_failure(F.MALFORMED_SNAPSHOT, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))


@pytest.mark.parametrize("change,code", [({"schema_version": "s2-ro-07.known-host.v2"}, F.UNSUPPORTED_SCHEMA),
    ({"target_ref": "target.other.lab01"}, F.TARGET_BINDING_MISMATCH),
    ({"address": "192.0.2.18"}, F.TARGET_BINDING_MISMATCH),
    ({"port": 23}, F.TARGET_BINDING_MISMATCH), ({"port": -22}, F.TARGET_BINDING_MISMATCH),
    ({"host_key_algorithm": "ssh-rsa"}, F.UNSUPPORTED_HOST_KEY_ALGORITHM),
    ({"host_key_algorithm": "ecdsa-sha2-nistp256"}, F.UNSUPPORTED_HOST_KEY_ALGORITHM),
    ({"host_key_algorithm": "ssh-ed25519-cert-v01@openssh.com"}, F.UNSUPPORTED_HOST_KEY_ALGORITHM)])
def test_schema_binding_algorithm_categories(monkeypatch, change, code):
    raw = canonical(record(**change))
    install(monkeypatch, FakeNative(raw))
    assert_failure(code, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))


def test_valid_different_endpoint_still_requires_matching_artifact(monkeypatch):
    install(monkeypatch, FakeNative())
    assert_failure(F.TARGET_BINDING_MISMATCH, lambda: subject.acquire_stage2_known_host_snapshot(
        configuration(expected_endpoint=endpoint("192.0.2.18"))))


BAD_BLOBS = [BLOB[:3] + b"\x0a" + BLOB[4:], BLOB[:4] + b"ssh-ed25518" + BLOB[15:],
    BLOB[:18] + b"\x1f" + BLOB[19:], PREFIX + bytes(range(31)), PREFIX + bytes(range(33)),
    BLOB[:-1], BLOB + b"x", BLOB + b"\x00\x00\x00\x00", BLOB[4:], b"", bytes(51)]
BAD_BASE64 = [base64.b64encode(value).decode() for value in BAD_BLOBS] + [
    base64.b64encode(BLOB).decode() + "=", base64.b64encode(BLOB).decode() + "==",
    base64.b64encode(BLOB).decode()[:-1], base64.b64encode(BLOB).decode() + "\n",
    "!" * 68, "=" * 68, " " * 68, "é" * 68,
    base64.urlsafe_b64encode(PREFIX + b"\xff" * 32).decode()]


@pytest.mark.parametrize("encoded", BAD_BASE64)
def test_malformed_key_structure_or_encoding(monkeypatch, encoded):
    raw = canonical(record(host_key_base64=encoded))
    install(monkeypatch, FakeNative(raw))
    expected = F.MALFORMED_HOST_KEY if encoded.isascii() else F.MALFORMED_SNAPSHOT
    assert_failure(expected, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))


def test_known_full_blob_fingerprint_vectors(monkeypatch):
    result, _ = acquire(monkeypatch)
    assert len(BLOB) == 51
    assert len(record()["host_key_base64"]) == 68
    assert BLOB[:4] == (11).to_bytes(4, "big")
    assert BLOB[15:19] == (32).to_bytes(4, "big")
    assert result.host_key_sha256 == "66402c9468c58941dd19ffd650bf2b42f9226f83d3bd06ad515d0e5104a77020"
    assert result.host_key_fingerprint == "SHA256:ZkAslGjFiUHdGf/WUL8rQvkib4PTvQatUV0OUQSncCA"
    assert result.host_key_sha256 != hashlib.sha256(BLOB[19:]).hexdigest()
    assert not result.host_key_fingerprint.endswith("=")


def test_one_bit_change_changes_identity(monkeypatch):
    first, _ = acquire(monkeypatch)
    changed = BLOB[:-1] + bytes([BLOB[-1] ^ 1])
    second, _ = acquire(monkeypatch, canonical(record(host_key_base64=base64.b64encode(changed).decode())))
    assert first.host_key_sha256 != second.host_key_sha256
    assert first.host_key_fingerprint != second.host_key_fingerprint


def test_snapshot_only_retains_exact_immutable_facts(monkeypatch):
    result, _ = acquire(monkeypatch)
    assert {f.name for f in dataclasses.fields(result)} == {
        "schema_version", "target_ref", "address", "port", "host_key_algorithm", "host_key_blob",
        "host_key_sha256", "host_key_fingerprint", "source_file_identity", "source_artifact_sha256",
        "execution_authorized"}
    assert not hasattr(result, "__dict__")
    for field in dataclasses.fields(result):
        assert type(getattr(result, field.name)) in (str, int, bytes, bool)
        with pytest.raises((AttributeError, TypeError)):
            setattr(result, field.name, "replacement")
        with pytest.raises((AttributeError, TypeError)):
            delattr(result, field.name)
    assert PATH not in repr(configuration())
    assert IDENTITY not in repr(configuration())
    assert repr(result) == str(result) == "Stage2KnownHostSnapshot(<host-trust-not-execution-authority>)"


def test_all_supported_snapshot_fabrication_routes_blocked(monkeypatch):
    result, _ = acquire(monkeypatch)
    operations = [lambda: subject.Stage2KnownHostSnapshot(),
        lambda: subject.Stage2KnownHostSnapshot(**dataclasses.asdict(result)),
        lambda: type("Child", (subject.Stage2KnownHostSnapshot,), {}),
        lambda: copy.copy(result), lambda: copy.deepcopy(result),
        lambda: dataclasses.replace(result), lambda: pickle.dumps(result),
        lambda: result.__reduce__(), lambda: result.__reduce_ex__(5),
        lambda: result.__getstate__(), lambda: result.__setstate__(dataclasses.asdict(result)),
        lambda: result.__init__(),
        lambda: object.__new__(subject.Stage2KnownHostSnapshot).__setstate__(dataclasses.asdict(result))]
    for operation in operations:
        with pytest.raises(TypeError):
            operation()
    assert_failure(F.INVALID_CONFIGURATION,
                   lambda: subject.acquire_stage2_known_host_snapshot(object.__new__(subject.Stage2KnownHostSnapshot)))


def test_close_before_only_issuance_site(monkeypatch):
    fake = install(monkeypatch, FakeNative())
    real_object = object
    issued = []

    class ObjectGuard:
        @staticmethod
        def __new__(cls):
            assert fake.events[-1] == ("close", 73)
            issued.append(cls)
            return real_object.__new__(cls)

        __setattr__ = staticmethod(real_object.__setattr__)

    monkeypatch.setattr(subject, "object", ObjectGuard, raising=False)
    subject.acquire_stage2_known_host_snapshot(configuration())
    assert issued == [subject.Stage2KnownHostSnapshot]
    fake.close_fail = True
    fake.offset = 0
    assert_failure(F.SOURCE_CLOSE_FAILED, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert len(issued) == 1


def test_same_open_handle_survives_fake_path_replacement_and_later_mutation(monkeypatch):
    class ReplacementNative(FakeNative):
        def open_source(self, path):
            handle = super().open_source(path)
            self.opened_bytes = self.raw
            return handle

        def metadata(self, handle):
            # Simulate a name now referring elsewhere; the opened object is stable.
            self.raw = b"replacement pathname content"
            return super().metadata(handle)

        def read(self, handle, maximum):
            self.event("read", handle, maximum)
            value = self.opened_bytes[self.offset:self.offset + maximum]
            self.offset += len(value)
            return value

    fake = install(monkeypatch, ReplacementNative())
    result = subject.acquire_stage2_known_host_snapshot(configuration())
    fake.opened_bytes = b"later mutation"
    fake.raw = b"later replacement"
    assert result.host_key_blob == BLOB
    assert result.source_artifact_sha256 == hashlib.sha256(RAW).hexdigest()
    assert sum(e[0] == "open" for e in fake.events) == 1


def test_historical_rollback_limit_is_not_a_freshness_guarantee(monkeypatch):
    historical = RAW
    current = canonical(record(host_key_base64=base64.b64encode(PREFIX + b"\xff" * 32).decode()))
    current_config = configuration(current, expected_file_identity=OTHER_ID)
    install(monkeypatch, FakeNative(historical))
    assert_failure(F.SOURCE_IDENTITY_MISMATCH, lambda: subject.acquire_stage2_known_host_snapshot(current_config))
    install(monkeypatch, FakeNative(historical, identity=OTHER_ID))
    assert_failure(F.SOURCE_HASH_MISMATCH, lambda: subject.acquire_stage2_known_host_snapshot(current_config))
    install(monkeypatch, FakeNative(historical))
    restored = subject.acquire_stage2_known_host_snapshot(configuration(historical))
    assert restored.host_key_blob == BLOB  # Historical pins + artifact accepted: no independent freshness.
    assert restored.execution_authorized is False


class NativeFunction:
    def __init__(self, implementation):
        self.implementation = implementation
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        return self.implementation(*args)


class FakeDLL:
    def __init__(self, failure=None):
        self.events = []
        self.failure = failure
        self.offset = 0
        for name in ("CreateFileW", "GetFileType", "GetFileInformationByHandleEx", "ReadFile", "CloseHandle"):
            setattr(self, name, NativeFunction(getattr(self, "do_" + name)))

    def do_CreateFileW(self, *args):
        self.events.append(("open", *args))
        return None if self.failure == "open" else 73

    def do_GetFileType(self, handle):
        self.events.append(("type", handle))
        return 0 if self.failure == "type" else 1

    def do_GetFileInformationByHandleEx(self, handle, kind, pointer, size):
        self.events.append(("info", handle, kind, size))
        if self.failure == ("info", kind):
            return 0
        if kind == 9:
            assert size == 8
            pointer._obj.attributes = 0
            pointer._obj.tag = 0
        else:
            assert kind == 18 and size == 24
            pointer._obj.volume = 0x0123456789abcdef
            pointer._obj.identifier[:] = bytes(range(16))
        return 1

    def do_ReadFile(self, handle, buffer, maximum, count, overlapped):
        self.events.append(("read", handle, maximum, overlapped))
        assert overlapped is None
        if self.failure == "read":
            return 0
        value = RAW[self.offset:self.offset + maximum]
        self.offset += len(value)
        buffer[:len(value)] = value
        count._obj.value = maximum + 1 if self.failure == "count" else len(value)
        return 1

    def do_CloseHandle(self, handle):
        self.events.append(("close", handle))
        return 0 if self.failure == "close" else 1


def dll_install(monkeypatch, dll):
    monkeypatch.setattr(subject, "_sys", SimpleNamespace(platform="win32"))
    loads = []

    def load(name, **kwargs):
        loads.append((name, kwargs))
        return dll

    monkeypatch.setattr(ctypes, "WinDLL", load, raising=False)
    return loads


def test_actual_private_wrapper_with_fake_dll_exact_flags_abi_and_identity(monkeypatch):
    dll = FakeDLL()
    loads = dll_install(monkeypatch, dll)
    result = subject.acquire_stage2_known_host_snapshot(configuration())
    assert loads == [("kernel32", {"use_last_error": True})]
    assert dll.events[0] == ("open", PATH, 0x80000000, 1, None, 3, 0x00200000, None)
    assert dll.events[0][3] & (2 | 4) == 0  # no share-write/delete
    assert dll.events[-1] == ("close", 73)
    assert result.source_file_identity == IDENTITY
    assert result.host_key_blob == BLOB
    for name, count in (("CreateFileW", 7), ("GetFileType", 1),
                         ("GetFileInformationByHandleEx", 4), ("ReadFile", 5), ("CloseHandle", 1)):
        function = getattr(dll, name)
        assert len(function.argtypes) == count
        assert function.restype is not None


@pytest.mark.parametrize("failure,code", [("open", F.SOURCE_UNAVAILABLE),
    ("type", F.SOURCE_TYPE_REJECTED), (("info", 9), F.SOURCE_UNAVAILABLE),
    (("info", 18), F.SOURCE_UNAVAILABLE), ("read", F.SOURCE_READ_FAILED),
    ("count", F.SOURCE_READ_FAILED), ("close", F.SOURCE_CLOSE_FAILED)])
def test_private_wrapper_native_failures_sanitized(monkeypatch, failure, code):
    dll = FakeDLL(failure)
    dll_install(monkeypatch, dll)
    assert_failure(code, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert sum(e[0] == "close" for e in dll.events) == (failure != "open")


@pytest.mark.parametrize("value", [None, 0, ctypes.c_void_p(-1).value])
def test_private_wrapper_invalid_handles(monkeypatch, value):
    dll = FakeDLL()
    dll.CreateFileW = NativeFunction(lambda *args: value)
    dll_install(monkeypatch, dll)
    assert_failure(F.SOURCE_UNAVAILABLE, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert not dll.events


def test_dll_load_exception_sanitized(monkeypatch):
    monkeypatch.setattr(subject, "_sys", SimpleNamespace(platform="win32"))

    def unavailable(*args, **kwargs):
        raise OSError("private DLL detail")

    monkeypatch.setattr(ctypes, "WinDLL", unavailable)
    assert_failure(F.SOURCE_UNAVAILABLE, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))


def test_source_structure_has_no_extra_capability_or_issuance_helpers():
    tree = ast.parse(inspect.getsource(subject))
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    imports.update(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert imports <= {"__future__", "base64", "dataclasses", "enum", "hashlib", "json", "re", "sys",
                       "unicodedata", "ctypes", "validation_framework.stage2_mikrotik_target_registry"}
    dll_attributes = {node.attr for node in ast.walk(tree)
                      if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                      and node.value.id == "dll"}
    assert dll_attributes == {"CreateFileW", "GetFileType", "GetFileInformationByHandleEx", "ReadFile", "CloseHandle"}
    issuances = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == "__new__"
                 and isinstance(node.func.value, ast.Name) and node.func.value.id == "object"]
    assert len(issuances) == 1
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"open", "eval", "exec", "compile", "__import__"}


def test_error_requires_exact_bounded_category():
    with pytest.raises(TypeError):
        subject.Stage2KnownHostError("source path")


@pytest.mark.parametrize("field", sorted(record()))
def test_every_duplicate_field_rejected(monkeypatch, field):
    duplicate = json.dumps(field).encode() + b":" + json.dumps(record()[field]).encode()
    raw = RAW[:-1] + b"," + duplicate + b"}"
    install(monkeypatch, FakeNative(raw))
    assert_failure(F.MALFORMED_SNAPSHOT, lambda: subject.acquire_stage2_known_host_snapshot(configuration(raw)))


@pytest.mark.parametrize("field,value,code", [
    ("expected_path", "request-path", F.INVALID_CONFIGURATION),
    ("expected_file_identity", "invalid", F.INVALID_CONFIGURATION),
    ("expected_file_sha256", "invalid", F.INVALID_CONFIGURATION),
    ("expected_endpoint", object(), F.INVALID_TARGET),
])
def test_acquisition_revalidates_all_captured_pins_before_native(field, value, code):
    # An uninitialized exact object cannot bypass validation on acquisition.
    incomplete = object.__new__(subject.Stage2KnownHostSourceConfiguration)
    for item in dataclasses.fields(configuration()):
        object.__setattr__(incomplete, item.name, value if item.name == field
                           else getattr(configuration(), item.name))
    assert_failure(code, lambda: subject.acquire_stage2_known_host_snapshot(incomplete))


def test_null_read_return_rejected_and_closed(monkeypatch):
    class NullRead(FakeNative):
        def read(self, handle, maximum):
            self.event("read", handle, maximum)
            return None
    fake = install(monkeypatch, NullRead())
    assert_failure(F.SOURCE_READ_FAILED, lambda: subject.acquire_stage2_known_host_snapshot(configuration()))
    assert fake.events[-1] == ("close", 73)
