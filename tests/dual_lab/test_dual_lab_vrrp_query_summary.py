"""DL-03 specification cases 1-42; synthetic data and no live dependencies."""

import ast
import builtins
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields
import importlib
import inspect
from itertools import product
import json
import socket
import subprocess
import sys

import pytest

from validation_framework import dual_lab_vrrp_query_contract as upstream


LAB1 = "target.mikrotik.lab01"
LAB2 = "target.mikrotik.lab02"
SCHEMA = "dual-lab-vrrp-query-summary.v1"
MODULE = "validation_framework.dual_lab_vrrp_query_summary"
COMPARE = ("role", "priority", "interval_ms", "version", "running", "disabled", "invalid")
SORT = ("instance_name", "vrid", *COMPARE)
KINDS = {
    "RESULT_AVAILABILITY", "VRID_SET_EQUAL", "VRID_SET_DIFFERENT",
    "VRID_ONLY_LAB1", "VRID_ONLY_LAB2", "INSTANCE_NAME_SET_EQUAL",
    "INSTANCE_NAME_SET_DIFFERENT", "RECORD_COUNT_EQUAL", "RECORD_COUNT_DIFFERENT",
    "RECORD_ONLY_LAB1", "RECORD_ONLY_LAB2", "MATCH_KEY_MULTIPLICITY",
    "FIELD_EQUAL", "FIELD_DIFFERENT",
}
PROHIBITED = (
    "HEALTHY", "UNHEALTHY", "DEGRADED", "FAILOVER_READY", "HA_READY",
    "PRODUCTION_READY", "SPLIT_BRAIN", "MISCONFIGURED", "CORRECT_CONFIGURATION",
    "INCORRECT_CONFIGURATION", "ROOT_CAUSE", "REMEDIATION_REQUIRED",
    "remediation_command", "configuration_command", "retry_advice", "fallback_advice",
    "credential_selection", "endpoint_selection", "authorization_decision",
    "command_selection", "execution_instruction",
)
SENSITIVE = (
    "raw_stdout", "credential_ref", "authorization_id", "authorization_ref",
    "signature", "private_key", "known_host_raw", "private_path", "replay_data",
    "exception", "runtime_configuration", "ssh_session",
)
SENTINEL = "synthetic-rejected-input"


