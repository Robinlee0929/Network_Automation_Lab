# Phase 2N-01 — Canonical Quick Start and Demo Runbook

Status: DONE / MERGED_TO_MAIN

Decision summary: Phase 2N-01 implementation commit `7be97b1f351dc139b06c7ea77c07930d0dcee6d3` was integrated into `main` by fast-forward only, with no merge commit and no conflict. Fresh post-merge validation passed full pytest with 1,866 tests and one existing warning; report-index exited 0 with only 13 optional reports missing and zero failures. The canonical reviewer entry point remains the Flask dashboard started with `python dashboard_app.py`. A bounded Phase 2N-01 check started that command with the already-available environment, verified the task-relevant local GET routes, and proved clean shutdown. The canonical path nevertheless remains `PARTIAL` for user-facing acceptance because the evidence does not establish a reproducible browser lifecycle or a general clean-environment prerequisite/startup contract. The Next.js app remains a secondary committed-evidence browser; its Reports navigation still returns 404. Therefore user-facing acceptance remains `NOT_READY`, Phase 2N implementation remains unauthorized, Phase 2N-03 remains only `CANDIDATE / NOT_AUTHORIZED / NOT_STARTED`, and no follow-on task has started.

```text
PHASE_2N_01_STATUS: DONE / MERGED_TO_MAIN
IMPLEMENTATION_COMMIT: 7be97b1f351dc139b06c7ea77c07930d0dcee6d3
INTEGRATION_TYPE: FAST_FORWARD_ONLY
MERGE_COMMIT: NONE
CONFLICTS: NONE
POST_MERGE_FULL_PYTEST: PASS / 1866 PASSED / 1 EXISTING WARNING
POST_MERGE_REPORT_INDEX: WARN_ACCEPTED / EXIT_0 / FAIL_0 / OPTIONAL_MISSING_13
USER_FACING_ACCEPTANCE_READINESS: NOT_READY
CANONICAL_STARTUP_PATH_STATUS: PARTIAL
SECONDARY_STARTUP_PATH_STATUS: PARTIAL
NEXTJS_REPORTS_404_RESOLVED: NO
PHASE_2N_IMPLEMENTATION_AUTHORIZED: NO
PHASE_2N_03_STATUS: CANDIDATE / NOT_AUTHORIZED / NOT_STARTED
PHASE_2N_02_THROUGH_2N_05_STARTED: NO
```

## A. Authority and scope

Phase 2N-01 is documentation-only. It may classify existing repository evidence and record bounded localhost verification, but it does not change application behavior. Phase 2N implementation remains unauthorized, and this task does not fix either Phase 2N-00 blocker. Candidate follow-on tasks remain `NOT_AUTHORIZED / NOT_STARTED`.

Runtime verification is optional and bounded to already-available dependencies, task-relevant localhost GET routes, and clean shutdown. Dependency installation, environment repair, source changes, route fixes, provider/API/model calls, secrets, live devices, SSH, NETCONF, RESTCONF, configuration backup/change, queues, schedulers, workers, AI agent loops, and production execution are forbidden.

Documentation and local display behavior do not grant live automation authority. The Demo boundary remains local, report-only, dry-run-only, mock-only, and reviewer-visible.

## B. Canonical startup decision

```text
CANONICAL_STARTUP_PATH: python dashboard_app.py

CANONICAL_STARTUP_PATH_STATUS:
PARTIAL

SECONDARY_STARTUP_PATH: npm.cmd run dev -- --hostname 127.0.0.1

SECONDARY_STARTUP_PATH_STATUS:
PARTIAL
```

The Flask command is canonical because README's Fastest Hands-on Path leads with it and its landing, Reports, detail, safety, and missing-artifact routes form the repository's reviewer-oriented Demo surface. Source and automated tests support those routes. In Phase 2N-01, the existing Python/Flask environment started the exact command on `127.0.0.1:5000`; `/`, `/reports`, `/reports/open/day6_lab_topology_summary.html`, `/ai-checklist`, `/ai-intent-reviewer`, and `/commands` returned 200, while an absent report detail returned 404. `Ctrl+C` stopped the exact server session and a follow-up probe confirmed localhost no longer responded.

The status remains `PARTIAL`, rather than redefining the Phase 2N-00 blocker as fixed, because this task did not install or repair an environment, did not perform an interactive browser lifecycle, and did not establish cross-environment reproducibility. Phase 2N-00's earlier unavailable-runtime result remains valid historical evidence for that environment.

Next.js is secondary because the canonical README path is Flask and because the Next.js surface includes provider-backed controls outside the safe Demo. Phase 2N-00 directly verified the secondary server, landing, `/network/day-results`, evidence selection, Jobs empty state, and clean shutdown with existing dependencies. The visible Reports link targets `/network/reports`, which returned 404. Phase 2N-01 did not rerun Next.js or repair that defect.

