"""Offline tests for the S2-RO-03 credential resolver."""

import ast
from dataclasses import FrozenInstanceError, fields, replace
import inspect

import pytest

from validation_framework import stage2_mikrotik_credential_resolver as module
from validation_framework.stage2_mikrotik_credential_resolver import (
    STAGE2_CREDENTIAL_BACKEND_KIND,
    STAGE2_CREDENTIAL_LOCATOR_REF,
    STAGE2_FIXED_CREDENTIAL_REF,
    STAGE2_SECOND_CREDENTIAL_REF,
    STAGE2_SECOND_CREDENTIAL_LOCATOR_REF,
    Stage2CredentialBinding,
    Stage2CredentialResolverError,
    Stage2CredentialResolverFailure,
    Stage2FixedCredentialResolver,
    build_stage2_fixed_credential_resolver,
)
from validation_framework.stage2_mikrotik_target_registry import (
    STAGE2_FIXED_TARGET_REF,
    STAGE2_SECOND_TARGET_REF,
    parse_stage2_fixed_target_registry,
)
from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpObservationRequest,
    parse_stage2_vrrp_observation_request,
)


def _request(**changes):
    result = {
        "schema_version": "1.0",
        "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.stage2.synthetic-0003",
        "target_ref": "target.mikrotik.lab01",
        "credential_ref": STAGE2_FIXED_CREDENTIAL_REF,
        "authorization_ref": "authorization.stage2.owner-gate",
        "read_only": True,
    }
    result.update(changes)
    return result


def _target_record():
    return {
        "target_ref": "target.mikrotik.lab01",
        "address": "192.0.2.10",
        "port": 22,
        "transport": "SSH",
        "declared_lab_only": True,
    }


def _assert_error(function, argument, code):
    with pytest.raises(Stage2CredentialResolverError) as error:
        function(argument)
    assert error.value.code is code
    assert str(error.value) == code.value
    assert repr(error.value) == (
        f"Stage2CredentialResolverError('{code.value}')"
    )


def test_public_surface_and_fixed_policy_constants_are_exact():
    assert set(module.__all__) == {
        "STAGE2_CREDENTIAL_BACKEND_KIND",
        "STAGE2_CREDENTIAL_LOCATOR_REF",
        "STAGE2_FIXED_CREDENTIAL_REF",
        "STAGE2_SECOND_CREDENTIAL_REF",
        "STAGE2_SECOND_CREDENTIAL_LOCATOR_REF",
        "Stage2CredentialBinding",
        "Stage2CredentialResolverError",
        "Stage2CredentialResolverFailure",
        "Stage2FixedCredentialResolver",
        "build_stage2_fixed_credential_resolver",
    }
    assert STAGE2_FIXED_CREDENTIAL_REF == "credential.mikrotik.lab01"
    assert STAGE2_CREDENTIAL_BACKEND_KIND == "WINDOWS_CREDENTIAL_MANAGER"
    assert STAGE2_CREDENTIAL_LOCATOR_REF == (
        "locator.stage2.mikrotik.lab01.readonly"
    )
    assert inspect.signature(build_stage2_fixed_credential_resolver).parameters == {}


def test_known_credential_resolves_to_one_deterministic_non_secret_binding():
    resolver = build_stage2_fixed_credential_resolver()
    binding = resolver.resolve(STAGE2_FIXED_CREDENTIAL_REF)

    assert binding is resolver.resolve(STAGE2_FIXED_CREDENTIAL_REF)
    assert binding == build_stage2_fixed_credential_resolver().resolve(
        STAGE2_FIXED_CREDENTIAL_REF
    )
    assert binding.credential_ref == STAGE2_FIXED_CREDENTIAL_REF
    assert binding.backend_kind == STAGE2_CREDENTIAL_BACKEND_KIND
    assert binding.locator_ref == STAGE2_CREDENTIAL_LOCATOR_REF
    assert {item.name for item in fields(binding)} == {
        "credential_ref",
        "backend_kind",
        "locator_ref",
    }


