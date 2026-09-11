"""Immutable offline credential bindings for exactly Lab1 and Lab2.

The target-aware resolver checks two fixed target/credential pairs. The legacy
credential-only API remains Lab1-only. It does not retrieve a credential, access a
credential store, read files or environment variables, or open a connection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Final

from validation_framework.stage2_vrrp_readonly_contract import MAX_REFERENCE_LENGTH
from validation_framework.stage2_mikrotik_target_registry import (
    STAGE2_FIXED_TARGET_REF,
    STAGE2_SECOND_TARGET_REF,
)


STAGE2_FIXED_CREDENTIAL_REF: Final = "credential.mikrotik.lab01"
STAGE2_CREDENTIAL_BACKEND_KIND: Final = "WINDOWS_CREDENTIAL_MANAGER"
STAGE2_CREDENTIAL_LOCATOR_REF: Final = "locator.stage2.mikrotik.lab01.readonly"
STAGE2_SECOND_CREDENTIAL_REF: Final = "credential.mikrotik.lab02"
STAGE2_SECOND_CREDENTIAL_LOCATOR_REF: Final = "locator.stage2.mikrotik.lab02.readonly"

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
    INVALID_TARGET_REFERENCE = "INVALID_TARGET_REFERENCE"
    UNKNOWN_TARGET = "UNKNOWN_TARGET"
    TARGET_CREDENTIAL_MISMATCH = "TARGET_CREDENTIAL_MISMATCH"
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
            or type(self.backend_kind) is not str
            or self.backend_kind != STAGE2_CREDENTIAL_BACKEND_KIND
            or type(self.locator_ref) is not str
            or (self.credential_ref, self.locator_ref) not in (
                (STAGE2_FIXED_CREDENTIAL_REF, STAGE2_CREDENTIAL_LOCATOR_REF),
                (STAGE2_SECOND_CREDENTIAL_REF, STAGE2_SECOND_CREDENTIAL_LOCATOR_REF),
            )
        ):
            _fail(Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2CredentialBinding(<fixed-non-secret-binding>)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True, repr=False)
class Stage2FixedCredentialResolver:
    """Two exact target-bound identities, with a compatible Lab1-only API."""

    _binding: Stage2CredentialBinding = field(repr=False)
    _lab2_binding: Stage2CredentialBinding = field(
        init=False,
        repr=False,
        default_factory=lambda: Stage2CredentialBinding(
            STAGE2_SECOND_CREDENTIAL_REF,
            STAGE2_CREDENTIAL_BACKEND_KIND,
            STAGE2_SECOND_CREDENTIAL_LOCATOR_REF,
        ),
    )

    def __post_init__(self) -> None:
        if type(self._binding) is not Stage2CredentialBinding:
            _fail(Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION)
        self._binding.__post_init__()
        if self._binding.credential_ref != STAGE2_FIXED_CREDENTIAL_REF:
            _fail(Stage2CredentialResolverFailure.INVALID_RESOLVER_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2FixedCredentialResolver(<two-fixed-bindings>)"

    __str__ = __repr__

    def resolve(self, credential_ref: object) -> Stage2CredentialBinding:
        """Legacy Lab1-only API; not a target/credential-pair validator."""

        if not _is_credential_reference(credential_ref):
            _fail(Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE)
        if credential_ref != STAGE2_FIXED_CREDENTIAL_REF:
            _fail(Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL)
        return self._binding

    def resolve_for_target(
        self, target_ref: object, credential_ref: object
    ) -> Stage2CredentialBinding:
        """Validate an exact pair; neither argument can override trusted identity.

        Both references are mandatory. This does not authorize a backend read
        or prove the existence of a credential record or target endpoint.
        """

        if not _is_target_reference(target_ref):
            _fail(Stage2CredentialResolverFailure.INVALID_TARGET_REFERENCE)
        if target_ref == STAGE2_FIXED_TARGET_REF:
            binding = self._binding
        elif target_ref == STAGE2_SECOND_TARGET_REF:
            binding = self._lab2_binding
        else:
            _fail(Stage2CredentialResolverFailure.UNKNOWN_TARGET)
        if not _is_credential_reference(credential_ref):
            _fail(Stage2CredentialResolverFailure.INVALID_CREDENTIAL_REFERENCE)
        if credential_ref not in (
            STAGE2_FIXED_CREDENTIAL_REF, STAGE2_SECOND_CREDENTIAL_REF
        ):
            _fail(Stage2CredentialResolverFailure.UNKNOWN_CREDENTIAL)
        if credential_ref != binding.credential_ref:
            _fail(Stage2CredentialResolverFailure.TARGET_CREDENTIAL_MISMATCH)
        return binding


def build_stage2_fixed_credential_resolver() -> Stage2FixedCredentialResolver:
    """Build the fixed pair without configuration, discovery, or I/O."""

    binding = Stage2CredentialBinding(
        credential_ref=STAGE2_FIXED_CREDENTIAL_REF,
        backend_kind=STAGE2_CREDENTIAL_BACKEND_KIND,
        locator_ref=STAGE2_CREDENTIAL_LOCATOR_REF,
    )
    return Stage2FixedCredentialResolver(binding)


def _is_target_reference(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= MAX_REFERENCE_LENGTH
        and value.isascii()
        and value.startswith("target.")
        and _REFERENCE_PATTERN.fullmatch(value) is not None
    )


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
    "STAGE2_SECOND_CREDENTIAL_REF",
    "STAGE2_SECOND_CREDENTIAL_LOCATOR_REF",
    "Stage2CredentialBinding",
    "Stage2CredentialResolverError",
    "Stage2CredentialResolverFailure",
    "Stage2FixedCredentialResolver",
    "build_stage2_fixed_credential_resolver",
)
