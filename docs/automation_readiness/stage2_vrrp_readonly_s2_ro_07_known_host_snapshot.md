# S2-RO-07: Immutable offline known-host snapshot

S2-RO-07 implements acquisition of immutable, exactly pinned server host-trust
material. A successful snapshot has `execution_authorized=False`. It authorizes
neither a connection nor authentication or command execution. This is a bounded
implementation candidate; integration and live operation require separate gates.

## Purpose and allowed scope

The module acquires one Owner-provisioned host-key record for the accepted
S2-RO-02 `Stage2FixedTargetEndpoint`. It verifies one source handle, parses the
exact bytes read, and retains immutable host-trust facts after closing that
handle. Production acquisition is Windows-specific; import is safe elsewhere.
Tests use synthetic bytes and fake native functions on Windows and Linux.

The only public names are:

- `Stage2KnownHostSourceConfiguration`
- `Stage2KnownHostSnapshot`
- `Stage2KnownHostFailure`
- `Stage2KnownHostError`
- `acquire_stage2_known_host_snapshot(configuration)`

Parsing is private and cannot independently issue snapshot evidence. There is
no public generic trusted-file loader or alternate snapshot factory.

## Forbidden scope

There is no system or user `known_hosts` loading, Paramiko `HostKeys` or
`SSHClient`, `AutoAddPolicy`, trust on first use (TOFU), fallback key, network
discovery, or dynamic registration. There is no DNS, socket, SSH, NETCONF,
RESTCONF, credential access, Owner verification, replay consumption, command
execution, VRRP parsing, or runtime composition. No runner or report-index
registration is added. S2-RO-01 through S2-RO-06 remain unchanged.

S2-RO-08 and later implementation, dependencies, queues, schedulers, workers,
AI loops, configuration backup/change, production execution, historical rewrites,
and an additional safety matrix are outside this slice.

## Trusted startup and source pins

The source is **one preprovisioned Owner-controlled local file outside Git**.
Trusted startup independently supplies exactly four logical inputs:

| Configuration field | Required meaning |
| --- | --- |
| `expected_path` | Exact canonical absolute Windows source path |
| `expected_file_identity` | Exact `win32-fileid-v1` identity |
| `expected_file_sha256` | Lowercase SHA-256 hex of the complete source bytes |
| `expected_endpoint` | Exact accepted S2-RO-02 endpoint type |

The configuration is frozen, slotted and redacted. Built-in string types are
required for pins. Acquisition checks the exact configuration type before
attribute access, checks and revalidates the exact endpoint, captures immutable
values, and validates pin syntax before native loading. Subclasses, lookalikes,
missing fields and invalid reconstructed values cannot bypass this boundary.
Endpoint validation delegates to the accepted public endpoint contract; this
module does not introduce another address parser or target registry.

This is a trusted-startup API, not a mechanism for proving a Python caller's
identity. Only trusted setup may construct and supply these pins. Requests,
approval artifacts, environment variables and CLI values are not wired to it.
Ordinary request handling receives no path, endpoint or key override. Application
integrity and separation of trusted startup from request handling remain
required. Hostile interpreter reflection or module replacement is outside this
boundary; the code does not claim tamper-proof Python objects.

Repository-external placement, local storage, protected ancestor directories
and Owner-controlled ACLs are existing provisioning preconditions. They are not
dynamically established by path syntax or FileId checks. This module does not
provision a source, inspect ancestor ACLs, rotate keys or create another Owner
trust root. No operational source path or real device key appears in this
document or its tests.

### Canonical path and identity

Paths must be 4–1024 characters, lowercase drive-rooted with backslashes, and
equal their NFC-normalized casefolded form. Component checks reject relative,
UNC/device namespace, alternate separator, ADS, traversal, control-character,
reserved-device, trailing-dot and trailing-space aliases. Reserved device stems
are checked even with extensions, spaces before extensions and recognized
superscript aliases. Paths are rejected rather than normalized or repaired.
These are syntax checks, not filesystem discovery.

File identity syntax is exactly:

```text
win32-fileid-v1:<16 lowercase hex volume serial>:<32 lowercase hex file ID>
```

The volume is unsigned 64-bit; the 16 FileId bytes retain native byte order in
hex. The SHA pin is exactly 64 lowercase hexadecimal characters.

## Same-handle acquisition and close semantics

Configuration and endpoint rejection precede platform checks and DLL loading.
Non-Windows acquisition returns `PLATFORM_UNSUPPORTED`. The private deferred
adapter exposes only `CreateFileW`, `GetFileType`,
`GetFileInformationByHandleEx`, `ReadFile` and `CloseHandle`.

