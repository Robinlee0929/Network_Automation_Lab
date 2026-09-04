import ast
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import inspect
import json

import pytest

from validation_framework import stage2_vrrp_readonly_contract as module
from validation_framework.stage2_vrrp_readonly_contract import (
    MAX_DURATION_MS,
    MAX_INSTANCE_NAME_UTF8_BYTES,
    MAX_RAW_OUTPUT_BYTES,
    MAX_REFERENCE_LENGTH,
    MAX_VRRP_RECORDS,
    NormalizedVrrpRecord,
    STAGE2_VRRP_CONTRACT_SCHEMA_VERSION,
    Stage2VrrpContractError,
    Stage2VrrpContractFailure,
    Stage2VrrpObservationEvidence,
    Stage2VrrpObservationRequest,
    VRRP_COMMAND_POLICY_VERSION,
    VRRP_OBSERVATION_OPERATION_ID,
    parse_stage2_vrrp_evidence_canonical_json,
    parse_stage2_vrrp_observation_evidence,
    parse_stage2_vrrp_observation_request,
    parse_stage2_vrrp_request_canonical_json,
)


def _request(**changes):
    result = {
        "schema_version": "1.0",
        "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.stage2.synthetic-0001",
        "target_ref": "target.mikrotik.lab01",
        "credential_ref": "credential.mikrotik.lab01.readonly",
        "authorization_ref": "authorization.stage2.owner-gate",
        "read_only": True,
    }
    result.update(changes)
    return result


def _record(**changes):
    result = {
        "instance_name": "vrrp-lan",
        "vrid": 49,
        "priority": 100,
        "interval_ms": 1_000,
        "version": 3,
        "running": True,
        "role": "BACKUP",
        "disabled": False,
        "invalid": False,
    }
    result.update(changes)
    return result


def _evidence(**changes):
    result = {
        "schema_version": "1.0",
        "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.stage2.synthetic-0001",
        "target_ref": "target.mikrotik.lab01",
        "authorization_ref": "authorization.stage2.owner-gate",
        "command_policy_version": "policy.stage2.vrrp-readonly.v1",
        "attempt_count": 1,
        "retry_count": 0,
        "duration_ms": 125,
        "raw_output_byte_count": 512,
        "raw_output_sha256": hashlib.sha256(b"synthetic-output").hexdigest(),
        "records": [_record()],
    }
    result.update(changes)
    return result


def _assert_rejected(function, payload, code):
    with pytest.raises(Stage2VrrpContractError) as error:
        function(payload)
    assert error.value.code is code
    assert str(error.value) == code.value


def test_policy_constants_and_public_surface_are_exact():
    assert STAGE2_VRRP_CONTRACT_SCHEMA_VERSION == "1.0"
    assert VRRP_OBSERVATION_OPERATION_ID == "mikrotik.vrrp_status"
    assert VRRP_COMMAND_POLICY_VERSION == "policy.stage2.vrrp-readonly.v1"
    assert MAX_REFERENCE_LENGTH == 160
    assert MAX_INSTANCE_NAME_UTF8_BYTES == 128
    assert MAX_VRRP_RECORDS == 32
    assert MAX_DURATION_MS == 60_000
    assert MAX_RAW_OUTPUT_BYTES == 65_536
    assert module.ALLOWED_VRRP_VERSIONS == frozenset({2, 3})
    assert module.ALLOWED_VRRP_ROLES == frozenset(
        {"MASTER", "BACKUP", "FAILURE", "UNKNOWN"}
    )


def test_valid_request_is_fixed_read_only_inert_and_canonical():
    request = parse_stage2_vrrp_observation_request(_request())

    assert type(request) is Stage2VrrpObservationRequest
    assert request.read_only is True
    assert request.execution_authorized is False
    assert request.to_dict() == _request()
    assert repr(request) == "Stage2VrrpObservationRequest(<offline-read-only>)"
    assert parse_stage2_vrrp_request_canonical_json(
        request.to_canonical_bytes()
    ) == request
    assert request.to_canonical_bytes() == json.dumps(
        _request(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "2.0"),
        ("operation_id", "stage2.vrrp.configure"),
        ("operation_id", "mikrotik.vrrp_status "),
        ("run_id", ""),
        ("run_id", "run.stage2/unsafe"),
        ("run_id", "run.stagé"),
        ("target_ref", "target"),
        ("target_ref", "target.mikrotik;reboot"),
        ("credential_ref", "credential.lab.password"),
        ("credential_ref", "credential.lab.password123"),
        ("credential_ref", "credential.lab.api-key"),
        ("credential_ref", "credential.lab.private-key"),
        ("authorization_ref", " authorization.stage2.owner"),
        ("read_only", False),
        ("read_only", 1),
    ],
)
def test_invalid_request_values_fail_closed(field, value):
    _assert_rejected(
        parse_stage2_vrrp_observation_request,
        _request(**{field: value}),
        Stage2VrrpContractFailure.INVALID_REQUEST,
    )


