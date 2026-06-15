# Day156 v0.5 AI Assistance Input Boundary Contract

## Roadmap Purpose

Day156 defines the v0.5 AI Assistance input boundary after the Day155 reopen rationale. It is review-only, report-only, and non-executable.

Task slug:

v05-ai-assistance-input-boundary-contract

Status:

V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_REVIEW_READY

## Required Status Fields

day: 156
status: REVIEW_READY
reviewer_assistance_only: true
executor_recommendation_only: true
config_json_read_allowed: false
credential_read_allowed: false
execution_allowed: false
executor_unlock_allowed: false
provider_allowed: false
api_allowed: false
openai_api_call_allowed: false
external_api_call_allowed: false
model_call_allowed: false
live_device_allowed: false
ssh_allowed: false
command_execution_allowed: false
secrets_allowed: false
microphone_allowed: false
voice_input_allowed: false
phase_gate_approval: false
next_phase_allowed: false

## Contract

- Allowed reviewer evidence inputs: repo reports, evidence files, pytest results, report-index results, task registry metadata, roadmap/docs, dry-run outputs, and mock-only fixtures.
- Forbidden data sources: secrets, credentials, private keys, `.env`, `config.json`, live device configs, microphone/voice input, and unauthorized external API responses.
- No live collection path is introduced.

## Report Artifacts

- `reports/lab-summary/day156_v05_ai_assistance_input_boundary_contract.json`
- `reports/lab-summary/day156_v05_ai_assistance_input_boundary_contract.html`
