# Day62 - AI Intent Reviewer Scenario Pack / Sample Cases

## Purpose

Day62 adds a reviewer-readable scenario pack for the AI Intent Reviewer flow.

The goal is to help a human reviewer understand how natural-language intents should be classified, mapped, blocked, or kept report-only before any future v0.3 assistant work is considered.

Day62 is documentation-only and report-only. It is not an AI decision system, not a runtime assistant, and not a device automation layer.

## Reviewer Scenario Pack Concept

The scenario pack is a static set of sample user intents with expected reviewer decisions. Each case shows:

- The natural-language request.
- The intent category.
- The expected reviewer decision.
- Whether the request stays report-only, dry-run-only, blocked, or clarification-required.
- The safety reason a reviewer should look for.

The pack is meant to make review expectations explicit. It does not run the mapped task, call a model, collect voice input, open SSH, or contact lab devices.

## Sample Intent Categories

Day62 covers these reviewer categories:

| Category | Reviewer meaning | Expected decision |
| --- | --- | --- |
| Report-only request | Reads or summarizes existing local evidence. | Allowed as report-only. |
| Dashboard navigation request | Points a reviewer to a local static dashboard page. | Reviewer-visible with no device action. |
| Dry-run request | Shows a proposed workflow without running it. | Dry-run only; no execution. |
| Direct execution request | Asks to apply or run a live network change. | Blocked. |
| SSH request | Asks to open a live device session. | Blocked. |
| Live failover request | Asks to trigger HA / VRRP behavior now. | Blocked. |
| Ambiguous automation request | Asks for broad automatic repair or optimization. | Blocked or requires human clarification. |
| Voice-driven request | Asks to control network settings by voice. | Blocked; voice is out of scope. |
| OpenAI/API request | Asks a model or API to decide the action. | Blocked/out of scope for Day62. |
| Existing report index request | Reviews local report availability and optional missing reports. | Report-only. |

## Expected Reviewer Decisions

Allowed as report-only:

- Generate a report summary for existing test results.
- Show existing reports and missing optional reports.
- Open the AI intent reviewer page.

Allowed as dry-run only:

- Show what would happen if I run the WireGuard workflow.
- Map this request to a proposed task without running it.

Blocked:

- Apply this WireGuard config to the router.
- SSH into the router and change firewall rules.
- Trigger VRRP failover now.
- Use my voice command to change router settings.
- Send this intent to OpenAI and let it decide.

Blocked or clarification-required:

- Fix the network automatically.
- Make the lab better.

## Reusable Scenario Pack

The reusable Day62 scenario pack lives at:

```text
docs/ai/intent_reviewer_scenario_pack.md
```

It is a committed Markdown artifact for reviewers. The dashboard links to it from `/ai-intent-reviewer`, but the page does not parse the file, submit the examples, or trigger any action from the examples.

## Safety Boundaries

Day62 does not:

- Connect OpenAI API.
- Add or use voice input.
- Execute mapped tasks.
- Add live execution.
- Use SSH.
- Access real devices.
- Modify router, switch, firewall, VPN, VRRP, NAT, interface, route, IP, WireGuard, or device settings.
- Add a `config.json` dependency.
- Create a release tag.
- Implement real v0.3 runtime execution.
- Modify Day9-Day15 plans or historical behavior.
- Add any feature that can execute mapped tasks automatically.

## Dashboard Reviewer Content

The `/ai-intent-reviewer` dashboard page may point reviewers to the scenario pack and summarize what Day62 adds.

Allowed dashboard content:

- Static link to `docs/ai/intent_reviewer_scenario_pack.md`.
- Static reviewer guidance.
- Static safety boundary text.

Not allowed dashboard content:

- Action runner.
- SSH trigger.
- API call.
- Task execution endpoint.
- Form submission that triggers mapped actions.
- Device operation button.

## Validation Steps

Run:

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
git status --short --branch
```

Expected validation result:

- `pytest` passes.
- `report-index` may return WARN only when optional generated local reports are missing and `fail=0`.
- `intent-workflow-demo` returns PASS and keeps the statement that no mapped task was executed.
- The working tree contains only Day62 documentation, static dashboard text, and tests before commit.

## What Day62 Intentionally Does Not Implement

Day62 intentionally does not implement:

- A real AI reviewer.
- OpenAI API integration.
- Voice input.
- Live intent-to-runner execution.
- SSH/device connectivity.
- Device configuration workflows.
- New runner tasks.
- New dashboard execution buttons.
- New task execution endpoints.
- Release tagging.
- Real v0.3 runtime behavior.

Day62 is a reviewer scenario pack only.
