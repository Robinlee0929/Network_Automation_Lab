# Phase 2O-05 Secondary Next.js Evidence, Reports, AI Actions, and Jobs Visualization — Prerequisite Planning Only

## 1. Conclusion and status

**Conclusion:** Phase 2O-05 prerequisite planning is complete on a local-only
planning branch and is ready for independent review. This document supplies the
controlling per-component safe-field matrix, exact evidence sources, exact
future implementation boundary, state contracts, exclusions, dependency
decision, and validation plan that were missing from the prior continuation
decision. It does not authorize or perform Phase 2O-05 implementation.

```text
PHASE_2O_05_PREREQUISITE_PLANNING_STATUS:
DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_REVIEW

PHASE_2O_05_IMPLEMENTATION_STATUS:
NOT_AUTHORIZED / NOT_STARTED

PHASE_2O_STATUS:
IN_PROGRESS / NOT_READY

PHASE_2O_06_THROUGH_2O_07_STATUS:
NOT_AUTHORIZED / NOT_STARTED

PHASE_2P_STATUS:
NOT_AUTHORIZED / NOT_STARTED

DEPENDENCY_CHANGE_REQUIRED:
NO

STAGE_0_BOUNDARY:
PRESERVED
```

The matrix is an allowlist for presentation only. A field omitted from the
allowlist remains unavailable to the future UI even when it currently exists in
a TypeScript type, API response, local artifact, mock record, or component.
Presence in mock data or current rendering is not evidence that a value is safe.

## 2. Authority and exact planning scope

| Field | Value |
| --- | --- |
| Task mode | `PLANNING_ONLY_DOCUMENTATION` |
| Task subtype | `PHASE_2O_05_PREREQUISITE_SAFE_FIELD_MATRIX_AND_BOUNDED_SCOPE_PLANNING_ONLY` |
| Parent phase | `Phase 2O` |
| Starting commit | `5fc25f9035ee23ee98147e15caeb044e3ed405ba` |
| Planning branch | `codex/phase-2o-05-prerequisite-safe-field-matrix-planning` |
| Changed-file authorization | This new document, `README.md`, and the Phase 2O-00 plan only |
| Application behavior | Unchanged |
| Implementation authority | None |

This task creates prerequisite evidence only. It does not change a route,
component, stylesheet, test, schema, importer, API, store, fixture, artifact,
package, lockfile, configuration, or runtime path.

## 3. Repository evidence inventory

### 3.1 Current routes, consumers, and suppliers

| Surface | Existing route and component | Existing supplier | Current material risk or retained contract |
| --- | --- | --- | --- |
| Evidence | `app/network/day-results/page.tsx`; `components/network/DayResultsClient.tsx` | `importDayResults()` in `lib/network-ai/dayResults.ts`; latest historical analysis GET at `app/api/network/reports/[reportId]/analysis/latest/route.ts` | Current component renders raw output, device identity, arbitrary check/title text, provider/model-bearing analysis records, and action-shaped boundary labels. These are not safe merely because they are already rendered. |
| Reports | `app/network/reports/page.tsx`; `components/network/ReportsClient.tsx` | The same `importDayResults()` result | The accepted metadata-only projection is aggregate count, fixed category, normalized Day/date/status, plus the HTTP-200 empty state. Raw payload, paths, identifiers, titles, check types, and device identity remain excluded. |
| AI Actions | `app/network/ai-actions/page.tsx`; `components/network/AiActionsClient.tsx` | Static `getAvailableActions()` catalog; latest parse-result GET at `app/api/network/ai/parse-request/latest/route.ts` | Static catalog descriptions contain action-shaped historical language. Stored parse records contain user text, inventory material, device/config fields, and provider-derived output. No Parse or Create Job control is rendered. |
| Jobs | `app/network/jobs/page.tsx`; `components/network/JobsClient.tsx` | `listNetworkJobs()` and GET `app/api/network/jobs/route.ts` | Stored records contain target identity and unrestricted `params`. Status values describe recorded readiness, not an active runner. The existing refresh is a GET-only local record reload; no Run control exists. |

The shared shell and Stage 0 terminology are controlled by
`app/network/layout.tsx`, `components/network/NetworkNav.tsx`, and
`components/network/Phase2N04DemoPresentation.ts`. Phase 2O-04 preserved the
exact four routes, canonical Flask identity, skip target, focus baseline, and
`EMPTY`, `MISSING`, `UNAVAILABLE`, `ERROR`, and `BLOCKED` vocabulary.

### 3.2 Schemas, records, artifacts, and tests

- `lib/network-ai/schemas.ts` defines all `DayResult`, `AnalysisRecord`,
  `AvailableAction`, `ParseResultRecord`, `ParseRequestOutput`, and `NetworkJob`
  fields enumerated below.
- `lib/network-ai/dayResults.ts` walks only current `reports/` and `summary/`
  JSON/TXT files, but it can derive values from arbitrary artifact content. It
  stores raw content in `rawOutput`, parsed content in `parsedResult`, and a
  repository-relative path in `sourcePath`. Missing directories return `[]`;
  malformed JSON becomes a fixed `parseWarning` object.
- Representative current report artifacts contain host, username, SSH port,
  device identity, nested checks, raw outputs, report paths, provider/model
  audit fields, private paths, IP addresses, and unrestricted summary arrays.
  Their top-level shapes are evidenced by current JSON under
  `reports/Hex-s-2025-lab01/`, `reports/cisco-switch/`,
  `reports/lab-summary/`, and `summary/`. None of those values is directly
  allowlisted by this matrix.
- `data/network-ai/parse-results.json` and `data/network-ai/jobs.json` are
  currently empty arrays. They prove valid empty stores, not the safety of
  future record values. There is no current committed analyses store.
- The historical Phase 2A-08/2A-09 Jobs planning documents describe
  display-only/mock-only semantics, but their named generated JSON artifacts
  are not present. They are terminology evidence only and are not Phase 2O-05
  data sources.
- `reports/report_index.html` demonstrates that `FOUND` and `MISSING` are
  availability states and that existing reports may describe historical live,
  guarded-live, dry-run, mock-only, or report-only evidence. Phase 2O-05 must
  never convert artifact provenance into current network status.
- `dashboard_app.py` supplies the existing Python `ReportEntry` and
  `DashboardEvidenceEntry` models and the repository's current fixed-field,
  bounded-text, private-path, private-address, provider/model, and secret
  redaction precedents. Those Python helpers are evidence, not a runtime
  dependency for Next.js and are not modified by Phase 2O-05.
- `components/network/ReportsClient.test.tsx` is the controlling synthetic
  prohibited-sentinel and HTTP-200 empty-state projection test.
- `components/network/Phase2N04SafetyLabels.test.ts` and
  `tests/test_network_phase1_ui_presentation.py` preserve provider-unavailable,
  no-submission, no-job-control, recorded-result, and no-run behavior.
- `tests/test_network_day_result_normalization.py`,
  `tests/test_network_ai_analysis_persistence.py`,
  `tests/test_network_ai_workflow_persistence.py`, and
  `tests/test_network_ai_action_recommendation_safety.py` define current
  normalization and record shapes; they do not authorize displaying every
  persisted field.
- `tests/test_phase_2o_03_canonical_flask_display_only_and_technical_detail_presentation.py`
  proves the required private-path, private-address, provider/model, secret,
  bounded-output, and sanitized-JSON negative cases. Phase 2O-05 must provide
  equivalent Next.js sentinels without importing Flask behavior.

## 4. Classification and universal display rules

| Classification | Controlling meaning |
| --- | --- |
| `SAFE_DISPLAY` | May be rendered exactly as a closed enum, committed fixed label, validated opaque identifier, or normalized timestamp defined by this matrix. |
| `DERIVED_SAFE` | Raw value is not rendered. A fixed projection may be rendered only after exact validation/mapping described in the row. |
| `REDACT` | A value may contribute only after the named deterministic redaction; no unredacted fallback is permitted. |
| `OMIT` | Field may be consumed internally but must not be visible, linked, filtered, grouped, counted, or copied into an accessible name. |
| `PROHIBITED` | Field and every derivative that could reveal it must not be consumed for presentation. Encountering it never unlocks detail or execution. |
| `NOT_PRESENT` | The named class is not part of that surface's consumed schema/source. Tests must keep it absent rather than add it. |

Universal rules:

1. Normalize before rendering; unknown or malformed values use fixed copy.
2. Never render a raw object, raw array, `JSON.stringify()` result, raw error,
   traceback, source path, absolute path, payload, command, argument, target,
   inventory, provider, model, secret, credential, or configuration content.
3. `createdAt` and report dates describe recorded artifact time only. They must
   not be labeled current, live, last checked, healthy, reachable, or running.
4. `ready`, `jobCreationAllowed`, `readOnly`, `requiresApproval`, and risk values
   are historical record/catalog attributes. They grant no present capability.
5. Unknown identifiers, enum values, status values, or object shapes produce a
   fixed `UNKNOWN`, `REJECTED`, or `UNAVAILABLE` state; they do not fall back to
   raw text.
6. No row authorizes a new data source, schema field, API, importer, or store.

## 5. Controlling per-component safe-field matrix

The four tables below form one controlling matrix. Every field in every current
consumed schema is classified. Row IDs are used by the class-coverage and
validation crosswalks.

For table compactness only, `Same` is strict ditto notation rather than a
catch-all. It expands to the closest preceding non-`Same` value in the same
column. The following range map makes every route/component and source expansion
explicit; no row may resolve to any source outside this map:

