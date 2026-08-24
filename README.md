# Network Automation Lab

## Project Summary

Network Automation Lab is a safety-first network automation and testing portfolio
project. It demonstrates how network validation can be planned, reviewed, tested,
and presented as structured evidence without granting live automation authority
by default.

The August 2026 release baseline is a local Stage-0 product:

- Python validation and reporting utilities;
- a canonical Flask reviewer dashboard;
- a secondary Next.js evidence interface;
- deterministic dry-run, mock, and report-oriented workflows;
- structured JSON, HTML, and text evidence;
- explicit safety gates for anything that could reach a device or external
  provider.

The supported release path is designed for local portfolio review. It does not
require a router, switch, VPN peer, SSH session, cloud provider, model API, or
private lab configuration.

![AI-assisted workflow overview](docs/assets/readme-ai-assisted-workflow.png)

The diagram summarizes the intended human-guided flow: local inputs and existing
evidence are reviewed through bounded tools and display surfaces, while later
execution capabilities remain gated.

## What This Project Demonstrates

Network validation is often proved through one-off terminal sessions,
screenshots, and manually copied output. That approach is difficult to repeat,
compare, test, or review. This project instead treats network validation like a
small QA platform.

It demonstrates:

- repeatable validation logic for MikroTik, Cisco, WireGuard, VRRP, and iperf3
  scenarios;
- clear separation between report-only, dry-run, mock, historical, and
  separately gated capabilities;
- machine-readable evidence with reviewer-friendly summaries;
- fail-closed handling of missing, malformed, unavailable, or blocked evidence;
- local dashboards that expose status and evidence without turning the public
  review flow into a device console;
- automated regression coverage for parsers, safety boundaries, report
  projection, CLI behavior, and presentation;
- documentation and evidence trails that explain both supported behavior and
  deliberate limitations.

Historical Day and Phase records remain under [docs/](docs/). They are retained
as engineering evidence, not reproduced as a chronological diary in this
release README.

## Architecture Overview

The current reviewer-facing architecture has four layers.

### Validation and report layer

Python modules implement deterministic validation, parsing, report generation,
and task metadata. The unified entry point is:

```text
network_lab.py
```

The task catalog distinguishes safety and execution modes. A task name or
catalog entry is descriptive metadata; it is not automatic authorization to run
a live workflow.

### Evidence layer

Supported workflows produce or inspect structured artifacts under paths such as:

```text
reports/
summary/
docs/portfolio_evidence/
```

Generated runtime reports are generally local and may be absent from a clean
checkout. Committed summaries, documentation, tests, and screenshots provide a
review path when runtime evidence is unavailable.

### Reviewer interfaces

The canonical reviewer entry point is the Flask dashboard:

```text
dashboard_app.py
http://127.0.0.1:5000/
```

Its current public review surfaces include:

| Route | Current purpose |
| --- | --- |
| `/` | Project positioning, Stage-0 status, evidence health, and review links |
| `/reports` | Evidence summaries, status filters, safe JSON previews, and bounded artifact links |
| `/commands` | Display-only registry and historical execution-record review; no Run or POST control is rendered |
| `/ai-checklist` | Static AI and safety review checklist |
| `/ai-intent-reviewer` | Static intent, mock-runtime, readiness-gate, and safety evidence |

The Next.js Network Automation AI Node is a secondary Stage-0 interface. Its
supported default presentation provides bounded committed or local evidence;
it does not replace the Flask Quick Start
and does not activate provider, model, job, or device execution.

### Governance and safety layer

Repository rules are defined in [AGENTS.md](AGENTS.md). The staged automation
boundary is described in the
[Actual Automation Integration Plan](docs/automation_readiness/actual_automation_integration_plan.md).

The repository contains a version-2 workflow governance contract and hardened
helper foundation. That contract is declarative and remains inactive until a
separate reviewed activation decision.

### Repository map

