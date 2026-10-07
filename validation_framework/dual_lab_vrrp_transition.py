"""DL-06-01 inert transition facts over sequential DL-03 observation windows.

Elapsed metadata is caller-supplied data, not a runtime deadline guarantee.
An offline gap followed by a sample neither classifies a live failure nor
authorizes continuation. No clock, collection, authority or execution lives here.
"""

from dataclasses import dataclass as _dataclass, fields as _members
from functools import wraps as _wraps
import json as _json
import re as _re

from validation_framework import dual_lab_vrrp_query_summary as _summary


_SCHEMA = "dual-lab-vrrp-transition.v1"
_TOP = frozenset(("schema_version", "timeline_id", "execution_order",
                  "planned_sample_count", "inter_sample_delay_ms", "max_duration_ms",
                  "samples", "termination", "facts"))
_SAMPLE = frozenset(("sample_index", "elapsed_start_ms", "elapsed_finish_ms", "summary"))
_REFERENCE = _re.compile(r"timeline\.[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*")
_MAX_BYTES = 4_194_304
_MAX_FACTS = 4096
_TARGETS = ("target.mikrotik.lab01", "target.mikrotik.lab02")
_KINDS = ("TARGET_RESULT_STATUS_CHANGED", "ROLE_CHANGED", "RUNNING_CHANGED",
          "PRIORITY_CHANGED", "INTERVAL_CHANGED", "VERSION_CHANGED",
          "VRID_SET_CHANGED", "MASTER_TARGET_CHANGED", "OBSERVATION_GAP")
_CHANGES = (("role", "ROLE_CHANGED"), ("running", "RUNNING_CHANGED"),
            ("priority", "PRIORITY_CHANGED"), ("interval_ms", "INTERVAL_CHANGED"),
            ("version", "VERSION_CHANGED"))
_REASONS = ("COUNT_REACHED", "SESSION_INTEGRITY_FAILURE", "DURATION_LIMIT",
            "PRECHECK_REJECTED", "INVALID_SAMPLE")


class DualLabTransitionError(ValueError):
    """Fixed rejection; no rejected payload or upstream exception is exposed."""

    def __init__(self):
        super().__init__("invalid Dual-Lab transition")


def _reject():
    try:
        raise DualLabTransitionError() from None
    except DualLabTransitionError as error:
        error.__context__ = None
        raise


def _checked(function):
    @_wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            pass
        args = kwargs = None
        _reject()
    return checked


class _Inert:
    __slots__ = ()

    def __repr__(self):
        return "<inert-dual-lab-transition>"

    __str__ = __repr__

    @property
    def execution_authorized(self):
        return False


@_dataclass(frozen=True, slots=True, repr=False)
class _Sample(_Inert):
    sample_index: int
    elapsed_start_ms: int
    elapsed_finish_ms: int
    summary: _summary.DualLabVrrpSummary


@_dataclass(frozen=True, slots=True, repr=False)
class _Termination(_Inert):
    reason: str
    elapsed_ms: int


@_dataclass(frozen=True, slots=True, repr=False)
class _Subject(_Inert):
    instance_name: str
    vrid: int


@_dataclass(frozen=True, slots=True, repr=False)
class _Fact(_Inert):
    kind: str
    from_sample: int
    to_sample: int
    target_ref: str | None
    subject: _Subject | None
    from_value: str | int | bool | tuple | None
    to_value: str | int | bool | tuple | None


@_dataclass(frozen=True, slots=True, repr=False, init=False)
class DualLabVrrpTransition(_Inert):
    """Factory-created immutable timeline; every export revalidates all data."""

    schema_version: str
    timeline_id: str
    execution_order: str
    planned_sample_count: int
    inter_sample_delay_ms: int
    max_duration_ms: int
    samples: tuple
    termination: _Termination
    facts: tuple

    def __init__(self, *args, **kwargs):
        _reject()

    @_checked
    def to_dict(self) -> dict[str, object]:
        if type(self) is not DualLabVrrpTransition:
            _reject()
        raw = _plain(self)
        _validate(raw, with_facts=True)
        _encode(raw)
        return raw

    @_checked
    def to_canonical_bytes(self) -> bytes:
        return _encode(DualLabVrrpTransition.to_dict(self))


_VALUES = (DualLabVrrpTransition, _Sample, _Termination, _Subject, _Fact)


def _plain(value):
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [_plain(item) for item in value]
    if type(value) is _summary.DualLabVrrpSummary:
        return _summary.DualLabVrrpSummary.to_dict(value)
    if type(value) in _VALUES:
        return {field.name: _plain(getattr(value, field.name)) for field in _members(value)}
    _reject()


