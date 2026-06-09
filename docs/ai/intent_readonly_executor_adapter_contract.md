# Read-only Executor Adapter Interface Contract

Day84 defines the future read-only executor adapter interface contract only.

It is a contract-only boundary. It does not implement an executor, implement an adapter, open SSH, connect to devices, run live commands, call an AI API, unlock approval, unlock execution, or add dashboard actions.

## Purpose

Day83 marked the Day79-Day82 evidence chain as ready for future adapter design review. Day84 takes the next smallest step: it names the interface objects a future read-only executor adapter would have to satisfy.

The contract defines:

- adapter request shape
- adapter response shape
- adapter capability declaration shape
- adapter evidence/reference shape
- adapter safety flags
- validation result shape
- deterministic example fixtures

The fixtures are examples for reviewer inspection. They are not executable objects.

## Locked Invariants

The Day84 contract requires:

```json
{
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

Additional flags also remain false for device connection, live execution, mapped task execution, dashboard action, network change, subprocess use, runnable entrypoints, runtime transports, and config dependency.

## Request Contract

The request shape is a structured future adapter input. It contains a request id, contract version, requested task, source reference, target scope, input payload, safety flags, and evidence references.

The request shape deliberately keeps these fields null:

- target address
- credentials reference
- command text
- raw device command

This lets reviewers see the intended input boundary without creating a path to a real device.

## Response Contract

The response shape is a structured future adapter output. It contains a response id, request id, response status, output contract, safety flags, and evidence references.

The response shape deliberately keeps:

- `execution_result: null`
- `commands_executed: []`
- `device_session: null`

This proves Day84 does not record or imply live execution.

## Capability Declaration

The capability declaration is contract-only:

- `capability_kind: interface_contract_only`
- `supported_transports: ["none_contract_only"]`
- `runnable_entrypoint: null`
- `implementation_module: null`

Validation rejects unsafe declarations that add SSH/device transports, runnable entrypoints, implementation modules, live command flags, device access flags, AI API permission, approval unlock, execution unlock, or adapter implementation presence.

## Connection To Day80-Day83

Day80 introduced non-executing broker records and mock request data.

Day81 made those records reviewer-facing through queue and decision state evidence.

Day82 exported traceable reviewer audit evidence.

Day83 validated the chain as ready for future read-only adapter design review only.

Day84 does not move from review into execution. It only defines the contract a future adapter would need to satisfy before any separate implementation proposal exists.

## Runner

Run:

```bash
python network_lab.py --task readonly-executor-adapter-contract
```

Reports:

- `reports/lab-summary/day84_readonly_executor_adapter_contract.json`
- `reports/lab-summary/day84_readonly_executor_adapter_contract.html`

The HTML report is static and reviewer-facing. It contains no forms, POST actions, execution buttons, scripts, or live endpoints.
