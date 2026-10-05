"""DL-03 inert facts-only projection; data validity grants no execution authority.

The aggregate boundary is owned by DL-01. Summary parsing independently checks
the projected schema and recomputes every observation from its target records.
"""

from dataclasses import dataclass as _dataclass, fields as _members
from functools import wraps as _wraps
import json as _json

from validation_framework import dual_lab_vrrp_query_contract as _upstream
from validation_framework import stage2_vrrp_readonly_contract as _stage2


_SCHEMA = "dual-lab-vrrp-query-summary.v1"
_IDENTITY = ("schema_version", "query_id", "operation_id", "execution_order")
_TOP = frozenset((*_IDENTITY, "lab1", "lab2", "cross_target_observations"))
_COMPARE = ("role", "priority", "interval_ms", "version", "running", "disabled", "invalid")
_SORT = ("instance_name", "vrid", *_COMPARE)
_LAB1 = "target.mikrotik.lab01"
_LAB2 = "target.mikrotik.lab02"
_MAX_BYTES = 262_144
_MAX_OBSERVATIONS = 356


class DualLabSummaryError(ValueError):
    """Fixed public rejection without rejected data or child exceptions."""

    def __init__(self):
        super().__init__("invalid Dual-Lab summary")


def _reject():
    try:
        raise DualLabSummaryError() from None
    except DualLabSummaryError as error:
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
        return "<inert-dual-lab-summary>"

    __str__ = __repr__


@_dataclass(frozen=True, slots=True, repr=False)
class _Record(_Inert):
    instance_name: str
    role: str
    vrid: int
    priority: int
    interval_ms: int
    version: int
    running: bool
    disabled: bool
    invalid: bool


@_dataclass(frozen=True, slots=True, repr=False)
class _Success(_Inert):
    status: str
    target_ref: str
    records: tuple


@_dataclass(frozen=True, slots=True, repr=False)
class _Failure(_Inert):
    status: str
    target_ref: str
    failure_category: str


@_dataclass(frozen=True, slots=True, repr=False)
class _Key(_Inert):
    instance_name: str
    vrid: int


@_dataclass(frozen=True, slots=True, repr=False)
class _FieldKey(_Inert):
    instance_name: str
    vrid: int
    field: str


@_dataclass(frozen=True, slots=True, repr=False)
class _Observation(_Inert):
    kind: str
    subject: _Key | _FieldKey | int | None
    lab1_value: str | int | bool | tuple
    lab2_value: str | int | bool | tuple


@_dataclass(frozen=True, slots=True, repr=False, init=False)
class DualLabVrrpSummary(_Inert):
    """Factory-created immutable DTO; serialization revalidates nested data."""

    schema_version: str
    query_id: str
    operation_id: str
    execution_order: str
    lab1: _Success | _Failure
    lab2: _Success | _Failure
    cross_target_observations: tuple

    def __init__(self, *args, **kwargs):
        _reject()

    @property
    def execution_authorized(self):
        return False

    @_checked
    def to_dict(self) -> dict[str, object]:
        if type(self) is not DualLabVrrpSummary:
            _reject()
        raw = _plain(self)
        _validate(raw)
        _encode(raw)
        return raw

    @_checked
    def to_canonical_bytes(self) -> bytes:
        return _encode(DualLabVrrpSummary.to_dict(self))


_VALUE_TYPES = (DualLabVrrpSummary, _Success, _Failure, _Record, _Key, _FieldKey, _Observation)


def _plain(value):
    """Export only exact inert values, never arbitrary mappings or methods."""
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [_plain(item) for item in value]
    if type(value) in _VALUE_TYPES:
        return {field.name: _plain(getattr(value, field.name)) for field in _members(value)}
    _reject()


def _exact_fields(raw, expected):
    if type(raw) is not dict or raw.keys() != set(expected):
        _reject()


def _sort_key(record):
    return tuple(record[field] for field in _SORT)


def _validate_target(raw, target):
    if type(raw) is not dict or type(raw.get("status")) is not str:
        _reject()
    if type(raw.get("target_ref")) is not str or raw["target_ref"] != target:
        _reject()
    if raw["status"] == "FAILURE":
        # The projected failure is exactly the existing inert DL-01 variant.
        _upstream.parse_target_result(raw)
        return
    if raw["status"] != "SUCCESS":
        _reject()
    _exact_fields(raw, ("status", "target_ref", "records"))
    records = raw["records"]
    if type(records) is not list or len(records) > _stage2.MAX_VRRP_RECORDS:
        _reject()
    for record in records:
        _exact_fields(record, _SORT)
        _stage2.NormalizedVrrpRecord(**record)
    if records != sorted(records, key=_sort_key):
        _reject()


def _row(kind, left, right, subject=None):
    return {"kind": kind, "subject": subject, "lab1_value": left, "lab2_value": right}


def _equality(prefix, left, right, subject=None):
    return _row(prefix + ("_EQUAL" if left == right else "_DIFFERENT"), left, right, subject)


def _groups(records):
    groups = {}
    for record in records:
        key = (record["instance_name"], record["vrid"])
        groups.setdefault(key, []).append(record)
    return groups


def _subject(key):
    return {"instance_name": key[0], "vrid": key[1]}


