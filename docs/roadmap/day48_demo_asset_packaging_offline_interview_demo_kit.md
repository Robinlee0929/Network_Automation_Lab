# Day48 - Demo Asset Packaging / Offline Portfolio Demo Kit

## Purpose

Day48 packages a self-contained offline portfolio demo kit for Network Automation Lab.

The goal is to make the project easy to demonstrate from a local checkout without depending on GitHub, internet access, live routers, switches, VPN peers, WireGuard clients, iperf3 endpoints, or lab devices.

## Scope

- Create an offline portfolio demo kit under `docs/demo/offline_interview_demo_kit/`.
- Provide a demo checklist, safe command list, troubleshooting guide, portfolio demo talk track, no-live-dependency statement, and screenshot backup plan.
- Reference the Day47 portfolio demo baseline runbook.
- Keep the work documentation-only, report-only, and offline-only.
- Preserve the existing live workflow boundaries.

## Non-goals

- No live network testing.
- No SSH.
- No MikroTik, Cisco, router, switch, firewall, VPN, WireGuard, or iperf3 endpoint connection.
- No NAT, IP, VRRP, WireGuard, firewall, route, interface, reboot, reset, or device configuration change.
- No `config.json` creation or modification.
- No GitHub, internet, or cloud dependency during the portfolio demo.
- No new runner behavior, dashboard behavior, live workflow, or device-control logic.

## Offline Demo Assumptions

- The repository has been cloned or copied to the review computer before the demo.
- Python and project dependencies are already available, or the demo reviewer accepts a code and document walkthrough without executing commands.
- Generated reports under ignored `reports/` folders may be missing on a clean checkout.
- Missing generated reports can produce `WARN` output in report-index views; that is acceptable when the missing evidence is optional local history.
- The demo can still explain the architecture, runner safety model, dashboard/report index, VRRP evidence chain, and WireGuard direction from committed source and documentation.
- Local dashboard launch is optional. The documentation kit remains usable even if Flask is not installed or a browser cannot be opened.

## Demo Checklist

Use the detailed checklist in:

```text
docs/demo/offline_interview_demo_kit/demo_checklist.md
```

Summary:

- Confirm repository state with `git status --short --branch`.
- Confirm Python with `python --version`.
- Run `python -m pytest`.
- Run `python network_lab.py --task report-index`.
- Run `python network_lab.py --task demo-flow`.
- Confirm the dashboard can start locally if the demo environment allows it.
- Confirm `/reports` can open locally if the dashboard is started.
- Confirm Day47 and Day48 documents are available offline.
- Confirm no live device connection is required.

## Offline Demo Folder Structure

```text
docs/demo/offline_interview_demo_kit/
|-- README.md
|-- demo_checklist.md
|-- demo_commands.md
|-- troubleshooting_guide.md
|-- interview_talk_track_3_to_5_min.md
|-- no_live_dependency_statement.md
`-- screenshots/
    `-- README.md
```

## Demo Command List

Use copy-ready PowerShell commands from:

```text
docs/demo/offline_interview_demo_kit/demo_commands.md
```

Safe command highlights:

```powershell
git status --short --branch
python --version
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task demo-flow
python dashboard_app.py
```

Open local dashboard pages only after `python dashboard_app.py` is running:

```powershell
Start-Process "http://127.0.0.1:5000/"
Start-Process "http://127.0.0.1:5000/reports"
```

These commands are local and non-live. They do not require SSH or device access.

## Troubleshooting Guide

Use the detailed guide in:

```text
docs/demo/offline_interview_demo_kit/troubleshooting_guide.md
```

Covered cases:

- Dashboard cannot start.
- Reports page is missing or empty.
- `pytest` fails.
- `report-index` shows `WARN`.
- Generated reports are missing.
- Browser cannot open the local page.
- Demo site has no internet.
- Router or switch cannot be reached.

## 3-5 Minute Portfolio Demo Talk Track

Use the Traditional Chinese talk track in:

```text
docs/demo/offline_interview_demo_kit/interview_talk_track_3_to_5_min.md
```

The talk track covers:

- Problem solved by the project.
- Why safety guards matter.
- Unified Runner.
- Report Index and Dashboard.
- VRRP evidence and offline demo readiness.
- WireGuard and future AI/Voice direction.
- Why the demo does not need live devices.
- What demo reviewers should notice.

## No Live Dependency Statement

The Day48 offline portfolio demo does not require live router or switch access. It does not require SSH. It does not require GitHub, internet, VPN, WireGuard peers, iperf3 endpoints, or lab devices.

The demo is intentionally based on committed source code, committed documentation, local tests, local report-index generation, local dashboard routes, and existing evidence references. Live testing remains separated from the portfolio demo flow for safety.

## Safety Statement

Day48 is documentation/report-only/offline-only work.

Day48 does not run live tasks, use SSH, connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard, or iperf3 endpoints, create or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, route, interface, reboot, reset, or device configuration.

During a portfolio review or offline demo, use only the safe local commands listed in the kit. Do not run VRRP live validation, WireGuard live execution, SSH-based validation, iperf3 performance tests, or device-changing tasks.

## Validation Result

Day48 safe local validation commands:

```powershell
python -m pytest
python network_lab.py --task report-index
```

Observed result:

- `python -m pytest`: `487 passed, 1 warning in 2.48s`.
- The warning is the existing non-live `getpass` terminal echo warning seen in recent full-suite runs.
- `python network_lab.py --task report-index`: completed with `Overall result: [WARN]`.
- Report-index counts: `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- The two missing items are optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- The `WARN` result is acceptable because it is caused by existing optional missing generated reports, not by a live-device failure.

## Final Day48 Summary

Day48 adds a committed offline portfolio demo kit and roadmap note so the project can be presented safely without live infrastructure.

The kit gives the demo reviewer a predictable open order, safe command set, troubleshooting path, Traditional Chinese talk track, and explicit no-live-dependency statement. It builds on Day47 by turning the demo runbook into portable offline assets.
