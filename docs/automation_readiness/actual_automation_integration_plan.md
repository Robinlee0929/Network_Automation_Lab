# Actual Automation Integration Plan

**Decision summary: Stage 2 is CLOSED / LIVE PROVEN** for the separately
Owner-authorized MikroTik Lab1 VRRP read-only workflow on observed RouterOS
7.24.2 output. The third one-shot attempt passed and the closure review passed.
The default public review path remains Stage-0 offline evidence browsing.
Stage 3 is **NOT STARTED / requires separate Owner authorization**.

## 1. Purpose

This planning reference defines the gate-based conditions that must be met before the Network Automation Lab can move from mock-only and dry-run automation toward actual automation integration.

The document is documentation-only. It does not authorize live device access, SSH, NETCONF, RESTCONF, API access, provider integration, model integration, queue execution, scheduler execution, worker execution, AI agent loops, config backup execution, config change execution, or production execution paths.

## 2. Current Safety Position

The default platform safety position remains mock-only, dry-run, report-only,
and reviewer-visible. The separately approved Stage-2 one-shot validation is
recorded below as completed evidence. It provides no standing permission for
another live attempt or broader capability.

Phase 2C Interview MVP does not authorize live device access. It is intended to demonstrate safe planning, static evidence, local reports, reviewer workflows, and dry-run behavior without contacting routers, switches, controllers, provider APIs, model APIs, or other live infrastructure.

Queue, scheduler, worker, and AI agent loop capabilities are not required for the interview MVP. Their absence is intentional and does not block the current milestone.

## 3. Integration Principle

Real automation must be introduced by capability gates, not by calendar dates.

No stage becomes available because a date, phase label, demo target, or milestone has arrived. Each stage requires explicit review, documented safety evidence, negative tests where applicable, and separate user approval for the exact capability being introduced.

Read-only lab access may only happen after explicit user approval. Config change execution is future-only and requires separate approval beyond any read-only approval.

## 4. Stage Model

### Stage 0: Mock-only / Dry-run Platform

Status: CLOSED at
`main@aff250735ade18e4c274be8ac53c9672bb2cb07f`. Its operational safety
boundary remains the default until a later capability is separately authorized,
implemented, and validated.

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

Closure decision: PASS. The owner accepted the completed S0-EXIT review and
authorized formal Stage 0 closure. See
[Stage 0 Formal Closure](stage0_formal_closure.md).

### Stage 1: Read-only Lab Integration Planning

Historical entry status: PLANNING ENTRY. The Stage 0 closure record itself
authorized planning only and did not start implementation. This retained
planning boundary is distinct from the subsequently authorized, completed
Stage-2 workflow recorded below.

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

Status: **CLOSED / LIVE PROVEN**. The third real one-shot validation passed
under its exact Owner authorization; formal closure review is PASS. This
records a completed bounded operation and does not authorize another attempt.

#### Proven scope and result

- Device: one specified MikroTik **Lab1**, identified publicly only as
  `target.mikrotik.lab01`.
- Operation: `mikrotik.vrrp_status`; exact allowlisted read-only command
  `/interface vrrp print detail`, executed **once**, with **zero retries**.
- Compatibility: the observed RouterOS **7.24.2** output shape passed the
  strict parser and produced **valid canonical evidence**.
- Normalized demo result: `vrrp-lan`, `MASTER`, VRID `88`, priority
  `150`, running `true`.
- Raw device output was **not persisted**.

```text
STAGE2_REAL_LIVE_ONE_SHOT_VALIDATION = PASS
STAGE2_RUNTIME_CHAIN_PROVEN = YES
ROUTEROS_7_24_PARSER_COMPATIBILITY_PROVEN_LIVE = YES
CALLER_GUARD_RESTORATION_PROVEN = YES
STAGE2_CLOSURE_REVIEW = PASS
STAGE2_STATUS = CLOSED / LIVE PROVEN
```

#### Three live attempts

| Attempt | Classification and reached boundary | Cause and resolution |
| --- | --- | --- |
| 1 | **FAIL-CLOSED**; the exact RouterOS command executed | RouterOS 7.24.2 parser compatibility drift. Subsequently remediated by a bounded parser fix merged through PR #79. |
| 2 | **FAIL-CLOSED**; SSH/session reached; **no RouterOS command emitted** | Temporary caller-side observability guard defect. Production runtime defect **NOT ESTABLISHED**. |
| 3 | **PASS**; exact command once, zero retries; valid canonical evidence produced | The bounded Stage-2 real-device one-shot chain was proven and closure review passed. |

The first two attempts demonstrate fail-closed behavior; they do not represent
successful Stage-2 live closure. The temporary caller guard was restored after
the successful invocation and is not a permanent product/runtime component.

#### Proven authority chain and limits

