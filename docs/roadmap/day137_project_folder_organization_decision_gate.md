# Day137 - Project Folder Organization Decision Gate

## Scope

This is Day137.

This is not the next day's feature.

This does not implement the original Day137 AI Assistance Review Demo Package.

This does not open execution, provider behavior, API behavior, SSH, adapters, brokers, runners, live commands, device access, or cloud execution.

No files were moved, deleted, renamed, or import paths changed.

Folder restructuring is deferred.

Day137-Day140 should be used for folder organization decision and dry-run gates.

Day141-Day144 may resume the original AI Assistance line only after organization risk is controlled.

## AGENTS.md Compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md pre-read before changes | YES |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

## Decision Result

Final recommendation:

```text
DO_NOT_REORGANIZE_YET_DECISION_ONLY
```

Day137 produces reviewer-visible decision evidence only. It is not approval to reorganize folders.

## Required Safety Fields

| Field | Value |
| --- | --- |
| day | `137` |
| task | `project-folder-organization-decision-gate` |
| mode | `DECISION_ONLY` |
| moves_allowed | `false` |
| deletes_allowed | `false` |
| renames_allowed | `false` |
| import_path_changes_allowed | `false` |
| execution_allowed | `false` |
| provider_allowed | `false` |
| api_allowed | `false` |
| ssh_allowed | `false` |
| live_command_allowed | `false` |
| next_feature_allowed | `false` |
| original_day137_ai_assistance_demo_allowed | `false` |
| final_recommendation | `DO_NOT_REORGANIZE_YET_DECISION_ONLY` |

## Areas That Cannot Move First

| Area | Move allowed now? | Why |
| --- | --- | --- |
| `network_lab.py` | NO | Main CLI entry point, task runner surface, report-index helpers, and tests depend on this stable path. |
| `network_lab_task_registry.py` and `network_lab_cli_dispatch.py` | NO | Registry resolution, CLI choices, aliases, help text, and handler dispatch are regression-sensitive. |
| Report-index modules and templates | NO | `network_lab.py`, `dashboard_app.py`, `dashboard_command_runner.py`, and `templates/**` may depend on current paths. |
| AI reviewer and provider-disabled modules | NO | Day134-Day136 stability must be preserved before any package or folder migration is attempted. |
| `tests/**` | NO | Pytest discovery, direct imports, fixtures, and report-index visibility tests may break if moved. |
| Generated reports and historical evidence | NO | `reports/**`, `summary/**`, demo assets, fixtures, and topology profiles must remain traceable. |

## Why Folders Cannot Be Moved Directly

Direct folder movement is blocked because current paths are coupled to:

- CLI entry and dispatch behavior.
- Registry task-name resolution.
- Report-index discovery and reviewer-visible links.
- Day134-Day136 disabled-provider and AI reviewer export evidence.
- Test discovery and direct imports.
- Generated report and historical evidence locations.

Any future move must first prove import compatibility, report-index compatibility, safety invariants, and no-execution behavior in a separate dry-run-only gate.

## Day134-Day136 Stability

Day137 preserves and checks the current AI reviewer/export/package stability line:

- Day134 disabled AI provider adapter contract remains read-only and provider/API/execution disabled.
- Day135 disabled-by-default provider safety regression remains read-only and provider/API/execution disabled.
- Day136 AI reviewer export package integration remains review-only and provider/API/execution disabled.

Day137 does not modify those reports or move their locations. It reads their JSON evidence as local, read-only stability input for the Day137 decision report.

## Required Future Proof Before Any Move

Before any future file move is allowed:

- The user must approve the exact move list.
- A separate dry-run-only day task must exist.
- Every affected import consumer must be mapped.
- Compatibility shims must be planned where module paths change.
- Report-index, dashboard, template, generated report, summary, and documentation links must be checked.
- Negative tests must prove rejected scenarios do not reach adapters, brokers, runners, execution, providers, APIs, SSH, or live commands.
- `python -m pytest` must pass before and after any future dry-run or move proposal.
- `python network_lab.py --task report-index` must pass or return only a documented acceptable WARN unrelated to safety or regression.
- Day134-Day136 evidence must remain stable.

## Deferred Original Day137 Feature

The original Day137 AI Assistance Review Demo Package is deferred.

This Day137 task is a folder organization decision gate only. It does not add AI Assistance demo packaging, provider behavior, API behavior, model calls, prompt submission, cloud execution, voice, SSH, device access, adapters, brokers, runners, or execution unlocks.

## Report Outputs

Generate reviewer evidence with:

```powershell
python network_lab.py --task project-folder-organization-decision-gate
```

Expected outputs:

- `reports/lab-summary/day137_project_folder_organization_decision_gate.json`
- `reports/lab-summary/day137_project_folder_organization_decision_gate.html`

## Validation

Required local validation:

```powershell
python -m pytest
python network_lab.py --task project-folder-organization-decision-gate
python network_lab.py --task report-index
git status --short --branch
```

## Final Safety Summary

| Check | Result |
| --- | --- |
| Not next day's feature | YES |
| No file moves | YES |
| No file deletes | YES |
| No file renames | YES |
| No import path changes | YES |
| Execution/provider/API remains disabled | YES |
| Original AI Assistance Review Demo Package not implemented | YES |
| Folder restructuring deferred | YES |

Final recommendation:

```text
DO_NOT_REORGANIZE_YET_DECISION_ONLY
```