| Row range | Exact route/component expansion | Exact data-source expansion |
| --- | --- | --- |
| E02-E17 | `/network/day-results`; `components/network/DayResultsClient.tsx` | `DayResult` from `lib/network-ai/schemas.ts` and `importDayResults()` in `lib/network-ai/dayResults.ts`, except an explicit row-level derivation replaces this source |
| E19-E40 | `/network/day-results`; the historical-analysis panel in `components/network/DayResultsClient.tsx` | `AnalysisRecord` from `lib/network-ai/schemas.ts`, read by GET `app/api/network/reports/[reportId]/analysis/latest/route.ts`, except an explicit row-level derivation replaces this source |
| R02-R16 | `/network/reports`; `components/network/ReportsClient.tsx` | `DayResult` from `lib/network-ai/schemas.ts` and `importDayResults()` in `lib/network-ai/dayResults.ts`, except an explicit row-level derivation replaces this source |
| A02-A08 | `/network/ai-actions`; `components/network/AiActionsClient.tsx` | committed `AvailableAction[]` from `getAvailableActions()` in `lib/network-ai/actions.ts` |
| A10-A31 | `/network/ai-actions`; the recorded-recommendation panel in `components/network/AiActionsClient.tsx` | `ParseResultRecord`/nested `ParseRequestOutput` from `lib/network-ai/schemas.ts`, read by GET `app/api/network/ai/parse-request/latest/route.ts`, except an explicit row-level derivation replaces this source |
| J02-J21 | `/network/jobs`; `components/network/JobsClient.tsx` | `NetworkJob[]` from `lib/network-ai/schemas.ts` and `listNetworkJobs()` in `lib/network-ai/jobs.ts`, read by GET `app/api/network/jobs/route.ts`, except an explicit row-level derivation replaces this source |

`Current client`, `current component`, and shortened file stems in the Evidence
column refer only to the exact paths enumerated in Section 3. An Evidence cell
is a cross-reference, not permission to discover or substitute another source.

### 5.1 Evidence matrix

| ID | Surface | Route or component | Data source | Field path | Classification | Display rule | Null/empty rule | Unavailable-state rule | Sanitization rule | Historical/current rule | Evidence | Required test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | Evidence | `/network/day-results`; `DayResultsClient` | `DayResult` from `importDayResults()` | `id` | `DERIVED_SAFE` | Use only as React key/selection and encoded existing latest-analysis GET input; never render or link it. | No ID means reject the item from visible projection. | Latest analysis is `UNAVAILABLE`; evidence summary remains. | Accept only non-empty bounded string for internal equality; never interpolate into visible copy. | Internal recorded correlation only. | `schemas.ts`; `dayResults.ts`; current client | Sentinel must not appear in markup or accessible names; encoded GET remains GET-only. |
| E02 | Evidence | Same | Same | `sourceDay` | `DERIVED_SAFE` | Render only `Day N` when the whole value matches `^day[-_ ]?([0-9]{1,3})$`; otherwise `Unspecified day`. | Null/blank becomes `Unspecified day`. | Same fixed fallback. | Never render unmatched source text. | Artifact grouping only, never current progress. | `dayResults.ts::inferSourceDay`; normalization tests | Valid/malformed/adversarial day sentinels. |
| E03 | Evidence | Same | Same | `dayLabel` | `OMIT` | Do not render; E02 is the sole visible day projection. | No visible output. | No visible output. | None; omission is mandatory. | Not a current phase label. | `schemas.ts`; current client fallback behavior | Prohibited sentinel absent. |
| E04 | Evidence | Same | Same | `resultKind` | `DERIVED_SAFE` | Map the five schema enum values to fixed category/type labels and fixed grouping order. Raw enum may be a non-visible data value only. | Missing/unknown becomes fixed `Uncategorized Evidence`. | Category remains available if collection item is otherwise valid. | Closed enum mapping only. | Recorded artifact type. | `schemas.ts::dayResultKinds`; current fixed maps; normalization tests | All enum values and an unknown sentinel map without raw leakage. |
| E05 | Evidence | Same | Same | `deviceName` | `PROHIBITED` | Never render, group, filter, count, title, or derive identity from it. | No target placeholder is needed. | Fixed Stage 0 copy states device identity is withheld. | No partial masking; omit whole value. | Must not imply a current target. | Reports safe contract; representative device reports | Device/hostname/IP sentinels absent. |
| E06 | Evidence | Same | Same | `reportTitle` | `OMIT` | Do not render; arbitrary artifact text has no Next.js sanitizer contract. | Fixed category is sufficient. | Fixed category remains. | No basename/title fallback. | Recorded free text is not current project status. | `dayResults.ts::inferReportTitle`; Reports prohibited-sentinel test | Title sentinel absent, including button names. |
| E07 | Evidence | Same | Same | `vendor` | `OMIT` | Do not display or filter; importer may infer it by scanning raw content. | No visible output. | No visible output. | No provider/device-vendor inference in presentation. | No current support claim. | `dayResults.ts::inferVendor`; schemas | Vendor sentinels absent. |
| E08 | Evidence | Same | Same | `checkType` | `OMIT` | Do not render arbitrary check/task/type text. | Fixed category is sufficient. | Fixed category remains. | No raw fallback. | No current operation claim. | `dayResults.ts::inferCheckType`; Reports safe contract | Check-type sentinel absent. |
| E09 | Evidence | Same | Same | `status` | `DERIVED_SAFE` | Map only PASS/success/ok to `PASS`, warn/warning to `WARN`, fail to `FAIL`, block to `BLOCKED`, review to `REVIEW`, else `UNKNOWN`. | Blank becomes `UNKNOWN`. | `UNKNOWN`, never inferred PASS. | Raw status text never renders. | `Recorded result`; not live health. | `ReportsClient::reportStatus`; Phase 2O status vocabulary | Closed vocabulary, raw-status sentinel rejection, non-color text. |
| E10 | Evidence | Same | Same | `rawOutput` | `PROHIBITED` | Remove the raw evidence block; no raw or bounded preview is authorized in this slice. | No raw-detail placeholder. | Fixed statement: technical payload is not displayed on this surface. | Omit entire value; never use `dangerouslySetInnerHTML` or stringify. | Historical payload grants no current authority. | Current client exposure; Phase 2O-00 §3.6; Flask redaction tests | Secrets, paths, IPs, commands, provider/model, traceback, and long payload sentinels absent. |
| E11 | Evidence | Same | Same | `parsedResult` | `PROHIBITED` | Never render/stringify/traverse for display, status, boundary, or summary. E12 separately defines the sole exact fixed-warning derivation. | No visible output. | Fixed rejected/malformed state may come only from E12. | No catch-all object projection. | Historical payload only. | `schemas.ts`; `parseReport()` | Nested forbidden sentinels absent. |
| E12 | Evidence | Same | `parseReport()` fixed parse failure record | `parsedResult.parseWarning` | `DERIVED_SAFE` | When exact fixed value is `JSON report could not be parsed.`, show fixed `REJECTED — malformed local evidence`; never render the field. | Absent means no malformed marker. | Malformed detail remains unavailable. | Exact equality only; ignore all other object fields. | Recorded import condition, not current runtime health. | `dayResults.ts::parseReport` | Exact/mutated warning cases and no raw JSON. |
| E13 | Evidence | Same | `DayResult` | `createdAt` | `DERIVED_SAFE` | Parse valid timestamp and render UTC `YYYY-MM-DD` labeled `Recorded`; invalid becomes `Unknown date`. | Missing becomes `Unknown date`. | Same fallback. | Do not render locale/private timezone or raw timestamp. | Historical artifact date only. | `ReportsClient::creationDate`; schemas | Valid/invalid timestamp and no `current/latest health` wording. |
| E14 | Evidence | Same | `DayResult` | `sourcePath` | `PROHIBITED` | Never display, link, derive a filename/title, filter, or accessible name. | No path placeholder. | Fixed `Source path withheld`. | Omit absolute, home, repository-relative, basename, username, and extension-bearing private identity. | Not evidence freshness. | Reports safe contract; private-path tests | Windows/POSIX/quoted/spaced path and filename sentinels absent. |
| E15 | Evidence | Imported collection | `DayResult[]` | `results.length` | `DERIVED_SAFE` | Display integer aggregate count and fixed singular/plural label. | Zero is valid `EMPTY`. | Missing directories also yield `[]`; do not claim `MISSING` without a distinct source signal. | Count only validated projected items; never count rejected objects as safe. | Count of locally recorded artifacts, not devices/jobs. | `importDayResults()`; current toolbar | 0/1/many and rejected-item count tests. |
| E16 | Evidence | Evidence list | Derived from E04/E02/E09/E13 | grouping, sorting, filtering, selection | `DERIVED_SAFE` | Group/filter/sort only by fixed category, normalized Day number, normalized status, and recorded date; selection is local UI state. | No matches use fixed `EMPTY — no matching recorded evidence`. | No data source triggers `EMPTY`; no network retry. | Never use title, device, path, raw text, or provider/model metadata. | Recorded collection only. | Phase 2O-00 §§6.2, 8.1; current sorting helpers | Keyboard selection, result count announcement, reset, and sentinel non-influence. |
| E17 | Evidence | Current client | `deriveExecutionBoundary()` | derived `ExecutionBoundary` | `PROHIBITED` | Remove `Read-only candidate` and `Approval required` display; use fixed `Recorded evidence · non-executing` presentation. | No item means no boundary badge. | Stage 0 remains `UNAVAILABLE` for operations. | Do not inspect device identity or parsed risk to derive visible authority. | Never present execution readiness as current. | Current client; Stage 0 shell | Forbidden labels/derivation absent; fixed non-executing label present. |
| E18 | Evidence | Historical Analysis panel | Latest-analysis GET | analysis presence | `DERIVED_SAFE` | Show only fixed `Recorded analysis available` or `No recorded analysis`; optional safe rows E34-E36, E38, and E40 follow. | Null means no record. | Provider analysis remains `UNAVAILABLE`; no Analyze control. | Boolean presence only. | Historical record, not a fresh provider result. | latest-analysis GET; Phase2N04 presentation/test | Null/record/error/loading states and no POST/control. |
| E19 | Evidence | Same | `AnalysisRecord` | `id` | `OMIT` | Do not display or link. | No visible output. | No visible output. | Omit arbitrary identifier. | Internal record identity only. | `schemas.ts` | Identifier sentinel absent. |
| E20 | Evidence | Same | Same | `reportId` | `OMIT` | Do not display. | No visible output. | No visible output. | Omit. | Internal correlation only. | `schemas.ts`; analysis store | Sentinel absent. |
| E21 | Evidence | Same | Same | `sourceDay` | `OMIT` | Use E02 from selected artifact, not analysis copy. | No visible output. | No visible output. | Omit. | Prevent conflicting chronology. | `schemas.ts` | Conflicting value cannot alter UI. |
| E22 | Evidence | Same | Same | `resultKind` | `OMIT` | Use E04 from selected artifact. | No visible output. | No visible output. | Omit. | Prevent conflicting category. | `schemas.ts` | Conflicting value cannot alter UI. |
| E23 | Evidence | Same | Same | `targetDevice` | `PROHIBITED` | Never render. | No target placeholder. | Fixed identity-withheld copy if needed. | Omit whole value. | No current target implication. | `schemas.ts`; safe Reports contract | Device/host/IP sentinel absent. |
| E24 | Evidence | Same | Same | `checkType` | `OMIT` | Never render. | No output. | No output. | Omit. | No operation implication. | `schemas.ts` | Sentinel absent. |
| E25 | Evidence | Same | Same | `model` | `PROHIBITED` | Never render provider/model identity. | No model placeholder. | Provider/model capability is `UNAVAILABLE`. | Omit key and value. | Historical model use grants no current provider authority. | `schemas.ts`; Flask provider/model tests | Case/separator/provider/model sentinels absent. |
| E26 | Evidence | Same | Same | `promptVersion` | `OMIT` | Never render. | No output. | No output. | Omit. | Historical implementation metadata. | `schemas.ts` | Sentinel absent. |
| E27 | Evidence | Same | Same | `inputHash` | `OMIT` | Never render or link. | No output. | No output. | Omit hash. | Historical correlation only. | `schemas.ts`; analysis store | Hash sentinel absent. |
| E28 | Evidence | Same | Same | `output.summary` | `OMIT` | Do not render provider-produced/user-influenced summary text in Stage 0. | No summary placeholder. | Fixed `Recorded analysis detail unavailable`. | Omit, not truncate. | Historical provider output only. | `schemas.ts`; Phase 2O-00 raw-detail rule | User text/secret/provider/path sentinels absent. |
| E29 | Evidence | Same | Same | `output.findings` | `OMIT` | Do not render. | No output. | Fixed detail-unavailable copy. | Omit array. | Historical provider output. | `schemas.ts` | Array sentinels absent. |
| E30 | Evidence | Same | Same | `output.warnings` | `OMIT` | Do not render raw warnings. | No output. | Fixed detail-unavailable copy. | Omit array. | Historical provider output. | `schemas.ts` | Array sentinels absent. |
| E31 | Evidence | Same | Same | `output.possibleCauses` | `OMIT` | Do not render. | No output. | Fixed detail-unavailable copy. | Omit array. | Historical provider output. | `schemas.ts` | Array sentinels absent. |
| E32 | Evidence | Same | Same | `output.recommendedActions` | `PROHIBITED` | Never render action text. | No output. | Operations remain `UNAVAILABLE`. | Omit array and derivatives. | Never current authority. | `schemas.ts`; Stage 0 no-action tests | Action/command sentinels absent. |
| E33 | Evidence | Same | Same | `output.recommendedExistingActionIds` | `PROHIBITED` | Never render or create links/controls. | No output. | Operations remain `UNAVAILABLE`. | Omit array and counts. | Never current authority. | `schemas.ts`; action-safety tests | IDs and controls absent. |
| E34 | Evidence | Same | Same | `output.riskLevel` | `DERIVED_SAFE` | Map exact `low`, `medium`, or `high` to fixed label prefixed `Recorded risk`; else `UNKNOWN`. | Missing becomes `UNKNOWN`. | No risk means no operational inference. | Closed enum only. | Historical analysis attribute. | `schemas.ts::riskLevels` | Enum/unknown and `Recorded` qualifier. |
| E35 | Evidence | Same | Same | `output.requiresApproval` | `DERIVED_SAFE` | Render fixed `Recorded approval flag: yes/no`; never an approval control. | Missing becomes `Unknown`. | Approval workflow remains unavailable. | Boolean only. | Historical flag, no approval authority. | `schemas.ts`; safety tests | Boolean/null and no button/form. |
| E36 | Evidence | Same | Same | `output.needsHumanReview` | `DERIVED_SAFE` | Render fixed `Recorded human-review flag: yes/no`. | Missing becomes `Unknown`. | No workflow is created. | Boolean only. | Historical flag. | `schemas.ts` | Boolean/null and no workflow language. |
| E37 | Evidence | Same | Same | `safety.recommendedActionIdsSanitized` | `OMIT` | Do not display internal sanitizer flag. | No output. | No output. | Omit. | Historical implementation detail. | `schemas.ts` | Sentinel absent. |
| E38 | Evidence | Same | Same | `safety.jobCreationAllowed` | `DERIVED_SAFE` | Render only fixed `Recorded job eligibility: yes/no · job creation unavailable in Stage 0`. | Missing becomes `Unknown · unavailable`. | Always state current unavailability. | Boolean only. | Historical flag cannot authorize a job. | `schemas.ts`; Phase2N04 tests | Both booleans retain unavailable suffix; no control. |
| E39 | Evidence | Same | Same | `safety.reason` | `OMIT` | Do not render arbitrary reason text; use fixed Stage 0 explanation. | No output. | Fixed explanation remains. | Omit. | Historical text. | `schemas.ts` | Sentinel absent. |
| E40 | Evidence | Same | Same | `createdAt` | `DERIVED_SAFE` | Valid UTC date as `Recorded analysis date`; invalid `Unknown date`. | Missing unknown. | Same. | Same timestamp rule as E13. | Historical only. | `schemas.ts`; analysis store | Valid/invalid date and recorded qualifier. |
| E41 | Evidence | Client fetch state | existing GET | loading/error | `DERIVED_SAFE` | Loading uses `role=status`; error uses fixed `Unable to read the recorded analysis.` No payload/error text. | Settled null follows E18. | No retry that contacts provider/device. | Ignore raw exception, response body, stack, URL, and identifiers. | Current UI read state only, not network/device state. | Current client; API route | Loading announcement; synthetic raw-error/traceback sentinels absent. |

