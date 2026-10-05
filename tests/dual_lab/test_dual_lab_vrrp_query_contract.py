"""Synthetic DL-01 contract checks; no runtime or live entrypoint invocation."""

import ast
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
import inspect
import json
from pathlib import Path

import pytest

from validation_framework import dual_lab_vrrp_query_contract as m
from validation_framework import stage2_vrrp_readonly_contract as s2


LAB1 = "target.mikrotik.lab01"
LAB2 = "target.mikrotik.lab02"
SENTINEL = "synthetic-secret-signature-path-stdout-exception"
CATEGORIES = (
    "PREFLIGHT_TARGET_BUNDLE_INVALID",
    "PREFLIGHT_AUTHORIZATION_INVALID",
    "PREFLIGHT_AUTHORIZATION_NOT_DISTINCT",
    "PREFLIGHT_STARTUP_BINDING_UNAVAILABLE",
    "CANONICAL_EVIDENCE_VALIDATION_FAILED",
    "INVALID_REQUEST_INPUT",
    "INVALID_AUTHORIZATION_INPUT",
    "INVALID_TRUSTED_CONFIGURATION",
    "TRUSTED_RUNTIME_FAILED",
    "OUTPUT_RENDER_FAILED",
    "INTERNAL_FAILURE",
)


def query():
    return {"schema_version": "dual-lab-vrrp-query.v1", "query_id": "query.synthetic-01",
            "operation_id": "mikrotik.vrrp_status", "execution_order": "LAB1_THEN_LAB2"}


def record():
    return {"instance_name": "vrrp-synthetic", "vrid": 88, "priority": 100,
            "interval_ms": 1000, "version": 3, "running": False, "role": "BACKUP",
            "disabled": False, "invalid": False}


def evidence(target):
    return {"schema_version": "1.0", "operation_id": "mikrotik.vrrp_status",
            "run_id": "run.synthetic", "target_ref": target,
            "authorization_ref": "authorization.synthetic",
            "command_policy_version": "policy.stage2.vrrp-readonly.v1",
            "attempt_count": 1, "retry_count": 0, "duration_ms": 1,
            "raw_output_byte_count": 0, "raw_output_sha256": "a" * 64,
            "records": [record()]}


def success(target):
    return {"status": "SUCCESS", "target_ref": target, "evidence": evidence(target)}


def failure(target, category="INTERNAL_FAILURE"):
    return {"status": "FAILURE", "target_ref": target, "failure_category": category}


def aggregate():
    return {**query(), "lab1": success(LAB1), "lab2": success(LAB2)}


