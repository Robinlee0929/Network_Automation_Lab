"""Synthetic Ed25519 approvals and fake Win32 only; no real native access."""

import ast
import base64
import builtins
import copy
import ctypes
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import inspect
import json
import pickle
import socket
import subprocess
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from validation_framework import stage2_owner_verifier as m
from validation_framework import stage2_live_authorization_owner_trust_root as tr
from validation_framework import stage2_authorization_envelope_ledger as env
from validation_framework import stage2_mikrotik_credential_resolver as cr
from validation_framework import stage2_windows_credential_backend as wb

DIRECTORY = r"c:\synthetic-owner\approvals"
IDENTITY = "win32-fileid-v1:0000000000000001:" + "02" * 16
ISSUER = "issuer.synthetic.owner"
REF = "authorization.synthetic"
NATIVE_CLASS = m._Win32ApprovalNative


def canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def envelope():
    return env.Stage2AuthorizationEnvelope("1.0", "12345678-1234-4234-8234-123456789abc",
        "mikrotik.vrrp_status", "a" * 64, REF, "target.mikrotik.lab01", "credential.mikrotik.lab01", 1000, 1300, 1)


def record(signature=b"\0" * 64):
    return dict(schema_version=m.APPROVAL_SCHEMA_VERSION, issuer_ref=ISSUER,
        signature_algorithm="Ed25519", signature_base64=base64.b64encode(signature).decode())


def deny(*args, **kwargs):
    pytest.fail("forbidden native or downstream capability reached")


@pytest.fixture(autouse=True)
def no_real_dll(monkeypatch):
    monkeypatch.setattr(ctypes, "WinDLL", deny, raising=False)


class TrustNative:
    def __init__(self, raw): self.raw, self.offset = raw, 0
    def open_read_only(self, path): return 1
    def file_type(self, handle): return 1
    def attribute_flags(self, handle): return 0
    def file_identity_parts(self, handle): return 1, b"\2" * 16
    def close(self, handle): pass
    def read(self, handle, maximum):
        result = self.raw[self.offset:self.offset + maximum]
        self.offset += len(result)
        return result


def acquire(monkeypatch, key, **changes):
    data = dict(schema_version="1.0", ed25519_public_key_base64=base64.b64encode(
        key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode(), issuer_ref=ISSUER,
        lab_only_attestation_ref="attestation.synthetic.lab", approval_source_id="source.synthetic.owner",
        approval_source_absolute_path=DIRECTORY, approval_source_directory_identity=IDENTITY)
    data.update(changes)
    raw = canonical(data)
    monkeypatch.setattr(tr, "_Win32TrustRootNative", lambda: TrustNative(raw))
    return tr.acquire_owner_trust_root_configuration(expected_path=r"c:\synthetic-owner\root.json",
        expected_file_identity=IDENTITY, expected_file_sha256=hashlib.sha256(raw).hexdigest())


class Native:
    def __init__(self, raw):
        self.raw, self.offset, self.chunk_size, self.fault = raw, 0, 2048, None
        self.calls, self.directory_metadata, self.file_metadata = [], (1, 0x10), (1, 0)
        self.identity = IDENTITY
    def event(self, name, *args):
        self.calls.append((name, *args))
        if self.fault == name: raise OSError("synthetic-sensitive-native-detail")
    def open_directory(self, path):
        self.event("open_directory", path)
        return 10
    def open_artifact(self, path):
        self.event("open_artifact", path)
        return 20
    def metadata(self, handle):
        self.event("directory_metadata" if handle == 10 else "file_metadata", handle)
        return self.directory_metadata if handle == 10 else self.file_metadata
    def directory_identity(self, handle):
        self.event("identity", handle)
        return self.identity
    def read(self, handle, maximum):
        self.event("read", handle, maximum)
        if self.fault == "partial_read" and self.offset: raise OSError("synthetic-read-detail")
        chunk = self.raw[self.offset:self.offset + min(maximum, self.chunk_size)]
        self.offset += len(chunk)
        return chunk
    def close(self, handle):
        self.event("close_artifact" if handle == 20 else "close_directory", handle)


@pytest.fixture
def setup(monkeypatch):
    key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))  # synthetic test seed only
    root = acquire(monkeypatch, key)
    native = Native(canonical(record(key.sign(env.owner_verification_payload(envelope())))))
    monkeypatch.setattr(m, "_Win32ApprovalNative", lambda: native)
    return key, root, native


