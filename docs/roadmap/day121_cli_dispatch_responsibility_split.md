# Day121 CLI Dispatch Responsibility Split

## Scope

Day121 extracts CLI parsing and task dispatch orchestration out of `network_lab.py` into `network_lab_cli_dispatch.py`.

`network_lab.py` remains the main entry point and keeps compatibility wrappers for callers that import `main()`, `_build_parser()`, `_build_task_handlers()`, or `_run_profile_backed_cli_task()`.

## AGENTS.md Read Status

YES. The repository `AGENTS.md` instructions were read before Day121 work.

## Implementation Notes

- Added `network_lab_cli_dispatch.py` for argparse setup, CLI task handler wiring, profile-backed dispatch, and exit-code flow.
- Kept task implementation bodies, report generation helpers, and report-index internals in `network_lab.py`.
- Preserved `python network_lab.py --help`, `python network_lab.py --task report-index`, `python network_lab.py --report-index`, and existing task dispatch behavior.
- Added focused tests for the importable dispatch module, script help entry point, both report-index entry paths, one lightweight report-only task path, and dependency-import safety.

## Safety Boundary

Day121 is a structure-only CLI dispatch refactor.

No live execution, SSH capability, device access, adapter execution, broker execution, OpenAI API call, external AI runtime, voice input, speech-to-text, text-to-speech, microphone, cloud execution, execution unlock, configuration mutation, or dashboard action is added.

Unknown or rejected task names remain non-executing through the existing task registry rejection path.

## Explicit Non-Changes

- `report-index` implementation was intentionally not split.
- Report schemas and generated report filenames were not changed.
- Task behavior and task safety semantics were not changed.
- No Day121 dedicated runner task was added.

## Required Validation

Run before closeout:

```bash
python -m pytest
python network_lab.py --help
python network_lab.py --task report-index
python network_lab.py --report-index
```

No Day121 task command is required because Day121 does not add a dedicated runner task.
