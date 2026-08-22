# Contributing to Network Automation Lab

Thank you for contributing. This guide describes the supported, safety-first
path for making a focused change, validating it locally, and preparing it for
review without requiring physical network devices or private infrastructure.

## Project contribution model

Network Automation Lab is currently a Stage-0 network automation and testing
platform. Its supported contribution path is local, mock-only, dry-run,
report-only, and reviewer-visible. The project demonstrates deterministic
validation and evidence workflows without granting live automation authority by
default.

Normal Stage-0 contributions do not require Cisco or MikroTik hardware, SSH
access, private lab configuration, a provider account, or a model API. The
canonical reviewer interface is the local Flask dashboard; the Next.js
application is a secondary evidence interface.

## Good contribution areas

Useful Stage-0 contributions include:

- documentation and reviewer guidance;
- deterministic parser and network-validation fixtures;
- malformed, missing, unavailable, and blocked evidence fixtures;
- negative safety tests and fail-closed regression coverage;
- structured report and reviewer-evidence improvements;
- reviewer UI, usability, and accessibility improvements;
- Cisco, MikroTik, WireGuard, VRRP, and iperf3 validation fixtures;
- bounded, non-live adapter scaffolding;
- more reliable, hermetic tests and validation tooling.

Live execution is not part of the normal contribution path.

## Before you start

Read the [project overview](README.md) and [repository rules](AGENTS.md) before
changing files or running project commands. They define the current interfaces,
validation requirements, repository discipline, and safety boundary.

If your proposal concerns future read-only or live automation, also read the
[Actual Automation Integration Plan](docs/automation_readiness/actual_automation_integration_plan.md).
That plan defines future capability gates; reading it does not authorize live
automation or advance the project beyond Stage 0.

## Safety boundary

Stage-0 work must preserve the mock-only, dry-run, report-only, and
reviewer-visible default. Without a separate, explicit capability gate and
task-specific approval, do not add live device access, SSH, NETCONF, RESTCONF,
configuration changes, production execution, secrets or credentials, queues,
schedulers, workers, autonomous AI execution, or unapproved provider/model
capabilities.

Rejected and unapproved paths must fail closed. They must not reach adapters,
brokers, runners, device access, or other execution paths. Preserve the
reviewer evidence and negative tests that prove this boundary.

## Local setup

The repository does not declare one universal Python version. Use a supported
local Python installation and create an isolated environment:

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

Install the committed Python requirements:

```bash
python -m pip install -r requirements.txt
```

Node.js and npm are needed only when changing the secondary Next.js interface
or running its validation lane. Safe CI currently uses Node.js 22. The
canonical Flask reviewer path does not require Node.js.

For local environment placeholders, copy values from [.env.example](.env.example)
into an ignored local environment file and keep real secrets out of the
repository. The normal Stage-0 review path remains provider-free.

## Running validation

The baseline Python validation lane is:

```bash
python -m pytest
python network_lab.py --task report-index
```

`report-index` is local and report-only; it does not contact devices. A `WARN`
is acceptable only when `fail=0` and the missing artifacts are documented as
optional. Required evidence failures are not acceptable.

For relevant Next.js changes, run:

```bash
npm ci
npm run typecheck
npm run lint
npm run test:unit
npm run build
```

Safe CI disables Next.js telemetry during its production build. When reproducing
that build locally, set `NEXT_TELEMETRY_DISABLED=1` using the syntax appropriate
for your shell.

Validation should be proportional to the change, but repository policy and Safe
CI may require broader checks before integration. Behavior and safety changes
need corresponding tests, including negative coverage where applicable.

## Branch and scope discipline

- Start from the current `main` branch and create one focused task branch.
- Keep changes small, reviewable, and limited to the approved scope.
- Avoid opportunistic refactors or unrelated cleanup.
- Add or update tests for behavior changes.
- Preserve structured evidence and reviewer-visible safety decisions.
- Recheck the final diff so only intended files remain.

## Pull requests

A useful pull request description should include:

- a concise summary and exact scope;
- the validation commands run and their results;
- the safety impact of the change;
- whether provider, device, live, or execution behavior changed;
- screenshots when they help reviewers evaluate UI changes.

Do not present a proposed capability, issue, milestone, or merged change as
automatic authorization for a new Stage.

## Secrets and local artifacts

Never commit credentials, API keys, tokens, private device configuration,
private lab data, personal filesystem paths, private memory, local secrets, or
unapproved generated runtime artifacts. Use [.env.example](.env.example) only
as a placeholder reference and never add real values to it.

Before committing, inspect the staged diff and confirm that ignored local
reports, virtual environments, dependency directories, caches, and environment
files have not been included.

## Future-stage proposals

Stage 1 and later work is capability-gated. Contributors may propose future
read-only or live integration work, but implementation requires separate,
explicit authorization and compliance with the Actual Automation Integration
Plan. A date, issue, pull request, milestone, or merge does not authorize a
Stage transition.

## Definition of done

A contribution is ready for review when its approved scope is complete, the
required validation has passed, documentation is accurate, safety boundaries
and fail-closed behavior are preserved, no secrets or private artifacts are
present, and the final diff contains only intended changes.
