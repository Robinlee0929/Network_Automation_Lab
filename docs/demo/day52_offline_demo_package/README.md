# Day52 Offline Demo Package

This folder is the final Day52 offline interview demo package for Network Automation Lab. It combines real local dashboard screenshots with a short usage guide so the demo can be shown even when GitHub, internet access, live devices, SSH, VPN, WireGuard, VRRP, or lab access are unavailable.

## Purpose

Use this package to present the dashboard pages as stable interview evidence without running live network workflows. The screenshots were captured from the local Flask dashboard at `http://127.0.0.1:5000/`.

## Screenshot List

| Screenshot | Dashboard route | Interview use |
| --- | --- | --- |
| `screenshots/dashboard_home.png` | `/` | Open the demo and explain project purpose, status, proof points, and safety boundary. |
| `screenshots/dashboard_reports.png` | `/reports` | Show generated evidence visibility and explain optional missing local reports. |
| `screenshots/dashboard_commands.png` | `/commands` | Explain allowlisted local commands, disabled lab workflows, and command visibility without arbitrary shell input. |
| `screenshots/dashboard_ai_checklist.png` | `/ai-checklist` | Explain AI/safety review boundaries and concrete code-level controls. |

## Open The Dashboard Locally

From the repository root:

```powershell
python dashboard_app.py
```

Then open:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/reports
http://127.0.0.1:5000/commands
http://127.0.0.1:5000/ai-checklist
```

If the report index needs to be refreshed for local dashboard context, use only the report-only task:

```powershell
python network_lab.py --task report-index
```

A `WARN` result is acceptable for this package when `fail=0` and the missing items are optional generated local reports.

## Interview Use

Start with `screenshots/dashboard_home.png` if the dashboard cannot be opened live. If the dashboard is available, open the live home page first and keep these screenshots as backup evidence.

Use the screenshots to keep the demo moving:

1. Home: project purpose, `READY WITH NOTES`, proof points, and no-live-router boundary.
2. Reports: generated evidence browser and optional missing-report explanation.
3. Commands: safe command visibility, allowlisted local commands, disabled lab workflows, and logs.
4. AI Checklist: safety controls for AI-assisted review and command boundaries.

## Safety Statement

This is an offline demo only.

Day52 does not run live network tests, use SSH, connect to devices, depend on or modify `config.json`, or change router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration.

Day52 does not start `v0.3` work and does not create a release tag.
