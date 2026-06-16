# Phase 2A-03 Job Request Normalization and Dry-Run Plan Gate

Phase 2A-03 is a dry-run plan-only safety gate for controlled Phase 2A job
requests.

It normalizes allowlisted mock/local/read-only request shapes and renders
non-executable dry-run plans for reviewer evidence. It rejects dangerous,
live-capable, provider-capable, or arbitrary execution-capable requests before
plan generation.

## Scope

- Phase 2A-03 is dry-run plan-only.
- Phase 2A-03 does not open live execution.
- Phase 2A-03 does not invoke a runner.
- Phase 2A-03 does not invoke an adapter.
- Phase 2A-03 does not authorize Phase 2B.
- Phase 2A-03 does not authorize real device execution.
- Phase 2A-03 does not add SSH, NETCONF, RESTCONF, backup_config, config
  change, arbitrary command, scriptPath, provider API, OpenAI API, or model-call
  behavior.

## Allowed Job Types

The gate reuses the Phase 2A allowlist:

- `mock_parse_report`
- `mock_collect_local_evidence`
- `mock_validate_existing_artifact`

Allowed requests may include only the existing controlled input fields for their
job type, such as `report_path`, `artifact_path`, and `evidence_ref`. Artifact
references must remain reviewer-safe local references under approved repository
evidence roots.

## Rejected Job Types

The gate rejects these job types before plan generation:

- `backup_config`
- `config_change`
- `ssh_command`
- `netconf_get`
- `restconf_get`
- `arbitrary_command`
- `custom_command`
- `scriptPath`
- `custom_script_path`
- `arbitrary_script_path`
- `provider_api_call`
- `model_call`

## Rejected Fields

The gate rejects dangerous or live-target fields anywhere in the request,
including:

- `host`
- `hostname`
- `ip`
- `username`
- `password`
- `secret`
- `token`
- `ssh`
- `netconf`
- `restconf`
- `command`
- `cmd`
- `shell`
- `custom_command`
- `scriptPath`
- `script_path`
- `custom_script_path`
- `arbitrary_script_path`
- `provider`
- `provider_api`
- `api_key`
- `model`

Port `22` is also rejected as a live SSH target signal.

## Dry-Run Plan Format

Allowed requests produce a plan shaped as:

- `plan_id`: `phase_2a_03::<job_type>`
- `plan_type`: `non_executable_dry_run_job_plan`
- `execution_mode`: `dry-run-plan-only`
- `executable`: `false`
- `safe_artifact_references`: validated `report_path`, `artifact_path`, or
  `evidence_ref` values only
- `steps`: semantic review steps with `executable=false`
- `non_executable_proof`: all command, script, credential, target, runner, and
  adapter capability booleans set to `false`

Plan steps are descriptive reviewer evidence only. They do not contain shell
commands, device commands, SSH commands, script paths, credentials, live host
targets, runner calls, or adapter calls.

## Required Safety Flags

Every report keeps these flags false:

- `live_execution_opened`
- `runner_invoked`
- `adapter_invoked`
- `ssh_enabled`
- `netconf_enabled`
- `restconf_enabled`
- `backup_config_enabled`
- `config_change_enabled`
- `arbitrary_command_enabled`
- `arbitrary_script_path_enabled`
- `provider_api_enabled`
- `model_call_enabled`
- `next_phase_allowed`

## Reviewer Evidence

The fixed CLI task:

```bash
python network_lab.py --task phase2a-03-dry-run-job-plan-gate
```

writes:

- `reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.json`
- `reports/lab-summary/phase_2a_03_dry_run_job_plan_gate.html`

The task does not accept arbitrary job execution input. It renders a fixed local
evidence report for reviewer inspection only.
