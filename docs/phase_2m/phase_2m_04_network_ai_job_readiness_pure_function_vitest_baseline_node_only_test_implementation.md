# Phase 2M-04 — Network AI Job-readiness Pure-function Vitest Baseline / Node-only Test Implementation

Status: DONE / READY_FOR_REVIEW

Conclusion: Phase 2M-04 completes the one authorized Node-only Vitest slice for `evaluateJobCreateReadiness`. The implementation adds 9 deterministic public-behavior tests in exactly one new TypeScript test module, uses only synthetic in-memory inputs, and leaves production source, dependencies, lockfiles, configuration, servers, browsers, workflows, provider/device access, and execution paths unchanged. All required feature-branch validation passes; report-index returns only the documented optional-local-report WARN.

```text
PHASE: 2M-04
TASK_MODE: IMPLEMENTATION_ONLY
SAFETY_MODE: LOCAL_ONLY / NODE_ONLY / TEST_ONLY / DETERMINISTIC / NON_EXECUTING
STATUS: DONE / READY_FOR_REVIEW
SOURCE_BRANCH: codex/phase-2m-04-network-ai-job-readiness-vitest-baseline
PRODUCTION_SOURCE_MODIFIED: NO
DEPENDENCIES_MODIFIED: NO
CONFIGURATION_MODIFIED: NO
NEXT_PHASE_STARTED: NO
```

## Purpose and implementation boundary

Phase 2M-03 authorized one future native behavior-test slice for `evaluateJobCreateReadiness` in the existing `lib/network-ai/readiness.ts`. This task implements only that slice.

Allowed:

- create `lib/network-ai/readiness.test.ts`;
- directly import and test only `evaluateJobCreateReadiness`;
- use the existing Vitest 4.1.10 default Node environment;
- use synthetic in-memory inventory objects;
- update README and this evidence document for reviewer visibility;
- run the required local validation and Git diff review.

Forbidden and untouched:

- production `.ts` or `.tsx` changes, including `lib/network-ai/readiness.ts`;
- dependency, package, lockfile, TypeScript, ESLint, or Vitest configuration changes;
- React/DOM, jsdom, Playwright, browser, server, GitHub Actions, or workflow work;
- a second TypeScript module test or any other exported-function test;
- filesystem stores, routes, providers, APIs, models, secrets, devices, runners, or adapters;
- SSH, NETCONF, RESTCONF, live devices, real inventory, backup execution, or configuration execution;
- queue, scheduler, broker, worker, AI loop, production execution, Day1-Day160 rewrite, or a second safety matrix;
- Phase 2M-05 or any additional slice.

## Behavior coverage

The new test module contains 9 test cases:

1. Unknown action ID is blocked with `Unknown actionId` and requires approval.
2. Undefined target device is blocked with `Missing targetDevice` and normalized to `null`.
3. Null target device is blocked with `Missing targetDevice` and normalized to `null`.
4. Whitespace-only target device is blocked with `Missing targetDevice` and normalized to `null`.
5. A target not proven ready by synthetic inventory is blocked with the existing device-readiness reason.
6. `backup_config` for a ready synthetic device remains pending approval with the existing backup reason.
7. `change_access_vlan` for a ready synthetic device remains pending approval with the existing configuration-change reason.
8. `update_description` for a ready synthetic device remains pending approval with the existing configuration-change reason.
9. `baseline_check` for a ready synthetic device is ready without approval and returns the trimmed target device.

No test depends on execution order, snapshots, timers, filesystem I/O, network I/O, providers, devices, routes, stores, servers, browsers, runners, or adapters.

## Feature-branch validation

The existing local dependency tree was used. No package was installed, removed, updated, audited, or queried.

| Exact command | Result | Exit code |
| --- | --- | ---: |
| `npm.cmd run test:unit -- lib/network-ai/readiness.test.ts` | PASS; 1 file, 9 tests; Node environment, 0 ms setup | 0 |
| `npm.cmd run test:unit` | PASS; 2 files, 56 tests | 0 |
| `npm.cmd run typecheck` | PASS; no diagnostics | 0 |
| `npm.cmd run lint` | PASS; zero errors and zero warnings | 0 |
| `$env:NEXT_TELEMETRY_DISABLED = '1'` then `npm.cmd run build` | PASS; compiled successfully; 24/24 static pages generated | 0 |
| `python -m pytest` | Environment retry required because `python` was initially absent from the restricted shell PATH; no tests ran and no repository/environment change occurred | 1 |
| `python -m pytest` with the existing local Python exposed only to the validation process PATH | PASS; Python 3.13.7, pytest 8.4.2; 1,866 passed, 0 failed, 1 existing `GetPassWarning` | 0 |
| `python network_lab.py --task report-index` with the same process-local PATH exposure | WARN accepted; total 14, pass 1, fail 0, optional missing 13 | 0 |
| `git diff --check` | PASS | 0 |
| `git diff --name-status` | PASS; tracked diff contained no unauthorized file at the initial test-only checkpoint | 0 |
| `git status --short --branch` | PASS; only the new readiness test was present at the initial checkpoint | 0 |

The report-index WARN is accepted because all 13 missing artifacts are explicitly marked optional local runtime reports, the command exits 0, and the fail count is 0.

## Diff and safety review

- Production source remains byte-for-byte unchanged from the Phase 2M-03 baseline.
- `package.json`, `package-lock.json`, `tsconfig.json`, and `eslint.config.mjs` remain unchanged.
- The implementation diff is limited to `lib/network-ai/readiness.test.ts`, README, and this Phase 2M-04 document.
- Tests directly exercise public return values with synthetic objects and create no I/O or external side effects.
- README and this document both record `DONE / READY_FOR_REVIEW` for the feature-branch state.
- React/DOM, Playwright, GitHub Actions, a second module, and real-device work remain unauthorized.
- Phase 2M-05 is not authorized and has not started.

## Documentation readability review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT_AND_NOT_WEAKENED: PASS
README_AND_PHASE_STATUS_CONSISTENT: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT: PASS
TERMINOLOGY_CONSISTENT_WITH_PHASE_2M_AND_AGENTS_MD: PASS
FINAL_READABILITY_RESULT: PASS
```
