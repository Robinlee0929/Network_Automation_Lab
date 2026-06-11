# Day102 Parser Fixture Expansion

Day102 completed scope is a read-only, report-only parser fixture expansion.
It follows the Day101 closure plan by turning coverage gaps into deterministic
static fixtures.

Day102 does not:

- add parser capability
- advance parser output into broker scope
- invoke adapters or executors
- use SSH or live device access
- execute RouterOS commands
- change configuration
- read `config.json`
- call OpenAI APIs or external services
- add dashboard actions

Required Day102 locks:

- `parser_capability_added = false`
- `parser_ready_for_broker = false`
- `broker_handoff_allowed = false`
- `ssh_allowed = false`
- `config_change_allowed = false`

## Success Criteria

Day102 proves five fixture categories:

- Positive fixtures: legal read-only and report-only parser evidence is not
  rejected.
- Negative fixtures: unsupported but well-formed evidence is clearly rejected.
- Malformed fixtures: broken input shapes fail closed without crashing.
- Ambiguous fixtures: unclear meaning is not silently accepted.
- Unsafe fixtures: live, mutating, SSH, and config-change intent is blocked.

## Next Step

Day103 should use these fixtures to freeze normalized parser schema and detect
accidental output drift. Broker integration remains blocked.
