# Phase 2M-05 — Platform Quality Continuation and Closure Authorization Gate / Planning Only

Status: DONE / READY_FOR_REVIEW

Decision summary: the merged Phase 2M evidence meets the current minimum local quality baseline, but Phase 2M should not close while the repository has no reviewer-visible CI baseline for its Python and Node validation stacks. The Gate therefore sets `PHASE_2M_DISPOSITION: CONTINUE_TO_SAFE_CI` and authorizes exactly one separate future task, `Phase 2M-06 — GitHub Actions Dual-Stack Safe CI Baseline`, as `AUTHORIZED / NOT_STARTED`. React/DOM component testing is deferred because no current defect or requirement evidence justifies its additional dependency and configuration surface. Playwright E2E is deferred to Phase 2N, where user-facing acceptance and demo readiness can define the browser, server, artifact, and cleanup boundary. This planning task does not create a workflow, run CI, add tests or dependencies, start 2M-06, start 2M-07, or start Phase 2N.

```text
PHASE: 2M-05
TASK_MODE: PLATFORM_QUALITY_CONTINUATION_AND_CLOSURE_AUTHORIZATION_GATE_PLANNING_ONLY
TASK_MODE_CLASS: planning-only / authorization-gate
SAFETY_MODE: PLANNING_ONLY / DOCUMENTATION_ONLY / LOCAL_ONLY / NON_EXECUTING
STATUS: DONE / READY_FOR_REVIEW
PHASE_2M_MINIMUM_QUALITY_BASELINE: MET
SAFE_CI_NECESSITY: REQUIRED
REACT_DOM_TESTING_DECISION: DEFER
PLAYWRIGHT_E2E_DECISION: DEFER_TO_PHASE_2N
PHASE_2M_DISPOSITION: CONTINUE_TO_SAFE_CI
NEXT_AUTHORIZED_TASK: Phase 2M-06 — GitHub Actions Dual-Stack Safe CI Baseline
NEXT_AUTHORIZED_TASK_MODE: IMPLEMENTATION_ONLY / CI_WORKFLOW_ONLY / DOCUMENTATION_ONLY_SUPPORT / NON_LIVE
NEXT_AUTHORIZED_TASK_STATUS: AUTHORIZED / NOT_STARTED
PHASE_2M_06_STARTED: NO
PHASE_2M_07_STARTED: NO
PHASE_2N_STARTED: NO
```

## Purpose and boundary

This Gate decides whether Phase 2M has enough platform-quality evidence to close, whether a safe GitHub Actions baseline is required first, and whether React/DOM or Playwright testing should be the next work. It is a decision record only.

Allowed in Phase 2M-05:

- inspect merged repository evidence and the current Git state;
- classify the minimum quality baseline;
- decide the Safe CI, React/DOM, and Playwright dispositions;
- define one exact future Safe CI implementation boundary;
- update README and create this Phase 2M-05 record.

Forbidden and untouched:

- `.github/workflows/`, GitHub repository settings, branch protection, deployment, release, or package publishing;
- production TypeScript, JavaScript, or Python source;
- tests, fixtures, dependencies, package metadata, lockfiles, TypeScript, ESLint, or Vitest configuration;
- React Testing Library, jsdom, Playwright, browser binaries, server startup, browser execution, or E2E artifacts;
- live device access, SSH, NETCONF, RESTCONF, provider/API/model calls, secrets, real inventory, runners, adapters, configuration backup, or configuration change;
- queue, scheduler, broker, worker, AI agent loop, production execution, Day1-Day160 rewrite, or a second safety matrix;
- implementation of Phase 2M-06, review/closure work for Phase 2M-07, Phase 2N, push, merge, pull request, or branch cleanup.

## Guidance and evidence reviewed

The repository-root `AGENTS.md`, the requested `manage-network-lab-codex-tasks` skill, and the skill's task-mode and result-contract references were read before repository action. Because the requested evidence review includes workflow and automation boundaries, `docs/automation_readiness/actual_automation_integration_plan.md` was also read. It keeps the repository at Stage 0 mock-only/dry-run and authorizes no real automation.

