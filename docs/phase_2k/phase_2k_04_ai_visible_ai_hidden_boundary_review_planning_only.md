# Phase 2K-04 - AI-visible / AI-hidden Boundary Review / Planning Only

Status: READY_FOR_REVIEW

Decision summary: Phase 2K-04 defines the planning-only boundary between information that may be visible to AI-assisted guidance and information that must remain hidden, excluded, redacted, or unavailable. It is documentation-only and does not authorize AI execution, provider calls, model calls, live device access, automation loops, runtime prompt construction, policy enforcement code, or implementation behavior.

## Status

```text
PHASE: 2K-04
TASK_NAME: AI-visible / AI-hidden Boundary Review / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION
STATUS: PLANNING_ONLY
AUTHORIZATION_LEVEL: DOCUMENTATION_ONLY_BOUNDARY_REVIEW
UPSTREAM_DEPENDENCY: 2K-03 Instruction Template Contract / Planning Only
DOWNSTREAM_CANDIDATE: 2K-05 Guidance Mode Instruction Card Design / Static Only
PLANNING_ONLY_DOCUMENTATION: YES
IMPLEMENTATION_AUTHORIZED: NO
AI_EXECUTION_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
RUNTIME_PROMPT_CONSTRUCTION_AUTHORIZED: NO
SECRETS_HANDLING_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
```

This artifact is documentation-only, planning-only, local-only, deterministic, report-only, and non-executing. It defines a reviewer-facing visibility boundary only.

## Purpose

Phase 2K-04 defines what information may be shown to AI-assisted guidance and what information must remain hidden, excluded, redacted, or unavailable.

The purpose is to help future planning phases discuss guidance safely without confusing static documentation with runtime AI behavior. This phase confirms that AI-visible content must be safe, non-secret, static, and policy-approved before it can be referenced by future guidance concepts.

This phase does not authorize AI execution, provider calls, model calls, API calls, live device access, automation loops, runtime prompt construction, hidden prompts, instruction rendering, catalog loading, policy enforcement code, adapters, runners, schedulers, queues, workers, agent loops, or device execution paths.

## AI-visible Information Category

AI-visible information is content that may be suitable for AI-assisted guidance only after it is reviewed as static, non-secret, non-executing, and policy-approved.

Examples of AI-visible information include:

- static vendor profile descriptions
- non-secret capability labels
- non-executing guidance templates
- public or mock-only lab context
- report-only validation summaries
- policy-approved planning metadata
- reviewer-approved safety boundary notices
- static evidence references that do not expose private data

AI-visible content must remain guidance text for human review. It must not become a runtime prompt, model payload, provider payload, hidden instruction, command generator, execution request, or approval bypass.

## AI-hidden Information Category

AI-hidden information is content that must remain excluded from AI-assisted guidance unless a later separately approved safety gate explicitly changes the boundary. Unknown or ambiguous content defaults to AI-hidden.

Examples of AI-hidden information include:

- secrets
- passwords
- API keys
- tokens
- private keys
- device credentials
- real customer data
- live device inventory
- live topology requiring access control
- raw configuration files containing sensitive values
- private local memory
- private local paths or environment-specific details
- source material that has not been reviewed for AI-visible use
- any data not explicitly authorized for AI-visible guidance

AI-hidden content must not be inserted into prompts, templates, generated guidance, reports, provider payloads, model payloads, logs, evidence exports, or reviewer-facing summaries that are labeled AI-visible.

## Boundary Rules

The Phase 2K-04 boundary uses these planning rules:

- AI-visible content must be static, non-secret, non-executing, and policy-approved.
- AI-hidden content must not be inserted into prompts, templates, generated guidance, reports, provider payloads, model payloads, logs, or evidence exports.
- Redaction must happen before content becomes AI-visible.
- Unknown or ambiguous data must default to AI-hidden.
- Reviewer-only notes must not conflict with visible safety boundaries.
- Hidden notes must not become hidden runtime instructions.
- Planning documents do not authorize runtime access.
- A future vendor profile, instruction template, guidance card, or policy gate cannot authorize live access, provider calls, model calls, secrets handling, or execution by itself.

These rules are planning language only. They do not implement redaction, scanning, filtering, enforcement, prompt construction, provider calls, or runtime validation.

## Review Checklist

Future phases should answer this checklist before treating any content as AI-visible:

- Is the content static?
- Is the content non-secret?
- Is the content mock-only or report-only?
- Is the content free of credentials?
- Is the content free of customer-sensitive or device-sensitive data?
- Is the content free of private local memory, private paths, tokens, and keys?
- Is the content explicitly allowed by the current phase?
- Is the content consistent with the visible safety boundary?
- If uncertain, is it treated as AI-hidden?

