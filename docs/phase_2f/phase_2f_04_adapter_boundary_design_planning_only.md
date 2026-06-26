# Phase 2F-04 - Adapter Boundary Design / Planning Only

Status: PLANNING_ONLY

Decision: `ADAPTER_BOUNDARY_DESIGN_PLANNING_ONLY_COMPLETE`

## Scope Statement

Phase 2F-04 creates a planning-only adapter boundary design from the Phase 2F-02 candidate inventory and the Phase 2F-03 safety delta review.

This is a conceptual reviewer boundary only.

This document does not authorize implementation.

This document does not create adapter code, runner behavior, execution paths, scheduler, queue, broker, worker, agent-loop behavior, live device access, SSH, NETCONF, RESTCONF, provider/API/model integration, secrets handling, config backup, config change, production execution paths, Day1-Day160 rewrite, or a second safety matrix.

## AGENTS.md Compliance Note

`AGENTS.md` was found and read before repository analysis and file changes.

Task mode: planning-only / documentation-only / report-only.

Required automation reference read: `docs/automation_readiness/actual_automation_integration_plan.md`.

## References Reviewed

- `AGENTS.md`
- Phase 2F-04 task brief
- `README.md`
- `docs/automation_readiness/actual_automation_integration_plan.md`
- `docs/phase_2f/phase_2f_00_readonly_lab_adapter_reentry_gate_planning_only.md`
- `docs/phase_2f/phase_2f_01_adapter_scope_reconciliation_planning_only.md`
- `docs/phase_2f/phase_2f_02_adapter_boundary_candidate_inventory_planning_only.md`
- `docs/phase_2f/phase_2f_03_adapter_safety_delta_review_planning_only.md`

## Prior-State Evidence

Phase 2F-00 allowed planning discussion only.

Phase 2F-01 reconciled adapter planning scope and explicitly did not create a candidate inventory, select a slice, authorize implementation, design adapter boundaries, add adapter code, change runners or execution paths, use live access, or create a second safety matrix.

Phase 2F-02 listed five adapter boundary discussion candidates. It selected no candidate, ranked no candidate, performed no safety delta review, created no adapter boundary design, authorized no implementation, and changed no code or execution behavior.

Phase 2F-03 completed a safety delta review for those five candidates. It selected no candidate, ranked no candidate, authorized no implementation, and recorded that some candidates require narrowing, exclusion, or deferral before Phase 2F-04.

Phase 2F-04 accepts that safety review as a constraint. Candidate-02 remains deferred and is not designed as a live source boundary.

## Planning-Only Boundary Design Rules

The design below is intentionally limited to reviewer-visible planning boundaries.

It may define:

- conceptual boundary names
- allowed planning inputs
- forbidden planning inputs
- expected reviewer labels
- no-execution proof expectations
- later-gate questions

It may not define:

- adapter source files
- classes, functions, method signatures, or imports
- transport clients
- device inventory
- credential references
- command or RPC allowlists
- SSH, NETCONF, RESTCONF, API, or controller behavior
- runner routing
- dashboard action behavior
- report schema changes
- implementation tests
- live or production execution behavior

## Boundary Design Summary

| Boundary | Source candidate | Planning-only purpose | Allowed in this phase | Explicitly deferred or forbidden |
| --- | --- | --- | --- | --- |
| Boundary A - static evidence intake boundary | candidate-01 | Keep already-existing local static artifacts separate from any live source or adapter behavior. | Describe how static artifacts may be cited as planning evidence. | Artifact intake code, accepted artifact schemas, runner validation, live collection, or adapter invocation. |
| Boundary B - blocked live-source boundary | candidate-02 | Preserve a visible stop line around future read-only lab source discussion. | Record that live-source details are deferred because Phase 2F-03 marked this candidate close to forbidden scope. | Protocols, device targets, inventory, credential references, command lists, transport mechanics, or readiness claims. |
| Boundary C - rejection and no-execution boundary | candidate-03 | Keep rejected, unapproved, unsafe, or out-of-scope requests from reaching adapters, brokers, runners, or execution paths. | State the reviewer-visible invariant that rejection must happen before any execution-capable boundary. | Enforcement design, guard code, runner changes, adapter invocation, broker behavior, or tests. |
| Boundary D - reviewer evidence boundary | candidate-04 | Keep planning evidence explicit about status, limits, and no-execution proof. | Define labels reviewers should see in future planning artifacts. | Report rendering changes, dashboard changes, report-index changes, evidence generators, or schema changes. |
| Boundary E - later authorization boundary | candidate-05 | Keep candidate discussion separate from any later implementation authorization gate. | List questions a later gate must answer before implementation can be considered. | Implementation authorization, slice selection, validation requirements for implementation, or parallel safety framework creation. |

## Boundary A - Static Evidence Intake Boundary

Planning-only design:

- Static evidence may be referenced only when it already exists locally in the repository or in committed reviewer documentation.
- Static evidence must remain a citation source, not an execution source.
- Static evidence must not be refreshed by contacting devices, controllers, providers, APIs, or models.
- Static evidence must not imply that a future adapter exists, is callable, or is approved.

Reviewer-visible labels:

- `STATIC_EVIDENCE_ONLY`
- `NO_LIVE_COLLECTION`
- `NO_ADAPTER_INVOCATION`
- `IMPLEMENTATION_NOT_AUTHORIZED`

No-execution proof expectation:

- A reviewer should be able to see that this boundary cites existing documents or artifacts only and does not add any path that can run, collect, or refresh data.

## Boundary B - Blocked Live-Source Boundary

Planning-only design:

