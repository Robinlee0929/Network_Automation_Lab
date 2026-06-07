# Public Reviewer Walkthrough

## One-Sentence Project Positioning

Network Automation Lab is a safety-first Python portfolio project that turns MikroTik, Cisco, WireGuard, VRRP, and performance validation workflows into repeatable test evidence, reports, and a local dashboard.

## What Problem This Project Solves

Network checks are often proven with ad hoc SSH sessions, screenshots, and copied command output. This project shows how those checks can be organized like a QA automation platform:

- Scripts collect or generate structured evidence.
- Reports use readable PASS / FAIL / WARN status.
- Dashboard pages make local evidence easier to review.
- Safety levels separate report-only, read-only, dry-run, guarded-live, and controlled failover workflows.
- Public review can happen without touching real lab devices.

## Suggested Reading Order

1. `README.md`
2. `docs/portfolio/public_reviewer_walkthrough.md`
3. `docs/demo/offline_interview_demo_kit/README.md`
4. `docs/demo/day52_offline_demo_package/README.md`
5. `docs/roadmap/day55_public_repository_readiness_review.md`
6. `docs/roadmap/day54_public_facing_portfolio_demo_wording_audit.md`

For a shorter review, read this document first, then open the dashboard screenshots in `docs/demo/day52_offline_demo_package/screenshots/`.

## How To Start The Local Dashboard

From the repository root:

```powershell
python dashboard_app.py
```

Then open:

```text
http://127.0.0.1:5000/
```

If dependencies are not installed, review the committed screenshots instead:

```text
docs/demo/day52_offline_demo_package/screenshots/
```

## Dashboard Pages To Review

| Route | What to look for |
| --- | --- |
| `/` | Project positioning, demo status, proof points, quick links, and no-live-router boundary. |
| `/reports` | Evidence browser for generated JSON/HTML reports, grouped report metadata, and missing-report visibility. |
| `/commands` | Safe command execution model, allowlisted command cards, disabled lab workflows, and execution logs. |
| `/ai-checklist` | Review evidence for AI/safety boundaries and command execution controls. |

These pages are local review surfaces. Opening them does not require SSH, live device access, VPN access, WireGuard access, VRRP failover, iperf3, or router/switch configuration changes.

## Offline Demo Materials

Start here:

```text
docs/demo/offline_interview_demo_kit/README.md
```

Useful supporting files:

```text
docs/demo/offline_interview_demo_kit/demo_checklist.md
docs/demo/offline_interview_demo_kit/demo_commands.md
docs/demo/offline_interview_demo_kit/interview_talk_track_3_to_5_min.md
docs/demo/offline_interview_demo_kit/no_live_dependency_statement.md
docs/demo/offline_interview_demo_kit/troubleshooting_guide.md
```

The folder name is historical. It remains unchanged so existing Day47-Day53 references continue to work.

## Screenshots

Committed dashboard screenshots are available here:

```text
docs/demo/day52_offline_demo_package/screenshots/
```

Recommended screenshot order:

1. `dashboard_home.png`
2. `dashboard_reports.png`
3. `dashboard_commands.png`
4. `dashboard_ai_checklist.png`

These screenshots are useful when a reviewer cannot run Flask locally or when the repository is being reviewed without live lab access.

## How To Interpret Reports

Reports are evidence artifacts, not raw terminal dumps.

| Status | Meaning |
| --- | --- |
| PASS | Expected condition matched. |
| FAIL | Required condition failed or required evidence was missing. |
| WARN | Non-blocking issue, drift, missing optional generated evidence, or review note. |
| MISSING | Expected local generated report is not present. |
| UNKNOWN | The report exists but does not expose a supported status field. |

Start with the overall status, then read failed or warning items, then inspect expected/actual fields only when deeper troubleshooting is needed.

## Why `report-index` May Return WARN

Run this only as a report-only local evidence scan:

```powershell
python network_lab.py --task report-index
```

This command reads local metadata and report files. It does not connect to live devices and does not run router, switch, VPN, WireGuard, VRRP, SSH, or iperf3 workflows.

It may return WARN when optional generated local reports are missing from `reports/`. That is expected on clean public checkouts because generated reports are intentionally local and generally ignored by Git.

WARN is acceptable when all of these are true:

- `fail=0`.
- Missing items are optional generated local reports.
- The output still provides report visibility and refreshed local index files.

WARN is not acceptable if required evidence fails or if `fail` is greater than zero.

## What Can Be Reviewed Without Live Lab Access

A public reviewer can review:

- Python source organization.
- Unit tests.
- README and roadmap docs.
- Safety levels and no-live-device boundaries.
- Dashboard page structure.
- Committed dashboard screenshots.
- Offline demo package.
- Report-index behavior and report interpretation.

No router, switch, VPN, VRRP, WireGuard, SSH, iperf3, firewall, or live lab access is required for this public review path.

## Safety Boundaries

For public review, do not run live workflows. The safe review path has:

- No live network tests.
- No SSH.
- No device access.
- No router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration changes.
- No iperf3 live test.
- No `config.json` dependency.
- No `config.json` changes.

Use committed documentation, tests, screenshots, and local report-only/dashboard views for review.