## C. Prerequisite matrix

| Requirement | Exact requirement | How to verify | Required for Flask | Required for Next.js | Current verification |
| ----------- | ----------------- | ------------- | ------------------ | -------------------- | -------------------- |
| Working directory | Repository root containing `dashboard_app.py`, `package.json`, `reports/`, and `summary/` | Confirm those committed paths are visible before startup | Yes | Yes | Repository evidence verified |
| Python command | A usable `python` command | `python --version` | Yes | No | Directly available in 2N-01; Python 3.13.7 is current-task evidence, not a universal requirement |
| Flask package | Installed package satisfying committed requirement `flask>=3.0.0,<4.0.0` | `python -c "import importlib.metadata as m; print(m.version('flask'))"` | Yes | No | Directly available as Flask 3.1.3 in 2N-01 |
| Node and npm commands | Usable `node` and `npm.cmd` commands | `node --version` and `npm.cmd --version` | No | Yes | Directly available as Node v22.20.0 and npm 11.17.0; these are observed versions, not universal requirements |
| Existing Node dependency tree | Existing local `node_modules` matching the committed package metadata | Confirm `node_modules` exists; do not install or repair it in this task | No | Yes | Directly present in 2N-01; Phase 2N-00 used it successfully |
| Local evidence | Committed or local JSON/TXT/HTML evidence under the repository's supported `reports/` and `summary/` paths | Inspect the repository paths before the Demo | Yes | Yes | Committed evidence is present; availability varies by artifact |

No browser, operating-system, Python, Node, npm, or package-manager version is declared as a universal prerequisite. If a required command or package is missing, stop: installation and environment repair are outside Phase 2N-01.

## D. Exact startup and shutdown instructions

### Canonical Flask reviewer dashboard

| Step | Command or action | Expected result | URL | Shutdown method | Verification status |
| ---- | ----------------- | --------------- | --- | --------------- | ------------------- |
| 1 | From the repository root, run `python --version` and the Flask import/version check in the prerequisite matrix | Both commands succeed; otherwise stop because installation or repair would be required and is forbidden in this task | N/A | N/A | Directly verified in 2N-01 with existing dependencies |
| 2 | Run `python dashboard_app.py` | Flask development server remains running and reports binding to `127.0.0.1:5000`; an import error or unsuccessful exit is a known failure state | `http://127.0.0.1:5000/` | `Ctrl+C` in the server terminal | Directly verified in 2N-01 |
| 3 | Open the landing page | `Network Automation Lab - Portfolio Demo` and Demo status are visible | `http://127.0.0.1:5000/` | Keep the same server running | HTTP status and page identity directly verified; interactive browser presentation remains evidence-only |
| 4 | Open Reports, then select an available detail | Reports index is visible; the committed Day6 HTML detail opens when present | `http://127.0.0.1:5000/reports` and `/reports/open/day6_lab_topology_summary.html` | Keep the same server running | Directly verified in 2N-01 |
| 5 | Review safety pages and Commands as display-only | AI Checklist, AI Intent Reviewer, and Commands pages load; do not submit an action | `/ai-checklist`, `/ai-intent-reviewer`, `/commands` | Keep the same server running | Directly verified as GET routes in 2N-01 |
| 6 | Request an absent report detail | A missing detail returns 404 rather than exposing another path | `/reports/open/does-not-exist.html` | Keep the same server running | Directly verified in 2N-01; richer empty-state behavior is also test-backed |
| 7 | Press `Ctrl+C`, then confirm the landing URL no longer responds | The exact temporary process exits and localhost is closed | `http://127.0.0.1:5000/` | `Ctrl+C` | Directly verified in 2N-01 |

### Secondary Next.js evidence browser

| Step | Command or action | Expected result | URL | Shutdown method | Verification status |
| ---- | ----------------- | --------------- | --- | --------------- | ------------------- |
| 1 | From the repository root, verify `node`, `npm.cmd`, and the existing `node_modules` tree | Commands and the existing dependency tree are available; otherwise stop because installation is forbidden | N/A | N/A | Availability directly verified in 2N-01 |
| 2 | Run `npm.cmd run dev -- --hostname 127.0.0.1` | Next.js development server starts on localhost; an unsuccessful exit is a known failure state | `http://127.0.0.1:3000/` | `Ctrl+C`; confirm localhost closes | Directly verified in Phase 2N-00; not rerun in 2N-01 |
| 3 | Open the evidence browser directly | `Automation Evidence` and committed/local evidence items are visible when data exists | `http://127.0.0.1:3000/network/day-results` | Keep the same server running | Directly verified in Phase 2N-00; source evidence reconfirmed in 2N-01 |
| 4 | Select an evidence item | Selected detail, status, boundary, and raw JSON update | Same URL | Keep the same server running | Directly verified with Day159 in Phase 2N-00 |
| 5 | Do not use Reports navigation as a successful Demo step | The current `/network/reports` target returns 404 | `http://127.0.0.1:3000/network/reports` | Keep the same server running | 404 directly verified in Phase 2N-00 and supported by current route inventory |
| 6 | Press `Ctrl+C` and confirm localhost closes | The temporary server stops | `http://127.0.0.1:3000/` | `Ctrl+C`; if a child process remains, stop only the recorded task process | Clean shutdown directly verified in Phase 2N-00 |

