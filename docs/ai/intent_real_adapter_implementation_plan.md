# Day90 Real Adapter Implementation Plan

Day90 is not implementation. It is a planning-only decision record that decides
whether the repository evidence is ready to enter a later real read-only adapter
prototype phase.

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

If Day90 approves entry, the first implementation phase must be a minimal
read-only prototype only. Any future live-read path must require:

- Explicit allow flag.
- Bounded positive command allowlist.
- Timeout and fail-closed handling.
- Evidence logging.
- Redaction or digest-only output handling.
- No configuration mutation.

Configuration changes, write operations, automatic apply behavior, arbitrary
commands, destructive RouterOS commands, host credentials in repo, and adapter
connection logic outside the approved prototype boundary remain forbidden.
