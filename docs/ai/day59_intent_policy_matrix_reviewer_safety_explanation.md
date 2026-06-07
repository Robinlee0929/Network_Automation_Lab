# Day59 - Intent Policy Matrix / Reviewer Safety Explanation

## Purpose

Day59 turns the Day57 and Day58 intent mapping safety model into a reviewer-facing policy matrix. The goal is to make it easy for an external reviewer to see which natural-language intents are allowed, blocked, or clarification-required before any future assistant layer can act.

Day59 is documentation-only and report-only. It does not call OpenAI APIs, implement voice control, execute mapped tasks, use SSH, connect to devices, read or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.

## Reviewer Explanation

- The system separates understanding intent from executing a task.
- Intent mapping is not permission to run the mapped task.
- Safety review must happen before execution.
- Report-only and documentation-only tasks may be allowed because they only read or write local evidence.
- Live-capable tasks require explicit human confirmation in future design and are blocked by default now.
- Voice input, OpenAI API calls, SSH, live device access, and device control are intentionally out of scope.

## Policy Matrix

| Intent category | Example user phrase | Mapped task type | Safety classification | Default decision | Requires confirmation? | Allowed to execute automatically? | Reviewer explanation | Evidence / report output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Open dashboard / latest reports | Open the dashboard and show the latest reports | local UI / report-only | `report_only` | allowed | no | yes | Local dashboard/report views read existing artifacts only. | Dashboard `/reports`, `reports/report_index.html` |
| Show task catalog | Show me the available runner tasks | local metadata / report-only | `report_only` | allowed | no | yes | Task catalog listing prints committed runner metadata only. | `python network_lab.py --list-tasks` |
| Generate report index | Generate the report index | report-only | `report_only` | allowed | no | yes | Report index scans local report metadata and writes summary JSON/HTML. | `reports/report_index.json`, `reports/report_index.html` |
| Dry-run intent mapping | Map this request to a runner task, but dry-run only | dry-run proposal | `dry_run` | allowed dry-run only | no | yes for the dry-run task only | Day57 may classify intent, but the proposed task is never executed. | Day57 CLI JSON output |
| Read-only safety review | Review whether this intent is safe | report-only safety explanation | `report_only` | allowed | no | yes | Day58 writes a local safety decision report and does not delegate to mapped tasks. | `reports/portfolio/day58_intent_mapping_safety_review.json` |
| VRRP failover request | Do the VRRP failover test | live-capable network test | `blocked_live_capable` | blocked by default | yes | no | VRRP failover can affect network availability and must not run from intent alone. | Day58 blocked policy match |
| WireGuard live validation request | Run the WireGuard validation | guarded-live capable validation | `blocked_live_capable` | blocked by default | yes | no | WireGuard validation may touch live VPN state or test endpoints. | Day57/Day58 dry-run safety output |
| SSH command request | SSH to the router and run this command | direct device access | `blocked_live_capable` | blocked by default | yes | no | SSH and RouterOS command execution are outside Day59 scope. | Day58 blocked policy match |
| Router / switch configuration change request | Apply this router configuration change | device-changing action | `blocked_live_capable` | blocked by default | yes | no | Router, switch, firewall, VPN, NAT, IP, VRRP, WireGuard, interface, and route changes are blocked. | Day58 blocked live-capable action policy |
| Unknown or ambiguous request | Make everything better | no safe task mapped | `unknown_blocked` | blocked or requires clarification | yes | no | Ambiguous requests must stop for human clarification and must not execute any task. | Day57 unknown / Day58 unknown blocked output |

## Report-only Runner Task

Day59 adds an optional local report generator:

```powershell
python network_lab.py --task intent-policy-matrix
```

It writes:

```text
reports/portfolio/day59_intent_policy_matrix.json
reports/portfolio/day59_intent_policy_matrix.html
```

The task only writes local report files. It does not execute mapped tasks, call OpenAI APIs, use voice, open SSH, connect to devices, or read `config.json`.

## Safety Boundary

Blocked by default:

- VRRP failover execution.
- WireGuard live validation from intent alone.
- SSH or RouterOS command execution.
- Router, switch, firewall, VPN, NAT, IP, VRRP, WireGuard, interface, route, or device configuration changes.
- Unknown or ambiguous requests.

Allowed:

- Documentation-only and report-only explanation tasks.
- Local task catalog display.
- Local report index generation.
- Dry-run intent mapping when the mapped task is not executed.
- Safety review reports that explain an allowed or blocked decision.

## Validation

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-policy-matrix
```
