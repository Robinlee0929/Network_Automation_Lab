"""Offline S2-RO-09 contract tests: all execution boundaries are inert fakes."""

import ast
import base64
import copy
from dataclasses import FrozenInstanceError, fields
import hashlib
import inspect
import pickle
from pathlib import Path
import socket
import threading
from types import SimpleNamespace

import paramiko
from paramiko.kex_gex import KexGexSHA256
import pytest

from validation_framework import stage2_pinned_ssh_transport as sut


F = sut.Stage2PinnedSshTransportFailure
BLOB = b"\x00\x00\x00\x0bssh-ed25519\x00\x00\x00\x20" + bytes(range(32))
SECRET = b"synthetic-secret-\xff"
GEX = "diffie-hellman-group-exchange-sha256"


def issued(kind, **values):
    """Synthetic prior-slice output without calling any acquisition backend."""
    value = object.__new__(kind)
    for name, item in values.items():
        object.__setattr__(value, name, item)
    return value


@pytest.fixture
def inputs():
    endpoint = sut._Endpoint("target.mikrotik.lab01", "192.0.2.10", 22, "SSH", True)
    digest = hashlib.sha256(BLOB).digest()
    snapshot = issued(
        sut._Snapshot, schema_version="s2-ro-07.known-host.v1",
        target_ref=endpoint.target_ref, address=endpoint.address, port=22,
        host_key_algorithm="ssh-ed25519", host_key_blob=BLOB,
        host_key_sha256=digest.hex(),
        host_key_fingerprint="SHA256:" + base64.b64encode(digest).decode().rstrip("="),
        source_file_identity="win32-fileid-v1:" + "0" * 16 + ":" + "1" * 32,
        source_artifact_sha256="a" * 64, execution_authorized=False)
    specification = issued(
        sut._Specification, schema_version="s2-ro-08.command-policy.v1",
        operation_id="mikrotik.vrrp_status",
        command_policy_version="policy.stage2.vrrp-readonly.v1",
        command_text="/interface vrrp print detail", read_only=True,
        execution_authorized=False)
    return [endpoint, sut._Credential("synthetic-user", SECRET), snapshot, specification]


class Clock:
    def __init__(self):
        self.now = 100.0

    def monotonic(self):
        return self.now

    def sleep(self, duration):
        self.now += duration


