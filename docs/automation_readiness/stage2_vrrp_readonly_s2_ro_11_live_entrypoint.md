# S2-RO-11: One-shot live entrypoint

## Decision summary

S2-RO-11 adds a trusted-caller library boundary around the accepted S2-RO-10
runtime. Status: validated implementation candidate; independent security review PASS,
zero unresolved material findings. Ready for separate local-commit authorization. It returns only canonical S2-RO-01 evidence bytes, or one
sanitized failure category. This final Stage-2 implementation slice supplies
no deployment bootstrap and authorizes no real invocation.

`S2_RO_11_IMPLEMENTED != REAL_RUN_AUTHORIZED`

`S2_RO_11_MERGED != REAL_RUN_AUTHORIZED`

## Allowed scope and API

Exactly three candidate files are included:

- [Entrypoint](../../validation_framework/stage2_vrrp_readonly_live_entrypoint.py).
- [Offline tests](../../tests/stage2/test_vrrp_readonly_live_entrypoint.py).
- This document.

The sole operation is
`run_stage2_vrrp_live_once(request_bytes: bytes,
authorization_envelope_bytes: bytes,
trusted_configuration: Stage2TrustedRuntimeConfiguration) -> bytes`.
The only other public names are `Stage2VrrpLiveEntrypointFailure` and
`Stage2VrrpLiveEntrypointError`. There is no public dependency injection.

The request must be exact built-in bytes, length 1 through 2048, parsed by
`parse_stage2_vrrp_request_canonical_json`. No coercion, repair, stripping,
second JSON parser, file input, or override is provided. The envelope also
must be exact built-in bytes of length 1 through 2048. It reaches S2-RO-10 as
the unchanged original object. Framing acceptance never validates authority:
S2-RO-10/S2-RO-05 exclusively own envelope canonical and authorization checks.

Configuration must be the exact accepted concrete configuration class.
Subclasses, dictionaries and lookalikes reject. S2-RO-10 retains validation of
its initialized fields, nested values and all security bindings.

Initial rejection makes zero runtime calls. Otherwise the boundary calls
`execute_stage2_vrrp_trusted_runtime` once. There is no retry, loop, fallback
or alternate runtime. Transport and command counts remain at most one under
S2-RO-10/S2-RO-09. A second API call is a distinct caller invocation; this
library does not enforce process-wide uniqueness. Replay protection remains
owned by S2-RO-05, including its documented anti-rollback limitation.

## Trusted startup

The caller supplies an already constructed exact configuration from separately
trusted external startup. This preserves the S2-RO-10 provisioning assumption;
it does not authenticate arbitrary Python callers or establish a new root of
trust. Independent provisioning, protected external storage and trusted
in-process code remain deployment preconditions.

Ordinary CLI arguments, environment variables, repository files, home-directory
search, fallback and implicit defaults cannot supply authority through this
entrypoint. It does not construct configuration, acquire trust assets, or
register a task in `network_lab.py`. No standalone executable is delivered.
External deployment bootstrap remains outside this candidate.

## Evidence and errors

The runtime result must be exact `Stage2VrrpObservationEvidence`. Its accepted
canonical serializer produces bytes; the accepted S2-RO-01 canonical evidence
parser checks that output before return, including malformed exact-type data.
The existing schema 1.0 and 32768-byte evidence bound remain authoritative.
No evidence construction, RouterOS parsing or second success schema is added.
The output contains normalized facts and the accepted digest/length metadata,
never raw RouterOS streams, credential material, approval signatures, host-key
blobs or trust-root contents. Evidence grants no future execution authority.

| Failure source | Boundary category |
| --- | --- |
| Request type, size or canonical rejection; runtime INVALID_REQUEST | INVALID_REQUEST_INPUT |
| Envelope type or size; runtime AUTHORIZATION_ENVELOPE_FAILED | INVALID_AUTHORIZATION_INPUT |
| Configuration type; runtime INVALID_TRUSTED_RUNTIME_CONFIGURATION | INVALID_TRUSTED_CONFIGURATION |
| All other expected runtime categories | TRUSTED_RUNTIME_FAILED |
| Wrong/malformed evidence or canonical rendering failure | OUTPUT_RENDER_FAILED |
| Unexpected implementation exception or malformed runtime error | INTERNAL_FAILURE |

These six categories are the entire failure model. The public exception
contains only its category. Child exceptions are discarded before the public
raise; cause and context are absent, including an active caller exception.
Request, envelope and configuration references are cleared in the public
failure frame. No child traceback or rejected content is presented. Python
still creates the boundary exception's own traceback; the library does not
print it and does not promise isolation from privileged process inspection.

There is no stdout, stderr, logging, file output, debug mode or partial success
output. Process exit codes are not applicable to this library-only API.
Transient input and evidence references are released; no configuration,
authorization or evidence cache exists. Reference release does not erase
immutable bytes, caller-owned objects or copies retained by the caller.

## Forbidden scope

