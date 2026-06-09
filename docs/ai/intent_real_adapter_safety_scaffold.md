# Day91 Real Adapter Safety Scaffold

Day91 exists because Day90 produced `CONDITIONAL_GO`, not `GO`. The project is not ready to implement a real adapter, live-read path, SSH client, RouterOS API client, socket transport, subprocess device operation, credential path, or read-only command execution.

Day91 is therefore scaffold-only safety evidence. Its job is to prove dangerous live or device-modifying actions are structurally denied before the project tries to prove that read-only behavior can pass through guards.

## Scope

- Status: `SCAFFOLD_ONLY`
- Runner task: `python network_lab.py --task real-adapter-safety-scaffold`
- Reports:
  - `reports/lab-summary/day91_real_adapter_safety_scaffold.json`
  - `reports/lab-summary/day91_real_adapter_safety_scaffold.html`

Day91 may define deterministic safety records, denied dangerous action categories, future read-only candidate categories, fail-closed decisions, invariants, evidence chain, and next required days.

Day91 must not implement real device access, SSH, RouterOS API, sockets, subprocess device operations, credentials, real adapter connection logic, executable guards, fake transport full path, runner live wiring, or live-read.

## Why Dangerous Denial Comes First

After `CONDITIONAL_GO`, the safest next proof is negative capability: show that the system cannot perform dangerous actions even before read-only behavior is considered.

The scaffold denies configuration writes, firewall changes, route changes, interface disable/enable, VRRP modification, WireGuard peer modification, reboot, reset configuration, raw command execution, device file transfer, credential export, and arbitrary command passthrough.

Only after this denial evidence exists should the project prove controlled read-only behavior through later guard layers.

## Read-only Candidates

Day91 may list future read-only candidates such as system identity read, interface print/read, IP address print/read, route print/read, firewall print/read, log read, and WireGuard peer print/read.

Every candidate remains:

- `NOT_EXECUTABLE`
- `PENDING_GUARD`
- `FUTURE_ONLY`

These records are labels for future guard work, not executable adapter behavior.

## Locked Invariants

- `fail_closed_default == True`
- `live_read_allowed == False`
- `write_allowed == False`
- `raw_command_allowed == False`
- `credential_required == False`
- `transport_required == False`
- `real_device_contact_allowed == False`

## Evidence Chain

Day91 links directly to Day90:

- Day90: `CONDITIONAL_GO` only, planning-only, no adapter implementation.
- Day91: scaffold-only proof that dangerous actions are denied and read-only candidates remain future-only.

## Future Proof Required

- Day92 must add executable guards that still block live-read.
- Day93 must prove a fake transport full path without device contact.
- Day94 must wire runner dry-run behavior without live transport.
- Day95 must lock regressions for no write, no raw command, no credential, and no live-read.
- Day96 may review limited live-read entry only after the previous proofs exist; it must not be treated as automatic enablement.
