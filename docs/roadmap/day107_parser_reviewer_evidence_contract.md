# Day107 Parser Reviewer Evidence Contract Consolidation

Day107 returns to the parser reviewer evidence mainline after the Day106 governance audit.

## Purpose

Create a deterministic, report-only contract that consolidates Day96-Day105 parser evidence and makes the reviewer decision explicit:

- evidence chain represented
- stage completion visible
- report-only, parser-only, static-only, review-only, and blocked scopes visible
- reviewer acceptance criteria explicit
- safety boundaries locked
- live-capable transition still blocked
- review-only continuation accepted when evidence is complete and safe
- no-execution proof preserved

## Deliverables

- `intent_parser_reviewer_evidence_contract.py`
- Runner task: `parser-reviewer-evidence-contract`
- JSON report: `reports/lab-summary/day107_parser_reviewer_evidence_contract.json`
- HTML report: `reports/lab-summary/day107_parser_reviewer_evidence_contract.html`
- Tests: `tests/test_intent_parser_reviewer_evidence_contract.py`
- Documentation: `docs/ai-intent/day107_parser_reviewer_evidence_contract.md`

## Safety Boundary

Day107 is report-only and deterministic. It must not add device access, SSH, network commands, adapter invocation, broker handoff, runner execution paths, configuration mutation, OpenAI API calls, external AI runtime, voice runtime, dashboard action endpoints, POST routes, or execution unlocks.

The wrong route remains prohibited:

Parser evidence contract -> adapter / broker / SSH / live device / config write / OpenAI API / voice runtime / rejected-intent execution.

## Validation

Run:

```bash
python -m pytest
python network_lab.py --task parser-reviewer-evidence-contract
python network_lab.py --task report-index
python network_lab.py --report-index
```

Also confirm `AGENTS.md` has no unstaged or staged diff.