class Boundary:
    def __init__(self):
        self.calls = []
        self.fail = set()
        self.delay = {}
        self.clock = Clock()
        self.stdout = b"sample\xffoutput"
        self.stderr = b""
        self.fragment = 4096
        self.eof = True
        self.status_ready = True
        self.status = 0
        self.algorithm = "ssh-ed25519"
        self.blob = BLOB
        self.keys = ("ssh-ed25519",)
        self.kex_info = dict(sut._Stage2PinnedTransport._kex_info)
        self.gex_prime = None
        self.active_close = True
        self.authenticated = True
        self.active = True
        self.exec_block = False
        self.block_until_socket_close = set()
        self.socket_close_event = threading.Event()
        self.socket_closed = 0
        self.transport_closed = 0
        self.channel_closed = 0
        self.close_event = threading.Event()
        self.options = SimpleNamespace()

    def call(self, name, *args):
        self.calls.append((name, args))
        self.clock.now += self.delay.get(name, 0)
        if name in self.fail:
            raise OSError("synthetic-native-secret-stderr")

    def socket(self, *args):
        self.call("socket", *args)
        boundary = self

        class Sock:
            def settimeout(self, timeout):
                boundary.call("socket_timeout", timeout)

            def connect(self, address):
                boundary.call("connect", address)

            def close(self):
                boundary.socket_closed += 1
                boundary.socket_close_event.set()
                boundary.call("socket_close")

        return Sock()

    def transport(self, owner, **kwargs):
        self.call("transport", kwargs)
        boundary = self

        class Transport:
            _kex_info = boundary.kex_info

            @property
            def preferred_keys(self):
                boundary.call("effective_keys")
                return boundary.keys

            def get_security_options(self):
                boundary.call("security_options")
                return boundary.options

            def start_client(self, *, event):
                boundary.call("start_client", vars(boundary.options).copy())
                if boundary.gex_prime is not None:
                    self._kex_info[GEX](self).parse_next(
                        31, gex_group(boundary.gex_prime))
                event.set()

            def is_active(self):
                return boundary.active

            def get_remote_server_key(self):
                boundary.call("remote_key")
                return SimpleNamespace(get_name=lambda: boundary.algorithm,
                                       asbytes=lambda: boundary.blob)

            def auth_password(self, username, secret, *, event, fallback):
                boundary.call("auth", username, secret, fallback)
                if "auth" in boundary.block_until_socket_close:
                    boundary.clock.now += 16
                    assert boundary.socket_close_event.wait(2)
                event.set()

            def is_authenticated(self):
                return boundary.authenticated

            def open_session(self, *, timeout, window_size, max_packet_size):
                boundary.call("open_session", timeout, window_size, max_packet_size)
                if "open_session" in boundary.block_until_socket_close:
                    boundary.clock.now += 31
                    assert boundary.socket_close_event.wait(2)
                return boundary.channel()

            def close(self):
                boundary.transport_closed += 1
                boundary.call("transport_close")
                if "transport_close" in boundary.block_until_socket_close:
                    assert boundary.socket_close_event.wait(2)
                if boundary.active_close:
                    owner.close()

        return Transport()

    def channel(self):
        boundary = self

        class Channel:
            def settimeout(self, timeout):
                boundary.call("channel_timeout", timeout)

            def exec_command(self, command):
                boundary.call("exec", command)
                if "exec" in boundary.block_until_socket_close:
                    boundary.clock.now += 31
                    assert boundary.socket_close_event.wait(2)
                if boundary.exec_block:
                    boundary.clock.now += 31
                    boundary.close_event.wait(2)

            def recv_stderr(self, maximum):
                boundary.call("stderr", maximum)
                if boundary.stderr:
                    result = boundary.stderr[:maximum]
                    boundary.stderr = boundary.stderr[maximum:]
                    return result
                if boundary.eof:
                    return b""
                raise socket.timeout()

            def recv(self, maximum):
                boundary.call("stdout", maximum)
                if boundary.stdout:
                    amount = min(maximum, boundary.fragment)
                    result = boundary.stdout[:amount]
                    boundary.stdout = boundary.stdout[amount:]
                    return result
                if boundary.eof:
                    return b""
                raise socket.timeout()

            def exit_status_ready(self):
                return boundary.status_ready

            def recv_exit_status(self):
                boundary.call("exit")
                return boundary.status

            def close(self):
                boundary.channel_closed += 1
                boundary.close_event.set()
                boundary.call("channel_close")
                if "channel_close" in boundary.block_until_socket_close:
                    assert boundary.socket_close_event.wait(2)

        return Channel()


@pytest.fixture
def boundary(monkeypatch):
    value = Boundary()

    def forbidden(*args, **kwargs):
        pytest.fail("real network boundary reached")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(sut, "_socket", SimpleNamespace(
        socket=value.socket, AF_INET=socket.AF_INET, SOCK_STREAM=socket.SOCK_STREAM,
        timeout=socket.timeout))
    monkeypatch.setattr(sut, "_Stage2PinnedTransport", value.transport)
    monkeypatch.setattr(sut, "_time", value.clock)
    return value


def run(inputs):
    return sut.execute_stage2_pinned_ssh_command(*inputs)


def rejected(inputs, code):
    with pytest.raises(sut.Stage2PinnedSshTransportError) as caught:
        run(inputs)
    error = caught.value
    assert error.code is code
    assert str(error) == code.value
    assert error.__context__ is None
    assert error.__cause__ is None
    assert "synthetic" not in repr(error)


@pytest.mark.parametrize("index,code", [(0, F.INVALID_ENDPOINT), (1, F.INVALID_CREDENTIAL),
                                     (2, F.INVALID_HOST_SNAPSHOT), (3, F.INVALID_COMMAND_SPECIFICATION)])
