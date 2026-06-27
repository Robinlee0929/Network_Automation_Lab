# Phase 2G-02 — Demo Flow Authorization Gate / Planning Only

## Status

```text
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_ONLY_REPORT_ONLY
PHASE_STATUS: DEMO_FLOW_AUTHORIZATION_GATE
IMPLEMENTATION_AUTHORIZED: NO
NEXT_PHASE_AUTHORIZED: YES
NEXT_PHASE_TYPE: Planning Only / Slice Definition / Implementation Kickoff Gate
RUNNER_ADAPTER_EXECUTION_PATH_CHANGES_AUTHORIZED: NO
LIVE_NETWORK_ACCESS_AUTHORIZED: NO
```

Phase 2G-02 is planning-only, documentation-only, and report-only. It does not implement runtime behavior, does not define a production execution path, and does not change source behavior, tests, runners, adapters, schedulers, queues, brokers, workers, or agent loops.

The safety baseline remains report-only, dry-run, mock-only, local, deterministic, and reviewer-visible.

## Baseline

Phase 2G-01 completed the track prioritization planning review and selected `Demo Flow` as priority #1.

Phase 2G-01 priority order:

1. Demo Flow
2. Evidence / Report Dashboard
3. Project Health Dashboard
4. Codex Workflow Accelerator
5. Phase Scaffold

This baseline comes from `docs/phase_2g/phase_2g_01_track_prioritization.md` and the Phase 2G-01 commit `24154ea8f072779fe82a6b7687712ec9c8e34069`.

## Objective

Define the authorization boundary for the Demo Flow track without implementation.

This phase evaluates what `Demo Flow` may mean for this repository, which existing artifacts may be used as future demo inputs, what a future slice may include, what it must not include, and which risks must be controlled before any implementation kickoff is considered.

## Demo Flow Track Definition

`Demo Flow` means a presentation, interview, reviewer, or demo-facing path through existing project evidence, reports, docs, static outputs, or already generated artifacts.

The track is intended to help a reviewer understand the project quickly by sequencing existing evidence into a clear walkthrough. It may explain what to inspect, why each artifact matters, and how the artifacts prove the repository's safety posture and portfolio value.

Demo Flow must remain local, deterministic, report-only, dry-run, mock-only, replay/static, or documentation-backed where applicable. It must not depend on runtime network execution, live lab access, external providers, new execution paths, background work, or mutable local state.

## Existing Inputs That May Be Referenced

Future Demo Flow planning may reference existing reviewer-visible artifacts, including:

- `README.md`
- Existing Phase 2G planning documents under `docs/phase_2g/`
- Existing Phase 2F closure and acceptance documents where they explain the current boundary
- Existing demo and portfolio documentation
- Existing report-index references and static report descriptions
- Existing committed screenshots or demo-facing materials
- Existing command/output explanations that are already part of reviewer evidence
- Existing static, dry-run, mock-only, or report-only evidence paths

These inputs may be used only as static references. Referencing an artifact does not authorize regenerating it, invoking a runner, accessing a device, or adding a new execution path.

## Candidate Demo Flow Scope

Candidate future scope items:

- Static demo narrative
- Existing report or evidence walkthrough
- Existing command/output explanation
- Existing dashboard/report index connection
- Demo-ready README or guide
- Replay/static evidence path
- Interview-safe project walkthrough
- Reviewer-facing explanation path

These candidates are planning candidates only. They do not include runtime network execution and do not authorize implementation in this phase.

## Explicit Non-Scope

Phase 2G-02 does not authorize:

- No live device access
- No SSH
- No NETCONF
- No RESTCONF
- No provider/API/model calls
- No secrets
- No credential handling
- No config backup
- No config change
- No runner/adapter/execution implementation
- No scheduler/queue/broker/worker/agent loop
- No broad test execution
- No cleanup of ACL-blocked workspace
- No second safety matrix
- No Day 1-160 rewrite

Rejected, out-of-scope, or future-only demo ideas must not invoke adapters, brokers, runners, schedulers, workers, queues, provider integrations, live network activity, or configuration-changing behavior.

