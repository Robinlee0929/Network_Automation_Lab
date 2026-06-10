# Day94 Adapter Boundary Regression Matrix

Day94 adds a deterministic regression matrix after the Day93 guarded fake
adapter contract.

Day93 proved the guard is evaluated before fake adapter boundary invocation.
Day94 keeps that proof alive across a wider matrix of scenario classes so a
future change cannot accidentally call an adapter for rejected, live-capable,
configuration-mutation, unknown, or real-adapter-targeted rows.

## Regression Matrix

The matrix combines:

- guard decision: `allowed` or `rejected`
- intent class: `readonly_safe`, `readonly_requires_review`, `live_capable`,
  `config_mutation`, and `unknown_intent`
- adapter target: `fake_adapter` or `real_adapter_blocked`
- boundary expectation: fake adapter evidence only for allowed fake-adapter rows

Each row records expected and actual fake adapter invocation, expected and
actual real adapter invocation, live execution flags, dry-run-only state,
evidence-chain state, boundary result, status, and reason.

## What Is Proven

- The matrix has at least 12 deterministic rows.
- Rejected rows never invoke the fake adapter.
- Real adapter invocations remain `0`.
- Live execution invocations remain `0`.
- `adapter_invoked_for_rejected` remains `0`.
- Allowed fake-adapter rows may invoke only the fake boundary as auditable
  evidence.
- The aggregate status is `PASS` only when all invariants pass.

## What Is Not Enabled

Day94 does not add:

- real device access
- SSH
- RouterOS/API access
- live command execution
- real adapter invocation
- `config.json` loading
- environment secret dependency
- execution unlocks
- dashboard form, POST route, execute button, or adapter control
- OpenAI API, AI SDK, voice, shell automation, or external service calls

## Evidence

Reports:

- `reports/lab-summary/day94_adapter_boundary_regression_matrix.json`
- `reports/lab-summary/day94_adapter_boundary_regression_matrix.html`

Runner:

```bash
python network_lab.py --task adapter-boundary-regression-matrix
```

Reviewers should read the summary first, then confirm invariant checks, then
inspect the matrix rows. The key pass/fail fields are
`adapter_invoked_for_rejected`, `real_adapter_invocations`,
`live_execution_invocations`, and every row's `regression_status`.
