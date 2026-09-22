# S2-RO-10: Trusted runtime composition

## Decision summary

The bounded target-aware composition supports the fixed Lab1 + Lab2 registry,
resolves the request-selected target, and returns only normalized S2-RO-01
evidence. Lab1 and Lab2 use the same fail-closed path, with no cross-target
fallback. The repository capability was proven offline and in hosted CI; a
later separately authorized Lab2 invocation also passed. External persistent
Lab2 startup bindings and fresh-process reconstruction passed independent
review. Those deployment bindings are not repository authority.

```text
S2_RO_10_LAB2_OFFLINE_COMPOSITION = PASS
S2_RO_10_LAB2_OFFLINE_COMPOSITION_MAINLINE_INTEGRATION = COMPLETE
S2_RO_10_LAB2_HOSTED_CI = PASS
S2_RO_10_LAB2_OFFLINE_STATUS = INTEGRATED_AND_HOSTED_CI_PROVEN
INDEPENDENT_SECURITY_REVIEW = PASS
UNRESOLVED_MATERIAL_FINDINGS = 0
S2_RO_10_LAB2_LIVE_VALIDATION = PASS
S2_RO_10_LAB2_LIVE_PROOF_STATUS = CLOSED
FINAL_PERSISTENT_LAB2_TARGET_STARTUP_BINDING = YES
FINAL_PERSISTENT_LAB2_KNOWN_HOST_STARTUP_BINDING = YES
CANONICAL_FRESH_PROCESS_RUNTIME_RECONSTRUCTION = PASS
PERSISTENT_STARTUP_BINDING_INDEPENDENT_REVIEW = PASS
STAGE2_RUNTIME_CLOSURE_GAP = NONE
S2_RO_10_LAB2_FUTURE_LIVE_AUTHORITY = NOT_GRANTED
NEXT_LIVE_ACTION = SEPARATE_EXACT_OWNER_AUTHORIZATION_REQUIRED
CANONICAL_STATUS = LAB2_PROOF_COMPLETE_STAGE2_CLOSURE_CANDIDATE
```

The accepted Lab2 proof covers one target, one operation, one command, and one
consumed authorization only. It does not revalidate Lab1, prove overall VRRP
pair health, establish production readiness or write automation, or grant
future live authority. Stage 2 remains a closure candidate until the separate
independent closure review and remote Safe CI complete.

`OFFLINE_IMPLEMENTATION_AUTHORITY != LIVE_EXECUTION_AUTHORITY`

`OWNER_VERIFIED != AUTHORIZATION_CONSUMED != TRANSPORT_SUCCESS != PARSE_SUCCESS != FINAL_OBSERVATION_SUCCESS`

## Historical delivery context

The original S2-RO-10 delivery composed and proved one bounded Lab1 VRRP
observation from the accepted S2-RO-01 through S2-RO-09 components. A later
scope review found three Lab1-only assumptions in composition: registry
retention and the target context supplied to credential resolution and
credential reading. The bounded extension corrected those assumptions by
retaining the complete fixed registry and using the existing target-aware
resolver and backend operations. It subsequently passed offline validation,
independent review, PR integration, and hosted CI.

## Integration and review evidence

- Implementation commit reviewed: `0750551cc4c1c941b250dc3328816ecb625549fc`.
- Independent read-only security review: **PASS**, with zero material findings,
  one non-material observation, and zero unresolved material findings.
- Pull request: **#90**, which integrated the implementation commit.
- Merge commit: `1eca8576e1da8aba41cb3c8be23b54a9b720371f`.
- Merge tree: `2c7fa1ac21221b2d8f26ce47663941549710230c`.
- Post-merge Safe CI run: **34870907764**, successful for the `push` event on
  `main` at the merge commit.
- Python validation: 4,018 collected; 4,016 passed; 2 accepted safety skips;
  zero failed.
- Node validation: 128 tests across 9 files passed. Typecheck, lint, build, and
  immutability checks passed.
- Report index: WARN with 1 pass, 13 optional reports missing, and zero
  mandatory missing, failed, or unknown reports.

Hosted CI proves the recorded offline validation and repository checks only.
The later Lab2 live proof is distinct evidence and does not retroactively
change what this hosted run proved.

## Allowed scope

The integrated implementation extension was limited to exactly three files:

- [Composition](../../validation_framework/stage2_trusted_runtime_composition.py).
- [Offline tests](../../tests/stage2/test_trusted_runtime_composition.py).
- This document.

