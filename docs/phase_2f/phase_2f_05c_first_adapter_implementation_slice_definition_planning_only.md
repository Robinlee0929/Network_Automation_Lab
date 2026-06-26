# Phase 2F-05C — First Adapter Implementation Slice Definition / Planning Only

Status: PLANNING_ONLY

Decision: `AUTHORIZE_2F_06_FOR_DEFINED_SCOPE_ONLY`

## Starting State from 2F-05B

Phase 2F-05B re-checked implementation authorization after Phase 2F-05A clarified the Phase 2F-03 safety delta uncertainty.

Phase 2F-05B recorded:

```text
AUTHORIZATION_DECISION: DEFERRED
IMPLEMENTATION_AUTHORIZED: NO
PHASE_2F_06_STATUS: BLOCKED
```

Phase 2F-05B deferred authorization because the existing Phase 2F evidence did not yet define one concrete Phase 2F-06 implementation slice, implementation-level adapter source ownership, interface shape, file boundary, negative-test boundary, or acceptance boundary.

## Purpose

Phase 2F-05C exists only to define the missing `AUTHORIZED_2F_06_SCOPE`.

This document is planning-only, documentation-only, and report-only. It does not start Phase 2F-06 and does not implement the adapter slice.

## AGENTS.md Compliance

`AGENTS.md` was found and read before repository analysis and file changes.

Task mode: planning-only / documentation-only / report-only.

Required automation reference read: `docs/automation_readiness/actual_automation_integration_plan.md`.

`AGENTS.md` was not modified.

## References Reviewed

- `AGENTS.md`
- Phase 2F-05C task brief
- `README.md`
- `docs/automation_readiness/actual_automation_integration_plan.md`
- `docs/phase_2f/phase_2f_00_readonly_lab_adapter_reentry_gate_planning_only.md`
- `docs/phase_2f/phase_2f_01_adapter_scope_reconciliation_planning_only.md`
- `docs/phase_2f/phase_2f_02_adapter_boundary_candidate_inventory_planning_only.md`
- `docs/phase_2f/phase_2f_03_adapter_safety_delta_review_planning_only.md`
- `docs/phase_2f/phase_2f_04_adapter_boundary_design_planning_only.md`
- `docs/phase_2f/phase_2f_05_authorization_gate_planning_only.md`
- `docs/phase_2f/phase_2f_05a_safety_delta_clarification_gate_planning_only.md`
- `docs/phase_2f/phase_2f_05b_authorization_recheck_gate_planning_only.md`

## Selected First Adapter Implementation Slice

```text
AUTHORIZED_2F_06_SCOPE:
  name: non_executing_local_adapter_contract_skeleton
  intent: Define a local-only, deterministic adapter contract/skeleton that documents the adapter boundary without connecting it to any runner, execution path, transport, live device, secret, or configuration behavior.
  allowed_changes:
    - Add isolated adapter-boundary source definitions for a non-executing local contract/skeleton only, with no SSH, NETCONF, RESTCONF, provider/API/model, secrets, inventory, command allowlist, or transport imports.
    - Add local deterministic unit tests and reviewer documentation proving the skeleton is not wired into runners, execution paths, scheduler, queue, broker, worker, agent loop, live access, secrets, config backup, or config change behavior.
  forbidden_changes:
    - runner integration
    - adapter execution wiring
    - scheduler/queue/broker/worker/agent loop
    - live network access
    - SSH/NETCONF/RESTCONF
    - provider/API/model/secrets
    - device inventory or credential references
    - command or RPC allowlists
    - config backup/change
    - production execution path
    - Day1-Day160 rewrite or replacement
    - second safety matrix
  verification:
    - local deterministic validation
    - no network access
    - no secrets access
    - no runner/execution path change
    - invalid input handling
    - direct unit-level proof that rejected or unsupported adapter calls remain non-executing
    - static evidence that no transport, credential, inventory, provider/API/model, queue, scheduler, worker, or agent-loop dependency was introduced
```