def test_resolver_and_binding_are_frozen_slotted_and_safe_in_repr():
    resolver = build_stage2_fixed_credential_resolver()
    binding = resolver.resolve(STAGE2_FIXED_CREDENTIAL_REF)

    with pytest.raises(FrozenInstanceError):
        binding.locator_ref = "locator.stage2.other"
    with pytest.raises(FrozenInstanceError):
        resolver._binding = binding
    with pytest.raises(Stage2CredentialResolverError):
        replace(binding, backend_kind="OTHER_BACKEND")

    assert not hasattr(binding, "__dict__")
    assert not hasattr(resolver, "__dict__")
    assert STAGE2_CREDENTIAL_LOCATOR_REF not in repr(binding)
    assert STAGE2_CREDENTIAL_LOCATOR_REF not in repr(resolver)
    assert repr(binding) == "Stage2CredentialBinding(<fixed-non-secret-binding>)"
    assert repr(resolver) == "Stage2FixedCredentialResolver(<two-fixed-bindings>)"


@pytest.mark.parametrize(
    "credential_ref",
    [
        "credential.mikrotik.lab02",
        "credential.mikrotik",
        "credential.mikrotik.lab01.readonly",
        "credential.mikrotik.lab0l",
        "credential.other.lab01",
    ],
)
def test_valid_but_unknown_prefix_suffix_and_near_matches_fail_closed(
    credential_ref,
):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        resolver.resolve,
        credential_ref,
        Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL,
    )


@pytest.mark.parametrize(
    "credential_ref",
    [
        "CREDENTIAL.MIKROTIK.LAB01",
        " credential.mikrotik.lab01",
        "credential.mikrotik.lab01 ",
        "credential.mikrotik.\nlab01",
        "credential.mikrotik/../lab01",
        "credential\\mikrotik\\lab01",
        "credential://mikrotik/lab01",
        "credential.mikrotik.lab01;echo",
        "credential.mikrotik.$(lab01)",
        "credential.mikrotik.*",
        "credential",
        "credential.",
        ".credential.mikrotik.lab01",
        "",
        None,
        True,
        1,
        b"credential.mikrotik.lab01",
        "credential." + "a" * 160,
    ],
)
def test_malformed_path_uri_shell_control_and_wrong_type_values_reject(
    credential_ref,
):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        resolver.resolve,
        credential_ref,
        Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE,
    )


@pytest.mark.parametrize(
    "credential_ref",
    [
        "credential.mikrotik.password",
        "credential.mikrotik.passphrase",
        "credential.mikrotik.private_key",
        "credential.mikrotik.api-key",
        "credential.mikrotik.token",
        "credential.mikrotik.username",
        "credential.secret.lab01",
    ],
)
def test_secret_material_like_logical_references_reject(credential_ref):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        resolver.resolve,
        credential_ref,
        Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE,
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("credential_ref", "credential.mikrotik.lab02"),
        ("credential_ref", None),
        ("backend_kind", "OTHER_BACKEND"),
        ("backend_kind", None),
        ("locator_ref", "locator.stage2.mikrotik.lab02.readonly"),
        ("locator_ref", None),
    ],
)
def test_callers_cannot_construct_alternate_backend_or_locator(field_name, value):
    values = {
        "credential_ref": STAGE2_FIXED_CREDENTIAL_REF,
        "backend_kind": STAGE2_CREDENTIAL_BACKEND_KIND,
        "locator_ref": STAGE2_CREDENTIAL_LOCATOR_REF,
    }
    values[field_name] = value
    with pytest.raises(Stage2CredentialResolverError) as error:
        Stage2CredentialBinding(**values)
    assert error.value.code is (
        Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION
    )


@pytest.mark.parametrize("binding", [None, {}, object(), "credential"])
def test_resolver_rejects_any_non_binding_configuration(binding):
    with pytest.raises(Stage2CredentialResolverError) as error:
        Stage2FixedCredentialResolver(binding)
    assert error.value.code is (
        Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION
    )


def test_valid_s2_ro_01_request_composes_without_mutation_or_retrieval():
    request = parse_stage2_vrrp_observation_request(_request())
    before = request.to_canonical_bytes()
    resolver = build_stage2_fixed_credential_resolver()

    binding = resolver.resolve(request.credential_ref)

    assert type(request) is Stage2VrrpObservationRequest
    assert request.to_canonical_bytes() == before
    assert binding.credential_ref == request.credential_ref
    assert not hasattr(binding, "username")
    assert not hasattr(binding, "password")
    assert not hasattr(binding, "secret")
    assert not hasattr(binding, "credential")


