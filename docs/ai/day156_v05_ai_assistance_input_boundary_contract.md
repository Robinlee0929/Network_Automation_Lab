# Day156 v0.5 AI Assistance Input Boundary Contract

## Scope

day: 156
task: v05-ai-assistance-input-boundary-contract
status: REVIEW_READY
status_label: V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY
mode: review-only / report-only / non-executable
day154_closure_baseline_lock_respected: true
day155_reopen_rationale_respected: true
reviewer_assistance_only: true
executor_recommendation_only: true
fixed_template_required: true
config_json_read_allowed: false
execution_allowed: false
executor_unlock_allowed: false
provider_allowed: false
api_allowed: false
openai_api_call_allowed: false
external_api_call_allowed: false
live_device_allowed: false
ssh_allowed: false
command_execution_allowed: false
secrets_allowed: false
phase_gate_approval: false
next_phase_allowed: false

## Allowed reviewer evidence inputs

- repo reports
- evidence files
- pytest results
- report-index results
- task registry metadata
- roadmap/docs
- dry-run outputs
- mock-only fixtures

## Forbidden data sources

- secrets, tokens, passwords, private keys, and `.env` files
- `config.json` and private runtime configuration
- live device configs
- microphone or voice input
- unauthorized external API responses

## No live collection path

Day156 does not collect from devices, providers, APIs, shells, or microphones. Inputs must already exist as static repo-local reviewer evidence.

PASS only means the input boundary is documented and blocks unsafe data sources. PASS does not allow AI execution, provider/API integration, live-device access, direct command generation, or executor action.
