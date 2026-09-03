import base64
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, replace
import hashlib
import inspect
import json
import os
import pickle

import pytest

from validation_framework import stage2_live_authorization_owner_trust_root as module
from validation_framework.stage2_live_authorization_owner_trust_root import (
    OWNER_TRUST_ROOT_MAX_BYTES,
    OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES,
    OWNER_TRUST_ROOT_SCHEMA_VERSION,
    OwnerTrustRootConfiguration,
    OwnerTrustRootError,
    OwnerTrustRootFailure,
    acquire_owner_trust_root_configuration,
)


TRUST_ROOT_PATH = r"c:\owner-controlled\stage2\owner-trust-root.json"
APPROVAL_SOURCE_PATH = r"c:\owner-controlled\stage2\approvals"
VOLUME_SERIAL = 0x1234
FILE_ID = bytes.fromhex("00112233445566778899aabbccddeeff")
FILE_IDENTITY = (
    "win32-fileid-v1:0000000000001234:00112233445566778899aabbccddeeff"
)
APPROVAL_DIRECTORY_IDENTITY = (
    "win32-fileid-v1:0000000000005678:ffeeddccbbaa99887766554433221100"
)
PUBLIC_KEY = bytes(range(32))
PUBLIC_KEY_BASE64 = base64.b64encode(PUBLIC_KEY).decode("ascii")


def _record(**changes):
    result = {
        "schema_version": "1.0",
        "ed25519_public_key_base64": PUBLIC_KEY_BASE64,
        "issuer_ref": "issuer.stage2.owner.synthetic",
        "lab_only_attestation_ref": "attestation.stage2.lab-only.synthetic",
        "approval_source_id": "approval-source.stage2.owner.synthetic",
        "approval_source_absolute_path": APPROVAL_SOURCE_PATH,
        "approval_source_directory_identity": APPROVAL_DIRECTORY_IDENTITY,
    }
    result.update(changes)
    return result