Repository evidence reviewed for this Gate:

- `README.md`, including the Phase 2M validation notes and progress-table rows;
- Phase 2M-00 through Phase 2M-04 planning, authorization, implementation, acceptance, repair, and reconciliation records under `docs/phase_2m/`;
- merged `main` and `origin/main` at reconciliation commit `1ce03036140b8766c87d7046780e34e90c8911da`;
- Phase 2M-04 implementation commit `e57f06c178f3456e83db73649ea6770388589441`, verified as an ancestor of `main`;
- `package.json`, the root package metadata in `package-lock.json`, `tsconfig.json`, and `eslint.config.mjs`;
- the two existing Node-only Vitest modules, `lib/ai/validators.test.ts` and `lib/network-ai/readiness.test.ts`;
- Python pytest and report-index results recorded in the merged Phase 2M-04 evidence;
- the current `.github/workflows/` inventory, which is absent;
- current React/TSX, DOM-library, Vitest-configuration, and Playwright inventory.

No fetch, pull, push, merge, rebase, registry query, dependency installation, build, server, browser, or live operation was used to reach the Gate decisions.

## Minimum quality baseline decision

```text
PHASE_2M_MINIMUM_QUALITY_BASELINE: MET
```

| Baseline area | Merged evidence | Gate assessment |
| --- | --- | --- |
| Python full pytest | Phase 2M-04 post-merge: 1,866 passed, 0 failed, 1 existing warning | MET |
| TypeScript typecheck | Phase 2M-04 post-merge: PASS, no diagnostics | MET |
| ESLint | Phase 2M-04 post-merge: PASS, zero errors and zero warnings | MET |
| Next.js production build | Phase 2M-04 post-merge: PASS, 24/24 static pages | MET |
| Node-only Vitest | Phase 2M-04 post-merge: 56 passed in two files | MET |
| Native TypeScript regression protection | Validator and job-readiness public behavior have deterministic Node-only tests | MET for the current bounded baseline |
| Report-index visibility | Phase 2M-04 post-merge: exit 0; 13 missing artifacts are documented optional local reports | MET with accepted WARN |
| No-execution safety | Existing tests use synthetic in-memory inputs; source, workflow, provider, device, runner, and adapter paths remained unchanged | MET |

This is an evidence classification, not a fresh validation claim. Phase 2M-05 did not rerun pytest, Vitest, typecheck, lint, build, or report-index because its tracked changes are documentation-only and the authoritative merged Phase 2M-04 record already supplies the required committed baseline.

`MET` does not mean every possible frontend or acceptance test is required or complete. It means the current local baseline is credible enough to proceed to the specifically bounded CI portability step.

## Safe CI decision

```text
GITHUB_ACTIONS_WORKFLOW_FOUND: NO
SAFE_CI_NECESSITY: REQUIRED
```

Safe CI is required before Phase 2M closure because the repository now has two established quality stacks:

- Python pytest and report-index validation; and
- Node typecheck, zero-warning lint, Vitest, and Next.js build validation.

All of these gates are currently reviewer-visible only through local or committed evidence. A minimal GitHub Actions workflow would make pull-request and main-branch regressions visible without adding application behavior, live automation, secrets, browser execution, deployment, or production authority.

This Gate does not create that workflow. It only authorizes a separately requested Phase 2M-06 within the exact boundary below.

## React/DOM testing decision

```text
REACT_DOM_TESTING_DECISION: DEFER
REACT_DOM_TESTING_REASON: NO CURRENT DEFECT OR REQUIREMENT EVIDENCE
```

The repository contains React/TSX components, hooks, form events, and reviewer-facing pages. However, there is no current defect, regression, or acceptance requirement that identifies one component boundary whose value clearly exceeds the dependency and configuration cost. The repository has no React Testing Library or jsdom direct dependency and no DOM-oriented Vitest configuration.

