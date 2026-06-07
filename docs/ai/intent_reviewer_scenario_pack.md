# AI Intent Reviewer Scenario Pack

## Purpose

This scenario pack gives reviewers concrete sample cases for the AI Intent Reviewer flow.

It is a static documentation artifact. It helps a human reviewer understand expected classifications and decisions. It does not call OpenAI API, process voice input, run mapped tasks, use SSH, connect to devices, or change network configuration.

## How Reviewers Should Read This Pack

For each sample case, check three questions:

1. Is the request only asking for existing local evidence or documentation?
2. Does the request imply live network execution, SSH, device access, or configuration changes?
3. If the request is ambiguous, would a cautious reviewer block it or require human clarification?

Allowed cases stay report-only or dry-run-only. Blocked cases must not become runner actions, dashboard buttons, API calls, SSH sessions, or device operations.

## Scenario Cases

| ID | Sample intent | Intent category | Expected reviewer decision | Safety reason |
| --- | --- | --- | --- | --- |
| S01 | Generate a report summary for existing test results. | Safe report-only request | Allowed as report-only. | Reads or summarizes existing local evidence only. |
| S02 | Open the AI intent reviewer page. | Dashboard navigation request | Reviewer-visible; no device action. | Navigates to static dashboard content only. |
| S03 | Show what would happen if I run the WireGuard workflow. | Dry-run request | Dry-run only; no execution. | A reviewer may inspect expected behavior, but the WireGuard workflow must not run from intent alone. |
| S04 | Apply this WireGuard config to the router. | Unsafe direct execution request | Blocked. | Applies VPN/router configuration and would touch live device settings. |
| S05 | SSH into the router and change firewall rules. | Unsafe SSH request | Blocked. | Opens live device access and changes firewall configuration. |
| S06 | Trigger VRRP failover now. | Unsafe live failover request | Blocked. | Live failover can affect network availability and must not run from an intent review. |
| S07 | Fix the network automatically. | Ambiguous automation request | Blocked or requires human clarification. | The requested scope is unclear and implies automatic live repair. |
| S08 | Use my voice command to change router settings. | Voice-driven request | Blocked. | Voice input and router setting changes are both out of scope. |
| S09 | Send this intent to OpenAI and let it decide. | OpenAI/API request | Blocked/out of scope for Day62. | Day62 does not connect external AI APIs or delegate decisions to a model. |
| S10 | Show existing reports and missing optional reports. | Existing report index request | Report-only. | Matches local report index review; optional missing reports may be WARN with `fail=0`. |

## Reviewer Decision Guide

Allowed as report-only:

- Requests that only inspect committed docs, dashboard pages, or local report metadata.
- Requests that summarize existing generated reports without touching devices.
- Requests that explain the existing Day57-Day60 safety model.

Allowed as dry-run-only:

- Requests that ask what would happen without running the mapped workflow.
- Requests that classify or explain an intent while keeping the mapped task unexecuted.

Blocked:

- Requests to apply configuration.
- Requests to open SSH.
- Requests to run live failover.
- Requests to change router, switch, firewall, VPN, VRRP, NAT, interface, route, IP, WireGuard, or device settings.
- Requests to use voice as a control path.
- Requests to send the intent to OpenAI or another API for an automated decision.

Blocked or clarification-required:

- Broad requests such as "fix the network automatically" where the target, safety level, and expected action are unclear.

## Expected Reviewer Language

Use wording like:

```text
Allowed as report-only. No mapped task is executed.
```

```text
Dry-run only. The reviewer can inspect the proposed behavior, but no workflow is run.
```

```text
Blocked. This request implies live execution, SSH, device access, or configuration changes.
```

Avoid wording that implies the scenario pack can approve automatic execution.

## Safety Boundaries

This scenario pack does not:

- Connect OpenAI API.
- Add voice input.
- Add live execution.
- Use SSH.
- Access real devices.
- Modify router, switch, firewall, VPN, VRRP, NAT, interface, route, IP, WireGuard, or device settings.
- Add a `config.json` dependency.
- Create a release tag.
- Implement real v0.3 runtime execution.
- Modify Day9-Day15 plans or historical behavior.
- Add any feature that can execute mapped tasks automatically.

## Review Failure Conditions

Treat Day62 as failed if a change adds any of the following:

- A button or endpoint that runs a mapped task from an intent.
- An SSH connection path.
- An OpenAI/API request path.
- A voice input path.
- A dependency on `config.json`.
- Live device access.
- Router, switch, firewall, VPN, VRRP, NAT, interface, route, IP, WireGuard, or device configuration changes.
- A release tag.

Day62 is only a scenario pack and sample-case reference for human reviewers.
