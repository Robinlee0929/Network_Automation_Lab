# Day95 Adapter Result Normalization / Evidence Hardening

## Scope

Day95 standardizes fake adapter result records after the guarded fake adapter boundary. It builds on Day93 guard-first boundary evidence and Day94 regression matrix evidence, then produces deterministic JSON and HTML reports for reviewer visibility.

## Non-goals

- No RouterOS access
- No SSH transport
- No live execution
- No real adapter execution
- No parser implementation
- No mapped task execution
- No dashboard action
- No POST endpoint
- No approval mechanism
- No execution unlock

## Deliverables

- `intent_adapter_result_normalization.py`
- Runner task `adapter-result-normalization`
- JSON report at `reports/lab-summary/day95_adapter_result_normalization.json`
- HTML report at `reports/lab-summary/day95_adapter_result_normalization.html`
- AI documentation at `docs/ai/intent_adapter_result_normalization.md`
- Roadmap documentation at `docs/roadmap/day95_adapter_result_normalization.md`
- Pytest coverage at `tests/test_intent_adapter_result_normalization.py`
- Read-only dashboard/report-index visibility

## Validation Checklist

- Fake adapter result schema is fixed and complete.
- Allowed scenarios produce normalized fake adapter results.
- Rejected scenarios produce no adapter result.
- Fake adapter result count equals allowed scenario count.
- Real adapter result count is zero.
- Live execution result count is zero.
- Result status comes only from the deterministic fake boundary.
- Evidence chain references Day93 and Day94.
- JSON and HTML reports are generated.
- Runner returns `PASS`.
- Dashboard remains read-only.
- No SSH, RouterOS, device access, real adapter, live execution, dashboard action, POST route, or execution unlock is added.

## Correct Route

- Day91 Real Adapter Safety Scaffold
- Day92 Executable Guards
- Day93 Guarded Fake Adapter Boundary Audit
- Day94 Adapter Boundary Regression Matrix
- Day95 Adapter Result Normalization / Evidence Hardening
- Day96 Read-only Output Parser Prototype
- Day97 Parser Regression Matrix
- Day98 Runner Dry-run Integration Harness
- Day99 Dashboard Evidence Visibility Review
- Day100 Live-read Phase Gate Review
- Day101+ possible live-read pilot only after explicit GO or CONDITIONAL_GO

## Relation To Day96-Day100

Day95 prepares Day96 by giving the parser prototype a stable fake result envelope. Day97 can then regression-test parser behavior against fixed fake outputs. Day98 may wire parser and runner dry-run evidence together without live execution. Day99 can expose that evidence in the dashboard as read-only visibility. Day100 remains the earliest live-read phase gate review.

Live-read pilot work is not allowed before the Day100 phase gate. The earliest reasonable live-read pilot is Day101 or later, and only if Day100 returns `GO` or `CONDITIONAL_GO`.
