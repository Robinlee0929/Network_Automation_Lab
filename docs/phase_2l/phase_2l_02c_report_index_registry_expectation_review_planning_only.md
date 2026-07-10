# Phase 2L-02C — Report-index Registry Expectation Review / Planning Only

Status: DONE / MERGED_TO_MAIN

Decision summary: the current registry does not fully match the repository's report lifecycle. Seven missing paths are valid optional runtime-output expectations. The two Day8 paths do not match the filenames written and tested by the current Day8 implementation. The two Day4 paths match the writer, but they are ignored, untracked outputs of a live-validation workflow while the registry marks them required, making a clean pre-execution checkout `INCOMPLETE`. No separate baseline fixture gap is supported by repository evidence. The overall outcome is `REGISTRY_EXPECTATION_MISMATCH_CONFIRMED`; no registry correction, report creation, fixture creation, or implementation is authorized.

## Status

```text
PHASE: 2L-02C
TASK_NAME: Report-index Registry Expectation Review / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_AND_REGISTRY_EXPECTATION_REVIEW_ONLY
STATUS: DONE / MERGED_TO_MAIN
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
REGISTRY_EXPECTATION_REVIEW_ONLY: YES
IMPLEMENTATION_AUTHORIZED: NO
```

## Purpose

Determine whether the current report-index registry expectations match the repository's actual artifact and runtime-output model, including tracked artifacts, runtime-generated outputs, optional historical evidence, baseline fixtures, and outputs expected only after a specific task is run.

## Evidence Basis

- Phase 2L-02A inventory: `docs/phase_2l/phase_2l_02a_report_index_missing_runtime_report_inventory_planning_only.md` records the 11 missing JSON paths and the saved `INCOMPLETE` result.
- Phase 2L-02B decision gate: `docs/phase_2l/phase_2l_02b_report_index_missing_runtime_report_decision_gate_planning_only.md` identifies the Day4 requiredness and Day8 naming concerns and requires this registry review.
- Current Day14 registry source: `topology_profiles/day14_lab_runner_profile.json` defines each expected JSON/HTML path and its `required` boolean.
- Report-index parsing and validation source: `network_lab.py` symbols `load_lab_runner_profile`, `iter_report_items`, `check_report_file`, `compute_overall_result`, `build_latest_lab_overview`, and `_run_report_index` define how profile entries are loaded, checked, classified, summarized, and returned.
- Runtime writer sources: `mikrotik_day2_auto_setup.py::write_reports`, `mikrotik_day4_multi_device_baseline.py::write_device_report`, `performance_test.py::write_reports`, `mikrotik_day12_wireguard_vpn_automation.py::write_reports`, `cisco_topology_validation.py` constants `REPORT_JSON` and `REPORT_HTML`, `mikrotik_day13_multi_router_wireguard_validation.py::write_reports`, and `mikrotik_day35_vrrp_failover_validation.py` constants `REPORT_JSON` and `REPORT_HTML`.
- Tracked artifact evidence at commit `95a1008d9fa487bd785ea797fed3ab186410b2d0`: `git ls-tree` shows none of the 11 paths; `.gitignore` ignores `reports/`; tracked `fixtures/` contains no Day4 baseline fixture; tracked `summary/` contains timestamped Day13 JSON/HTML evidence at a different path.
- Relevant tests: `tests/test_network_lab_runner.py::test_missing_required_report_makes_overall_incomplete`, `test_missing_optional_report_makes_overall_warn`, and `test_report_index_uses_lab_summary_latest_overview_output_paths`; `tests/test_mikrotik_day2_auto_setup.py` lab01/lab02 writer-path tests; `tests/test_mikrotik_day4_multi_device_baseline.py::test_write_device_and_summary_reports`; `tests/test_day8_interactive_inputs.py` directional filename assertions; `tests/test_cisco_topology_validation.py::test_write_json_and_html_reports`; `tests/test_day13_multi_router_wireguard_validation.py` canonical summary-path assertions; and the Day35 report-index/catalog tests in `tests/test_network_lab_runner.py`.
- README evidence: the report-index section says it reads local reports rather than running Day2-Day13 workflows, and the sample report paths show directional Day8 filenames and per-device Day4 outputs.
- Relevant Git history: commit `c12e285` introduced the reviewed profile entries; commit `a049666` established the current directional Day8 writer naming; commit `92890c3` demonstrates that profile paths are expected to be reconciled with canonical writer outputs when repository evidence supports a correction. History is supporting context only; current tracking status is based exclusively on the Git tree at `95a1008d9fa487bd785ea797fed3ab186410b2d0`.

The report-index command was not run. No report-producing task was run.

## Registry Definition Inventory

The primary registry for the 11-item Phase 2L review is `topology_profiles/day14_lab_runner_profile.json`. A report entry contains a display `name`, a `json` path, an `html` companion path, and a Boolean `required` flag. Device-level `required` metadata also exists, but `check_report_file` copies the report entry's `required` value into each report record.

