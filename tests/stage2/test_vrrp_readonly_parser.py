"""Synthetic offline S2-RO-08 parser verification."""
import ast
import dataclasses
import hashlib
import inspect

import pytest

from test_vrrp_readonly_command_policy import (
    no_external_or_execution_boundary, request, altered_request,
)
from validation_framework import stage2_vrrp_readonly_parser as subject
from validation_framework import stage2_vrrp_readonly_command_policy as policy
from validation_framework.stage2_vrrp_readonly_contract import (
    Stage2VrrpObservationEvidence,
)

F = subject.Stage2VrrpParserFailure
VALID = b'0 RM name="vrrp-lan" vrid=88 priority=150 interval=1s version=3\n'
ROUTEROS_7_24 = (
    b'Flags: R - RUNNING; M - MASTER\n'
    b'0 RM ;;; synthetic VRRP comment\n'
    b'    name="vrrp-lan" mtu=1500 mac-address=00:00:5E:00:01:58 '
    b'arp=enabled arp-timeout=auto interface=bridge\n'
    b'    group-authority="" vrid=88 priority=150 interval=1s '
    b'preemption-mode=yes authentication=none on-backup=""\n'
    b'    on-master="" on-fail="" version=3 v3-protocol=ipv4 '
    b'v3-checksum-as-v2=no sync-connection-tracking=no\n'
    b'    connection-tracking-mode=passive-active\n'
)


def parse(raw=VALID):
    return subject.parse_stage2_vrrp_readonly_output(request(), raw)


def rejected(raw, category):
    with pytest.raises(subject.Stage2VrrpParserError) as caught:
        parse(raw)
    error = caught.value
    assert error.code is category
    assert error.args == (category.value,)
    assert error.__cause__ is None
    assert error.__context__ is None
    assert 'vrrp-lan' not in repr(error)


def test_valid_normalized_record_and_s2_ro_01_compatibility():
    result = parse()
    assert dataclasses.asdict(result.records[0]) == dict(
        instance_name='vrrp-lan', vrid=88, priority=150, interval_ms=1000,
        version=3, running=True, role='MASTER', disabled=False, invalid=False,
    )
    assert result.raw_output_sha256 == hashlib.sha256(VALID).hexdigest()
    assert result.raw_output_byte_count == len(VALID)
    evidence = Stage2VrrpObservationEvidence(
        schema_version='1.0', operation_id='mikrotik.vrrp_status',
        run_id=request().run_id, target_ref=request().target_ref,
        authorization_ref=request().authorization_ref,
        command_policy_version='policy.stage2.vrrp-readonly.v1',
        attempt_count=1, retry_count=0, duration_ms=1,
        raw_output_byte_count=result.raw_output_byte_count,
        raw_output_sha256=result.raw_output_sha256, records=result.records,
    )
    assert evidence.execution_authorized is result.execution_authorized is False
    assert b'priority=150' not in evidence.to_canonical_bytes()
    assert 'vrrp-lan' not in repr(result)
    assert not hasattr(result, '__dict__')
    for field in dataclasses.fields(result):
        with pytest.raises((AttributeError, TypeError)):
            setattr(result, field.name, None)
    with pytest.raises((AttributeError, TypeError)):
        result.records[0].vrid = 12


