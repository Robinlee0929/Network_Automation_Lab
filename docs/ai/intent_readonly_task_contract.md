# Day79 Controlled Read-only Task Contract & Allowlist

Day79 adds a deterministic read-only task contract layer for future AI-requested
network tasks. It does not run tasks. It defines which requested task categories
may later be considered read-only candidates, which categories are blocked write
actions, which categories are destructive and always forbidden, and which
requests need manual classification.

Clear distinction:

```text
Day72-Day78 = AI runtime safety chain
Day79 = read-only task allowlist / capability definition layer
```

Day79 does not repeat Day72-Day78. The earlier chain validates controlled input,
generates mock decisions, builds dry-run plans, records manual review envelopes,
creates audit evidence, locks the runtime safety gate, and packages the final
REVIEW_ONLY safety case. Day79 starts the next layer by defining a read-only task
taxonomy. It is a capability definition layer only.

## Task

```bash
python network_lab.py --task readonly-task-contract
```

Generated report paths:

- `reports/lab-summary/day79_readonly_task_contract.json`
- `reports/lab-summary/day79_readonly_task_contract.html`

## Contract Concept

Each contract record includes:

- `contract_id`
- `scenario_id`
- `intent_id`
- `requested_task`
- `task_category`
- `readonly_eligible`
- `execution_candidate`
- `requires_human_approval`
- `allowed_command_refs`
- `blocked_command_patterns`
- `device_scope`
- `policy_reason`
- `safety_invariants`
- `contract_result`
- `allowed_to_execute`
- `dry_run_only`
- `execution_unlock_supported`
- `created_at`

Read-only eligibility is not permission to run anything. Every record keeps:

```text
allowed_to_execute = False
dry_run_only = True
execution_unlock_supported = False
```

## Allowlist Categories

Read-only candidate categories:

- `show_interface_status`
- `show_ip_address`
- `show_route_table`
- `show_wireguard_peer_status`
- `show_system_resource`
- `show_log_summary`
- `ping_readonly_probe`
- `iperf3_report_review`

These are candidates for future read-only review only. Day79 does not open SSH,
does not contact devices, and does not execute mapped tasks.

## Blocked Write Actions

Blocked write categories:

- `set_ip_address`
- `add_firewall_rule`
- `remove_firewall_rule`
- `enable_interface`
- `disable_interface`
- `create_wireguard_peer`
- `modify_vrrp_priority`
- `apply_config`

These can change router, switch, firewall, VPN, interface, route, address, or
VRRP state and are blocked by the read-only contract.

## Destructive Actions

Destructive categories:

- `reset_configuration`
- `reboot_device`
- `factory_reset`
- `delete_interface`
- `remove_firewall_rules`
- `wipe_config`

These are always forbidden by Day79.

## Unknown and Manual Cases

Unknown or unsupported categories:

- `unknown`
- `unsupported`
- `needs_manual_classification`

Unknown tasks produce `UNKNOWN_TASK` or `NEEDS_MANUAL_CLASSIFICATION` and remain
outside the read-only allowlist.

## Result Values

Day79 records use these deterministic results:

- `READONLY_CONTRACT_READY`
- `BLOCKED_WRITE_ACTION`
- `BLOCKED_DESTRUCTIVE_ACTION`
- `UNKNOWN_TASK`
- `NEEDS_MANUAL_CLASSIFICATION`

## Safety Boundary

Day79 preserves the current safety boundary:

- no OpenAI API
- no AI SDK
- no SSH
- no device access
- no live execution
- no mapped task execution
- no approval unlock
- no dashboard action surface
- no network configuration changes
- no `config.json` dependency

## Validation

```bash
python -m pytest
python network_lab.py --task readonly-task-contract
```

Expected summary:

```text
Overall status: PASS / REVIEW_READY
Contract records: 5
Read-only eligible values: [False, True]
Execution candidate values: [False, True]
Allowed to execute values: [False]
Dry-run-only values: [True]
Execution unlock supported values: [False]
```

## Future Path

- Day80 Read-only Execution Broker Skeleton
- Day81 Mock Read-only Execution Result Package
- Day82 Read-only SSH Precheck Readiness Review
- Day83 Real read-only SSH precheck for lab devices, only after explicit review
- Day84+ human-approved low-risk apply prototype, only after later review

Day79 does not claim real AI execution, real SSH, or real device control.
