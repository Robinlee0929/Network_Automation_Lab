# Day79 Read-only Task Contract & Allowlist

## Objective

Create a deterministic, standard-library-only, mock-only, dry-run-only
read-only task contract layer. The layer defines which future AI-requested tasks
may be considered read-only candidates, which tasks are blocked write actions,
which tasks are destructive and always forbidden, and which tasks need manual
classification.

Day79 is not an execution broker and not an SSH implementation.

```text
Day72-Day78 = AI runtime safety chain
Day79 = read-only task allowlist / capability definition layer
```

## Implementation

Files:

```text
intent_readonly_task_contract.py
network_lab.py
dashboard_app.py
templates/dashboard_ai_intent_reviewer.html
docs/ai/intent_readonly_task_contract.md
docs/roadmap/day79_readonly_task_contract.md
tests/test_intent_readonly_task_contract.py
```

Runner command:

```bash
python network_lab.py --task readonly-task-contract
```

Reports:

```text
reports/lab-summary/day79_readonly_task_contract.json
reports/lab-summary/day79_readonly_task_contract.html
```

## Scope

Day79 creates at least five deterministic contract records covering:

1. read-only eligible task
2. blocked write action
3. destructive action
4. unknown task
5. manual classification case

Every record keeps:

```text
allowed_to_execute = False
dry_run_only = True
execution_unlock_supported = False
```

## Categories

Read-only candidates:

- `show_interface_status`
- `show_ip_address`
- `show_route_table`
- `show_wireguard_peer_status`
- `show_system_resource`
- `show_log_summary`
- `ping_readonly_probe`
- `iperf3_report_review`

Blocked write actions:

- `set_ip_address`
- `add_firewall_rule`
- `remove_firewall_rule`
- `enable_interface`
- `disable_interface`
- `create_wireguard_peer`
- `modify_vrrp_priority`
- `apply_config`

Destructive actions:

- `reset_configuration`
- `reboot_device`
- `factory_reset`
- `delete_interface`
- `remove_firewall_rules`
- `wipe_config`

Unknown/manual classification:

- `unknown`
- `unsupported`
- `needs_manual_classification`

## Safety Boundary

Day79 must not enable real execution:

- no OpenAI API
- no AI SDK
- no SSH
- no device access
- no live execution
- no mapped task execution
- no approval unlock
- no dashboard action surface
- no router, switch, firewall, VPN, VRRP, or network configuration change
- no `config.json` dependency
- no merge
- no push
- no tag

## Dashboard

The AI intent reviewer dashboard shows static/read-only Day79 visibility:

- Day79 title
- short description
- link to Day79 AI doc
- link to Day79 roadmap doc
- link to JSON report path
- link to HTML report path
- safety notes for deterministic, mock-only, dry-run-only, no SSH, no device
  access, no execution unlock, and no dashboard action surface

The dashboard does not add forms, POST routes, buttons, action endpoints, task
triggers, or JavaScript hooks for Day79.

## Validation

```bash
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
python network_lab.py --task offline-mock-runtime
python network_lab.py --task offline-mock-runtime-contract
python network_lab.py --task offline-mock-runtime-review
python network_lab.py --task mock-ai-decision-pipeline
python network_lab.py --task dry-run-plan-builder
python network_lab.py --task manual-review-approval-envelope
python network_lab.py --task runtime-audit-trail
python network_lab.py --task runtime-safety-gate
python network_lab.py --task runtime-safety-case
python network_lab.py --task readonly-task-contract
git status --short --branch
```

Expected Day79 console result:

```text
Day79 Controlled Read-only Task Contract & Allowlist
Safety: deterministic mock-only / dry-run-only task eligibility contract
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

No future step is automatically authorized by Day79.
