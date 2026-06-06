# Day43 - v0.2 Release Verification and Interview Demo Baseline

## Purpose

Day43 verifies the checked-out `v0.2` release tag as an interview/demo baseline.

This is verification and documentation only. Day43 does not add product features, runner tasks, dashboard behavior, live workflows, generated evidence fixtures, or device configuration changes.

## Verification Summary

| Item | Result |
| --- | --- |
| Overall result | FAIL |
| `v0.2` tag checkout | PASS |
| Tests from `v0.2` | FAIL |
| Dashboard demo readiness | PASS |
| Reports index readiness | WARN |
| Demo flow readiness | PASS |
| Interview demo baseline | READY WITH NOTES |
| Safety result | PASS |

Day43 confirms that the `v0.2` tag can be checked out and the local dashboard/demo-flow surfaces are usable for a repository-only interview walkthrough. It does not confirm a fully green release verification run from a fresh tag checkout because the Python regression suite has one failing test and the report index is incomplete when ignored report artifacts are absent.

## Source Tag

| Field | Value |
| --- | --- |
| Verification date | 2026-06-06 |
| Source tag | `v0.2` |
| Annotated tag object | `c5d9a5a85ae826fe168bd4381482d59c065994f8` |
| Tagged commit | `f4fd4d5a33d6847d40baac87ae4ed285e56dea6a` |
| Tagged commit subject | `Prepare Day42 v0.2 release tag documentation` |
| Temporary worktree | `.tmp/day43_v0_2_verify` |

## Commands Executed

All commands were local, offline, report-only, read-only, or documentation-oriented.

```powershell
git status --short --branch
git tag --list
git show --no-patch --oneline v0.2
git switch -c day43-v0.2-release-verification-demo-baseline
New-Item -ItemType Directory -Force .tmp
git worktree add .tmp/day43_v0_2_verify v0.2
pytest
python network_lab.py --task report-index
python network_lab.py --task demo-flow
python -c "from dashboard_app import app; client=app.test_client(); paths=['/','/reports']; [print(path, client.get(path).status_code) for path in paths]"
python -c "from dashboard_app import create_app; app=create_app(); client=app.test_client(); paths=['/','/reports']; [print(path, client.get(path).status_code) for path in paths]"
git cat-file -p v0.2
git rev-parse HEAD
git log --oneline -3
git status --short
git ls-files reports
git worktree add .tmp/day43_v0_2_failure_probe v0.2
python -m pytest tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode -q
Test-Path -LiteralPath config.json
Test-Path -LiteralPath golden_day2_config.json
Test-Path -LiteralPath Set_WireguardVPN_config.json
rg -n "def load_default_router_config|def load_day12_config|config\.json|router_host|router_username|Missing required non-interactive" mikrotik_day12_wireguard_vpn_automation.py tests\test_day12_wireguard_vpn_automation.py .gitignore
```

## Results

### Branch and Working Tree

Initial branch state:

```text
## main...origin/main
```

No modified or staged files were reported before Day43 edits. The Day43 documentation branch was created:

```text
day43-v0.2-release-verification-demo-baseline
```

After the temporary worktree was created, the main worktree showed `.tmp/` as untracked. That directory is temporary verification state and is not part of the Day43 documentation deliverable.

### Tag Checkout

`v0.2` exists locally and was checked out through a temporary detached-head worktree:

```text
HEAD is now at f4fd4d5 Prepare Day42 v0.2 release tag documentation
Preparing worktree (detached HEAD f4fd4d5)
```

Result: PASS.

### Python Tests

Command:

```powershell
pytest
```

Result:

```text
1 failed, 485 passed, 2 warnings in 3.52s
```

Failing test:

```text
tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode
```

Observed failure:

```text
ValueError: Missing required non-interactive values: --router-host, --router-username
```

Classification: FAIL.

Reason: a fresh `v0.2` checkout does not include ignored local configuration such as `config.json`. The failing test calls the Day12 config builder in non-interactive mode with only `--device-name`, so the builder rejects the missing router host and username. This is a release verification issue in the tag checkout, not a live-device failure.

### Python Test Failure Investigation

The single failing test was recreated from a fresh temporary `v0.2` worktree:

```powershell
git worktree add .tmp/day43_v0_2_failure_probe v0.2
python -m pytest tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode -q
```

Failing test name:

```text
tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode
```

Captured failure message:

```text
ValueError: Missing required non-interactive values: --router-host, --router-username
```

Relevant v0.2 behavior:

- `load_default_router_config()` reads `config.json` from the current working directory.
- `config.json` is intentionally ignored by `.gitignore`.
- The failing test passes `--device-name` and `--non-interactive`, but it does not pass `--router-host`, does not pass `--router-username`, does not pass `--config`, and does not monkeypatch the config loader.
- In a fresh `v0.2` worktree, `config.json`, `golden_day2_config.json`, and `Set_WireguardVPN_config.json` were all absent.
- In the Day43 working tree, `config.json` and `Set_WireguardVPN_config.json` existed as ignored local files, and the same single test passed.

Root cause classification:

