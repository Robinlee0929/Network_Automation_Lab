# Day92 Real Adapter Executable Guards

Day92 implements the executable rejection layer requested after Day91.

It is guard-only. It is not an adapter implementation.

## Scope

- Add `intent_executable_guards.py`.
- Add runner task `real-adapter-executable-guards`.
- Produce deterministic JSON and HTML reports.
- Surface Day92 in the local report index and dashboard evidence references.
- Prove rejected requests never invoke the fake executor.

## Safety Boundaries

- No real routers.
- No SSH.
- No RouterOS commands.
- No sockets.
- No subprocess device operations.
- No ping, netmiko, paramiko, or real device adapters.
- No credential loading.
- No firewall, interface, IP, WireGuard, VRRP, route, reboot, reset, backup,
  export, or system configuration modification.
- No dashboard execution controls.

## Required Proof

The Day92 report must show:

- `status: PASS`
- `phase: GUARD_ENFORCED`
- `safety_level: offline_deterministic_guard`
- `no_real_device_access: true`
- `no_ssh: true`
- `no_subprocess: true`
- `rejected_adapter_invocations: 0`
- scenario evidence containing request, decision, reason code, matched rule,
  blocked action category, and evidence

## Guard Decisions

Allowed requests are limited to simulated read-only actions:

- collect interface status
- read route summary
- read WireGuard peer status with redacted output
- read system resource summary
- read-only precheck summary

Rejected requests include dangerous, sensitive, mutation-like, ambiguous, and
unknown actions. Unknown requests fail closed.

## Not Included

Day92 does not add:

- real adapter connection logic
- live read-only command execution
- transport setup
- credential handling
- command passthrough
- approval or execution unlocks

## Next Direction

Day93 should be `Guarded Fake Adapter Contract / Adapter Boundary Invocation
Audit`.

Day93 should continue to use fake/offline transport only unless a later
explicit gate approves real read-only integration.
