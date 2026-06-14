# Pre-Day137-2 – Project Folder Organization Policy / Move Risk Matrix

## 1. Scope statement

This is Pre-Day137-2.

This is not Day137.

This is not the next-day feature.

This is not implementation.

This document does not move, delete, rename, or rewrite imports.

This document does not enable execution, provider access, or API access.

This document only defines future folder organization policy and move-risk classification. It does not create a CLI task, runner, adapter, broker, provider, mapped execution path, API surface, or live-capable workflow.

## 2. AGENTS.md compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md read before work | YES |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

Applicable AGENTS.md safety constraints for this task:

- Do not perform live device access unless a future approved safety gate explicitly allows it and the user separately approves the specific live operation.
- Do not use SSH, API calls, or real network-device commands unless a future approved safety gate explicitly allows it and the user separately approves the specific live operation.
- Do not execute configuration-changing commands.
- Do not run reset, reboot, remove, disable, enable, or similarly destructive operations.
- Rejected intents must not invoke adapters, brokers, runners, or execution paths.
- Dry-run, mock-only, report-only, documentation-only, and design-only tasks must remain non-executing.
- Preserve safety gates, reviewer evidence, and no-execution proof.
- Do not add secrets, credentials, tokens, private local memory, private paths, or personal environment details to the repository.
- Do not add OpenAI API calls, external AI runtime, voice input, speech-to-text, text-to-speech, microphone, or cloud execution unless a future task explicitly approves a separate safety gate.
- Do not push, merge, tag, deploy, or publish changes without explicit user approval.
- Keep public documentation safe for GitHub publication.

## 3. Relationship to Pre-Day137

Existing baseline reference: `docs/roadmap/pre_day137_project_folder_safety_inventory_no_move_plan.md`.

Pre-Day137 created the project folder safety inventory and no-move baseline. It listed top-level folders, top-level files, report and output areas, documentation areas, generated or historical evidence, and import-path risk areas.

Pre-Day137-2 adds a future organization policy and move-risk classification on top of that baseline.

Neither Pre-Day137 nor Pre-Day137-2 is allowed to move files. Both phases are documentation-only and preserve all current paths.

## 4. Current folder problem statement

The current repository remains workable, but the folder structure is becoming harder to scan and reason about as the project grows.

- Root-level Python modules are growing.
- CLI, registry, dispatch, report-index, formatter, safety helper, AI reviewer summary, and day-specific logic are mixed in root-level visibility.
- Documentation is growing by day across roadmap, AI intent, demo, release, reviewer, and portfolio evidence folders.
- Tests are increasing and currently share one broad `tests/` namespace even when they cover separate concerns.
- Generated reports and historical evidence may be mixed with active project files, depending on local runtime outputs.
- Import-path changes are risky because tests and CLI dispatch import many root-level modules directly.

This document does not treat the current structure as broken. It records where future organization decisions may reduce review burden while preserving safety and compatibility.

## 5. Folder role policy

