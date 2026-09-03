"""Offline immutable acquisition of one production Owner trust-root record.

The module reads one externally pinned, repository-external canonical JSON
record through one stable Win32 handle.  It does not provision trust, compose
the Owner verifier, access an approval directory, or perform network/device
operations.  Only separately trusted startup composition may supply the
expected path, file identity, and complete-file SHA-256.
"""

from __future__ import annotations

import base64
import binascii
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
import re
from typing import Final, Protocol
import unicodedata


OWNER_TRUST_ROOT_SCHEMA_VERSION: Final = "1.0"
OWNER_TRUST_ROOT_MAX_BYTES: Final = 4_096
OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES: Final = 32
_READ_CHUNK_BYTES: Final = 4_096

_GENERIC_READ: Final = 0x80000000
_FILE_SHARE_READ: Final = 0x00000001
_OPEN_EXISTING: Final = 3
_FILE_FLAG_OPEN_REPARSE_POINT: Final = 0x00200000
_FILE_TYPE_DISK: Final = 0x0001
_FILE_ATTRIBUTE_DIRECTORY: Final = 0x00000010
_FILE_ATTRIBUTE_REPARSE_POINT: Final = 0x00000400
_FILE_ATTRIBUTE_TAG_INFO_CLASS: Final = 9
_FILE_ID_INFO_CLASS: Final = 18
_INVALID_HANDLE_VALUE: Final = ctypes.c_void_p(-1).value

_TRUST_ROOT_FIELDS: Final = (
    "schema_version",
    "ed25519_public_key_base64",
    "issuer_ref",
    "lab_only_attestation_ref",
    "approval_source_id",
    "approval_source_absolute_path",
    "approval_source_directory_identity",
)
_ALLOWED_TRUST_ROOT_FIELDS: Final = frozenset(_TRUST_ROOT_FIELDS)
_REFERENCE_PATTERN: Final = re.compile(
    r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$"
)
_CANONICAL_PATH_PATTERN: Final = re.compile(r"^[a-z]:\\[^\\]+(?:\\[^\\]+)*$")
_FILE_IDENTITY_PATTERN: Final = re.compile(
    r"^win32-fileid-v1:[0-9a-f]{16}:[0-9a-f]{32}$"
)
_LOWER_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_PUBLIC_KEY_BASE64_PATTERN: Final = re.compile(r"^[A-Za-z0-9+/]{43}=$")
_MAX_REFERENCE_LENGTH: Final = 160
_MAX_PATH_LENGTH: Final = 1_024
_FORBIDDEN_WINDOWS_COMPONENT_CHARACTERS: Final = frozenset('<>:"/\\|?*')
_RESERVED_WINDOWS_DEVICE_NAMES: Final = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "CONIN$",
        "CONOUT$",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "COM\u00b9",
        "COM\u00b2",
        "COM\u00b3",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
        "LPT\u00b9",
        "LPT\u00b2",
        "LPT\u00b3",
    }
)


class OwnerTrustRootFailure(Enum):
    """Bounded failures that never render trust material or native details."""

    INVALID_EXPECTATION = "INVALID_EXPECTATION"
    SOURCE_OPEN_FAILED = "SOURCE_OPEN_FAILED"
    SOURCE_TYPE_REJECTED = "SOURCE_TYPE_REJECTED"
    SOURCE_METADATA_FAILED = "SOURCE_METADATA_FAILED"
    SOURCE_IDENTITY_MISMATCH = "SOURCE_IDENTITY_MISMATCH"
    SOURCE_READ_FAILED = "SOURCE_READ_FAILED"
    SOURCE_TOO_LARGE = "SOURCE_TOO_LARGE"
    SOURCE_HASH_MISMATCH = "SOURCE_HASH_MISMATCH"
    SOURCE_CONTENT_INVALID = "SOURCE_CONTENT_INVALID"
    SOURCE_CLOSE_FAILED = "SOURCE_CLOSE_FAILED"


class OwnerTrustRootError(ValueError):
    """One sanitized fail-closed error for trust-root acquisition."""

    def __init__(self, code: OwnerTrustRootFailure) -> None:
        if type(code) is not OwnerTrustRootFailure:
            raise TypeError("trust-root error requires a bounded category")
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class _ParsedTrustRoot:
    ed25519_public_key: bytes
    issuer_ref: str
    lab_only_attestation_ref: str
    approval_source_id: str
    approval_source_absolute_path: str
    approval_source_directory_identity: str
    public_key_sha256_fingerprint: str


