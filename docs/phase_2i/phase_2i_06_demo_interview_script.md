# Phase 2I-06 - Demo Interview Script

Status: PASS

Final phase decision: `READY_FOR_PHASE_2I_09`

## Decision Summary

Phase 2I-06 creates a static demo interview script for explaining the Network Automation Lab during a portfolio review, interview, demo walkthrough, or reviewer-facing presentation.

The script is documentation-only. It does not implement demo runtime behavior, create demo aliases, create demo flows, change runner, job, adapter, scheduler, queue, broker, worker, or agent-loop behavior, add AI execution, call a provider/API/model, touch secrets, access live devices, use SSH, NETCONF, or RESTCONF, perform config backup, or perform config change behavior.

## Task Mode

```text
TASK_MODE: DEMO_SCRIPT_DOCUMENTATION_ONLY
PHASE: Phase 2I-06 - Demo Interview Script
DOCUMENTATION_ONLY: YES
STATIC_SCRIPT_ONLY: YES
IMPLEMENTATION_BEHAVIOR_CHANGED: NO
RUNTIME_BEHAVIOR_CHANGED: NO
DEFAULT_SAFETY_BASELINE: REPORT_ONLY_DRY_RUN_MOCK_ONLY
```

## Script Purpose

This script helps a reviewer understand the project safely and quickly.

It explains what the lab demonstrates, how to read the static dashboard evidence, what AI is allowed to explain, and what AI is forbidden to control. It gives the presenter clear wording for safety boundaries without implying runtime execution.

## Audience

- Portfolio reviewers
- Interviewers
- Hiring managers
- Technical reviewers
- Demo walkthrough participants

## Demo Opening Statement

This project is a safe, local, deterministic network automation lab. It focuses on reviewer-visible evidence, dry-run planning, mock-only flows, static dashboard copy, and report-only validation.

For this demo, the important point is that the dashboard and documentation are evidence surfaces. They help a reviewer understand the project. They do not control devices.

## Project Summary In Plain Language

The Network Automation Lab shows how network validation can be made reviewable before any live-capable workflow is trusted.

The project records evidence in local files, reports, and static dashboard pages. Those artifacts make the safety boundary visible to a reviewer: what is allowed, what is blocked, what is report-only, and what remains future work.

The current Phase 2I work adds clearer AI introduction wording and a safe interview script. It does not turn AI into an operator, controller, runner, broker, adapter, or executor.

## Safe AI Role Explanation

AI is allowed only as static explanation, review, and documentation support for committed evidence.

In this project, safe AI wording can:

- explain committed reports
- summarize static dashboard copy
- clarify safety boundaries
- help a reviewer understand existing evidence
- support mock-only demo narrative
- help draft documentation that remains non-executing

AI is not the control plane. AI does not approve itself. AI does not bypass manual reviewer interpretation.

## Forbidden AI Role Explanation

AI is not a controller.

In the project runtime/demo design, AI does not execute tools, jobs, commands, model calls, provider calls, or device operations. AI does not use SSH, NETCONF, RESTCONF, live discovery, external automation, secrets, config backup, or config change behavior.

This statement describes the lab/demo safety model. It does not restrict normal Codex development actions needed to edit documentation, inspect git state, or run safe deterministic checks for this documentation-only task.

## Dashboard Explanation

The dashboard is static and read-only.

It explains committed local evidence and report summaries. It does not connect to a live data source, runner, adapter, execution system, provider, API, model, secret store, SSH, NETCONF, or RESTCONF.

The dashboard is useful because it gives reviewers a single place to see the safety boundary before they inspect individual reports or phase documents.

## Static Evidence Explanation

The safe control object is evidence, report, and dashboard copy.

The safe control object is not a router, switch, session, interface, device command, job runner, adapter, queue, broker, worker, scheduler, agent loop, provider, model, secret, backup process, or configuration change.

Static evidence means the reviewer is reading committed documentation and static dashboard content. The dashboard may name optional local artifacts, but it does not probe the filesystem, discover artifacts, refresh reports, fetch data, recover missing files, or execute anything.

## Safety Boundary Explanation

The demo boundary is intentionally conservative:

