# Dual-Lab VRRP AI Query MVP: DL-05 Accepted

**Decision summary: DL-05 is ACCEPTED / PASS; the bounded offline Dual-Lab MVP
is complete.** The separate Owner acceptance decision accepted implementation
`0e5dfbc1d143a6de7ba59e4bff9bd1788e809043`, integrated into `main` through
PR #93. Pre-merge Safe CI, post-merge Safe CI on that exact SHA, and the fresh
exact-SHA governed review passed. All seven acceptance predicates passed, with
zero unresolved material findings. DL-02, DL-03, and DL-04 remain accepted.

`DL_05_OWNER_ACCEPTANCE = ACCEPTED`, `DL_05_ACCEPTANCE_RESULT = PASS`,
`DL_05_ACCEPTED = YES`, `COMPLETE_DUAL_LAB_MVP = YES`, and
`OFFLINE_DUAL_LAB_MVP_ACCEPTED = YES`. P3 remains OPEN_NON_BLOCKING; seven
pre-existing build warnings remain maintenance items. No live authority,
live readiness, configuration mutation, provider/model integration, or production
readiness is granted. DL-06's execution contract remains NOT_ESTABLISHED.

The [DL-05 record](#dl-05-reviewed-exact-sha-candidate) retains the reviewed
candidate and [completed Owner acceptance](#completed-owner-acceptance-and-active-status).
The [DL-05 canonical contract](#dl-05-canonical-integration-and-safe-ci-contract)
retains its requirements. Earlier specification and predecessor status snapshots
are historical; the completed DL-05 acceptance below defines current status.
The [accepted DL-04 closure record](#dl-04-reviewed-closure-candidate) and
[DL-04 closure contract](#dl-04-canonical-closure-contract) retain their accepted
identities, evidence, and safety boundaries.

## Purpose and planning boundary

This is the canonical repository record for the accepted DL-02 implementation,
its completed independent review and Owner acceptance, plus the DL-03 canonical
specification, accepted implementation, completed governed review, and completed
Owner acceptance decision, and the DL-04 closure specification, completed closure
execution, completed fresh governed review, and completed Owner acceptance.
It also establishes the DL-05 integration, Safe CI, evidence, fresh exact-SHA
review, and Owner-acceptance contract.
The DL-03 specification resolved the readiness
review's `BLOCKED_CANONICAL_SCOPE_AMBIGUITY`; the separately authorized
implementation, review, and acceptance are recorded below.
The prior DL-04 post-acceptance reconciliation recorded that completed decision.
The current Owner authorization permits post-acceptance status reconciliation in
this record, README, and the automation plan, followed by one local documentation
commit above pre-acceptance record `c275b1b58a696b85a9d516ab1b15cceb77432ad2`.
It records the completed decision without repeating acceptance or review.
No source, test, workflow, dependency, sealed-evidence, external-wrapper, or
Stage-2 closure change is authorized. No application validation, Safe CI rerun,
push, merge, branch deletion, P3 remediation, or live operation is performed.
The documentation descendant does not replace the accepted implementation SHA
or inherit its application CI/review. Accepted predecessors remain unchanged.

In the retained DL-02 history, the pre-acceptance documentation commit
`76ce998531de59c201eaa6f123e57b1f9d364b19` established the candidate record and
resolved the documentary gap. The subsequent read-only acceptance retry returned
ACCEPT / PASS without changing source, tests, or documentation. That completed
decision remains unchanged.

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
DL-03 Owner acceptance also completed, as recorded below. The subsequent DL-04
readiness review and documentation-only specification authorization are recorded
in the DL-04 section; neither starts closure execution.

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
DL_03_POST_ACCEPTANCE_NEXT_OWNER_DECISION_HISTORICAL = REVIEW_CANONICAL_PLAN_AND_AUTHORIZE_DL_04_READINESS_OR_SPECIFICATION_WORK
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
DL_03_POST_ACCEPTANCE_NEXT_OWNER_DECISION_HISTORICAL = REVIEW_CANONICAL_PLAN_AND_AUTHORIZE_DL_04_READINESS_OR_SPECIFICATION_WORK
```

## DL-04 reviewed closure candidate

This retained post-acceptance record describes the reconciliation at
`d3216f774d28e84b828355a727bc9807f1ce3b46`. References below to that
reconciliation and its next decision are historical; current DL-05 status and
authority are defined in the [DL-05 contract](#dl-05-canonical-integration-and-safe-ci-contract).
Acceptance, candidate identity, evidence, and the open finding remain unchanged.

**DL-04 is accepted: closure PASS, fresh governed review PASS, and completed
Owner acceptance ACCEPT / PASS.** The completed review found zero unresolved
material findings and exactly one open non-blocking P3 finding. This
documentation-only descendant records the completed decision; the accepted
closure candidate and sealed evidence retain their exact identities.

### Exact candidate, evidence identity, and current status

```text
DL_02_ACCEPTED = YES
DL_03_ACCEPTED = YES
DL_04_SPECIFICATION_STATUS = ESTABLISHED
DL_04_SPECIFICATION_COMMIT = 0972910c4d5e2bb7d70acbb50c4721234f20d0dc
DL_04_CLOSURE_EXECUTION_STARTED = YES
DL_04_CLOSURE_EXECUTION_COMPLETED = YES
DL_04_CLOSURE_RESULT = PASS
DL_04_CLOSURE_CANDIDATE = YES
DL_04_CANDIDATE_COMMIT = 0972910c4d5e2bb7d70acbb50c4721234f20d0dc
DL_04_CANDIDATE_PARENT = d3bbe767fa5653bb7ee213594959877fd4ff80fe
DL_04_MANIFEST_SHA256 = f7dd14e1ea471032cf68e108d2ea85b144096d28f3aa6c339efd89bf27567449
DL_04_FRESH_GOVERNED_REVIEW_RESULT = PASS
DL_04_REVIEW_MATERIAL_FINDINGS = 0
DL_04_REVIEW_NONBLOCKING_FINDINGS = 1
DL_04_OWNER_ACCEPTANCE = ACCEPTED
DL_04_ACCEPTANCE_RESULT = PASS
DL_04_ACCEPTED = YES
DL_04_STATUS = ACCEPTED
DL_04_ACCEPTED_CLOSURE_CANDIDATE = 0972910c4d5e2bb7d70acbb50c4721234f20d0dc
DL_04_ACCEPTED_CLOSURE_PARENT = d3bbe767fa5653bb7ee213594959877fd4ff80fe
DL_04_ACCEPTED_MANIFEST_SHA256 = f7dd14e1ea471032cf68e108d2ea85b144096d28f3aa6c339efd89bf27567449
DL_04_ACCEPTANCE_BASIS = CLOSURE_PASS_PLUS_FRESH_GOVERNED_REVIEW_PASS_PLUS_OWNER_ACCEPTANCE
DL_04_ACCEPTANCE_CANONICAL_STATE_HEAD = d921385021d21761af2aef81c9ec7e3d283123e9
DL_04_SAFE_CI_REQUIRED = NO
SAFE_CI_RUN = NO
DL_05_SAFE_CI_BOUNDARY_PRESERVED = YES
DL_05_STARTED = NO
COMPLETE_DUAL_LAB_MVP = NO
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
DL_04_POST_ACCEPTANCE_NEXT_OWNER_DECISION_HISTORICAL = AUTHORIZE_DL_05_READINESS_AND_P3_IMPACT_REVIEW
```

The sealed external execution is identified by run ID
`nal_dl04_closure_20261002_01`. Its evidence root is represented here as
`<closure-root>/evidence`; its physical retention path stays outside the public
repository. The root contains `candidate-manifest.json` and
`dl04-closure-result.json`; `manifest-receipt.json` is retained beside the evidence
root. The receipt binds the exact manifest hash above to the candidate and parent.
The specification and candidate identities are equal; the comparison base equals
the parent. The pre-acceptance canonical state commit
`d921385021d21761af2aef81c9ec7e3d283123e9` has that candidate as its direct
parent. This post-acceptance documentation commit descends directly from that
canonical state commit; its actual hash is reported after commit. The accepted
closure candidate remains `0972910c4d5e2bb7d70acbb50c4721234f20d0dc`.

Owner acceptance completed ACCEPT / PASS against that canonical state and the
exact candidate and manifest above. The completed decision is retained in the
authorized Owner-acceptance response in the same conversation and reaffirmed by
the post-acceptance reconciliation authorization. No repository or evidence
mutation occurred during acceptance. This task records that decision only.

The completed fresh review established exact manifest hash/candidate binding,
valid provenance, all 14 required artifacts present, and all 26 sealed evidence
files unchanged. Fresh execution results were distinguished from historical
comparison inputs. All 1,021 tracked candidate files retained their raw bytes
during closure execution and review. These are retained results for the candidate,
not a claim that this later documentation commit was closure-tested.

The completed governed review is recorded in the preceding authorized review
response in the same conversation and reaffirmed by the Owner's reconciliation
authorization. It was fresh technical/governed inspection of the exact candidate
and frozen evidence, with read-only checks and no required validation rerun. It
was not a separate-human, separate-agent-identity, or separate-conversation
attestation. Those process limits do not change its PASS result. This record does
not claim a new external `governed-review.json` or Owner-acceptance receipt was
created. The sealed execution artifact correctly retains its earlier
`PENDING_FRESH_GOVERNED_REVIEW` status; this later canonical record records the
completed review and Owner acceptance without altering that frozen artifact.

### Reviewed fresh closure results

These results belong to the completed fresh DL-04 execution. They are recorded
from the sealed bundle and completed governed review, not rerun by this task.
Use the [canonical command map](#candidate-identity-and-deterministic-offline-command-map)
and manifest index to navigate to the exact suite evidence.

| Validation | Collected | Passed | Established skips | Unexpected skips | Failures / errors | Logical artifact |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| DL-01 focused | 256 | 256 | 0 | 0 | 0 / 0 | `focused-dl01.json` |
| DL-02 focused | 185 | 185 | 0 | 0 | 0 / 0 | `focused-dl02.json` |
| DL-03 focused | 211 | 211 | 0 | 0 | 0 / 0 | `focused-dl03.json` |
| Complete Dual-Lab | 652 | 652 | 0 | 0 | 0 / 0 | `dual-lab.json` |
| Stage-2 offline | 1892 | 1890 | 2 | 0 | 0 / 0 | `stage2.json` |
| Full offline | 4672 | 4669 | 3 | 0 | 0 / 0 | `full-pytest.json` |

All six exact workflow/governance proofs passed (`workflow-proofs.json`), and all
28 canonical coverage areas passed (`requirement-to-evidence.json`). The review
checked suite membership and test-level outcomes, exact established skip
identities, source fingerprints, denial causality, and requirement mappings;
matching totals alone were not the basis for PASS.

```text
WORKFLOW_REQUIRED_PROOF_COUNT = 6
WORKFLOW_REQUIRED_PROOFS_PASSED = 6
CANONICAL_COVERAGE_AREA_COUNT = 28
CANONICAL_COVERAGE_AREAS_PASSED = 28
KNOWN_PRE_EXISTING_GUARD_DENIAL_COUNT = 3
KNOWN_PRE_EXISTING_GUARD_DENIAL_SET_MATCH = YES
NEW_OR_UNCLASSIFIED_GUARD_DENIAL_COUNT = 0
DL04_CAUSED_GUARD_DENIAL_COUNT = 0
REPORT_INDEX_RESULT = WARN
REPORT_INDEX_EXIT_CODE = 0
REPORT_INDEX_FAILURE_COUNT = 0
REPORT_INDEX_OPTIONAL_MISSING_COUNT = 13
REPORT_INDEX_MANDATORY_MISSING_COUNT = 0
REPORT_INDEX_UNKNOWN_COUNT = 0
REPORT_INDEX_WARN_ACCEPTABLE = YES
```

The guard counter covers the top-level parent process. The exact classifications
remain in `skip-classification.json` and `guard-classification.json`. Each missing
report in `report-index.log` and `report-index.json` was verified optional under
the unchanged registry. The WARN does not establish a safety or regression issue.

The candidate-bound security review's sixteen assertions and six preservation
checks passed. Stage-2 authority, Owner authorization, replay, credential,
pinned-host, and exact read-only command boundaries remain unchanged. Pair
identity collision precedence, rejected-target zero invocation, canonical
evidence revalidation, closed immutable schemas, and sanitized failures remain
supported. No secret or raw live data was found in the evidence. The external
preparation command-length failure occurred before process startup, affected no
repository state, and did not contaminate accepted evidence. Read-only review
probe corrections likewise changed no repository or sealed evidence files.

### Open non-blocking review finding

```text
FINDING_ID = DL04_REVIEW_P3_PYTEST_ARGV_RECORDING
SEVERITY = P3
TITLE = Preserve non-path arguments in recorded pytest argv
LOCATION = external closure wrapper run_review.py, reviewed line 67
CLASSIFICATION = NON_BLOCKING
MATERIAL_FINDING = NO
CLOSURE_INVALIDATED = NO
SEALED_EVIDENCE_CONTAMINATED = NO
REPOSITORY_AFFECTED = NO
NONBLOCKING_FINDINGS = 1
UNRESOLVED_MATERIAL_FINDINGS = 0
P3_ARGV_RECORDING_FINDING_STATUS = OPEN_NON_BLOCKING
```

The external wrapper's recorded pytest argv does not preserve all non-path
arguments with complete fidelity: the recorded `no:cacheprovider` option value
is rendered as `<external>/no:cacheprovider`. The fingerprinted guard passed the
correct literal argument to pytest. The fresh governed review independently
verified actual suite membership, test-level outcomes, exact skips, evidence
provenance, and candidate integrity, so this recording limitation does not
invalidate closure evidence. The finding is not fixed; neither wrapper nor sealed
evidence is edited by this reconciliation.

Future DL-05 planning must decide whether this finding requires remediation
before reusing the affected wrapper for exact argv / command-attestation evidence.
That decision requires separate authorization; this task does not repair the
finding or start DL-05.

### Documentation checks and remaining decision

This reconciliation aligns the decision summary, exact identities, evidence
references, finding counts, completed acceptance, and next decision with README
and the automation plan. Documentation checks cover consistency, readability,
local links/references, authorized path scope, and whitespace. No application
test, report-index, closure validation, or governed review is repeated.

DL-02 and DL-03 remain accepted without integration or release. DL-04 is accepted
for the exact closure candidate above, based on closure PASS, fresh governed
review PASS, and completed Owner acceptance ACCEPT / PASS. DL-05 remains
unstarted, and its integrated-implementation Safe CI has not run. At this
reconciliation, the next Owner decision was
`AUTHORIZE_DL_05_READINESS_AND_P3_IMPACT_REVIEW`. This documentation
grants no Lab1/Lab2 access, SSH/NETCONF/RESTCONF, provider/model operation, secrets
handling, configuration backup/change, production readiness, or complete-MVP
acceptance. No Stage-2 semantics, historical proof, or safety gate is changed.

## DL-04 canonical closure contract

**Retained specification: the separately authorized execution and review are
recorded above; its scope and requirements remain unchanged.** References below
to a future run or the specification task describe the original contract boundary.
DL-04 is the integrated offline validation, reviewer-evidence,
security-review, and closure layer over the accepted DL-01 through DL-03 behavior.
It adds no runtime capability. The completed readiness decision was
`DL_04_CANONICAL_SPECIFICATION_REQUIRED`: all 28 reviewed areas have predecessor
coverage, and no missing negative scenario or production-code defect was
demonstrated. This contract resolves the documentary scope gap without reopening
predecessor acceptance or creating tests merely to name a DL-04 file.

The specification base is `d3bbe767fa5653bb7ee213594959877fd4ff80fe` on
`codex/dual-lab-vrrp-ai-query-mvp`. Accepted DL-02 and DL-03 implementation SHAs
remain the exact identities above. The resulting documentation commit is
identified externally by its actual SHA and parent; no self-referential commit
identifier is guessed inside its own contents.

### Purpose, authority, and mutation boundary

```text
DL_04_PURPOSE = INTEGRATED_OFFLINE_NEGATIVE_REGRESSION_VALIDATION_AND_REVIEWER_EVIDENCE_CLOSURE
DL_04_RUNTIME_CAPABILITY_ADDED = NO
DL_04_NEW_PRODUCTION_SOURCE_REQUIRED = NO
DL_04_EXISTING_PRODUCTION_SOURCE_MODIFICATION_REQUIRED = NO
DL_04_EXECUTION_AUTHORITY = NONE
DL_04_MODEL_PROVIDER_INTEGRATION = NO
DL_04_LIVE_AUTHORITY = NO
DL_04_CONFIG_MUTATION_AUTHORITY = NO
PRODUCTION_SOURCE_CHANGES = NONE
EXISTING_PRODUCTION_SOURCE_CHANGES = NONE
NEW_TEST_FILES = NONE
EXISTING_TEST_FILE_CHANGES = NONE
DEPENDENCY_CHANGES = NONE
WORKFLOW_CHANGES = NONE
EXISTING_ACCEPTED_COVERAGE_MUST_BE_REUSED = YES
DUPLICATIVE_TEST_CREATION_REQUIRED = NO
NO_MISSING_NEGATIVE_SCENARIO_CURRENTLY_DEMONSTRATED = YES
```

The current specification task may modify only this document and create its one
local documentation commit. A later closure-execution task may produce fresh
external validation/reviewer evidence and candidate provenance after separate
authorization. Its default repository mutation scope is empty, including this
document. Canonical status/documentation reconciliation needs a separately named
Owner authorization and exact paths; it is not implied by a passing run.

No source, test, dependency, workflow, configuration, AGENTS.md, historical
Stage-2 record, Day1-Day160 artifact, dashboard, runner, or task registry change
is part of DL-04. No dedicated Stage-2 regression file is required. No live
Lab1/Lab2 access, SSH/NETCONF/RESTCONF, provider/model call, credential acquisition,
configuration backup/change, production execution, or DL-05 work is authorized.
If a genuine uncovered canonical requirement or defect is discovered, stop and
report it. Adding/fixing tests, source, or guard policy requires separate Owner
authorization; closure execution must not silently become a repair task.

### Existing coverage and reviewer navigation

DL-01 is the [inert aggregate contract](../../validation_framework/dual_lab_vrrp_query_contract.py).
DL-02 is the [fixed synchronous orchestrator](../../validation_framework/dual_lab_vrrp_query_orchestrator.py),
whose structural preflight and POLICY_2 behavior are described above. Pair-level
identity collisions reject both targets before invocation, even when a safely
parsed identity belongs to a locally ineligible target. With distinct identities,
a locally rejected target does not prevent the eligible peer's single mocked
handoff. DL-03 is the [facts-only projection](../../validation_framework/dual_lab_vrrp_query_summary.py):
deterministic sorting, exact comparisons, preserved multiplicity, failure absence,
and no health/root-cause/remediation inference. Data validity grants no authority.

Every row below has classification
`EXISTING_BUT_REQUIRES_DL04_REVALIDATION`. This means fresh closure evidence is
required, not that accepted DL-01/02/03 behavior is being reopened. These are
coverage references, not a second safety matrix. Test symbols are resolved at
the candidate; all parameterized instances run through the complete suites.

- **C**: [DL-01 tests](../../tests/dual_lab/test_dual_lab_vrrp_query_contract.py).
- **O**: [DL-02 tests](../../tests/dual_lab/test_dual_lab_vrrp_query_orchestrator.py).
- **S**: [DL-03 tests](../../tests/dual_lab/test_dual_lab_vrrp_query_summary.py).

| ID | Existing area | Representative test symbols (all prefixed `test_`) |
| ---: | --- | --- |
| 1 | Canonical aggregate validation | C: `all_outcome_combinations_round_trip`, `strict_json_framing_types_limits_and_canonical_bytes`; O: `final_aggregate_failure_returns_no_partial_output` |
| 2 | Immutable/exact-field contracts | C: `every_aggregate_field_required`, `immutability_direct_construction_and_input_output_isolation`; S: `10_to_13_every_field_required_and_extras_reject`, `40_serializers_revalidate_tampering` |
| 3 | Duplicate JSON-key rejection | C: `duplicate_keys_rejected_at_every_depth`; S: `39_summary_duplicate_keys_at_each_depth`, `39_aggregate_duplicate_keys_at_each_depth` |
| 4 | Target binding | C: `aggregate_slot_target_binding`; O: `other_lab_request_binding_rejected`; S: `28_29_upstream_binding_and_identity_rejections` |
| 5 | Authorization ID/reference distinctness | O: `duplicate_identity_blocks_both_with_zero_invocations`, `p1_parseable_collision_overrides_local_rejection` |
| 6 | Malformed/expired authorization | O: `envelope_rejection_uses_existing_stage2_semantics`, `p1_distinct_identity_preserves_local_failure_and_policy2`, `p1_unparseable_identity_does_not_fabricate_collision` |
| 7 | Cross-target swaps | O: `invalid_bundle_only_skips_its_target`, `configuration_preflight_is_structural_and_target_local`, `envelope_rejection_uses_existing_stage2_semantics`; S: `summary_target_binding_and_tag_validation` |
| 8 | Missing runtime/startup binding | O: `both_preflights_finish_before_any_invocation`, `configuration_preflight_is_structural_and_target_local`, `two_local_failures_have_no_invocations` |
| 9 | No retry | O: `six_runtime_failures_preserved_independently_without_retry`, `exact_public_surface_no_executor_and_no_parallel_or_alternate_path` |
| 10 | No fallback | O: `invalid_bundle_only_skips_its_target`, `candidate_evidence_revalidated_without_substitution`, `exact_public_surface_no_executor_and_no_parallel_or_alternate_path` |
| 11 | No parallelism | O: `success_order_overlap_call_limit_and_canonical_roundtrip`, `exact_public_surface_no_executor_and_no_parallel_or_alternate_path` |
| 12 | No threads | O: `exact_public_surface_no_executor_and_no_parallel_or_alternate_path`; S: `35_36_42_static_public_surface_and_inert_import` |
| 13 | No async | C: `exact_public_surface_and_no_execution_capabilities`; O: `exact_public_surface_no_executor_and_no_parallel_or_alternate_path`; S: `35_36_42_static_public_surface_and_inert_import` |
| 14 | No queue | Same C/O/S restricted-surface tests as row 13, with source inspection |
| 15 | No scheduler | Same C/O/S restricted-surface tests as row 13, with source inspection |
| 16 | No worker | Same C/O/S restricted-surface tests as row 13, with source inspection |
| 17 | Canonical evidence revalidation | C: `direct_success_detaches_evidence_and_revalidates_forged_records`, `serialization_rechecks_objects_altered_after_construction`; O: `candidate_evidence_revalidated_without_substitution` |
| 18 | Raw-output leakage rejection | C: `prohibited_data_cannot_enter_evidence_or_record`; O: `six_runtime_failures_preserved_independently_without_retry`; S: `13_envelope_exclusion_and_exact_fields`, `public_errors_discard_outer_context_and_upstream_failure` |
| 19 | Credential/signature/path leakage rejection | C: `unknown_and_prohibited_top_level_fields_rejected`; O: `bundle_immutable_redacted_exact_fields_and_no_leakage`; S: `10_to_13_every_field_required_and_extras_reject`, `27_extra_aggregate_fields_rejected_upstream` |
| 20 | Deterministic DL-03 projection | S: `07_to_09_multirecord_sort_permutations_metadata_and_identity`, `39_derived_rows_recomputed_and_exactly_typed` |
| 21 | Multi-record projection | S: `07_to_09_multirecord_sort_permutations_metadata_and_identity`, `41_maximum_records_name_lengths_and_serialization_bounds` |
| 22 | Duplicate matching-key handling | S: `24_duplicate_multiplicity_never_pairs_or_collapses`, `24_complete_duplicate_sort_tie_breaker` |
| 23 | Missing-evidence behavior | S: `01_to_04_outcomes_and_failure_absence`, `11_failure_cannot_have_records`, `25_38_failure_vocabulary_and_no_fabrication` |
| 24 | Prohibited health inference | S: `30_to_34_prohibited_structures_and_opaque_observed_names`; closed observation vocabulary above |
| 25 | Prohibited root-cause inference | S: `30_to_34_prohibited_structures_and_opaque_observed_names` (`ROOT_CAUSE`) |
| 26 | Prohibited remediation output | S: `30_to_34_prohibited_structures_and_opaque_observed_names`, `33_command_like_name_remains_only_data` |
| 27 | No provider/model integration | C: `exact_public_surface_and_no_execution_capabilities`; O: `exact_public_surface_no_executor_and_no_parallel_or_alternate_path`; S: `35_36_42_static_public_surface_and_inert_import` |
| 28 | No execution authority in DL-03 | S: `01_to_04_outcomes_and_failure_absence`, `35_36_42_static_public_surface_and_inert_import`, `40_serializers_revalidate_tampering` |

Restricted imports/public surfaces and source inspection support the absence of
threads/queue/scheduler/worker; do not describe them as separate dynamic tests
for every mechanism. Leakage checks cover schema exclusion, envelope removal,
sanitized errors/representations, and output silence. Opaque observed names are
not a general secret-detection mechanism. No new end-to-end composition test is
mandated by this contract; any later proposed coverage addition needs its own
demonstrated gap and authorization.

### Candidate identity and deterministic offline command map

Before a future run, the Owner must name the exact candidate SHA **C**, its parent
**P**, the comparison base **B**, and the specification commit **S** containing
this contract. Record all four as full resolved SHAs in `candidate-manifest.json`.
The specification's base above is fixed; do not assume that it is also a future
candidate's parent. No floating HEAD or branch-only identity suffices. Require
the clean authorized branch, the accepted predecessor identities, and unchanged
accepted source/test bytes before starting. A moved candidate or ambiguous base
blocks the run; do not move history to repair it.
Require C to equal S or be an explicitly authorized documentation-only descendant
of S. Compare the complete production-source/test file sets and bytes with S;
no source/test delta is allowed. Record the comparison with B separately rather
than treating an arbitrary comparison base as permission for new behavior.

Use a fresh external disposable checkout/copy of C, preserving exact tracked raw
bytes and required local fixture Git behavior. The primary checkout remains
unchanged. Verify any preinstalled interpreter/dependency assets without
installation, network fetch, or dependency changes. Record versions, executable
fingerprints, import-root identities, platform, non-TTY mode, guard and launcher
hashes, and the resolved command map externally. Never capture environment dumps,
credential stores, live startup bindings, or private runtime configuration.

All commands below are **future logical invocations inside the guarded external
launcher**, not permission to run unguarded CLI commands. The deterministic
procedure is to select one row, install the accepted guard before importing
pytest/application modules, then call `pytest.main` with this exact common argv:

```text
[-p, no:cacheprovider, --color=no, -q, --tb=short, -rs,
 --basetemp, <fresh-external-run-root>/pytest, <row-targets...>]
```

| Logical mode | Canonical targets / logical command | Required artifact |
| --- | --- | --- |
| `focused-dl01` | `python -m pytest tests/dual_lab/test_dual_lab_vrrp_query_contract.py` | `focused-dl01.json` |
| `focused-dl02` | `python -m pytest tests/dual_lab/test_dual_lab_vrrp_query_orchestrator.py` | `focused-dl02.json` |
| `focused-dl03` | `python -m pytest tests/dual_lab/test_dual_lab_vrrp_query_summary.py` | `focused-dl03.json` |
| `dual-lab` | `python -m pytest tests/dual_lab` | `dual-lab.json` |
| `stage2` | `python -m pytest tests/stage2` | `stage2.json` |
| `full` | `python -m pytest` (no target restriction) | `full-pytest.json` |
| `report` | `python network_lab.py --task report-index` | `report-index.log` and `report-index.json` |

Run rows serially, with fresh external temporary storage per mode. Disable plugin
autoload, pytest cache and bytecode writes; clear injected pytest options/plugins.
Do not use selectors, deselection, fail-open mocking, response files, or extra
skips to reduce required coverage. Preserve collection counts, every test outcome,
exit status, exact skip reasons, guard observations and sanitized logs. A test
failure, collection error, missing proof, or guard discrepancy stops promotion;
retain failed/setup-attempt evidence instead of overwriting it with a retry.

The accepted guard is the external `frozen_v3_guard.py`, SHA256
`0c0357e7291efb90b9c0a21aec212ddb183cc8778182060020e087ea60d4a5bb`.
Resolve it through retained evidence, never by an unverified same-name file.
The external launcher may relocate approved disposable/evidence/tool paths and
map the modes above, and add result collection, without changing frozen guard
bytes or denial/skip semantics. Review and fingerprint that launcher before
execution. If the guard or required baseline cannot be recovered, or relocation
needs a guard-policy change, stop for Owner resolution; do not improvise a weaker
guard or install dependencies. This task creates or executes no launcher.

Preserve guard coverage through collection, execution, teardown, ordinary Python
children, Windows spawn, and permitted Node subprocesses. Deny real sockets/DNS,
native credential/trust acquisition, provider calls, uncontrolled subprocesses,
private configuration, and live device I/O. The existing narrow synthetic-memory,
disposable SQLite, fixture-Git, guarded child-process, and symlink test allowances
may be reused only unchanged. They prove existing offline regressions, not new
production threads/workers/parallel execution. The guard is a trusted regression
harness, not a sandbox for arbitrary hostile code. Do not broaden its guarantees.

The six following proofs must each report call-phase `passed` in the complete
fresh full-suite result. Extract their node IDs/outcomes into
`workflow-proofs.json`; a count, collection-only result, xfail, or skip is not PASS:

```text
tests/stage2/test_authorization_envelope_ledger.py::test_competing_processes_and_process_restart
tests/workflow_governance/test_validate_fast.py::test_cli_plan_rejects_response_file_path_with_deterministic_json
tests/workflow_governance/test_validate_fast.py::test_symlink_escape_changed_path_is_rejected_when_supported
tests/workflow_governance/test_validate_scope.py::test_option_like_revision_cli_emits_json_and_exit_two[base]
tests/workflow_governance/test_validate_scope.py::test_option_like_revision_cli_emits_json_and_exit_two[head]
tests/workflow_governance/test_validate_scope.py::test_symlink_escape_is_rejected_when_supported
```

These are preservation checks for the accepted workflow/replay behavior. They
neither reopen deferred workflow research nor authorize running Safe CI.

```text
HISTORICAL_RESULTS_COUNT_AS_FRESH_DL04_EVIDENCE = NO
FRESH_DL04_VALIDATION_REQUIRED = YES
```

### Exact established skips and guard-denial baseline

The identity set below comes from the retained accepted DL-03 review evidence
summarized above, inspected during this specification task without rerunning it.
Logical baseline artifact fingerprints bind that source without publishing its
private retention path:

| Historical artifact | Raw SHA256 |
| --- | --- |
| `verification.json` | `1b982be6d356c1ec2af3548b26123563127c3205bcc46854aa6d1adcdf73eba6` |
| `stage2.json` | `69b273aa9f2aee28f05791e81b3a96bd8bb50d24a1d29fb19415f16e2ae063d9` |
| `full.json` | `52cc9c288bfc0401e8497db352aced56703a32ecb2a980371fe987f8cfb1b1d0` |

Historical artifacts are read-only comparison inputs, not files to copy into the
fresh result slots. Their retrieval location is supplied locally outside the
repository. Missing artifacts or fingerprint mismatch blocks exact baseline
comparison. The 211/652/1890/4669 passes, established 2/3 skips, 66 external probes,
three denials and 13 optional missing reports remain historical results only.
DL-04 does not require duplicating the old external probe suite or its test count;
it requires the mapped current tests and fresh security review below.

| Accepted skip node ID | Exact reason | Applicable suite/environment |
| --- | --- | --- |
| `tests/stage2/test_live_authorization_owner_trust_root.py::test_disposable_regular_file_is_accepted_by_exact_native_path` | `Accepted Stage-2 offline safety exclusion: real Win32 trust-root source operations are forbidden.` | Stage-2 and full, accepted Windows offline guard |
| `tests/stage2/test_live_authorization_owner_trust_root.py::test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical` | `Accepted Stage-2 offline safety exclusion: real Win32 trust-root source operations are forbidden.` | Stage-2 and full, accepted Windows offline guard |
| `tests/test_phase_2n_02_canonical_flask_demo_smoke.py::test_canonical_flask_process_lifecycle_and_get_only_routes` | `Accepted full-suite offline safety exclusion: Flask server/socket lifecycle and native process inspection are forbidden.` | Full only, accepted Windows offline guard |

All three predate C and are classified `ACCEPTED_PRE_EXISTING` only after baseline
and candidate source/environment checks. `skip-classification.json` records each
full node ID, exact observed reason, applicability, baseline evidence reference,
predates-candidate proof and disposition. The three focused suites and complete
Dual-Lab permit no skips. Stage-2 must match exactly its two rows, and full exactly
all three; counts alone do not establish a match. Changed environments do not
silently inherit these exclusions. An unexpected, missing, renamed or unexplained
skip blocks promotion and requires classification/Owner resolution; no additional
skip may be approved during closure execution.

```text
UNEXPECTED_SKIP_COUNT = 0
NEW_OR_UNEXPLAINED_SKIP_RESULT = DL_04_CLOSURE_RESULT: FAIL_OR_BLOCKED
```

The known full-suite denial set is exactly the following three call-phase events,
one occurrence each. The table lists the ordered repository frames from the
denied operation outward; the retained full artifact supplies the guard frames.

| Denial node ID | Exact ordered repository frame signature (`file:function:line`) |
| --- | --- |
| `tests/test_day13_multi_router_wireguard_validation.py::test_multi_device_live_validation_reminds_before_next_router` | `mikrotik_day2_auto_setup.py:connect_ssh_keyboard_interactive:311` → `mikrotik_day2_auto_setup.py:connect_ssh:338` → `mikrotik_day2_auto_setup.py:connect_ssh_with_auth_retry:370` → `mikrotik_day13_multi_router_wireguard_validation.py:run_router_lan_host_ping:911` → `mikrotik_day13_multi_router_wireguard_validation.py:run_day12_for_devices:950` → `mikrotik_day13_multi_router_wireguard_validation.py:main:1323` → `tests/test_day13_multi_router_wireguard_validation.py:test_multi_device_live_validation_reminds_before_next_router:628` |
| `tests/test_day8_iperf3_command_builder.py::test_default_args_use_40_second_duration_and_10_second_omit` | `performance_test.py:infer_wan_client_ip:126` → `performance_test.py:build_config_from_args:259` → `tests/test_day8_iperf3_command_builder.py:test_default_args_use_40_second_duration_and_10_second_omit:114` |
| `tests/workflow_governance/test_validate_scope.py::test_invalid_or_missing_revision_is_structured_error[missing-revision]` | `scripts/validate_scope.py:run_read_only_git:110` → `scripts/validate_scope.py:resolve_commit:193` → `scripts/validate_scope.py:validate_scope:321` → `tests/workflow_governance/test_validate_scope.py:test_invalid_or_missing_revision_is_structured_error:257` |

These are blocked attempts inside historical tests; their names do not grant
live permission. In particular, historical Day1-Day160 retry-oriented function
names do not describe DL-02 retry behavior and must not be rewritten here.
The operation must remain denied before the forbidden side effect. A passing
pytest assertion alone cannot excuse a different denial or an actual side effect.

The corresponding raw source/test fingerprints, verified equal to the retained
review workspace at specification time, are:

| Repository-relative file | SHA256 |
| --- | --- |
| `mikrotik_day2_auto_setup.py` | `707e60fd71e414f063f438d61dba1acff01e26a68c24d600a4d1c8cc7c1e75ee` |
| `mikrotik_day13_multi_router_wireguard_validation.py` | `97944fbebfad7a45ce597decf72a1c15555eed68d1474a0cb0a7e6a622022e74` |
| `tests/test_day13_multi_router_wireguard_validation.py` | `4711b59b14894ecd966ddccfcb3d1e02ef7433b08f4cbbff702fb87301e73ccd` |
| `performance_test.py` | `b0f28cf4555cc0b4519d4d7949bd690cfda8e49c29dce1cf1778b39ee6f88a60` |
| `tests/test_day8_iperf3_command_builder.py` | `e10cc5c3753a2e45bfd6728e7ca3e3d583161b40270419f05ee05badca82871a` |
| `scripts/validate_scope.py` | `e7a90e7e543439dfa2c7da9e51e9438ec23fc29ca064a2116cbfefd2be49f3e2` |
| `tests/workflow_governance/test_validate_scope.py` | `0e4e94c89f44aa45ed0e11f5f70b8b1f196cce5cdd52db375cdf6562184abd11` |

`guard-classification.json` must compare node ID, call phase, occurrence count,
guard fingerprint, ordered source frames and raw source bytes with this baseline.
Normalize only path separators and disposable-root prefixes; do not discard
function names, line numbers, test parameters, or causality. Record sanitized
event identities and process/accounting scope. The historical counter observes
the top-level parent; do not claim it counts every child. Preserve guard
installation in children and the required child-process proof outcomes. Any
observed child denial/error must be classified and cannot be hidden by parent
counts. Fresh focused/Dual-Lab/Stage-2/report modes require zero denials; full
requires exactly these three. Any new/unclassified or DL-04-caused denial blocks
closure, even inside a known test. Guard weakening to obtain zero denials fails.

```text
KNOWN_PRE_EXISTING_GUARD_DENIAL_COUNT = 3
KNOWN_PRE_EXISTING_GUARD_DENIAL_SET_MATCH = YES
NEW_OR_UNCLASSIFIED_GUARD_DENIAL_COUNT = 0
DL04_CAUSED_GUARD_DENIAL_COUNT = 0
```

### Stage-2 preservation and candidate-bound security review

```text
S2_RO_01_THROUGH_S2_RO_11_SEMANTICS_CHANGED = NO
STAGE2_CHANGE_REQUIRED = NO
STAGE2_REOPEN_REQUIRED = NO
DEDICATED_DL04_STAGE2_REGRESSION_FILE_REQUIRED = NO
```

Use the complete existing Stage-2 suite and inspect the accepted boundaries for
Owner authorization, replay consumption, credential binding, pinned-host
verification, exact read-only command policy and one-shot handoff. Relevant
existing suites include `test_owner_verifier.py`,
`test_authorization_envelope_ledger.py`, `test_mikrotik_credential_resolver.py`,
`test_windows_credential_backend.py`, `test_known_host_snapshot.py`,
`test_vrrp_readonly_command_policy.py`, `test_pinned_ssh_transport.py`,
`test_trusted_runtime_composition.py` and `test_vrrp_readonly_live_entrypoint.py`,
all under `tests/stage2`. Combine them with the mapped DL-02 collision,
zero-invocation and evidence-revalidation cases. Mock/synthetic coverage is not
fresh live proof and does not resolve historical Stage-2 closure or replay
provenance limits.

A fresh review of C against B must record reviewer/process provenance, exact
reviewed paths, assertion-to-source/test/result references, limitations, findings
and dispositions in `security-review.json`. A same-conversation review must be
labeled as such; do not invent a separate reviewer identity. Existing static
surface checks support, but do not replace, fresh inspection. Historical security
PASS cannot substitute for this review. The following are mandatory PASS
assertions about the Dual-Lab product boundary and authorized offline run, not
claims that the entire historical repository contains no process facilities:

```text
NO_ARBITRARY_EXECUTOR = YES
NO_RETRY = YES
NO_FALLBACK = YES
NO_PARALLEL_EXECUTION = YES
NO_THREADS = YES
NO_ASYNC = YES
NO_QUEUE = YES
NO_SCHEDULER = YES
NO_WORKER = YES
NO_PROVIDER_MODEL_CALLS = YES
NO_SECRET_LEAKAGE = YES
NO_RAW_STDOUT_LEAKAGE = YES
NO_CONFIG_MUTATION = YES
NO_LIVE_AUTHORITY_EXPANSION = YES
NO_PROHIBITED_INFERENCE = YES
NO_HISTORICAL_EVIDENCE_SUBSTITUTION = YES
PAIR_IDENTITY_COLLISION_PRECEDENCE = PASS
REJECTED_TARGET_ZERO_INVOCATION = PASS
CANONICAL_EVIDENCE_BINDING_REVALIDATION = PASS
IMMUTABLE_CLOSED_SCHEMAS = PASS
SANITIZED_FAILURE_BOUNDARY = PASS
STAGE2_AUTHORITY_BOUNDARIES_UNCHANGED = PASS
```

No arbitrary executor argument, alternate handoff, guessed duplicate pairing,
health/root-cause/remediation verdict, or weakening of fixed errors/schemas may
appear. Rejected targets must have zero handoff where the existing contract
requires it; a valid peer's POLICY_2 handoff remains bounded and mocked. A
material security finding fails the candidate gate; missing proof blocks it.
Neither permits an in-task repair or reopening accepted slices automatically.

### Report-index, external artifacts, and provenance

Fresh `report-index` must exit successfully and return PASS, or WARN only with
zero failures, zero mandatory missing, zero unknown, and every missing artifact
documented as optional under the existing registry. Thirteen optional missing
reports is the historical baseline, not a fixed expected total. Classify any
change and retain item-level evidence; do not relabel a new mandatory missing
artifact as optional to obtain WARN. No registry or report-rendering changes are
authorized.

Use one fresh non-repository evidence root with deterministic logical names
below. Physical locations remain external/private. JSON artifacts contain the
common metadata fields `candidate_sha`, `candidate_parent_sha`, `comparison_base_sha`,
`specification_sha`, `procedure`, `scope`, `result`, and `evidence_kind` (`FRESH`
or `HISTORICAL_BASELINE`). Include run identity and UTC start/end timestamps for
fresh run provenance; time alone is never proof of freshness. Commands use
logical root/tool aliases with fingerprinted resolutions, not personal paths or
environment values. Each result must reference the actual invocation and exact
input/source identities. Log metadata belongs in its companion JSON.

| Required logical artifact | Required contents / generation procedure |
| --- | --- |
| `candidate-manifest.json` | C/P/B/S, branch, accepted predecessor SHAs, platform/tool/guard/launcher fingerprints, frozen command map and baseline references; prepared before execution, finalized with artifact index |
| `focused-dl01.json` | Fresh mapped DL-01 suite invocation, collection/outcomes, exit status, skips and guard results |
| `focused-dl02.json` | Same for DL-02 |
| `focused-dl03.json` | Same for DL-03 |
| `dual-lab.json` | Complete fresh Dual-Lab suite results |
| `stage2.json` | Complete fresh guarded Stage-2 results and exact established skips |
| `full-pytest.json` | Complete fresh guarded full-suite results, node outcomes, exact skips and denial references |
| `workflow-proofs.json` | Extracted six required call-phase outcomes and references into `full-pytest.json` |
| `report-index.log` | Sanitized fresh report-index output |
| `report-index.json` | Common metadata, log hash, exit status, item classifications, failure/mandatory-missing/unknown counts and WARN rationale |
| `skip-classification.json` | Exact observed/expected identity sets, reasons, applicability, predecessor proof and unexpected-count decision |
| `guard-classification.json` | Exact baseline matching, event/source fingerprints, process scope, denied-before-side-effect proof, new/unclassified and candidate-causality decisions |
| `security-review.json` | Fresh candidate/base-bound review of all assertions and six preservation proofs; findings/dispositions and reviewer/process limitations |
| `tracked-integrity.json` | Before/after primary and disposable tracked-file sets/raw hashes, C/P/B identity checks, status results and mutation classification |
| `reviewer-readability.json` | Navigation/coverage mapping, readability assertions, exact reviewed document hash and evidence references |
| `dl04-closure-result.json` | Each completion predicate, findings, state reached, evidence references, `DL_04_ACCEPTED = NO` until a separate acceptance receipt |
| `governed-review.json` | Later fresh governed review of the frozen closure candidate; cannot be generated as completed evidence by the earlier execution gate |
| `owner-acceptance.json` | Later explicit Owner decision tied to C and the reviewed evidence manifest; absent/pending until that separate decision |

The manifest indexes every completed artifact by logical name, byte size,
SHA256, procedure, scope and freshness. It does not hash itself recursively:
freeze and hash the finalized manifest externally, and have later review/Owner
receipts reference that hash. Later receipts are append-only artifacts, each
with its own metadata, not edits that silently change the reviewed manifest.
The pre-run manifest snapshot and all failed attempts remain identifiable.
No artifact may contain credentials, private keys, signatures, raw device output,
raw secret-like environment values, or private live runtime details. Baseline
artifacts with local operational paths remain private comparison inputs; publish
only sanitized identities/fingerprints and logical references in new evidence.

```text
DL_04_EVIDENCE_PROVENANCE_REQUIRED = YES
HISTORICAL_EVIDENCE_MAY_IMPERSONATE_FRESH_EVIDENCE = NO
```

### Candidate integrity and reviewer readability

Before validation, enumerate the candidate's exact tracked-file set and record
raw-byte SHA256 for every file in both primary and disposable copies, together
with commit/tree identities and clean status. After all runs/reviews, compare
the same complete sets and bytes, especially source/tests, and recheck candidate
SHA and clean primary worktree. Git content normalization alone is insufficient
for raw-byte equality. No unexpected additions, deletions, index/ref changes, or
tracked mutation is acceptable. Evidence stays external.

The frozen harness may create only its already permitted disposable temporary
fixtures and untracked generated report outputs in the disposable copy. Classify
them explicitly; they are not permission to alter tracked reports or publish
runtime artifacts. A tracked-content change yields `DL_04_CLOSURE_RESULT = FAIL`.
This contract grants no restoration exception: stop and preserve evidence rather
than cleaning away the discrepancy. A future exception would require an existing
explicit canonical rule and exact authorized restoration proof, not an ad hoc
rule invented after the run. Final candidate/worktree identity must be clean.

The reviewer uses this single navigation layer, its linked contracts/tests,
command map, exact skip/guard tables, and the external manifest. Record C/P/B/S,
artifact provenance, report interpretation, candidate-bound security result,
integrity proof, closure state and incomplete-MVP status together. Do not add
another safety matrix or duplicate historical Stage-2 documentation. Missing
readability evidence blocks completion; readability PASS never overrides a
technical/security failure. Require these assertions in `reviewer-readability.json`:

```text
REVIEWER_NAVIGATION_CLEAR = YES
COMMAND_MAP_COMPLETE = YES
REQUIREMENT_TO_EVIDENCE_MAPPING_CLEAR = YES
SKIP_EXPLANATIONS_CLEAR = YES
GUARD_EXPLANATIONS_CLEAR = YES
SECURITY_BOUNDARIES_CLEAR = YES
NO_LIVE_AUTHORITY_CLAIM_CLEAR = YES
NO_PROVIDER_MODEL_AUTHORITY_CLAIM_CLEAR = YES
COMPLETE_MVP_STATUS_CLEAR = YES
```

### Closure states, checkpoints, and completion gate

States advance only on the named evidence/authorization. A later gate cannot
retroactively satisfy an earlier one. FAIL means a demonstrated failed predicate;
BLOCKED means missing/unverifiable evidence, environment or authorization. Both
stop promotion, leave acceptance NO, and require an exact reason. No automatic
repair, retry, acceptance or documentation reconciliation follows.

| Ordered state | Required transition checkpoint |
| --- | --- |
| `DL_04_SPECIFICATION_ESTABLISHED` | This bounded document is reviewed and committed; no execution or acceptance |
| `DL_04_CLOSURE_EXECUTION_AUTHORIZED` | Separate Owner authorization names C/P/B/S, external evidence boundary and unchanged mutation exclusions; clean status and pre-run integrity verified |
| `DL_04_FRESH_VALIDATION_PASS` | All seven command-map runs pass their policies; six workflow/replay proofs, skip/guard classification and integrity pass |
| `DL_04_REVIEWER_EVIDENCE_COMPLETE` | Validation, classification, integrity, requirement mapping, provenance and readability artifacts complete; security review and closure-result artifacts remain pending at their distinct checkpoints |
| `DL_04_SECURITY_REVIEW_PASS` | Fresh review of the same C/B and frozen validation inputs satisfies all security assertions with zero unresolved material findings |
| `DL_04_CLOSURE_CANDIDATE` | All predicates below pass, C unchanged and worktree clean; record candidate result with acceptance NO, then finalize and freeze the artifact manifest |
| `DL_04_FRESH_GOVERNED_REVIEW` | Separately authorized fresh review verifies C, frozen manifest hash, complete evidence, findings and integrity; record actual process/identity without claiming unperformed independence |
| `DL_04_OWNER_ACCEPTANCE` | Separate Owner ACCEPT/REJECT decision references exact C and governed-review receipt; a review PASS is not that decision |
| `DL_04_ACCEPTED` | Only after Owner ACCEPT with passing review and unchanged evidence identity; repository status reconciliation still requires separate exact documentation authority |

If canonical candidate documentation is requested between candidate creation and
governed review, that is a separate documentation-only authorization and commit
**D**. Record D and its parent alongside the unchanged validated C and frozen
manifest. Verify its exact permitted documentation diff; it must not masquerade
as the validated code commit. Any non-documentation candidate change invalidates
freshness and requires new scope/validation authority. The same distinction
applies to post-acceptance reconciliation: it records a decision, not new tests,
runtime acceptance or integration. No documentation write is implicitly granted
by this state machine.

A closure candidate requires **every** predicate below, supported by fresh
candidate-bound artifacts; the listed values are requirements, not current results:

```text
DL01_FOCUSED = PASS
DL02_FOCUSED = PASS
DL03_FOCUSED = PASS
DUAL_LAB = PASS
STAGE2 = PASS_WITH_ONLY_ESTABLISHED_SKIPS
FULL_PYTEST = PASS_WITH_ONLY_ESTABLISHED_SKIPS
WORKFLOW_GOVERNANCE_PROOFS = PASS
REPORT_INDEX = ACCEPTABLE
UNEXPECTED_SKIP_COUNT = 0
KNOWN_GUARD_SET_MATCH = YES
NEW_GUARD_DENIAL_COUNT = 0
DL04_CAUSED_GUARD_DENIAL_COUNT = 0
SECURITY_REVIEW = PASS
EVIDENCE_PROVENANCE = PASS
TRACKED_INTEGRITY = PASS
REVIEWER_DOCUMENTATION = COMPLETE
READABILITY_REVIEW = PASS
UNRESOLVED_MATERIAL_FINDINGS = 0
DL_04_ACCEPTED = NO
```

Even this candidate does not establish acceptance until separate fresh governed
review and Owner acceptance. DL-04 acceptance is local slice acceptance only.
DL-05 retains independent acceptance plus Safe CI at the integrated implementation
commit. Do not claim `SAFE_CI = COMPLETE`,
`FINAL_INTEGRATED_MVP_ACCEPTANCE = COMPLETE`, or
`LIVE_DUAL_LAB_AUTHORIZED = YES` from any DL-04 state.

```text
DL_04_SAFE_CI_REQUIRED = NO
DL_05_SAFE_CI_BOUNDARY_PRESERVED = YES
```

### Historical specification result and next Owner decision

At specification establishment, before the later execution and review recorded
above, the following status and next decision applied. This historical block is
not the current DL-04 status.

This specification's documentation consistency/readability review checks all 28
coverage references, the command/proof map, exact baseline identities, external
artifact contract, security predicates and distinct state transitions. Its
conclusion, allowed writes, forbidden execution, acceptance limits and next Owner
decision are explicit. Accepted predecessor statuses and historical Stage-2
semantics remain unchanged. No runtime pytest, report-index, closure execution,
new security-validation result, or Safe CI is performed by this task.

```text
DL_02_ACCEPTED = YES
DL_03_ACCEPTED = YES
DL_04_SPECIFICATION_STATUS = ESTABLISHED
DL_04_IMPLEMENTATION_STARTED = NO
DL_04_CLOSURE_EXECUTION_STARTED = NO
DL_04_ACCEPTED = NO
DL_05_STARTED = NO
COMPLETE_DUAL_LAB_MVP = NO
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
NEXT_REQUIRED_OWNER_DECISION = AUTHORIZE_BOUNDED_DL_04_CLOSURE_EXECUTION
```


## DL-05 reviewed exact-SHA candidate

**Accepted: Owner acceptance completed ACCEPT / PASS.** The candidate was
established as REVIEWED_READY_FOR_OWNER_ACCEPTANCE in pre-acceptance documentation
commit `c275b1b58a696b85a9d516ab1b15cceb77432ad2`. Both Safe CI gates and the
separately authorized fresh exact-SHA review had passed. The later, separately
authorized read-only Owner decision passed all seven acceptance predicates.
The heading is retained for stable links; this section now records accepted
status. Earlier specification and predecessor status snapshots remain historical.

### Integrated implementation and evidence identities

Repository: `Robinlee0929/Network_Automation_Lab`.
[PR #93](https://github.com/Robinlee0929/Network_Automation_Lab/pull/93) was
merged by a normal two-parent merge commit under the separate
`DL_05_PR_93_MERGE_TO_MAIN_ONLY` Owner authorization. The explicitly authorized
inherited Day147 change is included. The reviewed implementation identity is
permanent for this candidate:

```text
DL_05_INTEGRATED_IMPLEMENTATION_COMMIT = 0e5dfbc1d143a6de7ba59e4bff9bd1788e809043
DL_05_INTEGRATED_IMPLEMENTATION_TREE = 6252c2c632d217b4f02804626aac797b546f87f8
DL_05_BASE_PARENT = d57b802e5d7a9cbe1d684c3dd058527685c56d62
DL_05_FEATURE_PARENT = 73b60e679000ad719132595e75a098f8c00491d2
DL_05_PR_NUMBER = 93
PR_93_MERGED = YES
DL_05_PREMERGE_SAFE_CI_RESULT = PASS
PREMERGE_SAFE_CI_RUN_ID = 37264911602
PREMERGE_SAFE_CI_RUN_ATTEMPT = 1
PREMERGE_TEST_SHA = 76950ca49101ac2818c63a0e15fc1ce57d5afd35
PREMERGE_RECEIPT_SHA256 = 1ef9b5d389f3fe3d5f49970016e0fd2626e0ae343fce9f252124953878125a9c
DL_05_POSTMERGE_SAFE_CI_RESULT = PASS
DL_05_POSTMERGE_SAFE_CI_RUN_ID = 37281683818
DL_05_POSTMERGE_SAFE_CI_RUN_ATTEMPT = 1
POSTMERGE_SAFE_CI_RUN_ID = 37281683818
POSTMERGE_MAIN_SHA = 0e5dfbc1d143a6de7ba59e4bff9bd1788e809043
POSTMERGE_ACTUAL_CHECKOUT_SHA = 0e5dfbc1d143a6de7ba59e4bff9bd1788e809043
DL_05_POSTMERGE_RECEIPT_SHA256 = 68d5b93163ee70c0c2aeb70aec0814e20864b42e8938d02c356a935e03cbdb1c
DL_05_POSTMERGE_SUPPORTING_INDEX_SHA256 = 91d9a9f1ec7d16fea56ca737e329db0e201f082c2534a2ad2cc87f003648878b
PREMERGE_POSTMERGE_TREE_MATCH = YES
PREMERGE_POSTMERGE_VALIDATION_EQUIVALENT = YES
SAFE_CI_WORKFLOW_ID = 311663833
SAFE_CI_WORKFLOW_BLOB = 717eb0fc4cd54f1c1554137327c26cd2fe82e610
POSTMERGE_JOB_ID = 111670978062
```

The [pre-merge run](https://github.com/Robinlee0929/Network_Automation_Lab/actions/runs/37264911602)
tested PR #93's synthetic `refs/pull/93/merge` result, with the base and feature
parents above. Its tested SHA is distinct from the feature head. The
[post-merge run](https://github.com/Robinlee0929/Network_Automation_Lab/actions/runs/37281683818)
was `push` to `main`, attempt 1, completed/success. Its API head SHA and actual
checkout SHA both equal the integrated implementation SHA. The actual checkout
ref was `refs/remotes/origin/main`; its
[required job](https://github.com/Robinlee0929/Network_Automation_Lab/actions/runs/37281683818/job/111670978062)
passed all twelve mandatory steps. The workflow contract was unchanged.

External evidence retains the logical identities `DL05_PREMERGE_SAFE_CI_RECEIPT`,
`DL05_POSTMERGE_SAFE_CI_RECEIPT`, and `supporting-evidence-index.json`, bound by
the SHA256 values above. The post-merge bundle contains 11 indexed supporting
files and 13 read-only files including receipt and index. All supporting hashes
matched; provenance passed, receipt content matched supporting evidence, and
unsupported receipt claims were zero. Evidence remains external and unchanged;
no private retention paths or raw logs are reproduced here. The receipt records
the capture task's earlier state; the later review result is recorded separately
below. Read-only attributes and hashes are not a cryptographic signer or a
claim of tamper-proof storage.

### Hosted validation and retained findings

Both runs produced equivalent validation results; the post-merge results are:

| Gate | Exact recorded result |
| --- | --- |
| Mandatory steps | 12 success; 0 failed, cancelled, or skipped |
| Typecheck / zero-warning lint | PASS / PASS |
| Node unit tests | 9 files passed; 128 tests passed |
| Telemetry-disabled build | PASS; 7 retained pre-existing dynamic filesystem tracing warnings |
| Full pytest | Linux, Python 3.13.15, pytest 8.4.2; 4672 collected, 4670 passed, 2 skipped, 0 failed, 0 errors |
| Report-index | WARN, exit 0; 14 total, 1 PASS, 13 explicitly optional missing; 0 mandatory missing, failures, or unknowns |
| Tracked diff | `git diff --exit-code` PASS; validation changed no tracked files |

The two expected Linux skips are in
`tests/stage2/test_live_authorization_owner_trust_root.py`:

- `test_disposable_regular_file_is_accepted_by_exact_native_path`:
  `requires the reviewed Win32 APIs`;
- `test_confirmed_trailing_dot_alias_is_rejected_as_noncanonical`:
  `requires ordinary Win32 path aliases`.

Both predicates are `os.name != "nt"`. Exact identities and reasons were
established jointly from retained progress logs and immutable tested source,
not from counts alone; the log has no `-rs` reason records. Native Win32 coverage
is unavailable on Linux as expected; unexplained skips are zero. Retained
Windows guard denials remain historical evidence, not fresh hosted observations.

`DL04_REVIEW_P3_PYTEST_ARGV_RECORDING` remains **OPEN_NON_BLOCKING**. DL-05 does
not reuse the affected external wrapper or its argv attestation. P3 does not
affect Safe CI validity and requires no remediation before DL-05 acceptance.
The seven Next.js warnings remain pre-existing, non-blocking maintenance items;
neither P3 nor those warnings is fixed or closed by this record.

### Fresh review and preserved safety boundaries

The completed `DL_05_FRESH_EXACT_SHA_GOVERNED_REVIEW_ONLY` report in the
preceding separately Owner-authorized task is the review decision record.
It performed fresh read-only technical/governed inspection after post-merge CI
and evidence capture, bound to the exact integrated SHA. It used a separate task
context in the same conversation, with no separate-human or separate-agent
identity attestation and no separate-conversation requirement. It required and
performed no validation rerun. It verified all 754 retained hosted-log lines
against the existing run, eight accepted source/test byte hashes, 28 coverage
areas and 76 test-symbol references, and retained security/integrity evidence.

```text
DL_05_FRESH_EXACT_SHA_GOVERNED_REVIEW = PASS
DL_05_REVIEW_TARGET_SHA = 0e5dfbc1d143a6de7ba59e4bff9bd1788e809043
DL_05_REVIEW_PASS = YES
DL_05_NEW_MATERIAL_FINDINGS = 0
DL_05_UNRESOLVED_MATERIAL_FINDINGS = 0
ACCEPTED_DUAL_LAB_CONTENT_PRESENT = YES
ACCEPTED_IMPLEMENTATION_TEST_HASH_MATCH = PASS
UNEXPECTED_INTEGRATION_DRIFT = NO
CANONICAL_COVERAGE_AREAS_REVIEWED = 28
CANONICAL_COVERAGE_AREAS_PRESERVED = 28
RETAINED_SECURITY_AND_INTEGRITY_REVIEW = PASS
NO_LIVE_NETWORK_AUTHORITY_EXPANSION = YES
NO_CONFIG_MUTATION_AUTHORITY_EXPANSION = YES
NO_PROVIDER_MODEL_AUTHORITY_EXPANSION = YES
NO_ARBITRARY_EXECUTION_EXPANSION = YES
NO_NEW_RETRY_OR_FALLBACK_AUTHORITY = YES
NO_PARALLEL_LIVE_EXECUTION_AUTHORITY = YES
NO_SECRET_DEPENDENCY_FOR_PRODUCT_BEHAVIOR = YES
NO_DL04_ACCEPTANCE_REGRESSION = YES
DL_06_SEPARATE_LIVE_AUTHORIZATION_REQUIRED = YES
```

### Completed Owner acceptance and active status

The completed `DL_05_OWNER_ACCEPTANCE_DECISION_ONLY` report in the preceding
separately Owner-authorized task is the acceptance decision record. It returned
DONE, ACCEPT / PASS, with no blocker and all seven predicates satisfied. That
task verified authoritative main, the clean exact candidate record, and sealed
evidence integrity; it changed no files and reran no validation or review.
This reconciliation records that completed decision and completes canonical
documentation for the bounded offline DL-01 through DL-05 MVP.

| Acceptance predicate | Completed decision result |
| --- | --- |
| Integrated implementation established | PASS; exact main SHA, tree, and merge parents above |
| Post-merge Safe CI | PASS; run 37281683818, attempt 1, twelve mandatory steps successful |
| Exact-SHA correspondence | PASS; main, CI head, actual checkout, and review target match |
| Fresh exact-SHA governed review | PASS; 28 of 28 canonical coverage areas preserved |
| Unresolved material findings | 0 |
| Evidence provenance | PASS; accepted receipt/index hashes above, 13 sealed files unchanged |
| Canonical candidate record | ESTABLISHED at `c275b1b58a696b85a9d516ab1b15cceb77432ad2` |

```text
DL_02_ACCEPTED = YES
DL_03_ACCEPTED = YES
DL_04_ACCEPTED = YES
DL_04_ACCEPTED_CLOSURE_CANDIDATE = 0972910c4d5e2bb7d70acbb50c4721234f20d0dc
DL_04_ACCEPTED_MANIFEST_SHA256 = f7dd14e1ea471032cf68e108d2ea85b144096d28f3aa6c339efd89bf27567449
DL_05_SPECIFICATION_STATUS = ESTABLISHED
DL_05_STARTED = YES
DL_05_CANDIDATE_RECORD = ESTABLISHED
DL_05_STATUS = ACCEPTED
DL_05_OWNER_ACCEPTANCE = ACCEPTED
DL_05_ACCEPTANCE_RESULT = PASS
OWNER_ACCEPTANCE_DECISION = ACCEPT
OWNER_ACCEPTANCE_PREDICATE_COUNT = 7
OWNER_ACCEPTANCE_PREDICATES_PASSED = 7
UNMET_OWNER_ACCEPTANCE_PREDICATES = NONE
DL_05_ACCEPTED = YES
DL_05_ACCEPTED_IMPLEMENTATION_COMMIT = 0e5dfbc1d143a6de7ba59e4bff9bd1788e809043
DL_05_ACCEPTED_IMPLEMENTATION_TREE = 6252c2c632d217b4f02804626aac797b546f87f8
DL_05_ACCEPTED_POSTMERGE_RECEIPT_SHA256 = 68d5b93163ee70c0c2aeb70aec0814e20864b42e8938d02c356a935e03cbdb1c
DL_05_ACCEPTED_REVIEW_RESULT = PASS
DL_05_ACCEPTANCE_BASIS = POSTMERGE_SAFE_CI_PASS_PLUS_FRESH_EXACT_SHA_REVIEW_PASS_PLUS_OWNER_ACCEPTANCE
DL_05_POSTMERGE_SAFE_CI = PASS
DL_05_FRESH_EXACT_SHA_REVIEW = PASS
UNRESOLVED_MATERIAL_FINDINGS = 0
COMPLETE_DUAL_LAB_MVP = YES
OFFLINE_DUAL_LAB_MVP_ACCEPTED = YES
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
PROVIDER_MODEL_INTEGRATION_AUTHORIZED = NO
DL_06_SEPARATE_LIVE_AUTHORIZATION_REQUIRED = YES
DL_06_EXECUTION_CONTRACT_STATUS = NOT_ESTABLISHED
P3_ARGV_RECORDING_FINDING_STATUS = OPEN_NON_BLOCKING
P3_AFFECTS_SAFE_CI_VALIDITY = NO
P3_REMEDIATION_REQUIRED_BEFORE_DL05_ACCEPTANCE = NO
BUILD_WARNING_COUNT = 7
BUILD_WARNING_CLASSIFICATION = PRE_EXISTING_NON_BLOCKING_MAINTENANCE
PRE_ACCEPTANCE_CANDIDATE_RECORD_COMMIT = c275b1b58a696b85a9d516ab1b15cceb77432ad2
```

### Documentation provenance and remaining boundary

The historical pre-acceptance record at
`c275b1b58a696b85a9d516ab1b15cceb77432ad2`, directly above the accepted
implementation, recorded Owner acceptance PENDING, `DL_05_ACCEPTED = NO`,
and `COMPLETE_DUAL_LAB_MVP = NO`. Those values remained in repository text
during the read-only acceptance decision. This separately authorized
post-acceptance reconciliation replaces that temporary active status.

The new documentation commit descends directly from that pre-acceptance record.
Its actual hash and parent are reported externally after commit; neither
documentation commit is the accepted implementation
`0e5dfbc1d143a6de7ba59e4bff9bd1788e809043`. Neither inherits that
implementation's application Safe CI or exact-SHA review. The documentation
branch remains local and unpublished; no push or merge is performed here.

Documentation checks cover exact identities, receipt/index hashes, retained
review and acceptance results, status consistency, readability, links/anchors,
protected-file hashes, and unstaged/staged whitespace. Application tests,
report-index, Safe CI, exact-SHA review, and Owner acceptance are not repeated.
Sealed evidence, P3, and the seven maintenance warnings remain unchanged.

No further Owner decision is required to complete this documentation task.
Future publication needs separate authority. DL-06 remains unestablished and
requires its own readiness/specification and exact Owner authorization; it is
not started. Offline acceptance grants no standing Lab1/Lab2 access, live query,
configuration mutation, provider/model integration, or production readiness.
Historical Stage-2 proof and closure semantics remain unchanged.

## DL-05 canonical integration and Safe CI contract

**Retained canonical specification.** Its requirements remain authoritative;
references below to future integration, CI, or review describe the specification
boundary when established. Those gates have since passed for the exact candidate
in the [active DL-05 record](#dl-05-reviewed-exact-sha-candidate). Separate Owner
acceptance has completed ACCEPT / PASS; the open P3 disposition is unchanged.

### Specification basis and permitted scope

The specification base is
`d3216f774d28e84b828355a727bc9807f1ce3b46` on
`codex/dual-lab-vrrp-ai-query-mvp`. The completed
`DL_05_READINESS_AND_P3_IMPACT_REVIEW_ONLY` response in the same conversation
returned `DL_05_CANONICAL_SPECIFICATION_REQUIRED`. The subsequent Owner
specification authorization resolves its identified gaps through this contract;
it does not convert the prior review into an execution or acceptance result.

At readiness review, the feature branch and PR were absent remotely; the current
canonical HEAD and accepted DL-02/03/04 SHAs were local only. Authoritative remote
`main` was `d57b802e5d7a9cbe1d684c3dd058527685c56d62`. These are retained
readiness observations, not fresh remote-state checks by this specification task.
Future remote work must verify current remote identity and state again.

| Retained accepted identity | Exact value |
| --- | --- |
| DL-02 implementation | `bb39e8295a2fa5d69980396dbaf8c374c79a57b3` |
| DL-03 implementation | `e4c529507c6f5a26a289af4f6d3bfc9e0b170c18` |
| DL-04 closure candidate | `0972910c4d5e2bb7d70acbb50c4721234f20d0dc` |
| DL-04 accepted manifest SHA256 | `f7dd14e1ea471032cf68e108d2ea85b144096d28f3aa6c339efd89bf27567449` |

```text
DL_05_PURPOSE = INTEGRATE_ACCEPTED_DUAL_LAB_MVP_TO_AUTHORITATIVE_MAIN_AND_PROVE_EXACT_MAIN_SHA_WITH_SAFE_CI_AND_FRESH_EXACT_SHA_ACCEPTANCE
DL_05_NEW_PRODUCTION_BEHAVIOR = NO
DL_05_SOURCE_FEATURE_IMPLEMENTATION = NO
DL_05_TEST_FEATURE_IMPLEMENTATION = NO
DL_05_LIVE_AUTHORITY = NO
DL_05_CONFIG_MUTATION_AUTHORITY = NO
DL_05_MODEL_PROVIDER_INTEGRATION = NO
```

The historical specification task could edit only this canonical MVP record and
create its one local specification commit. No README, automation-plan, Stage-2
closure, source, test, workflow, dependency, configuration, wrapper, or
sealed-evidence change was permitted. No application test, report-index, push,
PR, merge, Safe CI, P3 repair, Owner acceptance, or live operation belonged to
that task. It reopened no accepted DL-02, DL-03, or DL-04 decision and introduced
no runtime feature, runner, adapter, queue, scheduler, worker, AI loop, arbitrary
executor, Day1-Day160 rewrite, or second safety matrix.

At specification time, README and the automation plan retained the earlier
readiness summary without implicit edit authority. Their historical DL-05 state
is superseded by the separately authorized candidate reconciliation above.
Historical Stage-2 semantics and its distinct closure gates remain unchanged.

### Integrated commit and candidate identity

Before integration, the exact approved feature/PR HEAD is
`DL_05_PREMERGE_CANDIDATE_SHA`. It contains the complete accepted Dual-Lab branch
content and approved canonical documentation state, including this specification.
It is not the final integrated implementation commit merely because it contains
accepted history. A later Owner authorization must name that exact candidate,
source branch, trusted repository, target `main`, and permitted remote actions.

Pre-merge provenance distinguishes three immutable commit identities:

| Identity | Meaning |
| --- | --- |
| `DL_05_PREMERGE_PR_HEAD_SHA` | Exact head commit of the feature branch submitted by the PR; the approved `DL_05_PREMERGE_CANDIDATE_SHA` must equal this SHA. |
| `DL_05_PREMERGE_BASE_SHA` | Authoritative `main` commit forming the PR integration base at the validated PR state. |
| `DL_05_PREMERGE_TEST_SHA` | Synthetic PR merge commit represented by `refs/pull/<PR_NUMBER>/merge` and actually checked out/tested by the unchanged Safe CI `pull_request` workflow. |

The workflow's pinned `actions/checkout` has no explicit `ref`. Its default
`pull_request` checkout tests the PR merged result. PR head and tested merge SHA
are separate provenance facts; their difference is expected, and equality must
not be required. Do not invent a future synthetic merge SHA before the PR exists.

```text
PREMERGE_CHECKOUT_EXPLICIT_PR_HEAD_REF = NO
PREMERGE_DEFAULT_PULL_REQUEST_MERGE_REF_BEHAVIOR = YES
PREMERGE_PR_HEAD_SHA_IS_SAFE_CI_CHECKOUT_SHA = NO
PREMERGE_SAFE_CI_TESTS_MERGED_RESULT = YES
```

After separately authorized integration, capture the resulting authoritative
`main` SHA as `DL_05_INTEGRATED_IMPLEMENTATION_COMMIT`. This is the final DL-05
acceptance target. Resolve every candidate, parent/base, workflow, and final main
identity to a full immutable SHA; branch names alone are insufficient.

```text
DL_05_INTEGRATED_IMPLEMENTATION_COMMIT_BEFORE_MERGE = NOT_YET_CREATED
INTEGRATED_COMMIT_MUST_BE_ON_AUTHORITATIVE_MAIN = YES
CURRENT_LOCAL_HEAD_IS_FINAL_INTEGRATED_COMMIT = NO
FINAL_DL05_ACCEPTANCE_TARGET = POSTMERGE_AUTHORITATIVE_MAIN_SHA
```

The merge strategy remains governed by repository integration policy and the
separate merge authorization. This specification selects no merge method. Do not
require accepted feature commits to become first-parent main commits. Regardless
of strategy, compare the resulting main tree/content with the approved integration
candidate: the accepted source/tests and approved documentation must be present,
the complete diff must be understood, and no unauthorized material change may
have entered. Record transformed commit relationships, the exact result SHA,
content comparison, and clean repository state. Unexpected behavior changes give
`DL_05_RESULT = FAIL_OR_BLOCKED`; do not repair or rewrite history in that gate.

### Pre-merge and post-merge CI gates

The future pre-merge operation requires separate Owner authorization to push the
exact branch and create its PR targeting authoritative `main`. Record PR number,
URL, head ref/SHA, base ref/SHA, merge ref, and exact tested merge SHA separately.
Let the existing PR-triggered Safe CI run on that PR's merged-result ref, capture
its receipt, and verify all required jobs/steps and head/base/test correspondence
before a separate read-only pre-merge CI/integration review. Only after that
review passes may the Owner separately authorize merge. A branch push alone
does not trigger the required Safe CI.

```text
REMOTE_BRANCH_REQUIRED = YES
PR_TARGET = main
PREMERGE_SAFE_CI_REQUIRED = YES
PREMERGE_SAFE_CI_TRIGGER = pull_request targeting main
MERGE_BEFORE_PREMERGE_SAFE_CI_PASS = NO
```

After authorized integration reaches authoritative main, capture its exact SHA
and the Safe CI run caused by the push to main. Require that post-merge run to
pass and retain its receipt before the final governed review. Pre-merge success
cannot replace this evidence, even if a merge strategy preserves the feature
commit SHA.

```text
POSTMERGE_SAFE_CI_REQUIRED = YES
POSTMERGE_SAFE_CI_TRIGGER = push to main
PREMERGE_CI_MAY_SUBSTITUTE_FOR_POSTMERGE_CI = NO
POSTMERGE_CI_MAY_BE_SKIPPED = NO
```

The existing `workflow_dispatch` trigger remains available in the workflow but
is not a substitute for either required event in this DL-05 sequence. No trigger
is invoked by this specification. Failed, cancelled, skipped, pending, missing,
or unverifiable mandatory results block promotion; they authorize no automatic
repair, retry, workflow change, merge, or acceptance.

### Safe CI workflow and command contract

Use the existing [Safe CI workflow](../../.github/workflows/safe-ci.yml) and its
[governing CI policy](../phase_2m/phase_2m_05_platform_quality_continuation_and_closure_authorization_gate_planning_only.md#workflow-trigger-and-permission-boundary).
The readiness-verified workflow ID is `311663833`; the specification-base Git blob
is `717eb0fc4cd54f1c1554137327c26cd2fe82e610`. These identify the baseline.
Each future receipt must identify the actual workflow source at its target SHA,
including action pins/version comments; a workflow change requires separate
scope resolution and cannot inherit this baseline silently.

```text
SAFE_CI_WORKFLOW = .github/workflows/safe-ci.yml
SAFE_CI_WORKFLOW_NAME = Safe CI
SAFE_CI_REQUIRED_JOB = validate
SAFE_CI_DISPLAYED_JOB = Node and Python quality gates
SAFE_CI_RUNNER = ubuntu-latest
SAFE_CI_TIMEOUT_MINUTES = 30
SAFE_CI_PERMISSIONS = contents: read
CHECKOUT_PERSIST_CREDENTIALS = false
SAFE_CI_SECRET_DEPENDENCY_REQUIRED = NO
SAFE_CI_ARTIFACT_UPLOAD_REQUIRED = NO
```

All twelve steps below are mandatory and ordered. A successful job label alone
is insufficient if a mandatory step did not succeed.

| Order | Exact workflow step | Command or required setup |
| ---: | --- | --- |
| 1 | Check out repository | Pinned `actions/checkout`; `persist-credentials: false` |
| 2 | Set up Node.js 22 | Pinned `actions/setup-node`; Node `22`, package-manager cache disabled |
| 3 | Install committed Node dependencies | `npm ci` |
| 4 | Typecheck | `npm run typecheck` |
| 5 | Lint with zero warnings | `npm run lint`; zero-warning policy retained |
| 6 | Run Node unit tests | `npm run test:unit` |
| 7 | Build Next.js with telemetry disabled | `npm run build`; `NEXT_TELEMETRY_DISABLED=1` |
| 8 | Set up Python 3.13 | Pinned `actions/setup-python`; Python `3.13` |
| 9 | Install committed Python dependencies | `python -m pip install -r requirements.txt` |
| 10 | Run Python tests | `python -m pytest` |
| 11 | Validate report index | `python network_lab.py --task report-index` |
| 12 | Prove validation changed no tracked file | `git diff --exit-code` |

Every mandatory command must exit zero. Report-index must be PASS or WARN only
under the existing optional-report policy: zero failures, zero mandatory missing,
zero unknowns, and evidence that every missing report is optional. The retained
13 optional reports are a comparison baseline, not a forced hosted count.
Validation must not change tracked files.

Existing CI policy permits public dependency-registry access needed to materialize
the committed lockfile and requirements in the ephemeral hosted runner. It grants
no dependency updates, arbitrary packages, device/private-service access, or
repository writes. Offline product validation does not mean the dependency setup
uses no Internet connection.

Safe CI grants no Lab1/Lab2 access, SSH, NETCONF, RESTCONF, device commands,
configuration backup/change, signing, credentials/private runtime configuration,
new live Owner authorization, provider/model API use, production execution,
queue/worker/scheduler, AI loop, or arbitrary execution authority.

```text
SAFE_CI_LIVE_NETWORK_ACCESS = NO
SAFE_CI_CONFIG_MUTATION = NO
SAFE_CI_PROVIDER_MODEL_ACCESS = NO
SAFE_CI_SECRET_DEPENDENCY_REQUIRED = NO
```

### Command attestation and open P3 disposition

`DL04_REVIEW_P3_PYTEST_ARGV_RECORDING` remains `OPEN_NON_BLOCKING`. The existing
hosted workflow does not use the affected external `run_review.py`. DL-05 must
neither reuse/copy that wrapper for its evidence procedure nor rely on its
recorded argv for exact command attestation.

DL-05 command evidence instead binds the committed workflow definition and its
exact source/blob at the target SHA to GitHub run ID, run attempt, run-head
metadata, actual checkout/test SHA, job identity, step identity, step outcome,
and available hosted logs. Preserve literal non-path command arguments in any
captured description; workflow source and hosted execution evidence must be
distinguishable from summaries.

```text
DL_05_REUSES_DL04_WRAPPER = NO
DL_05_DEPENDS_ON_WRAPPER_ARGV_ATTESTATION = NO
P3_AFFECTS_SAFE_CI_VALIDITY = NO
P3_REMEDIATION_REQUIRED_BEFORE_SAFE_CI = NO
P3_REMEDIATION_REQUIRED_BEFORE_DL05_ACCEPTANCE = NO
P3_MUST_BE_CLOSED_FOR_DL05_ACCEPTANCE = NO
P3_ARGV_RECORDING_FINDING_STATUS = OPEN_NON_BLOCKING
```

The finding may remain open beyond DL-05 unless separately prioritized. Do not
repair or close it as part of DL-05. Future work choosing to reuse the affected
argv recording must separately address the finding. The sealed DL-04 bundle and
wrapper remain unchanged; this disposition does not reopen DL-04 acceptance.

### External CI receipts and SHA correspondence

Retain two external read-only evidence receipts with these logical identities:

- `DL05_PREMERGE_SAFE_CI_RECEIPT` for the required PR run.
- `DL05_POSTMERGE_SAFE_CI_RECEIPT` for the required main push run; mandatory final
  acceptance evidence.

Both receipts must include the following fields or explicitly record a missing
field and its effect on the gate. Missing mandatory proof blocks promotion.

| Receipt group | Required evidence |
| --- | --- |
| Repository/workflow | Repository identity; workflow name, ID, path, source at the target SHA and blob identity where available; action pins/version |
| Invocation | Run ID and URL/identity, attempt, event/trigger, branch/ref, separately labeled run-head metadata, actual checkout/test ref and SHA, expected target identity |
| Pre-merge identities | PR number and URL/identity; PR head ref and `DL_05_PREMERGE_PR_HEAD_SHA`; base ref `main` and `DL_05_PREMERGE_BASE_SHA`; merge ref `refs/pull/<PR_NUMBER>/merge` and `DL_05_PREMERGE_TEST_SHA` |
| Timing/result | Start/completion timestamps, completed state, run conclusion |
| Jobs/steps | Required job ID/name/conclusion; every mandatory step identity/name/outcome; command exit status established by hosted results/logs |
| Python | Safely available pytest summary, collected/passed/failed/error/skip outcomes where reported, exact hosted skip identities/reasons and classifications |
| Other validation | Node quality-gate outcomes, report-index result and WARN rationale, tracked-diff exit/result |
| Provenance | GitHub source URLs/identities, available supporting logs, evidence-capture procedure and capture identity/time; limitations |

Do not substitute a historical/local DL-04 result for an unavailable hosted
result. Store no secrets, raw private runtime content, credentials, signatures,
or private live configuration. Receipts stay external; canonical documentation
records stable identities, sanitized findings, and status. No workflow artifact
upload or workflow modification is required or authorized by this contract.

The pre-merge receipt must prove all six conditions below for the captured
run/attempt and validated PR state:

1. `DL_05_PREMERGE_PR_HEAD_SHA` exactly equals the expected pushed Dual-Lab
   branch HEAD and approved pre-merge candidate.
2. The PR base ref is authoritative `main`; record its applicable full base SHA.
3. The Safe CI `pull_request` event belongs to the exact intended PR.
4. The actual checkout/test SHA is `DL_05_PREMERGE_TEST_SHA`, corresponding to
   that PR's `refs/pull/<PR_NUMBER>/merge` at the validated state.
5. The tested synthetic merge integrates both the exact expected PR head and
   the applicable authoritative main base. Retain immutable commit relationship
   evidence for both; a later value of the moving merge ref is insufficient.
6. Every required Safe CI result passes for that tested merged result. This proves
   the candidate integrated with its PR base, not the feature commit in isolation.

These are mandatory predicates for a future pre-merge PASS, not current results:

```text
DL_05_PREMERGE_PR_HEAD_SHA_MATCH = YES
DL_05_PREMERGE_BASE_REF = main
DL_05_PREMERGE_TEST_REF = refs/pull/<PR_NUMBER>/merge
DL_05_PREMERGE_TEST_SHA_MATCH = YES
DL_05_PREMERGE_TEST_SHA_CONTAINS_EXPECTED_PR_HEAD = YES
DL_05_PREMERGE_TEST_SHA_CONTAINS_EXPECTED_BASE = YES
PREMERGE_EVIDENCE_DISTINGUISHES_HEAD_BASE_AND_TEST_SHA = YES
```

Record any run API `head_sha` as `SAFE_CI_PREMERGE_RUN_HEAD_METADATA_SHA`, with
its source and meaning, separately from the PR head and actual checkout/test
SHA. Run metadata alone cannot establish checkout identity. Never label the
synthetic merge SHA as the PR head SHA or require those identities to match.
The workflow ID/source, run ID/attempt/event, and every required job/step outcome
must bind to this same receipt and tested state.

Post-merge correspondence retains literal full-SHA equality. The integrated
implementation commit is the exact authoritative main SHA after merge; the
required Safe CI event remains `push` to `main`:

```text
DL_05_INTEGRATED_IMPLEMENTATION_COMMIT = POSTMERGE_AUTHORITATIVE_MAIN_SHA
AUTHORITATIVE_MAIN_SHA = SAFE_CI_POSTMERGE_RUN_HEAD_SHA
REVIEW_TARGET_SHA = AUTHORITATIVE_MAIN_SHA = SAFE_CI_POSTMERGE_RUN_HEAD_SHA
SAFE_CI_POSTMERGE_CHECKOUT_SHA = DL_05_INTEGRATED_IMPLEMENTATION_COMMIT
FINAL_EXACT_SHA_REVIEW_TARGET = DL_05_INTEGRATED_IMPLEMENTATION_COMMIT
```

The pre-merge synthetic SHA must never become the final accepted DL-05
implementation identity. Mandatory checkout proof is required for both receipts;
post-merge run metadata does not substitute for actual checkout evidence.
Any target mismatch, moved candidate, or unexplained workflow/content difference
blocks acceptance. Never infer correspondence from a branch label or successful
run for another commit.

### Hosted skips and retained DL-04 evidence

Ubuntu hosted results require environment-specific classification. The local
Windows skip set is comparison evidence only. Record each actual hosted skip's
exact node identity, reason, environment applicability, and canonical-policy
basis. Valid documented environment differences may change counts; numeric
equality with DL-04's local totals is not required. Unexplained skips are never
accepted. If available hosted evidence cannot establish exact skip identities,
stop for a separately authorized evidence-resolution decision; do not infer them
from a count or change the workflow/tests inside a review task.

```text
WINDOWS_SKIP_SET_AUTOMATICALLY_ACCEPTED_ON_UBUNTU = NO
SAFE_CI_UNEXPLAINED_SKIP_COUNT = 0
```

| Retained DL-04 evidence | DL-05 classification |
| --- | --- |
| Accepted manifest | `REUSABLE_BASELINE` |
| Closure results | `REUSABLE_BASELINE` |
| Accepted Windows skip set | `BASELINE_ONLY / REQUIRES_FRESH_SAFE_CI_ENVIRONMENT_CONFIRMATION` |
| Guard baseline | `REQUIRES_FRESH_DL05_REVIEW` |
| 28-area mapping | `REQUIRES_FRESH_DL05_EXACT_SHA_REVIEW` |
| Security assertions | `REQUIRES_FRESH_DL05_EXACT_SHA_REVIEW` |
| Tracked-integrity baseline | `REQUIRES_FRESH_DL05_EXACT_SHA_REVIEW` |

The hosted workflow does not install the external DL-04 guard. Its old denial
counts and exclusions cannot be claimed as fresh hosted observations. Fresh
DL-05 review must assess preservation at the exact integrated content without
weakening the accepted safety boundaries or reopening predecessor acceptance.

### Fresh independent acceptance and findings gate

DL-05 independent acceptance means a fresh, read-only, separately authorized
exact-SHA governed review task after integration into authoritative main,
successful post-merge Safe CI, and capture of its exact evidence. Use a separate
task context with a fresh review mandate and fresh inspection. A new conversation,
separate human, or different agent identity is not required. Record the actual
process and its limitations; same-model technical review must not be presented
as an attestation by a different human or agent.

```text
EXACT_SHA_REVIEW_REQUIRED = YES
SAFE_CI_EVIDENCE_REQUIRED_BEFORE_REVIEW = YES
POSTMERGE_REVIEW_REQUIRED = YES
SEPARATE_TASK_CONTEXT_REQUIRED = YES
SEPARATE_CONVERSATION_REQUIRED = NO
SEPARATE_HUMAN_REVIEWER_REQUIRED = NO
SEPARATE_AGENT_IDENTITY_REQUIRED = NO
ZERO_UNRESOLVED_MATERIAL_FINDINGS_REQUIRED = YES
NONBLOCKING_FINDINGS_PERMITTED = YES
```

The fresh review must verify the authoritative main SHA and approved Dual-Lab
source/test/document content; preserved DL-02/03/04 accepted state; actual workflow
identity; post-merge exact-SHA correspondence; every required job/step PASS;
acceptable report-index; valid evidence provenance; and no unexpected content
drift, authority expansion, live access, provider/model integration, or
configuration mutation. Recheck the retained coverage/security/integrity evidence
against that exact target and accurately classify P3. Implementation, merge,
pre-merge-review, or historical review conclusions cannot replace fresh inspection.

The retained predecessor has `DL04_UNRESOLVED_MATERIAL_FINDINGS = 0` and
`DL04_NONBLOCKING_FINDINGS = 1`. These are baseline facts. The final review must
freshly establish `DL05_UNRESOLVED_MATERIAL_FINDINGS = 0` and return PASS.
An open non-blocking finding alone does not fail this gate. A material finding
fails it; missing evidence blocks it. Either outcome stops acceptance and requires
separate resolution authority, not an in-task repair.

### Required evidence package and documentation checkpoints

The canonical package contains all twenty items below. It may remain external
under existing evidence practice, with stable references in the canonical record.
No future receipt is represented as already created by this specification.

| Item | Required content |
| ---: | --- |
| 1 | Exact pre-merge candidate identity and approved scope |
| 2 | PR number and URL/identity |
| 3 | PR head ref/exact SHA; base ref/applicable SHA; PR merge ref/exact tested merge SHA |
| 4 | Pre-merge Safe CI run ID and attempt |
| 5 | `DL05_PREMERGE_SAFE_CI_RECEIPT` |
| 6 | Merge/integration result, authorization reference, method, and content comparison |
| 7 | Exact authoritative post-merge main SHA |
| 8 | Post-merge Safe CI run ID and attempt |
| 9 | `DL05_POSTMERGE_SAFE_CI_RECEIPT` |
| 10 | Actual workflow source/blob/version identity |
| 11 | All mandatory job/step outcomes |
| 12 | Hosted pytest result and exact skip classifications |
| 13 | Hosted report-index result and optional-WARN rationale |
| 14 | Hosted tracked-diff cleanliness result and reviewed repository clean state |
| 15 | Accepted DL-04 candidate/manifest and retained-baseline references |
| 16 | Fresh exact-SHA governed review result and actual reviewer/process provenance |
| 17 | Findings list, severity, material/non-blocking classification, disposition |
| 18 | Fresh zero-unresolved-material-findings determination |
| 19 | Canonical DL-05 candidate status tied to the reviewed main SHA and evidence |
| 20 | Later separate Owner-acceptance decision record tied to that candidate |

Capture receipts and supporting records externally with stable logical identities
and provenance; retain failed attempts separately. Later records reference the
captured run/attempt and exact SHA without overwriting earlier evidence. Repository
candidate/status documentation records sanitized stable identities and requires
separate exact documentation authorization. Owner acceptance cannot precede the
canonical candidate record. Post-acceptance reconciliation records the completed
decision under its own authorization.

Candidate and acceptance documentation commits are distinct from the validated
integrated implementation SHA. Record their actual hashes/parents externally;
never silently relabel a documentation descendant as the reviewed main target.
A proposed new acceptance target requires its own matching post-merge CI and fresh
review evidence. Any intervening change must be identified and classified before
acceptance, with no unsupported claim that the new HEAD was already validated.

### Required state and authorization sequence

The order below is mandatory. Each transition requires its preceding evidence
and the named separate authorization. Remote mutation, merge, fresh review, and
Owner acceptance must not be collapsed into one task. Receipt capture accompanies
each CI gate; canonical documentation writes require separately scoped authority.

```text
DL_05_SPECIFICATION_ESTABLISHED
-> OWNER_AUTHORIZES_REMOTE_BRANCH_PUSH_AND_PR_CREATION
-> REMOTE_BRANCH_PUSHED
-> PR_CREATED_TARGETING_MAIN
-> PREMERGE_SAFE_CI_RUNS_ON_PR_MERGED_RESULT_REF
-> PREMERGE_SAFE_CI_PASS
-> FRESH_PREMERGE_CI_AND_INTEGRATION_REVIEW
-> OWNER_AUTHORIZES_MERGE
-> MERGE_TO_AUTHORITATIVE_MAIN
-> POSTMERGE_MAIN_SHA_CAPTURED
-> POSTMERGE_SAFE_CI_RUNS_ON_EXACT_MAIN_SHA
-> POSTMERGE_SAFE_CI_PASS
-> POSTMERGE_CI_EVIDENCE_CAPTURED
-> FRESH_EXACT_SHA_DL05_GOVERNED_REVIEW
-> DL_05_REVIEW_PASS
-> CANONICAL_DL05_CANDIDATE_STATUS_RECORDED
-> OWNER_ACCEPTANCE
-> POST_ACCEPTANCE_DOCUMENTATION_RECONCILIATION
-> DL_05_ACCEPTED
```

Recheck trusted remote, source/target refs, exact authorized candidate, clean
status, and policy before each future remote mutation. Repository-mandated
post-merge validation remains required under the later task's offline boundary;
local results cannot replace hosted post-merge CI. A failed or missing gate stops
the sequence. This document grants no blanket execution, merge, retry, cleanup,
conflict repair, or future-phase authorization.

### Owner acceptance and offline completion semantics

Owner acceptance is a separate decision after every requirement below is proven.
These are future gate predicates, not results of this specification task:

```text
INTEGRATED_IMPLEMENTATION_COMMIT_ESTABLISHED = YES
POSTMERGE_SAFE_CI_PASS = YES
SAFE_CI_EXACT_SHA_MATCH = YES
FRESH_EXACT_SHA_GOVERNED_REVIEW = PASS
UNRESOLVED_MATERIAL_FINDINGS = 0
EVIDENCE_PROVENANCE = PASS
CANONICAL_CANDIDATE_RECORD = ESTABLISHED
```

Before Owner acceptance, `DL_05_ACCEPTED = NO` and
`COMPLETE_DUAL_LAB_MVP = NO`. A review PASS or green CI alone cannot set either
acceptance status. Successful Owner acceptance completes the bounded offline
Dual-Lab MVP; subsequent documentation reconciliation records the decision and
finishes the canonical `DL_05_ACCEPTED` state. Reconciliation cannot manufacture
acceptance or validate a different implementation SHA.

The following values apply only after successful DL-05 Owner acceptance:

```text
COMPLETE_DUAL_LAB_MVP = YES
OFFLINE_DUAL_LAB_MVP_ACCEPTED = YES
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
PROVIDER_MODEL_INTEGRATION_AUTHORIZED = NO
```

Offline acceptance authorizes no new live query and changes no Stage-2 live-proof
or closure semantics. Any future Dual-Lab live proof remains a separately gated
later capability. No exact DL-06 execution contract is established here; a future
readiness/specification/exact Owner-authorization flow is required before live
work. No DL-06 procedure, command, target credential, or live approval is invented.

```text
DL_06_SEPARATE_LIVE_AUTHORIZATION_REQUIRED = YES
DL_06_EXECUTION_CONTRACT_STATUS = NOT_ESTABLISHED
```

### Historical specification result and next Owner decision

Documentation review checks the conclusion, exact accepted identities, integrated
commit definition, both CI gates, SHA correspondence, P3 disposition, reviewer
meaning, twenty-item evidence package, ordered authorization boundaries, and
conditional offline completion. Local links, whitespace, one-file scope, preserved
predecessor contracts/evidence, and explicit no-live status are checked before
commit. Application validation, Safe CI, integration, and acceptance are not run.

The following is the historical state immediately after specification, retained
for provenance. It is superseded by the active reviewed candidate record above:

```text
DL_02_ACCEPTED = YES
DL_03_ACCEPTED = YES
DL_04_ACCEPTED = YES
DL_05_SPECIFICATION_STATUS = ESTABLISHED
DL_05_STARTED = NO
REMOTE_BRANCH_PUSHED = NO
PR_CREATED = NO
PREMERGE_SAFE_CI_RUN = NO
MERGED_TO_MAIN = NO
POSTMERGE_SAFE_CI_RUN = NO
SAFE_CI_RUN = NO
DL_05_ACCEPTED = NO
COMPLETE_DUAL_LAB_MVP = NO
P3_ARGV_RECORDING_FINDING_STATUS = OPEN_NON_BLOCKING
LIVE_AUTHORITY_GRANTED = NO
LIVE_READINESS_GRANTED = NO
CONFIGURATION_MUTATION_AUTHORIZED = NO
NEXT_REQUIRED_OWNER_DECISION = AUTHORIZE_DL_05_REMOTE_BRANCH_PUSH_AND_PR_CREATION
```
