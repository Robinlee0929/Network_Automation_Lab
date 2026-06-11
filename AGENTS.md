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

## Testing Expectations

- Add or update tests for new behavior.
- Safety gates must include negative tests.
- Rejected scenarios must prove no execution path was reached.
- Mock, dry-run, report-only, documentation-only, and design-only flows should not require live devices, SSH, VPN, WireGuard, external services, or private config files.
- Dashboard or report-index changes should include visibility tests where applicable.

## Done Criteria

Work is done only when the requested source, test, documentation, and report-index updates are complete; required validation commands have been run or clearly documented if unavailable; generated evidence remains reviewer-facing; and no safety gate, secret rule, or no-execution proof has been weakened.
