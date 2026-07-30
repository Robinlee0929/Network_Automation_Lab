# WF-01-00B Workflow Governance Foundation Reconciliation Plan

Status: **CURRENT / PLANNING_ONLY**
Activation status: **NOT ACTIVE**
Integration status: **LOCAL_ONLY / NOT MERGED / NOT PUSHED**

## 1. Executive decision

Phase 2O-06 is closed and complete. Phase 2O-07 remains deferred and is not authorized. Workflow Governance is the next priority, but WF-01 is not starting from zero: it already has completed local prototype work, independent review evidence, validated failures, and a known replacement bypass. The next goal is to reconcile those assets, correct the remaining repository-local foundations, and prepare a clean reviewed state for future integration.

Repository-local foundations must pass their required reviews and integration gates before any global Skill or `AGENTS.md` migration. This plan does not implement a workflow change, correct a helper or contract, activate workflow version 2, or authorize any later task.

## 2. Verified current baseline

### Live Git facts verified by this planning task

- Local `main` is `2035df121e5479ea97e18dfa5784cce2e66ade91`.
- Local tracking `origin/main` is `2035df121e5479ea97e18dfa5784cce2e66ade91`.
- The main worktree was clean before the planning worktree was created.
- The Phase 2O-06 feature branch is absent.
- The temporary Phase 2O-06 integration worktree is absent.
- The WF-01-00B branch, worktree, and document did not exist before this task.
- The local WF chain is present with `6961c29edd4623d8d2b07a924de7f64ba603fd63` directly descending from `07447586dc6f8b65144d85e9a524cc18fb70279c`, and `13d944c203f6a4755b16870eb39610473cff1df5` directly descending from `6961c29edd4623d8d2b07a924de7f64ba603fd63`.

### Controlling user-provided closure evidence

- Phase 2O-06 status is **CLOSED / COMPLETE**.
- The Phase 2O-06 validation record is 1,964 passing pytest tests, 79 passing Vitest tests, a 25/25 Next.js build, and rendered QA **PASS**.
- The Phase 2O-06 feature branch was deleted and its temporary integration worktree was removed.
- Remote `main` was reported synchronized to `2035df121e5479ea97e18dfa5784cce2e66ade91`.

### Evidence boundary

This task did not contact a remote. The remote synchronization statement above is controlling supplied closure evidence, not a freshly observed remote fact. No application, helper, test-suite, report-index, build, browser, provider, model, device, or external-test validation ran in this planning task.

## 3. Existing WF-01 asset reconciliation

| Work item | Commit / evidence | Current status | Future treatment |
| --- | --- | --- | --- |
| WF-01-00A parallelization audit | Controlling audit evidence | **DONE** | Retain its resource-collision conclusions: repository-local prototypes may use isolated worktrees; the Skill, `AGENTS.md`, canonical status, and shared main state remain global resources. |
| WF-01-01 config/schema | `07447586dc6f8b65144d85e9a524cc18fb70279c`; parent `7c501469a4d0468b5e3394a2f43c7605d8754245` | **DONE / INDEPENDENT REVIEW PASS / LOCAL_ONLY**; not integrated or activated | Correct the correction-policy contract in a separately authorized WF-01-01A task, review it, and include only the final reviewed config/schema state in clean linearization. |
| WF-01-02 original helpers | `6961c29edd4623d8d2b07a924de7f64ba603fd63`; parent `07447586dc6f8b65144d85e9a524cc18fb70279c` | **IMPLEMENTED / REVIEW FAIL** | Preserve as historical development and review evidence; do not copy this known-bad intermediate commit into final main history. |
| WF-01-02 first security correction | `13d944c203f6a4755b16870eb39610473cff1df5`; parent `6961c29edd4623d8d2b07a924de7f64ba603fd63` | **IMPLEMENTED / CUMULATIVE REVIEW FAIL** | Preserve as historical evidence and use its final state as the starting point for a separately authorized second correction. |
| pytest `@response-file` replacement bypass | Independent cumulative review reproduction | **P1 / FAIL_FIX_REQUIRED** | Reject normalized changed paths beginning with `@` before classification, planning, or argv construction; validate through a bounded two-file correction and full cumulative review. |
| Second helper correction | Required by the replacement-bypass finding | **REQUIRED / NOT YET AUTHORIZED** | Unless a future authorization establishes otherwise, limit exact scope to `scripts/validate_fast.py` and `tests/workflow_governance/test_validate_fast.py`. |
| Workflow activation | No activation authorization or evidence | **NOT AUTHORIZED / NOT ACTIVE** | Remain inactive through repository foundation integration, global migration review, pilot, and final acceptance. |
| WF chain integration | Historical branch began from an old base | **NOT A DIRECT INTEGRATION CANDIDATE** | Retain the historical branch as development/review evidence; later recreate only final reviewed content on a fresh linearization branch from then-current main. |

