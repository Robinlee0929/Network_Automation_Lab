# Phase 2N-03A — Reports Navigation, Empty-state and Error-state Root-cause Review

Status: DONE / MERGED_TO_MAIN

Decision summary: the current defect is `MISSING_PAGE_ROUTE`. The Next.js navigation visibly links `Reports` to `/network/reports`, but the repository has no `app/network/reports/page.tsx`; bounded localhost verification therefore returned HTTP 404 even though the local evidence importer returned data. Restoring ignored historical reports did not and cannot create the missing page. Planning commit `32bf94089b72507043cf1a8788a386f6164895be` was integrated into `main` by fast-forward only, with no merge commit or conflict. Phase 2N-03A is `DONE / MERGED_TO_MAIN`, parent Phase 2N-03 is `IN_PROGRESS`, user-facing acceptance remains `NOT_READY`, and Phase 2N-03B remains `CANDIDATE / NOT_AUTHORIZED / NOT_STARTED`.

## A. Scope and authority

- Parent phase: Phase 2N-03 — User-facing Navigation, Empty-state and Error-state Hardening.
- Current task: Phase 2N-03A.
- Mode: planning-only documentation and bounded read-only evidence review.
- Authorized writes: this document and directly relevant Phase 2N/Reports status text in `README.md`.
- Implementation is not authorized. No route, href, component, reader, API, test, dependency, configuration, workflow, or report was changed.
- Live devices, SSH, NETCONF, RESTCONF, providers, external APIs, model calls, secrets, queues, schedulers, workers, AI loops, configuration backup/change, and production execution remained forbidden and untouched.

## B. Current evidence state

- The user restored historical reports under the ignored local `reports/` directory.
- The latest user-observed report-index result is `PASS`, with `total=14`, `pass=14`, `fail=0`, `warn=0`, `missing=0`, and `unknown=0`.
- That result was not independently rerun. The authoritative command, `python network_lab.py --task report-index`, always rewrites `reports/lab-summary/latest_lab_overview.json` and `.html` with a new generation timestamp, which conflicts with this task's explicit no-report-modification boundary.
- The restored files are local historical evidence, not tracked clean-clone fixtures. Their contents and identifiers were not printed, copied, rewritten, staged, or committed.
- The previously observed Reports 404 required independent revalidation and was reproduced.
- Zero missing reports should produce HTTP 200 with an empty collection/filter state, not route-level 404.
- Source review found no `All Missing Reports` UI label, href, query handler, status filter, or page route. An unconfigured probe of `/network/reports?missing=0` returned 404 because the collection page itself is missing; this is not evidence that a zero-result filter invokes `notFound()`.

## C. Navigation and route map

API routes are listed separately and are not classified as user-facing page routes. In-page evidence selection is also not classified as a dynamic detail page.

| UI entry | Configured href | Matching page file | Matching API route, if any | Expected behavior | Runtime HTTP status | Evidence level |
| --- | --- | --- | --- | --- | --- | --- |
| Landing page | `/` | `app/page.tsx` | None | HTTP 200 and local entry links | 200 | SOURCE_AND_RUNTIME_VERIFIED |
| Network namespace entry | `/network` | `app/network/page.tsx` | None | Redirect to the evidence page | 307 to `/network/day-results` | SOURCE_AND_RUNTIME_VERIFIED |
| Main Reports entry | `/network/reports` from `components/network/NetworkNav.tsx` | **None** | No Reports collection API; a nested analysis API does not satisfy the page route | HTTP 200 with a list when data exists, otherwise a clear empty state | 404 | SOURCE_AND_RUNTIME_VERIFIED |
| `All Missing Reports` entry | **Not found/configured**; bounded probe used `/network/reports?missing=0` only to test the supplied semantic case | **None** | None | If implemented, HTTP 200 with a zero-result empty state when `missing=0` | 404 for the unconfigured probe; exact entry NOT_VERIFIED because no entry exists | SOURCE_AND_RUNTIME_VERIFIED |
| Evidence collection | `/network/day-results` | `app/network/day-results/page.tsx` | `app/api/network/day-results/route.ts` | HTTP 200 and available evidence; zero data must remain HTTP 200 | 200; API also 200 with data | SOURCE_AND_RUNTIME_VERIFIED |
| Report detail | **Not configured**; selection occurs inside `DayResultsClient` | **None** | None | A future supported specific-report detail may return 404 for an unknown ID | NOT_VERIFIED | SOURCE_VERIFIED |
| Latest report analysis API | N/A — API only | **None** | `app/api/network/reports/[reportId]/analysis/latest/route.ts` | HTTP 200 with an analysis record or `analysis: null`; it is not a report detail page | NOT_VERIFIED in this task | SOURCE_VERIFIED |
| Report analysis action | N/A — API only | **None** | `app/api/network/ai/analyze-report/route.ts` | Provider-backed POST outside the safe Demo and outside this task | NOT_VERIFIED | SOURCE_VERIFIED |

