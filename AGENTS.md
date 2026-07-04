# AGENTS.md

## Project

This repository is a Network Automation Lab and automated testing platform for safe, reviewer-visible network validation.

The project emphasizes offline portfolio review, structured evidence, dry-run planning, mock execution, read-only validation, and explicit safety gates before any live-capable workflow is introduced.

## Core Safety Rules

- Do not perform live device access unless a future approved safety gate explicitly allows it and the user separately approves the specific live operation.

- Do not use SSH, API calls, or real network-device commands unless a future approved safety gate explicitly allows it and the user separately approves the specific live operation.
- Do not execute configuration-changing commands.
- Do not run reset, reboot, remove, disable, enable, or similarly destructive operations.
- Rejected intents must not invoke adapters, brokers, runners, or execution paths.
- Dry-run, mock-only, report-only, documentation-only, and design-only tasks must remain non-executing.
- Preserve safety gates, reviewer evidence, and no-execution proof.
- Do not add secrets, credentials, tokens, private local memory, private paths, or personal environment details to the repository.
- Do not add OpenAI API calls, external AI runtime, voice input, speech-to-text, text-to-speech, microphone, or cloud execution unless a future task explicitly approves a separate safety gate.
- Do not push, merge, tag, deploy, or publish changes without explicit user approval.

## Standard Validation

Before considering work complete, run:

```bash
python -m pytest
python network_lab.py --task report-index
```

If the task has a dedicated runner, also run:

```bash
python network_lab.py --task <task-name>
```

For report-only tasks, `report-index` may return WARN when optional local runtime reports are missing. Treat WARN as acceptable only when the warning is documented and does not indicate a safety or regression issue.

## Git Workflow

- Use a dedicated feature branch for each day or task when branch work is requested.
- Keep changes focused.
- Commit only source code, tests, docs, and intended static report references.
- Do not commit local runtime artifacts, credentials, private memory files, or generated files unless they are deterministic, non-sensitive, explicitly requested, and intentionally part of reviewer evidence.
- After merge, rerun validation on `main`.
- Before push, check:

```bash
git status --short --branch
```

## Documentation Expectations

- Update relevant docs when adding a task, safety rule, runner, dashboard entry, report, or reviewer workflow.
- Keep reports and evidence traceable.
- Prefer explicit PASS, WARN, FAIL, BLOCKED, REVIEW_ONLY, LOCKED, or equivalent status fields.
- Explain safety boundaries in reviewer-facing language.
- Keep public documentation safe for GitHub publication.

## Documentation Readability Review

Before closing any phase, acceptance review, or closure document, contributors must perform a documentation readability review.

The review must verify:

- The document starts with a clear conclusion or decision summary.
- The phase purpose is understandable without relying on hidden context.
- Allowed scope and forbidden scope are clearly separated.
- Safety boundaries are explicit and not weakened.
- Status labels are consistent across README and phase documents.
- Acceptance criteria are concrete and verifiable.
- Long paragraphs are split into readable sections.
- Terminology is consistent with the current project glossary and previous phase documents.

This review is documentation-only. It must not introduce implementation behavior, runtime behavior, runner behavior, adapter behavior, execution behavior, scheduler / queue / broker / worker / agent loop behavior, AI execution, MCP, live access, SSH, NETCONF, RESTCONF, external API / provider / model calls, secrets handling, config backup/change, Day1-Day160 rewrites, or a second safety matrix.

## Testing Expectations

- Add or update tests for new behavior.
- Safety gates must include negative tests.
- Rejected scenarios must prove no execution path was reached.
- Mock, dry-run, report-only, documentation-only, and design-only flows should not require live devices, SSH, VPN, WireGuard, external services, or private config files.
- Dashboard or report-index changes should include visibility tests where applicable.

## Done Criteria

Work is done only when the requested source, test, documentation, and report-index updates are complete; required validation commands have been run or clearly documented if unavailable; generated evidence remains reviewer-facing; and no safety gate, secret rule, or no-execution proof has been weakened.

## Codex Task Protocol

### Task modes

Each task must be classified before action as one of:

* read-only
* planning-only
* implementation
* review-only
* documentation-only
* polish
* merge / push / sync
* AGENTS.md update

If the task mode is unclear, Codex must stop before editing and report:

`NEEDS_TASK_MODE_CONFIRMATION`

### Mandatory setup for every task

Before taking action, Codex must:

1. Read AGENTS.md.
2. Report whether AGENTS.md was found before action.
3. Report whether AGENTS.md was read before action.
4. Confirm the current branch.
5. Confirm git status.
6. Identify the task mode.
7. Identify the requested phase or scope.
8. Keep the task limited to the requested scope.

AGENTS.md must not be modified unless the task is explicitly an AGENTS.md update task.

### Branch rules

For implementation, planning-only, review-only, documentation-only, polish, and AGENTS.md update tasks:

* Work on a feature branch.
* Do not work directly on main unless the user explicitly asks for a read-only check or a merge / push / sync task.
* Do not start the next phase.
* Do not select extra slices.
* Do not implement extra slices.

For read-only tasks:

* Do not create a branch unless the user asks.
* Do not modify files.
* Do not commit.

For merge / push / sync tasks:

