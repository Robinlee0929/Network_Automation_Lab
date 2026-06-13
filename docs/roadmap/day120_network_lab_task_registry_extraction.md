# Day120 Network Lab Task Registry Extraction / Thin CLI Foundation

## Scope

Extract the `network_lab.py` task-name registry, task aliases, and handler resolve/lookup behavior into `network_lab_task_registry.py`.

`network_lab.py` remains the CLI entrypoint with argparse and `main()`. Task implementation bodies, report-index behavior, output formatting, safety invariant helpers, and Day119 ledger schema stay unchanged.

## AGENTS.md Read Status

YES. The repository AGENTS.md instructions were read before Day120 work.

## Implementation Notes

- Added `network_lab_task_registry.py` with ordered canonical task names, compatibility aliases, unknown-task rejection, and handler resolution.
- Kept `network_lab.py` as the CLI entrypoint.
- Replaced argparse task choices with the registry choice list.
- Replaced the long task-dispatch ladder with registry-backed handler lookup while preserving the existing interactive/profile-load ordering.
- Added focused registry tests for canonical resolution, alias resolution, unknown task rejection, handler callability, and task catalog preservation.

## Safety Boundary

Day120 is a CLI refactor only.

No live execution, SSH, adapter, broker, OpenAI, LLM provider, voice input, speech-to-text, text-to-speech, microphone, cloud execution, execution unlock, new reviewer gate, acceptance gate, closure package, or safety gate support is added.

Rejected or unknown task names remain non-executing. Aliases resolve only to existing canonical report/task handlers.

## Required Validation

Run before closeout:

```bash
python network_lab.py --task reviewer-evidence-intake-outcome-ledger
python network_lab.py --task deferred-evidence-collection-log
python network_lab.py --task report-index
python network_lab.py --report-index
python network_lab.py --help
python -m pytest
git status --short --branch
```

For `report-index`, existing optional local report warnings are acceptable only when they do not indicate a safety regression.