@pytest.mark.parametrize("replacement", [None, {}, (), object()])
def test_wrong_types_prevent_socket(inputs, boundary, index, code, replacement):
    inputs[index] = replacement
    rejected(inputs, code)
    assert boundary.calls == []


@pytest.mark.parametrize("index,code", [(0, F.INVALID_ENDPOINT), (1, F.INVALID_CREDENTIAL),
                                     (2, F.INVALID_HOST_SNAPSHOT), (3, F.INVALID_COMMAND_SPECIFICATION)])
def test_uninitialized_exact_type(inputs, boundary, index, code):
    inputs[index] = object.__new__(type(inputs[index]))
    rejected(inputs, code)
    assert boundary.calls == []


@pytest.mark.parametrize("index", [0, 1])
def test_subclass_rejected(inputs, boundary, index):
    subclass = type("Child", (type(inputs[index]),), {})
    inputs[index] = object.__new__(subclass)
    rejected(inputs, [F.INVALID_ENDPOINT, F.INVALID_CREDENTIAL][index])
    assert boundary.calls == []


@pytest.mark.parametrize("kind", [sut._Snapshot, sut._Specification])
def test_issued_inputs_cannot_be_subclassed(kind):
    with pytest.raises(TypeError):
        type("Child", (kind,), {})


@pytest.mark.parametrize("index,name,value,code", [
    (0, "address", "localhost", F.INVALID_ENDPOINT),
    (0, "address", "192.000.2.1", F.INVALID_ENDPOINT),
    (0, "port", 23, F.INVALID_ENDPOINT),
    (0, "port", True, F.INVALID_ENDPOINT),
    (0, "target_ref", "target.other", F.INVALID_ENDPOINT),
    (0, "transport", "HTTP", F.INVALID_ENDPOINT),
    (0, "declared_lab_only", False, F.INVALID_ENDPOINT),
    (1, "username", "", F.INVALID_CREDENTIAL),
    (1, "username", " user", F.INVALID_CREDENTIAL),
    (1, "username", "user\n", F.INVALID_CREDENTIAL),
    (1, "username", "a" * 257, F.INVALID_CREDENTIAL),
    (1, "username", 7, F.INVALID_CREDENTIAL),
    (1, "secret_blob", "password", F.INVALID_CREDENTIAL),
    (1, "secret_blob", b"", F.INVALID_CREDENTIAL),
    (1, "secret_blob", b"x" * 4097, F.INVALID_CREDENTIAL),
    (1, "secret_blob", bytearray(b"x"), F.INVALID_CREDENTIAL),
    (2, "target_ref", "target.other", F.ENDPOINT_BINDING_MISMATCH),
    (2, "address", "192.0.2.11", F.ENDPOINT_BINDING_MISMATCH),
    (2, "port", 23, F.ENDPOINT_BINDING_MISMATCH),
    (2, "port", True, F.INVALID_HOST_SNAPSHOT),
    (2, "schema_version", "other", F.INVALID_HOST_SNAPSHOT),
    (2, "host_key_algorithm", "ssh-rsa", F.INVALID_HOST_SNAPSHOT),
    (2, "host_key_blob", BLOB[:-1], F.INVALID_HOST_SNAPSHOT),
    (2, "host_key_blob", b"x" * 51, F.INVALID_HOST_SNAPSHOT),
    (2, "host_key_sha256", "0" * 64, F.INVALID_HOST_SNAPSHOT),
    (2, "host_key_fingerprint", "SHA256:other", F.INVALID_HOST_SNAPSHOT),
    (2, "source_file_identity", "invalid", F.INVALID_HOST_SNAPSHOT),
    (2, "source_artifact_sha256", "invalid", F.INVALID_HOST_SNAPSHOT),
    (2, "execution_authorized", True, F.INVALID_HOST_SNAPSHOT),
    (3, "schema_version", "other", F.INVALID_COMMAND_SPECIFICATION),
    (3, "operation_id", "other", F.INVALID_COMMAND_SPECIFICATION),
    (3, "command_policy_version", "other", F.INVALID_COMMAND_SPECIFICATION),
    (3, "command_text", "/interface vrrp print detail ", F.INVALID_COMMAND_SPECIFICATION),
    (3, "command_text", "/system reboot", F.INVALID_COMMAND_SPECIFICATION),
    (3, "read_only", False, F.INVALID_COMMAND_SPECIFICATION),
    (3, "read_only", 1, F.INVALID_COMMAND_SPECIFICATION),
    (3, "execution_authorized", True, F.INVALID_COMMAND_SPECIFICATION),
    (3, "execution_authorized", 0, F.INVALID_COMMAND_SPECIFICATION),
])
def test_malformed_inputs_no_network(inputs, boundary, index, name, value, code):
    object.__setattr__(inputs[index], name, value)
    rejected(inputs, code)
    assert boundary.calls == []


