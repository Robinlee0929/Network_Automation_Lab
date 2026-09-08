"""One trusted VRRP composition; no startup entrypoint or provisioning.

Only separately trusted startup supplies configuration. Testing this library
does not authorize real acquisition or transport. Consumption remains spent
after downstream failure; successful evidence grants no future authority.
"""

from __future__ import annotations

import base64 as _base64
from dataclasses import dataclass as _dataclass, fields as _fields
from enum import Enum as _Enum
import hashlib as _hashlib
import time as _time

from validation_framework import stage2_vrrp_readonly_contract as _contract
from validation_framework import stage2_mikrotik_target_registry as _target
from validation_framework import stage2_mikrotik_credential_resolver as _resolver
from validation_framework import stage2_windows_credential_backend as _windows
from validation_framework import stage2_authorization_envelope_ledger as _authorization
from validation_framework import stage2_live_authorization_owner_trust_root as _root
from validation_framework import stage2_owner_verifier as _owner
from validation_framework import stage2_known_host_snapshot as _host
from validation_framework import stage2_vrrp_readonly_command_policy as _policy
from validation_framework import stage2_vrrp_readonly_parser as _parser
from validation_framework import stage2_pinned_ssh_transport as _transport


class Stage2TrustedRuntimeFailure(_Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_TRUSTED_RUNTIME_CONFIGURATION = "INVALID_TRUSTED_RUNTIME_CONFIGURATION"
    AUTHORIZATION_ENVELOPE_FAILED = "AUTHORIZATION_ENVELOPE_FAILED"
    TARGET_RESOLUTION_FAILED = "TARGET_RESOLUTION_FAILED"
    CREDENTIAL_BINDING_FAILED = "CREDENTIAL_BINDING_FAILED"
    TRUST_ROOT_ACQUISITION_FAILED = "TRUST_ROOT_ACQUISITION_FAILED"
    APPROVAL_ACQUISITION_FAILED = "APPROVAL_ACQUISITION_FAILED"
    OWNER_VERIFICATION_FAILED = "OWNER_VERIFICATION_FAILED"
    REPLAY_REJECTED = "REPLAY_REJECTED"
    KNOWN_HOST_ACQUISITION_FAILED = "KNOWN_HOST_ACQUISITION_FAILED"
    CREDENTIAL_ACQUISITION_FAILED = "CREDENTIAL_ACQUISITION_FAILED"
    COMMAND_POLICY_FAILED = "COMMAND_POLICY_FAILED"
    TRANSPORT_FAILED = "TRANSPORT_FAILED"
    OUTPUT_PARSE_FAILED = "OUTPUT_PARSE_FAILED"
    EVIDENCE_CONSTRUCTION_FAILED = "EVIDENCE_CONSTRUCTION_FAILED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"


_F = Stage2TrustedRuntimeFailure


class Stage2TrustedRuntimeError(ValueError):
    """Only a bounded category, without child exceptions or rejected data."""

    def __init__(self, code: Stage2TrustedRuntimeFailure):
        if type(code) is not Stage2TrustedRuntimeFailure:
            raise TypeError("bounded runtime category required")
        self.code = code
        super().__init__(code.value)


@_dataclass(frozen=True, slots=True, repr=False)
class Stage2TrustedRuntimeConfiguration:
    """Seven trusted-startup inputs; no request authority or public test seam."""

    target_registry: _target.Stage2FixedTargetRegistry
    owner_trust_root_expected_path: str
    owner_trust_root_expected_file_identity: str
    owner_trust_root_expected_file_sha256: str
    replay_ledger_configuration: _authorization.Stage2ReplayLedgerConfiguration
    known_host_configuration: _host.Stage2KnownHostSourceConfiguration
    credential_configuration: _windows.Stage2TrustedWindowsCredentialConfiguration

    def __post_init__(self):
        invalid = False
        try:
            _configuration_values(self)
        except Exception:
            invalid = True
        if invalid:
            _raise_sanitized(_F.INVALID_TRUSTED_RUNTIME_CONFIGURATION)

    def __repr__(self):
        return "Stage2TrustedRuntimeConfiguration(<trusted-startup-redacted>)"

    __str__ = __repr__


def _raise_sanitized(code):
    # Also discard an exception active in the caller, which Python otherwise
    # attaches implicitly even when child handlers have already exited.
    try:
        raise Stage2TrustedRuntimeError(code) from None
    except Stage2TrustedRuntimeError as error:
        error.__context__ = None
        raise


def _require(condition):
    if not condition:
        raise ValueError("invalid handoff")


def _exact(value, kind):
    _require(type(value) is kind)


def _capture(value, kind):
    """Copy validated inert records so caller objects cannot drift mid-call."""
    _exact(value, kind)
    return kind(**{field.name: getattr(value, field.name) for field in _fields(kind)})


def _configuration_values(configuration):
    _exact(configuration, Stage2TrustedRuntimeConfiguration)
    registry = configuration.target_registry
    _exact(registry, _target.Stage2FixedTargetRegistry)
    endpoint = _capture(registry._endpoint, _target.Stage2FixedTargetEndpoint)
    registry = _target.Stage2FixedTargetRegistry(endpoint)
    path = configuration.owner_trust_root_expected_path
    identity = configuration.owner_trust_root_expected_file_identity
    digest = configuration.owner_trust_root_expected_file_sha256
    # The accepted root API has no public inert pin validator. Reuse its pure
    # syntax checks; only its acquisition operation establishes actual trust.
    _require(_root._is_canonical_absolute_path(path))
    _require(type(identity) is str and _root._FILE_IDENTITY_PATTERN.fullmatch(identity))
    _require(_digest(digest))
    ledger = _capture(configuration.replay_ledger_configuration,
                      _authorization.Stage2ReplayLedgerConfiguration)
    host = configuration.known_host_configuration
    _exact(host, _host.Stage2KnownHostSourceConfiguration)
    host = _host.Stage2KnownHostSourceConfiguration(
        host.expected_path, host.expected_file_identity, host.expected_file_sha256,
        _capture(host.expected_endpoint, _target.Stage2FixedTargetEndpoint))
    _require(host.expected_endpoint == endpoint)
    credential = _capture(configuration.credential_configuration,
                          _windows.Stage2TrustedWindowsCredentialConfiguration)
    return registry, path, identity, digest, ledger, host, credential


def _digest(value):
    return type(value) is str and _root._LOWER_SHA256_PATTERN.fullmatch(value) is not None


def _utc_now():
    return _time.time_ns() // 1_000_000_000


def _monotonic_now():
    value = _time.monotonic_ns()
    _exact(value, int)
    _require(value >= 0)
    return value


def _validate_root(root, configuration):
    _exact(root, _root.OwnerTrustRootConfiguration)
    # Acquisition owns parsing and key policy. Reject absent fields or a pin
    # handoff mismatch without re-reading, parsing, or issuing another root.
    for field in _fields(_root.OwnerTrustRootConfiguration):
        _exact(getattr(root, field.name), bytes if field.name == "ed25519_public_key" else str)
    _require(root.schema_version == _root.OWNER_TRUST_ROOT_SCHEMA_VERSION)
    _require(root.trust_root_source_file_identity == configuration.owner_trust_root_expected_file_identity)
    _require(root.trust_root_source_file_sha256 == configuration.owner_trust_root_expected_file_sha256)


def _validate_verification(result, root, envelope):
    _exact(result, _owner.Stage2VerifiedOwnerApproval)
    for field in _fields(_owner.Stage2VerifiedOwnerApproval):
        _exact(getattr(result, field.name), bool if field.name in
               ("verified", "execution_authorized") else str)
    _require(result.schema_version == _owner.APPROVAL_SCHEMA_VERSION
             and result.verified is True and result.execution_authorized is False
             and result.approval_ref == envelope.authorization_ref
             and result.verified_issuer_ref == root.issuer_ref
             and result.approval_source_id == root.approval_source_id
             and result.public_key_fingerprint == root.public_key_sha256_fingerprint
             and _digest(result.artifact_sha256)
             and result.payload_sha256 == _hashlib.sha256(
                 _authorization.owner_verification_payload(envelope)).hexdigest())


def _validate_consumption(result, envelope):
    _exact(result, _authorization.Stage2ConsumptionRecord)
    _authorization.Stage2ConsumptionRecord.__post_init__(result)
    _require(result.authorization_id == envelope.authorization_id
             and result.envelope_sha256 == _hashlib.sha256(envelope.to_canonical_bytes()).hexdigest()
             and envelope.issued_at <= result.consumed_at < envelope.expires_at
             and result.execution_authorized is False)


def _validate_snapshot(snapshot, endpoint, configuration):
    _exact(snapshot, _host.Stage2KnownHostSnapshot)
    for field in _fields(_host.Stage2KnownHostSnapshot):
        kind = {"port": int, "host_key_blob": bytes, "execution_authorized": bool}.get(field.name, str)
        _exact(getattr(snapshot, field.name), kind)
    _require(snapshot.schema_version == "s2-ro-07.known-host.v1"
             and snapshot.execution_authorized is False
             and (snapshot.target_ref, snapshot.address, snapshot.port) ==
                 (endpoint.target_ref, endpoint.address, endpoint.port)
             and snapshot.source_file_identity == configuration.expected_file_identity
             and snapshot.source_artifact_sha256 == configuration.expected_file_sha256
             and snapshot.host_key_algorithm == "ssh-ed25519"
             and len(snapshot.host_key_blob) == 51
             and snapshot.host_key_blob[:19] == b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20")
    digest = _hashlib.sha256(snapshot.host_key_blob).digest()
    _require(snapshot.host_key_sha256 == digest.hex()
             and snapshot.host_key_fingerprint == "SHA256:" +
                 _base64.b64encode(digest).decode("ascii").rstrip("="))


def _validate_credential(credential):
    _exact(credential, _windows.Stage2ResolvedCredential)
    _require(type(credential.username) is str
             and 1 <= len(credential.username) <= _windows.MAX_CREDENTIAL_USERNAME_LENGTH
             and credential.username == credential.username.strip()
             and not any(ord(c) < 32 or ord(c) == 127 for c in credential.username)
             and type(credential.secret_blob) is bytes
             and 1 <= len(credential.secret_blob) <= _windows.MAX_CREDENTIAL_SECRET_BLOB_LENGTH)


def _validate_command(command):
    _exact(command, _policy.Stage2VrrpReadOnlyCommandSpecification)
    expected = ("s2-ro-08.command-policy.v1", _contract.VRRP_OBSERVATION_OPERATION_ID,
                _contract.VRRP_COMMAND_POLICY_VERSION, "/interface vrrp print detail", True, False)
    values = tuple(getattr(command, field.name) for field in
                   _fields(_policy.Stage2VrrpReadOnlyCommandSpecification))
    _require(all(type(a) is type(b) for a, b in zip(values, expected)) and values == expected)


def _validate_transport(result, request, command, snapshot):
    _exact(result, _transport.Stage2PinnedSshCommandResult)
    for field in _fields(_transport.Stage2PinnedSshCommandResult):
        kind = {"stdout_bytes": bytes, "exit_status": int,
                "execution_attempts": int, "execution_authorized": bool}.get(field.name, str)
        _exact(getattr(result, field.name), kind)
    _require(result.schema_version == "s2-ro-09.pinned-ssh-command-result.v1"
             and result.target_ref == request.target_ref
             and result.command_policy_version == command.command_policy_version
             and result.exit_status == 0 and result.execution_attempts == 1
             and result.execution_authorized is False
             and len(result.stdout_bytes) <= _contract.MAX_RAW_OUTPUT_BYTES
             and result.stdout_sha256 == _hashlib.sha256(result.stdout_bytes).hexdigest()
             and result.host_key_fingerprint == snapshot.host_key_fingerprint)


def _run(request, raw_envelope, configuration):
    """Return only evidence/category so no child traceback reaches the API."""
    stage = _F.INVALID_REQUEST
    credential = transport_result = snapshot = root = verified = parsed = None
    try:
        _exact(request, _contract.Stage2VrrpObservationRequest)
        values = request.to_dict()
        _require(all(type(value) is str for name, value in values.items() if name != "read_only"))
        request = _contract.parse_stage2_vrrp_observation_request(values)
        stage = _F.INTERNAL_FAILURE
        started = _monotonic_now()
        stage = _F.INVALID_TRUSTED_RUNTIME_CONFIGURATION
        configuration = Stage2TrustedRuntimeConfiguration(*_configuration_values(configuration))
        stage = _F.AUTHORIZATION_ENVELOPE_FAILED
        envelope = _authorization.parse_stage2_authorization_envelope(raw_envelope)
        stage = _F.TARGET_RESOLUTION_FAILED
        endpoint = _capture(configuration.target_registry.lookup(request.target_ref),
                            _target.Stage2FixedTargetEndpoint)
        stage = _F.CREDENTIAL_BINDING_FAILED
        binding = _capture(_resolver.build_stage2_fixed_credential_resolver().resolve(request.credential_ref),
                           _resolver.Stage2CredentialBinding)
        stage = _F.AUTHORIZATION_ENVELOPE_FAILED
        _authorization.validate_stage2_authorization_binding(
            envelope, request, configuration.target_registry, binding, now=_utc_now())
        stage = _F.TRUST_ROOT_ACQUISITION_FAILED
        root = _root.acquire_owner_trust_root_configuration(
            expected_path=configuration.owner_trust_root_expected_path,
            expected_file_identity=configuration.owner_trust_root_expected_file_identity,
            expected_file_sha256=configuration.owner_trust_root_expected_file_sha256)
        _validate_root(root, configuration)
        stage = _F.OWNER_VERIFICATION_FAILED
        verified = _owner.Stage2OwnerVerifier(root).verify(envelope)
        _validate_verification(verified, root, envelope)
        stage = _F.REPLAY_REJECTED
        consumed = _authorization.Stage2ReplayLedger(configuration.replay_ledger_configuration).consume(
            envelope, request, configuration.target_registry, binding, utc_now=_utc_now)
        _validate_consumption(consumed, envelope)
        stage = _F.KNOWN_HOST_ACQUISITION_FAILED
        snapshot = _host.acquire_stage2_known_host_snapshot(configuration.known_host_configuration)
        _validate_snapshot(snapshot, endpoint, configuration.known_host_configuration)
        stage = _F.AUTHORIZATION_ENVELOPE_FAILED
        _authorization.validate_stage2_authorization_binding(
            envelope, request, configuration.target_registry, binding, now=_utc_now())
        stage = _F.CREDENTIAL_ACQUISITION_FAILED
        try:
            credential = _windows.build_stage2_windows_credential_backend(
                configuration.credential_configuration).read(binding)
            _validate_credential(credential)
            stage = _F.COMMAND_POLICY_FAILED
            command = _policy.resolve_stage2_vrrp_readonly_command(request)
            _validate_command(command)
            stage = _F.AUTHORIZATION_ENVELOPE_FAILED
            _authorization.validate_stage2_authorization_binding(
                envelope, request, configuration.target_registry, binding, now=_utc_now())
            stage = _F.TRANSPORT_FAILED
            transport_result = _transport.execute_stage2_pinned_ssh_command(
                endpoint, credential, snapshot, command)
        finally:
            # Reference release is not zeroization of immutable Python bytes.
            credential = None
        _validate_transport(transport_result, request, command, snapshot)
        stage = _F.OUTPUT_PARSE_FAILED
        parsed = _parser.parse_stage2_vrrp_readonly_output(request, transport_result.stdout_bytes)
        _exact(parsed, _parser.Stage2VrrpParsedOutput)
        _parser.Stage2VrrpParsedOutput.__post_init__(parsed)
        _require(parsed.execution_authorized is False
                 and parsed.raw_output_sha256 == transport_result.stdout_sha256
                 and parsed.raw_output_sha256 == _hashlib.sha256(transport_result.stdout_bytes).hexdigest()
                 and parsed.raw_output_byte_count == len(transport_result.stdout_bytes))
        stage = _F.EVIDENCE_CONSTRUCTION_FAILED
        elapsed = _monotonic_now() - started
        _require(elapsed >= 0)
        duration = max(1, (elapsed + 999_999) // 1_000_000)
        _require(duration <= _contract.MAX_DURATION_MS)
        evidence = _contract.Stage2VrrpObservationEvidence(
            schema_version=request.schema_version, operation_id=request.operation_id,
            run_id=request.run_id, target_ref=request.target_ref,
            authorization_ref=request.authorization_ref,
            command_policy_version=command.command_policy_version,
            attempt_count=1, retry_count=0, duration_ms=duration,
            raw_output_byte_count=parsed.raw_output_byte_count,
            raw_output_sha256=parsed.raw_output_sha256, records=parsed.records)
        evidence.to_canonical_bytes()
        return evidence, None
    except _owner.Stage2OwnerVerificationError as rejected:
        if (stage is _F.OWNER_VERIFICATION_FAILED
                and type(rejected) is _owner.Stage2OwnerVerificationError
                and type(getattr(rejected, "code", None)) is _owner.Stage2OwnerVerificationFailure
                and rejected.code.name.startswith("SOURCE_")):
            stage = _F.APPROVAL_ACQUISITION_FAILED
    except Exception:
        pass
    finally:
        credential = transport_result = snapshot = root = verified = parsed = None
    return None, stage


def execute_stage2_vrrp_trusted_runtime(
    request: _contract.Stage2VrrpObservationRequest,
    authorization_envelope_bytes: bytes,
    trusted_configuration: Stage2TrustedRuntimeConfiguration,
) -> _contract.Stage2VrrpObservationEvidence:
    """Compose one bounded observation; return normalized evidence or category.

    No retries, provisioning, fallback, or transferable authority are provided.
    The internal operation owns acquisition order and discards child tracebacks.
    """
    result, failure = _run(request, authorization_envelope_bytes, trusted_configuration)
    request = authorization_envelope_bytes = trusted_configuration = None
    if failure is not None:
        _raise_sanitized(failure)
    return result


__all__ = (
    "Stage2TrustedRuntimeConfiguration", "Stage2TrustedRuntimeFailure",
    "Stage2TrustedRuntimeError", "execute_stage2_vrrp_trusted_runtime",
)
