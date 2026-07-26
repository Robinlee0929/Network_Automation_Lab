# Phase 2O-00 UX/UI Baseline and Information Architecture — Planning Only

## 1. Status and decision

**Decision:** Phase 2O-00 planning is complete. Planning commit
`99b1929b6efd0af07ed3bbe634d7e7108867618f` received independent documentation
review `PASS` and was integrated into `main` by strict fast-forward. The evidence
supports a seven-slice Phase 2O sequence that keeps the Flask dashboard as the
canonical portfolio/reviewer surface and the Next.js application as a secondary
Stage 0 surface. The sequence separates Flask, Next.js, cross-surface
verification, and final closure responsibilities.

This document is planning evidence only. It authorizes no implementation. Every
later slice requires a separate explicit authorization decision. Phase 2P remains
separate and later. Stage 0 remains report-only, dry-run, mock-only, and
non-executing.

| Field | Status |
| --- | --- |
| `PHASE_2O_00_STATUS` | `DONE / REVIEWED / MERGED_TO_MAIN` |
| `DOCUMENTATION_REVIEW_DECISION` | `PASS` |
| `PLANNING_COMMIT` | `99b1929b6efd0af07ed3bbe634d7e7108867618f` |
| `PLANNING_COMMIT_STATUS` | `MERGED_TO_MAIN` |
| `PHASE_2O_STATUS` | `IN_PROGRESS / NOT_READY` |
| `PHASE_2O_01_CONTINUATION_AUTHORIZATION` | `DONE / AUTHORIZED` |
| `PHASE_2O_01_IMPLEMENTATION_COMMIT` | `a2d19722a48eae6f3e8573db0e023bdffdff4ce9` |
| `PHASE_2O_01_IMPLEMENTATION_STATUS` | `DONE / MERGED_TO_MAIN` |
| `PHASE_2O_01_IMPLEMENTATION_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_01_RESPONSIVE_FIX_COMMIT` | `f4a65339cd146b26c0d23810fea992cd6dfea9c6` |
| `PHASE_2O_01_FIX_COMMIT_STATUS` | `DONE / MERGED_TO_MAIN` |
| `PHASE_2O_01_FIX_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_01_TECHNICAL_AND_SAFETY_DISPOSITION` | `PASS` |
| `PHASE_2O_01_PRIOR_REMAINING_FINDING` | `STALE_PHASE_2O_00_STATUS_AND_HANDOFF_DOCUMENTATION` |
| `PHASE_2O_01_DOCUMENTATION_FIX_COMMIT` | `8fdeeb3dc3e605b5f1a80ea78b441fa982c1efb6` |
| `PHASE_2O_01_DOCUMENTATION_FIX_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_01_HISTORICAL_INTEGRATION_AUTHORIZATION_DECISION` | `BLOCKED` |
| `PHASE_2O_01_HISTORICAL_INTEGRATION_AUTHORIZATION_BLOCKER` | `STALE_APPLICABLE_STATUS_AND_HANDOFF_RECORDS` |
| `PHASE_2O_01_INTEGRATION_BLOCKER_DOCUMENTATION_FIX_COMMIT` | `b7d8ec9e63dd72d7a935ed6228deabfaba072a1a` |
| `PHASE_2O_01_INTEGRATION_BLOCKER_DOCUMENTATION_FIX_REVIEW` | `PASS` |
| `PHASE_2O_01_LATEST_INTEGRATION_AUTHORIZATION_DECISION` | `AUTHORIZED` |
| `PHASE_2O_01_INTEGRATION_BASE` | `ecaef4a0655cae10d4ed7154f4948fb4d6982e6c` |
| `PHASE_2O_01_INTEGRATION_TARGET` | `b7d8ec9e63dd72d7a935ed6228deabfaba072a1a` |
| `PHASE_2O_01_INTEGRATION_METHOD` | `STRICT_FAST_FORWARD` |
| `PHASE_2O_01_STATUS` | `DONE / MERGED_TO_MAIN / SYNCHRONIZED / POST_MERGE_STATUS_RECONCILIATION_READY_FOR_REVIEW` |
| `PHASE_2O_IMPLEMENTATION_STATUS` | `IN_PROGRESS / NOT_READY` |
| `PHASE_2O_02_IMPLEMENTATION_COMMIT` | `0548c6beab80a087ea02d00d49a213dd4336724a` |
| `PHASE_2O_02_IMPLEMENTATION_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_02_REVIEW_FIX_COMMIT` | `00862075494bc7a76dd478bee9d1742d53d43167` |
| `PHASE_2O_02_REVIEW_FIX_STATUS` | `DONE / MERGED_TO_MAIN` |
| `PHASE_2O_02_REVIEW_FIX_DECISION` | `PASS` |
| `PHASE_2O_02_CUMULATIVE_IMPLEMENTATION_STATUS` | `ACCEPTED` |
| `PHASE_2O_02_INTEGRATION_TARGET` | `00862075494bc7a76dd478bee9d1742d53d43167` |
| `PHASE_2O_02_INTEGRATION_METHOD` | `STRICT_FAST_FORWARD` |
| `PHASE_2O_02_POST_MERGE_RECONCILIATION_COMMIT` | `10cec5ca1911140decdba7b84f54667698dcedae` |
| `PHASE_2O_02_POST_MERGE_RECONCILIATION_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_02_STATUS` | `DONE / ACCEPTED / MERGED_TO_MAIN / SYNCHRONIZED` |
| `PHASE_2O_03_CONTINUATION_AUTHORIZATION` | `AUTHORIZED` |
| `PHASE_2O_03_INITIAL_ATTEMPT` | `BLOCKED / EXACT_SCOPE_TEST_CONTRACT_CONFLICT / NO_EDITS / NO_COMMIT` |
| `PHASE_2O_03_CORRECTED_SCOPE` | `AUTHORIZED / EXACT_14_FILE_SCOPE` |
| `PHASE_2O_03_IMPLEMENTATION_COMMIT` | `d18e6ccac87e45e7cc983bb09be1c50f07c0c6c2` |
| `PHASE_2O_03_IMPLEMENTATION_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_03_REVIEW_FIX_COMMIT` | `9ff474822a94d0f79ff45b061af590186b425def` |
| `PHASE_2O_03_REVIEW_FIX_DECISION` | `PASS` |
| `PHASE_2O_03_CUMULATIVE_IMPLEMENTATION_STATUS` | `ACCEPTED` |
| `PHASE_2O_03_INTEGRATION_TARGET` | `9ff474822a94d0f79ff45b061af590186b425def` |
| `PHASE_2O_03_INTEGRATION_METHOD` | `STRICT_FAST_FORWARD` |
| `PHASE_2O_03_POST_MERGE_RECONCILIATION_COMMIT_REFERENCE` | `THIS_COMMIT` |
| `PHASE_2O_03_POST_MERGE_RECONCILIATION_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_03_STATUS` | `DONE / REVIEWED / MERGED_TO_MAIN / SYNCHRONIZED` |
| `PHASE_2O_04_INITIAL_IMPLEMENTATION_ATTEMPT` | `BLOCKED / EXACT_SCOPE_TEST_CONTRACT_CONFLICT` |
| `PHASE_2O_04_SCOPE_CORRECTION_DECISION` | `AUTHORIZED / EXACT_12_FILE_MAXIMUM` |
| `PHASE_2O_04_IMPLEMENTATION_COMMIT` | `2643b24497011ea31c507d6f567daf5f20287a5d` |
| `PHASE_2O_04_IMPLEMENTATION_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_04_ORIGINAL_IMPLEMENTATION_STATUS` | `DONE / LOCAL_ONLY / REVIEWED / FAIL_FIX_REQUIRED` |
| `PHASE_2O_04_IMPLEMENTATION_TECHNICAL_AND_SAFETY_RESULT` | `PASS` |
| `PHASE_2O_04_IMPLEMENTATION_REVIEW_ORIGINAL_FINDING` | `STALE_PHASE_2O_03_AND_PHASE_2O_04_STATUS_WORDING` |
| `PHASE_2O_04_FIRST_DOCUMENTATION_REVIEW_FIX_COMMIT` | `4546f3f441ecaa14f208eee928da33b0ac9b5769` |
| `PHASE_2O_04_FIRST_DOCUMENTATION_REVIEW_FIX_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_04_FIRST_DOCUMENTATION_REVIEW_FIX_HISTORICAL_STATUS` | `DONE / LOCAL_ONLY / REVIEWED / FAIL_FIX_REQUIRED` |
| `PHASE_2O_04_FIRST_FIX_REVIEW_REMAINING_DOCUMENTATION_FINDING` | `STALE_UNQUALIFIED_PHASE_2O_04_UNAUTHORIZED_WORDING_IN_SECTIONS_12_AND_13_4` |
| `PHASE_2O_04_SECOND_DOCUMENTATION_REVIEW_FIX_COMMIT` | `7153cb9bcd328489057012a66dc5777e32cc0b26` |
| `PHASE_2O_04_SECOND_DOCUMENTATION_REVIEW_FIX_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_04_HISTORICAL_PRE_INTEGRATION_CUMULATIVE_STATUS` | `ACCEPTED / LOCAL_ONLY` |
| `PHASE_2O_04_FIRST_INTEGRATION_AUTHORIZATION_DECISION` | `NOT_AUTHORIZED / HISTORICAL` |
| `PHASE_2O_04_POST_AUTHORIZATION_DOCUMENTATION_STATUS_FIX_COMMIT` | `1e6561344b53161da85dac0e912bfead425af125` |
| `PHASE_2O_04_POST_AUTHORIZATION_DOCUMENTATION_STATUS_FIX_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_04_STABLE_EXTERNAL_REVIEW_HANDOFF_FIX_COMMIT` | `bc8b22934191187c18f1c1fc3c498cc2cc03c30f` |
| `PHASE_2O_04_STABLE_EXTERNAL_REVIEW_HANDOFF_FIX_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_04_PHASE_2O_00_HANDOFF_RECONCILIATION_COMMIT` | `413814ceefe5160cecda6bcfdd5c0f24c05cdcbb` |
| `PHASE_2O_04_PHASE_2O_00_HANDOFF_RECONCILIATION_REVIEW_DECISION` | `PASS` |
| `PHASE_2O_04_PHASE_2O_00_HANDOFF_RECONCILIATION_MATERIAL_FINDINGS` | `0` |
| `PHASE_2O_04_FINAL_INTEGRATION_AUTHORIZATION_DECISION` | `AUTHORIZED` |
| `PHASE_2O_04_INTEGRATION_BASE` | `93cf3bba0c74e7eec685dbc1f7925c0ceca218c7` |
| `PHASE_2O_04_INTEGRATED_COMMIT` | `413814ceefe5160cecda6bcfdd5c0f24c05cdcbb` |
| `PHASE_2O_04_INTEGRATION_METHOD` | `STRICT_FAST_FORWARD` |
| `PHASE_2O_04_INTEGRATION_STATUS` | `COMPLETED` |
| `PHASE_2O_04_PUSH_STATUS` | `COMPLETED / NON_FORCE` |
| `PHASE_2O_04_SYNCHRONIZATION_STATUS` | `LOCAL_MAIN_TRACKING_AND_REMOTE_MAIN_MATCH` |
| `PHASE_2O_04_LOCAL_SOURCE_BRANCH_CLEANUP` | `COMPLETED / SAFE DELETE` |
| `PHASE_2O_04_REMOTE_SOURCE_BRANCH` | `NOT DELETED` |
| `PHASE_2O_04_CUMULATIVE_STATUS` | `ACCEPTED / MERGED_TO_MAIN` |
| `PHASE_2O_04_POST_MERGE_RECONCILIATION_COMMIT` | `5fc25f9035ee23ee98147e15caeb044e3ed405ba` |
| `PHASE_2O_04_STATUS` | `DONE / MERGED_TO_MAIN / SYNCHRONIZED / RECONCILED` |
| `PHASE_2O_04_POST_MERGE_RECONCILIATION_STATUS` | `COMPLETED` |
| `PHASE_2O_04_CURRENT_HANDOFF` | `COMPLETED / SUPERSEDED_BY_PHASE_2O_05_PREREQUISITE_PLANNING` |
| `PHASE_2O_05_PREREQUISITE_PLANNING_STATUS` | `DONE / REVIEWED` |
| `PHASE_2O_05_PREREQUISITE_PLANNING_COMMIT` | `3a45e7fa7f5af1a36d57487b56192dae0f66ea87` |
| `PHASE_2O_05_IMPLEMENTATION_STATUS` | `ACCEPTED` |
| `PHASE_2O_05_RECONCILIATION_REVIEW_STATUS` | `PASS / ZERO MATERIAL FINDINGS` |
| `PHASE_2O_05_INTEGRATED_MAIN_TIP` | `c5c720d17919e2246d88cb8699341f24b8aec641` |
| `PHASE_2O_05_INTEGRATION_STATUS` | `DONE / MERGED_TO_MAIN / PUSHED / SYNCHRONIZED / SAFE_LOCAL_BRANCH_CLEANUP_COMPLETE` |
| `PHASE_2O_05_LOCAL_SOURCE_BRANCH_STATUS` | `PASS / SAFELY_DELETED` |
| `PHASE_2O_05_REMOTE_BRANCH_STATUS` | `NOT_DELETED` |
| `PHASE_2O_05_CURRENT_STATUS` | `INTEGRATED_AND_SYNCHRONIZED / FINAL_DOCUMENTATION_RECONCILIATION_IN_PROGRESS` |
| `PHASE_2O_05_POST_MERGE_RECONCILIATION_COMMIT` | `47a92b9cedeee6a25b5d5cfa502158290221736d` |
| `PHASE_2O_05_POST_MERGE_RECONCILIATION_REVIEW_RESULT` | `FAIL_FIX_REQUIRED / P2O05-RECON-REV-001 / P2O05-RECON-REV-002` |
| `PHASE_2O_05_RECONCILIATION_FIX_COMMIT` | `c5c720d17919e2246d88cb8699341f24b8aec641` |
| `PHASE_2O_05_RECONCILIATION_FIX_REVIEW_STATUS` | `PASS / ZERO MATERIAL FINDINGS` |
| `PHASE_2O_05_FINAL_DOCUMENTATION_RECONCILIATION_STATUS` | `DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW` |
| `PHASE_2O_05_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REFERENCE` | `THIS_COMMIT` |
| `PHASE_2O_05_CLOSURE_STATUS` | `NOT_CLOSED / PENDING_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW` |
| `PHASE_2O_05_CURRENT_HANDOFF` | `READY_FOR_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW` |
| `PHASE_2O_06_THROUGH_2O_07_STATUS` | `NOT_AUTHORIZED / NOT_STARTED` |
| `PHASE_2P_STATUS` | `NOT_AUTHORIZED / NOT_STARTED` |
| `STAGE_0_BOUNDARY` | `PRESERVED` |

