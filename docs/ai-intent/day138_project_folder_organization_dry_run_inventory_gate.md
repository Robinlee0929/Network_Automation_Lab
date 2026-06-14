# Day138 Project Folder Organization Dry-Run Inventory Gate AI Intent

## Intent

Create reviewer-visible dry-run inventory evidence for the current repository file layout before any future folder organization proposal.

This is not the next day's feature.

No execution, provider, or API is enabled.

The task must remain report-only, dry-run-only, local-only, and mock-safe.

## Required Boundary

- Do not move files.
- Do not delete files.
- Do not rename files.
- Do not change import paths.
- Do not reorganize folders.
- Do not enable execution.
- Do not enable providers.
- Do not enable APIs.
- Do not allow SSH.
- Do not allow live commands.
- Do not invoke adapters, brokers, runners, or mapped execution paths.
- Do not unlock the next phase.

## Expected Report Fields

- `agents_md_pre_read: true`
- `forbidden_actions.move: false`
- `forbidden_actions.delete: false`
- `forbidden_actions.rename: false`
- `forbidden_actions.import_path_change: false`
- `forbidden_actions.execution_enabled: false`
- `forbidden_actions.provider_enabled: false`
- `forbidden_actions.api_enabled: false`
- `forbidden_actions.ssh_allowed: false`
- `forbidden_actions.live_command_allowed: false`
- `next_phase_allowed: false`
- `final_recommendation: KEEP_DRY_RUN_INVENTORY_ONLY`
- `not_next_day_feature_statement: This is not the next day's feature.`
- `no_execution_provider_api_statement: No execution, provider, or API is enabled.`

## Inventory Requirement

The report inventories current repo file groups only:

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

Each inventory group must include `group_name`, `file_count`, `sample_files`, `current_location`, `future_organization_candidate`, `risk_level`, and `reason`.

## Expected Result

```text
overall_status=PASS
status=PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_RECORDED
mode=DRY_RUN_INVENTORY_ONLY
final_recommendation=KEEP_DRY_RUN_INVENTORY_ONLY
next_phase_allowed=false
```
