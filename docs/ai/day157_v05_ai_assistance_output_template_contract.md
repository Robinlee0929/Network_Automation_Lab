# Day157 v0.5 AI Assistance Output Template Contract

## Scope

day: 157
task: v05-ai-assistance-output-template-contract
status_label: V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_REVIEW_READY
command_execution_allowed: false
direct_command_generation_allowed: false
execution_allowed: false
executor_unlock_allowed: false
provider_allowed: false
api_allowed: false
openai_api_call_allowed: false
external_api_call_allowed: false
live_device_allowed: false
secrets_allowed: false
phase_gate_approval: false
next_phase_allowed: false

## Allowed output fields

- `review_subject`
- `evidence_references`
- `summary`
- `risk_flags`
- `comparison_notes`
- `open_questions`
- `human_reviewer_decision`

## Forbidden output fields

- live command fields
- command template fields
- executor action fields
- provider activation fields
- secret or credential fields
- approval unlock fields

## Human decision remains external

The template may record human reviewer decision notes, but it cannot approve a phase gate, unlock execution, or instruct an executor to act.

PASS only means the output template is fixed and cannot carry executable instructions.
