"""Immutable offline host trust; successful acquisition never authorizes execution.

Trusted startup supplies independent pins for one preprovisioned local file.
Owner-controlled storage outside Git, protected ancestors and ACLs are deployment
preconditions. This module neither provisions them nor establishes freshness.
"""

import base64 as _base64
from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
import hashlib as _hashlib
import json as _json
import re as _re
import sys as _sys
import unicodedata as _unicodedata

from validation_framework.stage2_mikrotik_target_registry import (
    Stage2FixedTargetEndpoint as _Endpoint,
)

_SCHEMA = "s2-ro-07.known-host.v1"
_ALGORITHM = "ssh-ed25519"
_MAX_BYTES = 2048
_BLOB_PREFIX = b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20"
_FIELDS = frozenset({"schema_version", "target_ref", "address", "port",
                     "host_key_algorithm", "host_key_base64"})
_IDENTITY = _re.compile(r"win32-fileid-v1:[0-9a-f]{16}:[0-9a-f]{32}")
_SHA = _re.compile(r"[0-9a-f]{64}")
_BASE64 = _re.compile(r"[A-Za-z0-9+/]{68}")
_PATH = _re.compile(r"[a-z]:\\[^\\]+(?:\\[^\\]+)*")
_DEVICES = frozenset({"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
                     | {prefix + digit for prefix in ("COM", "LPT")
                        for digit in "123456789¹²³"})


class Stage2KnownHostFailure(_Enum):
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    INVALID_TARGET = "INVALID_TARGET"
    PLATFORM_UNSUPPORTED = "PLATFORM_UNSUPPORTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_TYPE_REJECTED = "SOURCE_TYPE_REJECTED"
    SOURCE_REPARSE_REJECTED = "SOURCE_REPARSE_REJECTED"
    SOURCE_IDENTITY_MISMATCH = "SOURCE_IDENTITY_MISMATCH"
    SOURCE_HASH_MISMATCH = "SOURCE_HASH_MISMATCH"
    SOURCE_TOO_LARGE = "SOURCE_TOO_LARGE"
    SOURCE_READ_FAILED = "SOURCE_READ_FAILED"
    SOURCE_CLOSE_FAILED = "SOURCE_CLOSE_FAILED"
    MALFORMED_SNAPSHOT = "MALFORMED_SNAPSHOT"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
    UNSUPPORTED_HOST_KEY_ALGORITHM = "UNSUPPORTED_HOST_KEY_ALGORITHM"
    TARGET_BINDING_MISMATCH = "TARGET_BINDING_MISMATCH"
    MALFORMED_HOST_KEY = "MALFORMED_HOST_KEY"


class Stage2KnownHostError(ValueError):
    """Only a bounded category, never native exception details or source data."""

    def __init__(self, code: Stage2KnownHostFailure):
        if type(code) is not Stage2KnownHostFailure:
            raise TypeError("bounded known-host category required")
        self.code = code
        super().__init__(code.value)


def _fail(code):
    raise Stage2KnownHostError(code) from None


def _call(code, operation, *args):
    failed = False
    try:
        result = operation(*args)
    except Exception:
        failed = True
    # Outside except: neither __cause__ nor __context__ keeps rejected details.
    if failed:
        _fail(code)
    return result


def _valid_path(path):
    if (type(path) is not str or not 4 <= len(path) <= 1024
            or path != _unicodedata.normalize("NFC", path).casefold()
            or "/" in path or path.count(":") != 1
            or _PATH.fullmatch(path) is None):
        return False
    for component in path[3:].split("\\"):
        if (not component or component in (".", "..")
                or component.endswith((".", " "))
                or any(ord(c) < 32 or c in '<>:"/\\|?*' for c in component)
                or component.split(".", 1)[0].rstrip(" ").upper() in _DEVICES):
            return False
    return True


def _captured_configuration(configuration):
    if type(configuration) is not Stage2KnownHostSourceConfiguration:
        _fail(Stage2KnownHostFailure.INVALID_CONFIGURATION)
    endpoint = _call(Stage2KnownHostFailure.INVALID_CONFIGURATION,
                     lambda: configuration.expected_endpoint)
    if type(endpoint) is not _Endpoint:
        _fail(Stage2KnownHostFailure.INVALID_TARGET)
    _call(Stage2KnownHostFailure.INVALID_TARGET, _Endpoint.__post_init__, endpoint)
    path, identity, digest = _call(
        Stage2KnownHostFailure.INVALID_CONFIGURATION,
        lambda: (configuration.expected_path, configuration.expected_file_identity,
                 configuration.expected_file_sha256))
    target = (endpoint.target_ref, endpoint.address, endpoint.port)
    if (not _valid_path(path) or type(identity) is not str
            or _IDENTITY.fullmatch(identity) is None or type(digest) is not str
            or _SHA.fullmatch(digest) is None):
        _fail(Stage2KnownHostFailure.INVALID_CONFIGURATION)
    return path, identity, digest, target


@_dataclass(frozen=True, slots=True, repr=False)
class Stage2KnownHostSourceConfiguration:
    """Trusted-startup pins, not a request configuration or provenance service."""

    expected_path: str
    expected_file_identity: str
    expected_file_sha256: str
    expected_endpoint: _Endpoint

    def __post_init__(self):
        _captured_configuration(self)

    def __repr__(self):
        return "Stage2KnownHostSourceConfiguration(<trusted-startup-pins>)"

    __str__ = __repr__


@_dataclass(frozen=True, slots=True, init=False, repr=False)
class Stage2KnownHostSnapshot:
    """Acquisition-issued host trust facts, never an execution grant."""

    schema_version: str
    target_ref: str
    address: str
    port: int
    host_key_algorithm: str
    host_key_blob: bytes
    host_key_sha256: str
    host_key_fingerprint: str
    source_file_identity: str
    source_artifact_sha256: str
    execution_authorized: bool

    def __new__(cls, *args, **kwargs):
        raise TypeError("known-host snapshots are acquisition-issued only")

    def __init__(self, *args, **kwargs):
        raise TypeError("known-host snapshots are acquisition-issued only")

    def __init_subclass__(cls, **kwargs):
        raise TypeError("known-host snapshots cannot be subclassed")

    def __copy__(self):
        raise TypeError("known-host snapshots cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("known-host snapshots cannot be copied")

    def __getstate__(self):
        raise TypeError("known-host snapshots cannot be reconstructed")

    def __setstate__(self, state):
        raise TypeError("known-host snapshots cannot be reconstructed")

    def __reduce__(self):
        raise TypeError("known-host snapshots cannot be reconstructed")

    def __reduce_ex__(self, protocol):
        raise TypeError("known-host snapshots cannot be reconstructed")

    def __repr__(self):
        return "Stage2KnownHostSnapshot(<host-trust-not-execution-authority>)"

    __str__ = __repr__


def _unique_object(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            _fail(Stage2KnownHostFailure.MALFORMED_SNAPSHOT)
        record[key] = value
    return record


def _parse(raw, target):
    if type(raw) is not bytes or not 1 <= len(raw) <= _MAX_BYTES:
        _fail(Stage2KnownHostFailure.MALFORMED_SNAPSHOT)
    record = _call(Stage2KnownHostFailure.MALFORMED_SNAPSHOT,
                   lambda: _json.loads(raw.decode("utf-8", errors="strict"),
                                       object_pairs_hook=_unique_object,
                                       parse_constant=lambda _: _fail(
                                           Stage2KnownHostFailure.MALFORMED_SNAPSHOT)))
    if (type(record) is not dict or record.keys() != _FIELDS
            or type(record["port"]) is not int
            or any(type(value) is not str or not value.isascii()
                   for name, value in record.items() if name != "port")):
        _fail(Stage2KnownHostFailure.MALFORMED_SNAPSHOT)
    canonical = _json.dumps(record, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False, allow_nan=False).encode("utf-8")
    if canonical != raw:
        _fail(Stage2KnownHostFailure.MALFORMED_SNAPSHOT)
    if record["schema_version"] != _SCHEMA:
        _fail(Stage2KnownHostFailure.UNSUPPORTED_SCHEMA)
    if record["host_key_algorithm"] != _ALGORITHM:
        _fail(Stage2KnownHostFailure.UNSUPPORTED_HOST_KEY_ALGORITHM)
    if (record["target_ref"], record["address"], record["port"]) != target:
        _fail(Stage2KnownHostFailure.TARGET_BINDING_MISMATCH)
    encoded = record["host_key_base64"]
    if _BASE64.fullmatch(encoded) is None:
        _fail(Stage2KnownHostFailure.MALFORMED_HOST_KEY)
    blob = _call(Stage2KnownHostFailure.MALFORMED_HOST_KEY,
                 lambda: _base64.b64decode(encoded, validate=True))
    if (len(blob) != 51 or blob[:19] != _BLOB_PREFIX
            or _base64.b64encode(blob).decode("ascii") != encoded):
        _fail(Stage2KnownHostFailure.MALFORMED_HOST_KEY)
    return blob


class _Win32KnownHostNative:
    """Deferred five-function adapter for this single read-only source."""

    def __init__(self):
        if _sys.platform != "win32":
            raise OSError("unsupported platform")
        import ctypes
        from ctypes import wintypes

        class AttributeInfo(ctypes.Structure):
            _fields_ = [("attributes", ctypes.c_uint32), ("tag", ctypes.c_uint32)]

        class IdentityInfo(ctypes.Structure):
            _fields_ = [("volume", ctypes.c_uint64), ("identifier", ctypes.c_ubyte * 16)]

        self._ctypes = ctypes
        self._attribute_info = AttributeInfo
        self._identity_info = IdentityInfo
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create = dll.CreateFileW
        self._create.argtypes = (wintypes.LPCWSTR, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                 wintypes.HANDLE)
        self._create.restype = wintypes.HANDLE
        self._type = dll.GetFileType
        self._type.argtypes = (wintypes.HANDLE,)
        self._type.restype = ctypes.c_uint32
        self._information = dll.GetFileInformationByHandleEx
        self._information.argtypes = (wintypes.HANDLE, ctypes.c_int,
                                      ctypes.c_void_p, ctypes.c_uint32)
        self._information.restype = ctypes.c_int32
        self._read = dll.ReadFile
        self._read.argtypes = (wintypes.HANDLE, ctypes.c_void_p, ctypes.c_uint32,
                               ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p)
        self._read.restype = ctypes.c_int32
        self._close = dll.CloseHandle
        self._close.argtypes = (wintypes.HANDLE,)
        self._close.restype = ctypes.c_int32

    def open_source(self, path):
        handle = self._create(path, 0x80000000, 1, None, 3, 0x00200000, None)
        if handle is None or handle == self._ctypes.c_void_p(-1).value or handle == 0:
            raise OSError("open failed")
        return handle

    def metadata(self, handle):
        kind = int(self._type(handle))
        info = self._attribute_info()
        if not self._information(handle, 9, self._ctypes.byref(info), self._ctypes.sizeof(info)):
            raise OSError("metadata failed")
        return kind, int(info.attributes)

    def identity(self, handle):
        info = self._identity_info()
        if not self._information(handle, 18, self._ctypes.byref(info), self._ctypes.sizeof(info)):
            raise OSError("identity failed")
        return f"win32-fileid-v1:{info.volume:016x}:{bytes(info.identifier).hex()}"

    def read(self, handle, maximum):
        buffer = self._ctypes.create_string_buffer(maximum)
        count = self._ctypes.c_uint32()
        if not self._read(handle, buffer, maximum, self._ctypes.byref(count), None):
            raise OSError("read failed")
        if count.value > maximum:
            raise OSError("invalid read count")
        return buffer.raw[:count.value]

    def close(self, handle):
        if not self._close(handle):
            raise OSError("close failed")


def _read_bounded(native, handle):
    chunks = []
    size = 0
    while True:
        maximum = min(_MAX_BYTES, _MAX_BYTES + 1 - size)
        chunk = _call(Stage2KnownHostFailure.SOURCE_READ_FAILED, native.read, handle, maximum)
        if type(chunk) is not bytes or len(chunk) > maximum:
            _fail(Stage2KnownHostFailure.SOURCE_READ_FAILED)
        if not chunk:
            return b"".join(chunks)
        size += len(chunk)
        if size > _MAX_BYTES:
            _fail(Stage2KnownHostFailure.SOURCE_TOO_LARGE)
        chunks.append(chunk)


def acquire_stage2_known_host_snapshot(
    configuration: Stage2KnownHostSourceConfiguration,
) -> Stage2KnownHostSnapshot:
    """Acquire one pinned source; no request overrides, retries or trust fallback."""
    path, expected_identity, expected_sha, target = _captured_configuration(configuration)
    if _sys.platform != "win32":
        _fail(Stage2KnownHostFailure.PLATFORM_UNSUPPORTED)
    native = _call(Stage2KnownHostFailure.SOURCE_UNAVAILABLE, _Win32KnownHostNative)
    handle = _call(Stage2KnownHostFailure.SOURCE_UNAVAILABLE, native.open_source, path)
    # The private facade must return a positive native HANDLE, never a sentinel.
    if type(handle) is not int or handle <= 0 or handle in (0xffffffff, 0xffffffffffffffff):
        _fail(Stage2KnownHostFailure.SOURCE_UNAVAILABLE)
    failure = None
    try:
        metadata = _call(Stage2KnownHostFailure.SOURCE_UNAVAILABLE, native.metadata, handle)
        if (type(metadata) is not tuple or len(metadata) != 2
                or any(type(v) is not int or not 0 <= v <= 0xffffffff for v in metadata)):
            _fail(Stage2KnownHostFailure.SOURCE_TYPE_REJECTED)
        kind, attributes = metadata
        if kind != 1 or attributes & 0x10:
            _fail(Stage2KnownHostFailure.SOURCE_TYPE_REJECTED)
        if attributes & 0x400:
            _fail(Stage2KnownHostFailure.SOURCE_REPARSE_REJECTED)
        identity = _call(Stage2KnownHostFailure.SOURCE_UNAVAILABLE, native.identity, handle)
        if type(identity) is not str or identity != expected_identity:
            _fail(Stage2KnownHostFailure.SOURCE_IDENTITY_MISMATCH)
        raw = _read_bounded(native, handle)
        digest = _hashlib.sha256(raw).hexdigest()
        if digest != expected_sha:
            _fail(Stage2KnownHostFailure.SOURCE_HASH_MISMATCH)
        blob = _parse(raw, target)
        key_digest = _hashlib.sha256(blob).digest()
        facts = (
            ("schema_version", _SCHEMA), ("target_ref", target[0]),
            ("address", target[1]), ("port", target[2]),
            ("host_key_algorithm", _ALGORITHM), ("host_key_blob", blob),
            ("host_key_sha256", key_digest.hex()),
            ("host_key_fingerprint", "SHA256:" + _base64.b64encode(key_digest).decode("ascii").rstrip("=")),
            ("source_file_identity", identity), ("source_artifact_sha256", digest),
            ("execution_authorized", False),
        )
    except Stage2KnownHostError as error:
        failure = error.code
    finally:
        try:
            native.close(handle)
        except Exception:
            failure = failure or Stage2KnownHostFailure.SOURCE_CLOSE_FAILED
    if failure is not None:
        _fail(failure)
    # The only supported issuance site, reachable only after successful close.
    result = object.__new__(Stage2KnownHostSnapshot)
    for name, value in facts:
        object.__setattr__(result, name, value)
    return result


__all__ = (
    "Stage2KnownHostSourceConfiguration", "Stage2KnownHostSnapshot",
    "Stage2KnownHostFailure", "Stage2KnownHostError", "acquire_stage2_known_host_snapshot",
)