## Authorization Criteria for a Future Implementation Slice

Before any future Demo Flow implementation slice can be authorized, all of the following must be true:

- Exact demo entry point is identified
- Exact static/replay/report artifacts are identified
- No runtime network behavior is required
- No new execution path is introduced
- Demo output is deterministic
- Existing safety boundaries remain unchanged
- File list is narrow and predeclared
- Acceptance criteria are documentation-verifiable
- Rollback is documentation-only or static-artifact-only

If any future request cannot satisfy these criteria, implementation must remain unauthorized and the work must continue as planning-only or be blocked for scope clarification.

## Risk Controls Before Implementation Kickoff

The following risks must be controlled before any implementation kickoff:

- Demo wording must not imply live validation, real-time status, or device access.
- Dashboard/report-index references must not imply refresh, probing, scheduling, or background execution.
- Command/output explanations must identify existing evidence only and must not request reruns.
- File changes must stay narrow and reviewer-visible.
- No existing safety gate, no-execution proof, or forbidden-scope statement may be weakened.
- Any future implementation request must restate task mode, phase goal, forbidden scope, implementation boundary, validation plan, and exact files allowed.

## Phase 2G-03 Recommendation

Recommended next phase:

Phase 2G-03 — Demo Flow Slice Definition / Implementation Kickoff Gate / Planning Only

Purpose:

- Select the smallest safe Demo Flow slice
- Define exact files allowed for a future implementation phase
- Define acceptance criteria
- Decide whether a later implementation phase can be authorized

Phase 2G-03 should remain planning-only. It should define a narrow future implementation slice and should not directly authorize implementation unless a later task explicitly provides a complete safety boundary and approval.

## Authorization Result

```text
IMPLEMENTATION_AUTHORIZED: NO
NEXT_PHASE_AUTHORIZED: YES
NEXT_PHASE_TYPE: Planning Only / Slice Definition / Implementation Kickoff Gate
RECOMMENDED_NEXT_PHASE: Phase 2G-03 — Demo Flow Slice Definition / Implementation Kickoff Gate / Planning Only
```

## Evidence / Commands

Safe commands used for this phase:

- `git remote get-url origin`
- `git branch --show-current`
- `git status --short --branch`
- `git pull --ff-only origin main`
- `git log --oneline --decorate -n 12`
- `git cat-file -t 24154ea8f072779fe82a6b7687712ec9c8e34069`
- `git checkout -b codex/phase-2g-02-demo-flow-authorization-gate-planning-only`
- `Get-ChildItem -LiteralPath docs\phase_2g`
- `rg -n "Phase 2G|phase_2g|2G-01" README.md docs`
- `Get-Content -LiteralPath AGENTS.md`
- `Get-Content -LiteralPath docs\phase_2g\phase_2g_01_track_prioritization.md`
- `Get-Content -LiteralPath README.md`
- `Get-Content -LiteralPath docs\phase_2g\phase_2g_02_demo_flow_authorization_gate.md`
- `git diff --check`
- `git diff --stat`
- `git diff -- README.md docs/phase_2g/phase_2g_02_demo_flow_authorization_gate.md`

Validation commands run after edits:

- `git diff --check`
- `git diff`

Broad pytest is intentionally not run for this planning-only documentation task.

## Final Status

```text
PHASE_2G_02_DEMO_FLOW_AUTHORIZATION_GATE_COMPLETE: YES
PLANNING_ONLY: YES
DOCUMENTATION_ONLY: YES
REPORT_ONLY: YES
DEMO_FLOW_DEFINED: YES
STATIC_EXISTING_INPUTS_IDENTIFIED: YES
FUTURE_SCOPE_CANDIDATES_LISTED: YES
EXPLICIT_NON_SCOPE_RECORDED: YES
IMPLEMENTATION_AUTHORIZED: NO
NEXT_PHASE_AUTHORIZED: YES
RECOMMENDED_NEXT_PHASE: Phase 2G-03 — Demo Flow Slice Definition / Implementation Kickoff Gate / Planning Only
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
