# S2-RO-03 Credential Resolver

## Decision summary

S2-RO-03 implements one immutable, fully offline credential-identity resolver.
It validates exactly two fixed target/credential pairs with distinct synthetic
credential identities and locators. The existing credential-only API remains
Lab1-only for downstream compatibility. It does not retrieve credentials, contact Windows Credential Manager,
read secret material, or create network capability.

Status: implementation candidate ready for independent review after validation.

## Purpose and position in the flow

The resolver is an authority boundary for credential identity only:

```text
S2-RO-01 request target_ref + credential_ref
              |
              v
S2-RO-03 exact offline resolver
              |
              v
immutable non-secret binding
              |
              v
STOP: no backend is called by S2-RO-03
```

S2-RO-01 remains the request/evidence authority. S2-RO-02 remains the fixed
target and endpoint authority. S2-RO-03 neither changes nor broadens either
closed slice.

## Allowed scope

The target-aware API supports exactly these two fixed pairs:

```text
target.mikrotik.lab01 -> credential.mikrotik.lab01
target.mikrotik.lab02 -> credential.mikrotik.lab02
```

Lookup uses exact equality after applying the compatible S2-RO-01 logical
identifier rules. Invalid or unknown values fail closed through bounded,
sanitized error categories that do not retain rejected input.

The immutable result has exactly three fields:

- `credential_ref`: the accepted logical identity;
- `backend_kind`: the fixed declarative backend identity
  `WINDOWS_CREDENTIAL_MANAGER`;
- `locator_ref`: the matching fixed synthetic opaque locator,
  `locator.stage2.mikrotik.lab01.readonly` or
  `locator.stage2.mikrotik.lab02.readonly` respectively.

These are identity and routing metadata only. They contain no credential
material and provide no proof that a backend record exists.

```text
DECLARED_BACKEND_BINDING != CREDENTIAL_RETRIEVAL
```

## API and backward compatibility

`build_stage2_fixed_credential_resolver()` still takes no arguments. It now
constructs both immutable bindings, with no configurable Lab2 slot. The legacy
`Stage2FixedCredentialResolver(lab1_binding)` constructor remains compatible and
requires the exact Lab1 binding in its original slot.

- `resolve(credential_ref)` preserves the original Lab1-only behavior and
  three-field result. It still rejects Lab2. This compatibility API has never
  validated a target; it must not be used to validate new target/credential pairs.
- `resolve_for_target(target_ref, credential_ref)` requires both references.
  The target selects its fixed binding; the credential reference is an equality
  assertion, not an override. Both cross-Lab combinations fail closed.

There is no target default or credential default. A shared backend-kind label
does not confer shared operational credential authority: both credential and
locator identities are distinct. The resolver repr reports two fixed bindings
without displaying either locator.

S2-RO-04 still accepts only the original Lab1 locator and credential identity.
S2-RO-05 still validates Lab1-only envelopes. Existing downstream imports and
the credential-only resolver call remain compatible. No S2-RO-04 or later
production file is changed, and Lab2 runtime/backend support is not enabled.

## Rejection and no-fallback boundary

The resolver rejects:

- unknown, prefix, suffix, and near-match references;
- case, whitespace, and control-character variants;
- malformed, path-like, URI-like, glob, and shell-like values;
- references that resemble embedded credential material;
- unknown third targets or credential identities;
- either cross-Lab target/credential pair;
- mismatched credential/locator pairs, a different backend, or an arbitrary locator;
- attempts to substitute Lab2 for the constructor's Lab1 binding.

New bounded categories are `INVALID_TARGET_REFERENCE`, `UNKNOWN_TARGET`, and
`TARGET_CREDENTIAL_MISMATCH`. Existing credential/configuration categories remain
unchanged. Error messages and repr contain only the category, never rejected input.

There is no default credential, alias, fallback, alternate backend,
enumeration, discovery, list, registration, reload, environment override, or
mutable mapping. Callers cannot choose backend identity or locator dynamically.

## Secret and backend boundary

The binding contains no username, password, passphrase, private key, token,
API key, OTP, secret bytes, Windows credential blob, or real Windows
Credential Manager target. All identifiers are synthetic reviewer-visible
values.

`WINDOWS_CREDENTIAL_MANAGER` is a declarative label only. S2-RO-03 imports no
Windows credential API and performs no Credential Manager, registry, DPAPI,
PowerShell, subprocess, filesystem, or environment access. Actual credential
retrieval belongs exclusively to the separately gated S2-RO-04 slice.

## Endpoint and trust isolation

S2-RO-03 validates only the two exact logical target identities. It does not
inspect or select an address, port, or transport. It
cannot modify S2-RO-02 endpoint data and does not create a generalized
target-to-credential matrix.

The slice also contains no host-key fingerprint, known-hosts locator, trust
policy, trust-on-first-use behavior, or `AutoAddPolicy` equivalent. Host-key
authority remains future-only.

## Offline and no-execution boundary

The module has no socket, DNS, Paramiko, SSH, NETCONF, RESTCONF, HTTP, process,
filesystem, secret-store, or live-command execution path. Import, construction,
and lookup are deterministic in-memory operations.

No serialization is needed for this slice:

```text
SERIALIZATION_IMPLEMENTED = NO
WINDOWS_CREDENTIAL_ACCESS_PRESENT = NO
WINDOWS_CREDENTIAL_BACKEND_CHANGED_BY_THIS_EXTENSION = NO
LIVE_COMMAND_EXECUTION_PRESENT = NO
```

## Reviewer evidence

Focused tests cover:

- exact deterministic resolution of both target/credential pairs;
- distinct Lab1/Lab2 credential and locator identities;
- unchanged Lab1-only credential resolution for downstream callers;
- immutable resolver and binding objects;
- exact output fields and non-secret synthetic values;
- unknown, malformed, alias, prefix, case-confused and cross-Lab fail-closed cases;
- rejection of mixed credential/locator records and caller override attempts;
- absence of aliases, defaults, discovery, enumeration, and mutation APIs;
- S2-RO-01 request composition without mutation;
- cross-Lab rejection before forwarding to a downstream boundary spy;
- S2-RO-02 endpoint-authority isolation;
- static absence of Windows credential, filesystem, subprocess, network, and
  serialization capabilities.

Validation also includes Stage-2 regressions with synthetic/fake boundaries only,
full pytest, report-index policy evaluation, complete-diff review, and
tracked-file cleanliness verification.

Required offline commands (no dependency downloads):

```text
python -B -m pytest -p no:cacheprovider --tb=short tests/stage2/test_mikrotik_credential_resolver.py
python -B -m pytest -p no:cacheprovider --tb=short tests/stage2
python -B -m pytest -p no:cacheprovider --tb=short
python -B network_lab.py --task report-index
git diff --check
```

Full pytest and report-index use an external disposable copy of the exact
candidate when generated reports could affect the source worktree. Mandatory
failures are not acceptable; documented optional missing reports may remain WARN.

## Explicit exclusions

This slice does not implement S2-RO-04 or later capabilities. It does not
retrieve a username or secret, access a credential backend, establish host-key
trust, parse RouterOS output, implement Paramiko transport, compose a runtime,
register a live entrypoint, contact a device, or authorize live SSH.

The bounded local implementation authorization permits one local commit only
after all validation gates pass. Independent review, push, pull request, merge,
branch cleanup, and any Lab2 S2-RO-04 or later work require separate Owner
authorization. This extension does not create a real Lab2 credential record,
known-host data, authorization package, replay state, or Stage 3 capability.
