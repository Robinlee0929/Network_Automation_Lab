# Day25 v0.1 RC Validation

## Purpose

This document records the Day25 v0.1 release candidate validation result for Network Automation Lab. It is documentation-only evidence for reviewer and portfolio use.

The RC validation confirms whether the existing runner metadata, safety posture, demo-flow evidence, dashboard/report paths, and regression suite are ready for v0.1 review/demo without adding product behavior.

## Validation Scope

Validation covered:

- Runner task catalog metadata and safety labels.
- Existing Day24 RC demo-flow generation.
- Existing dashboard and report evidence paths.
- Git ignored artifact posture for generated outputs, exports, caches, real configs, and secrets.
- Full local regression suite.

Validation did not add:

- Product features.
- Runner behavior.
- Dashboard behavior.
- Live VPN behavior.
- SSH execution behavior.
- Generated reports, exports, real configs, caches, or secrets.

## Full Pytest Result

Full regression suite command:

```text
python -m pytest --basetemp=.pytest-tmp-day25-rc
```

Result:

```text
401 passed in 1.94s
```

An initial raw pytest run failed because pytest tried to use:

```text
C:\Users\Robin\AppData\Local\Temp
```

The sandbox could not access that temp path. This first failure is treated as an environment temp-path issue, not a product regression.

## Task Catalog Safety Review

Task metadata was reviewed with:

```text
python network_lab.py --list-tasks --verbose
```

Result: task metadata is complete for the RC review scope.

The catalog keeps safety posture explicit across report-only, read-only, guarded-live, dry-run, and disabled task types. WireGuard-related runner behavior remains conservative and does not add live VPN activation, firewall apply behavior, router reset/reboot behavior, or destructive configuration behavior.

## Demo-flow Evidence Review

The Day24 RC demo flow regenerated successfully.

Evidence paths:

```text
reports/portfolio/day24_rc_demo_flow.json
reports/portfolio/day24_rc_demo_flow.html
```

The demo flow remains report-only and provides a safe reviewer walkthrough without starting live device workflows.

## Dashboard / Reports Path Review

The report index ran successfully.

Overall result: WARN.

The WARN status is caused only by optional evidence gaps:

1. Hex-s-2025-lab02 Day8 iperf3 optional report.
2. Day6 lab topology optional summary.

These optional gaps are surfaced clearly rather than hidden. They do not block v0.1 review/demo.

The dashboard/reports review remains read-only evidence browsing. No dashboard behavior was added or changed as part of Day25 validation.

## Git Ignored Artifact Check

Git worktree was clean after validation.

No generated reports, exports, real configs, caches, or secrets are part of this Day25 documentation change.

## Known Limitations

- The initial raw pytest invocation was affected by sandbox access to `C:\Users\Robin\AppData\Local\Temp`; rerunning with `--basetemp=.pytest-tmp-day25-rc` resolved the environment issue.
- Report index remains WARN because two optional evidence files are missing.
- This validation records RC readiness only; it does not replace live lab execution evidence for optional reports that have not yet been generated.

## RC Verdict

PASS WITH NOTES

Reason:

The core runner, task catalog metadata, Day24 demo flow, and full regression suite passed. The remaining WARN items are optional evidence gaps and do not block v0.1 review/demo.

RC is ready for v0.1 review/demo.
