# Day58 - Intent Mapping Safety Review / Confirmation Gate Design

## Purpose

Day58 adds a conservative safety review layer for the Day57 intent mapping prototype. It classifies mapped intent proposals, documents a confirmation gate model, blocks live-capable actions by default, and writes local dry-run reports.

Day58 is report-only. It does not call OpenAI APIs, implement voice control, execute mapped tasks, use SSH, connect to devices, read or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.

## What Day57 Provided

Day57 introduced a deterministic dry-run-only intent mapping prototype. Static user text is normalized, classified into a reviewed intent, and mapped to an allowlisted runner task proposal when possible. The Day57 prototype prints mapping metadata only and sets `mapped_task_executed` to `false`.

## Why Day58 Is Needed

Intent mapping creates a useful bridge between natural language and runner tasks, but mapped tasks can imply different safety levels. Day58 adds a confirmation gate review so report-only, read-only, dry-run, live-capable, blocked, and unknown intents are separated before any future assistant layer is allowed to act.

## Safety Policy Review

Supported Day58 classifications:

- `report_only`: local report or dashboard review. Allowed without confirmation.
- `read_only`: state inspection request. May require an explicit flag or human review depending on live access risk.
- `dry_run`: preview or plan-only request that must not touch devices.
- `live_capable_requires_confirmation`: mapped task could become live-capable in a future workflow and must not execute directly.
- `blocked_live_capable`: action can change network/device state or disrupt availability and is blocked by default.
- `unknown_blocked`: unclear or ambiguous request and therefore blocked.

## Confirmation Gate Design

- Report-only tasks may run without confirmation.
- Read-only tasks may require an explicit flag or review depending on risk.
- Dry-run tasks may run only if they do not touch devices.
- Live-capable tasks must never execute directly from intent mapping.
- Any task capable of changing device/network state must be blocked by default.
- Future live-capable execution must require explicit user confirmation, visible task preview, safety classification, blocked action check, a non-default live flag, and a human-readable warning.
- Unknown intent must be blocked.

## Blocked Live-capable Action Policy

Blocked by default:

- VRRP failover execution
- interface disable/enable
- firewall rule add/remove/change
- NAT change
- IP address change
- route change
- WireGuard peer add/remove/recreate
- router reboot/reset
- SSH command execution
- arbitrary shell command execution
- direct device configuration apply

## Dry-run Report Behavior

The Day58 task is:

```powershell
python network_lab.py --task intent-safety-review --intent-text "show latest reports"
```

It writes local generated reports under ignored `reports/` paths:

```text
reports/portfolio/day58_intent_mapping_safety_review.json
reports/portfolio/day58_intent_mapping_safety_review.html
```

The report includes the Day number, task name, intent text, detected mapping, safety classification, confirmation gate requirement, blocked decision, rationale, safety boundaries, final status `PASS`, and an explicit statement that no live execution occurred.

## Examples

| User request | Classification | Decision |
| --- | --- | --- |
| show latest reports | `report_only` | allowed |
| run report index | `report_only` | allowed |
| do VRRP failover test | `blocked_live_capable` | blocked by default |
| change firewall rule | `blocked_live_capable` | blocked |
| unknown command | `unknown_blocked` | blocked |

## Non-goals

- No OpenAI API.
- No voice control.
- No live execution.
- No SSH.
- No device configuration changes.
