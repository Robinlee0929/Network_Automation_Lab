# Phase 2G-03 — Demo Flow Slice Definition / Implementation Kickoff Gate / Planning Only

## Status

```text
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_ONLY_REPORT_ONLY
PHASE_STATUS: DEMO_FLOW_SLICE_DEFINITION
IMPLEMENTATION_AUTHORIZED_IN_THIS_PHASE: NO
RUNTIME_BEHAVIOR_CHANGED: NO
NEXT_PHASE_IMPLEMENTATION_RECOMMENDED: YES
NEXT_PHASE_ALLOWED_BOUNDARY: STATIC_DOCUMENTATION_ONLY_DEMO_WALKTHROUGH
LIVE_NETWORK_ACCESS_AUTHORIZED: NO
RUNNER_ADAPTER_EXECUTION_PATH_CHANGES_AUTHORIZED: NO
```

Phase 2G-03 is planning-only. It defines the smallest safe Demo Flow slice for a possible later implementation phase and decides whether Phase 2G-04 may enter implementation under a narrow static-documentation boundary.

This phase does not implement the demo flow, does not modify runtime behavior, does not create new report generation logic, and does not change source behavior, tests, runners, adapters, schedulers, queues, brokers, workers, or agent loops.

## Purpose

Define the minimum safe Demo Flow slice and decide whether Phase 2G-04 may enter implementation.

The Demo Flow slice must help a reviewer find and understand existing evidence without implying live validation, refresh behavior, device access, artifact regeneration, or execution.

## Current Baseline

Phase 2G-02 is closed.

Work must continue from a clean workspace or the Phase 2G-02 recovery workspace.

The original ACL-blocked workspace must not be used.

Phase 2G-02 established that Demo Flow may use existing static evidence and report artifacts only, remains local and deterministic, and does not authorize implementation by itself.

## Minimum Demo Entry Point

Selected entry point:

```text
ENTRY_POINT_ID: phase_2g_static_demo_walkthrough_doc
ENTRY_POINT_TYPE: Single static Markdown walkthrough
FUTURE_FILE: docs/phase_2g/phase_2g_04_demo_flow_walkthrough.md
```

This is the smallest safe demo entry point because it is one reviewer-facing document that can sequence existing artifacts without adding runtime controls, report generation, dashboard behavior, background refresh, or execution logic.

The entry point must remain:

- local
- deterministic
- report-only
- dry-run
- mock/static-artifact based
- reviewer-visible
- non-executing

The future walkthrough may explain which existing artifact to open first, what safety boundary it proves, and what evidence to inspect next. It must not rerun tasks, refresh reports, call devices, invoke adapters, or generate new runtime artifacts.

## Allowed Existing Artifacts

A future Demo Flow implementation may reference only existing static, report, and evidence artifacts such as:

- `README.md`
- `docs/phase_2g/phase_2g_00_project_acceleration_demo_value_entry_review.md`
- `docs/phase_2g/phase_2g_00a_future_plan_addendum.md`
- `docs/phase_2g/phase_2g_01_track_prioritization.md`
- `docs/phase_2g/phase_2g_02_demo_flow_authorization_gate.md`
- `docs/phase_2f/phase_2f_12_close_or_continue_decision_gate_planning_only.md`
- `docs/demo/offline_interview_demo_kit/README.md`
- `docs/demo/offline_interview_demo_kit/demo_checklist.md`
- `docs/demo/offline_interview_demo_kit/demo_commands.md`
- `docs/demo/offline_interview_demo_kit/no_live_dependency_statement.md`
- `docs/demo/offline_interview_demo_kit/interview_talk_track_3_to_5_min.md`
- `docs/demo/day52_offline_demo_package/README.md`
- `docs/demo/day52_offline_demo_package/interview_demo_folder_usage_guide.md`
- committed screenshot references under `docs/demo/day52_offline_demo_package/screenshots/`
- `reports/report_index.html`
- `reports/portfolio/day24_rc_demo_flow.html`
- `reports/portfolio/day24_rc_demo_flow.json`
- `reports/portfolio/day40_v0.2_demo_readiness_review.html`
- `reports/portfolio/day40_v0.2_demo_readiness_review.json`
- existing committed report-only evidence under `reports/lab-summary/` when referenced as historical static evidence

These artifacts may be referenced only as existing reviewer evidence. Phase 2G-04 must not create new runtime artifact generation logic, regenerate reports, run report-producing tasks as part of the demo flow, or treat any historical Day1-Day160 artifact as editable source for a rewrite.