@pytest.mark.parametrize(('raw', 'category'), [
    (None, F.INVALID_OUTPUT_TYPE), ('text', F.INVALID_OUTPUT_TYPE),
    (bytearray(VALID), F.INVALID_OUTPUT_TYPE), (memoryview(VALID), F.INVALID_OUTPUT_TYPE),
    (b'', F.EMPTY_OUTPUT), (b' \n ', F.EMPTY_OUTPUT), (b'\xff', F.INVALID_UTF8),
    (b'\xef\xbb\xbf' + VALID, F.MALFORMED_OUTPUT),
    pytest.param(b'x' * 65537, F.OUTPUT_TOO_LARGE, id='output-overflow'),
    (VALID.replace(b' vrid=88', b''), F.MISSING_REQUIRED_FIELD),
    (VALID.replace(b' vrid=88', b' vrid=88 vrid=88'), F.DUPLICATE_FIELD),
    (VALID.replace(b'vrid=88', b'vrid=true'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'vrid=88', b'vrid=+88'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'vrid=88', b'vrid=088'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'vrid=88', b'vrid=0'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'priority=150', b'priority=256'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'version=3', b'version=4'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'interval=1s', b'interval=1'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'interval=1s', b'interval=256s'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'interval=1s', b'interval=1.5s'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b' RM ', b' RMB '), F.AMBIGUOUS_RECORD),
    (VALID.replace(b' RM ', b' RRM '), F.AMBIGUOUS_RECORD),
    (VALID.replace(b' RM ', b' Z '), F.MALFORMED_OUTPUT),
    (VALID.replace(b' version=3', b' version=3 state=master'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b' version=3', b' version=3 unknown=x'), F.UNSUPPORTED_VALUE),
    (VALID.replace(b'0 RM ', b'0RM '), F.MALFORMED_OUTPUT),
    (VALID + b'1 B name="partial"', F.MISSING_REQUIRED_FIELD),
    (VALID + VALID, F.AMBIGUOUS_RECORD),
    (VALID + VALID.replace(b'0 RM', b'1 B'), F.AMBIGUOUS_RECORD),
    (VALID.replace(b'\n', b'\r'), F.MALFORMED_OUTPUT),
    (VALID.replace(b' ', b'\t', 1), F.MALFORMED_OUTPUT),
    (VALID + b'garbage', F.MALFORMED_OUTPUT),
    (VALID.replace(b'vrrp-lan', b'bad\\name'), F.MALFORMED_OUTPUT),
    (VALID.replace(b'vrrp-lan', b'bad\x1bname'), F.MALFORMED_OUTPUT),
    (VALID.replace(b'vrrp-lan', b' bad '), F.UNSUPPORTED_VALUE),
])
def test_rejections(raw, category):
    rejected(raw, category)


def test_bytes_subclass_rejected():
    class Bytes(bytes):
        pass
    rejected(Bytes(VALID), F.INVALID_OUTPUT_TYPE)


def test_exact_byte_boundary_is_not_truncated():
    raw = VALID + b' ' * (65536 - len(VALID))
    result = parse(raw)
    assert result.raw_output_byte_count == 65536
    assert result.raw_output_sha256 == hashlib.sha256(raw).hexdigest()
    rejected(raw + b' ', F.OUTPUT_TOO_LARGE)
    rejected(VALID + b' ' * (65536 - len(VALID) - 1) + b'!', F.MALFORMED_OUTPUT)


@pytest.mark.parametrize('suffix', [b'', b'\n', b'\r\n', b'   \n\n'])
def test_whitespace_line_endings_and_order(suffix):
    raw = b' 0 RM version=3 interval=1000ms priority=150 name="vrrp-lan" vrid=88' + suffix
    assert parse(raw).records == parse().records


def test_repository_day35_shape_and_auxiliary_fields():
    raw = (subject._LEGEND + '\n 0 RM\n'
           '         name="vrrp-lan" mtu=1500 mac-address=00:00:5E:00:01:58 '
           'arp=enabled arp-timeout=auto interface=bridge\n'
           '         group-authority="" vrid=88 priority=150 interval=1s '
           'preemption-mode=yes authentication=none on-backup=""\n'
           '         on-master="" on-fail="" version=3 v3-protocol=ipv4 '
           'sync-connection-tracking=no\n'
           '         connection-tracking-mode=passive-active\n').encode()
    assert parse(raw).records == parse().records
    rejected(raw.replace(b'mtu=1500', b'mtu=1500 mtu=1500'), F.DUPLICATE_FIELD)


