# Day125 Thin CLI Regression Gate

Day125 adds a report-only regression gate for the Day120-Day124 split work. It
does not add a new network feature. Its purpose is to prove that the CLI
entrypoint, task registry, dispatch layer, report visibility, formatter shape,
and shared safety helper behavior stayed stable after the split.

## Scope

- Task: `thin-cli-regression-gate`
- Mode: `REPORT_ONLY`
- Overall status: `PASS` when all sub-gates pass
- Final recommendation: `KEEP_THIN_CLI_AND_CONTINUE_REVIEW_ONLY_REGRESSION`
- Reports:
  - `reports/lab-summary/day125_thin_cli_regression_gate.json`
  - `reports/lab-summary/day125_thin_cli_regression_gate.html`

## Required Evidence

The Day125 report records AGENTS.md pre-read evidence with:

- `agents_md_pre_read_result`
- `agents_md_read_before_day125_work`
- `agents_md_path`

If `AGENTS.md` is missing or unreadable, the Day125 gate must report `FAIL`.
It must not mark the pre-read evidence as passed unless the file is readable
and the required instruction sections are present.

## Gate Coverage

Day125 checks these regression surfaces:

- Thin CLI delegation remains in `network_lab.py`
- Registry resolves representative Day120-Day124 affected tasks plus Day125
- Unknown task handling still rejects unsupported names
- Dispatch contains the Day125 handler without a live execution flag
- Report shape keeps stable fields for report-index readability
- Day124 safety invariant helpers still keep dangerous capability flags false
- Representative smoke tasks are resolved without executing live workflows

## Safety Boundary

Day125 is report-only. It does not enable live device access, SSH, live command
execution, configuration changes, OpenAI API calls, voice runtime, dashboard
POST/action endpoints, broker execution, mapped task execution, runtime
unlocks, or next-phase approval.

The report keeps `allowed_to_execute=false`, `ssh_allowed=false`,
`live_command_allowed=false`, `next_phase_allowed=false`,
`live_execution_added=false`, `ssh_added=false`, `openai_api_added=false`, and
`dashboard_execution_endpoint_added=false`.
