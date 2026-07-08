# Phase 2K-06 - Reference Mode Policy Gate / Planning Only

Status: DONE / READY_FOR_REVIEW

Decision summary: Phase 2K-06 defines a planning-only policy gate for future Reference Mode. It is documentation-only and does not implement reference loading, catalog loading, provider runtime behavior, API calls, model calls, runtime prompt construction, schema enforcement, command generation, live device access, or automation workflow behavior.

## Status

```text
PHASE: 2K-06
TASK_NAME: Reference Mode Policy Gate / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION
STATUS: DONE / READY_FOR_REVIEW
AUTHORIZATION_LEVEL: DOCUMENTATION_ONLY_POLICY_GATE
UPSTREAM_REFERENCE: 2K-02 Vendor Profile Schema Contract / Planning Only
UPSTREAM_REFERENCE: 2K-03 Instruction Template Contract / Planning Only
UPSTREAM_REFERENCE: 2K-04 AI-visible / AI-hidden Boundary Review / Planning Only
UPSTREAM_REFERENCE: 2K-05 Guidance Mode Instruction Card Design / Static Only
DOWNSTREAM_CANDIDATE: 2K-07 Static Vendor Profile Catalog Authorization Gate
PLANNING_ONLY_DOCUMENTATION: YES
IMPLEMENTATION_AUTHORIZED: NO
REFERENCE_LOADING_AUTHORIZED: NO
CATALOG_LOADING_AUTHORIZED: NO
RUNTIME_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
COMMAND_GENERATION_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
```

This artifact is documentation-only, planning-only, local-only, deterministic, report-only, and non-executing. It defines a reviewer-facing policy gate concept only.

## Purpose

Phase 2K-06 explains how a future Reference Mode must stay gated before any static reference material can be presented as reviewer-facing guidance context.

Reference Mode means a future non-executing display concept that may point reviewers to approved static reference context, such as a safe upstream planning document, a non-secret profile label, or a reviewer-approved static evidence reference.

The policy gate exists to prevent Reference Mode from being mistaken for a runtime reference loader, external knowledge connector, catalog loader, search tool, prompt constructor, model payload builder, command generator, or automation approval path.

## Allowed Scope

A future Reference Mode policy gate may describe whether static reference content is eligible for reviewer-facing display.

Allowed planning concepts:

- static upstream document references
- safe vendor or platform profile labels
- non-secret report-only evidence references
- approved AI-visible summaries from Phase 2K-04
- reviewer-facing rationale for why a reference is allowed or blocked
- static status labels such as `REVIEW_ONLY`, `LOCKED`, `BLOCKED`, or `STATIC_REFERENCE_ALLOWED`
- explicit non-execution notices

These concepts are vocabulary for future review only. They are not schema files, runtime objects, provider payloads, prompt payloads, catalog entries, UI components, or executable inputs.

## Prohibited Reference Categories

Reference Mode must block reference candidates that contain, depend on, or imply use of forbidden material.

Prohibited reference categories:

- secrets, credentials, passwords, tokens, API keys, private keys, or credential references
- real customer data or customer-sensitive context
- live device inventory or live topology requiring access control
- raw configurations containing sensitive values
- private local memory, private paths, or environment-specific details
- executable device commands, command sequences, configuration snippets, or command-generation hints
- provider payloads, model payloads, API payloads, search requests, or external fetch targets
- catalog entries that have not passed a future separate catalog authorization gate
- any ambiguous reference that has not been explicitly approved as AI-visible or reviewer-visible

Unknown or ambiguous reference material defaults to blocked. This section is a documentation-only policy boundary and does not implement filtering, scanning, loading, enforcement, or validation code.

## Policy Gate Questions

A future Reference Mode gate should answer these questions before any reference is treated as displayable:

- Is the reference static and local to approved reviewer documentation?
- Is the reference free of secrets, credentials, tokens, private keys, private paths, customer-sensitive data, and live inventory?
- Is the reference explicitly approved as AI-visible or reviewer-visible?
- Is the reference non-executing and free of device commands?
- Does the reference avoid runtime prompt construction, placeholder expansion, and instruction rendering?
- Does the reference avoid provider, API, model, search, catalog, and external fetch behavior?
- Does the reference preserve the Phase 2K-04 AI-visible / AI-hidden boundary?
- Does the reference avoid implying authorization for live access, command generation, or configuration change?
- If any answer is unclear, is the reference blocked by default?

