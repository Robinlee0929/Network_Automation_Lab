# Read-only Executor Readiness Gate

Day83 adds a deterministic, offline, review-only readiness gate for the Day79-Day82 read-only safety evidence chain.

This is not the read-only executor. It does not design an executor adapter, execute mapped tasks, open SSH, connect to devices, call an AI runtime, add dashboard actions, or unlock approval or execution.

## Purpose

The gate answers one narrow question:

Is the current Day79-Day82 safety evidence sufficient to mark a request as a read-only executor candidate for future adapter design review?

When the evidence chain passes, the gate reports:

- `overall_status: PASS`
- `readiness_state: READINESS_REVIEW_READY`
- `readonly_executor_candidate: true`
- `executor_allowed: false`

Candidate status only means the request may be considered for a future read-only executor adapter design. It never means execution is allowed.

## Evidence Inputs

Day83 reuses deterministic in-memory builders from the existing modules:

- Day79 `intent_readonly_task_contract.py`: read-only allowlist and blocked action policy.
- Day80 `intent_readonly_execution_broker.py`: non-executing broker records.
- Day81 `intent_broker_review_queue.py`: queue review state and decision state.
- Day82 `intent_reviewer_decision_audit_summary.py`: traceable audit exports.

Existing local Day79-Day82 report files are optional for Day83 tests. Missing optional local reports do not break the readiness gate because the gate validates the committed deterministic modules directly. Day83 itself always writes its own JSON and HTML reports.

## Safety Invariants

The readiness gate requires these flags to remain false:

- `executor_allowed`
- `live_execution_allowed`
- `ssh_allowed`
- `device_access_allowed`
- `ai_runtime_allowed`
- `dashboard_action_allowed`
- `mapped_task_execution_allowed`
- `approval_unlock_allowed`
- `execution_unlock_supported`

The gate also records that no OpenAI API, AI SDK runtime, voice integration, config read, RouterOS command path, external command execution path, dashboard POST route, or network configuration change was added.

## Runner

Run:

```bash
python network_lab.py --task readonly-executor-readiness-gate
```

Reports:

- `reports/lab-summary/day83_readonly_executor_readiness_gate.json`
- `reports/lab-summary/day83_readonly_executor_readiness_gate.html`

The HTML report is static and reviewer-facing. It contains no forms, POST actions, buttons that trigger execution, scripts, or live endpoints.
