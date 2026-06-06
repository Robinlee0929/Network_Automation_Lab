# Day47 - Interview Demo Baseline Final Check / Demo Operation Runbook

## Purpose

Day47 finalizes the current `main` branch as the interview demo baseline.

The goal is stable local demo operation: clear navigation, clear safety boundaries, and a predictable explanation path for interviews. Day47 is not a release-tagging task and does not start new feature development.

## Scope

- Current `main` branch demo baseline
- Dashboard demo readiness
- Report index readiness
- Runner task catalog visibility
- Portfolio evidence visibility
- Safe explanation flow for an interview
- No live device dependency

## Explicit Non-goals

- No `v0.2.1` tag creation
- No GitHub release
- No `v0.3` feature work
- No live VRRP test
- No live WireGuard test
- No SSH
- No device configuration change

## Demo Baseline Assumptions

- The interview demo baseline should work from `main`.
- The demo should rely on committed source code and committed documentation.
- The demo must not require ignored local files such as `config.json`.
- Existing generated reports under ignored local report folders are optional demo evidence, not required test inputs.
- Missing local historical reports may produce warnings in dashboard or report-index views; that behavior is explainable and expected because generated evidence is intentionally not committed.
- The safe baseline demo should remain useful on an interview computer without access to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard, or iperf3 endpoints.

## Interview Demo Operation Runbook

### 1. Check Repository Status

Use a clean branch state as the starting point:

```powershell
git status --short --branch
git log --oneline -1
```

Expected story: current `main` is the corrected interview demo baseline after Day44-Day46. Day47 documents how to operate that baseline safely.

### 2. Run Full Local Regression Tests

Run the local test suite:

```powershell
python -m pytest
```

Expected story: pytest exercises parser logic, command builders, report generation behavior, dashboard helpers, and runner metadata without requiring live device access.

### 3. Launch or Explain the Dashboard

For a live local dashboard walkthrough, use:

```powershell
python dashboard_app.py
```

