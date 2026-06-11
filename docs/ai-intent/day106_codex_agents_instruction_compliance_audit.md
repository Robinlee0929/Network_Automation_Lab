# Day106 Codex AGENTS.md Instruction Compliance Audit

Day106 audits the repository-level `AGENTS.md` as a durable Codex instruction contract without changing that file.

The runner task is:

- `python network_lab.py --task codex-agents-instruction-audit`

Report outputs:

- `reports/ai/day106_codex_agents_instruction_compliance_audit.json`
- `reports/ai/day106_codex_agents_instruction_compliance_audit.html`

## Scope

Day106 is `REPORT_ONLY`.

It reads local `AGENTS.md` and produces reviewer-facing evidence only. It does not connect to devices, use SSH, execute real network-device commands, mutate router/switch/firewall/VRRP/NAT/interface configuration, call OpenAI APIs, use voice runtime, load private credentials, push, merge, tag, deploy, or publish.

During this AGENTS.md governance audit:

- Codex may read `AGENTS.md`.
- Codex may audit `AGENTS.md`.
- Codex may report findings and proposed wording.
- Codex must not modify `AGENTS.md`.
- Codex must not stage `AGENTS.md`.
- Codex must not commit `AGENTS.md`.

If `AGENTS.md` needs improvement, Day106 records proposed wording in the JSON/HTML report and documentation only.

## Audit Questions

Day106 verifies that `AGENTS.md`:

- exists at the repository root
- includes practical repository guidance
- includes validation commands
- preserves safety boundaries and do-not rules
- avoids secrets, credentials, private memory, and live-device instructions
- keeps review-only behavior as the default unless a future approved safety gate explicitly changes it
- defines done criteria for Codex work
- avoids vague or dangerous automation instructions
- avoids push, merge, tag, deployment, or publication without explicit user approval
- produces reviewer-facing evidence for future Codex sessions
- preserves the governance rule that `AGENTS.md` is input to the audit, not an edited or committed output

## Required Result

The accepted result is:

- `overall_status`: `PASS`
- `audit_type`: `REPORT_ONLY`
- `final_recommendation`: `AGENTS_INSTRUCTION_CONTRACT_ACCEPTABLE_FOR_REVIEW_ONLY_CODEX_WORK`
- `live_execution_allowed`: `false`
- `ssh_allowed`: `false`
- `device_connection_allowed`: `false`
- `config_mutation_allowed`: `false`
- `openai_api_allowed`: `false`
- `voice_runtime_allowed`: `false`
- `push_allowed_without_user_approval`: `false`
- `merge_allowed_without_user_approval`: `false`
- `tag_allowed_without_user_approval`: `false`
- `codex_must_not_modify_agents_md`: `true`
- `codex_must_not_stage_agents_md`: `true`
- `codex_must_not_commit_agents_md`: `true`

## Phase Exit

Day106 exits with `AGENTS.md` accepted for review-only Codex work when all required checks pass and no risky live execution, secret exposure, publication, or safety-unlock language is detected.

Any future live-capable workflow still requires a separate task, explicit user approval, a separate safety gate, and tests proving rejected scenarios do not reach execution paths.