def _derive(lab1, lab2):
    """Exact row order; duplicate keys carry counts and never imply pairing."""
    available1, available2 = lab1["status"] == "SUCCESS", lab2["status"] == "SUCCESS"
    rows = [_row("RESULT_AVAILABILITY", available1, available2)]
    if not (available1 and available2):
        return rows
    left, right = lab1["records"], lab2["records"]
    vrids1, vrids2 = ({r["vrid"] for r in records} for records in (left, right))
    rows.append(_equality("VRID_SET", sorted(vrids1), sorted(vrids2)))
    rows.extend(_row("VRID_ONLY_LAB1", True, False, v) for v in sorted(vrids1 - vrids2))
    rows.extend(_row("VRID_ONLY_LAB2", False, True, v) for v in sorted(vrids2 - vrids1))
    names1, names2 = (sorted({r["instance_name"] for r in records}) for records in (left, right))
    rows.append(_equality("INSTANCE_NAME_SET", names1, names2))
    rows.append(_equality("RECORD_COUNT", len(left), len(right)))
    groups1, groups2 = _groups(left), _groups(right)
    keys1, keys2 = set(groups1), set(groups2)
    rows.extend(_row("RECORD_ONLY_LAB1", len(groups1[k]), 0, _subject(k))
                for k in sorted(keys1 - keys2))
    rows.extend(_row("RECORD_ONLY_LAB2", 0, len(groups2[k]), _subject(k))
                for k in sorted(keys2 - keys1))
    common = sorted(keys1 & keys2)
    for key in common:
        a, b = len(groups1[key]), len(groups2[key])
        if a > 1 or b > 1:
            rows.append(_row("MATCH_KEY_MULTIPLICITY", a, b, _subject(key)))
    for key in common:
        if len(groups1[key]) == len(groups2[key]) == 1:
            for field in _COMPARE:
                rows.append(_equality("FIELD", groups1[key][0][field], groups2[key][0][field],
                                      {**_subject(key), "field": field}))
    return rows


def _validate(raw):
    _exact_fields(raw, _TOP)
    if type(raw["schema_version"]) is not str or raw["schema_version"] != _SCHEMA:
        _reject()
    # Query identity retains the existing DL-01 grammar and fixed operation/order.
    identity = {name: raw[name] for name in _IDENTITY}
    identity["schema_version"] = "dual-lab-vrrp-query.v1"
    _upstream.parse_query(identity)
    _validate_target(raw["lab1"], _LAB1)
    _validate_target(raw["lab2"], _LAB2)
    rows = raw["cross_target_observations"]
    if type(rows) is not list or len(rows) > _MAX_OBSERVATIONS:
        _reject()
    # Byte equality also rejects Python's True == 1 and False == 0 aliases.
    # The recomputed rows close all kind/subject/value domains and field sets.
    if _encode(rows) != _encode(_derive(raw["lab1"], raw["lab2"])):
        _reject()


def _freeze_target(raw):
    if raw["status"] == "FAILURE":
        return _Failure(**raw)
    return _Success(raw["status"], raw["target_ref"], tuple(_Record(**r) for r in raw["records"]))


def _freeze_row(raw):
    subject = raw["subject"]
    if type(subject) is dict:
        subject = _FieldKey(**subject) if "field" in subject else _Key(**subject)
    values = [tuple(raw[name]) if type(raw[name]) is list else raw[name]
              for name in ("lab1_value", "lab2_value")]
    return _Observation(raw["kind"], subject, *values)


def _build(raw):
    _validate(raw)
    _encode(raw)
    value = object.__new__(DualLabVrrpSummary)
    for name in _IDENTITY:
        object.__setattr__(value, name, raw[name])
    object.__setattr__(value, "lab1", _freeze_target(raw["lab1"]))
    object.__setattr__(value, "lab2", _freeze_target(raw["lab2"]))
    object.__setattr__(value, "cross_target_observations",
                       tuple(_freeze_row(row) for row in raw["cross_target_observations"]))
    return value


def _encode(raw):
    encoded = _json.dumps(raw, allow_nan=False, ensure_ascii=False,
                          sort_keys=True, separators=(",", ":")).encode("utf-8", errors="strict")
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


@_checked
def project_dual_lab_vrrp_summary(raw: bytes) -> DualLabVrrpSummary:
    """Project only upstream-validated canonical aggregate bytes, without I/O."""
    aggregate = _upstream.parse_aggregate_canonical_json(raw).to_dict()
    projected = {name: aggregate[name] for name in _IDENTITY}
    projected["schema_version"] = _SCHEMA
    for name in ("lab1", "lab2"):
        target = aggregate[name]
        if target["status"] == "FAILURE":
            projected[name] = target
        else:
            projected[name] = {"status": target["status"], "target_ref": target["target_ref"],
                               "records": sorted(target["evidence"]["records"], key=_sort_key)}
    projected["cross_target_observations"] = _derive(projected["lab1"], projected["lab2"])
    return _build(projected)


@_checked
def parse_summary_canonical_json(raw: bytes) -> DualLabVrrpSummary:
    """Validate exact summary bytes and all derived facts; never repair input."""
    if type(raw) is not bytes or not 1 <= len(raw) <= _MAX_BYTES or raw.startswith(b"\xef\xbb\xbf"):
        _reject()
    parsed = _json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_unique,
                         parse_constant=lambda _: _reject())
    if _encode(parsed) != raw:
        _reject()
    return _build(parsed)


__all__ = ("DualLabVrrpSummary", "DualLabSummaryError", "project_dual_lab_vrrp_summary",
           "parse_summary_canonical_json")
