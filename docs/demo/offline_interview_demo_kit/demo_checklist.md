# Offline Demo Checklist

Use this checklist before an interview. All commands are local and non-live.

## Pre-interview Checks

```powershell
git status --short --branch
python --version
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task demo-flow
```

## Local Demo Readiness

- Confirm the dashboard can start locally:

```powershell
python dashboard_app.py
```

- Confirm the dashboard home page can open:

```powershell
Start-Process "http://127.0.0.1:5000/"
```

- Confirm the reports page can open:

```powershell
Start-Process "http://127.0.0.1:5000/reports"
```

- Confirm the demo documents are available offline:

```powershell
Get-ChildItem docs\demo\offline_interview_demo_kit
Get-ChildItem docs\roadmap\day47_interview_demo_baseline_final_check_runbook.md
Get-ChildItem docs\roadmap\day48_demo_asset_packaging_offline_interview_demo_kit.md
```

- Confirm no live device connection is required:

```powershell
Get-Content docs\demo\offline_interview_demo_kit\no_live_dependency_statement.md
```

## Interview Go/No-go

| Check | Ready condition |
| --- | --- |
| Repository state | Branch and working tree are explainable with `git status --short --branch`. |
| Python | `python --version` returns a usable Python version. |
| Tests | `python -m pytest` passes. |
| Report index | `report-index` completes with `PASS` or acceptable optional-report `WARN`. |
| Demo flow | `demo-flow` completes locally. |
| Dashboard | Dashboard starts locally, or the fallback document walkthrough is ready. |
| Reports page | `/reports` opens locally, or missing generated reports are explained as optional local evidence. |
| Offline docs | Day47 and Day48 documents are present. |
| Safety | No SSH, live device connection, VPN, WireGuard, iperf3, or config change is needed. |
