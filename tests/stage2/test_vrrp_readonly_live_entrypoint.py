"""Offline entrypoint tests: only the private runtime binding is substituted."""

import ast
from dataclasses import fields
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
import typing

import pytest

from validation_framework import stage2_vrrp_readonly_live_entrypoint as m
from validation_framework import stage2_vrrp_readonly_contract as c
from validation_framework import stage2_trusted_runtime_composition as runtime


F = m.Stage2VrrpLiveEntrypointFailure
SENTINEL = "synthetic-secret-path-key-signature-raw-output"


class BytesSubclass(bytes):
    pass


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("real runtime forbidden in entrypoint tests")
    monkeypatch.setattr(m, "_execute", forbidden)


@pytest.fixture
def setup(monkeypatch, tmp_path):
    request = c.Stage2VrrpObservationRequest(
        "1.0", "mikrotik.vrrp_status", "run.synthetic", "target.mikrotik.lab01",
        "credential.mikrotik.lab01", "authorization.synthetic", True)
    endpoint = runtime._target.Stage2FixedTargetEndpoint(
        request.target_ref, "192.0.2.10", 22, "SSH", True)
    identity = "win32-fileid-v1:" + "1" * 16 + ":" + "2" * 32
    config = runtime.Stage2TrustedRuntimeConfiguration(
        runtime._target.Stage2FixedTargetRegistry(endpoint),
        r"c:\synthetic\root.json", identity, "a" * 64,
        runtime._authorization.Stage2ReplayLedgerConfiguration(
            tmp_path / "synthetic.db", "22345678-1234-4234-8234-123456789abc",
            (Path(__file__).resolve().parents[2],)),
        runtime._host.Stage2KnownHostSourceConfiguration(
            r"c:\synthetic\host.json", identity, "b" * 64, endpoint),
        runtime._windows.Stage2TrustedWindowsCredentialConfiguration(
            runtime._resolver.STAGE2_CREDENTIAL_LOCATOR_REF, "synthetic-only-target"))
    evidence = c.Stage2VrrpObservationEvidence(
        "1.0", request.operation_id, request.run_id, request.target_ref,
        request.authorization_ref, c.VRRP_COMMAND_POLICY_VERSION,
        1, 0, 1, 0, "a" * 64, ())
    s = SimpleNamespace(request=request.to_canonical_bytes(), envelope=b"untrusted-envelope",
                        config=config, evidence=evidence, calls=[], error=None)

    def fake(*args):
        s.calls.append(args)
        if s.error is not None:
            raise s.error
        return s.evidence

    monkeypatch.setattr(m, "_execute", fake)
    s.call = lambda: m.run_stage2_vrrp_live_once(s.request, s.envelope, s.config)
    return s


def rejected(s, category, count):
    with pytest.raises(m.Stage2VrrpLiveEntrypointError) as caught:
        s.call()
    error = caught.value
    assert error.code is category
    assert error.args == (category.value,)
    assert error.__cause__ is None and error.__context__ is None
    assert SENTINEL not in str(error) + repr(error)
    assert len(s.calls) == count
    tb = error.__traceback__
    while tb:
        frame = tb.tb_frame
        if frame.f_globals.get("__name__") == m.__name__:
            assert frame.f_code.co_name in ("run_stage2_vrrp_live_once", "_raise_sanitized")
            if frame.f_code.co_name == "run_stage2_vrrp_live_once":
                assert frame.f_locals["request_bytes"] is None
                assert frame.f_locals["authorization_envelope_bytes"] is None
                assert frame.f_locals["trusted_configuration"] is None
                assert frame.f_locals["result"] is None
        tb = tb.tb_next
    return error


def test_success_canonical_identity_and_no_output(setup, capsys):
    output = setup.call()
    assert type(output) is bytes
    assert output == setup.evidence.to_canonical_bytes()
    assert c.parse_stage2_vrrp_evidence_canonical_json(output) == setup.evidence
    assert len(setup.calls) == 1
    request, envelope, config = setup.calls[0]
    assert type(request) is c.Stage2VrrpObservationRequest
    assert request.to_canonical_bytes() == setup.request
    assert envelope is setup.envelope and config is setup.config
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("value", [None, True, 1, "{}", {}, [], bytearray(b"{}"),
                                 memoryview(b"{}"), BytesSubclass(b"{}"), b"", b"x" * 2049],
                         ids=lambda value: type(value).__name__)
@pytest.mark.parametrize("field,category", [("request", F.INVALID_REQUEST_INPUT),
                                            ("envelope", F.INVALID_AUTHORIZATION_INPUT)])