def _canonical(record):
    return json.dumps(
        record,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


class FakeNative:
    def __init__(
        self,
        payload,
        *,
        file_type=module._FILE_TYPE_DISK,
        attributes=0,
        volume_serial=VOLUME_SERIAL,
        file_id=FILE_ID,
        fail_at=None,
        invalid_read_result=None,
    ):
        self.payload = payload
        self.file_type_value = file_type
        self.attributes = attributes
        self.volume_serial = volume_serial
        self.file_id = file_id
        self.fail_at = fail_at
        self.invalid_read_result = invalid_read_result
        self.handle = object()
        self.position = 0
        self.calls = []

    def _maybe_fail(self, name):
        if self.fail_at == name:
            raise OSError("synthetic native failure")

    def open_read_only(self, path):
        self.calls.append(("open", path))
        self._maybe_fail("open")
        return self.handle

    def file_type(self, handle):
        self.calls.append(("file_type", handle))
        self._maybe_fail("file_type")
        return self.file_type_value

    def attribute_flags(self, handle):
        self.calls.append(("attributes", handle))
        self._maybe_fail("attributes")
        return self.attributes

    def file_identity_parts(self, handle):
        self.calls.append(("identity", handle))
        self._maybe_fail("identity")
        return self.volume_serial, self.file_id

    def read(self, handle, maximum):
        self.calls.append(("read", handle, maximum))
        self._maybe_fail("read")
        if self.invalid_read_result is not None:
            return self.invalid_read_result
        chunk = self.payload[self.position : self.position + maximum]
        self.position += len(chunk)
        return chunk

    def close(self, handle):
        self.calls.append(("close", handle))
        self._maybe_fail("close")


def _acquire(monkeypatch, payload=None, native=None, **expected_changes):
    payload = _canonical(_record()) if payload is None else payload
    native = FakeNative(payload) if native is None else native
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    expected = {
        "expected_path": TRUST_ROOT_PATH,
        "expected_file_identity": FILE_IDENTITY,
        "expected_file_sha256": hashlib.sha256(payload).hexdigest(),
    }
    expected.update(expected_changes)
    return acquire_owner_trust_root_configuration(**expected), native


def _assert_payload_rejected(monkeypatch, payload):
    native = FakeNative(payload)
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_CONTENT_INVALID
    assert [call[0] for call in native.calls].count("close") == 1


def test_policy_constants_and_exact_public_surface():
    assert OWNER_TRUST_ROOT_SCHEMA_VERSION == "1.0"
    assert OWNER_TRUST_ROOT_MAX_BYTES == 4_096
    assert OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES == 32
    assert module.__all__ == (
        "OWNER_TRUST_ROOT_MAX_BYTES",
        "OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES",
        "OWNER_TRUST_ROOT_SCHEMA_VERSION",
        "OwnerTrustRootConfiguration",
        "OwnerTrustRootError",
        "OwnerTrustRootFailure",
        "acquire_owner_trust_root_configuration",
    )
    assert module._TRUST_ROOT_FIELDS == (
        "schema_version",
        "ed25519_public_key_base64",
        "issuer_ref",
        "lab_only_attestation_ref",
        "approval_source_id",
        "approval_source_absolute_path",
        "approval_source_directory_identity",
    )


def test_valid_acquisition_uses_one_handle_and_returns_exact_configuration(monkeypatch):
    configuration, native = _acquire(monkeypatch)

    assert type(configuration) is OwnerTrustRootConfiguration
    assert configuration.schema_version == "1.0"
    assert configuration.ed25519_public_key == PUBLIC_KEY
    assert configuration.issuer_ref == "issuer.stage2.owner.synthetic"
    assert configuration.lab_only_attestation_ref == (
        "attestation.stage2.lab-only.synthetic"
    )
    assert configuration.approval_source_id == (
        "approval-source.stage2.owner.synthetic"
    )
    assert configuration.approval_source_absolute_path == APPROVAL_SOURCE_PATH
    assert configuration.approval_source_directory_identity == (
        APPROVAL_DIRECTORY_IDENTITY
    )
    assert configuration.trust_root_source_file_identity == FILE_IDENTITY
    expected_sha = hashlib.sha256(_canonical(_record())).hexdigest()
    assert configuration.trust_root_source_file_sha256 == expected_sha
    assert [call[0] for call in native.calls] == [
        "open",
        "file_type",
        "attributes",
        "identity",
        "read",
        "read",
        "close",
    ]
    assert [call[0] for call in native.calls].count("open") == 1
    assert [call[0] for call in native.calls].count("close") == 1
    assert all(
        call[1] is native.handle
        for call in native.calls
        if call[0] not in {"open"}
    )


def test_public_key_fingerprint_is_exact_audit_metadata(monkeypatch):
    configuration, _ = _acquire(monkeypatch)
    expected = "SHA256:" + base64.b64encode(
        hashlib.sha256(PUBLIC_KEY).digest()
    ).decode("ascii").rstrip("=")
    assert configuration.public_key_sha256_fingerprint == expected
    assert "public_key_sha256_fingerprint" not in module._TRUST_ROOT_FIELDS


def test_direct_configuration_construction_and_ordinary_new_are_blocked():
    values = (
        "1.0",
        PUBLIC_KEY,
        "issuer.stage2.owner.synthetic",
        "attestation.stage2.lab-only.synthetic",
        "approval-source.stage2.owner.synthetic",
        APPROVAL_SOURCE_PATH,
        APPROVAL_DIRECTORY_IDENTITY,
        "SHA256:synthetic",
        FILE_IDENTITY,
        "a" * 64,
    )
    with pytest.raises(TypeError):
        OwnerTrustRootConfiguration(*values)
    with pytest.raises(TypeError):
        OwnerTrustRootConfiguration(schema_version="1.0")
    with pytest.raises(TypeError):
        OwnerTrustRootConfiguration.__new__(OwnerTrustRootConfiguration)


def test_no_visible_configuration_factory_is_present():
    for name in (
        "create",
        "_create",
        "issue",
        "from_values",
        "from_verified",
        "unsafe_create",
    ):
        assert name not in vars(OwnerTrustRootConfiguration)
        assert not hasattr(module, name)


def test_configuration_subclassing_is_blocked():
    with pytest.raises(TypeError):

        class ForgedTrustRoot(OwnerTrustRootConfiguration):
            pass


def test_copy_deepcopy_pickle_and_replace_are_blocked(monkeypatch):
    configuration, _ = _acquire(monkeypatch)
    for operation in (copy, deepcopy, pickle.dumps):
        with pytest.raises(TypeError):
            operation(configuration)
    with pytest.raises(TypeError):
        replace(configuration, issuer_ref="issuer.other.owner")


def test_configuration_is_immutable_and_repr_is_bounded(monkeypatch):
    configuration, _ = _acquire(monkeypatch)
    with pytest.raises(FrozenInstanceError):
        configuration.issuer_ref = "issuer.other.owner"
    rendered = repr(configuration) + str(configuration)
    assert rendered == (
        "OwnerTrustRootConfiguration(<acquisition-issued>)" * 2
    )
    for sensitive in (
        PUBLIC_KEY_BASE64,
        APPROVAL_SOURCE_PATH,
        FILE_IDENTITY,
        configuration.public_key_sha256_fingerprint,
    ):
        assert sensitive not in rendered
    assert not hasattr(configuration, "handle")
    assert not hasattr(configuration, "raw_file")
    assert not hasattr(configuration, "private_key")


def test_lookalike_is_not_the_acquisition_issued_exact_type(monkeypatch):
    configuration, _ = _acquire(monkeypatch)

    class Lookalike:
        pass

    lookalike = Lookalike()
    for name in OwnerTrustRootConfiguration.__slots__:
        setattr(lookalike, name, getattr(configuration, name))
    assert type(lookalike) is not OwnerTrustRootConfiguration
    assert type(configuration) is OwnerTrustRootConfiguration


def _duplicate_field_payload():
    canonical = _canonical(_record()).decode("utf-8")
    needle = '"issuer_ref":"issuer.stage2.owner.synthetic"'
    return canonical.replace(needle, needle + "," + needle).encode("utf-8")


@pytest.mark.parametrize(
    "payload",
    [
        _duplicate_field_payload(),
        _canonical({**_record(), "unknown": "value"}),
        _canonical(
            {key: value for key, value in _record().items() if key != "issuer_ref"}
        ),
        _canonical({**_record(), "issuer_ref": 1}),
        json.dumps(_record(), sort_keys=True, indent=2).encode("utf-8"),
        json.dumps(_record(), separators=(",", ":")).encode("utf-8"),
        _canonical(_record()) + b"\n",
        b"\xef\xbb\xbf" + _canonical(_record()),
        b"\xff",
        _canonical({**_record(), "schema_version": "1.1"}),
        _canonical({**_record(), "issuer_ref": "Issuer.Stage2.Owner"}),
        _canonical({**_record(), "issuer_ref": "issuer stage2 owner"}),
        _canonical({**_record(), "approval_source_id": "approval_source"}),
    ],
    ids=(
        "duplicate",
        "unknown",
        "missing",
        "wrong-type",
        "pretty",
        "reordered",
        "trailing-newline",
        "bom",
        "invalid-utf8",
        "schema",
        "uppercase-ref",
        "whitespace-ref",
        "undotted-id",
    ),
)
def test_noncanonical_or_invalid_record_is_rejected(monkeypatch, payload):
    _assert_payload_rejected(monkeypatch, payload)


@pytest.mark.parametrize(
    "encoded",
    [
        base64.b64encode(b"a" * 31).decode("ascii"),
        base64.b64encode(b"a" * 33).decode("ascii"),
        "!" * 44,
        base64.b64encode(b"\xff" * 32).decode("ascii").replace("/", "_"),
        PUBLIC_KEY_BASE64[:10] + " " + PUBLIC_KEY_BASE64[10:],
        PUBLIC_KEY_BASE64[:-1] + "A",
        "-----BEGIN PUBLIC KEY-----",
    ],
    ids=(
        "31-bytes",
        "33-bytes",
        "invalid",
        "urlsafe",
        "whitespace",
        "padding",
        "pem",
    ),
)
def test_invalid_public_key_encoding_is_rejected(monkeypatch, encoded):
    _assert_payload_rejected(
        monkeypatch,
        _canonical({**_record(), "ed25519_public_key_base64": encoded}),
    )


@pytest.mark.parametrize(
    "path",
    [
        "relative\\approvals",
        r"\\server\share\approvals",
        "c:approvals",
        "/owner/approvals",
        r"c:\owner\..\approvals",
        r"c:\owner\.\approvals",
        r"c:\owner\approvals:stream",
        r"C:\owner\approvals",
        "c:/owner/approvals",
        r"%programdata%\owner\approvals",
        "c:\\owner\\approvals\\",
        r"c:\owner\bad?name",
        r"c:\owner\bad*name",
        r"c:\owner\bad<name",
        'c:\\owner\\bad"name',
        r"c:\owner\bad|name",
        "c:\\owner\\trailing.",
        "c:\\owner\\trailing ",
        r"c:\owner\con",
        r"c:\owner\con.txt",
        r"c:\owner\prn.log",
        r"c:\owner\aux",
        r"c:\owner\nul.json",
        r"c:\owner\com1",
        r"c:\owner\com9.txt",
        r"c:\owner\lpt1",
        r"c:\owner\lpt9.txt",
    ],
)
def test_invalid_approval_source_path_is_rejected(monkeypatch, path):
    _assert_payload_rejected(
        monkeypatch,
        _canonical({**_record(), "approval_source_absolute_path": path}),
    )


@pytest.mark.parametrize(
    "component",
    [
        "CON",
        "Con.txt",
        "pRn.log",
        "AUX",
        "Nul.json",
        "Com1",
        "cOM9.txt",
        "Lpt1",
        "lpT9.log",
    ],
)
def test_reserved_windows_device_components_are_case_insensitive(component):
    assert not module._is_safe_windows_path_component(component)


@pytest.mark.parametrize(
    "component",
    [
        "console",
        "printer",
        "auxiliary",
        "null",
        "com0",
        "com10",
        "lpt0",
        "lpt10",
        "report.json",
        "internal space.txt",
    ],
)
def test_nonreserved_windows_components_remain_accepted(component):
    assert module._is_safe_windows_path_component(component)


@pytest.mark.parametrize(
    "component",
    [
        "nul.txt",
        "nul .txt",
        "nul   .txt",
        "con .txt",
        "com1 .json",
        "com9  .log",
        "lpt1 .txt",
        "lpt9  .log",
        "com\u00b9.txt",
        "com\u00b2",
        "com\u00b3 .json",
        "lpt\u00b9.txt",
        "lpt\u00b2 .log",
        "lpt\u00b3",
        "conin$",
        "conout$",
        "conin$ .txt",
        "con\u0131n$",
        "con\u0131n$ .txt",
        "CoNoUt$  .log",
        "NuL .TxT",
        "pRn .log",
        "AuX .json",
    ],
)
def test_reserved_aliases_fail_closed_without_native_access(monkeypatch, component):
    native_calls = []

    def forbidden_native():
        native_calls.append("constructed")
        raise AssertionError("reserved aliases must never reach native access")

    monkeypatch.setattr(module, "_Win32TrustRootNative", forbidden_native)
    assert not module._is_safe_windows_path_component(component)
    leaf_path = "c:\\owner-controlled\\stage2\\" + component.casefold()
    for path in (leaf_path, leaf_path + "\\child"):
        assert not module._is_canonical_absolute_path(path)
        payload = _canonical(_record(approval_source_absolute_path=path))
        with pytest.raises(OwnerTrustRootError) as error:
            module._parse_canonical_record(payload)
        assert error.value.code is OwnerTrustRootFailure.SOURCE_CONTENT_INVALID

        with pytest.raises(OwnerTrustRootError) as error:
            acquire_owner_trust_root_configuration(
                expected_path=path,
                expected_file_identity=FILE_IDENTITY,
                expected_file_sha256="a" * 64,
            )
        assert error.value.code is OwnerTrustRootFailure.INVALID_EXPECTATION
    assert native_calls == []


@pytest.mark.parametrize(
    "component",
    [
        "console",
        "console .txt",
        "com0 .txt",
        "com10 .json",
        "lpt0 .txt",
        "lpt10 .log",
        "com\u2074.txt",
        "lpt\u2074.txt",
        "conin$-backup",
        "conout$x",
        "nul\u00a0.txt",
        "report .json",
    ],
)
def test_nonreserved_alias_like_paths_remain_unchanged(monkeypatch, component):
    def forbidden_native():
        raise AssertionError("pure path parsing must never reach native access")

    monkeypatch.setattr(module, "_Win32TrustRootNative", forbidden_native)
    assert module._is_safe_windows_path_component(component)
    path = "c:\\owner-controlled\\stage2\\" + component
    assert module._is_canonical_absolute_path(path)
    parsed = module._parse_canonical_record(
        _canonical(_record(approval_source_absolute_path=path))
    )
    assert parsed.approval_source_absolute_path == path


@pytest.mark.parametrize(
    "identity",
    [
        "synthetic-volume:synthetic-file",
        "win32-fileid-v1:" + "A" * 16 + ":" + "0" * 32,
        "win32-fileid-v1:" + "0" * 15 + ":" + "0" * 32,
        "win32-fileid-v1:" + "0" * 16 + ":" + "0" * 31,
        "win32-fileid-v1:" + "0" * 16 + ":" + "g" * 32,
    ],
)
def test_invalid_approval_source_directory_identity_is_rejected(
    monkeypatch, identity
):
    _assert_payload_rejected(
        monkeypatch,
        _canonical(
            {**_record(), "approval_source_directory_identity": identity}
        ),
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"expected_path": "relative.json"},
        {"expected_path": r"\\server\share\trust.json"},
        {"expected_path": r"c:\owner\..\trust.json"},
        {"expected_path": r"c:\owner\trust.json:stream"},
        {"expected_path": "c:\\owner\\trust.json."},
        {"expected_path": r"c:\owner\con.json"},
        {"expected_path": r"c:\owner\bad?name.json"},
        {"expected_file_identity": "wrong"},
        {"expected_file_identity": "win32-fileid-v1:" + "0" * 49},
        {"expected_file_sha256": "A" * 64},
        {"expected_file_sha256": "0" * 63},
    ],
)
def test_invalid_external_expectation_rejects_before_native_open(
    monkeypatch, changes
):
    calls = []

    def factory():
        calls.append("constructed")
        return FakeNative(_canonical(_record()))

    monkeypatch.setattr(module, "_Win32TrustRootNative", factory)
    expected = {
        "expected_path": TRUST_ROOT_PATH,
        "expected_file_identity": FILE_IDENTITY,
        "expected_file_sha256": "a" * 64,
    }
    expected.update(changes)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(**expected)
    assert error.value.code is OwnerTrustRootFailure.INVALID_EXPECTATION
    assert calls == []


