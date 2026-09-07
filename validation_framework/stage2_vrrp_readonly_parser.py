"""Offline, bounded decoding of the one Stage-2 VRRP detail format.

No acquisition or execution is performed. Output is untrusted synthetic or
future transport data; successful parsing grants no execution authority.
"""

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
from hashlib import sha256 as _sha256
import re as _re

from validation_framework.stage2_vrrp_readonly_command_policy import (
    resolve_stage2_vrrp_readonly_command as _resolve,
    Stage2VrrpCommandPolicyError as _PolicyError,
    Stage2VrrpCommandPolicyFailure as _PolicyFailure,
)
from validation_framework.stage2_vrrp_readonly_contract import (
    NormalizedVrrpRecord as _Record,
)

_REQUIRED = frozenset({'name', 'vrid', 'priority', 'interval', 'version'})
_AUXILIARY = frozenset({
    'mtu', 'mac-address', 'arp', 'arp-timeout', 'interface',
    'group-authority', 'preemption-mode', 'authentication', 'on-backup',
    'on-master', 'on-fail', 'v3-protocol', 'sync-connection-tracking',
    'connection-tracking-mode',
})
_LEGEND = ('Flags: X - DISABLED; I - INVALID; G - GRP-AUTHORITY, '
           'g - GRP-MEMBER; R - RUNNING; M - MASTER, B - BACKUP, F - FAILURE')
_START = _re.compile(r'([0-9]+) +(?:([XIGgRMBF]+)(?: +|$))?(.*)')
_FIELD = _re.compile(r'([a-z][a-z0-9-]*)=("[^"\\\r\n]*"|[^ "\\\r\n]+)(?: +|$)')
_INTEGER = _re.compile(r'(?:0|[1-9][0-9]{0,5})')
_INTERVAL = _re.compile(r'([1-9][0-9]{0,5})(ms|s)')


class Stage2VrrpParserFailure(_Enum):
    """Sanitized categories; rejected input is never attached."""

    INVALID_OPERATION = 'INVALID_OPERATION'
    COMMAND_POLICY_VIOLATION = 'COMMAND_POLICY_VIOLATION'
    INVALID_OUTPUT_TYPE = 'INVALID_OUTPUT_TYPE'
    OUTPUT_TOO_LARGE = 'OUTPUT_TOO_LARGE'
    INVALID_UTF8 = 'INVALID_UTF8'
    EMPTY_OUTPUT = 'EMPTY_OUTPUT'
    MALFORMED_OUTPUT = 'MALFORMED_OUTPUT'
    MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
    DUPLICATE_FIELD = 'DUPLICATE_FIELD'
    UNSUPPORTED_VALUE = 'UNSUPPORTED_VALUE'
    AMBIGUOUS_RECORD = 'AMBIGUOUS_RECORD'
    PARSER_INTERNAL_FAILURE = 'PARSER_INTERNAL_FAILURE'


class Stage2VrrpParserError(ValueError):
    """Public error with bounded category only."""

    def __init__(self, code):
        if type(code) is not Stage2VrrpParserFailure:
            raise TypeError('parser error requires a bounded category')
        self.code = code
        super().__init__(code.value)


@_dataclass(frozen=True, slots=True, repr=False)
class Stage2VrrpParsedOutput:
    """Immutable normalized facts and correlation metadata, without raw output."""

    records: tuple[_Record, ...]
    raw_output_byte_count: int
    raw_output_sha256: str

    def __post_init__(self):
        if (type(self.records) is not tuple or not 1 <= len(self.records) <= 32
                or any(type(record) is not _Record for record in self.records)
                or type(self.raw_output_byte_count) is not int
                or not 1 <= self.raw_output_byte_count <= 65536
                or type(self.raw_output_sha256) is not str
                or _re.fullmatch(r'[0-9a-f]{64}', self.raw_output_sha256) is None):
            raise TypeError('invalid normalized parser result')
        for record in self.records:
            _Record.__post_init__(record)

    @property
    def execution_authorized(self):
        return False

    def __repr__(self):
        return 'Stage2VrrpParsedOutput(<normalized-no-raw-output>)'

    __str__ = __repr__


def _fail(code):
    raise Stage2VrrpParserError(code)


def _number(value):
    if _INTEGER.fullmatch(value) is None:
        _fail(Stage2VrrpParserFailure.UNSUPPORTED_VALUE)
    return int(value)


