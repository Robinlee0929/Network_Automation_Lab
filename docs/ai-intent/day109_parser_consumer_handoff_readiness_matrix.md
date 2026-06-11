# Day109 Parser Consumer Handoff Readiness Matrix

## Purpose

Day109 converts Day108 parser contract consumer handoff records into a reviewer-facing readiness matrix. Each row is classified as `READY`, `NEEDS_CLARIFICATION`, or `BLOCKED` so reviewers can see whether a parser handoff can be interpreted safely without live execution.

This is `REVIEW_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE` evidence. It does not call adapters, brokers, SSH, network devices, OpenAI APIs, external APIs, command runners, or mapped task execution paths.

## Inputs from Day108

The matrix consumes the deterministic Day108 handoff record structure produced by `intent_parser_contract_consumer_handoff.py`.

The default source is:

- `parser-contract-consumer-handoff`
- `reports/lab-summary/day108_parser_contract_consumer_handoff.json`
- Day108 handoff fields such as `handoff_id`, `reviewer_decision`, `evidence_status`, `handoff_ready`, `handoff_blockers`, `safety_flags`, and `next_stage_recommendation`

## Readiness Classification Rules

`READY` means the row has a consumer identity, evidence references, required consumer actions, no blocking reasons, no clarification items, and all unsafe, live, SSH, write, command execution, and mapped task execution flags are false.

`NEEDS_CLARIFICATION` means no blocking condition is present, but the row still needs reviewer interpretation. Examples include missing required consumer actions, a Day108 clarification status, or a handoff that is not ready but is not unsafe.

`BLOCKED` means at least one blocking condition is present. Blocked rows must preserve at least one blocking reason and must never be rewritten as ready.

## Blocking Safety Flags

The following flags are blocking when true:

- `unsafe_flag`
- `live_flag`
- `ssh_flag`
- `write_flag`
- `command_execution_flag`
- `mapped_task_execution_flag`

Rows are also blocked when the consumer identity or handoff evidence is missing, or when the source handoff is explicitly marked unsafe, rejected, blocked, or unavailable for delivery.

## Reviewer Interpretation Guide

Reviewers should use `READY` rows as report-only handoff evidence. `NEEDS_CLARIFICATION` rows should be resolved by human review before the consumer contract is treated as complete. `BLOCKED` rows indicate preserved safety boundaries and must not be used to unlock execution.

The report may still return `overall_status: PASS` when blocked rows exist because the task validates classification accuracy, not readiness for execution. When blocked records or safety flags are present, `reviewer_status` becomes `BLOCKED_RECORDS_PRESENT`.

## Non-goals

Day109 does not add parser capability, broker handoff approval, adapter invocation, live read access, SSH, write/configuration changes, command execution, mapped task execution, OpenAI API use, voice input, cloud execution, or credential-dependent workflows.

## Evidence Outputs

Run:

```powershell
python network_lab.py --task parser-consumer-handoff-readiness-matrix
```

Outputs:

- `reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.json`
- `reports/lab-summary/day109_parser_consumer_handoff_readiness_matrix.html`

The HTML report includes a summary table, readiness counts, per-record readiness matrix, blocking reasons, clarification items, safety flags, evidence references, and the explicit `REVIEW_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE` labels.
