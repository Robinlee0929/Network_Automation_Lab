"""Synthetic offline composition tests; no trust files, credentials or sockets."""

import ast
import base64
from dataclasses import fields, FrozenInstanceError, replace
import hashlib
import inspect
from pathlib import Path
import socket
import sqlite3
from types import SimpleNamespace

import pytest

from validation_framework import stage2_trusted_runtime_composition as m

F = m.Stage2TrustedRuntimeFailure
AUTH_ID = "12345678-1234-4234-8234-123456789abc"
INSTANCE = "22345678-1234-4234-8234-123456789abc"
IDENTITY = "win32-fileid-v1:" + "1" * 16 + ":" + "2" * 32
RAW = b'0 RM name="synthetic-vrrp" vrid=1 priority=100 interval=1s version=3\r\n'
SENTINEL = "synthetic-secret-output-path-signature-key"
REAL_LEDGER = m._authorization.Stage2ReplayLedger
REAL_PARSE = m._parser.parse_stage2_vrrp_readonly_output
REAL_POLICY = m._policy.resolve_stage2_vrrp_readonly_command
REAL_EVIDENCE = m._contract.Stage2VrrpObservationEvidence


def issue(kind, **values):
    obj = object.__new__(kind)
    for name, value in values.items():
        object.__setattr__(obj, name, value)
    return obj


def drift(obj, name, value):
    return issue(type(obj), **{f.name: value if f.name == name else getattr(obj, f.name)
                              for f in fields(obj)})


def deny(*args, **kwargs):
    raise AssertionError("real acquisition/network forbidden")


