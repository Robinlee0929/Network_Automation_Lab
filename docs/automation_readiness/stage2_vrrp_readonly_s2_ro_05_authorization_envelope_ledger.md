# S2-RO-05 authorization envelope and durable replay ledger

## Decision summary

S2-RO-05 accepts exactly the Lab1/Lab1 and Lab2/Lab2 target/credential pairs
through the existing S2-RO-03 resolver. Mixed or noncanonical bindings reject
before replay filesystem access, path identity checks, or SQLite connection.
The durable replay engine and SQL schema are unchanged. This is an offline
binding-policy extension, not Owner authentication or execution authorization.
Status: bounded implementation candidate, subject to validation and independent
review. No earlier slice or S2-RO-06-or-later production module is modified.

`VALID ENVELOPE != OWNER APPROVAL != EXECUTION AUTHORITY`

## Allowed and forbidden scope

Allowed: immutable data validation, SHA-256 binding, canonical serialization,
and one append-only transaction against a pre-provisioned local SQLite ledger.
Tests use synthetic data and temporary storage only.

Excluded: Owner verification, signatures, trust roots, credential retrieval,
Credential Manager, known-host management, RouterOS parsing, transport, network,
DNS, SSH/NETCONF/RESTCONF, shell execution, runtime composition, live entrypoints,
configuration changes, retries, queues, workers, schedulers, and AI loops.
No new dependency or CLI registration is added.

## Exact envelope

| Field | Value or bound |
| --- | --- |
| schema_version | Exact string `1.0` |
| authorization_id | Canonical lowercase hyphenated UUIDv4, 36 ASCII characters |
| operation_id | Exact `mikrotik.vrrp_status` (20 characters) |
| request_sha256 | 64 lowercase hexadecimal characters |
| authorization_ref | Dotted lowercase ASCII reference beginning `authorization.`, maximum 160 characters |
| target_ref | Exact `target.mikrotik.lab01` or `target.mikrotik.lab02`, subject to the pair rule below |
| credential_ref | Exact matching `credential.mikrotik.lab01` or `credential.mikrotik.lab02` |
| issued_at | Integer UTC Unix seconds, 0 through 253402300799 |
| expires_at | Integer UTC Unix seconds, same bound |
| max_attempts | Exact integer 1 |

Boolean values are not integers for this contract. Reference segments match
`[a-z][a-z0-9_-]*`, separated by dots. No normalization, whitespace trimming,
coercion, optional fields, or defaults are applied.

Only these conceptual pairs are accepted:

- `target.mikrotik.lab01` + `credential.mikrotik.lab01`.
- `target.mikrotik.lab02` + `credential.mikrotik.lab02`.

S2-RO-03 `resolve_for_target(target_ref, credential_ref)` is the pair authority;
S2-RO-05 has no duplicate pair registry. Both cross-lab pairs, unknown identities,
aliases, prefixes, case-confused values, whitespace changes, and noncanonical
types reject. There is no wildcard, normalization, fallback, or default-to-Lab1.
Historical Lab1 canonical bytes remain valid under the same schema `1.0`.

The request digest is SHA-256 of S2-RO-01 `to_canonical_bytes()`. It binds all
request fields including run identity and read-only intent. Explicit operation,
authorization, target and credential references must also match. S2-RO-02
lookup and the S2-RO-03 binding remain immutable authorities; S2-RO-04 is neither
imported nor called. Logical target binding is not physical-device attestation.

Binding validation checks exact envelope/request/registry/binding object types,
revalidates the envelope, reparses the request, looks up and validates its
registry endpoint, and resolves the validated target/credential pair through
S2-RO-03. The supplied binding must equal that canonical result. Operation,
authorization reference, endpoint target, credential, and exact canonical
request digest must all match before time validation. Caller-supplied bindings
cannot override the resolver. S2-RO-02 must be configured with the exact pair
for a Lab2 lookup; this extension does not discover or provision endpoints.

`consume` still performs binding validation before `_path_identity` and
`sqlite3.connect`. Invalid bindings have zero ledger filesystem access, path
identity calls, connections, BEGINs, INSERTs, and durable mutations. Both labs
follow the same path and bounded failure categories; neither has a relaxed path.

The envelope is a frozen, slotted dataclass of immutable scalars. Exported
dictionaries are fresh copies. Parsing accepts only built-in bytes, at most
2048 bytes, strict UTF-8 and exactly ten fields. Duplicate keys, unknown or
missing fields, nested values, wrong types, invalid UUIDs and digests fail.
Canonical JSON uses sorted keys, compact comma/colon separators,
`ensure_ascii=False`, `allow_nan=False`, and byte-exact reserialization.
BOMs, alternative escapes, whitespace, trailing newlines and noncanonical
representations reject. Both the envelope and consumption record always expose
`execution_authorized=False` and have bounded redacted representations.

