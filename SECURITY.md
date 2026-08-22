# Security Policy

Network Automation Lab is currently a safety-first Stage-0 project. Its
supported public path is local, mock-only, dry-run, report-only, and
reviewer-visible. Execution-capable behavior that has not passed a separate
explicit safety gate must fail closed.

This policy complements the [project overview](README.md),
[contributor guide](CONTRIBUTING.md), [repository rules](AGENTS.md), and
[Actual Automation Integration Plan](docs/automation_readiness/actual_automation_integration_plan.md).
Those documents remain the detailed sources for project operation and future
capability gates.

## Supported security scope

Security review should focus on the current `main` branch and documented
Stage-0 release path, including:

- the canonical local Flask reviewer dashboard and its bounded GET-oriented
  review surfaces;
- the secondary Next.js evidence and demonstration surfaces where the current
  documentation explicitly supports them;
- parsers, validation, report projection, local artifact access, fixtures,
  public configuration examples, safety gates, and no-execution evidence;
- tests and workflows that enforce fail-closed handling and protect tracked
  repository content.

Historical branches, unreviewed local changes, private infrastructure, and
production deployments are not supported security baselines. Historical code
or documentation that names networking operations does not grant authority to
run those operations.

## Threat model and security invariants

Inputs such as request bodies, report identifiers, artifact paths, fixture
content, and optional demonstration prompts may be attacker-controlled or
malformed. Repository content, local evidence, environment configuration, and
external provider responses must not be treated as authorization.

The following properties must hold:

- rejected, unavailable, or unapproved requests do not reach adapters,
  brokers, runners, device access, provider calls, or other execution paths;
- artifact and report access remains bounded to intended local evidence paths;
- default Stage-0 review does not require a device, provider, credential,
  private lab, or production environment;
- secrets and private data do not enter source, tests, fixtures, reports,
  logs, screenshots, issues, or review evidence;
- any future read-only or execution-capable behavior requires its own explicit
  capability gate, validation evidence, and task-specific approval.

## Reporting a vulnerability

Do not publish sensitive vulnerability or exploitation details in a GitHub
issue. This repository does not currently advertise a verified private
security-reporting channel. If the repository owner later lists one, use that
verified private channel.

If no private channel is available, open a minimal, non-sensitive
[GitHub issue](https://github.com/Robinlee0929/Network_Automation_Lab/issues/new)
asking the maintainer to provide a private reporting path. Include no exploit
details, secrets, credentials, private infrastructure information, or real
device configuration in that public request.

Once a private path is established, a useful report contains only the
non-sensitive information needed to assess the issue:

- affected path or component and the relevant commit, when known;
- observed and expected behavior;
- a minimal reproduction description and potential impact;
- whether the issue exists in the default Stage-0 path or requires an optional
  provider/demo mode.

Redact API keys, tokens, passwords, private IP addresses, device inventories,
production configuration, personal filesystem paths, and private lab details.
Do not test against systems, accounts, networks, or devices without explicit
authorization.

## Secrets and sensitive data

Never commit or publicly report real credentials, API keys, tokens, passwords,
private device configuration, private lab data, personal paths, private memory,
or unapproved runtime artifacts. Use [.env.example](.env.example) only as a
placeholder reference and keep real values in ignored local configuration.

If sensitive data is exposed, do not repeat it in an issue, pull request,
fixture, test, or remediation commit. Identify the affected location without
copying the value and coordinate through a verified private path.

## Stage-0 boundaries and future capability gates

The current supported baseline does not grant default authority for live
device access; SSH, NETCONF, or RESTCONF execution; configuration changes;
production execution; configuration backup against real devices; or queue,
scheduler, worker, broker, or autonomous AI execution.

The canonical Stage-0 review path is provider-free. The secondary Next.js
interface documents an optional, bounded provider recommendation preview that
is disabled by default and uses synthetic inventory. Its presence does not
make other provider-capable or legacy/internal routes part of the supported
Stage-0 path, and it does not authorize device or job execution.

Future read-only lab access and later execution-capable stages remain governed
by the Actual Automation Integration Plan. A date, milestone, issue, pull
request, merge, or code path does not activate a capability.

## Unsupported behavior and reportable security issues

The intentional absence of default live-device execution, configuration
changes, production orchestration, or other future-stage capabilities is not
itself a vulnerability.

Potentially reportable issues include a rejected request reaching an
execution-capable path, bypass of an explicit provider or execution gate,
secret exposure, unsafe artifact access or path traversal, unintended
configuration mutation, authorization bypass, or other behavior that violates
the documented fail-closed boundary. Reachability, required mode, realistic
impact, and exposure should inform severity; an unsupported feature request
alone should not.

## Contributor and remediation expectations

Contributions must follow [CONTRIBUTING.md](CONTRIBUTING.md) and preserve
fail-closed handling, no-execution proof for rejected or unapproved flows,
secret exclusion, bounded scope, reviewer-visible evidence, and negative
safety tests when behavior changes.

Security fixes should be narrow, reviewable, and validated against the affected
boundary. This project does not promise a response time, remediation SLA,
bounty, CVE assignment, or embargo period.