No provider, model, job, command, device, or production authority follows from a
visual treatment, status label, navigation destination, reviewer view, or
technical-detail view.

## 2. Phase 2O purpose

### 2.1 Bounded purpose

Phase 2O may improve reviewer-facing information architecture, visual hierarchy,
state communication, responsive presentation, and accessibility by presenting
existing local evidence and existing application behavior more clearly. It may
not create a new evidence source, operational workflow, or execution capability.

### 2.2 Separation from adjacent work

| Area | Relationship to Phase 2O |
| --- | --- |
| Phase 2N | Phase 2N accepted the current user-facing Stage 0 Demo and closed it. Phase 2O may improve presentation without reopening that acceptance or weakening its safety labels. See `docs/phase_2n/phase_2n_05_final_user_facing_acceptance_review_phase_closure_review_only.md`. |
| Phase 2P | Packaging, distribution, deployment, and publication remain future Phase 2P work and are excluded. |
| Actual automation | No advancement. The readiness stages and gates in `docs/automation_readiness/actual_automation_integration_plan.md` remain controlling; this plan grants none of their future authority. |
| Providers and runtime | Existing provider-shaped code or dependencies do not make provider-backed behavior available. Phase 2O cannot enable provider, model, API, POST, job creation, runner, adapter, importer, or execution behavior. |
| Operational authority | Reviewer and technical-detail presentation are information-density choices only, never permission or execution modes. |

## 3. Current UX baseline

### 3.1 Evidence method

Current-state statements below are source observations unless a cited Phase 2N
record explicitly supplies rendered acceptance evidence. This planning task did
not start a server or browser and therefore does not claim fresh rendered
behavior.

The source inventory covered `README.md`, `dashboard_app.py`, all canonical Flask
templates in `templates/`, the relevant Next.js files in `app/`,
`components/network/`, and `lib/network-ai/`, applicable presentation tests,
`package.json`, `package-lock.json`, and `requirements.txt`.

### 3.2 Explicit assumptions

- **Assumption A:** The authorization prompt refers to a prior Phase 2O-01 through
  Phase 2O-07 candidate, but no committed candidate sequence was found in the
  repository. Section 12 treats those seven identifiers as placeholders and
  supplies a revised evidence-backed responsibility and gate model.
- **Assumption B:** Future visualizations use only the data already made available
  to a surface. If a proposed view needs a new field, importer, sanitizer, API, or
  data contract, that work is outside the affected UI slice until separately
  planned and authorized.
- **Assumption C:** Existing operational-looking history remains historical
  evidence. Historical wording is not current authority.

### 3.3 Surface relationship and entries

| Observed fact | Evidence | Limitation or planning consequence |
| --- | --- | --- |
| The Flask dashboard is the canonical reviewer entry, with `/` as its overview. | `README.md`; `templates/dashboard_home.html`; `dashboard_app.py`; `docs/phase_2n/phase_2n_04_user_facing_entry_point_and_safety_label_clarification_implementation.md` | The primary portfolio journey must remain Flask-owned. |
| Next.js is explicitly a secondary, demo-only Stage 0 surface. Its root links into `/network/day-results`, while `/network` redirects there. | `app/page.tsx`; `app/network/page.tsx`; `components/network/NetworkNav.tsx`; `components/network/Phase2N04DemoPresentation.ts` | Next.js must not become a competing canonical entry during Phase 2O. |
| Phase 2N accepted both rendered surfaces while preserving Stage 0 and the canonical/secondary relationship. | `docs/phase_2n/phase_2n_05_final_user_facing_acceptance_review_phase_closure_review_only.md` | Phase 2O is presentation improvement, not a replacement acceptance basis. |

### 3.4 Canonical Flask baseline

| Area | Source-backed current state | Inconsistency or limitation |
| --- | --- | --- |
| App shell and layout | Each template renders its own `<main>` and navigation. Styling is embedded separately in each template. See `templates/dashboard_home.html`, `templates/dashboard_reports.html`, `templates/dashboard_commands.html`, `templates/dashboard_ai_checklist.html`, `templates/dashboard_ai_intent_reviewer.html`, `templates/dashboard_command_logs.html`, `templates/dashboard_command_log.html`, and `templates/dashboard_json_preview.html`. | There is no shared Flask base template, shared navigation component, or shared token file. Repetition makes drift likely. |
| Navigation | The main destinations are Home, Reports, Commands, AI Intent Reviewer, and AI Checklist. Log navigation appears only on some pages. | `Historical Logs` and `Execution Logs` are used for the same route, and the destination is absent from some navigation instances. Active-state behavior is template-specific. |
| Overview hierarchy | The home template uses a hero, Stage 0 notices, proof cards, quick links, and report-readiness cards. Data comes from `discover_reports()` and `build_summary_cards()` in `dashboard_app.py`. | The overview mixes portfolio introduction, safety explanation, validation claims, quick starts, and report readiness. The highest-value reviewer question is not consistently prioritized. |
| Reports and evidence | `/reports` groups local evidence and presents VRRP, WireGuard, and Day 12/report-index-related tables. Safe open/preview routes constrain paths and extensions in `dashboard_app.py`. JSON preview supplies a summary and raw JSON. | The canonical page is technically dense and displays repository paths. Filter chips are presentation-only. Raw detail and reviewer summary are not clearly separated. |
| Commands | `/commands` renders a Stage 0 display-only allowlist reference, static examples, and historical records without a form or Run control. | The retained POST route in `dashboard_app.py` is intentionally not rendered. Operational nouns and historical log content can still appear action-like without prominent contextual framing. |
| AI review content | AI Checklist is a reference table. AI Intent Reviewer is a large Day 57–94 documentation/evidence index with repeated safety notices and links. | The AI Intent Reviewer has a very long single-page hierarchy and high cognitive load. It should not be interpreted as provider availability. |
| Status and safety | Templates reuse PASS, FAIL, warning, and unknown color families; `status_class` in `dashboard_app.py` normalizes aliases including WARN and missing. Stage 0 notices are prominent on Home and Commands. | `WARN` versus `WARNING`, `Historical Logs` versus `Execution Logs`, and availability/status language are not fully consistent. Some pages rely on the navigation context rather than a surface-level Stage 0 statement. |
| Empty and missing | Reports receives `reports_exist` and `has_evidence`; evidence sections render local missing/empty notices. Logs and report collections have empty states. Safe artifact routes return 404 for missing, disallowed, or path-traversal requests. | Empty, missing, unavailable, malformed, and error conditions use several visual patterns and are not organized as one state vocabulary. |
| Responsive behavior | Home uses 960 px and 620 px media rules; AI Intent Reviewer uses 720 px; most other pages use 620 px. Tables generally use horizontal overflow. | Breakpoints and dense-table behavior are page-specific. Source inspection cannot establish keyboard scroll discoverability or rendered content clipping. |
| Accessibility and keyboard | The templates use semantic headings, navigation, main content, tables, links, and some `role="note"` content. | No Flask template has a skip link, explicit `:focus-visible` treatment, `aria-current`, or a shared landmark/heading contract. Browser-default focus is the only source-visible fallback. |
| Presentation tests | `tests/test_dashboard_app.py`, `tests/test_phase_2n_02_canonical_flask_demo_smoke.py`, `tests/test_phase_2n_04_user_facing_safety_labels.py`, and the Phase 2N closure record cover route, empty-state, safety-label, and no-execution expectations. | Current tests protect key content and safety behavior, but they are not a complete keyboard, screen-reader, responsive, or contrast suite. |

