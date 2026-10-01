# Dual-Lab VRRP AI Query MVP: DL-02 and DL-03 Acceptance

**Decision summary: DL-02 remains accepted; the DL-03 facts-only projection is
implemented, governed review passed, and Owner acceptance completed ACCEPT / PASS.**
The exact accepted DL-02 implementation
commit is `bb39e8295a2fa5d69980396dbaf8c374c79a57b3`. DL-02 is not
integrated into main, merged, or released. The exact accepted DL-03 implementation
is `e4c529507c6f5a26a289af4f6d3bfc9e0b170c18`; it is not integrated,
merged, or released.
DL-04 has not started, and the complete Dual-Lab MVP remains unfinished.
No live authority or readiness is granted.

## Purpose and planning boundary

This is the canonical repository record for the accepted DL-02 implementation,
its completed independent review and Owner acceptance, plus the DL-03 canonical
specification, accepted implementation, completed governed review, and completed
Owner acceptance decision. The DL-03 specification resolved the readiness
review's `BLOCKED_CANONICAL_SCOPE_AMBIGUITY`; the separately authorized
implementation, review, and acceptance are recorded below.
This documentation reconciliation performs no implementation, repeated review,
validation rerun, or repeated Owner acceptance, and does not reopen DL-02 or
Stage 2.
The pre-acceptance documentation commit
`76ce998531de59c201eaa6f123e57b1f9d364b19` established the candidate record and
resolved the documentary gap. The subsequent read-only acceptance retry returned
ACCEPT / PASS without changing source, tests, or documentation. This update
retains that completed decision without reopening it.

The accepted Dual-Lab VRRP AI Query MVP planning scope, reaffirmed by the Owner's
documentation reconciliation authorization, defines DL-02 as the fixed
synchronous orchestrator in
`validation_framework/dual_lab_vrrp_query_orchestrator.py`: structural preflight,
Lab1-before-Lab2 ordering, bounded per-target failure handling, the existing
S2-RO-11 boundary only, and distinct authorization proof. Retry, fallback, and
parallel execution are excluded.

That planning scope assigns the detailed record to this document and status
summaries to [the automation plan](actual_automation_integration_plan.md) and
[README](../../README.md). Stage-2 historical proof and closure semantics remain
unchanged; this acceptance record does not resolve any Stage-2 closure gate.

```text
STAGE2_FILES_REQUIRING_SEMANTIC_CHANGE = NONE
STAGE2_REOPEN_REQUIRED = NO
```

## Exact accepted implementation and reviewed candidate

```text
DL_02_IMPLEMENTATION_CANDIDATE = YES
DL_02_CANDIDATE_COMMIT = bb39e8295a2fa5d69980396dbaf8c374c79a57b3
DL_02_CANDIDATE_PARENT = 314e50ad847caf04a6a200199b63e1b3d3505f61
DL_02_ACCEPTED_IMPLEMENTATION_COMMIT = bb39e8295a2fa5d69980396dbaf8c374c79a57b3
DL_02_ACCEPTED_IMPLEMENTATION_PARENT = 314e50ad847caf04a6a200199b63e1b3d3505f61
DL_02_CHANGED_PATH_COUNT = 2
DL_02_CHANGED_PATHS =
  validation_framework/dual_lab_vrrp_query_orchestrator.py
  tests/dual_lab/test_dual_lab_vrrp_query_orchestrator.py
DL_02_SOURCE_SHA256 = a669ec055feabe3464a8dac15ba5a043fc9032a5bdc5931696e7b5ad8e7877c9
DL_02_TEST_SHA256 = 5296035c6c40cabe1fae7963182245c29ad09a446bc3e8e39deb4b46560462e3
```

The SHA256 values identify the raw filesystem bytes used by the independent
review. The two-path scope above describes the remediation commit, not the later
documentation reconciliation commit. Documentation changes do not amend or
replace the reviewed code candidate.

## P1 finding and remediation

The original pair-level authorization collision check depended on both target
preflights succeeding. A safely available identity could be lost when a target
failed a later local eligibility check, allowing the other target to reach
S2-RO-11 despite a duplicate authorization ID or reference.

The remediation retains the identity from the existing strict envelope parser
independently of local execution eligibility. It uses that identity only to
determine pair-level distinctness before either target invocation. A duplicate
`authorization_id` or `authorization_ref` gives both targets
`PREFLIGHT_AUTHORIZATION_NOT_DISTINCT` and causes zero S2-RO-11 invocations.

POLICY_2 remains intact: when identities are distinct, a locally rejected target
retains its bounded failure, while the other target may proceed exactly once
only if independently eligible. An identity that cannot safely be established
does not fabricate a pair collision. Retained identity grants no execution
eligibility and bypasses no signature, time, target/request binding, replay,
credential, pinned-host, or command-policy control.

```text
DL_02_P1_FINDING = authorization identity collision could be lost when a target failed later local eligibility checks
DL_02_P1_REMEDIATION = pair identity retained independently from local execution eligibility for pair-level distinctness checking only
DL_02_PAIR_COLLISION_CATEGORY = PREFLIGHT_AUTHORIZATION_NOT_DISTINCT
DL_02_PAIR_COLLISION_ZERO_INVOCATIONS = YES
DL_02_POLICY_2_PRESERVED = YES
DL_02_NO_AUTHORIZATION_WEAKENING = YES
DL_02_NO_NEW_TRUST_BOUNDARY = YES
```