React/DOM testing is therefore deferred, not rejected. A later gate must name the exact component behavior, defect, or acceptance requirement before it may authorize dependencies, configuration, fixtures, or component tests.

## Playwright E2E decision

```text
PLAYWRIGHT_E2E_DECISION: DEFER_TO_PHASE_2N
PLAYWRIGHT_E2E_REASON: USER-FACING ACCEPTANCE AND DEMO READINESS NEED A SEPARATE BROWSER-SERVER LIFECYCLE GATE
```

Reviewer-facing pages and a passing production build make E2E potentially valuable, but they do not define the required browser/server contract. Playwright would add dependency ownership, browser binaries, a Playwright configuration, server lifecycle and ports, fixtures, artifacts, timeout and cleanup rules, and cross-platform reproducibility questions.

Those concerns fit `Phase 2N — User-facing Acceptance and Demo Readiness`. Phase 2N is not started or authorized here. No Playwright package, browser binary, configuration, server, browser, or E2E test is added by Phase 2M-05.

## Phase 2M disposition

```text
PHASE_2M_DISPOSITION: CONTINUE_TO_SAFE_CI
```

Phase 2M should continue through one Safe CI implementation task before a closure review. The Gate authorizes only Phase 2M-06. It does not classify Phase 2M as closed or merged, and it does not treat the future workflow as already implemented.

After Phase 2M-06 is separately implemented, reviewed, merged, and evidenced, a separate review-only closure task may be considered:

```text
Phase 2M-07
Platform Quality and TypeScript Automation Acceptance Review
Review / Closure Only
```

Phase 2M-07 is contingent future work, not authorized or started by this Gate. It must review actual Phase 2M-06 results and cannot rely on this planning decision as proof that CI exists or passes.

## Exact authorized Phase 2M-06 boundary

### Task identity

```text
Phase 2M-06 — GitHub Actions Dual-Stack Safe CI Baseline
TASK_MODE: IMPLEMENTATION_ONLY / CI_WORKFLOW_ONLY / DOCUMENTATION_ONLY_SUPPORT / NON_LIVE
STATUS: AUTHORIZED / NOT_STARTED
```

Phase 2M-06 may begin only as a separate user-requested task from a clean, synchronized `main` after Phase 2M-05 is reviewed and merged.

### Authorized tracked files

Exactly these tracked files may change:

1. `.github/workflows/safe-ci.yml` — new workflow only;
2. `README.md` — bounded Phase 2M-06 status and reviewer guidance only;
3. `docs/phase_2m/phase_2m_06_github_actions_dual_stack_safe_ci_baseline.md` — new implementation/evidence record only.

If implementation requires any other tracked file, Phase 2M-06 must stop with `NEEDS_SCOPE_CONFIRMATION`.

### Workflow trigger and permission boundary

- permit `pull_request` targeting `main`, `push` to `main`, and manual `workflow_dispatch` only;
- do not use `pull_request_target`, `schedule`, repository dispatch, reusable-workflow secrets, deployment, release, or package-publishing triggers;
- set workflow permissions to `contents: read` and do not grant write permissions;
- use no repository secret, environment secret, API key, credential, SSH key, device inventory, or private configuration;
- disable persisted checkout credentials;
- use one GitHub-hosted job with no matrix, service container, self-hosted runner, environment, deployment, or artifact upload;
- pin third-party actions to reviewed immutable commit SHAs rather than floating branches or tags, with the human-readable upstream version noted in comments.

### Runtime and command boundary

The workflow may prepare only the committed Python and Node dependency sets in the ephemeral GitHub-hosted runner. It may not modify package manifests, lockfiles, requirements, or repository source.

Required validation sequence:

```text
checkout with persisted credentials disabled
set up Node 22
npm ci
npm run typecheck
npm run lint
npm run test:unit
NEXT_TELEMETRY_DISABLED=1 npm run build
set up Python 3.13
python -m pip install -r requirements.txt
python -m pytest
python network_lab.py --task report-index
git diff --exit-code
```