def test_input_exact_type_and_bounds(setup, field, category, value):
    setattr(setup, field, value)
    rejected(setup, category, 0)


@pytest.mark.parametrize("raw", [b"{", b"null", b"[]", b"{}", b"\xff",
                                b'{"x":1,"x":1}', b'{"x":NaN}',
                                b"x" * 2048], ids=["syntax", "null", "list", "empty-object",
                                "utf8", "duplicate", "nan", "max-framing"])
def test_bad_request(setup, raw):
    setup.request = raw
    rejected(setup, F.INVALID_REQUEST_INPUT, 0)


@pytest.mark.parametrize("kind", ["bom", "newline", "space", "duplicate"])
def test_noncanonical_request(setup, kind):
    setup.request = {"bom": b"\xef\xbb\xbf" + setup.request,
                     "newline": setup.request + b"\n", "space": b" " + setup.request,
                     "duplicate": b'{"read_only":true,' + setup.request[1:]}[kind]
    rejected(setup, F.INVALID_REQUEST_INPUT, 0)


@pytest.mark.parametrize("field", ["schema_version", "operation_id", "run_id", "target_ref",
                                   "credential_ref", "authorization_ref", "read_only"])
@pytest.mark.parametrize("change", ["missing", "invalid"])
def test_request_fields(setup, field, change):
    data = json.loads(setup.request)
    if change == "missing":
        del data[field]
    else:
        data[field] = None
    setup.request = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    rejected(setup, F.INVALID_REQUEST_INPUT, 0)


@pytest.mark.parametrize("override", ["command", "timeout", "retry", "host_key", "password",
                                      "execution_mode", "target_override", "credential_override"])
def test_no_request_override_fields(setup, override):
    data = json.loads(setup.request)
    data[override] = SENTINEL
    setup.request = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    rejected(setup, F.INVALID_REQUEST_INPUT, 0)


@pytest.mark.parametrize("raw", [b"x", b"x" * 2048, b'{"x":1,"x":1}', b"\xff"],
                         ids=["min", "max", "noncanonical", "invalid-utf8"])
def test_envelope_only_framing_no_local_parse(setup, raw):
    setup.envelope = raw
    setup.call()
    assert setup.calls[0][1] is raw
    assert len(setup.calls) == 1


@pytest.mark.parametrize("kind", ["dict", "lookalike", "subclass", "none", "string"])
def test_config_rejects_wrong_type(setup, kind):
    class Subclass(runtime.Stage2TrustedRuntimeConfiguration):
        pass
    setup.config = {"dict": {}, "lookalike": SimpleNamespace(),
                    "subclass": object.__new__(Subclass), "none": None, "string": SENTINEL}[kind]
    rejected(setup, F.INVALID_TRUSTED_CONFIGURATION, 0)


@pytest.mark.parametrize("code", list(runtime.Stage2TrustedRuntimeFailure))
def test_all_runtime_categories(setup, code, capsys):
    setup.error = runtime.Stage2TrustedRuntimeError(code)
    setup.error.args = (SENTINEL,)
    expected = {
        runtime.Stage2TrustedRuntimeFailure.INVALID_REQUEST: F.INVALID_REQUEST_INPUT,
        runtime.Stage2TrustedRuntimeFailure.INVALID_TRUSTED_RUNTIME_CONFIGURATION: F.INVALID_TRUSTED_CONFIGURATION,
        runtime.Stage2TrustedRuntimeFailure.AUTHORIZATION_ENVELOPE_FAILED: F.INVALID_AUTHORIZATION_INPUT,
    }.get(code, F.TRUSTED_RUNTIME_FAILED)
    rejected(setup, expected, 1)
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("kind", ["unexpected", "missing-code", "wrong-code", "subclass"])
def test_unexpected_errors_are_internal(setup, kind):
    class Subclass(runtime.Stage2TrustedRuntimeError):
        pass
    error = runtime.Stage2TrustedRuntimeError(runtime.Stage2TrustedRuntimeFailure.REPLAY_REJECTED)
    if kind == "missing-code":
        del error.code
    elif kind == "wrong-code":
        error.code = SENTINEL
    elif kind == "subclass":
        error = Subclass(runtime.Stage2TrustedRuntimeFailure.REPLAY_REJECTED)
    else:
        error = RuntimeError(SENTINEL)
    setup.error = error
    rejected(setup, F.INTERNAL_FAILURE, 1)