### 5.2 Reports matrix

| ID | Surface | Route or component | Data source | Field path | Classification | Display rule | Null/empty rule | Unavailable-state rule | Sanitization rule | Historical/current rule | Evidence | Required test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Reports | `/network/reports`; `ReportsClient` | `DayResult` | `id` | `OMIT` | React key only; never visible or linked. | Reject missing item identity from projection. | No detail link. | Omit raw ID. | Internal correlation only. | Current component/test | ID sentinels absent. |
| R02 | Reports | Same | Same | `sourceDay` | `DERIVED_SAFE` | Same exact normalized `Day N` rule as E02. | `Unspecified day`. | Same fallback. | Never render unmatched raw value. | Recorded artifact grouping only. | Current component/test | Valid/untrusted values. |
| R03 | Reports | Same | Same | `dayLabel` | `OMIT` | Never render. | No output. | No output. | Omit. | Not current. | Reports sentinel test | Sentinel absent. |
| R04 | Reports | Same | Same | `resultKind` | `DERIVED_SAFE` | Closed mapping to five fixed report categories. | Unknown -> `Uncategorized Evidence`. | Fixed category available. | Closed enum only. | Recorded artifact category. | Current component/test | All enums/unknown. |
| R05 | Reports | Same | Same | `deviceName` | `PROHIBITED` | Never render/count/filter/link. | No output. | Fixed identity-withheld rule. | Omit. | No target/current implication. | Phase2N-03B/C; sentinel test | Device/host/IP absent. |
| R06 | Reports | Same | Same | `reportTitle` | `PROHIBITED` | Never render. | Fixed category is sufficient. | Same. | Omit arbitrary title. | Historical free text. | Phase2N-03B/C; sentinel test | Title absent. |
| R07 | Reports | Same | Same | `vendor` | `OMIT` | Never render/filter. | No output. | No output. | Omit. | No current support claim. | Sentinel test | Vendor absent. |
| R08 | Reports | Same | Same | `checkType` | `PROHIBITED` | Never render. | No output. | No output. | Omit. | No action implication. | Phase2N-03B/C; sentinel test | Check sentinel absent. |
| R09 | Reports | Same | Same | `status` | `DERIVED_SAFE` | Same normalized closed vocabulary as E09. | `UNKNOWN`. | `UNKNOWN`, never PASS by availability. | Raw status never renders. | Recorded result quality only. | Current component/test; report-index distinction | Raw/custom sentinels absent; non-color label. |
| R10 | Reports | Same | Same | `rawOutput` | `PROHIBITED` | Never render or summarize. | No output. | No output. | Omit. | Historical payload. | Phase2N-03B/C; sentinel test | Raw/secret/path/provider sentinels absent. |
| R11 | Reports | Same | Same | `parsedResult` | `PROHIBITED` | Never render or derive summary. | No output. | No output. | Omit nested object. | Historical payload. | Phase2N-03B/C | Nested sentinel absent. |
| R12 | Reports | Same | Same | `createdAt` | `DERIVED_SAFE` | UTC `YYYY-MM-DD`; invalid `Unknown date`. | Unknown date. | Same. | Never raw timestamp. | Recorded artifact date. | Current component/test | Valid/invalid. |
| R13 | Reports | Same | Same | `sourcePath` | `PROHIBITED` | Never display, derive filename, or link. | No output. | No output. | Omit path/basename. | Not freshness. | Phase2N-03B/C; sentinel test | Windows/POSIX/path sentinels absent. |
| R14 | Reports | Collection | `DayResult[]` | `reports.length` | `DERIVED_SAFE` | Integer count and fixed label. | Zero uses the exact accepted HTTP-200 empty copy. | Missing storage also yields zero; do not fabricate `MISSING`. | Count valid projected items only. | Local recorded reports only. | Reports test; Phase2N-03B/C | 0/1/many and HTTP 200. |
| R15 | Reports | Route/page | Existing GET page | links/identifiers | `NOT_PRESENT` | No report detail link is added; no safe filename or identifier is currently approved. | Empty remains on page. | No external/device link. | Keep absent. | No navigation to raw detail. | Current component; Phase2N-03B/C | No href/ID/path/title. |
| R16 | Reports | Route/page | Importer behavior | empty/missing/malformed/error | `DERIVED_SAFE` | `[]` -> accepted `EMPTY`; unexpected importer/programming failure remains error boundary; malformed individual artifact may project only normalized metadata/`UNKNOWN`, never raw detail. | Exact accepted empty copy retained. | No device/external operation suggested. | Fixed state copy only. | Page/read state, not device health. | Phase2N-03B/C; importer | HTTP-200 empty; failure not converted to empty; malformed sentinels absent. |

