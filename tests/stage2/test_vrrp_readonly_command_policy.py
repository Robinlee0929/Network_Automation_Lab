"""Synthetic S2-RO-08 policy tests; no credential, transport, or device use."""

import ast
import builtins
import copy
import ctypes
import dataclasses
import inspect
import pickle
import socket
import subprocess

import pytest

from validation_framework import stage2_vrrp_readonly_command_policy as subject
from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpObservationRequest,
    parse_stage2_vrrp_observation_request,
)


Failure = subject.Stage2VrrpCommandPolicyFailure


def request() -> Stage2VrrpObservationRequest:
    return parse_stage2_vrrp_observation_request(
        {
            "schema_version": "1.0",
            "operation_id": "mikrotik.vrrp_status",
            "run_id": "run.stage2.synthetic-0008",
            "target_ref": "target.mikrotik.lab01",
            "credential_ref": "credential.mikrotik.lab01",
            "authorization_ref": "authorization.stage2.synthetic-0008",
            "read_only": True,
        }
    )


def altered_request(**changes) -> Stage2VrrpObservationRequest:
    original = request()
    result = object.__new__(Stage2VrrpObservationRequest)
    for field in dataclasses.fields(original):
        object.__setattr__(
            result,
            field.name,
            changes.get(field.name, getattr(original, field.name)),
        )
    return result


def assert_failure(code: Failure, operation) -> None:
    with pytest.raises(subject.Stage2VrrpCommandPolicyError) as caught:
        operation()
    error = caught.value
    assert error.code is code
    assert error.args == (code.value,)
    assert str(error) == code.value
    assert error.__cause__ is None
    assert error.__context__ is None


@pytest.fixture(autouse=True)
def no_external_or_execution_boundary(monkeypatch):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append("forbidden boundary")
        raise AssertionError("external, credential, transport, or execution boundary used")

    monkeypatch.setattr(ctypes, "WinDLL", forbidden, raising=False)
    for name in (
        "socket",
        "create_connection",
        "getaddrinfo",
        "gethostbyname",
        "gethostbyaddr",
    ):
        monkeypatch.setattr(socket, name, forbidden)
    for name in ("Popen", "run", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, name, forbidden)

    original_import = builtins.__import__
    blocked = (
        "paramiko",
        "ncclient",
        "requests",
        "win32cred",
        "keyring",
        "validation_framework.stage2_windows_credential_backend",
        "validation_framework.stage2_known_host_snapshot",
        "validation_framework.stage2_owner_verifier",
        "validation_framework.stage2_authorization_envelope_ledger",
    )

    def guarded_import(name, *args, **kwargs):
        if any(name == prefix or name.startswith(prefix + ".") for prefix in blocked):
            return forbidden(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    yield
    assert calls == []


def test_exact_public_surface_and_authorized_request_binding():
    assert set(subject.__all__) == {
        "Stage2VrrpCommandPolicyError",
        "Stage2VrrpCommandPolicyFailure",
        "Stage2VrrpReadOnlyCommandSpecification",
        "resolve_stage2_vrrp_readonly_command",
    }
    assert {name for name in vars(subject) if not name.startswith("_")} == set(
        subject.__all__
    )
    assert tuple(
        inspect.signature(subject.resolve_stage2_vrrp_readonly_command).parameters
    ) == ("request",)


def test_exact_request_resolves_one_non_authorizing_command_specification():
    result = subject.resolve_stage2_vrrp_readonly_command(request())

    assert type(result) is subject.Stage2VrrpReadOnlyCommandSpecification
    assert dataclasses.asdict(result) == {
        "schema_version": "s2-ro-08.command-policy.v1",
        "operation_id": "mikrotik.vrrp_status",
        "command_policy_version": "policy.stage2.vrrp-readonly.v1",
        "command_text": "/interface vrrp print detail",
        "read_only": True,
        "execution_authorized": False,
    }
    assert repr(result) == str(result) == (
        "Stage2VrrpReadOnlyCommandSpecification(<offline-policy-only>)"
    )


@pytest.mark.parametrize(
    "operation_id",
    (
        "mikrotik.vrrp",
        "mikrotik.vrrp_status.extra",
        "mikrotik.vrrp-status",
        "Mikrotik.vrrp_status",
        "mikrotik.vrrp_status ",
        "/interface vrrp print detail",
        "default",
    ),
)
def test_unknown_near_match_alias_and_default_requests_fail_closed(operation_id):
    assert_failure(
        Failure.UNKNOWN_REQUEST,
        lambda: subject.resolve_stage2_vrrp_readonly_command(
            altered_request(operation_id=operation_id)
        ),
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("schema_version", "2.0"),
        ("run_id", "run/invalid"),
        ("target_ref", "target"),
        ("credential_ref", "credential.lab.password"),
        ("authorization_ref", "authorization invalid"),
        ("read_only", False),
        ("read_only", 1),
    ),
)
def test_malformed_exact_request_objects_fail_closed(field, value):
    assert_failure(
        Failure.INVALID_REQUEST,
        lambda: subject.resolve_stage2_vrrp_readonly_command(
            altered_request(**{field: value})
        ),
    )


