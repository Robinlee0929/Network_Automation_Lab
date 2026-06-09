# Day89 Real Adapter Safety Boundary Spec

Day89 is a pre-implementation safety boundary for the future real read-only
adapter path. It locks the boundary before any implementation work begins.

Day89 does not implement a real adapter. It does not introduce SSH, RouterOS
device access, live read-only command execution, arbitrary command execution,
file upload, shell escape, or device configuration changes.

## Position

- Phase: `DESIGN_ONLY`
- Status: `PASS`
- Safety boundary: locked
- Adapter scope: read-only evidence collection only
- Implementation allowed: false
- Live device access allowed: false
- SSH allowed: false
- Configuration changes allowed: false
- Command execution allowed: false
- Reviewer decision required: true

## Allowed Future Behavior

Future behavior is intentionally narrow and remains blocked until a later gate.
A future adapter may only collect read-only evidence after the command is
allowlisted, reviewer-gated, redaction-safe, evidence-producing, and
fail-closed.

Day89 itself only allows static safety-boundary loading, future allowlist
metadata validation, candidate command classification, evidence-only report
generation, deterministic output, and no network side effects.

## Blocked Behavior

The boundary blocks configuration changes, firewall changes, interface
disable/enable, reboot/reset, package install/update, password or secret export,
arbitrary command execution, write-mode SSH sessions, command shell escape, file
upload to devices, destructive RouterOS commands, and fallback to
non-allowlisted commands.

## Required Invariants

- Default deny.
- No command may run unless allowlisted.
- No command may mutate device state.
- No secret-bearing output may be stored unredacted.
- Every future live read-only run must produce evidence.
- Every future live read-only run must be reviewer-gated.
- Adapter errors must fail closed.
- Design-only reports must not imply live readiness.

## Evidence, Failure, Redaction, And Audit

Future live read-only runs must produce reviewer-visible evidence tied to a
request id, approval envelope, target alias, allowlist command id, normalized
command, policy decision, timing, digests, redaction status, error code, and
correlation id.

Failures must stop before execution and fail closed. Missing approval, expired
approval, command mismatch, target mismatch, allowlist metadata mismatch, or
missing redaction policy must deny the request.

Secret-bearing output must be rejected or redacted before storage. Dashboard and
report visibility remain static/read-only: no live action button, POST route, or
command execution control is introduced.

## Day90 Entry Note

Day90 may plan implementation only if the Day89 boundary is satisfied. Any
future implementation must remain read-only, allowlisted, reviewer-gated,
evidence-producing, redaction-safe, and fail-closed.
