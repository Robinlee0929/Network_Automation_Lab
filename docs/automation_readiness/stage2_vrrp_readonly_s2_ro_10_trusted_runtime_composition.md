# S2-RO-10: Trusted runtime composition

## Decision summary

S2-RO-10 composes one bounded VRRP observation from the accepted S2-RO-01
through S2-RO-09 components. Status: validated implementation candidate;
independent security review PASS, zero unresolved material findings. Ready for
separate local-commit authorization. It returns only normalized S2-RO-01 evidence.
No startup executable, CLI, live task registration, or S2-RO-11 behavior is added.
Implementation and offline validation do not authorize a live invocation.

`OWNER_VERIFIED != AUTHORIZATION_CONSUMED != TRANSPORT_SUCCESS != PARSE_SUCCESS != FINAL_OBSERVATION_SUCCESS`

## Allowed scope

The candidate consists of exactly three files:

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
acquisition. Target and known-host configuration must agree. Request fields
are captured and reparsed with S2-RO-01. Malformed objects and subclasses fail.

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

## Ordered composition

1. Validate and capture the exact request and trusted configuration.
2. Parse the canonical S2-RO-05 envelope, resolve and revalidate the S2-RO-02
   endpoint, resolve the S2-RO-03 credential binding, and validate all bindings
   against the current UTC time.
3. Acquire the pinned Owner root once. Construct `Stage2OwnerVerifier` and call
   `verify(envelope)` once. Validate the exact issued result and matching facts.
   S2-RO-06 owns the sole approval read; composition performs no separate
   approval acquisition, parsing, issuer selection, or signature verification.
4. Consume the authorization once using S2-RO-05. Validate the returned
   authorization ID, envelope digest, consumption time, and non-authority flag.
5. Acquire the S2-RO-07 known-host snapshot once and check the exact endpoint,
   source pins, Ed25519 blob, digest, fingerprint, and non-authority flag.
6. Revalidate authorization/time, construct the default S2-RO-04 backend, and
   read the fixed credential binding once.
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
record, read another credential, or execute another command.

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

## Forbidden scope

No prior-slice or integration-plan file changes, dependencies, second trust
root, second evidence schema, environment authority, CLI, interactive prompt,
startup executable, live registration, scheduler, worker, AI loop, retry,
configuration backup/change, or S2-RO-11 implementation is included.

The implementation task performs no real trust-root/approval/known-host read,
Credential Manager read, persistent replay mutation, loopback, DNS, SSH, or
RouterOS access. Remote base inspection and local branch creation are separate
repository operations, not device validation. Staging, commit, push, PR, merge,
and branch/worktree deletion require separate authorization.

## Validation and review

Tests use synthetic exact-type records and private module monkeypatches.
Guards prohibit real acquisition and network. Integration tests use the real
S2-RO-05 ledger only against disposable synthetic SQLite state, force each
later failure, and prove the second invocation rejects before credentials or
transport. Tests also cover strict types, missing fields, ordered counts,
clock boundaries, unchanged stdout object identity, integrity cross-binding,
credential reference release, and sanitized failures for every child category.

Required validation order: three-file scope, UTF-8 without BOM/LF-only,
focused tests with no skips, Stage-2 regression, full pytest, report-index,
whitespace, independent read-only security review, and documentation review.
The accepted guarded Windows launcher disables native/network operations,
plugin autoload, cache, and bytecode before pytest startup. Its inert non-TTY
Colorama/click stubs avoid native console initialization. Allowed Python/Node
regression children retain guards; Git fixtures remain temporary and local.

The two real Win32 trust-root tests and the Flask process/socket lifecycle test
are the only accepted local safety skips. No S2-RO-10 test was skipped.

### Recorded candidate evidence

| Validation | Collected | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: |
| Focused S2-RO-10 | 272 | 272 | 0 | 0 |
| Stage 2 | 1416 | 1414 | 0 | 2 |
| Full pytest | 3542 | 3539 | 0 | 3 |

- Report-index: 14/14 PASS; zero failures, warnings, missing, or unknown entries.
- UTF-8 without BOM, LF-only, and whitespace validation: PASS. Because the
  candidate is untracked, direct file checks supplement `git diff --check`.
- Independent read-only security review: PASS; zero unresolved material
  findings. The reviewer inspected all three files and relevant accepted
  contracts, using the recorded guarded test results without another test run.
- Documentation readability and local reference links: PASS.
- Prior S2-RO-01 through S2-RO-09 files: unchanged. Index: empty.

Focused validation executed `tests/stage2/test_trusted_runtime_composition.py`;
regression executed `tests/stage2` and the full suite. Report-index executed
`network_lab.py --task report-index`. All used the accepted guarded Python 3.13
validation setup, pytest 8.4.2, and existing dependencies. Early test-fixture
issues involving an oversized pytest identifier and a deliberately mutated
comparison object were corrected in the candidate tests; the final runs pass.

The two Stage-2 skips are
`test_disposable_regular_file_is_accepted_by_exact_native_path` and
`test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical`, both requiring
real Win32 APIs. The additional full-suite skip is
`test_canonical_flask_process_lifecycle_and_get_only_routes`, which requires
process/socket lifecycle operations excluded by this task.

Candidate hashes are frozen after validation and review and returned to the
Owner. This delivery grants no staging, commit, push, PR, merge, or live-access
authority. S2-RO-11 remains unimplemented and separately gated.

References: [integration gates](actual_automation_integration_plan.md),
[S2-RO-01 evidence](stage2_vrrp_readonly_s2_ro_01_contract.md),
[S2-RO-05 replay](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md),
[S2-RO-06 verifier](stage2_vrrp_readonly_s2_ro_06_owner_verifier.md),
[S2-RO-07 snapshot](stage2_vrrp_readonly_s2_ro_07_known_host_snapshot.md),
[S2-RO-08 policy/parser](stage2_vrrp_readonly_s2_ro_08_command_policy.md), and
[S2-RO-09 transport](stage2_vrrp_readonly_s2_ro_09_pinned_ssh_transport.md).
