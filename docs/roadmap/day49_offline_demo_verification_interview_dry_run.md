# Day49 - Offline Demo Verification / Portfolio Demo Dry Run

## Objective

Verify that the Day48 offline portfolio demo kit is usable for a 3-5 minute portfolio walkthrough without live network devices, internet access, GitHub access, SSH, WireGuard peers, VRRP failover, iperf3 endpoints, or generated local screenshots.

Day49 is a documentation/report-only/offline-only dry run. It checks the portfolio demo flow, safe command list, dashboard/report explanation path, Traditional Chinese talk track, and fallback story for missing local artifacts.

## Scope

- Review the Day48 offline demo kit from committed files.
- Confirm the demo can be explained from local source, docs, tests, report-index output, and dashboard route behavior.
- Run only safe offline validation commands.
- Document readiness notes for optional generated reports and optional screenshots.
- Update README roadmap/progress references for Day49.

## Safety Constraints

Day49 did not run live network tests.

Day49 did not use SSH, connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peers, or iperf3 endpoints, run live VRRP validation, run WireGuard live execution, or modify NAT, IP, VRRP, WireGuard, firewall, interface, route, reboot, reset, or device configuration.

Day49 did not create, modify, or depend on `config.json`.

## Reviewed Day48 Demo Kit Files

Reviewed:

- `docs/demo/offline_interview_demo_kit/README.md`
- `docs/demo/offline_interview_demo_kit/demo_checklist.md`
- `docs/demo/offline_interview_demo_kit/demo_commands.md`
- `docs/demo/offline_interview_demo_kit/troubleshooting_guide.md`
- `docs/demo/offline_interview_demo_kit/interview_talk_track_3_to_5_min.md`
- `docs/demo/offline_interview_demo_kit/no_live_dependency_statement.md`
- `docs/demo/offline_interview_demo_kit/screenshots/README.md`

Note: the Day49 brief referred to `interview_talk_track_zh.md`, but the committed Day48 kit stores the Traditional Chinese 3-5 minute talk track at `interview_talk_track_3_to_5_min.md`. The README and Day48 roadmap document both point to the committed path, so the talk track is available for the portfolio demo flow.

## Offline Demo Dry-run Checklist

| Check | Result | Notes |
| --- | --- | --- |
| 3-5 minute portfolio demo flow has enough material | PASS | README open order, checklist, commands, talk track, troubleshooting guide, and no-live-dependency statement form a complete walkthrough. |
| Demo can be explained without live routers or switches | PASS | The kit explicitly separates portfolio demo behavior from live-device validation. |
| Dashboard demo path is clear | PASS | `python dashboard_app.py`, `/`, and `/reports` are documented; route behavior is covered by local tests. |
| Reports/report-index path is clear | PASS WITH NOTES | `report-index` completed with acceptable optional missing-report WARN and `fail=0`. |
| Safe commands are listed | PASS | Commands are local/report-only and the kit warns against SSH, live VRRP, live WireGuard, iperf3, and configuration changes. |
| Traditional Chinese talk track is usable | PASS WITH NOTES | The talk track is present and portfolio-ready under `interview_talk_track_3_to_5_min.md`; only the alternate filename from the Day49 brief is absent. |
| Fallback explanations are present | PASS | Troubleshooting guide covers dashboard, reports, pytest, WARN, generated reports, browser, internet, and device access limits. |
| No live dependency is required | PASS | The no-live-dependency statement is explicit and aligned with the checklist and commands. |

## Validation Commands and Results

Start state:

```powershell
git status --short --branch
git branch --show-current
git pull origin main
git switch -c day49-offline-demo-verification-interview-dry-run
```

Observed start result:

- Started from `main`.
- `git pull origin main` returned `Already up to date.`
- Created branch `day49-offline-demo-verification-interview-dry-run`.

Offline validation:

```powershell
python -m pytest
```

Result:

- `487 passed, 1 warning in 2.47s`.
- The warning is the existing non-live `getpass` terminal echo warning in `tests/test_day13_multi_router_wireguard_validation.py::test_multi_device_live_validation_reminds_before_next_router`.

```powershell
python network_lab.py --task report-index
```