The response-file finding is supported by established independent-review evidence, not merely by a missing regression test or a theoretical concern:

- A repository-relative changed path beginning with `@` was accepted and reached pytest argv.
- The locally observed pytest 8.4.2 expanded that path as a response file.
- The response-file contents selected a repository-external test, which executed and created a marker.
- The helper nevertheless reported **PASS** and returned exit status 0.
- Repository containment of the response file therefore did not guarantee containment of the arguments expanded from that file.
- This was a real replacement bypass and external-execution containment failure.

Future correction validation must not recreate or execute the repository-external test. It must instead prove that every normalized `@`-prefixed changed path is rejected before classification, validation selection, planning, argv construction, command safety approval, or subprocess execution.

WF-01-01 and WF-01-02 are completed local prototype efforts with different review outcomes; neither is unstarted work. The current WF branch is valuable evidence but is not a valid strict-fast-forward integration candidate for current main.

## 4. Phase 2O-06 process findings mapped to WF work

| Observed issue | Future owner | Planning direction |
| --- | --- | --- |
| 1. Windows path literal distortion | WF-01-01 contract and policy; WF-01-02 bootstrap/scope helpers | Define platform-safe path representation in the contract and require deterministic path parsing at helper boundaries. |
| 2. Pre-Git document-reading deadlocks | WF-01-02 bootstrap/scope helpers; WF-01-05 Skill and `AGENTS.md` migration | Keep non-Git prerequisite discovery separate from Git inspection, then migrate only the reviewed sequence globally. |
| 3. Same-scope fixes repeatedly restarting authorization chains | WF-01-01 contract and policy; WF-01-05 migration | Replace a hard correction-count interpretation with an explicitly authorized, cumulatively reviewed security-correction policy. |
| 4. Terminal output truncation and evidence loss | WF-01-03 validation router and durable commands; WF-01-04 canonical status and evidence ownership | Produce structured command results and define which summaries are retained instead of treating terminal scrollback as evidence. |
| 5. Canonical commands differing from temporary validation commands | WF-01-03 validation router and durable commands | Record canonical commands separately from safe task-specific temporary invocations and prove their relationship. |
| 6. Worktrees lacking Node dependency resolution | WF-01-03 validation router, durable commands, and worktree dependency handling | Detect missing dependencies and fail closed unless a verified local resolution source and separately authorized link method are available. |
| 7. Junction creation, verification, source attribution, and safe removal | WF-01-03 worktree dependency handling; WF-01-04 evidence ownership | Require explicit authorization, source/target/type/identity evidence, worktree-local unlinking, and proof that the source survives cleanup. |
| 8. Transient output being confused with retained evidence | WF-01-03 durable commands; WF-01-04 canonical status and evidence ownership | Label transient output, retained review artifacts, and canonical status as different evidence classes with owners and lifetimes. |
| 9. Merge, push, synchronization, and cleanup split into excessive tasks | WF-01-01 contract and policy; WF-01-05 migration | Define a bounded combined integration workflow after review PASS without inferring authority from earlier gates. |
| 10. Correction-commit quantity treated as a security hard limit | WF-01-01 contract and policy | Use a normal target that can be exceeded only through a new explicit security-correction authorization and full cumulative review. |
| 11. Tool-specific secondary argument parsing, including pytest response files | WF-01-02 helpers; WF-01-03 validation router; WF-01-05 migration | Model every selected tool's secondary parsing rules, including response files, before treating a repository-relative argv element as safe. |

These ownership assignments are future planning decisions. They do not implement a solution or authorize the named owner task.

### WF-01-05 Skill and `AGENTS.md` migration boundary