## Completed fresh independent review evidence

These are the completed independent-review results accepted by the Owner as
evidence for this documentation task. They are not new validation runs or remote
Safe CI results. The review confirmed the exact commit, parent, two-file scope,
hashes, P1 remediation, adequate regression coverage, and preserved DL-02
invariants. It left the repository unchanged and the worktree clean.

| Validation | Collected | Passed | Failed | Errors | Accepted skips | Unexpected skips |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Focused orchestrator suite | 185 | 185 | 0 | 0 | 0 | 0 |
| Stage-2 offline suite | 1892 | 1890 | 0 | 0 | 2 | 0 |
| Full offline suite | 4461 | 4458 | 0 | 0 | 3 | 0 |

The guard review matched exactly three proven pre-existing denials. New or
unclassified denials and DL-02-remediation-caused denials were both zero.
Report-index returned acceptable WARN with exit code 0: 13 optional missing
reports, zero failures, zero mandatory missing reports, and zero unknown results.

```text
DL_02_FRESH_INDEPENDENT_REVIEW_RESULT = PASS
DL_02_FOCUSED_VALIDATION = 185 passed
DL_02_STAGE2_VALIDATION = 1890 passed / 2 accepted skips
DL_02_FULL_OFFLINE_VALIDATION = 4458 passed / 3 accepted skips
KNOWN_PRE_EXISTING_GUARD_DENIAL_COUNT = 3
KNOWN_PRE_EXISTING_GUARD_DENIAL_SET_MATCH = YES
DL_02_NEW_GUARD_DENIALS = 0
DL02_REMEDIATION_CAUSED_GUARD_DENIAL_COUNT = 0
DL_02_REPORT_INDEX = acceptable WARN / 13 optional missing / no failures
```

## Preserved safety boundary

The reviewed candidate remains synchronous, with Lab1 before Lab2 and both
structural preflights before the first invocation. It has no retry, fallback,
async, thread, pool, queue, scheduler, or public arbitrary executor. It uses only
the existing S2-RO-11 boundary and revalidates canonical success evidence.

It makes no pair-health verdict, temporal-skew threshold, or simultaneous
snapshot claim, and exposes no raw device stdout or secrets. This record grants
no Lab1/Lab2 access, SSH/NETCONF/RESTCONF execution, provider/API/model operation,
secrets handling, configuration backup/change, production execution, worker, or
AI agent loop. It adds no second safety matrix.

## Completed Owner acceptance and remaining gates

```text
DL_02_OWNER_ACCEPTANCE = ACCEPTED
DL_02_ACCEPTED = YES
DL_02_ACCEPTANCE_RESULT = PASS
DL_02_ACCEPTANCE_BASIS = FRESH_INDEPENDENT_REVIEW_PASS_AND_OWNER_ACCEPTANCE
ACCEPTANCE_CANONICAL_STATE_HEAD = 76ce998531de59c201eaa6f123e57b1f9d364b19
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
COMPLETE_DUAL_LAB_MVP = NO
```

Owner acceptance establishes that the exact implementation identified above
satisfies the defined DL-02 requirements. The accepted implementation identity
remains separate from the pre-acceptance and post-acceptance documentation
commits. The review results, hashes, and safety findings remain unchanged.

Integration, remote availability, integrated-MVP Safe CI, further slices, live
readiness, and production readiness remain separate gates. None of those later
states, complete Dual-Lab MVP acceptance, or DL-05 completion is established here.
DL-03 Owner acceptance also completed, as recorded below. Reviewing the canonical
plan and authorizing any DL-04 readiness or specification work remains a separate
Owner decision; this record does not start that work.

## DL-03 accepted implementation and completed Owner acceptance

The canonical specification was established by commit
`fe4877a6a9c812e1f8e03ccdaceff8528f9fba7a`. Its direct child below implements
only the deterministic facts-only projection and its tests. The two-path scope
and raw filesystem hashes identify the implementation candidate, separately
from this documentation commit; reconciliation does not amend the candidate.

