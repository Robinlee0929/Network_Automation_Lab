# Day108 Parser Contract Consumer / Reviewer Decision Handoff

## Goal

Add a deterministic, report-only consumer handoff layer that consumes the Day107 parser reviewer evidence contract shape and produces reviewer decision handoff records for the next review phase.

Day108 is a consumer of Day107. It does not replace, revise, or redefine the Day107 source contract.

## Deliverables

- `intent_parser_contract_consumer_handoff.py`
- `tests/test_intent_parser_contract_consumer_handoff.py`
- `docs/ai-intent/day108_parser_contract_consumer_handoff.md`
- `docs/roadmap/day108_parser_contract_consumer_handoff.md`
- `network_lab.py` task: `parser-contract-consumer-handoff`
- `docs/ai-intent/README.md` index entry

## Source Contract Assumption

Day108 references:

```text
source_contract = day107.parser_reviewer_evidence_contract
source_contract_version = day107.parser_reviewer_evidence_contract.v1
consumer_schema_version = day108.parser_contract_consumer_handoff.v1
```

The Day107 contract remains the source of truth for parser reviewer evidence consolidation. Day108 only creates a consumer-facing handoff shape from Day107-style records.

## Acceptance Criteria

Acceptable:

- The new task runs with `python network_lab.py --task parser-contract-consumer-handoff`.
- The task remains report-only.
- Handoff records are deterministic and verifiable.
- Unsafe flags block handoff.
- Consumer schema has an explicit Day107 source contract reference.
- No live execution entry point is introduced.

Not acceptable:

- Redefining the Day107 contract.
- Connecting to real devices.
- Adding SSH.
- Adding OpenAI API calls.
- Allowing approval unlock.
- Adding only docs without tests.
- Adding only tests without a runner task.

## Validation Model

The consumer validator blocks or marks records not ready when:

- Required handoff fields are missing.
- Source contract is unknown.
- Source contract version is empty.
- Consumer schema version is empty.
- Reviewer decision is outside the allowed enum.
- Evidence status is not acceptable for a ready handoff.
- Any live execution, SSH, device connection, command execution, write/config-change, approval unlock, mapped task execution, OpenAI API, or voice flag is true.

Allowed reviewer decisions:

```text
READY_FOR_REVIEW_HANDOFF
NEEDS_REVIEWER_CLARIFICATION
BLOCKED_UNSAFE_OR_UNSUPPORTED
```

## Safety Boundary

Day108 preserves:

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

Rejected or unsafe handoff records do not invoke adapters, brokers, runners, devices, SSH, commands, API clients, approval flows, mapped tasks, or write/config paths.

## Runbook

```powershell
python -m pytest tests/test_intent_parser_contract_consumer_handoff.py
python network_lab.py --task parser-contract-consumer-handoff
python network_lab.py --task report-index
python network_lab.py --report-index
```

Expected report outputs:

```text
reports/lab-summary/day108_parser_contract_consumer_handoff.json
reports/lab-summary/day108_parser_contract_consumer_handoff.html
```
