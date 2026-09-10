"""Offline tests for the S2-RO-02 fixed target registry."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
import inspect

import pytest

from validation_framework import stage2_mikrotik_target_registry as module
from validation_framework.stage2_mikrotik_target_registry import (
    STAGE2_FIXED_SSH_PORT,
    STAGE2_FIXED_TARGET_REF,
    STAGE2_SECOND_TARGET_REF,
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


def _pair():
    return [
        _record(),
        _record(target_ref=STAGE2_SECOND_TARGET_REF, address="198.51.100.20"),
    ]


@pytest.mark.parametrize("reverse", [False, True])
def test_complete_pair_resolves_only_its_own_endpoints_in_either_input_order(reverse):
    records = _pair()
    registry = parse_stage2_fixed_target_registry(records[::-1] if reverse else records)
    first = registry.lookup(STAGE2_FIXED_TARGET_REF)
    second = registry.lookup(STAGE2_SECOND_TARGET_REF)
    assert first == Stage2FixedTargetEndpoint(**records[0])
    assert second == Stage2FixedTargetEndpoint(**records[1])
    assert first is registry._endpoint
    assert second is registry.lookup(STAGE2_SECOND_TARGET_REF)
    assert first is not second
    assert first.target_ref != second.target_ref
    assert first.address != second.address
    request = parse_stage2_vrrp_observation_request(
        _request(target_ref=STAGE2_SECOND_TARGET_REF)
    )
    assert registry.lookup(request.target_ref) is second


@pytest.mark.parametrize(
    "target_ref,code",
    [
        ("target.mikrotik.lab03", Stage2TargetRegistryFailure.UNKNOWN_TARGET),
        ("target.mikrotik.lab2", Stage2TargetRegistryFailure.UNKNOWN_TARGET),
        ("target.mikrotik", Stage2TargetRegistryFailure.UNKNOWN_TARGET),
        ("target.mikrotik.lab02.extra", Stage2TargetRegistryFailure.UNKNOWN_TARGET),
        ("TARGET.MIKROTIK.LAB02", Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
        ("target.mikrotik.lab02 ", Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
        ("target.mikrotik.*", Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
        ("target.mikrotik/lab02", Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
        (None, Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
        ({"target_ref": STAGE2_SECOND_TARGET_REF}, Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE),
    ],
)
def test_pair_rejections_stop_before_downstream_handoff(target_ref, code):
    registry = parse_stage2_fixed_target_registry(_pair())
    downstream = []

    def resolve_then_handoff(value):
        endpoint = registry.lookup(value)
        downstream.append(endpoint)

    _assert_error(resolve_then_handoff, target_ref, code)
    assert downstream == []


@pytest.mark.parametrize(
    "records",
    [
        [], [_pair()[0]], [_pair()[1]],
        [_pair()[0], _pair()[0]], [_pair()[1], _pair()[1]],
        _pair() + [_record(target_ref="target.mikrotik.lab03")],
        [_pair()[0], _record(target_ref="target.mikrotik.lab03")],
        [_pair()[0], None], [_pair()[0], {}],
        tuple(_pair()), {"targets": _pair()},
        [_pair()[0], _record(target_ref=STAGE2_SECOND_TARGET_REF)],
    ],
)
def test_pair_rejects_missing_duplicate_third_wrapped_and_shared_endpoints(records):
    _assert_error(parse_stage2_fixed_target_registry, records,
                  Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION)


@pytest.mark.parametrize(
    "changes",
    [
        {"address": "router.example"}, {"address": "198.051.100.20"},
        {"address": "2001:db8::20"}, {"port": 2222}, {"port": True},
        {"transport": "NETCONF"}, {"transport": "ssh"},
        {"declared_lab_only": False}, {"declared_lab_only": 1},
        {"target_ref": "target.mikrotik.lab2"},
        {"target_ref": "TARGET.MIKROTIK.LAB02"},
        {"fallback": "192.0.2.10"}, {"credential_ref": "synthetic-rejected"},
    ],
)
def test_lab2_preserves_all_endpoint_policy_gates(changes):
    records = _pair()
    records[1].update(changes)
    _assert_error(parse_stage2_fixed_target_registry, records,
                  Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION)


def test_pair_is_frozen_isolated_redacted_and_has_no_registration_surface():
    records = _pair()
    registry = parse_stage2_fixed_target_registry(records)
    second = registry.lookup(STAGE2_SECOND_TARGET_REF)
    records[1]["address"] = "203.0.113.30"
    records.clear()
    assert second.address == "198.51.100.20"
    with pytest.raises(FrozenInstanceError):
        registry._lab2_endpoint = registry._endpoint
    with pytest.raises(FrozenInstanceError):
        second.address = "203.0.113.30"
    assert not hasattr(registry, "__dict__")
    assert not hasattr(second, "__dict__")
    assert "198.51.100.20" not in repr(second) + repr(registry)
    for name in ("add", "register", "remove", "replace", "update", "default"):
        assert not hasattr(registry, name)


@pytest.mark.parametrize("field_name", ["address", "hostname", "port", "transport"])
def test_lab2_request_and_lookup_cannot_override_endpoint(field_name):
    registry = parse_stage2_fixed_target_registry(_pair())
    with pytest.raises(TypeError):
        registry.lookup(STAGE2_SECOND_TARGET_REF, **{field_name: "synthetic-rejected"})
    with pytest.raises(Stage2VrrpContractError):
        parse_stage2_vrrp_observation_request(
            _request(target_ref=STAGE2_SECOND_TARGET_REF,
                     **{field_name: "synthetic-rejected"})
        )
    assert registry.lookup(STAGE2_SECOND_TARGET_REF).address == "198.51.100.20"


def test_direct_construction_preserves_lab1_capture_without_promoting_lab2():
    first, second = (Stage2FixedTargetEndpoint(**record) for record in _pair())
    pair = Stage2FixedTargetRegistry(first, second)
    legacy = Stage2FixedTargetRegistry(pair._endpoint)
    assert legacy.lookup(STAGE2_FIXED_TARGET_REF) is first
    assert repr(legacy) == "Stage2FixedTargetRegistry(<one-fixed-target>)"
    _assert_error(legacy.lookup, STAGE2_SECOND_TARGET_REF,
                  Stage2TargetRegistryFailure.UNKNOWN_TARGET)
    for args in ((second,), (second, first), (first, first), (None, second),
                 (first, {})):
        with pytest.raises(Stage2TargetRegistryError) as error:
            Stage2FixedTargetRegistry(*args)
        assert str(error.value) == "INVALID_REGISTRY_CONFIGURATION"