Source evidence also shows that `components/network/ReportsClient.tsx` exists but is not imported by any page. `notFound()` is not used in the directly relevant source. The only directly relevant redirect is `/network` to `/network/day-results`.

## D. Runtime evidence

```text
COMMAND: npm.cmd run dev -- --hostname 127.0.0.1
ADDRESS: http://127.0.0.1:3000
PORT: 3000
LISTENER_PID: 19688
LANDING_PAGE_HTTP_STATUS: 200
NETWORK_NAMESPACE_HTTP_STATUS: 307
EVIDENCE_PAGE_HTTP_STATUS: 200
EVIDENCE_API_HTTP_STATUS: 200
REPORTS_LABEL: Reports
REPORTS_HREF: /network/reports
REPORTS_HTTP_STATUS: 404
ALL_MISSING_REPORTS_UI_ENTRY_FOUND: NO
UNCONFIGURED_MISSING_ZERO_PROBE: /network/reports?missing=0
UNCONFIGURED_MISSING_ZERO_PROBE_HTTP_STATUS: 404
REPORTS_EMPTY_STATE_RENDERED: NO
NONEXISTENT_SPECIFIC_REPORT_ROUTE_TESTED: NO
SERVER_PROCESS_STOPPED: YES
PORT_3000_CLOSED: YES
```

The imported evidence API returned 56 items without printing any payload. Repository inventory explains that count as 9 tracked importer-readable JSON/TXT artifacts plus 47 ignored local importer-readable JSON/TXT artifacts. Local data was therefore available, but `/network/reports` still returned 404. The restored reports changed evidence availability, not routing behavior.

No specific-report negative route was tested because source review found no supported user-facing report detail route. The dynamic path under `/api/network/reports/[reportId]/analysis/latest` is an analysis API and must not be reclassified as a report detail page.

The managed terminal did not exit after two interrupts, so the recorded listener PID was stopped directly. Follow-up process, terminal-session, and `netstat` checks proved that the process exited and port 3000 closed.

## E. Root-cause classification

```text
NEXTJS_REPORTS_ROOT_CAUSE: MISSING_PAGE_ROUTE
```

`components/network/NetworkNav.tsx` configures a valid-looking user-facing link to `/network/reports`, while the route tree contains no matching page. `ReportsClient` and the local importer do not become routable merely by existing. Current runtime data availability and a successful `/network/day-results` response independently prove that the Reports 404 is not caused only by absent report data. There is no collection/filter route on which zero-match or `notFound()` behavior could be demonstrated.

## F. Empty-state and error-state contract

