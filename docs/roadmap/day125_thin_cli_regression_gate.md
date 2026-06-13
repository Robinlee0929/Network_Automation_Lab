# Day125 Thin CLI Regression Gate

## Goal

Create a report-only regression gate proving that Day120-Day124 did not regress
the thin CLI split, task registry, dispatch behavior, report visibility,
formatter shape, or shared safety helper invariants.

## Deliverables

- `intent_thin_cli_regression_gate.py`
- CLI task: `python network_lab.py --task thin-cli-regression-gate`
- JSON report: `reports/lab-summary/day125_thin_cli_regression_gate.json`
- HTML report: `reports/lab-summary/day125_thin_cli_regression_gate.html`
- Report-index visibility
- Tests for AGENTS.md evidence, thin CLI boundaries, registry and dispatch
  invariants, safety flags, report shape, and report-index discovery

## Safety Rules

Day125 must not add:

- Live device access
- SSH
- Live command execution
- Configuration-changing commands
- OpenAI API or AI SDK runtime
- Voice input, speech-to-text, text-to-speech, or microphone use
- Dashboard POST routes, forms, or action endpoints
- Broker, runner, adapter, mapped task, approval, or execution unlock paths

## Acceptance

The Day125 task is accepted only when:

- `overall_status` is `PASS`
- `agents_md_pre_read_result` is `PASS`
- `agents_md_read_before_day125_work` is `true`
- Thin CLI, registry, dispatch, report/formatter, safety helper, and smoke
  regression sub-gates are all `PASS`
- `allowed_to_execute`, `ssh_allowed`, and `live_command_allowed` remain `false`
- `next_phase_allowed` remains `false`
- `network_lab.py` only performs minimal Day125 wiring and delegates gate logic
  to `intent_thin_cli_regression_gate.py`

## Validation

```bash
python network_lab.py --task thin-cli-regression-gate
python network_lab.py --task report-index
python network_lab.py --report-index
python -m pytest
git status --short --branch
```