The single source open uses `GENERIC_READ`, `FILE_SHARE_READ`, `OPEN_EXISTING`
and `FILE_FLAG_OPEN_REPARSE_POINT`, with null security/template arguments.
There is no share-write, share-delete, create, truncate, backup-semantics or
overlapped mode.

The acquisition sequence is:

1. Open exactly the pinned path once; reject invalid handles.
2. Inspect the same handle for disk type and file attributes. Reject directories,
   non-disk objects and reparse points.
3. Read `FileIdInfo` from that handle and compare the exact pinned identity.
4. Accumulate bounded ordinary short reads from the same handle until EOF.
5. At exactly 2048 bytes, request one additional byte to prove EOF. Byte 2049
   rejects with `SOURCE_TOO_LARGE`; no partial result is returned.
6. Hash all bytes actually read and compare the complete-file pin before parsing.
7. Parse those same bytes, check target and key, and derive provisional facts.
8. Close the opened handle exactly once, including every failure path.
9. Issue the snapshot only after a successful close.

There is no stat-then-reopen, parser reopen, retry, fallback or source mutation.
A close failure prevents issuance. When an earlier failure and close failure
coincide, the earlier bounded category is preserved. Native exception messages,
causes and contexts are discarded from public errors. Handles never escape.

## Exact canonical source record

The source is strict UTF-8 JSON, at most **2048 bytes**, with **one record** and
exactly these six fields:

| Field | Contract |
| --- | --- |
| `schema_version` | `s2-ro-07.known-host.v1` |
| `target_ref` | Exact accepted endpoint target reference |
| `address` | Exact accepted endpoint address |
| `port` | Exact integer 22; Boolean is rejected |
| `host_key_algorithm` | `ssh-ed25519` |
| `host_key_base64` | Canonical standard Base64 of the complete SSH key blob |

Keys are sorted; separators are compact; reserialization must match the original
bytes exactly. All values except the integer port are ASCII strings. There is
no BOM, whitespace outside strings, trailing newline, duplicate/unknown/missing
field, nesting, coercion, alternate escape encoding, comment or second record.
OpenSSH line syntax, markers, aliases, hashed names, wildcards, certificates and
revocation records are unsupported.

Target reference, address and port must equal the captured endpoint tuple.
A structurally valid artifact for another target is rejected even if its file
identity and content hash match their startup pins.

## One host-key algorithm and complete-blob identity

Only `ssh-ed25519` is supported. Canonical standard Base64 is exactly 68
characters and decodes to exactly 51 bytes:

```text
uint32_be(11) || b"ssh-ed25519" || uint32_be(32) || 32 public-key bytes
```

The exact prefix, both length fields and total size are checked. Wrong embedded
or outer algorithms, 31/33-byte key components, truncated or trailing bytes,
extra SSH fields, URL-safe encoding and padding are rejected. This is structural
public-key acceptance; it does not prove private-key possession or perform SSH
signature verification. The approved algorithm policy does not assert that a
real device's configured algorithm has already been inspected.

Identity calculations use the **complete 51-byte SSH blob**, not just the
32-byte public-key component:

```text
host_key_sha256 = lowercase_hex(SHA256(complete_blob))
host_key_fingerprint = "SHA256:" + unpadded_standard_Base64(SHA256(complete_blob))
source_artifact_sha256 = lowercase_hex(SHA256(complete_source_bytes))
```

Tests pin fixed digest/fingerprint vectors and a one-bit key-change case.

## Immutable acquisition result

The snapshot retains only `schema_version`, `target_ref`, `address`, `port`,
`host_key_algorithm`, `host_key_blob`, `host_key_sha256`,
`host_key_fingerprint`, `source_file_identity`, `source_artifact_sha256` and
`execution_authorized=False`. All values are immutable scalars or bytes.

It retains no path, handle, complete source bytes, mutable mapping, Paramiko
object, credentials, approval artifact or private key. Its representation is
bounded and redacted. Ordinary construction, subclassing, copy/deepcopy,
`dataclasses.replace`, pickle and reconstruction hooks are blocked. The only
supported issuance site is the successful acquisition function after close.
Raw `object` reflection is not a supported fabrication interface. Future
consumers must reject lookalikes and uninitialized objects before use.

## Failure categories