| Case | Expected HTTP behavior | Expected user-facing behavior |
| --- | --- | --- |
| Reports collection with data | 200 | Render the report list and a safe initial selection. |
| Reports collection without data | 200 | Render a clear collection-level empty state; do not invoke route-level not-found. |
| Missing-report filter with zero matches | 200 | Render a zero-result empty state and preserve navigation back to the unfiltered collection. |
| Specific nonexistent report | 404, only when a supported specific-report detail route exists | Render a specific not-found state without exposing filesystem paths or other identifiers. |
| Report data-read failure | 500, or an explicitly designed recoverable 200 error state | Render a clear data-unavailable error; never misclassify the failure as a missing page or missing report ID. |
| Missing page route | 404 | Next.js not-found is technically correct, but the condition is a user-facing defect when navigation links to that route. |

## G. Local-report dependency

- `lib/network-ai/dayResults.ts` recursively reads JSON/TXT files from top-level `reports/` and `summary/`.
- `reports/` is ignored for new local files, while the repository also contains a bounded set of already tracked report evidence. Ignore rules do not retroactively untrack committed files.
- Current source inventory contains 9 tracked importer-readable artifacts and 47 ignored local importer-readable artifacts; the runtime API returned their combined count of 56.
- The evidence page can render committed data in a clean clone, but the current local collection, restored historical reports, and user-observed report-index `PASS 14/14` state are not clean-clone reproducible.
- Report data is not required for Next.js to recognize a page route. Restoring data cannot create `app/network/reports/page.tsx`.

```text
REPORT_DATA_LOCALLY_AVAILABLE: YES
REPORT_DATA_CLEAN_CLONE_REPRODUCIBLE: NO
```

## H. Minimal implementation recommendation

Recommend exactly one future candidate:

```text
PHASE_2N_03B_CANDIDATE: Bounded Reports Collection Route and Empty-state Correction
STATUS: CANDIDATE / NOT_AUTHORIZED / NOT_STARTED
```

Likely files for that separately authorized candidate:

- Create `app/network/reports/page.tsx` to mount `NetworkNav`, call the existing read-only `importDayResults()`, and render `ReportsClient`.
- Modify `components/network/ReportsClient.tsx` only as needed to render an explicit collection empty state when the input array is empty.
- Add or update only bounded route/presentation tests chosen by the future authorization.

Files that should remain unchanged unless new evidence and separate authorization require otherwise:

- `components/network/NetworkNav.tsx` because its current `/network/reports` href matches the intended namespace.
- `lib/network-ai/dayResults.ts` and all report filesystem readers.
- All current API routes, provider-backed analysis behavior, job behavior, dependencies, configuration, workflows, Python source, Flask routes, and local reports.

Future contracts:

- Route: `/network/reports` returns 200 for both non-empty and empty collections.
- Href: the existing `Reports` link remains `/network/reports`.
- Empty state: zero reports renders explicit reviewer-facing copy and no `notFound()` call.
- Error state: filesystem/read errors are distinct from route not-found and specific-ID not-found.
- Specific report: no detail route is added by implication; any future supported detail route may return 404 only for a nonexistent specific ID.
- `All Missing Reports`: do not invent a filter from the current source. Define its data contract separately if Phase 2N-03B is explicitly authorized to include it; zero matches must return 200.
- Safety: local, read-only, report-only; no provider, external service, device access, execution, or report mutation.

Required future tests should cover the Reports link/route match, HTTP 200 with data, HTTP 200 with zero data, explicit empty-state copy, missing-filter HTTP 200 if that filter is authorized, and specific-ID 404 only if a detail route is authorized. Existing unit/source tests do not currently test `/network/reports`; no Playwright suite is present.

## I. Validation plan

A future authorized implementation should run:

1. Targeted Vitest for any pure collection/filter logic added under the existing Node-only dependency baseline.
2. Targeted route-level localhost verification, or Playwright only if separately authorized and already available, proving:
   - `/network/reports` returns 200 with data;
   - `/network/reports` returns 200 with no data;
   - an authorized zero-result missing filter returns 200 and renders an empty state;
   - a supported nonexistent specific-report detail returns 404.