def test_success_order_exact_calls_and_result(inputs, boundary):
    original = boundary.stdout
    result = run(inputs)
    names = [name for name, _ in boundary.calls]
    for name in ("socket", "connect", "transport", "start_client", "remote_key", "auth", "open_session", "exec"):
        assert names.count(name) == 1
    assert names.index("effective_keys") < names.index("start_client")
    assert names.index("remote_key") < names.index("auth") < names.index("exec")
    assert dict(boundary.calls)["socket"] == (socket.AF_INET, socket.SOCK_STREAM)
    assert dict(boundary.calls)["connect"] == (("192.0.2.10", 22),)
    assert dict(boundary.calls)["auth"] == ("synthetic-user", SECRET, False)
    assert dict(boundary.calls)["exec"] == ("/interface vrrp print detail",)
    assert boundary.socket_closed == boundary.transport_closed == boundary.channel_closed == 1
    assert names.index("channel_close") < names.index("transport_close") < names.index("socket_close")
    assert result.stdout_bytes == original
    assert result.stdout_sha256 == hashlib.sha256(original).hexdigest()
    assert result.execution_authorized is False
    assert result.execution_attempts == 1 and result.exit_status == 0
    assert result.host_key_fingerprint == inputs[2].host_key_fingerprint
    assert "sample" not in repr(result) and "synthetic" not in repr(result)
    assert not hasattr(result, "__dict__")
    with pytest.raises(FrozenInstanceError):
        result.execution_authorized = True
    for operation in (copy.copy, copy.deepcopy, pickle.dumps):
        with pytest.raises(TypeError):
            operation(result)


@pytest.mark.parametrize("size", [0, 1, 65535, 65536, 65537])
@pytest.mark.parametrize("fragment", [137, 4096])
def test_output_bounds(inputs, boundary, size, fragment):
    boundary.stdout = b"\xff" * size
    boundary.fragment = fragment
    if size > 65536:
        rejected(inputs, F.OUTPUT_TOO_LARGE)
    else:
        assert run(inputs).stdout_bytes == b"\xff" * size
        if size == 65536:
            assert ("stdout", (1,)) in boundary.calls
    assert boundary.socket_closed == boundary.transport_closed == boundary.channel_closed == 1


@pytest.mark.parametrize("algorithm", ["ssh-rsa", "ecdsa-sha2-nistp256", "ssh-ed25519-cert-v01@openssh.com", None])
def test_algorithm_rejection_before_auth(inputs, boundary, algorithm):
    boundary.algorithm = algorithm
    rejected(inputs, F.HOST_KEY_ALGORITHM_MISMATCH)
    assert "auth" not in [n for n, _ in boundary.calls]


@pytest.mark.parametrize("blob", [BLOB[:-1] + bytes([BLOB[-1] ^ 1]), BLOB[19:], bytearray(BLOB)])
def test_exact_full_blob_required(inputs, boundary, blob):
    boundary.blob = blob
    rejected(inputs, F.HOST_KEY_MISMATCH)
    assert "auth" not in [n for n, _ in boundary.calls]


@pytest.mark.parametrize("keys", [("ssh-ed25519", "ssh-ed25519-cert-v01@openssh.com"), ("ssh-rsa",), (), ["ssh-ed25519"]])
def test_effective_key_drift_before_negotiation(inputs, boundary, keys):
    boundary.keys = keys
    rejected(inputs, F.SSH_NEGOTIATION_FAILED)
    assert "start_client" not in [n for n, _ in boundary.calls]


