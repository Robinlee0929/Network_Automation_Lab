# Phase 2K-05 - Guidance Mode Instruction Card Design / Static Only

Status: DONE / READY_FOR_REVIEW

Decision summary: Phase 2K-05 defines a static reviewer-facing design for future Guidance Mode instruction cards. It is static-only documentation and does not execute, generate, transform, send, validate, or authorize device commands, provider calls, model calls, runtime prompts, schema enforcement, live device access, or automation workflow behavior.

## Status

```text
PHASE: 2K-05
TASK_NAME: Guidance Mode Instruction Card Design / Static Only
TASK_MODE: STATIC_ONLY_DOCUMENTATION
STATUS: DONE / READY_FOR_REVIEW
AUTHORIZATION_LEVEL: STATIC_DESIGN_ONLY
UPSTREAM_REFERENCE: 2K-02 Vendor Profile Schema Contract / Planning Only
UPSTREAM_REFERENCE: 2K-03 Instruction Template Contract / Planning Only
UPSTREAM_REFERENCE: 2K-04 AI-visible / AI-hidden Boundary Review / Planning Only
DOWNSTREAM_CANDIDATE: 2K-06 Reference Mode Policy Gate / Planning Only
STATIC_ONLY_DOCUMENTATION: YES
IMPLEMENTATION_AUTHORIZED: NO
RUNTIME_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
COMMAND_GENERATION_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
```

This artifact is documentation-only, static-only, local-only, deterministic, report-only, and non-executing. It defines the shape of a future reviewer-facing card only.

## Purpose

Phase 2K-05 explains what a non-executing Guidance Mode instruction card is supposed to show to a reviewer or future user-facing layer.

The card design gives reviewers a readable way to inspect static guidance context, approved AI-visible inputs, prohibited AI-hidden data categories, and the safety boundary before any future implementation is considered.

The instruction card must not execute, generate, transform, send, or validate commands. It must not call providers, APIs, or models. It must not connect to live devices, load credentials, enforce schemas, render prompts, expand placeholders, or create runner, adapter, scheduler, queue, broker, worker, or agent-loop logic.

## Guidance Mode Card Structure

A future Guidance Mode instruction card should remain a static display artifact. It may describe reviewed guidance, but it must not become an executable workflow, runtime prompt, command generator, or policy decision engine.

Static card fields:

- `card_title`: short reviewer-facing title.
- `guidance_mode_label`: static mode label such as `guidance_mode_static_review`.
- `vendor_platform_profile_reference`: safe reference to a future static vendor or platform profile label.
- `scenario_or_job_type`: non-executing scenario label, such as report review or evidence review.
- `human_readable_instruction_summary`: plain-English guidance summary for reviewers.
- `allowed_ai_visible_input_summary`: summary of safe, static, policy-approved information that may be visible.
- `ai_hidden_prohibited_data_summary`: summary of data categories that must stay hidden, excluded, redacted, or unavailable.
- `safety_boundary_reminder`: visible reminder that the card is non-executing and does not authorize runtime behavior.
- `reviewer_checklist`: reviewer confirmation items before the card could be considered safe as static guidance.
- `non_execution_notice`: explicit notice that the card does not run commands or contact systems.
- `related_contracts_upstream_references`: references to Phase 2K-02, Phase 2K-03, and Phase 2K-04.

These fields are design vocabulary only. They are not a schema file, UI implementation, template renderer, prompt payload, provider payload, catalog entry, or runtime input.

## Alignment With Prior Contracts

Phase 2K-02 defines static vendor profile field-group expectations. A guidance card may reference safe profile labels or capability labels, but it must not load, parse, validate, or enforce a vendor profile.

Phase 2K-03 defines a static instruction template contract. A guidance card may reflect template concepts such as context, allowed guidance scope, forbidden actions, evidence references, and review checklist items, but it must not render instructions, expand placeholders, or construct prompts.

Phase 2K-04 defines the AI-visible / AI-hidden boundary. A guidance card may show only safe, static, policy-approved AI-visible summaries. It must not expose AI-hidden content in prompt text, output cards, generated instructions, examples, logs, provider payloads, or model payloads.

