# Day138 - Project Folder Organization Dry-Run Inventory Gate

## Scope

This is Day138.

This is not the next day's feature.

This is a dry-run inventory gate before any future project folder organization work.

This does not move, delete, rename, organize, restructure, or relocate any existing files.

This does not change import paths.

This does not open execution, provider behavior, API behavior, SSH, adapters, brokers, runners, mapped execution, live commands, device access, or cloud execution.

No execution, provider, or API is enabled.

## AGENTS.md Compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md pre-read before changes | YES |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

## Task

Task name:

```text
project-folder-organization-dry-run-inventory-gate
```

Mode:

```text
DRY_RUN_INVENTORY_ONLY
```

Final recommendation:

```text
KEEP_DRY_RUN_INVENTORY_ONLY
```

`next_phase_allowed` remains `false`.

## Forbidden Actions

| Action | Allowed / enabled |
| --- | --- |
| move | `false` |
| delete | `false` |
| rename | `false` |
| import_path_change | `false` |
| execution_enabled | `false` |
| provider_enabled | `false` |
| api_enabled | `false` |
| ssh_allowed | `false` |
| live_command_allowed | `false` |

## Inventory Groups

Day138 records current file group inventory only. It does not act on the inventory.

Required groups:

- root CLI / entrypoint files
- task registry / dispatch files
- intent / task modules
- tests
- docs / roadmap
- docs / ai-intent
- reports / lab-summary
- fixtures / samples
- safety / review-only related files
- other / uncategorized

Each group records:

- `group_name`
- `file_count`
- `sample_files`
- `current_location`
- `future_organization_candidate`
- `risk_level`
- `reason`

## Risk Rules

- Files whose movement would affect import paths are `HIGH`.
- CLI entrypoint, task dispatch, and registry files are `HIGH`.
- Files heavily referenced by tests are `HIGH`.
- Safety, guard, invariant, review-only, disabled-provider, adapter, broker, and runner related files are `HIGH`.
- Docs-only groups are `LOW`.
- Generated reports are `LOW`.
- Fixtures and samples are `LOW` when unreferenced and `MEDIUM` when referenced by tests or task code.

## Report Outputs

Generate reviewer evidence with:

```powershell
python network_lab.py --task project-folder-organization-dry-run-inventory-gate
```

Expected outputs:

- `reports/lab-summary/day138_project_folder_organization_dry_run_inventory_gate.json`
- `reports/lab-summary/day138_project_folder_organization_dry_run_inventory_gate.html`

## Validation

Required local validation:

```powershell
python network_lab.py --task project-folder-organization-dry-run-inventory-gate
python -m pytest
python network_lab.py --task report-index
git status --short --branch
git diff --name-status
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
| SSH/live command remains disallowed | YES |
| Adapter/broker/runner/mapped execution not invoked | YES |
| next_phase_allowed | `false` |
| final recommendation | `KEEP_DRY_RUN_INVENTORY_ONLY` |