| Folder / Area | Intended role | Allowed content | Not allowed content | Notes |
| --- | --- | --- | --- | --- |
| project root | Stable entry points and repository-level metadata | `AGENTS.md`, `README.md`, `requirements.txt`, example config files, root CLI entry points until explicitly migrated | Bulk day-specific modules after a future approved migration, generated runtime reports, secrets, live config | Keep root stable until import mapping and shims are approved. |
| `docs/roadmap` | Day plans, pre-day gates, future decision records | Roadmap plans, pre-day safety inventories, decision gates, move plans | Runtime reports, source modules, generated local artifacts | Existing daily docs remain traceable. |
| `docs/architecture` | Future architecture decision records and module maps | Architecture notes, import maps, compatibility-shim plans | Executable code, runtime output, secrets | Future folder; do not create or populate during Pre-Day137-2 unless separately approved. |
| `docs/safety` | Future consolidated safety policy and safety gate documentation | Safety invariants, safety boundary explanations, no-execution policy docs | Live credentials, executable adapters, runtime unlocks | Future folder; safety material may remain where it is until an approved docs move. |
| `docs/ai-intent` | AI intent reviewer evidence and daily AI intent documentation | AI intent reports, reviewer packets, schema/prompt/redaction evidence | Provider credentials, API calls, AI runtime code | Existing paths should remain stable for reviewer traceability. |
| `tests` | Current test suite root | Existing unit/regression tests and shared conftest | Generated reports, live-device requirements, credentials | Future subfolders may be introduced only after test import mapping. |
| future `tests/cli` | Future CLI and dispatch regression tests | CLI parser, help, dispatch, and task registry tests | Live network tests, provider/API tests | Future only; no tests moved now. |
| future `tests/report_index` | Future report-index and dashboard visibility tests | Report discovery, report-index, formatter, dashboard card tests | Generated report outputs unless deterministic fixtures | Future only; no tests moved now. |
| future `tests/safety` | Future safety invariant and boundary tests | Safety gate, no-execution, provider-disabled, adapter-boundary tests | Tests requiring SSH, live devices, external services, or secrets | Future only; no tests moved now. |
| future `tests/ai_reviewer` | Future AI reviewer summary tests | Schema, fixture renderer, prompt contract, redaction, audit, dashboard-card tests | OpenAI API calls, provider runtime, non-deterministic AI output | Future only; no tests moved now. |
| future `network_lab/` | Future package root for source modules | Package entry shims, grouped source modules after explicit migration | Unmapped moves, generated reports, secrets | Requires compatibility strategy before creation or migration. |
| future `network_lab/tasks` | Future task implementation package | Day-specific task modules, report-only task modules, validation helpers | CLI entry-point behavior, live execution unlocks without gate | Future only; high import risk. |
| future `network_lab/report_index` | Future report-index package | Report discovery, index generation, formatter helpers, dashboard-card metadata | Runtime reports, unrelated task logic | Future only; must preserve `report-index` behavior. |
| future `network_lab/output` | Future output formatting package | Formatting helpers, status rendering, HTML/JSON serialization helpers | Generated output files, CLI dispatch policy | Future only; formatter behavior is regression-sensitive. |
| future `network_lab/safety` | Future safety helper package | Safety invariants, disabled-provider checks, boundary matrices, guard helpers | Live unlocks, destructive operations, secrets | Future only; negative tests required before migration. |
| future `network_lab/ai_reviewer` | Future AI reviewer summary package | Schema contract, fixture renderer, prompt contract, redaction, audit, export package integration | Provider runtime, API calls, execution unlocks | Future only; provider/API must remain disabled. |
| generated report folders, if present | Local report outputs and reviewer-generated artifacts | `reports/**`, `summary/**`, deterministic generated outputs when explicitly intended | Source modules, secrets, private local state | Move risk depends on report-index dependencies. |
| historical evidence folders, if present | Stable reviewer evidence and demo assets | `docs/demo/**`, `docs/assets/**`, `docs/portfolio_evidence/**`, `fixtures/*.example.json`, `topology_profiles/**` | Live credentials, non-reviewed runtime artifacts | Prefer path stability unless links and tests are mapped. |

## 6. Move risk matrix

