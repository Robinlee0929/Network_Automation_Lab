# Phase 2G-01 — Track Prioritization / Planning Only

## Status

```text
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_ONLY_REPORT_ONLY
PHASE_STATUS: TRACK_PRIORITIZATION
IMPLEMENTATION_AUTHORIZED: NO
RUNNER_ADAPTER_EXECUTION_PATH_CHANGES_AUTHORIZED: NO
LIVE_NETWORK_ACCESS_AUTHORIZED: NO
```

## Phase Title and Scope

Phase 2G-01 — Track Prioritization / Planning Only compares the five existing Phase 2G candidate tracks and records a planning-only priority recommendation.

This document is planning-only, documentation-only, and report-only. It does not authorize implementation, does not select an implementation slice, does not start implementation, and does not change source behavior, tests, runners, adapters, schedulers, queues, workers, brokers, or agent loops.

The safety baseline remains report-only, dry-run, and mock-only.

## Inputs Reviewed

AGENTS.md confirmation:

- `AGENTS.md` found before action: YES
- `AGENTS.md` read before action: YES
- `AGENTS.md` modified: NO

Existing documents reviewed:

- `AGENTS.md`
- `README.md`
- `docs/phase_2g/phase_2g_00_project_acceleration_demo_value_entry_review.md`
- `docs/phase_2g/phase_2g_00a_future_plan_addendum.md`
- `docs/phase_2a/phase_2a_11_phase_closure_final_readiness_review.md`
- `docs/phase_2b/phase_2b_12_future_implementation_authorization_review.md`
- `docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md`
- `docs/phase_2c/phase_2c_27_close_or_continue_decision_gate_planning_only.md`
- `docs/phase_2d/phase_2d_07_close_or_continue_decision_gate_planning_only.md`
- `docs/phase_2e/phase_2e_08_close_or_continue_decision_gate_planning_only.md`
- `docs/phase_2f/phase_2f_12_close_or_continue_decision_gate_planning_only.md`

These inputs were used only to compare existing Phase 2G candidate tracks and preserve the prior planning-gate pattern.

## Candidate Track Inventory

Phase 2G-00 and Phase 2G-00A define exactly five candidate tracks. Phase 2G-01 does not add a sixth track and does not rename the tracks.

| Track name | Source planning role | Phase 2G-01 inventory status |
| --- | --- | --- |
| Demo Flow | Make the reviewer path easier to follow from entry point to evidence, with clearer sequencing for a portfolio walkthrough. | Existing candidate only |
| Project Health Dashboard | Surface project status, phase closure state, validation posture, and reviewer-visible readiness in one planning direction. | Existing candidate only |
| Evidence / Report Dashboard | Improve reviewer navigation across evidence documents, report-only outputs, and acceptance gates. | Existing candidate only |
| Codex Workflow Accelerator | Clarify repeatable Codex task protocol, branch/review rhythm, scope gates, and final reporting patterns for safer future work. | Existing candidate only |
| Phase Scaffold | Prepare a consistent planning scaffold for future Phase 2G slices so each slice starts with status, non-goals, gates, and safety checks. | Existing candidate only |

## Prioritization Criteria

Each track is compared using planning-only criteria:

- Safety fit: how naturally the track preserves the current report-only, dry-run, mock-only boundary.
- Evidence value: how much the track improves reviewer traceability and proof visibility.
- User/demo value: how much the track helps a reviewer or interviewer understand the project quickly.
- Implementation risk: whether later work could drift toward source behavior, runtime behavior, live access, or automation.
- Scope clarity: whether the next planning conversation can be kept narrow and reviewer-visible.
- Dependency readiness: whether existing static documents and reports are enough to plan the track.
- Boundary preservation: whether the track clearly avoids live access, providers, model/API use, secrets, config backup/change, and execution paths.

## Comparison Table

