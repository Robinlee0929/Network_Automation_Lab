# Day140 - Folder Move Compatibility Gate

## Scope

This is Day140.

This is not the next-day feature implementation.

This task only decides whether the repository is compatible with entering a future first-batch docs-only move review.

It does not move files, move folders, rename files, rename folders, modify import statements, modify source import paths, or change the real repository structure.

It does not enable execution, provider behavior, API behavior, adapters, brokers, runners, mapped execution, SSH, NETCONF, RESTCONF, live commands, router access, secrets, or external integrations.

No execution, provider, or API is enabled.

Readiness only means a future docs-only move review may begin; it never authorizes moving files now.

## AGENTS.md Compliance

| Check | Result |
| --- | --- |
| AGENTS.md found | YES |
| AGENTS.md read before Day140 work | YES |
| AGENTS.md pre-read result | PASS |
| AGENTS.md modified | NO |
| AGENTS.md path | `AGENTS.md` |

## Task

Task name:

```text
folder-move-compatibility-gate
```

Mode:

```text
REVIEW_ONLY
```

Source scope:

```text
docs-only compatibility review
```

Expected final recommendation:

```text
READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW
```

## Required Evidence

Day140 records:

- docs-only move candidates that are identifiable for future review
- whether candidate docs are isolated enough to review later
- import-sensitive files excluded from a first-batch docs-only review
- CLI, task, test, and report-index references that could be affected by a future docs movement
- explicit no-move, no-import-change, no-execution, no-provider, no-API, and no-live-device safety boundaries

## Safety Invariants

| Field | Value |
| --- | --- |
| `files_moved_count` | `0` |
| `folders_moved_count` | `0` |
| `imports_modified_count` | `0` |
| `execution_allowed` | `false` |
| `provider_enabled` | `false` |
| `api_enabled` | `false` |
| `ssh_allowed` | `false` |
| `netconf_allowed` | `false` |
| `restconf_allowed` | `false` |
| `live_command_allowed` | `false` |
| `adapter_execution_allowed` | `false` |
| `broker_execution_allowed` | `false` |
| `runner_execution_allowed` | `false` |
| `next_day_feature_implemented` | `false` |
| `move_allowed_now` | `false` |

## Decision Rule

The gate may allow only a future review, not a move.

The gate fails if any file or folder was moved, if imports were modified, if execution/provider/API behavior appears enabled, if SSH/NETCONF/RESTCONF/live-device behavior appears enabled, or if AGENTS.md was not read before Day140 work.

If docs-only candidates are identifiable and all safety boundaries remain locked, the gate may return:

```text
READY_FOR_FUTURE_DOCS_ONLY_MOVE_REVIEW
```

## Report Outputs

Generate reviewer evidence with:

```powershell
python network_lab.py --task folder-move-compatibility-gate
```

Expected outputs:

- `reports/lab-summary/day140_folder_move_compatibility_gate.json`
- `reports/lab-summary/day140_folder_move_compatibility_gate.html`

## Validation

Required local validation:

```powershell
git status --short --branch
python -m pytest
python network_lab.py --task folder-move-compatibility-gate
python network_lab.py --task report-index
git diff --check
git status --short --branch
```

## Final Safety Summary

| Check | Result |
| --- | --- |
| AGENTS.md pre-read | `PASS` |
| AGENTS.md read before Day140 work | `true` |
| files moved | `0` |
| folders moved | `0` |
| imports modified | `0` |
| execution/provider/API enabled | `false` |
| SSH/NETCONF/RESTCONF/live command enabled | `false` |
| adapter/broker/runner execution enabled | `false` |
| next-day feature implemented | `false` |
| first-batch docs-only move review allowed | future review only |
