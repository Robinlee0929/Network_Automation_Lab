"""Immutable offline registry for one future MikroTik lab endpoint.

Trusted setup may construct one validated endpoint record.  Ordinary requests
can supply only its logical target reference to ``lookup``.  This module does
not load configuration, resolve DNS, access credentials, establish trust, open
a connection, or authorize execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from ipaddress import AddressValueError, IPv4Address
import re
from typing import Final

from validation_framework.stage2_vrrp_readonly_contract import MAX_REFERENCE_LENGTH


STAGE2_FIXED_TARGET_REF: Final = "target.mikrotik.lab01"
STAGE2_FIXED_SSH_PORT: Final = 22
STAGE2_FIXED_TRANSPORT: Final = "SSH"

_TARGET_REFERENCE_PATTERN: Final = re.compile(
    r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$"
)
_ENDPOINT_FIELDS: Final = frozenset(
    {"target_ref", "address", "port", "transport", "declared_lab_only"}
)


class Stage2TargetRegistryFailure(Enum):
    """Protocol-neutral failure categories with no rejected values."""

    INVALID_TARGET_REFERENCE = "INVALID_TARGET_REFERENCE"
    UNKNOWN_TARGET = "UNKNOWN_TARGET"
    INVALID_REGISTRY_CONFIGURATION = "INVALID_REGISTRY_CONFIGURATION"


class Stage2TargetRegistryError(ValueError):
    """Sanitized fail-closed target-registry error."""

    def __init__(self, code: Stage2TargetRegistryFailure) -> None:
        if type(code) is not Stage2TargetRegistryFailure:
            raise TypeError("target registry error requires a bounded category")
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True, repr=False)
class Stage2FixedTargetEndpoint:
    """One credential-free IPv4 endpoint supplied by trusted setup."""

    target_ref: str
    address: str = field(repr=False)
    port: int
    transport: str
    declared_lab_only: bool

    def __post_init__(self) -> None:
        if (
            type(self.target_ref) is not str
            or self.target_ref != STAGE2_FIXED_TARGET_REF
            or not _is_canonical_ipv4_literal(self.address)
            or type(self.port) is not int
            or self.port != STAGE2_FIXED_SSH_PORT
            or type(self.transport) is not str
            or self.transport != STAGE2_FIXED_TRANSPORT
            or self.declared_lab_only is not True
        ):
            _fail(Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2FixedTargetEndpoint(<fixed-lab-endpoint>)"

    __str__ = __repr__


@dataclass(frozen=True, slots=True, repr=False)
class Stage2FixedTargetRegistry:
    """An immutable singleton registry with exact lookup and no fallback."""

    _endpoint: Stage2FixedTargetEndpoint = field(repr=False)

    def __post_init__(self) -> None:
        if type(self._endpoint) is not Stage2FixedTargetEndpoint:
            _fail(Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION)

    def __repr__(self) -> str:
        return "Stage2FixedTargetRegistry(<one-fixed-target>)"

    __str__ = __repr__

    def lookup(self, target_ref: object) -> Stage2FixedTargetEndpoint:
        """Resolve only the exact fixed logical reference."""

        if not _is_target_reference(target_ref):
            _fail(Stage2TargetRegistryFailure.INVALID_TARGET_REFERENCE)
        if target_ref != STAGE2_FIXED_TARGET_REF:
            _fail(Stage2TargetRegistryFailure.UNKNOWN_TARGET)
        return self._endpoint


def parse_stage2_fixed_target_registry(
    raw_data: object,
) -> Stage2FixedTargetRegistry:
    """Freeze one trusted plain record without file, environment, or network I/O.

    This is a trusted setup boundary, not a request parser.  The representation
    is exactly one endpoint record, so duplicate target declarations and target
    collections are structurally unsupported.
    """

    if type(raw_data) is not dict or raw_data.keys() != _ENDPOINT_FIELDS:
        _fail(Stage2TargetRegistryFailure.INVALID_REGISTRY_CONFIGURATION)
    return Stage2FixedTargetRegistry(Stage2FixedTargetEndpoint(**raw_data))


def _is_target_reference(value: object) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= MAX_REFERENCE_LENGTH
        and value.isascii()
        and value.startswith("target.")
        and _TARGET_REFERENCE_PATTERN.fullmatch(value) is not None
    )


def _is_canonical_ipv4_literal(value: object) -> bool:
    if type(value) is not str or not 7 <= len(value) <= 15 or not value.isascii():
        return False
    try:
        parsed = IPv4Address(value)
    except AddressValueError:
        return False
    return str(parsed) == value


def _fail(code: Stage2TargetRegistryFailure) -> None:
    raise Stage2TargetRegistryError(code)


__all__ = (
    "STAGE2_FIXED_SSH_PORT",
    "STAGE2_FIXED_TARGET_REF",
    "STAGE2_FIXED_TRANSPORT",
    "Stage2FixedTargetEndpoint",
    "Stage2FixedTargetRegistry",
    "Stage2TargetRegistryError",
    "Stage2TargetRegistryFailure",
    "parse_stage2_fixed_target_registry",
)
