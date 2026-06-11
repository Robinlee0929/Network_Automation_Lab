# Day106 Codex AGENTS.md Instruction Compliance Audit

Day106 validates the repository-level `AGENTS.md` before treating it as the durable instruction layer for future Codex work. `AGENTS.md` is audit input, not an output to be modified, staged, or committed by this governance task.

## Required Locks

Day106 must remain:

- `REPORT_ONLY`
- deterministic
- offline
- reviewer-facing
- local-file-only
- no-execution
- no `AGENTS.md` modification
- no `AGENTS.md` staging
- no `AGENTS.md` commit

Day106 must not add platform features, parser behavior, adapter execution, broker handoff, live-device access, SSH, external API calls, OpenAI runtime, voice runtime, dashboard action surfaces, configuration mutation, deployment, tag creation, merge, or push.

Codex may read `AGENTS.md`, audit `AGENTS.md`, and report findings with proposed wording. Codex must not modify, stage, or commit `AGENTS.md` during this governance audit.

## Completion Criteria

- `AGENTS.md` exists at the repository root.
- The audit checks repository guidance, validation guidance, safety boundaries, secrets exposure, done criteria, and unauthorized publication language.
- Proposed `AGENTS.md` improvements are recorded in reports or docs only.
- The JSON and HTML reports are generated under `reports/ai/`.
- The runner task `codex-agents-instruction-audit` returns PASS when the instruction contract is acceptable.
- Report-index visibility includes Day106.
- Tests prove the runner does not call subprocess execution paths or load live profile/config data.

## Phase Exit

Day106 exits with `AGENTS_INSTRUCTION_CONTRACT_ACCEPTABLE_FOR_REVIEW_ONLY_CODEX_WORK` only when `AGENTS.md` is safe, practical, and explicit enough for future review-only Codex sessions, while `AGENTS.md` remains unstaged and uncommitted by the audit.

This does not unlock live execution. Any future live-capable work requires a separate branch, separate task, explicit user approval, dedicated safety gate, and negative tests proving rejected scenarios do not reach execution paths.