def rejection(code, operation, *args):
    with pytest.raises(m.Stage2OwnerVerificationError) as caught: operation(*args)
    assert caught.value.code.value == code
    assert str(caught.value) == code
    assert caught.value.__context__ is None and caught.value.__cause__ is None


def test_canonical_roundtrip_no_authority():
    raw = canonical(record())
    parsed = m.parse_stage2_owner_approval(raw)
    assert parsed.to_canonical_bytes() == raw
    assert {f.name for f in fields(parsed)} == set(record())
    assert not hasattr(parsed, "verified") and ISSUER not in repr(parsed)
    with pytest.raises(FrozenInstanceError): parsed.issuer_ref = "issuer.changed"


@pytest.mark.parametrize("raw", [b"", b"\xff", b"{}", b"[]", b"null", b"NaN", b"Infinity",
    b"{" * 300, "{}", bytearray(b"{}"), b"x" * 2049])
def test_malformed_raw(raw):
    rejection("MALFORMED_ARTIFACT", m.parse_stage2_owner_approval, raw)


@pytest.mark.parametrize("variant", ["leading", "trailing", "newline", "bom", "pretty", "order", "escape"])
def test_noncanonical(variant):
    raw = canonical(record())
    variants = {"leading": b" " + raw, "trailing": raw + b" ", "newline": raw + b"\n",
        "bom": b"\xef\xbb\xbf" + raw, "pretty": json.dumps(record(), indent=2).encode(),
        "order": json.dumps(record(), separators=(",", ":")).encode(),
        "escape": raw.replace(b"issuer.synthetic", b"issuer.\\u0073ynthetic")}
    rejection("MALFORMED_ARTIFACT", m.parse_stage2_owner_approval, variants[variant])


@pytest.mark.parametrize("field", list(record()))
@pytest.mark.parametrize("value", [None, 1, True, {}, [], "é"])
def test_wrong_field_types(field, value):
    rejection("MALFORMED_ARTIFACT", m.parse_stage2_owner_approval, canonical({**record(), field: value}))


@pytest.mark.parametrize("field", list(record()))
def test_missing_and_duplicate_each_field(field):
    data = record()
    del data[field]
    rejection("MALFORMED_ARTIFACT", m.parse_stage2_owner_approval, canonical(data))
    raw = canonical(record())[:-1] + b"," + canonical({field: record()[field]})[1:]
    rejection("MALFORMED_ARTIFACT", m.parse_stage2_owner_approval, raw)


@pytest.mark.parametrize("field,value,code", [("unknown", "x", "MALFORMED_ARTIFACT"),
    ("schema_version", "1.0", "UNSUPPORTED_SCHEMA"), ("signature_algorithm", "RSA", "UNSUPPORTED_ALGORITHM"),
    ("signature_algorithm", "ed25519", "UNSUPPORTED_ALGORITHM"), ("issuer_ref", "Issuer.owner", "MALFORMED_ARTIFACT"),
    ("issuer_ref", "issuer", "MALFORMED_ARTIFACT"), ("issuer_ref", "issuer." + "a" * 154, "MALFORMED_ARTIFACT"),
    ("issuer_ref", "issuer.owner\n", "MALFORMED_ARTIFACT")])
def test_exact_fields(field, value, code):
    rejection(code, m.parse_stage2_owner_approval, canonical({**record(), field: value}))


@pytest.mark.parametrize("signature", ["!" * 86 + "==", "_" * 86 + "==", "-" * 86 + "==",
    "A" * 87 + "=", "A" * 86, "A" * 85 + "B==", "A" * 86 + "==\n",
    base64.b64encode(b"x" * 63).decode(), base64.b64encode(b"x" * 65).decode()])
