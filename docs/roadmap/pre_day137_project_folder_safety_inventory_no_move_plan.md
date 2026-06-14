# Pre-Day137 - Project Folder Safety Inventory / No-Move Plan

## Scope Statement

This is Pre-Day137.

This is not Day137.

This is not the next-day feature.

This document does not enable execution, provider access, or API access.

This document does not move, delete, rename, or rewrite imports.

This is an inventory-only, documentation-only safety review package. It does not create a CLI task, runner, adapter, broker, provider, mapped execution path, API surface, or any live-capable workflow.

## AGENTS.md Compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md read before work | YES |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

Applicable AGENTS.md constraints for this task:

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

## Project Folder Inventory

Read-only inventory source: `AGENTS.md`, `rg --files`, and targeted text searches for CLI, registry, report-index, AI reviewer summary, safety helper, and test import references. No file was moved, renamed, deleted, or refactored.

### Top-Level Folders

- `adapters/` - Adapter modules for Cisco IOS and MikroTik RouterOS boundaries. Treat as safety-sensitive even when not used by this pre-day task.
- `config/` - Configuration documentation.
- `core/` - Device base and factory abstractions.
- `docs/` - Reviewer-facing documentation, roadmap plans, AI intent documentation, release material, demo kits, assets, and portfolio evidence.
- `fixtures/` - Deterministic example fixtures, including AI reviewer summary and redaction-policy examples.
- `parsers/` - Offline parser modules for Cisco and MikroTik output.
- `runner_profiles/` - Task catalog and safety-level metadata.
- `summary/` - Historical summary output for earlier WireGuard validation evidence.
- `templates/` - Dashboard HTML templates, including AI intent reviewer and report views.
- `tests/` - Unit and regression tests.
- `topology_profiles/` - JSON topology/profile inputs for offline and dry-run workflows.

### Top-Level Files

- `AGENTS.md` - Repository safety and validation instructions.
- `README.md` - Project overview.
- `network_lab.py` - Main CLI entry point and report/index orchestration surface.
- `network_lab_cli_dispatch.py` - CLI parser and task dispatch mapping.
- `network_lab_task_registry.py` - Task registry and task-name resolution.
- `dashboard_app.py` - Local dashboard/report discovery and rendering support.
- `dashboard_command_runner.py` - Dashboard command metadata and command runner definitions.
- `requirements.txt` - Python dependencies.
- `config.example.json`, `config.cisco.example.json`, `golden_day2_config.example.json` - Example configuration files.
- Day/task modules such as `mikrotik_*.py`, `cisco_*.py`, `intent_*.py`, `disabled_ai_provider_*.py`, `ai_reviewer_export_package_integration.py`, `performance_*.py`, and `topology_summary.py` - Existing task implementations, report-only flows, safety reviews, parser evidence, AI intent evidence, provider-disabled gates, and lab validation helpers.

### Python Source Files Related to Requested Classification

- CLI entry point: `network_lab.py`.
- Task registry: `network_lab_task_registry.py`.
- CLI dispatch: `network_lab_cli_dispatch.py`.
- Report index and output formatting: `network_lab.py`, `dashboard_app.py`, `templates/dashboard_reports.html`, `templates/dashboard_json_preview.html`, `templates/dashboard_home.html`.
- Dashboard command metadata: `dashboard_command_runner.py`, `templates/dashboard_commands.html`, `templates/dashboard_command_log.html`, `templates/dashboard_command_logs.html`.
- Safety helpers and safety gates: `intent_safety_invariant_helpers.py`, `intent_runtime_safety_gate.py`, `intent_safety_boundary_regression_matrix.py`, `intent_executable_guards.py`, `intent_real_adapter_safety_scaffold.py`, `intent_real_adapter_safety_boundary_spec.py`, `disabled_ai_provider_interface_boundary.py`, `disabled_ai_provider_adapter_contract.py`, `ai_provider_disabled_by_default_safety_regression.py`.
- AI reviewer summary and provider-disabled evidence: `intent_ai_reviewer_summary_schema_contract.py`, `intent_ai_reviewer_summary_fixture_renderer.py`, `intent_ai_summary_prompt_contract.py`, `intent_ai_summary_redaction_policy.py`, `intent_ai_summary_audit_trail_binding.py`, `intent_ai_summary_dashboard_card_integration.py`, `ai_reviewer_export_package_integration.py`.
- Tests: `tests/test_network_lab_runner.py`, `tests/test_network_lab_cli_dispatch.py`, `tests/test_network_lab_task_registry.py`, `tests/test_network_lab_task_catalog.py`, `tests/test_intent_thin_cli_regression_gate.py`, `tests/test_intent_safety_invariant_helpers.py`, `tests/test_intent_safety_boundary_regression_matrix.py`, `tests/test_intent_ai_reviewer_summary_schema_contract.py`, `tests/test_intent_ai_reviewer_summary_fixture_renderer.py`, `tests/test_intent_ai_summary_prompt_contract.py`, `tests/test_intent_ai_summary_redaction_policy.py`, `tests/test_intent_ai_summary_audit_trail_binding.py`, `tests/test_intent_ai_summary_dashboard_card_integration.py`, `tests/test_disabled_ai_provider_interface_boundary.py`, `tests/test_disabled_ai_provider_adapter_contract.py`, `tests/test_ai_provider_disabled_by_default_safety_regression.py`, `tests/test_ai_reviewer_export_package_integration.py`.

