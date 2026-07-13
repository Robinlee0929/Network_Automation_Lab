# Phase 2N-03A1 — Reports Collection Safe-presentation Reconciliation

Status: DONE / READY_FOR_REVIEW

Decision summary: Phase 2N-03B should add the missing `/network/reports` page, reuse the existing read-only `importDayResults()` collection, and change `ReportsClient` into a metadata-only reviewer view. The current `ReportsClient` must not be mounted unchanged because it renders `sourcePath` and `rawOutput`, exposes an AI Summary action, and sends report content plus the complete selected result to `/api/network/ai/analyze-report`. The future collection must return HTTP 200 with data or with an explicit empty state, must not expose report payloads or device identity, and must not offer provider/API/model actions. This record is planning only; Phase 2N-03B remains unauthorized and has not started.

## A. Scope and authority

- Parent phase: Phase 2N-03 — User-facing Navigation, Empty-state and Error-state Hardening.
- Current task: Phase 2N-03A1 — Reports Collection Safe-presentation Reconciliation.
- Mode: planning-only documentation and bounded read-only source review.
- Purpose: resolve one safety ambiguity in the Phase 2N-03A recommendation without changing implementation.
- Authorized writes: this planning record and directly relevant Phase 2N-03 status text in `README.md`.
- No source, test, dependency, configuration, workflow, API, Python, or report implementation is authorized.
- Phase 2N-03B and Phase 2N-03C do not start in this task.

Forbidden scope remains live device access, SSH, NETCONF, RESTCONF, provider/API/model calls, secrets, queues, schedulers, workers, AI agent loops, configuration backup/change, production execution, Day1-Day160 rewrites, and a second safety matrix.

## B. Trigger for reconciliation

Phase 2N-03A correctly established `NEXTJS_REPORTS_ROOT_CAUSE: MISSING_PAGE_ROUTE`. Its proposed `app/network/reports/page.tsx` remains directionally correct: `NetworkNav` links Reports to `/network/reports`, and no matching page exists.

Direct inspection of `components/network/ReportsClient.tsx` adds a necessary safety constraint. The existing component presents raw report information and offers a provider-backed analysis action. It therefore conflicts with the local, read-only, report-only Phase 2N user-facing Demo boundary and must not be mounted unchanged.

## C. Source evidence

No real report payload was opened or printed. The answers below are based only on source field names and code behavior.

| # | Evidence question | Source-based answer |
| --- | --- | --- |
| 1 | Does `ReportsClient` render `sourcePath`? | Yes. It places `report.sourcePath` in the report-list row. |
| 2 | Does it render `rawOutput`? | Yes. The selected result's `rawOutput` is rendered in a `pre` element. |
| 3 | Does it render `parsedResult` or another complete payload? | It does not directly render `parsedResult`, but it renders the complete `rawOutput`. It also sends the complete selected `DayResult` as `deviceContext`, which includes `parsedResult`. |
| 4 | Does it render device identity or another potentially sensitive field? | It does not directly reference `deviceName`, but `sourcePath` and `rawOutput` can contain equipment identity or filesystem-derived information. The full selected object sent as context also contains `deviceName`, vendor, identifiers, and payload fields. |
| 5 | Does it expose an AI Summary action? | Yes. The action is visible and invokes `summarize()`. |
| 6 | Does it call `/api/network/ai/analyze-report`? | Yes, with an HTTP POST. |
| 7 | What does it send? | It sends `reportId`, `rawOutput` as `reportText`, and the complete selected `DayResult` as `deviceContext`, including `parsedResult`, `sourcePath`, and device context fields. |
| 8 | Could mounting it expose equipment identity, private content, or filesystem information? | Yes, through visible `sourcePath`/`rawOutput` and the complete context sent by the action. |
| 9 | Could mounting it introduce a provider/API/model path? | Yes. The action reaches a route that calls `analyzeReportWithAi()` and stores the resulting analysis. |
| 10 | Is `ReportsClient` currently mounted? | No. Repository source references only its own declaration; no page imports it. |
| 11 | Is it safe to mount unchanged? | No. |
| 12 | Does `importDayResults()` return an empty array when `reports/` or `summary/` is absent? | Yes. `walkFiles()` returns `[]` for a missing directory, and the two directory results are flattened. |
| 13 | Does the importer read recursively? | Yes. `walkFiles()` recursively descends into subdirectories and the importer reads supported JSON/TXT files. |
| 14 | Does `DayResult` contain sensitive fields? | Yes. Its contract includes `id`, `deviceName`, `rawOutput`, `parsedResult`, and `sourcePath`, in addition to reviewer metadata. |
| 15 | Can expected absence be distinguished from malformed or unexpected failures? | Yes, with an important limitation. Missing directories produce `[]`; malformed JSON produces an item whose `parsedResult` contains a synthetic parse warning; unexpected directory, read, or stat failures are not converted to `[]` and propagate as errors. |
| 16 | Must the importer change for the missing page and empty state? | No. Its current missing-directory behavior already supports an empty collection, and preserving thrown unexpected errors prevents false empty states. |
| 17 | Must the Reports navigation href change? | No. `NetworkNav` already uses `/network/reports`, the intended route. |
| 18 | Is Playwright a direct dependency? | No. It is absent from dependencies and devDependencies. |
| 19 | Is a Playwright configuration present? | No. |
| 20 | Are jsdom, Testing Library, or another DOM-test dependency available? | No such dependency is declared or locked. |
| 21 | Can existing dependencies support a Node-only render test? | Yes. Vitest, React, React DOM, and their types are already present; `react-dom/server` can render synthetic component input without a browser DOM. Source-level route-presence assertions may supplement rendering coverage without a new dependency. |