def test_signature_encoding(signature):
    rejection("MALFORMED_SIGNATURE", m.parse_stage2_owner_approval, canonical({**record(), "signature_base64": signature}))


def test_success_exact_payload_once(setup, monkeypatch):
    _, root, native = setup
    calls, original = [], m.owner_verification_payload
    def payload(value):
        calls.append(value)
        return original(value)
    monkeypatch.setattr(m, "owner_verification_payload", payload)
    result = m.Stage2OwnerVerifier(root).verify(envelope())
    assert calls == [envelope()]
    assert type(result) is m.Stage2VerifiedOwnerApproval
    assert result.verified is True and result.execution_authorized is False
    assert result.payload_sha256 == hashlib.sha256(original(envelope())).hexdigest()
    assert result.artifact_sha256 == hashlib.sha256(native.raw).hexdigest()
    assert result.approval_ref == REF and result.verified_issuer_ref == ISSUER
    assert result.approval_source_id == root.approval_source_id
    assert result.public_key_fingerprint == root.public_key_sha256_fingerprint
    assert native.calls[0] == ("open_directory", DIRECTORY)
    assert native.calls[3] == ("open_artifact", DIRECTORY + "\\" + REF + ".json")
    assert native.calls[-2:] == [("close_artifact", 20), ("close_directory", 10)]


@pytest.mark.parametrize("changes", [dict(request_sha256="b" * 64),
    dict(authorization_id="22345678-1234-4234-8234-123456789abc"), dict(authorization_ref="authorization.other"),
    dict(issued_at=1001), dict(expires_at=1299)])
def test_changed_valid_envelope(setup, changes):
    rejection("SIGNATURE_INVALID", m.Stage2OwnerVerifier(setup[1]).verify, replace(envelope(), **changes))


@pytest.mark.parametrize("variant", ["bit", "json_only", "wrong_domain", "digest", "equivalent"])
def test_wrong_signed_bytes(setup, variant):
    key, root, native = setup
    payload = env.owner_verification_payload(envelope())
    variants = {"bit": bytes([payload[0] ^ 1]) + payload[1:], "json_only": envelope().to_canonical_bytes(),
        "wrong_domain": b"other\0" + payload, "digest": hashlib.sha256(payload).digest(),
        "equivalent": env.OWNER_PAYLOAD_DOMAIN + json.dumps(envelope().to_dict(), indent=2).encode()}
    native.raw = canonical(record(key.sign(variants[variant])))
    rejection("SIGNATURE_INVALID", m.Stage2OwnerVerifier(root).verify, envelope())


@pytest.mark.parametrize("field,value", [("target_ref", "target.other"), ("credential_ref", "credential.other")])
def test_fixed_binding_rejected_by_prior_contract(setup, field, value):
    with pytest.raises(env.Stage2AuthorizationError): replace(envelope(), **{field: value})
    assert setup[2].calls == []


def test_wrong_acquired_key_and_random_signature(setup, monkeypatch):
    _, root, native = setup
    wrong = acquire(monkeypatch, Ed25519PrivateKey.from_private_bytes(b"\xff" * 32))
    rejection("SIGNATURE_INVALID", m.Stage2OwnerVerifier(wrong).verify, envelope())
    native.offset, native.raw = 0, canonical(record(bytes(range(64))))
    rejection("SIGNATURE_INVALID", m.Stage2OwnerVerifier(root).verify, envelope())


def test_wrong_issuer_before_crypto(setup, monkeypatch):
    _, root, native = setup
    native.raw = canonical({**record(), "issuer_ref": "issuer.other"})
    monkeypatch.setattr(m, "_verification_key", deny)
    monkeypatch.setattr(m, "owner_verification_payload", deny)
    monkeypatch.setattr(m, "_signature_bytes", deny)
    rejection("UNKNOWN_ISSUER", m.Stage2OwnerVerifier(root).verify, envelope())


