# Day53 - Portfolio Demo Final Rehearsal / Demo Operation Checklist

## Purpose

Day53 prepares a public-facing portfolio demo workflow for Network Automation Lab. The goal is not to add capability; the goal is to make the existing offline demo easy to run, explain, pause, recover, and close for portfolio reviewers, evaluators, or portfolio review use cases.

## Scope

Included:

- Final portfolio demo rehearsal flow.
- Traditional Chinese demo opening script.
- 3-5 minute operation sequence.
- Common reviewer Q&A preparation.
- Final operation checklist.
- Local validation result documentation.

## Non-goals

- No new product features.
- No Flask route changes.
- No dashboard behavior changes.
- No runner behavior changes.
- No task execution behavior changes.
- No live network tests.
- No SSH.
- No device connections.
- No `config.json` creation or modification.
- No `v0.2.1` release tag.
- No release tag of any kind.
- No `v0.3` work.
- No Day9-Day15 behavior or plan changes.

## Safety Boundaries

Day53 is documentation-only and rehearsal-only. It does not execute live network tests, does not use SSH, does not connect to network devices, does not modify router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration, does not create or edit `config.json`, does not create release tags, and does not start `v0.3`.

The offline demo path is limited to local repository review, local tests, report-only commands, local dashboard review, committed screenshots, and prepared explanation.

## Final Portfolio Demo Rehearsal Flow

1. Open the project folder.
2. Confirm current branch and working tree status.
3. Reference the latest local validation result, or run local validation only.
4. Start the local dashboard only if the local environment is available.
5. Open the dashboard home page.
6. Show the portfolio demo landing page.
7. Show the report index.
8. Show the commands and safety page.
9. Show the AI checklist.
10. Explain the evidence model, safety guard, and report-only demo workflow.
11. Close with the future evolution path: richer report intelligence, stronger guarded-live orchestration, and future AI assistance after safety controls are explicit.

## Demo Opening Script

Use the prepared Traditional Chinese script:

```text
docs/demo/day53_interview_demo_rehearsal/demo_opening_script_zh.md
```

Short version:

```text
這個專案是 Network Automation Lab。它展示的是安全的網路自動化、可追溯的報告證據、本機 dashboard evidence，以及可以在作品集展示或專案審查中穩定操作的 demo 流程。這次 demo 刻意採用 offline/report-only 路徑，不做 live VRRP、WireGuard、router、firewall 或 interface 變更，因為 demo 重點是展示工程設計、測試證據與安全邊界，而不是在不受控環境中修改真實設備。
```

## 3-5 Minute Operation Sequence

Use the prepared Traditional Chinese sequence:

```text
docs/demo/day53_interview_demo_rehearsal/three_to_five_minute_demo_sequence_zh.md
```

Required sequence:

1. Open project folder.
2. Confirm branch and status.
3. Run local tests or reference latest validation result.
4. Start dashboard locally if applicable.
5. Open dashboard home page.
6. Show portfolio demo landing page.
7. Show report index.
8. Show commands and safety page.
9. Show AI checklist.
10. Explain evidence, safety guard, and report-only workflow.
11. Close with the future platform path.

## Common Q&A

Use the prepared Traditional Chinese Q&A:

```text
docs/demo/day53_interview_demo_rehearsal/common_interview_qa_zh.md
```

Covered questions:

- Why is the demo offline?
- Why not perform live VRRP failover during the demo?
- What is the safety model?
- What did the project prove?
- How does this connect to real network automation work?
- What is the role of AI in the future version?
- What would `v0.3` or `v3.0` do?
- How do you prevent AI from directly changing router settings?
- What is the difference between report-only, read-only, dry-run, and guarded-live tasks?
- What are the current limitations?

## Final Operation Checklist

Use the prepared checklist:

```text
docs/demo/day53_interview_demo_rehearsal/final_operation_checklist.md
```

Pre-demo:

- [ ] Repository on latest `main`.
- [ ] Working tree clean before rehearsal changes.
- [ ] Day52 merged into `main`.
- [ ] No live network dependency.
- [ ] Dashboard pages reachable locally, or screenshots ready.
- [ ] Reports index reviewed.
- [ ] Demo script reviewed.
- [ ] Q&A reviewed.
- [ ] Screenshots/package location known.
- [ ] Safety statement ready.
- [ ] Backup plan ready if dashboard cannot open.

## Validation Result

Commands:

```powershell
python -m pytest
python network_lab.py --task report-index
git status --short --branch
```

Observed results:

- `python -m pytest`: `488 passed, 1 warning in 2.61s`.
- `python network_lab.py --task report-index`: `WARN`, counts `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- `git status --short --branch`: only `README.md`, `docs/demo/day53_interview_demo_rehearsal/`, and `docs/roadmap/day53_interview_demo_final_rehearsal_operation_checklist.md` were changed before staging.

Expected handling:

The `report-index` warning is acceptable for Day53 because `fail=0` and the missing reports are optional generated local reports.

## Final Day53 Status

Day53 status: READY WITH NOTES.

Notes are limited to acceptable documentation-only rehearsal conditions. Day53 adds no new runtime behavior and does not start `v0.3`.
