# Offline Demo Troubleshooting Guide

Use this guide when the demo environment is missing local dependencies, generated evidence, internet, browser access, or lab devices.

## Dashboard Cannot Start

| Field | Detail |
| --- | --- |
| Symptom | `python dashboard_app.py` fails or Flask is unavailable. |
| Likely cause | Python dependencies are not installed on the review computer, or another process is using port `5000`. |
| Safe recovery action | Use `python -m pytest` and `python network_lab.py --task report-index` if available. If the dashboard still cannot run, continue with the committed docs and explain the dashboard route behavior is covered by tests. |
| Fallback explanation for reviewer | "The dashboard is a local evidence browser. The important architecture is the report model, route safety, and local evidence navigation; it does not need live devices." |

## Reports Page Missing

| Field | Detail |
| --- | --- |
| Symptom | `http://127.0.0.1:5000/reports` does not open or shows little evidence. |
| Likely cause | Dashboard is not running, the browser cannot access localhost, or ignored generated reports are absent from a clean checkout. |
| Safe recovery action | Start `python dashboard_app.py`, then open `/reports` again. If generated reports are missing, show `docs/portfolio_evidence.md`, Day47, Day48, and `runner_profiles/task_catalog.json`. |
| Fallback explanation for reviewer | "Generated reports are intentionally local working evidence and may not be committed. The demo can still show the report paths, safety metadata, and evidence design." |

## Pytest Fails

| Field | Detail |
| --- | --- |
| Symptom | `python -m pytest` exits with failures. |
| Likely cause | Missing dependencies, wrong Python environment, stale generated files, or a local environment difference. |
| Safe recovery action | Capture the failing test names, do not run live tasks, and continue with a document walkthrough if the failure is environment-related. |
| Fallback explanation for reviewer | "The test suite is local and non-live. If this machine is missing a dependency, I can still explain which behavior the tests cover and why hidden live dependencies are avoided." |

## Report-index Shows WARN

| Field | Detail |
| --- | --- |
| Symptom | `python network_lab.py --task report-index` completes but reports `WARN`. |
| Likely cause | Optional generated reports under ignored `reports/` folders are missing on the local machine. |
| Safe recovery action | Confirm the warning is about optional generated evidence, not a live-device failure. Use committed docs and known report paths to explain the expected evidence chain. |
| Fallback explanation for reviewer | "WARN is acceptable here when optional historical generated reports are absent. The index is honest about missing evidence instead of pretending it exists." |

## Missing Generated Reports

| Field | Detail |
| --- | --- |
| Symptom | Expected files under `reports/` are absent. |
| Likely cause | `reports/` is ignored because generated evidence can be machine-specific, historical, or sensitive. |
| Safe recovery action | Use committed roadmap, portfolio, summary, topology, and runner metadata files. Do not create live evidence during a portfolio review or offline demo. |
| Fallback explanation for reviewer | "The committed repository demonstrates the architecture and workflow. Generated reports are normally produced by safe local or controlled lab runs, but they are not required for this offline portfolio demo." |

## Browser Cannot Open Local Page

| Field | Detail |
| --- | --- |
| Symptom | `Start-Process "http://127.0.0.1:5000/reports"` fails or browser launch is blocked. |
| Likely cause | Browser restrictions, no GUI access, local security policy, or dashboard not running. |
| Safe recovery action | Keep the dashboard command window open if it started successfully. Read the documents directly with `Get-Content` or open them in the editor. |
| Fallback explanation for reviewer | "The browser is only a presentation surface. The same evidence model is visible from committed Markdown, JSON metadata, and tests." |

## Demo Site Has No Internet

| Field | Detail |
| --- | --- |
| Symptom | GitHub, package installation, or online references are unavailable. |
| Likely cause | Offline demo environment or restricted network. |
| Safe recovery action | Use the local checkout only. Open Day47, Day48, README, task catalog, safety levels, and committed portfolio docs. |
| Fallback explanation for reviewer | "The offline kit was created specifically so the demo does not depend on GitHub or internet access." |

## Cannot Connect To Router Or Switch

| Field | Detail |
| --- | --- |
| Symptom | Router, switch, VPN, WireGuard, or lab device access is unavailable. |
| Likely cause | The demo environment is intentionally offline or not connected to the lab. |
| Safe recovery action | Do not attempt SSH or live validation. Use the offline kit, Day47 runbook, task catalog, safety levels, topology docs, and existing evidence references. |
| Fallback explanation for reviewer | "Live testing is intentionally separated from the portfolio demo flow. The demo focuses on architecture, safety, repeatability, and evidence design without touching devices." |
