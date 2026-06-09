# Day93 Guarded Fake Adapter Contract

Day93 implements a guarded fake adapter contract and adapter boundary
invocation audit.

## Scope

- Add `intent_guarded_fake_adapter_contract.py`.
- Model allowed and rejected read-only intent scenarios deterministically.
- Evaluate the guard before any adapter boundary attempt.
- Invoke only a fake read-only adapter for guard-allowed scenarios.
- Generate JSON and static HTML evidence.
- Surface Day93 in `network_lab.py`, the report index, and the static dashboard
  reviewer references.

## Non-Goals

Day93 does not add:

- real adapter execution
- SSH or RouterOS/API execution
- live command execution
- device access
- `config.json` loading
- execution unlocks
- dashboard POST routes, forms, buttons, or live adapter toggles
- OpenAI API, AI SDK, voice, shell automation, or external service calls

## Acceptance Evidence

The Day93 report must pass only when:

- allowed scenarios exist
- rejected scenarios exist
- fake adapter invocations equal allowed scenario count
- rejected adapter invocations are 0
- real adapter invocations are 0
- guard ordering violations are 0
- safety violations are 0
- audit chain is complete
- adapter boundary is verified

Final recommendation remains `KEEP_FAKE_ONLY`.
