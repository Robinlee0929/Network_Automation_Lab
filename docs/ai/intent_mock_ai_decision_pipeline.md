# Day73 Mock AI Decision Pipeline

Day73 adds a deterministic mock decision stage after the Day72 controlled AI
runtime input contract validator.

The pipeline demonstrates how a future AI-assisted network test assistant could
turn a validated or rejected intent payload into a reviewer-facing decision
record. It is still mock-only: it does not call OpenAI, use any AI SDK, start a
real AI runtime, open SSH, access devices, execute mapped tasks, read
`config.json`, or change router, switch, firewall, VPN, VRRP, or network
configuration.

## Connection To Day72

Day72 validates structured input payloads. Day73 consumes those validation
results and adds a second, deterministic decision layer.

Day73 does not weaken Day72. Unsafe payloads blocked by Day72 remain blocked.
Invalid payloads remain invalid. Valid report-only or documentation-only
payloads can become reviewer-ready evidence, but they still do not execute.

## Mock Scenarios

Day73 includes five fixed in-memory scenarios:

| Scenario | Day72 result | Day73 label |
| --- | --- | --- |
| Documentation-only request | Valid | `DOCUMENTATION_ONLY` |
| Report-only request | Valid | `REPORT_ONLY` |
| Ambiguous reviewer request | Valid, reviewer required | `REVIEW_REQUIRED` |
| Live device/network action request | Blocked | `BLOCKED_LIVE_ACTION` |
| Structurally invalid input | Invalid | `INVALID_INPUT_BLOCKED` |

## Decision Record Fields

Each decision record includes:

- `scenario_id`
- `input_summary`
- `validator_status`
- `mock_decision`
- `decision_label`
- `allowed_to_execute`
- `requires_manual_review`
- `blocked_reason`
- `safety_rationale`
- `evidence`
- `next_reviewer_action`

`allowed_to_execute` is always `false`. This is the central Day73 invariant.
Day73 is a reviewer decision simulation, not an execution stage.

## Decision Labels

`DOCUMENTATION_ONLY` means the input can be presented as documentation evidence.
No task is executed.

`REPORT_ONLY` means the input can be presented as report evidence. No task is
executed.

`REVIEW_REQUIRED` means the input is ambiguous or risky enough to require human
review before any later design stage.

`BLOCKED_LIVE_ACTION` means the input requested live device or network behavior
and is blocked before any execution path.

`INVALID_INPUT_BLOCKED` means the input did not satisfy the Day72 input contract
and must be corrected before review.

## Preserved Safety Boundaries

- No OpenAI API.
- No AI SDK dependency.
- No real AI runtime.
- No SSH.
- No device access.
- No live execution.
- No mapped task execution.
- No arbitrary command execution.
- No `config.json` dependency.
- No dashboard form, POST route, or action endpoint.
- No router, switch, firewall, VPN, VRRP, or network configuration change.

## Generated Reports

Run:

```text
python network_lab.py --task mock-ai-decision-pipeline
```

Outputs:

```text
reports/lab-summary/day73_mock_ai_decision_pipeline.json
reports/lab-summary/day73_mock_ai_decision_pipeline.html
```

## Future Day74 Direction

Day74 could add a reviewer acceptance checklist for the Day72-to-Day73 chain,
or a contract validator for the Day73 decision record schema. It should still
remain offline, deterministic, and no-execution unless a separate safety design
explicitly approves a new boundary.
