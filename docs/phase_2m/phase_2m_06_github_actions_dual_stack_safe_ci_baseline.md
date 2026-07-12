# Phase 2M-06 — GitHub Actions Dual-Stack Safe CI Baseline

Status: DONE / MERGED_TO_MAIN

Decision summary: Phase 2M-06 is `DONE / MERGED_TO_MAIN`. The exact Safe CI boundary authorized by merged Phase 2M-05 remains one GitHub-hosted Ubuntu job with read-only repository contents permission, no secrets, disabled checkout credential persistence, immutable action pins, and the existing Node and Python validation commands. The first hosted run `29190165478` failed pytest with 36 failed and 1,830 passed because nine positive-path test modules depended on locally generated evidence absent from a clean runner. Bounded `TEST_ONLY_CI_HERMETICITY_REPAIR` commit `1a1795a51b41ee75bfd54638d67297bdf4b7f548` creates deterministic evidence under pytest temporary roots and passed corrective PR run `29192238344`. The source branch was integrated into `main` by fast-forward only with no merge commit or conflict, and push-triggered Safe CI run `29192854074` passed. GitHub recognized PR #47 as merged at the exact repair commit without the PR merge button. Production source, workflow behavior, dependencies, generated reports, and safety semantics remain unchanged by the repair. Phase 2M-07 and Phase 2N remain unauthorized and unstarted.

```text
PHASE: 2M-06
TASK_MODE: IMPLEMENTATION_ONLY / CI_WORKFLOW_ONLY / DOCUMENTATION_ONLY_SUPPORT / NON_LIVE
SAFETY_MODE: STAGE_0 / LOCAL_ONLY_IMPLEMENTATION / NO_SECRETS / NO_LIVE_ACCESS
STATUS: DONE / MERGED_TO_MAIN
BASE_COMMIT: 0dd62844c05acfe8936124a9aad11688b09206aa
FEATURE_BRANCH: codex/phase-2m-06-github-actions-dual-stack-safe-ci-baseline
ORIGINAL_WORKFLOW_COMMIT: 843b4e62a6990cdad6a60a280bb053458817ebe8
CORRECTIVE_COMMIT: 1a1795a51b41ee75bfd54638d67297bdf4b7f548
PR_NUMBER: 47
PR_STATE: CLOSED / MERGED_BY_FAST_FORWARD_MAIN_PUSH / NO_PR_MERGE_BUTTON
CORRECTION_CLASSIFICATION: TEST_ONLY_CI_HERMETICITY_REPAIR
PUSH_AUTHORIZED: YES — SEPARATE BOUNDED INTEGRATION TASK
MERGE_AUTHORIZED: YES — FAST_FORWARD_ONLY IN SEPARATE BOUNDED INTEGRATION TASK
PHASE_2M_07_STARTED: NO
PHASE_2N_STARTED: NO
```

## Mandatory pre-Git gate

The fresh task completed all required reading before invoking Git. The first Git command was exactly `git status --short --branch`, run by itself, and returned `## main...origin/main`.

```text
SKILL_READ_BEFORE_ANY_GIT_COMMAND: YES
AGENTS_MD_READ_BEFORE_ANY_GIT_COMMAND: YES
FIRST_GIT_COMMAND_REQUIRED: git status --short --branch
FIRST_GIT_COMMAND_RUN: git status --short --branch
FIRST_GIT_COMMAND_MATCHED: YES
PRE_GIT_PARALLEL_ORCHESTRATION_USED: NO
```

Pre-Git filesystem-only work, in order:

1. Read the complete `manage-network-lab-codex-tasks` skill.
2. Read `task-modes.md` and `result-contracts.md` completely.
3. Confirmed `C:\Dev\Network_Automation_Lab` as the workspace path without Git.
4. Located and read the applicable root `AGENTS.md` completely.
5. Discovered Phase 2M filenames with filesystem enumeration.
6. Read `README.md` completely using ordered, non-overlapping character windows after the initial full-file output exceeded the display limit.
7. Read every Phase 2M-00 through Phase 2M-05 record completely, including Phase 2M-02A through Phase 2M-02D.
8. Read `docs/automation_readiness/actual_automation_integration_plan.md` completely.

Two early PowerShell process-creation attempts for path confirmation were rejected by Windows before a child process started. They executed neither Git nor a repository command. Path confirmation then succeeded with Windows PowerShell.

## Authorization and implementation boundary

Merged Phase 2M-05 records `SAFE_CI_NECESSITY: REQUIRED` and authorized exactly one workflow plus bounded README and evidence documentation. The Phase 2M-05 implementation commit `f8d9c311cf42e36154b3b2ed7e2b03eca283f7a1` is an ancestor of the synchronized starting commit. Original workflow commit `843b4e62a6990cdad6a60a280bb053458817ebe8` contains exactly the workflow, README, and this evidence record.

