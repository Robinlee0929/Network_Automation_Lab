# S2-RO-09: Pinned SSH transport

## Decision summary

S2-RO-09 implements one bounded pinned SSH transport primitive for the exact
command `/interface vrrp print detail`. The current compatibility remediation
adds only `diffie-hellman-group-exchange-sha256`, with a 2048-bit minimum for
both the request and the server's actual group. Status: validated offline
remediation candidate; independent security review PASS, zero unresolved
material findings. Ready for separate local-commit authorization. The original
slice's delivery evidence is retained below as historical context.
No live operation is authorized by this document or by a successful result.

The Owner approved a private Paramiko `Transport.preferred_keys` override to
enforce raw `ssh-ed25519` negotiation. This correction is part of this slice;
it does not modify Paramiko or any prior-slice contract. The compatibility
remediation also uses a private GEX subclass and registry, without changing
installed dependencies or global Paramiko state.

## Allowed scope

Exactly three files comprise this candidate:

- [Transport](../../validation_framework/stage2_pinned_ssh_transport.py)
- [Offline tests](../../tests/stage2/test_pinned_ssh_transport.py)
- This document.

The sole public operation is `execute_stage2_pinned_ssh_command(endpoint,
credential, known_host_snapshot, command_specification)`. It accepts only exact
S2-RO-02 `Stage2FixedTargetEndpoint`, S2-RO-04 `Stage2ResolvedCredential`,
S2-RO-07 `Stage2KnownHostSnapshot`, and S2-RO-08
`Stage2VrrpReadOnlyCommandSpecification` objects. It revalidates initialized
fields and captures immutable values before creating any socket. Subclasses,
lookalikes, malformed objects, command drift, and authority-flag drift reject.

Endpoint target reference, canonical IPv4 address, and integer port must match
the snapshot exactly. The port is always 22. The snapshot's complete Ed25519
blob, hash, fingerprint, source identity syntax, and source artifact digest
syntax are checked without reacquiring its source. This validates the handoff;
it does not independently prove acquisition provenance or source freshness.
Arbitrary privileged in-process mutation remains outside the Python contract.

## Forbidden scope and later composition

There is no target resolution, Credential Manager call, known-host acquisition,
Owner verification, approval acquisition, replay consumption, VRRP parsing,
final S2-RO-01 evidence construction, or runtime orchestration. S2-RO-10 and
S2-RO-11 remain separately gated. S2-RO-01 through S2-RO-08 are unchanged.

No DNS, hostname, alternate address, retry, reconnect, system/user known_hosts,
TOFU, host-key rotation fallback, SSH agent, keyfile, public-key authentication,
keyboard-interactive fallback, GSSAPI, PTY, shell, subsystem, SFTP, forwarding,
X11, or environment request is used. There are no public security-policy,
command, timeout, credential, or generic SSH options.

## Negotiation and exact pin verification

The sequence is one AF_INET/SOCK_STREAM socket, one connect to the validated
IPv4 literal on port 22, private Transport construction, SecurityOptions
hardening, an exact effective-key assertion, and `start_client(event=...)`.
Paramiko must complete cryptographic KEX/server-signature verification before
`get_remote_server_key()` succeeds. The returned algorithm must be exactly
`ssh-ed25519`; its complete `asbytes()` blob must match the snapshot using
`hmac.compare_digest`. Authentication is unreachable after any mismatch.

| Setting | Exact allowlist |
| --- | --- |
| Server host keys | `ssh-ed25519` |
| KEX | `ecdh-sha2-nistp256`, `diffie-hellman-group16-sha512`, `diffie-hellman-group14-sha256`, `diffie-hellman-group-exchange-sha256` |
| Ciphers | `aes256-ctr`, `aes192-ctr`, `aes128-ctr` |
| MACs | `hmac-sha2-512-etm@openssh.com`, `hmac-sha2-256-etm@openssh.com`, `hmac-sha2-512`, `hmac-sha2-256` |
| Compression | `none` |

The installed validation version is Paramiko 3.5.1. Its base `preferred_keys`
property appends certificate variants after disabled-algorithm filtering.
Thus `SecurityOptions.key_types = ("ssh-ed25519",)` alone is insufficient.
An offline test uses inert, uninitialized Transport objects with the actual
SecurityOptions/property implementations to reproduce this behavior and prove
that the private subclass returns exactly `("ssh-ed25519",)` instead. The
subclass preserves this property override. No package/global monkeypatch is used
by production code. A drifted effective tuple fails before `start_client`.