If any answer is unclear, the content remains AI-hidden until a later review explicitly approves it for AI-visible guidance.

## Relationship To Adjacent Phases

Phase 2K-01 introduced the future Vendor Profile Provider architecture flow as a static planning concept. Phase 2K-02 defined static vendor profile field-group expectations. Phase 2K-03 defined a static instruction template contract.

Phase 2K-04 refines the visibility boundary those earlier documents referenced. It does not create a provider, catalog, schema, instruction renderer, prompt renderer, guidance card, policy gate, runtime integration, or enforcement path.

Phase 2K-05 may later design static guidance-mode instruction cards that reference only approved AI-visible planning content. Phase 2K-04 does not start Phase 2K-05, select an implementation slice, or authorize any future card runtime.

Phase 2K-06 and Phase 2K-07 remain future-only. This document does not authorize reference-mode policy gates, static catalog authorization, catalog loading, provider registries, runtime providers, AI/model/API calls, live access, or execution-capable behavior.

## Non-goals

Phase 2K-04 does not:

- implement AI provider integration
- add runtime prompt construction
- add provider, API, or model calls
- add secret scanning runtime
- add secrets handling or credential loading
- add device access
- add SSH, NETCONF, RESTCONF, SNMP, or HTTP device calls
- add execution workflows
- add runner, adapter, scheduler, queue, broker, worker, or agent-loop behavior
- add policy enforcement code
- add redaction, filtering, or validation code
- add configuration backup or configuration change behavior
- authorize future implementation by itself
- rewrite Day1-Day160 materials
- create a second safety matrix

Rejected or forbidden boundary claims must not invoke adapters, brokers, runners, queues, schedulers, workers, agent loops, provider clients, model clients, API clients, catalog loaders, prompt renderers, or execution paths.

## Acceptance Checklist

Phase 2K-04 is acceptable only if:

- The boundary review is documentation-only.
- AI-visible information examples are static, non-secret, and non-executing.
- AI-hidden information examples include secrets, credentials, customer-sensitive data, live inventory, and sensitive configuration material.
- Unknown or ambiguous content defaults to AI-hidden.
- Redaction is described as required before content becomes AI-visible.
- No runtime behavior is added.
- No provider, model, or API calls are added.
- No prompt construction or instruction rendering is added.
- No secrets handling, credential loading, or secret scanning runtime is added.
- No runner, adapter, scheduler, queue, broker, worker, or agent loop is added.
- No live device access, SSH, NETCONF, RESTCONF, SNMP, or HTTP device calls are added.
- No configuration backup or configuration change behavior is added.
- Phase 2K-05 through Phase 2K-07 remain future tasks.
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
TERMINOLOGY_CONSISTENT_WITH_PHASE_2K_01_PHASE_2K_02_AND_PHASE_2K_03: PASS
AI_VISIBLE_CATEGORY_STATIC_NON_SECRET_AND_POLICY_APPROVED: PASS
AI_HIDDEN_CATEGORY_EXCLUDES_SENSITIVE_AND_UNAUTHORIZED_DATA: PASS
UNKNOWN_DATA_DEFAULTS_TO_AI_HIDDEN: PASS
NO_IMPLEMENTATION_AUTHORIZATION_LANGUAGE: PASS
NO_RUNTIME_PROVIDER_AUTHORIZATION_LANGUAGE: PASS
NO_DUPLICATED_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

This document starts with the decision, explains the visibility boundary without hidden context, separates AI-visible examples from AI-hidden examples, keeps forbidden scope explicit, and avoids language that could imply runtime AI behavior, provider execution, live device access, secrets handling, or automation approval.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS_WITH_NOTES
PHASE: 2K-04
STATUS: PLANNING_ONLY
AI_VISIBLE_AI_HIDDEN_BOUNDARY_REVIEWED: YES
IMPLEMENTATION_AUTHORIZED: NO
AI_EXECUTION_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
RUNTIME_PROMPT_CONSTRUCTION_AUTHORIZED: NO
SECRET_SCANNING_RUNTIME_AUTHORIZED: NO
SECRETS_HANDLING_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
NEXT_CANDIDATE: 2K-05 Guidance Mode Instruction Card Design / Static Only
FORBIDDEN_SCOPE_TOUCHED: NO
RUNTIME_CODE_MODIFIED: NO
TEST_CODE_MODIFIED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
DAY1_DAY160_REWRITTEN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

The phase decision is PASS_WITH_NOTES because the AI-visible / AI-hidden boundary is documented for future planning use only, while AI execution, provider runtime, API calls, model calls, runtime prompt construction, secrets handling, live-device access, and execution-capable work remain unauthorized.
