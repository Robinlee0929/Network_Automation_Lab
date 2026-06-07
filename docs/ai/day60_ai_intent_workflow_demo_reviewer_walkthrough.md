# Day60 - AI Intent Workflow Demo / Reviewer Walkthrough Flow

## Purpose

Day60 connects Day57, Day58, and Day59 into one reviewer-facing walkthrough flow. The goal is to let a reviewer run a local demo of the AI intent workflow and verify the safety model without connecting any real AI API, voice input, SSH session, lab device, or live execution path.

This is documentation-only and report-only. The walkthrough explains how an intent would be mapped, reviewed, explained, and allowed or blocked. It does not execute the mapped task.

## Relationship to Day57, Day58, and Day59

- Day57 introduced deterministic, dry-run-only intent mapping from static text to reviewed runner task proposals.
- Day58 added intent safety review and confirmation gate design, with live-capable actions blocked by default.
- Day59 added a reviewer-facing policy matrix explaining which intent categories are allowed, blocked, or require future confirmation.
- Day60 ties those three artifacts into a single local walkthrough report that a reviewer can inspect.

## Reviewer Walkthrough Steps

1. Input intent text.
2. Review the Day57-style dry-run intent mapping.
3. Review the Day58-style safety classification.
4. Review the Day59-style policy explanation.
5. Confirm the reviewer decision: allowed or blocked.
6. Verify that no execution was performed.

The final safety statement must remain:

```text
No mapped task was executed. This is a dry-run reviewer walkthrough only.
```

## Demo Commands

```powershell
python network_lab.py --task intent-workflow-demo
python network_lab.py --task report-index
```

Optional context commands:

```powershell
python network_lab.py --task intent-mapping-prototype --intent-text "show latest reports"
python network_lab.py --task intent-safety-review --intent-text "do VRRP failover test"
python network_lab.py --task intent-policy-matrix
python network_lab.py --list-tasks --verbose
```

## Expected Outputs

The Day60 task writes:

- `reports/portfolio/day60_intent_workflow_demo.json`
- `reports/portfolio/day60_intent_workflow_demo.html`

The console should show `PASS` and this exact sentence:

```text
No mapped task was executed. This is a dry-run reviewer walkthrough only.
```

The generated report includes these example intents:

| Intent text | Expected classification | Reviewer decision |
| --- | --- | --- |
| `show latest reports` | report-only | allowed |
| `explain available runner tasks` | documentation/report-only | allowed |
| `do VRRP failover test` | live-capable | blocked by default |
| `change router firewall rule` | configuration-changing | blocked |
| `run WireGuard throughput test` | live-capable | blocked unless future guarded-live flow exists |

## Safety Boundaries

Day60 must not:

- Connect OpenAI API.
- Add or use voice input.
- Execute mapped tasks.
- Run live network tests.
- Use SSH.
- Touch MikroTik, Cisco, router, switch, firewall, VPN, or device settings.
- Read or require `config.json`.
- Modify NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.
- Create release tags.
- Start the real v0.3 runtime implementation.

## What Is Intentionally Not Implemented

- Real AI assistant runtime.
- OpenAI API integration.
- Voice input or speech recognition.
- Live intent-to-runner execution.
- SSH/device connectivity.
- Config loading.
- Router, firewall, NAT, VPN, VRRP, route, or interface changes.
- Release tagging.

## Suggested Reviewer Questions and Answers

**Q: Does Day60 call an AI model?**  
A: No. The report is deterministic local data and code.

**Q: Can an allowed report-only intent trigger `report-index` automatically?**  
A: No. Day60 records the reviewer decision only. It does not delegate to the mapped task.

**Q: Why are VRRP and WireGuard examples blocked?**  
A: They are live-capable workflows. The current intent workflow may explain them, but it cannot run them.

**Q: Why is a firewall change blocked?**  
A: It is configuration-changing and outside the safe reviewer walkthrough boundary.

**Q: Does Day60 require `config.json`?**  
A: No. The task runs before profile loading and does not read or require `config.json`.

## Troubleshooting Notes

- If the Day60 report is missing from `report-index`, run `python network_lab.py --task intent-workflow-demo` first.
- `report-index` may return `WARN` when optional generated local reports from prior days are missing. This is acceptable when `fail=0`.
- If a reviewer sees any output implying SSH, device access, API access, or mapped task execution, treat that as a Day60 safety failure.