## Validity and future Owner handoff

Require `issued_at <= now < expires_at`, a positive lifetime of at most
300 seconds, and zero clock skew. Issuance is inclusive; expiry exclusive.
The trusted clock returns bounded integer UTC seconds (default: `time.time_ns`
converted to whole seconds). Invalid or failing clocks reject. Time is checked
before I/O, before insertion under the transaction, and after commit. Expiry
after commit returns failure but leaves the authorization spent.

`owner_verification_payload(envelope)` returns exactly:

```python
b"Network_Automation_Lab/S2-RO-05/authorization-envelope/v1\x00" + envelope.to_canonical_bytes()
```

S2-RO-06 must authenticate these exact domain-separated bytes. No verification
algorithm, approval Boolean, or Owner trust receipt is implemented here.
Future runtime must verify the Owner before consumption, preserve the exact
bindings, and enforce one attempt afterward. A consumption record is audit data,
not a transferable execution ticket. S2-RO-07 through S2-RO-10 remain separate.

## Trusted persistent storage

`Stage2ReplayLedgerConfiguration` contains one absolute local `database_path`,
an expected canonical UUIDv4 `expected_ledger_instance_id`, and an immutable
non-empty tuple of at most 32 absolute `excluded_roots` identifying checkouts.
Paths are bounded to 1024 characters. The module's own repository root is also
excluded. Trusted provisioning must list other checkout roots. Neither request
nor envelope selects the path or ledger identity.

The ledger and parent directories must already exist outside Git. Production
storage must be persistent Owner-controlled local storage, not a temporary,
network, or synchronized restore location. Tests exclusively use temporary
synthetic storage. Missing storage blocks and is never created. Configuration
does not discover environment variables or load files automatically.

Basic standard-library checks reject traversal, network path forms, controls,
unexpected object types, observable symlinks/reparse points, and hard links.
Database identity is checked across consumption; detected inconsistency rejects.
These checks do not implement a general Windows trust-root subsystem or claim
protection against privileged concurrent replacement. SQLite manages its own
rollback journal; no application code removes or repairs sidecars.

## Exact pre-provisioned schema

Provisioning is a separate future Owner/admin action; no initializer is exposed.

```sql
CREATE TABLE ledger_metadata (
    schema_version TEXT NOT NULL PRIMARY KEY COLLATE BINARY,
    ledger_instance_id TEXT NOT NULL COLLATE BINARY
) STRICT;

CREATE TABLE consumed_authorizations (
    authorization_id TEXT NOT NULL PRIMARY KEY COLLATE BINARY,
    envelope_sha256 TEXT NOT NULL COLLATE BINARY,
    consumed_at INTEGER NOT NULL
) STRICT, WITHOUT ROWID;
```

Exactly one metadata row must match schema `1.0` and configured instance ID.
The stored DDL must match this token shape, allowing only case, whitespace, and
one terminal semicolon variation. This rejects changed conflict policy, column
shape, nullability, collation, or strictness. Additional user objects reject.
SQLite internal primary-key structures are permitted. Integrity checking and
validation of every bounded stored record run under the write transaction.
Unsupported SQLite features fail closed; no package is installed automatically.

The replay key is authorization UUID alone. The envelope SHA-256 is audit
metadata, not a second replay namespace. Same-ID/different-envelope replay is
rejected. No raw envelope, request, endpoint, credential, or command is stored.

Lab1 and Lab2 share this replay-key meaning: changing the lab or any envelope
field does not make an already consumed authorization UUID reusable. Only
temporary pre-provisioned synthetic ledgers are used to validate this extension.
No real replay database, rows, ledger identity, authorization package, credential
store, Owner trust-root artifact, or private key is accessed or provisioned.

Records are retained permanently. The limit is 100000 records and 64 MiB of
database pages. Capacity exhaustion blocks; it never prunes or resets history.

## Atomic consumption and durability

`Stage2ReplayLedger.consume(envelope, request, registry, credential_binding,
utc_now=...)` validates all bindings before filesystem access. It opens one
SQLite connection using an internally constructed `mode=rw` URI, timeout zero,
and explicit transactions. No caller-supplied URI options are accepted.