def test_wrong_types_scalar_subclasses_lookalikes_and_subclasses_reject():
    class Text(str):
        pass

    class RequestChild(Stage2VrrpObservationRequest):
        pass

    variants = (
        None,
        {},
        "mikrotik.vrrp_status",
        object(),
        altered_request(operation_id=Text("mikrotik.vrrp_status")),
        RequestChild(**dataclasses.asdict(request())),
        object.__new__(Stage2VrrpObservationRequest),
    )
    for variant in variants:
        assert_failure(
            Failure.INVALID_REQUEST,
            lambda variant=variant: subject.resolve_stage2_vrrp_readonly_command(
                variant
            ),
        )


@pytest.mark.parametrize(
    "bindings",
    (
        (),
        (
            (
                "mikrotik.vrrp_status",
                "policy.stage2.vrrp-readonly.v1",
                "/interface vrrp print detail",
            ),
            (
                "mikrotik.vrrp_status",
                "policy.stage2.vrrp-readonly.v1",
                "/interface vrrp print detail",
            ),
        ),
        (
            (
                "mikrotik.vrrp_status",
                "policy.stage2.vrrp-readonly.v1",
                "/interface/vrrp/set",
            ),
        ),
        {
            "mikrotik.vrrp_status": "/interface vrrp print detail",
        },
    ),
)
def test_missing_duplicate_ambiguous_altered_or_mutable_policy_fails_closed(
    monkeypatch, bindings
):
    monkeypatch.setattr(subject, "_POLICY_BINDINGS", bindings)
    assert_failure(
        Failure.INVALID_POLICY,
        lambda: subject.resolve_stage2_vrrp_readonly_command(request()),
    )


def test_policy_mapping_is_one_exact_immutable_tuple():
    assert subject._POLICY_BINDINGS == (
        (
            "mikrotik.vrrp_status",
            "policy.stage2.vrrp-readonly.v1",
            "/interface vrrp print detail",
        ),
    )
    assert type(subject._POLICY_BINDINGS) is tuple
    assert type(subject._POLICY_BINDINGS[0]) is tuple
    with pytest.raises(TypeError):
        subject._POLICY_BINDINGS[0][2] = "/interface/vrrp/set"


def test_command_and_execution_cannot_be_supplied_or_overridden():
    resolver = subject.resolve_stage2_vrrp_readonly_command
    for kwargs in (
        {"command_text": "/interface/vrrp/set"},
        {"command_text": "/interface vrrp print detail;set disabled=yes"},
        {"execution_authorized": True},
        {"backend": "SSH"},
        {"transport": "SSH"},
        {"mode": "execute"},
    ):
        with pytest.raises(TypeError):
            resolver(request(), **kwargs)
    with pytest.raises(TypeError):
        resolver(request(), "/interface/vrrp/set")