SSH certificates are not inherently insecure. They are outside this slice's
raw-key pin model, which defines no CA or certificate-validation semantics.
The negotiation restriction never replaces the post-KEX complete-blob check.

### Live compatibility finding and remediation trigger

A separately authorized, non-authenticated real Lab1 diagnostic against
`192.168.88.2:22` opened no SSH channel and recorded
`PRIMARY_DIAGNOSIS = NO_COMMON_KEX`, with Paramiko classification
`IncompatiblePeer`. The remote KEX proposal included
`mlkem768x25519-sha256`, `curve25519-sha256`,
`diffie-hellman-group-exchange-sha256`, and `ext-info-s`. The then-current
Stage-2 KEX allowlist was `ecdh-sha2-nistp256`,
`diffie-hellman-group16-sha512`, and
`diffie-hellman-group14-sha256`; therefore
`KEX_INTERSECTION_WITH_STAGE2 = []`.

Other negotiation dimensions did have compatible intersections: host key
`ssh-ed25519`; ciphers `aes256-ctr` and `aes192-ctr`; MACs
`hmac-sha2-512` and `hmac-sha2-256`; and compression `none`.

This diagnostic directly triggered the bounded compatibility remediation: add
exactly `diffie-hellman-group-exchange-sha256` while retaining
`STAGE2_GEX_MINIMUM_BITS = 2048`, `STAGE2_GEX_PREFERRED_BITS = 2048`, and
`STAGE2_GEX_MAXIMUM_BITS = 8192`, bounding GEX to 2048–8192 bits. No other KEX
was added. The remediation did not add `mlkem768x25519-sha256`,
`curve25519-sha256`, `curve25519-sha256@libssh.org`, or any SHA-1 KEX.

`POST_REMEDIATION_LIVE_CONNECTION_RESULT = NOT_YET_VERIFIED`.
Post-remediation live success is not yet verified; this evidence does not
establish a successful SSH handshake, host-key observation or known-host trust,
authentication, RouterOS command execution, or a Stage-2 real live run.

### Bounded GEX SHA-256 compatibility

Paramiko 3.5.1 natively registers GEX SHA-256. It does not register the exact
`curve25519-sha256` name; its `curve25519-sha256@libssh.org` identifier is
distinct. Neither Curve25519 identifier, ML-KEM, nor any SHA-1 KEX is added
to Stage-2 policy. The existing three KEX algorithms retain their order and
GEX SHA-256 is appended. Cipher, MAC, compression, raw-key pinning, deadlines,
authentication, command, retry, and cleanup policies are unchanged.

The private `_Stage2GexSHA256` requests minimum/preferred/maximum sizes of
2048/2048/8192 bits. Paramiko's native group-reply parser has a hardcoded
1024-bit lower bound independent of `min_bits`; changing that attribute alone
would not enforce this contract. The private parser inspects the positive
group modulus from a copy of the message and rejects sizes outside 2048–8192
bits before native exponent generation or a GEX-init packet. It then delegates
to the native SHA-256 implementation with the original message intact.
This is a group-size restriction, not a new primality validation guarantee.

`_Stage2PinnedTransport` owns an immutable copy of the native KEX registry
with only the GEX SHA-256 entry replaced. An effective mapping check rejects
a missing or native lower-floor entry before `start_client`. There is no
fallback, global monkeypatch, package edit, or public algorithm override.
Offline tests exercise actual Paramiko KEXINIT dispatch on an uninitialized
transport, synthetic group replies below/at/above the limits, the wire request,
mapping drift, unchanged native state, and rejection before auth with cleanup.

Authentication is one `auth_password(username, secret_blob, event=...,
fallback=False)` call. Paramiko 3.5.1's password path preserves bytes through
its `b()` helper; no secret decoding or alternate authentication is introduced.

## Deadlines and output

One absolute `time.monotonic()` deadline starts before socket construction.
Its 15 seconds cover connect, Transport setup, negotiation, pin verification,
and password authentication. Every wait uses remaining time.