`network_lab.py::check_report_file` checks the configured JSON path first. When that JSON does not exist, the record is immediately returned with `status: MISSING`; the HTML companion does not replace it. `network_lab.py::compute_overall_result` returns `INCOMPLETE` when a required record is `MISSING`, and returns `WARN` when missing records are optional and no higher-priority failure exists. The tests `test_missing_required_report_makes_overall_incomplete` and `test_missing_optional_report_makes_overall_warn` preserve this distinction.

The profile distinguishes required from optional entries only through `required`. It does not identify an artifact as tracked baseline, runtime-generated, historical, or task-dependent; it has no producer-task, lifecycle, pre-execution, fixture, or historical-evidence field. Those roles can be established only by comparing writer source, tests, tracked files, documentation, and history.

`network_lab.py` also contains `REPORT_CATALOG` and a separate report-visibility path used by the legacy `--report-index` surface. That catalog is relevant corroborating evidence for some canonical paths, but it is not the source of the 11 missing rows recorded by Phase 2L-02A; those rows come from the Day14 profile used by `--task report-index`.

Historical expectations that no longer match current behavior are present. The two generic Day8 filenames remain in the profile even though the writer and tests use direction-qualified filenames. The two Day4 paths are current writer paths, but their `required: true` lifecycle expectation conflicts with their status as ignored, untracked outputs that exist only after the live Day4 workflow runs.

## Classification Meanings Applied

- `VALID_RUNTIME_OUTPUT_EXPECTATION`: repository evidence shows that a specific task or runtime action is designed to produce the item, and absence before that action runs is consistent with the current model.
- `VALID_BASELINE_FIXTURE_EXPECTATION`: repository evidence shows that the item is intended to be a tracked or otherwise persistent baseline fixture rather than an ordinary runtime output.
- `OPTIONAL_HISTORICAL_EXPECTATION`: repository evidence shows that the item is historical or optional and that its absence is accepted.
- `OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION`: repository evidence shows that the current path, naming, requiredness, lifecycle, or supported behavior no longer matches the repository's current report model.
- `MIXED_OR_AMBIGUOUS_EXPECTATION`: repository evidence supports conflicting roles or does not distinguish clearly between runtime output, baseline fixture, and historical evidence.
- `INSUFFICIENT_EVIDENCE`: repository evidence is insufficient to support any other classification.

## Eleven-item Expectation Review

| Missing item or path | Registry source or definition | Current registry expectation | Repository evidence | Tracked in Git: YES / NO | Runtime-generated by design: YES / NO / UNKNOWN | Baseline fixture by design: YES / NO / UNKNOWN | Optional historical item: YES / NO / UNKNOWN | Expectation classification | Registry mismatch suspected: YES / NO / UNKNOWN | Implementation authorized: NO | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `reports/Hex-s-2025-lab01/day2_auto_setup_report.json` | Day14 profile, lab01 Day2 entry | Optional JSON; missing contributes `WARN` | `mikrotik_day2_auto_setup.py::write_reports` and lab01 path tests write this exact per-device path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Day2 workflow writes lab01 evidence; this task does not authorize that workflow. |
| `reports/Hex-s-2025-lab01/day4_baseline_validation.json` | Day14 profile, lab01 Day4 entry | Required JSON; missing forces `INCOMPLETE` | `write_device_report` and its test use this exact path; `reports/` is ignored; no tracked Day4 fixture exists | NO | YES | NO | NO | `OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION` | YES | NO | Path is current, but requiredness conflicts with an untracked live-workflow output's pre-execution lifecycle. |
| `reports/Hex-s-2025-lab01/day8_iperf3_performance_report.json` | Day14 profile, lab01 Day8 entry | Optional generic JSON; missing contributes `WARN` | `performance_test.py::write_reports` writes `day8_iperf3_{direction_name}_report.json`; tests require directional names | NO | YES | NO | NO | `OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION` | YES | NO | Configured filename is not produced by the current writer. |
| `reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.json` | Day14 profile, lab01 Day12 entry | Optional JSON; missing contributes `WARN` | `mikrotik_day12_wireguard_vpn_automation.py::write_reports` writes this exact per-device path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Day12 workflow writes lab01 evidence; no backfill is authorized. |
| `reports/Hex-s-2025-lab02/day2_auto_setup_report.json` | Day14 profile, lab02 Day2 entry | Optional JSON; missing contributes `WARN` | `mikrotik_day2_auto_setup.py::write_reports` and lab02 path tests write this exact per-device path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Day2 workflow writes lab02 evidence; this task does not authorize that workflow. |
| `reports/Hex-s-2025-lab02/day4_baseline_validation.json` | Day14 profile, lab02 Day4 entry | Required JSON; missing forces `INCOMPLETE` | `write_device_report` constructs the same path from device name; test covers the filename; no tracked Day4 fixture exists | NO | YES | NO | NO | `OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION` | YES | NO | Path is current, but requiredness conflicts with an untracked live-workflow output's pre-execution lifecycle. |
| `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json` | Day14 profile, lab02 Day8 entry | Optional generic JSON; missing contributes `WARN` | `performance_test.py::write_reports` writes direction-qualified names; no current writer emits the configured generic name | NO | YES | NO | NO | `OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION` | YES | NO | Configured filename is not produced by the current writer. |
| `reports/Hex-s-2025-lab02/day12_wireguard_vpn_automation_report.json` | Day14 profile, lab02 Day12 entry | Optional JSON; missing contributes `WARN` | Day12 `write_reports` uses the report device name; runner tests use this exact lab02 delegated-report path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Day12 workflow writes lab02 evidence; no backfill is authorized. |
| `reports/cisco-switch/switch_topology_report.json` | Day14 profile, Cisco Day5 entry | Optional JSON; missing contributes `WARN` | `cisco_topology_validation.py::REPORT_JSON` and writer/report-visibility tests use this exact path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Cisco topology validation workflow produces local evidence. |
| `reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary.json` | Day14 profile, Day13 summary entry | Optional JSON; missing contributes `WARN` | Day13 `REPORT_JSON_PATH` and `write_reports` use this exact canonical path; only a timestamped historical copy under `summary/` is tracked | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | The tracked timestamped file is separate historical evidence and does not satisfy or redefine the canonical runtime path. |
| `reports/lab-summary/day35_vrrp_failover_validation.json` | Day14 profile, Day35 summary entry | Optional JSON; missing contributes `WARN` | Day35 `REPORT_JSON` and report catalog tests use this exact controlled-observation output path | NO | YES | NO | NO | `VALID_RUNTIME_OUTPUT_EXPECTATION` | NO | NO | Expected only after the Day35 controlled workflow produces local evidence; execution is not authorized here. |

