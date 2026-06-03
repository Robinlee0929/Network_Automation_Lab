# Portfolio Demo Script - v0.1

## Purpose

This document provides a 5 to 10 minute reviewer/interview demo script for the current v0.1 state of Network Automation Lab.

The goal is to help a reviewer, interviewer, or technical hiring manager understand what the platform already demonstrates without changing platform behavior, starting live VPN execution, or touching real device configuration.

## Audience

- Reviewer
- Interviewer
- Technical hiring manager

## Demo Duration

5 to 10 minutes.

## What This Demo Shows

- A Python-based network automation lab platform for infrastructure validation.
- MikroTik hEX S router validation workflows.
- Cisco switch topology validation workflows.
- WireGuard VPN validation evidence from existing report output.
- iperf3 throughput evidence from existing performance reports.
- A unified runner and task catalog concept for organizing lab actions.
- A dashboard and report-viewer concept for local evidence browsing.
- JSON and HTML report outputs for automation and human review.
- Portfolio evidence organization across README, docs, and ignored local report folders.
- A safety-first automation boundary that separates report-only, read-only, guarded-live, dry-run, and disabled behavior.

## What This Demo Does NOT Do

- It does not add features.
- It does not modify runner behavior.
- It does not modify dashboard behavior.
- It does not start live VPN execution.
- It does not apply configuration to routers, switches, or VPN clients.
- It does not run device-changing commands.
- It does not commit generated reports, exports, real configs, secrets, passwords, private keys, or WireGuard config files.

## Safety Boundaries

Keep the demo focused on repository structure, existing report evidence, safe metadata, and local read-only views.

Use these boundaries during the demo:

- Prefer `--list-tasks`, `--report-index`, portfolio docs, and existing report viewer pages.
- Treat live-device scripts as evidence sources, not as commands to run during an interview unless the lab is prepared and explicit consent is given.
- Do not show or open real secret files, exported WireGuard `.conf` files, private keys, or local password-bearing configs.
- Do not paste secrets into the terminal, README, docs, chat, PRs, screenshots, or reports.
- Keep generated `reports/`, `exports/`, caches, local configs, and WireGuard config files out of Git.

## Suggested Repository Walkthrough

Start at `README.md` and explain the project in one sentence:

> This is a Python-based network automation lab that validates MikroTik routers, a Cisco switch, WireGuard VPN evidence, throughput measurements, and report visibility in a safety-first portfolio format.

Then walk through the repository at a high level:

- `network_lab.py` is the unified runner entry point and task catalog.
- `mikrotik_*` scripts contain MikroTik validation and automation workflows.
- `cisco_topology_validation.py` contains Cisco switch topology validation.
- `performance_test.py` and `performance_regression.py` cover iperf3 throughput evidence and regression-style checks.
- `dashboard_app.py` and `templates/` provide the local dashboard and report viewer concept.
- `docs/portfolio_evidence/` stores committed portfolio review notes.
- `reports/`, `exports/`, and real configs remain local working artifacts and should not be committed.

## Suggested Runner Demonstration

Show the task catalog first:

```powershell
python network_lab.py --list-tasks --verbose
```

Explain what to look for:

- Task IDs and day labels show the growth of the platform.
- Safety labels make the execution model explicit.
- Report-only tasks can index or summarize local evidence.
- Read-only tasks inspect state.
- Guarded-live tasks require explicit confirmation before touching lab devices.
- Dry-run tasks preview planned actions.
- Disabled tasks intentionally block unsupported or unsafe execution.

If local reports are available, show the report index command:

```powershell
python network_lab.py --report-index
```

Then explain:

- The runner can inventory expected evidence without connecting to devices.
- Missing reports are visible as missing evidence instead of causing a crash.
- Existing JSON and HTML reports are linked for human review.

## Suggested Dashboard / Report-Viewer Demonstration

Start the local dashboard only if it is appropriate for the demo environment:

```powershell
python dashboard_app.py
```

Open:

```text
http://127.0.0.1:5000/reports
```

Explain the report-viewer concept:

- The dashboard is a local evidence browser.
- The `/reports` page groups available evidence by day and task.
- JSON previews are readable and should stay redacted.
- HTML report links open existing local reports.
- Missing reports are shown clearly.
- The report viewer does not start live validation, apply device changes, activate VPN clients, or reveal secrets.

## Suggested Evidence / Report Walkthrough

If reports exist locally, use a small curated path instead of opening everything.

Suggested evidence order:

1. MikroTik hEX S validation evidence.
2. Cisco switch topology validation evidence.
3. Lab-level topology summary.
4. iperf3 throughput evidence.
5. WireGuard VPN validation evidence.
6. Runner report index or portfolio evidence index.
7. Day24 demo flow, Day25 RC validation evidence, Day26 release documentation, and Day28 final review notes.

