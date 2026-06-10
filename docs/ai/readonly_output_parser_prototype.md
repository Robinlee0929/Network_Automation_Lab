# Day96 Read-only Output Parser Prototype

Day96 is fake-only and parser-only. It does not connect to RouterOS, does not use SSH, does not perform live-read, and does not read `config.json`.

The parser accepts Day95 normalized fake adapter result records and inspects only `result_payload.simulated_output`. It produces structured parser records, parser status, warnings, unsupported sections, and safety metadata. The parsed output is evidence from simulated fake adapter output only; it is not verified device truth.

## Boundary

- Source kind: `fake_adapter_simulated_output`
- Parser mode: `parser_only`
- Live-read enabled: `false`
- SSH enabled: `false`
- RouterOS enabled: `false`
- Device access enabled: `false`
- Adapter fallback enabled: `false`
- Runner live path enabled: `false`
- Dashboard action allowed: `false`

Unsupported or malformed input returns `REVIEW_NEEDED` or `UNSUPPORTED`. The parser does not attempt recovery through an adapter, runner, SSH transport, RouterOS API, socket, subprocess, dashboard action, or any live path.

## Position In The Chain

Day95 normalizes fake adapter results. Day96 consumes those normalized fake results and parses their simulated text into records. This prepares a safe parser boundary for future live-read review work, but it does not unlock live-read.