A separate absolute 30-second deadline starts immediately before
`open_session`. It covers channel opening, the one exact exec request,
stdout/stderr collection, EOF, overflow probing, and exit status. No operation
resets either deadline. Private helper threads externally bound password-auth
initiation, channel opening, and the exec acknowledgement. This includes sends
that Paramiko may perform before beginning its response timeout. Each helper
initiates its operation at most once and rejects pre-start cancellation or an
expired deadline. Late channel returns are owned and closed even after timeout;
they cannot reach exec. A surviving helper fails cleanup and cannot issue a
successful result.

Collection uses nonblocking reads and services stderr before stdout. It retains
at most 65,537 stdout bytes while deciding overflow. Any stderr byte fails
immediately, without retaining the full stderr. Byte 65,537 fails; a full
65,536-byte output must still reach EOF without another byte. Both streams
must reach EOF and exit status must be ready within the deadline; status alone
does not establish stream completion. Exit status must be the exact integer 0.
There is no truncation or partial success.

The channel window is fixed at 2,097,152 bytes with a 32,768-byte packet bound.
The maximum consumed output is below Paramiko's one-tenth-window adjustment
threshold, avoiding a synchronous window-adjust send during bounded collection.

Stdout remains raw bytes. Empty stdout with exit 0 and no stderr is transport
success. The S2-RO-08 parser owns EMPTY_OUTPUT and strict UTF-8 rejection when
future S2-RO-10 composition invokes it. Transport does not duplicate parsing.

## Resource ownership and failures

Cleanup initiation order is channel, Transport, then a private socket owner. The owner
serializes all physical socket-close requests, including requests originating
inside Paramiko. Inactive Transport cleanup still reaches the owner; active
Transport cleanup cannot physically double-close the socket. A close failure
is recorded and fails closed; no success asserts cleanup certainty after an
OS close error. The physical close is attempted at most once, including errors.

Channel and Transport close calls run in private cleanup helpers. Each receives
at most a 50-millisecond head start before the next cleanup step, so a stalled
close-packet send cannot prevent the final socket-close escape. After socket
shutdown, all initiation and cleanup helpers share one one-second join
allowance. No successful result is issued while a helper remains alive or a
required close failed. The cleanup allowance is separate from, and does not
reset, either execution deadline. Channel ownership handles cancellation before
or after publication and invokes its close at most once.

Cleanup runs after operation failures too. Deterministic cleanup precedence is
CHANNEL_CLOSE_FAILED, TRANSPORT_CLOSE_FAILED, SOCKET_CLOSE_FAILED; these
override an earlier operation failure. Otherwise the operation failure remains.
Public exceptions contain only the bounded category, with no chained native
exception, stderr, stdout, server banner, or secret in their message/repr.

The failure enum is exactly: INVALID_ENDPOINT, INVALID_CREDENTIAL,
INVALID_HOST_SNAPSHOT, INVALID_COMMAND_SPECIFICATION, ENDPOINT_BINDING_MISMATCH,
HOST_KEY_ALGORITHM_MISMATCH, HOST_KEY_MISMATCH, CONNECT_FAILED, CONNECT_TIMEOUT,
SSH_NEGOTIATION_FAILED, SSH_HOST_VERIFICATION_FAILED, AUTHENTICATION_FAILED,
CHANNEL_OPEN_FAILED, COMMAND_EXEC_FAILED, COMMAND_TIMEOUT, STDERR_PRESENT,
NONZERO_EXIT_STATUS, OUTPUT_TOO_LARGE, OUTPUT_READ_FAILED, CHANNEL_CLOSE_FAILED,
TRANSPORT_CLOSE_FAILED, SOCKET_CLOSE_FAILED, INTERNAL_FAILURE.

## Result contract

Only after required cleanup succeeds, the operation issues a frozen, slotted
`Stage2PinnedSshCommandResult` with exactly `schema_version`, `target_ref`,
`command_policy_version`, `stdout_bytes`, `stdout_sha256`, `host_key_fingerprint`,
`exit_status`, `execution_attempts`, and `execution_authorized`.
The schema is `s2-ro-09.pinned-ssh-command-result.v1`, attempts is 1, exit status
is 0, and `execution_authorized` is False. SHA-256 covers all returned bytes.
The safe representation hides output. Credentials, mutable buffers, stderr,
socket, Transport, and Channel are absent. This result proves bounded transport
success only; trusted later composition must establish Owner/replay authority.

