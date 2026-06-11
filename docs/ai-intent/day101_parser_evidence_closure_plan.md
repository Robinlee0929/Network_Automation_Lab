# Day101 Parser Evidence Closure Plan

Day101 turns the Day100 parser phase-gate findings into a closure roadmap.

It is not an execution milestone. It does not approve broker handoff, release
the parser gate, invoke adapters, use SSH, contact live devices, read
`config.json`, execute RouterOS commands, call OpenAI APIs, use a voice runtime,
or add dashboard actions.

## Position

Parser phase is not moving toward execution. It is converting reviewable
evidence into proof of stable parser behavior.

Day101 keeps:

- `parser_ready_for_broker = false`
- `broker_handoff_allowed = false`
- `execution_allowed = false`
- `live_device_access_allowed = false`
- `ssh_allowed = false`
- `openai_api_allowed = false`
- `evidence_closure_required = true`
- `phase_gate_rerun_required = true`

## Source

Day101 reads the Day100 parser phase-gate review result:

- `reports/ai/day100_parser_phase_gate_review.json`
- `intent_parser_phase_gate_review.py`

Day100 found parser evidence that is still `UNDER_COVERED` and parser evidence
that must remain `REVIEW_ONLY`. Day101 converts those findings into closure
items with priority, category, gap, required evidence, and target follow-up day.

## Required Findings

The Day101 report must show:

- `UNDER_COVERED` categories that need fixture expansion before advancement.
- `REVIEW_ONLY` categories that remain reviewer evidence and cannot cross into
  broker scope.
- Missing or weak fixture coverage.
- Missing positive cases.
- Missing negative cases.
- Malformed input coverage gaps.
- Schema stability risks.
- Reject-by-default risks.
- Categories blocked from advancement.

## Day102-Day105 Sequence

Day101 defines the required closure sequence:

- Day102 Parser Fixture Expansion: add positive, negative, malformed,
  ambiguous, and unsafe parser fixtures.
- Day103 Parser Schema Stability Regression: freeze normalized parser schema
  and detect accidental output drift.
- Day104 Parser Reject-by-default Regression: strengthen unknown, ambiguous,
  and unsafe input rejection behavior.
- Day105 Parser Re-Gate Review: re-run the parser phase gate and decide which
  categories, if any, may advance.

Broker integration remains blocked through Day101. Any future advance requires
the Day105 re-gate decision after Day102-Day104 evidence closure work is done.

## Reports

Generate with:

```bash
python network_lab.py --task parser-evidence-closure-plan
```

Outputs:

- `reports/ai/day101_parser_evidence_closure_plan.json`
- `reports/ai/day101_parser_evidence_closure_plan.html`