### 5.3 AI Actions matrix

| ID | Surface | Route or component | Data source | Field path | Classification | Display rule | Null/empty rule | Unavailable-state rule | Sanitization rule | Historical/current rule | Evidence | Required test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | AI Actions | `/network/ai-actions`; `AiActionsClient` | committed `AvailableAction` catalog | `id` | `SAFE_DISPLAY` | Display only when exact ID exists in `availableNetworkActions`; otherwise omit item. | No catalog items -> fixed `No static action references available`. | All actions remain unavailable for execution. | Exact catalog membership; no arbitrary ID. | Static reference, not executable action. | `actions.ts`; schemas | Known/unknown catalog IDs and no controls. |
| A02 | AI Actions | Same | Same | `label` | `SAFE_DISPLAY` | Display committed label only for an A01-approved catalog row. | Use fixed ID label only if committed label blank; no user fallback. | Fixed unavailable notice precedes catalog. | No runtime value. | Static reference. | `actions.ts` | Exact fixed labels. |
| A03 | AI Actions | Same | Same | `description` | `OMIT` | Do not render current action-shaped descriptions. Future helper maps each approved ID to new fixed Stage 0 reviewer copy. | No description -> fixed `Static catalog reference`. | Copy must say no request/run/provider/job capability. | ID-to-fixed-copy map only. | Design-time reference. | Current action descriptions; Phase2N04 tests | `Run`, `prepare`, `Create a job`, and unknown text absent from cards. |
| A04 | AI Actions | Same | Same | `checkType` | `OMIT` | Never render/filter. | No output. | No output. | Omit. | No operation claim. | `schemas.ts`; actions | Sentinel absent. |
| A05 | AI Actions | Same | Same | `readOnly` | `DERIVED_SAFE` | Fixed `Catalog property: read-only yes/no · execution unavailable`. | Missing -> `Unknown · execution unavailable`. | Always unavailable. | Boolean only. | Static catalog attribute, no authority. | `schemas.ts`; actions | Both booleans keep unavailable suffix. |
| A06 | AI Actions | Same | Same | `configChange` | `DERIVED_SAFE` | Fixed `Configuration-changing capability: unavailable`; boolean may select warning tone but not text/action. | Missing uses same unavailable copy. | Always unavailable. | Boolean only; no detail/control. | Never current capability. | `schemas.ts`; actions | No config action/control. |
| A07 | AI Actions | Same | Same | `riskLevel` | `DERIVED_SAFE` | Closed enum with `Catalog risk` qualifier. | Unknown -> `UNKNOWN`. | No operational authority. | Enum only. | Static design risk. | schemas/actions | Enum/unknown and qualifier. |
| A08 | AI Actions | Same | Same | `allowedVendors` | `OMIT` | Never render/count/filter; may imply live support. | No output. | No output. | Omit array. | No current device support claim. | schemas/actions | Vendor list absent. |
| A09 | AI Actions | Recorded recommendation | latest parse GET | `ParseResultRecord.id` | `OMIT` | Never render or link. | Null follows A28. | No output. | Omit arbitrary ID. | Internal historical identity. | schemas/store/API | ID sentinel absent. |
| A10 | AI Actions | Same | Same | `userRequest` | `PROHIBITED` | Never render, summarize, title, or accessible-name. | No output. | Request input unavailable. | Omit entire user-controlled text. | Historical input. | schemas/store; persistence test | User/secret/path/command sentinels absent. |
| A11 | AI Actions | Same | Same | `deviceInventoryHash` | `OMIT` | Never render or link. | No output. | Inventory unavailable. | Omit hash. | Historical correlation only. | schemas/store | Hash absent. |
| A12 | AI Actions | Same | Same | `deviceInventorySnapshot` | `PROHIBITED` | Never traverse or render. | No output. | Inventory/device access unavailable. | Omit object including host/IP/credentials. | Historical input, never current inventory. | schemas/store; workflow test | Nested identity/IP/secret sentinels absent. |
| A13 | AI Actions | Same | `ParseRequestOutput` | `intent` | `DERIVED_SAFE` | Closed schema enum mapped to fixed `Recorded intent category`; config/backup categories retain blocked/unavailable wording. | Unknown -> `UNKNOWN`. | No intent submission/execution. | Enum only. | Historical parser record. | `schemas.ts::networkIntents` | Every enum/unknown; no control. |
| A14 | AI Actions | Same | Same | `targetDevice` | `PROHIBITED` | Never render. | No target placeholder. | Device access unavailable. | Omit identity/IP/hostname. | Never current target. | schemas; workflow test | Target sentinel absent. |
| A15 | AI Actions | Same | Same | `vendor` | `OMIT` | Never render; avoid provider/device-support implication. | No output. | No output. | Omit. | Historical only. | schemas | Vendor absent. |
| A16 | AI Actions | Same | Same | `interfaceName` | `PROHIBITED` | Never render. | No output. | Configuration operations unavailable. | Omit device/config identifier. | Historical request detail. | schemas/readiness | Interface sentinel absent. |
| A17 | AI Actions | Same | Same | `vlanId` | `PROHIBITED` | Never render. | No output. | Configuration operations unavailable. | Omit. | Historical request detail. | schemas/readiness | VLAN sentinel absent. |
| A18 | AI Actions | Same | Same plus action catalog | `recommendedActionId` | `DERIVED_SAFE` | If exact A01 catalog match, render fixed catalog label prefixed `Recorded recommendation`; otherwise `Unknown catalog reference`. No link/button. | Null -> `No recorded recommendation`. | Execution/job creation unavailable. | Exact membership and fixed label only. | Historical recommendation. | schemas/actions/readiness tests | Known/unknown/null and no action control. |
| A19 | AI Actions | Same | Same | `missingFields` | `DERIVED_SAFE` | Map only exact schema field names to fixed reviewer labels; unknown names counted as `Other required information withheld` without raw text. | Empty -> `No recorded missing-field flags`. | No request form appears. | Closed field-name allowlist; no join of raw array. | Historical validation flags. | schemas/readiness | Known/unknown/user-text array sentinels. |
| A20 | AI Actions | Same | Same | `riskLevel` | `DERIVED_SAFE` | Closed enum prefixed `Recorded risk`. | Unknown. | No authority. | Enum only. | Historical record. | schemas | Enum/unknown. |
| A21 | AI Actions | Same | Same | `requiresApproval` | `DERIVED_SAFE` | Fixed `Recorded approval flag: yes/no`; no approval interaction. | Unknown. | Approval workflow unavailable. | Boolean only. | Historical flag. | schemas/readiness tests | Boolean/null; no button. |
| A22 | AI Actions | Same | Same | `blocked` | `DERIVED_SAFE` | Fixed `Recorded safety result: BLOCKED/NOT BLOCKED`; always append `non-executing`. | Unknown. | Current capability unavailable regardless. | Boolean only. | Historical result. | schemas/readiness | Boolean/null and qualifier. |
| A23 | AI Actions | Same | Same | `jobCreationAllowed` | `DERIVED_SAFE` | Fixed `Recorded eligibility: yes/no · job creation unavailable in Stage 0`. | Unknown/unavailable. | Always unavailable. | Boolean only. | Historical flag cannot authorize a job. | schemas/workflow tests | Both booleans, no Create Job. |
| A24 | AI Actions | Same | Same | `blockedReason` | `DERIVED_SAFE` | Map only exact repository constants (`DEVICE_READINESS_BLOCKED_REASON`, `BACKUP_CONFIG_BLOCKED_REASON`, `CONFIG_CHANGE_BLOCKED_REASON`) to fixed labels; other text -> `Recorded reason withheld`. | Null -> `No recorded reason`. | No remediation/action link. | Exact equality only. | Historical safety result. | `readiness.ts` | Known/unknown/secret/path reason sentinels. |
| A25 | AI Actions | Same | Same | `notes` | `PROHIBITED` | Never render or count. | No output. | Fixed Stage 0 note is supplied by component, not stored notes. | Omit array. | Historical provider/user-influenced text. | schemas/readiness | Notes sentinels absent. |
| A26 | AI Actions | Same | `ParseResultRecord` | `createdAt` | `DERIVED_SAFE` | UTC `YYYY-MM-DD` labeled `Recorded parse date`. | Unknown date. | Same. | Valid timestamp only. | Historical record. | schemas/store | Valid/invalid and qualifier. |
| A27 | AI Actions | Current `<pre>` | entire `parseResult.output` | raw serialized output | `PROHIBITED` | Remove raw JSON rendering. | No raw placeholder. | Fixed `Recorded detail withheld; parsing unavailable`. | Never stringify raw record. | Historical payload. | Current client; Stage 0 rules | Nested sentinels absent; no `<pre>` payload. |
| A28 | AI Actions | Panel state | latest parse GET | null/empty | `DERIVED_SAFE` | Null -> `No recorded parse result is available`; provider parsing remains unavailable. | Valid empty state. | `UNAVAILABLE`, not failed AI execution. | Fixed copy. | Current local record availability only. | API/store; persistence test | Empty state and no provider/control. |
| A29 | AI Actions | Client fetch state | latest parse GET | loading/error | `DERIVED_SAFE` | Loading uses status announcement; error uses fixed `Unable to read the recorded parse result.` | Settled null follows A28. | No provider retry/action. | Never render payload/error/traceback/URL. | UI read state only. | Current client/API | Loading announcement and raw-error sentinels absent. |
| A30 | AI Actions | Consumed record | parse-result store | provider/model names | `NOT_PRESENT` | Keep absent. Provider/model values returned by other runtime layers are not stored in `ParseResultRecord`. | No output. | Provider/model capability `UNAVAILABLE`. | Do not add source fields. | No current provider evidence. | schemas/store | Provider/model keys and names absent. |
| A31 | AI Actions | Consumed record | parse-result store | commands/arguments/secrets/tracebacks/raw payload | `PROHIBITED` | No independent source field is present and none may be introduced; occurrences inside A10/A12/A25 remain prohibited. | No output. | All operational capability unavailable. | Sentinel scan across nested input. | Never current. | schemas/API/readiness; secret/redaction tests | Command/argv/credential/token/traceback/payload sentinels absent. |

