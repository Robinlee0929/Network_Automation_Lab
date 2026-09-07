# S2-RO-08: Immutable VRRP read-only command policy

## Decision summary

S2-RO-08 is the offline, code-native positive command policy for the one
accepted Stage-2 operation, `mikrotik.vrrp_status`. Its future implementation
will map that exact operation to the exact RouterOS command
`/interface/vrrp/print` and issue an immutable, non-authorizing command
specification for the separately gated S2-RO-09 transport.

This document defines scope only. It does not implement S2-RO-08, create a
command execution path, or authorize S2-RO-09.

`VALID COMMAND POLICY != EXECUTION AUTHORIZATION`

`S2-RO-08 DEFINED != S2-RO-08 IMPLEMENTED`

`S2-RO-08 IMPLEMENTED OFFLINE != S2-RO-09 TRANSPORT AUTHORIZED`

## Canonical reference basis

The scope decision was made at
`main@a945bfe3642663b813eaa8e71db72232a925801f` after reading 11 canonical
governing references:

1. `AGENTS.md`;
2. `README.md`, including the Stage-2 and safety sections;
3. `docs/automation_readiness/actual_automation_integration_plan.md`;
4. `docs/automation_readiness/stage2_live_authorization_owner_trust_root.md`;
5. the seven canonical S2-RO-01 through S2-RO-07 documents.

Five supplementary references were also read: the S2-RO-02 endpoint
implementation, S2-RO-07 implementation, and S2-RO-07 synthetic validation
module directly cited by the S2-RO-07 record, plus the retained Day88 command
allowlist design and Day89 adapter safety-boundary record. These supporting
records establish the pre-existing `/interface/vrrp/print`, positive-allowlist,
and default-deny design evidence; they do not supersede the 11 canonical
governing references.

`CANONICAL_REFERENCE_COUNT = 11`

No separate S2-RO sequence or manifest existed at that base. The canonical
sequence is now indexed in the Stage-2 section of the actual automation
integration plan.

## Completed capability matrix

All `LIVE ACCESS`, `SECRET ACCESS`, and `TRANSPORT` values describe capability
present in the completed slice, not whether this documentation review used it.

| Slice | Objective | New abstraction or contract | Inputs | Outputs | Exact lookup or fail-closed property | Live access | Secret access | Transport | Next dependency exposed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2-RO-01 | Fix one protocol-neutral VRRP observation request and normalized evidence shape | Immutable request, record, and evidence contracts | Exact plain records or canonical JSON | Validated request or normalized evidence | Exact fields, operation, references, bounds, and byte-canonical JSON; no coercion | NO | NO | NO | Fixed target resolution |
| S2-RO-02 | Bind one logical target to one lab endpoint | Immutable singleton target registry and endpoint | Trusted fixed endpoint record; exact `target_ref` lookup | One IPv4/22/SSH endpoint | Exact case-sensitive lookup; no alias, DNS, discovery, or fallback | NO | NO | NO | Credential identity resolution |
| S2-RO-03 | Bind one logical credential reference to one backend identity | Immutable offline credential resolver and non-secret binding | Exact `credential_ref` | Fixed backend kind and opaque locator | One exact reference; no default, enumeration, alternate backend, or fallback | NO | NO | NO | Bounded credential retrieval |
| S2-RO-04 | Read the one accepted binding from Windows Credential Manager | Trusted target configuration, exact backend, and ephemeral credential contract | Exact S2-RO-03 binding plus trusted runtime target configuration | Bounded username and immutable secret bytes | Backend/locator/target fixed before one read; no enumeration, mutation, retry, or fallback | NO | YES | NO | Authorization envelope and replay control |
| S2-RO-05 | Bind a short-lived single-attempt approval and consume it durably | Immutable authorization envelope, exact Owner payload, and append-only replay ledger | Envelope, S2-RO-01 request, registry, credential binding, trusted clock and ledger | Permanent consumption record or bounded failure | Exact digests/bindings/time/schema; atomic UUID-only replay barrier; no repair or reuse | NO | NO | NO | Owner authenticity verification before consumption |
| S2-RO-06 | Authenticate the exact S2-RO-05 Owner payload | Exact approval source, Ed25519 verifier, and immutable verification result | Acquired trust root and exact envelope-linked approval artifact | Verified approval facts with `execution_authorized=False` | Exact file derivation, issuer, algorithm, signature, and payload; no search, alternate key, or fallback | NO | NO | NO | Pinned server host trust |
| S2-RO-07 | Acquire immutable, endpoint-bound host-key facts | Same-handle known-host source acquisition and immutable snapshot | Trusted source pins and exact S2-RO-02 endpoint | Pinned `ssh-ed25519` complete-blob identity with `execution_authorized=False` | Exact path/FileId/hash/endpoint/key; no ambient known-hosts, TOFU, rotation, or fallback | NO | NO | NO | One positive command policy before the reserved S2-RO-09 transport |

