# Day72 Controlled AI Runtime Input Contract Validator

Day72 adds a deterministic input contract validator for future controlled AI
runtime requests. Its job is to accept a structured intent payload, validate the
payload shape and safety fields, and return reviewer-readable validation
results before any future runtime decision path can be considered.

The validator is input validation only. It does not call an AI model, connect to
OpenAI, listen for voice input, open SSH, access devices, run commands, execute
mapped tasks, read `config.json`, call APIs, or change router, switch, firewall,
VPN, VRRP, or network configuration.

## Relationship To Day71

Day71 defined the controlled AI runtime prototype entry design as a static
contract. Day72 adds the next safety layer by validating candidate input
payloads against that contract. This still stops before runtime decision-making:
the validator only says whether a payload is valid, blocked, reviewer-required,
or malformed.

## Required Input Schema

The payload must be a dictionary with these fields:

| Field | Type | Requirement |
| --- | --- | --- |
| `user_intent_text` | `str` | Non-empty reviewer intent text. |
| `requested_operation_type` | `str` | Declared safe operation type. |
| `target_scope` | `str` | Declared safe target scope. |
| `safety_level` | `str` | Declared safety classification. |
| `evidence_required` | `bool` | Whether reviewer evidence is required. |
| `reviewer_required` | `bool` | Whether human review is required. |
| `execution_allowed` | `bool` | Must always be `False`. |

## Allowed Values

Allowed `requested_operation_type` values:

- `documentation_only`
- `report_only`
- `dry_run_review`
- `reviewer_summary`

Allowed `target_scope` values:

- `lab_summary`
- `ai_intent_reviewer`
- `offline_mock_runtime`
- `documentation`
- `portfolio_evidence`

Allowed `safety_level` values:

- `documentation_only`
- `report_only`
- `review_required`
- `blocked`

`safety_level=blocked` is an allowed label, but it produces a blocked result and
requires reviewer triage.

## Blocked Unsafe Examples

These intent examples are blocked with `risk_level=high`,
`valid=false`, `blocked=true`, and `execution_allowed=false`:

- Run SSH command on router
- Apply firewall rule
- Change VRRP priority
- Reboot device
- Connect to OpenAI API
- Start voice command mode
- Execute mapped task
- Use `config.json` to connect device
- Run subprocess command
- Push configuration to switch

Blocked text patterns include SSH, firewall rule changes, VRRP priority changes,
device reboot, OpenAI/API connection, voice command mode, mapped task execution,
`config.json`, device connection, subprocess, socket, requests, Paramiko,
Netmiko, API keys, secrets, router/switch configuration, and live execution.

## Output Fields

The validator always returns this shape:

| Field | Meaning |
| --- | --- |
| `valid` | Whether the payload satisfies the Day72 contract and is not blocked. |
| `risk_level` | `low`, `medium`, or `high`. Blocked results are `high`. |
| `blocked` | Whether the payload is blocked before any runtime decision path. |
| `blocked_reason` | Reviewer-readable reason for a blocked or invalid result. |
| `reviewer_required` | Whether human review is required. |
| `execution_allowed` | Always `False`. |
| `next_safe_step` | Safe reviewer/report-only next step. |
| `validation_errors` | List of contract or safety validation errors. |

## Why Execution Remains Disabled

Day72 is a contract validator, not a runtime. Even safe report-only payloads
return `execution_allowed=false` because a valid payload only proves that the
input shape and declared safety fields are acceptable for review. It does not
grant permission to call APIs, invoke models, run commands, open device sessions,
or execute mapped tasks.

## Safety Boundary

Day72 does not add:

- OpenAI API usage or model invocation
- Voice integration
- SSH or device access
- Live execution
- Mapped task execution
- Router, switch, firewall, VPN, or VRRP configuration changes
- Dashboard forms, POST routes, or action endpoints
- API key, secret, or `config.json` handling
- Subprocess, socket, requests, or HTTP client usage
- Release tag creation

## Future Path Toward Day73

Day73 can build a mock AI decision pipeline only after this Day72 input
validator stays deterministic and blocked-by-default for unsafe requests. The
next safe step is a mock pipeline that consumes validated payloads and produces
reviewer-facing decisions without model calls, device access, command execution,
or dashboard action surfaces.