### 5.4 Jobs matrix

| ID | Surface | Route or component | Data source | Field path | Classification | Display rule | Null/empty rule | Unavailable-state rule | Sanitization rule | Historical/current rule | Evidence | Required test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J01 | Jobs | `/network/jobs`; `JobsClient` | `NetworkJob` from local store/GET | `id` | `DERIVED_SAFE` | Display only exact `job_` plus UUID form, bounded, with `Recorded job ID` label; invalid -> `Identifier withheld`. | Missing -> reject row as malformed. | No detail/run link. | Strict regex, never raw fallback. | Historical record identity. | schemas/jobs store | Valid/invalid/path/secret IDs. |
| J02 | Jobs | Same | Same plus action catalog | `actionId` | `DERIVED_SAFE` | Exact catalog membership -> fixed label; unknown -> `Unknown catalog reference`. No control/link. | Missing -> malformed row. | Action unavailable. | Exact allowlist only. | Historical catalog reference. | schemas/actions/jobs | Known/unknown and no action. |
| J03 | Jobs | Same | Same | `targetDevice` | `PROHIBITED` | Never render/filter/title. | No target placeholder. | Device access unavailable. | Omit identity, host, IP. | Never current target. | schemas/workflow test | Identity/IP sentinel absent. |
| J04 | Jobs | Same | Same | `vendor` | `DERIVED_SAFE` | Map exact `mikrotik`, `cisco`, or `unknown` to fixed `Recorded device platform`; never call it provider/support. | Missing -> `Unknown`. | No device connection/support implication. | Closed enum only. | Historical record. | schemas/jobs | Enum/unknown and qualifier. |
| J05 | Jobs | Same | Same | `params` | `PROHIBITED` | Never traverse/render/count/filter. | No output. | Commands/config/device data unavailable. | Omit whole object including command, scriptPath, interface, VLAN, inventory, source, secrets, credentials. | Historical input. | schemas/jobs/create API | Nested forbidden sentinels absent. |
| J06 | Jobs | Same | Same | `status` | `DERIVED_SAFE` | Map `ready` -> `RECORDED / NEVER EXECUTED`; `pending_approval` -> `RECORDED / APPROVAL UNAVAILABLE`; `blocked` -> `RECORDED / BLOCKED`; else `REJECTED`. | Missing -> malformed row. | Runner/worker/queue unavailable. | Closed enum only; never render raw `ready`. | Recorded readiness, not active execution. | schemas/readiness tests | All enum/unknown; no running/queued/success implication. |
| J07 | Jobs | Same | Same | `blockedReason` | `DERIVED_SAFE` | Same exact constant mapping as A24 plus fixed `Unknown action`/`Missing target`; unknown -> `Recorded reason withheld`. | Null -> `No recorded reason`. | No remediation/action. | Exact equality only. | Historical safety result. | readiness/jobs | Known/unknown/secret/path sentinels. |
| J08 | Jobs | Same | Same | `riskLevel` | `DERIVED_SAFE` | Closed enum prefixed `Recorded risk`. | Unknown. | No authority. | Enum only. | Historical record. | schemas/jobs | Enum/unknown. |
| J09 | Jobs | Same | Same | `requiresApproval` | `DERIVED_SAFE` | Fixed `Recorded approval flag: yes/no`; no approval interaction. | Unknown. | Approval workflow unavailable. | Boolean only. | Historical flag. | schemas/readiness | Boolean/null; no control. |
| J10 | Jobs | Same | Same | `readOnly` | `DERIVED_SAFE` | Fixed `Recorded catalog property: read-only yes/no · execution unavailable`. | Unknown/unavailable. | Always unavailable. | Boolean only. | Historical property, no authority. | schemas/actions/jobs | Both booleans and qualifier. |
| J11 | Jobs | Same | Same | `source` | `OMIT` | Never render; it is sourced from unrestricted params text. | No output. | No output. | Omit. | Historical user-controlled metadata. | jobs::stringParam; workflow test | Source sentinel absent. |
| J12 | Jobs | Same | Same | `parseResultId` | `OMIT` | Never render/link. | No output. | No output. | Omit arbitrary identifier. | Internal correlation only. | schemas/jobs | Sentinel absent. |
| J13 | Jobs | Same | Same | `createdAt` | `DERIVED_SAFE` | UTC `YYYY-MM-DD` labeled `Recorded`. | Unknown date. | Same. | Valid timestamp only. | Historical record date. | schemas/jobs | Valid/invalid. |
| J14 | Jobs | Collection | `NetworkJob[]` | `jobs.length` | `DERIVED_SAFE` | Integer `recorded jobs` count after safe projection. | Zero -> `EMPTY — no recorded jobs in this local store`. | Runner remains unavailable. | Exclude malformed/rejected rows and disclose rejected count only as aggregate. | Local recorded count, not active queue size. | empty `jobs.json`; current client | 0/1/many/malformed. |
| J15 | Jobs | Existing refresh | GET `/api/network/jobs` | loading/refresh | `DERIVED_SAFE` | Retain GET-only reload, relabel `Reload recorded jobs`; loading announced and button disabled. | Empty follows J14. | No scheduler/worker/runner inference. | Never POST or call create/run route. | Current local record read only. | current client/API; Phase1 UI test | GET-only source assertion, keyboard/focus, no POST/create/run. |
| J16 | Jobs | Client fetch | Same | error | `DERIVED_SAFE` | Fixed `Unable to read recorded jobs.` | Existing safe rows may remain with an explicit stale-local-record note. | No device/provider retry. | Never render response payload, raw error, traceback, URL, path, or identifiers. | UI read failure only. | current client/API | Raw error/traceback sentinels absent. |
| J17 | Jobs | Consumed schema | `NetworkJob` | commands/arguments/credentials/secrets | `PROHIBITED` | Never display; J05 covers nested params. | No output. | Command/config operations unavailable. | Sentinel scan whole record before projection. | Never current. | create API rejects command/scriptPath; secret tests | command/argv/token/password/key sentinels absent. |
| J18 | Jobs | Consumed schema | `NetworkJob` | IP addresses/hostnames/device identifiers | `PROHIBITED` | Never display or derive; J03/J05 cover sources. | No output. | Device access unavailable. | Whole-value omission; no partial host/address mask. | Never current target/health. | schemas/jobs; workflow fixtures | IPv4/IPv6/hostname/device sentinels absent. |
| J19 | Jobs | Consumed schema | `NetworkJob` | queue/worker/scheduler/runner state | `NOT_PRESENT` | Keep absent; status is not queue/execution state. | No output. | Fixed `Runner, queue, scheduler, and worker unavailable in Stage 0`. | Do not add polling or derived active state. | No active execution exists. | schemas; current no-Run tests | No running/queued/worker/scheduler/runner-enabled copy or controls. |
| J20 | Jobs | Route/component | current source | links/detail routes | `NOT_PRESENT` | No job detail/run/approval link or new route. | Empty stays on page. | No external/device destination. | Keep absent. | Display-only list. | current routes/navigation | No new href/route/button. |
| J21 | Jobs | Projection boundary | unvalidated JSON store cast | malformed/unknown record shape | `DERIVED_SAFE` | Reject row before rendering and show aggregate `N recorded rows withheld as malformed`; never expose raw detail. | All rejected -> `ERROR — no safely displayable recorded jobs`. | No repair/write/execute action. | Pure presentation validator in the future helper; no store/schema change. | Local file content only. | jobs readStore currently casts array | Missing/type/extra/forbidden sentinels; source store unchanged. |

### 5.5 Required information-class coverage and explicit absence

`NOT_PRESENT` below means the current consumed source has no such independent
field. It does not authorize adding one.