### 3.5 Secondary Next.js baseline

| Area | Source-backed current state | Inconsistency or limitation |
| --- | --- | --- |
| App shell and layout | `app/layout.tsx` supplies metadata, `lang="zh-Hant"`, and the global stylesheet. Network pages repeat a header plus `NetworkNav`; there is no `app/network/layout.tsx`. | Shared network-page markup is duplicated and the Chinese language declaration does not match all-English/mixed-language content. |
| Navigation | `components/network/NetworkNav.tsx` links Evidence, AI Actions, Reports, and Jobs, carries a secondary Stage 0 label, and uses `aria-current`. | The root page also links to older `/ai` and `/automation/ai-nodes` surfaces that look provider-oriented. Those older surfaces are not part of the Phase 2O Stage 0 network journey. |
| Evidence | `/network/day-results` imports local JSON/TXT evidence, groups and sorts it, shows safe boundary/status badges, raw output, and any historical analysis record. Sources are `app/network/day-results/page.tsx`, `components/network/DayResultsClient.tsx`, and `lib/network-ai/dayResults.ts`. | The page is dense, exposes raw technical output, and has visible mojibake-like separator/empty copy in source. It fetches an existing analysis record but renders no Analyze control in Stage 0. |
| Reports | `/network/reports` uses the same importer but `ReportsClient` renders only bounded category, normalized day, date, count, and normalized status metadata. The accepted empty/error-state evidence is in `docs/phase_2n/phase_2n_03c_navigation_empty_and_error_state_acceptance_review_only.md`. | It is safer and simpler than the Evidence detail surface, but offers no filtering or reviewer summary beyond the list. |
| AI Actions | `/network/ai-actions` renders a static allowlist and any recorded parse result. Phase 2N removed request input, Parse, and Create Job controls from the Stage 0 parent. | Catalog descriptions include action-like historical language. The page loads an existing record and needs clearer separation between recorded evidence, capability availability, and operational authority. |
| Jobs | `/network/jobs` lists locally stored job records and can refresh the list; it has no Run Job control and says the runner is not enabled. | The page lacks the same prominent Stage 0 presentation component used by Evidence and AI Actions. `lib/network-ai/jobs.ts` is behavior-bearing persistence code and is outside a UI-only slice. |
| Status and safety | `app/globals.css` defines success, warning, danger, neutral, boundary, disabled, error, and status-strip patterns. Phase 2N presentation components state provider-unavailable behavior. | Status normalization is duplicated across Evidence and Reports. `Runner not enabled in Phase 1` does not match current Phase 2N/Stage 0 terminology. |
| Loading, empty, missing, error | Evidence, AI Actions, and Jobs show inline loading or error content for their existing reads. Reports has a reviewed HTTP-200 empty state. Evidence and Jobs have local empty states. | Only `app/layout.tsx` exists among layout/loading/error/not-found convention files; there are no route-level `loading.tsx`, `error.tsx`, or `not-found.tsx` files. State wording and announcement semantics are inconsistent. |
| Responsive behavior | `app/globals.css` has a shared 860 px media rule, responsive grids, wrapping navigation, and horizontally scrollable dense jobs output. | One breakpoint covers many different content pressures; the jobs row collapses from a nine-column minimum width to a one-column flow without a documented mobile field-label strategy. |
| Accessibility and keyboard | Network navigation uses a label and `aria-current`; icons are hidden from assistive technology; buttons have minimum sizes; the icon action button has `:focus-visible`; semantic headings and definition lists are present. | General links, result-row buttons, tabs, and other controls lack a shared focus-visible rule. The jobs ARIA table supplies row roles but not explicit cell/columnheader roles. Loading/error announcements are inconsistent, and no skip link is visible in source. |
| Reusable patterns | `app/globals.css` supplies global variables and shared panel, toolbar, badge, status, grid, action-card, and table patterns. `NetworkNav` and Phase 2N presentation components are reusable. | Presentation and status helpers remain partly component-local; network-page headers are repeated. |
| Presentation tests | `tests/test_network_phase1_ui_presentation.py`, `components/network/ReportsClient.test.tsx`, `components/network/Phase2N04SafetyLabels.test.ts`, and the Phase 2N closure record cover evidence wording, safe report metadata, empty state, navigation, Stage 0 labels, and removed action controls. | Vitest uses server-rendered markup and Python checks source contracts; no directly declared browser E2E or accessibility runner currently supplies interactive coverage. |

### 3.6 Current data and responsibility constraints

- Flask presentation reads local report/evidence metadata through `dashboard_app.py`
  and bounded repository evidence directories. It also has technical preview and
  historical-record surfaces.
- Next.js Evidence and Reports use `importDayResults()` from
  `lib/network-ai/dayResults.ts`, which walks local `reports` and `summary` JSON/TXT
  sources. Reports deliberately exposes a smaller safe metadata set than Evidence.
- Existing AI Actions and Jobs records are historical/local application records.
  Their presence is not provider, command, job-execution, or device authority.
- Any current raw output, device identity, source path, or log content is technical
  detail, not an approved field for a new reviewer summary by default.

## 4. Target users and journeys

### 4.1 Bounded user groups

| User group | Primary question | Intended journey |
| --- | --- | --- |
| Portfolio or hiring reviewer | What does the project prove, and can I understand its safety and evidence quickly? | Canonical Flask Overview → evidence/status summary → selected report summary → optional technical detail. |
| Technical reviewer | Which local artifact supports a claim, what is its status, and what boundary applied? | Flask Overview or Reports → filter/group → metadata and state → bounded raw/technical evidence where already safe. |
| Project maintainer reviewing local evidence | Are local evidence sets present, missing, stale, or inconsistent across the two presentation surfaces? | Canonical Flask status and Reports → secondary Next.js Evidence/Reports for comparison → documented source path or test reference. |

An operator, command executor, live-device administrator, AI execution user, or
production user is explicitly not a Phase 2O target user.

### 4.2 Journey rules

- A reviewer must encounter canonical/secondary identity and Stage 0 capability
  boundaries before any operational-looking historical content.
- Summary comes before technical detail; technical detail is an optional
  presentation layer, not an authorization layer.
- Every journey has useful present, empty, missing, unavailable, and error endings.
- No journey ends in Analyze, Parse, Create Job, Run, execute, connect, configure,
  backup, deploy, or publish.

## 5. Canonical and secondary surface responsibilities

| Responsibility | Canonical Flask | Secondary Next.js |
| --- | --- | --- |
| Primary portfolio/reviewer journey | Owns it. Overview, proof summary, evidence discovery, safety explanation, and bounded technical drilldown live here. | Does not own it. The root must continue to identify Flask as canonical. |
| Evidence alignment | Owns the project-wide reviewer narrative and existing local evidence index. | Owns the Stage 0 network evidence exploration demonstration using its existing importer. |
| Shared alignment candidates | Terminology, status vocabulary, safety/capability notices, empty/error state taxonomy, focus treatment, spacing rhythm, and reviewer-versus-detail hierarchy. | Same, adapted to React/Next.js components and existing global CSS. |
| Surface-specific work | Jinja layout/navigation extraction, Flask templates, safe artifact links, report tables, command/history framing, and long AI reference hierarchy. | Network app shell, React component states, route-specific lists/cards, client-side selection/refresh behavior, and Next.js semantic patterns. |
| Implementation slicing | Separate Flask slices are required because its templates and tests are independent of Next.js. | Separate Next.js slices are required; shared visual intent does not justify mixed framework edits in one slice. |

Older Next.js `/ai` and `/automation/ai-nodes` provider-shaped workbenches are
excluded from the Phase 2O Stage 0 network journey and retained unchanged unless a
separate future authorization explicitly scopes them. Existing Flask POST routes,
command runners, persistence code, provider APIs, and importer behavior are also
retained unchanged and excluded from UI-only slices. Presentation work must not
surface their controls or imply that they are available.

## 6. Information architecture and navigation plan

### 6.1 Recommended canonical Flask model

1. **App shell:** persistent project identity, canonical Stage 0 label, primary
   navigation, consistent page title, and a route-specific capability notice.
2. **Overview:** conclusion-first project proof, evidence health, safety boundary,
   then reviewer shortcuts. Historical and setup detail remains secondary.
3. **Evidence and Reports:** one primary discovery destination with a reviewer
   summary layer; existing report families and safe preview routes remain
   surface-specific detail.
4. **Safety and capability:** a consistent notice explains display-only,
   report-only, unavailable, and historical states without suggesting an action.
5. **Commands:** clearly named display-only command reference. Historical records
   remain a secondary technical destination and use one consistent label.
6. **AI review:** AI Checklist and the long AI Intent evidence index remain static
   evidence/reference surfaces, with the latter grouped progressively by review
   purpose rather than presented as an execution workflow.
7. **Technical detail:** repository paths, raw JSON, historical argv/log detail,
   and long evidence chains remain subordinate and are never promoted into the
   default portfolio summary without a safe-field review.

### 6.2 Recommended secondary Next.js model

1. **Secondary landing:** retain the explicit link and wording that identify Flask
   as canonical; separate the Stage 0 network demo from older excluded workbenches.
2. **Network app shell:** shared network header and navigation for Evidence,
   Reports, AI Actions, and Jobs, with current location and Stage 0 identity.
3. **Evidence:** grouped local evidence with reviewer metadata first and existing
   raw/historical detail second.
4. **Reports:** safe metadata-only collection and the accepted HTTP-200 empty state.
5. **AI Actions:** static allowlist plus recorded result, always preceded by
   provider-unavailable and no-submission context.
6. **Jobs:** historical/local record list with a Stage 0 unavailable notice; no
   create or run control.

### 6.3 Presentation framing

`Reviewer summary` and `Technical detail` are recommended labels or disclosure
levels. They do not alter permissions, routes, data access, safety gates, or
execution availability. There is one Stage 0 authorization boundary for both.

## 7. Visual hierarchy and design-token strategy

The following are planning principles, not token implementation or framework
selection.

| Concern | Recommended principle |
| --- | --- |
| Typography | Use a compact type scale with one page heading, ordered section headings, readable body line length, and monospace only for identifiers or evidence. Do not use typography alone to encode status. |
| Spacing | Adopt a named spacing rhythm for shell, section, card, and dense-table contexts. Preserve comfortable touch/focus targets. |
| Layout | Summary before detail; one primary content column at narrow widths; bounded wide layouts for dense evidence; progressive disclosure for raw data. |
| Cards | Use cards for discrete reviewer questions, not as decoration. Every summary card identifies its source, status, and empty behavior. |
| Tables | Use native tables when data is tabular, with captions or accessible names, header scope, and a narrow-screen strategy. Avoid ARIA table reconstruction when native semantics suffice. |
| Status | Normalize visible labels to `PASS`, `WARN`, `FAIL`, `BLOCKED`, `REVIEW_ONLY`, `UNKNOWN`, `MISSING`, or an explicitly documented subset. Keep evidence result separate from capability availability. |
| Color | Preserve text labels and icons/patterns in addition to color. Verify foreground, border, badge, disabled, and focus contrast before acceptance. |
| Focus | Provide a consistent, high-contrast `:focus-visible` treatment for every link, button, disclosure, tab, filter, and scrollable region. |
| Safety notice | Give Stage 0 and unavailable notices a stable component pattern and concise wording. Safety notices must precede operational-looking history. |
| State model | `empty` means a valid collection with zero items; `missing` means an expected local artifact is absent; `unavailable` means the capability is intentionally not offered; `error` means an attempted existing read failed; `blocked` is a recorded safety result. These labels are not interchangeable. |
| Breakpoints | Start from content reflow rather than device names. Reconcile current 620/720/860/960 px behaviors only after rendered measurement. A future slice must document why each retained breakpoint exists. |
| Motion | Prefer no essential motion. If a later slice adds non-essential transition, respect reduced-motion preferences and never animate status as the only alert. |

