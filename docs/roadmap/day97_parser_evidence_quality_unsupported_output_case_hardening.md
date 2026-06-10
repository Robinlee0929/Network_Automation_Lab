# Day97 Parser Evidence Quality / Unsupported Output Case Hardening

## Scope

Day97 builds on Day96 by adding a parser-only evidence hardening layer for unsupported, incomplete, malformed, ambiguous, empty, and degraded output cases.

The goal is reviewer evidence quality. Day97 does not expand supported device behavior and does not replace the Day96 parser prototype.

## Non-goals

- No real device access
- No SSH
- No RouterOS command execution
- No live-read capability
- No write/config capability
- No `config.json` dependency
- No credentials
- No POST route, dashboard form, execution button, approval action, or unlock action
- No OpenAI API, AI SDK runtime, voice runtime, or agent execution
- No mapped task execution

## Deliverables

- `intent_parser_evidence_quality.py`
- Runner task `parser-evidence-quality`
- JSON report at `reports/ai/day97_parser_evidence_quality_report.json`
- HTML report at `reports/ai/day97_parser_evidence_quality_report.html`
- AI documentation at `docs/ai/intent_parser_evidence_quality.md`
- Roadmap documentation at `docs/roadmap/day97_parser_evidence_quality_unsupported_output_case_hardening.md`
- Pytest coverage for static fake cases, unsupported classifications, safety flags, runner output, report-index visibility, and forbidden live-access imports

## Acceptance Criteria

- Empty, whitespace-only, malformed, missing, partial, mixed, duplicate, contradictory, and unsupported output cases are represented.
- Unsupported output is classified as parser evidence such as `UNSUPPORTED_OUTPUT`, not `FAILED_EXECUTION`.
- Every case includes `case_id`, `case_name`, `input_source`, `command_family`, `raw_output_present`, `parser_supported`, `parser_status`, `unsupported_reason`, `evidence_quality`, `reviewer_action`, and `safety_flags`.
- `live_read_allowed`, `ssh_allowed`, `write_allowed`, `command_execution_allowed`, `raw_command_allowed`, `device_contact_allowed`, `approval_unlock_supported`, and `mapped_task_execution_allowed` are always `false`.
- Runner returns `PASS / HARDENED`.
- Reports are generated under `reports/ai/`.
- Report index can find the generated Day97 reports.

## Correct Route

Day96 parser-only prototype -> Day97 static fake unsupported-output hardening -> reviewer evidence quality report.

The wrong route remains prohibited: RouterOS / SSH / live command / config write / approval unlock -> Day97 parser.

## Run

```text
python network_lab.py --task parser-evidence-quality
python network_lab.py --task report-index
```
