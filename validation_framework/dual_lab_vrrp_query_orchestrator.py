"""DL-02 fixed synchronous orchestration; configuration is not live authority.

Trusted callers supply the accepted persistent configurations. None represents
an unavailable startup binding; this module cannot attest provider provenance.
Both bundles are preflighted before any call. A local rejection skips only that
target; colliding parseable authorization identities reject the pair. Lab1's outcome
is finalized before Lab2 is invoked. Ordering does not imply simultaneous data.
"""

from dataclasses import dataclass as _dataclass
import time as _time

from validation_framework import dual_lab_vrrp_query_contract as _dual
from validation_framework import stage2_vrrp_readonly_contract as _stage2
from validation_framework import stage2_authorization_envelope_ledger as _authorization
from validation_framework import stage2_mikrotik_credential_resolver as _credentials
from validation_framework.stage2_trusted_runtime_composition import (
    Stage2TrustedRuntimeConfiguration as _Configuration,
    _configuration_values,
)
from validation_framework.stage2_vrrp_readonly_live_entrypoint import (
    Stage2VrrpLiveEntrypointError as _EntrypointError,
    Stage2VrrpLiveEntrypointFailure as _EntrypointFailure,
    run_stage2_vrrp_live_once as _invoke_once,
)


_LAB1 = "target.mikrotik.lab01"
_LAB2 = "target.mikrotik.lab02"
_F = _dual.FailureCategory


@_dataclass(frozen=True, slots=True, repr=False)
class DualLabTargetBundle:
    """Three inert inputs; malformed inputs become target-local preflight errors."""

    request_bytes: bytes
    envelope_bytes: bytes
    trusted_configuration: _Configuration | None

    def __repr__(self):
        return "DualLabTargetBundle(<trusted-caller-inputs-redacted>)"

    __str__ = __repr__


def _utc_now():
    return _time.time_ns() // 1_000_000_000


def _preflight(bundle, target_ref):
    """Return eligible inputs, local failure, and independently retained identity.

    Bundle/request errors precede configuration errors, which precede envelope
    errors. None has its dedicated configuration error. Once an envelope safely
    parses, retain it for pair comparison even if local binding/time checks fail.
    This identity grants no execution eligibility and acquires no authority.
    """
    stage = _F.PREFLIGHT_TARGET_BUNDLE_INVALID
    envelope = None
    try:
        if type(bundle) is not DualLabTargetBundle:
            return None, stage, envelope
        request_bytes, envelope_bytes = bundle.request_bytes, bundle.envelope_bytes
        request = _stage2.parse_stage2_vrrp_request_canonical_json(request_bytes)
        if request.target_ref != target_ref:
            return None, stage, envelope
        binding = _credentials.build_stage2_fixed_credential_resolver().resolve_for_target(
            request.target_ref, request.credential_ref)
        if bundle.trusted_configuration is None:
            return None, _F.PREFLIGHT_STARTUP_BINDING_UNAVAILABLE, envelope
        # Reuse S2-RO-10's pure capture/validation, including every nested record.
        # It performs no asset acquisition and avoids a second configuration schema.
        configuration = _Configuration(*_configuration_values(bundle.trusted_configuration))
        endpoint = configuration.target_registry.lookup(target_ref)
        if (configuration.known_host_configuration.expected_endpoint != endpoint
                or configuration.credential_configuration.locator_ref != binding.locator_ref):
            return None, stage, envelope
        stage = _F.PREFLIGHT_AUTHORIZATION_INVALID
        envelope = _authorization.parse_stage2_authorization_envelope(envelope_bytes)
        _authorization.validate_stage2_authorization_binding(
            envelope, request, configuration.target_registry, binding, now=_utc_now())
        return (request_bytes, envelope_bytes, configuration, request, envelope), None, envelope
    except Exception:
        pass
    return None, stage, envelope


def _failure(target_ref, category):
    return _dual.TargetFailure("FAILURE", target_ref, category)


def _target_result(target_ref, captured, preflight_failure):
    if preflight_failure is not None:
        return _failure(target_ref, preflight_failure)
    request_bytes, envelope_bytes, configuration, request, _ = captured
    candidate = None
    failure = None
    try:
        candidate = _invoke_once(request_bytes, envelope_bytes, configuration)
    except _EntrypointError as error:
        failure = _F.INTERNAL_FAILURE
        if type(error) is _EntrypointError and type(getattr(error, "code", None)) is _EntrypointFailure:
            failure = _F(error.code.value)
    except Exception:
        failure = _F.INTERNAL_FAILURE
    if failure is not None:
        return _failure(target_ref, failure)
    try:
        evidence = _stage2.parse_stage2_vrrp_evidence_canonical_json(candidate)
        evidence = _stage2.parse_stage2_vrrp_evidence_canonical_json(evidence.to_canonical_bytes())
        if (evidence.target_ref != target_ref
                or evidence.operation_id != request.operation_id
                or evidence.command_policy_version != _stage2.VRRP_COMMAND_POLICY_VERSION
                or evidence.run_id != request.run_id
                or evidence.authorization_ref != request.authorization_ref):
            return _failure(target_ref, _F.CANONICAL_EVIDENCE_VALIDATION_FAILED)
        return _dual.TargetSuccess("SUCCESS", target_ref, evidence)
    except Exception:
        pass
    return _failure(target_ref, _F.CANONICAL_EVIDENCE_VALIDATION_FAILED)


def _run(query, lab1, lab2):
    try:
        if type(query) is not _dual.DualLabVrrpQuery:
            return None
        query = _dual.parse_query_canonical_json(query.to_canonical_bytes())
        first, first_failure, first_identity = _preflight(lab1, _LAB1)
        second, second_failure, second_identity = _preflight(lab2, _LAB2)
        if first_identity is not None and second_identity is not None:
            if (first_identity.authorization_ref == second_identity.authorization_ref
                    or first_identity.authorization_id == second_identity.authorization_id):
                first_failure = second_failure = _F.PREFLIGHT_AUTHORIZATION_NOT_DISTINCT
        first_result = _target_result(_LAB1, first, first_failure)
        second_result = _target_result(_LAB2, second, second_failure)
        aggregate = _dual.DualLabVrrpAggregate(
            **query.to_dict(), lab1=first_result, lab2=second_result)
        return _dual.parse_aggregate_canonical_json(aggregate.to_canonical_bytes())
    except Exception:
        # No child traceback, input data or partial aggregate crosses this boundary.
        pass
    return None


def run_dual_lab_vrrp_query(
    query: _dual.DualLabVrrpQuery,
    lab1: DualLabTargetBundle,
    lab2: DualLabTargetBundle,
) -> _dual.DualLabVrrpAggregate:
    """Return the canonical fixed-pair aggregate or a sanitized contract error.

    At most one synchronous S2-RO-11 invocation per eligible target, without retry.
    The private binding is a test seam, never a public execution override. Input
    reference release is not memory zeroization or isolation from trusted callers.
    """
    result = _run(query, lab1, lab2)
    query = lab1 = lab2 = None
    if result is None:
        try:
            raise _dual.DualLabContractError() from None
        except _dual.DualLabContractError as error:
            error.__context__ = None
            raise
    return result


__all__ = ("DualLabTargetBundle", "run_dual_lab_vrrp_query")
