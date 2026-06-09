# Day84 Read-only Executor Adapter Interface Contract

## Goal

Define the future read-only executor adapter input/output contract without implementing the executor or adapter.

Day84 is the contract-only boundary after the Day83 readiness gate. It creates deterministic reviewer evidence for what a future adapter must look like, while keeping every execution path locked.

## Scope

Implemented:

- Deterministic module: `intent_readonly_executor_adapter_contract.py`
- Runner task: `python network_lab.py --task readonly-executor-adapter-contract`
- JSON report: `reports/lab-summary/day84_readonly_executor_adapter_contract.json`
- HTML report: `reports/lab-summary/day84_readonly_executor_adapter_contract.html`
- Static report visibility metadata and task catalog entry
- Tests for deterministic output, runner integration, report generation, locked flags, unsafe capability rejection, and forbidden runtime imports

Not implemented:

- executor runtime
- adapter runtime
- device transport
- SSH
- live command execution
- AI API or AI SDK runtime
- approval or execution unlock
- dashboard action endpoint
- mapped task execution

## Contract Shapes

Day84 defines these shapes:

- adapter request shape
- adapter response shape
- adapter capability declaration shape
- adapter evidence/reference shape
- adapter safety flags
- validation result shape

The shapes are deterministic fixtures for review. They are not executable objects and they do not contain a runnable entrypoint or implementation module.

## Required Passing State

The expected passing state is:

```json
{
  "overall_status": "PASS",
  "reviewer_status": "REVIEW_READY",
  "contract_state": "LOCKED_REVIEW_ONLY_CONTRACT",
  "read_only_only": true,
  "dry_run_only": true,
  "allowed_to_execute": false,
  "ssh_allowed": false,
  "device_access_allowed": false,
  "live_command_allowed": false,
  "approval_unlock_supported": false,
  "execution_unlock_supported": false,
  "ai_api_allowed": false,
  "adapter_implementation_present": false
}
```

## Validation Rules

Day84 validation checks:

- request, response, capability, evidence, and validation result shapes are present
- `read_only_only` and `dry_run_only` remain true
- execution, SSH, device, live command, AI API, approval unlock, execution unlock, and implementation flags remain false
- request target address, credentials reference, command text, and raw device command remain null
- response execution result and device session remain null
- response command execution list remains empty
- capability declaration exposes no SSH/device/live transport
- capability declaration has no runnable entrypoint or implementation module

Unsafe capability declarations are rejected by the contract validator.

## Relationship To Day80-Day83

Day80 defines a non-executing broker skeleton and mock request data.

Day81 turns broker records into reviewer queue and decision state evidence.

Day82 exports traceable audit evidence for reviewer decisions.

Day83 verifies that the Day79-Day82 chain is ready for future read-only adapter design review only.

Day84 defines the interface contract that any future read-only adapter proposal must satisfy. It does not convert readiness into execution permission.

## Reviewer Acceptance Criteria

Accept Day84 only if:

- `python -m pytest` passes
- `python network_lab.py --task report-index` has zero failures
- `python network_lab.py --task readonly-executor-adapter-contract` exits 0
- reports are written under `reports/lab-summary/`
- JSON shows `contract_state: LOCKED_REVIEW_ONLY_CONTRACT`
- HTML is static and contains no form, button, script, POST route, or action endpoint
- all required true and false safety invariants match the locked state
- no SSH, device access, live command, real executor implementation, AI API, approval unlock, or execution unlock is added

## Safety Boundary

Day84 is complete only while it remains contract-only. Any future executor implementation must be proposed, reviewed, and tested as a separate day with a separate safety gate.
