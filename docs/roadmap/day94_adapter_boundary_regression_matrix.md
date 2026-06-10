# Day94 Adapter Boundary Regression Matrix

Day94 creates a matrix-style regression evidence layer for the Day93 guarded
fake adapter boundary.

## Scope

- Add `intent_adapter_boundary_regression_matrix.py`.
- Model allowed and rejected boundary rows deterministically.
- Cover read-only safe, read-only review, live-capable, config mutation, and
  unknown intent classes.
- Include fake-adapter and real-adapter-blocked targets.
- Generate JSON and static HTML reports.
- Surface the report through the existing report index and static dashboard
  reviewer references.

## Why This Follows Day93

Day93 proved a single contract: guard decision first, fake adapter invocation
only after approval. Day94 turns that into regression coverage so the same
boundary rule is checked across multiple scenario classes and adapter targets.

## Acceptance Invariants

The Day94 report must pass only when:

- `total_rows >= 12`
- `failed_rows == 0`
- `real_adapter_invocations == 0`
- `live_execution_invocations == 0`
- `adapter_invoked_for_rejected == 0`
- rejected rows have no fake or real adapter invocation
- overall status is `PASS`

## Non-Goals

Day94 does not add:

- real adapter execution
- SSH or RouterOS/API execution
- live command execution
- device access
- `config.json` loading
- environment secret loading
- execution unlocks
- dashboard POST routes, forms, buttons, adapter controls, or live execution
  endpoints
- OpenAI API, AI SDK, voice, shell automation, or external service calls

Day94 remains fake-adapter-only, deterministic, offline, and evidence/report
only.
