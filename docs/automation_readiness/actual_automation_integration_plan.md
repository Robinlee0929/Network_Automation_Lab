# Actual Automation Integration Plan

## 1. Purpose

This planning reference defines the gate-based conditions that must be met before the Network Automation Lab can move from mock-only and dry-run automation toward actual automation integration.

The document is documentation-only. It does not authorize live device access, SSH, NETCONF, RESTCONF, API access, provider integration, model integration, queue execution, scheduler execution, worker execution, AI agent loops, config backup execution, config change execution, or production execution paths.

## 2. Current Safety Position

The current platform safety position remains mock-only, dry-run, report-only, and reviewer-visible unless a future approved safety gate explicitly changes that boundary.

Phase 2C Interview MVP does not authorize live device access. It is intended to demonstrate safe planning, static evidence, local reports, reviewer workflows, and dry-run behavior without contacting routers, switches, controllers, provider APIs, model APIs, or other live infrastructure.

Queue, scheduler, worker, and AI agent loop capabilities are not required for the interview MVP. Their absence is intentional and does not block the current milestone.

## 3. Integration Principle

Real automation must be introduced by capability gates, not by calendar dates.

No stage becomes available because a date, phase label, demo target, or milestone has arrived. Each stage requires explicit review, documented safety evidence, negative tests where applicable, and separate user approval for the exact capability being introduced.

Read-only lab access may only happen after explicit user approval. Config change execution is future-only and requires separate approval beyond any read-only approval.

## 4. Stage Model

### Stage 0: Mock-only / Dry-run Platform

Status: Current default.

Allowed:

- Static documentation and reviewer evidence.
- Mock execution paths.
- Dry-run planning.
- Report-only validation.
- Local fixtures and deterministic generated reports.

Not allowed:

- Live device access.
- SSH, NETCONF, RESTCONF, or provider API execution.
- Config backup execution against real devices.
- Config change execution.
- Queue, scheduler, worker, or AI agent loop execution.

Exit gate:

- Reviewer can verify no-execution proof for rejected, dry-run, mock-only, report-only, and documentation-only flows.
- Safety boundaries remain visible in documentation, tests, and report evidence.
- User explicitly approves planning for the next read-only lab integration stage.

### Stage 1: Read-only Lab Integration Planning

Status: Future planning only.

Allowed:

- Documentation of proposed read-only lab boundaries.
- Adapter interface design without execution.
- Fixture design and expected output contracts.
- Approval checklists for read-only lab access.
- Negative test plans proving rejected intents cannot reach adapters, brokers, runners, or live access paths.

Not allowed:

- Actual SSH, NETCONF, RESTCONF, provider API, or device communication.
- Secret creation or credential storage.
- Config backup execution.
- Config change execution.
- Production-like execution paths.

Exit gate:

- User explicitly approves the specific read-only lab capability to implement.
- Reviewers can see the exact commands or RPCs that would be permitted before any implementation exists.
- Failure, timeout, authentication, and rejection behavior are defined without requiring live access.

### Stage 2: Read-only Lab Adapter

Status: Future-only, approval required.

Allowed only after explicit user approval:

- A narrowly scoped read-only adapter for a lab environment.
- Read-only command or RPC allowlists.
- No-op behavior for rejected or unapproved intents.
- Local evidence that proves no configuration mutation is possible.

Not allowed:

- Configuration changes.
- Config backup execution unless separately approved by a future safety gate.
- Production device access.
- Queue, scheduler, worker, or AI agent loop driven execution.
- Secrets committed to the repository.

Exit gate:

- Adapter behavior is covered by negative tests proving rejected scenarios do not invoke execution paths.
- Read-only operations are allowlisted and reviewer-visible.
- User separately approves any expansion beyond the initial read-only lab scope.

### Stage 3: Controlled Config Plan Generation

Status: Future-only, approval required.

Allowed only after separate approval:

- Generation of configuration plans as text or structured artifacts.
- Human review envelopes for proposed changes.
- Diff-style reviewer views.
- Safety classification before any plan is considered eligible for execution.

Not allowed:

- Applying changes to devices.
- Running generated plans automatically.
- Queue, scheduler, worker, or AI agent loop execution of generated plans.
- Production execution paths.

Exit gate:

- Generated plans are review-only by default.
- Plans include explicit safety classification, target scope, rollback assumptions, and reviewer approval state.
- Rejected plans cannot reach adapters, brokers, runners, or execution paths.

### Stage 4: Controlled Change Execution

Status: Future-only, separate approval required.

Allowed only after a dedicated future safety gate and explicit user approval:

- Narrow, controlled execution of approved changes in a lab environment.
- Predefined command allowlists.
- Human approval immediately before execution.
- Evidence capture for attempted, skipped, failed, and completed operations.

Not allowed by earlier stages:

- Any config change execution.
- Any production change execution.
- Autonomous execution by queue, scheduler, worker, or AI agent loop.
- Broad command access.

Exit gate:

- A separate future authorization package authorizes this stage.
- Negative tests prove unsafe, rejected, or unapproved changes cannot execute.
- Reviewers can trace every execution decision to an explicit approval.

### Stage 5: Production-like Platform

Status: Future-only, not authorized by this document.

Allowed only after future approval:

- Production-like workflows with mature access control, audit evidence, rollback planning, operational monitoring, and explicit human approval gates.

Not allowed by this document:

- Production execution.
- Production credentials.
- Production device access.
- Autonomous remediation.
- Calendar-based promotion into production-like behavior.

Exit gate:

- A separate future authorization package defines production-like scope, risk ownership, operational controls, audit requirements, rollback expectations, and user approval requirements.

## 5. Go / No-Go Checklist for Real Automation

Go requires all of the following:

- The requested capability maps to a named stage.
- The stage is authorized by an explicit user approval for that exact capability.
- The capability is introduced by a documented gate, not by a date or phase label.
- The safety boundary states what is allowed and what remains forbidden.
- Negative tests prove rejected scenarios do not reach adapters, brokers, runners, or execution paths.
- Secrets, credentials, tokens, and private local details are excluded from the repository.
- Reviewer evidence clearly distinguishes mock-only, dry-run, read-only, plan-generation, and execution-capable behavior.
- Config change execution has its own separate future approval if it is in scope.

No-Go applies when any of the following is true:

- Approval is implied by schedule, phase name, milestone, or interview timing rather than explicitly granted.
- The request would add SSH, NETCONF, RESTCONF, provider API, model API, secrets, queue, scheduler, worker, AI agent loop, config backup execution, config change execution, or live device access without a specific future safety gate.
- The request weakens no-execution proof for rejected, dry-run, mock-only, report-only, documentation-only, or design-only flows.
- The request introduces production execution behavior.
- The request relies on live infrastructure that is not explicitly approved for the current stage.

## 6. Default Decision

Default decision: NO-GO for real automation.

The platform remains Stage 0 mock-only / dry-run by default. Any movement toward read-only lab access, controlled plan generation, controlled change execution, or production-like behavior must be introduced by an explicit capability gate and separate user approval.

This document does not start Phase 2C-10 or any implementation phase. It does not create a second safety matrix. It is a durable planning reference for future review and approval decisions.