- local deterministic files only
- report-only, dry-run, and mock-only framing
- static dashboard and documentation evidence
- manual reviewer interpretation
- no live device access
- no SSH, NETCONF, or RESTCONF
- no external API, provider, or model call
- no secrets or credentials handling
- no config backup or config change
- no runner, job, adapter, scheduler, queue, broker, worker, or agent-loop behavior change

This boundary keeps the demo safe for portfolio review. It also makes the future automation boundary easier to evaluate because current evidence does not hide execution behavior behind presentation copy.

## What This Demo Does Not Do

This demo does not:

- execute network commands
- open live sessions
- contact routers, switches, APIs, providers, or models
- run AI as an agent loop
- create a demo alias
- create a demo flow implementation
- modify runtime behavior
- modify runner, job, adapter, scheduler, queue, broker, worker, or agent-loop behavior
- start Phase 2I-09, Phase 2I-13, Phase 2I-18, or Phase 2J
- perform config backup or config change behavior
- rewrite Day1-Day160 artifacts
- create a second safety matrix

## Suggested Interview Q&A

### What is this project?

It is a safe network automation lab that emphasizes reviewer-visible evidence. The project demonstrates structured validation, static reports, dry-run planning, mock-only boundaries, and explicit safety gates before any live-capable behavior is trusted.

### What does the dashboard demonstrate?

The dashboard demonstrates static reviewer evidence. It shows report summaries, artifact references, missing-artifact messaging, and AI boundary wording as committed copy. It does not run automation or collect live data.

### What is AI allowed to do here?

AI may help explain committed evidence, summarize reports, clarify safety boundaries, and support documentation. AI remains a static explanation and review aid.

### What is AI not allowed to do here?

AI is not allowed to act as a controller. It does not execute tools, jobs, commands, model calls, provider calls, or device operations in the project runtime/demo design.

### Does the demo touch live devices?

No. The demo touches no live device, no SSH session, no NETCONF or RESTCONF session, no provider/API/model call, no secret, no config backup, and no config change.

### Why keep the demo static?

A static demo makes the safety boundary auditable. Reviewers can inspect the exact committed evidence without wondering whether a hidden runtime action changed the result.

### What remains future work?

Phase 2J remains future non-device automation control work. Phase 2I-06 does not start Phase 2J and does not implement a job contract, policy gate, approval envelope, local job runner, or validation job.

## Reviewer Talking Points

- Start with safety: the project is local, deterministic, report-only, dry-run, and mock-only unless a later approved gate says otherwise.
- Point to the dashboard as static evidence, not a control surface.
- Explain AI as review and documentation support only.
- Say clearly that AI is not a controller.
- Emphasize that no live device access, SSH, NETCONF, RESTCONF, provider/API/model call, secret, config backup, or config change is allowed.
- Close by noting that Phase 2J is future work and is not implemented by this script.

## Review Sources

- `AGENTS.md`
- `README.md`
- `docs/phase_2i/phase_2i_00_ai_introduction_dashboard_refresh_scope_review.md`
- `docs/phase_2i/phase_2i_01_ai_introduction_dashboard_refresh_authorization.md`
- `docs/phase_2i/phase_2i_02_ai_introduction_dashboard_refresh.md`
- `docs/phase_2i/phase_2i_03_ai_introduction_dashboard_refresh_acceptance_review.md`
- `docs/phase_2h/phase_2h_06_evidence_report_dashboard_static_shell.html`
- `phase_2h_06_evidence_report_dashboard_static_shell.py`
- `tests/test_phase_2h_06_evidence_report_dashboard_static_shell.py`