@pytest.mark.parametrize("constructor", [m.Stage2OwnerVerifier, m.Stage2ExactOwnerApprovalSource])
def test_no_key_or_source_substitution(setup, constructor):
    _, root, native = setup
    for value in (b"a" * 32, {}, object(), type("Lookalike", (), {"issuer_ref": ISSUER})()):
        rejection("INVALID_CONFIGURATION", constructor, value)
    for name in ("pinned_public_key", "public_key", "approval_source", "path", "key_callback"):
        with pytest.raises(TypeError): constructor(root, **{name: object()})
    instance = constructor(root)
    with pytest.raises(FrozenInstanceError): instance.trust_root = object()
    assert native.calls == []


@pytest.mark.parametrize("ref", [None, "approval.other", "authorization.A", "authorization.a/b",
    "authorization..a", "authorization.a\\b", "authorization.a:stream", "authorization.a*",
    "authorization.a ", "authorization.a\n", "authorization." + "a" * 147])
def test_invalid_ref_before_native(setup, ref, monkeypatch):
    monkeypatch.setattr(m, "_Win32ApprovalNative", deny)
    rejection("INVALID_ENVELOPE", m.Stage2ExactOwnerApprovalSource(setup[1]).read_exact, ref)


def test_invalid_envelope_before_native(setup, monkeypatch):
    monkeypatch.setattr(m, "_Win32ApprovalNative", deny)
    for value in (None, {}, object(), object.__new__(env.Stage2AuthorizationEnvelope)):
        rejection("INVALID_ENVELOPE", m.Stage2OwnerVerifier(setup[1]).verify, value)


@pytest.mark.parametrize("where,metadata", [("directory", (1, 0)), ("directory", (1, 0x410)),
    ("directory", (2, 0x10)), ("file", (1, 0x10)), ("file", (1, 0x400)), ("file", (2, 0)),
    ("file", (0, 0)), ("file", (True, 0)), ("file", None)])
def test_wrong_source_types(setup, where, metadata):
    _, root, native = setup
    setattr(native, "directory_metadata" if where == "directory" else "file_metadata", metadata)
    rejection("SOURCE_TYPE_REJECTED", m.Stage2ExactOwnerApprovalSource(root).read_exact, REF)
    assert native.calls[-1] == ("close_directory", 10)
    if where == "directory": assert not any(c[0] == "open_artifact" for c in native.calls)
    else: assert native.calls[-2] == ("close_artifact", 20)


def test_wrong_directory_identity(setup):
    _, root, native = setup
    native.identity = IDENTITY + "0"
    rejection("SOURCE_IDENTITY_MISMATCH", m.Stage2ExactOwnerApprovalSource(root).read_exact, REF)
    assert not any(c[0] == "open_artifact" for c in native.calls)


@pytest.mark.parametrize("fault,code", [("open_directory", "SOURCE_UNAVAILABLE"), ("open_artifact", "SOURCE_UNAVAILABLE"),
    ("directory_metadata", "SOURCE_UNAVAILABLE"), ("file_metadata", "SOURCE_UNAVAILABLE"), ("identity", "SOURCE_UNAVAILABLE"),
    ("read", "SOURCE_READ_FAILED"), ("partial_read", "SOURCE_READ_FAILED"),
    ("close_artifact", "SOURCE_CLOSE_FAILED"), ("close_directory", "SOURCE_CLOSE_FAILED")])
def test_failures_close_once_no_retry(setup, fault, code):
    _, root, native = setup
    native.fault, native.chunk_size = fault, 10
    rejection(code, m.Stage2ExactOwnerApprovalSource(root).read_exact, REF)
    names = [c[0] for c in native.calls]
    assert names.count("open_directory") == 1 and names.count("open_artifact") <= 1
    assert names.count("close_directory") == (0 if fault == "open_directory" else 1)
    assert names.count("close_artifact") == (1 if "file_metadata" in names else 0)