| Information class | Evidence | Reports | AI Actions | Jobs |
| --- | --- | --- | --- | --- |
| Identifiers | E01 internal only; E19/E20 omitted | R01 omitted | A01 static safe; A09 omitted | J01 validated; J02 allowlisted |
| Timestamps | E13/E40 recorded dates | R12 recorded date | A26 recorded date | J13 recorded date |
| Status values | E09/E34-E38/E41 fixed recorded/read states | R09/R16 normalized/read states | A20-A24/A28-A29 fixed recorded/unavailable states | J06-J10/J14-J16 fixed recorded/read states |
| Summary text | E28-E31 omitted | `NOT_PRESENT`; no arbitrary summary field | A03 fixed ID mapping only; A10/A25 prohibited | `NOT_PRESENT`; no summary field |
| Counts | E15 | R14 | Static catalog count may use A01-approved rows only; recorded parse count is `NOT_PRESENT` | J14 |
| Artifact types | E04 | R04 | `NOT_PRESENT` | `NOT_PRESENT` |
| Report categories | E04 | R04 | `NOT_PRESENT` | `NOT_PRESENT` |
| Safe filenames | E14 prohibits filename derivation | R13 prohibits filename/path | `NOT_PRESENT` | `NOT_PRESENT` |
| Private or absolute paths | E10/E14 prohibited | R10/R13 prohibited | A10/A12/A25/A31 prohibited | J05/J11/J17 prohibited |
| Provider names | E25 prohibited; nested payloads E10/E11/E28-E33 prohibited | R10/R11 prohibited | A30 `NOT_PRESENT` and must remain absent | `NOT_PRESENT`; params prohibited by J05 |
| Model names | E25 prohibited | R10/R11 prohibited | A30 `NOT_PRESENT` and must remain absent | `NOT_PRESENT`; params prohibited |
| Commands | E10/E32/E33 prohibited | R10/R11 prohibited | A03 action-shaped text replaced; A31 prohibited | J05/J17 prohibited |
| Arguments | E10/E11 prohibited | R10/R11 prohibited | A10/A12/A25/A31 prohibited | J05/J17 prohibited |
| Device identifiers | E05/E23 prohibited | R05 prohibited | A12/A14/A16 prohibited | J03/J18 prohibited |
| IP addresses | E10/E11/E14/E23 prohibited | R10/R11/R13 prohibited | A12/A14/A31 prohibited | J03/J05/J18 prohibited |
| Hostnames | E05/E10/E11/E23 prohibited | R05/R10/R11 prohibited | A12/A14/A31 prohibited | J03/J05/J18 prohibited |
| User-controlled text | E06/E08/E10/E11/E28-E33/E39 omitted/prohibited | R06/R08/R10/R11 prohibited | A10/A19 unknowns/A24 unknowns/A25/A31 prohibited | J05/J07 unknowns/J11/J17 prohibited |
| Error messages | E41 fixed only | R16 framework/fixed only | A29 fixed only | J16 fixed only |
| Tracebacks | E10/E41 prohibited | R10/R16 prohibited | A29/A31 prohibited | J16/J17 prohibited |
| Raw payloads | E10/E11/E28-E33 prohibited | R10/R11 prohibited | A12/A25/A27/A31 prohibited | J05/J17 prohibited |
| Secrets or credentials | E10/E11/E14/E28-E33 prohibited | R10/R11/R13 prohibited | A10/A12/A25/A31 prohibited | J05/J17 prohibited |
| Job execution state | E17 prohibited; E38 historical flag only | `NOT_PRESENT` | A23 historical eligibility only | J06/J19 recorded readiness, never execution |
| Recorded versus live status | Every E row must use `Recorded` or read-state wording | Every result/date is recorded artifact evidence | Every parse/catalog value is static or recorded; provider capability unavailable | Every job value is recorded; runner/queue/worker unavailable |
| Unavailable or unsupported state | E18/E38/E41 | R15/R16 | A28-A31 | J14-J21 |

## 6. State, redaction, and UX contracts

| State | Controlling behavior for all applicable surfaces |
| --- | --- |
| Normal recorded data | Present only safely projected fields, lead with `Recorded`, `Static catalog`, or `Local artifact`, and keep Stage 0 unavailable copy before action-shaped history. |
| Valid empty | Use `EMPTY`; describe a valid zero-item collection. Reports retains its exact HTTP-200 empty-state meaning. Jobs uses an empty local store. AI Actions uses no recorded parse result. |
| Missing artifact | Use `MISSING` only when the current source supplies a distinct missing signal. Because `importDayResults()` maps absent directories to `[]`, Evidence and Reports must not infer `MISSING` from zero items. |
| Malformed or rejected | Use fixed `REJECTED`/`ERROR` copy, omit raw detail, preserve the source unchanged, and expose no repair/run/retry action beyond an existing local GET reload. |
| Unsupported Stage 0 | Use `UNAVAILABLE`; provider parsing/analysis, job creation/execution, commands, approval workflows, live/device access, and configuration work remain absent. |
| Loading | Only existing client GET reads may show loading. Use a status announcement, do not suggest provider/device progress, and retain the last safe projection where appropriate. |
| Error | Use fixed surface-specific error copy. Never show raw errors, response bodies, URLs, stack traces, paths, identifiers, or provider/device language. |
| Narrow layout | Use a single-column summary-first flow. Replace the ARIA-div job table with native table semantics plus either labeled card reflow or keyboard-focusable horizontal scrolling; do not silently drop approved fields. |
| Keyboard and focus | Preserve the shell skip link. Evidence selection, any filter/reset, native disclosures, the Jobs GET reload, and scroll containers must be reachable, named, operable, and visibly focused without traps. |
| Non-color status | Every status/risk/availability value has text; color is supplemental. Selected state includes non-color text/semantics. |
| Reflow/zoom | Review at 320, 768, and 1440 CSS px. Supply native 400% zoom evidence when the available browser supports it; otherwise record the unavailable mechanism and provide equivalent narrow reflow evidence without falsely calling a 320 px viewport native zoom. |

Sanitization is fail-closed. The future pure presentation helper validates the
allowlisted fields above and returns only fixed projections. It must not import
or call Flask helpers, mutate source records, write stores, add schemas, or
silently preserve unknown fields. Omission is preferred to partial masking for
paths, identities, provider/model fields, commands, arguments, payloads, and
secrets.

## 7. Exact future Phase 2O-05 implementation boundary

This section defines one future boundary; it does not authorize it now.

```text
AUTHORIZED_EXISTING_ROUTES:
- /network/day-results
- /network/reports
- /network/ai-actions
- /network/jobs

NEW_ROUTE_PATHS:
NONE

AUTHORIZED_EXISTING_COMPONENTS:
- components/network/DayResultsClient.tsx
- components/network/ReportsClient.tsx
- components/network/AiActionsClient.tsx
- components/network/JobsClient.tsx
- components/network/Phase2N04DemoPresentation.ts

AUTHORIZED_EXISTING_TEST_FILES:
- components/network/ReportsClient.test.tsx
- components/network/Phase2N04SafetyLabels.test.ts
- tests/test_network_phase1_ui_presentation.py

AUTHORIZED_NEW_PRESENTATION_HELPER:
- components/network/Phase2O05SafePresentation.ts

AUTHORIZED_REQUIRED_NEW_TEST_FILES:
- components/network/Phase2O05SafePresentation.test.ts

AUTHORIZED_DOCUMENTATION_FILES:
- README.md
- docs/phase_2o/phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md
- docs/phase_2o/phase_2o_05_secondary_nextjs_evidence_reports_ai_actions_and_jobs_visualization_implementation.md

EXPECTED_CHANGED_FILE_COUNT:
14
```

The exact future changed-file list is:

1. `app/globals.css`
2. `components/network/DayResultsClient.tsx`
3. `components/network/ReportsClient.tsx`
4. `components/network/AiActionsClient.tsx`
5. `components/network/JobsClient.tsx`
6. `components/network/Phase2N04DemoPresentation.ts`
7. `components/network/Phase2O05SafePresentation.ts` — new, pure
   presentation-only allowlist/normalization helper
8. `components/network/ReportsClient.test.tsx`
9. `components/network/Phase2N04SafetyLabels.test.ts`
10. `components/network/Phase2O05SafePresentation.test.ts` — new
11. `tests/test_network_phase1_ui_presentation.py`
12. `README.md`
13. `docs/phase_2o/phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md`
14. `docs/phase_2o/phase_2o_05_secondary_nextjs_evidence_reports_ai_actions_and_jobs_visualization_implementation.md` — new

All 14 paths above are mandatory for the future implementation. File 10,
`components/network/Phase2O05SafePresentation.test.ts`, is required rather than
optional or implementation-dependent. An implementation that changes only 13
of the listed files fails scope validation, as does omission of any other listed
file. A fifteenth changed file is not authorized.

The four existing route pages, shared layout, navigation, all `lib/network-ai/**`
files, all API routes, stores, schemas, importers, packages, lockfiles, and data
files are reference-only and must remain byte-for-byte unchanged. If a future
implementation requires a fifteenth file, a page change, a new source field, or
an importer/API/schema/store change, it must stop with a new scope decision
instead of expanding this list.

## 8. Explicit exclusions and dependency gate

The future boundary explicitly prohibits:

- new or changed route paths, HTTP methods, API routes, importers, schemas,
  stores, persistence, fixtures, generated artifacts, or data sources;
- `package.json`, lockfile, dependency, configuration, or workflow changes;
- provider, API, or model calls and any provider/model identity display;
- secrets or credentials handling;
- Analyze, Parse, Create Job, Run Job, approval, command, or submission controls;
- command/argument execution, SSH, NETCONF, RESTCONF, live-device access,
  discovery, polling, configuration backup/change, or production execution;
- queue, scheduler, broker, worker, runner, autonomous loop, or AI agent loop;
- raw output, raw JSON, paths, device identity, IP addresses, hostnames,
  unrestricted user text, raw errors, or tracebacks;
- topology, older `/ai` or `/automation/ai-nodes` workbenches, canonical Flask
  changes, unrelated UI redesign, Phase 2O-06, Phase 2O-07, or Phase 2P;
- Day 1–Day 160 replacement and creation of a second safety matrix.

```text
DEPENDENCY_CHANGE_REQUIRED:
NO

DEPENDENCY_BASIS:
Existing React, Next.js, CSS, Vitest, TypeScript, ESLint, and browser-review
capabilities are sufficient. Native summaries, definition lists, tables,
disclosures, and CSS provide the planned visualization.
```

If a future task concludes that any package or lockfile change is necessary, it
must stop before editing and obtain a separate dependency-decision task. It must
not install or select a package under this plan.

