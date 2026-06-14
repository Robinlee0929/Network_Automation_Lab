# Day135 AI Provider Disabled-by-Default Safety Regression

Adopt: `Day135 - AI Provider Disabled-by-Default Safety Regression`.

Day135 verifies that AI provider safety remains disabled by default after the
Day134 disabled provider adapter contract. The consumer-style read of Day134
evidence is only one read-only regression case.

This is not the next day's feature.

This is not Day136.

No execution/provider/API path is opened.

## Day135 Scope

- Add `ai-provider-disabled-by-default-safety-regression` as a review-only task.
- Read Day134 disabled provider contract/evidence as JSON data only.
- Verify disabled-by-default provider, API, execution, model, network, registry, CLI, report, and next-phase flags.
- Reject regression inputs where any enablement or invocation flag becomes true.
- Emit JSON/HTML reviewer evidence.

## Explicit Non-Goals

- Not the next day's feature.
- Not Day136 export package integration.
- No provider implementation.
- No provider object instantiation.
- No OpenAI, Anthropic, Gemini, local LLM, network service, or subprocess provider.
- No provider SDK import.
- No API call.
- No model invocation.
- No execution invocation.
- No registry, CLI, or report activation path.
- No next-phase unlock.

## Required Regression Cases

- Baseline Day134 disabled provider contract is accepted as read-only evidence.
- Consumer-style read is allowed only as read-only inspection.
- `provider_enabled=true` fails regression.
- `api_enabled=true` fails regression.
- `execution_enabled=true` fails regression.
- `model_invocation_enabled=true` fails regression.
- `network_enabled=true` fails regression.
- `provider_instantiated=true` fails regression.
- `api_called=true` fails regression.
- `execution_invoked=true` fails regression.
- Missing or unreadable Day134 evidence must not advance.
- CLI/report/registry paths must not activate provider/API/execution.

## Safety Evidence Fields

- `provider_enabled: false`
- `api_enabled: false`
- `execution_enabled: false`
- `model_invocation_enabled: false`
- `network_enabled: false`
- `provider_instantiated: false`
- `api_called: false`
- `execution_invoked: false`
- `registry_activation_allowed: false`
- `cli_activation_allowed: false`
- `report_activation_allowed: false`
- `next_phase_allowed: false`

## Expected Result

```text
status=PASS
mode=REVIEW_ONLY
scope=DISABLED_BY_DEFAULT_SAFETY_REGRESSION
regression_verdict=DISABLED_BY_DEFAULT_PRESERVED
```

## Reports

- `reports/lab-summary/day135_ai_provider_disabled_by_default_safety_regression.json`
- `reports/lab-summary/day135_ai_provider_disabled_by_default_safety_regression.html`

## Validation Commands

```powershell
python -m pytest
python network_lab.py --task ai-provider-disabled-by-default-safety-regression
python network_lab.py --task report-index
python network_lab.py --report-index
git status --short --branch
```

## AGENTS.md Read Status

- `AGENTS.md pre-read: YES`
- `AGENTS.md path: AGENTS.md`
- `AGENTS.md modified: false`
