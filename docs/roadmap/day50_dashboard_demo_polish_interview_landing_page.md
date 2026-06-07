# Day50 - Dashboard Demo Polish / Portfolio Demo Landing Page

## Objective

Polish the dashboard home page into a portfolio-review-friendly landing page that quickly explains what Network Automation Lab solves, what evidence it can show, how the safe demo flow works, and why the project can be demonstrated without live lab access.

Day50 is documentation, dashboard UI, and test coverage only. It does not start a new release line, create `v0.2.1`, or begin `v0.3` work.

## Scope

- Improve the dashboard `/` route as the primary portfolio demo landing page.
- Keep existing dashboard routes available: `/reports`, `/commands`, and `/ai-checklist`.
- Add quick links to report evidence, safe command execution, AI checklist, and the offline portfolio demo kit.
- Document the 3-5 minute portfolio demo flow and safety boundary.
- Add route coverage so the landing page remains available from a clean local checkout.

## What Changed

- Reworked `templates/dashboard_home.html` into `Network Automation Lab - Portfolio Demo`.
- Added a demo status card showing `READY WITH NOTES`.
- Added proof-point cards for Unified Runner, Safety Guard / AI Checklist, VRRP evidence and topology planning, WireGuard automation safety, report index/dashboard viewer, and the offline portfolio demo kit.
- Added a recommended 3-5 minute portfolio demo flow.
- Added a clear safety boundary: `This demo does not require live router access. Live tests are separated from report-only and read-only tasks.`
- Kept the existing report readiness cards so generated local report availability remains visible.
- Added a Flask test that verifies `/` returns HTTP 200 and contains the key portfolio demo text.

## Demo Flow

1. Open the dashboard landing page at `/`.
2. Show Reports for report index evidence, latest overview, VRRP evidence, and WireGuard summaries.
3. Show AI Checklist for command, dashboard, report, and WireGuard safety controls.
4. Show Commands or the offline demo kit for safe local demo commands and fallback flow.
5. Explain that live device actions are guarded and not triggered directly by voice or AI.

## Safety Result

Day50 did not run live network tests.

Day50 did not use SSH, connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peers, or iperf3 endpoints, run live VRRP validation, run WireGuard live execution, or modify NAT, IP, VRRP, WireGuard, firewall, interface, route, reboot, reset, or device configuration.

Day50 did not create, modify, or depend on `config.json`.

## Validation Result

Validation commands for Day50:

```powershell
python -m pytest
python network_lab.py --task report-index
```

Expected result:

- `python -m pytest` should pass.
- `python network_lab.py --task report-index` may return `WARN` only when optional generated local reports are missing and `fail=0`.

Observed result:

- `python -m pytest`: `488 passed, 1 warning in 3.61s`.
- `python network_lab.py --task report-index`: overall result `[WARN]`, counts `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- Generated/updated ignored local overview outputs:
  - `reports/lab-summary/latest_lab_overview.json`
  - `reports/lab-summary/latest_lab_overview.html`

The `report-index` WARN is acceptable for Day50 because `fail=0` and the missing items are optional generated local reports.

## Known Notes

- Optional generated reports are local evidence and may be intentionally absent from a clean checkout.
- `report-index` WARN remains acceptable when missing items are optional generated local reports and `fail=0`.
- The dashboard landing page is a presentation surface, not a live device control surface.