Useful committed documentation:

```text
docs/portfolio_evidence.md
docs/portfolio_evidence/day25_v0.1_rc_validation.md
docs/portfolio_evidence/v0.1_release_notes.md
docs/portfolio_evidence/v0.1_portfolio_checklist.md
```

Useful local report examples when generated:

```text
reports/report_index.html
reports/portfolio/day19_runner_evidence_index.html
reports/portfolio/day24_rc_demo_flow.html
reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.html
reports/Hex-s-2025-lab01/day9_performance_regression_report.html
reports/cisco-switch/switch_topology_report.html
```

Keep the explanation focused on evidence design:

- JSON reports support automation, regression comparison, and future integration.
- HTML reports support reviewer-friendly reading, screenshots, and portfolio demos.
- Report organization shows expected scope, actual output, pass/fail/warning state, and missing evidence.

## Suggested Speaking Script

Opening:

> Network Automation Lab is my Python-based infrastructure validation platform. It started with MikroTik router checks and grew into a small multi-vendor lab story with Cisco topology validation, iperf3 throughput evidence, WireGuard VPN validation evidence, a unified runner, and a local report viewer.

Safety positioning:

> The important design choice is that the platform separates evidence browsing from live execution. For a portfolio or interview demo, I can show the task catalog, report index, dashboard viewer, and generated evidence without applying device-changing commands or exposing secrets.

Runner walkthrough:

> The unified runner makes the lab easier to review because tasks are cataloged with names, days, safety levels, execution modes, related scripts, and report paths. That turns a folder of scripts into a platform-style interface.

MikroTik and Cisco validation:

> On the MikroTik side, the project validates router identity, baseline state, WAN/LAN expectations, SSH availability, and later VPN-related evidence. On the Cisco side, it validates topology-oriented switch facts such as model, interface state, VLAN behavior, MAC learning, and spanning-tree evidence.

Performance and VPN evidence:

> The iperf3 workflows capture throughput evidence as structured JSON and readable HTML. The WireGuard work records validation evidence while keeping real client configs, private keys, and exported `.conf` files outside Git and outside the reports.

Dashboard/report viewer:

> The dashboard is intentionally local and evidence-oriented. It gives a reviewer a faster way to inspect generated JSON and HTML reports, including missing evidence, without implying that the browser page is changing the network.

Close:

> v0.1 is not trying to be a production NMS. It is a safety-first automation portfolio that shows how I structure network validation, evidence, report visibility, and guardrails as an engineering system.

## Demo Checklist

Before the demo:

- Confirm the working tree does not include generated reports, exports, real configs, secrets, passwords, private keys, or WireGuard config files.
- Confirm any screenshots or reports you plan to show are safe to share.
- Confirm the dashboard, if used, is pointed at local evidence only.
- Run the test suite when preparing the repo for review.

During the demo:

- Start with README scope and v0.1 positioning.
- Show the unified runner task catalog.
- Show safety labels and execution modes.
- Show the report index or dashboard report viewer.
- Walk through one router, one switch, one performance, and one VPN evidence example.
- End with release notes, portfolio checklist, and next steps.

After the demo:

- Do not commit generated report output.
- Do not commit local configs, exports, or WireGuard `.conf` files.
- Keep any follow-up changes scoped and documented.

## Troubleshooting / Fallback

If the dashboard is not available:

- Use `README.md`, `docs/portfolio_evidence.md`, and committed release docs.
- Open existing local HTML reports directly from `reports/` if they are safe and available.
- Use `python network_lab.py --list-tasks --verbose` to show runner metadata without the dashboard.

If generated reports are missing:

- Explain that generated reports are intentionally ignored by Git.
- Show the expected report paths in README.
- Use committed portfolio evidence docs to explain the validation story.
- Avoid running live-device workflows unless the lab is ready and explicit permission is given.

If a live lab is unavailable:

- Keep the demo repository-only.
- Emphasize unit tests, parser coverage, safety metadata, and report schema design.
- Show how missing evidence is represented instead of treated as an unhandled error.

If tests fail during preparation:

- Do not hide the failure.
- Capture the failing test names.
- Explain whether the failure is documentation-related, environment-related, or behavior-related before changing anything.

## Next-Step Roadmap

Potential post-v0.1 directions:

- Add clearer versioned demo fixtures that are safe to commit.
- Improve dashboard filtering and evidence comparison while preserving read-only behavior.
- Add richer report summaries for reviewer navigation.
- Expand read-only validation coverage for additional lab devices.
- Add AI-assisted report summarization only after the evidence model and secret-handling rules remain explicit.
- Keep all future live execution behind clear safety labels, confirmations, and documentation.
