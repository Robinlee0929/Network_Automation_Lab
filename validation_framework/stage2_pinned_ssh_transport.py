"""One pinned Stage-2 SSH primitive; trusted runtime authorization is separate.

No acquisition, parser, CLI, or runtime composition is provided here. Merely
importing this module performs no network or credential operation.
"""

import base64 as _base64
from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
import hashlib as _hashlib
import hmac as _hmac
import re as _re
import socket as _socket
import threading as _threading
import time as _time
from types import MappingProxyType as _MappingProxyType

import paramiko as _paramiko
from paramiko.kex_gex import KexGexSHA256 as _KexGexSHA256

from validation_framework.stage2_mikrotik_target_registry import (
    Stage2FixedTargetEndpoint as _Endpoint,
)
from validation_framework.stage2_windows_credential_backend import (
    Stage2ResolvedCredential as _Credential,
)
from validation_framework.stage2_known_host_snapshot import (
    Stage2KnownHostSnapshot as _Snapshot,
)
from validation_framework.stage2_vrrp_readonly_command_policy import (
    Stage2VrrpReadOnlyCommandSpecification as _Specification,
)

_KEYS = ("ssh-ed25519",)
_KEX = ("ecdh-sha2-nistp256", "diffie-hellman-group16-sha512",
        "diffie-hellman-group14-sha256", "diffie-hellman-group-exchange-sha256")
_CIPHERS = ("aes256-ctr", "aes192-ctr", "aes128-ctr")
_MACS = ("hmac-sha2-512-etm@openssh.com", "hmac-sha2-256-etm@openssh.com",
         "hmac-sha2-512", "hmac-sha2-256")
_COMMAND = "/interface vrrp print detail"
_POLICY = "policy.stage2.vrrp-readonly.v1"
_MAX_STDOUT = 65536
_BLOB_PREFIX = b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20"


class Stage2PinnedSshTransportFailure(_Enum):
    INVALID_ENDPOINT = "INVALID_ENDPOINT"
    INVALID_CREDENTIAL = "INVALID_CREDENTIAL"
    INVALID_HOST_SNAPSHOT = "INVALID_HOST_SNAPSHOT"
    INVALID_COMMAND_SPECIFICATION = "INVALID_COMMAND_SPECIFICATION"
    ENDPOINT_BINDING_MISMATCH = "ENDPOINT_BINDING_MISMATCH"
    HOST_KEY_ALGORITHM_MISMATCH = "HOST_KEY_ALGORITHM_MISMATCH"
    HOST_KEY_MISMATCH = "HOST_KEY_MISMATCH"
    CONNECT_FAILED = "CONNECT_FAILED"
    CONNECT_TIMEOUT = "CONNECT_TIMEOUT"
    SSH_NEGOTIATION_FAILED = "SSH_NEGOTIATION_FAILED"
    SSH_HOST_VERIFICATION_FAILED = "SSH_HOST_VERIFICATION_FAILED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    CHANNEL_OPEN_FAILED = "CHANNEL_OPEN_FAILED"
    COMMAND_EXEC_FAILED = "COMMAND_EXEC_FAILED"
    COMMAND_TIMEOUT = "COMMAND_TIMEOUT"
    STDERR_PRESENT = "STDERR_PRESENT"
    NONZERO_EXIT_STATUS = "NONZERO_EXIT_STATUS"
    OUTPUT_TOO_LARGE = "OUTPUT_TOO_LARGE"
    OUTPUT_READ_FAILED = "OUTPUT_READ_FAILED"
    CHANNEL_CLOSE_FAILED = "CHANNEL_CLOSE_FAILED"
    TRANSPORT_CLOSE_FAILED = "TRANSPORT_CLOSE_FAILED"
    SOCKET_CLOSE_FAILED = "SOCKET_CLOSE_FAILED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"


_F = Stage2PinnedSshTransportFailure


class Stage2PinnedSshTransportError(ValueError):
    """Public failure contains only one category, without native causes."""

    def __init__(self, code: Stage2PinnedSshTransportFailure):
        if type(code) is not Stage2PinnedSshTransportFailure:
            raise TypeError("bounded transport category required")
        self.code = code
        super().__init__(code.value)