## Gap analysis and uniqueness decision

The Stage-2 plan requires reviewer-visible read-only command allowlisting. The
S2-RO-01 contract fixes both `mikrotik.vrrp_status` and
`policy.stage2.vrrp-readonly.v1`, but deliberately contains no RouterOS command.
S2-RO-02 explicitly excludes a command allowlist, and S2-RO-03 through
S2-RO-07 provide no command policy. Historical design evidence already names
`/interface/vrrp/print` as the VRRP read-only command candidate. S2-RO-07, in
turn, reserves SSH key exchange, host verification, authentication, and network
access for S2-RO-09.

| Gap ID | Why required | Canonical evidence | Depends on S2-RO-07 | Belongs to S2-RO-09 | Requires live access | Requires secret access | Offline declarative only |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GAP-COMMAND-POLICY | S2-RO-09 must receive one pre-approved command rather than caller-selected text | Stage-2 plan requires a read-only allowlist; S2-RO-01 fixes operation/policy identities but excludes the command; S2-RO-02 excludes the allowlist | NO; it is independently bounded, but remains the outstanding prerequisite after S2-RO-07 | NO | NO | NO | YES |
| GAP-TRANSPORT | A later component must connect, verify the presented host key, authenticate, and invoke the accepted command | S2-RO-07 section “Future S2-RO-09 handoff” | YES | YES | YES | YES | NO |
| GAP-RUNTIME-COMPOSITION | The accepted contracts must eventually be ordered, revalidated, consumed, and invoked once | S2-RO-06 future sequence; S2-RO-04 explicitly names S2-RO-10 runtime composition | YES | NO | NOT PROVEN for an offline composition test; live invocation would require it | NOT PROVEN for an offline composition test; live invocation would require it | NO |
| GAP-OUTPUT-PARSER-AND-EVIDENCE | Raw RouterOS output must later become the bounded S2-RO-01 evidence shape | S2-RO-01 defers parsing and authentic-output checks to later parser/transport slices | NO | NO; it follows transport output | NO when fixture-tested | NO | YES, but it is not a pre-transport prerequisite |
| GAP-OWNER-PROVISIONING | A real run would require Owner-controlled external records, pins, ACLs, ledger, approval, credential, and known-host material | S2-RO-04 through S2-RO-07 state these deployment preconditions and exclude provisioning | YES for real operation | NO | NOT PROVEN; provisioning is an operational gate | YES for real credential provisioning | NO |

Only `GAP-COMMAND-POLICY` satisfies every S2-RO-08 uniqueness condition. It is
required before transport, absent from S2-RO-01 through S2-RO-07, outside the
reserved S2-RO-09 transport, independently bounded, fail-closed, testable with
pure offline data, and compatible with the fixed read-only operation.

`UNIQUE_SAFE_S2_RO_08_SCOPE_FOUND = YES`

## Objective and problem statement

Objective: define and, under a later separate authorization, implement one
immutable positive policy that converts the exact accepted Stage-2 operation
identity into one reviewer-visible command specification without accepting any
command text from a request or caller.

Problem: S2-RO-01 identifies the requested observation and the expected command
policy version, but no completed slice owns the command that S2-RO-09 may
invoke. Letting transport invent, normalize, or accept that command would merge
policy with execution and would permit caller-selected command text. S2-RO-08
closes that gap before any transport exists.

## Prerequisites

- S2-RO-01 remains the authority for exact operation ID, read-only intent, and
  command policy version.
- S2-RO-02 through S2-RO-07 remain accepted and unchanged.
- The Stage-2 rule remains one lab target, one transport, a positive read-only
  allowlist, normalized bounded evidence, and no configuration mutation.
- S2-RO-09 remains a separate future transport gate.
- S2-RO-10 remains the later runtime-composition boundary.

## First bounded implementation slice

The first separately authorized implementation must be exactly one production
module, one synthetic test module, and the existing canonical document updated
from definition status to implementation-candidate status:

```text
validation_framework/stage2_vrrp_readonly_command_policy.py
tests/stage2/test_vrrp_readonly_command_policy.py
docs/automation_readiness/stage2_vrrp_readonly_s2_ro_08_command_policy.md
```

No existing S2-RO source or test should need modification. If safe
implementation requires another production module, external dependency,
transport behavior, credential access, or an existing-contract change, that
implementation must stop for a new scope decision.

