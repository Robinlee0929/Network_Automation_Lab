"""Offline tests for the S2-RO-02 fixed target registry."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
import inspect

import pytest

from validation_framework import stage2_mikrotik_target_registry as module
from validation_framework.stage2_mikrotik_target_registry import (
    STAGE2_FIXED_SSH_PORT,
    STAGE2_FIXED_TARGET_REF,
    STAGE2_FIXED_TRANSPORT,
    Stage2FixedTargetEndpoint,
    Stage2FixedTargetRegistry,
    Stage2TargetRegistryError,
    Stage2TargetRegistryFailure,
    parse_stage2_fixed_target_registry,
)
from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpContractError,
    parse_stage2_vrrp_observation_request,
)


def _record(**changes):
    result = {
        "target_ref": "target.mikrotik.lab01",
        "address": "192.0.2.10",
        "port": 22,
        "transport": "SSH",
        "declared_lab_only": True,
    }
    result.update(changes)
    return result


def _request(**changes):
    result = {
        "schema_version": "1.0",
        "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.stage2.synthetic-0002",
        "target_ref": STAGE2_FIXED_TARGET_REF,
        "credential_ref": "credential.mikrotik.lab01.readonly",
        "authorization_ref": "authorization.stage2.owner-gate",
        "read_only": True,
    }
    result.update(changes)
    return result


def _assert_error(function, argument, code):
    with pytest.raises(Stage2TargetRegistryError) as error:
        function(argument)
    assert error.value.code is code
    assert str(error.value) == code.value


def test_exact_known_target_resolves_to_one_fixed_endpoint_deterministically():
    registry = parse_stage2_fixed_target_registry(_record())
    endpoint = registry.lookup(STAGE2_FIXED_TARGET_REF)

    assert endpoint is registry.lookup(STAGE2_FIXED_TARGET_REF)
    assert endpoint == Stage2FixedTargetEndpoint(**_record())
    assert endpoint.target_ref == "target.mikrotik.lab01"
    assert endpoint.address == "192.0.2.10"
    assert endpoint.port == STAGE2_FIXED_SSH_PORT == 22
    assert endpoint.transport == STAGE2_FIXED_TRANSPORT == "SSH"
    assert endpoint.declared_lab_only is True
    assert {item.name for item in fields(endpoint)} == set(_record())


def test_registry_and_endpoint_are_frozen_slotted_and_address_safe_in_repr():
    registry = parse_stage2_fixed_target_registry(_record())
    endpoint = registry.lookup(STAGE2_FIXED_TARGET_REF)

    with pytest.raises(FrozenInstanceError):
        endpoint.port = 2222
    with pytest.raises(FrozenInstanceError):
        registry._endpoint = endpoint
    with pytest.raises(Stage2TargetRegistryError):
        replace(endpoint, port=2222)
    assert not hasattr(endpoint, "__dict__")
    assert not hasattr(registry, "__dict__")
    assert "192.0.2.10" not in repr(endpoint)
    assert "192.0.2.10" not in repr(registry)


@pytest.mark.parametrize(
    "target_ref",
    [
        "target.mikrotik.lab02",
        "target.mikrotik",
        "target.mikrotik.lab01.extra",
        "target.other.lab01",
    ],
)
def test_valid_but_unknown_near_prefix_suffix_targets_fail_closed(target_ref):
    registry = parse_stage2_fixed_target_registry(_record())
    _assert_error(
        registry.lookup,
        target_ref,
        Stage2TargetRegistryFailure.UNKNOWN_TARGET,
    )


@pytest.mark.parametrize(
    "target_ref",
    [
        "TARGET.MIKROTIK.LAB01",
        " target.mikrotik.lab01",
        "target.mikrotik.lab01 ",
        "target.mikrotik/lab01",
        "target",
        "",
        None,
        1,
        True,
    ],
)
def test_noncanonical_or_invalid_target_references_fail_closed(target_ref):
    registry = parse_stage2_fixed_target_registry(_record())
    _assert_error(
        registry.lookup,
        target_ref,
        Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE,
    )


@pytest.mark.parametrize(
    "address",
    [
        "router.example",
        "192.0.2",
        "192.0.2.999",
        "192.000.2.10",
        "192.0.2.10:22",
        "192.0.2.10/24",
        "ssh://192.0.2.10",
        " 192.0.2.10",
        "192.0.2.10 ",
        "192.0.2.10\n",
        "2001:db8::10",
        "[2001:db8::10]",
        "C:\\synthetic\\host",
        "",
        None,
        3221225994,
        True,
    ],
)
def test_only_canonical_plain_ipv4_literals_are_accepted(address):
    _assert_error(
        parse_stage2_fixed_target_registry,
        _record(address=address),
        Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION,
    )


@pytest.mark.parametrize("port", [0, 23, 2222, "22", 22.0, True, None])
def test_port_is_exact_integer_22_and_cannot_be_overridden(port):
    _assert_error(
        parse_stage2_fixed_target_registry,
        _record(port=port),
        Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION,
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("transport", "ssh"),
        ("transport", "NETCONF"),
        ("transport", "RESTCONF"),
        ("transport", None),
        ("declared_lab_only", False),
        ("declared_lab_only", 1),
        ("target_ref", "target.mikrotik.lab02"),
    ],
)
def test_other_fixed_endpoint_policy_fields_cannot_be_overridden(field_name, value):
    _assert_error(
        parse_stage2_fixed_target_registry,
        _record(**{field_name: value}),
        Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION,
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "hostname",
        "username",
        "credential_ref",
        "password",
        "host_key",
        "known_hosts_path",
        "fallback",
        "alternate_address",
        "command",
        "timeout",
    ],
)
def test_unknown_credential_trust_fallback_and_execution_fields_reject(field_name):
    _assert_error(
        parse_stage2_fixed_target_registry,
        _record(**{field_name: "synthetic-rejected"}),
        Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION,
    )


@pytest.mark.parametrize(
    "raw_data",
    [
        None,
        {},
        [],
        [_record()],
        [_record(), _record()],
        {"targets": [_record()]},
        "synthetic.json",
    ],
)
def test_collections_duplicates_discovery_and_non_records_are_unsupported(raw_data):
    _assert_error(
        parse_stage2_fixed_target_registry,
        raw_data,
        Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION,
    )


def test_plain_record_input_is_isolated_and_registry_has_no_mutation_api():
    raw_data = _record()
    registry = parse_stage2_fixed_target_registry(raw_data)
    raw_data.update(address="198.51.100.20", port=2222, fallback="203.0.113.30")

    endpoint = registry.lookup(STAGE2_FIXED_TARGET_REF)
    assert endpoint.address == "192.0.2.10"
    assert endpoint.port == 22
    for name in ("add", "register", "remove", "replace", "update", "default"):
        assert not hasattr(registry, name)


def test_s2_ro_01_request_composes_only_through_exact_target_ref():
    registry = parse_stage2_fixed_target_registry(_record())
    request = parse_stage2_vrrp_observation_request(_request())
    assert registry.lookup(request.target_ref).target_ref == request.target_ref

    unknown_request = parse_stage2_vrrp_observation_request(
        _request(target_ref="target.mikrotik.lab02")
    )
    _assert_error(
        registry.lookup,
        unknown_request.target_ref,
        Stage2TargetRegistryFailure.UNKNOWN_TARGET,
    )
    with pytest.raises(Stage2VrrpContractError):
        parse_stage2_vrrp_observation_request(
            _request(target_ref=" target.mikrotik.lab01")
        )


def test_request_cannot_supply_or_override_endpoint_data():
    registry = parse_stage2_fixed_target_registry(_record())
    request = parse_stage2_vrrp_observation_request(_request())

    with pytest.raises(TypeError):
        registry.lookup(request.target_ref, address="198.51.100.20")
    with pytest.raises(Stage2VrrpContractError):
        parse_stage2_vrrp_observation_request(
            _request(address="198.51.100.20")
        )
    assert registry.lookup(request.target_ref).address == "192.0.2.10"


def test_module_has_no_external_boundary_or_live_runtime_surface():
    tree = ast.parse(inspect.getsource(module))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    forbidden_imports = {
        "ctypes",
        "dns",
        "io",
        "keyring",
        "os",
        "paramiko",
        "pathlib",
        "requests",
        "socket",
        "subprocess",
        "win32cred",
    }
    assert forbidden_imports.isdisjoint(imported_roots)
    called_builtins = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "open" not in called_builtins
    for name in (
        "main",
        "connect",
        "execute",
        "resolve_dns",
        "resolve_credential",
        "load_known_hosts",
    ):
        assert not hasattr(module, name)