@pytest.mark.parametrize("size", [0, 1, 2047, 2048, 2049])
def test_bounded_read_eof(setup, size):
    _, root, native = setup
    native.raw = b"x" * size
    source = m.Stage2ExactOwnerApprovalSource(root)
    if size > 2048: rejection("SOURCE_TOO_LARGE", source.read_exact, REF)
    else: assert source.read_exact(REF) == native.raw
    reads = [c for c in native.calls if c[0] == "read"]
    assert all(c[1] == 20 and 1 <= c[2] <= 2048 for c in reads)
    if size >= 2048: assert reads[-1] == ("read", 20, 1)


def test_one_byte_short_reads(setup):
    _, root, native = setup
    native.chunk_size = 1
    assert m.Stage2ExactOwnerApprovalSource(root).read_exact(REF) == native.raw


@pytest.mark.parametrize("bad", [None, bytearray(b"x"), "x", b"x" * 2049])
def test_bad_native_read(setup, bad, monkeypatch):
    _, root, native = setup
    monkeypatch.setattr(native, "read", lambda *args: bad)
    rejection("SOURCE_READ_FAILED", m.Stage2ExactOwnerApprovalSource(root).read_exact, REF)
    assert native.calls[-2:] == [("close_artifact", 20), ("close_directory", 10)]


def test_result_authority_and_repr(setup):
    _, root, native = setup
    result = m.Stage2OwnerVerifier(root).verify(envelope())
    operations = [lambda: m.Stage2VerifiedOwnerApproval(),
        lambda: m.Stage2VerifiedOwnerApproval.__new__(m.Stage2VerifiedOwnerApproval),
        lambda: type("Forged", (m.Stage2VerifiedOwnerApproval,), {}), lambda: copy.copy(result),
        lambda: copy.deepcopy(result), lambda: replace(result, verified=True),
        lambda: pickle.dumps(result), lambda: result.__getstate__()]
    for operation in operations:
        with pytest.raises(TypeError): operation()
    with pytest.raises(FrozenInstanceError): result.verified = False
    assert not hasattr(result, "__dict__")
    assert {f.name for f in fields(result)} == {"schema_version", "artifact_sha256", "approval_ref",
        "verified_issuer_ref", "approval_source_id", "public_key_fingerprint", "payload_sha256", "verified", "execution_authorized"}
    for value in (REF, ISSUER, DIRECTORY, native.raw.decode(), record()["signature_base64"]):
        assert value not in repr(result)


def test_crypto_unavailable(setup, monkeypatch):
    def unavailable(*args): raise RuntimeError("synthetic-sensitive-crypto-detail")
    monkeypatch.setattr(m, "_verification_key", unavailable)
    rejection("CRYPTO_UNAVAILABLE", m.Stage2OwnerVerifier(setup[1]).verify, envelope())


@pytest.mark.parametrize("valid", [True, False])
def test_no_downstream_execution(setup, monkeypatch, valid):
    _, root, native = setup
    monkeypatch.setattr(env.Stage2ReplayLedger, "consume", deny)
    monkeypatch.setattr(cr.Stage2FixedCredentialResolver, "resolve", deny)
    monkeypatch.setattr(wb.Stage2WindowsCredentialBackend, "read", deny)
    monkeypatch.setattr(wb.Stage2CtypesWindowsCredentialApi, "read_exact", deny)
    for name in ("socket", "getaddrinfo", "create_connection"): monkeypatch.setattr(socket, name, deny)
    monkeypatch.setattr(subprocess, "Popen", deny)
    original_import = builtins.__import__
    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.split(".")[0] in {"paramiko", "ncclient", "requests", "dns"}:
            deny()
        if "Ed25519PrivateKey" in fromlist:
            deny()
        return original_import(name, globals, locals, fromlist, level)
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    if valid: assert m.Stage2OwnerVerifier(root).verify(envelope()).verified
    else:
        native.raw = canonical(record())
        rejection("SIGNATURE_INVALID", m.Stage2OwnerVerifier(root).verify, envelope())


class Function:
    def __init__(self, implementation): self.implementation = implementation
    def __call__(self, *args): return self.implementation(*args)