@pytest.mark.parametrize(('flags', 'role'), [
    ('RMB', None), ('RM', 'MASTER'), ('B', 'BACKUP'), ('F', 'FAILURE'),
    ('XI', 'UNKNOWN'), ('GgR', 'UNKNOWN'),
])
def test_flag_interpretation(flags, role):
    raw = VALID.replace(b'RM', flags.encode())
    if role is None:
        rejected(raw, F.AMBIGUOUS_RECORD)
    else:
        record = parse(raw).records[0]
        assert record.role == role
        assert record.running is ('R' in flags)
        assert record.disabled is ('X' in flags)
        assert record.invalid is ('I' in flags)


def test_multiple_records_limit_and_input_order():
    rows = [VALID.replace(b'0 RM', str(i).encode() + b' RM').replace(
        b'vrrp-lan', f'vrrp-{i}'.encode()) for i in range(33)]
    assert len(parse(b''.join(rows[:32])).records) == 32
    rejected(b''.join(rows), F.AMBIGUOUS_RECORD)
    result = parse(rows[2] + rows[1])
    assert [r.instance_name for r in result.records] == ['vrrp-2', 'vrrp-1']


def test_failure_mapping_and_internal_error_sanitization(monkeypatch):
    with pytest.raises(subject.Stage2VrrpParserError) as caught:
        subject.parse_stage2_vrrp_readonly_output(altered_request(operation_id='bad'), VALID)
    assert caught.value.code is F.INVALID_OPERATION
    with monkeypatch.context() as patch:
        patch.setattr(policy, '_POLICY_BINDINGS', ())
        rejected(VALID, F.COMMAND_POLICY_VIOLATION)
    def broken(_):
        raise RuntimeError('raw transport confidential')
    monkeypatch.setattr(subject, '_parse', broken)
    rejected(VALID, F.PARSER_INTERNAL_FAILURE)


def test_no_io_import_or_execution_surface():
    tree = ast.parse(inspect.getsource(subject))
    roots = {node.module.split('.')[0] for node in ast.walk(tree)
             if isinstance(node, ast.ImportFrom)}
    roots |= {alias.name.split('.')[0] for node in ast.walk(tree)
              if isinstance(node, ast.Import) for alias in node.names}
    assert roots <= {'dataclasses', 'enum', 'hashlib', 're', 'unicodedata', 'validation_framework'}
    calls = {node.func.id for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert calls.isdisjoint({'open', 'exec', 'eval', '__import__', 'compile'})
    assert tuple(inspect.signature(subject.parse_stage2_vrrp_readonly_output).parameters) == ('request', 'raw_output')

@pytest.mark.parametrize('raw', [
    VALID.replace(b'vrrp-lan', b'vrrp-\n lan'),
    VALID.replace(b'version=3', b'\n version="3\n "'),
    VALID + b' on-master="one\n two"',
])
def test_quoted_values_cannot_cross_physical_lines(raw):
    rejected(raw, F.MALFORMED_OUTPUT)


@pytest.mark.parametrize(('field', 'value'), [
    (b'vrid=88', b'vrid=255'), (b'vrid=88', b'vrid=1'),
    (b'priority=150', b'priority=0'), (b'priority=150', b'priority=255'),
    (b'interval=1s', b'interval=1ms'), (b'interval=1s', b'interval=255s'),
    (b'version=3', b'version=2'),
])
def test_numeric_valid_boundaries(field, value):
    assert len(parse(VALID.replace(field, value)).records) == 1


def test_exact_parser_dependency_boundary():
    tree = ast.parse(inspect.getsource(subject))
    dependencies = {node.module for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom)
                    and node.module.startswith('validation_framework')}
    assert dependencies == {
        'validation_framework.stage2_vrrp_readonly_contract',
        'validation_framework.stage2_vrrp_readonly_command_policy',
    }