`components/network/DayResultsClient.tsx` was inspected only as a comparison and is not recommended for modification. It has its own raw evidence and provider-backed controls, but changing that separate Evidence page is outside Phase 2N-03A1 and the bounded future Reports collection.

## D. Safety conflict

The current Reports presentation combines four behaviors that are incompatible with the safe Demo boundary:

- `sourcePath` reveals filesystem-derived report location information;
- `rawOutput` can reveal complete report content and equipment identifiers;
- the complete selected `DayResult` includes device context and parsed payload data;
- AI Summary invokes a provider/API/model-capable route.

The existing `ReportsClient` is therefore **not safe to mount unchanged**. The correction is not to delete or modify the API route; it is to remove the Reports collection's presentation and action path to that route.

## E. Exact Phase 2N-03B recommendation

Produce one bounded implementation: create `app/network/reports/page.tsx`, call the existing `importDayResults()`, render `NetworkNav`, and mount a rewritten metadata-only `ReportsClient`.

### Route and collection behavior

- `/network/reports` returns HTTP 200 when reports exist.
- An empty collection also returns HTTP 200 and renders a clear reviewer-facing empty state.
- The empty state says that no report evidence is currently available, the page is working, and no external service or device operation is required.
- Do not call `notFound()` solely because the collection is empty.
- Do not redirect the empty collection to an unrelated route.
- Preserve normal Next.js error behavior for unexpected programming or filesystem failures; do not catch every error and convert it to an empty collection.

### Safe presentation contract

Render only a constrained reviewer-safe projection rather than arbitrary `DayResult` strings. The exact visible set should be:

- aggregate collection count;
- a fixed reviewer category label derived from `resultKind`;
- normalized status;
- a normalized source-day label when it matches the existing Day-number convention, otherwise a neutral `Unspecified day` label;
- creation date in a stable display format.

Do not fall back to a filename or `sourcePath` for a title. Direct `reportTitle` and `checkType` values are omitted from this bounded recommendation because the importer may derive them from filenames or untrusted report fields and the current contract does not prove that every value is identifier-free.

Explicitly prohibit rendering or embedding in visible markup:

- `sourcePath`, `rawOutput`, `parsedResult`, complete JSON, or complete text payloads;
- device names, hostnames, target-device values, vendor/device context, serial numbers, MAC addresses, credentials, secrets, or private paths;
- report contents that may identify equipment;
- internal exception details;
- complete report identifiers when they are unnecessary for the collection view.

Remove the AI Summary action and all POST requests to `/api/network/ai/analyze-report` from `ReportsClient`. Do not render provider/API/model controls, modifying actions, execution-capable actions, or controls that imply live-device or external-service behavior. Do not modify the provider-backed API route itself.

### Error-state distinction

1. Missing `reports/` or `summary/` directories are expected absence and yield an empty collection.
2. An empty collection renders the HTTP 200 empty state.
3. Malformed JSON remains distinguishable as an imported item with the current parse-warning representation; it is not silently treated as no data.
4. Unexpected filesystem, adapter, or programming failures remain errors and are not converted to empty state.
5. A missing Next.js page is route-level 404 and is corrected by adding the collection page.
6. A nonexistent specific report ID may return 404 only if a separate future task authorizes and implements a supported detail route.

No detail route, missing-only filter, `missing` query parameter, `All Missing Reports` entry, or filter infrastructure is authorized by implication. Preserve the existing Reports href `/network/reports`.

### Test strategy

Use one or more directly relevant Node-only Vitest files with synthetic in-memory `DayResult` objects. Use React server rendering to prove that:

- an empty array renders the explicit empty state;
- safe synthetic metadata and aggregate count render for a non-empty array;
- sentinel values placed in `sourcePath`, `rawOutput`, `parsedResult`, `deviceName`, arbitrary identifiers, and other prohibited fields do not appear in rendered output;
- AI Summary text and analyze-report action markers do not appear;
- no browser DOM, filesystem report fixture, provider, model, external service, or runtime is needed.

A bounded source-level assertion may additionally prove that the new page exists, imports `NetworkNav` and `importDayResults()`, and preserves `/network/reports`. Do not add Playwright, jsdom, Testing Library, or any dependency.

## F. Authorized future files

Future Phase 2N-03B should be limited to:

- `app/network/reports/page.tsx`;
- `components/network/ReportsClient.tsx`;
- one or more directly relevant Node-only Vitest files;
- `docs/phase_2n/phase_2n_03b_bounded_reports_collection_route_and_empty_state_correction.md`;
- `README.md`.

Keep `components/network/NetworkNav.tsx`, `components/network/DayResultsClient.tsx`, `lib/network-ai/dayResults.ts`, all current API routes, dependencies, lockfiles, configuration, workflows, Python source, and report files unchanged unless new evidence and separate authorization require otherwise.

## G. Future validation plan

Phase 2N-03B implementation should run:

1. Targeted Node-only Vitest for the safe Reports collection.
2. `npm.cmd run test:unit`.
3. `npm.cmd run typecheck`.
4. `npm.cmd run lint`, with zero warnings.
5. `$env:NEXT_TELEMETRY_DISABLED = '1'; npm.cmd run build`.
6. `python -m pytest` because report presentation and cross-stack evidence behavior are involved.
7. Bounded localhost startup on `127.0.0.1` only, proving `/`, `/network/reports`, and `/network/day-results` return HTTP 200; both non-empty safe metadata and an isolated zero-data empty state are covered; no raw payload, AI Summary, or `All Missing Reports` feature appears; the temporary process stops and its port closes.
8. `git diff --check` and an exact changed-file audit.

`python network_lab.py --task report-index` must not run when it would rewrite protected ignored reports. Record `REPORT_INDEX_RESULT: NOT_RUN_MUTATING_COMMAND_PROHIBITED`; that is not an implementation failure.

For this planning-only task, Node, npm, Python, pytest, Playwright, runtime, and report-index validation are not applicable and were not run. Only documentation readability, changed-file audit, and `git diff --check` apply.

## H. Report-data boundary

- Restored local reports are ignored historical evidence.
- Their payload content was not read or printed.
- They were not copied, modified, staged, committed, or force-added.
- No real report was used as a fixture.
- Clean-clone reproduction of the complete restored collection remains `NO` / `NOT_VERIFIED`.
- The future page must still render an HTTP 200 empty state when local ignored reports are absent.

## I. Status effect

```text
USER_FACING_ACCEPTANCE_READINESS:
NOT_READY

PARENT_PHASE_2N_03_STATUS:
IN_PROGRESS

PHASE_2N_03A_STATUS:
DONE / MERGED_TO_MAIN

PHASE_2N_03A1_STATUS:
DONE / READY_FOR_REVIEW

PHASE_2N_03B_STATUS:
CANDIDATE / NOT_AUTHORIZED / NOT_STARTED

PHASE_2N_03B_IMPLEMENTATION_AUTHORIZED:
NO

REPORTS_COLLECTION_SAFE_PRESENTATION_CONTRACT_DEFINED:
YES

RAW_REPORT_PRESENTATION_ALLOWED:
NO

SOURCE_PATH_PRESENTATION_ALLOWED:
NO

DEVICE_IDENTITY_PRESENTATION_ALLOWED:
NO

PROVIDER_OR_AI_ACTION_ALLOWED:
NO

ALL_MISSING_REPORTS_FEATURE_AUTHORIZED:
NO

PHASE_2N_03C_AUTHORIZED:
NO
```

## J. Next candidate

```text
RECOMMENDED_NEXT_CANDIDATE:
Phase 2N-03A1 Merge, Push, Synchronization, Cleanup, and Post-merge Status Reconciliation

RECOMMENDED_NEXT_CANDIDATE_STATUS:
CANDIDATE / NOT_AUTHORIZED / NOT_STARTED
```

Do not start Phase 2N-03B until Phase 2N-03A1 is separately reviewed, merged, synchronized, and reconciled.

## Documentation readability review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT_AND_NOT_WEAKENED: PASS
README_AND_PHASE_STATUS_CONSISTENT: PASS
FUTURE_ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT: PASS
TERMINOLOGY_CONSISTENT_WITH_PHASE_2N_03A: PASS
NO_IMPLEMENTATION_BEHAVIOR_INTRODUCED: PASS
FINAL_READABILITY_RESULT: PASS
```
