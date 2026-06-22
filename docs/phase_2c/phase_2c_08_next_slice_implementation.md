# Phase 2C-08 Next-Slice Implementation

Status: PASS

Final verdict: `PHASE_2C_08_NEXT_SLICE_IMPLEMENTED_LOCAL_REPORT_ONLY`

This artifact implements the selected next slice, `artifact_validation_job`, as a bounded local artifact validation job. It remains report-only, dry-run-only, mock-only, deterministic, and local to repository artifacts.

## Scope Confirmation

SCOPE_CONFIRMATION_WRITTEN: YES

PHASE_NAME_USED: Phase 2C-08 Next-Slice Implementation

SELECTED_NEXT_SLICE: artifact_validation_job

PHASE_GOAL_CONFIRMED: YES

PHASE_2C_06_SELECTION_CONFIRMED: YES

PHASE_2C_07_AUTHORIZATION_CONFIRMED: YES

SCOPE_NARROWED_TO_ONE_EXAMPLE: NO

NEEDS_SCOPE_CONFIRMATION: NO

## Phase Goal

Implement Phase 2C-08 as the approved Next-Slice Implementation. The selected next slice is `artifact_validation_job`.

The goal is to add the smallest verifiable local deterministic artifact validation job capability while preserving the existing project safety boundary.

This phase implements only a bounded local artifact validation job. It does not create a general runner, adapter, execution path, scheduler, queue, broker, worker, or agent loop.

## Selected Next Slice

SELECTED_CANDIDATE_ID: candidate-02

SELECTED_NEXT_SLICE: artifact_validation_job

SELECTED_EXAMPLE_JOB_TYPE: artifact validation job

`artifact_validation_job` is the selected next slice, not merely one example job type.

## Example Job Types

Artifact validation behavior may include examples such as:

- checking that required local documentation artifacts exist
- checking that expected Phase 2C artifacts are present
- checking that task registry or CLI metadata references are internally consistent
- checking that report-only output can be generated deterministically
- checking that local artifact naming or report metadata follows existing repository patterns

These are examples of artifact validation behavior only. Phase 2C-08 is not narrowed to one artifact, one file, one Day1-Day160 entry, one network command, or one device workflow.

## Forbidden Scope

Do not add or enable:

- runner, adapter, or execution path
- scheduler, queue, broker, worker, or agent loop
- SSH, NETCONF, RESTCONF, or live device access
- provider calls, API calls, model calls, or secrets handling
- config backup
- config change
- real command execution
- Day1-Day160 rewrite or replacement
- second safety matrix
- external network access
- non-deterministic behavior

Required preserved flags:

- RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO
- SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO
- SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO
- PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
- CONFIG_BACKUP_OR_CHANGE_ADDED: NO
- DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
- SECOND_SAFETY_MATRIX_CREATED: NO

## Existing Artifacts To Reference

Phase 2C-08 references existing repository artifacts and prior Phase 2C evidence:

- `AGENTS.md`
- `network_lab.py`
- `network_lab_cli_dispatch.py`
- `network_lab_task_registry.py`
- `phase_2c_01_local_static_job_first_slice.py`
- `phase_2c_02_post_first_slice_acceptance_review.py`
- `phase_2c_03_next_slice_decision_gate_authorization_review.py`
- `phase_2c_04_next_slice_candidate_inventory.py`
- `phase_2c_05_next_slice_safety_delta_review.py`
- `phase_2c_06_next_slice_final_selection_gate.py`
- `phase_2c_07_next_slice_implementation_kickoff_gate.py`
- `docs/phase_2c/phase_2c_01_local_static_job_first_slice.md`
- `docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md`
- `docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md`
- `docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md`
- `docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md`
- `docs/phase_2c/phase_2c_06_next_slice_final_selection_gate.md`
- `docs/phase_2c/phase_2c_07_next_slice_implementation_kickoff_gate.md`
- `reports/lab-summary/phase_2c_06_next_slice_final_selection_gate.json`
- `reports/lab-summary/phase_2c_07_next_slice_implementation_kickoff_gate.json`

## Implementation Boundary

Allowed in this task:

- add a bounded local `artifact_validation_job`
- validate fixed local repository artifact paths
- validate Phase 2C-06 local selection evidence
- validate Phase 2C-07 local authorization evidence
- write deterministic JSON/HTML reviewer reports
- update required task registry, CLI, report-index, and tests

Not allowed in this task:

- create a general runner, adapter, execution path, scheduler, queue, broker, worker, or agent loop
- touch SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets
- add config backup, config change, or real command execution
- rewrite or replace Day1-Day160 artifacts
- create a second safety matrix

## Validation Method

The job validates local repository artifacts only.

It checks a fixed list of local paths for required source, docs, and prior Phase 2C JSON reports.

It checks the Phase 2C-06 report confirms `artifact_validation_job` was selected while implementation remained locked.

It checks the Phase 2C-07 report confirms `artifact_validation_job` was authorized for Phase 2C-08 while implementation had not started.

It writes deterministic JSON and HTML reports under `reports/lab-summary/`.

## Report-Only / Dry-Run / Mock-Only Behavior

Machine-readable boundary:

```text
AGENTS_MD_FOUND: YES
AGENTS_MD_READ_BEFORE_ACTION: YES
AGENTS_MD_MODIFIED: NO
PHASE_NAME_USED: Phase 2C-08 Next-Slice Implementation
SELECTED_NEXT_SLICE: artifact_validation_job
PHASE_GOAL_CONFIRMED: YES
PHASE_2C_06_SELECTION_CONFIRMED: YES
PHASE_2C_07_AUTHORIZATION_CONFIRMED: YES
SCOPE_NARROWED_TO_ONE_EXAMPLE: NO
NEEDS_SCOPE_CONFIRMATION: NO
ARTIFACT_VALIDATION_JOB_IMPLEMENTED: YES
LOCAL_ONLY: YES
DETERMINISTIC: YES
REPORT_ONLY_DRY_RUN_MOCK_ONLY: YES
RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO
SCHEDULER_QUEUE_BROKER_WORKER_AGENT_LOOP_ADDED: NO
SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO
PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
CONFIG_BACKUP_OR_CHANGE_ADDED: NO
DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
```

## Final Verdict

`PHASE_2C_08_NEXT_SLICE_IMPLEMENTED_LOCAL_REPORT_ONLY`