## Documentation Readability Review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
CLEAR_HEADINGS: PASS
SHORT_PARAGRAPHS: PASS
PLAIN_LANGUAGE: PASS
SAFETY_WORDING_UNAMBIGUOUS: PASS
NO_RUNTIME_IMPLICATION: PASS
NO_AI_CONTROLLER_IMPLICATION: PASS
NO_PROVIDER_API_MODEL_IMPLICATION: PASS
NO_OVERBROAD_CLAIMS_BEYOND_CURRENT_REPOSITORY_STATE: PASS
NO_UNRELATED_PHASE_EXPANSION: PASS
CONSISTENT_PHASE_2I_06_NAMING: PASS
CONSISTENT_PROGRESS_WORDING_WITH_README_CONVENTION: PASS
FINAL_READABILITY_RESULT: PASS
```

The document starts with the decision, separates allowed and forbidden scope, keeps safety wording explicit, avoids long paragraphs, uses consistent status labels, and does not weaken the repository safety boundary.

## Tests And Checks Run

```text
git diff --check
RESULT: PASS - no whitespace errors; Git emitted the normal README LF-to-CRLF working-copy warning.

python network_lab.py --task report-index
RESULT: WARN - exit 0; 11 PASS, 0 FAIL, 1 optional MISSING for Hex-s-2025-lab02 Day8 iperf3 report.

python -m pytest tests/test_phase_2h_06_evidence_report_dashboard_static_shell.py
RESULT: PASS - 15 passed in 0.14s.

python -m pytest
RESULT: FAIL - collection stopped on the pre-existing tolerated untracked codex_pytest_tmp_phase_2h_08/ directory with PermissionError before project test execution completed.

git diff --name-only
RESULT: PASS - tracked unstaged diff limited to README.md before final documentation artifact update; the new Phase 2I-06 artifact was visible as the intended untracked file in git status.

git diff --cached --name-only
RESULT: PASS - no staged files before final staging.
```

## Safety Boundary Confirmation

```text
DOCUMENTATION_ONLY: YES
STATIC_DEMO_INTERVIEW_SCRIPT_ONLY: YES
LOCAL_DETERMINISTIC_FILES_ONLY: YES
REPORT_ONLY_DRY_RUN_MOCK_ONLY: YES
IMPLEMENTATION_BEHAVIOR_CHANGED: NO
RUNTIME_BEHAVIOR_CHANGED: NO
RUNNER_JOB_ADAPTER_CHANGED: NO
SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO
AI_EXECUTION_ADDED: NO
REPOSITORY_RUNTIME_AI_TOOL_CALL_BEHAVIOR_ADDED: NO
MCP_ADDED: NO
LIVE_DEVICE_ACCESS_ADDED: NO
SSH_NETCONF_RESTCONF_ADDED: NO
EXTERNAL_API_PROVIDER_MODEL_CALL_ADDED: NO
SECRETS_TOUCHED: NO
CONFIG_BACKUP_CHANGE_BEHAVIOR_ADDED: NO
DEMO_ALIAS_ADDED: NO
DEMO_FLOW_IMPLEMENTATION_ADDED: NO
PHASE_2I_09_STARTED: NO
PHASE_2I_13_STARTED: NO
PHASE_2I_18_STARTED: NO
PHASE_2J_STARTED: NO
DAY1_DAY160_REWRITTEN: NO
SECOND_SAFETY_MATRIX_CREATED: NO
PRE_EXISTING_UNTRACKED_PATHS_TOUCHED: NO
```

## Final Decision

```text
FINAL_PHASE_DECISION: READY_FOR_PHASE_2I_09
DEMO_INTERVIEW_SCRIPT_CREATED: YES
SCRIPT_SCOPE_CONFIRMED: DOCUMENTATION_ONLY
AI_ALLOWED_ROLE_CLEAR: YES
AI_FORBIDDEN_ROLE_CLEAR: YES
PROJECT_RUNTIME_DEMO_AI_EXECUTION_WORDING_CLEAR: YES
CODEX_DEVELOPMENT_ACTION_CLARIFICATION_INCLUDED: YES
DASHBOARD_STATIC_READ_ONLY_CLEAR: YES
SAFE_CONTROL_OBJECT_CLEAR: YES
LIVE_DEVICE_ACCESS_FORBIDDEN_CLEAR: YES
FORBIDDEN_SCOPE_TOUCHED: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

## Next Phase Readiness

Phase 2I-06 is ready for Phase 2I-09 only as the next separately requested phase.

This artifact does not implement or authorize Phase 2I-09, Phase 2I-13, Phase 2I-18, Phase 2J, or any later work.
