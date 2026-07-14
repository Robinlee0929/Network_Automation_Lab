# Phase 2N-02 — Canonical Flask Local Demo Smoke-test Baseline

## Conclusion and decision

Phase 2N-02 is `DONE / MERGED_TO_MAIN` with acceptance decision `PASS_WITH_NOTES`.
The canonical Flask entry point was started as an actual local process on fixed endpoint
`127.0.0.1:5000` with the same Python interpreter that ran pytest. The bounded GET-only
reviewer flow passed, synthetic safe report details and negative states passed, the exact
server process exited, no child process existed, and port 5000 was closed and bindable
after cleanup.

The note is environmental: the literal `python` command is not available in this Codex
shell. No dependency or interpreter repair was authorized or attempted. Validation used
the existing repository-capable Python 3.13.7 interpreter at
`C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe`; the automated
lifecycle itself used `sys.executable`, so the spawned server and pytest used that same
interpreter.

User-facing acceptance remains `NOT_READY`, overall Phase 2N remains `IN_PROGRESS`, and
final Phase 2N acceptance or closure is not authorized.

The source commit `5832a2452ca5541ceb94c642256e4f873b84d795`, with direct parent
`83ff84d3a972ce8bdc787e044518126f13ca8d65`, was pushed normally on the source
branch, integrated into `main` by fast-forward only, and pushed normally to the trusted
remote. No merge commit, squash, rebase, cherry-pick, conflict, or force push occurred.

## Authority and scope

- `TASK_MODE: implementation`
- `TASK_SUBTYPE: CANONICAL_FLASK_LOCAL_DEMO_SMOKE_TEST_BASELINE_ONLY`
- `PHASE: 2N-02`
- `PARENT_PHASE: 2N`
- Starting repository: `C:\Dev\Network_Automation_Lab`
- Starting branch: `main`
- Starting commit: `83ff84d3a972ce8bdc787e044518126f13ca8d65`
- Working branch: `codex/phase-2n-02-canonical-flask-local-demo-smoke-baseline`
- Authorized tracked files: this record, `README.md`, and
  `tests/test_phase_2n_02_canonical_flask_demo_smoke.py`

The implementation is test-and-documentation-only. It changes no production Flask source,
existing test, dependency, configuration, workflow, Next.js or TypeScript source, tracked
report, or prior phase record.

## Prerequisite and instruction evidence

The immediately preceding bootstrap in this same Codex task recorded `TASK_RESULT: DONE`,
`PREREQUISITE_GATE_PASSED: YES`, and
`READY_FOR_SAME_TASK_IMPLEMENTATION_CONTINUATION: YES`. It also recorded no deliberate Git
command and no repository state change.

Before deliberate repository action, the requested
`manage-network-lab-codex-tasks` skill was read completely, including:

- `C:\Users\Robin\.codex\skills\manage-network-lab-codex-tasks\SKILL.md`
- `references/required-references.md`
- `references/task-modes.md`
- `references/result-contracts.md`
- `references/single-prompt-self-gated-execution.md`

`C:\Dev\Network_Automation_Lab\AGENTS.md` was found and read completely before any Git
command or state-changing action. No more-specific applicable `AGENTS.md` exists. The
actual-automation reference is not applicable because this task adds no runner, adapter,
live integration, SSH, NETCONF, RESTCONF, device inventory, credential, command allowlist,
or production execution behavior.

The first deliberate Git command was executed exactly and independently as:

```text
git status --short --branch
```

It returned `## main...origin/main`. Preflight then confirmed a clean worktree and index,
local `main`, local `origin/main`, and independently queried trusted remote `main` at the
expected commit, no active Git operation, no existing local or remote target branch, and
the required predecessor phase states. Phase 2N-02 had not started.

## Process lifecycle method

The test first proves port 5000 is not listening and can be bound. It then starts:

```text
sys.executable dashboard_app.py
```

The process uses repository root as its working directory, no stdin, a bounded 20-second
startup timeout, fixed loopback address `127.0.0.1`, and fixed port `5000`. Every HTTP
request is constructed from the hard-coded loopback base URL and uses `urllib.request`
with method `GET`. No alternate port or non-local destination is available in the test.

The passing targeted run recorded server PID `23212`. The test enumerated direct child
processes through the Windows Tool Help process snapshot and found none, consistent with
the production entry point's `debug=False` behavior. Cleanup called `terminate()` only on
the exact `Popen` instance, waited with a five-second bound, retained a kill fallback only
for that exact process, proved the process had exited, proved no children required cleanup,
and proved port 5000 was closed and bindable again. The Windows termination return code was
`1`; the process-exit and port-release assertions passed. No unrelated process was
terminated.

## Reviewer route evidence

| Route | Method | Result |
| --- | --- | --- |
| `/` | GET | HTTP 200; contains `Network Automation Lab - Portfolio Demo` |
| `/reports` | GET | HTTP 200 |
| `/ai-checklist` | GET | HTTP 200 |
| `/ai-intent-reviewer` | GET | HTTP 200 |
| `/commands` | GET | HTTP 200 |

No command-run POST was performed. The Commands page was viewed only through GET. No
provider, API, model, secret, external service, SSH, NETCONF, RESTCONF, or live device was
contacted.