@pytest.mark.parametrize("fault,code", [(None, None), ("directory_open", "SOURCE_UNAVAILABLE"),
    ("file_open", "SOURCE_UNAVAILABLE"), ("directory_metadata", "SOURCE_UNAVAILABLE"),
    ("identity", "SOURCE_UNAVAILABLE"), ("file_metadata", "SOURCE_UNAVAILABLE"),
    ("read", "SOURCE_READ_FAILED"), ("count", "SOURCE_READ_FAILED"),
    ("file_close", "SOURCE_CLOSE_FAILED"), ("directory_close", "SOURCE_CLOSE_FAILED")])
def test_ctypes_marshaling_with_fake_dll(setup, monkeypatch, fault, code):
    _, root, native = setup
    calls, offset, closed = [], [0], []
    def create(path, access, share, security, disposition, flags, template):
        calls.append((path, access, share, security, disposition, flags, template))
        if (path == DIRECTORY and fault == "directory_open") or (path != DIRECTORY and fault == "file_open"):
            return ctypes.c_void_p(-1).value
        return 10 if path == DIRECTORY else 20
    def info(handle, kind, pointer, size):
        if ((fault == "identity" and kind == 18)
                or (fault == "directory_metadata" and handle == 10 and kind == 9)
                or (fault == "file_metadata" and handle == 20 and kind == 9)):
            return 0
        value = pointer._obj
        if kind == 9: value.attributes = 0x10 if handle == 10 else 0
        elif kind == 18:
            value.volume = 1
            value.identifier[:] = b"\2" * 16
        else: pytest.fail("unexpected metadata capability")
        return 1
    def read(handle, buffer, maximum, count, overlapped):
        assert handle == 20 and overlapped is None
        if fault == "read": return 0
        chunk = native.raw[offset[0]:offset[0] + maximum]
        offset[0] += len(chunk)
        ctypes.memmove(buffer, chunk, len(chunk))
        count._obj.value = maximum + 1 if fault == "count" else len(chunk)
        return 1
    def close(handle):
        closed.append(handle)
        return 0 if (handle == 20 and fault == "file_close") or (handle == 10 and fault == "directory_close") else 1
    class Dll:
        CreateFileW = Function(create)
        GetFileType = Function(lambda handle: 1)
        GetFileInformationByHandleEx = Function(info)
        ReadFile = Function(read)
        CloseHandle = Function(close)
    monkeypatch.setattr(m, "_Win32ApprovalNative", NATIVE_CLASS)
    monkeypatch.setattr(m.sys, "platform", "win32")
    monkeypatch.setattr(ctypes, "WinDLL", lambda name, **kwargs: Dll())
    if code: rejection(code, m.Stage2OwnerVerifier(root).verify, envelope())
    else: assert m.Stage2OwnerVerifier(root).verify(envelope()).verified
    expected = [(DIRECTORY, 0, 1, None, 3, 0x02200000, None),
        (DIRECTORY + "\\" + REF + ".json", 0x80000000, 1, None, 3, 0x00200000, None)]
    assert calls == expected[:len(calls)]
    if fault == "directory_open": assert closed == []
    elif fault in {"file_open", "directory_metadata", "identity"}: assert closed == [10]
    else: assert closed == [20, 10]


def test_exact_maximum_path_and_reference(setup, monkeypatch):
    key, _, native = setup
    directory = "c:\\" + "d" * 1021
    root = acquire(monkeypatch, key, approval_source_absolute_path=directory)
    ref = "authorization." + "a" * 146
    assert len(ref) == 160
    assert m.Stage2ExactOwnerApprovalSource(root).read_exact(ref) == native.raw
    path = next(c[1] for c in native.calls if c[0] == "open_artifact")
    assert len(path) == 1190 and path == directory + "\\" + ref + ".json"