## Validation and acceptance

All execution tests use synthetic in-memory inputs, fake sockets/transports/
channels, and a deterministic clock. They do not call prior-slice acquisition,
create a real socket, use loopback/DNS, or negotiate with an SSH server.
Actual Paramiko regression checks use inert objects and do not initialize a
Transport. Required validation is focused tests without skips, all Stage-2
tests, full pytest, report-index, whitespace/LF checks, independent read-only
security review, documentation readability review, and final SHA-256 freeze.

Windows validation follows S2-RO-08's guarded non-TTY setup: native/network/
process guards precede pytest import, plugin autoload/cache/bytecode are
disabled, and source-reviewed ephemeral Colorama/click console stubs avoid
native console initialization. Existing local Python/Node regression children
retain network blockers; Git-fixture subprocesses are restricted to disposable
test repositories. Socket denial raises OSError so existing offline fallback
tests exercise their network-unavailable path without creating a socket.
The two real Win32 trust-root tests and the
Flask process/socket lifecycle test remain explicitly classified safety skips.
No S2-RO-09 test may skip. No dependency or requirements change is needed.

### Current KEX remediation evidence

- Base commit: `2a71dc8eb5d7dcb12f5c3b1e533a339d2744ecea`.
- Base tree: `48eec05773e8a731ad953f5e86ab5a4e80ec67d1`.
- Focused: 156 collected, 156 passed, zero failures or skips.
- Stage 2: 1,562 collected, 1,560 passed, zero failures, two safety skips.
- Full pytest: 3,688 collected, 3,685 passed, zero failures, three safety skips.
- Report-index: 14/14 PASS, zero failures, warnings, or missing entries.
- Exact three-file scope, UTF-8/LF without BOM, and `git diff --check`: PASS.
- Independent read-only security review: PASS; zero unresolved material findings.
- Documentation readability review: PASS.

Validation used the guarded offline setup described above with Python 3.13,
Paramiko 3.5.1, and pytest 8.4.2. The same two Win32 tests and one Flask
lifecycle test were skipped for safety; no S2-RO-09 test skipped. The commands
inside the guard invoke pytest with `-p no:cacheprovider --color=no -ra`, then
`tests/stage2/test_pinned_ssh_transport.py -q`, `tests/stage2 -q`, or `-q` for
the three respective suites. Report-index runs `network_lab.py --task
report-index` through the same guard. All transport and GEX evidence is
synthetic: no real socket, loopback, device, known-host asset, credential,
private signing key, or authorization consumption was used.

### Historical original-slice candidate evidence

- Focused: 136 collected, 136 passed, zero failures or skips.
- Stage 2: 1,144 collected, 1,142 passed, zero failures, two safety skips.
- Full pytest: 3,270 collected, 3,267 passed, zero failures, three safety skips.
- Report-index: 14/14 PASS, zero failures, warnings, or missing entries.
- LF-only UTF-8 without BOM and whitespace checks: PASS.
- Independent read-only security re-review: PASS; zero unresolved material
  findings. The review's initiation-deadline and blocking-cleanup findings were
  remediated and covered by tests that block until socket shutdown.
- Documentation readability review: PASS.

The two Stage-2 skips are the real Win32 disposable-file and trailing-dot-alias
trust-root tests. The additional full-suite skip is the Flask process/socket
lifecycle test. These are the accepted local safety exclusions; no S2-RO-09
test was skipped. Validation used Python 3.13, Paramiko 3.5.1, and pytest 8.4.2.
Early validation-launcher compatibility failures were corrected only in the
temporary harness; no prior-slice files or installed packages were modified.

This evidence grants no staging, commit, push, merge, or live-access authority.

References: [S2-RO-02](stage2_vrrp_readonly_s2_ro_02_target_registry.md),
[S2-RO-04](stage2_vrrp_readonly_s2_ro_04_windows_credential_backend.md),
[S2-RO-07](stage2_vrrp_readonly_s2_ro_07_known_host_snapshot.md),
[S2-RO-08](stage2_vrrp_readonly_s2_ro_08_command_policy.md), and
[integration gates](actual_automation_integration_plan.md).