3. `npm.cmd run typecheck`.
4. `npm.cmd run lint`.
5. `$env:NEXT_TELEMETRY_DISABLED = '1'; npm.cmd run build`.
6. `npm.cmd run test:unit`.
7. `python network_lab.py --task report-index` only in a task that authorizes its deterministic local overview outputs.
8. Relevant targeted pytest, and full `python -m pytest` if a shared report contract or cross-stack behavior changes.
9. `git diff --check` and an exact changed-file audit.

No validation may require a live device, SSH, NETCONF, RESTCONF, provider, model, external service, secret, or configuration change.

## J. Acceptance effect

```text
USER_FACING_ACCEPTANCE_READINESS: NOT_READY
PARENT_PHASE_2N_03_STATUS: IN_PROGRESS
PHASE_2N_03A_STATUS: DONE / MERGED_TO_MAIN
PHASE_2N_03A_PLANNING_COMMIT: 32bf94089b72507043cf1a8788a386f6164895be
PHASE_2N_03A_INTEGRATION_METHOD: FAST_FORWARD_ONLY
PHASE_2N_03A_MERGE_COMMIT_CREATED: NO
PHASE_2N_03A_MERGE_CONFLICT: NO
NEXTJS_REPORTS_DEFECT_REPRODUCED: YES
NEXTJS_REPORTS_ROOT_CAUSE: MISSING_PAGE_ROUTE
REPORT_DATA_LOCALLY_AVAILABLE: YES
REPORT_INDEX_CURRENT_RESULT: NOT_RUN
USER_OBSERVED_REPORT_INDEX_RESULT: PASS_14_OF_14
MISSING_REPORT_COUNT: 0
MISSING_REPORT_COUNT_EVIDENCE: USER_REPORTED_NOT_INDEPENDENTLY_REVERIFIED
ALL_MISSING_REPORTS_EXPECTED_HTTP_BEHAVIOR: HTTP_200_EMPTY_STATE
ALL_MISSING_REPORTS_ACTUAL_HTTP_STATUS: NOT_VERIFIED_NO_CONFIGURED_ENTRY
UNCONFIGURED_MISSING_ZERO_PROBE_HTTP_STATUS: 404
REPORT_DATA_CLEAN_CLONE_REPRODUCIBLE: NO
PHASE_2N_03B_IMPLEMENTATION_AUTHORIZED: NO
```

## K. Next candidate

```text
RECOMMENDED_NEXT_CANDIDATE: Phase 2N-03B — Bounded Reports Collection Route and Empty-state Correction
RECOMMENDED_NEXT_CANDIDATE_STATUS: CANDIDATE / NOT_AUTHORIZED / NOT_STARTED
```

No implementation, next phase, or extra slice was started.

## Current task validation record

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| Authorized changed-file audit | PASS; only `README.md` and this planning document changed |
| Bounded Next.js localhost verification | PASS; exact route statuses recorded above and temporary server/port closed |
| `python -m pytest` | `VALIDATION_NOT_RUN`; `python` was not available on `PATH` |
| Existing alternate Python/pytest availability | `VALIDATION_NOT_RUN`; the available bundled Python had no pytest, no repository `.venv` interpreter existed, and standalone `pytest` was unavailable |
| `python network_lab.py --task report-index` | `NOT_RUN`; the command would rewrite protected ignored overview reports with a new timestamp |

No dependency was installed or repaired. The pytest limitation is an unavailable-runtime condition, not a reported test failure. The user-observed report-index summary remains evidence supplied by the user rather than a current command result.

## Documentation readability review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT_AND_NOT_WEAKENED: PASS
README_AND_PHASE_STATUS_CONSISTENT: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT: PASS
TERMINOLOGY_CONSISTENT_WITH_CURRENT_PHASE_RECORDS: PASS
SOURCE_AND_RUNTIME_EVIDENCE_DISTINGUISHED: PASS
COLLECTION_EMPTY_AND_SPECIFIC_NOT_FOUND_DISTINGUISHED: PASS
FINAL_READABILITY_RESULT: PASS
```