def test_native_facade_construction_failure_is_bounded(monkeypatch):
    def fail():
        raise OSError("synthetic")

    monkeypatch.setattr(module, "_Win32TrustRootNative", fail)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256="a" * 64,
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_OPEN_FAILED


def test_open_failure_has_no_handle_to_close(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload, fail_at="open")
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_OPEN_FAILED
    assert [call[0] for call in native.calls] == ["open"]


@pytest.mark.parametrize("fail_at", ["file_type", "attributes", "identity"])
def test_metadata_failure_closes_exactly_once(monkeypatch, fail_at):
    payload = _canonical(_record())
    native = FakeNative(payload, fail_at=fail_at)
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_METADATA_FAILED
    assert [call[0] for call in native.calls].count("close") == 1


@pytest.mark.parametrize(
    "file_type,attributes",
    [
        (0, 0),
        (module._FILE_TYPE_DISK, module._FILE_ATTRIBUTE_DIRECTORY),
        (module._FILE_TYPE_DISK, module._FILE_ATTRIBUTE_REPARSE_POINT),
    ],
    ids=("non-disk", "directory", "reparse"),
)
def test_non_regular_or_reparse_source_is_rejected_and_closed(
    monkeypatch, file_type, attributes
):
    payload = _canonical(_record())
    native = FakeNative(payload, file_type=file_type, attributes=attributes)
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_TYPE_REJECTED
    assert [call[0] for call in native.calls].count("close") == 1
    assert "read" not in [call[0] for call in native.calls]


