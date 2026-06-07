# Day51 - Portfolio Demo Visual QA / Screenshot Capture

## Purpose

Day51 checks the dashboard from the point of view of a demo reviewer seeing the project for the first time. The goal is to make sure the demo pages explain the project quickly, keep the safety boundary visible, and give a practical screenshot plan for portfolio demo prep.

Day51 is documentation, visual QA, and local route verification only.

## Scope

- Review the dashboard pages at `/`, `/reports`, `/commands`, and `/ai-checklist`.
- Confirm the first screen of each page has a clear title and a useful next click.
- Confirm the wording does not imply that the dashboard directly changes real routers, switches, firewalls, VPN devices, WireGuard peers, or lab topology.
- Confirm warnings and missing local report notes are explainable in a portfolio review.
- Add screenshot capture guidance for the dashboard pages.
- Add a portfolio demo sequence and page-level talk track.

## Non-goals

- Do not add runner tasks.
- Do not add live network tests.
- Do not use SSH.
- Do not connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peer, or iperf endpoint.
- Do not change `config.json`.
- Do not change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.
- Do not create a `v0.2.1` tag.
- Do not start `v0.3` architecture or feature work.
- Do not add screenshots as committed binary files unless there is a clear need to refresh the demo package.

## Page-by-page Visual QA Checklist

| Page | Portfolio review use | Visual QA result |
| --- | --- | --- |
| `/` | Use this page to open the demo. It shows the project name, status, proof points, 3-5 minute flow, quick links, and no-live-router boundary. | PASS WITH NOTES. The first screen clearly says `Network Automation Lab - Portfolio Demo`, shows `READY WITH NOTES`, and explains that optional generated reports can be missing when `fail=0`. |
| `/reports` | Show this page after explaining the safety boundary. It is the evidence browser for generated JSON/HTML reports, VRRP artifacts, and WireGuard summaries. | PASS WITH NOTES. The title is clear, the page says it reads metadata and does not run router/switch/VPN/iperf workflows, and missing local evidence is framed as generated report availability. |
| `/commands` | Use this page to explain allowlisted local commands and disabled lab workflows. It is useful when the demo reviewer asks how command safety works. | PASS. The page title says `Safe Command Execution`, states that arbitrary shell input is not accepted, and shows enabled/disabled command state plus recent logs. |
| `/ai-checklist` | Show this page when discussing AI readiness and safety review. This page is optional if time is short. | PASS. The checklist reads like review evidence, not raw AI output, and points to code/dashboard evidence for each safety control. |

## Screenshot Capture Checklist

Before a portfolio review, retake screenshots from a fresh local dashboard session if possible:

1. Start the dashboard locally with `python dashboard_app.py`.
2. Open `http://127.0.0.1:5000/`.
3. Capture the visible first screen of each route at a normal laptop viewport.
4. Avoid screenshots that show local usernames, private paths outside the repo, browser bookmarks, or unrelated tabs.
5. Keep the screenshots under `docs/demo/day51_visual_qa_screenshots/` only when they are meant to be part of the demo package.
6. Do not present WARN as a failure if `fail=0` and the missing items are optional local reports.
7. Retake screenshots after any dashboard wording change, route layout change, or report-index behavior change.

Suggested screenshot files:

| File | Route | Use |
| --- | --- | --- |
| `01_dashboard_home.png` | `/` | Main portfolio demo landing page. Use it to open the demo and establish the safety boundary. |
| `02_reports_page.png` | `/reports` | Report evidence overview. Use it to show generated evidence and optional missing-report notes. |
| `03_commands_page.png` | `/commands` | Safe command/reference page. Use it to show allowlisted commands and disabled lab workflows. |
| `04_ai_checklist_page.png` | `/ai-checklist` | Safety and AI readiness checklist. Use it when discussing guardrails. |

## Suggested Portfolio Demo Sequence

