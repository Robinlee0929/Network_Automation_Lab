# Offline Demo Commands

These commands are PowerShell-friendly and safe for an offline interview demo. They are local/report-only commands and must not be replaced with live VRRP, WireGuard, SSH, iperf3, or device configuration workflows.

## Check Repository State

```powershell
git status --short --branch
git log --oneline -1
```

## Check Python

```powershell
python --version
```

## Run Local Tests

```powershell
python -m pytest
```

## Generate Report Index

```powershell
python network_lab.py --task report-index
```

If you want to preview report-index inputs and outputs without writing generated files:

```powershell
python network_lab.py --task report-index --dry-run
```

## Run Safe Demo Flow

```powershell
python network_lab.py --task demo-flow
```

## Show Runner Metadata

```powershell
python network_lab.py --list-tasks
python network_lab.py --list-tasks --verbose
```

## Start Dashboard Locally

```powershell
python dashboard_app.py
```

The dashboard binds to:

```text
http://127.0.0.1:5000/
```

## Open Local Dashboard and Reports

Run these in a second PowerShell window after the dashboard is running:

```powershell
Start-Process "http://127.0.0.1:5000/"
Start-Process "http://127.0.0.1:5000/reports"
```

If `Start-Process` is blocked, copy the URL into a local browser.

## Show Day47 and Day48 Documents

```powershell
Get-Content docs\roadmap\day47_interview_demo_baseline_final_check_runbook.md
Get-Content docs\roadmap\day48_demo_asset_packaging_offline_interview_demo_kit.md
Get-Content docs\demo\offline_interview_demo_kit\README.md
Get-Content docs\demo\offline_interview_demo_kit\interview_talk_track_3_to_5_min.md
```

## Optional Local File Listing

```powershell
Get-ChildItem docs\demo\offline_interview_demo_kit
Get-ChildItem docs\demo\offline_interview_demo_kit\screenshots
```

## Commands Not To Run During Offline Interview Demo

Do not run live-device tasks during the offline interview demo.

Avoid commands that:

- Open SSH sessions.
- Connect to MikroTik or Cisco devices.
- Run live VRRP validation.
- Run live WireGuard execution.
- Start iperf3 performance tests.
- Modify NAT, IP, VRRP, WireGuard, firewall, route, interface, reboot, reset, or device configuration.
- Create or modify `config.json`.
