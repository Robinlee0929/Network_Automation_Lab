# Portfolio Evidence Guide

This repository is a network automation lab portfolio. It demonstrates repeatable validation for MikroTik routers, Cisco topology checks, iperf3 performance testing, WireGuard VPN validation, and a unified runner that indexes local evidence.

## What To Review

- `python network_lab.py --list-tasks` shows user-facing runner tasks.
- `python network_lab.py --list-tasks --verbose` shows day metadata, scripts, report paths, and safety notes.
- `python network_lab.py --report-index` creates `reports/report_index.html` from local report files.
- `python network_lab.py --portfolio-finalize` creates `reports/portfolio/day19_runner_evidence_index.html`.
- `python network_lab.py --task demo-flow` creates `reports/portfolio/day24_rc_demo_flow.html`.

Generated `reports/` output is intentionally ignored by git. Reviewers can regenerate it locally from test fixtures or from real lab evidence.

## Safety Model

- Report index and portfolio finalization are local-only. They read report metadata and do not connect to devices.
- Day4 baseline and Day8 iperf3 workflows are live-device tasks and remain behind explicit runner actions or confirmation.
- WireGuard runner is dry-run by default. Guarded live validation requires explicit flags and does not delegate unsafe Day12 flags such as peer recreation or firewall fixes.
- Day13 WireGuard summary remains report-only in the runner until it has its own safety layer.
- Dashboard report browsing is read-only. The `/reports` viewer opens grouped evidence cards, redacted JSON preview, and safe HTML links for already-generated evidence only.
- Day24 demo flow is report-only. It creates a reviewer walkthrough and does not connect to lab devices, start VPN validation, run iperf3, or read local secrets.

## Evidence Locations

- Latest runner overview: `reports/lab-summary/latest_lab_overview.html`
- Report visibility index: `reports/report_index.html`
- Day18 WireGuard runner evidence: `reports/lab-summary/wireguard_runner_safety_layer.html`
- Day21 dashboard evidence viewer: `/reports`
- Portfolio evidence index: `reports/portfolio/day19_runner_evidence_index.html`
- Day24 RC demo flow: `reports/portfolio/day24_rc_demo_flow.html`

The report index marks missing files as unavailable instead of failing. It also includes report type, availability, safety label, description, and links to JSON/HTML evidence when present.

## Reviewer Evidence Path

Start with `python network_lab.py --task demo-flow` when preparing an RC or portfolio walkthrough. It writes a safe open order and talk track that starts with README context, continues through task safety metadata and report visibility, then closes with the dashboard `/reports` viewer and portfolio evidence.

For a deeper review, run `python network_lab.py --list-tasks --verbose` to understand automation scope, safety labels, execution modes, and report outputs. Then use the dashboard `/reports` viewer or `reports/report_index.html` to inspect generated evidence without starting live workflows.

Use the README to confirm safety boundaries, especially the difference between report-only, read-only, dry-run, guarded-live, and disabled tasks. Not every runner task is live execution, and WireGuard live behavior is intentionally guarded by explicit CLI flags or interactive confirmation.

Run `python -m pytest` to confirm regression safety. The catalog and report visibility tests do not require router access, SSH, iperf3, VPN activation, generated reports, or local secrets.

Day25 RC readiness checklist:

- Runner task metadata is complete.
- Safety labels are consistent.
- Report outputs are traceable.
- `/reports` viewer remains functional and read-only.
- WireGuard tasks remain guarded.
- Day24 demo flow remains report-only.
- No destructive live behavior was introduced.
- Full pytest suite passes.

## Secret Handling

Generated evidence should not include SSH passwords, WireGuard private keys, `.conf` contents, or local config secrets. Config files, exports, backups, and generated reports stay ignored by git.