### Documentation Folders

- `docs/roadmap/` - Day and pre-day plans, including this Pre-Day137 no-move inventory.
- `docs/ai/` - AI intent design and reviewer documentation.
- `docs/ai-intent/` - AI intent daily evidence and reviewer-facing package.
- `docs/ai-intent/reviewer/` - Reviewer-specific AI intent evidence.
- `docs/assets/` - Static topology and demo images.
- `docs/demo/` - Offline demo kits, screenshots, scripts, and checklists.
- `docs/portfolio/` and `docs/portfolio_evidence/` - Portfolio and release evidence.
- `docs/releases/` - Release packages and artifact checklists.
- `docs/reviewer/` - Reviewer entry material.

### Report and Output Folders

- `summary/` - Existing historical output files. Treat as historical evidence.
- `reports/` - Report-index and lab-summary output target used by existing code and tests. If present locally, treat contents as generated report output or reviewer evidence.
- `docs/demo/**/screenshots/` - Static screenshot evidence for demo packaging.

### Generated Output or Historical Evidence

- `summary/*.html` and `summary/*.json` - Historical Day13 summary evidence.
- `reports/report_index.html` and `reports/report_index.json` - Generated report-index outputs, if present locally.
- `reports/lab-summary/*.json`, `reports/lab-summary/*.html`, and `reports/lab-summary/*.txt` - Generated or reviewer-facing lab summary reports, if present locally.
- `docs/demo/**/screenshots/*.png` - Static demo screenshot evidence.
- `fixtures/*.example.json` - Deterministic sample fixtures; not runtime output, but reviewer evidence should remain stable.

## No-Move Classification Table

