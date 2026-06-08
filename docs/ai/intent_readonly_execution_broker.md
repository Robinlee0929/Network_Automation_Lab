# Day80 Read-only Execution Broker Skeleton

Day80 follows Day79 by adding a deterministic skeleton for a future read-only
execution broker. Day79 defines the read-only task contract and allowlist;
Day80 shows how future read-only requests could be received, checked, rejected,
queued for review, or converted into mock execution request data.

This is not a real execution broker. It is a review artifact and report
generator only.

## Runner

```bash
python network_lab.py --task readonly-execution-broker
```

Generated reports:

- `reports/lab-summary/day80_readonly_execution_broker.json`
- `reports/lab-summary/day80_readonly_execution_broker.html`

## Broker Lifecycle

1. Receive a fixed mock request.
2. Validate the requested task against the Day79 read-only task contract.
3. Compare the result with the read-only allowlist.
4. Reject unsupported, write/config-changing, or unsafe requests.
5. Queue read-only requests that still need manual review.
6. Prepare mock execution request data for a valid read-only request.
7. Produce reviewer evidence.

## Broker Statuses

- `RECEIVED`
- `REJECTED`
- `QUEUED_FOR_REVIEW`
- `MOCK_EXECUTION_REQUEST_PREPARED`

`MOCK_EXECUTION_REQUEST_PREPARED` means a data object was prepared. It does not
mean a command, mapped task, SSH session, or device connection was started.

## Safety Boundary

Day80 intentionally does not add:

- SSH
- device access
- command execution
- live command execution
- router, switch, firewall, VPN, VRRP, interface, route, NAT, or IP changes
- OpenAI API or AI SDK integration
- mapped task execution
- `config.json` dependency
- dashboard forms
- dashboard POST routes
- dashboard action endpoints
- approval unlock
- execution control

Every broker record keeps:

- `allowed_to_execute = False`
- `dry_run_only = True`
- `execution_unlock_supported = False`
- `device_connection_allowed = False`
- `ssh_allowed = False`
- `live_command_allowed = False`

## Relationship to Day79

Day79 answers: "Is this task category a read-only candidate, blocked write
action, destructive action, unknown task, or manual-classification case?"

Day80 answers: "Given a fixed mock request and that Day79 contract result, what
broker-shaped review record would be produced?"

The answer remains review-only. Read-only eligibility is not permission to run
anything.