## Allowed boundary

The future S2-RO-08 implementation may:

- import the fixed S2-RO-01 operation and command-policy identifiers;
- define one code-native singleton positive policy;
- accept only the exact S2-RO-01 request, with no caller command field;
- map `mikrotik.vrrp_status` to exactly `/interface/vrrp/print`;
- return one immutable command specification containing only exact policy
  metadata and the fixed command text;
- expose bounded sanitized failure categories;
- validate and test all behavior entirely in memory.

The command specification must contain exactly:

| Field | Exact contract |
| --- | --- |
| `schema_version` | `s2-ro-08.command-policy.v1` |
| `operation_id` | `mikrotik.vrrp_status` |
| `command_policy_version` | `policy.stage2.vrrp-readonly.v1` |
| `command_text` | `/interface/vrrp/print` |
| `read_only` | Exact Boolean `true` |
| `execution_authorized` | Exact Boolean `false` |

No timeout, retry, endpoint, transport, username, credential, host key,
authorization, output, parser, or mutable policy field belongs in this slice.
Those authorities already belong elsewhere or remain separately gated.

## Forbidden scope

S2-RO-08 may not add or perform:

- caller-supplied command text, command fragments, arguments, filters,
  normalization, interpolation, concatenation, shell syntax, aliases, wildcard
  matching, prefix matching, discovery, enumeration, dynamic registration,
  multiple commands, defaults, or fallback;
- caller-selected endpoint, transport, backend, credential, policy version, or
  execution mode;
- Windows Credential Manager calls, credential existence probes, username or
  password retrieval, secret access, host-key acquisition, approval reads, or
  replay-ledger access;
- SSH, NETCONF, RESTCONF, sockets, DNS, subprocesses, RouterOS connections,
  command execution, output collection, parsing, or live-device access;
- runtime composition, CLI/task/runner registration, queue/scheduler/worker/AI
  loops, provider or model APIs, configuration backup/change, or production
  execution;
- a dependency addition or modification of S2-RO-01 through S2-RO-07.

## Input and output contracts

The only command-resolution operation is expected to be
`resolve_stage2_vrrp_readonly_command(request)`. It consumes one exact
S2-RO-01 `Stage2VrrpObservationRequest`, revalidates the exact concrete type and
all fixed fields, and accepts no other parameter. Subclasses, lookalikes,
reconstructed invalid objects, scalar subclasses, missing dependencies, and
requests with an unknown or altered operation reject before a specification is
issued.

The lookup returns one exact immutable command-specification type. It is policy
data for S2-RO-09, not a transport callback, callable, shell argument list, or
execution ticket. It must have a bounded representation and no mutable export,
serialization requirement, or authority-bearing handle.

## Fail-closed conditions

The future implementation must reject with bounded sanitized categories before
returning a specification when any of these conditions occurs:

- the operation reference is malformed, unknown, noncanonical, or not exact;
- the S2-RO-01 request/type/identifier dependency is missing, altered, or
  unavailable;
- zero, duplicate, conflicting, or ambiguous policy bindings exist;
- the request is not exact read-only mode, or an unsupported mode, backend, or
  transport selection is presented;
- policy schema, version, command text, Boolean fields, or internal
  configuration is malformed or changed;
- a caller attempts to supply or override command text, arguments, endpoint,
  backend, transport, policy version, retry, timeout, or fallback behavior;
- the immutable policy or command-specification prerequisite cannot be
  established.

There is no silent repair, coercion, normalization, default command, default
credential, alternate policy, discovery, alias lookup, dynamic registration,
or fallback.

## Immutability and security boundary

The policy and issued specification must use immutable scalar state and exact
types. The implementation must prevent supported mutation, subclass
substitution, mutable-container leakage, copy-based alteration, dataclass
replacement, and reconstruction from creating an accepted altered policy.

The exact fixed command must be reviewer-visible in code and documentation.
It must contain no control characters, line breaks, separators, chaining,
redirection, interpolation, write verbs, export, secret-bearing selectors, or
caller data. A valid specification always reports `execution_authorized=False`.
Possession of the specification grants no target, credential, approval, host
trust, transport, or execution authority.

## Access classification