def test_overlong_reference_and_wrong_scalar_types_reject():
    _assert_rejected(
        parse_stage2_vrrp_observation_request,
        _request(target_ref="target." + "a" * MAX_REFERENCE_LENGTH),
        Stage2VrrpContractFailure.INVALID_REQUEST,
    )
    for field in (
        "schema_version",
        "operation_id",
        "run_id",
        "target_ref",
        "credential_ref",
        "authorization_ref",
    ):
        _assert_rejected(
            parse_stage2_vrrp_observation_request,
            _request(**{field: 1}),
            Stage2VrrpContractFailure.INVALID_REQUEST,
        )


@pytest.mark.parametrize(
    "field",
    ["command", "password", "private_key", "retry_count", "target_ip"],
)
def test_unknown_or_forbidden_request_fields_are_impossible(field):
    _assert_rejected(
        parse_stage2_vrrp_observation_request,
        _request(**{field: "synthetic"}),
        Stage2VrrpContractFailure.INVALID_REQUEST,
    )


def test_request_requires_one_plain_exact_record():
    class DictSubclass(dict):
        pass

    _assert_rejected(
        parse_stage2_vrrp_observation_request,
        DictSubclass(_request()),
        Stage2VrrpContractFailure.INVALID_REQUEST,
    )
    missing = _request()
    missing.pop("authorization_ref")
    _assert_rejected(
        parse_stage2_vrrp_observation_request,
        missing,
        Stage2VrrpContractFailure.INVALID_REQUEST,
    )


def test_request_is_immutable_and_direct_construction_cannot_bypass_validation():
    request = parse_stage2_vrrp_observation_request(_request())
    with pytest.raises(FrozenInstanceError):
        request.read_only = False
    with pytest.raises(Stage2VrrpContractError) as error:
        replace(request, operation_id="mikrotik.vrrp_set")
    assert error.value.code is Stage2VrrpContractFailure.INVALID_REQUEST


def test_valid_evidence_is_bounded_normalized_immutable_and_canonical():
    evidence = parse_stage2_vrrp_observation_evidence(_evidence())

    assert type(evidence) is Stage2VrrpObservationEvidence
    assert evidence.execution_authorized is False
    assert type(evidence.records) is tuple
    assert type(evidence.records[0]) is NormalizedVrrpRecord
    assert evidence.records[0].interval_ms == 1_000
    assert repr(evidence) == (
        "Stage2VrrpObservationEvidence(<normalized-no-raw-output>)"
    )
    assert repr(evidence.records[0]) == "NormalizedVrrpRecord(<bounded>)"
    assert parse_stage2_vrrp_evidence_canonical_json(
        evidence.to_canonical_bytes()
    ) == evidence


def test_zero_vrrp_records_is_valid_complete_observation_shape():
    evidence = parse_stage2_vrrp_observation_evidence(
        _evidence(raw_output_byte_count=0, records=[])
    )
    assert evidence.records == ()


@pytest.mark.parametrize("attempt_count", [0, 2, -1, True, "1"])
def test_attempt_count_must_be_exactly_one(attempt_count):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(attempt_count=attempt_count),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


@pytest.mark.parametrize("retry_count", [-1, 1, True, "0"])
def test_retry_count_must_be_exactly_zero(retry_count):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(retry_count=retry_count),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


@pytest.mark.parametrize("duration", [0, MAX_DURATION_MS + 1, True, "125"])
def test_duration_is_strictly_bounded(duration):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(duration_ms=duration),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


@pytest.mark.parametrize(
    "byte_count", [-1, MAX_RAW_OUTPUT_BYTES + 1, True, "512"]
)
def test_raw_output_byte_count_is_strictly_bounded(byte_count):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(raw_output_byte_count=byte_count),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


@pytest.mark.parametrize(
    "digest",
    ["", "0" * 63, "0" * 65, "G" * 64, b"0" * 64],
)
def test_raw_output_digest_is_exact_lowercase_sha256(digest):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(raw_output_sha256=digest),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