def _record(flags, body):
    failure = Stage2VrrpParserFailure
    if len(set(flags)) != len(flags) or sum(c in flags for c in 'MBF') > 1:
        _fail(failure.AMBIGUOUS_RECORD)
    fields = {}
    position = 0
    while position < len(body):
        match = _FIELD.match(body, position)
        if match is None:
            _fail(failure.MALFORMED_OUTPUT)
        key, value = match.group(1, 2)
        if key in fields:
            _fail(failure.DUPLICATE_FIELD)
        if key not in _REQUIRED | _AUXILIARY:
            _fail(failure.UNSUPPORTED_VALUE)
        fields[key] = value[1:-1] if value.startswith('"') else value
        position = match.end()
    if not _REQUIRED <= fields.keys():
        _fail(failure.MISSING_REQUIRED_FIELD)
    interval = _INTERVAL.fullmatch(fields['interval'])
    if interval is None:
        _fail(failure.UNSUPPORTED_VALUE)
    interval_ms = int(interval[1]) * (1000 if interval[2] == 's' else 1)
    role = next((role for flag, role in (
        ('M', 'MASTER'), ('B', 'BACKUP'), ('F', 'FAILURE')
    ) if flag in flags), 'UNKNOWN')
    invalid = False
    try:
        record = _Record(
            instance_name=fields['name'], vrid=_number(fields['vrid']),
            priority=_number(fields['priority']), interval_ms=interval_ms,
            version=_number(fields['version']), running='R' in flags,
            role=role, disabled='X' in flags, invalid='I' in flags,
        )
    except Stage2VrrpParserError:
        raise
    except ValueError:
        invalid = True
    if invalid:
        _fail(failure.UNSUPPORTED_VALUE)
    return record


def _parse(text):
    failure = Stage2VrrpParserFailure
    # Only printable text and LF/CRLF are accepted; no terminal escapes,
    # tabs, bare CR, Unicode line separators, or invisible format characters.
    import unicodedata
    text = text.replace('\r\n', '\n')
    if any(c != '\n' and unicodedata.category(c).startswith('C') for c in text):
        _fail(failure.MALFORMED_OUTPUT)
    if '\u2028' in text or '\u2029' in text:
        _fail(failure.MALFORMED_OUTPUT)
    groups = []
    seen_indexes = set()
    legend_seen = False
    for line in text.split('\n'):
        stripped = line.strip(' ')
        if not stripped:
            continue
        if stripped == _LEGEND:
            if groups or legend_seen:
                _fail(failure.MALFORMED_OUTPUT)
            legend_seen = True
            continue
        if stripped.count(chr(34)) % 2:
            _fail(failure.MALFORMED_OUTPUT)
        match = _START.fullmatch(stripped)
        if match:
            if len(match[1]) > 5:
                _fail(failure.AMBIGUOUS_RECORD)
            index = int(match[1])
            if index in seen_indexes or len(groups) == 32:
                _fail(failure.AMBIGUOUS_RECORD)
            seen_indexes.add(index)
            groups.append([match[2] or '', match[3]])
        elif groups and line.startswith(' ') and not stripped[0].isdigit():
            groups[-1][1] += ' ' + stripped
        else:
            _fail(failure.MALFORMED_OUTPUT)
    if not groups:
        _fail(failure.EMPTY_OUTPUT)
    records = tuple(_record(flags, body.strip(' ')) for flags, body in groups)
    if len({record.instance_name for record in records}) != len(records):
        _fail(failure.AMBIGUOUS_RECORD)
    return records


def parse_stage2_vrrp_readonly_output(request, raw_output):
    """Validate the exact operation, then parse complete built-in bytes only.

    The caller cannot supply a command. Metadata/records can later populate
    S2-RO-01 evidence; request binding and duration remain runtime duties.
    """
    failure = Stage2VrrpParserFailure
    error = None
    result = None
    try:
        _resolve(request)
        if type(raw_output) is not bytes:
            _fail(failure.INVALID_OUTPUT_TYPE)
        if len(raw_output) > 65536:
            _fail(failure.OUTPUT_TOO_LARGE)
        if not raw_output:
            _fail(failure.EMPTY_OUTPUT)
        text = raw_output.decode('utf-8', errors='strict')
        records = _parse(text)
        result = Stage2VrrpParsedOutput(records, len(raw_output), _sha256(raw_output).hexdigest())
    except _PolicyError as rejected:
        error = (failure.COMMAND_POLICY_VIOLATION
                 if rejected.code is _PolicyFailure.INVALID_POLICY else failure.INVALID_OPERATION)
    except UnicodeDecodeError:
        error = failure.INVALID_UTF8
    except Stage2VrrpParserError as rejected:
        error = rejected.code
    except Exception:
        error = failure.PARSER_INTERNAL_FAILURE
    # Raise outside handlers: no raw-bearing exception cause/context survives.
    if error is not None:
        raise Stage2VrrpParserError(error) from None
    return result


__all__ = (
    'Stage2VrrpParserFailure', 'Stage2VrrpParserError', 'Stage2VrrpParsedOutput',
    'parse_stage2_vrrp_readonly_output',
)
