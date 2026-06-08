# Day69 - Offline Mock Runtime Reviewer Dashboard Evidence Drilldown

Day69 improves the static `/ai-intent-reviewer` dashboard so a reviewer can follow the Day66-Day68 offline mock runtime evidence without switching between source files first.

The work is dashboard-only and documentation-only. It does not start an AI runtime, call OpenAI APIs, add voice integration, use SSH, access devices, run live tests, execute mapped tasks, add forms, add POST routes, add command surfaces, depend on `config.json`, or change router, switch, firewall, VPN, VRRP, interface, route, IP, NAT, or WireGuard configuration.

## Purpose

Day66 introduced deterministic offline mock runtime records.

Day67 validated those records against a fixed contract and safety invariants.

Day68 checked whether the records and reports are readable enough for a human reviewer to trust.

Day69 makes that chain visible directly on `/ai-intent-reviewer` by adding:

- A Day69 Reviewer Evidence Drilldown section.
- A Day66 -> Day67 -> Day68 -> Day69 evidence chain.
- Scenario-level evidence cards for every deterministic offline mock scenario.
- Visible Day67 contract status.
- Visible Day68 reviewer quality status.
- Static links to related documentation and expected generated report paths.

## Reviewer Workflow

1. Open `/ai-intent-reviewer`.
2. Read the Day69 Reviewer Evidence Drilldown section.
3. Confirm the chain shows Day66 Offline Mock Runtime, Day67 Contract Validation / Safety Invariants, Day68 Reviewer Report Quality, and Day69 Dashboard Evidence Drilldown.
4. Inspect each scenario evidence card.
5. Confirm the scenario decision, safety category, evidence source, contract status, review quality status, safety note, and related report paths are visible.
6. Confirm the page remains static/read-only/report-only with no form, POST route, command control, or live execution behavior.

## Evidence Chain

| Day | Evidence | Reviewer Question |
| --- | --- | --- |
| Day66 | Deterministic offline mock runtime records | What would the future runtime record shape look like without executing anything? |
| Day67 | Contract validation and safety invariant checks | Do the fixed mock records preserve required fields and no-live behavior? |
| Day68 | Reviewer report quality checks | Can a human reviewer trace each scenario decision to visible evidence? |
| Day69 | Dashboard evidence drilldown | Can the reviewer inspect the chain and scenario evidence from `/ai-intent-reviewer`? |

## Scenario Drilldown

The dashboard renders one read-only card for each scenario returned by the deterministic Day66 helper:

- `documentation_only`
- `report_only`
- `blocked_live_action`
- `needs_manual_review`
- Any additional committed scenario returned by the existing mock runtime helper

Each card shows:

- Scenario name and ID.
- Safety category.
- Expected decision/status.
- Evidence source.
- Day67 contract status.
- Day68 review quality status.
- Safety note.
- Static report/document paths.

## Contract Status

The contract status comes from the existing Day68 report data, which reuses the Day67 in-memory validator. A `PASS` status means the scenario satisfies the Day67 offline mock runtime contract and safety invariants.

Day69 does not add a new validator or a new runner task. It only displays the existing deterministic validation result on the reviewer dashboard.

## Review Quality Status

The review quality status comes from the existing Day68 reviewer quality report helper. `REVIEW_READY` means the scenario has visible intent, decision, safety classification, evidence references, contract validation proof, and no-execution evidence.

Day69 does not change Day68 quality logic. It only exposes the result in a reviewer-friendly dashboard drilldown.

## Safety Boundaries

Day69 confirms:

- Static/read-only/report-only dashboard changes only.
- No AI runtime start.
- No OpenAI API call.
- No voice integration.
- No SSH.
- No device access.
- No live execution.
- No mapped task execution.
- No arbitrary command execution.
- No `config.json` dependency.
- No dashboard form.
- No POST route.
- No command surface.
- No network or device configuration change.
- No release tag.

## Validation Commands

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-workflow-demo
python network_lab.py --task offline-mock-runtime
python network_lab.py --task offline-mock-runtime-contract
python network_lab.py --task offline-mock-runtime-review
git status --short --branch
```

Expected results:

- `python -m pytest` passes.
- `report-index` may warn about optional missing local reports, but `fail=0` is required.
- `intent-workflow-demo` remains report-only and does not execute mapped tasks.
- `offline-mock-runtime` remains offline/mock only.
- `offline-mock-runtime-contract` validates deterministic mock scenarios.
- `offline-mock-runtime-review` remains reviewer/report-only.
- Git status is clean after the Day69 commit.