## 9. Required future implementation validation

### 9.1 Automated validation

Run exactly the applicable repository commands, including:

```text
npm run test:unit -- components/network/Phase2O05SafePresentation.test.ts components/network/ReportsClient.test.tsx components/network/Phase2N04SafetyLabels.test.ts components/network/Phase2O04NetworkShell.test.ts
npm run test:unit
npm run typecheck
npm run lint
npm run build
python -m pytest tests/test_network_phase1_ui_presentation.py tests/test_network_day_result_normalization.py tests/test_network_ai_analysis_persistence.py tests/test_network_ai_workflow_persistence.py tests/test_network_ai_action_recommendation_safety.py
python -m pytest
python network_lab.py --task report-index
git diff --check
```

### 9.2 Deterministic exact changed-file scope validation

This validation has two mandatory stages. Stage A binds the future implementation
to the exact authorization-supplied starting commit before any implementation
file is edited, generated, staged, or committed. Stage B validates the resulting
commit against that same preserved commit and tree identity. Merely resolving a
supplied SHA as a valid commit is insufficient.

The stable sequence is: authorization supplies exact base `B`; implementation
starts only when `HEAD == B`; the task preserves `B` and `B^{tree}`;
implementation creates result `H`; final validation verifies that literal `B`
is an ancestor of `H`; final validation compares literal `B` directly with `H`;
and the task reports `H` for independent review. The future result SHA is not a
prerequisite and must not be inserted into this plan before it exists.

Run each Git command below as a separate, independent tool call. Do not batch,
chain, pipe, wrap, alias, or combine them. Preserve each required stdout value
verbatim as task-local execution evidence and include the resolved base commit,
base tree, and result commit in the final structured implementation report. Do
not create a repository file solely to store these values.

#### Stage A — mandatory pre-implementation base binding

The fresh Phase 2O continuation-authorization decision must supply one explicit
full starting commit SHA as `AUTHORIZED_IMPLEMENTATION_BASE_INPUT`. Before any
implementation modification, resolve and preserve it as
`AUTHORIZED_IMPLEMENTATION_BASE_COMMIT`, resolve and preserve its exact tree as
`AUTHORIZED_IMPLEMENTATION_BASE_TREE`, and obtain
`ACTUAL_PRE_IMPLEMENTATION_HEAD` from `HEAD^{commit}`:

```powershell
$AuthorizedBaseInput = "<AUTHORIZATION_SUPPLIED_SHA>"

if ($AuthorizedBaseInput -cnotmatch '^[0-9a-fA-F]{40}$') {
    throw "Authorized implementation base must be one full commit SHA."
}

$AuthorizedBaseCommit = (
    git rev-parse --verify "$AuthorizedBaseInput^{commit}"
).Trim()

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AuthorizedBaseCommit)) {
    throw "Authorized implementation base is not a valid commit: $AuthorizedBaseInput"
}

$ActualPreImplementationHead = (
    git rev-parse --verify "HEAD^{commit}"
).Trim()

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ActualPreImplementationHead)) {
    throw "Unable to resolve the pre-implementation HEAD."
}

if ($ActualPreImplementationHead -cne $AuthorizedBaseCommit) {
    throw @"
Incorrect implementation starting HEAD.
Authorized: $AuthorizedBaseCommit
Actual:     $ActualPreImplementationHead
"@
}

$AuthorizedBaseTree = (
    git rev-parse --verify "$AuthorizedBaseCommit^{tree}"
).Trim()

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AuthorizedBaseTree)) {
    throw "Unable to resolve the authorized implementation base tree."
}
```

Any mismatch is an immediate stop condition; no implementation is permitted
after it. The authorization-supplied base must not be replaced by a merge base,
current `main`, `origin/main`, a parent approximation, branch or tag name,
remote-tracking ref, sibling, ancestor, descendant, or another valid commit.
Such a ref or commit is acceptable only when its fully resolved commit equals
the exact authorization-supplied SHA and the actual starting `HEAD` equals that
same commit.

#### Stage B — mandatory post-implementation exact-tree validation

Only after the implementation result commit exists, resolve and preserve
`IMPLEMENTATION_RESULT_HEAD`:

```powershell
$ImplementationResultHead = (
    git rev-parse --verify "HEAD^{commit}"
).Trim()

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ImplementationResultHead)) {
    throw "Unable to resolve the implementation result HEAD."
}
```

Verify that the exact preserved authorized base is an ancestor of that result:

```powershell
git merge-base --is-ancestor `
    $AuthorizedBaseCommit `
    $ImplementationResultHead

if ($LASTEXITCODE -ne 0) {
    throw "The exact authorized implementation base is not an ancestor of the result HEAD."
}
```

Re-resolve the preserved base tree and require the same tree identity. Git
commit and tree objects are immutable, but this check proves final validation
did not silently substitute a different valid base:

```powershell
$RecheckedAuthorizedBaseTree = (
    git rev-parse --verify "$AuthorizedBaseCommit^{tree}"
).Trim()

if ($LASTEXITCODE -ne 0 -or $RecheckedAuthorizedBaseTree -cne $AuthorizedBaseTree) {
    throw "Authorized implementation base tree evidence does not match."
}
```

Capture the complete tracked change status by comparing the literal preserved
base commit directly with the result commit. The authoritative command consumes
the preserved variables directly and has no caller-supplied base or result
parameter:

```powershell
$AuthoritativeNameStatus = @(
    git diff --name-status --no-renames --diff-filter=ACDMRTUXB `
        $AuthorizedBaseCommit `
        $ImplementationResultHead `
        --
)

if ($LASTEXITCODE -ne 0) {
    throw "Unable to compare the exact authorized base with the implementation result."
}
```

Preserve this command's stdout verbatim as
`BOUND_AUTHORITATIVE_NAME_STATUS_STDOUT`. Exact path validation below may
consume only that captured output; it must not run or accept a second
independently parameterized name-status comparison.

Capture all untracked, non-ignored paths in a second independent call:

```text
git ls-files --others --exclude-standard --
```

Capture any staged or unstaged tracked worktree entry in a third independent
call:

```text
git status --porcelain --untracked-files=no
```

Run the whitespace/error check independently against the same two literal
commits, again using the preserved variables directly:

```powershell
git diff --check `
    $AuthorizedBaseCommit `
    $ImplementationResultHead `
    --

if ($LASTEXITCODE -ne 0) {
    throw "git diff --check failed for the exact authorized base-to-result range."
}
```

The name-status and diff-check commands consume the same preserved
`$AuthorizedBaseCommit` and `$ImplementationResultHead` variables. Callers may
not provide alternative Stage B base or result parameters. A branch, tag,
`main`, `origin/main`, raw SHA argument, merge base, same-tree sibling, ancestor,
descendant, or other commit must not replace either preserved variable.
`$AuthorizedBaseCommit` originates only from the authorization-supplied base
validated before implementation, and `$ImplementationResultHead` originates
only from the actual resulting `HEAD^{commit}`. Stage B must not re-read or
accept a second independently supplied base or result value, and neither
preserved variable may be reassigned before final validation.

The authoritative changed-file calculation therefore uses the literal
preserved commit pair directly. It must not use `git diff <base>...<head>`, a
separately calculated merge base, `git diff <branch-name>...HEAD`, or
`git diff origin/main...HEAD`. Three-dot diff uses the merge base, which can
differ from the literal supplied base. A wrong sibling commit can therefore
produce the same changed-path set and pass path-only validation unless Stage A
first binds `HEAD` exactly and Stage B consumes only the preserved identities.

Then run the following non-Git PowerShell comparison in its own tool call.
Replace the three stdout placeholders verbatim with the captured output from
the bound Stage B name-status command, untracked command, and worktree command.
The first placeholder must contain only `BOUND_AUTHORITATIVE_NAME_STATUS_STDOUT`;
no output from another base/result comparison is permitted. Preserve tabs in
the name-status output. Empty command output
must replace its placeholder with an empty here-string; it must not be replaced
with explanatory text.

```powershell
$trackedNameStatusText = @'
<EXACT_BOUND_AUTHORITATIVE_NAME_STATUS_STDOUT>
'@
$untrackedText = @'
<EXACT_STDOUT_FROM_UNTRACKED_PATHS>
'@
$trackedWorktreeText = @'
<EXACT_STDOUT_FROM_TRACKED_WORKTREE_STATUS>
'@

[string[]]$expectedPaths = @(
    "app/globals.css"
    "components/network/DayResultsClient.tsx"
    "components/network/ReportsClient.tsx"
    "components/network/AiActionsClient.tsx"
    "components/network/JobsClient.tsx"
    "components/network/Phase2N04DemoPresentation.ts"
    "components/network/Phase2O05SafePresentation.ts"
    "components/network/ReportsClient.test.tsx"
    "components/network/Phase2N04SafetyLabels.test.ts"
    "components/network/Phase2O05SafePresentation.test.ts"
    "tests/test_network_phase1_ui_presentation.py"
    "README.md"
    "docs/phase_2o/phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md"
    "docs/phase_2o/phase_2o_05_secondary_nextjs_evidence_reports_ai_actions_and_jobs_visualization_implementation.md"
)

function Convert-CapturedLines([string]$text) {
    return [string[]]@(
        $text -split "`r?`n" |
            ForEach-Object { $_.TrimEnd() } |
            Where-Object { $_ }
    )
}

function Normalize-GitPath([string]$path) {
    return $path.Trim().Replace("\", "/")
}

$actualTrackedList = [System.Collections.Generic.List[string]]::new()
$deletedEntries = [System.Collections.Generic.List[string]]::new()
$renamedOrCopiedEntries = [System.Collections.Generic.List[string]]::new()
$unexpectedStatusEntries = [System.Collections.Generic.List[string]]::new()

foreach ($entry in (Convert-CapturedLines $trackedNameStatusText)) {
    [string[]]$parts = $entry -split "`t"
    $status = $parts[0]
    if ($status -match '^[AM]$' -and $parts.Count -eq 2) {
        $actualTrackedList.Add((Normalize-GitPath $parts[1]))
    } elseif ($status -eq 'D') {
        $deletedEntries.Add($entry)
    } elseif ($status -match '^[RC][0-9]{0,3}$') {
        $renamedOrCopiedEntries.Add($entry)
    } else {
        $unexpectedStatusEntries.Add($entry)
    }
}