def test_wrong_same_handle_file_identity_rejects_before_read(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload, volume_serial=0x9999)
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_IDENTITY_MISMATCH
    assert "read" not in [call[0] for call in native.calls]
    assert [call[0] for call in native.calls].count("close") == 1


def test_wrong_complete_file_sha_rejects_before_parse_and_closes(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload)
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256="0" * 64,
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_HASH_MISMATCH
    assert [call[0] for call in native.calls].count("close") == 1


@pytest.mark.parametrize(
    "native",
    [
        FakeNative(_canonical(_record()), fail_at="read"),
        FakeNative(_canonical(_record()), invalid_read_result="not-bytes"),
    ],
)
def test_read_failure_or_invalid_result_rejects_and_closes(monkeypatch, native):
    native.position = 0
    native.calls = []
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(native.payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_READ_FAILED
    assert [call[0] for call in native.calls].count("close") == 1


def test_exact_byte_bound_requires_and_accepts_eof_probe():
    native = FakeNative(b"x" * OWNER_TRUST_ROOT_MAX_BYTES)
    result = module._bounded_read(native, native.handle)
    assert result == b"x" * OWNER_TRUST_ROOT_MAX_BYTES
    reads = [call for call in native.calls if call[0] == "read"]
    assert reads == [
        ("read", native.handle, OWNER_TRUST_ROOT_MAX_BYTES),
        ("read", native.handle, 1),
    ]


def test_byte_4097_is_rejected_without_unbounded_read():
    native = FakeNative(b"x" * (OWNER_TRUST_ROOT_MAX_BYTES + 1))
    with pytest.raises(OwnerTrustRootError) as error:
        module._bounded_read(native, native.handle)
    assert error.value.code is OwnerTrustRootFailure.SOURCE_TOO_LARGE
    assert max(call[2] for call in native.calls if call[0] == "read") <= 4_096


def test_close_failure_after_valid_parse_returns_no_configuration(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload, fail_at="close")
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_CLOSE_FAILED
    assert [call[0] for call in native.calls].count("close") == 1


def test_close_failure_does_not_replace_prior_failure(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload, fail_at="close")
    native.volume_serial = 0x9999
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    assert error.value.code is OwnerTrustRootFailure.SOURCE_IDENTITY_MISMATCH
    assert [call[0] for call in native.calls].count("close") == 1


def test_bounded_errors_never_render_path_key_or_native_detail(monkeypatch):
    payload = _canonical(_record())
    native = FakeNative(payload, fail_at="read")
    monkeypatch.setattr(module, "_Win32TrustRootNative", lambda: native)
    with pytest.raises(OwnerTrustRootError) as error:
        acquire_owner_trust_root_configuration(
            expected_path=TRUST_ROOT_PATH,
            expected_file_identity=FILE_IDENTITY,
            expected_file_sha256=hashlib.sha256(payload).hexdigest(),
        )
    rendered = str(error.value) + repr(error.value)
    assert error.value.code is OwnerTrustRootFailure.SOURCE_READ_FAILED
    for sensitive in (TRUST_ROOT_PATH, PUBLIC_KEY_BASE64, "synthetic native"):
        assert sensitive not in rendered


def test_win32_capability_surface_and_policy_are_exact():
    public_methods = {
        name
        for name, value in vars(module._Win32TrustRootNative).items()
        if not name.startswith("_") and callable(value)
    }
    assert public_methods == {
        "open_read_only",
        "file_type",
        "attribute_flags",
        "file_identity_parts",
        "read",
        "close",
    }
    source = inspect.getsource(module._Win32TrustRootNative)
    for required in (
        "CreateFileW",
        "GetFileType",
        "GetFileInformationByHandleEx",
        "ReadFile",
        "CloseHandle",
        "_GENERIC_READ",
        "_FILE_SHARE_READ",
        "_OPEN_EXISTING",
        "_FILE_FLAG_OPEN_REPARSE_POINT",
    ):
        assert required in source
    for forbidden in (
        "FILE_SHARE_WRITE",
        "FILE_SHARE_DELETE",
        "WriteFile",
        "DeleteFile",
        "MoveFile",
    ):
        assert forbidden not in source


def test_no_environment_network_credential_or_runtime_composition_surface():
    source = inspect.getsource(module)
    for forbidden in (
        "os.environ",
        "os.getenv",
        "expandvars",
        "expanduser",
        "socket",
        "paramiko",
        "CredReadW",
        "WindowsCredentialManager",
        "ProductionOwnerAuthorizationVerifier",
        "Stage2MikroTikVrrpRuntime",
        "private_key",
    ):
        assert forbidden not in source


@pytest.mark.skipif(os.name != "nt", reason="requires the reviewed Win32 APIs")
def test_disposable_regular_file_is_accepted_by_exact_native_path(tmp_path):
    payload = _canonical(_record())
    path = tmp_path / "synthetic-owner-trust-root.json"
    path.write_bytes(payload)
    canonical_path = str(path.resolve()).casefold()

    native = module._Win32TrustRootNative()
    handle = native.open_read_only(canonical_path)
    try:
        identity = module._format_file_identity(
            *native.file_identity_parts(handle)
        )
    finally:
        native.close(handle)

    configuration = acquire_owner_trust_root_configuration(
        expected_path=canonical_path,
        expected_file_identity=identity,
        expected_file_sha256=hashlib.sha256(payload).hexdigest(),
    )
    assert type(configuration) is OwnerTrustRootConfiguration
    assert configuration.trust_root_source_file_identity == identity
    assert configuration.ed25519_public_key == PUBLIC_KEY


@pytest.mark.skipif(os.name != "nt", reason="requires ordinary Win32 path aliases")
def test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical(tmp_path):
    path = tmp_path / "synthetic-trailing-dot-alias.txt"
    path.write_bytes(b"synthetic")
    canonical_path = str(path.resolve()).casefold()
    trailing_dot_alias = canonical_path + "."

    native = module._Win32TrustRootNative()
    identities = []
    for candidate in (canonical_path, trailing_dot_alias):
        handle = native.open_read_only(candidate)
        try:
            identities.append(
                module._format_file_identity(*native.file_identity_parts(handle))
            )
        finally:
            native.close(handle)

    assert identities[0] == identities[1]
    assert module._is_canonical_absolute_path(canonical_path)
    assert not module._is_canonical_absolute_path(trailing_dot_alias)