def test_specification_is_immutable_and_all_fabrication_routes_are_blocked():
    result = subject.resolve_stage2_vrrp_readonly_command(request())
    assert not hasattr(result, "__dict__")
    for field in dataclasses.fields(result):
        with pytest.raises((AttributeError, TypeError)):
            setattr(result, field.name, True)
        with pytest.raises((AttributeError, TypeError)):
            delattr(result, field.name)

    operations = (
        lambda: subject.Stage2VrrpReadOnlyCommandSpecification(),
        lambda: subject.Stage2VrrpReadOnlyCommandSpecification(
            **dataclasses.asdict(result)
        ),
        lambda: type(
            "Child", (subject.Stage2VrrpReadOnlyCommandSpecification,), {}
        ),
        lambda: copy.copy(result),
        lambda: copy.deepcopy(result),
        lambda: dataclasses.replace(result),
        lambda: pickle.dumps(result),
        lambda: result.__reduce__(),
        lambda: result.__reduce_ex__(5),
        lambda: result.__getstate__(),
        lambda: result.__setstate__(dataclasses.asdict(result)),
        lambda: result.__init__(),
    )
    for operation in operations:
        with pytest.raises(TypeError):
            operation()


def test_no_alias_default_fallback_discovery_enumeration_or_registration_surface():
    forbidden = {
        "add",
        "alias",
        "all",
        "default",
        "discover",
        "enumerate",
        "execute",
        "fallback",
        "get",
        "items",
        "keys",
        "list",
        "register",
        "run",
        "send",
        "set",
        "values",
    }
    assert forbidden.isdisjoint(set(subject.__all__))
    assert not hasattr(subject, "main")
    assert not hasattr(subject, "connect")


def test_resolution_reaches_no_external_credential_transport_or_execution_boundary():
    result = subject.resolve_stage2_vrrp_readonly_command(request())
    assert result.command_text == "/interface vrrp print detail"
    assert result.execution_authorized is False


def test_source_has_only_offline_standard_library_and_s2_ro_01_dependency():
    tree = ast.parse(inspect.getsource(subject))
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imports == {"dataclasses", "enum", "validation_framework"}

    forbidden_imports = {
        "ctypes",
        "dns",
        "io",
        "keyring",
        "ncclient",
        "os",
        "paramiko",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "tempfile",
        "win32cred",
    }
    assert forbidden_imports.isdisjoint(imports)

    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    assert {"connect", "execute", "run", "send"}.isdisjoint(function_names)
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert {"open", "eval", "exec", "compile", "__import__"}.isdisjoint(
        called_names
    )


def test_error_requires_an_exact_bounded_category():
    with pytest.raises(TypeError):
        subject.Stage2VrrpCommandPolicyError("rejected request detail")

@pytest.mark.parametrize('command', [
    '/interface/vrrp/print', '/interface vrrp print detail suffix',
    'prefix /interface vrrp print detail', '/interface vrrp print detail\n',
    '/interface vrrp print detail\r', '/interface vrrp print detail;set x=y',
    '/interface vrrp print detail|x', '/interface vrrp print detail>x',
    '/interface vrrp set disabled=yes',
])
def test_explicit_command_override_rejection(command):
    with pytest.raises(TypeError):
        subject.resolve_stage2_vrrp_readonly_command(request(), command_text=command)


def test_command_constant_and_binding_cannot_drift_together(monkeypatch):
    monkeypatch.setattr(subject, '_COMMAND_TEXT', 'wrong')
    monkeypatch.setattr(subject, '_POLICY_BINDINGS', (
        ('mikrotik.vrrp_status', 'policy.stage2.vrrp-readonly.v1', 'wrong'),
    ))
    assert_failure(Failure.INVALID_POLICY,
                   lambda: subject.resolve_stage2_vrrp_readonly_command(request()))
