# Day123 Safety Boundary Regression Matrix

Day123 adds a report-only regression matrix after the Day120 task registry extraction, Day121 CLI dispatch split, and Day122 report-index responsibility split.

The matrix verifies that safety-critical mock, review-only, report-only, dry-run-only, fake-adapter-only, locked, disabled, parser-only, design-only, planning-only, scaffold-only, registry, CLI dispatch, and report-index boundaries remain non-executing.

## Report Outputs

- `reports/lab-summary/day123_safety_boundary_regression_matrix.json`
- `reports/lab-summary/day123_safety_boundary_regression_matrix.html`

Generate with:

```powershell
python network_lab.py --task safety-boundary-regression-matrix
```

## Matrix Fields

Each row records:

- task or component name
- expected boundary
- observed boundary
- execution_allowed
- ssh_allowed
- live_command_allowed
- mutation_allowed
- unlock_supported
- adapter_invocation_allowed
- broker_invocation_allowed
- runner_invocation_allowed
- openai_api_allowed
- voice_runtime_allowed
- dashboard_post_action_allowed
- status
- evidence / reason

## Safety Invariants

Day123 is report-only. It does not run the reviewed tasks.

These values must remain false for every row:

```text
execution_allowed = false
ssh_allowed = false
live_command_allowed = false
mutation_allowed = false
unlock_supported = false
adapter_invocation_allowed = false
broker_invocation_allowed = false
runner_invocation_allowed = false
openai_api_allowed = false
voice_runtime_allowed = false
dashboard_post_action_allowed = false
```

If any row indicates live execution, SSH, mutation, unlock support, adapter/broker/runner invocation, OpenAI API use, voice runtime, or dashboard POST action support, the matrix becomes `BLOCKED`.

## Reviewed Boundary Families

- Day57-Day78 AI intent and runtime safety evidence
- Day79-Day87 read-only broker, queue, and phase-gate evidence
- Day88-Day95 real-adapter design, scaffold, guard, and fake-adapter evidence
- Day96-Day119 parser and reviewer report-only evidence
- Day120 task registry boundary
- Day121 CLI dispatch boundary
- Day122 report-index visibility and profile-backed boundaries
- Disabled Day13 live execution guardrail

## Expected Result

`overall_status == PASS` means all reviewed rows remained locked, disabled, read-only, dry-run-only, review-only, report-only, mock-only, fake-adapter-only, design-only, planning-only, or scaffold-only as expected.
