# Day86 Controlled Runner Harness

Day86 adds a deterministic controlled runner harness for runner-level safety regression.

It consumes Day85-style adapter compatibility, blocked adapter, and evidence binding signals, then verifies that the runner still cannot execute anything live. Adapter compatibility and report generation are treated as reviewer evidence only.

## Relation to Day85

Day85 is Mock Adapter + Evidence Binding. It proves that mock adapter responses can conform to the Day84 contract and remain bound to request, adapter, contract, evidence, and reviewer decision fields.

Day86 does not add adapter features. It raises those signals into the runner layer and checks that the runner keeps the same safety boundary even when:

- an adapter is compatible
- report output is requested
- a blocked adapter appears
- compatibility mismatches occur
- evidence binding is incomplete
- unsafe execution flags are requested

## Safety Invariants

Every Day86 scenario must keep:

- `dry_run_only = true`
- `allowed_to_execute = false`
- `ssh_allowed = false`
- `live_command_allowed = false`
- `mapped_task_executed = false`
- `execution_unlock_supported = false`
- `final_recommendation = REVIEW_ONLY`

Compatible adapters may produce review-ready report output, but compatibility is not execution approval.

## Runner-Level Regression Behavior

The `controlled-runner-harness` task writes deterministic JSON and HTML reports. It does not load lab profiles, read `config.json`, open SSH, connect to devices, call APIs, execute mapped tasks, or run subprocess-backed lab commands.

The runner scenarios cover:

1. compatible mock adapter with complete evidence binding
2. compatible adapter with report output requested
3. blocked adapter attempt
4. adapter compatibility mismatch
5. missing or incomplete evidence binding
6. unsafe execution flag regression attempt

Expected conclusion:

```text
PASS / REVIEW_ONLY
```

## Report Paths

```text
reports/lab-summary/day86_controlled_runner_harness.json
reports/lab-summary/day86_controlled_runner_harness.html
```

## Non-Goals

Day86 does not add:

- adapter implementation changes
- SSH
- device access
- live command execution
- mapped task execution
- OpenAI API or SDK calls
- dashboard forms, POST routes, buttons, or action endpoints
- approval unlocks or execution unlocks
- network or device configuration changes