The sole public operation is
`execute_stage2_vrrp_trusted_runtime(request, authorization_envelope_bytes,
trusted_configuration) -> Stage2VrrpObservationEvidence`. The other public
names are `Stage2TrustedRuntimeConfiguration`, `Stage2TrustedRuntimeFailure`,
and `Stage2TrustedRuntimeError`.

This is a trusted library boundary for the exact `mikrotik.vrrp_status`
operation and `/interface vrrp print detail` command. It composes the accepted
real component implementations, while validation substitutes only private
module references. No public dependency injection is exposed.

## Trusted configuration

`Stage2TrustedRuntimeConfiguration` is frozen, slotted, and redacted, with
exactly seven fields:

| Field | Accepted type |
| --- | --- |
| target_registry | S2-RO-02 Stage2FixedTargetRegistry |
| owner_trust_root_expected_path | str |
| owner_trust_root_expected_file_identity | str |
| owner_trust_root_expected_file_sha256 | str |
| replay_ledger_configuration | S2-RO-05 Stage2ReplayLedgerConfiguration |
| known_host_configuration | S2-RO-07 Stage2KnownHostSourceConfiguration |
| credential_configuration | S2-RO-04 Stage2TrustedWindowsCredentialConfiguration |

These inputs come only from separately trusted startup. Requests, CLI options,
environment variables, and repository files cannot supply authority through
this API. There is no public key, secret, approval artifact, callback, clock,
backend, transport override, or dependency dictionary in configuration.

Exact types and initialized fields are required. Inert nested records are
captured and revalidated with their accepted constructors before external
acquisition. The complete supplied S2-RO-02 fixed registry is retained, and
the request's exact `target_ref` selects its endpoint through the existing
registry policy. The single trusted known-host configuration must name an
endpoint in that registry and must equal the endpoint selected for the current
request before credential access or transport. Request fields are captured
and reparsed with S2-RO-01. Malformed objects and subclasses fail.

The Owner-root API has no public inert pin configuration validator. Composition
reuses its private pure path, FileId, and digest syntax checks. This is an
explicit internal coupling, not a new authority model. Only the accepted
acquisition operation establishes the root. Approval-directory identity,
issuer, and public key come exclusively from that acquired root.

Independent provisioning, repository-external Owner-controlled storage,
protected ancestors/ACLs, and non-rolled-back ledger history remain deployment
preconditions. This module neither establishes nor repairs them. Arbitrary
privileged in-process mutation is outside the immutable Python contract.
Future startup lifecycle and configuration replacement remain separately gated;
there is no cache, hot reload, or repeated invocation loop here.

### External persistent Lab2 startup binding

The repository exposes the generic seven-field configuration contract; it does
not contain deployment pins. Separately controlled Owner startup configuration
now persistently reconstructs the Lab2 target registry and known-host binding
for a fresh process. The accepted provider
`stage2_lab2_trusted_runtime_binding.py` has SHA-256
`b21ff9df445cb3fc2bde3c0ea05dcbdc558c2b996a31c451ad5a6de13a8e77a5`.
Its external offline test
`test_stage2_lab2_trusted_runtime_binding.py` has SHA-256
`22d0473709243de416d1aeccf88338316c81833cf15fcdb36be8874ba4ba0bf4`
and passed 6/6; focused repository validation passed 397/397. Independent
review confirmed preserved bytes, Owner-controlled ownership, matching DACLs,
exact `target.mikrotik.lab02` / `192.168.88.3:22` reconstruction, and the
accepted known-host and credential bindings.

The personal filesystem prefix, credential contents, private keys, signatures,
approval material, and raw device output are intentionally not published.
The external provider is deployment configuration, not a repository startup
executable and not a source of reusable authority. Historical trusted-startup
replay provenance remains unresolved.

## Ordered composition

1. Validate and capture the exact request and trusted configuration.
2. Parse the canonical S2-RO-05 envelope, resolve and revalidate the exact
   request-selected S2-RO-02 endpoint, require the trusted known-host endpoint
   to equal it, resolve the S2-RO-03 credential binding with
   `resolve_for_target(request.target_ref, request.credential_ref)`, and
   validate all bindings against the current UTC time.
3. Acquire the pinned Owner root once. Construct `Stage2OwnerVerifier` and call
   `verify(envelope)` once. Validate the exact issued result and matching facts.
   S2-RO-06 owns the sole approval read; composition performs no separate
   approval acquisition, parsing, issuer selection, or signature verification.
4. Consume the authorization once using S2-RO-05. Validate the returned
   authorization ID, envelope digest, consumption time, and non-authority flag.
5. Acquire the S2-RO-07 known-host snapshot once and check the exact endpoint,
   source pins, Ed25519 blob, digest, fingerprint, and non-authority flag.
