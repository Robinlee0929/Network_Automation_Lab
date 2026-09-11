# S2-RO-04 Windows Credential Backend

## Decision summary

S2-RO-04 extends only the trusted policy wrapper to accept the two exact
S2-RO-03 target/credential bindings, each with its matching trusted locator.
Legacy `read(binding)` remains Lab1-only; `read_for_target(target_ref, binding)`
checks the exact pair through S2-RO-03 before comparing configuration identity.
The native Windows reader is unchanged. This is an **offline policy extension**,
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
bounded ephemeral credential material
                    |
                    v
future transport (not implemented)
```

S2-RO-04 owns bounded credential retrieval policy only. Endpoint selection, authorization,
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

- both exact target-bound identities perform exactly one read;
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

Validation order is focused S2-RO-04 tests, all `tests/stage2`, full pytest,
report-index, and `git diff --check`. Python runs use `-B`; pytest disables its
cache provider. Validation uses an external disposable copy of the exact
candidate, without dependency downloads or source-worktree runtime artifacts.
The source worktree must retain its pre-validation HEAD/tree, clean status, and
file content/size/mtime during sandbox validation. Only the three authorized
backend/test/document files are applied afterward, before the separately
authorized single local implementation commit.

Every test suite requires zero failures. Existing platform-specific skips are
acceptable. Report-index may retain WARN only for optional missing artifacts,
with no mandatory failure. This policy extension does not remediate unrelated
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
