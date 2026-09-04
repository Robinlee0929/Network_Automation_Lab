# S2-RO-02 fixed target registry

## Decision summary

**S2-RO-02 implements one immutable, offline target registry for the future
MikroTik VRRP read-only lab workflow. It is an uncommitted candidate ready only
for independent review after validation.**

The registry maps exactly one logical target reference to one fixed IPv4
endpoint record. It performs no I/O and grants no authority to contact that
endpoint.

`DECLARED_LAB_ONLY != PROVEN_NON_PRODUCTION_DEVICE`

`VALID TARGET LOOKUP != LIVE ACCESS AUTHORIZATION`

## Fixed boundary

The implementation is
`validation_framework.stage2_mikrotik_target_registry`. The one supported
logical reference is synthetic:

```text
target.mikrotik.lab01
```

Its immutable endpoint has exactly five fields:

| Field | Required value or boundary |
| --- | --- |
| `target_ref` | Exactly `target.mikrotik.lab01` |
| `address` | Canonical plain IPv4 literal supplied by trusted setup |
| `port` | Exact integer `22` |
| `transport` | Exact string `SSH` |
| `declared_lab_only` | Exact Boolean `true` |

IPv6 is intentionally excluded because the first planned lab device does not
require it. Hostnames, DNS names, malformed addresses, embedded ports, CIDR,
URIs, whitespace, control characters, paths, alternate ports, and non-string
addresses fail closed.

The documentation-only example address `192.0.2.10` is from TEST-NET-1. It is
not a real lab endpoint. A real environment-specific address must be supplied
later by trusted, Owner-controlled provisioning outside Git and must never be
committed in source, tests, documentation, or generated public evidence.

## Trusted construction versus request lookup

`parse_stage2_fixed_target_registry` accepts exactly one already-decoded plain
record from a future trusted setup boundary. It is not a request parser and it
does not establish provenance. The future request path must receive an already
constructed registry and may pass only the S2-RO-01 `target_ref` to `lookup`.

Caller-supplied address, hostname, port, transport, credential, host-key,
fallback, or discovery fields therefore have no request path. S2-RO-01 already
rejects endpoint override fields, and the composition test confirms lookup uses
only its accepted logical target reference.

The registry representation is one endpoint record, not a target list or
mapping. Duplicate target declarations are therefore structurally impossible;
lists, inventory wrappers, and multi-record inputs are rejected. There is no
registration, add, remove, replace, update, alias, search, prefix match,
default, discovery, or fallback API.

## Exact lookup and failures

Lookup uses exact case-sensitive equality. It performs no trimming or
normalization. Valid but different logical references produce `UNKNOWN_TARGET`;
malformed or non-canonical references produce `INVALID_TARGET_REFERENCE`.
Invalid endpoint shape or policy produces `INVALID_REGISTRY_CONFIGURATION`.

Errors retain only these bounded categories and never echo rejected data.

## Immutability and serialization decision

`Stage2FixedTargetEndpoint` and `Stage2FixedTargetRegistry` are frozen, slotted
dataclasses. Stored state consists only of immutable scalars and one frozen
endpoint. Input-dictionary mutation cannot change a constructed registry, and
the registry exposes no mutable mapping.

Serialization is deliberately absent. S2-RO-02 needs only trusted construction
and exact in-memory lookup. An export API would create another place where a
future real address could be copied or published without helping this slice.

## Lab-only declaration is not proof

`declared_lab_only=true` records trusted setup intent for later authorization
composition. The registry does not inspect the device or network and cannot
prove that an address belongs to a lab, is non-production, or is safe to
contact. That attestation and the exact live target remain future authorization
requirements.

## Explicit exclusions

This slice contains no:

- socket creation, DNS resolution, discovery, ping, HTTP, SSH, NETCONF, or
  RESTCONF operation;
- Paramiko or other transport dependency;
- username, password, credential resolver, Windows Credential Manager access,
  secret enumeration, or credential binding;
- host key, fingerprint, known-hosts path, trust-on-first-use, or host-key
  policy;
- authorization envelope, Owner signature verification, replay ledger, command
  allowlist, RouterOS output parser, runtime composition, or live entrypoint;
- configuration file loader, environment override, hot reload, serialization,
  generated evidence, runner, CLI, queue, scheduler, worker, or AI loop.

S2-RO-01 remains unchanged. S2-RO-03 and later capabilities remain unauthorized.

## Verification and next gate

Focused tests cover exact lookup, singleton structure, fixed port and transport,
IPv4-only parsing, malformed and hostname rejection, immutable state, bounded
failures, no fallback, S2-RO-01 composition, request override rejection, and
AST-based proof that no external boundary or live runtime surface exists.

After focused, S2-RO-01 regression, full pytest, report-index, diff, and tracked
cleanliness validation pass, the only next state is
`READY_FOR_S2_RO_02_INDEPENDENT_REVIEW`. It does not authorize a commit, push,
PR, merge, S2-RO-03 implementation, or live access.
