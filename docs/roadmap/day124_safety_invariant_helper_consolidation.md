# Day124 Safety Invariant Helper Consolidation

## Goal

Create a shared deterministic safety invariant helper module so review-only,
dry-run-only, provider-planning, and reviewer evidence tasks do not redefine
the same dangerous capability flags.

## Deliverables

- `intent_safety_invariant_helpers.py`
- CLI task: `python network_lab.py --task safety-invariant-helper-review`
- JSON report: `reports/lab-summary/day124_safety_invariant_helper_review.json`
- HTML report: `reports/lab-summary/day124_safety_invariant_helper_review.html`
- Task catalog and report-index visibility
- Tests for deterministic helpers, blocked capabilities, CLI output, report
  generation, and report-index discovery

## Safety Rules

Day124 is review-only and report-only. It does not enable:

- AI runtime
- OpenAI API
- Voice input, speech-to-text, text-to-speech, or microphone use
- SSH
- Live device access
- Live command execution
- Dashboard POST/action endpoints
- Broker execution
- Mapped task execution
- Write operations
- Configuration changes
- Runtime unlocks

## Acceptance

The Day124 task is accepted only when:

- `overall_status` is `PASS`
- `mode` is `REVIEW_ONLY`
- `execution_allowed` is `false`
- `final_recommendation` is `KEEP_REVIEW_ONLY_SAFETY_INVARIANTS`
- All dangerous capability flags remain `false`
- Report index discovers the Day124 JSON and HTML reports
- The required validation commands complete without safety regressions

## Validation

```bash
python -m pytest
python network_lab.py --task safety-invariant-helper-review
python network_lab.py --task report-index
python network_lab.py --report-index
git status --short --branch
```