| Path / Pattern | Current role | Proposed future location | Move risk | Move allowed now? | Reason |
| --- | --- | --- | --- | --- | --- |
| `network_lab.py` | Main CLI entry point and report-index orchestration surface | Root shim plus future `network_lab/cli` or `network_lab/report_index` split | BLOCKED | NO | Root entry point, direct imports, CLI behavior, and report-index behavior are highly regression-sensitive. |
| `network_lab_task_registry.py` | Task registry and task-name resolution | Future `network_lab/tasks/registry.py` with compatibility shim | HIGH | NO | Registry imports and task IDs are used by CLI and tests. |
| `network_lab_cli_dispatch.py` | CLI parser, help text, and task handler dispatch | Future `network_lab/cli/dispatch.py` with compatibility shim | HIGH | NO | Help output and task dispatch must remain stable. |
| `dashboard_app.py` | Dashboard/report discovery and rendering support | Future `network_lab/report_index/dashboard.py` | HIGH | NO | Report visibility and dashboard behavior are tested and reviewer-facing. |
| `dashboard_command_runner.py` | Dashboard command metadata and command runner definitions | Future `network_lab/report_index/commands.py` or `network_lab/cli/commands.py` | HIGH | NO | Command metadata includes safety language and report-only expectations. |
| `templates/*.html` | Formatter and dashboard HTML templates | Future `network_lab/report_index/templates/` or retained `templates/` | MEDIUM | NO | Moving requires template loader/path verification. |
| report-index related helpers in `network_lab.py` | Report-index generation, report discovery, output formatting | Future `network_lab/report_index/` modules | BLOCKED | NO | Helpers are inside the root entry point and require careful extraction. |
| formatter related helpers in `network_lab.py` | Status, heading, HTML/JSON, and display formatting helpers | Future `network_lab/output/` | HIGH | NO | Broad call surface and many tests may rely on exact output. |
| `intent_safety_invariant_helpers.py` | Shared safety invariant helper evidence | Future `network_lab/safety/invariants.py` | HIGH | NO | Safety invariant behavior and negative tests must remain stable. |
| `intent_runtime_safety_gate.py` | Runtime safety gate report logic | Future `network_lab/safety/runtime_gate.py` | HIGH | NO | Safety gate evidence must stay review-only and traceable. |
| `intent_safety_boundary_regression_matrix.py` | Safety boundary regression matrix evidence | Future `network_lab/safety/boundary_matrix.py` | HIGH | NO | Safety boundary coverage is regression-sensitive. |
| `intent_executable_guards.py` | Executable guard evidence | Future `network_lab/safety/executable_guards.py` | HIGH | NO | Guard behavior must keep rejected scenarios non-executing. |
| `intent_real_adapter_safety_scaffold.py` | Real-adapter safety scaffold evidence | Future `network_lab/safety/adapter_scaffold.py` | HIGH | NO | Adapter-adjacent safety boundaries are sensitive. |
| `intent_real_adapter_safety_boundary_spec.py` | Real-adapter safety boundary specification | Future `network_lab/safety/adapter_boundary.py` | HIGH | NO | Future live-capable boundary documentation must not be disturbed. |
| `disabled_ai_provider_interface_boundary.py` | Disabled provider interface boundary evidence | Future `network_lab/ai_reviewer/provider_boundary.py` or `network_lab/safety/provider_boundary.py` | HIGH | NO | Provider-disabled invariant must remain stable. |
| `disabled_ai_provider_adapter_contract.py` | Disabled provider adapter contract evidence | Future `network_lab/ai_reviewer/provider_contract.py` | HIGH | NO | Moving could weaken provider-disabled regression coverage. |
| `ai_provider_disabled_by_default_safety_regression.py` | Provider disabled-by-default safety regression | Future `network_lab/ai_reviewer/provider_disabled_regression.py` | HIGH | NO | Proves provider/API remain disabled. |
| `intent_ai_reviewer_summary_schema_contract.py` | AI reviewer summary schema contract | Future `network_lab/ai_reviewer/schema_contract.py` | HIGH | NO | Tests and fixtures likely import current module directly. |
| `intent_ai_reviewer_summary_fixture_renderer.py` | Deterministic AI reviewer fixture renderer | Future `network_lab/ai_reviewer/fixture_renderer.py` | HIGH | NO | Depends on stable schema and fixture paths. |
| `intent_ai_summary_prompt_contract.py` | AI summary prompt contract evidence | Future `network_lab/ai_reviewer/prompt_contract.py` | HIGH | NO | Must remain report-only and provider-disabled. |
| `intent_ai_summary_redaction_policy.py` | AI summary redaction and no-secret policy evidence | Future `network_lab/ai_reviewer/redaction_policy.py` | HIGH | NO | Secret-safety behavior and tests are sensitive. |
| `intent_ai_summary_audit_trail_binding.py` | AI summary audit trail binding evidence | Future `network_lab/ai_reviewer/audit_binding.py` | HIGH | NO | Audit traceability relies on stable evidence paths. |
| `intent_ai_summary_dashboard_card_integration.py` | AI summary dashboard card integration evidence | Future `network_lab/ai_reviewer/dashboard_card.py` | HIGH | NO | Report-index and dashboard visibility may depend on current path. |
| `ai_reviewer_export_package_integration.py` | AI reviewer export package integration evidence | Future `network_lab/ai_reviewer/export_package.py` | HIGH | NO | Latest AI reviewer evidence path and report-index visibility are sensitive. |
| `mikrotik_*.py` | MikroTik task modules and validation helpers | Future `network_lab/tasks/mikrotik/` | HIGH | NO | Network-task modules are safety-sensitive and import-sensitive. |
| `cisco_*.py` | Cisco validation helpers | Future `network_lab/tasks/cisco/` | HIGH | NO | Network-task modules are safety-sensitive and import-sensitive. |
| `intent_*.py` | Intent, parser, reviewer, runtime, safety, and AI evidence modules | Future `network_lab/tasks/intent/`, `network_lab/safety/`, or `network_lab/ai_reviewer/` | HIGH | NO | Pattern spans multiple roles; must be classified file-by-file. |
| `performance_*.py` | Performance test/report helpers | Future `network_lab/tasks/performance/` | HIGH | NO | May touch runner behavior and existing tests. |
| `topology_summary.py` and `day6_lab_topology_summary.py` | Topology summary helpers | Future `network_lab/tasks/topology/` | MEDIUM | NO | Requires import and report path verification. |
| `tests/*.py` | Current unit and regression tests | Future grouped `tests/cli`, `tests/report_index`, `tests/safety`, `tests/ai_reviewer`, and task folders | MEDIUM | NO | Test discovery, direct imports, and fixtures must be mapped first. |
| `docs/roadmap/*.md` | Daily roadmap plans and safety evidence | Retain or future classified subfolders under `docs/roadmap` | LOW | NO | Documentation-only files may be lower risk, but traceability links may exist. |
| `docs/ai/**/*.md` | AI intent and safety documentation | Future `docs/ai-intent` or `docs/safety` classification only after review | LOW | NO | Reviewer links and historical continuity matter. |
| `docs/ai-intent/**/*.md` | AI intent day evidence and reviewer material | Retain or future role-based AI intent docs folders | LOW | NO | Reviewer package paths may be referenced. |
| generated reports / outputs: `reports/**`, `summary/**` | Generated report-index, lab-summary, or historical summary outputs | Future generated output policy area, possibly retained in place | UNKNOWN | NO | Dependencies must be verified before moving; report-index may scan known paths. |
| historical evidence files: `docs/demo/**`, `docs/assets/**`, `docs/portfolio_evidence/**`, `fixtures/*.example.json`, `topology_profiles/**` | Demo assets, screenshots, release evidence, fixtures, profiles | Retain or future evidence-specific folders after link/test map | MEDIUM | NO | Documentation links, tests, and reviewer workflows may reference current paths. |
| `AGENTS.md` | Repository instructions and safety contract | Project root | BLOCKED | NO | Must remain discoverable and unmodified unless explicitly requested. |