- Future read-only lab source details remain explicitly deferred.
- This boundary is a stop line, not a design for live access.
- No protocol, transport, command, RPC, target, inventory, credential, or allowlist detail is defined in Phase 2F-04.
- Any later task that wants to discuss those details must provide a separate task mode, phase goal, allowed scope, forbidden scope, boundary, and validation plan.

Reviewer-visible labels:

- `LIVE_SOURCE_DETAILS_DEFERRED`
- `READ_ONLY_LAB_ACCESS_NOT_AUTHORIZED`
- `SSH_NETCONF_RESTCONF_NOT_AUTHORIZED`
- `SECRETS_NOT_TOUCHED`

No-execution proof expectation:

- A reviewer should be able to confirm that this document does not name devices, protocols, commands, credentials, transports, or inventory paths.

## Boundary C - Rejection and No-Execution Boundary

Planning-only design:

- Rejected, unapproved, unsafe, or out-of-scope requests must remain outside any adapter, broker, runner, or execution path.
- The rejection boundary must be described before any future boundary that could reach an adapter.
- Rejection evidence must be reviewer-visible before any future implementation gate is considered.
- Phase 2F-04 does not define the enforcement mechanism.

Reviewer-visible labels:

- `REJECTED_BEFORE_ADAPTER`
- `ADAPTER_INVOCATION_ALLOWED_FALSE`
- `RUNNER_EXECUTION_ALLOWED_FALSE`
- `NO_EXECUTION_PATH_REACHED`

No-execution proof expectation:

- A reviewer should be able to see that the invariant is preserved as a planning requirement and that no code path is added to enforce or bypass it.

## Boundary D - Reviewer Evidence Boundary

Planning-only design:

- Future planning artifacts should distinguish status from authorization.
- Evidence should use explicit status fields such as `PLANNING_ONLY`, `REPORT_ONLY`, `LOCKED`, `BLOCKED`, `DEFERRED`, or `NOT_AUTHORIZED`.
- Evidence must state whether implementation, adapter invocation, live access, secrets, and config change behavior are authorized.
- Evidence must not become a dashboard action, runner task, or report-index behavior change during this phase.

Reviewer-visible labels:

- `REVIEWER_EVIDENCE_ONLY`
- `STATUS_IS_NOT_AUTHORIZATION`
- `NO_REPORT_RENDERING_CHANGE`
- `NO_DASHBOARD_ACTION_CHANGE`

No-execution proof expectation:

- A reviewer should be able to read the status labels without needing to run a live workflow or infer authorization from the presence of planning evidence.

## Boundary E - Later Authorization Boundary

Planning-only design:

- Any later implementation authorization gate must be separate from this planning-only design.
- Any later gate must name the exact capability under review.
- Any later gate must separately define allowed scope, forbidden scope, implementation boundary, validation requirements, and negative tests.
- Any later gate must continue to preserve the repository default safety baseline unless the user explicitly authorizes a narrower safety change.

Reviewer-visible labels:

- `LATER_GATE_REQUIRED`
- `IMPLEMENTATION_NOT_AUTHORIZED`
- `NO_SLICE_SELECTED`
- `NO_SECOND_SAFETY_MATRIX`

No-execution proof expectation:

- A reviewer should be able to confirm that Phase 2F-04 does not approve any future implementation step and does not create a competing safety framework.

## Candidate Handling Decision

| Candidate | Phase 2F-04 handling | Reason |
| --- | --- | --- |
| candidate-01 - Static artifact intake boundary | Included as Boundary A | It can be safely described as citation-only planning evidence. |
| candidate-02 - Future read-only lab source boundary | Deferred as Boundary B stop line only | Phase 2F-03 marked this candidate close to forbidden scope; live-source details are not designed here. |
| candidate-03 - Rejection and no-execution boundary | Included as Boundary C | It preserves an existing no-execution invariant without defining enforcement code. |
| candidate-04 - Reviewer evidence boundary | Included as Boundary D | It keeps planning status visible without changing report or dashboard behavior. |
| candidate-05 - Approval gate boundary | Included as Boundary E | It preserves staged authorization discipline without approving implementation. |

## Explicit Non-Decisions

Phase 2F-04 does not decide:

- implementation authorization
- adapter source ownership
- adapter interface shape
- command or RPC allowlists
- device inventory
- credential handling
- transport mechanics
- runner routing
- report rendering behavior
- dashboard action behavior
- implementation tests
- next implementation slice
- next phase

## Validation Plan

Validate this planning-only documentation change with:

- `git diff --check`
- `python network_lab.py --task report-index`
- `python -m pytest`

Full pytest is included because `AGENTS.md` lists it as standard validation before completion, even though this planning-only documentation/index change does not affect task registry, CLI dispatch, runner behavior, adapter behavior, report rendering code, shared utilities, cross-phase behavior, or safety validation behavior.

## Final Safety Confirmation

TASK_MODE: planning-only / documentation-only / report-only

BOUNDARY_DESIGN_CREATED: PLANNING_ONLY

IMPLEMENTATION_AUTHORIZED: NO

CANDIDATE_SELECTED_FOR_IMPLEMENTATION: NO

LIVE_SOURCE_DETAILS_DESIGNED: NO

ADAPTER_CODE_ADDED: NO

RUNNER_OR_EXECUTION_PATH_CHANGED: NO

SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO

SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO

PROVIDER_API_MODEL_SECRETS_TOUCHED: NO

CONFIG_BACKUP_OR_CHANGE_ADDED: NO

PRODUCTION_EXECUTION_PATH_ADDED: NO

DAY1_DAY160_REWRITTEN_OR_REPLACED: NO

SECOND_SAFETY_MATRIX_CREATED: NO

NEXT_PHASE_STARTED: NO

EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