@pytest.mark.parametrize("step,code", [
    ("socket", F.CONNECT_FAILED), ("socket_timeout", F.CONNECT_FAILED),
    ("connect", F.CONNECT_FAILED), ("transport", F.SSH_NEGOTIATION_FAILED),
    ("security_options", F.SSH_NEGOTIATION_FAILED),
    ("start_client", F.SSH_NEGOTIATION_FAILED),
    ("remote_key", F.SSH_HOST_VERIFICATION_FAILED), ("auth", F.AUTHENTICATION_FAILED),
    ("open_session", F.CHANNEL_OPEN_FAILED), ("exec", F.COMMAND_EXEC_FAILED),
    ("stdout", F.OUTPUT_READ_FAILED), ("stderr", F.OUTPUT_READ_FAILED),
    ("exit", F.OUTPUT_READ_FAILED), ("channel_close", F.CHANNEL_CLOSE_FAILED),
    ("transport_close", F.TRANSPORT_CLOSE_FAILED),
])
def test_failures_sanitized_and_cleanup(inputs, boundary, step, code):
    boundary.fail.add(step)
    rejected(inputs, code)
    names = [n for n, _ in boundary.calls]
    assert names.count("connect") <= 1
    assert names.count("auth") <= 1 and names.count("exec") <= 1
    assert boundary.socket_closed == (0 if step == "socket" else 1)
    assert boundary.transport_closed <= 1 and boundary.channel_closed <= 1


@pytest.mark.parametrize("active_close", [False, True])
def test_socket_owner_all_transport_states(inputs, boundary, active_close):
    boundary.active_close = active_close
    run(inputs)
    assert boundary.socket_closed == 1


def test_socket_failure_is_fail_closed(inputs, boundary):
    boundary.active_close = False
    boundary.fail.add("socket_close")
    rejected(inputs, F.SOCKET_CLOSE_FAILED)
    assert boundary.socket_closed == 1


def test_cleanup_failure_overrides_operation_failure(inputs, boundary):
    boundary.fail.update(("exec", "channel_close", "transport_close", "socket_close"))
    rejected(inputs, F.CHANNEL_CLOSE_FAILED)
    assert boundary.socket_closed == boundary.channel_closed == boundary.transport_closed == 1


@pytest.mark.parametrize("step", ["connect", "transport", "start_client", "remote_key", "auth"])
def test_connect_deadline_never_reset(inputs, boundary, step):
    boundary.delay[step] = 16
    rejected(inputs, F.CONNECT_TIMEOUT)
    assert boundary.socket_closed == 1


@pytest.mark.parametrize("step", ["open_session", "exec", "stdout", "exit"])
def test_command_deadline_never_reset(inputs, boundary, step):
    boundary.delay[step] = 31
    rejected(inputs, F.COMMAND_TIMEOUT)
    assert boundary.socket_closed == 1


def test_connect_phase_time_is_shared(inputs, boundary):
    boundary.delay.update(connect=6, start_client=5, auth=5)
    rejected(inputs, F.CONNECT_TIMEOUT)
    assert "open_session" not in [n for n, _ in boundary.calls]


def test_command_phase_time_is_shared(inputs, boundary):
    boundary.delay.update(open_session=12, exec=12, exit=7)
    rejected(inputs, F.COMMAND_TIMEOUT)


def test_exec_ack_wait_cancelled_and_cleaned(inputs, boundary):
    boundary.exec_block = True
    rejected(inputs, F.COMMAND_TIMEOUT)
    assert boundary.channel_closed == boundary.transport_closed == boundary.socket_closed == 1


@pytest.mark.parametrize("step,code", [("auth", F.CONNECT_TIMEOUT),
                                     ("open_session", F.COMMAND_TIMEOUT),
                                     ("exec", F.COMMAND_TIMEOUT)])
def test_stalled_initiation_is_released_by_socket_shutdown(inputs, boundary, step, code):
    boundary.block_until_socket_close.add(step)
    rejected(inputs, code)
    assert boundary.socket_closed == boundary.transport_closed == 1
    names = [n for n, _ in boundary.calls]
    if step in ("auth", "open_session"):
        assert "exec" not in names
    if step == "open_session":
        # A channel published after cancellation is still closed exactly once.
        assert boundary.channel_closed == 1