The corrective task additionally authorizes only these test/helper files plus README and this evidence record:

- `tests/ai_assistance_evidence_test_fixtures.py`;
- `tests/test_ai_provider_disabled_by_default_safety_regression.py`;
- `tests/test_ai_reviewer_export_package_integration.py`;
- `tests/test_project_folder_organization_decision_gate.py`;
- `tests/test_day145_v04_ai_assistance_evidence_freeze_package.py`;
- `tests/test_day146_v04_ai_assistance_non_advancement_gate.py`;
- `tests/test_day148_ai_assistance_display_consistency_audit.py`;
- `tests/test_day149_ai_assistance_docs_registry_report_index_consistency_audit.py`;
- `tests/test_day150_v04_ai_assistance_phase_gate_closure_review.py`;
- `tests/test_day151_v04_ai_assistance_closure_evidence_index.py`;
- `README.md` and this Phase 2M-06 evidence record for accuracy.

Forbidden and untouched by the implementation and repair tasks:

- production source, workflow content, dependencies, package metadata, lockfiles, requirements, TypeScript, ESLint, or Vitest configuration;
- generated or historical reports, repository-root fixture outputs, test skips, xfails, reduced assertions, or weakened fail-closed behavior;
- React/DOM, jsdom, React Testing Library, Playwright, browser binaries, servers, E2E tests, or artifacts;
- secrets, repository write permission, deployment, release, publishing, branch protection, repository settings, or a second workflow;
- provider/API/model calls, SSH, NETCONF, RESTCONF, live devices, real inventory, configuration backup/change, runner or adapter execution, queue, scheduler, broker, worker, or AI loop;
- Day1-Day160 rewriting, a second safety matrix, Phase 2M-07, Phase 2N, push, or merge.

## Workflow design

The workflow is `.github/workflows/safe-ci.yml` and contains one `ubuntu-latest` job with a 30-minute timeout. It runs only for pull requests targeting `main`, pushes to `main`, and manual `workflow_dispatch`.

```text
WORKFLOW_PERMISSIONS: contents: read
CHECKOUT_PERSIST_CREDENTIALS: false
JOB_COUNT: 1
MATRIX_USED: NO
SELF_HOSTED_RUNNER_USED: NO
SERVICE_CONTAINER_USED: NO
ENVIRONMENT_OR_DEPLOYMENT_USED: NO
ARTIFACT_UPLOAD_USED: NO
SECRETS_REFERENCED: NO
```

The validation sequence is:

```text
checkout
setup Node 22
npm ci
npm run typecheck
npm run lint
npm run test:unit
NEXT_TELEMETRY_DISABLED=1 npm run build
setup Python 3.13
python -m pip install -r requirements.txt
python -m pytest
python network_lab.py --task report-index
git diff --exit-code
```

Dependency installation is limited to materializing the committed `package-lock.json` and `requirements.txt` sets in the ephemeral runner. The workflow does not update dependency versions, run an audit fix, download a browser, start an application server, contact a device/provider/model/private service, or write to the repository.

## Immutable action pins

Official GitHub release pages and commit pages were reviewed read-only before implementation. The workflow uses these immutable full commit SHAs with the upstream release versions retained in comments:

| Action | Upstream version | Immutable commit |
| --- | --- | --- |
| `actions/checkout` | `v4.2.2` | `11bd71901bbe5b1630ceea73d27597364c9af683` |
| `actions/setup-node` | `v4.4.0` | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/setup-python` | `v5.6.0` | `a26af69be951a213d495a4c3e4e4022e16d87065` |

The selected v4/v5 action releases avoid introducing the newer Node 24 action-runtime and minimum-runner requirement into this conservative first baseline. The project runtimes remain explicitly Node 22 and Python 3.13.

## Original local validation evidence

The implementation reused the existing local Node and Python environments. No dependency was installed, removed, updated, audited, or repaired for local validation.

| Gate | Exact command or inspection | Result |
| --- | --- | --- |
| Workflow required entries | Static inspection of triggers, permissions, runner, language versions, and every required command | PASS; no required entry missing |
| Immutable action pins | Full-SHA regex plus official upstream release/commit review | PASS; exactly three 40-character action SHAs |
| One-job boundary | Static indentation-aware `jobs` inspection | PASS; exactly one job |
| Forbidden workflow surface | Static scan for secret references, write permission, unsafe triggers, matrix, self-hosted runner, service, environment/deployment, artifact upload, browser, live-access, provider, and ad-hoc download tokens | PASS; zero matches |
| TypeScript | `npm.cmd run typecheck` | PASS; exit 0; no diagnostics or emit |
| ESLint | `npm.cmd run lint` | PASS; exit 0; zero errors and zero warnings |
| Vitest | `npm.cmd run test:unit` | PASS; 2 files, 56 tests |
| Next.js build | `$env:NEXT_TELEMETRY_DISABLED = '1'; npm.cmd run build` | PASS; exit 0; compiled successfully; 24/24 static pages generated |
| Full pytest | existing Python 3.13.7: `python -m pytest` | PASS; 1,866 passed, 0 failed, 1 existing `GetPassWarning` in 69.09 seconds |
| Report index | existing Python 3.13.7: `python network_lab.py --task report-index` | WARN accepted; exit 0; total 14, pass 1, fail 0, optional missing 13 |
| Staged whitespace | `git diff --cached --check` | PASS; exit 0 |
| Tracked scope | `git diff --cached --name-status` | PASS; exactly the workflow, README, and this evidence document |

The full pytest command was run twice because the first command wrapper yielded before preserving its final exit code. The first process was allowed to finish before the same suite was rerun with explicit session polling. The second run provides the authoritative captured PASS result above. No test, dependency, source, or environment was changed between runs.

Report-index refreshed only its normal ignored latest-overview JSON and HTML outputs. It created, repaired, backfilled, or modified no tracked report or registry file. The Next.js build created or refreshed only ignored `.next/` output.

The original local pass was not proof of clean-runner hermeticity. It consumed generated reports already present in the developer worktree, which the first hosted run did not have.

## GitHub-hosted failure and test-only hermeticity repair

Run `29190165478` executed on Python 3.13.14 under Linux. The job `Node and Python quality gates` passed checkout, dependency installation, typecheck, zero-warning lint, 56 Node unit tests, the 24/24-page Next.js build, Python setup, and Python dependency installation. Step `Run Python tests` failed with 36 failed and 1,830 passed; report-index and tracked-diff proof were then skipped by normal step ordering.

The earliest direct failure was missing `reports/lab-summary/day134_disabled_ai_provider_adapter_contract.json`. Day135 read that ignored/generated file directly; Day136 and Day137 consumed the resulting failed or absent Day134-Day136 evidence; Day145-Day151 then propagated fail-closed evidence-chain results. Complete log review found no independent failure, Linux/Windows path defect, Python 3.13 incompatibility, or workflow-order defect. The workflow correctly installed dependencies before pytest, and its fail-fast ordering only explains why the later report-index and no-diff steps were skipped.

The repair uses one explicit helper, `tests/ai_assistance_evidence_test_fixtures.py`, to copy tracked static inputs and create the minimum deterministic Day127-Day150 prerequisite evidence inside each pytest-managed temporary root. The nine affected modules now pass that root to positive-path builders and CLI checks. Missing, malformed, enabled-provider, enabled-API, enabled-execution, and other negative cases remain fail-closed; no autouse fixture, repository-root write, persistent report, test ordering, skip, xfail, or assertion reduction was introduced.

| Corrective gate | Exact command or method | Result |
| --- | --- | --- |
| GitHub failure inspection | PR #47, run `29190165478`, job `86643307056`, complete decoded job log | CONFIRMED; 36 failed, 1,830 passed; nine failing modules |
| Clean pre-fix reproduction | detached worktree at original commit; exact nine modules | CONFIRMED; 36 failed, 32 passed; same modules and Day134 root prerequisite |
| Targeted normal worktree | exact nine modules | PASS; 68 passed |
| Full pytest normal worktree | `python -m pytest` | PASS; 1,866 passed, one existing warning |
| Clean targeted validation | disposable tracked-files-only worktree plus intended test patch | PASS; 68 passed |
| Clean full pytest | existing Node dependency tree reused through `NODE_PATH`; no install/update | PASS; 1,866 passed, one existing warning |
| Clean report-index | `python network_lab.py --task report-index` | WARN accepted; exit 0; optional missing 13 |
| TypeScript | `npm.cmd run typecheck` | PASS |
| ESLint | `npm.cmd run lint` | PASS; zero warnings |
| Vitest | `npm.cmd run test:unit` | PASS; 2 files, 56 tests |
| Next.js build | telemetry-disabled `npm.cmd run build` | PASS; 24/24 pages |

The first clean full-suite attempt intentionally had no `node_modules` and produced 28 unrelated Node-bridge test failures because `typescript` could not resolve. The authoritative clean full-suite rerun reused the existing unchanged dependency tree via `NODE_PATH`, matching the workflow's already-completed `npm ci` prerequisite without installing or updating anything.

## Post-merge integration and Safe CI reconciliation

The exact two-commit source branch was integrated into local `main` from base `0dd62844c05acfe8936124a9aad11688b09206aa` by `git merge --ff-only`. The resulting `main` head was the repair commit itself, proving that no merge commit, squash, rebase, rewrite, conflict resolution, or PR merge-button action occurred. The main push caused GitHub to recognize PR #47 as merged at `1a1795a51b41ee75bfd54638d67297bdf4b7f548`.

Post-merge local validation passed before the first main push:

| Gate | Result |
| --- | --- |
| TypeScript | PASS; `npm.cmd run typecheck` |
| ESLint | PASS; `npm.cmd run lint`; zero warnings |
| Vitest | PASS; 2 files, 56 tests |
| Next.js build | PASS; telemetry disabled; 24/24 static pages |
| Full pytest | PASS; 1,866 passed; one existing `GetPassWarning` |
| Report index | PASS for command exit; overall WARN only for 13 optional missing local reports; fail 0 |
| Whitespace | PASS; `git diff --check` |

Corrective PR run `29192238344` passed all Safe CI steps at repair commit `1a1795a51b41ee75bfd54638d67297bdf4b7f548`. After fast-forward integration and the first main push, run `29192854074` (`Safe CI #3`) completed successfully on `main`. Its single `Node and Python quality gates` job passed checkout, committed dependency installation, typecheck, zero-warning lint, 56 Node tests, the telemetry-disabled 24/24-page build, 1,866 Python tests, report-index with expected optional-report warnings and exit 0, and `git diff --exit-code` tracked-file immutability proof.

