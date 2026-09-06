# S2-RO-06 Owner verifier and exact approval source

## Decision summary

S2-RO-06 implements bounded offline Owner authenticity verification and one
exact read-only approval file source. Status: **UNCOMMITTED CANDIDATE**; validation
and independent review results accompany the handoff. It reuses the accepted Owner trust root and
S2-RO-05 payload API without modifying any accepted slice.

`VERIFIED OWNER APPROVAL != VALID CURRENT AUTHORIZATION != EXECUTION AUTHORITY`

The delivery is exactly one production module, one synthetic test module, and
this document. It adds no CLI, registry entry, runner, production composition,
provisioning workflow, or dependency. It does not advance S2-RO-07.

## Allowed scope and exclusions

Allowed: strict immutable artifact parsing, Ed25519 public-key verification,
bounded local approval reads, and sanitized verification evidence. Tests use
synthetic signatures and deterministic fake native functions exclusively.

Excluded: private-key loading, production signing, real approvals or credentials,
Credential Manager, replay consumption, target selection, known-host snapshots,
RouterOS output parsing, transport, sockets, DNS, SSH/NETCONF/RESTCONF, shell
execution, runtime composition, live entrypoints, configuration backup/change,
queues, schedulers, workers, and AI loops. No existing source or test is changed.

## Accepted authority boundary

Both public operation entrypoints require an exact receiver class before reading
its authority. Each captures and validates one acquired trust root, then uses that
same local value throughout the operation. Subclasses and unbound lookalike
receivers cannot substitute a path, issuer, or verification key between reads.

Both `Stage2OwnerVerifier(trust_root)` and
`Stage2ExactOwnerApprovalSource(trust_root)` require the exact acquired
`OwnerTrustRootConfiguration` type from
[the accepted trust-root contract](stage2_live_authorization_owner_trust_root.md).
They accept no raw key, key callback, path override, injected approval source,
environment discovery, or alternate authority. Configuration holders are frozen.

The accepted acquisition API authenticates its record using independently
supplied expected path, Win32 FileId, and complete-file SHA-256. S2-RO-06 does
not acquire or provision that record itself. Future trusted startup must acquire
one configuration, once. The record supplies the sole 32-byte raw Ed25519
public key, fixed issuer, approval-source ID, directory path/identity, and audit
fingerprint. Key replacement requires separate Owner provisioning and restart;
there is no key ring, TOFU, network lookup, registration, or fallback.

Repository-external local storage, protected ancestor directories, and
Owner-controlled ACLs remain the accepted deployment preconditions. S2-RO-06
does not inspect ACLs or prove ancestor integrity. A canonical drive path does
not itself prove local storage: trusted provisioning must exclude mapped remote
or synchronized storage. No second trust-root or persistent trust subsystem is
introduced. The existing lab-attestation reference remains trusted configuration;
this slice makes no new physical-device attestation claim.

## Exact approval artifact

`parse_stage2_owner_approval(raw: bytes) -> Stage2OwnerApprovalArtifact` accepts
exactly four ASCII string fields:

| Field | Exact rule |
| --- | --- |
| schema_version | `s2-ro-06.owner-approval.v1` |
| issuer_ref | Lowercase dotted ASCII reference, at most 160 characters |
| signature_algorithm | `Ed25519` |
| signature_base64 | Canonical standard Base64 of exactly 64 signature bytes |

Issuer segments match `[a-z][a-z0-9_-]*`, separated by dots. Verification
requires exact equality with the sole acquired issuer; the artifact cannot
select a key. Signature encoding is exactly 88 ASCII characters with `==`
padding, strict decoding, and exact re-encoding equality. URL-safe Base64,
whitespace, malformed padding, and noncanonical pad bits fail.

Raw input is bounded to 2048 bytes. Canonical JSON uses UTF-8, sorted keys,
compact comma/colon separators, `ensure_ascii=False`, and `allow_nan=False`.
The raw input must equal canonical reserialization byte for byte. Missing,
unknown, duplicate, nested, non-string, and non-ASCII fields reject, as do
invalid UTF-8, BOMs, whitespace, alternate escapes, trailing newlines, NaN,
unsupported schemas, and unsupported algorithms. There is no coercion or repair.