* Confirm remote trust before pushing.
* Confirm branch and git status before the operation.
* Do not create new implementation changes.
* Do not modify files unless merge conflict resolution is required.
* Report whether any commit was created during the sync step.

### Default safety baseline

Unless a task explicitly authorizes a different safety level, all work must remain:

* report-only
* dry-run
* mock-only

The following are forbidden by default:

* No SSH execution.
* No NETCONF execution.
* No RESTCONF execution.
* No live device access.
* No provider / API / model integration.
* No secrets handling.
* No queue.
* No scheduler.
* No worker.
* No AI agent loop.
* No config backup execution.
* No config change execution.
* No production execution path.
* No Day1-Day160 rewrite or replacement.
* No second safety matrix.

### Safety override rule

A task may only override the default safety baseline when all of the following are true:

1. The user explicitly authorizes the safety change in the task prompt.
2. The phase goal explicitly requires the safety change.
3. The task defines the allowed boundary.
4. The task defines validation requirements.
5. Codex reports the safety change clearly before implementation.

If any of these are missing, Codex must stop and report:

`NEEDS_SCOPE_CONFIRMATION`

### Scope confirmation before implementation

Before implementation, Codex must confirm the scope in writing and clearly separate:

* task mode
* phase goal
* example job types, if any
* forbidden scope
* existing artifacts to reference
* implementation boundary
* validation plan

Codex must not implement yet if the task title, branch name, file name, or implementation goal narrows a broader phase to only one example.

If the scope appears narrower than the phase goal, Codex must stop and report:

`NEEDS_SCOPE_CONFIRMATION`

### Implementation boundary

Codex must only implement files and behavior required for the current task.

Codex must not:

* start the next phase
* select the next slice unless explicitly asked
* implement extra slices
* add production execution paths
* add live execution paths
* broaden examples into platform behavior unless explicitly authorized
* rewrite historical artifacts unless explicitly authorized

### Validation requirements

Codex must run the targeted pytest for the current phase when tests exist.

Codex must run report-index validation when available.

Codex must run full pytest when the change affects:

* task registry
* CLI dispatch
* runner behavior
* adapter behavior
* report rendering
* shared utilities
* cross-phase behavior
* safety validation behavior

Codex must report exact commands and exact results.

If validation cannot be run, Codex must report:

`VALIDATION_NOT_RUN`

and explain the reason.

### Final report format

Every task must end with this report:

* TASK_RESULT: DONE or BLOCKED
* Task mode:
* AGENTS.md found before action: YES/NO
* AGENTS.md read before action: YES/NO
* AGENTS.md modified: YES/NO
* AGENTS.md modification authorized: YES/NO
* Required reference documents read: YES/NO/N/A
* Current branch:
* Git status before action:
* Git status after action:
* Files changed:
* Commit hash:
* Tests run:
* Test results:
* Report-index result:
* Full pytest run: YES/NO
* Full pytest result:
* Forbidden scope touched: YES/NO
* SSH/NETCONF/RESTCONF/live device touched: YES/NO
* queue/scheduler/worker/AI loop added: YES/NO
* provider/API/model/secrets touched: YES/NO
* config backup/change behavior added: YES/NO
* production execution path added: YES/NO
* Day1-Day160 rewritten/replaced: YES/NO
* Second safety matrix created: YES/NO
* Next phase started: YES/NO
* Extra slice selected or implemented: YES/NO

### Stop conditions

Codex must stop and report BLOCKED, NEEDS_TASK_MODE_CONFIRMATION, NEEDS_SCOPE_CONFIRMATION, or BLOCKED_REFERENCE_DOCUMENT_MISSING if:

* AGENTS.md is missing and the task requires repository guidance.
* The task mode is unclear.
* The task asks for implementation but only provides a vague goal.
* The task title, branch name, file name, and phase goal conflict.
* The task would require forbidden scope without explicit authorization.
* The task would touch live device access, SSH, NETCONF, RESTCONF, secrets, provider/API/model integration, queue, scheduler, worker, or AI agent loop without explicit authorization.
* The task would rewrite Day1-Day160 artifacts.
* The task would create a second safety matrix.
* A required reference document is missing.
* Required validation cannot be run and no acceptable reason is available.

### Repository discipline

Codex must keep changes small and reviewable.

Prefer:

* one task
* one branch
* one phase
* one clear commit
* targeted tests
* explicit validation report

Avoid:

* large mixed-purpose commits
* hidden refactors
* unrelated cleanup
* speculative architecture
* unrequested production behavior
* unrequested UI or dashboard work

## Required Reference Documents

Codex must read additional reference documents when the task scope matches them.

### Actual automation integration

For any task involving real automation, live device access, read-only lab integration, runner behavior, adapter behavior, execution path design, SSH, NETCONF, RESTCONF, device inventory, credential reference, command allowlist, queue, scheduler, worker, AI agent loop, or production-like automation, Codex must read this file before scope confirmation:

`docs/automation_readiness/actual_automation_integration_plan.md`

Codex must report whether the file was found and read before scope confirmation.

If the file is required but missing or unreadable, Codex must stop and report:

`BLOCKED_REFERENCE_DOCUMENT_MISSING`

This reference document does not authorize real automation by itself.
It only defines readiness gates and boundaries for future phases.

For tasks that do not involve actual automation integration, Codex may report:

`Required reference documents read: N/A`
