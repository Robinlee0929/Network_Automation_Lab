# S2-RO-04 Windows Credential Backend

## Decision summary

S2-RO-04 implements one bounded Windows Credential Manager read capability for
the exact immutable S2-RO-03 binding. The credential target is trusted runtime
configuration supplied outside Git, and the operational caller can request only
`read(binding)`. The implementation has no enumeration, mutation, persistence,
subprocess, network, or live-device capability.

Status: implementation candidate ready for independent review after validation.

No real Windows credential was read while implementing or validating this
slice. Every behavioral test uses an injected fake Windows API.

## Position in the flow

```text
S2-RO-03 immutable non-secret binding
                    |
                    v
S2-RO-04 exact Windows credential read
                    |
                    v
bounded ephemeral credential material
                    |
                    v
future transport (not implemented)
```

S2-RO-04 owns credential retrieval only. Target selection, authorization,
Owner verification, replay protection, host-key trust, network transport,
command execution, runtime composition, and live-device access remain outside
this slice.

## Accepted input and trusted target boundary

The backend accepts only the S2-RO-03 binding whose values are:

- `credential_ref`: `credential.mikrotik.lab01`
- `backend_kind`: `WINDOWS_CREDENTIAL_MANAGER`
- `locator_ref`: `locator.stage2.mikrotik.lab01.readonly`

Backend and locator identity are validated before any Windows boundary call.
Invalid objects, alternate backends, alternate locators, and altered credential
references fail closed without a read attempt.

The real Windows Credential Manager target name is not present in Git. A future
trusted composition layer must supply exactly one target through the redacted
`Stage2TrustedWindowsCredentialConfiguration`. The request and operational
`read(binding)` call cannot select or override a Windows target, backend,
locator, username, secret, credential type, or read flags.

This trusted configuration boundary is not S2-RO-10 runtime composition and
does not discover configuration from files, environment variables, command
line input, or a remote provider.

## Exact Windows capability

The production adapter contains one deferred standard-library `ctypes` call to
Windows `CredReadW` for a generic credential with flags fixed to zero. It frees
the returned Windows allocation with `CredFree` after copying the bounded blob.
Windows libraries are neither loaded nor called at module import time.

The adapter exposes only `read_exact`. It has no broad discovery surface and no
credential enumeration, creation, update, write, delete, persistence change,
fallback target, wildcard, alias, or retry capability.

No new dependency is introduced. The module imports on non-Windows systems;
invoking the real adapter there produces the sanitized `UNSUPPORTED_PLATFORM`
failure before loading a Windows library.

## Ephemeral credential contract

Successful retrieval returns an immutable, slotted
`Stage2ResolvedCredential` with exactly:

- `username`: a non-empty bounded string of at most 256 characters;
- `secret_blob`: non-empty immutable bytes of at most 4096 bytes.

The blob remains bytes. S2-RO-04 does not assume UTF-8 or silently decode
arbitrary credential material.

Configuration, raw API records, backend objects, and resolved material all use
redacted `repr` and `str` output. No `to_dict`, `to_json`, evidence, report,
filesystem, environment, global cache, or module-global secret path exists.
Default JSON serialization rejects the credential object.

### Credential-memory lifetime and zeroization limit

`EPHEMERAL_LIFETIME_INTENT = YES`: credential material is intended to remain in
memory only for the minimum practical lifetime. S2-RO-04 introduces no
filesystem persistence or global cache, and secret material must not be logged
or serialized. Later consumers must minimize the secret's lifetime and must not
persist, serialize, or log it.

`GUARANTEED_PYTHON_MEMORY_ZEROIZATION = NO`: Python immutable `bytes` do not
provide a reliable guarantee that their underlying memory can be zeroized.
S2-RO-04 therefore does not claim guaranteed secure erase of Python-managed
memory. The ephemeral-lifetime intent limits exposure, but it is not a memory
clearing guarantee.

## Fail-closed model

Public exceptions contain only a bounded category. They never retain or render
the Windows target, username, or secret blob. Deterministic categories cover:

- invalid binding;
- unsupported backend or locator;
- invalid trusted configuration;
- unsupported platform;
- credential not found;
- Windows read failure;
- malformed credential record;
- missing or oversized username;
- invalid, empty, or oversized secret blob.

An API exception is converted to a sanitized backend error. There is no retry,
alternate target, or fallback lookup.

## Offline reviewer evidence

Focused tests use only a synthetic target, username, and secret with an injected
fake API. They prove:

- the exact accepted binding performs exactly one read;
- the binding is not mutated and returned material is immutable;
- wrong backend, locator, or malformed binding rejects before the API boundary;
- callers cannot override target, backend, locator, credential type, or flags;
- not-found, API-error, malformed, missing, wrong-type, empty, and oversized
  results fail closed;
- representations and errors redact identifying and secret material;
- JSON serialization is unavailable;
- no retry, enumeration, mutation, cache, persistence, subprocess, DPAPI,
  network, transport, or command-execution surface exists;
- non-Windows invocation fails before a Windows library is loaded;
- tests use the fake boundary and never call the real adapter.

Validation also includes the accepted S2-RO-01, S2-RO-02, and S2-RO-03 focused
regression suites, full pytest, report-index, complete-diff review, and tracked
file verification.

## Explicit exclusions

This slice does not implement or authorize known-hosts handling, host-key trust,
TOFU, `AutoAddPolicy`, a VRRP parser, Paramiko, sockets, DNS, SSH, NETCONF,
RESTCONF, HTTP, live commands, live-device access, evidence serialization, or
S2-RO-05 and later capabilities.

No real Credential Manager target, username, password, or secret is committed.
No real credential store was probed. Commit, push, pull request, merge, branch
cleanup, and the start of S2-RO-05 require separate Owner authorization.