Existing Flask teal/neutral/status palettes and Next.js variables in
`app/globals.css` are useful inputs, not a finalized shared design system.

## 8. Visualization principles

### 8.1 Proposed bounded visualizations

| Proposal | Existing data source | Reviewer question | Safe field set | Empty or missing behavior | Accessibility alternative | Dependency decision |
| --- | --- | --- | --- | --- | --- | --- |
| Overview summary cards | Flask `build_summary_cards()` / `discover_reports()` in `dashboard_app.py`; Next.js report count from `importDayResults()` | What evidence is available and what needs attention? | Aggregate count, normalized status, approved category, availability, and existing report title only after safe-field review | Zero is an explicit valid count; missing source is `MISSING`, not zero; include explanation and next non-executing review step | Heading plus definition list or text summary in DOM | No new dependency; use existing HTML/CSS |
| PASS/WARN/FAIL summary | Existing normalized Flask status classes and bounded Next.js report status normalization in `components/network/ReportsClient.tsx` | What is the distribution of known outcomes? | Aggregate normalized status and total only; never arbitrary raw status text | Display zero-count categories and an `UNKNOWN`/`MISSING` explanation; do not infer PASS | Text totals and a semantic table; color is supplemental | No dependency for cards/bars; any chart library requires a separate gate |
| Evidence filter/sort/search | Existing Flask evidence metadata from `collect_dashboard_evidence()` and existing Next.js `DayResult` metadata already rendered | Can I find evidence by category, day, date, or normalized status? | Approved category, normalized status, normalized Day label, safe date, availability, and already-approved title | Preserve an all-empty state and distinguish no-source from no-filter-match | Labeled native controls, result count announcement, keyboard-operable reset, DOM list/table | No dependency expected; no new importer or API |
| Report summaries | Existing Flask report cards and safe Next.js `ReportsClient` fields | What does this report prove without opening raw detail? | Count, category, normalized status, normalized Day/date, availability, and existing safe summary text | HTTP-200 empty state remains informative; missing fields show `Unknown`, never fabricated content | Semantic summary list/definition list and link text that identifies destination | No dependency |
| Day timeline | Existing normalized `sourceDay` and `createdAt` in `DayResult`, or existing committed Day references in Flask evidence data | In what evidence order did work occur? | Normalized Day number, safe date, category, status, and bounded title | Unknown Day/date is a separate group; never invent ordering from filenames beyond existing normalization | Ordered list or table with the same items and order | No dependency for list/timeline CSS; graphical library requires a gate |
| Phase timeline | No single approved structured source currently exists | Which accepted phase milestones are recorded? | Not yet approved. A future proposal may use a curated, committed phase-record index only. | Defer rather than scrape arbitrary docs or infer phase status | Ordered textual milestone list | New data-contract decision required before implementation; no library decision until then |
| Reviewer summary / technical detail | Existing safe metadata plus existing bounded detail routes/components | What is the conclusion, and where is supporting detail? | Summary uses only safe fields above. Raw output, device identity, paths, argv, logs, and provider/model metadata remain technical and require current safety controls. | Summary remains useful without detail; unavailable detail explains why | Native disclosure/heading structure with keyboard support; full text remains available | No dependency |

### 8.2 Visualization prohibitions

No visualization may fabricate, poll, discover, or imply live state. It may not
read credentials, secrets, private inventory, arbitrary internal paths, network
devices, providers, APIs, models, or runtime systems. Visual freshness labels must
describe the local artifact timestamp, never operational network freshness.

## 9. Responsive and accessibility baseline

These requirements apply to every future implementation slice. Phase 2O-06 may
consolidate and independently verify them, but cannot be the first slice to add
them.

### 9.1 Cross-cutting requirements

- **Keyboard:** logical source order; all interactive elements reachable and
  operable; no keyboard trap; Escape behavior only where an actual dismissible
  component exists; scrollable regions keyboard reachable when necessary.
- **Focus:** visible focus on every control and link, including navigation,
  evidence rows, filters, disclosures, and technical preview links; focus is not
  hidden by sticky content.
- **Landmarks and headings:** one primary `<main>`, named navigation where needed,
  one page `<h1>`, ordered section headings, and a skip link on full app shells.
- **Tables:** native table semantics, captions or accessible names, column/row
  headers, meaningful empty rows, and an explicit narrow-screen strategy. If a
  grid is not a table, do not label it as one.
- **Status and alerts:** status is text plus visual treatment. Dynamic loading,
  completion, empty-result count, and existing-read errors use appropriate live
  announcements without repeatedly announcing static safety copy.
- **Names and labels:** controls have visible labels or equivalent accessible
  names; icon-only controls are avoided unless the accessible name is explicit.
- **Non-color meaning:** PASS/WARN/FAIL, selected state, and capability availability
  remain understandable without color.
- **Reduced motion:** no essential animation; any future decorative movement
  respects `prefers-reduced-motion`.
- **Narrow navigation:** links wrap or become an accessible disclosure without
  horizontal clipping; canonical/secondary identity remains visible.
- **Dense tables:** choose labeled reflow, priority columns plus detail, or keyboard-
  accessible horizontal scrolling based on the data; do not silently drop fields.
- **Content reflow:** at 320 CSS px equivalent width and 400% zoom, primary content
  reflows without two-dimensional scrolling except genuinely tabular or raw-code
  regions.

### 9.2 Minimum acceptance evidence for every later slice

Each separately authorized implementation slice must provide:

1. A changed-file and route/component scope inventory.
2. Source and test proof that Stage 0 negative controls remain absent.
3. Keyboard walkthrough evidence covering entry, navigation, main content,
   interactive content, focus order, and return path.
4. Rendered viewport evidence at narrow, intermediate, and wide widths, including
   empty/missing/unavailable/error variants within the slice.
5. Heading/landmark/table/name checks and non-color status confirmation.
6. Contrast and focus visibility results using an approved existing method, or a
   separately authorized dependency decision before a new tool is added.
7. Targeted tests and the repository-required validation appropriate to the
   changed behavior, including negative no-execution proof.
8. A documentation readability review and an explicit statement that no new
   operational authority was introduced.

## 10. Dependency decision gates

### 10.1 Current relevant dependency inventory

| Category | Current state | Planning disposition |
| --- | --- | --- |
| Next.js presentation | Direct dependencies: `next`, `react`, `react-dom`, and `lucide-react`; global CSS is hand-authored. See `package.json`. | Reuse is allowed only inside a separately authorized Next.js UI slice. Lucide is not a Flask dependency. |
| Existing provider package | `openai` is a direct dependency, but Stage 0 provider behavior is unavailable. | Excluded. Its presence is not authority and it must not be used by Phase 2O. |
| Python presentation | `flask` is the direct presentation dependency in `requirements.txt`; `pytest` supports tests. `paramiko` is present but is not a presentation dependency. | Flask may be used only as already configured in a separately authorized UI slice. Paramiko/live access is excluded. |
| Charting | No direct chart library is declared. | Native HTML/CSS summaries are the default. Any library selection and installation require separate authorization. |
| Topology/graph | No direct graph or topology visualization library is declared. | Conditional and deferred behind Section 11.3. |
| Design system/CSS framework | No direct design system or CSS framework is declared. | Do not select or install one by implication. |
| Accessibility tooling | `eslint-config-next` brings JSX accessibility lint dependencies, including transitive `eslint-plugin-jsx-a11y`/`axe-core`; there is no directly declared standalone accessibility test runner. | Existing lint may contribute evidence. Adding axe integration or another runner requires a separate decision. |
| Browser E2E | No direct Playwright, Puppeteer, Selenium, or Vitest browser adapter is declared. Playwright appears only as an optional peer reference in the lockfile. | Browser E2E installation/configuration requires a separate decision. Manual existing-browser review does not authorize a dependency. |
| Unit/source validation | `vitest` is direct and current Python/source tests exist. | Use only when an authorized implementation or review task requires them. Do not treat unit markup rendering as full interactive accessibility proof. |

### 10.2 Gate required before any dependency change

For a chart, graph/topology, design system, CSS framework, accessibility runner,
browser E2E tool, icon set, or visualization package, stop the affected slice and
obtain a separate decision that records:

- the exact unmet reviewer need and why existing HTML/CSS/dependencies are
  insufficient;
- candidate and no-new-dependency alternatives;
- direct/transitive package, license, maintenance, bundle, security, offline, and
  lockfile impact;
- Flask versus Next.js applicability;
- accessibility and fallback behavior;
- test and removal strategy;
- exact allowed files and validation commands.

No approval to evaluate a dependency is approval to install it. Installation must
be explicitly authorized before the affected implementation slice resumes.

## 11. Static topology safety gate

Static topology is excluded from the default Phase 2O sequence. Before it can be
added, a separate future authorization must pass every item below:

| Gate item | Required decision/evidence |
| --- | --- |
| Local source | Identify an approved, committed, bounded local static source and its owner. No dynamically discovered or runtime source is allowed. |
| No live discovery | Prove the view makes no network call and performs no SSH, NETCONF, RESTCONF, API, provider, scanner, inventory refresh, or device access. |
| Sensitive data | Prove credentials, secrets, tokens, management addresses, private device identity, and private environment details are absent. Device labels must be sanitized or de-identified under an explicit rule. |
| Paths and metadata | Exclude internal absolute source paths, usernames, local home paths, and arbitrary raw metadata. |
| Meaning | Label the view `static evidence` with an artifact date. It must not claim current reachability, health, adjacency, configuration, or operational status. |
| Authority | Nodes and edges cannot imply a command, configuration, backup, approval, or execution action. No action control is allowed. |
| Sanitization | Define allowlisted node/edge fields, stable pseudonymous labels, rejection behavior, and negative fixtures for prohibited values. |
| Dependency | Complete Section 10.2 before selecting or installing a graph library. A semantic HTML/SVG alternative must be assessed first. |
| Empty/unavailable | A valid zero-node source says no static topology evidence is available; a missing source says `MISSING`; neither triggers discovery. |
| Accessibility | Supply an equivalent ordered adjacency list or table, meaningful text description, keyboard behavior, focus order, and non-color encoding. |
| Acceptance | Provide source fixture provenance, sanitization tests, prohibited-sentinel tests, no-network/no-execution proof, rendered narrow/wide review, keyboard/accessibility review, and changed-file scope evidence. |

