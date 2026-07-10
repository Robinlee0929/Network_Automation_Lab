# Phase 2L-02B — Report-index Missing Runtime Report Decision Gate / Planning Only

Status: DONE / MERGED_TO_MAIN

Decision summary: the current `INCOMPLETE` result cannot be accepted as a set of documented optional gaps because two missing Day4 runtime outputs are marked required by the current report-index profile. Repository evidence also shows that the configured Day8 paths do not match the filenames written by the current Day8 implementation. The gate outcome is `REGISTRY_EXPECTATION_REVIEW_REQUIRED`. This task authorizes no report creation, regeneration, backfill, registry change, report-index change, or runtime implementation.

## Status

```text
PHASE: 2L-02B
TASK_NAME: Report-index Missing Runtime Report Decision Gate / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_AND_DECISION_GATE_ONLY
STATUS: DONE / MERGED_TO_MAIN
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
DECISION_GATE_ONLY: YES
IMPLEMENTATION_AUTHORIZED: NO
```

## Purpose

Decide the future planning treatment of every missing report item inventoried by Phase 2L-02A. The decision gate distinguishes optional runtime outputs that must not be backfilled from paths whose current registry expectations require a later read-only planning review.

## Evidence Basis

- Phase 2L-02A inventory: `docs/phase_2l/phase_2l_02a_report_index_missing_runtime_report_inventory_planning_only.md`
- Recorded report-index result: `INCOMPLETE`, exit code `1`
- Recorded counts: `total=12 pass=1 fail=0 warn=0 missing=11 unknown=0`
- Registry/profile evidence: `topology_profiles/day14_lab_runner_profile.json`
- Report-index code evidence: `network_lab.py` checks the configured JSON path first; a missing required JSON produces `INCOMPLETE`, while missing optional rows produce `WARN`
- Runtime writer evidence: `mikrotik_day2_auto_setup.py`, `mikrotik_day4_multi_device_baseline.py`, `performance_test.py`, `mikrotik_day12_wireguard_vpn_automation.py`, `cisco_topology_validation.py`, `mikrotik_day13_multi_router_wireguard_validation.py`, and `mikrotik_day35_vrrp_failover_validation.py`
- Tracked-file evidence: none of the 11 configured missing paths is tracked; `.gitignore` ignores `reports/`
- Existing tracked report evidence: timestamped Day13 JSON and HTML evidence exists under `summary/`, but it does not satisfy the configured canonical `reports/lab-summary/` path
- Fixture evidence: tracked files under `fixtures/` contain no Day4 baseline fixture

The report-index command was not rerun. This decision uses the recorded Phase 2L-02A result and read-only repository inspection.

## Decision Table

| Missing item or path | Phase 2L-02A classification | Current repository evidence | Required by current report-index logic | Expected artifact type | Decision | Implementation authorized | Follow-up required | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `reports/Hex-s-2025-lab01/day2_auto_setup_report.json` | Runtime-generated artifact missing | Profile marks optional; Day2 writer creates this exact per-device JSON path; path is untracked and absent | NO | Per-device runtime JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Absence remains an optional runtime gap; do not fabricate historical output. |
| `reports/Hex-s-2025-lab01/day4_baseline_validation.json` | Required artifact missing | Profile marks required; Day4 live validation writer creates this exact path; no tracked Day4 fixture exists | YES | Per-device live-validation runtime JSON output | `REGISTRY_EXPECTATION_REVIEW_NEEDED` | NO | YES | A clean checkout lacks the ignored runtime output, but the required flag makes report-index `INCOMPLETE`. |
| `reports/Hex-s-2025-lab01/day8_iperf3_performance_report.json` | Runtime-generated artifact missing | Profile marks optional; current Day8 writer emits `day8_iperf3_{direction}_report.json`, not this configured filename | NO | Per-device guarded-live performance JSON output | `REGISTRY_EXPECTATION_REVIEW_NEEDED` | NO | YES | Later planning must reconcile the configured path with the actual writer naming; no change is authorized here. |
| `reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.json` | Runtime-generated artifact missing | Profile marks optional; Day12 writer creates this exact per-device JSON path; path is untracked and absent | NO | Per-device guarded-live validation JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Optional runtime evidence must not be backfilled. |
| `reports/Hex-s-2025-lab02/day2_auto_setup_report.json` | Runtime-generated artifact missing | Profile marks optional; Day2 writer creates this exact per-device JSON path; path is untracked and absent | NO | Per-device runtime JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Absence remains an optional runtime gap; do not fabricate historical output. |
| `reports/Hex-s-2025-lab02/day4_baseline_validation.json` | Required artifact missing | Profile marks required; Day4 live validation writer creates this exact path; no tracked Day4 fixture exists | YES | Per-device live-validation runtime JSON output | `REGISTRY_EXPECTATION_REVIEW_NEEDED` | NO | YES | A clean checkout lacks the ignored runtime output, but the required flag makes report-index `INCOMPLETE`. |
| `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json` | Runtime-generated artifact missing | Profile marks optional; current Day8 writer emits `day8_iperf3_{direction}_report.json`, not this configured filename | NO | Per-device guarded-live performance JSON output | `REGISTRY_EXPECTATION_REVIEW_NEEDED` | NO | YES | Later planning must reconcile the configured path with the actual writer naming; no change is authorized here. |
| `reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json` | Runtime-generated artifact missing | Profile marks optional; Day12 writer creates this exact per-device JSON path; path is untracked and absent | NO | Per-device guarded-live validation JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Optional runtime evidence must not be backfilled. |
| `reports/cisco-switch/switch_topology_report.json` | Runtime-generated artifact missing | Profile marks optional; Cisco topology validation defines this exact JSON output; path is untracked and absent | NO | Device-validation runtime JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Optional runtime evidence must not be generated for historical completeness. |
| `reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary.json` | Runtime-generated artifact missing | Profile marks optional; Day13 writer creates this canonical path; tracked timestamped evidence exists under `summary/`, not at the configured path | NO | Aggregate runtime JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Historical tracked evidence does not justify copying or fabricating the missing canonical runtime output. |
| `reports/lab-summary/day35_vrrp_failover_validation.json` | Runtime-generated artifact missing | Profile marks optional; Day35 controlled failover workflow defines this exact JSON output; path is untracked and absent | NO | Controlled live-observation runtime JSON output | `RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL` | NO | NO | Optional runtime evidence must not be generated or copied for backfill. |

