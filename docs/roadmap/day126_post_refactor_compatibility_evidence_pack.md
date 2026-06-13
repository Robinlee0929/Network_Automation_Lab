# Day126 Post-Refactor Compatibility Evidence Pack

## Goal

Create a report-only compatibility evidence pack proving the Day120-Day125
responsibility-split work remains compatible after the thin CLI, task registry,
dispatch, report visibility, formatter, and safety helper changes.

## Decision

Adopt: `Day126 - Post-Refactor Compatibility Evidence Pack`.

Do not adopt: `Day126 - Thin CLI Responsibility Budget Gate`.

Day126 does not add a thin CLI budget gate, numeric thresholds, long-term budget
enforcement, or any policy that blocks future work based on CLI size.

## Deliverables

- `intent_post_refactor_compatibility_evidence_pack.py`
- CLI task: `python network_lab.py --task post-refactor-compatibility-evidence-pack`
- JSON report: `reports/lab-summary/day126_post_refactor_compatibility_evidence_pack.json`
- HTML report: `reports/lab-summary/day126_post_refactor_compatibility_evidence_pack.html`
- Report-index visibility
- AI intent documentation and roadmap documentation
- Tests for AGENTS.md pre-read evidence, compatibility records, snapshot-only
  thin CLI evidence, CLI/catalog wiring, report-index visibility, and no
  budget-gate enforcement

## Acceptance

The Day126 task is accepted only when:

- `overall_status` is `PASS`
- `agents_md_pre_read_result` is `PASS`
- `agents_md_read_before_day126_work` is `true`
- `compatibility_pack_status` is `COMPATIBILITY_EVIDENCE_READY`
- Compatibility records for Day120-Day125 are all compatible
- Exactly one Day125 thin CLI snapshot is included
- No thin CLI budget gate, numeric threshold, long-term budget enforcement, or
  budget blocking policy is added
- Live execution, SSH, OpenAI/voice runtime, mapped task execution, dashboard
  action endpoint, and execution unlock flags remain false
- `next_phase_allowed` remains `false`

## Validation

```bash
python network_lab.py --task post-refactor-compatibility-evidence-pack
python -m pytest
python network_lab.py --task report-index
```

For report-only validation, existing optional missing-report warnings are
acceptable only when they do not indicate a safety or regression issue.
