# Phase 2M-02D - Network AI Pytest Job-status Contract Baseline Repair / Test-only

Status: DONE / READY_FOR_REVIEW

Conclusion: Phase 2M-02D repaired one stale Python source-text contract and restored the full pytest baseline. Production source and runtime status behavior were unchanged. The repaired test now follows the authoritative delegation chain from the job creation route through `jobs.ts` to `readiness.ts`, while also checking the `NetworkJob.status` union in `schemas.ts` and preserving the no-execution assertions. Phase 2M-03 remains unstarted and unauthorized.

## Task and starting point

```text
PHASE: 2M-02D
TASK_MODE: TEST_ONLY_IMPLEMENTATION
SAFETY_MODE: LOCAL_ONLY / DETERMINISTIC / TEST_ONLY / NON_EXECUTING
START_BRANCH: main
START_COMMIT: 7029c5986fa0859f70fea30f4ab9082179a4720e
FEATURE_BRANCH: codex/phase-2m-02d-network-ai-pytest-job-status-contract-repair
```

The original failing test was:

```text
tests/test_network_ai_node_contract.py::test_network_ai_job_adapter_creates_jobs_without_execution_paths
```

Before editing, the exact targeted command reached the expected stale assertion and exited 1:

```text
python -m pytest tests/test_network_ai_node_contract.py::test_network_ai_job_adapter_creates_jobs_without_execution_paths -q
FAILED: assert "pending_approval" in jobs
1 failed in 0.08s
```

The complete contract file baseline also exited 1 with `1 failed, 3 passed in 0.08s`. The restricted process environment initially could not resolve the `python` command; the same exact commands were rerun with the existing host Python 3.13.7 and pytest 8.4.2, without installing or changing dependencies.

## Root-cause evidence

Commit `79fe866d1f788816a6aa152d0938d4f601378c63` (`fix:remove-unused-network-ai-lint-symbols`) removed this unused declaration from `lib/network-ai/jobs.ts` during Phase 2M-01:

```typescript
const PHASE1_JOB_STATUSES = ["ready", "pending_approval", "blocked"] as const;
```

That deletion removed no referenced or executable behavior. The current authoritative chain remained intact:

- `app/api/network/jobs/create/route.ts` calls `createNetworkJob`.
- `lib/network-ai/jobs.ts` imports and calls `evaluateJobCreateReadiness`.
- `lib/network-ai/jobs.ts` stores `status: readiness.status`.
- `lib/network-ai/readiness.ts` explicitly returns `blocked`, `pending_approval`, and `ready`.
- `lib/network-ai/schemas.ts` defines `NetworkJob.status` as `"ready" | "pending_approval" | "blocked"`.

The Python test still required `pending_approval` and `ready` to appear directly in `jobs.ts`, so it became stale when the unused declaration was removed. File history confirms that the relevant Network AI source and Python contract test were not changed by Phase 2M-02B or Phase 2M-02C.

```text
ROOT_CAUSE_CONFIRMED: YES
ROOT_CAUSE_COMMIT: 79fe866d1f788816a6aa152d0938d4f601378c63
ROOT_CAUSE_CLASSIFICATION: STALE_SOURCE_TEXT_CONTRACT
PRODUCTION_BEHAVIOR_REGRESSION_FOUND: NO
TEST_CONTRACT_REPAIR_APPROPRIATE: YES
PRODUCTION_SOURCE_REPAIR_REQUIRED: NO
```

## Test-only repair

Only `test_network_ai_job_adapter_creates_jobs_without_execution_paths` was changed. No TypeScript module was imported or executed by the test.

Before the repair, the status assertions searched for `pending_approval` and `ready` directly in `jobs.ts`. After the repair, the test:

- verifies the create route still uses `createNetworkJob`;
- verifies `jobs.ts` still uses `evaluateJobCreateReadiness`;
- verifies `jobs.ts` stores `readiness.status`;
- verifies `readiness.ts` explicitly represents `blocked`, `pending_approval`, and `ready`;
- verifies `schemas.ts` retains the complete `NetworkJob.status` union;
- retains the forbidden-term checks across the job creation path.

The status assertions were replaced with assertions against the actual authoritative sources; they were not merely removed. No production declaration, comment, unused symbol, or runtime behavior was added to satisfy the textual contract.

## Validation results

| Gate | Exact command | Result | Exit code |
| --- | --- | --- | ---: |
| Targeted repaired test | `python -m pytest tests/test_network_ai_node_contract.py::test_network_ai_job_adapter_creates_jobs_without_execution_paths -q` | PASS - `1 passed in 0.05s` | 0 |
| Complete Network AI contract file | `python -m pytest tests/test_network_ai_node_contract.py -q` | PASS - `4 passed in 0.05s` | 0 |
| Full pytest | `python -m pytest` | PASS - `1866 passed, 1 warning in 71.77s` | 0 |
| Report index | `python network_lab.py --task report-index` | WARN accepted - total 14, pass 1, fail 0, missing optional 13 | 0 |

The full pytest warning is the existing `GetPassWarning` from `tests/test_day13_multi_router_wireguard_validation.py`. Report-index warnings concern only documented optional local reports; no tracked report or registry file was changed.

## Changed-file scope

Exactly these reviewer-facing files are intended for the Phase 2M-02D commit:

- `tests/test_network_ai_node_contract.py`
- `README.md`
- `docs/phase_2m/phase_2m_02d_network_ai_pytest_job_status_contract_baseline_repair_test_only.md`

No production source, TypeScript or TSX source, other Python test, dependency metadata, Vitest file or configuration, report registry, workflow, or CI file was modified.

## Safety boundary

This repair is local-only, deterministic, test-only, and non-executing. It adds no runtime behavior, job behavior, approval behavior, execution path, runner, adapter, scheduler, queue, broker, worker, AI agent loop, provider/API/model integration, secrets handling, SSH, NETCONF, RESTCONF, live-device access, configuration backup/change behavior, or production execution path. It does not rewrite Day1-Day160 or create a second safety matrix.

Phase 2M-03 remains `FUTURE / NOT_AUTHORIZED`. It was not started, scoped, selected, or authorized by this repair.

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