def _fail(code):
    raise Stage2PinnedSshTransportError(code) from None


def _call(code, operation, *args, **kwargs):
    failed = False
    try:
        value = operation(*args, **kwargs)
    except Exception:
        failed = True
    if failed:
        _fail(code)
    return value


class _Stage2GexSHA256(_KexGexSHA256):
    """Enforce the requested group range on the server's actual reply too."""

    min_bits = 2048
    preferred_bits = 2048
    max_bits = 8192

    def _parse_kexdh_gex_group(self, message):
        # Paramiko 3.5.1's parser hardcodes 1024, ignoring min_bits here.
        # Inspect a copy without consuming the original parser's input.
        prime = _paramiko.Message(message.get_remainder()).get_mpint()
        if prime <= 0 or not 2048 <= prime.bit_length() <= 8192:
            raise _paramiko.SSHException("Stage-2 GEX group size rejected")
        return super()._parse_kexdh_gex_group(message)


class _Stage2PinnedTransport(_paramiko.Transport):
    """Pin raw keys and a private GEX implementation without global changes."""

    _kex_info = _MappingProxyType({
        **_paramiko.Transport._kex_info,
        "diffie-hellman-group-exchange-sha256": _Stage2GexSHA256,
    })

    @property
    def preferred_keys(self):
        return ("ssh-ed25519",)


class _SocketOwner:
    """Serialize every physical close, including Paramiko's own close paths."""

    def __init__(self, sock):
        self._socket = sock
        self._lock = _threading.Lock()
        self.attempted = False
        self.failed = False

    def __getattr__(self, name):
        return getattr(self._socket, name)

    def close(self):
        with self._lock:
            if not self.attempted:
                self.attempted = True
                try:
                    self._socket.close()
                except Exception:
                    self.failed = True
            failed = self.failed
        if failed:
            raise OSError("socket cleanup failed") from None


@_dataclass(frozen=True, slots=True, init=False, repr=False)
class Stage2PinnedSshCommandResult:
    """Transport-issued bytes, never Owner/replay/runtime authorization."""

    schema_version: str
    target_ref: str
    command_policy_version: str
    stdout_bytes: bytes
    stdout_sha256: str
    host_key_fingerprint: str
    exit_status: int
    execution_attempts: int
    execution_authorized: bool

    def __new__(cls, *args, **kwargs):
        raise TypeError("transport results are operation-issued only")

    def __init_subclass__(cls, **kwargs):
        raise TypeError("transport results cannot be subclassed")

    def __copy__(self):
        raise TypeError("transport results cannot be copied")

    def __deepcopy__(self, memo):
        raise TypeError("transport results cannot be copied")

    def __reduce_ex__(self, protocol):
        raise TypeError("transport results cannot be reconstructed")

    def __repr__(self):
        return "Stage2PinnedSshCommandResult(<bounded-transport-not-authority>)"

    __str__ = __repr__