## AI-visible Vs AI-hidden Boundary

AI-visible card content may include safe instructional metadata and static profile references.

Allowed AI-visible examples:

- static card title
- guidance mode label
- safe vendor or platform profile reference
- non-secret scenario label
- report-only or mock-only evidence summary
- reviewer-approved safety reminder
- static upstream document references

AI-hidden content must not be surfaced into prompt text, output cards, generated instructions, examples, reports, logs, provider payloads, model payloads, or hidden instructions.

AI-hidden examples include:

- secrets, passwords, tokens, API keys, private keys, and device credentials
- real customer data
- live device inventory
- live topology requiring access control
- raw configurations containing sensitive values
- private local memory, private paths, or environment-specific details
- ambiguous data that has not been explicitly approved as AI-visible

Unknown or ambiguous data defaults to AI-hidden. Redaction must happen before any content is treated as AI-visible.

## Non-execution Boundary

The Guidance Mode instruction card:

- does not run commands
- does not generate device commands
- does not call providers, APIs, or models
- does not connect to live devices
- does not use SSH, NETCONF, RESTCONF, SNMP, HTTP device calls, or any device transport
- does not create runner, adapter, scheduler, queue, broker, worker, or agent-loop logic
- does not modify configurations
- does not back up configurations
- does not introduce secrets, credential loading, or secrets handling
- does not implement schema enforcement
- does not render runtime prompts or expand placeholders
- does not authorize future implementation by itself

Any future work that moves beyond static documentation requires a separate task request, an explicit authorization boundary, and separate validation requirements.

## Static Example Card

The following example is placeholder-only static documentation. It is not executable input and must not be loaded by runtime code.

```text
guidance_instruction_card:
  card_title: "Static Report Review Guidance"
  guidance_mode_label: "guidance_mode_static_review"
  vendor_platform_profile_reference:
    vendor_profile_id: "example_vendor_profile"
    platform_label: "example_platform_profile"
  scenario_or_job_type:
    scenario: "static_report_review"
  human_readable_instruction_summary:
    instruction_summary: "Review the existing report-only evidence summary."
  allowed_ai_visible_input_summary:
    - "Static report status labels."
    - "Reviewer-approved evidence summary wording."
    - "Non-secret vendor profile reference label."
  ai_hidden_prohibited_data_summary:
    - "No credentials, tokens, private keys, customer data, live inventory, or sensitive configuration values."
    - "Unknown or ambiguous data remains AI-hidden."
  safety_boundary_reminder:
    execution_notice: "This card is non-executing and reviewer-facing only."
  reviewer_checklist:
    - "Confirm static-only wording."
    - "Confirm no command generation."
    - "Confirm no hidden data leakage."
  related_contracts_upstream_references:
    - "Phase 2K-02 Vendor Profile Schema Contract / Planning Only"
    - "Phase 2K-03 Instruction Template Contract / Planning Only"
    - "Phase 2K-04 AI-visible / AI-hidden Boundary Review / Planning Only"
```

This example is safe because it uses neutral placeholders only. It contains no real credentials, real device identifiers, real IP addresses, executable vendor commands, provider payloads, model prompts, live inventory, or sensitive configuration data.

## Reviewer Checklist

A reviewer should confirm:

- Static-only: PASS / FAIL
- Non-executing: PASS / FAIL
- No provider, model, or API call: PASS / FAIL
- No command generation: PASS / FAIL
- No live-device access: PASS / FAIL
- No SSH, NETCONF, RESTCONF, SNMP, or HTTP device transport: PASS / FAIL
- No hidden data leakage: PASS / FAIL
- No secrets, credentials, tokens, or private keys: PASS / FAIL
- No runner, adapter, scheduler, queue, broker, worker, or agent loop: PASS / FAIL
- No config backup or config change: PASS / FAIL
- No Day1-Day160 rewrite: PASS / FAIL
- No second safety matrix: PASS / FAIL

If any checklist item is unclear, the card remains review-only and must not be treated as implementation-ready.

## Relationship To Future Phases