Configuration failures are `INVALID_CONFIGURATION` and `INVALID_TARGET`.
Platform failure is `PLATFORM_UNSUPPORTED`. Source failures are
`SOURCE_UNAVAILABLE`, `SOURCE_TYPE_REJECTED`, `SOURCE_REPARSE_REJECTED`,
`SOURCE_IDENTITY_MISMATCH`, `SOURCE_HASH_MISMATCH`, `SOURCE_TOO_LARGE`,
`SOURCE_READ_FAILED` and `SOURCE_CLOSE_FAILED`.

Content failures are `MALFORMED_SNAPSHOT`, `UNSUPPORTED_SCHEMA`,
`UNSUPPORTED_HOST_KEY_ALGORITHM`, `TARGET_BINDING_MISMATCH` and
`MALFORMED_HOST_KEY`. Failure text contains only the bounded category, never
source paths, raw keys or native diagnostic details.

## Replacement and rollback limits

Same-handle inspection/read/hash/parse prevents ordinary acquisition-time
pathname replacement from changing the verified object. A returned immutable
snapshot is independent of later path or source changes. Current FileId/hash
pins reject stale material that differs from those pins.

**ANTI_ROLLBACK_STORAGE_PROTECTION = NOT_PROVIDED.** Joint restoration of an
older artifact and its historical trusted-startup pins has no independent
freshness detector in S2-RO-07. A synthetic test demonstrates that limitation.
There is no monotonic anchor, rollback-proof storage, hot reload or rotation
service. This is separate from S2-RO-05 replay-ledger rollback assumptions.

## Future S2-RO-09 handoff — documentation only

Future transport receives the accepted S2-RO-02 endpoint, this immutable snapshot
and a separate accepted credential path. Before any network access, it must
validate the exact snapshot type, initialized immutable facts and endpoint
target/address/port binding. Then it must restrict host-key negotiation to
`ssh-ed25519`, perform SSH key exchange and server-signature verification,
compare the presented algorithm and **complete public-key blob** exactly, and
only then permit authentication.

That future sequence must not reopen this source or consult ambient host trust.
None of the transport sequence is implemented here. Snapshot validity alone is
never authorization to execute it.

## Validation and acceptance

Use the repository-approved Python runtime with plugin autoload disabled,
bytecode disabled and `-p no:cacheprovider`. On Windows, do not launch raw
pytest: install the native guard before importing pytest or collecting tests.
Colorama must be disabled before its startup import. Guard the ctypes bootstrap
kernel32 reference as well as subsequent DLL loading and symbol lookup; the
guard must remain active through teardown. Fake DLL functions preserve ABI and
same-handle tests without invoking real native functions.

Run focused `tests/stage2/test_known_host_snapshot.py`, then all `tests/stage2`,
then full pytest through the guarded in-process launcher. Focused tests must
have zero failures and zero skips. Apply only the accepted in-process safety
skips for these existing tests, without editing them:

- `tests/stage2/test_live_authorization_owner_trust_root.py::test_disposable_regular_file_is_accepted_by_exact_native_path`
- `tests/stage2/test_live_authorization_owner_trust_root.py::test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical`
- `tests/test_phase_2n_02_canonical_flask_demo_smoke.py::test_canonical_flask_process_lifecycle_and_get_only_routes`

The first two require real Win32 source operations. The third starts a local
server and performs native process inspection. The third is an additional
local safety skip relative to the accepted two-skip CI baseline, not a passing
regression. No S2-RO-07 test is skipped. Standard interpreter/process mechanics
are distinct from invoking device, credential or native acquisition APIs.

Run `network_lab.py --task report-index` under the safe startup boundary after
pytest passes. Its report-only generated outputs are local evidence, not
candidate source. Policy-accepted optional-report WARN must be explained.
Run `git diff --check` and directly check all three untracked files for trailing
whitespace, UTF-8/BOM issues and unintended artifacts.

Acceptance requires classified zero-failure validation, exact three-file scope,
unchanged prior slices, an exact public API, independent security review and
documentation readability review with no unresolved material findings. The
candidate remains unstaged and uncommitted pending separate Owner authorization.

## References

- [Actual automation integration gates](actual_automation_integration_plan.md)
- [Accepted S2-RO-02 endpoint](../../validation_framework/stage2_mikrotik_target_registry.py)
- [Accepted S2-RO-06 boundary and validation policy](stage2_vrrp_readonly_s2_ro_06_owner_verifier.md)
- [S2-RO-07 implementation](../../validation_framework/stage2_known_host_snapshot.py)
- [Synthetic S2-RO-07 tests](../../tests/stage2/test_known_host_snapshot.py)