If any gate item cannot be satisfied, defer static topology. Authorization of any
other Phase 2O slice does not authorize this gate or a topology implementation.
If the gate later passes, a separately planned and authorized optional sub-slice
or sequence amendment is required; it is not silently inserted into Phase 2O-01
through Phase 2O-07.

## 12. Final proposed Phase 2O sequence

The sequence retains seven identifiers but revises the placeholder candidate into
explicit framework responsibilities, cross-cutting acceptance, dependency gates,
and a separate closure review. When this Phase 2O-00 sequence was originally
proposed, every later slice was `NOT_AUTHORIZED / NOT_STARTED`. The status table
and Sections 13.1 through 13.8 record the later, separately authorized and
completed Phase 2O-01 through Phase 2O-04 work plus the Phase 2O-05 prerequisite
planning handoff that was current at that historical checkpoint. The handoff at
that time was prerequisite-planning review; it was superseded by the subsequent
implementation, review, fixes, integration, and reconciliation sequence.

| Slice | Mode | Surface | Purpose | Allowed scope | Forbidden scope | Prerequisites | Required acceptance evidence | Separate authorization required |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Phase 2O-01 — Canonical Flask shell and IA foundation | Implementation | Flask | Establish a consistent canonical shell, navigation vocabulary, page hierarchy, focus baseline, and Stage 0 notice pattern. | Flask presentation templates/shared layout and targeted presentation tests/docs only, within an approved file list. | Data discovery, routes, POST, command behavior, report helpers, dependencies, Next.js, topology. | Phase 2O-00 review accepted; exact file/scope decision; clean baseline; no dependency needed. | Canonical identity retained; nav/heading/skip/focus keyboard evidence; narrow/intermediate/wide render review; Stage 0 negative controls; targeted/full validation required by repository rules. | YES |
| Phase 2O-02 — Canonical Flask overview, evidence, and Reports visualization | Implementation | Flask | Make the portfolio conclusion, evidence health, normalized status, report summary, empty/missing states, and safe drilldown easier to review. | Existing Flask summary/evidence data and safe routes; native cards/tables/filter presentation; tests/docs in exact scope. | New evidence source, importer, API, raw/private-field promotion, command behavior, dependencies without gate, topology by default. | 2O-01 accepted; safe-field inventory; selected visualization list; dependency gate if needed. | Data-source-to-field trace, PASS/WARN/FAIL non-color proof, filter keyboard behavior, empty/missing/malformed/error variants, path-sentinel safety tests, responsive/a11y evidence. | YES |
| Phase 2O-03 — Canonical Flask display-only and technical-detail presentation | Implementation | Flask | Clarify Commands, historical records, JSON/detail, AI Checklist, and AI Intent evidence as secondary, non-executing technical/reference content. | Presentation hierarchy/copy/disclosure patterns and targeted tests/docs for existing GET surfaces. | Rendering a Run/form/POST control; modifying runner/routes/log generation; provider/model work; changing execution or evidence policies. | 2O-02 accepted; explicit safe technical-field review; terminology decision for historical logs. | No form/button/run negative proof; safety notice precedes action-like history; detail keyboard/heading/table evidence; long-page and raw-content reflow; existing safe 404/path controls preserved. | YES |
| Phase 2O-04 — Secondary Next.js network shell and Stage 0 IA alignment | Implementation | Next.js | Consolidate the secondary network shell and align navigation, canonical link, terminology, focus, and state taxonomy without changing responsibility. | `app`/network presentation, existing CSS/components, targeted presentation tests/docs in an approved list. | Making Next.js canonical; older `/ai` or `/automation/ai-nodes`; APIs, importers, persistence, provider/model behavior, new dependencies without gate. | 2O-03 accepted; exact surface decision; direct dependency posture rechecked. | Flask remains named canonical; four network destinations remain; shared shell keyboard/heading/skip/focus and viewport evidence; no provider/job/command controls; current routes and APIs unchanged. | YES |
| Phase 2O-05 — Secondary Next.js evidence, Reports, AI Actions, and Jobs visualization | Implementation | Next.js | Improve existing local evidence summaries, safe report metadata, recorded-result hierarchy, Stage 0 unavailable states, and job-record presentation. | Existing component inputs and already-rendered safe fields; native summary/filter/table patterns; targeted tests/docs. | Importer/API/persistence changes; Analyze, Parse, Create Job, Run Job; provider calls; fabricated data; topology by default; dependency installation without gate. | 2O-04 accepted; per-component safe-field matrix; HTTP-200 Reports empty-state contract retained; dependency gate if needed. | Safe metadata sentinel tests; no action-control negative tests; loading/empty/missing/unavailable/error announcement evidence; jobs/evidence narrow-screen semantics; keyboard/focus/contrast review; required repository validation. | YES |
| Phase 2O-06 — Cross-surface responsive, accessibility, and consistency consolidation | Polish and independent verification | Cross-surface | Audit and, only within an explicitly authorized bounded list, remediate residual terminology, responsive, keyboard, focus, semantic, state, and contrast inconsistencies. | Cross-surface presentation-only fixes and acceptance evidence identified by the audit. | First introduction of accessibility requirements; new capability/data behavior; dependency install without gate; topology without Section 11; packaging. | 2O-01 through 2O-05 accepted or explicitly skipped; each prior slice already met Section 9; exact residual issue list; any dependency decision completed first. | Cross-surface route/state matrix; keyboard and viewport replay; semantics/non-color/contrast/focus evidence; regression and no-execution proof; no unresolved blocking presentation inconsistency. | YES |
| Phase 2O-07 — Final user-facing acceptance and phase closure | Review-only | Cross-surface | Independently decide whether the bounded Phase 2O implementation is acceptable and closable with Stage 0 preserved. | Read-only inspection, approved rendered replay, validation, evidence reconciliation, and one closure record if separately authorized. | New implementation, speculative fixes, merge/push/Phase 2P by implication, topology or dependency changes. | Every authorized implementation slice separately accepted; clean review baseline; required evidence available. | Requirement-by-requirement verdict; canonical/secondary replay; empty/error/safety and a11y/responsive evidence; exact tests; diff and repository status; explicit Stage 0/Phase 2P disposition. | YES |

Static topology remains outside this default sequence. Dependency decisions occur
before any installation. Phase 2P can be considered only after a separate accepted
Phase 2O-07 closure and a new explicit authorization.

## 13. Phase 2O-00 acceptance criteria

Phase 2O-00 passed independent documentation review because this document
provides:

- [x] A source-backed Flask and Next.js current-state inventory.
- [x] Explicit canonical Flask and secondary Next.js responsibilities.
- [x] A reviewer-first information architecture and navigation model.
- [x] Visual hierarchy, state, visualization, responsive, and accessibility
  principles grounded in existing sources.
- [x] A final Phase 2O-01 through Phase 2O-07 sequence with explicit surface,
  scope, prerequisites, evidence, and separate-authorization decisions.
- [x] Stage 0 preservation and no runtime or operational authority.
- [x] Dependency decision gates before any selection or installation.
- [x] A conditional static-topology safety gate with deferral as the default when
  evidence is insufficient.
- [x] Responsive and accessibility requirements applied to every implementation
  slice rather than deferred to Phase 2O-06.
- [x] Planning-only, one-document scope with no UI/source/test/dependency/runtime
  implementation.

### 13.1 Phase 2O-01 implementation chronology and handoff

Review acceptance of this planning document did not itself authorize Phase
2O-01. The Phase 2O-01 chronology at reconciliation time was:

1. Phase 2O-01 continuation authorization is `DONE / AUTHORIZED`.
2. The original implementation commit is
   `a2d19722a48eae6f3e8573db0e023bdffdff4ce9`.
3. The original implementation status is `DONE / LOCAL_ONLY`.
4. Independent review of the original implementation returned
   `FAIL_FIX_REQUIRED`.
5. That review found page-level horizontal overflow on `/ai-intent-reviewer` at
   320 CSS pixels, missing regression coverage, and inaccurate documentation
   evidence.
6. The responsive-fix commit is
   `f4a65339cd146b26c0d23810fea992cd6dfea9c6`.
7. The responsive-fix commit status is `DONE / LOCAL_ONLY`.
8. Independent review of the complete two-commit implementation state returned
   `FAIL_FIX_REQUIRED`.
9. That review's technical and safety disposition is `PASS`: source and reflow,
   regression coverage, targeted pytest (`70 passed`), full pytest (`1,884
   passed`), report-index (`14/14 PASS`), rendered review at 320, 768, and 1440
   CSS pixels, keyboard and accessibility review, and server lifecycle all
   passed; it found no functional or safety error and required no accessibility
   or responsive fix.
10. At that point, the sole remaining finding was the stale Phase 2O-01 status
    and handoff chronology in this Phase 2O-00 planning document.
11. Documentation correction commit
    `8fdeeb3dc3e605b5f1a80ea78b441fa982c1efb6` addressed that historical finding
    and subsequently received independent documentation-fix review `PASS`.
12. The first post-review integration-authorization decision verified the
    exact three-commit range as clean, three commits ahead, zero commits behind,
    and strict-fast-forward eligible.
13. That decision nevertheless remained `BLOCKED` because README, the Phase
    2O-01 implementation record, and this planning record still contained stale
    pre-review status or handoff text.
14. Integration-blocker documentation correction commit
    `b7d8ec9e63dd72d7a935ed6228deabfaba072a1a` addressed those blockers and
    received independent review `PASS`.
15. A fresh post-review integration-authorization decision returned
    `AUTHORIZED` for only the exact four-commit range from
    `ecaef4a0655cae10d4ed7154f4948fb4d6982e6c` through
    `b7d8ec9e63dd72d7a935ed6228deabfaba072a1a`, which was four commits ahead,
    zero behind, and strict-fast-forward eligible.
16. Local `main` advanced to the reviewed target by strict fast-forward only,
    without a merge commit, squash, rebase, or cherry-pick.
17. Post-fast-forward validation passed targeted pytest (`14 passed`), full
    pytest (`1,884 passed`, one existing warning), authorized-range
    `git diff --check`, and report-index (`14/14 PASS`).
18. The reviewed target was normally pushed, and remote `main` was proven at
    `b7d8ec9e63dd72d7a935ed6228deabfaba072a1a` before this reconciliation.
19. The fully merged local source branch was safely deleted. No remote branch
    was deleted.
20. This bounded three-file post-merge status reconciliation changes no
    implementation behavior and has not passed independent review.
21. Phase 2O remains `IN_PROGRESS / NOT_READY`.
22. Phase 2O-02 through Phase 2O-07 remain
    `NOT_AUTHORIZED / NOT_STARTED`.
23. Phase 2P remains `NOT_AUTHORIZED / NOT_STARTED`.
24. Stage 0 remains `PRESERVED`.
25. The sole next candidate is one separately authorized
    `PHASE_2O_01_POST_MERGE_STATUS_RECONCILIATION_COMMIT_REVIEW_ONLY` task
    covering only this reconciliation; it does not directly authorize Phase
    2O-02.