def test_import_safe_without_native_loading(monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("synthetic_owner_import", m.__file__)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(m.sys.modules, spec.name, module)
    monkeypatch.setattr(m.sys, "platform", "unsupported")
    spec.loader.exec_module(module)
    assert module.SIGNATURE_ALGORITHM == "Ed25519"


def test_source_is_repeatable_data_not_authority(setup):
    _, root, native = setup
    source = m.Stage2ExactOwnerApprovalSource(root)
    raw = source.read_exact(REF)
    assert type(raw) is bytes and not isinstance(raw, m.Stage2VerifiedOwnerApproval)
    native.offset = 0
    assert source.read_exact(REF) == raw
    assert native.raw == raw


def test_cleanup_error_preserves_original_failure_and_closes_both(setup, monkeypatch):
    _, root, native = setup
    native.fault = "read"
    def close(handle):
        native.calls.append(("close", handle))
        raise OSError("synthetic-close-detail")
    monkeypatch.setattr(native, "close", close)
    rejection("SOURCE_READ_FAILED", m.Stage2ExactOwnerApprovalSource(root).read_exact, REF)
    assert native.calls[-2:] == [("close", 20), ("close", 10)]


@pytest.mark.parametrize("base,method,argument", [
    (m.Stage2OwnerVerifier, m.Stage2OwnerVerifier.verify, envelope()),
    (m.Stage2ExactOwnerApprovalSource, m.Stage2ExactOwnerApprovalSource.read_exact, REF),
])
@pytest.mark.parametrize("subclass", [False, True])
def test_public_receiver_cannot_substitute_authority(setup, base, method, argument, subclass):
    _, root, native = setup
    attacker = Ed25519PrivateKey.from_private_bytes(b"\xfe" * 32)
    native.raw = canonical(record(attacker.sign(env.owner_verification_payload(envelope()))))
    substitutions = SimpleNamespace(
        ed25519_public_key=attacker.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw),
        approval_source_absolute_path=r"c:\synthetic-other\approvals",
        approval_source_directory_identity=IDENTITY)
    reads = []
    def changing_root(self):
        reads.append(1)
        # The old verifier used access 4 for its key; the old source used
        # accesses 2 and 3 for the unchecked directory path and identity.
        if base is m.Stage2OwnerVerifier and len(reads) == 4:
            return substitutions
        if base is m.Stage2ExactOwnerApprovalSource and len(reads) >= 2:
            return substitutions
        return root
    receiver_type = type("ChangingReceiver", (base if subclass else object,), {
        "__init__": lambda self: None, "trust_root": property(changing_root)})
    rejection("INVALID_CONFIGURATION", method, receiver_type(), argument)
    assert reads == [] and native.calls == []


def test_unsupported_platform_before_dll(setup, monkeypatch):
    monkeypatch.setattr(m, "_Win32ApprovalNative", NATIVE_CLASS)
    monkeypatch.setattr(m.sys, "platform", "unsupported")
    rejection("SOURCE_UNAVAILABLE", m.Stage2ExactOwnerApprovalSource(setup[1]).read_exact, REF)


def test_no_production_signer_network_discovery_or_runtime():
    source = inspect.getsource(m)
    tree = ast.parse(source)
    imports = {a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
    assert not imports & {"socket", "paramiko", "subprocess", "requests", "Ed25519PrivateKey"}
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert not calls & {"sign", "generate", "consume", "resolve", "glob", "iterdir", "listdir", "scandir",
        "walk", "getenv", "expanduser", "expandvars", "write", "unlink"}
    for name in ("CredReadW", "WriteFile", "FindFirstFile", "FindNextFile", "AdjustTokenPrivileges",
        "CreateProcess", "DeleteFile", "MoveFile", "OWNER_PAYLOAD_DOMAIN"):
        assert name not in source
    assert set(m.__all__) == {"APPROVAL_SCHEMA_VERSION", "SIGNATURE_ALGORITHM", "MAX_APPROVAL_ARTIFACT_BYTES",
        "MAX_APPROVAL_PATH_CHARACTERS", "Stage2OwnerVerificationFailure", "Stage2OwnerVerificationError",
        "Stage2OwnerApprovalArtifact", "parse_stage2_owner_approval", "Stage2ExactOwnerApprovalSource",
        "Stage2OwnerVerifier", "Stage2VerifiedOwnerApproval"}