## E. Primary Demo runbook

1. From the repository root, confirm the expected branch/worktree and verify the existing Python and Flask prerequisites without installing anything.
2. Read `AGENTS.md` and state that the Demo is local, report-only, dry-run-only, mock-only, and grants no live automation authority.
3. Run `python dashboard_app.py`. If startup fails, disclose the failure and stop; do not install or repair dependencies.
4. Open `http://127.0.0.1:5000/` and identify the portfolio landing and Demo status.
5. Open `/reports` and explain that it browses local evidence without running router, switch, VPN, or performance workflows.
6. Open one available report detail, such as `/reports/open/day6_lab_topology_summary.html` when that committed file is present, and identify its status and evidence purpose.
7. Open `/ai-checklist` or `/ai-intent-reviewer` and explain that intent, approval, audit, and runtime-gate artifacts are mock-only, dry-run-only, review-only, or report-only. Treat `/commands` as display-only and submit no action.
8. Demonstrate a negative state with an absent report detail returning 404, or explain the Reports empty/missing-artifact message when the relevant optional data is absent.
9. Disclose both known limitations: Phase 2N has no accepted reproducible browser lifecycle, and the secondary Next.js Reports navigation returns 404.
10. Stop the Flask server with `Ctrl+C` and confirm `http://127.0.0.1:5000/` no longer responds.
11. Confirm that the Demo used no live device, SSH, NETCONF, RESTCONF, provider/API/model call, secret, credential, configuration backup, or configuration change.

## F. Secondary fallback Demo

The Next.js path is a secondary fallback for browsing committed/local evidence. With the already-installed dependency tree, Phase 2N-00 demonstrated its landing page, `/network/day-results`, evidence selection, Jobs empty state, and initial action catalog. It can show evidence type, source day, status, report-only boundary, and raw JSON.

It cannot demonstrate a working Reports page: the visible Reports navigation points to `/network/reports`, which returns 404. The verified safe workaround is to open `/network/day-results` directly and use the Evidence list/detail there. This workaround does not repair or resolve the navigation defect and does not make Next.js the canonical platform.

The fallback Demo must exclude `AI Analyze`, parsing, job creation, legacy AI pages, and any other provider-backed or action-submitting control. Those paths may require API keys, model calls, external services, or state changes and are outside the safe Demo. The Evidence page imports local `reports/` and `summary/` JSON/TXT files, so the bounded evidence list/detail can be demonstrated with local committed/sample evidence and without a provider, secret, live device, or external service.

## G. Success and failure criteria

### Observable success

| Area | Success criterion |
| --- | --- |
| Flask startup | `python dashboard_app.py` stays running and binds to `127.0.0.1:5000` |
| Next.js startup | The exact secondary command reaches the localhost ready state using the existing dependency tree |
| Landing access | Flask `/` returns 200 and shows `Network Automation Lab - Portfolio Demo`; the secondary landing/evidence route shows `Network Automation AI Node` / `Automation Evidence` |
| Evidence browsing | `/reports` or `/network/day-results` renders available local evidence or an explicit empty state |
| Detail access | A selected safe report/evidence detail opens and identifies source/status/boundary |
| Missing artifact | Missing content produces an understandable empty/404 state and does not expose an unsafe path or crash the server |
| Safety disclosure | Presenter states report-only/mock-only/no-live boundaries and submits no action |
| Shutdown | The exact temporary process exits and its localhost URL no longer responds |

### Observable failure

- The required runtime or package is unavailable.
- Startup exits unsuccessfully or does not bind to the documented localhost address.
- A documented route returns 404, or the visible page differs materially from this runbook.
- Sample/report evidence is unavailable without an understandable empty state.
- A page requires a secret, provider, model, external service, live device, or dependency installation.
- The documented and actual routes disagree, including the known Next.js `/network/reports` 404.
- A temporary process cannot be stopped cleanly.

Any failure must be recorded. Do not repair it under Phase 2N-01.

## H. Known limitations