Pass conditions:

- every command exits 0;
- lint retains its existing zero-warning policy;
- Vitest remains Node-only and runs the existing complete suite;
- the build starts no development or production server and launches no browser;
- report-index may report only the documented optional-local-report WARN while still exiting 0 with no failed report;
- `git diff --exit-code` proves validation changed no tracked file;
- no step contacts a device, provider, model, private service, deployment target, or repository write API.

The setup and dependency-install steps may use only the public package registries required to materialize the already committed `package-lock.json` and `requirements.txt` dependency sets in the ephemeral runner. They do not authorize dependency-version changes, `npm update`, `npm audit fix`, unpinned ad-hoc packages, browser downloads, or generated evidence commits.

### Explicit exclusions

Phase 2M-06 must not add or change:

- production source, tests, fixtures, package metadata, lockfiles, requirements, TypeScript, ESLint, or Vitest configuration;
- React/DOM, jsdom, React Testing Library, Playwright, browser binaries, server processes, E2E tests, screenshots, traces, videos, or uploaded artifacts;
- provider/API/model calls, secrets, live devices, SSH, NETCONF, RESTCONF, real inventory, configuration backup/change, runner/adapter execution, queue, scheduler, broker, worker, or AI loop;
- deployment, release, package publishing, repository settings, branch protection, status-check enforcement, or a second workflow;
- Phase 2M-07 implementation, Phase 2N work, Day1-Day160 history, or a second safety matrix.

### Required Phase 2M-06 evidence

The future evidence document must record:

- exact base commit and feature branch;
- exact workflow action SHAs and noted upstream versions;
- exact triggers, permissions, runner image, language versions, and commands;
- local static YAML/scope review and the result of all locally available validation commands;
- the first GitHub Actions run URL and per-step result after push, if push and remote execution are separately authorized;
- whether GitHub-hosted CI evidence was unavailable because push was not authorized;
- exact tracked diff, no-secrets/no-live review, documentation readability review, and final status.

Local workflow creation is not proof that GitHub Actions ran. Phase 2M-06 may be `DONE / READY_FOR_REVIEW` locally, but `DONE / MERGED_TO_MAIN` requires verified integration, and CI PASS requires an actual run result rather than inference.

## Validation for this planning task

Phase 2M-05 validation is documentation-only:

```text
git diff --check
git status --short
tracked-scope review limited to README.md and this Phase 2M-05 document
```

```text
VALIDATION_TESTS_RERUN: NO
VALIDATION_NOT_RUN_REASON: Phase 2M-05 changes documentation only; it does not affect source, tests, dependencies, registry, CLI dispatch, runner or adapter behavior, report rendering, shared utilities, cross-phase runtime behavior, or safety validation behavior. The merged Phase 2M-04 document is the committed baseline evidence.
```

No npm, Node, Python, pytest, Vitest, typecheck, lint, build, or report-index command is required to validate the content-only diff.

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

## Gate result contract

```text
AUTHORIZATION_DECISION: AUTHORIZED
AUTHORIZED_BOUNDARY: One separately requested Phase 2M-06 Safe CI workflow implementation within the exact three-file, read-only-permissions, no-secrets, dual-stack validation boundary above.
EXPLICIT_EXCLUSIONS: Source, tests, dependencies, configuration, React/DOM, Playwright, browser/server, live access, SSH, NETCONF, RESTCONF, provider/API/model calls, secrets, repository settings, deployment, release, package publishing, queue, scheduler, broker, worker, AI loop, config backup/change, production execution, Phase 2M-07, and Phase 2N.
IMPLEMENTATION_PERFORMED: NO
NEXT_CANDIDATE_SELECTED: YES
NEXT_TASK_STARTED: NO
PUSH_PERFORMED: NO
MERGE_PERFORMED: NO
FINAL_PHASE_STATUS: DONE / READY_FOR_REVIEW
```