```text
DL_03_SPECIFICATION_STATUS = ESTABLISHED
DL_03_IMPLEMENTED = YES
DL_03_IMPLEMENTATION_STARTED = YES
DL_03_IMPLEMENTATION_CANDIDATE = YES
DL_03_CANDIDATE_COMMIT = e4c529507c6f5a26a289af4f6d3bfc9e0b170c18
DL_03_CANDIDATE_PARENT = fe4877a6a9c812e1f8e03ccdaceff8528f9fba7a
DL_03_CHANGED_PATH_COUNT = 2
DL_03_CHANGED_PATHS =
  validation_framework/dual_lab_vrrp_query_summary.py
  tests/dual_lab/test_dual_lab_vrrp_query_summary.py
DL_03_SOURCE_SHA256 = 54c35c63b43dacc5d7f5d50a468a4ffe27d9094504766a42f737234784dac234
DL_03_TEST_SHA256 = 700c746c704bf2f51f2b9bff6fa0eb299493563b390a5272cf94bfc9e0dbd2c9
DL_03_SCHEMA_VERSION = dual-lab-vrrp-query-summary.v1
DL_03_OWNER_ACCEPTANCE = ACCEPTED
DL_03_ACCEPTANCE_RESULT = PASS
DL_03_ACCEPTED = YES
DL_03_STATUS = ACCEPTED
DL_03_ACCEPTED_IMPLEMENTATION_COMMIT = e4c529507c6f5a26a289af4f6d3bfc9e0b170c18
DL_03_ACCEPTED_IMPLEMENTATION_PARENT = fe4877a6a9c812e1f8e03ccdaceff8528f9fba7a
DL_03_FRESH_GOVERNED_REVIEW_RESULT = PASS
DL_03_ACCEPTANCE_BASIS = GOVERNED_REVIEW_PASS_AND_OWNER_ACCEPTANCE
DL_03_ACCEPTANCE_CANONICAL_STATE_HEAD = 3709a9eded6cf66205a1ac7d4113cf2d06e433ea
DL_04_IMPLEMENTATION_STARTED = NO
COMPLETE_DUAL_LAB_MVP = NO
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
NEXT_REQUIRED_OWNER_DECISION = REVIEW_CANONICAL_PLAN_AND_AUTHORIZE_DL_04_READINESS_OR_SPECIFICATION_WORK
```

The accepted source is the [DL-03 summary module](../../validation_framework/dual_lab_vrrp_query_summary.py),
with [DL-03 contract tests](../../tests/dual_lab/test_dual_lab_vrrp_query_summary.py).
It preserves the DL-01 aggregate schema and DL-02/Stage-2 behavior. It derives
observations only from canonical Lab1 and Lab2 results, preserves duplicates,
and emits no guessed duplicate pairing or prohibited inference. The normative
contract below remains unchanged.

```text
DL_03_PURPOSE = DETERMINISTIC_FACTS_ONLY_PROJECTION
DL_03_EXECUTION_AUTHORITY = NONE
DL_03_MODEL_PROVIDER_INTEGRATION = NO
DL_01_AGGREGATE_SCHEMA_CHANGE_REQUIRED = NO
DL_02_CHANGE_REQUIRED = NO
STAGE2_CHANGE_REQUIRED = NO
CROSS_TARGET_OBSERVATIONS_SOURCE = DERIVED_FROM_CANONICAL_LAB1_AND_LAB2_RESULTS_ONLY
OBSERVATION_KIND_COUNT = 14
RECORD_MATCHING_KEY = (instance_name, vrid)
DUPLICATES_PRESERVED = YES
DUPLICATE_KEYS_GUESSED_PAIRED = NO
PROHIBITED_INFERENCE_IMPLEMENTED = NO
```

### Retained DL-03 fresh review and validation evidence

The completed governed review returned PASS with no findings and no repository
mutation. It performed fresh read-only inspection and fresh validation in the
same conversation. Here, "fresh independent review" describes that process;
it is not an attestation by a separate human, agent identity, or conversation.
These Owner-supplied accepted results are retained evidence, not new validation
runs, remote Safe CI, Owner acceptance, or integration evidence.

| Validation | Collected | Passed | Failed | Errors | Established skips | Unexpected skips |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DL-03 focused suite | 211 | 211 | 0 | 0 | 0 | 0 |
| Complete Dual-Lab suite | 652 | 652 | 0 | 0 | 0 | 0 |
| Stage-2 offline suite | 1892 | 1890 | 0 | 0 | 2 | 0 |
| Full offline suite | 4672 | 4669 | 0 | 0 | 3 | 0 |
| External review probes | 66 | 66 | 0 | 0 | 0 | 0 |

The guard matched the established set of three pre-existing denials; new,
unclassified, and DL-03-caused denials were zero. All tracked repository files
remained unchanged during the fresh review. Report-index returned acceptable
WARN, exit code 0, with 13 optional missing reports, zero mandatory missing
reports, zero failures, and zero unknown results. These optional runtime-report
gaps do not establish a safety or regression issue.

```text
DL_03_FRESH_INDEPENDENT_REVIEW_RESULT = PASS
DL_03_REVIEW_FINDINGS = NONE
DL_03_REVIEW_REPOSITORY_MUTATION = NONE
DL_03_FOCUSED_VALIDATION = 211 passed
DL_03_DUAL_LAB_VALIDATION = 652 passed
DL_03_STAGE2_VALIDATION = 1890 passed / 2 established skips
DL_03_FULL_OFFLINE_VALIDATION = 4669 passed / 3 established skips
DL_03_EXTERNAL_REVIEW_PROBES = 66 passed
DL_03_KNOWN_PRE_EXISTING_GUARD_DENIAL_COUNT = 3
DL_03_KNOWN_PRE_EXISTING_GUARD_DENIAL_SET_MATCH = YES
DL_03_NEW_GUARD_DENIALS = 0
DL_03_NEW_OR_UNCLASSIFIED_GUARD_DENIAL_COUNT = 0
DL_03_CAUSED_GUARD_DENIAL_COUNT = 0
DL_03_REPORT_INDEX = acceptable WARN / 13 optional missing / zero failures
DL_03_REPORT_INDEX_EXIT_CODE = 0
DL_03_REPORT_INDEX_MANDATORY_MISSING = 0
DL_03_REPORT_INDEX_UNKNOWN = 0
```

