# Phase 2K-03 - Instruction Template Contract / Planning Only

Status: READY_FOR_REVIEW

Decision summary: Phase 2K-03 defines a static planning contract for future instruction templates used by the Platform Guidance Provider concept. It is planning-only documentation and does not implement a runtime prompt, instruction renderer, provider runtime, model call, API call, schema enforcement, runner, adapter, scheduler, queue, worker, agent loop, or device execution path.

## Status

```text
PHASE: 2K-03
TASK_NAME: Instruction Template Contract / Planning Only
TASK_MODE: PLANNING_ONLY_DOCUMENTATION
STATUS: PLANNING_ONLY
AUTHORIZATION_LEVEL: DOCUMENTATION_ONLY_CONTRACT
UPSTREAM_DEPENDENCY: 2K-02 Vendor Profile Schema Contract / Planning Only
DOWNSTREAM_DEPENDENCY: 2K-04 AI-visible / AI-hidden Boundary Review / Planning Only
PLANNING_ONLY_DOCUMENTATION: YES
IMPLEMENTATION_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
INSTRUCTION_RENDERER_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
LIVE_ACCESS_AUTHORIZED: NO
```

This artifact is documentation-only, planning-only, local-only, deterministic, report-only, and non-executing. It defines reviewer-facing expectations for a future instruction template contract. It does not create runtime prompt behavior.

## Purpose

Phase 2K-03 defines how a future instruction template could describe guidance or reference-style outputs that rely on structured vendor profile information. The contract gives reviewers a stable vocabulary for template identity, inputs, safety notices, output types, evidence references, and review notes.

This contract is not a runtime prompt implementation. It does not render instructions, expand placeholders, call a provider, invoke a model, load a vendor profile, validate a schema, or execute any network automation behavior.

## Non-goals

This task does not create:

- provider runtime
- model or API integration
- instruction renderer
- prompt executor
- device execution behavior
- enforcement code
- UI card design
- AI-visible / AI-hidden final boundary decision

It also does not create SSH, NETCONF, RESTCONF, device inventory, credential handling, command allowlists, runner behavior, adapter behavior, scheduler behavior, queue or worker behavior, agent-loop behavior, configuration backup, or configuration change behavior.

## Relationship To 2K-02

Phase 2K-02 defines the Vendor Profile Schema Contract. It describes static field-group expectations for future vendor profile documents, including vendor identity, supported guidance modes, capability declarations, forbidden capabilities, safety boundaries, and visibility notes.

Phase 2K-03 defines how future instruction templates may refer to structured vendor profile information. A template may reference vendor profile concepts such as vendor identity, supported guidance modes, capability labels, safety boundaries, and evidence notes, but this phase does not add new vendor profile schema fields and does not implement schema enforcement.

The relationship is reference-only: Phase 2K-02 defines the future profile vocabulary, while Phase 2K-03 defines a static template contract that may later point at that vocabulary after separate authorization.

## Instruction Template Contract

The future instruction template contract should require these template-level fields in documentation form only:

- `template_id`: stable, safe identifier for the future template.
- `template_version`: planning contract version used by the template.
- `template_name`: human-readable name for reviewers.
- `template_mode`: guidance mode label such as review guidance, reference guidance, or approval-readiness guidance.
- `supported_vendor_profile_refs`: allowed references to future vendor profile field groups or safe labels.
- `required_inputs`: documentation-only list of inputs a reviewer would expect before a template could be considered complete.
- `optional_inputs`: documentation-only list of supplementary context that may improve reviewer clarity.
- `safety_boundary_notice`: visible statement that the template is non-executing and does not authorize live access.
- `allowed_output_types`: output categories the future template may describe.
- `forbidden_output_types`: output categories the future template must not produce.
- `approval_dependency`: explicit note that any implementation or runtime use requires a separate future authorization gate.
- `evidence_reference_policy`: expectations for citing static documents, reports, or reviewer evidence without requiring runtime access.
- `result_format`: expected static shape of the output, such as checklist, review note, or planning summary.
- `review_notes`: reviewer-facing notes about limitations, assumptions, and unresolved future-phase questions.

These fields are planning vocabulary only. They must not be interpreted as a schema file, executable configuration, hidden prompt, runtime template loader, model instruction, or approval to call any provider.

## Required Template Sections

A future instruction template should contain these standard sections before it is considered complete as a static planning artifact:

- Context
- Vendor profile references
- User intent boundary
- Allowed guidance scope
- Forbidden actions
- Safety and authorization reminder
- Output contract
- Evidence / traceability references
- Review checklist

Each section must keep the dry-run, mock-only, report-only, and non-executing boundary visible to a reviewer. The template may describe safe guidance expectations, but it must not include device commands intended for execution or operational instructions for live systems.

## Allowed Output Types

Planning-only examples of allowed output types include:

