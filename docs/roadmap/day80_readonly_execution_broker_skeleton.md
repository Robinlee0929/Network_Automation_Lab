# Day80 Read-only Execution Broker Skeleton

Day80 adds a deterministic read-only execution broker skeleton after the Day79
read-only task contract and allowlist.

## Scope

Implemented:

- `intent_readonly_execution_broker.py`
- `python network_lab.py --task readonly-execution-broker`
- JSON and HTML reports under `reports/lab-summary/`
- static `/ai-intent-reviewer` dashboard visibility
- tests for deterministic output, runner registration, report generation,
  dashboard visibility, and locked safety invariants

Generated reports:

```text
reports/lab-summary/day80_readonly_execution_broker.json
reports/lab-summary/day80_readonly_execution_broker.html
```

## Why Day80 Follows Day79

Day79 defines the contract layer: read-only candidates, blocked write actions,
destructive actions, unknown tasks, and manual classification cases.

Day80 builds the next non-executing layer. It models how a future broker would
receive a request, check the Day79 contract, reject unsafe requests, queue
review-only requests, or prepare mock execution request data.

## What Day80 Does

- Produces deterministic broker request records.
- Produces deterministic broker decision records.
- Uses Day79 read-only contract logic.
- Includes at least five fixed mock requests:
  - valid read-only request prepared as mock data
  - valid read-only request queued for manual review
  - unsupported task rejected
  - write/config-changing task rejected
  - ambiguous natural-language request queued for review
- Writes reviewer JSON and HTML reports.

## What Day80 Does Not Do

Day80 does not add SSH, device access, command execution, live command
execution, OpenAI API calls, AI SDK integration, mapped task execution,
dashboard forms, POST routes, action endpoints, approval unlock, execution
control, or network/device configuration changes.

## Safety Invariants

Every broker record preserves:

```text
allowed_to_execute = False
dry_run_only = True
execution_unlock_supported = False
device_connection_allowed = False
ssh_allowed = False
live_command_allowed = False
```

## Validation

Recommended validation:

```bash
python -m pytest
python network_lab.py --task readonly-execution-broker
python network_lab.py --task readonly-task-contract
python network_lab.py --task report-index
```

Expected result: tests pass, Day80 returns `PASS / REVIEW_READY`, and the
summary confirms no live command was executed, no mapped task was executed, no
device was accessed, and no execution unlock occurred.
