"""Exact offline Owner authenticity verification, never execution authority.

Only an acquisition-issued Owner trust root supplies authority. Native access
is deferred to the exact approval source; no provisioning or runtime wiring
is performed here. Protected ancestors and local Owner-controlled storage are
the existing trust-root deployment preconditions, not established by this code.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, fields
from enum import Enum
import hashlib
import json
import re
import sys

from validation_framework.stage2_live_authorization_owner_trust_root import (
    OwnerTrustRootConfiguration,
)
from validation_framework.stage2_authorization_envelope_ledger import (
    Stage2AuthorizationEnvelope,
    owner_verification_payload,
)


APPROVAL_SCHEMA_VERSION = "s2-ro-06.owner-approval.v1"
SIGNATURE_ALGORITHM = "Ed25519"
MAX_APPROVAL_ARTIFACT_BYTES = 2048
MAX_APPROVAL_PATH_CHARACTERS = 1190
_FIELDS = frozenset({"schema_version", "issuer_ref", "signature_algorithm", "signature_base64"})
_REFERENCE = re.compile(r"[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+")
_SIGNATURE = re.compile(r"[A-Za-z0-9+/]{86}==")
_GENERIC_READ = 0x80000000
_FILE_SHARE_READ = 1
_OPEN_EXISTING = 3
_OPEN_REPARSE_POINT = 0x00200000
_BACKUP_SEMANTICS = 0x02000000
_DISK = 1
_DIRECTORY = 0x10
_REPARSE_POINT = 0x400


class Stage2OwnerVerificationFailure(Enum):
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    INVALID_ENVELOPE = "INVALID_ENVELOPE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_TYPE_REJECTED = "SOURCE_TYPE_REJECTED"
    SOURCE_IDENTITY_MISMATCH = "SOURCE_IDENTITY_MISMATCH"
    SOURCE_TOO_LARGE = "SOURCE_TOO_LARGE"
    SOURCE_READ_FAILED = "SOURCE_READ_FAILED"
    SOURCE_CLOSE_FAILED = "SOURCE_CLOSE_FAILED"
    MALFORMED_ARTIFACT = "MALFORMED_ARTIFACT"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"
    UNSUPPORTED_ALGORITHM = "UNSUPPORTED_ALGORITHM"
    UNKNOWN_ISSUER = "UNKNOWN_ISSUER"
    MALFORMED_SIGNATURE = "MALFORMED_SIGNATURE"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    CRYPTO_UNAVAILABLE = "CRYPTO_UNAVAILABLE"


class Stage2OwnerVerificationError(ValueError):
    """Only a bounded category is retained; underlying errors are discarded."""

    def __init__(self, code: Stage2OwnerVerificationFailure):
        if type(code) is not Stage2OwnerVerificationFailure:
            raise TypeError("bounded Owner verification category required")
        self.code = code
        super().__init__(code.value)


def _fail(code):
    raise Stage2OwnerVerificationError(code) from None


def _call(code, operation, *args):
    failed = False
    try:
        result = operation(*args)
    except Exception:
        failed = True
    # Raise outside the except block so __context__ retains no native detail.
    if failed:
        _fail(code)
    return result


def _configuration(trust_root):
    if type(trust_root) is not OwnerTrustRootConfiguration:
        _fail(Stage2OwnerVerificationFailure.INVALID_CONFIGURATION)
    # Do not duplicate acquisition validation or accept reconstructed records.
    # Access every issued field to reject an uninitialized exact-type object.
    _call(Stage2OwnerVerificationFailure.INVALID_CONFIGURATION,
          lambda: tuple(getattr(trust_root, f.name) for f in fields(trust_root)))


def _reference(value):
    return (type(value) is str and 1 <= len(value) <= 160
            and value.isascii() and _REFERENCE.fullmatch(value) is not None)


def _approval_reference(value):
    if not _reference(value) or not value.startswith("authorization."):
        _fail(Stage2OwnerVerificationFailure.INVALID_ENVELOPE)


def _canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _signature_bytes(value):
    if type(value) is not str or len(value) != 88 or not _SIGNATURE.fullmatch(value):
        _fail(Stage2OwnerVerificationFailure.MALFORMED_SIGNATURE)
    decoded = _call(Stage2OwnerVerificationFailure.MALFORMED_SIGNATURE,
                    lambda: base64.b64decode(value, validate=True))
    if len(decoded) != 64 or base64.b64encode(decoded).decode("ascii") != value:
        _fail(Stage2OwnerVerificationFailure.MALFORMED_SIGNATURE)
    return decoded


@dataclass(frozen=True, slots=True, repr=False)
class Stage2OwnerApprovalArtifact:
    """Untrusted immutable parsed data, not successful verification evidence."""

    schema_version: str
    issuer_ref: str
    signature_algorithm: str
    signature_base64: str

    def __post_init__(self):
        if any(type(getattr(self, f.name)) is not str or not getattr(self, f.name).isascii()
               for f in fields(self)):
            _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
        if self.schema_version != APPROVAL_SCHEMA_VERSION:
            _fail(Stage2OwnerVerificationFailure.UNSUPPORTED_SCHEMA)
        if self.signature_algorithm != SIGNATURE_ALGORITHM:
            _fail(Stage2OwnerVerificationFailure.UNSUPPORTED_ALGORITHM)
        if not _reference(self.issuer_ref):
            _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
        _signature_bytes(self.signature_base64)

    def to_canonical_bytes(self):
        self.__post_init__()
        return _canonical({f.name: getattr(self, f.name) for f in fields(self)})

    def __repr__(self):
        return "Stage2OwnerApprovalArtifact(<untrusted-data>)"

    __str__ = __repr__


def _unique_object(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
        record[key] = value
    return record


def parse_stage2_owner_approval(raw: bytes) -> Stage2OwnerApprovalArtifact:
    return _parse_approval(raw)


def _parse_approval(raw, expected_issuer=None):
    if type(raw) is not bytes or not 1 <= len(raw) <= MAX_APPROVAL_ARTIFACT_BYTES:
        _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
    record = _call(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT,
                   lambda: json.loads(raw.decode("utf-8", errors="strict"),
                                      object_pairs_hook=_unique_object,
                                      parse_constant=lambda _: _fail(
                                          Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)))
    if (type(record) is not dict or record.keys() != _FIELDS
            or any(type(v) is not str or not v.isascii() for v in record.values())):
        _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
    if _canonical(record) != raw:
        _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
    if record["schema_version"] != APPROVAL_SCHEMA_VERSION:
        _fail(Stage2OwnerVerificationFailure.UNSUPPORTED_SCHEMA)
    if record["signature_algorithm"] != SIGNATURE_ALGORITHM:
        _fail(Stage2OwnerVerificationFailure.UNSUPPORTED_ALGORITHM)
    if not _reference(record["issuer_ref"]):
        _fail(Stage2OwnerVerificationFailure.MALFORMED_ARTIFACT)
    if expected_issuer is not None and record["issuer_ref"] != expected_issuer:
        _fail(Stage2OwnerVerificationFailure.UNKNOWN_ISSUER)
    return Stage2OwnerApprovalArtifact(**record)


class _Win32ApprovalNative:
    """Deferred minimal Win32 facade; tests replace the DLL before construction."""

    def __init__(self):
        if sys.platform != "win32":
            raise OSError("unsupported platform")
        import ctypes
        from ctypes import wintypes

        class AttributeInfo(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]

        class IdentityInfo(ctypes.Structure):
            _fields_ = [("volume", ctypes.c_ulonglong), ("identifier", ctypes.c_ubyte * 16)]

        self._ctypes = ctypes
        self._wintypes = wintypes
        self._attribute_info = AttributeInfo
        self._identity_info = IdentityInfo
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        self._create = dll.CreateFileW
        self._create.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                 wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        self._create.restype = wintypes.HANDLE
        self._type = dll.GetFileType
        self._type.argtypes = (wintypes.HANDLE,)
        self._type.restype = wintypes.DWORD
        self._information = dll.GetFileInformationByHandleEx
        self._information.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
        self._information.restype = wintypes.BOOL
        self._read = dll.ReadFile
        self._read.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                               ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID)
        self._read.restype = wintypes.BOOL
        self._close = dll.CloseHandle
        self._close.argtypes = (wintypes.HANDLE,)
        self._close.restype = wintypes.BOOL

    def open_directory(self, path):
        return self._open(path, 0, _OPEN_REPARSE_POINT | _BACKUP_SEMANTICS)

    def open_artifact(self, path):
        return self._open(path, _GENERIC_READ, _OPEN_REPARSE_POINT)

    def _open(self, path, access, flags):
        handle = self._create(path, access, _FILE_SHARE_READ, None, _OPEN_EXISTING, flags, None)
        if handle is None or handle == self._ctypes.c_void_p(-1).value:
            raise OSError("open failed")
        return handle

    def metadata(self, handle):
        info = self._attribute_info()
        if not self._information(handle, 9, self._ctypes.byref(info), self._ctypes.sizeof(info)):
            raise OSError("metadata failed")
        return int(self._type(handle)), int(info.attributes)

    def directory_identity(self, handle):
        info = self._identity_info()
        if not self._information(handle, 18, self._ctypes.byref(info), self._ctypes.sizeof(info)):
            raise OSError("identity failed")
        return f"win32-fileid-v1:{info.volume:016x}:{bytes(info.identifier).hex()}"

    def read(self, handle, maximum):
        buffer = self._ctypes.create_string_buffer(maximum)
        count = self._wintypes.DWORD()
        if not self._read(handle, buffer, maximum, self._ctypes.byref(count), None):
            raise OSError("read failed")
        if count.value > maximum:
            raise OSError("invalid read count")
        return buffer.raw[:count.value]

    def close(self, handle):
        if not self._close(handle):
            raise OSError("close failed")


def _check_metadata(native, handle, *, directory):
    metadata = _call(Stage2OwnerVerificationFailure.SOURCE_UNAVAILABLE, native.metadata, handle)
    if (type(metadata) is not tuple or len(metadata) != 2
            or any(type(v) is not int for v in metadata)):
        _fail(Stage2OwnerVerificationFailure.SOURCE_TYPE_REJECTED)
    kind, attributes = metadata
    if (kind != _DISK or attributes & _REPARSE_POINT
            or bool(attributes & _DIRECTORY) != directory):
        _fail(Stage2OwnerVerificationFailure.SOURCE_TYPE_REJECTED)


def _read_bounded(native, handle):
    chunks = []
    size = 0
    while True:
        maximum = min(MAX_APPROVAL_ARTIFACT_BYTES, MAX_APPROVAL_ARTIFACT_BYTES + 1 - size)
        chunk = _call(Stage2OwnerVerificationFailure.SOURCE_READ_FAILED, native.read, handle, maximum)
        if type(chunk) is not bytes or len(chunk) > maximum:
            _fail(Stage2OwnerVerificationFailure.SOURCE_READ_FAILED)
        if not chunk:
            return b"".join(chunks)
        size += len(chunk)
        if size > MAX_APPROVAL_ARTIFACT_BYTES:
            _fail(Stage2OwnerVerificationFailure.SOURCE_TOO_LARGE)
        chunks.append(chunk)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2ExactOwnerApprovalSource:
    trust_root: OwnerTrustRootConfiguration

    def __post_init__(self):
        _configuration(self.trust_root)

    def __repr__(self):
        return "Stage2ExactOwnerApprovalSource(<exact-read-only>)"

    __str__ = __repr__

    def read_exact(self, owner_approval_ref: str) -> bytes:
        if type(self) is not Stage2ExactOwnerApprovalSource:
            _fail(Stage2OwnerVerificationFailure.INVALID_CONFIGURATION)
        trust_root = self.trust_root
        _configuration(trust_root)
        _approval_reference(owner_approval_ref)
        directory_path = trust_root.approval_source_absolute_path
        artifact_path = directory_path + "\\" + owner_approval_ref + ".json"
        if len(artifact_path) > MAX_APPROVAL_PATH_CHARACTERS:
            _fail(Stage2OwnerVerificationFailure.INVALID_CONFIGURATION)
        native = _call(Stage2OwnerVerificationFailure.SOURCE_UNAVAILABLE, _Win32ApprovalNative)
        directory = _call(Stage2OwnerVerificationFailure.SOURCE_UNAVAILABLE,
                          native.open_directory, directory_path)
        artifact = None
        failure = None
        raw = None
        try:
            _check_metadata(native, directory, directory=True)
            identity = _call(Stage2OwnerVerificationFailure.SOURCE_UNAVAILABLE,
                             native.directory_identity, directory)
            if type(identity) is not str or identity != trust_root.approval_source_directory_identity:
                _fail(Stage2OwnerVerificationFailure.SOURCE_IDENTITY_MISMATCH)
            artifact = _call(Stage2OwnerVerificationFailure.SOURCE_UNAVAILABLE,
                             native.open_artifact, artifact_path)
            _check_metadata(native, artifact, directory=False)
            raw = _read_bounded(native, artifact)
        except Stage2OwnerVerificationError as error:
            failure = error.code
        finally:
            for handle in (artifact, directory):
                if handle is not None:
                    try:
                        native.close(handle)
                    except Exception:
                        failure = failure or Stage2OwnerVerificationFailure.SOURCE_CLOSE_FAILED
        if failure is not None:
            _fail(failure)
        return raw


@dataclass(frozen=True, slots=True, init=False, repr=False)
class Stage2VerifiedOwnerApproval:
    """Verifier-issued audit facts, not a transferable execution grant."""

    schema_version: str
    artifact_sha256: str
    approval_ref: str
    verified_issuer_ref: str
    approval_source_id: str
    public_key_fingerprint: str
    payload_sha256: str
    verified: bool
    execution_authorized: bool

    def __new__(cls, *args, **kwargs):
        raise TypeError("Owner verification results are verifier-issued only")

    def __init__(self, *args, **kwargs):
        raise TypeError("Owner verification results are verifier-issued only")

    def __init_subclass__(cls, **kwargs):
        raise TypeError("Owner verification results cannot be subclassed")

    def __copy__(self):
        raise TypeError("Owner verification results cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("Owner verification results cannot be copied")

    def __getstate__(self):
        raise TypeError("Owner verification results cannot be reconstructed")

    def __reduce__(self):
        raise TypeError("Owner verification results cannot be reconstructed")

    def __reduce_ex__(self, protocol):
        raise TypeError("Owner verification results cannot be reconstructed")

    def __repr__(self):
        return "Stage2VerifiedOwnerApproval(<verified-not-execution-authority>)"

    __str__ = __repr__


def _verification_key(raw):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    return Ed25519PublicKey.from_public_bytes(raw)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2OwnerVerifier:
    trust_root: OwnerTrustRootConfiguration

    def __post_init__(self):
        _configuration(self.trust_root)

    def __repr__(self):
        return "Stage2OwnerVerifier(<acquired-authority-only>)"

    __str__ = __repr__

    def verify(self, envelope: Stage2AuthorizationEnvelope) -> Stage2VerifiedOwnerApproval:
        if type(self) is not Stage2OwnerVerifier:
            _fail(Stage2OwnerVerificationFailure.INVALID_CONFIGURATION)
        trust_root = self.trust_root
        _configuration(trust_root)
        if type(envelope) is not Stage2AuthorizationEnvelope:
            _fail(Stage2OwnerVerificationFailure.INVALID_ENVELOPE)
        _call(Stage2OwnerVerificationFailure.INVALID_ENVELOPE, envelope.__post_init__)
        _approval_reference(envelope.authorization_ref)
        raw = Stage2ExactOwnerApprovalSource(trust_root).read_exact(envelope.authorization_ref)
        artifact = _parse_approval(raw, trust_root.issuer_ref)
        signature = _signature_bytes(artifact.signature_base64)
        key = _call(Stage2OwnerVerificationFailure.CRYPTO_UNAVAILABLE,
                    _verification_key, trust_root.ed25519_public_key)
        payload = _call(Stage2OwnerVerificationFailure.INVALID_ENVELOPE,
                        owner_verification_payload, envelope)
        _call(Stage2OwnerVerificationFailure.SIGNATURE_INVALID, key.verify, signature, payload)
        result = object.__new__(Stage2VerifiedOwnerApproval)
        for name, value in (
            ("schema_version", APPROVAL_SCHEMA_VERSION),
            ("artifact_sha256", hashlib.sha256(raw).hexdigest()),
            ("approval_ref", envelope.authorization_ref),
            ("verified_issuer_ref", trust_root.issuer_ref),
            ("approval_source_id", trust_root.approval_source_id),
            ("public_key_fingerprint", trust_root.public_key_sha256_fingerprint),
            ("payload_sha256", hashlib.sha256(payload).hexdigest()),
            ("verified", True),
            ("execution_authorized", False),
        ):
            object.__setattr__(result, name, value)
        return result


__all__ = (
    "APPROVAL_SCHEMA_VERSION", "SIGNATURE_ALGORITHM", "MAX_APPROVAL_ARTIFACT_BYTES",
    "MAX_APPROVAL_PATH_CHARACTERS", "Stage2OwnerVerificationFailure",
    "Stage2OwnerVerificationError", "Stage2OwnerApprovalArtifact",
    "parse_stage2_owner_approval", "Stage2ExactOwnerApprovalSource",
    "Stage2OwnerVerifier", "Stage2VerifiedOwnerApproval",
)
