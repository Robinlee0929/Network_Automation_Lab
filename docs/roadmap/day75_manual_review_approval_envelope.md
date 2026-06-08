# Day75 Manual Review Approval Envelope

## Day75 Goal

Add a deterministic, mock-only, dry-run-only manual review approval envelope
layer after Day74.

The layer simulates reviewer sign-off records for the existing Day74 dry-run
plans. It is not an execution approval system.

## What Day75 Adds

- `intent_manual_review_approval_envelope.py`
- `manual-review-approval-envelope` runner task
- JSON and HTML report output
- Static/read-only dashboard visibility
- Reviewer documentation and roadmap notes
- Tests for determinism, invariants, report generation, dashboard visibility,
  and absent unsafe runtime surfaces

## Approval Envelope Definition

An approval envelope is a structured reviewer evidence record. It connects a
Day73 scenario and Day74 dry-run plan to a simulated reviewer state and decision.

It can record:

- source scenario and dry-run plan identifiers
- reviewer sign-off state
- reviewer decision label
- required review items
- preserved safety invariants
- execution policy showing only record-only evidence is allowed

It must not run commands, call an AI provider, access devices, execute mapped
tasks, submit dashboard approval, or change network configuration.

## Required Invariants

- `allowed_to_execute` is always `false`.
- `dry_run_only` is always `true`.
- `execution_unlock_supported` is always `false`.
- `approved_for_record_only` remains record-only.
- `rejected_for_review_gap` remains blocked from execution.
- `requires_manual_follow_up` remains stopped for human review.
- `blocked_live_action` preserves the live-action block.

## Safety Boundaries

Day75 must not add:

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
- Approval or execution controls.
- Action endpoints.
- Approval mechanisms that unlock execution.
- Router, switch, firewall, VPN, VRRP, or network configuration changes.

## Expected Reports

```text
reports/lab-summary/day75_manual_review_approval_envelope.json
reports/lab-summary/day75_manual_review_approval_envelope.html
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
python network_lab.py --task manual-review-approval-envelope
```

## Acceptance Criteria

Day75 is accepted when:

- One approval envelope is generated for every Day74 dry-run plan.
- Approval envelopes are deterministic.
- Every envelope has `allowed_to_execute=false`.
- Every envelope has `dry_run_only=true`.
- Every envelope has `execution_unlock_supported=false`.
- Reviewer decision labels do not unlock execution.
- JSON and HTML reports are written.
- `/ai-intent-reviewer` shows Day75 docs and report paths without forms, POST
  routes, action endpoints, execution controls, or approval unlocks.

## Future Work

Future work can add richer static reviewer checklists or schema comparisons, but
it must stay explicit about whether it is documentation-only, report-only,
dry-run-only, guarded-live, disabled, or design-only before adding any live lab
behavior.
