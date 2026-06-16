# Phase 2A Read-only Job Runner Framework

Phase 2A has started.

Status markers:

- PHASE_2A_STARTED
- READ_ONLY_JOB_RUNNER_FRAMEWORK_SCAFFOLD_READY
- MOCK_ONLY_TRUE
- LOCAL_ONLY_TRUE
- LIVE_DEVICE_ACCESS_FALSE
- SSH_ENABLED_FALSE
- ARBITRARY_COMMAND_ALLOWED_FALSE
- ARBITRARY_SCRIPT_PATH_ALLOWED_FALSE
- BACKUP_CONFIG_RUN_ALLOWED_FALSE
- CONFIG_CHANGE_ALLOWED_FALSE

## Scope

Phase 2A only prepares a mock/local read-only job runner framework scaffold.

It is framework-only. It records deterministic local/mock result records for fixed job types and reviewer evidence.

Allowed job types are fixed:

- mock_parse_report
- mock_collect_local_evidence
- mock_validate_existing_artifact

Explicitly rejected job types include:

- backup_config
- config_change
- ssh_command
- netconf_get
- restconf_get
- custom_command
- custom_script_path

## Safety Boundary

Phase 2A is not live execution.

Phase 2A is not SSH.

Phase 2A is not NETCONF.

Phase 2A is not RESTCONF.

Phase 2A is not arbitrary command execution.

Phase 2A is not arbitrary script path execution.

Phase 2A is not backup_config execution.

Phase 2A is not config change execution.

Phase 2A does not connect to any live device.

Phase 2A does not call external APIs.

Phase 2A does not call any AI provider or model.

Rejected job types and rejected fields return structured safe rejection records with no adapter, broker, live execution, SSH, NETCONF, RESTCONF, command, script path, provider, API, model-call, backup, or configuration-change capability opened.