@pytest.mark.parametrize("step", ["channel_close", "transport_close"])
def test_stalled_cleanup_cannot_prevent_socket_escape(inputs, boundary, step):
    boundary.block_until_socket_close.add(step)
    run(inputs)
    assert boundary.socket_closed == boundary.transport_closed == boundary.channel_closed == 1


def test_stalled_exec_and_both_close_sends(inputs, boundary):
    boundary.block_until_socket_close.update(("exec", "channel_close", "transport_close"))
    rejected(inputs, F.COMMAND_TIMEOUT)
    assert boundary.socket_closed == boundary.transport_closed == boundary.channel_closed == 1


def test_cancelled_open_channel_owner_closes_late_result_once(boundary):
    owner = sut._ChannelOwner()
    owner.close()
    transport = SimpleNamespace(open_session=lambda **kwargs: boundary.channel())
    owner.acquire(transport, boundary.clock.now + 30)
    owner.close()
    assert boundary.channel_closed == 1


def test_channel_window_exceeds_output_adjust_threshold(inputs, boundary):
    run(inputs)
    _, window, packet = dict(boundary.calls)["open_session"]
    assert window == 2097152 and packet == 32768
    assert window // 10 > 65537 + 1


@pytest.mark.parametrize("status", [1, -1, 255, True, None])
def test_nonzero_or_invalid_status(inputs, boundary, status):
    boundary.status = status
    rejected(inputs, F.NONZERO_EXIT_STATUS)


def test_any_stderr_fails(inputs, boundary):
    boundary.stderr = b"synthetic-error" * 100
    rejected(inputs, F.STDERR_PRESENT)
    assert dict(boundary.calls)["stderr"] == (1,)


@pytest.mark.parametrize("missing", ["eof", "status_ready"])
def test_stream_and_status_completion_required(inputs, boundary, missing):
    setattr(boundary, missing, False)
    rejected(inputs, F.COMMAND_TIMEOUT)
    assert boundary.socket_closed == 1


@pytest.mark.parametrize("flag,code", [("active", F.SSH_NEGOTIATION_FAILED),
                                     ("authenticated", F.AUTHENTICATION_FAILED)])
def test_unsuccessful_events(inputs, boundary, flag, code):
    setattr(boundary, flag, False)
    rejected(inputs, code)


def test_actual_paramiko_negotiation_correction_without_constructor():
    # No Transport.__init__, socket, thread, or SSH negotiation occurs here.
    base = object.__new__(paramiko.Transport)
    base.disabled_algorithms = {"keys": ["ssh-ed25519-cert-v01@openssh.com"]}
    base.get_security_options().key_types = ("ssh-ed25519",)
    assert base.preferred_keys == ("ssh-ed25519", "ssh-ed25519-cert-v01@openssh.com")
    private = object.__new__(sut._Stage2PinnedTransport)
    private.disabled_algorithms = {}
    sut._harden(private)
    assert private.preferred_keys == ("ssh-ed25519",)
    options = private.get_security_options()
    assert options.key_types == ("ssh-ed25519",)
    assert options.kex == ("ecdh-sha2-nistp256", "diffie-hellman-group16-sha512",
                           "diffie-hellman-group14-sha256", GEX)
    assert private.preferred_kex == options.kex
    assert options.ciphers == ("aes256-ctr", "aes192-ctr", "aes128-ctr")
    assert options.digests == ("hmac-sha2-512-etm@openssh.com", "hmac-sha2-256-etm@openssh.com", "hmac-sha2-512", "hmac-sha2-256")
    assert options.compression == ("none",)
    assert base.preferred_keys != private.preferred_keys
    assert set(sut._Stage2PinnedTransport.__dict__) - {"__module__", "__doc__", "preferred_keys", "_kex_info", "__firstlineno__", "__static_attributes__"} == set()


def gex_group(prime):
    message = paramiko.Message()
    message.add_mpint(prime)
    message.add_mpint(2)
    return paramiko.Message(message.asbytes())