def _inputs(endpoint, credential, snapshot, specification):
    for value, kind, code in (
        (endpoint, _Endpoint, _F.INVALID_ENDPOINT),
        (credential, _Credential, _F.INVALID_CREDENTIAL),
        (snapshot, _Snapshot, _F.INVALID_HOST_SNAPSHOT),
        (specification, _Specification, _F.INVALID_COMMAND_SPECIFICATION),
    ):
        if type(value) is not kind:
            _fail(code)
    _call(_F.INVALID_ENDPOINT, _Endpoint.__post_init__, endpoint)
    target = (endpoint.target_ref, endpoint.address, endpoint.port)
    username, secret = _call(_F.INVALID_CREDENTIAL,
                             lambda: (credential.username, credential.secret_blob))
    if (type(username) is not str or not 1 <= len(username) <= 256
            or username != username.strip()
            or any(ord(c) < 32 or ord(c) == 127 for c in username)
            or type(secret) is not bytes or not 1 <= len(secret) <= 4096):
        _fail(_F.INVALID_CREDENTIAL)
    names = ("schema_version", "target_ref", "address", "port",
             "host_key_algorithm", "host_key_blob", "host_key_sha256",
             "host_key_fingerprint", "source_file_identity",
             "source_artifact_sha256", "execution_authorized")
    values = _call(_F.INVALID_HOST_SNAPSHOT,
                   lambda: tuple(getattr(snapshot, name) for name in names))
    schema, ref, address, port, algorithm, blob, digest, fingerprint, identity, source, authority = values
    if (any(type(v) is not str for v in
            (schema, ref, address, algorithm, digest, fingerprint, identity, source))
            or type(port) is not int or type(blob) is not bytes
            or schema != "s2-ro-07.known-host.v1" or authority is not False
            or algorithm != "ssh-ed25519" or len(blob) != 51
            or blob[:19] != _BLOB_PREFIX
            or _re.fullmatch(r"win32-fileid-v1:[0-9a-f]{16}:[0-9a-f]{32}", identity) is None
            or _re.fullmatch(r"[0-9a-f]{64}", source) is None):
        _fail(_F.INVALID_HOST_SNAPSHOT)
    key_digest = _hashlib.sha256(blob).digest()
    expected_fingerprint = "SHA256:" + _base64.b64encode(key_digest).decode("ascii").rstrip("=")
    if digest != key_digest.hex() or fingerprint != expected_fingerprint:
        _fail(_F.INVALID_HOST_SNAPSHOT)
    if (ref, address, port) != target:
        _fail(_F.ENDPOINT_BINDING_MISMATCH)
    expected = ("s2-ro-08.command-policy.v1", "mikrotik.vrrp_status",
                "policy.stage2.vrrp-readonly.v1", "/interface vrrp print detail",
                True, False)
    command_values = _call(_F.INVALID_COMMAND_SPECIFICATION, lambda: (
        specification.schema_version, specification.operation_id,
        specification.command_policy_version, specification.command_text,
        specification.read_only, specification.execution_authorized))
    if (any(type(a) is not type(b) for a, b in zip(command_values, expected))
            or command_values != expected):
        _fail(_F.INVALID_COMMAND_SPECIFICATION)
    return target, username, secret, blob, fingerprint


def _remaining(deadline, code):
    remaining = deadline - _time.monotonic()
    if remaining <= 0:
        _fail(code)
    return remaining


def _wait(event, deadline, code):
    if not event.wait(_remaining(deadline, code)):
        _fail(code)
    _remaining(deadline, code)


def _harden(transport):
    options = transport.get_security_options()
    options.key_types = _KEYS
    options.kex = _KEX
    options.ciphers = _CIPHERS
    options.digests = _MACS
    options.compression = ("none",)
    # This is an effective-policy check, not merely the SecurityOptions input.
    if (type(transport.preferred_keys) is not tuple
            or transport.preferred_keys != ("ssh-ed25519",)):
        raise ValueError("effective key policy rejected")
    if (transport._kex_info.get("diffie-hellman-group-exchange-sha256")
            is not _Stage2GexSHA256):
        raise ValueError("effective GEX implementation rejected")


class _PendingOperation:
    """Externally bound a private initiation without changing Paramiko internals."""

    def __init__(self, operation, deadline=None):
        self.done = _threading.Event()
        self.cancelled = _threading.Event()
        self.failed = False
        self.thread = _threading.Thread(
            target=self._run, args=(operation, deadline), daemon=True)

    def _run(self, operation, deadline):
        try:
            if deadline is not None and (
                    self.cancelled.is_set() or _time.monotonic() >= deadline):
                self.failed = True
            else:
                operation()
        except Exception:
            self.failed = True
        finally:
            self.done.set()


class _ChannelOwner:
    """Own even a channel returned after cancellation of open_session."""

    def __init__(self):
        self._lock = _threading.Lock()
        self.channel = None
        self.close_requested = False
        self.close_attempted = False
        self.close_failed = False

    def acquire(self, transport, deadline):
        channel = transport.open_session(
            timeout=_remaining(deadline, _F.COMMAND_TIMEOUT),
            window_size=2097152, max_packet_size=32768)
        with self._lock:
            self.channel = channel
            cancelled = self.close_requested
        if cancelled:
            self.close()

    def close(self):
        with self._lock:
            self.close_requested = True
            channel = self.channel
            if channel is None or self.close_attempted:
                return
            self.close_attempted = True
        # Never hold the ownership lock over a potentially blocking packet send.
        try:
            channel.close()
        except Exception:
            self.close_failed = True