## 7. Import-sensitive inventory

Files listed here must not be moved until import dependencies are fully mapped. Imports are not changed by this document.

| File | Import sensitivity | Likely consumers | Future mitigation before move |
| --- | --- | --- | --- |
| `network_lab.py` | BLOCKED | CLI users, `network_lab_cli_dispatch.py`, broad tests, report-index flows | Create a package migration plan, keep root shim, map all imported task runners, run full regression before and after. |
| `network_lab_task_registry.py` | HIGH | `network_lab_cli_dispatch.py`, registry tests, catalog tests, AI/provider/safety tests | Add compatibility shim and verify task ID/name resolution remains unchanged. |
| `network_lab_cli_dispatch.py` | HIGH | `network_lab.py`, CLI dispatch tests, help smoke checks | Preserve CLI help text, parser behavior, and task handler mapping through a shim. |
| `dashboard_app.py` | HIGH | Dashboard tests, report-index generation, templates | Map template/report paths and preserve dashboard discovery behavior. |
| `dashboard_command_runner.py` | HIGH | Dashboard command tests and templates | Preserve command metadata, safety wording, and report-only behavior. |
| `intent_safety_invariant_helpers.py` | HIGH | `tests/test_intent_safety_invariant_helpers.py`, safety gate modules | Build safety package shim and run negative safety tests before/after. |
| `intent_runtime_safety_gate.py` | HIGH | Runtime safety tests, registry/CLI handlers | Preserve report-only output and disabled execution flags. |
| `intent_safety_boundary_regression_matrix.py` | HIGH | Safety boundary tests, registry/CLI handlers | Preserve safety matrix fields and no-execution proof. |
| `intent_executable_guards.py` | HIGH | Executable guard tests, safety reports | Prove rejected scenarios still do not reach adapters, brokers, runners, or execution. |
| `disabled_ai_provider_interface_boundary.py` | HIGH | Provider-disabled interface tests, later provider contract reports | Keep provider/API disabled and maintain direct import compatibility. |
| `disabled_ai_provider_adapter_contract.py` | HIGH | Provider-disabled adapter tests, Day135 regression | Keep provider adapter paths disabled and prove no provider instantiation. |
| `ai_provider_disabled_by_default_safety_regression.py` | HIGH | Day135 tests, registry/CLI handlers, report-index | Preserve disabled-by-default report behavior and task catalog visibility. |
| `intent_ai_reviewer_summary_schema_contract.py` | HIGH | AI reviewer schema tests, fixture renderer | Preserve schema fields, fixture compatibility, and import shim. |
| `intent_ai_reviewer_summary_fixture_renderer.py` | HIGH | AI reviewer fixture tests, report-index | Preserve deterministic fixture output and source fixture paths. |
| `intent_ai_summary_prompt_contract.py` | HIGH | Prompt contract tests, audit binding | Preserve no-provider prompt evidence and report fields. |
| `intent_ai_summary_redaction_policy.py` | HIGH | Redaction tests, prompt/audit flows | Preserve redaction behavior and no-secret guarantees. |
| `intent_ai_summary_audit_trail_binding.py` | HIGH | Audit trail tests, dashboard-card integration | Preserve audit binding fields and evidence references. |
| `intent_ai_summary_dashboard_card_integration.py` | HIGH | Dashboard-card tests, report-index | Preserve dashboard card metadata and visibility expectations. |
| `ai_reviewer_export_package_integration.py` | HIGH | Export package tests, report-index | Preserve export package schema and report-index references. |
| `mikrotik_*.py` | HIGH | CLI task handlers, MikroTik tests, dry-run/read-only plans | Classify each file by live risk, add shims, and keep safety gates unchanged. |
| `cisco_*.py` | HIGH | Cisco tests and CLI handlers | Classify each file by task role and preserve parser/validation imports. |
| `parsers/*.py` | MEDIUM | Parser tests, task modules | Add package import shims and fixture-based parser regression coverage. |
| `adapters/*.py` | HIGH | Adapter contract tests and future safety gates | Treat as safety-sensitive; require explicit safety gate and no live enablement. |
| `core/*.py` | MEDIUM | Device factory/base consumers, adapter modules | Map consumers and preserve public classes/functions through shims. |

