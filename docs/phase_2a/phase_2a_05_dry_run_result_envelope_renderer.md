# Phase 2A-05 Dry-Run Result Envelope / Renderer

Phase 2A-05 is an envelope-and-renderer-only step for the existing Phase 2A-04
dry-run plan evidence ledger report.

It first consumes the existing `phase_2a_04_plan_evidence_ledger.py` report
builder interface, then creates a compact reviewer-facing `result_envelope`.
Renderer metadata and output paths are kept in a separate sibling
`render_outputs` object.

## Scope

- Phase 2A-05 consumes the existing Phase 2A-04 report interface.
- Phase 2A-05 does not rebuild the Phase 2A-03 planner.
- Phase 2A-05 does not rebuild the Phase 2A-04 ledger.
- Phase 2A-05 does not put `render_outputs` inside `result_envelope`.
- Phase 2A-05 does not put `result_envelope` inside `render_outputs`.
- Phase 2A-05 writes deterministic JSON, HTML, and text reviewer outputs.
- Phase 2A-05 does not execute jobs.
- Phase 2A-05 does not invoke a runner.
- Phase 2A-05 does not invoke an adapter.
- Phase 2A-05 does not open live execution.
- Phase 2A-05 does not open SSH, NETCONF, RESTCONF, provider/API/model,
  backup_config, arbitrary command, or arbitrary script path capability.
- Phase 2A-05 does not authorize Phase 2B.
- Phase 2A-05 does not authorize real execution.

## Result Shape

The report keeps the two major objects as siblings:

```text
{
  "result_envelope": { ... },
  "render_outputs": { ... }
}
```

`result_envelope` contains the envelope id, source Phase 2A-04 report reference,
source counts, AGENTS.md status, non-execution proof, and fixed false safety
flags.

`render_outputs` contains only renderer metadata, formats, paths, and the source
envelope id reference. It does not contain the envelope object.

## AGENTS.md Status

The final report includes both:

- `agents_md_pre_read`
- `result_envelope.agents_md_status`

These fields record whether AGENTS.md was required, found, read before work, and
modified. Phase 2A-05 expects `read=true` and `modified=false`.

## Validation Rules

The Phase 2A-05 validator proves:

- the existing Phase 2A-04 implementation was searched and consumed
- the Phase 2A-04 report builder interface is present
- `result_envelope` and `render_outputs` are separate sibling objects
- renderer outputs do not recursively embed the result envelope
- the report is JSON serializable
- planner rebuild is false
- ledger rebuild is false
- all runner, adapter, live execution, SSH, NETCONF, RESTCONF, provider/API/model,
  backup_config, arbitrary command, arbitrary script path, Phase 2B, real
  execution, and next-phase flags remain false

## Reviewer Evidence

The fixed CLI task:

```bash
python network_lab.py --task phase2a-05-dry-run-result-envelope-renderer
```

writes:

- `reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.json`
- `reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.html`
- `reports/lab-summary/phase_2a_05_dry_run_result_envelope_renderer.txt`

This task does not accept arbitrary job execution input. It renders a fixed local
reviewer envelope for inspection only.
