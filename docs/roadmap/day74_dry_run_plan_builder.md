# Day74 Controlled Dry-run Plan Builder

## Day74 Goal

Add a deterministic dry-run plan builder after the Day73 mock AI decision
pipeline.

Day72 validates controlled AI runtime input. Day73 produces deterministic mock
AI decision records. Day74 converts those Day73 records into reviewer-friendly
dry-run plans.

Day74 is a decision post-processing layer. It is not a real runtime and does
not execute mapped tasks.

## What Day74 Adds

- `intent_dry_run_plan_builder.py`
- `dry-run-plan-builder` runner task
- JSON and HTML report output
- Static/read-only dashboard visibility
- Reviewer documentation and roadmap notes
- Tests for plan mapping and no-execution safety invariants

## Dry-run Plan Definition

A dry-run plan is a structured preview for reviewer inspection.

It may show planned preview steps, blocked steps, reviewer checks, safety
rationale, evidence references, and the next reviewer action. It must not run
commands, call an AI provider, access devices, execute mapped tasks, or change
network configuration.

## Required Invariants

- `allowed_to_execute` is always `false`.
- `dry_run_only` is always `true`.
- Documentation-only decisions become `DRY_RUN_READY`.
- Report-only decisions become `DRY_RUN_READY`.
- Review-required decisions become `REVIEW_REQUIRED`.
- Blocked live-action decisions become `BLOCKED`.
- Invalid input decisions become `INVALID_INPUT_BLOCKED`.

## Safety Boundaries

Day74 must not add:

- OpenAI API usage.
- AI SDK dependency.
- Real AI runtime behavior.
- Network or device access.
- SSH.
- Live execution.
- Mapped task execution.
- Arbitrary command execution.
- `config.json` dependency.
- Dashboard forms.
- POST routes.
- Action endpoints.
- Approval mechanisms that unlock execution.
- Router, switch, firewall, VPN, VRRP, or network configuration changes.

## Expected Reports

```text
reports/lab-summary/day74_dry_run_plan_builder.json
reports/lab-summary/day74_dry_run_plan_builder.html
```

## Validation Commands

```text
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
python network_lab.py --task offline-mock-runtime
python network_lab.py --task offline-mock-runtime-contract
python network_lab.py --task offline-mock-runtime-review
python network_lab.py --task mock-ai-decision-pipeline
python network_lab.py --task dry-run-plan-builder
```

## Acceptance Criteria

Day74 is accepted when:

- One dry-run plan is generated for every Day73 decision scenario.
- All expected plan statuses are present.
- Every plan has `allowed_to_execute=false`.
- Every plan has `dry_run_only=true`.
- Live action and invalid input scenarios remain blocked.
- Review-required plans include reviewer checks.
- JSON and HTML reports are written.
- `/ai-intent-reviewer` shows Day74 docs and report paths without forms,
  POST routes, action endpoints, execution controls, or approval unlocks.

## Future Day75

Day75 could validate the Day74 plan record schema, add reviewer acceptance
criteria for the Day74 dry-run plans, or compare Day66 offline mock planning
records with Day74 validator-backed dry-run plans.

Future work should remain explicit about whether it is documentation-only,
report-only, dry-run-only, guarded-live, disabled, or design-only before adding
new live behavior.