Then open:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/reports
```

If starting a server is not desirable during the interview, explain that the dashboard is the local human review surface for generated JSON / HTML evidence and that route behavior is covered by the test suite.

### 4. Show the Reports Page or Report Index

Show the dashboard `/reports` page when local generated evidence is available.

For a safe report-index preview without requiring live devices:

```powershell
python network_lab.py --task report-index --dry-run
```

Expected story: the report index reads local report metadata and visibility rules. It does not connect to devices. Missing ignored reports should be treated as optional historical evidence rather than a demo blocker.

### 5. Show Runner Task Catalog Entry Points

Show the runner catalog and the user-facing command entry point:

```powershell
python network_lab.py --list-tasks
```

Useful files to point at:

```text
runner_profiles/task_catalog.json
runner_profiles/safety_levels.json
network_lab.py
```

Expected story: tasks declare execution mode, report outputs, safety category, and live-device expectations so the platform can separate local/report-only workflows from guarded live workflows.

### 6. Show the Safety Model

Use these committed docs and metadata:

```text
docs/roadmap/ha_vrrp_safety_model.md
runner_profiles/safety_levels.json
README.md
```

Expected story: the project deliberately separates report-only, read-only, dry-run, guarded-live, and disabled behavior. Live operations are intentionally guarded and should not be triggered during the interview baseline demo.

### 7. Show VRRP Evidence as Portfolio Material

Use committed roadmap and portfolio materials:

```text
docs/roadmap/day35_vrrp_failover_validation_plan.md
docs/roadmap/day35_vrrp_failover_validation_safety.md
docs/roadmap/day36_vrrp_failover_evidence_review_report_hardening.md
docs/roadmap/day37_vrrp_report_regression_evidence_policy.md
docs/roadmap/day39_vrrp_evidence_dashboard_integration.md
docs/portfolio_v0.2_demo_checklist.md
docs/portfolio/v0.2_demo_handoff_guide.md
```

Expected story: VRRP validation is presented as documented, safety-scoped portfolio evidence. The interview demo does not run a live failover.

### 8. Show WireGuard Evidence as Portfolio Material

Use committed runner and report documentation:

```text
docs/portfolio_demo_script.md
docs/portfolio_demo_script_zh-TW.md
runner_profiles/task_catalog.json
topology_profiles/day13_wireguard_client_to_site_profiles.json
summary/day13_multi_router_wireguard_client_to_site_summary_20260602_022950.html
summary/day13_multi_router_wireguard_client_to_site_summary_20260602_022950.json
```

Expected story: WireGuard work is visible as guarded runner and portfolio evidence. The interview baseline demo does not run a live WireGuard test or export secrets.

### 9. Explain Guarded Live Operations

Close the demo by explaining that live network actions exist only behind explicit task selection, profile requirements, prompts, and safety levels. Day47 intentionally uses documentation, local tests, local dashboard/report visibility, and committed evidence paths instead of connecting to devices.

## Recommended Interview Narrative

Problem: manual network validation is repetitive, hard to compare, and risky when every check depends on ad hoc SSH sessions and copied command output.

Solution: Network Automation Lab turns common network validation work into repeatable Python workflows with structured JSON / HTML evidence, local dashboard review, and regression tests.

Key design: the platform is organized around a runner, safety levels, reports, dashboard views, and an evidence index. Device-specific scripts stay explicit, while shared parsing, report, and runner conventions keep the lab understandable.

Reliability: pytest regression coverage and fresh-checkout verification protect the local baseline from hidden dependencies such as ignored `config.json`.

Safety: read-only, report-only, dry-run, guarded-live, and disabled tasks are separated. The demo baseline is local and documentation/report oriented.

Future direction: v2.0 platform completion, followed later by v3.0 Voice + AI Network Test Assistant as a feature-level roadmap direction.

## Demo Risk Checklist

| Risk | Mitigation |
| --- | --- |
| Missing ignored reports | Explain that generated reports are intentionally local and optional; committed docs and tests are the baseline. |
| Dashboard report WARN | Explain that optional historical reports may be absent on a clean machine and that warnings preserve evidence honesty. |
| Live device not available | Use the local documentation, dashboard/report-only explanation, task catalog, and committed portfolio evidence. |
| Interview computer network unavailable | The core demo still works locally from committed code and docs; live network access is not required. |
| User accidentally triggers live task | Explain guarded flags, task metadata, prompts, safety levels, and the Day47 non-live scope before running anything. |

## Final Day47 Decision

- Current `main` remains the interview demo baseline.
- `v0.2.1` tag creation is still deferred.
- `v0.3` is not started in Day47.
- Recommended next step after Day47 is either:
  - Day48 - Demo Asset Packaging / Offline Interview Demo Kit
  - Day48 - Dashboard Demo Polish and Local Launch Guide

## Validation Commands and Results

Day47 start-state commands:

```powershell
git status --short --branch
git pull origin main
git log --oneline -1
git switch -c day47-interview-demo-baseline-runbook
```

Observed start-state result:

```text
main was clean and already up to date with origin/main.
Latest main commit: e07a747 Merge pull request #33 from Robinlee0929/day46-v021-rc-decision-release-strategy
Created branch: day47-interview-demo-baseline-runbook
```

Day47 local validation command:

```powershell
python -m pytest
```

Result:

```text
487 passed, 1 warning in 2.69s
```

The warning is the existing non-live `getpass` terminal echo warning seen in recent full-suite runs. It does not indicate a live device connection or a failed test.

Optional safe local demo commands:

```powershell
python network_lab.py --task report-index --dry-run
python network_lab.py --list-tasks
python dashboard_app.py
```

These optional demo commands are local-only from the Day47 perspective. They should not be replaced by live VRRP, live WireGuard, SSH, iperf3, or device configuration workflows during the interview baseline demo.

## Safety Confirmation

Day47 is documentation/report-only/local-validation work.

Day47 does not create or push a tag, create `v0.2.1`, create a GitHub release, start `v0.3`, run live network tests, use SSH, connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard, or iperf3 endpoints, create or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, route, interface, or device configuration.