| Possible cause | Applies? | Notes |
| --- | --- | --- |
| Missing generated reports | No | The failing test is a Day12 config-builder unit test and does not read `reports/`. |
| Ignored reports path | No | `reports/` absence explains report-index WARN, not this pytest failure. |
| Worktree path assumptions | No | The failure is not caused by path layout; it is caused by absent local config values. |
| Stale v0.2 test expectation | Yes | The v0.2 test assumes host and username are available from local environment/config instead of making the test self-contained. |
| Environment difference | Yes | The Day43 branch had ignored local `config.json`; the fresh `v0.2` worktree did not. |
| Real release defect | Partial | This is a real release verification/test hermeticity defect, but not a live-device or interview-demo runtime defect. |

Recommended action: fix on `main` in a later non-live test-only change by making the test self-contained. The lowest-risk fix is to provide `--router-host` and `--router-username` in the test or monkeypatch `load_default_router_config()` so the expected `recreate_peer` default is tested without depending on ignored local files.

`v0.2.1` recommendation: not required for the interview demo baseline. Create `v0.2.1` only if the release policy requires an immutable tag with a fully green fresh-checkout pytest result.

### Dashboard Readiness

Initial smoke command attempted to import a module-level `app` object:

```powershell
python -c "from dashboard_app import app; client=app.test_client(); paths=['/','/reports']; [print(path, client.get(path).status_code) for path in paths]"
```

Result:

```text
ImportError: cannot import name 'app' from 'dashboard_app'
```

The v0.2 dashboard uses the existing `create_app()` factory. Corrected local Flask test-client smoke command:

```powershell
python -c "from dashboard_app import create_app; app=create_app(); client=app.test_client(); paths=['/','/reports']; [print(path, client.get(path).status_code) for path in paths]"
```

Result:

```text
/ 200
/reports 200
```

Classification: PASS.

Dashboard readiness: the home page and reports page are testable locally without starting a long-running server and without connecting to devices.

### Reports Index Readiness

Command:

```powershell
python network_lab.py --task report-index
```

Result:

```text
Overall result: [INCOMPLETE]
Counts: total=12 pass=0 fail=0 warn=0 missing=12 unknown=0
JSON overview: reports/lab-summary/latest_lab_overview.json
HTML overview: reports/lab-summary/latest_lab_overview.html
```

Classification: WARN.

Reason: the command runs locally and writes the expected latest overview paths, but the fresh tag checkout has no committed `reports/` evidence. `reports/` is ignored by `.gitignore`, and `git ls-files reports` returned no tracked report files. The index therefore reports missing evidence, including required Day4 baseline reports.

This is explainable for an interview demo if the presenter states that live/generated evidence is intentionally ignored and must be regenerated or supplied from the local lab evidence archive. It is not a clean all-green release verification result.

### Demo Flow Readiness

Command:

```powershell
python network_lab.py --task demo-flow
```

Result:

```text
Day24 RC Demo Flow
Result: READY
Walkthrough steps: 6
JSON demo flow: reports/portfolio/day24_rc_demo_flow.json
HTML demo flow: reports/portfolio/day24_rc_demo_flow.html
[PASS] Day24 demo flow completed without live execution.
```

Classification: PASS.

Demo-flow readiness: the existing report-only demo flow runs successfully from the `v0.2` checkout.

## Generated Reports

The verification commands generated report-only files under ignored `reports/` paths in the temporary worktree:

- `reports/lab-summary/latest_lab_overview.json`
- `reports/lab-summary/latest_lab_overview.html`
- `reports/portfolio/day24_rc_demo_flow.json`
- `reports/portfolio/day24_rc_demo_flow.html`

These generated files are not committed. `reports/` is ignored by `.gitignore`, and `git ls-files reports` returned no tracked report files in the `v0.2` checkout.

## Known Limitations

- The `v0.2` fresh checkout does not produce a fully green test suite in this environment.
- The failing test depends on router host and username values that are not present in a fresh checkout because `config.json` is intentionally ignored.
- The failure is caused by a non-hermetic v0.2 test expectation plus a local environment difference, not by missing generated reports, the ignored `reports/` path, worktree path assumptions, or live-device behavior.
- The report index can be generated, but it reports `INCOMPLETE` without local generated report evidence.
- The dashboard is ready for local route smoke testing, but generated report content depends on ignored local report artifacts.
- Day43 did not regenerate live evidence and did not run any live network or device command.

## Interview Demo Baseline Recommendation

Recommendation: READY WITH NOTES.

Use `v0.2` for an interview demo only as a repository-only, safety-first walkthrough:

- Open README and v0.2 release docs.
- Show the HA / VRRP topology and safety model.
- Show the dashboard `/` and `/reports` route readiness.
- Run or show `python network_lab.py --task demo-flow`.
- Explain that live/generated report artifacts are intentionally ignored and may be absent from a fresh checkout.
- Do not claim that the fresh `v0.2` tag has a fully passing regression suite until the Day12 non-interactive config test is made self-contained in a later change.
- Do not create `v0.2.1` solely for the interview demo unless the release standard requires a fresh-checkout all-green test tag.

## Safety Confirmation

Safety result: PASS.

Day43 did not run live network tests, did not use SSH, did not connect to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peer, or iperf3 endpoint, and did not change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.

Only local Git inspection, temporary checkout, Python tests, Flask test-client smoke checks, report-index generation, demo-flow generation, and documentation edits were performed.