@pytest.mark.parametrize(('legend', 'flags'), [
    ('Flags: X - DISABLED; I - INVALID; G - GRP-AUTHORITY, '
     'g - GRP-MEMBER; R - RUNNING; M - MASTER, B - BACKUP, F - FAILURE', 'RM'),
    ('Flags: R - RUNNING; M - MASTER', 'RM'),
    ('Flags: B - BACKUP', 'B'),
    ('Flags: R - RUNNING; B - BACKUP', 'RB'),
    ('Flags: F - FAILURE', 'F'),
    ('Flags: X - DISABLED; I - INVALID', 'XI'),
    ('Flags: G - GRP-AUTHORITY; g - GRP-MEMBER', 'Gg'),
    ('Flags: M - MASTER; R - RUNNING', 'RM'),
    ('Flags: X - DISABLED; I - INVALID; G - GRP-AUTHORITY; '
     'g - GRP-MEMBER; R - RUNNING; M - MASTER; B - BACKUP; F - FAILURE', 'RM'),
])
def test_legacy_and_bounded_subset_legends(legend, flags):
    raw = VALID.replace(b' RM ', b' ' + flags.encode() + b' ')
    assert parse(legend.encode() + b'\n' + raw).records == parse(raw).records


@pytest.mark.parametrize('legend', [
    'Flags:', 'Flags: ', 'Flags:R - RUNNING', 'Flags:  R - RUNNING',
    ' Flags: R - RUNNING', 'flags: R - RUNNING', 'Flags: R - RUNNING ',
    'Flags: Z - UNKNOWN', 'Flags: R - MASTER', 'Flags: g - GRP-AUTHORITY',
    'Flags: R - RUNNING; R - RUNNING',
    'Flags: R - RUNNING;M - MASTER',
    'Flags: R - RUNNING;  M - MASTER',
    'Flags: R - RUNNING, M - MASTER',
    'Flags: R - RUNNING;; M - MASTER',
    'Flags: R - RUNNING; ', 'Flags: R - RUNNING;',
    'Flags: R-RUNNING', 'Flags: RR - RUNNING',
])
def test_malformed_unknown_or_duplicate_legend_rejected(legend):
    rejected(legend.encode() + b'\n' + VALID, F.MALFORMED_OUTPUT)


def test_legend_remains_optional_unique_and_before_records():
    legend = b'Flags: R - RUNNING; M - MASTER\n'
    rejected(legend + legend + VALID, F.MALFORMED_OUTPUT)
    rejected(VALID + legend, F.MALFORMED_OUTPUT)
    rejected(legend, F.EMPTY_OUTPUT)


@pytest.mark.parametrize('comment', [
    b';;; synthetic VRRP comment', b';;;', b';;;   synthetic',
    b';;; inert " quote', b';;; MASTER BACKUP FAILURE disabled priority 0',
])
def test_comment_only_record_header_is_inert(comment):
    raw = VALID.replace(b'0 RM ', b'0 RM ' + comment + b'\n    ')
    assert parse(raw).records == parse().records


@pytest.mark.parametrize('comment', [
    b';; synthetic', b';;;; synthetic', b';;;synthetic', b'! synthetic',
    b';;; synthetic name=x vrid=1', b';;; name="hidden"',
    b';;; unknown=x', b';;; synthetic=metadata',
])
def test_malformed_or_mixed_comment_header_rejected(comment):
    raw = VALID.replace(b'0 RM ', b'0 RM ' + comment + b'\n    ')
    rejected(raw, F.MALFORMED_OUTPUT)


@pytest.mark.parametrize('raw', [
    b';;; synthetic\n' + VALID,
    VALID + b'    ;;; synthetic\n',
    VALID.replace(b' vrid=88', b'\n    ;;; synthetic\n    vrid=88'),
    VALID.rstrip() + b' ;;; synthetic\n',
])
def test_comment_form_rejected_outside_record_header(raw):
    rejected(raw, F.MALFORMED_OUTPUT)


@pytest.mark.parametrize('text', [
    b'\t', b'\r', b'\x1b[0m', b'\x00', b'\xef\xbb\xbf',
    '\u2028'.encode(), '\u2029'.encode(),
])
def test_comment_does_not_bypass_outer_text_policy(text):
    raw = ROUTEROS_7_24.replace(b'synthetic VRRP comment', b'before' + text + b'after')
    rejected(raw, F.MALFORMED_OUTPUT)


