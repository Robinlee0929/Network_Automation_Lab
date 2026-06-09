# Day89 Real Adapter Safety Boundary Spec

Day89 locks the safety boundary before any future real adapter implementation.
This is a `DESIGN_ONLY` day.

## Scope

- Add deterministic Day89 JSON/HTML reports under `reports/lab-summary/`.
- Add runner task `real-adapter-safety-boundary-spec`.
- Make the Day89 report visible in report-index/dashboard paths.
- Add tests for deterministic output, locked safety flags, blocked destructive
  capabilities, static dashboard visibility, and absence of live adapter
  dependencies.

## Non-Scope

- No real SSH adapter.
- No RouterOS connection.
- No live read-only command execution.
- No arbitrary command executor.
- No device configuration changes.
- No dashboard live action button or command execution control.

## Acceptance

- Report has `day=89`, `phase=DESIGN_ONLY`, `status=PASS`, and
  `safety_boundary_locked=true`.
- `implementation_allowed=false`, `live_device_access_allowed=false`,
  `ssh_allowed=false`, `config_change_allowed=false`, and
  `command_execution_allowed=false`.
- Blocked capabilities include destructive/write actions and fallback to
  non-allowlisted commands.
- Allowed capabilities stay spec-level only and include no live implementation.
- Runner prints `PASS / DESIGN_ONLY`, `safety_boundary_locked=True`,
  `implementation_allowed=False`, and `live_device_access_allowed=False`.
- Report-index may warn about optional missing reports, but must not fail due to
  Day89.

## Day90 Handoff

Day90 may plan implementation only if Day89 remains satisfied. Future
implementation must remain read-only, allowlisted, reviewer-gated,
evidence-producing, redaction-safe, and fail-closed.
