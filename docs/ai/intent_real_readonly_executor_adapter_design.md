# Day88 Real Read-only Executor Adapter Design Draft

Day88 is a deterministic design draft for a future real read-only executor adapter. It does not implement SSH, RouterOS connectivity, live command support, dashboard action controls, or execution unlocks.

## Scope

- Define the future adapter architecture boundary.
- Define a positive command allowlist design.
- Define evidence, error, timeout, and denial contracts.
- Define a safety boundary for later implementation review.
- Produce JSON/HTML reports for reviewer visibility.

## Non-goals

- Do not redo Day87.
- Do not implement a real adapter.
- Do not connect to RouterOS.
- Do not open SSH or any device transport.
- Do not run live commands.
- Do not add dashboard action controls or API endpoints.
- Do not add Paramiko, Netmiko, RouterOS client, OpenAI, AI SDK, voice, or transport dependencies.

## Adapter Architecture Draft

Day88 defines these future design concepts as contract data only:

- `ReadOnlyAdapterRequest`
- `ReadOnlyAdapterResponse`
- `ReadOnlyCommandSpec`
- `ReadOnlyEvidenceRecord`
- `ReadOnlyErrorRecord`
- `ReadOnlyTimeoutPolicy`
- `ReadOnlyPolicyDecision`

The adapter state for Day88 is `ADAPTER_NOT_IMPLEMENTED`. The phase state is `DESIGN_ONLY`.

## Command Allowlist Design

The allowlist is a positive allowlist, not a blacklist. Future command text must be normalized before policy comparison. Unlisted commands are denied by default. Commands containing mutation tokens are denied even when they resemble read-only commands.

Design examples only:

- `/system/resource/print`
- `/system/identity/print`
- `/interface/print`
- `/ip/address/print`
- `/ip/route/print`
- `/interface/vrrp/print`

`export` is intentionally excluded because it may disclose sensitive configuration.

Forbidden mutation tokens include `add`, `set`, `remove`, `enable`, `disable`, `reboot`, `reset-configuration`, `import`, `export`, `password`, `secret`, `certificate`, `user`, `tool`, `fetch`, `script`, and `scheduler`.

## Evidence Contract

The future evidence record must include:

- `request_id`
- `adapter_name`
- `device_alias`
- `command_spec_id`
- `normalized_command`
- `policy_decision`
- `started_at`
- `completed_at`
- `duration_ms`
- `stdout_digest`
- `stderr_digest`
- `raw_output_redacted`
- `redaction_applied`
- `timeout_applied`
- `error_code`
- `error_message`
- `correlation_id`

Day88 does not collect stdout or stderr. The example evidence record marks raw output as `NOT_COLLECTED_DESIGN_ONLY_EXAMPLE_ONLY`.

## Error Contract

The error contract defines:

- `POLICY_DENIED`
- `COMMAND_NOT_ALLOWLISTED`
- `MUTATION_TOKEN_DETECTED`
- `TIMEOUT`
- `CONNECTION_UNAVAILABLE`
- `AUTH_UNAVAILABLE`
- `ADAPTER_NOT_IMPLEMENTED`
- `OUTPUT_REDACTION_REQUIRED`
- `UNKNOWN_ERROR`

Day88's current state is `ADAPTER_NOT_IMPLEMENTED / DESIGN_ONLY`.

## Timeout Contract

- `default_timeout_seconds`: 10
- `max_timeout_seconds`: 30
- `retry_supported`: false
- `retry_count`: 0
- `timeout_result_status`: `TIMEOUT`

Retries remain disabled in the initial design to avoid repeated observation against a device in a future adapter.

## Safety Boundary

- `execution_supported = False`
- `ssh_supported = False`
- `routeros_connection_supported = False`
- `live_command_supported = False`
- `execution_unlock_supported = False`
- `dashboard_execute_button_supported = False`

Day88 does not unlock real read-only execution. Day88 only defines the contract for a future adapter.

## Future Implementation Checklist

- Write Day89 Real Adapter Safety Boundary Spec.
- Keep adapter disabled until a later explicit implementation gate.
- Validate positive allowlist and mutation token denial before any transport boundary.
- Require reviewer approval envelope for every future adapter request.
- Add output redaction and digest-only evidence storage before raw output handling.
- Add deterministic timeout handling with `retry_supported = False` for first implementation.
- Prove dashboard remains report-view only.
