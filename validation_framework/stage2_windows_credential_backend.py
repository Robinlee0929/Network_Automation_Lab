"""Bounded Windows Credential Manager reader for the Stage 2 VRRP lab.

The public operation consumes the exact immutable S2-RO-03 binding and performs
one credential read through an injected narrow API.  A real Windows target is
trusted runtime configuration: it is never accepted by ``read`` and no target
value is committed here.  Windows libraries are loaded only when the real API
adapter is explicitly invoked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import sys
from typing import Final, Protocol

from validation_framework.stage2_mikrotik_credential_resolver import (
    STAGE2_CREDENTIAL_BACKEND_KIND,
    STAGE2_CREDENTIAL_LOCATOR_REF,
    STAGE2_FIXED_CREDENTIAL_REF,
    Stage2CredentialBinding,
)


MAX_WINDOWS_CREDENTIAL_TARGET_LENGTH: Final = 512
MAX_CREDENTIAL_USERNAME_LENGTH: Final = 256
MAX_CREDENTIAL_SECRET_BLOB_LENGTH: Final = 4096

_WINDOWS_GENERIC_CREDENTIAL_TYPE: Final = 1
_WINDOWS_CREDENTIAL_READ_FLAGS: Final = 0
_WINDOWS_ERROR_NOT_FOUND: Final = 1168


class Stage2WindowsCredentialFailure(Enum):
    """Sanitized fail-closed outcomes for the bounded backend."""

    INVALID_BINDING = "INVALID_BINDING"
    UNSUPPORTED_BACKEND = "UNSUPPORTED_BACKEND"
    UNSUPPORTED_LOCATOR = "UNSUPPORTED_LOCATOR"
    INVALID_TRUSTED_CONFIGURATION = "INVALID_TRUSTED_CONFIGURATION"
    UNSUPPORTED_PLATFORM = "UNSUPPORTED_PLATFORM"
    CREDENTIAL_NOT_FOUND = "CREDENTIAL_NOT_FOUND"
    CREDENTIAL_READ_FAILED = "CREDENTIAL_READ_FAILED"
    MALFORMED_CREDENTIAL_RECORD = "MALFORMED_CREDENTIAL_RECORD"
    CREDENTIAL_USERNAME_MISSING = "CREDENTIAL_USERNAME_MISSING"
    CREDENTIAL_USERNAME_TOO_LONG = "CREDENTIAL_USERNAME_TOO_LONG"
    CREDENTIAL_SECRET_INVALID = "CREDENTIAL_SECRET_INVALID"
    CREDENTIAL_SECRET_TOO_LARGE = "CREDENTIAL_SECRET_TOO_LARGE"


class Stage2WindowsCredentialError(ValueError):
    """Public error containing only one bounded category."""

    def __init__(self, code: Stage2WindowsCredentialFailure) -> None:
        if type(code) is not Stage2WindowsCredentialFailure:
            raise TypeError("credential backend error requires a bounded category")
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2TrustedWindowsCredentialConfiguration:
    """One target supplied by a future trusted composition layer outside Git."""

    locator_ref: str
    credential_target: str = field(repr=False)

    def __post_init__(self) -> None:
        if (
            type(self.locator_ref) is not str
            or self.locator_ref != STAGE2_CREDENTIAL_LOCATOR_REF
            or not _is_bounded_windows_target(self.credential_target)
        ):
            _fail(Stage2WindowsCredentialFailure.INVALID_TRUSTED_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2TrustedWindowsCredentialConfiguration(<redacted-target>)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True, repr=False)
class Stage2WindowsCredentialApiRecord:
    """Untrusted narrow result returned by the Windows API boundary."""

    username: object = field(repr=False)
    secret_blob: object = field(repr=False)

    def __repr__(self) -> str:
        return "Stage2WindowsCredentialApiRecord(<redacted>)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True, repr=False)
class Stage2ResolvedCredential:
    """Bounded ephemeral material for a future transport."""

    username: str = field(repr=False)
    secret_blob: bytes = field(repr=False)

    def __repr__(self) -> str:
        return "Stage2ResolvedCredential(<redacted>)"

    __str__ = __repr__


class Stage2WindowsCredentialApi(Protocol):
    """The only OS-facing capability accepted by the backend."""

    def read_exact(
        self, credential_target: str
    ) -> Stage2WindowsCredentialApiRecord | None:
        """Read exactly one generic credential target with fixed flags."""


class _WindowsApiUnsupportedPlatform(RuntimeError):
    pass


class _WindowsApiReadFailure(RuntimeError):
    pass


class _WindowsApiSecretTooLarge(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Stage2CtypesWindowsCredentialApi:
    """Deferred stdlib adapter for the single permitted CredReadW call."""

    def read_exact(
        self, credential_target: str
    ) -> Stage2WindowsCredentialApiRecord | None:
        if sys.platform != "win32":
            raise _WindowsApiUnsupportedPlatform
        return _read_windows_credential_exact(credential_target)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2WindowsCredentialBackend:
    """Use one trusted target to retrieve the exact accepted S2-RO-03 binding."""

    _configuration: Stage2TrustedWindowsCredentialConfiguration = field(
        repr=False
    )
    _windows_api: Stage2WindowsCredentialApi = field(repr=False)

    def __post_init__(self) -> None:
        if (
            type(self._configuration)
            is not Stage2TrustedWindowsCredentialConfiguration
            or not callable(getattr(self._windows_api, "read_exact", None))
        ):
            _fail(Stage2WindowsCredentialFailure.INVALID_TRUSTED_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2WindowsCredentialBackend(<one-redacted-target>)"

    __str__ = __repr__

    def read(self, binding: object) -> Stage2ResolvedCredential:
        """Perform exactly one read after validating the immutable binding."""

        _validate_binding(binding)
        failure: Stage2WindowsCredentialFailure | None = None
        try:
            record = self._windows_api.read_exact(
                self._configuration.credential_target
            )
        except _WindowsApiUnsupportedPlatform:
            failure = Stage2WindowsCredentialFailure.UNSUPPORTED_PLATFORM
        except _WindowsApiSecretTooLarge:
            failure = Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_TOO_LARGE
        except Exception:
            failure = Stage2WindowsCredentialFailure.CREDENTIAL_READ_FAILED

        if failure is not None:
            _fail(failure)

        if record is None:
            _fail(Stage2WindowsCredentialFailure.CREDENTIAL_NOT_FOUND)
        return _validate_record(record)


def build_stage2_windows_credential_backend(
    trusted_configuration: Stage2TrustedWindowsCredentialConfiguration,
    *,
    windows_api: Stage2WindowsCredentialApi | None = None,
) -> Stage2WindowsCredentialBackend:
    """Build from trusted runtime configuration without reading a credential."""

    selected_api: Stage2WindowsCredentialApi
    if windows_api is None:
        selected_api = Stage2CtypesWindowsCredentialApi()
    else:
        selected_api = windows_api
    return Stage2WindowsCredentialBackend(trusted_configuration, selected_api)


def _validate_binding(binding: object) -> None:
    if type(binding) is not Stage2CredentialBinding:
        _fail(Stage2WindowsCredentialFailure.INVALID_BINDING)
    if binding.backend_kind != STAGE2_CREDENTIAL_BACKEND_KIND:
        _fail(Stage2WindowsCredentialFailure.UNSUPPORTED_BACKEND)
    if binding.locator_ref != STAGE2_CREDENTIAL_LOCATOR_REF:
        _fail(Stage2WindowsCredentialFailure.UNSUPPORTED_LOCATOR)
    if binding.credential_ref != STAGE2_FIXED_CREDENTIAL_REF:
        _fail(Stage2WindowsCredentialFailure.INVALID_BINDING)


def _validate_record(record: object) -> Stage2ResolvedCredential:
    if type(record) is not Stage2WindowsCredentialApiRecord:
        _fail(Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD)

    username = record.username
    secret_blob = record.secret_blob
    if type(username) is not str:
        if username is None:
            _fail(Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING)
        _fail(Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD)
    if not username or not username.strip():
        _fail(Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_MISSING)
    if len(username) > MAX_CREDENTIAL_USERNAME_LENGTH:
        _fail(Stage2WindowsCredentialFailure.CREDENTIAL_USERNAME_TOO_LONG)
    if username != username.strip() or any(
        ord(character) < 32 or ord(character) == 127 for character in username
    ):
        _fail(Stage2WindowsCredentialFailure.MALFORMED_CREDENTIAL_RECORD)

    if type(secret_blob) is not bytes or not secret_blob:
        _fail(Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_INVALID)
    if len(secret_blob) > MAX_CREDENTIAL_SECRET_BLOB_LENGTH:
        _fail(Stage2WindowsCredentialFailure.CREDENTIAL_SECRET_TOO_LARGE)

    return Stage2ResolvedCredential(username=username, secret_blob=secret_blob)


def _is_bounded_windows_target(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= MAX_WINDOWS_CREDENTIAL_TARGET_LENGTH
        and value == value.strip()
        and not any(
            ord(character) < 32 or ord(character) == 127 for character in value
        )
    )


def _read_windows_credential_exact(
    credential_target: str,
) -> Stage2WindowsCredentialApiRecord | None:
    """Invoke only CredReadW/CredFree, with no discovery or mutation surface."""

    import ctypes
    from ctypes import wintypes

    class _CredentialW(ctypes.Structure):
        _fields_ = (
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        )

    credential_pointer = ctypes.POINTER(_CredentialW)()
    advapi32 = ctypes.WinDLL("Advapi32.dll", use_last_error=True)
    credential_read = advapi32.CredReadW
    credential_read.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.POINTER(_CredentialW)),
    )
    credential_read.restype = wintypes.BOOL
    credential_free = advapi32.CredFree
    credential_free.argtypes = (ctypes.c_void_p,)
    credential_free.restype = None

    succeeded = credential_read(
        credential_target,
        _WINDOWS_GENERIC_CREDENTIAL_TYPE,
        _WINDOWS_CREDENTIAL_READ_FLAGS,
        ctypes.byref(credential_pointer),
    )
    if not succeeded:
        if ctypes.get_last_error() == _WINDOWS_ERROR_NOT_FOUND:
            return None
        raise _WindowsApiReadFailure

    try:
        credential = credential_pointer.contents
        blob_size = int(credential.CredentialBlobSize)
        if blob_size > MAX_CREDENTIAL_SECRET_BLOB_LENGTH:
            raise _WindowsApiSecretTooLarge
        if blob_size and not credential.CredentialBlob:
            raise _WindowsApiReadFailure
        secret_blob = (
            ctypes.string_at(credential.CredentialBlob, blob_size)
            if blob_size
            else b""
        )
        return Stage2WindowsCredentialApiRecord(
            username=credential.UserName,
            secret_blob=secret_blob,
        )
    finally:
        credential_free(credential_pointer)


def _fail(code: Stage2WindowsCredentialFailure) -> None:
    raise Stage2WindowsCredentialError(code)


__all__ = (
    "MAX_CREDENTIAL_SECRET_BLOB_LENGTH",
    "MAX_CREDENTIAL_USERNAME_LENGTH",
    "MAX_WINDOWS_CREDENTIAL_TARGET_LENGTH",
    "Stage2CtypesWindowsCredentialApi",
    "Stage2ResolvedCredential",
    "Stage2TrustedWindowsCredentialConfiguration",
    "Stage2WindowsCredentialApi",
    "Stage2WindowsCredentialApiRecord",
    "Stage2WindowsCredentialBackend",
    "Stage2WindowsCredentialError",
    "Stage2WindowsCredentialFailure",
    "build_stage2_windows_credential_backend",
)
