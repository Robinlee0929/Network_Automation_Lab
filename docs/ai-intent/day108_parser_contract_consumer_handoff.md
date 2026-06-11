# Day108 Parser Contract Consumer / Reviewer Decision Handoff

Day108 adds a report-only consumer handoff layer for the Day107 parser reviewer evidence contract. It consumes Day107-style reviewer evidence records and emits deterministic reviewer decision handoff records for the next reviewer-facing phase.

Day108 does not redefine the Day107 contract. The source contract remains `day107.parser_reviewer_evidence_contract`, and the consumer report records the Day107 source schema version as `day107.parser_reviewer_evidence_contract.v1`.

## Purpose

Day107 consolidated Day96-Day105 parser evidence into a reviewer evidence contract. Day108 is the consumer-facing handoff that answers a different question: can a downstream reviewer safely receive a structured decision handoff record from that contract?

The answer is still report-only. A handoff-ready record means only that reviewer evidence can proceed to the next reviewer decision step. It does not grant runtime, broker, adapter, SSH, mapped-task, device, approval, or write/config-change permission.

## Consumer Handoff Schema

Each handoff record includes:

| Field | Meaning |
| --- | --- |
| `handoff_id` | Deterministic Day108 handoff record ID. |
| `source_contract` | Must be `day107.parser_reviewer_evidence_contract`. |
| `source_contract_version` | Must be non-empty and tied to the Day107 schema version. |
| `consumer_schema_version` | Must be `day108.parser_contract_consumer_handoff.v1`. |
| `intent_id` | Deterministic sample intent ID. |
| `normalized_intent` | Consumer-facing normalized intent text. |
| `parser_supported` | Whether the parser outcome can support a reviewer handoff. |
| `reviewer_decision` | One of the allowed Day108 reviewer decision enum values. |
| `evidence_status` | Evidence quality/status used by the handoff validator. |
| `handoff_ready` | True only when validation passes and the reviewer decision is ready. |
| `handoff_blockers` | Deterministic blockers explaining why a record is not ready. |
| `safety_flags` | Fail-closed flags for live, SSH, device, command, write/config, approval, mapped task, OpenAI API, and voice paths. |
| `next_stage_recommendation` | Reviewer-facing recommendation for the next report-only step. |

## Reviewer Decision Enum

Day108 permits only these reviewer decisions:

| Decision | Meaning |
| --- | --- |
| `READY_FOR_REVIEW_HANDOFF` | Evidence can move to the next reviewer handoff step as report-only data. |
| `NEEDS_REVIEWER_CLARIFICATION` | Evidence exists, but a reviewer must clarify the next report-only interpretation. |
| `BLOCKED_UNSAFE_OR_UNSUPPORTED` | The consumer request is unsafe, unsupported, or attempts to convert evidence into execution. |

## Validation Rules

The Day108 validator blocks or marks a handoff not ready when:

- Required handoff fields are missing.
- `source_contract` is not the Day107 source contract.
- `source_contract_version` is empty.
- `consumer_schema_version` is empty.
- `reviewer_decision` is outside the allowed enum.
- A ready handoff has an unacceptable `evidence_status`.
- Any live execution, SSH, device connection, command execution, write/config-change, approval unlock, mapped task execution, OpenAI API, or voice input flag is true.

Unsupported parser outcomes become `BLOCKED_UNSAFE_OR_UNSUPPORTED`. Degraded or ambiguous evidence becomes `NEEDS_REVIEWER_CLARIFICATION`.

## Safety Invariants

Day108 preserves these fixed invariants:

```text
report_only = True
dry_run_only = True
live_execution_allowed = False
ssh_allowed = False
device_connection_allowed = False
command_execution_allowed = False
write_or_config_change_allowed = False
approval_unlock_supported = False
mapped_task_execution_allowed = False
openai_api_used = False
voice_input_used = False
```

The task writes reviewer evidence only. It does not add SSH, live-device access, command execution, OpenAI API calls, voice input, approval unlock, mapped task execution, adapters, brokers, POST endpoints, or configuration-changing behavior.

## Run

```powershell
python network_lab.py --task parser-contract-consumer-handoff
```

Reports:

```text
reports/lab-summary/day108_parser_contract_consumer_handoff.json
reports/lab-summary/day108_parser_contract_consumer_handoff.html
```

## Tests

```powershell
python -m pytest tests/test_intent_parser_contract_consumer_handoff.py
python network_lab.py --task parser-contract-consumer-handoff
python network_lab.py --task report-index
```
