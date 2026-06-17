# Next-Phase Authorization Criteria Pack

This document records reviewer-facing criteria for future next-phase
authorization. It is documentation only. It does not authorize Phase 2A-07,
does not authorize Phase 2B, and does not change runtime behavior.

Do not add CLI task, report renderer, or runtime behavior for this pack.

## Current Locked State

Status record:

- Phase 2A-06: completed
- Phase 2A-07: not authorized
- Phase 2B: not authorized
- next_phase_allowed: false
- Final lock verdict: NEXT_PHASE_LOCK_CONFIRMED

The current lock remains in force. `NEXT_PHASE_AUTHORIZATION_CRITERIA_PACK_READY`
means only that this authorization criteria document is ready for review. It
does not authorize Phase 2A-07, does not authorize Phase 2B, and does not
change `next_phase_allowed`.

## Phase 2A-07 Authorization Criteria

Before Phase 2A-07 can start, the project owner must review and explicitly
approve:

- the exact Phase 2A-07 scope and non-scope
- whether Phase 2A-07 is planning only or implementation
- the safety boundaries that remain false
- the reviewer evidence expected from the phase
- the stop conditions that apply to the phase
- the files or documentation areas allowed to change
- any test or validation expectations for the phase
- confirmation that Phase 2A-07 still does not imply Phase 2B authorization

This section defines criteria only. It does not authorize Phase 2A-07 and does
not implement Phase 2A-07.

## Phase 2B Authorization Criteria

Before Phase 2B can start, the project owner must review and explicitly
approve:

- the exact Phase 2B scope and non-scope
- whether Phase 2B is planning only or implementation
- any proposed change to execution, runner, adapter, broker, provider, API,
  model, SSH, NETCONF, RESTCONF, or live device boundaries
- the safety gate that would permit any newly proposed capability
- the reviewer evidence required before, during, and after the phase
- the negative tests required to prove rejected scenarios do not reach execution
- the rollback or stop process if a proposed capability exceeds approval
- confirmation that no implied approval from prior phases carries into Phase 2B

This section defines criteria only. It does not authorize Phase 2B and does not
implement Phase 2B.

## Permanent Safety Boundaries

The following boundaries must remain false unless explicitly authorized in a
future phase:

- execution: false
- provider/API/model calls: false
- SSH: false
- NETCONF: false
- RESTCONF: false
- live device access: false
- adapter: false
- broker: false
- runner: false
- secrets: false

No preparation work may change these values, introduce a code path that behaves
as if they were true, or add a hidden runtime path that bypasses reviewer
visibility.

## Allowed Preparation Work

Before explicit next-phase authorization, the following preparation work is
allowed:

- documentation review
- checklist refinement
- risk review
- terminology cleanup
- owner approval wording review
- reviewer-facing status wording review
- traceability review of existing evidence references

These preparation items must not change runtime behavior. They must not add a
CLI task, report renderer, runner, adapter, broker, provider/API/model call,
SSH path, NETCONF path, RESTCONF path, live device access path, secret, or
safety gate change.

## Human Authorization Format

Only the following exact project-owner statements can authorize next-phase work:

- `I authorize Phase 2A-07 planning only`
- `I authorize Phase 2A-07 implementation`
- `I authorize Phase 2B planning only`
- `I authorize Phase 2B implementation`

Unclear, partial, implied, conversational, or retrospective approval is not
enough. Approval for planning only does not authorize implementation. Approval
for Phase 2A-07 does not authorize Phase 2B. Approval for documentation does not
authorize runtime behavior.

## Stop Conditions

Codex must stop if:

- `AGENTS.md` was not read before changes
- the task would enable execution
- the task would enable provider/API/model calls
- the task would enable SSH or live device access
- the task would add adapter, broker, or runner behavior
- the task would add secrets
- the task would change safety gates
- the task would implement Phase 2A-07 without explicit authorization
- the task would implement Phase 2B without explicit authorization
- the task would change `next_phase_allowed` from false to true
- the task would add a CLI task, report renderer, or runtime behavior for this
  criteria pack

## Final Lock Statement

Phase 2A-06: closed
Next-phase criteria: documented
Phase 2A-07: still not authorized
Phase 2B: still not authorized
next_phase_allowed: false

Final verdict for this document only:
NEXT_PHASE_AUTHORIZATION_CRITERIA_PACK_READY