Classification count:

```text
INVENTORY_ITEMS_REVIEWED: 11
INVENTORY_ITEMS_CLASSIFIED: 11
VALID_RUNTIME_OUTPUT_EXPECTATION: 7
VALID_BASELINE_FIXTURE_EXPECTATION: 0
OPTIONAL_HISTORICAL_EXPECTATION: 0
OBSOLETE_OR_MISMATCHED_REGISTRY_EXPECTATION: 4
MIXED_OR_AMBIGUOUS_EXPECTATION: 0
INSUFFICIENT_EVIDENCE: 0
```

## Day4 Baseline JSON Report Review

The Day4 expectations are defined by the two `Day4 Baseline Validation` entries in `topology_profiles/day14_lab_runner_profile.json`. Both JSON paths are marked `required: true`. `mikrotik_day4_multi_device_baseline.py::write_device_report` produces `reports/<device-name>/day4_baseline_validation.json`, and `tests/test_mikrotik_day4_multi_device_baseline.py::test_write_device_and_summary_reports` requires that filename for lab01. The same function constructs the lab02 path from the report's device name.

Repository evidence does not support treating these files as tracked fixtures. Neither path exists in the Git tree at `95a1008d9fa487bd785ea797fed3ab186410b2d0`; `.gitignore` ignores `reports/`; and the tracked `fixtures/` tree has no Day4 baseline file. Tests require the writer contract and status semantics, but they do not require either runtime report to exist in a clean checkout.

Their absence before the Day4 live-validation workflow runs is therefore an accepted runtime condition, not a missing fixture. It is not accepted as a complete report-index state because `check_report_file` returns `MISSING` and `compute_overall_result` converts either required miss into `INCOMPLETE`. The mismatch is the registry's required lifecycle expectation, not the writer path and not a missing baseline fixture.

```text
DAY4_EXPECTATIONS_DEFINED_IN_PROFILE: YES
DAY4_EXPECTED_TRACKED_IN_GIT: NO
DAY4_RUNTIME_GENERATED_BY_DESIGN: YES
DAY4_EXISTENCE_REQUIRED_BY_TESTS: NO
DAY4_WRITER_PATH_REQUIRED_BY_TESTS: YES
DAY4_ABSENCE_IS_MISSING_FIXTURE: NO
DAY4_ABSENCE_INDICATES_REGISTRY_MISMATCH: YES
DAY4_ABSENCE_IS_ACCEPTED_PRE_EXECUTION_RUNTIME_CONDITION: YES
DAY4_REPORT_CREATION_AUTHORIZED: NO
DAY4_REPORT_REGENERATION_AUTHORIZED: NO
DAY4_REGISTRY_MODIFICATION_AUTHORIZED: NO
```

## Required-versus-optional Model Review

