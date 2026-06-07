# Day51 Visual QA Screenshot Notes

Use this folder for portfolio demo screenshots when a fresh local dashboard capture is useful. Screenshot files are optional; the repo should still be explainable from the committed docs and dashboard routes without binary images.

## Screenshots To Capture

| File name | Route | Purpose |
| --- | --- | --- |
| `01_dashboard_home.png` | `/` | Main portfolio demo landing page. Use this page to open the demo. |
| `02_reports_page.png` | `/reports` | Report evidence overview. Show this page after explaining the safety boundary. |
| `03_commands_page.png` | `/commands` | Safe command/reference page. Use this to explain allowlisted local commands and disabled lab workflows. |
| `04_ai_checklist_page.png` | `/ai-checklist` | Safety and AI readiness checklist. This page is optional if time is short. |

## How To Retake Screenshots

1. Run `python dashboard_app.py`.
2. Open `http://127.0.0.1:5000/`.
3. Capture each route at a normal laptop viewport.
4. Make sure the screenshot does not show unrelated browser tabs, private bookmarks, or local files outside the repo.
5. Retake all four screenshots after dashboard copy, layout, or route behavior changes.

## Portfolio Demo Notes

- Do not present WARN as a failure if `fail=0` and the missing items are optional local generated reports.
- Use the home page first; it gives the status, proof points, quick links, and safety boundary.
- Use Reports to show evidence, Commands to show command safety, and AI Checklist only when the demo reviewer asks about AI readiness or guardrails.
- Do not use screenshot capture as a substitute for route checks. Before a portfolio review, still confirm the pages return HTTP 200 locally.
