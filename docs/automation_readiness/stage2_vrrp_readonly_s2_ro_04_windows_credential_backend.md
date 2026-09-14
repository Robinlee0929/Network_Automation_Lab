# S2-RO-04 Windows Credential Backend

## Decision summary

S2-RO-04 validates the trusted Stage-2 Windows password representation as strict
UTF-16LE and returns the same password as strict UTF-8 transport bytes. This
offline remediation corrects the credential handoff to the unchanged S2-RO-09
transport. It does not authorize a live retry or claim compatibility PASS.

The trusted policy wrapper continues to accept the two exact
S2-RO-03 target/credential bindings, each with its matching trusted locator.
Legacy `read(binding)` remains Lab1-only; `read_for_target(target_ref, binding)`
checks the exact pair through S2-RO-03 before comparing configuration identity.
The native Windows reader is unchanged. This is an **offline remediation**,
not permission to read a credential store or contact either lab.

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
bounded raw UTF-16LE bytes -> strict validation -> canonical UTF-8 bytes
                    |
                    v
unchanged S2-RO-09 transport (no execution authorized here)
```

S2-RO-04 owns bounded credential retrieval and representation validation.
Endpoint selection, authorization,
Owner verification, replay protection, host-key trust, network transport,
command execution, runtime composition, and live-device access remain outside
this slice.

## Accepted input and trusted target boundary

The target-aware API accepts only these exact relationships, as resolved by
`Stage2FixedCredentialResolver.resolve_for_target`:

| Logical target | Credential identity | Required trusted configuration |
| --- | --- | --- |
| `target.mikrotik.lab01` | `credential.mikrotik.lab01` | Existing Lab1 locator, equal to the Lab1 binding locator |
| `target.mikrotik.lab02` | `credential.mikrotik.lab02` | Distinct externally provisioned Lab2 credential locator, equal to the Lab2 binding locator |

Both bindings use `WINDOWS_CREDENTIAL_MANAGER`; sharing the native read primitive
does not share credential authority. S2-RO-03 remains the authority for the
target/credential relationship. S2-RO-04 does not maintain a second pair registry.

Before any Windows boundary call, the policy requires an exact binding object,
the fixed backend kind, a resolver-approved target/credential pair, a binding
locator equal to that resolver result, and a trusted configuration locator equal
to the same result. Cross-lab credentials or locators, unknown identities,
aliases, prefixes, case-confused values, and malformed objects fail closed with
zero reader calls. Valid pairs perform exactly one read, without retries.

`read(binding)` retains its original signature and Lab1-only identity checks;
it then applies the same target-aware policy with the fixed Lab1 target. It
cannot read a Lab2 binding or use a Lab2 configuration for Lab1. Existing Lab1
configuration, error sanitization, reader call semantics, and output fields are
unchanged. No S2-RO-05 or later production consumer is modified or enabled for
Lab2 by this extension.

The real Windows Credential Manager target name is not present in Git. A future
trusted composition layer must supply exactly one target through the redacted
`Stage2TrustedWindowsCredentialConfiguration`. The request and operational
`read(binding)` and `read_for_target(target_ref, binding)` calls cannot select or
override a Windows target, backend,
locator, username, secret, credential type, or read flags.

Each backend instance has one immutable trusted configuration, with no default
locator. The actual Windows record name must be separately provisioned and
supplied by the trusted owner outside Git. This offline policy neither probes
record existence nor verifies external provisioning; distinct real Lab2 record
provisioning remains separately authorized work. Logical locators are not stored
secret values or evidence that an actual credential record exists.

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
- `secret_blob`: non-empty canonical UTF-8 password bytes of at most 4096 bytes.

`Stage2WindowsCredentialApiRecord.secret_blob` holds raw bytes copied from the
trusted `CRED_TYPE_GENERIC` Windows `CredentialBlob`. Under the Stage-2
provisioning contract these bytes contain strict UTF-16LE password data.
Generic credential blob semantics are application/provisioning-defined: this
is not a universal claim about every Windows Generic Credential.

The backend has exactly one private conversion: `STRICT_UTF16LE -> STRICT_UTF8`.
It requires exact `bytes`, non-empty input, the existing 4096-byte raw bound,
even byte length, and no leading UTF-16 BOM in either byte order. Strict
UTF-16LE decoding must produce non-empty text without U+0000. Strict UTF-8
encoding must produce non-empty bytes within the same 4096-byte bound.

The logical password is unchanged, including leading/trailing whitespace,
Unicode form, case, and line endings. There is no encoding autodetection,
raw UTF-8 fallback, alternate encoding, repair, replacement, normalization,
trimming, or retry. Interior U+FEFF is preserved as password data; a leading
BOM is rejected. Public field names and failure categories remain unchanged.

S2-RO-09 passes these transport-ready bytes exactly to
`transport.auth_password(username, secret, event=..., fallback=False)`.
It performs no credential decoding, alternate encoding, or fallback
authentication. Neither its production code nor its tests change here.

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

`GUARANTEED_PYTHON_MEMORY_ZEROIZATION = NO`: the conversion may transiently
create raw Windows bytes, a decoded Python string, and canonical UTF-8 bytes.
All must remain ephemeral and must never be logged or persisted. Python
immutable `bytes` and `str` provide no reliable underlying-memory zeroization.
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
- `CREDENTIAL_SECRET_INVALID` for wrong type, empty, odd-length, BOM-bearing,
  malformed UTF-16LE, or decoded U+0000 input;
- `CREDENTIAL_SECRET_TOO_LARGE` for raw or canonical UTF-8 bytes above the bound.

API and encoding exceptions become sanitized backend errors outside their
exception handlers, with no native cause/context or representation detail in
the public error. There is no retry, alternate target, or fallback lookup.

## Sanitized integration finding

Two separately authorized Lab2 attempts passed pinned host-key verification
but failed password authentication; no remote command executed. An authorized
offline Owner-secret comparison established that the stored bytes matched
UTF-16LE and did not match UTF-8. The accepted source returned raw Windows
bytes from S2-RO-04 and supplied them unchanged to S2-RO-09 authentication.
This remediation corrects only that representation handoff. No credential
store or device is accessed during this offline implementation or validation.

`POST_REMEDIATION_LIVE_AUTHENTICATION_RESULT = NOT_YET_VERIFIED`

Independent read-only review and any later live retry require separate Owner
authorization. Offline test success does not establish S2-RO-09 compatibility.

## Offline reviewer evidence

Focused tests use only a synthetic target, username, and secret with an injected
fake API. They prove:

- both exact target-bound identities perform exactly one read;
- ASCII, non-ASCII (including distinct Unicode forms), and whitespace passwords
  yield exact UTF-8 bytes from synthetic UTF-16LE input for both targets;
- raw and canonical size bounds are enforced independently;
- odd length, either BOM, unpaired surrogates, and decoded U+0000 reject without
  encoding fallback and with sanitized unchained errors;
- the fake native DLL copies bytes before `CredFree`; backend conversion occurs
  after freeing the test-owned Windows allocation, including rejection paths;
- the 16-case target/credential/binding-locator/configuration-locator matrix
  admits only the two fully matched combinations, with zero calls otherwise;
- legacy Lab1 calls still work and cannot retrieve Lab2 credentials;
- unknown, alias, prefix, case-confused, malformed, and caller-override inputs
  reject before the reader, without a default or fallback;
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
- behavioral tests inject a fake reader; the existing native-layout tests use
  a fake DLL and test-owned memory, never the real credential store. An autouse
  test guard denies real Windows library loading unless a test installs its
  deterministic fake boundary.

Validation order is focused S2-RO-04 tests, unchanged focused S2-RO-09 tests,
all `tests/stage2`, full pytest, report-index, and `git diff --check`. Python runs use `-B`; pytest disables its
cache provider. Validation uses an external disposable copy of the exact
candidate, without dependency downloads or source-worktree runtime artifacts.
The source worktree must retain its pre-validation HEAD/tree, clean status, and
file content/size/mtime during sandbox validation. Only the three authorized
backend/test/document files are applied afterward, before the separately
authorized single local implementation commit.

Windows runs follow the existing guarded, non-TTY policy described in the
[S2-RO-09 validation evidence](stage2_vrrp_readonly_s2_ro_09_pinned_ssh_transport.md):
native/network/process guards precede pytest import; plugin autoload and cache
are disabled, with guards retained in Python/Node regression children. Test
results must not render synthetic passwords in failure output.

Every test suite requires zero failures. Only the existing accepted safety
skips may remain; this remediation adds none. Report-index may retain WARN only
for optional missing artifacts, with no mandatory failure. This remediation
does not remediate unrelated
CI maintenance warnings or constitute independent review PASS.

## Explicit exclusions

This slice does not implement or authorize known-hosts handling, host-key trust,
TOFU, `AutoAddPolicy`, a VRRP parser, Paramiko, sockets, DNS, SSH, NETCONF,
RESTCONF, HTTP, live commands, live-device access, evidence serialization, or
S2-RO-05 and later capabilities.

No real Credential Manager target, username, password, or secret is committed.
No real credential store was probed. The bounded implementation authorization
permits one local commit only after validation passes. Push, pull request,
merge, branch/worktree cleanup, and S2-RO-05 or later Lab2 work still require
separate Owner authorization. No Lab2 credential record, known-host data,
authorization package, replay access, private-key access, live attempt, or
Stage-3 work is authorized here.