Only lab operation `mikrotik.vrrp_status` and inherited command
`/interface vrrp print detail` are supported. No dynamic or production target,
caller target/command/credential/timeout override, configuration backup/change,
bypass flag, CLI, server, daemon, Flask route, scheduler, queue, worker or agent
is added. S2-RO-01 through S2-RO-10, `network_lab.py`, the integration plan and
dependencies remain unchanged. S2-RO-10 remains the sole runtime orchestrator.

Implementation and validation must not acquire real trust-root, approval,
known-host or credential assets; mutate real replay storage; create sockets;
perform loopback/DNS/SSH; or invoke RouterOS. Repository metadata checks are
separate from device validation. Staging, commit, push, PR and merge require
separate authorization.

## Pre-live deployment checklist

This checklist is documentation only. No listed asset is provisioned or read
by this implementation task.

1. S2-RO-10 is closed; S2-RO-11 is independently validated, merged, passed
   post-merge CI and technically closed at an exact main commit.
2. The fixed lab target remains exact, uses canonical IPv4/22, and is not a
   production device.
3. The operation remains `mikrotik.vrrp_status`.
4. The command remains `/interface vrrp print detail`.
5. Owner trust root, approval directory/source, persistent replay ledger and
   known-host source are repository-external with protected ancestors/ACLs.
6. Trusted startup independently possesses the expected trust-root path,
   FileId and complete-file SHA-256.
7. One current valid signed approval exists with matching request/envelope
   IDs, target, credential, operation and authorization bindings.
8. Replay storage is persistent and protected against ordinary tampering;
   rollback of valid history remains outside the accepted protection.
9. The known-host source is independently pinned by path/FileId/hash and binds
   the exact endpoint to its exact `ssh-ed25519` key.
10. Windows Credential Manager contains the exact fixed credential target;
    that credential has least-privilege read-only lab-device permissions.
11. No real secret, authority, approval, host key or deployment artifact is
    committed to the repository.
12. Authorization consumed before a downstream failure remains spent. No
    second attempt, retry, reset, repair or unconsume follows that failure.
13. A separate fresh Owner authorization for
    `STAGE2_REAL_MIKROTIK_ONE_SHOT_READ_ONLY_RUN` binds the exact merged main
    SHA, lab target, operation, command, one attempt, zero retries, current
    signed approval and externally provisioned trusted configuration/assets,
    with no configuration mutation.

## Offline validation and review

Tests substitute only the entrypoint's private runtime function binding; they
never invoke the real composition. Synthetic exact configuration records and
evidence contain no real assets. Input bounds, canonical rejection, every
runtime category, malformed results, no-output behavior, exception sanitation,
reference release, exact public surface and absence of broader capabilities
are covered. The 2048-byte request boundary remains subject to the unchanged
canonical request schema; it does not make an invalid padded request valid.

Required validation order is exact scope, UTF-8 without BOM/LF, focused tests
without skips, Stage-2 regression, full pytest, report-index, whitespace,
independent read-only security review, and documentation readability/links.
All execution uses an offline guard established before pytest startup, with
native/network access disabled. Any unrelated safety skips must be classified.

### Recorded validation

| Suite | Collected | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: | ---: |
| Focused S2-RO-11 | 126 | 126 | 0 | 0 |
| Stage 2 | 1542 | 1540 | 0 | 2 |
| Full pytest | 3668 | 3665 | 0 | 3 |

Report-index: 14/14 PASS, with no failures, warnings, missing or unknown entries.
No S2-RO-11 test skipped. UTF-8 without BOM, LF-only and direct untracked-file
whitespace checks pass, as does `git diff --check`.

The two Stage-2 safety skips are
`test_disposable_regular_file_is_accepted_by_exact_native_path` and
`test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical`, which require
real Win32 APIs. The third full-suite safety skip is
`test_canonical_flask_process_lifecycle_and_get_only_routes`, requiring process
and socket lifecycle operations excluded by this task.

Runs used existing Python 3.13 and the previously reviewed offline launcher
before pytest startup, with bytecode/cache/plugin autoload disabled and inert
Colorama/click console stubs. Python/Node regression children retained guards;
Git regression fixtures were disposable and local. No dependency was added.
An initial focused run caught an unnecessary future-annotations namespace
binding; removing it made the exact public-surface test pass. Final focused,
Stage-2 and full results above follow that correction.

Independent read-only security review: PASS; zero unresolved material findings.
Documentation readability and all seven local reference links: PASS. The review
confirmed the exact trusted-caller boundary, failure mapping, unchanged envelope,
single runtime call, canonical evidence, no broader authority surface, and all
13 pre-live requirements. Candidate hashes are returned separately to the Owner.
No staging, commit, remote publication or live invocation is authorized here.

References: [integration gates](actual_automation_integration_plan.md),
[S2-RO-01](stage2_vrrp_readonly_s2_ro_01_contract.md),
[S2-RO-05](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md),
[S2-RO-09](stage2_vrrp_readonly_s2_ro_09_pinned_ssh_transport.md), and
[S2-RO-10](stage2_vrrp_readonly_s2_ro_10_trusted_runtime_composition.md).