def test_unknown_s2_ro_01_credential_fails_before_any_backend_boundary():
    request = parse_stage2_vrrp_observation_request(
        _request(credential_ref="credential.mikrotik.lab02")
    )
    resolver = build_stage2_fixed_credential_resolver()

    _assert_error(
        resolver.resolve,
        request.credential_ref,
        Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL,
    )


def test_resolution_depends_only_on_credential_ref_not_target_identity():
    first = parse_stage2_vrrp_observation_request(_request())
    second = parse_stage2_vrrp_observation_request(
        _request(target_ref="target.mikrotik.lab99")
    )
    resolver = build_stage2_fixed_credential_resolver()

    assert resolver.resolve(first.credential_ref) is resolver.resolve(
        second.credential_ref
    )
    assert list(inspect.signature(resolver.resolve).parameters) == [
        "credential_ref"
    ]


def test_s2_ro_02_endpoint_authority_remains_separate_and_unchanged():
    registry = parse_stage2_fixed_target_registry(_target_record())
    endpoint = registry.lookup("target.mikrotik.lab01")
    before = (endpoint.target_ref, endpoint.address, endpoint.port, endpoint.transport)

    build_stage2_fixed_credential_resolver().resolve(STAGE2_FIXED_CREDENTIAL_REF)

    assert (endpoint.target_ref, endpoint.address, endpoint.port, endpoint.transport) == (
        before
    )
    assert {item.name for item in fields(Stage2CredentialBinding)}.isdisjoint(
        {"target_ref", "address", "port", "transport", "host_key"}
    )


def test_no_default_alias_fallback_discovery_enumeration_or_mutation_api():
    resolver = build_stage2_fixed_credential_resolver()
    forbidden_names = {
        "add",
        "aliases",
        "all",
        "default",
        "discover",
        "enumerate",
        "fallback",
        "get",
        "items",
        "keys",
        "list",
        "register",
        "reload",
        "remove",
        "set",
        "update",
        "values",
    }
    assert forbidden_names.isdisjoint(set(dir(resolver)))
    assert list(inspect.signature(resolver.resolve).parameters) == [
        "credential_ref"
    ]


def test_binding_contains_only_synthetic_non_secret_text():
    binding = build_stage2_fixed_credential_resolver().resolve(
        STAGE2_FIXED_CREDENTIAL_REF
    )
    field_names = {item.name for item in fields(binding)}
    forbidden_field_names = {
        "api_key",
        "credential",
        "otp",
        "passphrase",
        "password",
        "private_key",
        "secret",
        "token",
        "username",
        "windows_credential_target",
    }
    assert field_names.isdisjoint(forbidden_field_names)
    assert all(type(getattr(binding, name)) is str for name in field_names)
    assert not any(
        token in getattr(binding, name).lower()
        for name in field_names
        for token in ("password=", "token=", "secret=", "private key")
    )


def test_serialization_and_external_capabilities_are_absent():
    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    forbidden_imports = {
        "ctypes",
        "json",
        "keyring",
        "os",
        "paramiko",
        "pathlib",
        "requests",
        "socket",
        "subprocess",
        "win32cred",
        "winreg",
    }
    assert imported_roots.isdisjoint(forbidden_imports)
    assert not any(
        isinstance(node, ast.Name) and node.id in {"open", "exec", "eval"}
        for node in ast.walk(tree)
    )
    assert not hasattr(Stage2CredentialBinding, "to_dict")
    assert not hasattr(Stage2CredentialBinding, "to_json")
    assert not hasattr(Stage2FixedCredentialResolver, "from_file")
    assert not hasattr(Stage2FixedCredentialResolver, "from_environment")


def test_backend_kind_is_declarative_identity_not_credential_retrieval():
    resolver = build_stage2_fixed_credential_resolver()
    binding = resolver.resolve(STAGE2_FIXED_CREDENTIAL_REF)

    assert binding.backend_kind == "WINDOWS_CREDENTIAL_MANAGER"
    assert set(vars(module)).isdisjoint(
        {
            "Credential",
            "get_credential",
            "load_credential",
            "read_credential",
            "resolve_username",
            "retrieve_credential",
            "win32cred",
        }
    )