The parsed object is immutable scalar data and returns canonical bytes. Parsing
does not establish authenticity. No timestamp, approval ID, payload body,
envelope duplication, payload digest, or key is stored in the artifact.

## Exact signed bytes

The verifier calls the accepted S2-RO-05 `owner_verification_payload(envelope)`
once when an attempt reaches payload verification, then passes those exact
bytes to `Ed25519PublicKey.from_public_bytes(acquired_key).verify(signature,
payload)`. Early rejected attempts never need to obtain the payload.

The domain separator belongs exclusively to
[S2-RO-05](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md).
It is not duplicated here. Artifact JSON, selected fields, raw envelope JSON,
and the payload digest alone are not the signed message. A changed valid
envelope or byte-different representation fails the signature check. Invalid
fixed target/credential fields reject through the unchanged S2-RO-05 contract.

The four artifact metadata fields are constrained independently. The signature
authenticates the S2-RO-05 message, not a second metadata message. The result's
artifact SHA-256 identifies the bytes actually read; it is not a second signed
claim. Exactly one algorithm is supported. Cryptography is already supplied by
the committed dependency graph; no Paramiko import or dependency change is used.

## Exact approval source

`read_exact(owner_approval_ref: str) -> bytes` uses
`owner_approval_ref = envelope.authorization_ref`, unchanged. No envelope field
is added. References must start with `authorization.` and obey the same bounded
dotted grammar before native access. The only filename is
`<exact authorization_ref>.json`, appended to the acquired approval directory.
The complete path is at most 1190 characters. There is no path normalization,
caller filename, extension alternative, enumeration, newest-file selection,
glob, retry, or fallback. One path yields bytes or an error, never a collection.

The deferred ctypes facade uses only `CreateFileW`, `GetFileType`,
`GetFileInformationByHandleEx`, `ReadFile`, and `CloseHandle`. No DLL is loaded
at import. Non-Windows invocation fails closed before DLL loading.

1. Open the configured pre-existing directory with zero requested data access,
   `FILE_SHARE_READ`, `OPEN_EXISTING`, and
   `FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS`.
2. Require disk-directory type and reject a reparse point. Query FileIdInfo and
   compare the exact acquired directory identity. Keep the handle open.
3. Open the one artifact with `GENERIC_READ`, `FILE_SHARE_READ`,
   `OPEN_EXISTING`, and `FILE_FLAG_OPEN_REPARSE_POINT`.
4. Require a regular disk file and reject directories/devices/reparse points.
5. Read only through that file handle, bounded to 2048 bytes plus an EOF or
   overflow probe. Short reads are accumulated; byte 2049 rejects.
6. Close the artifact and directory handles exactly once, in that order. An
   open failure closes only handles actually acquired. Cleanup failure prevents
   success; an earlier bounded failure retains precedence.

Directory backup semantics is solely the Windows requirement for obtaining a
directory handle. There is no privilege adjustment or backup operation. Neither
handle requests share-write or share-delete. No content reopen, file creation,
mutation, ACL change, repair, or broad filesystem trust traversal exists.
Platform/path limitations reject rather than normalize into another path.

Holding the pinned directory does not establish the integrity of its ancestors;
the already accepted trusted-ancestor precondition remains necessary. This
source does not claim protection from a hostile administrator or kernel.

## Verification result and failure order

`Stage2OwnerVerifier.verify(envelope) -> Stage2VerifiedOwnerApproval` checks
configuration, exact envelope type/structure, and lookup reference before native
access. It acquires one bounded artifact, validates canonical representation,
schema, algorithm, issuer syntax and trusted issuer equality, then signature
encoding. It obtains the sole public key and exact payload, verifies, then
issues a result. The standalone parser validates syntax without selecting an
authority; the verifier's internal parse additionally requires issuer equality.

