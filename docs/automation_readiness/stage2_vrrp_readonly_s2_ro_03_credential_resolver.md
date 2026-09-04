# S2-RO-03 Credential Resolver

## Decision summary

S2-RO-03 implements one immutable, fully offline credential-identity resolver.
It maps the accepted synthetic logical reference
`credential.mikrotik.lab01` to one fixed non-secret binding for a future
backend. It does not retrieve credentials, contact Windows Credential Manager,
read secret material, or create network capability.

Status: implementation candidate ready for independent review after validation.

## Purpose and position in the flow

The resolver is an authority boundary for credential identity only:

```text
S2-RO-01 request credential_ref
              |
              v
S2-RO-03 exact offline resolver
              |
              v
immutable non-secret binding
              |
              v
future S2-RO-04 backend (not implemented)
```

S2-RO-01 remains the request/evidence authority. S2-RO-02 remains the fixed
target and endpoint authority. S2-RO-03 neither changes nor broadens either
closed slice.

## Allowed scope

The resolver supports exactly one logical credential reference:

```text
credential.mikrotik.lab01
```

Lookup uses exact equality after applying the compatible S2-RO-01 logical
identifier rules. Invalid or unknown values fail closed through bounded,
sanitized error categories that do not retain rejected input.

The immutable result has exactly three fields:

- `credential_ref`: the accepted logical identity;
- `backend_kind`: the fixed declarative backend identity
  `WINDOWS_CREDENTIAL_MANAGER`;
- `locator_ref`: the fixed synthetic opaque locator
  `locator.stage2.mikrotik.lab01.readonly`.

These are identity and routing metadata only. They contain no credential
material and provide no proof that a backend record exists.

```text
DECLARED_BACKEND_BINDING != CREDENTIAL_RETRIEVAL
```

## Rejection and no-fallback boundary

The resolver rejects:

- unknown, prefix, suffix, and near-match references;
- case, whitespace, and control-character variants;
- malformed, path-like, URI-like, glob, and shell-like values;
- references that resemble embedded credential material;
- attempts to construct a different backend or locator.

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

S2-RO-03 does not inspect or select an address, target, port, or transport. It
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
WINDOWS_CREDENTIAL_BACKEND_IMPLEMENTED = NO
LIVE_COMMAND_EXECUTION_PRESENT = NO
```

## Reviewer evidence

Focused tests cover:

- exact deterministic resolution of the one credential reference;
- immutable resolver and binding objects;
- exact output fields and non-secret synthetic values;
- unknown and malformed fail-closed cases;
- absence of aliases, defaults, discovery, enumeration, and mutation APIs;
- S2-RO-01 request composition without mutation;
- rejection before any future backend boundary;
- S2-RO-02 endpoint-authority isolation;
- static absence of Windows credential, filesystem, subprocess, network, and
  serialization capabilities.

Validation also includes the accepted S2-RO-01 and S2-RO-02 focused regression
suites, full pytest, report-index policy evaluation, complete-diff review, and
tracked-file cleanliness verification.

## Explicit exclusions

This slice does not implement S2-RO-04 or later capabilities. It does not
retrieve a username or secret, access a credential backend, establish host-key
trust, parse RouterOS output, implement Paramiko transport, compose a runtime,
register a live entrypoint, contact a device, or authorize live SSH.

Independent review, commit, push, pull request, merge, branch cleanup, and the
start of S2-RO-04 all require separate Owner authorization.
