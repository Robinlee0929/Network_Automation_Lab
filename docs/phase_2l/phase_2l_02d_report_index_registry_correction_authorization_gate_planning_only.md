# Phase 2L-02D — Report-index Registry Correction Authorization Gate / Planning Only

Decision summary: a later, separate registry-only task may correct all four mismatches confirmed by Phase 2L-02C. The exact bounded correction is deterministic: change the two current Day4 report entries from required to optional, and replace each device's generic Day8 entry with two optional entries covering both currently supported direction-qualified writer outputs. This authorization does not modify the registry now and does not authorize Python behavior changes, report generation, fixtures, runtime implementation, or general implementation.

## Status

```text
PHASE: 2L-02D
TASK_NAME: Report-index Registry Correction Authorization Gate / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_AND_REGISTRY_CORRECTION_AUTHORIZATION_GATE_ONLY
STATUS: DONE / READY_FOR_REVIEW
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
REGISTRY_MODIFIED_IN_THIS_TASK: NO
REPORT_INDEX_BEHAVIOR_MODIFIED_IN_THIS_TASK: NO
GENERAL_IMPLEMENTATION_AUTHORIZED: NO
```

## Purpose

The only decision in Phase 2L-02D is whether a later, separate, bounded registry-only correction task may be authorized. Phase 2L-02D records the evidence, exact correction boundary, exclusions, rollback boundary, and deterministic validation requirements. It performs no registry correction and grants no broader implementation authority.

## Evidence Basis

- Phase 2L-02A inventories 11 missing runtime-report rows and records the existing local report-index result as `INCOMPLETE`, with the two required Day4 rows directly contributing to that result.
- Phase 2L-02B determines that seven optional runtime outputs are not backfill candidates and sends the two Day4 requiredness expectations plus the two generic Day8 filename expectations to registry review.
- Phase 2L-02C confirms four registry expectation mismatches, classifies the other seven missing rows as valid optional runtime-output expectations, and finds no separate Day4 baseline fixture gap.
- `topology_profiles/day14_lab_runner_profile.json` currently marks both per-device Day4 entries `required: true` and configures one generic optional Day8 filename for each device.
- `mikrotik_day4_multi_device_baseline.py::write_device_report` writes `reports/<device-name>/day4_baseline_validation.json`; the corresponding test fixes that writer path. The outputs are ignored and untracked, and the tracked `fixtures/` tree contains no Day4 baseline fixture.
- `topology_profiles/day8_iperf3_router_performance.json` defines exactly two supported directions: `WAN_TO_LAN_DNAT` and `LAN_TO_WAN_DNAT_REPLY`.
- `performance_test.py::write_reports` writes `day8_iperf3_<direction>_report.json` and `.html`. `tests/test_day8_interactive_inputs.py` fixes both current direction-qualified filename pairs, and README examples use those same two direction-qualified outputs.
- `network_lab.py::iter_report_items` accepts multiple report definitions per device, `check_report_file` reads each configured JSON/HTML pair and its `required` Boolean, and `compute_overall_result` already distinguishes missing required rows from missing optional rows. No Python report-index behavior change is needed to represent the correction.
- Relevant report-index tests preserve the required-missing `INCOMPLETE` and optional-missing `WARN` contracts.
- Current Git tree evidence at base commit `f175d25d1a17460cb509d92859630522c4f605f1` shows no relevant source, profile, or test change since the Phase 2L-02C evidence commit. The reviewed report paths remain ignored by `.gitignore`, none is tracked, and no Day4 fixture exists.
- Git history shows commit `c12e285` introduced the Day14 profile, commit `a049666` established the two-direction Day8 contract, and commit `92890c3` previously reconciled report-index metadata with canonical writer outputs. History is supporting evidence; the authorization is based on the current tree.

No Day2, Day4, Day8, Day12, Day13, Day35, live, SSH, NETCONF, or RESTCONF workflow was run to reach this decision.

