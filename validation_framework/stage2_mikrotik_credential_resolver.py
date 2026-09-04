"""Immutable offline resolver for one future MikroTik credential binding.

The resolver maps one synthetic logical credential reference to one fixed,
non-secret backend binding.  It does not retrieve a credential, access a
credential store, read files or environment variables, or open a connection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Final

from validation_framework.stage2_vrrp_readonly_contract import MAX_REFERENCE_LENGTH


STAGE2_FIXED_CREDENTIAL_REF: Final = "credential.mikrotik.lab01"
STAGE2_CREDENTIAL_BACKEND_KIND: Final = "WINDOWS_CREDENTIAL_MANAGER"
STAGE2_CREDENTIAL_LOCATOR_REF: Final = "locator.stage2.mikrotik.lab01.readonly"

_REFERENCE_PATTERN: Final = re.compile(
    r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$"
)
_FORBIDDEN_CREDENTIAL_REFERENCE_TOKENS: Final = frozenset(
    {
        "apikey",
        "password",
        "passphrase",
        "passwd",
        "privatekey",
        "pwd",
        "secret",
        "token",
        "username",
    }
)


class Stage2CredentialResolverFailure(Enum):
    """Bounded resolver failures that retain no rejected input."""

    INVALID_CREDENTIAL_REFERENCE = "INVALID_CREDENTIAL_REFERENCE"
    UNKNOWN_CREDENTIAL = "UNKNOWN_CREDENTIAL"
    INVALID_RESOLVER_CONFIGURATION = "INVALID_RESOLVER_CONFIGURATION"


class Stage2CredentialResolverError(ValueError):
    """Sanitized fail-closed error for the offline resolver."""

    def __init__(self, code: Stage2CredentialResolverFailure) -> None:
        if type(code) is not Stage2CredentialResolverFailure:
            raise TypeError("credential resolver error requires a bounded category")
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2CredentialBinding:
    """One immutable, non-secret declaration for a future trusted backend."""

    credential_ref: str
    backend_kind: str
    locator_ref: str = field(repr=False)

    def __post_init__(self) -> None:
        if (
            type(self.credential_ref) is not str
            or self.credential_ref != STAGE2_FIXED_CREDENTIAL_REF
            or type(self.backend_kind) is not str
            or self.backend_kind != STAGE2_CREDENTIAL_BACKEND_KIND
            or type(self.locator_ref) is not str
            or self.locator_ref != STAGE2_CREDENTIAL_LOCATOR_REF
        ):
            _fail(Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2CredentialBinding(<fixed-non-secret-binding>)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True, repr=False)
class Stage2FixedCredentialResolver:
    """Resolve one exact credential reference with no alias or fallback."""

    _binding: Stage2CredentialBinding = field(repr=False)

    def __post_init__(self) -> None:
        if type(self._binding) is not Stage2CredentialBinding:
            _fail(Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2FixedCredentialResolver(<one-fixed-binding>)"

    __str__ = __repr__

    def resolve(self, credential_ref: object) -> Stage2CredentialBinding:
        """Return a binding only for the exact fixed logical reference."""

        if not _is_credential_reference(credential_ref):
            _fail(Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE)
        if credential_ref != STAGE2_FIXED_CREDENTIAL_REF:
            _fail(Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL)
        return self._binding


def build_stage2_fixed_credential_resolver() -> Stage2FixedCredentialResolver:
    """Build the fixed resolver without configuration, discovery, or I/O."""

    binding = Stage2CredentialBinding(
        credential_ref=STAGE2_FIXED_CREDENTIAL_REF,
        backend_kind=STAGE2_CREDENTIAL_BACKEND_KIND,
        locator_ref=STAGE2_CREDENTIAL_LOCATOR_REF,
    )
    return Stage2FixedCredentialResolver(binding)


def _is_credential_reference(value: object) -> bool:
    if (
        type(value) is not str
        or not 1 <= len(value) <= MAX_REFERENCE_LENGTH
        or not value.isascii()
        or not value.startswith("credential.")
        or _REFERENCE_PATTERN.fullmatch(value) is None
    ):
        return False
    compacted = re.sub(r"[._-]+", "", value)
    return not any(
        token in compacted for token in _FORBIDDEN_CREDENTIAL_REFERENCE_TOKENS
    )


def _fail(code: Stage2CredentialResolverFailure) -> None:
    raise Stage2CredentialResolverError(code)


__all__ = (
    "STAGE2_CREDENTIAL_BACKEND_KIND",
    "STAGE2_CREDENTIAL_LOCATOR_REF",
    "STAGE2_FIXED_CREDENTIAL_REF",
    "Stage2CredentialBinding",
    "Stage2CredentialResolverError",
    "Stage2CredentialResolverFailure",
    "Stage2FixedCredentialResolver",
    "build_stage2_fixed_credential_resolver",
)