1. Open `/` and spend 30-45 seconds on the project purpose, demo status, and no-live-router boundary.
2. Open `/reports` and show how generated evidence is discoverable without starting live workflows.
3. Open `/commands` and point out that commands are allowlisted, logged, timed, and not arbitrary shell input.
4. Open `/ai-checklist` if the demo reviewer asks about AI, safety, or command review.
5. Close by explaining that live lab work exists in guarded/read-only/dry-run lanes, but this portfolio demo path is safe to run without lab access.

## UX Notes From A User Perspective

- The home page gives a good first impression for a portfolio review because it names the project and tells the viewer what to click next.
- The `READY WITH NOTES` status is useful because it prevents optional missing local reports from sounding like a broken demo.
- The Reports page is dense, but the safety sentence near the top helps: it says the page reads report metadata and does not run device workflows.
- The Commands page is the strongest safety proof for the dashboard because it shows allowlisted command cards, disabled commands, timeouts, and execution logs.
- The AI Checklist page works best as supporting evidence. Use it when the demo reviewer asks how AI assistance is kept away from direct device changes.
- Missing local reports should be explained as generated evidence that is intentionally not always committed.

## What To Say During The Portfolio Demo

### Home

"Use this page to open the demo. The important parts are the status, the proof points, and the safety note. I can explain the whole project from here without connecting to a router."

### Reports

"This page is the evidence browser. It lets me show JSON and HTML reports from previous runs. A WARN here is not automatically a failure; if `fail=0`, it can simply mean optional local generated reports are not present on this machine."

### Commands

"This page shows the command safety model. The dashboard does not accept arbitrary shell text. Enabled commands are registered, timed, and logged. Lab workflows that need real parameters or devices are not one-click portfolio demo actions."

### AI Checklist

"This page is the review checklist I use before adding AI-assisted behavior. It keeps the conversation grounded in concrete controls: allowlists, `shell=False`, log output, redaction, and no direct device operation from the dashboard."

## Validation Commands And Results

Commands to run for Day51:

```powershell
python -m pytest
python network_lab.py --task report-index
python dashboard_app.py
```

Observed results:

- `python -m pytest`: `488 passed, 1 warning in 3.91s`.
- `python network_lab.py --task report-index`: overall result `[WARN]`, counts `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- Generated/updated ignored local overview outputs:
  - `reports/lab-summary/latest_lab_overview.json`
  - `reports/lab-summary/latest_lab_overview.html`
- Dashboard route check: PASS WITH NOTES for `/`, `/reports`, `/commands`, and `/ai-checklist`.

Browser note:

- The in-app browser runtime failed before navigation in this environment, so Day51 used the documented fallback: localhost HTTP 200 checks plus expected title/key text checks for each route.
- No binary screenshots were committed. Screenshot capture is documented in `docs/demo/day51_visual_qa_screenshots/README.md`.

Expected route checks:

- `/`: HTTP 200 and contains `Network Automation Lab - Portfolio Demo`, `READY WITH NOTES`, `Reports`, `Commands`, and `AI Checklist`.
- `/reports`: HTTP 200 and contains `Reports`, `Local evidence browser`, `HA / VRRP Evidence`, and safe read-only wording.
- `/commands`: HTTP 200 and contains `Safe Command Execution`, `allowlist`, `arbitrary shell input`, and `Execution Logs`.
- `/ai-checklist`: HTTP 200 and contains `AI Review Checklist`, `Use this page as review evidence`, and command safety evidence.

Observed route checks:

```text
/ status=200 missing=[]
/reports status=200 missing=[]
/commands status=200 missing=[]
/ai-checklist status=200 missing=[]
```

## Safety Confirmation

Day51 did not run live tests.

Day51 did not use SSH, connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peer, or iperf endpoint, or access any live device.

Day51 did not change `config.json`.

Day51 did not change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.

Day51 did not create a `v0.2.1` tag.

Day51 did not start `v0.3` work.

## Final Status

Day51 status: READY WITH NOTES.

The notes are limited to expected local-demo conditions: `report-index` returned WARN because optional generated local reports were missing while `fail=0`, and browser screenshot capture was documented but not committed because the browser runtime was unavailable in this environment.