class GexBoundary:
    """Only the in-memory packet methods needed by the native GEX parser."""

    server_mode = False

    def __init__(self):
        self.sent = []
        self.expected = []

    def _send_message(self, message):
        self.sent.append(message.asbytes())

    def _expect_packet(self, *types):
        self.expected.append(types)

    def _log(self, *args):
        pass


def test_native_registry_and_private_gex_isolation():
    registry = paramiko.Transport._kex_info
    before = registry.copy()
    native_attributes = dict(vars(KexGexSHA256))
    native_policy = (KexGexSHA256.min_bits, KexGexSHA256.preferred_bits,
                     KexGexSHA256.max_bits)
    assert registry[GEX] is KexGexSHA256
    assert "curve25519-sha256" not in registry
    assert "curve25519-sha256@libssh.org" in registry
    private = object.__new__(sut._Stage2PinnedTransport)
    private.disabled_algorithms = {}
    sut._harden(private)
    assert private._kex_info is not registry
    assert dict(private._kex_info) == {**registry, GEX: sut._Stage2GexSHA256}
    assert private._kex_info[GEX] is sut._Stage2GexSHA256
    with pytest.raises(TypeError):
        private._kex_info[GEX] = KexGexSHA256
    # Exercise the registered class, not a separately constructed substitute.
    transport = GexBoundary()
    engine = private._kex_info[GEX](transport)
    assert isinstance(engine, KexGexSHA256)
    assert engine.hash_algo is hashlib.sha256
    assert (engine.min_bits, engine.preferred_bits, engine.max_bits) == (2048, 2048, 8192)
    engine.start_kex()
    request = paramiko.Message(transport.sent[0])
    assert request.get_byte() == b"\x22"
    assert (request.get_int(), request.get_int(), request.get_int()) == (2048, 2048, 8192)
    assert request.get_remainder() == b""
    assert transport.expected == [(31,)]
    assert paramiko.Transport._kex_info is registry and registry == before
    assert dict(vars(KexGexSHA256)) == native_attributes
    assert native_policy == (1024, 2048, 8192)
    assert (KexGexSHA256.min_bits, KexGexSHA256.preferred_bits,
            KexGexSHA256.max_bits) == native_policy


def test_native_kexinit_dispatch_uses_hardened_gex_without_transport_constructor():
    private = object.__new__(sut._Stage2PinnedTransport)
    private.disabled_algorithms = {}
    private.server_mode = False
    private.agreed_on_strict_kex = False
    private._log = lambda *args: None
    sut._harden(private)
    packet = paramiko.Message()
    packet.add_bytes(bytes(16))
    for algorithms in ([GEX], ["ssh-ed25519"], ["aes256-ctr"], ["aes256-ctr"],
                       ["hmac-sha2-256"], ["hmac-sha2-256"], ["none"], ["none"], [], []):
        packet.add_list(algorithms)
    packet.add_boolean(False)
    packet.add_int(0)
    private._parse_kex_init(paramiko.Message(packet.asbytes()))
    assert type(private.kex_engine) is sut._Stage2GexSHA256
    assert private.kex_engine.transport is private
    assert private.host_key_type == "ssh-ed25519"
    assert private.local_cipher == private.remote_cipher == "aes256-ctr"
    assert private.local_mac == private.remote_mac == "hmac-sha2-256"
    assert private.local_compression == private.remote_compression == "none"


@pytest.mark.parametrize("excluded", [
    "diffie-hellman-group-exchange-sha1", "diffie-hellman-group14-sha1",
    "diffie-hellman-group1-sha1", "mlkem768x25519-sha256",
    "curve25519-sha256", "curve25519-sha256@libssh.org",
])
def test_disallowed_kex_not_effective(excluded):
    private = object.__new__(sut._Stage2PinnedTransport)
    private.disabled_algorithms = {}
    sut._harden(private)
    assert excluded not in private.preferred_kex


@pytest.mark.parametrize("prime", [0, -1, -(1 << 2047), 1 << 1023,
                                   (1 << 2047) - 1, 1 << 8192])