## Deterministic report and negative-state evidence

The second test uses only pytest temporary directories and synthetic, non-sensitive HTML
and JSON. It proves:

- report discovery normalizes the synthetic HTML and JSON evidence to `PASS`;
- a safe HTML detail returns HTTP 200;
- a safe redacted JSON preview returns HTTP 200;
- a missing detail returns controlled HTTP 404;
- direct and percent-encoded `..` traversal attempts return HTTP 404;
- an empty temporary reports directory returns HTTP 200 and visible `MISSING` states;
- no real report fixture is committed and restored ignored reports are not required.

The report-index command did update its normal ignored local overview outputs under
`reports/lab-summary/`; they remained ignored and unstaged. No tracked report changed.

## Validation evidence

The literal command probe `python --version` returned exit code `1` because `python` was
not found. A bundled artifact-runtime Python was also inspected without modification; it
did not contain pytest or Flask and was not used for repository validation. No package was
installed or updated.

| Validation | Exact command | Result |
| --- | --- | --- |
| Targeted Phase 2N-02 | `C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe -m pytest tests/test_phase_2n_02_canonical_flask_demo_smoke.py -s` | Exit 0; 2 passed in 1.87s; PID 23212; all route, cleanup, child, and port proofs passed |
| Existing Flask tests | `C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe -m pytest tests/test_dashboard_app.py` | Exit 0; 41 passed in 1.18s |
| Full pytest | `C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe -m pytest` | Exit 0; 1,868 passed, 1 existing `GetPassWarning`, in 70.52s |
| Report index | `C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe network_lab.py --task report-index` | Exit 0; PASS; total 14, pass 14, fail 0, warn 0, missing 0, unknown 0 |
| Whitespace | `git diff --check` | PASS |

During test development, the same targeted command had three initial one-assertion failures
while the synthetic expectations were aligned to existing report discovery and missing-state
wording. Every failed iteration still proved server cleanup and port closure. The final
targeted run above and the subsequent full suite are the acceptance evidence.

## Post-integration evidence

The integration task independently verified the source branch and commit, its exact three-file
scope, its one-commit direct ancestry from the expected `main`, and trusted remote state. The
source branch was pushed with a normal non-force push. Local `main`, tracking `origin/main`,
and trusted remote `main` were all rechecked at the expected parent before integration. The
source commit was then integrated with `git merge --ff-only` and pushed normally to `main`.

Post-integration validation on local `main` recorded:

| Validation | Result |
| --- | --- |
| Phase 2N-02 targeted test | Exit 0; 2 passed in 2.14s; PID 8684; all five GET routes returned 200; exact process, child, and port cleanup passed |
| Full pytest | Exit 0; 1,868 passed, 1 existing `GetPassWarning`, in 76.93s |
| Report index | Exit 0; PASS; total 14, pass 14, fail 0, warn 0, missing 0, unknown 0 |
| Whitespace and tracked state | `git diff --check` passed; no tracked report or other tracked file changed |

The literal `python` alias remains unavailable in the tested environment. The automated
baseline and integration validation used the explicit existing Python 3.13 interpreter at
`C:\Users\Robin\AppData\Local\Programs\Python\Python313\python.exe`; no dependency or
environment repair was attempted.

## Reproducibility and limitations

`CLEAN_CLONE_REPRODUCIBILITY: TEST_LOGIC_HERMETIC_WITH_EXISTING_DEPENDENCIES`. The test
creates its own report evidence, requires no ignored report restoration, contacts only
loopback, and cleans its process and temporary files. A clean environment must still provide
the committed requirements, and the literal README command `python dashboard_app.py` was
not universally verified in this shell because `python` is not on the effective executable
path. The same-interpreter lifecycle is verified with `sys.executable`.

This baseline is an automated HTTP smoke test, not an interactive browser or visual-layout
acceptance test. It does not exercise the Commands POST action, run a device workflow, prove
external browser behavior, add CI, or authorize a later Phase 2N slice.

## Documentation readability review

The record starts with the decision, states its purpose without hidden context, separates
allowed and forbidden scope, preserves the safety boundary, uses consistent status labels,
lists concrete acceptance evidence, splits lifecycle and validation details into focused
sections, and uses the current Phase 2N terminology. The review introduced no runtime or
execution behavior.

## Final status

- `PHASE_2N_02_ACCEPTANCE_DECISION: PASS_WITH_NOTES`
- `PHASE_2N_02_STATUS: DONE / MERGED_TO_MAIN`
- `USER_FACING_ACCEPTANCE_READINESS: NOT_READY`
- `OVERALL_PHASE_2N_STATUS: IN_PROGRESS`
- `PHASE_2N_FINAL_CLOSURE_AUTHORIZED: NO`
- Source push and fast-forward-only main integration: completed with normal non-force pushes
- Merge commit, squash, rebase, cherry-pick, conflict, force push, and pull request: none
- Phase 2N-04 and Phase 2N-05: unstarted and unauthorized

A separate user-authorized continuation decision is required before any next Phase 2N task.
No Phase 2N-04, Phase 2N-05, final acceptance, or final closure is selected or authorized by
this reconciliation.
