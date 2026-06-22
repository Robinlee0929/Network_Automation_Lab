# Phase 2C-06 Next-Slice Final Selection Gate - Planning Only

## Scope Confirmation

SCOPE_CONFIRMATION_WRITTEN: YES
PHASE_2C_04_READ: YES
PHASE_2C_05_READ: YES
FINAL_SELECTION_GATE_ONLY: YES
CANDIDATE_SELECTED: YES
NEXT_SLICE_AUTHORIZED: NO
PHASE_2C_07_STARTED: NO
PHASE_2C_08_STARTED: NO
IMPLEMENTATION_ADDED: NO
RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO
SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO
PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
SECOND_SAFETY_MATRIX_CREATED: NO

## Phase Goal

Select exactly one next-slice candidate from the Phase 2C-04 candidate inventory, using the Phase 2C-05 safety delta review as the required safety input.

This phase may select the next slice. It does not authorize implementation, start Phase 2C-07, start Phase 2C-08, scaffold the selected slice, or implement the selected slice.

## Candidate Source

Use only:

- `docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md`
- `phase_2c_04_next_slice_candidate_inventory.py`
- `docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md`
- `phase_2c_05_next_slice_safety_delta_review.py`

No unrelated new candidates are added. No candidate requiring expanded forbidden scope is selected.

## Example Job Types

These remain example job types from Phase 2C-04:

- `local_static_job` continuation
- artifact validation job
- report-only evidence collection job
- dry-run result rendering job
- mock parse/report job
- candidate UI display contract follow-up
- candidate safety regression follow-up

## Selection Criteria

The selected next slice is chosen based on:

- lowest safety delta
- smallest implementation boundary
- strongest alignment with existing report-only / dry-run / mock-only constraints
- no need for SSH, NETCONF, RESTCONF, live-device access, provider/API/model calls, or secrets
- no need for runner, adapter, scheduler, queue, broker, worker, or agent loop
- no Day1-Day160 rewrite or replacement
- no second safety matrix
- clear targeted validation path
- ability to remain minimal and verifiable in a later implementation phase

## Safety Delta Dependency

Phase 2C-05 is the required safety input. It reports that all Phase 2C-04 candidates have no new safety delta within the planning boundary.

The selected candidate, `candidate-02`, has:

- example job type: artifact validation job
- Phase 2C-05 delta status: no new safety delta within planning boundary
- expanded forbidden scope required: no

Because Phase 2C-05 does not show unacceptable safety risk for the selected candidate, `NO_SAFE_NEXT_SLICE_SELECTED` is not triggered.

## Forbidden Scope

- Do not authorize implementation.
- Do not start Phase 2C-07.
- Do not start Phase 2C-08.
- Do not implement the selected candidate.
- Do not create a runner.
- Do not create an adapter.
- Do not create an execution path.
- Do not create a scheduler, queue, broker, worker, or agent loop.
- Do not touch SSH, NETCONF, RESTCONF, live device access, provider/API/model calls, or secrets.
- Do not add real command execution.
- Do not add config backup or config change behavior.
- Do not rewrite or replace Day1-Day160 artifacts.
- Do not create a second safety matrix.
- Do not modify AGENTS.md.
- Do not modify unrelated files.

## Existing Artifacts To Reference

- `docs/phase_2b/phase_2b_13_first_slice_final_selection_gate.md`
- `docs/phase_2b/phase_2b_14_first_slice_implementation_kickoff_gate.md`
- `docs/phase_2c/phase_2c_01_local_static_job_first_slice.md`
- `docs/phase_2c/phase_2c_02_post_first_slice_acceptance_review.md`
- `docs/phase_2c/phase_2c_03_next_slice_decision_gate_authorization_review.md`
- `docs/phase_2c/phase_2c_04_next_slice_candidate_inventory.md`
- `docs/phase_2c/phase_2c_05_next_slice_safety_delta_review.md`
- Existing Day1-Day160 artifacts only as reference material, without rewriting or replacing them

## Implementation Boundary

Allowed:

- Add this Phase 2C-06 planning-only final selection artifact.
- Add minimal report-only Python evidence generation consistent with existing Phase 2C patterns.
- Add targeted tests for Phase 2C-06.
- Register a report-only task through existing registry, CLI, and report-index metadata.

Not allowed:

- Authorize Phase 2C-07 or Phase 2C-08.
- Implement or scaffold the selected candidate.
- Add runtime execution behavior, network access, device access, provider/API/model access, secrets, backup behavior, config-change behavior, Day1-Day160 replacement, AGENTS.md modification, or second safety-matrix behavior.

## Selected Next Slice

SELECTED_CANDIDATE_ID: candidate-02
SELECTED_NEXT_SLICE: artifact_validation_job
SELECTED_EXAMPLE_JOB_TYPE: artifact validation job
SELECTED_SLICE_DISPLAY_NAME: Artifact Validation Job

## Rationale

`candidate-02` is selected because artifact validation can remain a narrow, deterministic, report-only follow-up over existing artifact shape and reviewer visibility.

Compared with the other Phase 2C-04 candidates, it has the clearest minimal later validation path and does not require expanded runtime, runner, adapter, scheduler, broker, live-device, provider/API/model, secret, Day1-Day160 replacement, or second safety matrix scope. Phase 2C-05 confirms it has no new safety delta within the planning boundary.

Selection is not authorization. The selected slice remains locked until a separate Phase 2C-07 authorization gate is explicitly completed and approved.

## Final Verdict

PHASE_2C_06_FINAL_SELECTION_GATE_DONE_IMPLEMENTATION_LOCKED

Required preserved flags:

- FINAL_SELECTION_GATE_ONLY: YES
- CANDIDATE_SELECTED: YES
- NEXT_SLICE_AUTHORIZED: NO
- PHASE_2C_07_STARTED: NO
- PHASE_2C_08_STARTED: NO
- IMPLEMENTATION_ADDED: NO
- RUNNER_ADAPTER_EXECUTION_PATH_ADDED: NO
- SSH_NETCONF_RESTCONF_LIVE_DEVICE_TOUCHED: NO
- PROVIDER_API_MODEL_SECRETS_TOUCHED: NO
- DAY1_DAY160_REWRITTEN_OR_REPLACED: NO
- SECOND_SAFETY_MATRIX_CREATED: NO