@pytest.fixture(autouse=True)
def no_external(monkeypatch):
    monkeypatch.setattr(socket, "socket", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    monkeypatch.setattr(m._root, "_Win32TrustRootNative", deny)
    monkeypatch.setattr(m._owner, "_Win32ApprovalNative", deny)
    monkeypatch.setattr(m._host, "_Win32KnownHostNative", deny, raising=False)
    monkeypatch.setattr(m._windows, "_read_windows_credential_exact", deny)
    monkeypatch.setattr(m._transport, "_Stage2PinnedTransport", deny)


@pytest.fixture
def setup(monkeypatch, tmp_path):
    request = m._contract.Stage2VrrpObservationRequest(
        "1.0", "mikrotik.vrrp_status", "run.synthetic", "target.mikrotik.lab01",
        "credential.mikrotik.lab01", "authorization.synthetic", True)
    endpoint = m._target.Stage2FixedTargetEndpoint(request.target_ref, "192.0.2.10", 22, "SSH", True)
    config = m.Stage2TrustedRuntimeConfiguration(
        m._target.Stage2FixedTargetRegistry(endpoint), r"c:\synthetic\root.json", IDENTITY, "a" * 64,
        m._authorization.Stage2ReplayLedgerConfiguration(
            tmp_path / "synthetic.db", INSTANCE, (Path(__file__).resolve().parents[2],)),
        m._host.Stage2KnownHostSourceConfiguration(r"c:\synthetic\host.json", IDENTITY, "b" * 64, endpoint),
        m._windows.Stage2TrustedWindowsCredentialConfiguration(
            m._resolver.STAGE2_CREDENTIAL_LOCATOR_REF, "synthetic-only-target"))
    envelope = m._authorization.Stage2AuthorizationEnvelope(
        "1.0", AUTH_ID, request.operation_id, hashlib.sha256(request.to_canonical_bytes()).hexdigest(),
        request.authorization_ref, request.target_ref, request.credential_ref, 1000, 1300, 1)
    root = issue(m._root.OwnerTrustRootConfiguration, schema_version="1.0",
        ed25519_public_key=b"r" * 32, issuer_ref="issuer.synthetic", lab_only_attestation_ref="attestation.synthetic",
        approval_source_id="source.synthetic", approval_source_absolute_path=r"c:\synthetic\approvals",
        approval_source_directory_identity=IDENTITY, public_key_sha256_fingerprint=hashlib.sha256(b"r" * 32).hexdigest(),
        trust_root_source_file_identity=IDENTITY, trust_root_source_file_sha256="a" * 64)
    verification = issue(m._owner.Stage2VerifiedOwnerApproval,
        schema_version=m._owner.APPROVAL_SCHEMA_VERSION, artifact_sha256="c" * 64,
        approval_ref=request.authorization_ref, verified_issuer_ref=root.issuer_ref,
        approval_source_id=root.approval_source_id, public_key_fingerprint=root.public_key_sha256_fingerprint,
        payload_sha256=hashlib.sha256(m._authorization.owner_verification_payload(envelope)).hexdigest(),
        verified=True, execution_authorized=False)
    blob = b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20" + b"h" * 32
    digest = hashlib.sha256(blob).digest()
    snapshot = issue(m._host.Stage2KnownHostSnapshot, schema_version="s2-ro-07.known-host.v1",
        target_ref=request.target_ref, address=endpoint.address, port=22, host_key_algorithm="ssh-ed25519",
        host_key_blob=blob, host_key_sha256=digest.hex(),
        host_key_fingerprint="SHA256:" + base64.b64encode(digest).decode().rstrip("="),
        source_file_identity=IDENTITY, source_artifact_sha256="b" * 64, execution_authorized=False)
    consumed = m._authorization.Stage2ConsumptionRecord(
        AUTH_ID, hashlib.sha256(envelope.to_canonical_bytes()).hexdigest(), 1100)
    s = SimpleNamespace(request=request, config=config, envelope=envelope, root=root,
        verification=verification, snapshot=snapshot, consumed=consumed,
        credential=m._windows.Stage2ResolvedCredential("synthetic-user", SENTINEL.encode()),
        command=REAL_POLICY(request), raw=RAW, trace=[], fail={}, returns={}, spent=False,
        parser_input=None, transport_inputs=None, credential_released=[], evidence_fields=None)

    def step(name, value):
        s.trace.append(name)
        if name in s.fail:
            raise s.fail[name]
        return s.returns.get(name, value)

    def acquire_root(**pins):
        assert pins == dict(expected_path=config.owner_trust_root_expected_path,
                            expected_file_identity=IDENTITY, expected_file_sha256="a" * 64)
        return step("root", s.root)

    class Verifier:
        def __init__(self, value):
            assert value is s.root
            step("verifier", None)

        def verify(self, value):
            assert value == s.envelope
            return step("verify", s.verification)

    class Ledger:
        def __init__(self, value):
            assert value == config.replay_ledger_configuration
            step("ledger", None)

        def consume(self, e, r, registry, binding, *, utc_now):
            assert e == s.envelope and r == s.request and registry == s.config.target_registry
            assert binding == m._resolver.build_stage2_fixed_credential_resolver().resolve(r.credential_ref)
            assert utc_now is m._utc_now
            value = step("consume", s.consumed)
            if s.spent:
                raise m._authorization.Stage2AuthorizationError(m._authorization.Stage2AuthorizationFailure.REPLAY)
            s.spent = True
            return value

    def host(value):
        assert value.expected_path == r"c:\synthetic\host.json"
        assert value.expected_file_identity == IDENTITY and value.expected_file_sha256 == "b" * 64
        assert value.expected_endpoint.address == "192.0.2.10"
        return step("host", s.snapshot)

    class Backend:
        def read(self, binding):
            assert binding.credential_ref == request.credential_ref
            return step("credential", s.credential)

    def backend(value):
        assert value == config.credential_configuration
        step("backend", None)
        return Backend()

    def command(value):
        assert value == s.request
        return step("command", s.command)

    def result():
        return issue(m._transport.Stage2PinnedSshCommandResult,
            schema_version="s2-ro-09.pinned-ssh-command-result.v1", target_ref=request.target_ref,
            command_policy_version=s.command.command_policy_version, stdout_bytes=s.raw,
            stdout_sha256=hashlib.sha256(s.raw).hexdigest(), host_key_fingerprint=s.snapshot.host_key_fingerprint,
            exit_status=0, execution_attempts=1, execution_authorized=False)

    def transport(*args):
        assert len(args) == 4
        ep, cred, snap, spec = args
        assert type(ep) is m._target.Stage2FixedTargetEndpoint and ep.address == "192.0.2.10"
        assert cred is s.credential and snap is s.snapshot and spec is s.command
        s.transport_inputs = (type(ep), type(cred), type(snap), type(spec))
        return step("transport", result())

    def parser(r, raw):
        frame = inspect.currentframe().f_back
        s.credential_released.append(frame.f_locals["credential"] is None)
        s.parser_input = raw
        step("parser", None)
        if "parser" in s.returns:
            return s.returns["parser"]
        return REAL_PARSE(r, raw)

    def evidence(**kwargs):
        s.evidence_fields = kwargs
        step("evidence", None)
        return REAL_EVIDENCE(**kwargs)

    real_binding = m._authorization.validate_stage2_authorization_binding

    def binding(*args, **kwargs):
        step("binding", None)
        return real_binding(*args, **kwargs)

    monkeypatch.setattr(m._root, "acquire_owner_trust_root_configuration", acquire_root)
    monkeypatch.setattr(m._owner, "Stage2OwnerVerifier", Verifier)
    monkeypatch.setattr(m._owner.Stage2ExactOwnerApprovalSource, "read_exact", deny)
    monkeypatch.setattr(m._authorization, "Stage2ReplayLedger", Ledger)
    monkeypatch.setattr(m._authorization, "validate_stage2_authorization_binding", binding)
    monkeypatch.setattr(m._host, "acquire_stage2_known_host_snapshot", host)
    monkeypatch.setattr(m._windows, "build_stage2_windows_credential_backend", backend)
    monkeypatch.setattr(m._policy, "resolve_stage2_vrrp_readonly_command", command)
    monkeypatch.setattr(m._transport, "execute_stage2_pinned_ssh_command", transport)
    monkeypatch.setattr(m._parser, "parse_stage2_vrrp_readonly_output", parser)
    monkeypatch.setattr(m._contract, "Stage2VrrpObservationEvidence", evidence)
    monkeypatch.setattr(m, "_utc_now", lambda: 1100)
    ticks = iter((1_000_000_000, 1_001_000_001))
    monkeypatch.setattr(m, "_monotonic_now", lambda: next(ticks))
    s.result = result
    s.call = lambda: m.execute_stage2_vrrp_trusted_runtime(s.request, s.envelope.to_canonical_bytes(), s.config)
    return s


def rejected(call, category):
    with pytest.raises(m.Stage2TrustedRuntimeError) as caught:
        call()
    error = caught.value
    assert error.code is category
    assert error.args == (category.value,)
    assert error.__cause__ is None and error.__context__ is None
    assert SENTINEL not in str(error) + repr(error)
    tb = error.__traceback__
    while tb:
        if (tb.tb_frame.f_globals.get("__name__") == m.__name__
                and tb.tb_frame.f_code.co_name != "_raise_sanitized"):
            assert tb.tb_frame.f_code.co_name == "execute_stage2_vrrp_trusted_runtime"
            assert tb.tb_frame.f_locals["request"] is None
            assert tb.tb_frame.f_locals["authorization_envelope_bytes"] is None
            assert tb.tb_frame.f_locals["trusted_configuration"] is None
        tb = tb.tb_next
    return error


def test_success_exact_order_and_evidence(setup):
    s = setup
    evidence = s.call()
    assert type(evidence) is REAL_EVIDENCE
    assert s.trace == ["binding", "root", "verifier", "verify", "ledger", "consume", "host",
                       "binding", "backend", "credential", "command", "binding", "transport", "parser", "evidence"]
    assert s.spent and s.credential_released == [True]
    assert s.parser_input is s.raw
    assert evidence.duration_ms == 2
    assert evidence.execution_authorized is False
    assert evidence.raw_output_byte_count == len(RAW)
    assert evidence.raw_output_sha256 == hashlib.sha256(RAW).hexdigest()
    assert evidence.records[0].instance_name == "synthetic-vrrp"
    assert evidence.attempt_count == 1 and evidence.retry_count == 0
    assert set(s.evidence_fields) == {f.name for f in fields(REAL_EVIDENCE)}
    assert SENTINEL.encode() not in evidence.to_canonical_bytes()
    assert RAW not in evidence.to_canonical_bytes()
    assert m._contract.parse_stage2_vrrp_evidence_canonical_json(evidence.to_canonical_bytes()) == evidence


@pytest.mark.parametrize("value", [None, {}, object(), True])
def test_request_wrong_types(setup, value):
    setup.request = value
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(value, b"", setup.config), F.INVALID_REQUEST)
    assert setup.trace == []