| Track name | Safety fit | Evidence value | User/demo value | Implementation risk | Scope clarity | Dependency readiness | Report-only / dry-run / mock-only boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Demo Flow | High - can be planned as a non-executing narrative over existing artifacts. | High - clarifies which evidence to inspect and in what order. | High - directly improves portfolio walkthrough clarity. | Low - risk stays low if the next phase remains narrative-only and avoids new controls. | High - Phase 2G-00A already names Demo Flow Definition as the next planning step. | High - existing README, demo docs, phase docs, and report-index outputs provide enough planning material. | Strong fit - can preserve static, reviewer-visible, no-execution boundaries. |
| Project Health Dashboard | Medium - safe if static, but dashboard wording can imply refresh, probes, or live status if not constrained. | Medium - could summarize phase closure and validation posture. | Medium - useful orientation, but less immediately narrative than Demo Flow. | Medium - later work would need tight constraints to avoid background refresh, probes, schedulers, queues, workers, or runtime integrations. | Medium - Phase 2G-03 must split it from Evidence / Report Dashboard before it is narrow enough. | Medium - existing phase status is available, but display scope needs definition. | Preserved only if future planning limits it to existing static artifacts. |
| Evidence / Report Dashboard | High - naturally aligns with reviewer evidence and report-only outputs. | High - improves traceability across planning, acceptance, and report artifacts. | Medium-high - helps reviewers inspect proof after they know the demo path. | Medium - later work must avoid invoking report generators, runners, adapters, or live collection. | Medium - needs Phase 2G-03 scope split before it becomes a clear next focus. | Medium-high - many static evidence docs exist, but source-of-truth rules need planning. | Strong if limited to existing static artifacts and documented report references. |
| Codex Workflow Accelerator | Medium-high - can remain templates and checklists only. | Medium - improves process evidence and repeatability. | Medium - valuable to maintainers and reviewers of process discipline, less visible in a first demo. | Medium - must avoid agent loops, queues, schedulers, workers, model/API integration, or autonomous execution behavior. | Medium-high - requirements can be documented without source changes. | High - AGENTS.md and prior final-report patterns provide strong context. | Preserved if treated as documentation templates only. |
| Phase Scaffold | High - a documentation scaffold can preserve gate discipline. | Medium - improves consistency across future phase records. | Low-medium - helps future maintainability more than immediate demo clarity. | Low-medium - risk is low if no generator or execution framework is created. | Medium-high - scaffold sections are clear, but it should not select or imply future slices. | High - prior phase documents already model the expected sections. | Strong if it remains a static document pattern only. |

## Recommended Priority Order

This is a planning recommendation only. It does not authorize implementation.

1. Demo Flow
2. Evidence / Report Dashboard
3. Project Health Dashboard
4. Codex Workflow Accelerator
5. Phase Scaffold

## Recommendation Rationale

`Demo Flow` is the highest priority because it gives the strongest immediate demo value with the clearest safety fit. It can be planned as a non-executing narrative over existing README, phase, evidence, and report-index artifacts.

`Evidence / Report Dashboard` ranks second because it increases reviewer traceability and pairs well with the demo narrative, but it should wait for a planning scope split so it does not become an implementation or report-generation task.

`Project Health Dashboard` ranks third because it could improve orientation, but its dashboard language carries more drift risk unless future planning limits it to existing static status and avoids refresh, probe, scheduler, queue, worker, or runtime behavior.

`Codex Workflow Accelerator` ranks fourth because it improves delivery discipline, but its value is process-oriented rather than the first reviewer-facing demo path. It must remain documentation/template planning only.

`Phase Scaffold` ranks fifth because it is useful for consistency, but it is less urgent for demo value than the tracks that improve immediate reviewer navigation and evidence discovery.

## Selected Next Planning Direction

Recommended next planning focus: `Demo Flow`.

This next planning direction should remain a planning-only definition of a reviewer-safe narrative using existing reports, evidence artifacts, and phase documents. It must not define an implementation slice, create implementation acceptance criteria, authorize implementation, or add execution-capable behavior.

## Explicit Non-Authorization Statement

```text
IMPLEMENTATION_AUTHORIZED: NO
RUNNER_ADAPTER_EXECUTION_PATH_CHANGES_AUTHORIZED: NO
LIVE_NETWORK_ACCESS_AUTHORIZED: NO
PROVIDER_API_MODEL_USE_AUTHORIZED: NO
SECRETS_USE_AUTHORIZED: NO
CONFIG_BACKUP_CHANGE_AUTHORIZED: NO
```

Additional preserved boundaries:

- Source code changes authorized: NO
- Test changes authorized: NO
- Runner changes authorized: NO
- Adapter changes authorized: NO
- Scheduler / queue / broker / worker / agent loop authorized: NO
- SSH authorized: NO
- NETCONF authorized: NO
- RESTCONF authorized: NO
- Day1-Day160 rewrite authorized: NO
- Second safety matrix authorized: NO

## Continuation Rule

The next phase may only proceed as another planning / authorization gate unless the user explicitly authorizes implementation in a later task.

If a later task requests Phase 2G continuation, it must restate the task mode, phase goal, allowed scope, forbidden scope, implementation boundary, and validation plan before any edits. If implementation is requested later, it must be authorized by a separate explicit gate and remain within the safety boundary stated by that task.

## Final Status

```text
PHASE_2G_01_TRACK_PRIORITIZATION_COMPLETE: YES
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
REPORT_ONLY: YES
FIVE_EXISTING_TRACKS_COMPARED: YES
SIXTH_TRACK_ADDED: NO
TRACKS_RENAMED: NO
RECOMMENDED_NEXT_PLANNING_FOCUS: Demo Flow
IMPLEMENTATION_AUTHORIZED: NO
IMPLEMENTATION_SLICE_DEFINED: NO
IMPLEMENTATION_ACCEPTANCE_CRITERIA_CREATED: NO
SOURCE_CODE_CHANGED: NO
TESTS_CHANGED: NO
RUNNER_ADAPTER_EXECUTION_PATH_CHANGED: NO
FORBIDDEN_SCOPE_TOUCHED: NO
LIVE_NETWORK_SSH_NETCONF_RESTCONF_TOUCHED: NO
PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED: NO
DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```