## Authorization Criteria

| Criterion | Result | Basis |
| --- | --- | --- |
| The mismatch is confirmed by current evidence | YES | Current profile definitions conflict with the established Day4 lifecycle and Day8 filename contracts. |
| The exact later change can be described without guessing | YES | Day4 retains its exact paths with only requiredness changed; Day8 uses both and only the two supported directions. |
| The correction can remain limited to registry definitions | YES | The existing profile shape accepts the required entries and metadata. |
| Writer and test contracts are already clear | YES | Current writer functions and tests fix the Day4 path and both Day8 direction-qualified paths. |
| No Python report-index behavior change is needed | YES | Existing iteration, path checking, requiredness, and aggregation behavior already support the bounded representation. |
| No report generation or fixture backfill is needed | YES | All four items are runtime outputs; no tracked Day4 fixture gap exists. |
| Unrelated registry entries can remain untouched | YES | The four corrections are isolated to the two Day4 and two Day8 definitions. |
| The future correction can be validated deterministically | YES | Exact paths, required values, supported directions, scope checks, tests, and report-index behavior are reviewable without live execution. |
| Rollback and review boundaries are clear | YES | A one-file registry-only diff can be reviewed or reverted without source, test, writer, report, or runtime changes. |

## Four-item Authorization Matrix

| Registry item | Confirmed mismatch | Current evidence | Exact future correction definable | Runtime/source change required | Future correction authorized | Reason | Explicitly excluded scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Day4 lab01 requiredness | YES | Exact writer path; ignored untracked runtime output; no tracked fixture; currently `required: true` | YES | NO | YES | Keep both current paths and change only `required` to `false` | Writer, report-index logic, report creation, fixture backfill, live execution |
| Day4 lab02 requiredness | YES | Exact writer-derived device path; ignored untracked runtime output; no tracked fixture; currently `required: true` | YES | NO | YES | Keep both current paths and change only `required` to `false` | Writer, report-index logic, report creation, fixture backfill, live execution |
| Day8 lab01 filename expectation | YES | Generic configured filename is not emitted; current profile, writer, tests, and README establish exactly two supported direction-qualified filenames | YES | NO | YES | Replace the generic entry with two optional entries, one for each supported direction | Choosing one direction, writer changes, report generation, schema redesign, live execution |
| Day8 lab02 filename expectation | YES | Generic configured filename is not emitted; the device-scoped output directory and current two-direction writer contract define both exact filename pairs | YES | NO | YES | Replace the generic entry with two optional entries, one for each supported direction | Choosing one direction, writer changes, report generation, schema redesign, live execution |

## Overall Authorization Decision

```text
FUTURE_BOUNDED_REGISTRY_CORRECTION_AUTHORIZED: YES
PARTIAL_SCOPE_ONLY: NO
AUTHORIZED_ITEMS: Day4 lab01 requiredness; Day4 lab02 requiredness; Day8 lab01 filename expectation; Day8 lab02 filename expectation
NOT_AUTHORIZED_ITEMS: NONE
```

This is authorization for a later separate task only. It is not authorization to modify any registry during Phase 2L-02D and is not general implementation authority.

## Authorized Future Boundary

The later task may modify only `topology_profiles/day14_lab_runner_profile.json`, with exactly these registry corrections:

1. For `Hex-s-2025-lab01 / Day4 Baseline Validation`, retain the current JSON and HTML paths and change only `required` from `true` to `false`.
2. For `Hex-s-2025-lab02 / Day4 Baseline Validation`, retain the current JSON and HTML paths and change only `required` from `true` to `false`.
3. For `Hex-s-2025-lab01`, remove the generic optional Day8 expectation and replace it with these two optional JSON/HTML pairs:
   - `reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.json`
   - `reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.html`
   - `reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.json`
   - `reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.html`
