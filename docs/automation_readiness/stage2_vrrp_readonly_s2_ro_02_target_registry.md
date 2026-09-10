# S2-RO-02 fixed target registry

## Decision summary

**S2-RO-02 supports the exact Lab1 and Lab2 logical identities in an immutable,
offline registry. Legacy Lab1 setup remains compatible. The Lab2 extension is
a bounded candidate for independent review, not live authorization.**

Trusted setup may supply the complete fixed pair or retain the legacy Lab1
record. Each exact reference resolves only to its own fixed IPv4 endpoint.
The registry performs no I/O and grants no authority to contact either endpoint.
Lab1 authority is not Lab2 authority. Historical Stage-2 Lab1 closure remains
CLOSED / LIVE PROVEN; this extension establishes no Lab2 live evidence and
does not start Stage 3.

`DECLARED_LAB_ONLY != PROVEN_NON_PRODUCTION_DEVICE`

`VALID TARGET LOOKUP != LIVE ACCESS AUTHORIZATION`

## Fixed boundary

The implementation is
`validation_framework.stage2_mikrotik_target_registry`. Only these two logical
references are supported; they do not identify public physical endpoints:

```text
target.mikrotik.lab01
target.mikrotik.lab02
```

Its immutable endpoint has exactly five fields:

| Field | Required value or boundary |
| --- | --- |
| `target_ref` | Exactly `target.mikrotik.lab01` or `target.mikrotik.lab02` |
| `address` | Canonical plain IPv4 literal supplied by trusted setup |
| `port` | Exact integer `22` |
| `transport` | Exact string `SSH` |
| `declared_lab_only` | Exact Boolean `true` |

IPv6 remains intentionally excluded by the existing endpoint policy.
Hostnames, DNS names, malformed addresses, embedded ports, CIDR,
URIs, whitespace, control characters, paths, alternate ports, and non-string
addresses fail closed.

The documentation-only examples `192.0.2.10` and `198.51.100.20` are from
TEST-NET-1 and TEST-NET-2. Neither is a real lab endpoint. Real addresses must be supplied
later by trusted, Owner-controlled provisioning outside Git and must never be
committed in source, tests, documentation, or generated public evidence.

## Trusted construction versus request lookup

`parse_stage2_fixed_target_registry` accepts either one already-decoded plain
Lab1 dictionary (legacy mode) or a plain list of exactly two dictionaries,
one for Lab1 and one for Lab2, in either order. Pair mode requires both targets
and distinct addresses; a missing target, duplicate identity, shared endpoint,
third target, extra field, or inventory wrapper fails closed. A standalone
Lab2 dictionary is not legacy Lab1 setup and is rejected.

It is not a request parser and it
does not establish provenance. The future request path must receive an already
constructed registry and may pass only the S2-RO-01 `target_ref` to `lookup`.

Caller-supplied address, hostname, port, transport, credential, host-key,
fallback, or discovery fields therefore have no request path. S2-RO-01 already
rejects endpoint override fields, and the composition test confirms lookup uses
only its accepted logical target reference.

The frozen representation holds dedicated Lab1 and optional Lab2 endpoint
fields, not a mutable inventory. No input dictionary or list is retained.
There is no
registration, add, remove, replace, update, alias, search, prefix match,
default, discovery, or fallback API.

`STAGE2_FIXED_TARGET_REF` still means Lab1; `STAGE2_SECOND_TARGET_REF` means
Lab2. Existing `Stage2FixedTargetRegistry(lab1_endpoint)` construction and its
`_endpoint` Lab1 field remain compatible. Explicit pair construction is
`Stage2FixedTargetRegistry(lab1_endpoint, lab2_endpoint)`; reversed or duplicate
constructor slots reject. The parser alone accepts either input order.

S2-RO-10 currently captures `_endpoint` and reconstructs a Lab1 singleton.
That behavior remains unchanged: pair availability must not be interpreted as
Lab2 runtime support. S2-RO-03 credential binding, authorization, trust, command
policy, transport, and later runtime/entrypoint modules are not expanded here.

## Exact lookup and failures

Lookup uses exact case-sensitive equality. It performs no trimming or
normalization. Valid but different logical references produce `UNKNOWN_TARGET`;
malformed or non-canonical references produce `INVALID_TARGET_REFERENCE`.
Invalid endpoint shape or policy produces `INVALID_REGISTRY_CONFIGURATION`.

Errors retain only these bounded categories and never echo rejected data.

## Immutability and serialization decision

`Stage2FixedTargetEndpoint` and `Stage2FixedTargetRegistry` are frozen, slotted
dataclasses. Stored state consists only of immutable scalars and frozen
endpoints. Input-dictionary/list mutation cannot change a constructed registry, and
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

S2-RO-01 remains unchanged. Changes to S2-RO-03 and later capabilities are
unauthorized in this extension. No real Lab2 endpoint asset is created.

## Verification and next gate

Focused tests cover exact Lab1/Lab2 lookup, legacy singleton compatibility,
complete-pair validation, duplicates, missing setup, third-target rejection,
no cross-target substitution, fixed port and transport,
IPv4-only parsing, malformed and hostname rejection, immutable state, bounded
failures, no fallback, S2-RO-01 composition, request override rejection, and
AST-based proof that no external boundary or live runtime surface exists.
Rejected lookups also prove no downstream handoff in a synthetic composition.

Acceptance requires focused S2-RO-02 and Stage-2 regression tests to pass,
full pytest to have zero failures, report-index to have no mandatory failure,
and the diff to contain only this registry, its existing test file, and this
document. Full validation uses the exact candidate in a disposable local
sandbox when reports could alter files. Any safety-gated native/network tests
skipped during offline validation must be disclosed, not claimed as proven.

After validation and the separately Owner-authorized single local commit, the
next state is `READY_FOR_INDEPENDENT_S2_RO_02_LAB2_REVIEW`. This grants no push,
PR, merge, later-slice implementation, credential/trust/replay provisioning,
dual-device aggregation, or live access authority.