Result:

- Overall result: `[WARN]`
- Counts: `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- Generated/updated local ignored report-index outputs:
  - `reports/lab-summary/latest_lab_overview.json`
  - `reports/lab-summary/latest_lab_overview.html`

The `WARN` is acceptable for Day49 because `fail=0` and the missing items are optional generated local reports, not live-device failures.

## Dashboard Readiness Result

Dashboard readiness: PASS.

The Day48 kit gives a clear local dashboard path:

```powershell
python dashboard_app.py
Start-Process "http://127.0.0.1:5000/"
Start-Process "http://127.0.0.1:5000/reports"
```

Day49 did not require browser automation or a live Flask launch. Readiness was verified by the passing dashboard test coverage and static route inspection:

- `tests/test_dashboard_app.py` covers dashboard app creation, `/reports`, report JSON/open routes, evidence route behavior, and empty/missing report directory behavior.
- `dashboard_app.py` defines local routes for `/`, `/reports`, `/commands`, report open/JSON/evidence views, and WireGuard report drill-down.

## Reports Readiness Result

Reports readiness: READY WITH NOTES.

The report-index path is usable for an offline demo. The observed WARN is acceptable because it has `fail=0` and is caused by optional generated local reports that may be absent from a clean checkout or review machine.

The demo explanation should state that generated reports are local evidence and may be intentionally uncommitted, while committed docs, source, task metadata, and tests still demonstrate the architecture and safety model.

## Commands Readiness Result

Commands readiness: PASS.

The safe command list is portfolio-ready and focuses on:

- Git/Python environment checks.
- `python -m pytest`.
- `python network_lab.py --task report-index`.
- `python network_lab.py --task demo-flow`.
- Local dashboard startup and local browser opening only after Flask is running.
- Local documentation viewing.

The command list also explicitly warns not to run live-device workflows during the offline portfolio demo.

## Talk Track Readiness Result

Talk track readiness: READY WITH NOTES.

The Traditional Chinese talk track is usable for a 3-5 minute portfolio presentation. It explains:

- The project problem and why manual SSH checks are hard to repeat.
- Safety levels and demo boundaries.
- Unified Runner.
- Report Index and Dashboard.
- VRRP evidence chain.
- WireGuard direction.
- Why the demo can run without live devices.
- What demo reviewers should notice.

The only note is filename alignment: the committed talk-track file is `interview_talk_track_3_to_5_min.md`, while the Day49 brief mentioned `interview_talk_track_zh.md`.

## Fallback Readiness Result

Fallback readiness: PASS.

The troubleshooting guide includes usable explanations for:

- Dashboard cannot start.
- Report-index returns WARN because optional local reports are missing.
- Screenshots are not available.
- No live network devices are connected.
- Browser cannot open a local page.
- Demo site has no internet.
- Generated reports are absent.
- Local Python/pytest environment is incomplete.

For demo reviewer requests to run live VRRP or WireGuard execution, the fallback explanation is covered by the command safety warnings and no-live-dependency statement: live testing is intentionally separated from the portfolio demo and should only be run in a controlled lab with explicit operator intent.

## Known Limitations

- Optional generated local reports can be missing from the review machine, causing acceptable report-index WARN output with `fail=0`.
- Optional screenshot binaries are not required and may be absent.
- The dashboard may not launch if the review machine lacks dependencies or cannot open localhost; the docs and tests remain sufficient for the offline walkthrough.
- The Day49 brief names `interview_talk_track_zh.md`, but the committed Day48 kit uses `interview_talk_track_3_to_5_min.md` for the Traditional Chinese talk track.
- Day49 does not prove live VRRP, WireGuard, iperf3, SSH, or device configuration behavior.

## Final Portfolio Demo Status

Overall status: READY WITH NOTES

Reason: Offline portfolio demo flow is usable, but optional generated local reports/screenshots may still depend on local artifacts that are intentionally not committed.

## Recommended Next Step

Use the Day48 kit as the portfolio demo entry point and keep Day49 as the verification note. If more polish is needed, the next small offline task should align the talk-track filename referenced by future briefs and optionally add curated non-sensitive screenshots, without adding live-device dependencies.
