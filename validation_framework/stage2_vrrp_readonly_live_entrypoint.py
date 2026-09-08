"""One trusted-caller invocation; implementation does not authorize a live run.

Startup provisioning is external. S2-RO-10 owns all authorization, acquisition
and transport. This boundary returns canonical evidence without process I/O.
"""

from enum import Enum as _Enum

from validation_framework import stage2_vrrp_readonly_contract as _contract
from validation_framework.stage2_authorization_envelope_ledger import (
    MAX_CANONICAL_ENVELOPE_BYTES as _MAX_ENVELOPE_BYTES,
)
from validation_framework.stage2_trusted_runtime_composition import (
    Stage2TrustedRuntimeConfiguration as _Configuration,
    Stage2TrustedRuntimeError as _RuntimeError,
    Stage2TrustedRuntimeFailure as _RuntimeFailure,
    execute_stage2_vrrp_trusted_runtime as _execute,
)


class Stage2VrrpLiveEntrypointFailure(_Enum):
    INVALID_REQUEST_INPUT = "INVALID_REQUEST_INPUT"
    INVALID_AUTHORIZATION_INPUT = "INVALID_AUTHORIZATION_INPUT"
    INVALID_TRUSTED_CONFIGURATION = "INVALID_TRUSTED_CONFIGURATION"
    TRUSTED_RUNTIME_FAILED = "TRUSTED_RUNTIME_FAILED"
    OUTPUT_RENDER_FAILED = "OUTPUT_RENDER_FAILED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"


_F = Stage2VrrpLiveEntrypointFailure


class Stage2VrrpLiveEntrypointError(ValueError):
    """Only a bounded category; no child detail or authority-bearing data."""

    def __init__(self, code: Stage2VrrpLiveEntrypointFailure) -> None:
        if type(code) is not _F:
            raise TypeError("bounded entrypoint category required")
        self.code = code
        super().__init__(code.value)


def _raise_sanitized(code):
    try:
        raise Stage2VrrpLiveEntrypointError(code) from None
    except Stage2VrrpLiveEntrypointError as error:
        # Discard even an exception active in the trusted caller.
        error.__context__ = None
        raise


def _invoke(request_bytes, authorization_envelope_bytes, trusted_configuration):
    request = evidence = output = None
    try:
        if (type(request_bytes) is not bytes
                or not 1 <= len(request_bytes) <= _contract.MAX_REQUEST_CANONICAL_BYTES):
            return None, _F.INVALID_REQUEST_INPUT
        try:
            request = _contract.parse_stage2_vrrp_request_canonical_json(request_bytes)
        except _contract.Stage2VrrpContractError:
            return None, _F.INVALID_REQUEST_INPUT
        if (type(authorization_envelope_bytes) is not bytes
                or not 1 <= len(authorization_envelope_bytes) <= _MAX_ENVELOPE_BYTES):
            return None, _F.INVALID_AUTHORIZATION_INPUT
        if type(trusted_configuration) is not _Configuration:
            return None, _F.INVALID_TRUSTED_CONFIGURATION
        try:
            evidence = _execute(request, authorization_envelope_bytes, trusted_configuration)
        except _RuntimeError as error:
            if type(error) is not _RuntimeError or type(getattr(error, "code", None)) is not _RuntimeFailure:
                return None, _F.INTERNAL_FAILURE
            if error.code is _RuntimeFailure.INVALID_REQUEST:
                return None, _F.INVALID_REQUEST_INPUT
            if error.code is _RuntimeFailure.INVALID_TRUSTED_RUNTIME_CONFIGURATION:
                return None, _F.INVALID_TRUSTED_CONFIGURATION
            if error.code is _RuntimeFailure.AUTHORIZATION_ENVELOPE_FAILED:
                return None, _F.INVALID_AUTHORIZATION_INPUT
            return None, _F.TRUSTED_RUNTIME_FAILED
        try:
            if type(evidence) is not _contract.Stage2VrrpObservationEvidence:
                return None, _F.OUTPUT_RENDER_FAILED
            output = evidence.to_canonical_bytes()
            # Reuse the accepted schema to reject malformed exact-type records,
            # including records altered after construction; no second schema.
            _contract.parse_stage2_vrrp_evidence_canonical_json(output)
        except Exception:
            return None, _F.OUTPUT_RENDER_FAILED
        return output, None
    except Exception:
        return None, _F.INTERNAL_FAILURE
    finally:
        request_bytes = authorization_envelope_bytes = trusted_configuration = None
        request = evidence = output = None


def run_stage2_vrrp_live_once(
    request_bytes: bytes,
    authorization_envelope_bytes: bytes,
    trusted_configuration: _Configuration,
) -> bytes:
    """Return canonical S2-RO-01 bytes or one sanitized boundary error.

    Zero calls on framing rejection, otherwise at most one S2-RO-10 call.
    Reference release is not memory zeroization or isolation from the caller.
    """
    result, failure = _invoke(request_bytes, authorization_envelope_bytes, trusted_configuration)
    request_bytes = authorization_envelope_bytes = trusted_configuration = None
    if failure is not None:
        _raise_sanitized(failure)
    return result


__all__ = (
    "Stage2VrrpLiveEntrypointFailure",
    "Stage2VrrpLiveEntrypointError",
    "run_stage2_vrrp_live_once",
)