WF-01-05 planning, implementation, and independent review must cover all of the following requirements. Defining them here does not authorize migration.

#### Risk routing

- Route tasks through explicit `low_risk`, `standard`, or `high_risk` profiles.
- When multiple profiles apply, the highest applicable risk takes precedence.
- Ambiguous tasks must fail closed or use the safer profile.

#### Repository workflow contract

- The global Skill must consume the reviewed repository workflow contract rather than silently duplicating or contradicting repository policy.
- Workflow-version compatibility must be checked before use.
- An unavailable, invalid, or incompatible contract must fail closed.

#### Reviewed helper routing

- Route only to reviewed and integrated repository versions of `codex_task_bootstrap.py`, `validate_scope.py`, `validate_fast.py`, and `validate_full.py`.
- Do not reference helper versions that exist only on historical local branches or have not been integrated.

#### Pre-Git separation

- Preserve three distinct stages: non-Git prerequisite discovery; the explicit standalone first `git status --short --branch` command; and post-gate read-only Git inspection.
- Helpers must not claim to prove historical first-command ordering or semantic document reading that they cannot independently observe.

#### Same-scope correction handling

- Treat one correction commit as the normal target, not a hard safety limit.
- Require explicit authorization for an additional security correction, bounded scope, no amend or history rewrite, and cumulative independent review.
- Never retain a known defect merely because the normal target count was reached.

#### Layered validation

- Define deterministic selection among `fast`, `phase`, and `full` validation and fail closed when safe selection cannot be made.
- Distinguish implementation validation from integration validation.
- Do not run the full suite automatically for documentation-only work.
- Require full validation before integration wherever the applicable gate requires it.

#### Combined closure flow

- Where separately and explicitly authorized after all gates pass, one bounded task may perform strict fast-forward, push, local/tracking/remote synchronization verification, status update, safe branch/worktree cleanup, and closure.
- Combining those operations must not remove their separate merge, push, external-operation, evidence, or cleanup authorization requirements.

#### Workflow-version migration boundary

- Define an explicit boundary between workflow version 1 and workflow version 2 and prohibit partially activated mixed-version operation.
- Each active task remains governed by its declared controlling version; resumed version 1 tasks must not silently switch versions.
- New workflow use begins only after migration review passes, and activation state must remain explicit and verifiable.

#### Rollback or disable path

- Provide a safe rollback or disable path when migration review or the pilot fails, helper output is unsafe or inconsistent, contract and helper versions disagree, or repository state cannot be verified.
- Rollback must not rewrite reviewed history, delete required evidence, or leave partially activated global rules.

#### Pilot and review

- Require independent migration review before pilot use.
- Run one bounded low-risk pilot with explicit acceptance criteria and rollback on failure.
- Permit general activation only after pilot **PASS** and final acceptance.

Global Skill or `AGENTS.md` migration cannot begin until the repository-local config/schema foundation is corrected and reviewed, the helper security correction is complete, cumulative helper security review passes, clean linearization is reviewed, full validation passes, and the repository foundation is integrated. These are prerequisites for a future separately authorized migration task, not authorization granted by this plan.

## 5. Correction policy decision

The existing `same_scope_correction.max_additional_commits: 1` value is a normal expected target, not an absolute safety limit. A count target must never force a known vulnerability to remain, force reviewed history to be amended or squashed, or weaken a correction.

The recommended future contract shape is:

```yaml
same_scope_correction:
  normal_additional_commit_target: 1
  normal_additional_commit_target_is_hard_limit: false
  additional_security_correction_requires_authorization: true
  additional_security_correction_requires_cumulative_review: true
```

The future contract must state all of the following:

- One correction commit is the normal expected path, but the target is not a hard limit.
- An additional correction may be authorized after independent review discovers a new P1 finding, replacement bypass, safety regression, or defect that cannot be safely corrected without another commit.
- Every additional correction requires a new explicit authorization decision, the same requirement/finding chain, bounded file scope, no unapproved safety-boundary expansion, no amend or history rewrite, targeted regression validation, and complete cumulative independent review.
- Reaching the normal target must never require preserving a vulnerability, amending reviewed history, squashing away review evidence, weakening a correction, or broadening scope without authorization.

The actual config and schema remain unchanged in this task. WF-01-01A owns the future contract/schema correction, subject to its own authorization and review.

