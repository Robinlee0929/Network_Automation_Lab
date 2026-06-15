# Day140 Folder Move Compatibility Gate AI Intent

## Intent

Create reviewer-visible compatibility evidence for deciding whether a future first-batch docs-only move review may begin.

This is not the next-day feature implementation.

No file or folder movement is allowed.

No execution, provider, or API is enabled.

The task must remain review-only, report-only, dry-run-only, docs-only, local-only, and non-executing.

## Required Boundary

- Do not move files.
- Do not move folders.
- Do not rename files.
- Do not rename folders.
- Do not modify import statements.
- Do not modify source-code import paths.
- Do not change the real repository structure.
- Do not implement the next-day feature.
- Do not enable execution.
- Do not enable providers.
- Do not enable APIs.
- Do not add adapter behavior.
- Do not add broker behavior.
- Do not add runner behavior.
- Do not add SSH behavior.
- Do not add NETCONF behavior.
- Do not add RESTCONF behavior.
- Do not add live command behavior.
- Do not add router access.
- Do not use network access.
- Do not use secrets.

## Expected Report Fields

- `day: 140`
- `task: folder-move-compatibility-gate`
- `mode: REVIEW_ONLY`
- `agents_md_read_before_day140_work: true`
- `agents_md_pre_read_result: PASS`
- `files_moved_count: 0`
- `folders_moved_count: 0`
- `imports_modified_count: 0`
- `execution_allowed: false`
- `provider_enabled: false`
- `api_enabled: false`
- `ssh_allowed: false`
- `netconf_allowed: false`
- `restconf_allowed: false`
- `live_command_allowed: false`
- `adapter_execution_allowed: false`
- `broker_execution_allowed: false`
- `runner_execution_allowed: false`
- `next_day_feature_implemented: false`
- `first_batch_docs_only_move_review_allowed: true`
- `final_recommendation: READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW`

## Evidence Sections

The report must include:

- `docs_only_move_candidates`
- `import_sensitive_exclusions`
- `cli_task_test_report_index_reference_audit`
- `compatibility_decision_inputs`
- `safety_invariants`
- `final_recommendation`

## Expected Result

```text
overall_status=PASS
status=FOLDER_MOVE_COMPATIBILITY_GATE_READY_FOR_FUTURE_DOCS_ONLY_REVIEW
mode=REVIEW_ONLY
final_recommendation=READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW
```

Readiness only means a future docs-only move review may begin; it never authorizes moving files now.