Phase 2K-06 Reference Mode Policy Gate remains future work. Phase 2K-05 does not define, implement, or authorize that policy gate.

Phase 2K-07 Static Vendor Profile Catalog Authorization Gate remains future work. Phase 2K-05 does not define, implement, load, validate, or authorize a catalog.

Phase 2K-05 does not authorize either Phase 2K-06 or Phase 2K-07 implementation. Future phases require separate user requests and must preserve the default safety baseline unless explicitly authorized otherwise.

## Non-goals

Phase 2K-05 does not add or modify:

- runtime code
- provider code
- schema enforcement code
- runner code
- adapter code
- scheduler, queue, broker, worker, or agent-loop behavior
- SSH, NETCONF, RESTCONF, SNMP, HTTP device calls, or live device access
- API, model, or provider calls
- secrets or credential handling
- configuration backup or configuration change behavior
- Day1-Day160 materials
- a second safety matrix
- tests that imply runtime execution behavior

Rejected or forbidden card claims must not invoke adapters, brokers, runners, queues, schedulers, workers, agent loops, provider clients, model clients, API clients, catalog loaders, prompt renderers, or execution paths.

## Acceptance Checklist

Phase 2K-05 is acceptable only if:

- The artifact is static-only documentation.
- The card structure is reviewer-facing and non-executing.
- The card fields align with Phase 2K-02, Phase 2K-03, and Phase 2K-04.
- AI-visible and AI-hidden content are clearly separated.
- The static example uses placeholder data only.
- No real credentials, device identifiers, IP addresses, executable vendor commands, provider payloads, or model prompts are included.
- No runtime behavior is added.
- No provider, model, or API calls are added.
- No command generation is added.
- No schema enforcement code is added.
- No runner, adapter, scheduler, queue, broker, worker, or agent loop is added.
- No live device access, SSH, NETCONF, RESTCONF, SNMP, or HTTP device calls are added.
- No configuration backup or configuration change behavior is added.
- Phase 2K-06 and Phase 2K-07 remain future work.
- README progress is updated.
- AGENTS.md was read before action.
- AGENTS.md was not modified.
- Documentation Readability Review was performed.

## Documentation Readability Review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_SCOPE_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT: PASS
STATUS_LABELS_CONSISTENT: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT_FOR_READABILITY: PASS
TERMINOLOGY_CONSISTENT_WITH_PHASE_2K_02_PHASE_2K_03_AND_PHASE_2K_04: PASS
CARD_FIELDS_UNDERSTANDABLE_TO_REVIEWERS: PASS
AI_VISIBLE_AND_AI_HIDDEN_BOUNDARY_PRESERVED: PASS
STATIC_EXAMPLE_USES_PLACEHOLDERS_ONLY: PASS
NO_IMPLEMENTATION_AUTHORIZATION_LANGUAGE: PASS
NO_RUNTIME_PROVIDER_AUTHORIZATION_LANGUAGE: PASS
NO_DUPLICATED_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

This document starts with the decision, explains the card purpose in short reviewer-friendly sections, separates static card fields from forbidden runtime behavior, preserves the AI-visible / AI-hidden boundary, and avoids language that could imply command generation, provider execution, live device access, secrets handling, or automation approval.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS_WITH_NOTES
PHASE: 2K-05
STATUS: DONE / READY_FOR_REVIEW
GUIDANCE_MODE_INSTRUCTION_CARD_STATIC_DESIGN_DEFINED: YES
IMPLEMENTATION_AUTHORIZED: NO
RUNTIME_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
COMMAND_GENERATION_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
NEXT_CANDIDATE: 2K-06 Reference Mode Policy Gate / Planning Only
FORBIDDEN_SCOPE_TOUCHED: NO
RUNTIME_CODE_MODIFIED: NO
TEST_CODE_MODIFIED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
DAY1_DAY160_REWRITTEN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

The phase decision is PASS_WITH_NOTES because the Guidance Mode instruction card is documented as a static reviewer-facing design only, while runtime behavior, command generation, provider runtime, API calls, model calls, schema enforcement, live-device access, and execution-capable work remain unauthorized.