The repair changed no production source, workflow, dependency, package metadata, generated report, or runtime safety behavior. No live device, SSH, NETCONF, RESTCONF, provider, API, model, secret, queue, scheduler, worker, broker, agent loop, configuration backup/change, Day1-Day160 rewrite, or second safety matrix work occurred.

Current hosted state:

```text
GITHUB_HOSTED_INITIAL_CI_RUN: FAIL — run 29190165478 at original commit 843b4e62a6990cdad6a60a280bb053458817ebe8
GITHUB_HOSTED_CORRECTIVE_PR_RUN: PASS — run 29192238344 at repair commit 1a1795a51b41ee75bfd54638d67297bdf4b7f548
GITHUB_HOSTED_PUSH_TO_MAIN_RUN: PASS — run 29192854074 at repair commit 1a1795a51b41ee75bfd54638d67297bdf4b7f548
CI_PASS_CLAIMED: YES
LOCAL_VALIDATION_RESULT: PASS
CLEAN_TRACKED_FILES_ONLY_VALIDATION: PASS
REPORT_INDEX_RESULT: WARN_ACCEPTED_OPTIONAL_LOCAL_REPORTS_ONLY
FAST_FORWARD_INTEGRATION: YES
MERGE_COMMIT_CREATED: NO
MERGE_CONFLICT_OCCURRED: NO
PR_47_STATE: CLOSED / MERGED
```

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
LOCAL_IMPLEMENTATION_DISTINGUISHED_FROM_HOSTED_CI_EXECUTION: PASS
FINAL_READABILITY_RESULT: PASS
```

## Final structured status

```text
FINAL_PHASE_DECISION: PASS
PHASE_2M_06_STATUS: DONE / MERGED_TO_MAIN
AUTHORIZED_SCOPE_TOUCHED: YES
FORBIDDEN_SCOPE_TOUCHED: NO
WORKFLOW_CREATED: YES
WORKFLOW_COUNT: 1
WORKFLOW_PERMISSIONS_READ_ONLY: YES
SECRETS_REFERENCED: NO
LOCAL_VALIDATION_RESULT: PASS
GITHUB_HOSTED_INITIAL_CI_RUN: FAIL — run 29190165478 before correction
GITHUB_HOSTED_CORRECTIVE_PR_RUN: PASS — run 29192238344
GITHUB_HOSTED_PUSH_TO_MAIN_RUN: PASS — run 29192854074
CI_PASS_CLAIMED: YES
CORRECTION_CLASSIFICATION: TEST_ONLY_CI_HERMETICITY_REPAIR
PRODUCTION_SOURCE_CHANGED: NO
WORKFLOW_CHANGED_BY_CORRECTION: NO
DEPENDENCIES_CHANGED: NO
GENERATED_REPORTS_COMMITTED: NO
PR_47_DRAFT_AND_UNMERGED: NO
PR_47_RECOGNIZED_MERGED: YES
FAST_FORWARD_INTEGRATION: YES
MERGE_COMMIT_CREATED: NO
MERGE_CONFLICT_OCCURRED: NO
PUSH_PERFORMED: YES
MERGE_PERFORMED: YES — FAST_FORWARD_ONLY
PHASE_2M_07_STARTED: NO
PHASE_2N_STARTED: NO
```