def _await_operation(pending, deadline, timeout_code, failure_code):
    pending.thread.start()
    _wait(pending.done, deadline, timeout_code)
    if pending.failed:
        _fail(failure_code)


def _cleanup(channel_owner, transport, socket_owner, pending_operations):
    for pending in pending_operations:
        pending.cancelled.set()
    close_operations = []
    # Start in logical channel -> Transport -> socket order. Do not let a
    # blocked close-packet send prevent shutdown of the socket that releases it.
    for resource, code in ((channel_owner, _F.CHANNEL_CLOSE_FAILED),
                           (transport, _F.TRANSPORT_CLOSE_FAILED)):
        if resource is not None:
            pending = _PendingOperation(resource.close)
            close_operations.append((pending, code))
            try:
                pending.thread.start()
                pending.done.wait(0.05)
            except Exception:
                pending.failed = True
    socket_failed = False
    if socket_owner is not None:
        try:
            socket_owner.close()
        except Exception:
            socket_failed = True
        socket_failed = socket_failed or socket_owner.failed
    # One shared cleanup join allowance; it grants no further execution time.
    join_deadline = _time.monotonic() + 1.0
    failures = []
    for pending, code in close_operations + [
            (pending, _F.TRANSPORT_CLOSE_FAILED) for pending in pending_operations]:
        if pending.thread.ident is not None:
            pending.thread.join(max(0.0, join_deadline - _time.monotonic()))
            if pending.thread.is_alive():
                failures.append(code)
        if (pending, code) in close_operations and pending.failed:
            failures.append(code)
    if channel_owner is not None and channel_owner.close_failed:
        failures.append(_F.CHANNEL_CLOSE_FAILED)
    if socket_failed:
        failures.append(_F.SOCKET_CLOSE_FAILED)
    for code in (_F.CHANNEL_CLOSE_FAILED, _F.TRANSPORT_CLOSE_FAILED,
                 _F.SOCKET_CLOSE_FAILED):
        if code in failures:
            return code
    return None


def _collect(channel, deadline):
    output = bytearray()
    stdout_eof = stderr_eof = False
    channel.settimeout(0.0)
    while True:
        _remaining(deadline, _F.COMMAND_TIMEOUT)
        progressed = False
        # Nonblocking recv also distinguishes EOF from a temporarily empty buffer.
        if not stderr_eof:
            try:
                error_byte = channel.recv_stderr(1)
            except _socket.timeout:
                error_byte = None
            if error_byte is not None:
                if type(error_byte) is not bytes or len(error_byte) > 1:
                    _fail(_F.OUTPUT_READ_FAILED)
                if error_byte:
                    _fail(_F.STDERR_PRESENT)
                stderr_eof = True
        if not stdout_eof:
            maximum = min(4096, _MAX_STDOUT + 1 - len(output))
            try:
                chunk = channel.recv(maximum)
            except _socket.timeout:
                chunk = None
            if chunk is not None:
                if type(chunk) is not bytes or len(chunk) > maximum:
                    _fail(_F.OUTPUT_READ_FAILED)
                if not chunk:
                    stdout_eof = True
                else:
                    output.extend(chunk)
                    progressed = True
                    if len(output) > _MAX_STDOUT:
                        _fail(_F.OUTPUT_TOO_LARGE)
        if stdout_eof and stderr_eof and channel.exit_status_ready():
            _remaining(deadline, _F.COMMAND_TIMEOUT)
            status = channel.recv_exit_status()
            _remaining(deadline, _F.COMMAND_TIMEOUT)
            if type(status) is not int or status != 0:
                _fail(_F.NONZERO_EXIT_STATUS)
            return bytes(output)
        if not progressed:
            _time.sleep(min(0.01, _remaining(deadline, _F.COMMAND_TIMEOUT)))