This chronology records the completed technical/safety, documentation-fix, and
integration-blocker correction review dispositions as `PASS`, but does not
claim that this post-merge reconciliation has been reviewed. It does not
itself authorize Phase 2O-02, any later Phase 2O slice, or Phase 2P. A later,
separate continuation-authorization decision authorized only the bounded Phase
2O-02 implementation recorded below.

### 13.2 Phase 2O-02 original local implementation handoff

**Original conclusion: `DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_REVIEW`.** The
bounded Phase 2O-02 Flask overview-evidence and reports-visualization
implementation was completed locally on branch
`codex/phase-2o-02-canonical-flask-overview-evidence-reports-visualization` from
base `1c0fe027e547d4fa89f5ad09ca0f924eb9b6763a` in original implementation
commit `0548c6beab80a087ea02d00d49a213dd4336724a`.

The original implementation record used this stable self-reference:

```text
PHASE_2O_02_IMPLEMENTATION_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_IMPLEMENTATION_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_REVIEW_TARGET
```

The original authorized change was limited to exactly seven files:
`dashboard_app.py`, `templates/dashboard_home.html`,
`templates/dashboard_reports.html`,
`tests/test_phase_2o_02_canonical_flask_overview_evidence_and_reports_visualization.py`,
`README.md`, this Phase 2O-00 plan, and the Phase 2O-02 implementation record.
It added only six presentation patterns: a Home conclusion block, seven
category-based Home evidence-health cards corresponding to the existing seven
`build_summary_cards()` category groups, normalized Reports counts, GET-only
status-filter links with a filtered-result count, native disclosure rows that
retain the existing safe GET drill-down path, and deterministic
collection/filter state panels. No category was removed, and no additional
evidence source or field was introduced.

Presentation data is restricted to the approved Home card fields, safe evidence
labels/type/result/availability fields, normalized aggregate counts, the active
status filter, and the collection state. Availability facts are not promoted to
results: for example, `FOUND` remains an availability fact and normalizes to
result `UNKNOWN`. Filter input is allowlisted and invalid values fall back to
`ALL`; a filter no-match is reported separately and does not rewrite the
collection state.

The original implementation validation evidence was:

- `git diff --check`: PASS, with informational Git line-ending warnings only.
- Required affected pytest command: `107 passed`.
- Full pytest: `1,921 passed`, with one existing `GetPassWarning`.
- Report index: `PASS`, with `14/14` reports passing and zero fail, warn,
  missing, or unknown results.
- Rendered `/` and `/reports` review: PASS at 320, 768, and 1440 CSS pixels.
- Reports state/filter review: PASS for `READY`, `EMPTY`, `MISSING`,
  `MALFORMED`, `UNAVAILABLE`, `ERROR`, every allowlisted status filter, invalid
  filter fallback, and filter-no-match handling.
- Responsive/accessibility review: one page-level `h1`, visible conclusion and
  state text, non-color status labels, visible focus, wrapping filter links,
  no page-level horizontal overflow, and wide tables bounded within their own
  scroll wrappers.
- Server lifecycle: the task-owned loopback servers were stopped and TCP port
  5000 was proven released.

No route, method, POST path, form, button, JavaScript action, dependency,
evidence source, execution path, topology, Next.js surface, or operational
authority was added. Stage 0 and all repository safety boundaries remained
preserved. At this original handoff, the sole next candidate was independent
review of the exact Phase 2O-02 implementation commit.

### 13.3 Phase 2O-02 bounded review-finding correction

**Correction conclusion when created: `DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_FIX_REVIEW`.**
Independent review targeted original implementation commit
`0548c6beab80a087ea02d00d49a213dd4336724a` and returned
`FAIL_FIX_REQUIRED` for exactly two findings:

1. Mixed collections with usable evidence were globally downgraded to
   `MALFORMED` or `UNAVAILABLE` instead of remaining `READY` while degraded
   counts stayed visible.
2. This Phase 2O-00 record and the Phase 2O-02 implementation record stated an
   incorrect count of three for the Home evidence-health cards even though the
   existing implementation renders seven category-based cards.

The bounded fix was applied locally and committed as
`00862075494bc7a76dd478bee9d1742d53d43167` in exactly four files:

1. `dashboard_app.py`
2. `tests/test_phase_2o_02_canonical_flask_overview_evidence_and_reports_visualization.py`
3. `docs/phase_2o/phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md`
4. `docs/phase_2o/phase_2o_02_canonical_flask_overview_evidence_and_reports_visualization_implementation.md`

The review-fix commit uses this stable self-reference:

```text
PHASE_2O_02_REVIEW_FIX_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_REVIEW_FIX_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_FIX_REVIEW_TARGET
```

The corrected collection model treats safely available `PASS`, `WARN`, `FAIL`,
and `UNKNOWN` results as usable reviewer evidence. A non-empty mixed collection
with any such entry remains `READY`; wholly unusable safely available malformed
evidence is `MALFORMED`; otherwise a non-empty collection without usable safe
evidence is `UNAVAILABLE`. `ERROR`, `MISSING`, and `EMPTY` retain their explicit
conditions. Malformed, unavailable, missing, and unknown counts remain visible.

Final bounded fix validation passed with exactly four modified files,
`git diff --check`, `114` affected pytest tests, `1,928` full pytest tests with
one existing warning, report-index `14/14 PASS`, and rendered `/` and `/reports`
review at 320, 768, and 1440 CSS pixels. The rendered matrix covered every
required degraded and mixed state, every status filter, invalid fallback, and
filter-no-match; it found no page-level overflow, raw error, action control, or
console issue. Native disclosure behavior, explicit non-color labels, rendered
focus rules, headings, landmarks, and bounded table overflow remained intact.
All three task-owned servers stopped and ports 5000 through 5002 were released.

The seven existing Home card categories are preserved and behaviorally checked
by their rendered titles. No dependency, route, route method, POST behavior,
safe-view boundary, evidence source, importer, action control, or execution path
was added or expanded. The independent bounded-fix review later returned
`PASS`; the cumulative Phase 2O-02 implementation was therefore `ACCEPTED`.

### 13.4 Phase 2O-02 integration and post-merge status reconciliation

**Historical conclusion at the completion of Phase 2O-02:** Phase 2O-02 was
`DONE / ACCEPTED / MERGED_TO_MAIN / SYNCHRONIZED`. Its bounded implementation
and review-fix target `00862075494bc7a76dd478bee9d1742d53d43167` had been
integrated by strict fast-forward. The post-merge reconciliation commit
`10cec5ca1911140decdba7b84f54667698dcedae` was pushed, synchronized, and
independently reviewed `PASS`.

The accepted Phase 2O-02 history changed no route, execution, provider, model,
live-device, or Stage 0 boundary. At that historical point, Phase 2O remained
`IN_PROGRESS / NOT_READY`; Phase 2O-04 through Phase 2O-07 and Phase 2P were
`NOT_AUTHORIZED / NOT_STARTED`; and Stage 0 remained `PRESERVED`.

**Later controlling chronology:** A separate continuation decision used the
accepted Phase 2O-02 state only as the base for bounded Phase 2O-03. Phase
2O-03 was independently reviewed, integrated, and synchronized. A later,
separate decision authorized Phase 2O-04. Phase 2O-04 implementation commit
`2643b24497011ea31c507d6f567daf5f20287a5d` was completed locally and
independently reviewed `FAIL_FIX_REQUIRED` because of documentation accuracy
findings; its technical and safety result was `PASS`. At that review point, it
was not accepted, merged, pushed, synchronized, or closed. Second documentation
fix commit `7153cb9bcd328489057012a66dc5777e32cc0b26` later received independent
review `PASS`, making the cumulative Phase 2O-04 implementation
`ACCEPTED / LOCAL_ONLY` at that historical pre-integration point. Subsequent
status corrections `1e6561344b53161da85dac0e912bfead425af125` and
`bc8b22934191187c18f1c1fc3c498cc2cc03c30f`, plus Phase 2O-00 handoff
reconciliation `413814ceefe5160cecda6bcfdd5c0f24c05cdcbb`, received independent
`PASS` reviews. Fresh authorization then allowed strict-fast-forward integration
from `93cf3bba0c74e7eec685dbc1f7925c0ceca218c7` through
`413814ceefe5160cecda6bcfdd5c0f24c05cdcbb`; the non-force push,
synchronization, and safe local source-branch cleanup completed. The later
post-merge reconciliation commit `5fc25f9035ee23ee98147e15caeb044e3ed405ba`
completed the Phase 2O-04 record on `main`; Phase 2O-04 is now
`DONE / MERGED_TO_MAIN / SYNCHRONIZED / RECONCILED`. At that historical
checkpoint, a continuation decision identified Phase 2O-05 as the sole candidate
but withheld implementation authorization pending the prerequisite evidence now
recorded in Section 13.8. The handoff at that time kept Phase 2O
`IN_PROGRESS / NOT_READY` and Phase 2O-05 implementation, Phase 2O-06 through
Phase 2O-07, and Phase 2P `NOT_AUTHORIZED / NOT_STARTED`, with Stage 0
`PRESERVED`. This was superseded by the subsequent Phase 2O-05 implementation,
review, fixes, integration, and reconciliation sequence.

### 13.5 Phase 2O-03 bounded implementation handoff

**Historical handoff at fix creation:** The original Phase 2O-03 implementation commit
`d18e6ccac87e45e7cc983bb09be1c50f07c0c6c2` received independent review
`FAIL_FIX_REQUIRED`. The strictly bounded five-file correction is complete in
this commit and is `DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_FIX_REVIEW`; it
did not claim at that handoff that the fix had passed independent review.

The first Phase 2O-03 implementation attempt stopped before editing with
`EXACT_SCOPE_TEST_CONTRACT_CONFLICT`; it modified no file and created no commit.
A separate scope-correction decision authorized visible-label expectation
updates in exactly two existing regression tests. The corrected implementation
scope is exactly fourteen files: `dashboard_app.py`, seven named Flask
templates, the new Phase 2O-03 test, the two existing label-regression tests,
`README.md`, this plan, and the Phase 2O-03 implementation record. No wildcard,
fifteenth file, dependency, or lockfile is authorized.

The controlling active label is `Historical Execution Records`. Superseded
visible labels are removed without hidden compatibility content, and every
existing route, navigation, accessibility, Stage 0, no-form, no-button, and
zero-execution test assertion remains active. The selected implementation adds
conclusion-first display-only notices, bounded historical summaries, sanitized
and truncated output previews, fixed allowlisted JSON summary projection,
bounded subordinate JSON detail, static AI Checklist evidence, historical or
design-time AI Intent evidence, semantic tables/lists, native disclosures,
visible focus, and narrow-screen reflow.

Safe technical data is limited to fixed copy, approved command labels and
descriptions, static examples, bounded record identifiers, normalized statuses,
recorded timestamps and result indicators, sanitized bounded output/JSON,
fixed checklist and reviewer evidence labels, and approved repository-relative
references. Absolute/private paths, usernames, environment values, secrets,
provider/model configuration, unrestricted arguments, arbitrary input, raw
exceptions, tracebacks, unbounded output, private/management addresses,
configuration content, topology, and mutable execution state remain prohibited.