def test_exact_two_target_pairs_have_distinct_fixed_credential_authority():
    resolver = build_stage2_fixed_credential_resolver()
    lab1 = resolver.resolve_for_target(
        STAGE2_FIXED_TARGET_REF, STAGE2_FIXED_CREDENTIAL_REF
    )
    lab2 = resolver.resolve_for_target(
        STAGE2_SECOND_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF
    )

    assert lab1 is resolver.resolve(STAGE2_FIXED_CREDENTIAL_REF)
    assert lab2 is resolver.resolve_for_target(
        STAGE2_SECOND_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF
    )
    assert lab1.credential_ref == "credential.mikrotik.lab01"
    assert lab2.credential_ref == "credential.mikrotik.lab02"
    assert lab2.locator_ref == "locator.stage2.mikrotik.lab02.readonly"
    assert lab1.credential_ref != lab2.credential_ref
    assert lab1.locator_ref != lab2.locator_ref
    assert lab1.backend_kind == lab2.backend_kind == STAGE2_CREDENTIAL_BACKEND_KIND
    assert lab2 == build_stage2_fixed_credential_resolver().resolve_for_target(
        STAGE2_SECOND_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF
    )
    assert {item.name for item in fields(lab2)} == {
        "credential_ref", "backend_kind", "locator_ref"
    }


@pytest.mark.parametrize(
    "target_ref,credential_ref",
    [
        (STAGE2_FIXED_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF),
        (STAGE2_SECOND_TARGET_REF, STAGE2_FIXED_CREDENTIAL_REF),
    ],
)
def test_cross_lab_pair_rejects_before_any_downstream_boundary(
    target_ref, credential_ref,
):
    resolver = build_stage2_fixed_credential_resolver()
    downstream_calls = []

    def resolve_then_forward(reference):
        binding = resolver.resolve_for_target(target_ref, reference)
        downstream_calls.append(binding)

    _assert_error(
        resolve_then_forward, credential_ref,
        Stage2CredentialResolverFailure.TARGET_CREDENTIAL_MISMATCH,
    )
    assert downstream_calls == []


@pytest.mark.parametrize("credential_ref", [
    STAGE2_FIXED_CREDENTIAL_REF, STAGE2_SECOND_CREDENTIAL_REF,
])
@pytest.mark.parametrize("target_ref", [
    "target.mikrotik.lab03", "target.mikrotik", "target.mikrotik.lab0l",
    "target.mikrotik.lab01.readonly", "target.mikrotik.lab02.readonly",
    "target.other.lab02",
])
def test_target_aware_unknown_third_alias_prefix_and_suffix_reject(
    target_ref, credential_ref,
):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        lambda value: resolver.resolve_for_target(value, credential_ref),
        target_ref, Stage2CredentialResolverFailure.UNKNOWN_TARGET,
    )


@pytest.mark.parametrize("target_ref", [
    "TARGET.MIKROTIK.LAB02", " target.mikrotik.lab01", "target.mikrotik.lab02 ",
    "target.mikrotik.*", "target.mikrotik/../lab02", "target.mikrotik.lab02\n",
    "target://mikrotik/lab02", "target." + "a" * 160,
    "target.mikrotik.l\u0430b02", "", None, True, 1, {}, b"target.mikrotik.lab02",
])
def test_target_aware_malformed_targets_have_sanitized_failures(target_ref):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        lambda value: resolver.resolve_for_target(value, STAGE2_SECOND_CREDENTIAL_REF),
        target_ref, Stage2CredentialResolverFailure.INVALID_TARGET_REFERENCE,
    )


@pytest.mark.parametrize("target_ref", [STAGE2_FIXED_TARGET_REF, STAGE2_SECOND_TARGET_REF])
@pytest.mark.parametrize("credential_ref", [
    "credential.mikrotik.lab03", "credential.mikrotik", "credential.mikrotik.lab0l",
    "credential.mikrotik.lab01.readonly", "credential.mikrotik.lab02.readonly",
])
def test_target_aware_unknown_credential_cannot_override_binding(target_ref, credential_ref):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        lambda value: resolver.resolve_for_target(target_ref, value),
        credential_ref, Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL,
    )