This selected scope is intentionally smaller than a read-only lab adapter. It is an adapter boundary/contract skeleton only. It may define local data shapes, status labels, and deterministic unsupported/not-authorized behavior for direct unit tests, but it must not collect data, contact devices, run commands, call transports, load credentials, or become reachable from existing runner or execution workflows.

## Explicit Authorization Result

Because this document defines one clear, minimal, verifiable scope, Phase 2F-05C records:

```text
AUTHORIZATION_DECISION: AUTHORIZE_2F_06_FOR_DEFINED_SCOPE_ONLY
IMPLEMENTATION_AUTHORIZED: YES_FOR_AUTHORIZED_2F_06_SCOPE_ONLY
PHASE_2F_06_STATUS: UNBLOCKED_FOR_AUTHORIZED_SCOPE_ONLY
```

Phase 2F-06 remains blocked for all work outside `AUTHORIZED_2F_06_SCOPE`.

This authorization does not authorize broad adapter implementation, read-only lab access, live source details, runner integration, adapter execution wiring, command or RPC allowlists, credential handling, or any production-capable path.

## Non-Authorization List

Phase 2F-05C does not authorize:

- broad adapter implementation
- runner integration
- execution path changes
- scheduler/queue/broker/worker/agent loop
- live network access
- SSH/NETCONF/RESTCONF
- provider/API/model integration
- secrets usage
- device inventory or credential references
- command or RPC allowlists
- config backup/change
- rewriting Day1-Day160 history
- creating a second safety matrix

## Acceptance Criteria for Future Phase 2F-06

Future Phase 2F-06 acceptance is limited only to `non_executing_local_adapter_contract_skeleton`.

Phase 2F-06 may be accepted only if all of the following are true:

- The implementation remains local-only, deterministic, dry-run / report-only / mock-only compatible, and independently testable.
- The implementation adds no SSH, NETCONF, RESTCONF, live device, provider/API/model, secrets, credential, inventory, command allowlist, transport, config backup, or config change behavior.
- The implementation is not imported by or wired into any runner, execution path, scheduler, queue, broker, worker, agent loop, dashboard action, report-index behavior, or production path.
- Unit tests prove invalid, unsupported, or not-authorized adapter inputs remain deterministic and non-executing.
- Static or test evidence proves no network access and no secrets access are required.
- Reviewer-facing documentation states that Phase 2F-06 is unblocked only for the authorized scope and remains blocked for every other adapter capability.
- No Day1-Day160 history is rewritten or replaced.
- No second safety matrix is created.

If any future Phase 2F-06 work needs live access, read-only lab communication, SSH, NETCONF, RESTCONF, provider/API/model integration, secrets, inventory, command allowlists, runner wiring, execution paths, config backup, or config changes, it is outside this authorization and must remain blocked until a separate explicit safety gate authorizes it.

## Validation Plan

Validate this planning-only documentation change with:

- `git diff --check`
- `python network_lab.py --task report-index`
- `python -m pytest`

Full pytest is included because `AGENTS.md` lists it as standard validation before completion, even though this planning-only documentation/index change does not affect task registry, CLI dispatch, runner behavior, adapter behavior, report rendering code, shared utilities, cross-phase behavior, or safety validation behavior.

## Final Status Block

```text
PHASE_2F_05C_STATUS: COMPLETE
TASK_MODE: PLANNING_ONLY_DOCUMENTATION_ONLY_REPORT_ONLY
AUTHORIZED_2F_06_SCOPE_DEFINED: YES
AUTHORIZED_2F_06_SCOPE: non_executing_local_adapter_contract_skeleton
AUTHORIZATION_DECISION: AUTHORIZE_2F_06_FOR_DEFINED_SCOPE_ONLY
IMPLEMENTATION_AUTHORIZED: YES_FOR_AUTHORIZED_2F_06_SCOPE_ONLY
PHASE_2F_06_STATUS: UNBLOCKED_FOR_AUTHORIZED_SCOPE_ONLY
FORBIDDEN_SCOPE_TOUCHED: NO
IMPLEMENTATION_ADDED: NO
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
```
