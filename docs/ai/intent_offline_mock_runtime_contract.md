# AI Intent Offline Mock Runtime Contract

## Purpose

Day67 defines a fixed output contract for the Day66 offline mock runtime.

The contract exists so reviewers can confirm that future AI, voice, SSH, or live execution work cannot silently weaken the current safety boundary. It validates only in-memory mock runtime result dictionaries.

Day67 does not enable AI, voice, SSH, device access, live execution, mapped task execution, arbitrary command execution, or network configuration changes.

## Required Fields

Each scenario result must include:

- `scenario_id`
- `scenario_name`
- `intent_category`
- `execution_mode`
- `safety_category`
- `decision`
- `live_execution_allowed`
- `mapped_task_executed`
- `blocked`
- `reviewer_warning`
- `evidence_references`

## Allowed Execution Modes

The validator accepts only:

- `offline_mock`
- `dry_run_only`

Any other execution mode fails contract validation.

## Allowed Safety Categories

The validator accepts only Day66-compatible mock and reviewer categories:

- `documentation_only`
- `report_only`
- `blocked_live_action`
- `needs_manual_review`

New categories must be added deliberately with tests and documentation before they can pass validation.

## Blocked Action Handling

Blocked live-action scenarios must satisfy all of these rules:

- `blocked` is `True`.
- `live_execution_allowed` is `False`.
- `mapped_task_executed` is `False`.
- `reviewer_warning` is non-empty.
- `evidence_references` contains at least one non-empty reference.

This makes blocked live-action examples reviewer-visible instead of silently ignored.

## Reviewer Evidence Requirements

`evidence_references` must be a list of non-empty text references.

The references should point to committed documentation or report paths that explain why the scenario is allowed, blocked, or held for manual review.

## Safety Invariants

The validator enforces these invariants:

- `live_execution_allowed` must always be `False`.
- `mapped_task_executed` must always be `False`.
- `execution_mode` must be `offline_mock` or `dry_run_only`.
- Blocked live-action scenarios must remain blocked.
- Blocked live-action scenarios must have reviewer warning text.
- Blocked live-action scenarios must have evidence references.
- Scenario flags must not imply SSH, device access, API access, voice integration, live execution, mapped task execution, or network configuration changes.

## Future Extension Rules

Future changes must keep the validator deterministic and standard-library-only.

Future AI, voice, SSH, device, or live execution planning must not bypass this contract. Any new allowed field, execution mode, safety category, or decision value should be added with tests that prove live execution and mapped task execution remain rejected by default.

## Explicit Non-Enablement Statement

Day67 is a validation layer only.

It does not add:

- OpenAI API integration.
- Voice integration.
- SSH.
- Device access.
- Live execution.
- Mapped task execution.
- `config.json` dependency.
- Arbitrary command execution.
- Dashboard form submission.
- POST action route.
- Action endpoint.
- Router, switch, firewall, VPN, VRRP, or network configuration changes.
