"""DL-02 synthetic tests: private entrypoint fake only, no live authority."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import inspect
import json
from pathlib import Path
import socket
import sqlite3
from types import SimpleNamespace

import pytest

from validation_framework import dual_lab_vrrp_query_orchestrator as m
from validation_framework import dual_lab_vrrp_query_contract as d
from validation_framework import stage2_vrrp_readonly_contract as c
from validation_framework import stage2_authorization_envelope_ledger as a
from validation_framework import stage2_trusted_runtime_composition as r
from validation_framework import stage2_vrrp_readonly_live_entrypoint as entry


LABS = ("target.mikrotik.lab01", "target.mikrotik.lab02")
NOW = 1_800_000_000
SENTINEL = "synthetic-secret-raw-stdout-signature-private-path-exception"
F = d.FailureCategory


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def configuration(number, root):
    first = r._target.Stage2FixedTargetEndpoint(LABS[0], "192.0.2.1", 22, "SSH", True)
    second = r._target.Stage2FixedTargetEndpoint(LABS[1], "192.0.2.2", 22, "SSH", True)
    registry = r._target.Stage2FixedTargetRegistry(first, second)
    identity = "win32-fileid-v1:" + "1" * 16 + ":" + "2" * 32
    return r.Stage2TrustedRuntimeConfiguration(
        registry, r"c:\synthetic\root.json", identity, "a" * 64,
        a.Stage2ReplayLedgerConfiguration(
            root / "never-opened.db", "22345678-1234-4234-8234-123456789abc",
            (Path(__file__).resolve().parents[2],)),
        r._host.Stage2KnownHostSourceConfiguration(
            rf"c:\synthetic\lab{number}.json", identity, "b" * 64,
            registry.lookup(LABS[number - 1])),
        r._windows.Stage2TrustedWindowsCredentialConfiguration(
            f"locator.stage2.mikrotik.lab0{number}.readonly", f"synthetic-only-lab{number}"))


def request(number):
    return c.Stage2VrrpObservationRequest(
        "1.0", "mikrotik.vrrp_status", f"run.synthetic-lab{number}", LABS[number - 1],
        f"credential.mikrotik.lab0{number}", f"authorization.synthetic-lab{number}", True)


def envelope(req, number):
    return a.Stage2AuthorizationEnvelope(
        "1.0", f"{number}2345678-1234-4234-8234-123456789abc", req.operation_id,
        hashlib.sha256(req.to_canonical_bytes()).hexdigest(), req.authorization_ref,
        req.target_ref, req.credential_ref, NOW - 10, NOW + 100, 1)


def evidence(req, number):
    record = c.NormalizedVrrpRecord(
        "vrrp-synthetic", 88, 150 if number == 1 else 100, 1000, 3,
        number == 1, "MASTER" if number == 1 else "BACKUP", False, False)
    return c.Stage2VrrpObservationEvidence(
        "1.0", req.operation_id, req.run_id, req.target_ref, req.authorization_ref,
        c.VRRP_COMMAND_POLICY_VERSION, 1, 0, 1 if number == 1 else 60_000,
        0, "a" * 64, (record,)).to_canonical_bytes()


@pytest.fixture(autouse=True)
def no_real_execution(monkeypatch):
    attempted = []

    def forbidden(*args, **kwargs):
        attempted.append("forbidden execution boundary")
        raise AssertionError("real execution is forbidden in DL-02 tests")

    for obj, name in (
        (m, "_invoke_once"), (entry, "run_stage2_vrrp_live_once"), (entry, "_execute"),
        (r, "execute_stage2_vrrp_trusted_runtime"),
        (r._root, "acquire_owner_trust_root_configuration"),
        (r._owner.Stage2OwnerVerifier, "verify"),
        (a.Stage2ReplayLedger, "consume"),
        (r._host, "acquire_stage2_known_host_snapshot"),
        (r._windows, "build_stage2_windows_credential_backend"),
        (r._transport, "execute_stage2_pinned_ssh_command"),
        (socket, "create_connection"), (socket, "getaddrinfo"), (sqlite3, "connect"),
    ):
        monkeypatch.setattr(obj, name, forbidden)
    monkeypatch.setattr(m, "_utc_now", lambda: NOW)
    yield
    assert attempted == []


@pytest.fixture
def setup(monkeypatch, tmp_path):
    requests = [request(1), request(2)]
    bundles = [m.DualLabTargetBundle(req.to_canonical_bytes(), envelope(req, n).to_canonical_bytes(),
                                   configuration(n, tmp_path))
               for n, req in enumerate(requests, 1)]
    state = SimpleNamespace(
        query=d.DualLabVrrpQuery("dual-lab-vrrp-query.v1", "query.synthetic", "mikrotik.vrrp_status",
                                "LAB1_THEN_LAB2"),
        bundles=bundles, calls=[], ledger=[], active=False,
        outputs=[evidence(req, n) for n, req in enumerate(requests, 1)],
        errors=[None, None])

    def fake(request_bytes, envelope_bytes, config):
        assert not state.active, "S2-RO-11 calls overlapped"
        state.active = True
        target = c.parse_stage2_vrrp_request_canonical_json(request_bytes).target_ref
        index = LABS.index(target)
        state.calls.append((request_bytes, envelope_bytes, config))
        state.ledger.append((target, "begin"))
        try:
            if state.errors[index] is not None:
                raise state.errors[index]
            return state.outputs[index]
        finally:
            state.ledger.append((target, "end"))
            state.active = False

    monkeypatch.setattr(m, "_invoke_once", fake)
    state.call = lambda: m.run_dual_lab_vrrp_query(state.query, *state.bundles)
    return state


def outcomes(value):
    return value.lab1, value.lab2


def assert_failure(value, code):
    assert type(value) is d.TargetFailure
    assert value.failure_category is code
    assert value.to_dict() == {"status": "FAILURE", "target_ref": value.target_ref,
                               "failure_category": code.value}


def change_request(state, index, **changes):
    raw = json.loads(state.bundles[index].request_bytes)
    raw.update(changes)
    state.bundles[index] = replace(state.bundles[index], request_bytes=canonical(raw))


def change_envelope(state, index, **changes):
    raw = json.loads(state.bundles[index].envelope_bytes)
    raw.update(changes)
    state.bundles[index] = replace(state.bundles[index], envelope_bytes=canonical(raw))


def test_success_order_overlap_call_limit_and_canonical_roundtrip(setup):
    value = setup.call()
    assert type(value) is d.DualLabVrrpAggregate
    assert [item.status for item in outcomes(value)] == ["SUCCESS", "SUCCESS"]
    assert setup.ledger == [(LABS[0], "begin"), (LABS[0], "end"),
                            (LABS[1], "begin"), (LABS[1], "end")]
    assert not setup.active and len(setup.calls) == 2
    for index, (req, env, config) in enumerate(setup.calls):
        assert req is setup.bundles[index].request_bytes
        assert env is setup.bundles[index].envelope_bytes
        assert config == setup.bundles[index].trusted_configuration
        assert config is not setup.bundles[index].trusted_configuration
    assert value.to_canonical_bytes() == canonical(value.to_dict())
    assert d.parse_aggregate_canonical_json(value.to_canonical_bytes()) == value
    assert set(value.to_dict()) == {"schema_version", "query_id", "operation_id", "execution_order", "lab1", "lab2"}
    # Different durations are observations, not skew/health acceptance rules.
    assert value.lab1.evidence.duration_ms == 1
    assert value.lab2.evidence.duration_ms == 60_000
    assert value.execution_authorized is False


@pytest.mark.parametrize("invalid_target", [None, 0, 1])
def test_both_preflights_finish_before_any_invocation(setup, monkeypatch, invalid_target):
    events = []
    original_preflight, original_invoke = m._preflight, m._invoke_once
    if invalid_target is not None:
        setup.bundles[invalid_target] = replace(setup.bundles[invalid_target], trusted_configuration=None)

    def preflight(bundle, target):
        result = original_preflight(bundle, target)
        events.append(target)
        return result

    def invoke(*args):
        assert events == list(LABS)
        return original_invoke(*args)

    monkeypatch.setattr(m, "_preflight", preflight)
    monkeypatch.setattr(m, "_invoke_once", invoke)
    value = setup.call()
    assert events == list(LABS)
    if invalid_target is not None:
        assert_failure(outcomes(value)[invalid_target], F.PREFLIGHT_STARTUP_BINDING_UNAVAILABLE)
        assert outcomes(value)[1 - invalid_target].status == "SUCCESS"
        assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("code", list(entry.Stage2VrrpLiveEntrypointFailure))
def test_six_runtime_failures_preserved_independently_without_retry(setup, index, code, capsys):
    error = entry.Stage2VrrpLiveEntrypointError(code)
    error.args = (SENTINEL,)
    setup.errors[index] = error
    value = setup.call()
    assert_failure(outcomes(value)[index], F(code.value))
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert setup.ledger == [(LABS[0], "begin"), (LABS[0], "end"),
                            (LABS[1], "begin"), (LABS[1], "end")]
    assert len(setup.calls) == 2 and not setup.active
    assert SENTINEL not in value.to_canonical_bytes().decode()
    assert capsys.readouterr() == ("", "")


def test_both_runtime_failures_keep_separate_categories(setup):
    setup.errors = [entry.Stage2VrrpLiveEntrypointError(entry.Stage2VrrpLiveEntrypointFailure.INVALID_REQUEST_INPUT),
                    entry.Stage2VrrpLiveEntrypointError(entry.Stage2VrrpLiveEntrypointFailure.TRUSTED_RUNTIME_FAILED)]
    value = setup.call()
    assert_failure(value.lab1, F.INVALID_REQUEST_INPUT)
    assert_failure(value.lab2, F.TRUSTED_RUNTIME_FAILED)
    assert len(setup.calls) == 2


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("kind", ["unexpected", "wrong-code", "missing-code", "subclass"])
def test_unexpected_or_forged_boundary_error_is_internal(setup, index, kind):
    class Subclass(entry.Stage2VrrpLiveEntrypointError):
        pass
    error = entry.Stage2VrrpLiveEntrypointError(entry.Stage2VrrpLiveEntrypointFailure.TRUSTED_RUNTIME_FAILED)
    if kind == "unexpected":
        error = RuntimeError(SENTINEL)
    elif kind == "wrong-code":
        error.code = SENTINEL
    elif kind == "missing-code":
        del error.code
    else:
        error = Subclass(entry.Stage2VrrpLiveEntrypointFailure.TRUSTED_RUNTIME_FAILED)
    setup.errors[index] = error
    value = setup.call()
    assert_failure(outcomes(value)[index], F.INTERNAL_FAILURE)
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert SENTINEL not in value.to_canonical_bytes().decode() + repr(value)
    assert len(setup.calls) == 2


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("kind", ["absent", "lookalike", "subclass", "uninitialized", "swapped"])
def test_invalid_bundle_only_skips_its_target(setup, index, kind):
    class Subclass(m.DualLabTargetBundle):
        pass
    setup.bundles[index] = {
        "absent": None, "lookalike": {}, "subclass": object.__new__(Subclass),
        "uninitialized": object.__new__(m.DualLabTargetBundle),
        "swapped": setup.bundles[1 - index],
    }[kind]
    value = setup.call()
    assert_failure(outcomes(value)[index], F.PREFLIGHT_TARGET_BUNDLE_INVALID)
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("field,value", [
    ("operation_id", "mikrotik.vrrp_set"), ("credential_ref", "credential.other"),
    ("target_ref", "target.mikrotik.lab03"), ("read_only", False),
    ("schema_version", "2.0"), ("run_id", None), ("command", SENTINEL),
])
def test_invalid_request_field_fails_before_authorization(setup, index, field, value):
    change_request(setup, index, **{field: value})
    setup.bundles[index] = replace(setup.bundles[index], envelope_bytes=None)
    result = setup.call()
    assert_failure(outcomes(result)[index], F.PREFLIGHT_TARGET_BUNDLE_INVALID)
    assert outcomes(result)[1 - index].status == "SUCCESS"
    assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("field", ["target_ref", "credential_ref"])
def test_other_lab_request_binding_rejected(setup, index, field):
    other = request(2 - index)
    change_request(setup, index, **{field: getattr(other, field)})
    value = setup.call()
    assert_failure(outcomes(value)[index], F.PREFLIGHT_TARGET_BUNDLE_INVALID)
    assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("raw", [None, b"", b"{}", b"null", b"\xff", b"x" * 2049, bytearray(b"{}")])
def test_request_framing(setup, index, raw):
    setup.bundles[index] = replace(setup.bundles[index], request_bytes=raw)
    value = setup.call()
    assert_failure(outcomes(value)[index], F.PREFLIGHT_TARGET_BUNDLE_INVALID)
    assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("kind", ["none", "wrong-type", "uninitialized", "swapped", "host", "locator",
                                  "root-pin", "endpoint", "ledger", "credential-target"])
def test_configuration_preflight_is_structural_and_target_local(setup, index, kind):
    config = setup.bundles[index].trusted_configuration
    if kind == "none":
        config = None
    elif kind == "wrong-type":
        config = {}
    elif kind == "uninitialized":
        config = object.__new__(r.Stage2TrustedRuntimeConfiguration)
    elif kind == "swapped":
        config = setup.bundles[1 - index].trusted_configuration
    elif kind == "host":
        config = replace(config, known_host_configuration=setup.bundles[1 - index].trusted_configuration.known_host_configuration)
    elif kind == "locator":
        config = replace(config, credential_configuration=setup.bundles[1 - index].trusted_configuration.credential_configuration)
    elif kind == "root-pin":
        object.__setattr__(config, "owner_trust_root_expected_file_sha256", SENTINEL)
    elif kind == "endpoint":
        object.__setattr__(config.known_host_configuration.expected_endpoint, "port", 23)
    elif kind == "ledger":
        object.__setattr__(config.replay_ledger_configuration, "expected_ledger_instance_id", SENTINEL)
    else:
        object.__setattr__(config.credential_configuration, "credential_target", "")
    setup.bundles[index] = replace(setup.bundles[index], trusted_configuration=config, envelope_bytes=None)
    value = setup.call()
    expected = F.PREFLIGHT_STARTUP_BINDING_UNAVAILABLE if kind == "none" else F.PREFLIGHT_TARGET_BUNDLE_INVALID
    assert_failure(outcomes(value)[index], expected)
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert len(setup.calls) == 1


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("kind", ["missing", "malformed", "expired", "not-yet-valid", "hash", "ref", "id",
                                  "swapped", "target", "credential", "operation", "duplicate-key", "noncanonical"])
def test_envelope_rejection_uses_existing_stage2_semantics(setup, index, kind):
    if kind in ("missing", "malformed", "swapped", "noncanonical", "duplicate-key"):
        raw = setup.bundles[index].envelope_bytes
        raw = {"missing": None, "malformed": b"{}", "swapped": setup.bundles[1 - index].envelope_bytes,
               "noncanonical": raw + b"\n", "duplicate-key": b'{"max_attempts":1,' + raw[1:]}[kind]
        setup.bundles[index] = replace(setup.bundles[index], envelope_bytes=raw)
    else:
        changes = {
            "expired": {"issued_at": NOW - 100, "expires_at": NOW},
            "not-yet-valid": {"issued_at": NOW + 1, "expires_at": NOW + 100},
            "hash": {"request_sha256": "0" * 64}, "ref": {"authorization_ref": "authorization.other"},
            "id": {"authorization_id": SENTINEL}, "target": {"target_ref": LABS[1 - index]},
            "credential": {"credential_ref": f"credential.mikrotik.lab0{2 - index}"},
            "operation": {"operation_id": "mikrotik.other"},
        }[kind]
        change_envelope(setup, index, **changes)
    value = setup.call()
    assert_failure(outcomes(value)[index], F.PREFLIGHT_AUTHORIZATION_INVALID)
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert len(setup.calls) == 1


@pytest.mark.parametrize("field", ["authorization_ref", "authorization_id"])
def test_duplicate_identity_blocks_both_with_zero_invocations(setup, field):
    if field == "authorization_ref":
        duplicate = request(1).authorization_ref
        change_request(setup, 1, authorization_ref=duplicate)
        change_envelope(setup, 1, authorization_ref=duplicate,
                        request_sha256=hashlib.sha256(setup.bundles[1].request_bytes).hexdigest())
    else:
        change_envelope(setup, 1, authorization_id=envelope(request(1), 1).authorization_id)
    value = setup.call()
    for result in outcomes(value):
        assert_failure(result, F.PREFLIGHT_AUTHORIZATION_NOT_DISTINCT)
    assert setup.calls == [] and setup.ledger == []


def test_two_local_failures_have_no_invocations(setup):
    setup.bundles[0] = replace(setup.bundles[0], trusted_configuration=None)
    setup.bundles[1] = replace(setup.bundles[1], envelope_bytes=b"{}")
    value = setup.call()
    assert_failure(value.lab1, F.PREFLIGHT_STARTUP_BINDING_UNAVAILABLE)
    assert_failure(value.lab2, F.PREFLIGHT_AUTHORIZATION_INVALID)
    assert setup.calls == []


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("kind", ["none", "object", "noncanonical", "duplicate-key", "other-target",
                                  "operation", "policy", "schema", "run", "authorization", "record", "raw-output"])
def test_candidate_evidence_revalidated_without_substitution(setup, index, kind):
    raw = setup.outputs[index]
    if kind in ("none", "object", "noncanonical", "duplicate-key", "other-target"):
        raw = {"none": None, "object": c.parse_stage2_vrrp_evidence_canonical_json(raw),
               "noncanonical": raw + b"\n", "duplicate-key": b'{"attempt_count":1,' + raw[1:],
               "other-target": setup.outputs[1 - index]}[kind]
    else:
        data = json.loads(raw)
        field, changed = {
            "operation": ("operation_id", "mikrotik.other"),
            "policy": ("command_policy_version", "policy.other"), "schema": ("schema_version", "2.0"),
            "run": ("run_id", "run.historical"), "authorization": ("authorization_ref", "authorization.historical"),
            "record": ("records", [{"raw_stdout": SENTINEL}]), "raw-output": ("raw_stdout", SENTINEL),
        }[kind]
        data[field] = changed
        raw = canonical(data)
    setup.outputs[index] = raw
    value = setup.call()
    assert_failure(outcomes(value)[index], F.CANONICAL_EVIDENCE_VALIDATION_FAILED)
    assert outcomes(value)[1 - index].status == "SUCCESS"
    assert len(setup.calls) == 2
    assert SENTINEL not in value.to_canonical_bytes().decode()


@pytest.mark.parametrize("field,bad", [("query_id", "bad"), ("schema_version", "2.0"),
                                      ("operation_id", "other"), ("execution_order", "PARALLEL")])
def test_invalid_query_rejected_before_preflight_or_target_results(setup, monkeypatch, field, bad):
    object.__setattr__(setup.query, field, bad)
    attempted = []

    def forbidden(*args):
        attempted.append("preflight or result")
        raise AssertionError(SENTINEL)

    monkeypatch.setattr(m, "_preflight", forbidden)
    monkeypatch.setattr(m, "_target_result", forbidden)
    with pytest.raises(d.DualLabContractError) as caught:
        setup.call()
    assert caught.value.args == ("invalid Dual-Lab contract",)
    assert caught.value.__context__ is None and caught.value.__cause__ is None
    assert attempted == [] and setup.calls == []


@pytest.mark.parametrize("bad", [None, {}, b"{}", b'{"query_id":', "query.synthetic"])
def test_top_level_requires_exact_accepted_query_type(setup, bad):
    setup.query = bad
    with pytest.raises(d.DualLabContractError):
        setup.call()
    assert setup.calls == []


def test_configuration_capture_isolated_before_first_invocation(setup, monkeypatch):
    fake = m._invoke_once
    second_config = setup.bundles[1].trusted_configuration

    def mutate_original_during_first(req, env, config):
        if c.parse_stage2_vrrp_request_canonical_json(req).target_ref == LABS[0]:
            object.__setattr__(second_config.known_host_configuration.expected_endpoint, "address", "192.0.2.99")
            object.__setattr__(second_config.credential_configuration, "locator_ref", "locator.invalid")
            object.__setattr__(second_config.replay_ledger_configuration, "expected_ledger_instance_id", "invalid")
        return fake(req, env, config)

    monkeypatch.setattr(m, "_invoke_once", mutate_original_during_first)
    value = setup.call()
    assert value.lab1.status == value.lab2.status == "SUCCESS"
    second = setup.calls[1][2]
    assert second.known_host_configuration.expected_endpoint.address == "192.0.2.2"
    assert second.credential_configuration.locator_ref == "locator.stage2.mikrotik.lab02.readonly"
    assert second.replay_ledger_configuration.expected_ledger_instance_id == "22345678-1234-4234-8234-123456789abc"


@pytest.mark.parametrize("stage", ["construction", "serialize", "reparse"])
def test_final_aggregate_failure_returns_no_partial_output(setup, monkeypatch, stage, capsys):
    def fail(*args, **kwargs):
        raise ValueError(SENTINEL)

    if stage == "construction":
        monkeypatch.setattr(d.DualLabVrrpAggregate, "__post_init__", fail)
    elif stage == "serialize":
        monkeypatch.setattr(d.DualLabVrrpAggregate, "to_canonical_bytes", fail)
    else:
        monkeypatch.setattr(d, "parse_aggregate_canonical_json", fail)
    with pytest.raises(d.DualLabContractError) as caught:
        setup.call()
    assert caught.value.__cause__ is None and caught.value.__context__ is None
    assert caught.value.args == ("invalid Dual-Lab contract",)
    assert len(setup.calls) == 2
    assert capsys.readouterr() == ("", "")
    tb = caught.value.__traceback__
    while tb:
        if tb.tb_frame.f_globals.get("__name__") == m.__name__:
            assert tb.tb_frame.f_code.co_name == "run_dual_lab_vrrp_query"
            for name in ("query", "lab1", "lab2", "result"):
                assert tb.tb_frame.f_locals[name] is None
        tb = tb.tb_next


def test_bundle_immutable_redacted_exact_fields_and_no_leakage(setup, capsys):
    value = setup.call()
    for bundle in setup.bundles:
        assert {f.name for f in fields(bundle)} == {"request_bytes", "envelope_bytes", "trusted_configuration"}
        assert not hasattr(bundle, "__dict__")
        with pytest.raises(FrozenInstanceError):
            bundle.trusted_configuration = None
        assert repr(bundle) == str(bundle) == "DualLabTargetBundle(<trusted-caller-inputs-redacted>)"
        assert bundle.envelope_bytes.decode() not in repr(bundle)
    encoded = value.to_canonical_bytes().decode()
    for bundle in setup.bundles:
        assert json.loads(bundle.envelope_bytes)["authorization_id"] not in encoded
        assert bundle.trusted_configuration.known_host_configuration.expected_path not in encoded
    for field in ("raw_stdout", "password", "authorization_id", "signature", "traceback", "model_output",
                  "health", "healthy", "pair_health", "split_brain", "recommended_action", "remediation",
                  "observation_timestamp", "aggregate_timestamp", "observation_skew_ms", "max_skew_ms",
                  "temporal_health", "simultaneous_snapshot", "replay_consumed"):
        assert f'"{field}":' not in encoded
    assert capsys.readouterr() == ("", "")


def test_exact_public_surface_no_executor_and_no_parallel_or_alternate_path(setup):
    assert m.__all__ == ("DualLabTargetBundle", "run_dual_lab_vrrp_query")
    assert {name for name in vars(m) if not name.startswith("_")} == set(m.__all__)
    sig = inspect.signature(m.run_dual_lab_vrrp_query)
    assert list(sig.parameters) == ["query", "lab1", "lab2"]
    assert all(p.default is inspect.Parameter.empty and p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
               for p in sig.parameters.values())
    for keyword in ("invoke_function", "executor", "runner", "callback"):
        with pytest.raises(TypeError):
            m.run_dual_lab_vrrp_query(setup.query, *setup.bundles, **{keyword: lambda: None})
    assert setup.calls == []
    tree = ast.parse(inspect.getsource(m))
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert imports == {"dataclasses", "validation_framework",
                       "validation_framework.stage2_trusted_runtime_composition",
                       "validation_framework.stage2_vrrp_readonly_live_entrypoint"}
    assert {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names} == {"time"}
    assert not any(isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor,
                                    ast.For, ast.While, ast.ListComp, ast.GeneratorExp))
                   for node in ast.walk(tree))
    calls = [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)]
    assert calls.count("_invoke_once") == 1
    assert not {"open", "exec", "eval", "print", "__import__"} & set(calls)
    handoff = next(node for node in tree.body if isinstance(node, ast.ImportFrom)
                   and node.module.endswith("stage2_vrrp_readonly_live_entrypoint"))
    assert any(alias.name == "run_stage2_vrrp_live_once" and alias.asname == "_invoke_once"
               for alias in handoff.names)
