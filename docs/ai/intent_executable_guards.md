# Day92 Real Adapter Executable Guards

Day92 converts the Day91 static safety scaffold into an executable guard layer.
It evaluates simulated request objects before any executor-like path can be
called.

Day92 is not a real adapter implementation. It does not add SSH, sockets,
RouterOS API, subprocess device operations, credentials, live-read behavior,
dashboard execution controls, or any device contact.

## Builds On Day91

Day91 proved the static boundary:

- dangerous live/device-modifying actions are denied
- read-only candidates are future-only
- live-read remains blocked
- no real adapter, transport, credential use, executable guard, or live-read
  path exists

Day92 keeps that boundary and adds deterministic code that can make an
ALLOW/REJECT decision for simulated requests.

## Executable Guard Behavior

The Day92 guard exposes these reviewer-visible concepts:

- `GuardRequest`
- `GuardDecision`
- `ExecutableGuard`
- decision: `ALLOW` or `REJECT`
- reason code
- human-readable reason
- matched rule name
- evidence list
- blocked action category
- `adapter_invocation_allowed`

Safe simulated read-only requests are allowed:

- collect interface status
- read route summary
- read WireGuard peer status with redacted output
- read system resource summary
- read-only precheck summary

Dangerous, sensitive, ambiguous, and unknown requests are rejected by default:

- reboot, reset, interface enable/disable
- firewall, route, IP address, WireGuard, and VRRP modification
- arbitrary command requests
- export or exposure of secrets/private keys
- request text or fields containing password, token, private key, or secret
- write/apply/configure/set/add/remove/delete/enable/disable verbs
- unknown actions

## Why Rejected Requests Cannot Reach Execution

All executor access must pass through `execute_guarded_request()`.

For a rejected request, the function returns a structured blocked result and
does not call the executor callable. The Day92 report proves this with
`rejected_adapter_invocations: 0` across the deterministic scenario set.

Allowed requests use deterministic offline fixture data only. They do not
connect anywhere and do not execute external commands.

## Offline Boundary

Day92 remains fully offline and deterministic:

- `no_real_device_access: true`
- `no_ssh: true`
- `no_subprocess: true`
- `no_socket: true`
- `no_real_adapter: true`
- `adapter_implementation_added: false`

## Day92 Does Not Do

Day92 does not:

- implement a real adapter
- open SSH or RouterOS API sessions
- execute RouterOS commands
- run ping, netmiko, paramiko, subprocess network commands, or sockets
- read credentials or config secrets
- modify firewall, interface, IP address, WireGuard, VRRP, routing, reboot,
  reset, backup, export, or system configuration
- add dashboard action buttons or POST execution routes
- approve live-read

## Reports

- `reports/lab-summary/day92_real_adapter_executable_guards_report.json`
- `reports/lab-summary/day92_real_adapter_executable_guards_report.html`

## Recommended Next Day

Day93 should be `Guarded Fake Adapter Contract / Adapter Boundary Invocation
Audit`.

Day93 should still avoid real devices unless a later explicit gate approves
real read-only integration.
