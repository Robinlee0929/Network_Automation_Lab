# Day74 Controlled Dry-run Plan Builder

Day74 adds a deterministic dry-run plan builder after the Day73 mock AI
decision pipeline.

The builder converts Day73 mock decision records into reviewer-friendly dry-run
plans. A dry-run plan is only a structured preview for inspection. It is not an
execution flow, not an approval path, and not a runtime.

## Connection To Day72 And Day73

Day72 validates controlled AI runtime input payloads. It blocks unsafe payloads
and always keeps `execution_allowed` false.

Day73 consumes those Day72 validation results and produces deterministic mock
decision records. It labels documentation-only, report-only, review-required,
blocked live-action, and invalid-input scenarios without executing anything.

Day74 consumes the Day73 decision records and turns each record into a dry-run
plan preview. It does not weaken the Day72 validator or the Day73 decision
safety rules.

## What A Dry-run Plan Means

A Day74 dry-run plan is reviewer evidence. It can show:

- Preview steps for documentation-only and report-only decisions.
- Reviewer checks for ambiguous or review-required decisions.
- Blocked steps for live-action and invalid-input decisions.
- Evidence references back to Day72, Day73, and Day74.

A dry-run plan cannot execute a mapped task, call an API, open SSH, access a
device, read `config.json`, or change network configuration.

## Plan Status Mapping

| Day73 decision label | Day74 plan status |
| --- | --- |
| `DOCUMENTATION_ONLY` | `DRY_RUN_READY` |
| `REPORT_ONLY` | `DRY_RUN_READY` |
| `REVIEW_REQUIRED` | `REVIEW_REQUIRED` |
| `BLOCKED_LIVE_ACTION` | `BLOCKED` |
| `INVALID_INPUT_BLOCKED` | `INVALID_INPUT_BLOCKED` |

## Plan Record Fields

Each dry-run plan includes:

- `plan_id`
- `source_scenario_id`
- `decision_label`
- `plan_status`
- `allowed_to_execute`
- `dry_run_only`
- `planned_steps`
- `blocked_steps`
- `reviewer_checks`
- `safety_rationale`
- `evidence`
- `next_reviewer_action`

`allowed_to_execute` is always `false`. Day74 is a planning preview, not an
execution stage.

`dry_run_only` is always `true`. The plan can be reviewed, but it cannot be
used to unlock live behavior.

## Blocked Plans

Blocked plans protect against unsafe actions by preserving the Day72-Day73
block. A live-action decision becomes `BLOCKED`; an invalid input decision
becomes `INVALID_INPUT_BLOCKED`.

Blocked plans list the steps that remain forbidden, including mapped task
execution, AI API calls, SSH, device access, arbitrary commands, `config.json`
dependency, and router, switch, firewall, VPN, VRRP, or network configuration
changes.

## Preserved Safety Boundaries

- No OpenAI API.
- No AI SDK dependency.
- No real AI runtime.
- No SSH.
- No device access.
- No live execution.
- No mapped task execution.
- No arbitrary command execution.
- No `config.json` dependency.
- No dashboard form, POST route, action endpoint, or approval mechanism.
- No router, switch, firewall, VPN, VRRP, or network configuration change.

## Generated Reports

Run:

```text
python network_lab.py --task dry-run-plan-builder
```

Outputs:

```text
reports/lab-summary/day74_dry_run_plan_builder.json
reports/lab-summary/day74_dry_run_plan_builder.html
```

## Future Day75 Direction

Day75 could add a deterministic schema validator for Day74 plan records, a
reviewer acceptance checklist for dry-run plans, or a static comparison between
Day66 offline mock plans and Day74 validator-backed plans.

Day75 should remain mock-only, deterministic, and no-execution unless a separate
safety design explicitly approves a new boundary.