@pytest.mark.parametrize("name", [f.name for f in fields(m._contract.Stage2VrrpObservationRequest)])
def test_request_malformed_each_field(setup, name):
    bad = drift(setup.request, name, None)
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(bad, b"", setup.config), F.INVALID_REQUEST)
    assert setup.trace == []


def test_request_subclass_and_uninitialized(setup):
    class Child(m._contract.Stage2VrrpObservationRequest):
        pass
    for bad in (Child(**setup.request.to_dict()), object.__new__(m._contract.Stage2VrrpObservationRequest)):
        rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(bad, b"", setup.config), F.INVALID_REQUEST)
    assert setup.trace == []


@pytest.mark.parametrize("name", [f.name for f in fields(m.Stage2TrustedRuntimeConfiguration)])
def test_configuration_missing_and_wrong_each_field(setup, name):
    bad = drift(setup.config, name, None)
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(setup.request, b"", bad),
             F.INVALID_TRUSTED_RUNTIME_CONFIGURATION)
    assert setup.trace == []


@pytest.mark.parametrize("kind", ["none", "dict", "subclass", "uninitialized", "endpoint", "ledger", "host", "credential", "rootpath", "identity", "digest"])
def test_configuration_adversarial(setup, kind):
    c = setup.config
    class Child(m.Stage2TrustedRuntimeConfiguration):
        pass
    candidates = {
        "none": None, "dict": {}, "subclass": object.__new__(Child),
        "uninitialized": object.__new__(m.Stage2TrustedRuntimeConfiguration),
        "endpoint": drift(c, "target_registry", m._target.Stage2FixedTargetRegistry(
            replace(c.target_registry._endpoint, address="192.0.2.11"))),
        "ledger": drift(c, "replay_ledger_configuration", drift(c.replay_ledger_configuration, "excluded_roots", [])),
        "host": drift(c, "known_host_configuration", drift(c.known_host_configuration, "expected_file_sha256", "A" * 64)),
        "credential": drift(c, "credential_configuration", drift(c.credential_configuration, "credential_target", "")),
        "rootpath": drift(c, "owner_trust_root_expected_path", r"C:\synthetic\root.json"),
        "identity": drift(c, "owner_trust_root_expected_file_identity", "bad"),
        "digest": drift(c, "owner_trust_root_expected_file_sha256", "A" * 64),
    }
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(setup.request, b"", candidates[kind]),
             F.INVALID_TRUSTED_RUNTIME_CONFIGURATION)
    assert setup.trace == []


