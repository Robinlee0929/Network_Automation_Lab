"""DL-06-01 canonical data tests; synthetic summaries, no observation runtime."""

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
import time

import pytest

from validation_framework import dual_lab_vrrp_query_contract as contract
from validation_framework import dual_lab_vrrp_query_summary as summary
from validation_framework import dual_lab_vrrp_transition as m


LAB1, LAB2 = "target.mikrotik.lab01", "target.mikrotik.lab02"
SCHEMA = "dual-lab-vrrp-transition.v1"
KINDS = ("TARGET_RESULT_STATUS_CHANGED", "ROLE_CHANGED", "RUNNING_CHANGED",
         "PRIORITY_CHANGED", "INTERVAL_CHANGED", "VERSION_CHANGED",
         "VRID_SET_CHANGED", "MASTER_TARGET_CHANGED", "OBSERVATION_GAP")
SENTINEL = "synthetic-private-payload"


def canonical(raw):
    return json.dumps(raw, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def record(**changes):
    return {"instance_name": "vrrp-synthetic", "vrid": 88, "role": "BACKUP",
            "running": False, "priority": 100, "interval_ms": 1000, "version": 3,
            "disabled": False, "invalid": False, **changes}


def target(ref, records):
    if records is None or type(records) is str:
        return {"status": "FAILURE", "target_ref": ref,
                "failure_category": records or "TRUSTED_RUNTIME_FAILED"}
    return {"status": "SUCCESS", "target_ref": ref, "evidence": {
        "schema_version": "1.0", "operation_id": "mikrotik.vrrp_status",
        "run_id": "run.synthetic", "target_ref": ref,
        "authorization_ref": "authorization.synthetic",
        "command_policy_version": "policy.stage2.vrrp-readonly.v1",
        "attempt_count": 1, "retry_count": 0, "duration_ms": 1,
        "raw_output_byte_count": 0, "raw_output_sha256": "a" * 64,
        "records": deepcopy(records)}}


def snapshot(index, left=(), right=()):
    aggregate = {"schema_version": "dual-lab-vrrp-query.v1", "query_id": f"query.sample{index}",
                 "operation_id": "mikrotik.vrrp_status", "execution_order": "LAB1_THEN_LAB2",
                 "lab1": target(LAB1, left), "lab2": target(LAB2, right)}
    return summary.project_dual_lab_vrrp_summary(canonical(aggregate)).to_dict()


def source(pairs=(((), ()),), *, planned=None, reason="COUNT_REACHED", elapsed=None):
    samples = [{"sample_index": i, "elapsed_start_ms": (i - 1) * 2001,
                "elapsed_finish_ms": (i - 1) * 2001 + 1,
                "summary": snapshot(i, left, right)}
               for i, (left, right) in enumerate(pairs, 1)]
    return {"schema_version": SCHEMA, "timeline_id": "timeline.synthetic",
            "execution_order": "LAB1_THEN_LAB2", "planned_sample_count": planned or len(samples) or 1,
            "inter_sample_delay_ms": 2000, "max_duration_ms": 30000, "samples": samples,
            "termination": {"reason": reason, "elapsed_ms": elapsed if elapsed is not None
                            else samples[-1]["elapsed_finish_ms"] if samples else 0}}


def project(raw):
    return m.project_dual_lab_vrrp_transition(canonical(raw))


def fact(kind, first, last, target_ref, before, after, subject=None):
    return {"kind": kind, "from_sample": first, "to_sample": last, "target_ref": target_ref,
            "subject": subject, "from_value": before, "to_value": after}


def key(name="vrrp-synthetic", vrid=88):
    return {"instance_name": name, "vrid": vrid}


def reject(function, raw):
    with pytest.raises(m.DualLabTransitionError) as caught:
        function(raw)
    error = caught.value
    assert error.args == ("invalid Dual-Lab transition",)
    assert error.__cause__ is None and error.__context__ is None
    assert SENTINEL not in str(error) + repr(error) + repr(vars(error))


def reject_source(raw):
    reject(m.project_dual_lab_vrrp_transition, canonical(raw))
    reject(m.parse_transition_canonical_json, canonical({**raw, "facts": []}))


def test_single_identical_and_empty_success_samples_have_no_facts():
    for pairs in ((((), ()),), (([record()], [record()]),),
                  (([record()], [record()]), ([record()], [record()]))):
        raw = source(pairs)
        value = project(raw)
        assert value.to_dict() == {**raw, "facts": []}
        assert value.to_canonical_bytes() == canonical({**raw, "facts": []})
        assert m.parse_transition_canonical_json(value.to_canonical_bytes()).to_dict() == value.to_dict()
        assert value.execution_authorized is False
        assert {f.name for f in fields(value)} == set(raw) | {"facts"}


@pytest.mark.parametrize("field,new,kind", [
    ("role", "MASTER", "ROLE_CHANGED"), ("running", True, "RUNNING_CHANGED"),
    ("priority", 150, "PRIORITY_CHANGED"), ("interval_ms", 2000, "INTERVAL_CHANGED"),
    ("version", 2, "VERSION_CHANGED")])
@pytest.mark.parametrize("target_index", [0, 1])
def test_exact_field_changes_both_targets_and_directions(field, new, kind, target_index):
    first, second = [[record()], [record()]], [[record()], [record()]]
    second[target_index] = [record(**{field: new})]
    for a, b in ((first, second), (second, first)):
        raw = project(source((a, b))).to_dict()
        assert raw["facts"] == [fact(kind, 1, 2, (LAB1, LAB2)[target_index],
                                     a[target_index][0][field], b[target_index][0][field], key())]


def test_vrid_sets_are_sorted_distinct_and_unmatched_records_have_count_gaps():
    left = [record(vrid=9), record(vrid=2), record(vrid=2)]
    right = [record(vrid=1), record(vrid=9)]
    rows = project(source(((left, []), (right, [])))).to_dict()["facts"]
    assert rows == [fact("VRID_SET_CHANGED", 1, 2, LAB1, [2, 9], [1, 9]),
                    fact("OBSERVATION_GAP", 1, 2, LAB1, 0, 1, key(vrid=1)),
                    fact("OBSERVATION_GAP", 1, 2, LAB1, 2, 0, key(vrid=2))]


def test_manual_transition_gap_then_later_sample_is_facts_only():
    master, backup = [record(role="MASTER")], [record()]
    raw = source(((master, backup), (master, backup), (None, master), (backup, master)))
    rows = project(raw).to_dict()["facts"]
    assert rows == [fact("TARGET_RESULT_STATUS_CHANGED", 2, 3, LAB1, "SUCCESS", "FAILURE"),
                    fact("ROLE_CHANGED", 2, 3, LAB2, "BACKUP", "MASTER", key()),
                    fact("OBSERVATION_GAP", 3, 3, LAB1, None, "TRUSTED_RUNTIME_FAILED"),
                    fact("TARGET_RESULT_STATUS_CHANGED", 3, 4, LAB1, "FAILURE", "SUCCESS")]
    assert not any(r["kind"] == "MASTER_TARGET_CHANGED" for r in rows)
    assert m.parse_transition_canonical_json(project(raw).to_canonical_bytes()).to_dict()["facts"] == rows


@pytest.mark.parametrize("left,right", product((None, []), repeat=2))
def test_first_and_consecutive_failure_samples_keep_gaps_without_inventing_state(left, right):
    rows = project(source(((left, right), (left, right)))).to_dict()["facts"]
    assert rows == [fact("OBSERVATION_GAP", i, i, ref, None, "TRUSTED_RUNTIME_FAILED")
                    for i in (1, 2) for ref, records in ((LAB1, left), (LAB2, right)) if records is None]


@pytest.mark.parametrize("reverse", [False, True])
def test_complete_master_movement_is_conservative_and_bidirectional(reverse):
    a = ([record(role="MASTER")], [record()])
    b = ([record()], [record(role="MASTER")])
    if reverse:
        a, b = b, a
    rows = project(source((a, b))).to_dict()["facts"]
    assert rows == [fact("ROLE_CHANGED", 1, 2, LAB1, a[0][0]["role"], b[0][0]["role"], key()),
                    fact("ROLE_CHANGED", 1, 2, LAB2, a[1][0]["role"], b[1][0]["role"], key()),
                    fact("MASTER_TARGET_CHANGED", 1, 2, None,
                         LAB2 if reverse else LAB1, LAB1 if reverse else LAB2, key())]


@pytest.mark.parametrize("position", range(4))
@pytest.mark.parametrize("condition", ["failure", "empty", "duplicate", "disabled", "invalid",
                                      "unknown", "both-master", "both-backup", "different-key"])
def test_master_movement_never_guessed_with_insufficient_evidence(position, condition):
    targets = [[record(role="MASTER")], [record()], [record()], [record(role="MASTER")]]
    if condition == "failure":
        targets[position] = None
    elif condition == "empty":
        targets[position] = []
    elif condition == "duplicate":
        targets[position] *= 2
    else:
        change = {"disabled": {"disabled": True}, "invalid": {"invalid": True},
                  "unknown": {"role": "UNKNOWN"}, "both-master": {"role": "MASTER"},
                  "both-backup": {"role": "BACKUP"}, "different-key": {"instance_name": "other"}}[condition]
        targets[position][0].update(change)
        # Ensure the chosen pair loses complementary roles for the pair cases.
        if condition in ("both-master", "both-backup"):
            targets[position ^ 1][0].update(change)
    rows = project(source(((targets[0], targets[1]), (targets[2], targets[3])))).to_dict()["facts"]
    assert "MASTER_TARGET_CHANGED" not in [row["kind"] for row in rows]


def test_running_is_not_a_master_health_predicate_and_flags_do_not_hide_field_changes():
    pairs = (([record(role="MASTER", running=False)], [record(running=True)]),
             ([record(running=True)], [record(role="MASTER", running=False)]))
    assert "MASTER_TARGET_CHANGED" in [r["kind"] for r in project(source(pairs)).to_dict()["facts"]]
    rows = project(source((([record(disabled=True)], []),
                           ([record(role="MASTER", disabled=True, invalid=True)], [])))).to_dict()["facts"]
    assert rows == [fact("ROLE_CHANGED", 1, 2, LAB1, "BACKUP", "MASTER", key())]


@pytest.mark.parametrize("a,b", [(0, 1), (1, 0), (1, 2), (2, 1), (2, 2), (32, 32)])
def test_missing_duplicate_keys_keep_multiplicity_without_pairing(a, b):
    rows = project(source((([record()] * a, []), ([record(role="MASTER")] * b, [])))).to_dict()["facts"]
    assert rows[-1] == fact("OBSERVATION_GAP", 1, 2, LAB1, a, b, key())
    assert not any(row["kind"] in ("ROLE_CHANGED", "MASTER_TARGET_CHANGED") for row in rows)


def test_order_is_sample_then_kind_then_target_then_unicode_subject():
    names = ("Ω", "é", "a", "Z")
    old = [record(instance_name=n) for n in names]
    new = [record(instance_name=n, role="MASTER", running=True, priority=200,
                  interval_ms=2000, version=2) for n in reversed(names)]
    value = project(source(((old, old), (new, new), (old, old))))
    rows = value.to_dict()["facts"]
    expected = []
    for first, last, before, after in ((1, 2, old[0], new[0]), (2, 3, new[0], old[0])):
        for kind, field in (("ROLE_CHANGED", "role"), ("RUNNING_CHANGED", "running"),
                            ("PRIORITY_CHANGED", "priority"), ("INTERVAL_CHANGED", "interval_ms"),
                            ("VERSION_CHANGED", "version")):
            for ref in (LAB1, LAB2):
                expected.extend(fact(kind, first, last, ref, before[field], after[field], key(n))
                                for n in sorted(names))
    assert rows == expected
    for _ in range(3):
        assert project(source(((old[::-1], old), (new, new[::-1]), (old, old)))).to_canonical_bytes() == value.to_canonical_bytes()


@pytest.mark.parametrize("reason,planned,elapsed,pairs", [
    ("PRECHECK_REJECTED", 1, 0, ()), ("SESSION_INTEGRITY_FAILURE", 2, 0, ()),
    ("INVALID_SAMPLE", 1, 0, ()), ("DURATION_LIMIT", 1, 30000, ()),
    ("COUNT_REACHED", 1, 1, ((None, []),)),
    ("DURATION_LIMIT", 2, 30000, ((None, []),)),
    ("INVALID_SAMPLE", 2, 5, ((None, []),)),
    ("SESSION_INTEGRITY_FAILURE", 2, 5, (([], []),)),
    ("SESSION_INTEGRITY_FAILURE", 1, 1, (("INTERNAL_FAILURE", []),))])
def test_all_termination_branches_and_valid_failure_prefixes(reason, planned, elapsed, pairs):
    value = project(source(pairs, reason=reason, planned=planned, elapsed=elapsed))
    assert value.termination.reason == reason
    assert m.parse_transition_canonical_json(value.to_canonical_bytes()).to_dict() == value.to_dict()


@pytest.mark.parametrize("category", [c.value for c in contract.FailureCategory
                                       if c.value != "TRUSTED_RUNTIME_FAILED"])
def test_known_integrity_categories_require_final_sample_and_fatal_termination(category):
    value = project(source(((None, []), (category, [])), reason="SESSION_INTEGRITY_FAILURE"))
    assert value.samples[-1].summary.lab1.failure_category == category
    reject_source(source(((category, []),), reason="COUNT_REACHED"))
    reject_source(source(((category, []), ([], [])), reason="SESSION_INTEGRITY_FAILURE"))


@pytest.mark.parametrize("reason,planned,elapsed,count", [
    ("COUNT_REACHED", 2, 1, 1), ("COUNT_REACHED", 1, 0, 0),
    ("DURATION_LIMIT", 1, 30000, 1), ("DURATION_LIMIT", 2, 29999, 1),
    ("PRECHECK_REJECTED", 2, 1, 1), ("PRECHECK_REJECTED", 1, 1, 0),
    ("INVALID_SAMPLE", 1, 1, 1), ("SESSION_INTEGRITY_FAILURE", 1, 0, 1),
    ("TARGET_FAILURE", 1, 1, 1), (True, 1, 1, 1)])
def test_invalid_termination_combinations(reason, planned, elapsed, count):
    reject_source(source(tuple(([], []) for _ in range(count)), planned=planned, reason=reason, elapsed=elapsed))


def test_maximum_samples_exact_deadline_and_reference_length():
    raw = source(tuple(([], []) for _ in range(10)))
    raw["samples"][-1]["elapsed_finish_ms"] = 30000
    raw["termination"]["elapsed_ms"] = 30000
    raw["timeline_id"] = "timeline." + "a" * 151
    value = project(raw)
    assert len(value.samples) == 10 and value.samples[-1].elapsed_finish_ms == 30000
    assert value.to_dict() == {**raw, "facts": []}
    raw["samples"][-1]["elapsed_finish_ms"] = 30001
    reject_source(raw)
    reject_source(source(tuple(([], []) for _ in range(11))))


@pytest.mark.parametrize("field,bad", [
    ("schema_version", "dual-lab-vrrp-transition.v2"), ("schema_version", None),
    ("timeline_id", "query.synthetic"), ("timeline_id", "timeline."),
    ("timeline_id", "timeline.A"), ("timeline_id", "timeline.a..b"),
    ("timeline_id", "timeline.a\n"), ("timeline_id", "timeline.é"),
    ("timeline_id", "timeline." + "a" * 152), ("timeline_id", True),
    ("execution_order", "LAB2_THEN_LAB1"), ("planned_sample_count", 0),
    ("planned_sample_count", 11), ("planned_sample_count", True),
    ("planned_sample_count", 1.0), ("inter_sample_delay_ms", 1999),
    ("inter_sample_delay_ms", 2001), ("inter_sample_delay_ms", True),
    ("max_duration_ms", 30001), ("max_duration_ms", False), ("samples", {}),
    ("termination", None)])
def test_exact_top_level_domains(field, bad):
    raw = source()
    raw[field] = bad
    reject_source(raw)


@pytest.mark.parametrize("where,field,bad", [
    (0, "sample_index", 0), (0, "sample_index", True), (1, "sample_index", 1),
    (1, "sample_index", 3), (0, "elapsed_start_ms", -1), (0, "elapsed_start_ms", 1),
    (0, "elapsed_start_ms", False), (0, "elapsed_finish_ms", -1),
    (0, "elapsed_finish_ms", True), (0, "elapsed_finish_ms", 1.0),
    (1, "elapsed_start_ms", 0), (1, "elapsed_start_ms", 2000),
    (1, "elapsed_start_ms", 2003), (1, "elapsed_finish_ms", 30001),
    (1, "summary", []), (1, "summary", None)])
def test_indices_windows_and_sample_domains(where, field, bad):
    raw = source((([], []), ([], [])))
    raw["samples"][where][field] = bad
    reject_source(raw)


def test_reordering_and_repeated_query_identity_reject_without_repair():
    raw = source((([], []), ([], [])))
    raw["samples"].reverse()
    reject_source(raw)
    raw = source((([], []), ([], [])))
    raw["samples"][1]["summary"]["query_id"] = raw["samples"][0]["summary"]["query_id"]
    reject_source(raw)


@pytest.mark.parametrize("bad", [-1, True, 1.0, "1", 30001, None])
def test_termination_elapsed_exact_integer_domain(bad):
    raw = source()
    raw["termination"]["elapsed_ms"] = bad
    reject_source(raw)


def rich_source():
    return source((([record()], []), ([record(role="MASTER", running=True, vrid=88), record(vrid=99)], [])))


@pytest.mark.parametrize("where", ["top", "sample", "termination", "summary", "target", "record", "fact", "subject"])
def test_every_nested_field_is_required_and_unknown_fields_rejected(where):
    raw = project(rich_source()).to_dict()
    row = next(row for row in raw["facts"] if row["kind"] == "ROLE_CHANGED")
    container = {"top": raw, "sample": raw["samples"][0], "termination": raw["termination"],
                 "summary": raw["samples"][0]["summary"], "target": raw["samples"][0]["summary"]["lab1"],
                 "record": raw["samples"][0]["summary"]["lab1"]["records"][0],
                 "fact": row, "subject": row["subject"]}[where]
    for name in list(container):
        saved = container.pop(name)
        reject(m.parse_transition_canonical_json, canonical(raw))
        container[name] = saved
    for name in ("extra", "authorization_ref", "raw_stdout", "execution_authorized", "retry"):
        container[name] = SENTINEL
        reject(m.parse_transition_canonical_json, canonical(raw))
        del container[name]


@pytest.mark.parametrize("change", ["schema", "record", "forged-observation", "unsorted", "record-limit"])
def test_embedded_summary_validation_is_reused(change):
    raw = source((([record(instance_name="a"), record(instance_name="b")], []),))
    embedded = raw["samples"][0]["summary"]
    if change == "schema":
        embedded["schema_version"] = SCHEMA
    elif change == "record":
        embedded["lab1"]["records"][0]["priority"] = True
    elif change == "forged-observation":
        embedded["cross_target_observations"][0]["lab1_value"] = False
    elif change == "unsorted":
        embedded["lab1"]["records"].reverse()
    else:
        embedded["lab1"]["records"] *= 17
    reject_source(raw)


@pytest.mark.parametrize("change", ["missing", "extra", "reverse", "value", "bool-alias", "subject",
                                     "index-alias", "target", "unknown", "fact-limit", "fact-type"])
def test_facts_are_recomputed_never_trusted(change):
    raw = project(rich_source()).to_dict()
    rows = raw["facts"]
    if change == "missing":
        rows.pop()
    elif change == "extra":
        rows.append(deepcopy(rows[0]))
    elif change == "reverse":
        rows.reverse()
    elif change == "value":
        rows[0]["to_value"] = "BACKUP"
    elif change == "bool-alias":
        next(row for row in rows if row["kind"] == "RUNNING_CHANGED")["to_value"] = 1
    elif change == "subject":
        rows[0]["subject"]["vrid"] = 99
    elif change == "index-alias":
        rows[0]["from_sample"] = True
    elif change == "target":
        rows[0]["target_ref"] = LAB2
    elif change == "unknown":
        rows[0]["kind"] = "NEW_FACT"
    elif change == "fact-limit":
        raw["facts"] = [rows[0]] * 4097
    else:
        raw["facts"] = {}
    reject(m.parse_transition_canonical_json, canonical(raw))


@pytest.mark.parametrize("kind", ["HEALTHY", "UNHEALTHY", "FAILOVER_SUCCESS", "FAILOVER_READY",
                                    "SPLIT_BRAIN", "RECOVERY_SUCCESS", "EXPECTED", "UNEXPECTED",
                                    "RECOMMENDED_ACTION"])
def test_interpretive_verdicts_are_not_fact_kinds(kind):
    raw = project(rich_source()).to_dict()
    raw["facts"][0]["kind"] = kind
    reject(m.parse_transition_canonical_json, canonical(raw))
    # Names remain opaque observed data, never instructions or verdicts.
    assert project(source((([record(instance_name=kind)], []),))).facts == ()


@pytest.mark.parametrize("parser", ["project_dual_lab_vrrp_transition", "parse_transition_canonical_json"])
def test_strict_bytes_types_framing_and_size(parser):
    function = getattr(m, parser)
    valid = canonical(source()) if parser.startswith("project") else project(source()).to_canonical_bytes()
    class BytesSubclass(bytes):
        pass
    class Hostile:
        def __bytes__(self):
            pytest.fail("must not coerce inputs")
    invalid = (None, {}, [], True, 1, valid.decode(), bytearray(valid), memoryview(valid),
               BytesSubclass(valid), Hostile(), b"", b"\xff", b"\xef\xbb\xbf" + valid,
               b" " + valid, valid + b"\n", b"null", b"[]", b"{}", b'{"x":NaN}',
               b'{"x":Infinity}', b'{"x":-Infinity}', b"x" * 4_194_305,
               b"[" * 2000 + b"0" + b"]" * 2000)
    for raw in invalid:
        reject(function, raw)
    reject(function, json.dumps(json.loads(valid), indent=2).encode())
    reject(function, canonical(json.loads(valid)).replace(b'"schema_version"', b'"schema_versio\\u006e"', 1))


@pytest.mark.parametrize("needle", [b'"schema_version":"dual-lab-vrrp-transition.v1"',
    b'"sample_index":1', b'"reason":"COUNT_REACHED"', b'"query_id":"query.sample1"',
    b'"target_ref":"target.mikrotik.lab01"', b'"priority":100',
    b'"kind":"ROLE_CHANGED"', b'"instance_name":"vrrp-synthetic"'])
def test_duplicate_keys_rejected_at_all_depths(needle):
    raw = project(rich_source()).to_canonical_bytes()
    assert needle in raw
    reject(m.parse_transition_canonical_json, raw.replace(needle, needle + b"," + needle, 1))


def test_immutable_values_fresh_exports_and_bounded_repr():
    raw = rich_source()
    original = deepcopy(raw)
    value = project(raw)
    expected = value.to_canonical_bytes()
    assert raw == original
    objects = [value, value.samples[0], value.termination, *value.facts,
               *[row.subject for row in value.facts if row.subject is not None]]
    for obj in objects:
        assert obj.execution_authorized is False
        assert not hasattr(obj, "__dict__")
        assert repr(obj) == str(obj) == "<inert-dual-lab-transition>"
        with pytest.raises(FrozenInstanceError):
            setattr(obj, fields(obj)[0].name, None)
    assert value.samples[0].summary.execution_authorized is False
    assert type(value.samples) is type(value.facts) is tuple
    assert type(next(row for row in value.facts if row.kind == "VRID_SET_CHANGED").to_value) is tuple
    raw["samples"].clear()
    exported = value.to_dict()
    exported["samples"][0]["summary"]["lab1"]["records"].clear()
    exported["facts"][0]["subject"]["vrid"] = 1
    assert value.to_canonical_bytes() == expected


@pytest.mark.parametrize("where,field,bad", [
    ("top", "timeline_id", "bad"), ("top", "samples", []), ("top", "facts", ()),
    ("sample", "sample_index", True), ("sample", "elapsed_finish_ms", 30001),
    ("sample", "summary", {}), ("summary", "query_id", "bad"),
    ("record", "priority", True), ("termination", "elapsed_ms", 0),
    ("fact", "to_value", "wrong"), ("subject", "vrid", True)])
def test_serializers_revalidate_exact_type_nested_tampering(where, field, bad):
    value = project(rich_source())
    obj = {"top": value, "sample": value.samples[0], "summary": value.samples[0].summary,
           "record": value.samples[0].summary.lab1.records[0], "termination": value.termination,
           "fact": value.facts[0], "subject": value.facts[0].subject}[where]
    object.__setattr__(obj, field, bad)
    reject(lambda _: value.to_dict(), None)
    reject(lambda _: value.to_canonical_bytes(), None)
    assert value.execution_authorized is False


def test_factory_only_uninitialized_and_subclass_values_do_not_invoke_callbacks():
    calls = []
    class Forged(m.DualLabVrrpTransition):
        def to_dict(self):
            calls.append(True)
            return {}
    for value in (object.__new__(Forged), object.__new__(m.DualLabVrrpTransition)):
        reject(lambda _: m.DualLabVrrpTransition.to_dict(value), None)
        reject(lambda _: m.DualLabVrrpTransition.to_canonical_bytes(value), None)
    reject(lambda _: m.DualLabVrrpTransition(), None)
    class ForgedSummary(summary.DualLabVrrpSummary):
        def to_dict(self):
            calls.append(True)
            return {}
    value = project(source())
    object.__setattr__(value.samples[0], "summary", object.__new__(ForgedSummary))
    reject(lambda _: value.to_dict(), None)
    assert calls == []


def test_large_bounded_record_sets_round_trip_and_all_nine_kinds_exist():
    # Worst-case field churn is finite; the limit is contractual, not a quota.
    a = [record(instance_name="é" * 64, vrid=i + 1) for i in range(32)]
    b = [dict(r, role="MASTER", running=True, priority=200, interval_ms=2000, version=2) for r in a]
    raw = source(tuple((a, b) if i % 2 == 0 else (b, a) for i in range(10)))
    value = project(raw)
    assert len(value.samples) == 10 and len(value.facts) == 3168
    assert len(value.to_canonical_bytes()) <= 4_194_304
    assert m.parse_transition_canonical_json(value.to_canonical_bytes()).to_dict() == value.to_dict()
    cases = [raw, source(((a, []), ([], []))), source(((None, []), ([], [])))]
    observed = {row["kind"] for case in cases for row in project(case).to_dict()["facts"]}
    assert observed == set(KINDS)


def test_public_errors_discard_child_and_outer_context(monkeypatch, capsys):
    try:
        raise RuntimeError(SENTINEL)
    except RuntimeError:
        reject(m.parse_transition_canonical_json, b"bad")
    raw = canonical(source())
    def broken(*args, **kwargs):
        raise RuntimeError(SENTINEL)
    monkeypatch.setattr(summary, "parse_summary_canonical_json", broken)
    reject(m.project_dual_lab_vrrp_transition, raw)
    assert capsys.readouterr() == ("", "")


def test_static_surface_and_import_projection_parsing_have_no_io(monkeypatch):
    public = {"DualLabVrrpTransition", "DualLabTransitionError",
              "project_dual_lab_vrrp_transition", "parse_transition_canonical_json"}
    assert set(m.__all__) == public
    assert {name for name in vars(m) if not name.startswith("_")} == public
    tree = ast.parse(inspect.getsource(m))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.Yield, ast.YieldFrom, ast.While))
        if isinstance(node, ast.Import):
            assert all(alias.name in {"json", "re"} for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in {"dataclasses", "functools", "validation_framework"}
            if node.module == "validation_framework":
                assert [alias.name for alias in node.names] == ["dual_lab_vrrp_query_summary"]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"open", "exec", "eval", "__import__", "print", "input"}
    raw = canonical(rich_source())
    expected = project(rich_source()).to_canonical_bytes()
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("forbidden side effect")
    with monkeypatch.context() as guard:
        guard.setattr(builtins, "open", forbidden)
        guard.setattr(socket, "socket", forbidden)
        guard.setattr(socket, "create_connection", forbidden)
        guard.setattr(socket, "getaddrinfo", forbidden)
        guard.setattr(subprocess, "Popen", forbidden)
        guard.setattr(time, "sleep", forbidden)
        before = set(sys.modules)
        importlib.reload(m)
        assert m.project_dual_lab_vrrp_transition(raw).to_canonical_bytes() == expected
        assert m.parse_transition_canonical_json(expected).to_canonical_bytes() == expected
        reject(m.project_dual_lab_vrrp_transition, b"bad")
        reject(m.parse_transition_canonical_json, b"bad")
        added = set(sys.modules) - before
    assert calls == []
    assert not any(any(part in name for part in ("orchestrator", "live_entrypoint", "paramiko",
                   "openai", "anthropic", "requests", "httpx", "network_lab")) for name in added)


def test_transition_parsing_never_uses_aggregate_or_summary_projection(monkeypatch):
    raw = project(source()).to_canonical_bytes()
    def forbidden(*args, **kwargs):
        pytest.fail("must reuse only the summary parser")
    monkeypatch.setattr(summary, "project_dual_lab_vrrp_summary", forbidden)
    monkeypatch.setattr(contract, "parse_aggregate_canonical_json", forbidden)
    assert m.parse_transition_canonical_json(raw).to_canonical_bytes() == raw