def test_gex_rejects_actual_out_of_range_group_before_crypto(monkeypatch, prime):
    transport = GexBoundary()
    engine = sut._Stage2PinnedTransport._kex_info[GEX](transport)

    def forbidden():
        pytest.fail("rejected group reached exponent generation")

    monkeypatch.setattr(engine, "_generate_x", forbidden)
    with pytest.raises(paramiko.SSHException, match="Stage-2 GEX group size rejected"):
        engine.parse_next(31, gex_group(prime))
    assert engine.p is None and engine.x is None and engine.e is None
    assert transport.sent == transport.expected == []


@pytest.mark.parametrize("bits", [2048, 3072, 8192])
def test_gex_accepts_bounded_group_without_consuming_parser_input(monkeypatch, bits):
    transport = GexBoundary()
    engine = sut._Stage2PinnedTransport._kex_info[GEX](transport)
    # Synthetic integers test size dispatch only, not group primality.
    prime = (1 << bits) - 1
    monkeypatch.setattr(engine, "_generate_x", lambda: setattr(engine, "x", 2))
    engine.parse_next(31, gex_group(prime))
    assert engine.p == prime and engine.g == 2 and engine.e == 4
    assert transport.expected == [(33,)]
    reply = paramiko.Message(transport.sent[0])
    assert reply.get_byte() == b"\x20" and reply.get_mpint() == 4
    assert reply.get_remainder() == b""


@pytest.mark.parametrize("replacement", [None, KexGexSHA256])
def test_gex_mapping_cannot_silently_fall_back(inputs, boundary, replacement):
    if replacement is None:
        del boundary.kex_info[GEX]
    else:
        boundary.kex_info[GEX] = replacement
    rejected(inputs, F.SSH_NEGOTIATION_FAILED)
    names = [name for name, _ in boundary.calls]
    assert names.count("connect") == 1
    assert not set(names) & {"start_client", "remote_key", "auth", "open_session", "exec"}
    assert boundary.socket_closed == boundary.transport_closed == 1
    assert boundary.channel_closed == 0


def test_undersized_gex_negotiation_fails_closed_without_retry_or_auth(inputs, boundary):
    boundary.gex_prime = (1 << 2047) - 1
    rejected(inputs, F.SSH_NEGOTIATION_FAILED)
    names = [name for name, _ in boundary.calls]
    assert names.count("connect") == names.count("start_client") == 1
    assert not set(names) & {"remote_key", "auth", "open_session", "exec"}
    assert boundary.socket_closed == boundary.transport_closed == 1
    assert boundary.channel_closed == 0


def test_actual_paramiko_password_bytes_path():
    from paramiko.util import b
    assert b(SECRET) is SECRET
    source = inspect.getsource(paramiko.auth_handler.AuthHandler)
    assert "password = b(self.password)" in source


def test_public_surface_and_no_orchestration():
    assert sut.__all__ == ("Stage2PinnedSshCommandResult", "Stage2PinnedSshTransportFailure",
                           "Stage2PinnedSshTransportError", "execute_stage2_pinned_ssh_command")
    assert list(inspect.signature(sut.execute_stage2_pinned_ssh_command).parameters) == [
        "endpoint", "credential", "known_host_snapshot", "command_specification"]
    assert [f.name for f in fields(sut.Stage2PinnedSshCommandResult)] == [
        "schema_version", "target_ref", "command_policy_version", "stdout_bytes", "stdout_sha256",
        "host_key_fingerprint", "exit_status", "execution_attempts", "execution_authorized"]
    tree = ast.parse(Path(sut.__file__).read_text(encoding="utf-8"))
    called = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert not called & {"getaddrinfo", "create_connection", "SSHClient", "AutoAddPolicy", "load_system_host_keys",
                         "get_pty", "invoke_shell", "invoke_subsystem", "open_sftp_client", "request_port_forward",
                         "request_forward_agent", "request_x11", "set_environment_variable", "auth_publickey",
                         "auth_interactive", "lookup", "read_exact", "consume"}
    assert sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "exec_command"
               for n in ast.walk(tree)) == 1
