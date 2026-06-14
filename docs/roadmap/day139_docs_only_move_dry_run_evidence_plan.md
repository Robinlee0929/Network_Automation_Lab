# Day139 - Docs-Only Move Dry-Run Evidence Plan

## Scope

This is Day139.

This is not the next-day feature implementation.

This is not Day140.

This is not Folder Move Compatibility Gate.

This task is a docs-only dry-run evidence plan based on the Day138 docs organization candidates.

It does not decide that docs migration is allowed.

It does not move files, rename files, modify import statements, modify source import paths, or change the real repository structure.

It does not enable execution, provider behavior, API behavior, adapters, SSH, live commands, router access, brokers, runners, mapped execution, network access, secrets, or external integrations.

No execution, provider, or API is enabled.

## AGENTS.md Compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md read before Day139 work | YES |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

## Task

Task name:

```text
docs-only-move-dry-run-evidence-plan
```

Mode:

```text
REVIEW_ONLY
```

Based on:

```text
Day138
```

Source scope:

```text
docs-only
```

Final recommendation:

```text
KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET
```

`next_phase_allowed=false`

## Required Evidence

Day139 records:

- hypothetical docs target folders
- docs-only dry-run move pairs
- proposal diff preview for docs-only paths
- affected documentation paths
- affected documentation links or references
- affected report-index paths, if applicable
- migration risk matrix
- dry-run evidence report

## Safety Invariants

| Field | Value |
| --- | --- |
| `dry_run_only` | `true` |
| `files_moved` | `false` |
| `files_renamed` | `false` |
| `imports_modified` | `false` |
| `source_import_paths_modified` | `false` |
| `execution_enabled` | `false` |
| `provider_enabled` | `false` |
| `api_enabled` | `false` |
| `adapter_enabled` | `false` |
| `ssh_enabled` | `false` |
| `live_command_enabled` | `false` |
| `next_phase_allowed` | `false` |

## Migration Risk Matrix Categories

- `documentation_link_breakage`
- `roadmap_link_breakage`
- `report_index_path_breakage`
- `readme_reference_breakage`
- `test_documentation_reference_breakage`
- `fixture_documentation_reference_breakage`
- `backward_compatibility_breakage`

Every risk row must keep:

```text
migration_allowed_now=false
```

## Report Outputs

Generate reviewer evidence with:

```powershell
python network_lab.py --task docs-only-move-dry-run-evidence-plan
```

Expected outputs:

- `reports/lab-summary/day139_docs_only_move_dry_run_evidence_plan.json`
- `reports/lab-summary/day139_docs_only_move_dry_run_evidence_plan.html`

## Validation

Required local validation:

```powershell
python network_lab.py --task docs-only-move-dry-run-evidence-plan
python -m pytest
python network_lab.py --task report-index
git diff --check
git status --short --branch
```

## Final Safety Summary

| Check | Result |
| --- | --- |
| AGENTS.md read before Day139 work | `true` |
| Not next-day feature | `true` |
| Not Day140 | `true` |
| No file moves | `true` |
| No file renames | `true` |
| No import modifications | `true` |
| No source import path modifications | `true` |
| Execution/provider/API remains disabled | `true` |
| Adapter/SSH/live command remains disabled | `true` |
| next_phase_allowed | `false` |
| final recommendation | `KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET` |
