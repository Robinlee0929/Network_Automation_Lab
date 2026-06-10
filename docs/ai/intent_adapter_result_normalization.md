# Day95 Adapter Result Normalization / Fake Adapter Evidence Hardening

Day95 exists to make fake adapter output predictable before parser work begins. Day93 proved that guard-approved scenarios are the only scenarios that may enter the fake adapter boundary. Day94 expanded that proof into regression matrix coverage. Day95 takes the next step by normalizing the fake adapter result into one stable schema.

This remains fake-only, deterministic-only, read-only, and report-only. It does not introduce OpenAI API calls, AI SDK runtime, voice input, SSH, RouterOS connections, device access, live command execution, real adapter invocation, mapped task execution, dashboard actions, POST routes, approval mechanisms, or execution unlocks.

## Normalized Fake Adapter Result

A normalized fake adapter result is a deterministic record created only after:

1. The scenario guard returns `ALLOW`.
2. The fake adapter boundary is invoked.
3. The fake boundary returns the deterministic status `FAKE_RESULT_READY`.

Rejected scenarios stop before the fake adapter boundary. Their `adapter_result` is `None`, no result payload is produced, and they are listed in rejection evidence only.

## Schema Guarantees

Every allowed fake adapter result uses `schema_version` `day95.adapter_result.v1` and `result_kind` `normalized_fake_adapter_result`.

The normalized record guarantees:

- `adapter_type` is always `fake`.
- `source_boundary` is always `guarded_fake_adapter_boundary`.
- `guard_decision` is always `ALLOW`.
- `adapter_invoked` is always `true`.
- `result_status` comes only from the deterministic fake boundary.
- `result_payload` is parser-ready but not parsed yet.
- `real_adapter_result_present`, `live_execution_result_present`, `ssh_used`, `device_access_used`, and `execution_unlocked` are always `false`.
- Evidence references Day93, Day94, and the Day95 normalization step.

## Why Rejected Scenarios Have No Adapter Result

The Day95 contract intentionally treats rejected scenarios as evidence of absence. A rejected write-capable, live-capable, or ambiguous request must not produce an adapter response shape that future code could accidentally treat as executable output. This keeps the boundary fail-closed: rejected scenarios have no adapter invocation, no adapter result, no payload, and no parser-ready output.

## Real And Live Results Are Absent

Day95 creates no real adapter object and no live execution path. The only result source is the deterministic fake adapter boundary. Real adapter result count and live execution result count are both fixed at zero in the report summary and validation checks.

## Preparation For Day96

Day96 can prototype read-only output parsing against a fixed fake result envelope instead of inventing its own input schema. Day95 deliberately stops before parsing; it only guarantees that future parser code receives a stable `result_payload` containing `command_family`, `readonly_intent`, `simulated_output`, and `parser_ready`.

## Safety Boundaries

- Fake-only
- Deterministic-only
- Report-only
- Read-only dashboard visibility only
- No OpenAI API
- No AI SDK runtime
- No voice
- No SSH
- No RouterOS connection
- No device access
- No live command execution
- No real adapter invocation
- No mapped task execution
- No dashboard action
- No POST route
- No approval or execution unlock