6. Revalidate authorization/time, construct the default S2-RO-04 backend, and
   read the selected binding once with
   `read_for_target(request.target_ref, binding)`.
7. Resolve the S2-RO-08 command once, revalidate authorization/time immediately
   before transport, then invoke S2-RO-09 once with exactly endpoint, credential,
   snapshot, and command specification. Release the credential reference in a
   `finally` block covering command/time/transport success and failure.
8. Validate the concrete transport result, all initialized fields, target,
   policy, host fingerprint, exit status zero, attempt count one, authority
   False, and built-in stdout bytes bounded to 65,536 bytes with matching SHA-256.
9. Pass that exact stdout bytes object unchanged to the accepted parser once.
   Validate the exact parser result, normalized records, digest, and byte count.
10. Construct one S2-RO-01 evidence object with attempt one, retry zero, measured
    bounded duration, and normalized parser facts. Require its accepted
    canonical serialization to succeed before returning it. Release transient
    raw-output and authority-bearing references.

S2-RO-05 performs additional internal pure binding checks. The S2-RO-08 parser
internally revalidates command policy. These do not consume another replay
record, read another credential, or execute another command. Lab1 and Lab2 use
this one target-aware composition path; there is no Lab2-to-Lab1 fallback,
alternate credential read, or target-specific retry path.

## Replay and failure ownership

`CONSUMED_AUTHORIZATION != SUCCESSFUL_DEVICE_RESULT`

Owner verification precedes replay. Replay precedes known-host acquisition,
credential access, and transport. A rejection stops every later stage. Once
consumption succeeds, a known-host, credential, command, time, transport,
parser, or evidence failure leaves authorization spent. There is no retry,
reset, unconsume, ledger repair, migration, alternate credential source, second
credential read, second transport attempt, or second command.

An uncertain replay commit fails closed, without claiming persistence or
retrying. Replay anti-rollback protection is **NOT provided**. Restoring an
older valid ledger is outside the accepted trust boundary. IDs and file pins
are consistency checks, not independent freshness anchors.

Child components own their resources and internal failure precedence.
Composition does not close transport resources again or undo consumption.
Credential reference release is **not secure zeroization** of immutable Python
bytes; the module makes no memory-erasure guarantee.

## Clocks and evidence

A private UTC function uses `time.time_ns() // 1_000_000_000`. The same function
is passed explicitly as replay `utc_now`. Binding/time checks occur initially,
inside accepted consumption, before credential access, and immediately before
transport. A failing clock has no fallback. Later pure checks never consume
again, and expiry after consumption cannot restore authority.

Duration uses private `time.monotonic_ns()` from validated request capture
through successful parsing and integrity checks. Milliseconds round upward,
with a minimum representable success of one. Negative elapsed time and values
above 60,000 milliseconds reject; excessive duration is never clamped into
success. Child transport deadlines remain unchanged. This measurement does
not promise a wall-clock timeout for every blocking acquisition operation or
cancel an in-progress transport when envelope validity ends.

The existing S2-RO-01 schema `1.0` is reused with no wrapper or new evidence
schema. Evidence contains request identity, policy version, attempt/retry and
duration metadata, output digest/length, and normalized VRRP records. It
contains no raw stdout, stderr, credential, signature, host key, trust root,
approval, snapshot, consumption record, or transport handle.
`execution_authorized` remains **False** and grants no future authority.
Empty output may be successful transport but fails the accepted parser.

## Bounded errors

The enum is exactly:

- INVALID_REQUEST
- INVALID_TRUSTED_RUNTIME_CONFIGURATION
- AUTHORIZATION_ENVELOPE_FAILED
- TARGET_RESOLUTION_FAILED
- CREDENTIAL_BINDING_FAILED
- TRUST_ROOT_ACQUISITION_FAILED
- APPROVAL_ACQUISITION_FAILED
- OWNER_VERIFICATION_FAILED
- REPLAY_REJECTED
- KNOWN_HOST_ACQUISITION_FAILED
- CREDENTIAL_ACQUISITION_FAILED
- COMMAND_POLICY_FAILED
- TRANSPORT_FAILED
- OUTPUT_PARSE_FAILED
- EVIDENCE_CONSTRUCTION_FAILED
- INTERNAL_FAILURE

Mapping follows the producing stage, including malformed successful child
outputs. S2-RO-06 `SOURCE_*` errors map to APPROVAL_ACQUISITION_FAILED; its
artifact, issuer, algorithm, signature, and cryptographic failures map to
OWNER_VERIFICATION_FAILED. Pure envelope/binding/time failures map to
AUTHORIZATION_ENVELOPE_FAILED. Actual consume failures map to REPLAY_REJECTED.
Initial duration-clock failure maps to INTERNAL_FAILURE; final duration or
serialization failure maps to EVIDENCE_CONSTRUCTION_FAILED.