### Completed acceptance decision and limits

The pre-acceptance candidate documentation commit
`3709a9eded6cf66205a1ac7d4113cf2d06e433ea` recorded the reviewed candidate
with Owner acceptance pending. The subsequent authorized read-only decision
returned `OWNER_ACCEPTANCE_DECISION = ACCEPT`, `ACCEPTANCE_RESULT = PASS`,
and `DL_03_ACCEPTED = YES`, with no repository mutation or validation rerun.
This reconciliation records that completed decision without repeating it.

Acceptance establishes only that implementation
`e4c529507c6f5a26a289af4f6d3bfc9e0b170c18` satisfies the canonical DL-03
specification and governed-review requirements. Its identity remains separate
from the pre-acceptance and post-acceptance documentation commits. The retained
review results, hashes, and same-conversation process meaning remain unchanged.

This record grants no Lab1/Lab2 access,
execution authority, configuration mutation, live or production readiness,
complete-MVP acceptance, integration into main, remote Safe CI completion, or
DL-04 implementation authority.

## DL-03 canonical specification: purpose and scope

The following specification is retained from its establishment commit. Its
references to "future" implementation describe that original specification
boundary; the current implemented, reviewed, Owner-accepted state is
recorded above. The contract and validation requirements are not broadened.

DL-03 projects an already canonical Dual-Lab aggregate into an immutable,
deterministic AI/UI-facing summary DTO. Its only claims are observed values,
availability, existing sanitized failure categories, equality/difference, set
membership/difference, and record counts. AI/UI-facing describes a data consumer;
it introduces no model or provider integration.