@dataclass(frozen=True, slots=True, init=False, repr=False)
class OwnerTrustRootConfiguration:
    """Acquisition-issued trusted composition; unsupported creation is blocked."""

    schema_version: str
    ed25519_public_key: bytes
    issuer_ref: str
    lab_only_attestation_ref: str
    approval_source_id: str
    approval_source_absolute_path: str
    approval_source_directory_identity: str
    public_key_sha256_fingerprint: str
    trust_root_source_file_identity: str
    trust_root_source_file_sha256: str

    def __new__(cls, *args, **kwargs):
        raise TypeError("trust-root configurations are created only by acquisition")

    def __init__(self, *args, **kwargs) -> None:
        raise TypeError("trust-root configurations are created only by acquisition")

    def __init_subclass__(cls, **kwargs) -> None:
        raise TypeError("trust-root configurations cannot be subclassed")

    def __getstate__(self):
        raise TypeError("trust-root configurations cannot be reconstructed")

    def __reduce__(self):
        raise TypeError("trust-root configurations cannot be reconstructed")

    def __reduce_ex__(self, protocol):
        raise TypeError("trust-root configurations cannot be reconstructed")

    def __copy__(self):
        raise TypeError("trust-root configurations cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("trust-root configurations cannot be copied")

    def __repr__(self) -> str:
        return "OwnerTrustRootConfiguration(<acquisition-issued>)"

    __str__ = __repr__


class _TrustRootNative(Protocol):
    def open_read_only(self, path: str) -> object: ...
    def file_type(self, handle: object) -> int: ...
    def attribute_flags(self, handle: object) -> int: ...
    def file_identity_parts(self, handle: object) -> tuple[int, bytes]: ...
    def read(self, handle: object, maximum: int) -> bytes: ...
    def close(self, handle: object) -> None: ...


class _FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [
        ("FileAttributes", wintypes.DWORD),
        ("ReparseTag", wintypes.DWORD),
    ]


class _FILE_ID_128(ctypes.Structure):
    _fields_ = [("Identifier", ctypes.c_ubyte * 16)]


class _FILE_ID_INFO(ctypes.Structure):
    _fields_ = [
        ("VolumeSerialNumber", ctypes.c_ulonglong),
        ("FileId", _FILE_ID_128),
    ]


class _Win32TrustRootNative:
    """Minimum private Win32 facade for one trust-root acquisition."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("unsupported platform")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create_file = kernel32.CreateFileW
        self._create_file.argtypes = (
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        )
        self._create_file.restype = wintypes.HANDLE
        self._get_file_type = kernel32.GetFileType
        self._get_file_type.argtypes = (wintypes.HANDLE,)
        self._get_file_type.restype = wintypes.DWORD
        self._get_information = kernel32.GetFileInformationByHandleEx
        self._get_information.argtypes = (
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        )
        self._get_information.restype = wintypes.BOOL
        self._read_file = kernel32.ReadFile
        self._read_file.argtypes = (
            wintypes.HANDLE,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID,
        )
        self._read_file.restype = wintypes.BOOL
        self._close_handle = kernel32.CloseHandle
        self._close_handle.argtypes = (wintypes.HANDLE,)
        self._close_handle.restype = wintypes.BOOL

    def open_read_only(self, path: str) -> object:
        handle = self._create_file(
            path,
            _GENERIC_READ,
            _FILE_SHARE_READ,
            None,
            _OPEN_EXISTING,
            _FILE_FLAG_OPEN_REPARSE_POINT,
            None,
        )
        if handle == _INVALID_HANDLE_VALUE:
            raise OSError("open failed")
        return handle

    def file_type(self, handle: object) -> int:
        return int(self._get_file_type(handle))

    def attribute_flags(self, handle: object) -> int:
        info = _FILE_ATTRIBUTE_TAG_INFO()
        if not self._get_information(
            handle,
            _FILE_ATTRIBUTE_TAG_INFO_CLASS,
            ctypes.byref(info),
            ctypes.sizeof(info),
        ):
            raise OSError("metadata failed")
        return int(info.FileAttributes)

    def file_identity_parts(self, handle: object) -> tuple[int, bytes]:
        info = _FILE_ID_INFO()
        if not self._get_information(
            handle,
            _FILE_ID_INFO_CLASS,
            ctypes.byref(info),
            ctypes.sizeof(info),
        ):
            raise OSError("identity failed")
        return int(info.VolumeSerialNumber), bytes(info.FileId.Identifier)

    def read(self, handle: object, maximum: int) -> bytes:
        buffer = ctypes.create_string_buffer(maximum)
        count = wintypes.DWORD()
        if not self._read_file(
            handle,
            buffer,
            maximum,
            ctypes.byref(count),
            None,
        ) or count.value > maximum:
            raise OSError("read failed")
        return buffer.raw[: count.value]

    def close(self, handle: object) -> None:
        if not self._close_handle(handle):
            raise OSError("close failed")


def acquire_owner_trust_root_configuration(
    *,
    expected_path: str,
    expected_file_identity: str,
    expected_file_sha256: str,
) -> OwnerTrustRootConfiguration:
    """Acquire one externally pinned trust root; no defaults or overrides."""

    if (
        not _is_canonical_absolute_path(expected_path)
        or type(expected_file_identity) is not str
        or not _FILE_IDENTITY_PATTERN.fullmatch(expected_file_identity)
        or type(expected_file_sha256) is not str
        or not _LOWER_SHA256_PATTERN.fullmatch(expected_file_sha256)
    ):
        _fail(OwnerTrustRootFailure.INVALID_EXPECTATION)

    try:
        native = _Win32TrustRootNative()
    except Exception:
        _fail(OwnerTrustRootFailure.SOURCE_OPEN_FAILED)
    try:
        handle = native.open_read_only(expected_path)
    except Exception:
        _fail(OwnerTrustRootFailure.SOURCE_OPEN_FAILED)

    parsed: _ParsedTrustRoot | None = None
    source_identity: str | None = None
    source_sha256: str | None = None
    failure: OwnerTrustRootError | None = None
    try:
        try:
            file_type = native.file_type(handle)
            attributes = native.attribute_flags(handle)
        except Exception:
            _fail(OwnerTrustRootFailure.SOURCE_METADATA_FAILED)
        if file_type != _FILE_TYPE_DISK or attributes & (
            _FILE_ATTRIBUTE_DIRECTORY | _FILE_ATTRIBUTE_REPARSE_POINT
        ):
            _fail(OwnerTrustRootFailure.SOURCE_TYPE_REJECTED)

        try:
            source_identity = _format_file_identity(
                *native.file_identity_parts(handle)
            )
        except OwnerTrustRootError:
            raise
        except Exception:
            _fail(OwnerTrustRootFailure.SOURCE_METADATA_FAILED)
        if source_identity != expected_file_identity:
            _fail(OwnerTrustRootFailure.SOURCE_IDENTITY_MISMATCH)

        raw_file = _bounded_read(native, handle)
        source_sha256 = hashlib.sha256(raw_file).hexdigest()
        if source_sha256 != expected_file_sha256:
            _fail(OwnerTrustRootFailure.SOURCE_HASH_MISMATCH)
        parsed = _parse_canonical_record(raw_file)
    except OwnerTrustRootError as exc:
        failure = exc
    except Exception:
        failure = OwnerTrustRootError(OwnerTrustRootFailure.SOURCE_METADATA_FAILED)

    try:
        native.close(handle)
    except Exception:
        if failure is None:
            failure = OwnerTrustRootError(OwnerTrustRootFailure.SOURCE_CLOSE_FAILED)

    if failure is not None:
        raise failure
    if parsed is None or source_identity is None or source_sha256 is None:
        _fail(OwnerTrustRootFailure.SOURCE_METADATA_FAILED)

    configuration = object.__new__(OwnerTrustRootConfiguration)
    for field_name, value in (
        ("schema_version", OWNER_TRUST_ROOT_SCHEMA_VERSION),
        ("ed25519_public_key", parsed.ed25519_public_key),
        ("issuer_ref", parsed.issuer_ref),
        ("lab_only_attestation_ref", parsed.lab_only_attestation_ref),
        ("approval_source_id", parsed.approval_source_id),
        ("approval_source_absolute_path", parsed.approval_source_absolute_path),
        (
            "approval_source_directory_identity",
            parsed.approval_source_directory_identity,
        ),
        ("public_key_sha256_fingerprint", parsed.public_key_sha256_fingerprint),
        ("trust_root_source_file_identity", source_identity),
        ("trust_root_source_file_sha256", source_sha256),
    ):
        object.__setattr__(configuration, field_name, value)
    return configuration


def _bounded_read(native: _TrustRootNative, handle: object) -> bytes:
    chunks: list[bytes] = []
    accumulated = 0
    while True:
        request = min(
            _READ_CHUNK_BYTES,
            OWNER_TRUST_ROOT_MAX_BYTES + 1 - accumulated,
        )
        if request <= 0:
            _fail(OwnerTrustRootFailure.SOURCE_TOO_LARGE)
        try:
            chunk = native.read(handle, request)
        except Exception:
            _fail(OwnerTrustRootFailure.SOURCE_READ_FAILED)
        if type(chunk) is not bytes or len(chunk) > request:
            _fail(OwnerTrustRootFailure.SOURCE_READ_FAILED)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        accumulated += len(chunk)
        if accumulated > OWNER_TRUST_ROOT_MAX_BYTES:
            _fail(OwnerTrustRootFailure.SOURCE_TOO_LARGE)


def _parse_canonical_record(raw_file: bytes) -> _ParsedTrustRoot:
    if (
        type(raw_file) is not bytes
        or not 1 <= len(raw_file) <= OWNER_TRUST_ROOT_MAX_BYTES
        or raw_file.startswith(b"\xef\xbb\xbf")
    ):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    try:
        text = raw_file.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    try:
        record = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: _fail(
                OwnerTrustRootFailure.SOURCE_CONTENT_INVALID
            ),
        )
    except OwnerTrustRootError:
        raise
    except Exception:
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    if (
        type(record) is not dict
        or len(record) != len(_TRUST_ROOT_FIELDS)
        or any(type(key) is not str for key in record)
        or record.keys() != _ALLOWED_TRUST_ROOT_FIELDS
        or any(type(value) is not str for value in record.values())
    ):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    if _canonical_json_bytes(record) != raw_file:
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    if record["schema_version"] != OWNER_TRUST_ROOT_SCHEMA_VERSION:
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)

    public_key = _decode_public_key(record["ed25519_public_key_base64"])
    issuer_ref = _canonical_reference(record["issuer_ref"])
    attestation_ref = _canonical_reference(record["lab_only_attestation_ref"])
    approval_source_id = _canonical_reference(record["approval_source_id"])
    approval_source_path = record["approval_source_absolute_path"]
    if not _is_canonical_absolute_path(approval_source_path):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    approval_source_identity = record["approval_source_directory_identity"]
    if not _FILE_IDENTITY_PATTERN.fullmatch(approval_source_identity):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)

    fingerprint = "SHA256:" + base64.b64encode(
        hashlib.sha256(public_key).digest()
    ).decode("ascii").rstrip("=")
    return _ParsedTrustRoot(
        ed25519_public_key=public_key,
        issuer_ref=issuer_ref,
        lab_only_attestation_ref=attestation_ref,
        approval_source_id=approval_source_id,
        approval_source_absolute_path=approval_source_path,
        approval_source_directory_identity=approval_source_identity,
        public_key_sha256_fingerprint=fingerprint,
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
        result[key] = value
    return result


def _canonical_json_bytes(record: dict[str, object]) -> bytes:
    try:
        return json.dumps(
            record,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeEncodeError):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)


def _decode_public_key(value: object) -> bytes:
    if (
        type(value) is not str
        or len(value) != 44
        or not _PUBLIC_KEY_BASE64_PATTERN.fullmatch(value)
    ):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    if (
        len(decoded) != OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES
        or base64.b64encode(decoded).decode("ascii") != value
    ):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    return decoded


def _canonical_reference(value: object) -> str:
    if (
        type(value) is not str
        or not 1 <= len(value) <= _MAX_REFERENCE_LENGTH
        or not value.isascii()
        or not _REFERENCE_PATTERN.fullmatch(value)
    ):
        _fail(OwnerTrustRootFailure.SOURCE_CONTENT_INVALID)
    return value


def _is_canonical_absolute_path(path: object) -> bool:
    if (
        type(path) is not str
        or not 4 <= len(path) <= _MAX_PATH_LENGTH
        or path != unicodedata.normalize("NFC", path).casefold()
        or "/" in path
        or path.count(":") != 1
        or any(ord(character) < 32 for character in path)
        or not _CANONICAL_PATH_PATTERN.fullmatch(path)
    ):
        return False
    return all(
        _is_safe_windows_path_component(part)
        for part in path[3:].split("\\")
    )


def _is_safe_windows_path_component(component: object) -> bool:
    if (
        type(component) is not str
        or not component
        or component in {".", ".."}
        or component.endswith((".", " "))
        or any(
            ord(character) < 32
            or character in _FORBIDDEN_WINDOWS_COMPONENT_CHARACTERS
            for character in component
        )
    ):
        return False
    # DOS device matching ignores ASCII spaces before the first extension
    # and uses uppercase matching (including dotless-i in CONIN$).
    # Classify only: never normalize an accepted component into another path.
    device_stem = component.split(".", 1)[0].rstrip(" ").upper()
    return device_stem not in _RESERVED_WINDOWS_DEVICE_NAMES


def _format_file_identity(volume_serial: int, file_id: bytes) -> str:
    if (
        type(volume_serial) is not int
        or not 0 <= volume_serial <= 0xFFFFFFFFFFFFFFFF
        or type(file_id) is not bytes
        or len(file_id) != 16
    ):
        _fail(OwnerTrustRootFailure.SOURCE_METADATA_FAILED)
    return f"win32-fileid-v1:{volume_serial:016x}:{file_id.hex()}"


def _fail(code: OwnerTrustRootFailure) -> None:
    raise OwnerTrustRootError(code)


__all__ = (
    "OWNER_TRUST_ROOT_MAX_BYTES",
    "OWNER_TRUST_ROOT_PUBLIC_KEY_BYTES",
    "OWNER_TRUST_ROOT_SCHEMA_VERSION",
    "OwnerTrustRootConfiguration",
    "OwnerTrustRootError",
    "OwnerTrustRootFailure",
    "acquire_owner_trust_root_configuration",
)
