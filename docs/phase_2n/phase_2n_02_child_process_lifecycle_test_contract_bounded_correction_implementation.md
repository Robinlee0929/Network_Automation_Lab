# Phase 2N-02 Child-process Lifecycle Test-contract Bounded Correction

Status: DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_CORRECTION_REVIEW

## Conclusion

The bounded Phase 2N-02 lifecycle test-contract correction and its
post-commit private-path redaction are complete in the separate local
worktree. The two-commit correction chain replaces the Windows PID-only child
check with a fail-closed identity-aware contract and removes a private
interpreter path from printed reviewer evidence. It accepts only the exact
single environment runtime bridge established by the controlling diagnosis,
continues to reject every unexplained child, and re-samples captured child
state after exact parent termination.

The change is test-and-documentation-only. Production Flask source, the
historical Phase 2N-02 baseline, README, and the preserved Phase 2O-06 files
did not change. This local result is a review candidate only; it does not
claim independent review, integration authority, merge, push, main
synchronization, worktree cleanup, or Phase 2O-06 completion.

## Task identity and authority

- Task mode: `implementation / FIX_IMPLEMENTATION_ONLY`.
- Initial correction task subtype:
  `PHASE_2N_02_CHILD_PROCESS_LIFECYCLE_TEST_CONTRACT_BOUNDED_CORRECTION_ONLY`.
- Post-commit redaction task subtype:
  `PHASE_2N_02_CORRECTION_POST_COMMIT_PRIVATE_PATH_REDACTION_ONLY`.
- Phase: Phase 2N-02 validation-contract correction.
- Parent context: blocked Phase 2O-06 implementation continuation.
- Starting base: `7c501469a4d0468b5e3394a2f43c7605d8754245`.
- Correction branch:
  `codex/phase-2n-02-child-process-lifecycle-test-contract-correction`.
- Work was isolated in the authorized sibling correction worktree.
- The first correction commit is
  `d53a3bdd696e2f43595314e53370c980f444a38c`.
- A separate review authorized exactly one descendant local redaction commit
  with message `test(phase-2n): redact private runtime path evidence` after all
  fresh validation passes.
- Amend, squash, rebase, and history rewrite remain prohibited.
- Integration, push, remote contact, and worktree removal remain unauthorized.

The controlling authorization was
`AUTHORIZE_ONE_FUTURE_BOUNDED_PHASE_2N_02_TEST_CONTRACT_CORRECTION_TASK`.
It authorized exactly the test and implementation-record paths below.

## Exact two-file scope

1. `tests/test_phase_2n_02_canonical_flask_demo_smoke.py`
2. `docs/phase_2n/phase_2n_02_child_process_lifecycle_test_contract_bounded_correction_implementation.md`

No optional, sibling, substitute, README, production Flask, historical Phase
2N, Phase 2O-06, dependency, configuration, workflow, or report source file is
in scope.

## Post-commit finding and redaction authorization

The first correction commit retained an `interpreter` field in
`PHASE_2N_02_RUNTIME_EVIDENCE` whose value came directly from
`sys.executable`. That reviewer-facing field exposed a private absolute path
and contradicted this record's private-path exclusion claim. Functional
classifier, lifecycle, cleanup, route, and regression results remained valid,
but the correction was blocked from independent review pending redaction.

A separate review-only decision authorized one bounded second commit in the
same two files. It required removal of that field, generic non-sensitive
identity evidence, deterministic redaction tests, fresh validation, and
preservation of the first commit and primary Phase 2O-06 dirty state.

## Root-cause diagnosis

The retained Windows virtual-environment interpreter is a launcher for a base
runtime interpreter. In that topology, starting `sys.executable` produces one
direct child whose full image path is exactly `sys._base_executable`. The child
persists while the launcher parent is alive and exits automatically when the
exact parent terminates.

This is not Werkzeug debug reloader behavior. The application entry point
continues to use `debug=False`, all five GET routes return HTTP 200, the parent
exits, and port 5000 closes and becomes bindable.

## PID-only contract failure

The former Windows helper returned only child PID values. The lifecycle test
therefore rejected every immediate child without executable identity and later
reused the pre-cleanup PID list as proof of final state. It could not
distinguish the exact environment bridge from a Flask/Werkzeug child or prove
that a captured bridge child exited after parent cleanup.

## Identity-aware fail-closed correction

Windows Toolhelp enumeration now records PID, parent PID, executable filename,
and full image path. `OpenProcess` uses only
`PROCESS_QUERY_LIMITED_INFORMATION`; `QueryFullProcessImageNameW` retrieves the
path for immediate children only, and every opened process handle is closed.
Failure to open the child or retrieve its path leaves the identity unavailable
and therefore unclassified.

The pure classifier recognizes a runtime bridge only when all of these
conditions are true:

- the platform is Windows;
- exactly one immediate child exists;
- `sys.executable` and `sys._base_executable` are both available;
- the normalized executable paths differ;
- the child's parent PID equals the exact launched interpreter PID;
- the child's full image path is accessible; and
- the normalized full image path exactly equals normalized
  `sys._base_executable`.

The executable filename alone has no allowlist authority.

## Cases that remain rejected

The contract remains fail-closed for an inaccessible image identity, wrong
full path, filename-only match, arbitrary `python.exe`, multiple children, an
additional unexplained child, an incorrect parent PID, equal executable/base
paths, a non-Windows exemption attempt, a Werkzeug/reloader-like child, or any
captured child still alive after cleanup. POSIX continues to require an empty
immediate child set and receives no runtime-bridge exemption.

## Post-cleanup re-sampling