Decision count:

```text
INVENTORY_ITEMS_REVIEWED: 11
RUNTIME_GENERATED_ARTIFACT_NOT_FOR_BACKFILL: 7
REGISTRY_EXPECTATION_REVIEW_NEEDED: 4
OTHER_ALLOWED_DECISION_VALUES_USED: 0
```

## Day4 Baseline JSON Decision

The two Day4 JSON paths are expected by current report-index logic. `topology_profiles/day14_lab_runner_profile.json` marks both as required, and `network_lab.py` returns `INCOMPLETE` when any required configured JSON path is missing.

Repository evidence classifies both files as runtime outputs from `mikrotik_day4_multi_device_baseline.py`, which is a live SSH validation workflow. They are not tracked baseline fixtures: the paths are untracked, `reports/` is ignored, and the tracked `fixtures/` inventory contains no Day4 baseline replacement.

Their absence is an expected runtime condition in a checkout where the live Day4 workflow has not produced local reports. It is not evidence of a missing tracked fixture. However, marking those ignored runtime outputs as required makes that expected condition a persistent report-index `INCOMPLETE`, so the suitability of the current registry expectation requires a later planning-only review.

```text
DAY4_EXPECTED_BY_CURRENT_REPORT_INDEX_LOGIC: YES
DAY4_ARTIFACT_CLASS: RUNTIME_OUTPUT
DAY4_TRACKED_BASELINE_FIXTURE: NO
DAY4_ABSENCE_CLASS: EXPECTED_RUNTIME_CONDITION_WITH_REGISTRY_EXPECTATION_REVIEW_NEEDED
DAY4_REGENERATION_AUTHORIZED: NO
```

## Overall Gate Outcome

```text
OVERALL_GATE_OUTCOME: REGISTRY_EXPECTATION_REVIEW_REQUIRED
```

The gate does not accept the current `INCOMPLETE` as optional-only because the Day4 rows are required. It also does not authorize artifact remediation because the required items are live-workflow runtime outputs, not missing tracked fixtures. The evidence supports reviewing the registry expectations before any later decision about behavior or artifacts.

## Authorization Boundary

- No report creation authorized.
- No report regeneration authorized.
- No report backfill authorized.
- No report-index code change authorized.
- No registry change authorized.
- No runtime implementation authorized.
- No execution component authorized.
- No live-device work authorized.

This task also authorizes no runner, adapter, scheduler, queue, broker, worker, agent loop, AI loop, provider/API/model call, secrets handling, configuration backup/change, SSH, NETCONF, RESTCONF, production execution path, Day1-Day160 rewrite, second safety matrix, or Phase 2M implementation.

## Smallest Safe Next Step

Create a later planning-only registry expectation review. That review should compare the required Day4 runtime-output lifecycle and the configured Day8 filenames with current writer behavior, then produce a planning decision only. It must not change the profile, report-index code, runtime code, reports, or fixtures unless a separate future task explicitly authorizes a bounded implementation.

Phase 2L-03 remains `NEW / FUTURE` and is not started by this recommendation.

## Documentation Readability Review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_SCOPE_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT: PASS
STATUS_LABELS_CONSISTENT_WITH_README: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT_FOR_READABILITY: PASS
TERMINOLOGY_CONSISTENT_WITH_CURRENT_PROJECT_GLOSSARY: PASS
NO_IMPLEMENTATION_BEHAVIOR_INTRODUCED: PASS
NO_REPORT_CREATION_OR_REGENERATION_AUTHORIZED: PASS
NO_REPORT_INDEX_OR_REGISTRY_CHANGE_AUTHORIZED: PASS
NO_DAY1_DAY160_REWRITE: PASS
NO_SECOND_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

## Final Decision

```text
FINAL_PHASE_DECISION: PASS
PHASE: 2L-02B
STATUS: DONE / MERGED_TO_MAIN
INVENTORY_ITEMS_REVIEWED: 11
DAY4_BASELINE_JSON_DECISION_INCLUDED: YES
OVERALL_GATE_OUTCOME: REGISTRY_EXPECTATION_REVIEW_REQUIRED
SMALLEST_SAFE_NEXT_STEP: LATER_PLANNING_ONLY_REGISTRY_EXPECTATION_REVIEW
IMPLEMENTATION_AUTHORIZED: NO
REPORT_CREATION_AUTHORIZED: NO
REPORT_REGENERATION_AUTHORIZED: NO
REPORT_BACKFILL_AUTHORIZED: NO
REPORT_INDEX_CHANGE_AUTHORIZED: NO
REGISTRY_CHANGE_AUTHORIZED: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```