4. For `Hex-s-2025-lab02`, remove the generic optional Day8 expectation and replace it with these two optional JSON/HTML pairs:
   - `reports/Hex-s-2025-lab02/day8_iperf3_WAN_TO_LAN_DNAT_report.json`
   - `reports/Hex-s-2025-lab02/day8_iperf3_WAN_TO_LAN_DNAT_report.html`
   - `reports/Hex-s-2025-lab02/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.json`
   - `reports/Hex-s-2025-lab02/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.html`

Both Day8 direction-specific entries for each device must remain `required: false`. Their names must distinguish the two directions. The two old generic Day8 JSON/HTML expectations must not remain as additional entries. All other device and lab-summary registry entries must remain byte-for-byte unchanged.

The future authorization explicitly excludes:

- Python report-index logic changes
- writer changes
- report creation, regeneration, or backfill
- fixture creation
- runtime implementation
- runner or adapter changes
- live execution
- unrelated registry cleanup
- broad schema redesign
- TypeScript automation work
- Phase 2M work

It also excludes tests, scheduler, queue, broker, worker, agent loop, SSH, NETCONF, RESTCONF, provider/API/model calls, secrets handling, configuration backup/change, production execution paths, GitHub Actions, Day1-Day160 rewrites, and a second safety matrix.

## Deterministic Acceptance and Rollback Boundary

A later correction is acceptable only if review confirms all of the following:

- the profile remains valid JSON;
- only `topology_profiles/day14_lab_runner_profile.json` changes;
- the two Day4 entries retain their exact paths and become optional;
- each generic Day8 entry is replaced by both exact direction-specific optional entries;
- all unrelated registry definitions remain unchanged;
- no source, test, writer, report, fixture, or runtime file changes;
- `git diff --check` passes;
- full pytest passes using the task-specific temporary directory required by that later task; and
- `python network_lab.py --task report-index` no longer reports either absent Day4 runtime output as a required missing row and introduces no unexpected result beyond the documented local artifact baseline.

The rollback boundary is the single registry-only commit from that later task. Rollback restores the two Day4 `required: true` values and the two generic optional Day8 entries exactly as they existed at base commit `f175d25d1a17460cb509d92859630522c4f605f1`, without touching any other file or registry item.

## Smallest Safe Next Step

Exactly one next candidate is selected:

```text
Phase 2L-02E — Bounded Report-index Registry Correction / Registry Only
STATUS: NEW / FUTURE
```

Phase 2L-02E is not started or implemented by this task. Phase 2L-03 remains `NEW / FUTURE` and is not selected. Phase 2M remains not started.

## Documentation Readability Review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_SCOPE_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT_AND_NOT_WEAKENED: PASS
STATUS_LABELS_CONSISTENT_WITH_README: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT_FOR_READABILITY: PASS
TERMINOLOGY_CONSISTENT_WITH_CURRENT_PROJECT_GLOSSARY: PASS
NO_HIDDEN_AUTHORIZATION: PASS
NO_REGISTRY_MODIFICATION: PASS
NO_REPORT_INDEX_BEHAVIOR_MODIFICATION: PASS
NO_GENERAL_IMPLEMENTATION_AUTHORIZATION: PASS
NO_DAY1_DAY160_REWRITE: PASS
NO_SECOND_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

The required authorization matrix evaluates only the four confirmed registry mismatches. It does not create or duplicate a repository safety matrix.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS
PHASE: 2L-02D
STATUS: DONE / READY_FOR_REVIEW
AUTHORIZED_ITEM_COUNT: 4
PARTIAL_SCOPE_ONLY: NO
CURRENT_TASK_REGISTRY_MODIFIED: NO
CURRENT_TASK_REPORT_INDEX_BEHAVIOR_MODIFIED: NO
GENERAL_IMPLEMENTATION_AUTHORIZED: NO
NEXT_FUTURE_CANDIDATE: Phase 2L-02E — Bounded Report-index Registry Correction / Registry Only
NEXT_CANDIDATE_STARTED: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```