## 6. WF-01-02 second security correction plan

The next bounded correction objective is to close the pytest response-file replacement bypass without broadening the helper design:

- Reject every normalized changed path whose first character is `@`.
- Reject it before classification, plan resolution, or argv construction.
- Do not rely on `--` to prevent response-file expansion.
- On direct, CLI, plan, or execution entry, execute zero commands, emit deterministic JSON, and return exit status 2.
- Preserve safe repository-relative paths containing spaces and Unicode.
- Add direct-function, CLI, plan-mode, and explicit-execution regression tests.
- Validate rejection without executing a repository-external test.
- Review other selected tools for equivalent secondary argument expansion so that tool-specific parsing is an explicit safety property.

Expected future exact file scope:

1. `scripts/validate_fast.py`
2. `tests/workflow_governance/test_validate_fast.py`

This scope is planned, not authorized. A future authorization may change it only with explicit evidence that the two files cannot safely implement the correction.

The subsequent independent review must cover the complete cumulative WF-01-02 chain and rerun all original P1 checks. The previous cumulative review stopped after proving the replacement bypass, so it is not evidence that the other original P1 findings passed the corrected cumulative state.

## 7. Clean linearization and integration strategy

The historical WF branch began from an old base. Current main is `2035df121e5479ea97e18dfa5784cce2e66ade91`, so the existing WF branch cannot be directly strict-fast-forwarded into current main. Known-bad intermediate commits must not become the final repository foundation history.

The required future strategy is:

1. Complete the WF-01-01 correction-policy contract and schema correction.
2. Complete the WF-01-02 second security correction.
3. Obtain a complete independent cumulative security-review **PASS**.
4. Preserve the historical WF branch as development and review evidence.
5. From the then-current clean main, create a new isolated linearization branch and worktree.
6. Recreate only the final reviewed repository state.
7. Use a clean logical commit chain, normally:
   - commit 1: final reviewed workflow config/schema;
   - commit 2: final hardened helper scripts/tests.
8. Do not copy known-bad intermediate WF commits into final main history.
9. Independently review exact content equivalence with the reviewed final WF state, the diff against then-current main, clean ancestry, full file scope, targeted workflow tests, and full repository validation.
10. Only after review **PASS** and separate integration authorization may an integration task perform strict fast-forward, push, local/tracking/remote synchronization verification, and status update; cleanup and closure must additionally satisfy the evidence-retention gate below.

### Historical WF evidence retention gate

Historical WF commits and their review evidence must remain available through every one of these milestones:

1. WF-01-01 policy correction.
2. WF-01-02 final security correction.
3. Complete cumulative security review.
4. Clean linearization.
5. Linearization content-equivalence review.
6. Full repository validation.
7. Repository-foundation integration authorization.
8. Strict fast-forward integration.
9. Verified push and synchronization.
10. Durable retention of final integration evidence.
11. An explicit retention-policy decision.

Successful integration alone does not authorize historical cleanup. Worktree removal and branch deletion are separate decisions: removing a temporary execution environment may occur earlier after its required evidence has been extracted, but deleting a worktree does not authorize deletion of its branch or commit references. A historical branch may be deleted only when an explicit retention-policy decision permits it, and cleanup must not make required review evidence unreachable. Known-bad intermediate commits may remain reachable as historical security-review evidence until all retention requirements are satisfied.

The future retention-policy decision must identify:

- which worktree may be removed and which local branch may be deleted;
- which commit references must remain reachable;
- which review summaries and final integration evidence must remain retained;
- the retained-evidence owner;
- the minimum retention lifetime or objective retention condition;
- proof that final integration evidence has been durably preserved; and
- proof that cleanup will not remove the only reachable reference to required evidence.

Final repository status must not depend on transient terminal output. Cleanup remains unauthorized until the applicable retention decision and all required evidence support it.

No linearization, integration, push, synchronization, cleanup, or closure occurs in this planning task.

## 8. Durable command and evidence policy

