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
| `PHASE_2O_01_IMPLEMENTATION_STATUS` | `DONE / LOCAL_ONLY` |
| `PHASE_2O_01_IMPLEMENTATION_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_01_RESPONSIVE_FIX_COMMIT` | `f4a65339cd146b26c0d23810fea992cd6dfea9c6` |
| `PHASE_2O_01_FIX_COMMIT_STATUS` | `DONE / LOCAL_ONLY` |
| `PHASE_2O_01_FIX_REVIEW_DECISION` | `FAIL_FIX_REQUIRED` |
| `PHASE_2O_01_TECHNICAL_AND_SAFETY_DISPOSITION` | `PASS` |
| `PHASE_2O_01_REMAINING_FINDING` | `STALE_PHASE_2O_00_STATUS_AND_HANDOFF_DOCUMENTATION` |
| `PHASE_2O_01_STATUS` | `DONE / DOCUMENTATION_FIX_APPLIED / READY_FOR_REVIEW / LOCAL_ONLY` |
| `PHASE_2O_IMPLEMENTATION_STATUS` | `IN_PROGRESS / NOT_READY` |
| `PHASE_2O_02_THROUGH_2O_07_STATUS` | `NOT_AUTHORIZED / NOT_STARTED` |
| `PHASE_2P_STATUS` | `NOT_AUTHORIZED / NOT_STARTED` |
| `STAGE_0_BOUNDARY` | `PRESERVED` |
| `NEXT_CANDIDATE` | `PHASE_2O_01_DOCUMENTATION_STATUS_FIX_COMMIT_REVIEW_ONLY` |

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
and a separate closure review. All entries are `NOT_AUTHORIZED / NOT_STARTED`.

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
2O-01. The complete current chronology is:

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
10. The sole remaining finding was the stale Phase 2O-01 status and handoff
    chronology in this Phase 2O-00 planning document.
11. After this one-file correction is committed, the Phase 2O-01 status is
    `DONE / DOCUMENTATION_FIX_APPLIED / READY_FOR_REVIEW / LOCAL_ONLY`.
12. No Phase 2O-01 commit is merged or pushed.
13. Phase 2O remains `IN_PROGRESS / NOT_READY`.
14. Phase 2O-02 through Phase 2O-07 remain
    `NOT_AUTHORIZED / NOT_STARTED`.
15. Phase 2P remains `NOT_AUTHORIZED / NOT_STARTED`.
16. Stage 0 remains `PRESERVED`.
17. The sole next candidate is one separately authorized
    `PHASE_2O_01_DOCUMENTATION_STATUS_FIX_COMMIT_REVIEW_ONLY` task.

This chronology does not claim that the complete Phase 2O-01 state has review
`PASS`, does not authorize integration, merge, or push, and does not authorize
Phase 2O-02.

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
- Packaging, distribution, deployment, publication, merge, push, pull request,
  branch cleanup, and all Phase 2P work.
- Phase 2O-02 through Phase 2O-07 implementation until each applicable slice
  receives its own fresh explicit authorization.

## 15. Documentation readability review

- The conclusion and authorization boundary appear first.
- Phase purpose, allowed presentation work, and forbidden operational work are
  separated.
- Current facts cite repository files or Phase 2N records; recommendations and
  assumptions are labeled.
- `DONE / REVIEWED / MERGED_TO_MAIN`, `IN_PROGRESS / NOT_READY`,
  `NOT_AUTHORIZED / NOT_STARTED`, and `PRESERVED` are used consistently.
- Flask canonical and Next.js secondary terminology matches the Phase 2N closure.
- Acceptance criteria and later-slice evidence are concrete and verifiable.
- Long findings are split into sections and tables.
- No historical status is presented as current operational authority.
- No implementation behavior, safety override, second safety matrix, or Phase 2P
  authority is introduced.