## Future Implementation Candidate Touch List

Candidate scope only. This list is not current authorization.

If Phase 2G-04 is explicitly authorized as implementation later, the candidate touch list is limited to:

- `docs/phase_2g/phase_2g_04_demo_flow_walkthrough.md`
- `README.md`, only for one narrow index/reference line to the Phase 2G-04 walkthrough if needed

No other files or file areas are pre-authorized.

The candidate implementation must not touch:

- Python source files
- tests
- runner registry or CLI dispatch
- adapters or adapter contracts
- dashboard application code
- report rendering code
- report generation scripts
- static report artifact contents
- Day1-Day160 historical documents or artifacts except by reference

## Explicit Forbidden Scope

Phase 2G-03 and any later Phase 2G-04 implementation using this boundary forbid:

- No SSH.
- No live device access.
- No NETCONF.
- No RESTCONF.
- No provider, API, model, or secret access.
- No config backup.
- No config change.
- No scheduler, queue, broker, worker, or agent loop.
- No runner or adapter expansion unless explicitly authorized by a later phase.
- No Day 1-160 rewrite.
- No second safety matrix.
- No implementation in this phase.

Rejected, out-of-scope, or future-only demo ideas must not invoke adapters, brokers, runners, schedulers, workers, queues, provider integrations, live network activity, or configuration-changing behavior.

## Acceptance Criteria

Phase 2G-03 is accepted only if all of the following are true:

- The phase document exists at `docs/phase_2g/phase_2g_03_demo_flow_slice_definition.md`.
- The document clearly states that Phase 2G-03 is planning-only.
- The document states that implementation is not authorized in Phase 2G-03.
- Exactly one minimum demo entry point is selected.
- The selected entry point remains local, deterministic, report-only, dry-run, and mock/static-artifact based.
- Allowed existing artifacts are listed as references only.
- No new runtime artifact generation logic is created or authorized.
- The Phase 2G-04 candidate touch list is exact and marked candidate scope only.
- Forbidden scope is explicitly listed.
- The Phase 2G-04 decision is recorded with a limited implementation boundary or a missing-items list.
- README is updated only as a narrow index/reference if needed.
- No runtime behavior, tests, runners, adapters, providers, secrets, scheduler, queue, broker, worker, or agent loop are changed.

## Phase 2G-04 Decision

Recommendation:

```text
PHASE_2G_04_RECOMMENDED_TO_ENTER_IMPLEMENTATION: YES
IMPLEMENTATION_BOUNDARY: STATIC_DOCUMENTATION_ONLY_DEMO_WALKTHROUGH
```

Phase 2G-04 may enter implementation only if the later task explicitly authorizes implementation and keeps the work inside this exact limited boundary:

- Create `docs/phase_2g/phase_2g_04_demo_flow_walkthrough.md` as a single static Markdown walkthrough.
- Use only existing static docs, committed screenshots, and committed report/evidence artifacts as references.
- Optionally add one README index/reference line to the new Phase 2G-04 walkthrough.
- Preserve report-only, dry-run, mock-only, local, deterministic, and non-executing boundaries.
- Do not modify runtime behavior, report generation logic, source code, tests, runners, adapters, dashboards, historical Day1-Day160 artifacts, or safety matrices.

If a later Phase 2G-04 task requests anything outside that boundary, implementation should remain blocked until the user provides a separate explicit safety gate with allowed scope, forbidden scope, and validation requirements.

## Final Status

```text
PHASE_2G_03_DEMO_FLOW_SLICE_DEFINITION_COMPLETE: YES
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
REPORT_ONLY: YES
IMPLEMENTATION_AUTHORIZED_IN_THIS_PHASE: NO
EXACTLY_ONE_MINIMUM_DEMO_ENTRY_POINT_SELECTED: YES
SELECTED_ENTRY_POINT: phase_2g_static_demo_walkthrough_doc
PHASE_2G_04_RECOMMENDED_TO_ENTER_IMPLEMENTATION: YES
PHASE_2G_04_ALLOWED_SCOPE: STATIC_DOCUMENTATION_ONLY_DEMO_WALKTHROUGH
SOURCE_CODE_CHANGED: NO
TESTS_CHANGED: NO
RUNNER_ADAPTER_EXECUTION_PATH_CHANGED: NO
FORBIDDEN_SCOPE_TOUCHED: NO
LIVE_NETWORK_SSH_NETCONF_RESTCONF_TOUCHED: NO
PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED: NO
SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO
DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```