The current registry clearly distinguishes only the status consequence of `required: true` and `required: false`. It does not clearly distinguish the artifact roles requested by this review:

- Required baseline artifacts: no artifact-role field exists, and repository evidence identifies no one of the 11 items as a baseline fixture. The two required Day4 entries are runtime outputs rather than fixtures.
- Runtime-generated artifacts: all 11 roles are discoverable from writer source and tests, but the registry does not record that role.
- Optional historical artifacts: the registry has no historical or retention marker. The tracked timestamped Day13 evidence is outside the configured canonical path and must be interpreted separately.
- Evidence expected only after a specific task is run: the registry has no producer-task or pre-execution-state field. This dependency is visible only in writer code, tests, task documentation, and README statements.

The Boolean required/optional model is therefore insufficient to represent the repository's actual artifact lifecycle. This review does not propose implementation code or detailed correction steps.

## Overall Review Outcome

```text
OVERALL_REVIEW_OUTCOME: REGISTRY_EXPECTATION_MISMATCH_CONFIRMED
```

This outcome is selected because four registry expectations are confirmed mismatches: two Day8 filenames do not match current writer output, and two required Day4 runtime outputs are absent by design before their live workflow runs but make a clean checkout `INCOMPLETE`. No separate baseline fixture gap is confirmed, so `MIXED_REGISTRY_AND_FIXTURE_GAPS_CONFIRMED` does not apply. All 11 items have sufficient evidence, so `INSUFFICIENT_EVIDENCE` does not apply.

## Authorization Boundary

```text
REGISTRY_CHANGES_AUTHORIZED: NO
REPORT_INDEX_BEHAVIOR_CHANGES_AUTHORIZED: NO
REPORT_CREATION_AUTHORIZED: NO
REPORT_REGENERATION_AUTHORIZED: NO
REPORT_BACKFILL_AUTHORIZED: NO
BASELINE_FIXTURE_CREATION_AUTHORIZED: NO
RUNTIME_IMPLEMENTATION_AUTHORIZED: NO
EXECUTION_COMPONENT_CHANGES_AUTHORIZED: NO
LIVE_DEVICE_WORK_AUTHORIZED: NO
```

No runner, adapter, scheduler, queue, broker, worker, agent loop, AI loop, TypeScript automation, Vitest, Playwright, GitHub Actions, provider/API/model call, secrets handling, configuration backup/change, production execution path, SSH, NETCONF, RESTCONF, Day1-Day160 rewrite, second safety matrix, Phase 2M implementation, or unrelated feature work is authorized.

## Smallest Safe Next Step

The outcome-specific next planning-only candidate is:

```text
Phase 2L-02D — Report-index Registry Correction Authorization Gate / Planning Only
STATUS: NEW / FUTURE
SELECTED_NEXT_CANDIDATE: YES
IMPLEMENTATION_AUTHORIZED: NO
```

Phase 2L-02D may decide whether a later bounded registry correction should be authorized. It must not perform a correction itself. Phase 2L-03 remains `NEW / FUTURE`, is not the selected next candidate, and is not started. Phase 2M remains not started.

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
ALL_ELEVEN_ITEMS_CLASSIFIED: PASS
DAY4_DEDICATED_REVIEW_PRESENT: PASS
REQUIRED_OPTIONAL_MODEL_REVIEW_PRESENT: PASS
EXACTLY_ONE_OVERALL_OUTCOME_SELECTED: PASS
EXACTLY_ONE_NEXT_CANDIDATE_SELECTED: PASS
NO_IMPLEMENTATION_BEHAVIOR_INTRODUCED: PASS
NO_REPORT_OR_FIXTURE_CREATION_AUTHORIZED: PASS
NO_REPORT_INDEX_OR_REGISTRY_CHANGE_AUTHORIZED: PASS
NO_DAY1_DAY160_REWRITE: PASS
NO_SECOND_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

## Final Decision

```text
FINAL_PHASE_DECISION: PASS
PHASE: 2L-02C
STATUS: DONE / MERGED_TO_MAIN
INVENTORY_ITEMS_REVIEWED: 11
INVENTORY_ITEMS_CLASSIFIED: 11
DAY4_REGISTRY_EXPECTATION_REVIEW_INCLUDED: YES
REGISTRY_DEFINITION_FILES_IDENTIFIED: YES
REQUIRED_OPTIONAL_MODEL_REVIEWED: YES
OVERALL_REVIEW_OUTCOME: REGISTRY_EXPECTATION_MISMATCH_CONFIRMED
NEXT_FUTURE_CANDIDATE: Phase 2L-02D — Report-index Registry Correction Authorization Gate / Planning Only
IMPLEMENTATION_AUTHORIZED: NO
REPORT_INDEX_COMMAND_RUN: NO
REPORT_PRODUCING_TASK_RUN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```