def test_record_collection_is_plain_bounded_and_input_isolated():
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(records=[_record()] * (MAX_VRRP_RECORDS + 1)),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(records=(_record(),)),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )

    payload = _evidence()
    evidence = parse_stage2_vrrp_observation_evidence(payload)
    payload["records"][0]["priority"] = 255
    exported = evidence.to_dict()
    exported["records"][0]["priority"] = 1
    assert evidence.records[0].priority == 100


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("instance_name", ""),
        ("instance_name", " vrrp-lan"),
        ("instance_name", "vrrp\nlan"),
        ("instance_name", "e\u0301"),
        ("instance_name", "a" * (MAX_INSTANCE_NAME_UTF8_BYTES + 1)),
        ("vrid", 0),
        ("vrid", 256),
        ("vrid", True),
        ("priority", -1),
        ("priority", 256),
        ("interval_ms", 0),
        ("interval_ms", 255_001),
        ("version", 1),
        ("version", 4),
        ("running", 1),
        ("role", "INIT"),
        ("disabled", 0),
        ("invalid", None),
    ],
)
def test_invalid_normalized_record_values_reject(field, value):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(records=[_record(**{field: value})]),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


def test_record_requires_exact_fields_and_is_immutable():
    extra = _record(raw_line="forbidden")
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(records=[extra]),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )
    evidence = parse_stage2_vrrp_observation_evidence(_evidence())
    with pytest.raises(FrozenInstanceError):
        evidence.records[0].priority = 254


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "2.0"),
        ("operation_id", "mikrotik.vrrp_set"),
        ("run_id", "run/unsafe"),
        ("target_ref", "target"),
        ("authorization_ref", "authorization unsafe"),
        ("command_policy_version", "policy.stage2.generic.v1"),
    ],
)
def test_invalid_evidence_bindings_reject(field, value):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(**{field: value}),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


@pytest.mark.parametrize(
    "field",
    ["raw_output", "password", "target_ip", "host_key_blob", "command"],
)
def test_secret_raw_and_transport_evidence_fields_are_impossible(field):
    _assert_rejected(
        parse_stage2_vrrp_observation_evidence,
        _evidence(**{field: "synthetic"}),
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


def test_canonical_json_rejects_noncanonical_duplicate_and_invalid_bytes():
    request = parse_stage2_vrrp_observation_request(_request())
    canonical = request.to_canonical_bytes()
    duplicate = canonical[:-1] + b',"read_only":true}'

    for raw in (
        b"\xef\xbb\xbf" + canonical,
        canonical + b"\n",
        b" " + canonical,
        duplicate,
        b"\xff",
        b"{}",
    ):
        _assert_rejected(
            parse_stage2_vrrp_request_canonical_json,
            raw,
            Stage2VrrpContractFailure.INVALID_REQUEST,
        )


def test_canonical_evidence_rejects_duplicate_nested_record_field():
    evidence = parse_stage2_vrrp_observation_evidence(_evidence())
    canonical = evidence.to_canonical_bytes()
    duplicate = canonical.replace(
        b'"vrid":49',
        b'"vrid":49,"vrid":49',
        1,
    )
    _assert_rejected(
        parse_stage2_vrrp_evidence_canonical_json,
        duplicate,
        Stage2VrrpContractFailure.INVALID_EVIDENCE,
    )


def test_contract_types_expose_no_secret_endpoint_command_or_retry_controls():
    request_fields = {field.name for field in fields(Stage2VrrpObservationRequest)}
    evidence_fields = {field.name for field in fields(Stage2VrrpObservationEvidence)}
    record_fields = {field.name for field in fields(NormalizedVrrpRecord)}
    forbidden = {
        "command",
        "endpoint",
        "hostname",
        "password",
        "private_key",
        "raw_output",
        "retry",
        "secret",
        "target_ip",
    }
    assert forbidden.isdisjoint(request_fields | evidence_fields | record_fields)


def test_module_has_no_external_io_or_execution_imports_and_no_entrypoint():
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
        "shutil",
        "socket",
        "subprocess",
        "tempfile",
        "win32cred",
    }
    assert forbidden_imports.isdisjoint(imported_roots)
    called_builtins = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "open" not in called_builtins
    assert not hasattr(module, "main")
    assert not hasattr(module, "connect")
    assert not hasattr(module, "execute")
    assert not hasattr(module, "parse_routeros_output")
