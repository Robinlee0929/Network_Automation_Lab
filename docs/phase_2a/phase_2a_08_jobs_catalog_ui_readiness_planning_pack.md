# Phase 2A-08 Jobs Catalog / UI Readiness Planning Pack

Phase 2A-08 creates a planning-only Jobs Catalog and UI-card readiness pack for
future `/network/jobs` work. It turns the Phase 2A-07 artifact-to-Jobs mapping
into deterministic JSON fields that a future product UI can consume.

This pack is not Phase 2B and is not executable.

## Scope

The catalog includes multiple example job types:

- `baseline_check`
- `interface_status_check`
- `wan_lan_check`
- `vrrp_validation`
- `backup_config_plan`
- `blocked_config_change_request`

VRRP remains one example card, not the whole scope.

## UI-Ready Catalog Fields

Each catalog entry includes:

- `job_id`
- `job_type`
- `display_name`
- `category`
- `user_goal`
- `supported_status`
- `dry_run`
- `planning_only`
- `requires_approval`
- `blocked_reason`
- `safety_summary`
- `forbidden_capabilities_confirmed`
- `ui_card_summary`
- `ui_card`
- `evidence_or_artifact_references`
- `expected_outputs`
- `next_phase_allowed`

The nested `ui_card` object is shaped for future `/network/jobs` consumption
with title, description, status badge, dry-run badge, approval badge, blocked
reason, evidence references, safety lock flags, and UI readiness state.

## Job Disposition

| Job type | UI status | Dry-run | Planning-only | Approval | Notes |
| --- | --- | --- | --- | --- | --- |
| `baseline_check` | planning_only | true | true | false | Local baseline evidence card only |
| `interface_status_check` | planning_only | true | true | false | Local interface/topology evidence card only |
| `wan_lan_check` | planning_only | true | true | false | Local WAN/LAN evidence card only |
| `vrrp_validation` | planning_only | true | true | false | Local mock VRRP example card only |
| `backup_config_plan` | planning_only | true | true | true | Planning-only; no real backup |
| `blocked_config_change_request` | blocked | false | true | true | Blocked config-change card only |

## Existing Artifacts Referenced

Phase 2A-08 references existing planning and evidence patterns rather than
inventing new execution paths:

- `docs/phase2a_readonly_job_runner_framework.md`
- `docs/phase_2a/phase_2a_03_dry_run_job_plan_gate.md`
- `docs/phase_2a/phase_2a_04_plan_evidence_ledger.md`
- `docs/phase_2a/phase_2a_05_dry_run_result_envelope_renderer.md`
- `docs/phase_2a/phase_2a_06_negative_regression_matrix.md`
- `docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md`
- `reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json`
- `reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.html`

## Safety Boundary

The pack keeps these capabilities disabled:

- Phase 2B
- runner
- adapter
- broker
- SSH
- NETCONF
- RESTCONF
- live device access
- provider/API/model calls
- secrets
- real backup
- real VRRP testing
- config changes
- command execution

`next_phase_allowed=false`.

## Outputs

Generated reports:

- `reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json`
- `reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.html`

Run:

```bash
python network_lab.py --task phase2a-08-jobs-catalog-ui-readiness-planning-pack
python -m pytest
python network_lab.py --task report-index
```