If any question cannot be answered with a safe reviewer-visible `PASS`, the reference remains blocked and must not be treated as Reference Mode display content.

## Reviewer Checklist

A reviewer should confirm:

- Title and status are present: PASS / FAIL
- Reference Mode is defined as future static display review only: PASS / FAIL
- Allowed reference categories are static, non-secret, and reviewer-facing: PASS / FAIL
- Prohibited reference categories are blocked by default: PASS / FAIL
- Policy gate questions preserve the AI-visible / AI-hidden boundary: PASS / FAIL
- The static example uses placeholder-only content: PASS / FAIL
- No reference loading or catalog loading is authorized: PASS / FAIL
- No provider, API, model, search, or external source call is authorized: PASS / FAIL
- No command generation is authorized: PASS / FAIL
- No live device access is authorized: PASS / FAIL
- No runner, adapter, scheduler, queue, broker, worker, or agent loop is added: PASS / FAIL
- No 2K-07 implementation or authorization is started: PASS / FAIL

If any checklist item is unclear, the reference gate remains review-only and must not be treated as implementation-ready.

## Gate Outcomes

The planning-only gate may use these reviewer labels:

- `STATIC_REFERENCE_ALLOWED`: the reference is static, non-secret, approved for display, and non-executing.
- `REVIEW_ONLY`: the reference may be inspected by a reviewer but is not approved as future display content.
- `BLOCKED`: the reference contains forbidden, ambiguous, unapproved, or unsafe material.
- `LOCKED`: the reference would require a future separate safety gate before any change in status.

These labels are documentation labels only. They do not implement enforcement, validation code, schema checks, runtime filters, loaders, adapters, providers, prompts, model calls, or execution paths.

## AI-visible And AI-hidden Boundary

Reference Mode must inherit the Phase 2K-04 boundary.

AI-visible reference content may include only safe, static, non-secret, reviewer-approved summaries.

AI-hidden content must remain excluded from Reference Mode display, examples, prompt text, generated instructions, reports, logs, provider payloads, model payloads, hidden instructions, or reference metadata.

Unknown or ambiguous content defaults to blocked. Redaction and review must happen before content can be described as AI-visible.

## Relationship To Guidance Mode

Phase 2K-05 defines static Guidance Mode instruction card design. Phase 2K-06 defines the planning-only policy gate that would decide whether a future reference is eligible to support static guidance display.

Guidance Mode and Reference Mode remain future concepts. Neither mode may execute commands, generate device commands, call providers, call APIs, call models, load catalogs, fetch external references, enforce schemas, construct prompts, expand placeholders, connect to devices, or create automation workflow behavior.

## Non-execution Boundary

The Reference Mode policy gate:

- does not load references
- does not load catalogs
- does not search external sources
- does not call providers, APIs, or models
- does not construct runtime prompts
- does not render instructions
- does not expand placeholders
- does not generate device commands
- does not run commands
- does not connect to live devices
- does not use SSH, NETCONF, RESTCONF, SNMP, or HTTP device transport
- does not create runner, adapter, scheduler, queue, broker, worker, or agent-loop logic
- does not modify configurations
- does not back up configurations
- does not introduce secrets, credential loading, or secrets handling
- does not implement schema enforcement
- does not authorize future implementation by itself

Any future work that moves beyond static planning documentation requires a separate task request, explicit authorization boundary, and separate validation requirements.

## Static Example Gate Record

The following example is placeholder-only static documentation. It is not executable input and must not be loaded by runtime code.

```text
reference_mode_policy_gate:
  gate_label: "reference_mode_static_gate"
  reference_candidate:
    reference_id: "example_static_reference"
    reference_type: "approved_planning_document"
  eligibility_review:
    static_and_local: "PASS"
    non_secret: "PASS"
    ai_visible_or_reviewer_visible: "PASS"
    non_executing: "PASS"
    no_command_generation: "PASS"
    no_runtime_prompt_construction: "PASS"
    no_provider_api_model_call: "PASS"
    no_catalog_loading: "PASS"
    no_live_access: "PASS"
  gate_outcome: "STATIC_REFERENCE_ALLOWED"
  reviewer_notice: "This record is static planning documentation only."
```

This example is safe because it uses neutral placeholders only. It contains no real credentials, real device identifiers, real IP addresses, executable vendor commands, provider payloads, model prompts, catalog entries, live inventory, external source calls, or sensitive configuration data.

## Relationship To Future Phases