| Path / Pattern | Type | Current role | Move allowed now? | Reason |
| --- | --- | --- | --- | --- |
| `network_lab.py` | Entry point | Main CLI entry point, imports task modules, owns report-index helpers and many day-task runners. | NO | Import and CLI behavior sensitive; Pre-Day137 is inventory-only. |
| `network_lab_task_registry.py` | Registry | Resolves task IDs and preserves catalog/task name behavior. | NO | Task IDs and tests depend on stable path/import. |
| `network_lab_cli_dispatch.py` | CLI dispatch | Builds parser, help text, and task handler dispatch. | NO | CLI help and task routing are regression-sensitive. |
| `dashboard_app.py` | Report index | Discovers reports and builds dashboard/report cards. | NO | Report visibility behavior is tested and user-facing. |
| `dashboard_command_runner.py` | CLI dispatch | Defines dashboard command metadata and safety descriptions. | NO | Dashboard command behavior and evidence wording are safety-sensitive. |
| `templates/*.html` | Formatter | Dashboard and report rendering templates. | NO | Moving would require path or loader changes. |
| `intent_safety_invariant_helpers.py` | Safety helper | Shared safety invariant helpers. | NO | Safety invariant checks must remain stable and review-only. |
| `intent_runtime_safety_gate.py` | Safety helper | Runtime safety gate report logic. | NO | Safety gate evidence and tests depend on stable imports. |
| `intent_safety_boundary_regression_matrix.py` | Safety helper | Safety boundary regression matrix evidence. | NO | Regression evidence must remain traceable. |
| `intent_executable_guards.py` | Safety helper | Executable guard evidence. | NO | Guard evidence is safety-critical. |
| `intent_real_adapter_safety_scaffold.py` | Safety helper | Real-adapter safety scaffold documentation/report logic. | NO | Future live-capable boundaries must not be disturbed in a pre-day inventory. |
| `intent_real_adapter_safety_boundary_spec.py` | Safety helper | Real-adapter safety boundary specification. | NO | Safety boundary documentation and tests depend on this path. |
| `disabled_ai_provider_interface_boundary.py` | Safety helper | Provider-disabled interface boundary evidence. | NO | Provider-disabled invariant must remain stable. |
| `disabled_ai_provider_adapter_contract.py` | Safety helper | Provider-disabled adapter contract evidence. | NO | Provider-disabled invariant must remain stable. |
| `ai_provider_disabled_by_default_safety_regression.py` | Safety helper | Disabled-by-default provider regression report. | NO | Proves provider/API remain disabled. |
| `intent_ai_reviewer_summary_schema_contract.py` | AI reviewer summary | Day127 reviewer summary schema contract. | NO | Imported by tests and later summary flows. |
| `intent_ai_reviewer_summary_fixture_renderer.py` | AI reviewer summary | Day128 deterministic fixture renderer. | NO | Depends on schema fixture path and report index visibility. |
| `intent_ai_summary_prompt_contract.py` | AI reviewer summary | Day129 prompt contract evidence, no provider calls. | NO | AI prompt contract must remain documentation/report-only. |
| `intent_ai_summary_redaction_policy.py` | AI reviewer summary | Day130 redaction and no-secret evidence. | NO | Secret-safety policy must remain stable. |
| `intent_ai_summary_audit_trail_binding.py` | AI reviewer summary | Day131 audit trail binding evidence. | NO | Audit traceability depends on stable report paths. |
| `intent_ai_summary_dashboard_card_integration.py` | AI reviewer summary | Day132 dashboard-card integration evidence. | NO | Dashboard/report-index tests depend on stable path. |
| `ai_reviewer_export_package_integration.py` | AI reviewer summary | Day136 export package integration evidence. | NO | Latest AI reviewer evidence path; no next-day changes allowed. |
| `tests/test_network_lab_runner.py` | Tests | Broad CLI, report-index, task, safety, and output regression coverage. | NO | Test import paths and expected report paths are sensitive. |
| `tests/test_network_lab_cli_dispatch.py` | Tests | CLI parser and dispatch regression coverage. | NO | Directly imports CLI dispatch and entry point modules. |
| `tests/test_network_lab_task_registry.py` | Tests | Task registry behavior coverage. | NO | Directly imports registry and network lab modules. |
| `tests/test_network_lab_task_catalog.py` | Tests | Task catalog visibility coverage. | NO | Depends on catalog/report path conventions. |
| `tests/test_intent_*ai*summary*.py` | Tests | AI reviewer summary tests for schema, renderer, prompt, redaction, audit, and dashboard integration. | NO | Direct imports and report-index visibility checks. |
| `tests/test_disabled_ai_provider*.py` | Tests | Provider-disabled safety regression tests. | NO | Proves provider/API remain disabled by default. |
| `tests/test_ai_reviewer_export_package_integration.py` | Tests | Day136 export package integration coverage. | NO | Direct imports and report-index visibility checks. |
| `tests/test_intent_safety_*.py` | Tests | Safety helper and boundary regression coverage. | NO | Directly validates safety invariants. |
| `docs/roadmap/*.md` | Docs | Day plans, safety packages, and roadmap evidence. | NO | Pre-Day137 allows only adding this document, not moving existing plans. |
| `docs/ai/**/*.md` | Docs | AI intent and safety documentation. | NO | Reviewer evidence should remain traceable. |
| `docs/ai-intent/**/*.md` | Docs | AI intent day evidence and reviewer material. | NO | Reviewer package paths are referenced by tests/catalogs. |
| `docs/demo/**` | Historical evidence | Offline demo kit, screenshots, scripts, and checklists. | NO | Demo evidence paths should stay stable. |
| `docs/assets/*.png` | Historical evidence | Topology and demo images. | NO | Documentation image links may depend on current paths. |
| `fixtures/*.example.json` | Historical evidence | Deterministic examples and AI summary fixtures. | NO | Tests and reviewer evidence rely on stable fixture paths. |
| `runner_profiles/*.json` | Registry | Task catalog and safety-level metadata. | NO | Catalog/report-index behavior may depend on these files. |
| `topology_profiles/*.json` | Historical evidence | Offline topology/profile inputs. | NO | CLI profile tests and dry-run workflows reference these paths. |
| `summary/*` | Historical evidence | Existing generated Day13 summary evidence. | NO | Historical evidence should not be moved in Pre-Day137. |
| `reports/**` | Generated reports | Existing or future generated report-index and lab-summary outputs. | NO | Generated/report evidence path stability matters; no generated reports modified by this doc task. |
| `adapters/*.py` | Unknown / inspect later | Adapter boundary modules. | NO | Safety-sensitive; future moves require explicit safety gate. |
| `core/*.py` | Unknown / inspect later | Device abstractions and factory helpers. | NO | Could affect adapters and tests. |
| `parsers/*.py` | Unknown / inspect later | Offline parser modules. | NO | Parser consumers and tests may import these paths. |
| `mikrotik_*.py` | Unknown / inspect later | MikroTik task modules and validation helpers. | NO | Network-task modules are safety-sensitive. |
| `cisco_*.py` | Unknown / inspect later | Cisco validation helpers. | NO | Network-task modules are safety-sensitive. |
| `performance_*.py` | Unknown / inspect later | Performance test/report helpers. | NO | Existing tests may reference current paths. |

