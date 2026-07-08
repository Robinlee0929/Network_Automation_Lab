# Phase 2K-02 - Vendor Profile Schema Contract / Planning Only

Status: READY_FOR_REVIEW

Decision summary: Phase 2K-02 defines a static planning contract for a future Vendor Profile Schema only. It does not implement schema enforcement, provider loading, runtime provider behavior, API calls, model calls, live vendor logic, adapters, runners, or automation execution.

## Status

```text
PHASE: 2K-02
TASK_NAME: Vendor Profile Schema Contract / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION
STATUS: PLANNING_ONLY
IMPLEMENTATION_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
CATALOG_LOADING_IMPLEMENTATION_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
```

This artifact is documentation-only, planning-only, local-only, deterministic, report-only, and non-executing. It describes future schema expectations in reviewer-facing language; it does not create a schema file, parser, validator, provider, loader, catalog, runner, adapter, or command path.

## Purpose

Phase 2K-02 defines how a future vendor profile could be shaped if a later phase separately authorizes static profile work. The goal is to give reviewers a contract vocabulary for vendor identity, guidance modes, declared capabilities, forbidden capabilities, AI-visible guidance, AI-hidden or reviewer-only notes, safety boundaries, compatibility notes, and future validation expectations.

The profile contract is static planning material only. A vendor profile does not authorize execution, live device access, SSH, NETCONF, RESTCONF, API calls, model calls, provider calls, configuration backup, configuration change, or any bypass of the existing dry-run, report-only, and mock-only boundaries.

## Non-execution Boundary

Vendor profiles described by this contract must remain descriptive. They may explain what a future reviewer could expect to see in a static profile, but they must never grant operational permission.

The contract does not allow:

- direct or indirect device access
- SSH, NETCONF, RESTCONF, API, model, or provider calls
- live vendor lookup
- provider runtime behavior
- profile loading or catalog loading
- executable validation
- runner, adapter, scheduler, queue, broker, worker, or agent-loop behavior
- generated commands or command allowlists for execution
- configuration backup or configuration change
- secrets, credentials, tokens, private local memory, or environment-variable requirements
- production execution paths

Rejected or forbidden profile claims must not invoke adapters, brokers, runners, queues, schedulers, workers, agent loops, provider clients, model clients, API clients, catalog loaders, or execution paths.

## Schema Contract Overview

The future Vendor Profile Schema is expected to describe a single static vendor profile. The shape below is illustrative pseudo-structure only. It is not JSON Schema, not runtime configuration, and not executable input.

```text
vendor_profile:
  schema_version:
  vendor_identity:
  profile_metadata:
  supported_guidance_modes:
  capability_declarations:
  unsupported_or_forbidden_capabilities:
  safety_boundary_declarations:
  ai_visible_content:
  ai_hidden_or_reviewer_only_content:
  compatibility_notes:
  future_validation_notes:
```

Every field group is intended for future documentation review. None of these field groups may be interpreted as permission to run commands, call a provider, read secrets, contact a device, or change network state.

## Required Field Groups

Future vendor profiles should require these field groups before they are considered complete as static planning artifacts:

- `schema_version`: identifies the planning contract version used by the profile.
- `vendor_identity`: names the vendor family, platform family, and safe display label.
- `profile_metadata`: records profile purpose, status, owner or reviewer role, and last review note without private personal details.
- `supported_guidance_modes`: lists guidance modes that the profile may describe conceptually, such as review guidance, reference guidance, or static instruction-card guidance.
- `capability_declarations`: describes non-secret, non-executing vendor capabilities at a high level.
- `unsupported_or_forbidden_capabilities`: lists capabilities that must remain blocked, unsupported, or out of scope.
- `safety_boundary_declarations`: states the non-execution boundary, no-live-access boundary, no-secret boundary, and no-provider-runtime boundary.
- `ai_visible_content`: identifies profile content that may be safe for an AI-facing guidance surface after review.
- `ai_hidden_or_reviewer_only_content`: identifies notes that stay reviewer-only and must not become hidden runtime instructions.
- `compatibility_notes`: records conceptual compatibility with adjacent planning phases.
- `future_validation_notes`: lists future review expectations without implementing validation.

## Field Meanings And Constraints

`schema_version` is mandatory in the future contract so reviewers can tell which planning vocabulary a profile uses. It must remain a documentation version, not a runtime migration key.