def test_configuration_immutable_redacted_exact_fields(setup):
    assert len(fields(setup.config)) == 7 and not hasattr(setup.config, "__dict__")
    with pytest.raises(FrozenInstanceError):
        setup.config.owner_trust_root_expected_path = "bad"
    assert "synthetic" not in repr(setup.config)
    values = {f.name: getattr(setup.config, f.name) for f in fields(setup.config)}
    values["owner_trust_root_expected_path"] = "bad"
    with pytest.raises(m.Stage2TrustedRuntimeError) as caught:
        m.Stage2TrustedRuntimeConfiguration(**values)
    assert caught.value.__cause__ is None and caught.value.__context__ is None


@pytest.mark.parametrize("raw", [None, "{}", bytearray(b"{}"), b"", b"x" * 2049, b"{}", b"\xef\xbb\xbf{}", b"{}\n"])
def test_envelope_rejects_without_external_stage(setup, raw):
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(setup.request, raw, setup.config),
             F.AUTHORIZATION_ENVELOPE_FAILED)
    assert setup.trace == []


@pytest.mark.parametrize("now", [999, 1300, -1, True, 1100.0, None, 253402300800])
def test_clock_and_validity_reject_before_root(setup, monkeypatch, now):
    monkeypatch.setattr(m, "_utc_now", lambda: now)
    rejected(setup.call, F.AUTHORIZATION_ENVELOPE_FAILED)
    assert setup.trace == ["binding"]


@pytest.mark.parametrize("field,value", [("request_sha256", "0" * 64), ("authorization_ref", "authorization.other")])
def test_envelope_binding_mismatch(setup, field, value):
    setup.envelope = replace(setup.envelope, **{field: value})
    rejected(setup.call, F.AUTHORIZATION_ENVELOPE_FAILED)
    assert setup.trace == ["binding"]


@pytest.mark.parametrize("stage,category", [
    ("root", F.TRUST_ROOT_ACQUISITION_FAILED), ("verifier", F.OWNER_VERIFICATION_FAILED),
    ("verify", F.OWNER_VERIFICATION_FAILED), ("ledger", F.REPLAY_REJECTED), ("consume", F.REPLAY_REJECTED),
    ("host", F.KNOWN_HOST_ACQUISITION_FAILED), ("backend", F.CREDENTIAL_ACQUISITION_FAILED),
    ("credential", F.CREDENTIAL_ACQUISITION_FAILED), ("command", F.COMMAND_POLICY_FAILED),
    ("transport", F.TRANSPORT_FAILED), ("parser", F.OUTPUT_PARSE_FAILED), ("evidence", F.EVIDENCE_CONSTRUCTION_FAILED)])
def test_short_circuit_and_sanitized_unexpected_errors(setup, stage, category):
    setup.fail[stage] = RuntimeError(SENTINEL)
    rejected(setup.call, category)
    assert setup.trace[-1] == stage
    assert setup.trace.count(stage) == 1
    if stage in ("host", "backend", "credential", "command", "transport", "parser", "evidence"):
        assert setup.spent