@pytest.mark.parametrize(('field', 'value'), [
    (b'name', b'"vrrp-lan"'), (b'vrid', b'88'), (b'priority', b'150'),
    (b'interval', b'1s'), (b'version', b'3'),
])
def test_comment_does_not_supply_missing_required_fields(field, value):
    raw = ROUTEROS_7_24.replace(field + b'=' + value + b' ', b'')
    rejected(raw, F.MISSING_REQUIRED_FIELD)


@pytest.mark.parametrize(('flags', 'category'), [
    (b'MB', F.AMBIGUOUS_RECORD), (b'MF', F.AMBIGUOUS_RECORD),
    (b'BF', F.AMBIGUOUS_RECORD), (b'MBF', F.AMBIGUOUS_RECORD),
    (b'RRM', F.AMBIGUOUS_RECORD), (b'Z', F.MALFORMED_OUTPUT),
])
def test_comment_does_not_bypass_flag_validation(flags, category):
    rejected(ROUTEROS_7_24.replace(b'0 RM ', b'0 ' + flags + b' '), category)


def test_checksum_auxiliary_field_is_bounded_and_duplicates_reject():
    raw = VALID.replace(b'\n', b' v3-checksum-as-v2=no\n')
    assert parse(raw).records == parse().records
    rejected(raw.replace(b'=no', b'=no v3-checksum-as-v2=no'), F.DUPLICATE_FIELD)
    rejected(ROUTEROS_7_24 + b'    v3-checksum-as-v2=no\n', F.DUPLICATE_FIELD)


@pytest.mark.parametrize('field', [
    b'unknown=x', b'password=""', b'remote-address=192.0.2.1',
    b'connection-tracking-port=1', b'group-master=""',
])
def test_unobserved_fields_remain_unsupported(field):
    rejected(ROUTEROS_7_24 + b'    ' + field + b'\n', F.UNSUPPORTED_VALUE)


def test_routeros_7_24_structure_and_evidence_exclude_inert_metadata(capsys, caplog):
    result = parse(ROUTEROS_7_24)
    assert dataclasses.asdict(result.records[0]) == dict(
        instance_name='vrrp-lan', vrid=88, priority=150, interval_ms=1000,
        version=3, running=True, role='MASTER', disabled=False, invalid=False,
    )
    assert {field.name for field in dataclasses.fields(result)} == {
        'records', 'raw_output_byte_count', 'raw_output_sha256',
    }
    assert result.raw_output_sha256 == hashlib.sha256(ROUTEROS_7_24).hexdigest()
    assert result.raw_output_byte_count == len(ROUTEROS_7_24)
    evidence = Stage2VrrpObservationEvidence(
        schema_version='1.0', operation_id='mikrotik.vrrp_status',
        run_id=request().run_id, target_ref=request().target_ref,
        authorization_ref=request().authorization_ref,
        command_policy_version='policy.stage2.vrrp-readonly.v1',
        attempt_count=1, retry_count=0, duration_ms=1,
        raw_output_byte_count=result.raw_output_byte_count,
        raw_output_sha256=result.raw_output_sha256, records=result.records,
    )
    for excluded in (b'synthetic VRRP comment', b';;;', b'v3-checksum-as-v2', b'mtu=1500'):
        assert excluded not in evidence.to_canonical_bytes()
        assert excluded.decode() not in repr(dataclasses.asdict(result))
        assert excluded.decode() not in repr(result)
    assert evidence.execution_authorized is result.execution_authorized is False
    changed_comment = parse(ROUTEROS_7_24.replace(b'synthetic VRRP comment', b'other'))
    assert changed_comment.records == result.records
    assert changed_comment.raw_output_sha256 != result.raw_output_sha256
    assert capsys.readouterr() == ('', '')
    assert caplog.records == []
