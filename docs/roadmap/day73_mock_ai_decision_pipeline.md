# Day73 Mock AI Decision Pipeline

## Goal

Add a deterministic mock AI decision pipeline after the Day72 controlled AI
runtime input contract validator.

Day72 answers: is the input structurally acceptable and safe enough for a later
review stage?

Day73 answers: given the Day72 validation result, what reviewer-facing mock
decision label should be recorded?

## Scope

Day73 adds:

- `intent_mock_ai_decision_pipeline.py`
- A `mock-ai-decision-pipeline` runner task.
- JSON and HTML reviewer reports.
- Static dashboard visibility on `/ai-intent-reviewer`.
- Documentation and tests for the Day72-to-Day73 chain.

## Decision Labels

| Label | Meaning |
| --- | --- |
| `DOCUMENTATION_ONLY` | Safe to present as documentation evidence only. |
| `REPORT_ONLY` | Safe to present as report evidence only. |
| `REVIEW_REQUIRED` | Requires manual reviewer triage. |
| `BLOCKED_LIVE_ACTION` | Live device or network action is blocked. |
| `INVALID_INPUT_BLOCKED` | Input failed the Day72 contract and is blocked. |

## Safety Invariants

- `allowed_to_execute` is always `false`.
- Live action requests are always blocked.
- Invalid inputs are always blocked.
- Ambiguous inputs require manual review.
- Documentation/report-only requests do not execute mapped tasks.
- The dashboard remains static/read-only for AI intent reviewer content.

## Explicit Non-Goals

Day73 does not add:

- OpenAI API usage.
- AI SDK dependencies.
- Real AI runtime.
- SSH.
- Device access.
- Live execution.
- Mapped task execution.
- Arbitrary command execution.
- `config.json` dependency.
- Dashboard forms.
- POST routes.
- Action endpoints.
- Router, switch, firewall, VPN, VRRP, or network configuration changes.
- Release tags.

## Validation Commands

```text
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
python network_lab.py --task offline-mock-runtime
python network_lab.py --task offline-mock-runtime-contract
python network_lab.py --task offline-mock-runtime-review
python network_lab.py --task mock-ai-decision-pipeline
```

`report-index` may warn for existing optional missing local reports, but should
not introduce Day73 failures.

## Completion Criteria

- The runner task is discoverable.
- Day73 JSON and HTML reports are generated.
- Tests confirm required decision fields and safety invariants.
- The dashboard shows Day73 docs, roadmap, and report paths without adding
  forms, POST routes, buttons, or action endpoints.
- README includes a concise Day73 progress note.

## Future Day74

Day74 could validate the Day73 decision record schema, add reviewer acceptance
criteria for the Day72-to-Day73 chain, or produce a static evidence comparison
between Day66 mock runtime decisions and Day73 validator-backed decisions. It
should stay mock-only and no-execution unless a future safety design explicitly
changes that boundary.
