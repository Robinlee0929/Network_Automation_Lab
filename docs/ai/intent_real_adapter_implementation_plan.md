# Day90 Real Adapter Implementation Plan

Day90 is not implementation. It is a planning-only decision record that decides
whether the repository evidence is ready to enter the next safety proof. Day90
produced `CONDITIONAL_GO`, not `GO`, so Day91 must be scaffold-only.

Day90 does not add a real SSH client, RouterOS command runner, real device host,
username, password, adapter connection logic, subprocess/network execution, or
automatic configuration apply behavior.

## Position

- Scope: `planning_only`
- Decision: `GO`, `CONDITIONAL_GO`, or `NO_GO`
- Adapter implementation allowed: false
- Live device access allowed: false
- SSH allowed: false
- RouterOS command execution allowed: false

## Evidence Basis

The Day90 decision is based only on repository evidence:

- Day83 read-only executor readiness artifact.
- Day84 adapter interface contract artifact.
- Day85 mock adapter evidence binding artifact.
- Day86 controlled runner harness and safety regression artifact.
- Day87 phase gate review artifact.
- Day88 real read-only adapter design draft artifact.
- Day89 real adapter safety boundary spec artifact.
- Runner task registration.
- Static report/dashboard visibility.
- AI reviewer and roadmap documentation.

Missing critical evidence must produce `NO_GO`; it cannot produce a fake `GO`.
When the major evidence chain is complete, Day90 may produce
`CONDITIONAL_GO`, because any next phase must remain tightly constrained.

## Day91 Boundary

After Day90 `CONDITIONAL_GO`, Day91 must be Real Adapter Safety Scaffold only.
It must prove dangerous actions are denied before any read-only behavior is
considered.

Day91 must keep:

- `fail_closed_default == True`
- `live_read_allowed == False`
- `write_allowed == False`
- `raw_command_allowed == False`
- `credential_required == False`
- `transport_required == False`
- `real_device_contact_allowed == False`

Configuration changes, write operations, automatic apply behavior, arbitrary
commands, destructive RouterOS commands, host credentials in repo, and adapter
connection logic remain forbidden. Future read-only candidates may be listed
only as `NOT_EXECUTABLE`, `PENDING_GUARD`, and `FUTURE_ONLY` until Day92-Day96
prove executable guards, fake transport, runner dry-run wiring, regression
locks, and live-read review.