def execute_stage2_pinned_ssh_command(
    endpoint: _Endpoint,
    credential: _Credential,
    known_host_snapshot: _Snapshot,
    command_specification: _Specification,
) -> Stage2PinnedSshCommandResult:
    """Execute the fixed primitive once; future trusted composition owns permission."""
    target, username, secret, blob, fingerprint = _inputs(
        endpoint, credential, known_host_snapshot, command_specification)
    owner = transport = channel_owner = None
    pending_operations = []
    failure = None
    phase = _F.CONNECT_FAILED
    deadline = _time.monotonic() + 15.0
    timeout_code = _F.CONNECT_TIMEOUT
    try:
        owner = _SocketOwner(_socket.socket(_socket.AF_INET, _socket.SOCK_STREAM))
        owner.settimeout(_remaining(deadline, timeout_code))
        owner.connect((target[1], 22))
        _remaining(deadline, timeout_code)
        phase = _F.SSH_NEGOTIATION_FAILED
        transport = _Stage2PinnedTransport(owner, strict_kex=True,
                                            gss_kex=False, gss_deleg_creds=False)
        _harden(transport)
        remaining = _remaining(deadline, timeout_code)
        transport.banner_timeout = remaining
        transport.handshake_timeout = remaining
        event = _threading.Event()
        transport.start_client(event=event)
        _wait(event, deadline, timeout_code)
        if not transport.is_active():
            _fail(_F.SSH_NEGOTIATION_FAILED)
        phase = _F.SSH_HOST_VERIFICATION_FAILED
        key = transport.get_remote_server_key()
        algorithm = key.get_name()
        if type(algorithm) is not str or algorithm != "ssh-ed25519":
            _fail(_F.HOST_KEY_ALGORITHM_MISMATCH)
        presented_blob = key.asbytes()
        if (type(presented_blob) is not bytes
                or not _hmac.compare_digest(presented_blob, blob)):
            _fail(_F.HOST_KEY_MISMATCH)
        _remaining(deadline, timeout_code)
        phase = _F.AUTHENTICATION_FAILED
        transport.auth_timeout = _remaining(deadline, timeout_code)
        event = _threading.Event()
        auth_request = _PendingOperation(
            lambda: transport.auth_password(username, secret, event=event, fallback=False),
            deadline)
        pending_operations.append(auth_request)
        _await_operation(auth_request, deadline, timeout_code, _F.AUTHENTICATION_FAILED)
        _wait(event, deadline, timeout_code)
        if not transport.is_authenticated():
            _fail(_F.AUTHENTICATION_FAILED)
        # No fresh timeout is granted within either phase.
        deadline = _time.monotonic() + 30.0
        timeout_code = _F.COMMAND_TIMEOUT
        phase = _F.CHANNEL_OPEN_FAILED
        channel_owner = _ChannelOwner()
        open_request = _PendingOperation(lambda: channel_owner.acquire(transport, deadline), deadline)
        pending_operations.append(open_request)
        _await_operation(open_request, deadline, timeout_code, _F.CHANNEL_OPEN_FAILED)
        channel = channel_owner.channel
        phase = _F.COMMAND_EXEC_FAILED
        channel.settimeout(_remaining(deadline, timeout_code))
        request = _PendingOperation(
            lambda: channel.exec_command("/interface vrrp print detail"), deadline)
        pending_operations.append(request)
        _await_operation(request, deadline, timeout_code, _F.COMMAND_EXEC_FAILED)
        phase = _F.OUTPUT_READ_FAILED
        stdout = _collect(channel, deadline)
    except Stage2PinnedSshTransportError as error:
        failure = error.code
    except Exception:
        failure = timeout_code if _time.monotonic() >= deadline else phase
    finally:
        secret = None
        cleanup_failure = _cleanup(channel_owner, transport, owner, pending_operations)
        failure = cleanup_failure or failure
    if failure is not None:
        _fail(failure)
    result = object.__new__(Stage2PinnedSshCommandResult)
    for name, value in (
        ("schema_version", "s2-ro-09.pinned-ssh-command-result.v1"),
        ("target_ref", target[0]), ("command_policy_version", _POLICY),
        ("stdout_bytes", stdout), ("stdout_sha256", _hashlib.sha256(stdout).hexdigest()),
        ("host_key_fingerprint", fingerprint), ("exit_status", 0),
        ("execution_attempts", 1), ("execution_authorized", False),
    ):
        object.__setattr__(result, name, value)
    return result


__all__ = ("Stage2PinnedSshCommandResult", "Stage2PinnedSshTransportFailure",
           "Stage2PinnedSshTransportError", "execute_stage2_pinned_ssh_command")