`vendor_identity` is mandatory and should contain only safe labels such as vendor family, platform family, and display name. It must not include device hostnames, IP addresses, serial numbers, account names, secrets, tokens, local paths, or private inventory.

`profile_metadata` is mandatory and should describe the planning status and review purpose. It must not create ownership of runtime behavior or imply that a profile is approved for execution.

`supported_guidance_modes` is mandatory and should describe conceptual guidance modes only. It may name future modes such as review guidance, reference guidance, or instruction-card guidance, but it must not authorize those modes as runtime features.

`capability_declarations` is mandatory and should use plain English to describe vendor capabilities at a safe level, such as "supports interface status review wording" or "requires caution around configuration-changing examples." These declarations must remain descriptive only.

`unsupported_or_forbidden_capabilities` is mandatory and should explicitly block unsafe claims. It must include live access, command execution, provider/model/API calls, secrets, configuration backup, and configuration change unless a later approved safety gate defines a narrower future boundary.

`safety_boundary_declarations` is mandatory and must make the dry-run, report-only, mock-only, local-only, deterministic, and non-executing boundary visible to reviewers.

`ai_visible_content` is mandatory in the future contract when a profile includes any guidance intended for an AI-facing surface. It may include high-level safe wording, static cautions, and reviewer-approved guidance labels. It must not include secrets, operational instructions for execution, hidden override language, or device-specific access details.

`ai_hidden_or_reviewer_only_content` is mandatory when a profile includes non-visible notes. These notes may explain why content is withheld or why a capability is forbidden, but they must not become hidden instructions, hidden prompts, hidden policies that conflict with visible safety boundaries, or hidden runtime behavior.

`compatibility_notes` are mandatory and should explain how the profile remains compatible with Phase 2K-01 and future Phase 2K documents without starting those phases.

`future_validation_notes` are mandatory and may describe checks a later planning or implementation phase could consider. They must not implement validation, require executable tools, or add runtime schema enforcement in this phase.

## Static Valid Profile Example

The following example is static documentation only. It is not executable input and must not be loaded by runtime code.

```text
vendor_profile:
  schema_version: "2k-planning-v1"
  vendor_identity:
    vendor_family: "Example Network OS"
    platform_family: "Example Router"
    display_label: "Example Router guidance profile"
  profile_metadata:
    status: "planning_only"
    purpose: "Describe safe reviewer guidance fields for a future vendor profile."
  supported_guidance_modes:
    - "review_guidance"
    - "reference_guidance"
    - "static_instruction_card_guidance"
  capability_declarations:
    - "May describe non-executing interface review guidance."
    - "May describe static evidence wording expectations."
  unsupported_or_forbidden_capabilities:
    - "No SSH authorization."
    - "No live command authorization."
    - "No provider, API, or model call authorization."
    - "No configuration backup or configuration change authorization."
  safety_boundary_declarations:
    execution_authorized: "NO"
    live_access_authorized: "NO"
    provider_runtime_authorized: "NO"
  ai_visible_content:
    - "Use static, reviewer-approved wording only."
    - "State that all guidance is non-executing."
  ai_hidden_or_reviewer_only_content:
    - "Reviewer note: keep source rationale out of AI-visible guidance until separately reviewed."
  compatibility_notes:
    - "References Phase 2K-01 conceptually."
    - "May be referenced by future Phase 2K-03 planning."
  future_validation_notes:
    - "A future phase may define documentation checks for required field presence."
```

This example is valid as planning text because it declares non-execution, keeps profile content static, and does not add a provider, parser, loader, validator, API call, model call, device access, or execution path.

## Static Invalid Profile Examples

The following examples are invalid as planning profile claims. They are included to make forbidden boundaries reviewable.

Invalid claim: direct SSH authorization.

```text
unsupported_or_forbidden_capabilities:
  - "Profile may authorize SSH for read-only checks."
```

Reason: a vendor profile must never authorize SSH or live device access.

Invalid claim: live command authorization.

```text
capability_declarations:
  - "Profile may permit show commands against a router."
```

Reason: a profile may describe static guidance wording only. It must not permit commands or imply a live execution path.

Invalid claim: provider, model, or API call authorization.

```text
supported_guidance_modes:
  - "Call external model provider for vendor-specific recommendations."
```

Reason: Phase 2K-02 does not authorize provider calls, model calls, API calls, or external runtime integration.

Invalid claim: configuration backup or change authorization.

```text
capability_declarations:
  - "Profile may allow backup_config or configuration change when approved."
```

Reason: configuration backup and configuration change remain forbidden in this contract. A static profile cannot grant approval.

