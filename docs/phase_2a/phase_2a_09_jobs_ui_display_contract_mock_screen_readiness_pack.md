# Phase 2A-09 Jobs UI Display Contract / Mock Screen Readiness Pack

Phase 2A-09 defines how a future `/network/jobs` screen should display the
full Phase 2A-08 Jobs Catalog. It is a planning-only, UI-contract-only, mock
screen readiness pack.

This pack is not Phase 2B and is not executable.

## Phase Goal

Define safe display contracts for the future `/network/jobs` list and detail
screens using the Phase 2A-08 Jobs Catalog as the source artifact.

The pack includes:

- job list view contract
- job detail view contract
- badge display rules
- empty state contract
- error state contract
- safety display contract
- mock screen fixture data
- validation tests

## Existing Artifacts Referenced

Phase 2A-09 references existing Phase 2A-08 catalog structures rather than
inventing a new job schema:

- `phase_2a_08_jobs_catalog_ui_readiness_planning_pack.py`
- `docs/phase_2a/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.md`
- `reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.json`
- `reports/lab-summary/phase_2a_08_jobs_catalog_ui_readiness_planning_pack.html`
- `phase_2a_07_vrrp_dry_run_validation_pack.py`
- `docs/phase_2a/phase_2a_07_vrrp_dry_run_validation_pack.md`
- `reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json`

## Example Job Types

The mock screen data covers the full Phase 2A-08 catalog shape:

- `baseline_check`
- `interface_status_check`
- `wan_lan_check`
- `vrrp_validation`
- `backup_config_plan`
- `blocked_config_change_request`

VRRP remains one example among multiple catalog entries. Backup remains a
planning-only or approval-required display example only.

## Job List View Contract

Each job row must show:

- `job_id`
- `job_name`
- `job_type`
- `category`
- `display_status`
- `allowed_or_blocked`
- `planning_only_indicator`
- `dry_run_indicator`
- `approval_required_indicator`
- `blocked_reason`
- `evidence_summary`
- `evidence_count`
- `safety_summary`
- `badges`

Rows are display-only. Selecting a row may open details in a future UI, but it
must not execute a job.

## Job Detail View Contract

Each job detail view must show:

- what the job can do
- what the job cannot do
- why it is blocked, if blocked
- why approval is required, if required
- referenced evidence
- related artifact or ledger reference
- dry-run boundary
- no-execution proof
- no live-device proof
- no SSH / NETCONF / RESTCONF proof
- safety display
- badges

## Badge Rules

Phase 2A-09 defines rules for:

- `allowed`
- `blocked`
- `planning-only`
- `dry-run`
- `approval-required`
- `mock-only`
- `local-only`
- `no-runner`
- `no-ssh`
- `no-live-device`
- `invalid-catalog`
- `empty-catalog`

Every badge is display-only and has `executable_allowed=false`.

## Empty State

The future UI must safely display:

- no catalog exists
- catalog exists but has zero jobs
- no displayable jobs are available

Empty states must not suggest running, executing, starting, connecting, or
launching a job.

## Error State

The future UI must block executable interpretation for:

- malformed JSON
- missing required fields
- unknown status
- forbidden execution fields
- unsafe capability

Invalid catalog payloads are display errors only. They must not be converted
into executable jobs.

## Safety Display

Every mock screen output must show:

- no SSH
- no runner
- no live device
- no NETCONF
- no RESTCONF
- dry-run only
- planning/mock/local only
- not Phase 2B

## Forbidden Scope

Phase 2A-09 does not introduce:

- Phase 2B
- real runner
- job execution
- adapter
- SSH
- NETCONF
- RESTCONF
- live device access
- live device pilot
- real backup
- real VRRP test or execution
- real frontend API integration
- provider, model, or API call
- secrets or credentials handling
- shell/script runner
- broker
- scheduler
- queue worker

## Outputs

Generated reports:

- `reports/lab-summary/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.json`
- `reports/lab-summary/phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack.html`

Run:

```bash
python network_lab.py --task phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack
python -m pytest
python network_lab.py --report-index
```
