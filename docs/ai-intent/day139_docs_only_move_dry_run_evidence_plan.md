# Day139 Docs-Only Move Dry-Run Evidence Plan AI Intent

## Intent

Create reviewer-visible docs-only dry-run evidence for a possible future documentation organization move.

This is not the next-day feature implementation.

This is not Day140.

This is not Folder Move Compatibility Gate.

No execution, provider, or API is enabled.

The task must remain review-only, dry-run-only, docs-only, local-only, and non-executing.

## Required Boundary

- Do not move files.
- Do not rename files.
- Do not modify import statements.
- Do not modify source-code import paths.
- Do not change the real repository structure.
- Do not make the move proposal executable.
- Do not mark docs migration as allowed.
- Do not enable execution.
- Do not enable providers.
- Do not enable APIs.
- Do not add adapter behavior.
- Do not add SSH behavior.
- Do not add live command behavior.
- Do not add router access.
- Do not add broker, runner, mapped execution, or real external integration.
- Do not use network access.
- Do not use secrets.

## Expected Report Fields

- `day: Day139`
- `task: docs-only-move-dry-run-evidence-plan`
- `title: Docs-Only Move Dry-Run Evidence Plan`
- `mode: REVIEW_ONLY`
- `based_on_day: Day138`
- `source_scope: docs-only`
- `agents_md_read_before_day139_work: true`
- `dry_run_only: true`
- `files_moved: false`
- `files_renamed: false`
- `imports_modified: false`
- `source_import_paths_modified: false`
- `execution_enabled: false`
- `provider_enabled: false`
- `api_enabled: false`
- `adapter_enabled: false`
- `ssh_enabled: false`
- `live_command_enabled: false`
- `next_phase_allowed: false`
- `final_recommendation: KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET`

## Evidence Sections

The report must include:

- `hypothetical_docs_target_folders`
- `docs_only_dry_run_move_pairs`
- `proposal_diff_preview`
- `affected_doc_paths`
- `affected_doc_links`
- `affected_report_index_paths`
- `migration_risk_matrix`
- `safety_invariants`
- `final_recommendation`

## Expected Result

```text
overall_status=PASS
status=DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_RECORDED
mode=REVIEW_ONLY
source_scope=docs-only
final_recommendation=KEEP_DRY_RUN_ONLY_DO_NOT_MOVE_DOCS_YET
next_phase_allowed=false
```
