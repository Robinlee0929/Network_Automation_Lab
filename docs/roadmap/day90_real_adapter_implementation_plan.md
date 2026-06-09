# Day90 Real Adapter Implementation Plan

Day90 turns the Day83-Day89 read-only executor evidence chain into an
implementation-entry decision. It is `planning_only`.

## Scope

- Generate deterministic Day90 JSON/HTML reports under `reports/lab-summary/`.
- Add runner task `real-adapter-implementation-plan`.
- Make the Day90 report visible in report-index/dashboard paths.
- Document the AI reviewer boundary and Day91 roadmap position.
- Add tests that prevent Day90 from becoming implementation.

## Non-Scope

- No true SSH client.
- No RouterOS command runner.
- No real device host, username, password, or secret.
- No adapter implementation class connection logic.
- No automatic configuration apply.
- No subprocess, network command, live device operation, or mutation path.

## Acceptance

- Report has `day=90`, `scope=planning_only`, and a decision in `GO`,
  `CONDITIONAL_GO`, or `NO_GO`.
- `adapter_implementation_allowed=false`,
  `live_device_access_allowed=false`, `ssh_allowed=false`, and
  `routeros_command_execution_allowed=false`.
- Missing critical evidence cannot produce `GO`.
- Evidence chain, blockers, conditional requirements, required controls,
  minimum safe adapter scope, and forbidden scope are reviewer-visible.
- Runner prints Day90 title, decision, `PLANNING_ONLY`, locked false flags, and
  JSON/HTML report paths.
- Static HTML has no forms, buttons, JavaScript, POST route, or action control.

## Day91 Roadmap

Day91 may enter prototype only if Day90 produces an approving decision and the
prototype remains minimal and read-only. Any future live-read path must require
an explicit allow flag, bounded command allowlist, timeout, evidence logging,
redaction, fail-closed behavior, and no configuration mutation.
