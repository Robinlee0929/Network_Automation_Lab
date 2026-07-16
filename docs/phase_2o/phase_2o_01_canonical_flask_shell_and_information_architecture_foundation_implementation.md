# Phase 2O-01 Canonical Flask Shell and Information Architecture Foundation

## 1. Conclusion and authorization boundary

**Status: `DONE / FIX_APPLIED / READY_FOR_REVIEW / LOCAL_ONLY`.** Original
implementation commit `a2d19722a48eae6f3e8573db0e023bdffdff4ce9`
established the shared Jinja shell, but its independent implementation review
returned `FAIL_FIX_REQUIRED`. The review reproduced page-level horizontal
overflow on `/ai-intent-reviewer` at 320 CSS pixels and found the original
responsive documentation and regression-test evidence insufficient.

The bounded local fix applies a narrow long-identifier wrapping contract and
adds source/rendered-contract regression coverage. It is not independently
reviewed, merged, or pushed. The controlling 320 CSS pixel evidence passes;
supplementary browser-native 400% evidence at a narrower 267 CSS pixel content
width fails and is disclosed as non-controlling. A later independent review
must repeat rendered validation and decide whether the controlling 320 CSS
pixel result satisfies the Phase 2O acceptance boundary.

Starting `main` was
`ecaef4a0655cae10d4ed7154f4948fb4d6982e6c`. Stage 0 remains `PRESERVED`.
Phase 2O remains `IN_PROGRESS / NOT_READY`. Phase 2O-02 through Phase 2O-07 and
Phase 2P remain `NOT_AUTHORIZED / NOT_STARTED`. The sole next candidate is one
separately authorized `PHASE_2O_01_IMPLEMENTATION_FIX_COMMIT_REVIEW_ONLY` task.

This implementation grants no merge, push, provider, model, API, POST, command,
runner, device, configuration, packaging, or production authority.

## 2. Original implementation and bounded-fix inventories

The original implementation changed-file inventory was:

Created:

- `templates/dashboard_base.html`
- `tests/test_phase_2o_01_canonical_flask_shell_and_ia_foundation.py`
- `docs/phase_2o/phase_2o_01_canonical_flask_shell_and_information_architecture_foundation_implementation.md`

Modified:

- `templates/dashboard_home.html`
- `templates/dashboard_reports.html`
- `templates/dashboard_commands.html`
- `templates/dashboard_command_logs.html`
- `templates/dashboard_command_log.html`
- `templates/dashboard_ai_checklist.html`
- `templates/dashboard_ai_intent_reviewer.html`
- `templates/dashboard_json_preview.html`
- `README.md`
- `docs/phase_2o/phase_2o_00_ux_ui_baseline_and_information_architecture_planning_only.md`

No other file is part of this implementation.

The later bounded fix modifies exactly:

- `templates/dashboard_ai_intent_reviewer.html`
- `tests/test_phase_2o_01_canonical_flask_shell_and_ia_foundation.py`
- `README.md`
- `docs/phase_2o/phase_2o_01_canonical_flask_shell_and_information_architecture_foundation_implementation.md`

The original shared base, the other seven migrated templates, runtime code,
routes, helpers, dependencies, pre-Phase-2O-01 tests, Next.js, workflows, and
configuration remain unchanged by the fix.

## 3. Shared base-template design

`templates/dashboard_base.html` owns the HTML document, language and viewport
metadata, canonical Network Automation Lab identity, skip link, one primary
navigation landmark, persistent Stage 0 notice, exactly one main landmark,
shared embedded CSS, focus treatment, and responsive shell. It exposes explicit
blocks for page title, optional page styles, page heading support, main content,
and optional existing scripts. No JavaScript was added.

All eight allowlisted pages extend the base and retain their page-specific
content, context variables, loops, conditionals, links, cards, tables, records,
and safe empty or missing branches. The only heading correction changes the
Commands page's second H1, `Static Command Examples`, to H2. Responsive child
CSS also permits long command metadata and JSON summary values to wrap at the
narrow baseline.

## 4. Preserved routes, behavior, and navigation

The route and method inventory remains unchanged. `dashboard_app.py`,
`dashboard_command_runner.py`, report and evidence helpers, the retained backend
POST route, dependencies, existing tests, and all Next.js files are unchanged.

The shared navigation vocabulary is: **Home**, **Reports**, **Commands**,
**Execution Logs**, **AI Intent Reviewer**, and **AI Checklist**. These labels
use the existing endpoint names and `url_for()` destinations. Exactly one
destination receives `aria-current="page"`; JSON/report detail routes map to
Reports, and execution-log detail maps to Execution Logs. Historical execution
records remain records, not a current execution surface.

The persistent notice identifies the canonical Flask surface as local Stage 0
reviewer evidence and states display-only/report-only behavior, no provider or
model access, no command execution, and no live-device access. The Commands page
still contains no form, Run control, submit control, command input, or action
button.

## 5. Original validation and independent review failure

The original implementation validation reported 69 targeted pytest tests,
1,883 full-suite pytest tests with one existing warning, report-index 14/14,
and responsive rendered review. Those automated results remain historical, but
the responsive conclusion was inaccurate. Independent review returned
`FAIL_FIX_REQUIRED` after reproducing the AI Intent Reviewer defect at 320 CSS
pixels:

- `document.documentElement.scrollWidth=342`
- `document.documentElement.clientWidth=305`

The original dedicated test did not materially enforce wrapping for unbroken
underscore-separated scenario and safety-boundary identifiers. The original
record also lacked verified browser-native 400% evidence. These deficiencies
are not represented as an independent review pass.

## 6. Bounded fix attempts and carried-forward rendered evidence

The first bounded fix attempt was `BLOCKED` before editing because
browser-native zoom could not initially be verified. It changed no repository
file.

The second bounded retry applied and preserved exactly two changes before its
validation tooling interrupted the task:

- `templates/dashboard_ai_intent_reviewer.html` adds the narrow
  `.breakable-identifier` contract with `max-width: 100%`,
  `overflow-wrap: anywhere`, and `word-break: break-word`; applies it only to
  scenario and safety-boundary identifiers; and gives the exact scenario grid
  child `min-width: 0`. It adds no clipping, ellipsis, hidden overflow, global
  `word-break: break-all`, data, route, interaction, or execution behavior.
- `tests/test_phase_2o_01_canonical_flask_shell_and_ia_foundation.py` renders
  `/ai-intent-reviewer`, preserves representative long identifiers, verifies
  every affected binding and the dedicated CSS contract, rejects nowrap and
  content-hiding workarounds, and repeats one-main, one-H1, Stage 0, navigation,
  and no-execution assertions. It is explicitly a source/rendered-contract
  regression test, not a browser-layout measurement.

That retry's exact targeted pytest command passed 70 tests with zero failures,
skips, or warnings. Its carried-forward, non-independent controlling evidence
for `/ai-intent-reviewer` at 320 CSS pixels was:

- `window.innerWidth=320`
- `document.documentElement.clientWidth=305`
- `document.documentElement.scrollWidth=305`
- `document.body.scrollWidth=305`
- identifier count: `98`
- overflowing identifiers: `0`
- hidden identifiers: `0`
- page-level horizontal overflow: `NO`
- result: `PASS`

Additional carried-forward rendered results were `PASS` at 768 and 1440 CSS
pixels. Keyboard navigation, skip-link activation, visible focus, landmark and
heading hierarchy, non-color status meaning, absence of execution controls,
and the isolated application browser console also passed. The task-owned Flask
process bound only to `127.0.0.1:5000`, was stopped by the task, exited, and
released port 5000 without terminating an unrelated process or adding a runtime
artifact.

Supplementary browser-native 400% zoom was later achieved. The browser outer
width remained 1084, `window.devicePixelRatio` changed from 1.25 to 5.0, and
`window.innerWidth` changed from 1070 to 267. At 400%, document scroll width was
301 versus client width 263, so page-level horizontal overflow was present.
This result is `FAIL / NON_CONTROLLING`: the resulting 267 CSS pixel content
width was narrower than the controlling 320 CSS pixel Reflow condition. It is
not hidden, rewritten as PASS, or treated as Phase 2O review acceptance.

The resume task did not start Flask, browser navigation, or computer-use. The
later independent fix-commit review must repeat rendered validation and decide
whether the controlling 320 CSS pixel result is sufficient under the Phase 2O
acceptance boundary.

## 7. Resume validation results

- Exact targeted pytest: `70 passed`, `0 failed`, `0 skipped`, `0 warnings`.
- Full pytest: `1884 passed`, `0 failed`, `0 skipped`, `1 warning`. The warning
  is the existing terminal `GetPassWarning` from
  `test_day13_multi_router_wireguard_validation.py`.
- Report index: overall `PASS`; total `14`, pass `14`, warn `0`, fail `0`,
  missing `0`; exit code `0`.
- Documentation/static checks: `git diff --check`, exact four-file scope,
  Markdown headings and fenced blocks, repository-relative links, UTF-8,
  conflict markers, forbidden-file immutability, and material-untracked-artifact
  checks passed.

The required exact validation commands were:

```text
python -m pytest tests/test_phase_2o_01_canonical_flask_shell_and_ia_foundation.py tests/test_dashboard_app.py tests/test_phase_2n_02_canonical_flask_demo_smoke.py tests/test_phase_2n_04_user_facing_safety_labels.py tests/test_dashboard_command_runner.py
python -m pytest
python network_lab.py --task report-index
```

## 8. No-execution and forbidden-scope proof

Rendered views contained no form or button and the Commands page retained its
explicit no-submission statement. Browser traffic was GET-only. No route,
handler, POST, helper, importer, persistence, command runner, report generator,
dependency, lockfile, workflow, static CSS asset, API, Next.js source, topology,
provider/model integration, secret handling, SSH, NETCONF, RESTCONF, live-device
access, configuration backup/change, or production behavior changed. Phase
2O-02 content was not implemented. Day1-Day160 history and the single safety
model were not rewritten.

## 9. Review handoff

Phase 2O-01 is `DONE / FIX_APPLIED / READY_FOR_REVIEW / LOCAL_ONLY`. The local
fix is not independently reviewed,
merged, pushed, or synchronized. The next candidate is
`PHASE_2O_01_IMPLEMENTATION_FIX_COMMIT_REVIEW_ONLY`; it requires separate
explicit authorization, must repeat rendered browser validation, and does not
authorize merge or push by implication.