## 8. Recommended organization sequence

Pre-Day137-2 performs step 0 only: policy and matrix.

No actual move is allowed in Pre-Day137-2.

Future sequence:

1. Documentation classification only.
2. Report/output classification only.
3. Test classification only.
4. Helper-module migration planning.
5. Import compatibility shim planning.
6. Source module migration only after explicit approval.
7. Full regression gate before and after each future move.

This sequence is a recommendation for later planning. It is not approval to execute any move.

## 9. Future move gate

Before any future move, all of the following conditions must be satisfied:

- Explicit user approval.
- Separate day task.
- Clear source path and target path list.
- Complete import consumer map.
- Compatibility shim plan if needed.
- Full `python -m pytest` pass before move.
- Full `python -m pytest` pass after move.
- `python network_lab.py --task report-index` pass or acceptable documented WARN with fail=0.
- `python network_lab.py --help` pass.
- Safety invariant remains review-only.
- No execution/provider/API enabled.
- AGENTS.md remains unmodified unless explicitly requested.

## 10. Recommended Day137 boundary

Recommended next decision label:

```text
Day137 – Project Folder Organization Decision Gate
```

Day137 should still:

- Not move files.
- Not delete files.
- Not rename files.
- Not change import paths.
- Not enable execution / provider / API.

Day137 should only decide:

- Which folder group is safest to organize first.
- Which paths are blocked.
- Which paths require import mapping.
- Which future day may perform the first low-risk move.

## 11. Validation commands

Required safe, local-only validation commands for this task:

```powershell
git status --short --branch
python -m pytest
python network_lab.py --task report-index
python network_lab.py --help
```

Validation results are recorded in the final Codex response after this documentation-only file is added.

## 12. Final safety summary

| Check | Result |
| --- | --- |
| AGENTS.md pre-read | YES |
| AGENTS.md modified | NO |
| Moved files | NO |
| Deleted files | NO |
| Renamed files | NO |
| Import paths changed | NO |
| Execution enabled | NO |
| Provider enabled | NO |
| API enabled | NO |
| Source files changed | NO |
| Tests changed | NO |
| Generated reports changed | NO |
| Docs-only change | YES |
| Not next-day feature | YES |

Final recommendation:

`KEEP_AS_PRE_DAY137_2_DOCS_ONLY_ORGANIZATION_POLICY_MOVE_RISK_MATRIX`