def canonical(raw):
    return json.dumps(raw, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def rejected(parser, raw):
    with pytest.raises(m.DualLabContractError) as caught:
        parser(raw)
    error = caught.value
    assert error.args == ("invalid Dual-Lab contract",)
    assert error.__cause__ is None
    assert error.__context__ is None
    assert SENTINEL not in str(error) + repr(error)
    assert not isinstance(error, (m.TargetSuccess, m.TargetFailure, m.DualLabVrrpAggregate))
    return error


@pytest.mark.parametrize("left", [success, failure])
@pytest.mark.parametrize("right", [success, failure])
def test_all_outcome_combinations_round_trip(left, right):
    raw = {**query(), "lab1": left(LAB1), "lab2": right(LAB2)}
    value = m.parse_aggregate(raw)
    assert value.to_dict() == raw
    assert value.to_canonical_bytes() == canonical(raw)
    assert m.parse_aggregate_canonical_json(value.to_canonical_bytes()) == value
    assert value.execution_authorized is False
    assert {f.name for f in fields(value)} == {
        "schema_version", "query_id", "operation_id", "execution_order", "lab1", "lab2"}


def test_minimum_query_has_fixed_implicit_pair_and_canonical_identity():
    value = m.parse_query(query())
    assert {f.name for f in fields(value)} == set(query())
    assert value.to_dict() == query()
    assert value.to_canonical_bytes() == canonical(query())
    assert m.parse_query_canonical_json(value.to_canonical_bytes()) == value
    assert value.execution_authorized is False


@pytest.mark.parametrize("query_id", ["", " ", "query.", "query.1bad", "wrong.synthetic",
    "query.a b", "query.a\nb", "query.a\x00", "query.a\t", "query.a\r", "query.a/b",
    "query.a\\b", "query.c:\\private", "query...", "query.é", "query.a@host",
    "query.a?token=x", "query.a;reboot", "query." + "a" * 155, None, True, 1, [], {}])
@pytest.mark.parametrize("factory,parser", [(query, m.parse_query), (aggregate, m.parse_aggregate)])
def test_invalid_query_id_rejects_without_result(factory, parser, query_id):
    raw = factory()
    raw["query_id"] = query_id
    rejected(parser, raw)


@pytest.mark.parametrize("query_id", ["query.a", "query.synthetic-01.part_a", "query." + "a" * 154])
def test_query_identifier_bound_and_existing_logical_grammar(query_id):
    raw = query()
    raw["query_id"] = query_id
    assert m.parse_query_canonical_json(canonical(raw)).query_id == query_id


@pytest.mark.parametrize("field,value", [
    ("schema_version", "1.0"), ("schema_version", True), ("schema_version", 1),
    ("operation_id", "mikrotik.vrrp_set"), ("operation_id", None), ("operation_id", 1),
    ("execution_order", "LAB2_THEN_LAB1"), ("execution_order", "PARALLEL"),
    ("execution_order", True), ("execution_order", [])])
@pytest.mark.parametrize("factory,parser", [(query, m.parse_query), (aggregate, m.parse_aggregate)])
def test_identity_is_exact(factory, parser, field, value):
    raw = factory()
    raw[field] = value
    rejected(parser, raw)


@pytest.mark.parametrize("field", list(aggregate()))
def test_every_aggregate_field_required(field):
    raw = aggregate()
    del raw[field]
    rejected(m.parse_aggregate, raw)


@pytest.mark.parametrize("field", list(query()))
def test_every_query_field_required(field):
    raw = query()
    del raw[field]
    rejected(m.parse_query, raw)


@pytest.mark.parametrize("field", ["timestamp", "duration", "health", "healthy", "pair_health",
    "failover_ready", "split_brain", "correct", "recommended_action", "remediation", "verdict",
    "authorization_id", "authorization_ref", "raw_output", "stdout", "password", "credential",
    "private_key", "signature", "envelope", "private_path", "model_output", "traceback",
    "exception", "replay_consumed", "targets", "lab3", "runtime_configuration", "command"])
@pytest.mark.parametrize("factory,parser", [(query, m.parse_query), (aggregate, m.parse_aggregate)])
def test_unknown_and_prohibited_top_level_fields_rejected(factory, parser, field):
    raw = factory()
    raw[field] = SENTINEL
    rejected(parser, raw)


@pytest.mark.parametrize("target", [LAB1, LAB2])
@pytest.mark.parametrize("factory", [success, failure])
def test_tagged_variants_standalone_round_trip(target, factory):
    raw = factory(target)
    value = m.parse_target_result(raw)
    assert {f.name for f in fields(value)} == set(raw)
    assert value.to_dict() == raw
    assert value.execution_authorized is False
    assert m.parse_target_result_canonical_json(value.to_canonical_bytes()) == value


@pytest.mark.parametrize("category", CATEGORIES)
@pytest.mark.parametrize("target", [LAB1, LAB2])
def test_all_and_only_approved_failure_values(category, target):
    value = m.parse_target_result(failure(target, category))
    assert type(value.failure_category) is m.FailureCategory
    assert value.failure_category.value == category
    assert m.parse_target_result_canonical_json(value.to_canonical_bytes()) == value


def test_exact_enum_and_six_s2_identifiers_without_importing_entrypoint():
    assert tuple(item.value for item in m.FailureCategory) == CATEGORIES
    assert tuple(item.name for item in m.FailureCategory) == CATEGORIES
    source = Path(s2.__file__).with_name("stage2_vrrp_readonly_live_entrypoint.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    enum = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                and node.name == "Stage2VrrpLiveEntrypointFailure")
    identifiers = tuple(node.value.value for node in enum.body if isinstance(node, ast.Assign))
    assert identifiers == CATEGORIES[5:]


@pytest.mark.parametrize("category", ["UNKNOWN", SENTINEL, "PREFLIGHT_ENVELOPE_EXPIRED",
    "PREFLIGHT_CREDENTIAL_MISMATCH", "INVALID_QUERY", "INVALID_EVIDENCE", None, 1, True,
    ["INTERNAL_FAILURE"], m.FailureCategory.INTERNAL_FAILURE])
def test_unknown_nonstring_and_exception_failure_categories_rejected(category):
    rejected(m.parse_target_result, failure(LAB1, category))


@pytest.mark.parametrize("factory", [success, failure])
@pytest.mark.parametrize("target", ["target.mikrotik.lab03", "target.other", "", LAB1 + " ",
                                    1, True, None, [LAB1]])
def test_arbitrary_target_and_wrong_types_rejected(factory, target):
    raw = factory(LAB1)
    raw["target_ref"] = target
    rejected(m.parse_target_result, raw)


@pytest.mark.parametrize("status", ["success", "PASS", "WARN", "", None, True, 1, []])
def test_invalid_tag_rejected(status):
    raw = success(LAB1)
    raw["status"] = status
    rejected(m.parse_target_result, raw)


@pytest.mark.parametrize("factory", [success, failure])
def test_missing_mixed_and_unknown_variant_fields(factory):
    raw = factory(LAB1)
    for field in raw:
        missing = deepcopy(raw)
        del missing[field]
        rejected(m.parse_target_result, missing)
    for field in ("failure_category" if factory is success else "evidence", "raw_stdout",
                  "authorization_id", "exception", "health"):
        rejected(m.parse_target_result, {**raw, field: SENTINEL})


@pytest.mark.parametrize("left,right", [(LAB2, LAB1), (LAB1, LAB1), (LAB2, LAB2)])
@pytest.mark.parametrize("factory", [success, failure])
def test_aggregate_slot_target_binding(left, right, factory):
    rejected(m.parse_aggregate, {**query(), "lab1": factory(left), "lab2": factory(right)})


@pytest.mark.parametrize("field,value", [("target_ref", LAB2), ("operation_id", "other.operation"),
    ("command_policy_version", "policy.other"), ("duration_ms", True), ("retry_count", 1),
    ("attempt_count", "1"), ("records", {}), ("raw_output_sha256", "bad")])
def test_malformed_or_mismatched_evidence_rejected(field, value):
    raw = success(LAB1)
    raw["evidence"][field] = value
    rejected(m.parse_target_result, raw)


@pytest.mark.parametrize("field", ["raw_stdout", "password", "signature", "authorization_id",
                                   "private_path", "model_output", "health"])
def test_prohibited_data_cannot_enter_evidence_or_record(field):
    for location in ("evidence", "record"):
        raw = success(LAB1)
        container = raw["evidence"] if location == "evidence" else raw["evidence"]["records"][0]
        container[field] = SENTINEL
        rejected(m.parse_target_result, raw)


def test_existing_evidence_schema_and_empty_multiple_records_preserved():
    for records in ([], [record()], [record(), {**record(), "role": "MASTER", "priority": 150}]):
        raw = success(LAB1)
        raw["evidence"]["records"] = records
        original = s2.parse_stage2_vrrp_observation_evidence(raw["evidence"])
        result = m.parse_target_result(raw)
        assert type(result.evidence) is s2.Stage2VrrpObservationEvidence
        assert result.evidence == original
        assert result.evidence.to_canonical_bytes() == original.to_canonical_bytes()
        assert result.to_dict()["evidence"] == raw["evidence"]
        assert not hasattr(result, "health")


@pytest.mark.parametrize("path,key", [("aggregate", "query_id"), ("target", "status"),
    ("evidence", "duration_ms"), ("record", "vrid")])
def test_duplicate_keys_rejected_at_every_depth(path, key):
    raw = canonical(aggregate())
    needles = {"aggregate": b'"query_id":"query.synthetic-01"', "target": b'"status":"SUCCESS"',
               "evidence": b'"duration_ms":1', "record": b'"vrid":88'}
    needle = needles[path]
    rejected(m.parse_aggregate_canonical_json, raw.replace(needle, needle + b"," + needle, 1))


@pytest.mark.parametrize("factory,parser", [(query, m.parse_query_canonical_json),
    (lambda: success(LAB1), m.parse_target_result_canonical_json),
    (lambda: failure(LAB2), m.parse_target_result_canonical_json),
    (aggregate, m.parse_aggregate_canonical_json)])
def test_strict_json_framing_types_limits_and_canonical_bytes(factory, parser):
    raw = canonical(factory())
    first_pair = raw[1:].split(b",", 1)[0]
    invalid = [None, True, 1, {}, raw.decode(), bytearray(raw), memoryview(raw), b"", b"\xff",
               b"\xef\xbb\xbf" + raw, b" " + raw, raw + b"\n", b"null", b"[]", b"{}",
               b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b"x" * 100_000,
               b'{"x":' + b"[" * 2000 + b"0" + b"]" * 2000 + b"}",
               b"{" + first_pair + b"," + raw[1:], json.dumps(factory(), indent=2).encode()]
    for value in invalid:
        rejected(parser, value)


@pytest.mark.parametrize("factory,parser", [(query, m.parse_query), (aggregate, m.parse_aggregate),
    (lambda: success(LAB1), m.parse_target_result)])
def test_plain_exact_containers_only(factory, parser):
    class MappingSubclass(dict):
        pass
    for value in (MappingSubclass(factory()), None, [], True, 1, canonical(factory())):
        rejected(parser, value)


def test_string_subclasses_do_not_bypass_fixed_identity():
    class StringSubclass(str):
        pass
    for field in query():
        raw = query()
        raw[field] = StringSubclass(raw[field])
        rejected(m.parse_query, raw)
    for field in ("status", "target_ref", "failure_category"):
        raw = failure(LAB1)
        raw[field] = StringSubclass(raw[field])
        rejected(m.parse_target_result, raw)


def test_immutability_direct_construction_and_input_output_isolation():
    raw = aggregate()
    value = m.parse_aggregate(raw)
    raw["query_id"] = "query.changed"
    raw["lab1"]["evidence"]["records"][0]["priority"] = 255
    exported = value.to_dict()
    exported["lab2"]["evidence"]["records"].clear()
    assert value.query_id == "query.synthetic-01"
    assert value.lab1.evidence.records[0].priority == 100
    assert len(value.lab2.evidence.records) == 1
    for obj, field, replacement in ((value, "query_id", "query.changed"),
            (value.lab1, "target_ref", LAB2), (value.lab1.evidence.records[0], "priority", 255),
            (m.parse_query(query()), "query_id", "query.changed"),
            (m.parse_target_result(failure(LAB1)), "status", "SUCCESS")):
        with pytest.raises(FrozenInstanceError):
            setattr(obj, field, replacement)
        assert not hasattr(obj, "__dict__")
    rejected(lambda _: replace(value, lab1=value.lab2), None)
    rejected(lambda _: replace(value, query_id="bad"), None)
    rejected(lambda _: m.TargetSuccess("FAILURE", LAB1, value.lab1.evidence), None)
    rejected(lambda _: m.TargetFailure("FAILURE", LAB1, "INTERNAL_FAILURE"), None)
    rejected(lambda _: m.TargetFailure("SUCCESS", LAB1, m.FailureCategory.INTERNAL_FAILURE), None)


def test_direct_success_detaches_evidence_and_revalidates_forged_records():
    original = s2.parse_stage2_vrrp_observation_evidence(evidence(LAB1))
    result = m.TargetSuccess("SUCCESS", LAB1, original)
    assert result.evidence == original and result.evidence is not original
    object.__setattr__(original.records[0], "priority", 999)
    assert result.evidence.records[0].priority == 100
    rejected(lambda _: m.TargetSuccess("SUCCESS", LAB1, original), None)


@pytest.mark.parametrize("location,field,bad", [("aggregate", "query_id", SENTINEL),
    ("target", "status", "FAILURE"), ("evidence", "operation_id", "other.operation"),
    ("record", "priority", 999), ("evidence", "duration_ms", object()),
    ("evidence", "run_id", "run." + "x" * 100_000)],
    ids=["query", "tag", "operation", "record", "non-json", "oversized"])
def test_serialization_rechecks_objects_altered_after_construction(location, field, bad):
    value = m.parse_aggregate(aggregate())
    obj = {"aggregate": value, "target": value.lab1, "evidence": value.lab1.evidence,
           "record": value.lab1.evidence.records[0]}[location]
    object.__setattr__(obj, field, bad)
    rejected(lambda _: value.to_dict(), None)
    rejected(lambda _: value.to_canonical_bytes(), None)


def test_failure_and_query_serialization_revalidate_and_missing_attributes_reject():
    value = m.parse_target_result(failure(LAB1))
    object.__setattr__(value, "failure_category", SENTINEL)
    rejected(lambda _: value.to_canonical_bytes(), None)
    value = m.parse_query(query())
    object.__delattr__(value, "operation_id")
    rejected(lambda _: value.to_canonical_bytes(), None)


def test_subclassed_and_uninitialized_objects_rejected():
    class EvidenceSubclass(s2.Stage2VrrpObservationEvidence):
        pass
    class ResultSubclass(m.TargetSuccess):
        pass
    for invalid in (object.__new__(EvidenceSubclass), object.__new__(s2.Stage2VrrpObservationEvidence),
                    {}, canonical(evidence(LAB1))):
        rejected(lambda value: m.TargetSuccess("SUCCESS", LAB1, value), invalid)
    valid = m.parse_aggregate(aggregate())
    rejected(lambda _: replace(valid, lab1=object.__new__(ResultSubclass)), None)


def test_determinism_unicode_and_sanitized_representations(capsys):
    raw = aggregate()
    raw["lab1"]["evidence"]["records"][0]["instance_name"] = "vrrp-é"
    reverse = {key: raw[key] for key in reversed(raw)}
    value = m.parse_aggregate(raw)
    assert value.to_canonical_bytes() == m.parse_aggregate(reverse).to_canonical_bytes()
    assert m.parse_aggregate_canonical_json(value.to_canonical_bytes()) == value
    for obj in (value, value.lab1, m.parse_target_result(failure(LAB2)), m.parse_query(query())):
        assert repr(obj) == f"{type(obj).__name__}(<inert-contract>)"
        assert str(obj) == repr(obj)
        assert "query.synthetic" not in repr(obj)
        assert LAB1 not in repr(obj)
    try:
        raise ValueError(SENTINEL)
    except ValueError:
        rejected(m.parse_aggregate, {"exception": SENTINEL})
    assert capsys.readouterr() == ("", "")


def test_exact_public_surface_and_no_execution_capabilities():
    expected = {"FailureCategory", "DualLabContractError", "DualLabVrrpQuery",
        "TargetSuccess", "TargetFailure", "TargetResult", "DualLabVrrpAggregate",
        "parse_query", "parse_target_result", "parse_aggregate", "parse_query_canonical_json",
        "parse_target_result_canonical_json", "parse_aggregate_canonical_json"}
    assert set(m.__all__) == expected
    assert {name for name in vars(m) if not name.startswith("_")} == expected
    tree = ast.parse(inspect.getsource(m))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
            if node.module == "validation_framework":
                assert [alias.name for alias in node.names] == ["stage2_vrrp_readonly_contract"]
    assert imports == {"dataclasses", "enum", "functools", "json", "re", "validation_framework"}
    calls = {node.func.id for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not calls & {"open", "exec", "eval", "print", "__import__", "run_stage2_vrrp_live_once"}
    assert not any(isinstance(node, (ast.AsyncFunctionDef, ast.Await)) for node in ast.walk(tree))


def test_serde_failure_returns_no_aggregate_or_target_failure(monkeypatch):
    value = m.parse_aggregate(aggregate())
    def fail(*args, **kwargs):
        raise RuntimeError(SENTINEL)
    monkeypatch.setattr(m._json, "dumps", fail)
    rejected(lambda _: value.to_canonical_bytes(), None)


def test_final_canonical_reparse_failure_returns_no_output(monkeypatch):
    value = m.parse_aggregate(aggregate())
    def fail(*args, **kwargs):
        raise RuntimeError(SENTINEL)
    monkeypatch.setattr(m, "parse_aggregate_canonical_json", fail)
    rejected(lambda _: value.to_canonical_bytes(), None)
