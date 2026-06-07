# Day61 - AI Intent Demo Dashboard Integration / Reviewer UI Entry Point

## Purpose

Day61 makes the Day57-Day60 AI intent workflow easier to review from the local dashboard.

The goal is to give a reviewer one dashboard entry point for understanding the workflow, the safety boundary, and the existing documentation/report artifacts without running live automation or implementing real v0.3 runtime behavior.

## Scope

In scope:

- Add a dashboard route for the AI intent reviewer entry point.
- Link the entry point from dashboard navigation and the dashboard home quick links.
- Summarize what Day57, Day58, Day59, and Day60 added.
- Link to committed Day57-Day60 AI docs and roadmap docs.
- Reference optional generated Day58-Day60 report paths.
- State the report-only/no-execution safety boundary clearly.
- Update README with the Day61 milestone.

Out of scope:

- OpenAI API integration.
- Voice input or speech recognition.
- Live runner execution.
- SSH or device access.
- Router, switch, firewall, VPN, VRRP, WireGuard, NAT, IP, interface, route, or device configuration changes.
- `config.json` dependency.
- Release tag creation.
- Real v0.3 runtime implementation.
- Day9-Day15 plan changes.

## What Changed

- Added `/ai-intent-reviewer` to the Flask dashboard.
- Added a reviewer-facing dashboard template for the Day57-Day60 workflow.
- Added static dashboard metadata for Day57-Day60 references and safety boundaries.
- Added dashboard navigation links for the new reviewer entry point.
- Added tests for the Day61 route, references, and safety boundary wording.
- Updated README with Day61 progress and reviewer guidance.
- Added this roadmap document.

## Reviewer Workflow

1. Start the dashboard locally with `python dashboard_app.py`.
2. Open `/ai-intent-reviewer`.
3. Review the workflow summary:
   - Day57 maps static text to proposed tasks without execution.
   - Day58 classifies safety and blocks live-capable actions by default.
   - Day59 explains the policy matrix for allowed, blocked, and ambiguous intents.
   - Day60 connects those pieces into a report-only walkthrough.
4. Open the linked Day57-Day60 AI docs and roadmap docs.
5. If local generated reports exist, use `/reports` to inspect Day58-Day60 report evidence.
6. Confirm the expected safety statement remains visible:

```text
No mapped task was executed. This is a dry-run reviewer walkthrough only.
```

## Safety Boundaries

Day61 is documentation/dashboard integration only.

Day61 does not:

- Call OpenAI API.
- Add or use voice input.
- Execute mapped runner tasks.
- Perform live execution.
- Use SSH.
- Access real devices.
- Modify router, switch, firewall, VPN, VRRP, WireGuard, NAT, IP, route, interface, or device settings.
- Require, read, create, or modify `config.json`.
- Create a release tag.
- Implement real v0.3 runtime execution.
- Change Day9-Day15 plans.

The new dashboard page is report-only. It presents committed docs and expected report paths; it does not include a run button or subprocess path.

## Validation Commands

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
git status --short --branch
```

## Known Limitations

- `/ai-intent-reviewer` is a static reviewer entry point, not a real AI assistant.
- Generated Day58-Day60 report files may be absent on a fresh checkout until their report-only tasks are run.
- `report-index` may return WARN with `fail=0` when optional local reports are missing.
- The page does not render Markdown contents inline; it links to committed docs through the existing safe evidence route.

## Next Suggested Step for Day62

Day62 can add a static reviewer example gallery for common intent phrases and expected decisions, still staying report-only and dry-run-only. It should not add OpenAI API, voice input, SSH, live execution, device access, or real v0.3 runtime behavior unless a separate safety design explicitly approves that scope.
