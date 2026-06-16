# Phase 2A-04 Dry-Run Job Plan Evidence Binding / Traceability Ledger

Phase 2A-04 is an evidence-binding-only step for Phase 2A-03 dry-run job plan
outcomes.

It creates a reviewer-visible traceability ledger from already built Phase
2A-03 dry-run outcomes. Accepted dry-run plans become accepted evidence records.
Rejected unsafe requests become rejected evidence records with deterministic
`REJECTED_NO_PLAN_<stable_digest>` source plan identifiers.

## Scope

- Phase 2A-04 is evidence-binding only.
- Phase 2A-04 does not execute jobs.
- Phase 2A-04 does not invoke a runner.
- Phase 2A-04 does not invoke an adapter.
- Phase 2A-04 does not open live execution.
- Phase 2A-04 does not open SSH, NETCONF, RESTCONF, provider/API/model,
  backup_config, arbitrary command, or arbitrary script path capability.
- Phase 2A-04 does not authorize Phase 2B.
- Phase 2A-04 does not authorize real execution.
- Phase 2A-04 stops after traceability ledger generation.

## Evidence Record Format

Each ledger record includes:

- `evidence_id`
- `source_job_type`
- `source_plan_id`
- `safe_normalized_request_summary`
- `accepted_or_rejected`
- `rejection_reason`
- `safe_artifact_references`
- `non_executable_proof`
- `runner_invoked=false`
- `adapter_invoked=false`
- `live_execution_opened=false`
- `next_phase_allowed=false`

Accepted records bind directly to the Phase 2A-03 `plan_id`.

Rejected records bind to a deterministic no-plan identifier:

```text
REJECTED_NO_PLAN_<stable_digest>
```

Unsafe rejected source values are represented through digest-backed safe
references instead of executable-looking payload text.

## Validation Rules

The Phase 2A-04 validator proves:

- every accepted Phase 2A-03 dry-run plan has an evidence record
- every rejected unsafe Phase 2A-03 request has an evidence record
- every evidence record has non-execution proof
- no evidence record contains executable command, script path, host, credential,
  provider, model, token, endpoint, live target, SSH, NETCONF, RESTCONF, or
  backup_config payload data
- no runner invocation is represented
- no adapter invocation is represented
- live execution is not opened
- Phase 2B is not authorized
- real execution is not authorized
- `next_phase_allowed=false`

## Report Safety Summary

The fixed report includes:

- `phase="2A-04"`
- `status="PASS"` only when all validation rules pass
- `mode="report_only"`
- `scope="mock_local_read_only_dry_run"`
- `runner_invoked=false`
- `adapter_invoked=false`
- `live_execution_opened=false`
- `ssh_execution_opened=false`
- `netconf_execution_opened=false`
- `restconf_execution_opened=false`
- `provider_api_model_call_opened=false`
- `backup_config_invoked=false`
- `arbitrary_command_execution_opened=false`
- `arbitrary_script_path_execution_opened=false`
- `phase_2b_authorized=false`
- `real_execution_authorized=false`
- `next_phase_allowed=false`

## Reviewer Evidence

The fixed CLI task:

```bash
python network_lab.py --task phase2a-04-plan-evidence-ledger
```

writes:

- `reports/lab-summary/phase_2a_04_plan_evidence_ledger.json`
- `reports/lab-summary/phase_2a_04_plan_evidence_ledger.html`

The task does not accept arbitrary job execution input. It renders a fixed local
evidence ledger for reviewer inspection only.