Trusted configuration → canonical request → Owner authorization → replay
protection → pinned device trust → read-only credential → exact command policy
→ pinned SSH → strict vendor parser → canonical evidence.

The successful validation recorded one live-entrypoint call, one replay
consumption, one credential resolution, one TCP connection, one SSH handshake,
one authentication, one session, and one RouterOS command, with retry = 0.
AI does not own or bypass these authorities.

This closure proves only one specified Lab1, one VRRP read-only operation, one
exact allowlisted command, and the observed RouterOS 7.24.2 output in a one-shot
safety chain. It does **not** establish generic RouterOS support, all MikroTik
versions/models, multi-vendor live support, arbitrary CLI, write/config
automation, automated retries, production HA readiness, fleet orchestration,
autonomous remediation, an anti-rollback guarantee, or Stage-3 functionality.
Any further attempt needs fresh exact Owner authorization; scope expansion
needs separate review and applicable safety gates.

#### Closure evidence and code baseline

The closed live workflow used authoritative
`main@39da163d80e5d8b2dde215eb6c0979448d0739fd`,
tree `54b33650ced903e5e9457869617958317b5beba3`.

The externally retained closure receipt has SHA256
`3a83858ef47bd5253df9ad382f2d1bbae01f1626a4c73c22c367bf6284ad0120`.
This public summary uses the approved logical target identifier and normalized
demo result. It excludes device addresses, local retention paths, credential
contents and locators, private trust/replay identifiers, and raw RouterOS stdout.

The existing post-merge Safe CI evidence passed for that main baseline.
Open npm and Next.js maintenance items remain separate in the
[project status](../../README.md#post-release-or-deferred); closure does not
resolve them.

#### Canonical bounded VRRP read-only sequence

The following sequence indexes components used by the closed bounded workflow.
Delivery-time statements in the individual records remain historical context.
Neither this index nor component integration grants fresh execution authority.

| Slice | Canonical scope | Current boundary |
| --- | --- | --- |
| S2-RO-01 | [Minimal VRRP request and evidence contract](stage2_vrrp_readonly_s2_ro_01_contract.md) | Accepted offline contract |
| S2-RO-02 | [Fixed target registry](stage2_vrrp_readonly_s2_ro_02_target_registry.md) | Accepted offline contract |
| S2-RO-03 | [Credential resolver](stage2_vrrp_readonly_s2_ro_03_credential_resolver.md) | Accepted offline contract |
| S2-RO-04 | [Windows Credential Manager read backend](stage2_vrrp_readonly_s2_ro_04_windows_credential_backend.md) | Accepted bounded backend; no credential was read by this sequence index |
| S2-RO-05 | [Authorization envelope and durable replay ledger](stage2_vrrp_readonly_s2_ro_05_authorization_envelope_ledger.md) | Accepted offline/local contract; not execution authority |
| S2-RO-06 | [Owner verifier and exact approval source](stage2_vrrp_readonly_s2_ro_06_owner_verifier.md) | Accepted bounded verifier; not execution authority |
| S2-RO-07 | [Immutable offline known-host snapshot](stage2_vrrp_readonly_s2_ro_07_known_host_snapshot.md) | Formally closed; no transport authority |
| S2-RO-08 | [Immutable VRRP read-only command policy](stage2_vrrp_readonly_s2_ro_08_command_policy.md) | Implemented bounded policy used by the proven workflow |
| S2-RO-09 | [Pinned SSH transport](stage2_vrrp_readonly_s2_ro_09_pinned_ssh_transport.md) | Implemented bounded transport used by the proven workflow |
| S2-RO-10 | [Trusted runtime composition](stage2_vrrp_readonly_s2_ro_10_trusted_runtime_composition.md) | Composed authority chain proven for this exact operation |
| S2-RO-11 | [One-shot live entrypoint](stage2_vrrp_readonly_s2_ro_11_live_entrypoint.md) | Exact Owner-authorized one-shot invocation proven |

The S2-RO-07 → S2-RO-08 → S2-RO-09 order is authoritative for scope
discovery. It does not imply automatic authorization between slices.

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

Status: **NOT STARTED / requires separate Owner authorization**.

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

This is the default policy. The completed Stage-2 live run is bounded historical
evidence of a prior explicit Owner authorization and grants no standing live
authority. Every new live access requires fresh exact Owner authorization.

Stage 0 remains the default mock-only, dry-run, report-only public review path.
Stage 2 is CLOSED / LIVE PROVEN only for the recorded Owner-authorized Lab1
VRRP read-only operation. This closure activates no new adapter, protocol,
provider, credential, device, or execution capability and permits no repeat
attempt. Stage 3 remains NOT STARTED. Further live access or scope expansion
requires the applicable capability gates and separate exact Owner approval.

This document does not start Phase 2C-10 or any implementation phase. It does not create a second safety matrix. It is a durable planning reference for future review and approval decisions.