The implementation introduces no route or HTTP-method change, POST behavior,
form, action control, runner/registry/log/report/persistence behavior change,
provider/API/model integration, job/importer, queue/scheduler/broker/worker,
SSH/NETCONF/RESTCONF/live-device path, dependency, Next.js change, later slice,
or Phase 2P authority. Stage 0 remains `PRESERVED`.

The original green validation did not establish the complete safe-display
contract. Independent review found that provider/model-identifying fields could
remain visible in nested structured JSON detail and historical output, and that
Windows private paths containing spaces could be only partially redacted. It
also found missing exact-boundary and indirect no-side-effect tests, two
unauthorized negative terminology assertions in the historical Phase 2N-04
test, insufficient rendered disclosure/reflow evidence, and stale handoff
status in the Phase 2O records.

This correction is limited to `dashboard_app.py`, the dedicated Phase 2O-03
test, the Phase 2N-04 historical label test, this plan, and the Phase 2O-03
implementation record. Provider/model keys are normalized across casing and
separator variants and omitted recursively from structured detail. Historical
provider/model field-value forms use fixed-value redaction. Quoted and
unquoted Windows private paths, including paths with spaces and forward or
backward separators, are fully replaced by a fixed private-path marker.

The dedicated tests now cover nested provider/model fields, allowed-field
survival, helper and rendered historical redaction, complete spaced-path
redaction, exact and one-over line/character/JSON bounds, indirect forbidden
GET primitives, active terminology negatives, and rendered closed native
disclosures with focus and bounded reflow contracts. The Phase 2N-04 test
removes exactly the two unauthorized negative assertions while retaining the
positive `Historical Execution Records` assertion and all pre-existing safety
negatives.

The review-fix commit uses this stable self-reference:

```text
PHASE_2O_03_REVIEW_FIX_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_REVIEW_FIX_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_FIX_REVIEW_TARGET
```

The fix task's final result is the authoritative source for the exact review-fix
SHA and validation results. That commit added no route, method, action control,
provider/model runtime, execution behavior, dependency, or live path. Stage 0
remained `PRESERVED`. At that historical handoff, the sole next candidate was
independent review of the exact Phase 2O-03 bounded review-fix commit, and
Phase 2O-04, push, merge, pull request, integration, and Phase 2P were
unauthorized. Section 13.6 records the later controlling review and integration
outcome.

### 13.6 Phase 2O-03 integration and post-merge status reconciliation

**Historical reconciliation handoff:** When the Phase 2O-03 post-merge
reconciliation commit was created, independent review of bounded fix commit
`9ff474822a94d0f79ff45b061af590186b425def` had returned `PASS`, the cumulative
Phase 2O-03 implementation was `ACCEPTED`, and local `main` had advanced from
base `10cec5ca1911140decdba7b84f54667698dcedae` to that accepted target by strict
fast-forward only. The accepted target was normally pushed and verified on
trusted `origin/main`. At that handoff, the reconciliation commit itself was
ready for independent review; that historical statement was not a claim that
its future review had already passed.

Before the first push, accepted-range `git diff --check` passed, the exact
seven-file targeted suite passed `129` tests, full pytest passed `1,943` tests
with one existing terminal warning, and report-index passed `14/14`. Focused
synthetic checks also passed for structured provider/model removal, historical
provider/model redaction, Windows private paths containing spaces and suffix
removal, output and JSON boundaries, and source immutability. No full browser
matrix was required because the accepted target had already passed independent
browser review and the focused checks revealed no contradiction.

Fresh remote verification proved trusted `origin/main` at accepted target
`9ff474822a94d0f79ff45b061af590186b425def`. The fully merged local source
branch was then deleted with the safe non-force operation; no remote source
branch was created or deleted. The integration used no merge commit, squash,
rebase, cherry-pick, reset, tag, release, or force push.

That reconciliation changed only README and the two applicable Phase 2O
records. It changed no application, template, test, dependency, workflow,
configuration, route, method, action control, runner, provider/model runtime,
execution behavior, or live-device boundary. At that historical handoff,
Stage 0 remained `PRESERVED`; Phase 2O remained `IN_PROGRESS / NOT_READY`; and
Phase 2O-04 through Phase 2O-07 and Phase 2P were
`NOT_AUTHORIZED / NOT_STARTED`.

The reconciliation commit uses this stable self-reference because a commit
cannot contain its own final SHA:

```text
PHASE_2O_03_POST_MERGE_RECONCILIATION_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_RECONCILIATION_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_POST_MERGE_REVIEW_TARGET
```

The reconciliation task's final result is the authoritative source for that
commit's exact SHA and second-push result. A later independent reconciliation
review returned `PASS` with no material findings. The controlling current
Phase 2O-03 state is therefore
`DONE / REVIEWED / MERGED_TO_MAIN / SYNCHRONIZED`. A later, separate
continuation decision authorized the bounded Phase 2O-04 implementation.
Section 13.7 records its current review and correction state; the historical
Phase 2O-03 handoff is not the current next candidate.

### 13.7 Phase 2O-04 bounded implementation handoff

**Current conclusion:** Phase 2O-04 cumulative implementation is
`ACCEPTED / MERGED_TO_MAIN`. Implementation commit
`2643b24497011ea31c507d6f567daf5f20287a5d` received independent review
`FAIL_FIX_REQUIRED` only for documentation accuracy; its technical, source,
test, safety, and rendered results were `PASS`. First documentation fix
`4546f3f441ecaa14f208eee928da33b0ac9b5769` received independent review
`FAIL_FIX_REQUIRED`, while second documentation fix
`7153cb9bcd328489057012a66dc5777e32cc0b26` received independent review
`PASS`. Later corrections `1e6561344b53161da85dac0e912bfead425af125`,
`bc8b22934191187c18f1c1fc3c498cc2cc03c30f`, and
`413814ceefe5160cecda6bcfdd5c0f24c05cdcbb` also received independent `PASS`
reviews. A fresh decision authorized integration; strict-fast-forward
integration, non-force push, three-ref synchronization, and safe local
source-branch cleanup are complete. Post-merge reconciliation commit
`5fc25f9035ee23ee98147e15caeb044e3ed405ba` completed the Phase 2O-04 record on
`main`; Phase 2O-04 is `DONE / MERGED_TO_MAIN / SYNCHRONIZED / RECONCILED`.
The implementation's presentation-only change gives the four existing `/network/*`
routes one shared secondary Next.js Stage 0 shell, continues to name the Flask
dashboard at `http://127.0.0.1:5000/` as canonical, and preserves the
report-only, dry-run, mock-only, demo-only, and non-executing boundary. At that
historical Phase 2O-04 handoff, Phase 2O was `IN_PROGRESS / NOT_READY`, while
Phase 2O-05 implementation, Phase 2O-06 through Phase 2O-07, and Phase 2P were
`NOT_AUTHORIZED / NOT_STARTED`. This was superseded by the subsequent Phase
2O-05 implementation, review, fixes, integration, and reconciliation sequence.

The first implementation attempt stopped with
`EXACT_SCOPE_TEST_CONTRACT_CONFLICT`. A separate scope-correction decision
authorized only `components/network/ReportsClient.test.tsx`, accepted the
preserved eight-file dirty state, and raised the cumulative maximum from 11 to
12 files. The corrected test assigns `NetworkNav` rendering to
`app/network/layout.tsx` and verifies that the Reports route does not duplicate
it while retaining the route, importer, HTTP-200, metadata-only, empty-state,
package-integrity, and negative-safety contracts.

The shared shell contains no `<main>` and no data, importer, API, provider,
model, persistence, job, or execution logic. Each route retains its existing
data/importer call and client component, with exactly one route-level `<main>`,
one page `<h1>`, the shared skip target, exact four-link navigation, and
`aria-current="page"`. The shell distinguishes `EMPTY`, `MISSING`,
`UNAVAILABLE`, `ERROR`, and `BLOCKED` without broadening any capability.

Targeted validation passed 3 Reports tests and 14 Phase/safety tests. Full
Vitest passed 70 tests; typecheck, zero-warning lint, the Next.js 25/25-page
production build, 1,943 pytest tests with one documented terminal warning, and
report-index 14/14 passed. The independent implementation review also passed
all 1,943 pytest tests and reproduced zero warnings; that warning-count
discrepancy was non-material. Browser QA of all four routes at 320, 768, and
1440 CSS px found one main and one H1 per route, correct current-route
semantics, visible focus, working primary-content skip behavior, readable state
vocabulary, bounded dense content, no page-level horizontal overflow, no
execution-style control, no framework overlay, and no console warning/error.
Native 400% zoom was not available and was not substituted with a 320
CSS-pixel viewport.

No dependency, lockfile, route path or method, API route, importer, data source,
runtime, persistence, provider/model call, job/command control, queue, scheduler,
worker, agent loop, SSH/NETCONF/RESTCONF/live-device behavior, configuration
backup/change, production execution path, topology, or older AI workbench was
changed. Stage 0 remains `PRESERVED`.

The implementation commit uses a stable self-reference because a commit cannot
contain its own final SHA:

```text
PHASE_2O_04_IMPLEMENTATION_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_IMPLEMENTATION_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_REVIEW_TARGET
```

The implementation task's final result is the authoritative source for the
exact implementation commit SHA. The implementation review was completed
against `2643b24497011ea31c507d6f567daf5f20287a5d` and returned
`FAIL_FIX_REQUIRED` solely for the stale status wording described above; it did
not authorize integration, push, merge, synchronization, closure, or a later
phase.

The first bounded documentation correction used this stable self-reference:

```text
PHASE_2O_04_DOCUMENTATION_REVIEW_FIX_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_DOCUMENTATION_REVIEW_FIX_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_FIX_REVIEW_TARGET
```

Its final task result identified the exact first correction commit as
`4546f3f441ecaa14f208eee928da33b0ac9b5769`. Independent review of that commit
returned `FAIL_FIX_REQUIRED` for the sole remaining finding named above. That
review did not authorize integration, push, merge, synchronization, closure, or
a later phase.

The second bounded documentation correction used a distinct stable
self-reference because a commit cannot contain its own final SHA:

```text
PHASE_2O_04_SECOND_DOCUMENTATION_REVIEW_FIX_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_SECOND_DOCUMENTATION_REVIEW_FIX_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_SECOND_FIX_REVIEW_TARGET
```

At that historical handoff, the second correction status was
`DONE / LOCAL_ONLY / READY_FOR_INDEPENDENT_SECOND_FIX_REVIEW`, and the sole next
candidate was
`PHASE_2O_04_SECOND_BOUNDED_DOCUMENTATION_REVIEW_FIX_COMMIT_REVIEW_ONLY`.
The final task result identified the exact correction commit as
`7153cb9bcd328489057012a66dc5777e32cc0b26`; its later independent review
returned `PASS`, making the cumulative Phase 2O-04 implementation
`ACCEPTED / LOCAL_ONLY` at that historical pre-integration point.

