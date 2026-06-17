# Phase 2A-06 Negative Regression Matrix

Phase 2A-06 is a negative regression matrix only. It replays fixed unsafe input
shapes against the existing Phase 2A safety layers and records that those inputs
remain rejected, redacted, and non-executing.

## Scope

- Phase 2A-06 reuses the Phase 2A-02 job spec validator.
- Phase 2A-06 reuses the Phase 2A-03 dry-run plan gate.
- Phase 2A-06 reuses the Phase 2A-04 evidence binding record shape.
- Phase 2A-06 does not modify Phase 2A-05.
- Phase 2A-06 does not add a runner, adapter, broker, execution path, or live
  target path.
- Phase 2A-06 does not open SSH, NETCONF, RESTCONF, provider/API/model,
  backup_config, arbitrary command, or arbitrary script path capability.
- Phase 2A-06 does not authorize Phase 2B.
- Phase 2A-06 does not authorize Phase 2A-07 or any next step.

## Matrix Assertions

Each fixed unsafe input case must prove:

- the Phase 2A-02 validator returns `REJECTED`
- the Phase 2A-03 plan gate returns `REJECTED`
- no dry-run plan is generated for the unsafe input
- Phase 2A-04 evidence binding records the outcome as rejected evidence
- raw unsafe input values are not emitted in reviewer reports
- runner, adapter, live execution, and next-phase flags remain false

## Reviewer Evidence

Run:

```bash
python network_lab.py --task phase2a-06-negative-regression-matrix
```

This writes:

- `reports/lab-summary/phase_2a_06_negative_regression_matrix.json`
- `reports/lab-summary/phase_2a_06_negative_regression_matrix.html`

The task is report-only and uses fixed local fixtures. It does not accept
arbitrary input from the CLI.
