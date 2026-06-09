# Day91 Real Adapter Safety Scaffold

## Decision

Day91 is `SCAFFOLD_ONLY`. It follows Day90 `CONDITIONAL_GO` by creating a deterministic safety scaffold and evidence chain only.

Day91 is not a real adapter implementation and not a read-only prototype.

## Goal

Prove dangerous live or device-modifying actions cannot be performed before proving any read-only behavior.

This order matters because read-only execution should be considered only after the project has evidence that write, destructive, raw command, credential, transport, and real device contact paths are structurally blocked.

## Allowed Work

- Create deterministic scaffold data.
- Deny dangerous action categories by default.
- List future read-only candidate categories as non-executable.
- Record fail-closed decision behavior.
- Write JSON and HTML evidence reports.
- Expose the report as static dashboard/report-index evidence.
- Add tests that prove no live, credential, transport, write, raw command, or device contact capability exists.

## Blocked Work

- Real device access.
- SSH.
- RouterOS API.
- Sockets.
- Subprocess device operations.
- Credentials.
- Real adapter connection logic.
- Live-read.
- Executable guards.
- Fake transport full path.
- Runner live wiring.
- Dashboard execution buttons, command inputs, POST routes, or action endpoints.

## Safety Invariants

- `fail_closed_default == True`
- `live_read_allowed == False`
- `write_allowed == False`
- `raw_command_allowed == False`
- `credential_required == False`
- `transport_required == False`
- `real_device_contact_allowed == False`

## Handoff

Day92 must prove executable guards. Day93 must prove fake transport. Day94 must prove runner dry-run wiring. Day95 must lock regressions. Day96 may review live-read entry only after those proofs exist.

Until then, Day91 keeps all read-only candidates `NOT_EXECUTABLE`, `PENDING_GUARD`, and `FUTURE_ONLY`.
