# Day121 CLI Dispatch Responsibility Split

## Purpose

Day121 reduces `network_lab.py` responsibility by moving CLI parsing and dispatch wiring into `network_lab_cli_dispatch.py`.

This is a refactor-only day. It does not add a new capability, safety gate, runner workflow, report schema, live access path, or execution unlock.

## Expected State

- `network_lab.py` remains the executable entry point.
- `network_lab_cli_dispatch.py` owns argparse setup and task dispatch orchestration.
- Existing public CLI behavior remains unchanged.
- `report-index` internals remain in place and are intentionally not split on Day121.
- Existing report-only and dry-run-only tasks continue to dispatch through the existing task registry and existing task handlers.

## Safety Boundary

Day121 must not introduce:

```text
live_execution = false
ssh_added = false
device_access_added = false
configuration_mutation_added = false
adapter_execution_added = false
broker_execution_added = false
openai_api_added = false
external_ai_runtime_added = false
voice_runtime_added = false
execution_unlock_added = false
dashboard_action_added = false
```

The dispatch split preserves rejected-task behavior. Rejected task names must not invoke handlers, adapters, brokers, runners, SSH, live commands, AI/API calls, voice paths, or device access.

## Evidence Expectations

Validation should show:

```powershell
python -m pytest
python network_lab.py --help
python network_lab.py --task report-index
python network_lab.py --report-index
```

There is no Day121 runner task. The Day121 evidence is the importable dispatch module, compatibility wrappers, tests, and unchanged CLI behavior.