## Import-Path Risk Inventory

Files likely to be sensitive to import-path changes:

- `network_lab.py` - Imports many task modules and exposes `main`, report-index helpers, task listing, output formatting, and task-specific runner functions used by tests.
- `network_lab_task_registry.py` - Imported by registry tests and AI/provider/safety tests through `resolve_task_handler` and `resolve_task_name`.
- `network_lab_cli_dispatch.py` - Imported by CLI dispatch tests and AI/provider summary tests.
- Report-index related modules and files:
  - `network_lab.py`
  - `network_lab_cli_dispatch.py`
  - `dashboard_app.py`
  - `dashboard_command_runner.py`
  - `templates/dashboard_reports.html`
  - `templates/dashboard_json_preview.html`
  - `templates/dashboard_home.html`
  - `runner_profiles/task_catalog.json`
- AI reviewer summary related modules:
  - `intent_ai_reviewer_summary_schema_contract.py`
  - `intent_ai_reviewer_summary_fixture_renderer.py`
  - `intent_ai_summary_prompt_contract.py`
  - `intent_ai_summary_redaction_policy.py`
  - `intent_ai_summary_audit_trail_binding.py`
  - `intent_ai_summary_dashboard_card_integration.py`
  - `ai_reviewer_export_package_integration.py`
  - `disabled_ai_provider_interface_boundary.py`
  - `disabled_ai_provider_adapter_contract.py`
  - `ai_provider_disabled_by_default_safety_regression.py`
- Tests that import these modules:
  - `tests/test_network_lab_runner.py`
  - `tests/test_network_lab_cli_dispatch.py`
  - `tests/test_network_lab_task_registry.py`
  - `tests/test_network_lab_task_catalog.py`
  - `tests/test_intent_thin_cli_regression_gate.py`
  - `tests/test_intent_ai_reviewer_summary_schema_contract.py`
  - `tests/test_intent_ai_reviewer_summary_fixture_renderer.py`
  - `tests/test_intent_ai_summary_prompt_contract.py`
  - `tests/test_intent_ai_summary_redaction_policy.py`
  - `tests/test_intent_ai_summary_audit_trail_binding.py`
  - `tests/test_intent_ai_summary_dashboard_card_integration.py`
  - `tests/test_disabled_ai_provider_interface_boundary.py`
  - `tests/test_disabled_ai_provider_adapter_contract.py`
  - `tests/test_ai_provider_disabled_by_default_safety_regression.py`
  - `tests/test_ai_reviewer_export_package_integration.py`

No import paths were changed for this Pre-Day137 task.

## No-Move Plan

- Do not move anything in Pre-Day137.
- Do not rename anything in Pre-Day137.
- Do not delete anything in Pre-Day137.
- Do not change imports in Pre-Day137.
- Do not refactor source code in Pre-Day137.
- Do not modify CLI behavior in Pre-Day137.
- Only classify and document.
- Any future move must require a separate explicit day plan and regression gate.

## Future-Safe Move Criteria

Before any future folder move is allowed, all of the following must be true:

- Explicit user approval is granted for the specific move.
- The work is a separate day task, not Pre-Day137.
- The future task includes a complete list of imports affected.
- The future task includes a compatibility shim or migration plan, if needed.
- `python -m pytest` passes.
- `python network_lab.py --task report-index` passes or returns only documented acceptable WARN output.
- `python network_lab.py --help` passes.
- The safety invariant check remains review-only.
- No execution is enabled.
- No provider is enabled.
- No API is enabled.
- No SSH, RouterOS, live network-device access, or external service access is introduced.
- No adapter, broker, runner, mapped execution path, or live-capable workflow is introduced without a separate approved safety gate.

## Validation Commands

Required safe, local-only validation commands for this pre-day package:

```powershell
git status --short --branch
python -m pytest
python network_lab.py --task report-index
python network_lab.py --help
```

Validation result placeholders are intentionally not pre-filled in this document. The final Codex response for the task records the actual command outcomes after this file is added.

## Final Safety Summary

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
| Docs-only change | YES |
| Not next-day feature | YES |

Final recommendation:

`KEEP_AS_PRE_DAY137_DOCS_ONLY_INVENTORY_NO_MOVE_PLAN`