The immutable verifier-issued result contains exactly:

```text
schema_version
artifact_sha256
approval_ref
verified_issuer_ref
approval_source_id
public_key_fingerprint
payload_sha256
verified = True
execution_authorized = False
```

It retains no handle, raw artifact, payload, signature, or key bytes. Repr is
bounded and redacted. Supported direct construction, subclassing, copy,
deepcopy, dataclass replacement, and pickle reconstruction are blocked, using
the accepted application-integrity pattern. Hostile same-process introspection,
low-level object construction/mutation, monkey-patching, and interpreter
compromise are outside this boundary. The result is not a transferable grant.

`Stage2OwnerVerificationError` retains only a
`Stage2OwnerVerificationFailure` category:

```text
INVALID_CONFIGURATION, INVALID_ENVELOPE, SOURCE_UNAVAILABLE,
SOURCE_TYPE_REJECTED, SOURCE_IDENTITY_MISMATCH, SOURCE_TOO_LARGE,
SOURCE_READ_FAILED, SOURCE_CLOSE_FAILED, MALFORMED_ARTIFACT,
UNSUPPORTED_SCHEMA, UNSUPPORTED_ALGORITHM, UNKNOWN_ISSUER,
MALFORMED_SIGNATURE, SIGNATURE_INVALID, CRYPTO_UNAVAILABLE
```

Metadata/open/platform failures map to `SOURCE_UNAVAILABLE`. Oversized raw
parser input is `MALFORMED_ARTIFACT`; source overflow is `SOURCE_TOO_LARGE`.
Wrong-payload signatures map to `SIGNATURE_INVALID`. Native and cryptographic
exception details are discarded rather than retained as exception context.

## Future runtime handoff

The future conceptual sequence remains:

```text
S2-RO-05 envelope parse and request/binding/time validation
→ S2-RO-06 verification of the exact S2-RO-05 payload
→ S2-RO-05 replay consumption and revalidation
→ separately authorized later execution boundary
```

This slice does not compose that flow. It performs no time validation or replay
consumption. A valid signature over a structurally valid expired envelope may
still establish authenticity; the future caller must enforce S2-RO-05 validity
and bindings. Untrusted approvals must fail before consumption. Verification
can repeat without changing approval files or burning authorization. S2-RO-05's
accepted non-rollback storage assumption is unchanged.

## Validation and acceptance

Run focused `python -m pytest tests/stage2/test_owner_verifier.py`, Stage-2
regressions `python -m pytest tests/stage2`, full `python -m pytest`, and
`python network_lab.py --task report-index` using the repository-approved
runtime and plugin isolation. For this task, explicitly safety-skip the
existing tests that require real Win32 operations:

- `test_disposable_regular_file_is_accepted_by_exact_native_path`
- `test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical`
- `tests/test_phase_2n_02_canonical_flask_demo_smoke.py::test_canonical_flask_process_lifecycle_and_get_only_routes`

The first two are trust-root native tests; the third starts a local Flask
server and invokes native process inspection. It is an additional full-suite
safety skip relative to the prior two-skip baseline, not a regression pass.

Apply these markers in the validation process without editing accepted tests.
All other Stage-2 tests must execute. S2-RO-06 tests intercept DLL loading before
any native construction, including tests of the real ctypes marshaling facade.
Synthetic signing occurs in test fixtures only. Source tests never open real
approval files. Positive and negative tests must prove no ledger, credential,
network, or subprocess path is reached by the verifier.

Acceptance requires zero failures, classified skips, a policy-accepted
report-index result, no unexpected tracked-file changes, whitespace checks of
all three untracked files, independent security review, and documentation
readability review. Optional missing runtime evidence may yield an explicitly
documented report-index WARN. No additional review artifact is created.

Passing these gates supports only separate local commit authorization. The
candidate remains unstaged and uncommitted. Commit, push, PR, merge, production
provisioning, real native access, and S2-RO-07 require separate authorization.
