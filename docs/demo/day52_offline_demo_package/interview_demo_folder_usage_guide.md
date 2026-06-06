# Day52 Interview Demo Folder Usage Guide

Open this file when preparing the Day52 offline demo package for an interview.

## What To Open First

1. `docs/demo/day52_offline_demo_package/README.md`
2. `docs/demo/day52_offline_demo_package/screenshots/dashboard_home.png`
3. `docs/demo/day52_offline_demo_package/screenshots/dashboard_reports.png`
4. `docs/demo/day52_offline_demo_package/screenshots/dashboard_commands.png`
5. `docs/demo/day52_offline_demo_package/screenshots/dashboard_ai_checklist.png`
6. `docs/demo/offline_interview_demo_kit/README.md` if you need the broader Day48 offline kit.

## Suggested Demo Order

1. Open the dashboard home screenshot.
   Say that the dashboard starts with the project purpose, demo status, proof points, and the no-live-router boundary.

2. Explain the reports page.
   Say that the reports page is a local evidence browser for generated JSON and HTML reports. It reads report metadata and does not start router, switch, VPN, VRRP, WireGuard, SSH, or iperf workflows.

3. Explain the commands page as safe command visibility, not live device execution.
   Say that commands are registered, visible, timed, and logged. The dashboard does not accept arbitrary shell input. Lab workflows that need real parameters or devices are not one-click interview actions.

4. Explain the AI checklist and safety boundary.
   Say that the checklist is review evidence for controls such as allowlists, `shell=False`, timeouts, redaction, and separation between AI assistance and direct device changes.

5. Explain that live tests are intentionally excluded from the offline interview package.
   Say that live tests belong in a separate guarded live demo plan, not in this Day52 package.

## If Optional Reports Are Missing

Missing optional generated local reports do not block the offline demo when `python network_lab.py --task report-index` returns `fail=0`.

Use this wording:

"The dashboard can show `WARN` when optional local reports are not present on this checkout. That is acceptable for the offline interview package as long as required checks are not failing and `fail=0`."

## What Not To Do

- Do not run live VRRP or WireGuard tests during the interview unless a separate guarded live demo plan is prepared.
- Do not connect to routers, switches, firewalls, VPN devices, WireGuard peers, or lab devices during this Day52 package step.
- Do not use SSH.
- Do not modify `config.json`.
- Do not change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.
- Do not start `v0.3` work from this package.
- Do not create a release tag from this package.
