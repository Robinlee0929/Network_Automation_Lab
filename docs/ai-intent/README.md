# AI Intent Reviewer Evidence

This folder holds reviewer-facing AI intent evidence docs that are report-only and mock/sample-only.

## Day98

- [Day98 Parser Classification Matrix](day98_parser_classification_matrix.md)

Day98 connects Day96 parser prototype samples and Day97 unsupported-output hardening into one traceability matrix. It does not add SSH, RouterOS execution, live-read behavior, dashboard actions, OpenAI API calls, voice runtime, or config loading.

## Day99

- [Day99 Parser Evidence Coverage / Sample Gap Audit](day99_parser_evidence_coverage_audit.md)

Day99 audits Day96-Day98 parser evidence coverage and preserves UNDER_COVERED sample gaps as Day100 review inputs. It does not add parser capability, adapter execution, broker execution, SSH, live access, dashboard actions, OpenAI API calls, voice runtime, or config loading.

## Day100

- [Day100 Parser Phase Gate Review / Readiness Decision](day100_parser_phase_gate_review.md)

Day100 grades Day96-Day99 parser evidence into ADVANCE_READY, REVIEW_ONLY, UNDER_COVERED, and BLOCKED decisions. Parser outputs remain review data only: broker_boundary_allowed, execution_allowed, adapter_invocation_allowed, ssh_allowed, and live_access_allowed stay false.
