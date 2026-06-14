# Day129 AI Summary Prompt Contract for Reviewer Text Only

Day129 is a prompt contract only. It defines deterministic reviewer-facing
prompt boundaries for a future AI summary prompt.

## Scope

- Task: `ai-summary-prompt-contract`
- Mode: `REPORT_ONLY`
- Contract scope: `REVIEWER_TEXT_ONLY`
- Day127 reference: AI reviewer summary schema contract
- Day128 reference: AI reviewer summary fixture renderer
- Output:
  - `reports/lab-summary/day129_ai_summary_prompt_contract.json`
  - `reports/lab-summary/day129_ai_summary_prompt_contract.html`

The only allowed prompt purpose is reviewer summary text only.

## Allowed Prompt Boundary

The prompt contract allows wording equivalent to:

```text
Produce a concise reviewer summary from the provided structured summary evidence.
Use only the provided evidence.
Do not make approval decisions.
Do not infer pass/fail.
Do not request execution.
Do not request tools.
Do not request API/provider access.
Do not unlock any next phase.
Return reviewer text only.
```

## Required Rejections

Day129 rejects prompts that ask for execution, commands, tool calls,
provider/API setup, OpenAI API calls, live integration, approval decisions,
pass/fail decisions, next phase unlocks, redaction or secrets masking, or audit
trail binding.

## Safety Boundary

Day129 is a prompt contract only.

Day129 is not the next day's feature.

Day129 does not enable execution / provider / API.

Day129 does not call OpenAI API.

Day129 does not implement redaction policy.

Day129 does not implement audit trail binding.

Day129 does not make AI decisions.

Day129 does not unlock next phase.

Day129 is not Day130 redaction policy.

Day129 is not Day131 audit trail binding.

Day129 is not Day132 reviewer approval gate.

Day129 is not Day133 mock provider boundary.

## Validation

Run:

```bash
python -m pytest
python network_lab.py --task ai-summary-prompt-contract
python network_lab.py --task report-index
```