A first integration-authorization decision returned `NOT_AUTHORIZED` because
README and the Phase 2O-04 implementation record still contained obsolete
current handoffs. Post-authorization documentation-status correction commit
`1e6561344b53161da85dac0e912bfead425af125` corrected those handoffs and
received independent review `PASS`. A later authorization decision remained
`NOT_AUTHORIZED` because the current handoff still routed reviewers to that
completed review. Stable external-review handoff fix commit
`bc8b22934191187c18f1c1fc3c498cc2cc03c30f` established the non-recursive
conditional gate and received independent exact-commit review `PASS`. The most
recent pre-integration authorization decision still returned `NOT_AUTHORIZED`
because this Phase 2O-00 record retained the competing stale current handoff
historicalized above.

Phase 2O-00 handoff reconciliation commit
`413814ceefe5160cecda6bcfdd5c0f24c05cdcbb` resolved that final stale handoff.
Its independent exact-commit review returned `PASS` with zero material findings,
and the next fresh integration-authorization decision returned `AUTHORIZED`.
Local `main` then advanced by strict fast-forward from
`93cf3bba0c74e7eec685dbc1f7925c0ceca218c7` to
`413814ceefe5160cecda6bcfdd5c0f24c05cdcbb`. Required post-fast-forward
validation passed. The integrated commit was pushed to `origin/main` using the
exact non-force `refs/heads/main:refs/heads/main` refspec, after which local
`main`, local tracking `origin/main`, and remote `main` matched. The fully merged
local source branch was safely deleted; no remote source branch was deleted.

The bounded three-document post-merge status reconciliation used a stable
self-reference because a commit cannot contain its own final SHA:

```text
PHASE_2O_04_POST_MERGE_STATUS_RECONCILIATION_COMMIT_REFERENCE:
THIS_COMMIT

EXACT_POST_MERGE_STATUS_RECONCILIATION_COMMIT_SHA_SOURCE:
FINAL_TASK_RESULT_AND_INDEPENDENT_POST_MERGE_REVIEW_TARGET
```

The final task result identified that reconciliation commit as
`5fc25f9035ee23ee98147e15caeb044e3ed405ba`; it is now the completed `main`
baseline. Its former conditional handoff is historical and does not compete
with the Phase 2O-05 implementation-review handoff that followed at that
historical checkpoint. That handoff was superseded by the subsequent Phase
2O-05 fixes, integration, reconciliation, and reconciliation review. The
completed Phase 2O-04 work was not used as authority for Phase 2O-05
implementation or integration.

### 13.8 Phase 2O-05 prerequisite safe-field matrix and bounded-scope planning

**Historical planning conclusion:** Phase 2O-05 prerequisite planning completed
and received independent review `PASS`. The
[controlling prerequisite plan](phase_2o_05_secondary_nextjs_evidence_reports_ai_actions_and_jobs_visualization_planning_only.md)
contains 109 field-level decisions across Evidence, Reports, AI Actions, and
Jobs, exact repository evidence, the retained HTTP-200 Reports empty-state
contract, dependency decision `NO`, an exact future 14-file boundary, explicit
exclusions, state/UX contracts, and automated/rendered validation requirements.

This planning task changed no application behavior. Its review-fix chain ended at
exact candidate `3a45e7fa7f5af1a36d57487b56192dae0f66ea87`, and the later fresh
implementation-authorization decision independently authorized one exact
14-file implementation task from that candidate. That external decision did not
reuse the previously invalidated authorization.

```text
PHASE_2O_05_PREREQUISITE_PLANNING_COMMIT:
3a45e7fa7f5af1a36d57487b56192dae0f66ea87

PREREQUISITE_PLANNING_REVIEW:
PASS / EXTERNAL RESULT
```

The prerequisite planning result remains historical evidence for the bounded
implementation below. Its former local-only and conditional-review handoffs do
not compete with the completed implementation, review, and integration history.
It does not independently authorize a later slice or live/production capability.

### 13.9 Phase 2O-05 bounded secondary Next.js visualization implementation

**Current conclusion:** Phase 2O-05 is `INTEGRATED_AND_SYNCHRONIZED /
FINAL_DOCUMENTATION_RECONCILIATION_IN_PROGRESS`. Its implementation is
`ACCEPTED`, and the reconciliation-fix review passed with zero material
findings. This final status correction is local-only and awaits independent
review; Phase 2O-05 is not closed.

The implementation applies one pure fail-closed presentation boundary to the
existing Evidence, Reports, AI Actions, and Jobs clients. Only approved fixed
projections from the singular 109-row matrix are visible. Unknown or malformed
records use explicit `REJECTED`, `ERROR`, or unavailable states; raw payloads,
arbitrary object keys, source paths, device identity, user text, provider/model
identity, secrets, commands, arguments, tracebacks, and operational detail are
not rendered.

The Reports HTTP-200 empty state and existing GET-only recorded-data reads are
preserved. The implementation adds no dependency, route, API, importer, schema,
store, persistence, provider/model call, secret handling, Analyze/Parse/Create
Job/Run control, queue, scheduler, worker, runner, polling loop, live-device
access, SSH, NETCONF, RESTCONF, configuration backup/change, or production
execution path. Stage 0 remains `PRESERVED`.

```text
AUTHORIZED_IMPLEMENTATION_BASE:
3a45e7fa7f5af1a36d57487b56192dae0f66ea87

PHASE_2O_05_IMPLEMENTATION_COMMIT:
a4761d89cb63a22ea104dd5e18082e3c5f2765f0

PHASE_2O_05_FIRST_BOUNDED_FIX_COMMIT:
120ef3096e86b7a3045495271486b78845d6f6e6

PHASE_2O_05_SECOND_BOUNDED_FIX_AND_INTEGRATED_MAIN_TIP:
236488db9ac320f73b96172961648b33e36e500c

PHASE_2O_05_IMPLEMENTATION_STATUS:
ACCEPTED

PHASE_2O_05_INTEGRATION_STATUS:
DONE / MERGED_TO_MAIN / PUSHED / SYNCHRONIZED /
SAFE_LOCAL_BRANCH_CLEANUP_COMPLETE

HISTORICAL_PHASE_2O_05_POST_MERGE_RECONCILIATION_COMMIT:
47a92b9cedeee6a25b5d5cfa502158290221736d

HISTORICAL_PHASE_2O_05_POST_MERGE_RECONCILIATION_REVIEW_RESULT:
FAIL_FIX_REQUIRED /
P2O05-RECON-REV-001 /
P2O05-RECON-REV-002

PHASE_2O_05_RECONCILIATION_FIX_COMMIT:
c5c720d17919e2246d88cb8699341f24b8aec641

PHASE_2O_05_RECONCILIATION_REVIEW_STATUS:
PASS / ZERO MATERIAL FINDINGS

PHASE_2O_05_FINAL_DOCUMENTATION_RECONCILIATION_STATUS:
DONE / LOCAL_ONLY /
READY_FOR_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW

PHASE_2O_05_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REFERENCE:
THIS_COMMIT

PHASE_2O_05_CLOSURE_STATUS:
NOT_CLOSED /
PENDING_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW

CURRENT_HANDOFF:
READY_FOR_INDEPENDENT_FINAL_DOCUMENTATION_RECONCILIATION_COMMIT_REVIEW
```

Original implementation commit `a4761d89cb63a22ea104dd5e18082e3c5f2765f0`
received independent finding `P2O05-REV-001`. Responsive fix
`120ef3096e86b7a3045495271486b78845d6f6e6` resolved it, and the first-fix
review identified `P2O05-FIX-REV-001` and `P2O05-FIX-REV-002`. Second bounded
fix `236488db9ac320f73b96172961648b33e36e500c` resolved both findings and
received a final independent review `PASS` with zero material findings.

Local `main` reached that tip by strict fast-forward only, without a merge
commit, squash, rebase, or cherry-pick. The main push was non-force, and local
`main`, local tracking `origin/main`, and actual remote `main` were synchronized
at the integrated tip when integration completed. The fully merged local source
branch was safely deleted; no remote branch was deleted.

The historical four-document reconciliation commit
`47a92b9cedeee6a25b5d5cfa502158290221736d` received independent review result
`FAIL_FIX_REQUIRED` for `P2O05-RECON-REV-001` and
`P2O05-RECON-REV-002`. This bounded documentation fix addresses only those
findings and used `THIS_COMMIT` because it could not contain its own final SHA.
Its later independent review passed with zero material findings; integration,
non-force push, synchronization, and safe local cleanup then completed. A final
closeout review found four stale current handoffs, and this authorized four-file
correction resolves only those statements. Its current handoff is independent
review of this local-only final documentation reconciliation commit. It
authorizes no integration, merge, push, remote contact,
branch cleanup, Phase 2O-06, Phase 2O-07, Phase 2P, or live/production
capability.

Phase 2O remains `IN_PROGRESS / NOT_READY`; Phase 2O-06 through Phase 2O-07 and
Phase 2P remain `NOT_AUTHORIZED / NOT_STARTED`.

## 14. Explicit exclusions and deferred work

The following remain excluded and unauthorized:

- UI implementation, CSS changes, component changes, shared-layout changes, or
  visual token implementation in Phase 2O-00.
- New or modified routes, APIs, POST behavior, tests, workflows, fixtures,
  screenshots, mockups, reports, exports, or runtime artifacts.
- Dependency selection, installation, removal, upgrade, or lockfile change.
- Provider, model, external API, AI runtime, secrets, or credentials integration.
- Analyze, Parse, Create Job, job advancement, command submission, command
  execution, runner, adapter, importer, or persistence advancement.
- Scheduler, queue, broker, worker, agent loop, or production execution path.
- Live-device access; SSH, NETCONF, RESTCONF; network discovery; configuration
  backup; configuration change; reset, reboot, enable, disable, or deployment.
- Day 1–160 rewrites or replacement and any second safety matrix.
- Static topology unless the separate Section 11 gate and a later implementation
  authorization both pass.
- Any further packaging, distribution, deployment, publication, merge, push,
  pull request, branch cleanup, or Phase 2P work not explicitly authorized by a
  separate task.
- Phase 2O-06 through Phase 2O-07 implementation until each applicable slice
  receives its own fresh explicit authorization.

## 15. Documentation readability review

- The conclusion and authorization boundary appear first.
- Phase purpose, allowed presentation work, and forbidden operational work are
  separated.
- Current facts cite repository files or Phase 2N records; recommendations and
  assumptions are labeled.
- `DONE / REVIEWED / MERGED_TO_MAIN / SYNCHRONIZED`, `FAIL_FIX_REQUIRED`,
  `ACCEPTED / MERGED_TO_MAIN`, `CONDITIONAL_EXTERNAL_REVIEW_GATE`,
  `IN_PROGRESS / NOT_READY`, `NOT_AUTHORIZED / NOT_STARTED`, and `PRESERVED`
  are used consistently.
- Flask canonical and Next.js secondary terminology matches the Phase 2N closure.
- Acceptance criteria and later-slice evidence are concrete and verifiable.
- Long findings are split into sections and tables.
- No historical status is presented as current operational authority.
- No implementation behavior, safety override, second safety matrix, or Phase 2P
  authority is introduced.
