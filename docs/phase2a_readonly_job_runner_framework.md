# Phase 2A-02 Job Spec Contract Validator + Negative Input Matrix

Phase 2A-02 is a validator, contract, matrix, and evidence task for the Job Runner Framework.

It does not unlock execution. It does not introduce live I/O. It does not add SSH, NETCONF, RESTCONF, RouterOS, provider/API/model calls, backup_config execution, config_change execution, arbitrary command execution, shell execution, scriptPath execution, or real adapter integration.

Status markers:

- PHASE_2A_STARTED
- JOB_SPEC_CONTRACT_VALIDATOR_READY
- ALLOWLIST_SCHEMA_PRIMARY_TRUE
- DENYLIST_EVIDENCE_ONLY_TRUE
- NEGATIVE_INPUT_MATRIX_RECORDED_TRUE
- INVALID_JOB_SPECS_REJECTED_BEFORE_RUNNER_TRUE
- RUNNER_INVOKED_FALSE_FOR_REJECTIONS_TRUE
- SAFE_ARTIFACT_PATHS_ONLY_TRUE
- NEXT_PHASE_ALLOWED_FALSE
- MOCK_ONLY_TRUE
- LOCAL_ONLY_TRUE
- LIVE_DEVICE_ACCESS_FALSE
- SSH_ENABLED_FALSE
- NETCONF_ENABLED_FALSE
- RESTCONF_ENABLED_FALSE
- ARBITRARY_COMMAND_ALLOWED_FALSE
- ARBITRARY_SCRIPT_PATH_ALLOWED_FALSE
- BACKUP_CONFIG_RUN_ALLOWED_FALSE
- CONFIG_CHANGE_ALLOWED_FALSE

## Scope

The validator transplants the prior executor, adapter, parser, and safety-gate model into the Phase 2A Job Runner Framework as a strict job spec contract.

Positive allowlisted schemas are the primary safety mechanism:

- allowed top-level fields: `job_type`, `inputs`
- allowed job types: `mock_parse_report`, `mock_collect_local_evidence`, `mock_validate_existing_artifact`
- allowed input fields are fixed per job type
- invalid specs are rejected before runner invocation
- rejected specs record `runner_invoked=false`

Denylist checks and the negative input matrix are evidence. They are not the only protection.

## Forbidden Job Types

The following job types are explicitly forbidden:

- backup_config
- config_change
- ssh_command
- netconf_get
- restconf_get
- custom_command
- custom_script_path

Unknown job types are rejected because they are not allowlisted.

## Dangerous Fields

Dangerous execution-capable fields are rejected even when the job type is otherwise allowed.

Covered fields and values include:

- command
- cmd
- shell
- scriptPath
- script_path
- custom_script_path
- executable_path
- host
- ip
- device
- routeros
- ssh
- username
- password
- port: 22
- netconf
- restconf
- api_key
- provider
- model

## Safe Artifact Paths

Path values are not globally allowed. Paths are only accepted through explicit artifact-style fields:

- artifact_path
- report_path
- evidence_ref for a non-executing reviewer reference

Artifact/report paths must be repo-local and under an approved artifact directory:

- reports
- docs
- fixtures
- summary

Path validation rejects:

- absolute paths
- URLs
- path traversal using `..`
- paths outside approved repo-local artifact directories
- paths pointing to secrets, `.env` files, credentials, keys, or key-like files
- paths pointing to executable scripts or executable file types
- paths used as scripts or commands

## Negative Input Matrix

The JSON/HTML report records a negative input matrix covering:

- safe allowed job type passes
- unknown job type fails
- forbidden job type fails
- allowed job type with command, cmd, shell, scriptPath, script_path, or custom_script_path fails
- allowed job type with host, ip, device, routeros, ssh, username, password, port 22, netconf, restconf, api_key, provider, or model fails
- allowed job type with unknown extra input field fails
- absolute artifact path fails
- path traversal artifact path fails
- secret-like artifact path fails
- rejected specs do not invoke the runner

All rejected cases must keep `runner_invoked=false`.

## Review Evidence

Generate reviewer-visible evidence with:

```bash
python network_lab.py --task phase2a-readonly-job-runner-framework
```

Evidence outputs:

- `reports/lab-summary/phase2a_readonly_job_runner_framework.json`
- `reports/lab-summary/phase2a_readonly_job_runner_framework.html`

The task remains mock/local/review-only and keeps `next_phase_allowed=false`.