def _fields(raw, expected):
    if type(raw) is not dict or raw.keys() != set(expected):
        _reject()


def _integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        _reject()


def _validate(raw, *, with_facts):
    _fields(raw, _TOP if with_facts else _TOP - {"facts"})
    for field, expected in (("schema_version", _SCHEMA), ("execution_order", "LAB1_THEN_LAB2")):
        if type(raw[field]) is not str or raw[field] != expected:
            _reject()
    identity = raw["timeline_id"]
    if type(identity) is not str or not 1 <= len(identity) <= 160 or not _REFERENCE.fullmatch(identity):
        _reject()
    _integer(raw["planned_sample_count"], 1, 10)
    _integer(raw["inter_sample_delay_ms"], 2000, 2000)
    _integer(raw["max_duration_ms"], 30000, 30000)
    samples = raw["samples"]
    if type(samples) is not list or len(samples) > raw["planned_sample_count"]:
        _reject()
    termination = raw["termination"]
    _fields(termination, ("reason", "elapsed_ms"))
    reason = termination["reason"]
    if type(reason) is not str or reason not in _REASONS:
        _reject()
    _integer(termination["elapsed_ms"], 0, 30000)
    summaries, identities = [], set()
    previous_finish = 0
    for index, sample in enumerate(samples, 1):
        _fields(sample, _SAMPLE)
        _integer(sample["sample_index"], index, index)
        start, finish = sample["elapsed_start_ms"], sample["elapsed_finish_ms"]
        _integer(start, 0, 30000)
        _integer(finish, start, 30000)
        if (index == 1 and start != 0) or (index > 1 and start < previous_finish + 2000):
            _reject()
        previous_finish = finish
        summary = _summary.parse_summary_canonical_json(_encode(sample["summary"]))
        if summary.query_id in identities:
            _reject()
        identities.add(summary.query_id)
        summaries.append(summary)
        for target in (summary.lab1, summary.lab2):
            if target.status == "FAILURE" and target.failure_category != "TRUSTED_RUNTIME_FAILED":
                if index != len(samples) or reason != "SESSION_INTEGRITY_FAILURE":
                    _reject()
    if termination["elapsed_ms"] < previous_finish:
        _reject()
    count, planned = len(samples), raw["planned_sample_count"]
    if reason == "COUNT_REACHED" and count != planned:
        _reject()
    if reason == "DURATION_LIMIT" and (count >= planned or termination["elapsed_ms"] != 30000):
        _reject()
    if reason == "PRECHECK_REJECTED" and (count or termination["elapsed_ms"] != 0):
        _reject()
    if reason == "INVALID_SAMPLE" and count >= planned:
        _reject()
    derived = _derive(samples)
    if with_facts:
        facts = raw["facts"]
        if type(facts) is not list or len(facts) > _MAX_FACTS:
            _reject()
        # Exact canonical bytes distinguish bool/int and close every nested
        # fact field, kind, reference, subject and value domain by recomputation.
        if _encode(facts) != _encode(derived):
            _reject()
    return summaries, derived


def _groups(target):
    groups = {}
    for record in target["records"]:
        groups.setdefault((record["instance_name"], record["vrid"]), []).append(record)
    return groups


def _fact(kind, first, last, target, before, after, key=None):
    return {"kind": kind, "from_sample": first, "to_sample": last, "target_ref": target,
            "subject": None if key is None else {"instance_name": key[0], "vrid": key[1]},
            "from_value": before, "to_value": after}


def _order(row):
    subject = row["subject"]
    key = (0, "", 0) if subject is None else (1, subject["instance_name"], subject["vrid"])
    return (row["to_sample"], row["from_sample"], _KINDS.index(row["kind"]),
            (*_TARGETS, None).index(row["target_ref"]), key)


