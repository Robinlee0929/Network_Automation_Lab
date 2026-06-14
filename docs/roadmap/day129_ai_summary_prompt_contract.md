# Day129 AI Summary Prompt Contract for Reviewer Text Only

## Goal

Define a deterministic prompt contract that limits any future AI reviewer
summary prompt to reviewer summary text only.

## Decision

Adopt: `Day129 - AI Summary Prompt Contract for Reviewer Text Only`.

Day129 references Day127 schema expectations and Day128 renderer expectations,
but it does not expand beyond prompt-contract scope.

## Non-Goals

Day129 is a prompt contract only.

Day129 is not the next day's feature.

Day129 does not enable execution / provider / API.

Day129 does not call OpenAI API.

Day129 does not implement redaction policy.

Day129 does not implement audit trail binding.

Day129 does not make AI decisions.

Day129 does not unlock next phase.

Day129 does not implement Day130 redaction policy, Day131 audit trail binding,
Day132 AI Summary Dashboard Card Integration, or Day133 mock provider boundary.

## Deliverables

- `intent_ai_summary_prompt_contract.py`
- CLI task: `python network_lab.py --task ai-summary-prompt-contract`
- JSON report: `reports/lab-summary/day129_ai_summary_prompt_contract.json`
- HTML report: `reports/lab-summary/day129_ai_summary_prompt_contract.html`
- Report-index visibility
- AI intent documentation and roadmap documentation
- Tests for allowed reviewer-text-only prompts and rejected execution,
  provider/API/OpenAI, approval, pass/fail, next-phase, redaction, secret
  masking, and audit trail prompts

## Acceptance

- `overall_status=PASS`
- `reviewer_status=PROMPT_CONTRACT_READY`
- `agents_md_pre_read_result=PASS`
- `agents_md_read_before_day129_work=true`
- `contract_scope=REVIEWER_TEXT_ONLY`
- `reviewer_text_only=true`
- `provider_enabled=false`
- `api_enabled=false`
- `execution_enabled=false`
- `tool_calling_enabled=false`
- `ai_decision_enabled=false`
- `next_phase_allowed=false`
- `redaction_policy_enabled=false`
- `audit_trail_binding_enabled=false`
- `violations=[]`

## Validation

Run:

```bash
python -m pytest
python network_lab.py --task ai-summary-prompt-contract
python network_lab.py --task report-index
git status --short --branch
```