```text
.
├── adapters/                 # adapter boundaries and non-live scaffolding
├── app/                      # secondary Next.js application routes
├── components/               # secondary UI components
├── config/                   # configuration and inert workflow contracts
├── docs/                     # architecture, safety, history, runbooks, evidence
├── scripts/                  # bounded repository and validation helpers
├── summary/                  # committed safe summary artifacts
├── templates/                # canonical Flask dashboard templates
├── tests/                    # Python regression and safety coverage
├── dashboard_app.py          # canonical local reviewer dashboard
├── network_lab.py            # unified task and report entry point
├── requirements.txt          # Python requirements
└── package.json              # secondary Next.js application metadata
```

## Interview / Demo Quick Path

Network Automation Lab is a safety-first network-validation and automation QA
platform for Network Engineers and Automation Reviewers. The shortest current
walkthrough uses the canonical Flask dashboard:

```bash
python dashboard_app.py
```

Open `http://127.0.0.1:5000/` and select **Open the 3-minute Stage-0 journey**.
The journey uses committed Day95 evidence to compare one allowed read-only
fake-adapter request with one write-capable request rejected before adapter
invocation. It connects the request, safety decision, deterministic evidence,
and reviewer conclusion without requiring repository-history context.

This accepted Stage-0 demo path is GET-only. It does not invoke provider-backed
operations, expose local command or job execution controls, contact devices by
SSH, NETCONF, or RESTCONF, change configuration, or demonstrate production
approval and orchestration. Other internal or legacy surfaces in the repository
are outside this interview path.

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Robinlee0929/Network_Automation_Lab.git
cd Network_Automation_Lab
```

Read [AGENTS.md](AGENTS.md) before running project commands. It defines the
current safety boundary and validation expectations.

### 2. Create a Python environment

The repository does not declare one universal Python version. Use a supported
local Python environment and create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the committed requirements:

```bash
python -m pip install -r requirements.txt
```

The Flask dashboard requires Flask 3.x as constrained by
[requirements.txt](requirements.txt).

### 3. Start the canonical dashboard

```bash
python dashboard_app.py
```

Open:

```text
http://127.0.0.1:5000/
```

Start with the landing page, then open `/reports`. Use `/commands`,
`/ai-checklist`, and `/ai-intent-reviewer` only as their current Stage-0
display/reviewer surfaces. The visible `/commands` page does not render a Run or
POST control.

Stop the Flask server with `Ctrl+C`.

### 4. Run local validation

```bash
python -m pytest
python network_lab.py --task report-index
```

`pytest` exercises the repository regression and safety contracts.
`report-index` scans local report metadata and evidence paths; it does not
connect to devices. It may return `WARN` when optional generated reports are
missing, provided there are no failures and the missing items are documented as
optional.

### Optional secondary interface

The Next.js application is a secondary evidence surface. It requires a usable
Node/npm environment and the committed package metadata, but it is not required
for the canonical Flask review flow. Node/NVM coexistence setup is outside the
August release path. See the
[canonical Quick Start and demo runbook](docs/phase_2n/phase_2n_01_canonical_quick_start_and_demo_runbook_documentation_only.md)
for the recorded primary/secondary boundary.

An **Optional Local AI Recommendation Preview** is available only on the
secondary `/network/ai-actions` page when
`NETWORK_AI_PROVIDER_DEMO_ENABLED=1` is set in `.env.local`. It also requires
`OPENAI_API_KEY`, which is used only by the server-side provider client. The
default remains `NETWORK_AI_PROVIDER_DEMO_ENABLED=0`, so the canonical Flask
Stage-0 demo stays provider-free. The preview classifies a request against the
fixed Action Catalog and stops at a sanitized recommendation; it does not create
jobs, generate commands, contact devices, or execute network operations.

Legacy/general provider workbenches at `/ai`, `/automation/ai-nodes`, and the
historical `/api/network/ai/analyze-report` route remain outside the canonical
provider-free Stage-0 reviewer path. They fail closed by default through
`LEGACY_AI_PROVIDER_ENABLED=0` and require the separate exact local opt-in
`LEGACY_AI_PROVIDER_ENABLED=1` plus a server-side `OPENAI_API_KEY`. Enabling
them sends submitted text to the configured external provider, so do not use
secrets, credentials, private device data, or private lab data. Provider
credential presence is not feature authorization, and neither flag grants
device, job, command, or configuration-execution capability.

## Get Involved

Contributions to the current Stage-0 baseline are welcome. Start with the
[contributor guide](CONTRIBUTING.md), review the [security policy](SECURITY.md),
and browse the [general Issues list](https://github.com/Robinlee0929/Network_Automation_Lab/issues)
or [currently open issues labeled `good first issue`](https://github.com/Robinlee0929/Network_Automation_Lab/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22).
Newcomer-friendly work may include UI and accessibility improvements, parser
tests, deterministic parser fixes, and fail-closed evidence handling.

The normal contribution flow is:

1. Choose an Issue or propose a bounded improvement.
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
3. Create a focused branch in your fork or local clone.
4. Implement one narrow, reviewable change.
5. Run targeted validation plus the repository-required checks.
6. Open a pull request without assuming repository write access.
7. Let Safe CI validate the pull request.
8. Address maintainer review; the maintainer performs the merge.

`main` is protected, so normal changes go through a pull request and Safe CI.
For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md). Do not post
exploit details, credentials, secrets, or private infrastructure data in a
public Issue; the public security-contact path is only for requesting a private
reporting channel.

## Public Roadmap

Stage 0 is the current public baseline and is in final open-source/security
closure. It now includes contributor and security guidance, Issue and pull
request templates, newcomer-friendly Issues, and protected-`main` governance
through pull requests and Safe CI.

| Stage | Purpose | Status |
| --- | --- | --- |
| **Stage 0 — Current public baseline** | Mock-only, dry-run, report-only, reviewer-visible, fail-closed validation and evidence | **Current / closure in progress** |
| **Stage 1 — Read-only Lab Integration Planning** | Define contracts, allowlists, failure behavior, evidence, and the credential boundary without live access | **Future / requires separate approval** |
| **Stage 2 — Narrow Read-only Lab Adapter** | Gate one lab target, one transport, a small read-only allowlist, normalized real output, and no-mutation evidence | **Future / separately gated** |
| **Stage 3 — Controlled Config Plan Generation** | Produce human-reviewable configuration plans only; no apply | **Future / separate gate** |
| **Stage 4 — Controlled Change Execution** | Permit narrowly approved lab changes with explicit safeguards and evidence | **Future / separate gate** |
| **Stage 5 — Production-like Platform** | Add mature access control, audit, rollback, monitoring, and human approval | **Long-term / not currently authorized** |

Stage 2 exit is the planned major-development pause point. A roadmap item,
Issue, pull request, merge, date, or milestone does **not** activate a
capability. Every Stage advancement requires separate explicit authorization
and validation. Live-device access, SSH, NETCONF, RESTCONF, configuration
changes, production execution, secrets handling, provider/model integration,
and autonomous execution therefore remain unauthorized by this roadmap.

## Core Capabilities

### Evidence discovery and presentation

- Index local JSON, HTML, text, image, and documentation evidence.
- Show explicit `PASS`, `FAIL`, `WARN`, `MISSING`, `UNKNOWN`, `UNAVAILABLE`,
  `ERROR`, and `BLOCKED` states where applicable.
- Keep evidence availability separate from validation quality.
- Render bounded summaries rather than arbitrary raw object projection.
- Constrain report links and previews to expected local evidence locations.

### Network-validation portfolio coverage

The repository contains code and retained evidence for:

- MikroTik baseline and setup validation;
- Cisco topology validation;
- iperf3 performance and regression reporting;
- WireGuard planning, validation, and evidence;
- HA/VRRP topology, dry-run planning, and retained validation evidence;
- unified task metadata, report indexing, and portfolio demo flows.

Some historical workflows describe read-only or guarded-live lab operations.
They are not part of the default August reviewer path and do not grant present
operational authority.

![MikroTik and Cisco lab topology](docs/assets/mikrotik-cisco-lab-topology-v0.2-final.png)

### Reviewer-oriented AI evidence

The AI-related surfaces demonstrate deterministic intent classification,
mock-runtime decisions, dry-run plans, reviewer approval envelopes, audit
records, safety gates, and fixed-template summaries. They remain evidence and
review aids:

- no model invocation is required for the supported review flow;
- no mapped task is automatically executed;
- no provider or secret is activated;
- no direct device command is generated or run.

### Quality and safety coverage

- Python unit and regression tests;
- TypeScript component tests for the secondary interface;
- type checking, lint, and production-build checks in the broader validation
  lanes;
- negative tests for rejected and unavailable states;
- report-index visibility and status handling;
- narrow-screen and accessibility presentation coverage;
- explicit no-execution and no-live-device evidence.

## Typical User / Reviewer Flow

1. Read this README and [AGENTS.md](AGENTS.md).
2. Create the Python environment and start `python dashboard_app.py`.
3. Open the landing page to understand the project, Stage-0 baseline, and
   evidence health.
4. Use `/reports` to inspect available summaries, status filters, safe previews,
   and missing-evidence states.
5. Review `/commands`, `/ai-checklist`, and `/ai-intent-reviewer` as display-only
   or static reviewer evidence.
6. Run `python -m pytest` and
   `python network_lab.py --task report-index` when local validation is desired.
7. Inspect relevant `reports/`, `summary/`, or linked documentation artifacts.
8. Stop the local dashboard with `Ctrl+C`.

For a shorter portfolio walkthrough, follow the
[Public Reviewer Walkthrough](docs/portfolio/public_reviewer_walkthrough.md).
If Flask is unavailable, use the current-suitable home, reports, and AI
checklist screenshots under:

```text
docs/demo/day52_offline_demo_package/screenshots/
```

The retained `dashboard_commands.png` is historical, superseded evidence of the
pre-display-only command UI. Do not use it as evidence of the current
`/commands` surface.

## Safety Boundaries

The August release remains **Stage 0**. Its supported reviewer path is local,
report-oriented, dry-run/mock-only, and display-only.

### Currently supported safe paths

- Read committed source, tests, documentation, summaries, and screenshots.
- Start the local Flask reviewer dashboard.
- Browse the dashboard GET-oriented review surfaces.
- Inspect bounded local report metadata and safe previews.
- Run deterministic unit/regression tests.
- Run the report-only `report-index` task.
- Review dry-run, mock, and historical evidence without contacting a device.

### Deferred or gated capabilities

The release grants no automatic authority for:

- live-device access;
- SSH, NETCONF, RESTCONF, or equivalent device protocols;
- configuration backup, apply, change, reset, reboot, enable, or disable;
- provider, external API, or model calls;
- credentials or secrets handling;
- arbitrary command execution;
- queue, scheduler, worker, broker, or autonomous agent loops;
- production execution paths.

Any later read-only or live integration requires a separate Stage gate, a
bounded implementation and validation plan, and task-specific user approval.
An MIT software license permits code use under its terms; it does not override
these operational safety boundaries.

## Validation / Quality Gates

The standard repository validation commands are:

```bash
python -m pytest
python network_lab.py --task report-index
```

Additional TypeScript checks used by broader product or release lanes are:

```bash
npm run test:unit
npm run typecheck
npm run lint
npm run build
```

These Node checks apply to the secondary interface and are not required merely
to open the canonical Flask review path.

### Interpreting report status

| Status | Meaning |
| --- | --- |
| `PASS` | Required evidence exists and the checked condition passed |
| `FAIL` | A required condition failed or required evidence is invalid |
| `WARN` | A non-blocking issue or documented optional-evidence gap exists |
| `MISSING` | An expected local generated artifact is absent |
| `UNKNOWN` | Evidence exists but exposes no supported status field |
| `UNAVAILABLE` | The source or bounded projection cannot currently be used |
| `ERROR` | Evidence could not be processed safely |
| `BLOCKED` | A safety or authorization boundary prevented the action |

Generated `reports/` content is generally local and ignored by Git. A clean
checkout may therefore show missing optional reports. Treat a `report-index`
warning as acceptable only when `fail=0` and every missing item is optional and
explained.

Release-wide regression, CI diagnosis, and final acceptance are separate August
release lanes; they are not performed by documentation-only changes.

## Current Release Status

| Area | August 2026 status |
| --- | --- |
| Stage-0 Network Automation Lab | Current release baseline |
| Canonical reviewer interface | Flask dashboard on `127.0.0.1:5000` |
| Secondary Next.js interface | Available as a bounded Stage-0 evidence surface |
| WF-01 workflow foundation | Contract and hardened helpers integrated on `main` |
| Workflow Version 2 | **INACTIVE** |
| WF-01-03B | **DEFERRED_SECURITY_RESEARCH_BLOCKED** |
| WF-01-03B unfinished research candidate | **NOT INCLUDED IN RELEASE** |
| WF-01-03B effect on August closure | Does not block the Stage-0 August release |
| WF-01-03C through WF-01-03F | Deferred future work / post-release |
| New project-status infrastructure | Not required; this section is the repository-facing release summary |

`DEFERRED_SECURITY_RESEARCH_BLOCKED` is not a Security PASS, completion,
activation, or integration claim. Detailed experimental research evidence is
retained separately and is intentionally excluded from the public release.

## Known Limitations / Future Work

### Current release baseline

The v0.3 release and its bounded post-release maintenance cycle are complete.
The current public portfolio path remains the local Stage-0 reviewer experience;
future capabilities stay behind their separate authorization and safety gates.

### Post-release or deferred

- Continue WF-01-03B security research only after explicit reauthorization.
- Revisit C017/AppContainer research if it remains relevant.
- Plan WF-01-03C through WF-01-03F as separate future work.
- Review and activate workflow v2 only through its later migration, pilot, and
  acceptance gates.
- Address Node/NVM coexistence only if a later environment-maintenance task
  requires it.
- Introduce read-only or live-device automation only through later Stage gates.

Current limitations also include variable local report availability, no
guarantee that every clean checkout contains generated evidence, and a
deliberately non-executing public review path.

## Documentation Index

### Start here

- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Repository rules and task safety](AGENTS.md)
- [Public Reviewer Walkthrough](docs/portfolio/public_reviewer_walkthrough.md)
- [Canonical Quick Start and demo runbook](docs/phase_2n/phase_2n_01_canonical_quick_start_and_demo_runbook_documentation_only.md)
- [Accepted Stage-0 user-facing baseline](docs/phase_2n/phase_2n_05_final_user_facing_acceptance_review_phase_closure_review_only.md)

### Architecture and safety

- [AI-assisted human-guided network testing architecture](docs/concepts/ai_assisted_human_guided_network_testing_architecture.md)
- [Actual automation integration plan and Stage model](docs/automation_readiness/actual_automation_integration_plan.md)
- [Workflow governance foundation planning record](docs/workflow_governance/wf_01_00b_workflow_governance_foundation_reconciliation_planning_only.md)

### Evidence and usage

- [Portfolio Evidence Guide](docs/portfolio_evidence.md)
- [Offline demo kit](docs/demo/offline_interview_demo_kit/README.md)
- [Portfolio demo script](docs/portfolio_demo_script.md)
- [Traditional Chinese portfolio demo script](docs/portfolio_demo_script_zh-TW.md)
- [v0.2 demo handoff guide](docs/portfolio/v0.2_demo_handoff_guide.md)

### Historical engineering records

- [Roadmap and Day records](docs/roadmap/)
- [Phase 2A–2O records](docs/)
- [Release records](docs/releases/)
- [Portfolio evidence history](docs/portfolio_evidence/)

Historical records describe the state and authorization boundary at the time
they were written. Use the concise Current Release Status above for the August
2026 repository-facing status.

This project is distributed under the [MIT License](LICENSE).
