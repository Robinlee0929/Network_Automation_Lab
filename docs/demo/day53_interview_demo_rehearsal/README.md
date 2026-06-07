# Day53 Portfolio Demo Rehearsal

This folder contains the final Day53 portfolio demo rehearsal materials for Network Automation Lab. Use it before a public project review, portfolio walkthrough, or interview to keep the demo short, safe, and repeatable.

## Files

| File | Use |
| --- | --- |
| `demo_opening_script_zh.md` | Traditional Chinese opening script for framing the project and safety boundary. |
| `three_to_five_minute_demo_sequence_zh.md` | Ordered 3-5 minute demo sequence. |
| `common_interview_qa_zh.md` | Prepared answers for likely reviewer or evaluator questions. |
| `final_operation_checklist.md` | Final rehearsal and operation checklist. |

## Demo Path

Use the local dashboard and committed evidence path when available:

```powershell
python -m pytest
python network_lab.py --task report-index
python dashboard_app.py
```

Then open:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/reports
http://127.0.0.1:5000/commands
http://127.0.0.1:5000/ai-checklist
```

If the dashboard cannot open, use the Day52 screenshot package:

```text
docs/demo/day52_offline_demo_package/
```

## Safety Statement

Day53 is documentation-only and rehearsal-only. It does not execute live network tests, does not use SSH, does not connect to network devices, does not modify router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration, does not create or edit `config.json`, does not create release tags, and does not start `v0.3`.
