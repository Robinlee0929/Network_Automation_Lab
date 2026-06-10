# Day97 Parser Evidence Quality

Day97 hardens the Day96 read-only output parser prototype by testing parser evidence quality under unsupported, missing, malformed, ambiguous, empty, and degraded output cases.

Day97 is not a new device capability. It does not add live-read, SSH, RouterOS execution, raw command execution, mapped task execution, write capability, approval unlocks, OpenAI API usage, or voice runtime behavior.

## Why Day97 Exists After Day96

Day96 proved that normalized fake adapter output can be parsed without live fallback. Day97 asks a stricter reviewer question: when output is bad or unsupported, does the parser produce clear evidence without pretending the device was contacted?

The answer should be yes. Unsupported parser output is a parser classification, not proof that a command executed and failed.

## Unsupported Output

Unsupported output means the parser cannot safely convert a local fake fixture into trusted structured evidence. Examples include:

- Empty or whitespace-only output
- Unsupported command families
- Unknown adapter sources
- Malformed normalized adapter result shapes
- Missing `raw_output` or command family context
- Header-only output with no data rows
- Mixed supported and unsupported sections
- Supported-looking output with missing required field values
- Unexpected encoding-like characters
- Repeated duplicate evidence lines
- Contradictory parser hints

These cases produce reviewer-facing statuses such as `UNSUPPORTED_OUTPUT`, `INCOMPLETE_OUTPUT`, `MALFORMED_INPUT`, `EMPTY_OUTPUT`, or `AMBIGUOUS_OUTPUT`.

## Evidence Quality

Evidence quality is judged by whether the parser can explain what happened without using live recovery:

- `HIGH`: evidence is parseable and complete.
- `MEDIUM`: evidence is partially parseable or degraded but still reviewable.
- `LOW`: evidence is present but not safe to trust without fixture repair.
- `NOT_APPLICABLE`: no raw output evidence exists.

Each case includes `unsupported_reason` and `reviewer_action` so a reviewer can decide whether to fix the fixture, split mixed output, reject provenance, or keep the result unsupported.

## Safety Boundary

Every Day97 case is a local static fake parser case. Every case sets these flags to `false`:

- `live_read_allowed`
- `ssh_allowed`
- `write_allowed`
- `command_execution_allowed`
- `raw_command_allowed`
- `device_contact_allowed`
- `approval_unlock_supported`
- `mapped_task_execution_allowed`

Day97 also keeps `no_config_json_read`, `no_openai_api`, `no_ai_sdk_runtime`, `no_voice_runtime`, and `no_dashboard_post_route` true.

## Run

```text
python network_lab.py --task parser-evidence-quality
```

Expected completion is `PASS / HARDENED` with `unsafe_flag_count = 0` and `failed_execution_count = 0`.