After terminating and waiting for the exact launched parent, the test
re-samples every captured PID with a bounded five-second wait. An accepted
runtime bridge must disappear automatically. Any captured PID still alive is
reported as unexpected and fails the test. The original pre-cleanup list is no
longer treated as final liveness proof.

Runtime evidence now exposes only generic identity data: PID, parent PID,
filename, path accessibility, fixed interpreter classification, runtime-bridge
detection, exact-identity-match result, paths-redacted state, post-cleanup
alive state, and unexpected-live PID values. Full executable paths remain
internal inputs to normalized exact identity comparison. They are not used as
printed evidence, persisted here, or replaced by a basename or redacted value
for security classification.

## Focused classifier coverage

Twelve deterministic cases in the same test file cover:

1. exact single base-executable bridge acceptance;
2. filename-only rejection;
3. wrong full-path rejection;
4. inaccessible-identity rejection;
5. multiple-child rejection;
6. additional-unexplained-child rejection;
7. equal executable/base rejection;
8. non-Windows exemption rejection;
9. incorrect-parent rejection;
10. unexpected live post-cleanup child rejection;
11. no-child normal acceptance; and
12. Werkzeug/reloader-like child rejection.

The classifier cases use synthetic generic paths and create no live process.

Two additional deterministic evidence tests prove that the former
`interpreter` field is absent, the four generic classification/redaction fields
are present, and recursively inspected JSON string values do not expose
supplied synthetic private-path values. Failure messages identify only a JSON
selector and never echo a matching value.

## Preserved lifecycle behavior

The correction retains all five GET-only routes, `127.0.0.1`, port 5000, the
20-second startup timeout, exact-parent termination, exact-parent kill
fallback, server-output check, port closure and bindability, no command-run
POST, and no non-local network contact.

## Validation evidence

Validation used the existing Python 3.12.13 environment with Flask 3.1.3 and
pytest 8.4.2. No dependency was installed, updated, copied, or linked.

| Validation | Result |
| --- | --- |
| Focused private-path evidence tests | PASS: 2 passed, 14 deselected in 0.48s |
| Existing classifier and cleanup selection | PASS: 12 passed, 4 deselected in 0.25s |
| Complete Phase 2N-02 file | PASS: 16 passed in 2.46s |
| Lifecycle independent run 1 | PASS: 1 passed in 1.91s; five HTTP 200 responses; bridge classified; child exited; port closed |
| Lifecycle independent run 2 | PASS: 1 passed in 1.85s; five HTTP 200 responses; bridge classified; child exited; port closed |
| Lifecycle independent run 3 | PASS: 1 passed in 1.73s; five HTTP 200 responses; bridge classified; child exited; port closed |
| Runtime-evidence private-path scan | PASS; exactly one structured lifecycle record parsed; required generic evidence present; no sensitive candidate or home/profile path found |
| Controlling full pytest | PASS: 1,960 passed in 60.04s |
| Report index | Exit 0; WARN; total 14, pass 1, missing 13; all missing entries are optional local reports; fail 0, warn 0, unknown 0 |
| Documentation private-path scan | PASS; no Windows user-profile path, POSIX home path, or retained runtime literal found |
| Whitespace and exact scope | PASS; cumulative and working changes remain limited to the same two authorized files |
| Primary Phase 2O-06 preservation | PASS; exact branch, HEAD, three dirty paths, empty staged set, and all three controlling SHA-256 values preserved |
| External validation cleanup | PASS; task-owned basetemps and captured output removed after evidence extraction |

Pytest cache writes were disabled and every pytest process used a unique
external task-owned base directory outside both worktrees. Captured output was
also external and was removed after evidence extraction. The controlling full
run used the already-present dependency tree read-only through `NODE_PATH`; it
performed no package install, update, copy, link, or environment repair.

## Safety boundary and non-goals

The correction adds no production application behavior, route, provider, API,
model, secret, device access, SSH, NETCONF, RESTCONF, SNMP, runner, adapter,
queue, scheduler, worker, broker, AI loop, configuration backup/change, or
production execution path. It does not weaken rejection of arbitrary or
unidentified children.

Phase 2O-07 and Phase 2P remain unauthorized and unstarted. Phase 2O-06
validation completion and commit authorization are not granted here.

## Preserved files and documentation state

- Production `dashboard_app.py`: unchanged.
- Historical
  `docs/phase_2n/phase_2n_02_canonical_flask_local_demo_smoke_test_baseline.md`:
  unchanged.
- `README.md`: unchanged.
- The three primary Phase 2O-06 dirty files retained their controlling SHA-256
  values before implementation, after worktree creation, and through final
  validation.

## Documentation readability review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT_AND_NOT_WEAKENED: PASS
STATUS_LABELS_CONSISTENT: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_SECTIONS_SPLIT_FOR_READABILITY: PASS
TERMINOLOGY_CONSISTENT_WITH_PHASE_2N_RECORDS: PASS
PRIVATE_LOCAL_EXECUTABLE_PATHS_EXCLUDED: PASS
RUNTIME_EVIDENCE_AND_DOCUMENTATION_CONSISTENT: PASS
NO_INTEGRATION_OR_NEXT_PHASE_AUTHORITY_IMPLIED: PASS
FINAL_READABILITY_RESULT: PASS
```

## Independent-review handoff

The only next candidate is a fresh independent review of the exact local
two-commit correction chain. Review PASS, integration authorization, merge,
push, main synchronization, worktree removal, branch deletion, and Phase
2O-06 reconciliation require separate future tasks.

## Final status

`DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_CORRECTION_REVIEW`
