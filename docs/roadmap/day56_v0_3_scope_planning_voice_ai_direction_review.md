# Day56 - v0.3 Scope Planning / Voice + AI Direction Review

## Purpose

Day56 starts the v0.3 planning line after the Day55 public repository readiness review.

The goal is to define conservative scope, safety boundaries, Voice/AI direction, and a future demo flow before any implementation begins. Day56 is planning-only: it does not add Voice Control, does not add an AI Agent, does not connect to an AI API, does not run live network tests, and does not modify runner, dashboard route, or device runtime behavior.

## Goal

Define the first v0.3 planning baseline:

- Clarify what v0.3 should and should not attempt.
- Keep Voice as a future interface layer, not an active control surface.
- Plan AI as intent mapping, explanation, evidence review, and dry-run planning only.
- Preserve the existing runner/runtime behavior.
- Make safety boundaries explicit before any future AI or Voice feature work.
- Define a future demo flow without implementing it.

## Non-Goals

Day56 does not:

- Implement Voice Control.
- Implement speech recognition, wake words, audio capture, transcription, or text-to-speech.
- Implement an AI Agent.
- Connect to OpenAI, local LLMs, RAG, vector stores, or any external AI API.
- Let AI execute shell commands.
- Let AI modify routers, switches, firewalls, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration.
- Change `network_lab.py`, runner task execution behavior, runner safety levels, or task catalog runtime semantics.
- Change dashboard route logic or add new dashboard routes.
- Run live network tests, SSH, iperf3, failover, or guarded-live workflows.
- Modify `config.json` or require local lab secrets.
- Create a release tag.

## v0.3 Conservative Scope

| Area | Day56 position | Allowed future planning direction |
| --- | --- | --- |
| Voice | Future interface layer only | Map spoken user intent to reviewed text actions after safety controls exist. |
| AI | Intent mapping only | Classify requests into report-only, read-only, dry-run, guarded-live, or blocked categories. |
| Runner | No runtime changes | Future AI/Voice work must call existing safe tasks only through explicit allowlists and human review. |
| Dashboard | No route changes | Future UI may show reviewed intent, safety classification, and proposed next steps after a separate implementation day. |
| Device workflows | No behavior changes | Future live behavior remains out of scope until dry-run evidence, safety metadata, approval, and rollback thinking are complete. |
| Demo | Flow definition only | Show a future conversational flow as documentation, not as a working assistant. |

## Safety Boundary

AI and Voice must not become implicit execution paths.

Required future controls before implementation:

- AI cannot directly execute arbitrary shell commands.
- AI cannot directly open SSH sessions.
- AI cannot directly modify router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP, interface, route, or device configuration.
- AI output must be treated as a proposal until a human reviews it.
- Any executable action must map to a known task id, safety level, device scope, and allowlist.
- Live or guarded-live workflows require dry-run preview, explicit human approval, audit log, and rollback notes.
- Portfolio/offline demo mode must remain no-live-device, no-SSH, and no-secret by default.
- Unknown, ambiguous, or high-risk intent must resolve to BLOCKED, not to execution.

## Intent Mapping Direction

The first AI planning layer should classify intent before considering any action.

| Example user intent | Planned classification | Expected behavior |
| --- | --- | --- |
| "Show me the latest reports" | report-only | Suggest report-index or dashboard report viewer. |
| "Explain this WARN" | evidence review | Summarize report status and cite optional missing-report rules. |
| "Check if VRRP is ready" | read-only or dry-run candidate | Point to existing VRRP planning/precheck evidence and require safety review. |
| "Apply the router config" | guarded-live or blocked | Block in portfolio/offline mode; require separate guarded workflow design. |
| "Fix the network automatically" | blocked | Refuse automatic device mutation and ask for scoped, reviewed intent. |
| "Run any command you need" | blocked | Arbitrary shell or SSH execution is not allowed. |

## Future Demo Flow Definition

Day56 only defines the future flow:

1. Reviewer asks a natural-language question.
2. Assistant converts the request into a structured intent proposal.
3. Proposal shows safety level, device scope, allowed evidence sources, and blocked actions.
4. Human reviewer approves only report-only or read-only paths during a portfolio demo.
5. System displays existing report evidence or dry-run planning notes.
6. Any live or configuration-changing request remains blocked in the public/offline demo.

This flow is documentation only. No voice UI, AI API, command execution, or dashboard implementation is added on Day56.

## Roadmap Gates

Future v0.3 work should proceed in this order:

1. Intent taxonomy and safety classification documentation.
2. Offline fixtures for report explanation and WARN interpretation.
3. Human-readable reviewed intent object format.
4. Non-executing dashboard mock or static review page.
5. Optional local-only summarization experiment using committed fixture reports.
6. Allowlist integration proposal, still non-executing.
7. Separate implementation review before any runtime changes.

Voice remains after these gates. It should wrap the intent layer only after text intent mapping is stable and safe.

## Day56 Completion Check

| Check | Standard |
| --- | --- |
| README | Shows Day56 as the v0.3 planning starting point. |
| Day56 doc | Includes clear goal, non-goals, safety boundary, intent mapping direction, and roadmap. |
| Runtime | No runner, dashboard route, device logic, SSH, live test, or task execution behavior changes. |
| Tests | `python -m pytest` passes. |
| report-index | WARN is acceptable only when `fail=0` and missing items are optional generated local reports. |
| Git | Branch should be clean after commit and ready for PR. |

## Report-Index WARN Rule

`python network_lab.py --task report-index` is report-only. It reads local metadata and generated report paths; it does not connect to devices.

WARN is acceptable for Day56 only when:

- `fail=0`.
- Missing items are optional generated local reports, usually under ignored local `reports/` paths.
- No required evidence failed.
- No runtime error caused the warning.

WARN is not acceptable if `fail` is greater than zero, if a required report fails, or if the warning is caused by an unrelated runtime failure.

## Validation Commands

Commands to run for Day56 validation:

```powershell
python -m pytest
python network_lab.py --task report-index
```

Observed Day56 results:

- `python -m pytest`: `488 passed, 1 warning in 2.74s`.
- `python network_lab.py --task report-index`: overall `WARN`, counts `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`

The `report-index` WARN is acceptable for Day56 because `fail=0` and the missing items are optional generated local reports.

Expected runtime-change review:

```text
Only README.md and docs/roadmap/day56_v0_3_scope_planning_voice_ai_direction_review.md should change.
No runner, dashboard route, device workflow, config, or task catalog file should change.
```

## Final Day56 Status

Day56 status: READY WITH NOTES.

Notes are limited to planning-only scope and optional local generated report availability. Day56 starts v0.3 planning conservatively but does not implement Voice, AI, runner changes, dashboard route changes, live tests, SSH, or device configuration behavior.