[string[]]$actualTracked = $actualTrackedList.ToArray()
[string[]]$untrackedPaths = @(
    Convert-CapturedLines $untrackedText | ForEach-Object { Normalize-GitPath $_ }
)
[string[]]$trackedWorktreeEntries = @(Convert-CapturedLines $trackedWorktreeText)

[Array]::Sort($expectedPaths, [StringComparer]::Ordinal)
[Array]::Sort($actualTracked, [StringComparer]::Ordinal)
[Array]::Sort($untrackedPaths, [StringComparer]::Ordinal)

[string[]]$missingPaths = @(
    $expectedPaths | Where-Object { $actualTracked -cnotcontains $_ }
)
[string[]]$unexpectedPaths = @(
    $actualTracked | Where-Object { $expectedPaths -cnotcontains $_ }
)
[string[]]$expectedUntrackedPaths = @(
    $untrackedPaths | Where-Object { $expectedPaths -ccontains $_ }
)
[string[]]$unexpectedUntrackedPaths = @(
    $untrackedPaths | Where-Object { $expectedPaths -cnotcontains $_ }
)

Write-Output "Expected tracked count: 14"
Write-Output "Actual tracked count: $($actualTracked.Count)"
Write-Output "Missing paths: $($missingPaths -join ', ')"
Write-Output "Unexpected paths: $($unexpectedPaths -join ', ')"
Write-Output "Deleted entries: $($deletedEntries -join ', ')"
Write-Output "Renamed/copied entries: $($renamedOrCopiedEntries -join ', ')"
Write-Output "Unexpected status entries: $($unexpectedStatusEntries -join ', ')"
Write-Output "Expected-scope untracked paths: $($expectedUntrackedPaths -join ', ')"
Write-Output "Outside-scope untracked paths: $($unexpectedUntrackedPaths -join ', ')"
Write-Output "Uncommitted tracked worktree entries: $($trackedWorktreeEntries -join ', ')"

$scopeFailed =
    $expectedPaths.Count -ne 14 -or
    $actualTracked.Count -ne 14 -or
    $missingPaths.Count -ne 0 -or
    $unexpectedPaths.Count -ne 0 -or
    $deletedEntries.Count -ne 0 -or
    $renamedOrCopiedEntries.Count -ne 0 -or
    $unexpectedStatusEntries.Count -ne 0 -or
    $expectedUntrackedPaths.Count -ne 0 -or
    $unexpectedUntrackedPaths.Count -ne 0 -or
    $trackedWorktreeEntries.Count -ne 0

if ($scopeFailed) {
    Write-Error "Phase 2O-05 exact 14-file implementation scope validation failed."
    exit 1
}

Write-Output "PASS: resulting HEAD changes exactly the required 14 paths."
```

This contract compares both count and case-sensitive normalized path contents.
Missing, extra, deleted, renamed, copied, untracked, or uncommitted tracked
paths make the comparison return non-zero. Any untracked path fails whether it
falls inside the expected list or outside it. The commands use only local Git
state and must not fetch or contact a remote.

`git diff --check` remains a separate whitespace/error check. It supplies no
changed-file scope evidence and cannot replace the deterministic validation
above.

The existing Stage A cases remain mandatory: exact `HEAD == B` passes; invalid
base input fails; any valid `W != B`, including a sibling or descendant of a
sibling, fails; branch, tag, `main`, and `origin/main` substitutions fail; and a
result not descended from `B` fails the exact-base ancestry check.

Required Stage B identity-binding validation and review evidence must also
cover all of these cases:

1. A different valid commit used as the diff base is rejected because the
   command accepts no base argument other than `$AuthorizedBaseCommit`.
2. A sibling commit used as the diff base is rejected.
3. A same-tree sibling used as the diff base is rejected even when it would
   produce the same changed-path set as the preserved base.
4. A branch or tag cannot replace `$AuthorizedBaseCommit`.
5. `main` or `origin/main` cannot replace `$AuthorizedBaseCommit`.
6. A different result commit cannot replace `$ImplementationResultHead`.
7. An independently supplied Stage B SHA that differs from either preserved
   value is rejected; Stage B accepts no such parameter.
8. A correct count or exact path set cannot rescue a command whose commit
   identity is wrong.
9. If ancestry and tree checks pass for preserved `B` and `H`, a command that
   attempts to diff `W` against `H` still fails because the authoritative
   command itself invokes `$AuthorizedBaseCommit` and `$ImplementationResultHead`
   directly and exposes no independently replaceable base argument.
10. A command that uses preserved `B` with an unpreserved substitute result
    fails because the authoritative command exposes no independently replaceable
    result argument and must use `$ImplementationResultHead` directly.

Exact path-set equality, a count of 14, or an equivalent three-dot path diff
cannot rescue any wrong-base or wrong-result identity case.

The targeted safe-presentation tests must connect every matrix classification
to evidence:

- all `SAFE_DISPLAY`/`DERIVED_SAFE` rows: valid, null, malformed, unknown, and
  boundary values with exact fixed output;
- all `OMIT`/`PROHIBITED` rows: unique nested sentinels for paths, filenames,
  identities, IP/host values, provider/model names, commands, arguments,
  configuration, user text, raw payload, secrets, credentials, error messages,
  and tracebacks;
- every status and date: closed normalization, recorded qualifier, non-color
  label, invalid fallback, and no live/current implication;
- Reports: exact HTTP-200 zero-data copy, no `notFound()`, no identifier/title/
  path/raw/device/provider/action leakage;
- AI Actions: static-catalog ID allowlist, fixed safe copy, parse-record null/
  loading/error states, and absence of request/Parse/Create Job controls;
- Jobs: validated ID, allowlisted action, recorded-only status mapping, malformed
  record rejection, GET-only reload, and absence of Run/approval/queue/worker/
  scheduler/target/params detail;
- immutability: projection helpers do not mutate the source objects and no
  importer/store/API/provider/device function is invoked by rejected inputs.

### 9.3 Rendered browser review

Review all four routes with normal recorded data and the applicable synthetic or
task-owned non-destructive empty, malformed/rejected, loading, error, and
unavailable variants. Do not delete or alter user artifacts to create a state.

Required evidence:

1. widths 320, 768, and 1440 CSS px;
2. native 400% zoom where available, or explicitly limited equivalent reflow
   evidence as defined in Section 6;
3. keyboard entry, shared skip link, navigation, Evidence selection/filter,
   disclosures, Jobs GET reload, scrollable regions, focus order, and return path;
4. visible focus, ordered headings, one route `<main>`/`<h1>`, native table or
   labeled reflow semantics, status announcements, and non-color meaning;
5. no page-level horizontal overflow except a deliberately keyboard-focusable
   genuine data table/raw-free region;
6. no Analyze, Parse, Create Job, Run Job, approval, command, submission,
   provider, model, queue, worker, scheduler, runner, or live-device control;
7. no raw/private sentinel, framework overlay, or browser console warning/error.

## 10. Planning completeness and future acceptance gates

This prerequisite plan is complete only when independent review confirms:

- all four surfaces and every current consumed field are classified;
- the class-coverage table contains no silent absence or catch-all field;
- every safe projection cites a concrete schema, source, test, artifact, or
  accepted contract;
- every arbitrary text/object/path/provider/model/device/command/secret/error
  class is omitted or prohibited;
- the HTTP-200 Reports empty-state contract is unchanged;
- the exact 14-file future boundary is sufficient and no unauthorized source
  behavior is required;
- dependency change remains `NO`;
- state, keyboard, focus, responsive, reflow/zoom, safe-field, sanitization, and
  Stage 0 negative evidence are all required;
- no implementation has occurred.

Independent planning review `PASS` is prerequisite evidence only. It does not
authorize Phase 2O-05 implementation. A fresh continuation-authorization
decision must separately decide whether the exact 14-file boundary may proceed.

## 11. Stable non-recursive external-review handoff

This planning commit uses a stable self-reference because a commit cannot
contain its own final SHA or authoritatively claim its own later review result:

```text
PHASE_2O_05_PREREQUISITE_PLANNING_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_PREREQUISITE_PLANNING_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_REVIEW_TARGET

CURRENT_HANDOFF:
CONDITIONAL_EXTERNAL_REVIEW_GATE
```

If the exact Phase 2O-05 prerequisite-planning commit has not received an
independent `PASS` review, the sole next action is independent review of that
exact commit.

If that exact commit has received an independent `PASS` review and the result
remains unsuperseded, the sole next action is a fresh Phase 2O continuation-
authorization decision for the exact Phase 2O-05 candidate and exact boundary.

No additional documentation-only commit is required solely to make the reviewed
planning commit self-record its own later `PASS` result. The external task
result and exact commit identity are authoritative. Neither branch of this gate
authorizes implementation, merge, push, remote contact, cleanup, Phase 2O-06,
Phase 2O-07, Phase 2P, or any live/production capability.

## 12. Documentation readability review

- The conclusion and status appear first.
- Purpose, allowed planning work, exact future boundary, and forbidden scope are
  separated.
- The four component matrices use one vocabulary and cite concrete repository
  evidence.
- Recorded state, availability, result quality, and current capability are not
  conflated.
- Every long requirement is grouped into named sections and tables.
- Acceptance criteria and validation commands are concrete and verifiable.
- Stage 0, canonical Flask/secondary Next.js responsibility, and the exact
  Phase 2O sequence remain unchanged.
- No implementation, behavior, runtime, authorization, or second safety matrix
  is introduced by this document.