- human-readable guidance
- checklist
- review note
- planning summary
- approval-readiness explanation
- reference-only vendor behavior explanation

Allowed output types must stay static and reviewer-facing. They may explain concepts, clarify approval status, or summarize safe reference behavior, but they must not become runtime instructions.

## Forbidden Output Types

The instruction template contract must forbid:

- device commands intended for execution
- SSH, NETCONF, or RESTCONF instructions for live systems
- configuration backup instructions
- configuration change instructions
- secrets or credential handling
- provider, API, or model invocation instructions
- runner, adapter, scheduler, queue, broker, or worker instructions
- instructions for an agent loop or autonomous execution path
- anything that bypasses authorization gates

Forbidden outputs must remain blocked even if the template references a vendor profile. A future profile reference cannot authorize live access, execution, provider calls, secrets, backup, configuration change, or runtime behavior.

## Placeholder Policy

Future instruction templates may define placeholder categories in documentation form only. Allowed placeholder categories include:

- vendor profile reference
- capability label
- safety boundary text
- evidence reference
- approval status
- output format expectation

Placeholder expansion is not implemented in this task. This phase does not create a placeholder resolver, instruction renderer, prompt renderer, runtime injection mechanism, schema validator, catalog loader, provider client, model client, or execution path.

## Boundary With Future Phases

Phase 2K-04 will handle AI-visible / AI-hidden boundary review. Phase 2K-03 does not pre-decide that boundary and does not create hidden runtime instructions.

Phase 2K-05 will handle static guidance mode instruction card design. Phase 2K-03 does not design UI cards or authorize a guidance-card runtime.

Phase 2K-06 will handle reference mode policy gate planning. Phase 2K-03 does not define or implement a policy gate.

Phase 2K-07 will handle static vendor profile catalog authorization gate. Phase 2K-03 does not create a catalog, loader, provider registry, or catalog authorization workflow.

Those phases remain future-only and require separate user authorization before work starts.

## Acceptance Checklist

Phase 2K-03 is acceptable only if:

- Contract is documentation-only.
- No runtime behavior is added.
- No provider, model, or API calls are added.
- No runner, adapter, scheduler, queue, broker, or worker is added.
- No live device behavior is added.
- No schema enforcement code is added.
- No instruction rendering engine is added.
- No placeholder expansion behavior is added.
- Phase 2K-04 through Phase 2K-07 remain future tasks.
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
TERMINOLOGY_CONSISTENT_WITH_PHASE_2K_01_AND_PHASE_2K_02: PASS
TEMPLATE_FIELDS_UNDERSTANDABLE: PASS
PLACEHOLDER_POLICY_MARKED_NON_EXECUTING: PASS
FUTURE_PHASE_BOUNDARIES_CLEAR: PASS
NO_IMPLEMENTATION_AUTHORIZATION_LANGUAGE: PASS
NO_RUNTIME_PROVIDER_AUTHORIZATION_LANGUAGE: PASS
NO_DUPLICATED_SAFETY_MATRIX: PASS
FINAL_READABILITY_RESULT: PASS
```

This document starts with the decision, explains the phase purpose without hidden context, separates allowed template planning scope from forbidden output types, keeps placeholder expansion non-implemented, preserves future phase boundaries, and avoids language that could imply automation execution or live device access.

## Final Decision

```text
FINAL_PHASE_DECISION: PASS_WITH_NOTES
PHASE: 2K-03
STATUS: PLANNING_ONLY
INSTRUCTION_TEMPLATE_CONTRACT_DEFINED: YES
IMPLEMENTATION_AUTHORIZED: NO
PROVIDER_RUNTIME_AUTHORIZED: NO
API_OR_MODEL_CALL_AUTHORIZED: NO
INSTRUCTION_RENDERER_AUTHORIZED: NO
SCHEMA_ENFORCEMENT_CODE_AUTHORIZED: NO
PLACEHOLDER_EXPANSION_IMPLEMENTED: NO
LIVE_ACCESS_AUTHORIZED: NO
NEXT_CANDIDATE: 2K-04 AI-visible / AI-hidden Boundary Review / Planning Only
FORBIDDEN_SCOPE_TOUCHED: NO
RUNTIME_CODE_MODIFIED: NO
TEST_CODE_MODIFIED: NO
SECOND_SAFETY_MATRIX_CREATED: NO
DAY1_DAY160_REWRITTEN: NO
NEXT_PHASE_STARTED: NO
EXTRA_SLICE_SELECTED_OR_IMPLEMENTED: NO
```

The phase decision is PASS_WITH_NOTES because the Instruction Template Contract is documented for future planning use only, while runtime prompts, instruction rendering, placeholder expansion, provider runtime, API calls, model calls, schema enforcement, live-device access, and execution-capable work remain unauthorized.