| Evidence type | Retention policy | Owner |
| --- | --- | --- |
| Terminal output | Transient; never the sole proof of a required result | Executing task |
| Deterministic JSON command result | Retain when it supports a gate or security conclusion; stable ordering required | WF-01-03 command contract |
| Targeted test summary | Retain command, scope, count, exit result, and limitations | Implementing/reviewing task |
| Failed adversarial proof | Retain a minimal reproducible summary and safety impact, not uncontrolled artifacts | Security review |
| Full validation summary | Retain canonical commands, counts, results, commit, and environment limitations | Integration review |
| Temporary directories | Task-unique and removed after evidence extraction | Executing task |
| Pytest basetemp | Unique per invocation and removed after result capture | WF-01-03 validation router |
| Node dependency workaround | Retain authorization, trusted source identity, method, target, and cleanup proof | WF-01-03 worktree dependency handling |
| Junction/reparse-point evidence | Retain source, target, type, identity verification, unlink result, and source-survival proof | WF-01-03 with WF-01-04 ownership rules |
| Retained review artifact | Explicit owner, purpose, sensitivity classification, and lifetime required | Review owner defined by WF-01-04 |
| Canonical project status | Durable and updated only by its authorized owner from reviewed evidence | WF-01-04 canonical status source |

Terminal output is transient and output truncation must not erase the only copy of a required result. Important command results require deterministic structured output. Temporary directories, caches, and basetemps must be task-unique and removed after evidence extraction. Failed security proofs retain a minimal reproducible summary rather than uncontrolled files.

Any future junction operation must record its source, target, reparse-point type, identity verification, cleanup verification, and source survival after unlink. Retained evidence requires an explicit owner and lifetime. Canonical project status must never be inferred solely from transient terminal logs. This task creates no evidence directory or status file.

## 9. Worktree dependency handling plan

WF-01-03 must define a separate dependency-resolution boundary for Node-enabled isolated worktrees:

- Detect whether the isolated worktree lacks `node_modules` before selecting Node validation.
- Prefer no installation. Use a local dependency source only when its repository identity, dependency/lock compatibility, source path, and trust are verified.
- Refuse unverified or ambiguous dependency sources.
- Treat junction or reparse-point creation as a separately authorized operation, never an implicit validation step.
- Record the trusted source path and identity before linking.
- Verify the target is the intended link/reparse-point type and resolves to the approved source.
- Make cleanup incapable of deleting the dependency source.
- Unlink only the worktree-local junction and verify the source survives afterward.
- Use unique build, cache, and temporary paths.
- Prevent simultaneous builds from sharing conflicting output locations.
- Keep dependency-resolution helpers distinct from validation commands and evidence.
- Fail closed when safe local resolution is unavailable.

This task does not install dependencies or create, inspect, or remove a junction.

## 10. Updated plan table

| Order | Work item | Status |
| ---: | --- | --- |
| 1 | Phase 2O-06 | **CLOSED / COMPLETE** |
| 2 | Phase 2O-07 | **DEFERRED / NOT AUTHORIZED** |
| 3 | WF-01-00A parallelization audit | **DONE** |
| 4 | WF-01-00B foundation reconciliation planning | **CURRENT / PLANNING_ONLY** |
| 5 | WF-01-00B independent planning review | **NEXT AFTER COMMIT** |
| 6 | WF-01-01A correction-policy config/schema update | **WAITING FOR WF-01-00B REVIEW PASS** |
| 7 | WF-01-02B `@response-file` second security correction | **FAIL_FIX_REQUIRED / WAITING FOR PLAN REVIEW PASS AND AUTHORIZATION** |
| 8 | WF-01-02 complete cumulative security review | **WAITING FOR SECOND CORRECTION** |
| 9 | WF-01-01/02 clean linearization from current main | **WAITING FOR CUMULATIVE REVIEW PASS** |
| 10 | Repository foundation independent integration review | **WAITING FOR LINEARIZATION** |
| 11 | Repository foundation integration/push/sync/cleanup | **NOT AUTHORIZED** |
| 12 | WF-01-03 validation router/durable commands/worktree dependencies | **FUTURE / PLANNING REQUIRED** |
| 13 | WF-01-04 canonical project status source | **FUTURE / PLANNING REQUIRED** |
| 14 | WF-01-05 global Skill and `AGENTS.md` migration | **AFTER REPOSITORY FOUNDATION REVIEW** |
| 15 | WF-01-06 low-risk pilot | **NOT STARTED** |
| 16 | WF-01-07 acceptance and activation | **NOT STARTED** |
| 17 | GitHub Actions reuse | **DEFERRED** |