| Capability | Required by S2-RO-08 | Reason |
| --- | --- | --- |
| Windows Credential Manager access | NO | S2-RO-04 already owns credential retrieval; command policy uses identifiers only |
| Credential existence probe | NO | Policy validity is independent of a deployed credential |
| Username retrieval | NO | No identity material belongs in a command specification |
| Password retrieval | NO | No secret material belongs in a command specification |
| Secret access | NO | The mapping is fixed code-native policy data |
| SSH | NO | Reserved for S2-RO-09 |
| NETCONF | NO | Outside the fixed Stage-2 transport boundary |
| RESTCONF | NO | Outside the fixed Stage-2 transport boundary |
| Socket or DNS | NO | The policy has no endpoint or network operation |
| Live device | NO | Exact mapping and validation are fully offline |
| Provider or model API | NO | No external decision or lookup is required |
| Fully offline implementation | YES | Standard-library immutable data and exact lookup are sufficient |

## Required test classes

A separately authorized implementation must include:

- exact public surface and exact valid mapping tests;
- exact S2-RO-01 request/operation/policy-version composition tests;
- malformed, unknown, near-match, case, whitespace, control, Unicode,
  subclass, lookalike, and wrong-type rejection tests;
- missing, duplicate, ambiguous, altered-policy, unsupported-mode/backend, and
  unavailable-prerequisite fail-closed tests;
- caller override, alias, default, discovery, enumeration, registration,
  normalization, interpolation, and fallback absence tests;
- immutable state, safe representation, copy/reconstruction, and
  `execution_authorized=False` tests;
- static import/call-surface tests proving no credential, filesystem, native,
  subprocess, network, transport, parser, runtime, provider, or entrypoint
  capability;
- S2-RO-01 through S2-RO-07 regression, full pytest, report-index, diff, and
  tracked-cleanliness validation under the repository safety procedure.

All behavioral tests must use synthetic in-memory values. No test may open a
credential store, approval source, known-host source, socket, protocol client,
device, provider, or model API.

## Completion criteria and S2-RO-09 handoff

S2-RO-08 is complete only when the later separately authorized three-file
implementation passes focused tests, all Stage-2 regressions, full repository
validation, report-index policy review, complete-diff review, independent
security review, and documentation review with no unresolved material finding.
The exact mapping and all forbidden capabilities must remain reviewer-visible.

S2-RO-09 may later accept only the exact S2-RO-08 issued specification together
with its separately accepted endpoint, known-host snapshot, credential path,
and authorization/runtime inputs. Before network access, S2-RO-09 must
revalidate the exact specification type and every immutable field. It may
invoke only the exact command once, with no retry, fallback, mutation, shell,
or caller override. S2-RO-09 remains responsible for transport, key exchange,
server-signature verification, exact complete-host-key comparison,
authentication, bounded I/O, and cleanup.

S2-RO-08 does not implement any part of that handoff.

## Conservation decision

```text
S2_RO_09_TRANSPORT_BOUNDARY_PRESERVED = YES
S2_RO_08_DOES_NOT_IMPLEMENT_TRANSPORT = YES
S2_RO_08_DOES_NOT_OPEN_SSH = YES
S2_RO_08_DOES_NOT_OPEN_NETCONF = YES
S2_RO_08_DOES_NOT_OPEN_RESTCONF = YES
S2_RO_08_DOES_NOT_CREATE_SOCKET_CAPABILITY = YES
S2_RO_07_CONTRACT_CHANGED = NO
S2_RO_07_KNOWN_HOST_SNAPSHOT_SEMANTICS_CHANGED = NO
S2_RO_07_CREDENTIAL_RESOLVER_SEMANTICS_CHANGED = NO
```

The next permitted action after this scope-definition commit is a separate
Owner decision on the S2-RO-08 first bounded implementation slice. No
implementation, push, pull request, merge, production provisioning, or
S2-RO-09 work is authorized by this document.

## References

- [Actual automation integration plan and canonical sequence](actual_automation_integration_plan.md)
- [S2-RO-01 request and evidence contract](stage2_vrrp_readonly_s2_ro_01_contract.md)
- [S2-RO-02 fixed target registry](stage2_vrrp_readonly_s2_ro_02_target_registry.md)
- [S2-RO-03 credential resolver](stage2_vrrp_readonly_s2_ro_03_credential_resolver.md)
- [S2-RO-04 Windows Credential Manager backend](stage2_vrrp_readonly_s2_ro_04_windows_credential_backend.md)
- [S2-RO-05 authorization envelope and replay ledger](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md)
- [S2-RO-06 Owner verifier](stage2_vrrp_readonly_s2_ro_06_owner_verifier.md)
- [S2-RO-07 known-host snapshot and S2-RO-09 handoff](stage2_vrrp_readonly_s2_ro_07_known_host_snapshot.md)
- [Retained Day88 command allowlist design](../ai/intent_real_readonly_executor_adapter_design.md)
- [Retained Day89 adapter safety boundary](../ai/real_adapter_safety_boundary_spec.md)
