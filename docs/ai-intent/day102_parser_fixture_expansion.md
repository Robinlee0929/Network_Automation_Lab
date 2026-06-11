# Day102 Parser Fixture Expansion

Day102 expands parser evidence fixtures after the Day101 closure plan.

It is not a parser capability milestone. It does not connect a broker, invoke
adapters, use SSH, contact live devices, read `config.json`, execute RouterOS
commands, change configuration, call OpenAI APIs, use a voice runtime, or add
dashboard actions.

## Position

Day102 converts parser evidence gaps into static fixtures and testable report
evidence. It keeps parser outputs as reviewer evidence only.

Day102 keeps:

- `parser_capability_added = false`
- `parser_ready_for_broker = false`
- `broker_handoff_allowed = false`
- `execution_allowed = false`
- `adapter_invocation_allowed = false`
- `live_device_access_allowed = false`
- `ssh_allowed = false`
- `config_change_allowed = false`

## Fixture Categories

The Day102 report must include:

- `positive`: legal read-only / report-only parser input is not rejected.
- `negative`: unsupported but normally formatted input is rejected with a clear
  reason.
- `malformed`: bad fixture shape does not crash and has an explicit reason.
- `ambiguous`: unclear semantic intent is not silently accepted.
- `unsafe`: live, mutating, SSH, and config-change intent is blocked.

## Reports

Generate with:

```bash
python network_lab.py --task parser-fixture-expansion
```

Outputs:

- `reports/ai/day102_parser_fixture_expansion.json`
- `reports/ai/day102_parser_fixture_expansion.html`