- The canonical Flask command succeeded in one bounded Phase 2N-01 environment, but the accepted cross-environment prerequisite and interactive browser lifecycle remain only partially verified.
- The Next.js Reports navigation still returns 404.
- Successful Next.js startup does not make it the canonical platform.
- Mock/sample/report-only display is not live automation.
- Documentation does not resolve an implementation or navigation defect.
- Historical pytest, Vitest, typecheck, lint, build, and Safe CI success does not prove the current user-facing startup path.
- Phase 2N-01 installed no dependency and repaired no environment.
- The Flask Reports empty-state template contains a historical command spelling that differs from the current repository `--task report-index` guidance; this runbook does not modify the template.

## I. User-facing acceptance effect

```text
USER_FACING_ACCEPTANCE_READINESS:
NOT_READY

ACCEPTANCE_BLOCKERS_RESOLVED_BY_2N_01:
NO

CANONICAL_STARTUP_PATH_VERIFIED:
PARTIAL

PRIMARY_DEMO_FLOW_AVAILABLE:
PARTIAL

PHASE_2N_IMPLEMENTATION_AUTHORIZED:
NO
```

- `NOT_READY`: the secondary Reports defect remains and no accepted reproducible browser lifecycle exists.
- `NO`: this documentation task repaired neither the earlier environment/reproducibility gap nor the Next.js route/navigation defect.
- Canonical startup is `PARTIAL`: the exact command and task-relevant HTTP routes were directly verified in this environment, but a cross-environment prerequisite baseline and interactive browser flow were not.
- The primary Demo is `PARTIAL`: its sequence is evidence-backed and the Flask GET flow ran, but final acceptance requires separately authorized lifecycle evidence and blocker disposition.
- Phase 2N implementation remains unauthorized; documentation and verification do not grant implementation authority.

## J. Candidate follow-on recommendation

```text
RECOMMENDED_NEXT_CANDIDATE: Phase 2N-03 — Next.js Reports Navigation Repair
RECOMMENDED_NEXT_CANDIDATE_STATUS: CANDIDATE / NOT_AUTHORIZED / NOT_STARTED
```

Phase 2N-03 is the smallest evidence-supported follow-on because `/network/reports` remains a user-visible 404. A future separately authorized task may correct or remove only that broken navigation contract with bounded tests. Phase 2N-01 does not authorize it, create its branch or document, change source, or start Phase 2N-02, 2N-03, 2N-04, or 2N-05.

## K. Evidence classification

| Finding | Evidence source | Directly verified in 2N-01 | Historical evidence only | Result |
| ------- | --------------- | -------------------------- | ------------------------ | ------ |
| Flask startup command | README, `dashboard_app.py`, current localhost run | Yes | Phase 2N-00 recorded an unavailable runtime | Command succeeded in this environment; overall acceptance status remains PARTIAL |
| Flask landing route | Flask source/template/tests and current GET | Yes | Safe CI test evidence | 200 with expected page identity |
| Flask Reports route | Flask source/template/tests and current GET | Yes | Safe CI test evidence | 200 with Reports heading |
| Flask report detail | Flask safe-path routes/tests and committed Day6 HTML | Yes | Safe CI test evidence | Existing detail returned 200; absent detail returned 404 |
| Next.js startup command | `package.json` and Phase 2N-00 server log | No | Yes | Secondary startup previously succeeded with existing dependencies |
| Next.js landing route | Next.js page source and Phase 2N-00 browser evidence | No | Yes | Previously rendered successfully |
| Next.js Reports navigation | `NetworkNav.tsx`, route inventory, Phase 2N-00 browser/server evidence | No | Yes | `/network/reports` remains 404 |
| Evidence/detail route | `/network/day-results` source/components and Phase 2N-00 interaction | No | Yes | Verified safe fallback for local evidence browsing |
| Missing-artifact behavior | Flask templates/tests, Next.js empty-state component, current absent-detail GET | Yes for Flask 404 | Historical/source/test evidence for richer empty states | Evidence-backed negative states; availability depends on local artifacts |
| Shutdown method | Current Flask session and Phase 2N-00 Next.js lifecycle | Yes for Flask | Yes for Next.js | `Ctrl+C` plus failed post-stop localhost probe |
| Safety boundary | `AGENTS.md`, README, templates/tests, Phase 2N records | Yes as governing documentation | Yes | Report-only/dry-run/mock-only; no live authority |

## Validation and readability record

This document records direct Phase 2N-01 runtime facts separately from Phase 2N-00 and Phase 2M historical evidence. It starts with the conclusion, separates allowed and forbidden scope, uses consistent statuses, gives observable criteria, and preserves the repository glossary and safety boundary. No application behavior, dependency, test, configuration, workflow, generated report, screenshot, Day1-Day160 artifact, or second safety matrix is changed.