@pytest.mark.parametrize("kind", ["none", "dict", "bytes", "subclass", "uninitialized"])
def test_wrong_evidence(setup, kind):
    class Subclass(c.Stage2VrrpObservationEvidence):
        pass
    setup.evidence = {"none": None, "dict": {}, "bytes": SENTINEL.encode(),
                      "subclass": object.__new__(Subclass),
                      "uninitialized": object.__new__(c.Stage2VrrpObservationEvidence)}[kind]
    rejected(setup, F.OUTPUT_RENDER_FAILED, 1)


@pytest.mark.parametrize("field", [f.name for f in fields(c.Stage2VrrpObservationEvidence)])
@pytest.mark.parametrize("change", ["missing", "invalid"])
def test_malformed_exact_evidence(setup, field, change, capsys):
    if change == "missing":
        object.__delattr__(setup.evidence, field)
    else:
        object.__setattr__(setup.evidence, field, None)
    rejected(setup, F.OUTPUT_RENDER_FAILED, 1)
    assert capsys.readouterr() == ("", "")


def test_oversized_serialization(setup):
    object.__setattr__(setup.evidence, "run_id", "run." + "x" * 32768)
    rejected(setup, F.OUTPUT_RENDER_FAILED, 1)


def test_non_json_serialization(setup):
    object.__setattr__(setup.evidence, "run_id", object())
    rejected(setup, F.OUTPUT_RENDER_FAILED, 1)


def test_nested_record_revalidation(setup):
    record = c.NormalizedVrrpRecord("synthetic", 1, 100, 1000, 3, True, "MASTER", False, False)
    object.__setattr__(record, "priority", 999)
    object.__setattr__(setup.evidence, "records", (record,))
    rejected(setup, F.OUTPUT_RENDER_FAILED, 1)


def test_active_caller_exception_not_retained(setup):
    setup.error = RuntimeError(SENTINEL)
    try:
        raise ValueError(SENTINEL)
    except ValueError:
        rejected(setup, F.INTERNAL_FAILURE, 1)


def test_second_invocation_is_explicit_only(setup):
    setup.call()
    assert len(setup.calls) == 1
    setup.call()
    assert len(setup.calls) == 2


def test_exact_public_surface_signature_and_no_state():
    assert m.__all__ == ("Stage2VrrpLiveEntrypointFailure", "Stage2VrrpLiveEntrypointError",
                         "run_stage2_vrrp_live_once")
    assert {name for name in vars(m) if not name.startswith("_")} == set(m.__all__)
    signature = inspect.signature(m.run_stage2_vrrp_live_once)
    assert list(signature.parameters) == ["request_bytes", "authorization_envelope_bytes", "trusted_configuration"]
    assert all(p.default is inspect.Parameter.empty and p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
               for p in signature.parameters.values())
    assert typing.get_type_hints(m.run_stage2_vrrp_live_once) == {
        "request_bytes": bytes, "authorization_envelope_bytes": bytes,
        "trusted_configuration": runtime.Stage2TrustedRuntimeConfiguration, "return": bytes}
    assert len(F) == 6
    assert not any(type(value) in (dict, list, set) for name, value in vars(m).items()
                   if not name.startswith("__"))


def test_static_single_handoff_and_no_authority_sources():
    tree = ast.parse(inspect.getsource(m))
    forbidden = (ast.For, ast.While, ast.AsyncFor, ast.AsyncFunctionDef, ast.Global,
                 ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
    assert not any(isinstance(node, forbidden) for node in ast.walk(tree))
    calls = [node.func for node in ast.walk(tree) if isinstance(node, ast.Call)]
    names = [node.id for node in calls if isinstance(node, ast.Name)]
    assert names.count("_execute") == 1
    assert not {"print", "open", "exec", "eval", "main", "getattr_from_env"} & set(names)
    imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert set(imports) == {"enum", "validation_framework",
                           "validation_framework.stage2_authorization_envelope_ledger",
                           "validation_framework.stage2_trusted_runtime_composition"}
    assert not any(isinstance(node, ast.Import) for node in ast.walk(tree))
    attributes = {node.attr for node in calls if isinstance(node, ast.Attribute)}
    assert attributes == {"parse_stage2_vrrp_request_canonical_json", "to_canonical_bytes",
                          "parse_stage2_vrrp_evidence_canonical_json", "__init__"}
    assert "stage2_vrrp_readonly_live_entrypoint" not in Path("network_lab.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("value", [None, "INTERNAL_FAILURE", SENTINEL, 1])
def test_error_requires_bounded_enum(value):
    with pytest.raises(TypeError, match="^bounded entrypoint category required$"):
        m.Stage2VrrpLiveEntrypointError(value)