It sets `synchronous=EXTRA`, `trusted_schema=OFF`, and `foreign_keys=ON`, then
executes `BEGIN IMMEDIATE`. Under the reservation it verifies all effective
settings, including DELETE journaling, normal locking and zero busy timeout,
then validates schema, metadata and rows. It rechecks time and executes exactly
one parameterized plain INSERT. The unique authorization-ID primary key is the
decisive duplicate barrier. It never releases the transaction between checking
state and inserting. COMMIT must succeed before any success can be returned.

Two competing processes cannot both obtain success: the loser encounters a
busy failure or a duplicate key. There is no reconnect, backoff, application
retry, UPSERT, UPDATE, DELETE, unconsume, reclaim, or reset operation.

Durability depends on SQLite and the OS/storage honoring locks and flushes.
EXTRA does not prove immunity to faulty hardware or storage rollback.

| Failure point | Result |
| --- | --- |
| Before commit | No consumption success; no execution authority inferred |
| After commit, before command | Authorization permanently spent even if execution never occurs |
| After future command | Already spent; restart rejects replay |
| Ambiguous commit | No success, no automatic retry; persistence is not asserted |
| Expiry or cleanup failure after commit | Failure returned; durable record remains spent |
| Missing, corrupt, wrong-version or inconsistent state | Fail closed; no creation, repair, migration or reset |

Normal SQLite recovery of an interrupted transaction is not application-level
repair. If recovery cannot establish valid state, consumption fails. A failed
uncommitted invocation may leave no row, but it never returned successful
consumption. The caller must not automatically reuse ambiguous authorization.

Errors expose only `Stage2AuthorizationFailure` categories, never raw input,
paths, SQL, stored rows, or underlying exception details. Cleanup is attempted
on all connection paths; cleanup failure cannot create a success result.

## Explicit anti-rollback limitation

The replay ledger prevents reuse of an authorization against the same
trusted persistent ledger history. S2-RO-05 does not provide an
independent anti-rollback anchor and therefore does not protect against
restoration or replacement with an earlier internally valid snapshot.

```text
REPLAY_RESISTANT_WITHIN_TRUSTED_NON_ROLLBACK_LEDGER_BOUNDARY = YES
ANTI_ROLLBACK_STORAGE_PROTECTION = NOT_PROVIDED
VALID_SNAPSHOT_ROLLBACK_PROTECTION = OUT_OF_SCOPE
```

The Owner explicitly accepts that storage will not be maliciously restored,
replaced by a historical copy, or rolled back by an administrator or OS/hardware
state restoration. Instance IDs and file identity are consistency checks, not
independent freshness anchors. Expanding this threat model requires separate
authorization. The test suite demonstrates this limitation using only a
disposable synthetic snapshot; it is not a recovery recipe for production.

## Validation and next gate

Focused tests cover strict parsing/bounds, exact bindings, UUID/time policy,
immutability, canonical payload bytes, first/repeated/changed-envelope replay,
fresh-process replay and concurrent consumers, malformed schema/storage,
missing storage, busy handling, injected write and ambiguous-commit failures,
post-commit expiry, sanitized errors, and absent forbidden capabilities.

The Lab2 extension adds exact-pair round trips, legacy Lab1 compatibility,
resolver-authority checks, cross-lab and malformed-input pre-I/O guards, and
synthetic consume-once/replay cases for both labs. Guards observe zero filesystem,
path identity, SQLite connect, BEGIN, INSERT, and mutation counts on rejected
bindings; test-ledger content, size, mtime, and directory entries remain intact.
Valid consumption uses one exact connection and one parameterized INSERT, with
no reconnect, retry, fallback ledger, or new replay namespace. Owner payload
domain bytes and both `execution_authorized=False` contracts are preserved.

Validate in this order using a disposable external copy and writable external
pytest basetemps: focused S2-RO-05, all `tests/stage2`, full pytest, report-index,
then `git diff --check`. Python uses `-B`; pytest uses `-p no:cacheprovider`
and `--tb=short`. Never print environment mappings or retain unsanitized
tracebacks. All tests require zero failures; unchanged platform skips are
acceptable. Optional missing reports may remain accepted WARN without a
mandatory failure. No dependency installation or download is part of this task.
Source HEAD/tree/status and content/size/mtime must remain unchanged during
external validation; only the three authorized candidate files are applied.

The separately bounded implementation authorization permits one local commit
only after every mandatory gate passes. Independent review remains a separate
gate. Push, PR, merge, cleanup, S2-RO-06-or-later Lab2 extension, real authorization
or replay operations, Lab1/Lab2 contact, and Stage 3 require separate approval.
