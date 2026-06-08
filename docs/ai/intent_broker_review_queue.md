# Day81 Read-only Broker Review Queue & Decision State Report

Day81 exists after Day80 to make the broker skeleton easier to review. Day80
records whether fixed mock requests are rejected, queued for review, or prepared
as mock request data. Day81 transforms those broker records into a reviewer
queue with stable review states and decision states.

## What Problem It Solves

The Day80 broker skeleton is intentionally low-level evidence. It shows broker
status, contract checks, and mock request data, but a reviewer still needs a
clear queue view. Day81 adds that queue view without changing broker behavior.

Each queue record explains:

- the Day80 source request
- the broker status
- the reviewer-facing review state
- the decision state
- the reason the record needs review
- the safety boundary that prevents execution
- the evidence chain back to Day79 and Day80

## How Day81 Differs From Day80

Day80 is the broker skeleton. It models fixed mock request handling after the
Day79 read-only task contract.

Day81 is the review queue layer. It does not receive new live requests and does
not run tasks. It reads deterministic Day80 broker records and assigns queue
state for reviewer reporting only.

## Review And Decision States

Day81 uses five deterministic review states:

- `REJECTED_BY_BROKER`
- `QUEUED_FOR_HUMAN_REVIEW`
- `MOCK_EXECUTION_REQUEST_PREPARED`
- `REVIEW_BLOCKED_BY_POLICY`
- `REVIEW_READY_NO_EXECUTION`

Day81 uses five deterministic decision states:

- `REJECT`
- `HOLD_FOR_REVIEW`
- `MOCK_ONLY`
- `POLICY_BLOCKED`
- `REVIEW_ONLY`

These states describe reviewer posture only. They do not approve execution.

## Why No Execution Is Possible

Day81 has no SSH code, no device access, no OpenAI API, no AI SDK runtime, no
voice integration, no command runner, no mapped task execution, no dashboard
form, no POST route, and no action endpoint. It writes only local JSON and HTML
reports.

Every queue record keeps these invariants:

- `allowed_to_execute == False`
- `dry_run_only == True`
- `execution_unlock_supported == False`
- `device_connection_allowed == False`
- `ssh_allowed == False`
- `live_command_allowed == False`
- `mapped_task_execution_allowed == False`
- `dashboard_action_allowed == False`
- `report_only == True`

## Run The Report

```powershell
python network_lab.py --task broker-review-queue
```

Expected result:

- `PASS / REVIEW_READY`
- 5 queue records
- allowed-to-execute values: `[False]`
- dry-run-only values: `[True]`
- execution unlock supported values: `[False]`
- SSH/device/live command/mapped task/dashboard action values: `[False]`

Report paths:

- `reports/lab-summary/day81_broker_review_queue.json`
- `reports/lab-summary/day81_broker_review_queue.html`