Phase 2K-07 Static Vendor Profile Catalog Authorization Gate remains future work. Phase 2K-06 does not define, implement, load, validate, or authorize a catalog.

Phase 2K-08 README Fastest Hands-on Path / Reviewer Onboarding Clarity remains future work. Phase 2K-06 does not update onboarding flow beyond current Phase 2K status references.

Phase 2K-09 README License Clarification / MIT License Usage Note remains future work. Phase 2K-06 does not define or change licensing guidance.

Phase 2K-06 does not authorize any future implementation. Future phases require separate user requests and must preserve the default safety baseline unless explicitly authorized otherwise.

## Non-goals

Phase 2K-06 does not add or modify:

- runtime code
- provider code
- schema enforcement code
- catalog loader code
- reference loader code
- runner code
- adapter code
- scheduler, queue, broker, worker, or agent-loop behavior
- SSH, NETCONF, RESTCONF, SNMP, HTTP device calls, or live device access
- API, model, provider, search, or external source calls
- secrets or credential handling
- configuration backup or configuration change behavior
- Day1-Day160 materials
- a second safety matrix
- tests that imply runtime execution behavior

Rejected or forbidden reference claims must not invoke adapters, brokers, runners, queues, schedulers, workers, agent loops, provider clients, model clients, API clients, catalog loaders, reference loaders, prompt renderers, or execution paths.

## Acceptance Checklist

Phase 2K-06 is acceptable only if:

- The artifact is planning-only documentation.
- The policy gate is reviewer-facing and non-executing.
- Allowed reference categories are explicit and static-only.
- Prohibited reference categories are explicit and blocked by default.
- The gate questions preserve the Phase 2K-04 AI-visible / AI-hidden boundary.
- A reviewer checklist is present.
- Reference Mode is described as future static display review only.
- Blocked or ambiguous reference content defaults to blocked.
- The static example uses placeholder data only.
- No real credentials, device identifiers, IP addresses, executable vendor commands, provider payloads, model prompts, catalog entries, external fetches, or sensitive configuration data are included.
- No runtime behavior is added.
- No reference loading or catalog loading is added.
- No provider, model, API, search, or external source calls are added.
- No command generation is added.
- No schema enforcement code is added.
- No runner, adapter, scheduler, queue, broker, worker, or agent loop is added.
- No live device access, SSH, NETCONF, RESTCONF, SNMP, or HTTP device calls are added.
- No configuration backup or configuration change behavior is added.
- Phase 2K-07 remains future work.
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
TERMINOLOGY_CONSISTENT_WITH_PHASE_2K_02_THROUGH_PHASE_2K_05: PASS
REFERENCE_MODE_BOUNDARY_PRESERVED: PASS
AI_VISIBLE_AND_AI_HIDDEN_BOUNDARY_PRESERVED: PASS
STATIC_EXAMPLE_USES_PLACEHOLDERS_ONLY: PASS
NO_IMPLEMENTATION_AUTHORIZATION_LANGUAGE: PASS
NO_RUNTIME_PROVIDER_AUTHORIZATION_LANGUAGE: PASS
NO_CATALOG_LOADING_AUTHORIZATION_LANGUAGE: PASS
NO_DUPLICATED_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

This document starts with the decision, explains the Reference Mode gate purpose in short reviewer-friendly sections, separates allowed planning vocabulary from forbidden runtime behavior, preserves the AI-visible / AI-hidden boundary, and avoids language that could imply reference loading, catalog loading, command generation, provider execution, live device access, secrets handling, or automation approval.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS_WITH_NOTES
PHASE: 2K-06
STATUS: DONE / READY_FOR_REVIEW
REFERENCE_MODE_POLICY_GATE_DEFINED: YES
IMPLEMENTATION_AUTHORIZED: NO
REFERENCE_LOADING_AUTHORIZED: NO
CATALOG_LOADING_AUTHORIZED: NO
RUNTIME_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
COMMAND_GENERATION_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
NEXT_CANDIDATE: 2K-07 Static Vendor Profile Catalog Authorization Gate
FORBIDDEN_SCOPE_TOUCHED: NO
RUNTIME_CODE_MODIFIED: NO
TEST_CODE_MODIFIED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
DAY1_DAY160_REWRITTEN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

The phase decision is PASS_WITH_NOTES because the Reference Mode policy gate is documented for future static review only, while runtime behavior, reference loading, catalog loading, command generation, provider runtime, API calls, model calls, schema enforcement, live-device access, and execution-capable work remain unauthorized.