## 11. Authorization gates

| Gate | Prerequisite | Exact artifact or commit | Required review | What becomes authorized | What remains prohibited |
| --- | --- | --- | --- | --- | --- |
| A — WF-01-00B planning review | This planning commit exists locally | WF-01-00B planning document commit | Independent planning review **PASS** | A separate decision may authorize WF-01-01A | Config/schema edits, helper correction, integration, activation |
| B — WF-01-01A policy correction review | Gate A PASS and bounded implementation authorization | Exact WF-01-01A config/schema correction commit | Independent contract/schema review **PASS** | A separate decision may authorize WF-01-02B | Helper correction before authorization, history rewrite, activation |
| C — WF-01-02B implementation complete | Gate B PASS and explicit two-file correction authorization | Exact second-correction commit and required parent | Implementation evidence and bounded regression validation | Complete cumulative security review | Integration, merge, push, activation |
| D — Complete cumulative WF-01-02 review | Gate C complete | Full WF-01-02 cumulative chain through second correction | Independent cumulative security review **PASS** covering every original P1 check | A separate task may create a linearization candidate | Direct use of historical commits as final main history; integration |
| E — Fresh linearization candidate review | Gate D PASS and clean then-current main | Fresh logical config/schema and helper commits | Independent equivalence, ancestry, diff, and scope review **PASS** | Full repository validation on the candidate | Integration, push, global migration |
| F — Full repository validation | Gate E PASS | Reviewed linearization candidate commit | Canonical full validation **PASS** | Repository foundation integration authorization decision | Integration without Gate G; activation |
| G — Repository foundation integration authorization | Gates E and F PASS with trusted destination evidence | Exact candidate and main destination commits | Explicit integration authorization | One bounded strict-fast-forward/push/sync/status task, plus only retention-gated cleanup and closure explicitly permitted by the applicable evidence decision | Force operations, unreviewed content, workflow activation, or cleanup that has not satisfied the retention gate |
| H — Skill and `AGENTS.md` migration review | Foundation integrated and synchronized; separately authorized migration implemented | Exact external Skill and repository `AGENTS.md` migration artifacts | Independent migration review **PASS** | A separately authorized low-risk pilot | General activation, live-device access, provider/model integration |
| I — Low-risk pilot | Gate H PASS and explicit pilot authorization | Exact WF-01-06 pilot scope and evidence | Pilot safety and outcome review **PASS** | Final activation acceptance review | Broad activation or undeclared execution |
| J — Final activation acceptance | Gate I PASS and complete acceptance evidence | Exact WF-01-07 acceptance candidate | Independent final acceptance **PASS** | A separate explicit task may activate workflow version 2 | Activation before separate authorization; Phase 2O-07 work |

Passing a gate proves only that gate. It does not retroactively authorize implementation, integration, migration, pilot execution, activation, or Phase 2O-07.

## 12. Required next sequence

1. Commit this planning document locally.
2. Perform independent WF-01-00B planning review.
3. Correct the WF-01-01 correction-policy contract and schema.
4. Independently review the contract correction.
5. Authorize and implement the two-file WF-01-02 response-file correction.
6. Perform complete cumulative WF-01-02 security review.
7. Create a clean linearization candidate from the then-current main.
8. Perform repository-foundation integration review and full validation.
9. Integrate, push, synchronize and clean up only after explicit authorization.
10. Plan and implement WF-01-03.
11. Plan and implement WF-01-04.
12. Migrate the global Skill and `AGENTS.md`.
13. Run the low-risk pilot.
14. Complete acceptance and activate workflow version 2.
15. Reassess Phase 2O-07 only after workflow stabilization.

## 13. Non-goals

- No Phase 2O-07 work.
- No helper correction.
- No config/schema correction.
- No Skill modification.
- No `AGENTS.md` modification.
- No README modification.
- No canonical status implementation.
- No workflow activation.
- No merge.
- No push.
- No remote contact.
- No branch cleanup.
- No dependency installation.
- No junction creation or removal.
- No full test execution.
- No external-test reproduction.

This document is planning evidence only. It neither represents workflow version 2 as active nor authorizes any implementation or integration step listed above.