This specification was established against repository baseline
`4d0abf0fd87986cb3fb054f9e265f5846ba52b47`. The normative upstream boundaries are
[DL-01's inert aggregate contract](../../validation_framework/dual_lab_vrrp_query_contract.py)
and [the inert Stage-2 evidence contract](../../validation_framework/stage2_vrrp_readonly_contract.py).
The former validates the fixed target pair and tagged results; the latter
validates normalized records. DL-03 consumes those boundaries without changing
their schemas or execution semantics.

```text
DL_03_PURPOSE = DETERMINISTIC_FACTS_ONLY_PROJECTION
DL_03_EXECUTION_AUTHORITY = NONE
DL_03_MODEL_PROVIDER_INTEGRATION = NO
DL_03_INPUT = EXISTING_CANONICAL_DUAL_LAB_AGGREGATE_ONLY
DL_03_OUTPUT = IMMUTABLE_FACTS_ONLY_SUMMARY_DTO
DL_03_SCHEMA_VERSION = dual-lab-vrrp-query-summary.v1
DL_01_AGGREGATE_SCHEMA_CHANGE_REQUIRED = NO
DL_01_CHANGE_REQUIRED = NO
DL_02_CHANGE_REQUIRED = NO
STAGE2_CHANGE_REQUIRED = NO
```

### Exact public API and input boundary

The future module's public exports are exactly `DualLabVrrpSummary`,
`DualLabSummaryError`, `project_dual_lab_vrrp_summary`, and
`parse_summary_canonical_json`. The two functions have these signatures:

```python
project_dual_lab_vrrp_summary(raw: bytes) -> DualLabVrrpSummary
parse_summary_canonical_json(raw: bytes) -> DualLabVrrpSummary
```

`project_dual_lab_vrrp_summary` accepts only exact built-in `bytes`, containing
the existing DL-01 aggregate's canonical JSON. It delegates validation to
`parse_aggregate_canonical_json` before deriving any output. Callers holding a
`DualLabVrrpAggregate` use its existing `to_canonical_bytes()` first. There is no
duck-typed object, dictionary, text, bytearray, subclass, runtime bundle, or
executor input overload. Forged objects therefore cannot bypass validation.

The input has exactly `schema_version`, `query_id`, `operation_id`,
`execution_order`, `lab1`, and `lab2`. Its schema remains
`dual-lab-vrrp-query.v1`; operation is `mikrotik.vrrp_status`; execution order is
`LAB1_THEN_LAB2`. Lab1 is bound to `target.mikrotik.lab01`, Lab2 to
`target.mikrotik.lab02`. Query identity retains DL-01's grammar and 160-character
bound. Success input carries canonical `evidence`; failure input carries the
existing bounded `failure_category`. All nested exact-field, value, target,
canonical JSON, and size checks remain upstream checks. The upstream aggregate
byte limit is 69,632 bytes. No new input field is permitted, including
`cross_target_observations`.

Malformed, noncanonical, extra-field, target-swapped, or invalid-success input
fails closed before projection. Invalid input is not repaired, normalized into
validity, or converted into a target failure. Contract validation establishes
data validity, not provenance, freshness, authorization, or device truth.

`parse_summary_canonical_json` accepts only exact built-in `bytes` containing
canonical summary JSON conforming to the output rules below. It does not accept
an aggregate, acquire evidence,
or call the projection entrypoint. It validates the entire DTO and recomputes
the required observations from its target projections, rejecting inconsistent,
missing, extra, or differently ordered observations. A parsed summary conveys
no stronger provenance than its data.

`DualLabVrrpSummary` is factory-created by those functions; direct construction
is not a public API. Its public data attributes are the seven output fields.
Its public methods are `to_dict() -> dict[str, object]` and
`to_canonical_bytes() -> bytes`; its nonserialized `execution_authorized`
property always returns `False`. Both methods revalidate all fields and derived
observations, including after deliberate frozen-object tampering. Nested
representations are private immutable value objects, with fields exactly as
specified below; arrays are tuples internally and lists only in fresh exports.

All public rejection paths raise `DualLabSummaryError`, a `ValueError` with
exact message `invalid Dual-Lab summary`. The error retains no input, child
exception, cause, or context. No partial DTO is returned. DTO and nested-object
`repr` and `str` return the fixed label `<inert-dual-lab-summary>`.

### Exact output and projected records

Every object is closed to extra or missing fields. Primitive types are exact;
booleans cannot substitute for integers. The top-level fields are exactly:

| Field | Required value |
| --- | --- |
| `schema_version` | `dual-lab-vrrp-query-summary.v1` |
| `query_id` | Validated input query identity, unchanged |
| `operation_id` | `mikrotik.vrrp_status`, unchanged |
| `execution_order` | `LAB1_THEN_LAB2`, unchanged; metadata only |
| `lab1` | Projection bound to `target.mikrotik.lab01` |
| `lab2` | Projection bound to `target.mikrotik.lab02` |
| `cross_target_observations` | Ordered array derived by the rules below |

A successful target has exactly `status`, `target_ref`, `records`, with status
`SUCCESS`. A failed target has exactly `status`, `target_ref`,
`failure_category`, with status `FAILURE`. Failure has **no `records` field**:
neither null nor an empty array is valid there. Success has 0 through 32 records;
an empty successful observation remains distinct from unavailable evidence.

Each projected record has exactly these nine observed fields, retaining the
upstream types and bounds without coercion, case folding, trimming, inference,
or substitutions:

| Field | Exact domain |
| --- | --- |
| `instance_name` | Nonempty NFC string; no surrounding whitespace or Unicode category C characters; at most 128 UTF-8 bytes |
| `role` | `MASTER`, `BACKUP`, `FAILURE`, or `UNKNOWN` |
| `vrid` | Integer 1 through 255 |
| `priority` | Integer 0 through 255 |
| `interval_ms` | Integer 1 through 255,000 |
| `version` | Integer 2 or 3 |
| `running` | Boolean |
| `disabled` | Boolean |
| `invalid` | Boolean |

No evidence-envelope fields are copied into a success projection. In particular,
run IDs, authorization IDs/references, policy versions, attempt/retry counts,
durations, raw-output byte counts, and raw-output hashes are excluded. Raw
stdout, credentials/references, signatures, private keys, known-host raw data,
private paths, replay data, exception text, runtime configuration, and SSH/session
details have no output field. `target_ref` is the existing fixed public logical
identifier, not an endpoint or credential reference.

### Record order, matching, and duplicate preservation

Sort each target's records ascending by the complete key:

```text
(instance_name, vrid, role, priority, interval_ms, version, running, disabled, invalid)
```

Strings use Python Unicode code-point order, integers numeric order, and booleans
`False` before `True`. The primary key is `(instance_name, vrid)`; the remaining
seven observable fields form the complete tie-breaker. Byte-identical duplicates
remain repeated entries. Upstream permits duplicate matching keys and identical
records, so DL-03 must neither reject valid duplicates nor collapse them.

Group records on each side by exact `(instance_name, vrid)`. Field comparisons
are emitted only when that key has exactly one record on each side. A common key
with multiplicity greater than one on either side yields one
`MATCH_KEY_MULTIPLICITY` observation with the two counts; it yields no field
comparison. This reports the ambiguity without inventing a record pairing.

A key occurring only on one side yields an unmatched-key observation with its
occurrence count, including all duplicates. It is never matched by array
position, role, priority, similar spelling, or VRID alone. Sorting does not
establish a cross-target pairing.

```text
RECORD_MATCHING_KEY = (instance_name, vrid)
INPUT_ORDER_INDEPENDENT = YES
DUPLICATE_RECORD_COLLAPSE = NO
DETERMINISTIC_OUTPUT = YES
```

Equivalent inputs with the same query identity, target statuses/failure labels,
and per-target record multisets produce identical output bytes. Changes only
to valid upstream evidence-envelope metadata also cannot affect the summary.
Canonical input bytes may contain any valid record-array order; DL-03 sorts its
output without rewriting or relaxing upstream canonical JSON validation.

### Closed cross-target observation vocabulary

```text
CROSS_TARGET_OBSERVATIONS_SOURCE = DERIVED_FROM_CANONICAL_LAB1_AND_LAB2_RESULTS_ONLY
CROSS_TARGET_OBSERVATION_SCHEMA = kind, subject, lab1_value, lab2_value
```

Every observation contains exactly those four fields. `kind` is one of the 14
literal strings in the table. `subject` and both values are constrained by its
row; there is no free-text explanation, arbitrary mapping, or extension kind.
`K` means an exact object with `instance_name` and `vrid`, using record domains.
`KF` means an exact object with `instance_name`, `vrid`, and `field`. `field` is
one of `role`, `priority`, `interval_ms`, `version`, `running`, `disabled`,
`invalid`. Array values are sorted unique sets, not record arrays.

| Permitted kind | Exact subject | Exact lab1_value / lab2_value | Emission condition |
| --- | --- | --- | --- |
| `RESULT_AVAILABILITY` | `null` | Boolean / boolean | Always once; true iff that target is SUCCESS |
| `VRID_SET_EQUAL` | `null` | Integer array / integer array | Both succeed and observed VRID sets equal |
| `VRID_SET_DIFFERENT` | `null` | Integer array / integer array | Both succeed and observed VRID sets differ |
| `VRID_ONLY_LAB1` | Integer VRID | `true` / `false` | One per VRID in Lab1 set minus Lab2 set |
| `VRID_ONLY_LAB2` | Integer VRID | `false` / `true` | One per VRID in Lab2 set minus Lab1 set |
| `INSTANCE_NAME_SET_EQUAL` | `null` | String array / string array | Both succeed and observed name sets equal |
| `INSTANCE_NAME_SET_DIFFERENT` | `null` | String array / string array | Both succeed and observed name sets differ |
| `RECORD_COUNT_EQUAL` | `null` | Integer count / integer count | Both succeed and full record counts equal |
| `RECORD_COUNT_DIFFERENT` | `null` | Integer count / integer count | Both succeed and full record counts differ |
| `RECORD_ONLY_LAB1` | `K` | Positive count / `0` | Key exists only in Lab1 |
| `RECORD_ONLY_LAB2` | `K` | `0` / positive count | Key exists only in Lab2 |
| `MATCH_KEY_MULTIPLICITY` | `K` | Positive count / positive count | Common key has count greater than one on either side |
| `FIELD_EQUAL` | `KF` | Observed scalar / observed scalar | Unique key on each side, selected field equal |
| `FIELD_DIFFERENT` | `KF` | Observed scalar / observed scalar | Unique key on each side, selected field different |

All rows other than availability require both targets to succeed. Counts range
from 0 through 32, or 1 through 32 where positive is specified. VRID and name
arrays contain at most 32 entries in their upstream domains. Field values have
exactly the selected field's domain. Set comparisons intentionally remove
duplicate set members; record projections and record counts never do.

The observation array has this exact order, with no optional rows:

1. One `RESULT_AVAILABILITY` row.
2. If either target failed, stop: the array contains only that row.
3. Exactly one VRID set equality/difference row; then all `VRID_ONLY_LAB1`
   rows ascending by VRID; then all `VRID_ONLY_LAB2` rows ascending by VRID.
4. Exactly one instance-name set equality/difference row.
5. Exactly one full record-count equality/difference row.
6. All `RECORD_ONLY_LAB1` rows ascending by K; then all `RECORD_ONLY_LAB2`
   rows ascending by K.
7. All `MATCH_KEY_MULTIPLICITY` rows ascending by K.
8. For every key unique on both sides, ascending by K, exactly seven field
   equality/difference rows in this field order: `role`, `priority`,
   `interval_ms`, `version`, `running`, `disabled`, `invalid`.

K uses the record primary sort order. Field equality is exact typed equality,
not health evaluation. Equal priorities yield `FIELD_EQUAL`; different priorities
yield `FIELD_DIFFERENT`; neither produces a recommendation. No timestamp, skew,
convergence, paired-health, or simultaneous-snapshot claim is available.

For example, two successful empty results produce exactly four rows:
availability `(true, true)`, VRID-set equality `([], [])`, name-set equality
`([], [])`, and count equality `(0, 0)`. Two identical single records produce
those four kinds of rows followed by seven `FIELD_EQUAL` rows. A shared key
with two Lab1 records and one Lab2 record emits multiplicity `(2, 1)` and zero
field rows for that key, retaining all three projected records.

### Failures and prohibited inference

Failure projection preserves the fixed target and exact upstream enum spelling:

```text
PREFLIGHT_TARGET_BUNDLE_INVALID
PREFLIGHT_AUTHORIZATION_INVALID
PREFLIGHT_AUTHORIZATION_NOT_DISTINCT
PREFLIGHT_STARTUP_BINDING_UNAVAILABLE
CANONICAL_EVIDENCE_VALIDATION_FAILED
INVALID_REQUEST_INPUT
INVALID_AUTHORIZATION_INPUT
INVALID_TRUSTED_CONFIGURATION
TRUSTED_RUNTIME_FAILED
OUTPUT_RENDER_FAILED
INTERNAL_FAILURE
```

Lab1-success/Lab2-failure yields only availability `(true, false)`; the reverse
yields `(false, true)`; both failures yield `(false, false)`. The successful
target's records are still projected and sorted. No comparison involving the
unavailable target is emitted: not even a zero count or empty set. There is no
historical substitution, copied peer evidence, fabricated record, inferred
failure explanation, or retry/fallback advice.

Closed fields and discriminated value domains make the DTO incapable of issuing
health, readiness, configuration-correctness, root-cause, or remediation
verdicts. In particular, no status or kind may be `HEALTHY`, `UNHEALTHY`,
`DEGRADED`, `FAILOVER_READY`, `HA_READY`, `PRODUCTION_READY`, `SPLIT_BRAIN`,
`MISCONFIGURED`, `CORRECT_CONFIGURATION`, `INCORRECT_CONFIGURATION`,
`ROOT_CAUSE`, or `REMEDIATION_REQUIRED`.

There are no remediation/configuration command, retry/fallback advice,
credential/endpoint selection, authorization decision, command selection, or
execution-instruction fields. A valid observed instance name is opaque data,
even if it spells a prohibited verdict or resembles a command. Preserve it as
data; never interpret or render it as a verdict or executable instruction.
This distinction preserves upstream compatibility without allowing free-form
claims in structural fields.

### Canonical serialization and isolation

Use the existing JSON convention: `json.dumps` with `allow_nan=False`,
`ensure_ascii=False`, `separators=(",", ":")`, `sort_keys=True`, then strict
UTF-8 encoding. No BOM, trailing newline, whitespace variation, alternate key
ordering, duplicate JSON keys at any depth, nonfinite numbers, coercion, or
extra fields are accepted by the summary parser. Re-encoding must equal the
input bytes exactly. Record and observation arrays must already have their
specified order when parsing a summary; the parser rejects rather than repairs
unsorted summaries. The projection entrypoint is responsible for sorting valid
aggregate records.

The summary canonical byte limit is 262,144 bytes; observations are limited to
356 rows (a conservative bound: 4 base rows, up to 64 VRID-only rows, up to 64
key-level rows, and up to 224 field rows). Upstream record/name limits keep all
valid derived summaries within this byte bound, including JSON escaping of
128-byte names. These output limits do not change upstream limits.

All nested DTO values are immutable and detached from upstream objects. Every
`to_dict()` returns fresh dictionaries/lists throughout. Mutating an exported
dictionary cannot change the DTO, another export, or later bytes. Serialization
and parsing enforce the full exact schema and derived-row consistency. They
introduce no alternative serialization framework or dependency.

```text
CANONICAL_SERIALIZATION_REQUIRED = YES
IMMUTABLE_DTO_REQUIRED = YES
EXACT_FIELD_VALIDATION_REQUIRED = YES
DUPLICATE_JSON_KEY_REJECTION_REQUIRED = YES
INPUT_OUTPUT_ISOLATION_REQUIRED = YES
```

### Future implementation boundary and validation contract

Only the following two new files are the canonical scope for a separately
authorized implementation. They are not created by this specification task.

```text
DL_03_AUTHORIZED_SOURCE_FILES = validation_framework/dual_lab_vrrp_query_summary.py
DL_03_AUTHORIZED_TEST_FILES = tests/dual_lab/test_dual_lab_vrrp_query_summary.py
EXISTING_SOURCE_FILES_TO_MODIFY = NONE
EXISTING_TEST_FILES_TO_MODIFY = NONE
DEPENDENCY_CHANGE_REQUIRED = NO
```

The future module may reuse the inert DL-01 and Stage-2 contract modules and
standard-library data/JSON facilities. It must not import or invoke S2-RO-11,
the DL-02 orchestrator, runners, adapters, brokers, or live entrypoints. No
network query, Lab1/Lab2 access, credential resolution, authorization acquisition
or signing, replay consumption, command selection, or trusted runtime-config
access is permitted. No SSH, NETCONF, RESTCONF, external API/provider/model,
queue, scheduler, worker, AI loop, config backup/change, or production execution
path is added. No CLI/task-registry/report renderer/dashboard integration,
Day1-Day160 rewrite, second safety matrix, or next-slice implementation belongs
to this scope. If implementation cannot satisfy the contract in these two new
files, stop and report the exact conflict; do not broaden the scope.

The future test file must establish the following deterministic assertions.
These are acceptance tests for the future implementation, not tests run by
this documentation task.

| Test | Required assertion |
| ---: | --- |
| 1 | Both targets SUCCESS: exact target projections and complete ordered derived rows. |
| 2 | Lab1 SUCCESS / Lab2 FAILURE: availability true/false only; Lab1 records retained. |
| 3 | Lab1 FAILURE / Lab2 SUCCESS: availability false/true only; Lab2 records retained. |
| 4 | Both FAILURE: availability false/false only; exact failure categories retained. |
| 5 | Both SUCCESS with zero records: exactly the four rows specified above. |
| 6 | Identical single records: exactly eleven rows, seven field equalities. |
| 7 | Multiple records: all records retained and sorted by the full key. |
| 8 | Reverse/shuffle either target's records: identical summary canonical bytes. |
| 9 | Repeat equivalent input, reorder input object keys before canonical encoding, or vary valid discarded envelope metadata: identical output bytes. |
| 10 | Exactly seven top-level fields; missing/extra fields reject in summary parsing. |
| 11 | Exact success/failure field sets; failure records absent, null/empty variants reject. |
| 12 | Exactly nine record fields; wrong domains, missing/extra fields reject. |
| 13 | Upstream envelope metadata excluded; sensitive/raw field injection rejected at every schema depth; sanitized errors retain no rejected input or child exception. |
| 14 | Same VRID sets: one VRID_SET_EQUAL row with sorted unique sets. |
| 15 | Different VRID sets: one VRID_SET_DIFFERENT and exact directional VRID-only rows. |
| 16 | Lab1-only record keys: RECORD_ONLY_LAB1 with full occurrence count and peer zero. |
| 17 | Lab2-only record keys: RECORD_ONLY_LAB2 with peer zero and full occurrence count. |
| 18 | Unique exact matched key with equal fields: seven ordered FIELD_EQUAL rows. |
| 19 | Change each comparable field independently: exactly that field's row becomes FIELD_DIFFERENT with exact values. |
| 20 | Equal priority values: factual equality only, no role/health inference. |
| 21 | Different priority values: factual difference only, no preference/advice. |
| 22 | All boolean flag combinations compare exact booleans; integers reject as flags. |
| 23 | Same VRID/different name, same name/different VRID, similar names, positions, or priorities never establish a match. |
| 24 | Identical and differing duplicates survive; complete tie-breakers are stable; common duplicate key yields counts and no field pairing. |
| 25 | Failed target never receives records, historical/peer substitution, zero-count, or empty-set comparisons. |
| 26 | Malformed/noncanonical/oversize aggregate bytes, wrong input types, subclasses, and forged objects reject with no DTO. |
| 27 | Extra aggregate fields, especially cross_target_observations, reject through DL-01 validation. |
| 28 | Swapped targets or mismatched target/evidence bindings reject. |
| 29 | Invalid success evidence, including forged/out-of-domain record values, rejects. |
| 30 | Health/readiness/configuration verdict kinds and fields reject; verdict-like instance names remain opaque observed data. |
| 31 | Root-cause kinds/fields reject. |
| 32 | Remediation kinds/fields reject. |
| 33 | Configuration command/instruction kinds/fields reject; command-like names remain inert data. |
| 34 | Retry/fallback advice kinds/fields reject. |
| 35 | Import and all public valid/rejected paths make zero execution/network calls and no application file/runtime I/O beyond normal Python module loading; existing execution boundaries are unreachable. |
| 36 | Import and all public paths make zero provider/model calls and load no provider integration. |
| 37 | Same/different instance-name sets yield exact sorted set rows, including empty sets. |
| 38 | Equal/different full counts include duplicates; all 11 failure categories preserve exact spelling. |
| 39 | Canonical summary round-trip; duplicate JSON keys at every depth, wrong byte framing, unsorted arrays, altered/missing/extra/inconsistent derived rows reject. |
| 40 | Frozen nested DTOs, fresh-export isolation, and revalidation after tampering; execution_authorized remains false. |
| 41 | Maximum 32 records per target, maximum UTF-8 names with escaping, Unicode ordering, and duplicate-heavy inputs stay within output bounds. |
| 42 | Exact public export set and byte-only signatures; no executor, callback, runtime-config, or authorization argument. |

Future validation must include
`python -m pytest tests/dual_lab/test_dual_lab_vrrp_query_summary.py`,
`python -m pytest tests/dual_lab/test_dual_lab_vrrp_query_contract.py`,
`python -m pytest`, and `python network_lab.py --task report-index` under the
repository's offline safety controls. Negative cases must demonstrate zero
execution, not merely an error result. No dedicated runner is introduced.
Record exact counts, skips, guard outcomes, and any optional-report WARN; none
of those results is pre-approved by this specification.

### Specification decision and documentation review

The specification's consistency/readability review confirmed distinct summary
and input schemas, closed observation types and ordering, duplicate handling
compatible with upstream, explicit failure absence, and a scope of two new
files. The accepted DL-02 identity, review evidence, and Stage-2
closure remain unchanged. The current documentation reconciliation aligns this
record, README, and the automation plan on DL-03 implemented / governed review PASS /
Owner acceptance ACCEPTED. The conclusion, allowed documentation scope, excluded
execution scope, accepted implementation identity, retained evidence, and next
Owner decision are explicit. This documentation review changes no runtime behavior or
specification requirement and creates no second safety matrix.

```text
DL_02_ACCEPTED = YES
DL_03_SPECIFICATION_STATUS = ESTABLISHED
DL_03_IMPLEMENTED = YES
DL_03_FRESH_INDEPENDENT_REVIEW_RESULT = PASS
DL_03_FRESH_GOVERNED_REVIEW_RESULT = PASS
DL_03_OWNER_ACCEPTANCE = ACCEPTED
DL_03_ACCEPTANCE_RESULT = PASS
DL_03_ACCEPTED = YES
DL_04_IMPLEMENTATION_STARTED = NO
MINIMUM_TEST_MATRIX_ESTABLISHED = YES
DOCUMENTATION_CONSISTENCY_REVIEW = PASS
DOCUMENTATION_READABILITY_REVIEW = PASS
COMPLETE_DUAL_LAB_MVP = NO
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
NEXT_REQUIRED_OWNER_DECISION = REVIEW_CANONICAL_PLAN_AND_AUTHORIZE_DL_04_READINESS_OR_SPECIFICATION_WORK
```
