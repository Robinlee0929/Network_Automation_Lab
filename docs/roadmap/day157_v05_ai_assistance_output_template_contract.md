# Day157 v0.5 AI Assistance Output Template Contract

## Roadmap Purpose

Day157 defines fixed reviewer-only output fields for v0.5 AI Assistance.

Task slug:

v05-ai-assistance-output-template-contract

Status:

V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY

## Required Status Fields

day: 157
status: REVIEW_READY
command_execution_allowed: false
direct_command_generation_allowed: false
execution_allowed: false
executor_unlock_allowed: false
provider_allowed: false
api_allowed: false
openai_api_call_allowed: false
external_api_call_allowed: false
model_call_allowed: false
live_device_allowed: false
secrets_allowed: false
phase_gate_approval: false
next_phase_allowed: false

## Contract

- Allowed output fields are review_subject, evidence_references, summary, risk_flags, comparison_notes, open_questions, and human_reviewer_decision.
- Forbidden output fields include live commands, command templates, executor actions, provider activation, secrets, credentials, and approval unlocks.
- Human reviewer authority remains external to the template.

## Report Artifacts

- `reports/lab-summary/day157_v05_ai_assistance_output_template_contract.json`
- `reports/lab-summary/day157_v05_ai_assistance_output_template_contract.html`