CHILD_ERRORS = [
    ("root", m._root.OwnerTrustRootError, m._root.OwnerTrustRootFailure, F.TRUST_ROOT_ACQUISITION_FAILED),
    ("consume", m._authorization.Stage2AuthorizationError, m._authorization.Stage2AuthorizationFailure, F.REPLAY_REJECTED),
    ("host", m._host.Stage2KnownHostError, m._host.Stage2KnownHostFailure, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("credential", m._windows.Stage2WindowsCredentialError, m._windows.Stage2WindowsCredentialFailure, F.CREDENTIAL_ACQUISITION_FAILED),
    ("command", m._policy.Stage2VrrpCommandPolicyError, m._policy.Stage2VrrpCommandPolicyFailure, F.COMMAND_POLICY_FAILED),
    ("transport", m._transport.Stage2PinnedSshTransportError, m._transport.Stage2PinnedSshTransportFailure, F.TRANSPORT_FAILED),
    ("parser", m._parser.Stage2VrrpParserError, m._parser.Stage2VrrpParserFailure, F.OUTPUT_PARSE_FAILED),
]


@pytest.mark.parametrize("stage,error,code,category", [
    (stage, error, code, category) for stage, error, codes, category in CHILD_ERRORS for code in codes])
def test_all_child_failure_categories(setup, stage, error, code, category):
    setup.fail[stage] = error(code)
    rejected(setup.call, category)
    assert setup.trace[-1] == stage


@pytest.mark.parametrize("code", list(m._owner.Stage2OwnerVerificationFailure))
def test_owner_source_and_crypto_failure_mapping(setup, code):
    setup.fail["verify"] = m._owner.Stage2OwnerVerificationError(code)
    category = F.APPROVAL_ACQUISITION_FAILED if code.name.startswith("SOURCE_") else F.OWNER_VERIFICATION_FAILED
    rejected(setup.call, category)
    assert "consume" not in setup.trace and setup.trace.count("verify") == 1


@pytest.mark.parametrize("stage,category", [("root", F.TRUST_ROOT_ACQUISITION_FAILED),
    ("verify", F.OWNER_VERIFICATION_FAILED), ("consume", F.REPLAY_REJECTED),
    ("host", F.KNOWN_HOST_ACQUISITION_FAILED), ("credential", F.CREDENTIAL_ACQUISITION_FAILED),
    ("command", F.COMMAND_POLICY_FAILED), ("transport", F.TRANSPORT_FAILED), ("parser", F.OUTPUT_PARSE_FAILED)])
@pytest.mark.parametrize("shape", ["none", "uninitialized"])
def test_wrong_or_uninitialized_child_result(setup, stage, category, shape):
    kind = {"root": type(setup.root), "verify": type(setup.verification), "consume": type(setup.consumed),
            "host": type(setup.snapshot), "credential": type(setup.credential), "command": type(setup.command),
            "transport": m._transport.Stage2PinnedSshCommandResult, "parser": m._parser.Stage2VrrpParsedOutput}[stage]
    setup.returns[stage] = None if shape == "none" else object.__new__(kind)
    rejected(setup.call, category)
    assert setup.trace[-1] == stage


@pytest.mark.parametrize("stage,attribute,category", [("root", "root", F.TRUST_ROOT_ACQUISITION_FAILED),
    ("verify", "verification", F.OWNER_VERIFICATION_FAILED), ("consume", "consumed", F.REPLAY_REJECTED),
    ("host", "snapshot", F.KNOWN_HOST_ACQUISITION_FAILED), ("credential", "credential", F.CREDENTIAL_ACQUISITION_FAILED),
    ("command", "command", F.COMMAND_POLICY_FAILED)])
def test_child_missing_every_field(setup, stage, attribute, category, monkeypatch):
    original = getattr(setup, attribute)
    for field in fields(original):
        setup.trace.clear()
        setup.spent = False
        monkeypatch.setattr(m, "_monotonic_now", lambda: 1)
        setup.returns[stage] = issue(type(original), **{f.name: getattr(original, f.name)
                                                      for f in fields(original) if f.name != field.name})
        rejected(setup.call, category)
        assert setup.trace[-1] == stage


@pytest.mark.parametrize("name,value", [
    ("schema_version", "bad"), ("target_ref", "target.other"), ("command_policy_version", "bad"),
    ("exit_status", 1), ("exit_status", False), ("execution_attempts", 2), ("execution_attempts", True),
    ("execution_authorized", True), ("execution_authorized", 0), ("stdout_bytes", bytearray(RAW)),
    pytest.param("stdout_bytes", b"x" * 65537, id="stdout-overflow"), ("stdout_sha256", "0" * 64), ("host_key_fingerprint", "bad")])
def test_transport_integrity_drift(setup, name, value):
    setup.returns["transport"] = drift(setup.result(), name, value)
    rejected(setup.call, F.TRANSPORT_FAILED)
    assert "parser" not in setup.trace


@pytest.mark.parametrize("name", [f.name for f in fields(m._transport.Stage2PinnedSshCommandResult)])
def test_transport_missing_each_field(setup, name):
    value = setup.result()
    setup.returns["transport"] = issue(type(value), **{f.name: getattr(value, f.name) for f in fields(value) if f.name != name})
    rejected(setup.call, F.TRANSPORT_FAILED)
    assert "parser" not in setup.trace


@pytest.mark.parametrize("stage,attribute,name,value,category", [
    ("verify", "verification", "verified", False, F.OWNER_VERIFICATION_FAILED),
    ("verify", "verification", "verified", 1, F.OWNER_VERIFICATION_FAILED),
    ("verify", "verification", "execution_authorized", True, F.OWNER_VERIFICATION_FAILED),
    ("verify", "verification", "approval_ref", "authorization.other", F.OWNER_VERIFICATION_FAILED),
    ("verify", "verification", "verified_issuer_ref", "issuer.other", F.OWNER_VERIFICATION_FAILED),
    ("verify", "verification", "payload_sha256", "0" * 64, F.OWNER_VERIFICATION_FAILED),
    ("consume", "consumed", "authorization_id", INSTANCE, F.REPLAY_REJECTED),
    ("consume", "consumed", "envelope_sha256", "0" * 64, F.REPLAY_REJECTED),
    ("consume", "consumed", "consumed_at", 1300, F.REPLAY_REJECTED),
    ("host", "snapshot", "address", "192.0.2.11", F.KNOWN_HOST_ACQUISITION_FAILED),
    ("host", "snapshot", "port", True, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("host", "snapshot", "host_key_blob", b"x" * 51, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("host", "snapshot", "host_key_sha256", "0" * 64, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("host", "snapshot", "source_artifact_sha256", "0" * 64, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("host", "snapshot", "execution_authorized", True, F.KNOWN_HOST_ACQUISITION_FAILED),
    ("credential", "credential", "username", "bad\nuser", F.CREDENTIAL_ACQUISITION_FAILED),
    ("credential", "credential", "secret_blob", b"", F.CREDENTIAL_ACQUISITION_FAILED),
    ("command", "command", "command_text", "/system reboot", F.COMMAND_POLICY_FAILED),
    ("command", "command", "read_only", False, F.COMMAND_POLICY_FAILED),
])
def test_handoff_value_drift(setup, stage, attribute, name, value, category):
    setup.returns[stage] = drift(getattr(setup, attribute), name, value)
    rejected(setup.call, category)
    assert setup.trace[-1] == stage


@pytest.mark.parametrize("raw", [b"", b"\xff", b"malformed\n"])
def test_actual_parser_failure(setup, raw):
    setup.raw = raw
    rejected(setup.call, F.OUTPUT_PARSE_FAILED)
    assert setup.parser_input is raw and "evidence" not in setup.trace


@pytest.mark.parametrize("field,value", [("raw_output_sha256", "0" * 64), ("raw_output_byte_count", 1),
    ("records", ()), ("raw_output_byte_count", True)])
def test_parser_integrity_rejects(setup, field, value):
    setup.returns["parser"] = drift(REAL_PARSE(setup.request, RAW), field, value)
    rejected(setup.call, F.OUTPUT_PARSE_FAILED)
    assert "evidence" not in setup.trace


@pytest.mark.parametrize("elapsed,expected", [(0, 1), (1, 1), (999999, 1), (1000001, 2), (60000000000, 60000),
                                           (60000000001, None), (-1, None)])
def test_duration_rounding_and_rejection(setup, monkeypatch, elapsed, expected):
    ticks = iter((100000000000, 100000000000 + elapsed))
    monkeypatch.setattr(m, "_monotonic_now", lambda: next(ticks))
    if expected is None:
        rejected(setup.call, F.EVIDENCE_CONSTRUCTION_FAILED)
        assert "evidence" not in setup.trace
    else:
        assert setup.call().duration_ms == expected


@pytest.mark.parametrize("point", [1, 2])
def test_expiry_rechecks_never_reconsume(setup, monkeypatch, point):
    ticks = iter([1100] * point + [1300])
    monkeypatch.setattr(m, "_utc_now", lambda: next(ticks))
    rejected(setup.call, F.AUTHORIZATION_ENVELOPE_FAILED)
    assert setup.trace.count("consume") == 1 and setup.spent
    assert "transport" not in setup.trace
    assert setup.trace.count("credential") == (point == 2)


@pytest.mark.parametrize("stage,category", [("command", F.COMMAND_POLICY_FAILED), ("transport", F.TRANSPORT_FAILED)])
def test_credential_reference_released_during_failure_unwind(setup, monkeypatch, stage, category):
    # Observe the composition frame on return after its finally block; retain
    # only a Boolean, never a frame or credential in the observation log.
    import sys
    observations = []
    prior = sys.getprofile()
    def profile(frame, event, arg):
        if event == "return" and frame.f_code is m._run.__code__:
            observations.append(frame.f_locals["credential"] is None)
    setup.fail[stage] = RuntimeError(SENTINEL)
    try:
        sys.setprofile(profile)
        rejected(setup.call, category)
    finally:
        sys.setprofile(prior)
    assert observations == [True]


def test_serialization_failure_remains_spent(setup, monkeypatch):
    monkeypatch.setattr(REAL_EVIDENCE, "to_canonical_bytes", lambda self: (_ for _ in ()).throw(RuntimeError(SENTINEL)))
    rejected(setup.call, F.EVIDENCE_CONSTRUCTION_FAILED)
    assert setup.spent and setup.trace.count("evidence") == 1


@pytest.mark.parametrize("stage,category", [("host", F.KNOWN_HOST_ACQUISITION_FAILED),
    ("credential", F.CREDENTIAL_ACQUISITION_FAILED), ("command", F.COMMAND_POLICY_FAILED),
    ("transport", F.TRANSPORT_FAILED), ("parser", F.OUTPUT_PARSE_FAILED), ("evidence", F.EVIDENCE_CONSTRUCTION_FAILED)])
def test_real_replay_remains_spent_after_each_downstream_failure(setup, monkeypatch, stage, category):
    path = setup.config.replay_ledger_configuration.database_path
    with sqlite3.connect(path) as connection:
        for ddl in m._authorization._SCHEMA:
            connection.execute(ddl)
        connection.execute("INSERT INTO ledger_metadata VALUES (?, ?)", ("1.0", INSTANCE))
    monkeypatch.setattr(m._authorization, "Stage2ReplayLedger", REAL_LEDGER)
    monkeypatch.setattr(m, "_monotonic_now", lambda: 1)
    setup.fail[stage] = RuntimeError(SENTINEL)
    rejected(setup.call, category)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT authorization_id FROM consumed_authorizations").fetchall() == [(AUTH_ID,)]
    setup.trace.clear()
    rejected(setup.call, F.REPLAY_REJECTED)
    assert "host" not in setup.trace and "credential" not in setup.trace and "transport" not in setup.trace


def test_request_and_nested_configuration_captured_before_external_stage(setup, monkeypatch):
    original = m._root.acquire_owner_trust_root_configuration
    # Mutate only caller-owned inputs after private capture.
    supplied_request = setup.request
    supplied_config = setup.config
    saved_request = replace(supplied_request)
    saved_config = m.Stage2TrustedRuntimeConfiguration(*m._configuration_values(supplied_config))
    def mutate(**kwargs):
        value = original(**kwargs)
        object.__setattr__(supplied_request, "run_id", "run.changed")
        object.__setattr__(supplied_config.target_registry._endpoint, "address", "192.0.2.99")
        setup.request = saved_request
        setup.config = saved_config
        return value
    monkeypatch.setattr(m._root, "acquire_owner_trust_root_configuration", mutate)
    evidence = m.execute_stage2_vrrp_trusted_runtime(
        supplied_request, setup.envelope.to_canonical_bytes(), supplied_config)
    assert evidence.run_id == "run.synthetic"
    assert supplied_request.run_id == "run.changed"
    assert supplied_config.target_registry._endpoint.address == "192.0.2.99"
    assert setup.trace[-1] == "evidence"


def test_public_surface_and_no_later_slice():
    assert set(m.__all__) == {"Stage2TrustedRuntimeConfiguration", "Stage2TrustedRuntimeFailure",
                             "Stage2TrustedRuntimeError", "execute_stage2_vrrp_trusted_runtime"}
    assert list(inspect.signature(m.execute_stage2_vrrp_trusted_runtime).parameters) == [
        "request", "authorization_envelope_bytes", "trusted_configuration"]
    assert len(F) == 16
    source = Path(m.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert {name for name in functions if not name.startswith("_")} == {"execute_stage2_vrrp_trusted_runtime"}
    for forbidden in ("argparse", "os.environ", "getenv", "__main__", "Stage2ExactOwnerApprovalSource",
                      "read_exact", "sqlite3", "paramiko", "Thread(", "input(", "print("):
        assert forbidden not in source


def test_failure_drops_callers_active_exception_context(setup):
    setup.fail["verify"] = RuntimeError(SENTINEL)
    try:
        raise RuntimeError(SENTINEL)
    except RuntimeError:
        rejected(setup.call, F.OWNER_VERIFICATION_FAILED)


def test_malformed_owner_exception_still_maps_to_stage(setup):
    error = m._owner.Stage2OwnerVerificationError(m._owner.Stage2OwnerVerificationFailure.SIGNATURE_INVALID)
    del error.code
    setup.fail["verify"] = error
    rejected(setup.call, F.OWNER_VERIFICATION_FAILED)
    assert "consume" not in setup.trace


@pytest.mark.parametrize("target", ["target.unknown", "target.mikrotik.other"])
def test_unknown_registry_target_prevents_root(setup, target):
    setup.request = replace(setup.request, target_ref=target)
    rejected(setup.call, F.TARGET_RESOLUTION_FAILED)
    assert setup.trace == []


def test_unknown_credential_binding_prevents_root(setup):
    setup.request = replace(setup.request, credential_ref="credential.unknown")
    rejected(setup.call, F.CREDENTIAL_BINDING_FAILED)
    assert setup.trace == []


@pytest.mark.parametrize("point,category", [("utc", F.AUTHORIZATION_ENVELOPE_FAILED), ("monotonic", F.INTERNAL_FAILURE)])
def test_failed_system_clock_has_no_fallback(setup, monkeypatch, point, category):
    def failure():
        raise RuntimeError(SENTINEL)
    monkeypatch.setattr(m, "_utc_now" if point == "utc" else "_monotonic_now", failure)
    rejected(setup.call, category)
    assert "root" not in setup.trace


def test_private_clock_definitions(monkeypatch):
    monkeypatch.setattr(m._time, "time_ns", lambda: 1234567890123)
    monkeypatch.setattr(m._time, "monotonic_ns", lambda: 456)
    assert m._utc_now() == 1234 and m._monotonic_now() == 456
    monkeypatch.setattr(m._time, "monotonic_ns", lambda: True)
    with pytest.raises(ValueError):
        m._monotonic_now()


@pytest.mark.parametrize("point", ["command", "time", "transport"])
def test_reference_release_after_all_post_read_failures(setup, monkeypatch, point):
    import sys
    observations = []
    prior = sys.getprofile()
    def profile(frame, event, arg):
        if event == "return" and frame.f_code is m._run.__code__:
            observations.append(frame.f_locals["credential"] is None)
    category = F.AUTHORIZATION_ENVELOPE_FAILED
    if point == "time":
        ticks = iter((1100, 1100, 1300))
        monkeypatch.setattr(m, "_utc_now", lambda: next(ticks))
    else:
        setup.fail[point] = RuntimeError(SENTINEL)
        category = F.COMMAND_POLICY_FAILED if point == "command" else F.TRANSPORT_FAILED
    try:
        sys.setprofile(profile)
        rejected(setup.call, category)
    finally:
        sys.setprofile(prior)
    assert observations == [True] and setup.trace.count("credential") == 1


@pytest.mark.parametrize("attribute", ["target_registry", "replay_ledger_configuration", "known_host_configuration", "credential_configuration"])
def test_nested_config_subclasses_reject_before_external(setup, attribute):
    original = getattr(setup.config, attribute)
    child = type("Child", (type(original),), {})
    bad = drift(setup.config, attribute, object.__new__(child))
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(setup.request, b"", bad),
             F.INVALID_TRUSTED_RUNTIME_CONFIGURATION)
    assert setup.trace == []


@pytest.mark.parametrize("attribute", ["target_registry", "replay_ledger_configuration", "known_host_configuration", "credential_configuration"])
def test_nested_config_uninitialized_reject_before_external(setup, attribute):
    bad = drift(setup.config, attribute, object.__new__(type(getattr(setup.config, attribute))))
    rejected(lambda: m.execute_stage2_vrrp_trusted_runtime(setup.request, b"", bad),
             F.INVALID_TRUSTED_RUNTIME_CONFIGURATION)
    assert setup.trace == []