@pytest.mark.parametrize("target_ref", [STAGE2_FIXED_TARGET_REF, STAGE2_SECOND_TARGET_REF])
@pytest.mark.parametrize("credential_ref", [
    "CREDENTIAL.MIKROTIK.LAB02", " credential.mikrotik.lab02",
    "credential.mikrotik.lab02 ", "credential.mikrotik.lab02\n",
    "credential.mikrotik.*", "credential.mikrotik/../lab02",
    "credential.mikrotik.password", "credential.mikrotik.l\u0430b02",
    "", None, True, 1, {}, b"credential.mikrotik.lab02",
])
def test_target_aware_malformed_credentials_have_sanitized_failures(
    target_ref, credential_ref,
):
    resolver = build_stage2_fixed_credential_resolver()
    _assert_error(
        lambda value: resolver.resolve_for_target(target_ref, value),
        credential_ref, Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE,
    )


def test_two_binding_configuration_is_immutable_and_has_no_override_or_default():
    resolver = build_stage2_fixed_credential_resolver()
    lab2 = resolver.resolve_for_target(STAGE2_SECOND_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF)
    with pytest.raises(FrozenInstanceError):
        resolver._lab2_binding = resolver._binding
    with pytest.raises(FrozenInstanceError):
        lab2.credential_ref = STAGE2_FIXED_CREDENTIAL_REF
    with pytest.raises(Stage2CredentialResolverError):
        Stage2FixedCredentialResolver(lab2)
    with pytest.raises(TypeError):
        Stage2FixedCredentialResolver(resolver._binding, _lab2_binding=lab2)
    with pytest.raises(TypeError):
        resolver.resolve_for_target(STAGE2_SECOND_TARGET_REF)
    with pytest.raises(TypeError):
        resolver.resolve_for_target(
            STAGE2_SECOND_TARGET_REF, STAGE2_SECOND_CREDENTIAL_REF,
            locator_ref=STAGE2_CREDENTIAL_LOCATOR_REF,
        )
    parameters = inspect.signature(resolver.resolve_for_target).parameters
    assert list(parameters) == ["target_ref", "credential_ref"]
    assert all(item.default is inspect.Parameter.empty for item in parameters.values())
    assert not hasattr(lab2, "__dict__")
    assert lab2.locator_ref not in repr(lab2) + repr(resolver)
    assert lab2.credential_ref not in repr(lab2) + repr(resolver)


@pytest.mark.parametrize("credential_ref,locator_ref", [
    (STAGE2_FIXED_CREDENTIAL_REF, STAGE2_SECOND_CREDENTIAL_LOCATOR_REF),
    (STAGE2_SECOND_CREDENTIAL_REF, STAGE2_CREDENTIAL_LOCATOR_REF),
    ("credential.mikrotik.lab03", "locator.stage2.mikrotik.lab03.readonly"),
    (STAGE2_SECOND_CREDENTIAL_REF, "locator.stage2.other"),
])
def test_binding_records_reject_cross_lab_and_unknown_locator_pairs(credential_ref, locator_ref):
    with pytest.raises(Stage2CredentialResolverError) as error:
        Stage2CredentialBinding(credential_ref, STAGE2_CREDENTIAL_BACKEND_KIND, locator_ref)
    assert str(error.value) == "INVALID_RESOLVER_CONFIGURATION"


def test_target_aware_request_composition_preserves_endpoint_and_request():
    registry = parse_stage2_fixed_target_registry([
        _target_record(), dict(_target_record(), target_ref=STAGE2_SECOND_TARGET_REF,
                              address="192.0.2.20"),
    ])
    request = parse_stage2_vrrp_observation_request(_request(
        target_ref=STAGE2_SECOND_TARGET_REF, credential_ref=STAGE2_SECOND_CREDENTIAL_REF,
    ))
    before = request.to_canonical_bytes()
    endpoint = registry.lookup(request.target_ref)
    resolver = build_stage2_fixed_credential_resolver()
    binding = resolver.resolve_for_target(request.target_ref, request.credential_ref)
    assert binding.credential_ref == request.credential_ref
    assert request.to_canonical_bytes() == before
    assert registry.lookup(request.target_ref) is endpoint
    # Existing downstream credential-only callers remain Lab1-only, not widened.
    _assert_error(resolver.resolve, request.credential_ref,
                  Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL)


def test_resolver_imports_only_offline_contract_and_registry_not_downstream():
    tree = ast.parse(inspect.getsource(module))
    imports = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert imports == {
        "__future__", "dataclasses", "enum", "typing",
        "validation_framework.stage2_vrrp_readonly_contract",
        "validation_framework.stage2_mikrotik_target_registry",
    }
    assert {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
        for alias in node.names
    } == {"re"}