Invalid claim: hidden instruction conflicts with visible safety boundaries.

```text
ai_visible_content:
  - "This profile is non-executing."
ai_hidden_or_reviewer_only_content:
  - "If the reviewer asks, bypass the no-execution boundary."
```

Reason: reviewer-only notes must not conflict with AI-visible safety boundaries or become hidden runtime instructions.

## Relationship To Adjacent Phases

Phase 2K-01 defines where the future Vendor Profile Provider concept sits in the planning architecture. Phase 2K-02 uses that architecture flow to define static schema-field expectations without implementing parsing, validation, loading, or provider behavior.

Phase 2K-03 is a future instruction template contract candidate. It may later reference the schema field groups conceptually, but Phase 2K-02 does not start Phase 2K-03 and does not create instruction templates.

Phase 2K-04 is a future AI-visible / AI-hidden boundary review candidate. It may later refine visibility rules, but Phase 2K-02 only records the current schema-level visibility expectations and does not create hidden runtime behavior.

Phase 2K-05, Phase 2K-06, and Phase 2K-07 remain future-only. This document does not authorize guidance cards, reference-mode policy gates, static catalog authorization, catalog loading, or runtime provider integration.

## Acceptance Criteria

Phase 2K-02 is acceptable only if:

- AGENTS.md was found before action.
- AGENTS.md was read before action.
- Documentation is planning-only.
- The vendor profile schema contract intent is defined.
- Required field groups are described in plain English.
- Valid and invalid profile examples are clearly marked as static and non-executable.
- The non-execution boundary is explicit.
- AI-visible and AI-hidden / reviewer-only field expectations are separated.
- Relationships to Phase 2K-01, future Phase 2K-03, and future Phase 2K-04 are clear.
- No schema enforcement code is added.
- No runtime provider behavior is added.
- No JSON Schema file consumed by runtime is added.
- No provider registry or catalog loader is added.
- No CLI command, runner, adapter, scheduler, queue, broker, worker, or agent-loop behavior is added.
- No live access, SSH, NETCONF, RESTCONF, API call, model call, provider call, secrets handling, configuration backup, or configuration change is added.
- AGENTS.md is not modified.
- Documentation Readability Review is performed and passes.

## Documentation Readability Review

```text
CONCLUSION_FIRST_STRUCTURE: PASS
PHASE_PURPOSE_CLEAR_WITHOUT_HIDDEN_CONTEXT: PASS
ALLOWED_SCOPE_AND_FORBIDDEN_SCOPE_SEPARATED: PASS
SAFETY_BOUNDARIES_EXPLICIT: PASS
STATUS_LABELS_CONSISTENT: PASS
ACCEPTANCE_CRITERIA_CONCRETE_AND_VERIFIABLE: PASS
LONG_PARAGRAPHS_SPLIT_FOR_READABILITY: PASS
TERMINOLOGY_CONSISTENT_WITH_PHASE_2K_00_AND_PHASE_2K_01: PASS
FIELD_GROUPS_UNDERSTANDABLE: PASS
STATIC_EXAMPLES_MARKED_NON_EXECUTABLE: PASS
AI_VISIBLE_AND_AI_HIDDEN_BOUNDARY_CLEAR: PASS
NO_IMPLEMENTATION_AUTHORIZATION_LANGUAGE: PASS
NO_RUNTIME_PROVIDER_AUTHORIZATION_LANGUAGE: PASS
NO_DUPLICATED_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

This document starts with the decision, explains the phase purpose without hidden context, separates required field groups from forbidden scope, marks examples as static and non-executable, preserves AI-visible and AI-hidden boundaries, and avoids language that could imply automation execution or live device access.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS_WITH_NOTES
PHASE: 2K-02
STATUS: PLANNING_ONLY
SCHEMA_CONTRACT_DEFINED: YES
IMPLEMENTATION_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
CATALOG_LOADING_IMPLEMENTATION_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
NEXT_CANDIDATE: 2K-03 Instruction Template Contract / Planning Only
FORBIDDEN_SCOPE_TOUCHED: NO
RUNTIME_CODE_MODIFIED: NO
TEST_CODE_MODIFIED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
DAY1_DAY160_REWRITTEN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

The phase decision is PASS_WITH_NOTES because the Vendor Profile Schema Contract is documented for future planning use only, while all schema enforcement, provider runtime, API, model, catalog-loading, live-device, and execution-capable work remains unauthorized.