The private operation discards child exceptions before returning a category.
The public API clears input references and raises outside child handlers.
Its error contains no child cause/context, rejected text, secret, raw output,
signature, key, or external path. No logging or alternate failure report is
emitted. This is not isolation against privileged inspection of a running
Python process or caller-owned objects.

## Historical delivery boundary and current forbidden scope

The S2-RO-10 delivery added no prior-slice changes, dependencies, second trust
root, second evidence schema, environment authority, CLI, interactive prompt,
startup executable, live registration, scheduler, worker, AI loop, retry,
configuration backup/change, or S2-RO-11 implementation. S2-RO-09 remained
unchanged. The existing S2-RO-10 public API, seven-field configuration,
sixteen-category failure enum, evidence schema, authority order, and replay
semantics remain unchanged.

S2-RO-11 source was unchanged by the S2-RO-10 delivery. Its existing one-call
delegation made a separately trusted Lab2 request and matching configuration
source-reachable through the integrated target-aware path. At that historical
point, this was configuration-only impact and neither execution authority nor
live proof. The later accepted proof is separately recorded in S2-RO-11 and the
formal closure candidate.

```text
S2_RO_11_SOURCE = UNCHANGED
S2_RO_11_LAB2_IMPACT = CONFIGURATION_ONLY
SOURCE_REACHABLE != EXECUTION_AUTHORIZED
S2_RO_11_LAB2_LIVE_VALIDATION_AT_S2_RO_10_DELIVERY = NOT_PERFORMED
S2_RO_11_LAB2_LIVE_VALIDATION_CURRENT = PASS
```

Offline implementation and validation performed no real trust-root, approval,
or known-host read; Credential Manager read; persistent replay mutation;
loopback, DNS, SSH, or RouterOS access. Repository operations are not device
validation during the S2-RO-10 delivery. The later one-shot Lab2 proof used
separate exact Owner authorization. Any future live attempt still requires a
new exact Owner authorization.

## Offline validation and review boundary

Tests use synthetic exact-type records and private module monkeypatches. The
Lab1 regression and Lab2 success cases verify exact target-aware resolver and
backend arguments, one Owner verification, one replay consumption, one
known-host acquisition, one credential acquisition, one command resolution,
one transport invocation, exact command text, unchanged stdout object identity,
one normalized evidence object, attempt one, retry zero, and non-authority.

Negative cases reject both cross-lab credential pairs, wrong trusted credential
locators, known-host/endpoint mismatches, and authorization binding mismatches.
Disposable SQLite cases prove that Lab2 authorization remains spent after
known-host, credential, command, transport, parser, and evidence-construction
failure. They also prove no alternate credential read, second replay success,
transport fallback, or retry occurs.

Guards prohibit real Credential Manager, Owner trust-root, approval artifact,
known-host source, socket, DNS, SSH, and device access. The real S2-RO-05 ledger
is used only against disposable synthetic test state. No Lab1 or Lab2 device is
contacted, and no RouterOS command is emitted. Public failures remain sanitized.

The integrated implementation satisfied exact three-file scope, UTF-8 without
BOM and LF-only text, `git diff --check`, focused S2-RO-10 tests without skips,
Stage-2 regression and full pytest with only accepted safety skips,
report-index review, documentation readability, and secret-diff review. Its
independent read-only security review passed, and post-merge hosted Safe CI
passed at the merge commit. Those offline and hosted results grant no live
execution authority. The later Lab2 PASS came only from its separate one-shot
authorization and is not reusable.

References: [integration gates](actual_automation_integration_plan.md),
[S2-RO-01 evidence](stage2_vrrp_readonly_s2_ro_01_contract.md),
[S2-RO-05 replay](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md),
[S2-RO-06 verifier](stage2_vrrp_readonly_s2_ro_06_owner_verifier.md),
[S2-RO-07 snapshot](stage2_vrrp_readonly_s2_ro_07_known_host_snapshot.md),
[S2-RO-08 policy/parser](stage2_vrrp_readonly_s2_ro_08_command_policy.md), and
[S2-RO-09 transport](stage2_vrrp_readonly_s2_ro_09_pinned_ssh_transport.md).
See also the [S2-RO-11 live proof](stage2_vrrp_readonly_s2_ro_11_live_entrypoint.md)
and [Stage-2 formal closure candidate](stage2_formal_closure.md).
