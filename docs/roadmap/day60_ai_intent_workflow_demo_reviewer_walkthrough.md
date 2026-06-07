# Day60 - AI Intent Workflow Demo / Reviewer Walkthrough Flow

## Goal

Create a safe reviewer walkthrough that connects Day57 dry-run intent mapping, Day58 safety review, and Day59 policy explanation into one local demo flow.

## Scope

- Add `intent-workflow-demo` as a report-only runner task.
- Generate `reports/portfolio/day60_intent_workflow_demo.json`.
- Generate `reports/portfolio/day60_intent_workflow_demo.html`.
- Document reviewer steps, expected output, safety boundaries, Q&A, and troubleshooting notes.
- Update README with the Day60 milestone.

## Safety Contract

Day60 is documentation-only and report-only. It does not connect OpenAI API, add voice input, execute mapped tasks, run live network tests, use SSH, touch device settings, read or require `config.json`, modify network/device configuration, create release tags, or start real v0.3 runtime implementation.

The required final sentence is:

```text
No mapped task was executed. This is a dry-run reviewer walkthrough only.
```

## Example Intent Coverage

- `show latest reports`: report-only, allowed.
- `explain available runner tasks`: documentation/report-only, allowed.
- `do VRRP failover test`: live-capable, blocked by default.
- `change router firewall rule`: configuration-changing, blocked.
- `run WireGuard throughput test`: live-capable, blocked unless a future guarded-live flow exists.

## Validation Plan

```powershell
python -m pytest
python network_lab.py --task intent-workflow-demo
python network_lab.py --task report-index
```

Expected result:

- `pytest` passes.
- `intent-workflow-demo` returns `PASS`.
- `report-index` may return `WARN` only when `fail=0` and missing items are optional generated local reports.

## Completion Notes

Day60 does not implement the v0.3 runtime. It only makes the reviewer path explicit and testable so the safety model can be shown before any future AI or voice implementation work begins.