def _derive(samples):
    rows = []
    for index, sample in enumerate(samples, 1):
        current = sample["summary"]
        for name, target_ref in zip(("lab1", "lab2"), _TARGETS):
            target = current[name]
            if target["status"] == "FAILURE":
                rows.append(_fact("OBSERVATION_GAP", index, index, target_ref,
                                  None, target["failure_category"]))
            if index == 1:
                continue
            before = samples[index - 2]["summary"][name]
            if before["status"] != target["status"]:
                rows.append(_fact("TARGET_RESULT_STATUS_CHANGED", index - 1, index,
                                  target_ref, before["status"], target["status"]))
            if before["status"] != "SUCCESS" or target["status"] != "SUCCESS":
                continue
            left, right = _groups(before), _groups(target)
            old_vrids = sorted({key[1] for key in left})
            new_vrids = sorted({key[1] for key in right})
            if old_vrids != new_vrids:
                rows.append(_fact("VRID_SET_CHANGED", index - 1, index,
                                  target_ref, old_vrids, new_vrids))
            for key in sorted(left.keys() | right.keys()):
                a, b = left.get(key, []), right.get(key, [])
                if len(a) != 1 or len(b) != 1:
                    rows.append(_fact("OBSERVATION_GAP", index - 1, index,
                                      target_ref, len(a), len(b), key))
                    continue
                for field, kind in _CHANGES:
                    if a[0][field] != b[0][field]:
                        rows.append(_fact(kind, index - 1, index, target_ref,
                                          a[0][field], b[0][field], key))
        if index > 1:
            rows.extend(_master_changes(samples[index - 2]["summary"], current, index))
        if len(rows) > _MAX_FACTS:
            _reject()
    return sorted(rows, key=_order)


def _master_changes(before, after, index):
    targets = (before["lab1"], before["lab2"], after["lab1"], after["lab2"])
    if any(target["status"] != "SUCCESS" for target in targets):
        return []
    groups = [_groups(target) for target in targets]
    common = set(groups[0]).intersection(*(set(group) for group in groups[1:]))
    rows = []
    for key in sorted(common):
        if any(len(group[key]) != 1 for group in groups):
            continue
        records = [group[key][0] for group in groups]
        if any(record["disabled"] or record["invalid"] for record in records):
            continue
        old, new = [record["role"] for record in records[:2]], [record["role"] for record in records[2:]]
        if sorted(old) != ["BACKUP", "MASTER"] or sorted(new) != ["BACKUP", "MASTER"]:
            continue
        if old != new:
            rows.append(_fact("MASTER_TARGET_CHANGED", index - 1, index, None,
                              _TARGETS[old.index("MASTER")], _TARGETS[new.index("MASTER")], key))
    return rows


def _build(raw, *, with_facts):
    summaries, facts = _validate(raw, with_facts=with_facts)
    complete = {**raw, "facts": facts}
    _encode(complete)
    value = object.__new__(DualLabVrrpTransition)
    for name in _TOP - {"samples", "termination", "facts"}:
        object.__setattr__(value, name, raw[name])
    object.__setattr__(value, "samples", tuple(
        _Sample(sample["sample_index"], sample["elapsed_start_ms"], sample["elapsed_finish_ms"], summary)
        for sample, summary in zip(raw["samples"], summaries)))
    object.__setattr__(value, "termination", _Termination(**raw["termination"]))
    object.__setattr__(value, "facts", tuple(_Fact(
        row["kind"], row["from_sample"], row["to_sample"], row["target_ref"],
        None if row["subject"] is None else _Subject(**row["subject"]),
        tuple(row["from_value"]) if type(row["from_value"]) is list else row["from_value"],
        tuple(row["to_value"]) if type(row["to_value"]) is list else row["to_value"])
        for row in facts))
    return value


def _encode(raw):
    encoded = _json.dumps(raw, allow_nan=False, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8", errors="strict")
    if not 1 <= len(encoded) <= _MAX_BYTES:
        _reject()
    return encoded


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _reject()
        result[key] = value
    return result


def _decode(raw):
    if type(raw) is not bytes or not 1 <= len(raw) <= _MAX_BYTES or raw.startswith(b"\xef\xbb\xbf"):
        _reject()
    parsed = _json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_unique,
                         parse_constant=lambda _: _reject())
    if _encode(parsed) != raw:
        _reject()
    return parsed


@_checked
def project_dual_lab_vrrp_transition(raw: bytes) -> DualLabVrrpTransition:
    """Derive facts from canonical outer fields excluding `facts`.

    Input embeds unchanged DL-03 summary objects in the specified samples;
    each is independently revalidated. No authority or live provenance is inferred.
    """
    return _build(_decode(raw), with_facts=False)


@_checked
def parse_transition_canonical_json(raw: bytes) -> DualLabVrrpTransition:
    """Validate the complete canonical timeline and recompute all nine fact kinds."""
    return _build(_decode(raw), with_facts=True)


__all__ = ("DualLabVrrpTransition", "DualLabTransitionError",
           "project_dual_lab_vrrp_transition", "parse_transition_canonical_json")
