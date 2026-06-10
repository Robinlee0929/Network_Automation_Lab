# Day98 Parser Classification Matrix

Day98 builds a reviewer-facing traceability matrix across Day96 and Day97 parser evidence.

The matrix proves this evidence chain:

```text
input sample -> parser classification -> parsed fields / unsupported reason -> reviewer action -> safety invariant
```

## Scope

Day98 is report-only and static-sample-only. It does not parse live device output, connect to routers, read `config.json`, execute RouterOS commands, call OpenAI APIs, use a voice runtime, or add dashboard actions.

Inputs are static sample strings representing Day96 read-only parser prototype outcomes and Day97 unsupported-output hardening cases.

## Classification Categories

The matrix includes these classifications:

- `parsed_supported`
- `parsed_partial`
- `unsupported_format`
- `unsupported_command_family`
- `empty_output`
- `ambiguous_output`
- `parser_error_guarded`

Supported parsed rows may use `unsupported_reason = null`. Every partial, unsupported, empty, ambiguous, or guarded-error row must include a non-empty `unsupported_reason`.

## Reviewer Actions

Each classification maps deterministically to a reviewer action:

- `parsed_supported` -> `review_parsed_fields`
- `parsed_partial` -> `review_missing_fields`
- `unsupported_format` -> `reject_and_attach_sample`
- `unsupported_command_family` -> `reject_out_of_scope`
- `empty_output` -> `request_new_sample`
- `ambiguous_output` -> `manual_review_required`
- `parser_error_guarded` -> `reject_until_parser_fixed`

## Safety Invariants

Every matrix row sets `executable_allowed` to `false`.

Rows also bind to one of these safety invariants:

- `parser_output_is_not_executable`
- `unsupported_output_is_blocked`
- `unknown_output_requires_review`
- `parser_error_fails_closed`
- `reviewer_action_required_before_any_future_runtime_use`

Day98 keeps live-read, SSH, RouterOS execution, command execution, device contact, approval unlocks, dashboard actions, and external runtime state disabled.

## Deliverables

- `intent_parser_classification_matrix.py`
- Runner task `parser-classification-matrix`
- JSON report at `reports/ai/day98_parser_classification_matrix.json`
- HTML report at `reports/ai/day98_parser_classification_matrix.html`
- Reviewer documentation at `docs/ai-intent/day98_parser_classification_matrix.md`

## Run

```text
python network_lab.py --task parser-classification-matrix
python network_lab.py --report-index
```

Expected completion is `PASS / TRACEABILITY_READY` with `executable_allowed_count = 0`, complete unsupported reasons, and no external runtime dependencies.