def canonical(raw):
    return json.dumps(raw, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def record(**changes):
    return {"instance_name": "vrrp-synthetic", "role": "BACKUP", "vrid": 88,
            "priority": 100, "interval_ms": 1000, "version": 3,
            "running": False, "disabled": False, "invalid": False, **changes}


def target(ref, records):
    if records is None:
        return {"status": "FAILURE", "target_ref": ref, "failure_category": "INTERNAL_FAILURE"}
    return {"status": "SUCCESS", "target_ref": ref, "evidence": {
        "schema_version": "1.0", "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.synthetic", "target_ref": ref,
        "authorization_ref": "authorization.synthetic",
        "command_policy_version": "policy.stage2.vrrp-readonly.v1",
        "attempt_count": 1, "retry_count": 0, "duration_ms": 1,
        "raw_output_byte_count": 0, "raw_output_sha256": "a" * 64,
        "records": deepcopy(records)}}


def aggregate(left=(), right=()):
    return {"schema_version": "dual-lab-vrrp-query.v1", "query_id": "query.synthetic",
            "operation_id": "mikrotik.vrrp_status", "execution_order": "LAB1_THEN_LAB2",
            "lab1": target(LAB1, left), "lab2": target(LAB2, right)}


def obs(kind, left, right, subject=None):
    return {"kind": kind, "subject": subject, "lab1_value": left, "lab2_value": right}


def key(name="vrrp-synthetic", vrid=88, **extra):
    return {"instance_name": name, "vrid": vrid, **extra}


def empty_summary():
    return {"schema_version": SCHEMA, "query_id": "query.synthetic",
            "operation_id": "mikrotik.vrrp_status", "execution_order": "LAB1_THEN_LAB2",
            "lab1": {"status": "SUCCESS", "target_ref": LAB1, "records": []},
            "lab2": {"status": "SUCCESS", "target_ref": LAB2, "records": []},
            "cross_target_observations": [obs("RESULT_AVAILABILITY", True, True),
                obs("VRID_SET_EQUAL", [], []), obs("INSTANCE_NAME_SET_EQUAL", [], []),
                obs("RECORD_COUNT_EQUAL", 0, 0)]}


def one_summary():
    raw = empty_summary()
    raw["lab1"]["records"] = [record()]
    raw["lab2"]["records"] = [record()]
    raw["cross_target_observations"] = [obs("RESULT_AVAILABILITY", True, True),
        obs("VRID_SET_EQUAL", [88], [88]),
        obs("INSTANCE_NAME_SET_EQUAL", ["vrrp-synthetic"], ["vrrp-synthetic"]),
        obs("RECORD_COUNT_EQUAL", 1, 1),
        *[obs("FIELD_EQUAL", record()[f], record()[f], key(field=f)) for f in COMPARE]]
    return raw


@pytest.fixture(scope="session")
def m():
    # Deferred import lets the test-first run validate fixture data independently.
    return importlib.import_module(MODULE)


def reject(m, function, value):
    with pytest.raises(m.DualLabSummaryError) as caught:
        function(value)
    error = caught.value
    assert error.args == ("invalid Dual-Lab summary",)
    assert error.__cause__ is None and error.__context__ is None
    assert SENTINEL not in str(error) + repr(error) + repr(vars(error))


def project(m, left=(), right=()):
    return m.project_dual_lab_vrrp_summary(canonical(aggregate(left, right)))


def test_test_first_fixture_contract_is_valid_without_production_module():
    for left, right in product((None, [], [record()], [record(), record(priority=200)]), repeat=2):
        raw = aggregate(left, right)
        assert upstream.parse_aggregate_canonical_json(canonical(raw)).to_dict() == raw
    assert len(one_summary()["cross_target_observations"]) == 11
    assert len(KINDS) == 14


@pytest.mark.parametrize("left,right", product((None, [record()]), repeat=2))
def test_01_to_04_outcomes_and_failure_absence(m, left, right):
    value = project(m, left, right)
    raw = value.to_dict()
    if left is not None and right is not None:
        assert raw == one_summary()
    else:
        assert raw["cross_target_observations"] == [
            obs("RESULT_AVAILABILITY", left is not None, right is not None)]
    for name, ref, records in (("lab1", LAB1, left), ("lab2", LAB2, right)):
        expected = target(ref, None) if records is None else {
            "status": "SUCCESS", "target_ref": ref, "records": records}
        assert raw[name] == expected
    assert value.execution_authorized is False
    assert value.to_canonical_bytes() == canonical(raw)
    assert m.parse_summary_canonical_json(canonical(raw)).to_dict() == raw


def test_05_06_empty_and_single_exact_output(m):
    assert project(m).to_dict() == empty_summary()
    assert project(m, [record()], [record()]).to_dict() == one_summary()


def test_07_to_09_multirecord_sort_permutations_metadata_and_identity(m):
    records = [record(instance_name="z"), record(instance_name="a", vrid=99),
               record(instance_name="a", priority=200), record(instance_name="a"), record()]
    expected = sorted(records, key=lambda r: tuple(r[f] for f in SORT))
    baseline = project(m, records, records).to_canonical_bytes()
    for order in (records[::-1], records[2:] + records[:2], records):
        raw = aggregate(order, records[::-1])
        raw["lab1"]["evidence"].update(run_id="run.other", duration_ms=2,
            authorization_ref="authorization.other", raw_output_sha256="b" * 64)
        raw = dict(reversed(list(raw.items())))
        result = m.project_dual_lab_vrrp_summary(canonical(raw))
        assert result.lab1.records[0].instance_name == "a"
        assert result.to_dict()["lab1"]["records"] == expected
        assert result.to_canonical_bytes() == baseline


@pytest.mark.parametrize("location", ["top", "success", "failure", "record", "observation", "subject"])
def test_10_to_13_every_field_required_and_extras_reject(m, location):
    raw = one_summary()
    if location == "failure":
        raw = project(m, None, None).to_dict()
    container = {"top": raw, "success": raw["lab1"], "failure": raw["lab1"],
                 "record": raw["lab2"].get("records", [{}])[0] if location != "failure" else {},
                 "observation": raw["cross_target_observations"][-1],
                 "subject": raw["cross_target_observations"][-1]["subject"]}[location]
    for field in list(container):
        saved = container.pop(field)
        reject(m, m.parse_summary_canonical_json, canonical(raw))
        container[field] = saved
    for field in SENSITIVE + ("extra",):
        container[field] = SENTINEL
        reject(m, m.parse_summary_canonical_json, canonical(raw))
        del container[field]


@pytest.mark.parametrize("bad", [None, []])
def test_11_failure_cannot_have_records(m, bad):
    raw = project(m, None, None).to_dict()
    raw["lab1"]["records"] = bad
    reject(m, m.parse_summary_canonical_json, canonical(raw))


@pytest.mark.parametrize("field,bad", [
    ("instance_name", ""), ("instance_name", " space"), ("instance_name", "a\n"),
    ("instance_name", "e\u0301"), ("instance_name", "x" * 129), ("instance_name", 1),
    ("role", "HEALTHY"), ("vrid", True), ("vrid", 0), ("vrid", 256),
    ("priority", -1), ("priority", 256), ("priority", True),
    ("interval_ms", 0), ("interval_ms", 255001), ("version", 1), ("version", True),
    ("running", 1), ("disabled", 0), ("invalid", None)])
def test_12_29_record_domains_in_aggregate_and_summary(m, field, bad):
    source = aggregate([record(**{field: bad})], [])
    reject(m, m.project_dual_lab_vrrp_summary, canonical(source))
    summary = one_summary()
    summary["lab1"]["records"][0][field] = bad
    reject(m, m.parse_summary_canonical_json, canonical(summary))


def test_13_envelope_exclusion_and_exact_fields(m):
    value = project(m, [record()], [record()])
    raw = value.to_dict()
    assert set(raw) == set(empty_summary())
    assert {f.name for f in fields(value)} == set(raw)
    assert set(raw["lab1"]) == {"status", "target_ref", "records"}
    assert set(raw["lab1"]["records"][0]) == set(SORT)
    assert b"authorization.synthetic" not in value.to_canonical_bytes()
    assert b"run.synthetic" not in value.to_canonical_bytes()
    assert b"raw_output" not in value.to_canonical_bytes()


def test_14_to_17_37_38_sets_unmatched_counts_and_order(m):
    left = [record(instance_name="a", vrid=1), record(instance_name="a", vrid=1)]
    right = [record(instance_name="b", vrid=2)]
    rows = project(m, left, right).to_dict()["cross_target_observations"]
    assert rows == [obs("RESULT_AVAILABILITY", True, True),
        obs("VRID_SET_DIFFERENT", [1], [2]), obs("VRID_ONLY_LAB1", True, False, 1),
        obs("VRID_ONLY_LAB2", False, True, 2),
        obs("INSTANCE_NAME_SET_DIFFERENT", ["a"], ["b"]),
        obs("RECORD_COUNT_DIFFERENT", 2, 1),
        obs("RECORD_ONLY_LAB1", 2, 0, key("a", 1)),
        obs("RECORD_ONLY_LAB2", 0, 1, key("b", 2))]
    same = project(m, left, left).to_dict()["cross_target_observations"]
    assert same == [obs("RESULT_AVAILABILITY", True, True), obs("VRID_SET_EQUAL", [1], [1]),
        obs("INSTANCE_NAME_SET_EQUAL", ["a"], ["a"]), obs("RECORD_COUNT_EQUAL", 2, 2),
        obs("MATCH_KEY_MULTIPLICITY", 2, 2, key("a", 1))]


@pytest.mark.parametrize("field,new", [("role", "MASTER"), ("priority", 150),
    ("interval_ms", 2000), ("version", 2), ("running", True),
    ("disabled", True), ("invalid", True)])
def test_18_to_21_exact_unique_field_comparisons(m, field, new):
    expected = one_summary()
    expected["lab2"]["records"][0][field] = new
    expected["cross_target_observations"][4 + COMPARE.index(field)] = obs(
        "FIELD_DIFFERENT", record()[field], new, key(field=field))
    assert project(m, [record()], [record(**{field: new})]).to_dict() == expected


@pytest.mark.parametrize("left,right", product(product((False, True), repeat=3), repeat=2))
def test_22_all_boolean_comparisons(m, left, right):
    names = ("running", "disabled", "invalid")
    rows = project(m, [record(**dict(zip(names, left)))],
                   [record(**dict(zip(names, right)))]).to_dict()["cross_target_observations"][-3:]
    assert rows == [obs("FIELD_EQUAL" if a == b else "FIELD_DIFFERENT", a, b, key(field=f))
                    for f, a, b in zip(names, left, right)]


@pytest.mark.parametrize("different", [record(vrid=89), record(instance_name="vrrp-synthetiC"),
                                      record(instance_name="other", priority=100)])
def test_23_no_guessed_matches(m, different):
    rows = project(m, [record()], [different]).to_dict()["cross_target_observations"]
    assert not any(row["kind"].startswith("FIELD_") for row in rows)
    assert rows[-2:] == [obs("RECORD_ONLY_LAB1", 1, 0, key()),
        obs("RECORD_ONLY_LAB2", 0, 1, key(different["instance_name"], different["vrid"]))]


@pytest.mark.parametrize("left_count,right_count", [(2, 1), (1, 2), (2, 2), (3, 2)])
def test_24_duplicate_multiplicity_never_pairs_or_collapses(m, left_count, right_count):
    left = [record()] * left_count
    right = [record(priority=200)] * right_count
    raw = project(m, left, right).to_dict()
    assert len(raw["lab1"]["records"]) == left_count
    assert len(raw["lab2"]["records"]) == right_count
    assert raw["cross_target_observations"][-1] == obs(
        "MATCH_KEY_MULTIPLICITY", left_count, right_count, key())
    assert not any(row["kind"].startswith("FIELD_") for row in raw["cross_target_observations"])


@pytest.mark.parametrize("field,new", [("role", "UNKNOWN"), ("priority", 200),
    ("interval_ms", 2000), ("version", 2), ("running", True),
    ("disabled", True), ("invalid", True)])
def test_24_complete_duplicate_sort_tie_breaker(m, field, new):
    records = [record(**{field: new}), record(), record()]
    expected = sorted(records, key=lambda r: tuple(r[f] for f in SORT))
    assert project(m, records).to_dict()["lab1"]["records"] == expected
    assert project(m, records).to_canonical_bytes() == project(m, records[::-1]).to_canonical_bytes()


@pytest.mark.parametrize("category", [c.value for c in upstream.FailureCategory])
def test_25_38_failure_vocabulary_and_no_fabrication(m, category):
    raw = aggregate(None, [])
    raw["lab1"]["failure_category"] = category
    result = m.project_dual_lab_vrrp_summary(canonical(raw)).to_dict()
    assert result["lab1"] == raw["lab1"]
    assert result["cross_target_observations"] == [obs("RESULT_AVAILABILITY", False, True)]


@pytest.mark.parametrize("parser", ["project_dual_lab_vrrp_summary", "parse_summary_canonical_json"])
def test_26_39_invalid_types_framing_limits_and_forged_objects(m, parser):
    function = getattr(m, parser)
    valid = canonical(aggregate() if parser.startswith("project") else empty_summary())
    class BytesSubclass(bytes):
        pass
    class Hostile:
        def __bytes__(self):
            raise AssertionError("must not coerce")
    for bad in (None, {}, [], True, 1, valid.decode(), bytearray(valid), memoryview(valid),
                BytesSubclass(valid), Hostile(), object.__new__(upstream.DualLabVrrpAggregate),
                b"", b"\xff", b"\xef\xbb\xbf" + valid, b" " + valid, valid + b"\n",
                b"null", b"[]", b"{}", b'{"x":NaN}', b'{"x":Infinity}',
                b"x" * 262145, b'{"x":' + b"[" * 2000 + b"0" + b"]" * 2000 + b"}"):
        reject(m, function, bad)
    reject(m, function, json.dumps(json.loads(valid), indent=2).encode())


@pytest.mark.parametrize("location", ["aggregate", "target", "evidence", "record"])
def test_27_extra_aggregate_fields_rejected_upstream(m, location):
    raw = aggregate([record()], [])
    container = {"aggregate": raw, "target": raw["lab1"],
        "evidence": raw["lab1"]["evidence"], "record": raw["lab1"]["evidence"]["records"][0]}[location]
    for field in SENSITIVE + ("cross_target_observations",):
        if field in container:
            continue
        container[field] = SENTINEL
        reject(m, m.project_dual_lab_vrrp_summary, canonical(raw))
        del container[field]


@pytest.mark.parametrize("change", ["swap", "fixed", "evidence", "operation", "order", "schema", "query"])
def test_28_29_upstream_binding_and_identity_rejections(m, change):
    raw = aggregate([record()], [record()])
    if change == "swap":
        raw["lab1"], raw["lab2"] = raw["lab2"], raw["lab1"]
    elif change == "fixed":
        raw["lab1"]["target_ref"] = "target.other"
    elif change == "evidence":
        raw["lab1"]["evidence"]["target_ref"] = LAB2
    else:
        raw[{"operation": "operation_id", "order": "execution_order",
             "schema": "schema_version", "query": "query_id"}[change]] = SENTINEL
    reject(m, m.project_dual_lab_vrrp_summary, canonical(raw))


@pytest.mark.parametrize("label", PROHIBITED)
def test_30_to_34_prohibited_structures_and_opaque_observed_names(m, label):
    raw = one_summary()
    raw["cross_target_observations"][0]["kind"] = label
    reject(m, m.parse_summary_canonical_json, canonical(raw))
    raw = one_summary()
    raw[label] = SENTINEL
    reject(m, m.parse_summary_canonical_json, canonical(raw))
    assert project(m, [record(instance_name=label)]).lab1.records[0].instance_name == label


def test_33_command_like_name_remains_only_data(m):
    name = "synthetic command-like name; do-nothing"
    result = project(m, [record(instance_name=name)]).to_dict()
    assert result["lab1"]["records"][0]["instance_name"] == name
    assert set(result) == set(empty_summary())


def test_35_36_42_static_public_surface_and_inert_import(m, monkeypatch):
    expected = {"DualLabVrrpSummary", "DualLabSummaryError", "project_dual_lab_vrrp_summary",
                "parse_summary_canonical_json"}
    assert set(m.__all__) == expected
    assert {n for n in vars(m) if not n.startswith("_")} == expected
    for name in ("project_dual_lab_vrrp_summary", "parse_summary_canonical_json"):
        assert list(inspect.signature(getattr(m, name)).parameters) == ["raw"]
    tree = ast.parse(inspect.getsource(m))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.Yield, ast.YieldFrom))
        if isinstance(node, ast.Import):
            assert all(a.name in {"json", "dataclasses", "functools"} for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in {"dataclasses", "functools", "validation_framework"}
            if node.module == "validation_framework":
                assert all(a.name in {"dual_lab_vrrp_query_contract", "stage2_vrrp_readonly_contract"}
                           for a in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"open", "exec", "eval", "__import__", "print", "input"}
    source = canonical(aggregate([record()], [record()]))
    summary = canonical(one_summary())
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("forbidden side effect")
    with monkeypatch.context() as guarded:
        guarded.setattr(builtins, "open", forbidden)
        guarded.setattr(socket, "create_connection", forbidden)
        guarded.setattr(socket, "getaddrinfo", forbidden)
        guarded.setattr(subprocess, "Popen", forbidden)
        before = set(sys.modules)
        importlib.reload(m)
        for function, data in ((m.project_dual_lab_vrrp_summary, source),
                               (m.parse_summary_canonical_json, summary)):
            value = function(data)
            assert value.to_canonical_bytes() == summary
            assert value.to_dict() == one_summary()
            reject(m, function, b"invalid")
        added = set(sys.modules) - before
    assert calls == []
    assert not any(any(part in name for part in ("orchestrator", "live_entrypoint", "openai",
        "anthropic", "paramiko", "requests", "httpx")) for name in added)


@pytest.mark.parametrize("needle", [b'"schema_version":"dual-lab-vrrp-query-summary.v1"',
    b'"target_ref":"target.mikrotik.lab01"', b'"priority":100',
    b'"kind":"FIELD_EQUAL"', b'"field":"role"'])
def test_39_summary_duplicate_keys_at_each_depth(m, needle):
    raw = canonical(one_summary())
    assert needle in raw
    reject(m, m.parse_summary_canonical_json, raw.replace(needle, needle + b"," + needle, 1))


@pytest.mark.parametrize("needle", [b'"schema_version":"dual-lab-vrrp-query.v1"',
    b'"status":"SUCCESS"', b'"duration_ms":1', b'"priority":100'])
def test_39_aggregate_duplicate_keys_at_each_depth(m, needle):
    raw = canonical(aggregate([record()], []))
    reject(m, m.project_dual_lab_vrrp_summary, raw.replace(needle, needle + b"," + needle, 1))


@pytest.mark.parametrize("change", ["missing", "extra", "order", "value", "bool-as-int", "subject", "field"])
def test_39_derived_rows_recomputed_and_exactly_typed(m, change):
    raw = one_summary()
    rows = raw["cross_target_observations"]
    if change == "missing":
        rows.pop()
    elif change == "extra":
        rows.append(deepcopy(rows[-1]))
    elif change == "order":
        rows.reverse()
    elif change == "value":
        rows[-1]["lab1_value"] = True
    elif change == "bool-as-int":
        rows[0]["lab1_value"] = 1
    elif change == "subject":
        rows[-1]["subject"]["vrid"] = 89
    else:
        rows[-1]["subject"]["field"] = "vrid"
    reject(m, m.parse_summary_canonical_json, canonical(raw))


def test_39_summary_parser_does_not_repair_unsorted_records(m):
    raw = project(m, [record(instance_name="a"), record(instance_name="z")]).to_dict()
    raw["lab1"]["records"].reverse()
    reject(m, m.parse_summary_canonical_json, canonical(raw))


def test_40_frozen_nested_objects_fresh_exports_and_sanitized_repr(m):
    raw = aggregate([record()], [record()])
    value = m.project_dual_lab_vrrp_summary(canonical(raw))
    objects = [value, value.lab1, value.lab1.records[0], value.cross_target_observations[-1],
               value.cross_target_observations[-1].subject]
    for obj in objects:
        assert not hasattr(obj, "__dict__")
        assert repr(obj) == str(obj) == "<inert-dual-lab-summary>"
        name = fields(obj)[0].name
        with pytest.raises(FrozenInstanceError):
            setattr(obj, name, None)
    assert type(value.lab1.records) is tuple
    assert type(value.cross_target_observations) is tuple
    assert type(value.cross_target_observations[1].lab1_value) is tuple
    exported = value.to_dict()
    exported["lab1"]["records"].clear()
    exported["cross_target_observations"][-1]["subject"]["vrid"] = 99
    raw["lab1"]["evidence"]["records"].clear()
    assert value.to_dict() == one_summary()
    assert value.to_canonical_bytes() == canonical(one_summary())


@pytest.mark.parametrize("where,field,bad", [
    ("top", "query_id", "invalid"), ("target", "target_ref", LAB2),
    ("record", "priority", True), ("record", "vrid", 999),
    ("row", "lab1_value", True), ("subject", "vrid", 99),
    ("top", "cross_target_observations", ()), ("target", "records", [])])
def test_40_serializers_revalidate_tampering(m, where, field, bad):
    value = project(m, [record()], [record()])
    obj = {"top": value, "target": value.lab1, "record": value.lab1.records[0],
           "row": value.cross_target_observations[-1],
           "subject": value.cross_target_observations[-1].subject}[where]
    object.__setattr__(obj, field, bad)
    reject(m, lambda _: value.to_dict(), None)
    reject(m, lambda _: value.to_canonical_bytes(), None)
    assert value.execution_authorized is False


@pytest.mark.parametrize("name", ['"' * 128, "\\" * 128, "é" * 64])
def test_41_maximum_records_name_lengths_and_serialization_bounds(m, name):
    records = [record(instance_name=name, vrid=i + 1) for i in range(32)]
    value = project(m, records[::-1], records)
    assert len(value.lab1.records) == 32
    assert len(value.cross_target_observations) == 228
    assert len(value.to_canonical_bytes()) <= 262144
    assert m.parse_summary_canonical_json(value.to_canonical_bytes()).to_dict() == value.to_dict()
    reject(m, m.project_dual_lab_vrrp_summary, canonical(aggregate(records + [record()], [])))


def test_41_unicode_sort_and_duplicate_heavy_inputs(m):
    records = [record(instance_name=n) for n in ("é", "a", "Ω", "Z")]
    assert [r.instance_name for r in project(m, records).lab1.records] == ["Z", "a", "é", "Ω"]
    raw = project(m, [record()] * 32, [record()] * 32).to_dict()
    assert len(raw["lab1"]["records"]) == 32
    assert raw["cross_target_observations"][-1] == obs("MATCH_KEY_MULTIPLICITY", 32, 32, key())


def test_public_errors_discard_outer_context_and_upstream_failure(m, monkeypatch, capsys):
    try:
        raise RuntimeError(SENTINEL)
    except RuntimeError:
        reject(m, m.project_dual_lab_vrrp_summary, b"bad")
    def broken(*args, **kwargs):
        raise RuntimeError(SENTINEL)
    monkeypatch.setattr(upstream, "parse_aggregate_canonical_json", broken)
    reject(m, m.project_dual_lab_vrrp_summary, canonical(aggregate()))
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("field,bad", [("schema_version", "dual-lab-vrrp-query.v1"),
    ("query_id", "invalid"), ("query_id", "query." + "a" * 155),
    ("operation_id", "other.operation"), ("execution_order", "LAB2_THEN_LAB1")])
def test_summary_identity_has_its_own_strict_boundary(m, field, bad):
    raw = empty_summary()
    raw[field] = bad
    reject(m, m.parse_summary_canonical_json, canonical(raw))


@pytest.mark.parametrize("change", ["swap", "target", "status", "failure_category"])
def test_summary_target_binding_and_tag_validation(m, change):
    raw = project(m, None, None).to_dict()
    if change == "swap":
        raw["lab1"], raw["lab2"] = raw["lab2"], raw["lab1"]
    else:
        raw["lab1"][{"target": "target_ref", "status": "status",
                     "failure_category": "failure_category"}[change]] = SENTINEL
    reject(m, m.parse_summary_canonical_json, canonical(raw))


def test_uninitialized_subclassed_and_callback_bearing_dtos_fail_closed(m):
    calls = []
    class Forged(m.DualLabVrrpSummary):
        def to_dict(self):
            calls.append(True)
            return empty_summary()
    subclass = object.__new__(Forged)
    reject(m, lambda _: m.DualLabVrrpSummary.to_dict(subclass), None)
    reject(m, lambda _: m.DualLabVrrpSummary.to_canonical_bytes(subclass), None)
    assert calls == []
    missing = object.__new__(m.DualLabVrrpSummary)
    reject(m, lambda _: missing.to_dict(), None)
    reject(m, lambda _: missing.to_canonical_bytes(), None)
    reject(m, lambda _: m.DualLabVrrpSummary(), None)
    value = project(m)
    object.__setattr__(value, "lab1", subclass)
    reject(m, lambda _: value.to_dict(), None)
    assert calls == []


def test_summary_parser_does_not_invoke_projection(m, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("summary parsing must not invoke projection or aggregate parsing")
    monkeypatch.setattr(m, "project_dual_lab_vrrp_summary", forbidden)
    monkeypatch.setattr(upstream, "parse_aggregate_canonical_json", forbidden)
    assert m.parse_summary_canonical_json(canonical(one_summary())).to_dict() == one_summary()
