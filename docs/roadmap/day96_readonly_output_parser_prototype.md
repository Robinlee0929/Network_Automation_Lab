# Day96 Read-only Output Parser Prototype

## Scope

Day96 adds a parser-only prototype for Day95 normalized fake adapter result data. It extracts only `result_payload.simulated_output` from fake normalized results and writes JSON/HTML evidence reports.

## Non-goals

- No RouterOS connection
- No SSH
- No live-read
- No `config.json`
- No credentials, hostnames, IP targets, passwords, or keys
- No real device command parser
- No adapter fallback
- No runner live path
- No dashboard execution trigger

## Deliverables

- `intent_readonly_output_parser_prototype.py`
- Runner task `readonly-output-parser-prototype`
- JSON report at `reports/lab-summary/day96_readonly_output_parser_prototype.json`
- HTML report at `reports/lab-summary/day96_readonly_output_parser_prototype.html`
- AI documentation at `docs/ai/readonly_output_parser_prototype.md`
- Roadmap documentation at `docs/roadmap/day96_readonly_output_parser_prototype.md`
- Pytest coverage for parser status, safety metadata, runner behavior, report files, and forbidden live-access imports
- Report-index visibility as read-only local evidence

## Validation Checklist

- Valid Day95 normalized fake adapter results parse into structured records.
- Missing simulated output returns `REVIEW_NEEDED`.
- Unsupported simulated output type returns `UNSUPPORTED`.
- Malformed input does not trigger live fallback.
- `live_read_enabled`, `ssh_enabled`, `routeros_enabled`, and `device_access_enabled` remain `false`.
- Runner returns `PASS / PARSER_PROTOTYPE_READY`.
- Reports are generated.
- Report index can find the generated Day96 reports without failures.

## Correct Route

Day95 normalized fake adapter result -> Day96 parser-only prototype -> structured parsed records plus safety evidence report.

The wrong route remains prohibited: RouterOS / SSH / live command -> Day96 parser.

