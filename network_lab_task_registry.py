from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Tuple


TaskHandler = Callable[[], int]


CANONICAL_TASK_NAMES: Tuple[str, ...] = (
    "report-index",
    "portfolio-finalize",
    "demo-flow",
    "day4-baseline",
    "iperf3-performance",
    "day32-vrrp-precheck",
    "day33-vrrp-dry-run",
    "day34-vrrp-staged-plan",
    "day35-vrrp-failover-validation",
    "day39-vrrp-evidence-dashboard-integration",
    "day40-v0.2-demo-readiness-review",
    "day41-v0.2-release-packaging",
    "intent-mapping-prototype",
    "intent-safety-review",
    "intent-policy-matrix",
    "intent-workflow-demo",
    "offline-mock-runtime",
    "offline-mock-runtime-contract",
    "offline-mock-runtime-review",
    "mock-ai-decision-pipeline",
    "dry-run-plan-builder",
    "manual-review-approval-envelope",
    "runtime-audit-trail",
    "runtime-safety-gate",
    "runtime-safety-case",
    "readonly-task-contract",
    "readonly-execution-broker",
    "broker-review-queue",
    "reviewer-decision-audit-summary",
    "readonly-executor-readiness-gate",
    "readonly-executor-adapter-contract",
    "mock-adapter-evidence-binding",
    "controlled-runner-harness",
    "readonly-executor-phase-gate-review",
    "readonly-executor-adapter-design",
    "real-adapter-safety-boundary-spec",
    "real-adapter-implementation-plan",
    "real-adapter-safety-scaffold",
    "real-adapter-executable-guards",
    "guarded-fake-adapter-contract",
    "adapter-boundary-regression-matrix",
    "adapter-result-normalization",
    "readonly-output-parser-prototype",
    "parser-evidence-quality",
    "parser-classification-matrix",
    "parser-evidence-coverage-audit",
    "parser-phase-gate-review",
    "parser-evidence-closure-plan",
    "parser-fixture-expansion",
    "parser-evidence-matrix-gap-traceability",
    "parser-reviewer-acceptance-gate",
    "parser-acceptance-closure",
    "codex-agents-instruction-audit",
    "parser-reviewer-evidence-contract",
    "parser-contract-consumer-handoff",
    "parser-consumer-handoff-readiness-matrix",
    "parser-consumer-final-gate",
    "parser-consumer-release-package",
    "parser-consumer-release-review-intake",
    "parser-consumer-reviewer-triage-decision-log",
    "parser-consumer-reviewer-triage-evidence-traceability",
    "parser-consumer-reviewer-triage-closure-summary",
    "reviewer-deferred-action-register",
    "deferred-action-traceability-review",
    "deferred-action-review-sequence-runbook",
    "reviewer-evidence-intake-outcome-ledger",
    "safety-boundary-regression-matrix",
    "safety-invariant-helper-review",
    "thin-cli-regression-gate",
    "post-refactor-compatibility-evidence-pack",
    "ai-reviewer-summary-schema-contract",
    "ai-reviewer-summary-fixture-renderer",
    "ai-summary-prompt-contract",
    "ai-summary-redaction-and-no-secret-policy",
    "ai-summary-audit-trail-binding",
    "ai-summary-dashboard-card-integration",
    "disabled-ai-provider-interface-boundary",
    "disabled-ai-provider-adapter-contract",
    "ai-provider-disabled-by-default-safety-regression",
    "ai-reviewer-export-package-integration",
    "project-folder-organization-decision-gate",
    "project-folder-organization-dry-run-inventory-gate",
    "docs-only-move-dry-run-evidence-plan",
    "folder-move-compatibility-gate",
    "ai-assistance-review-demo-package",
    "ai-summary-to-dry-run-draft-display-contract",
    "dry-run-draft-safety-diff-viewer",
    "v0.4-ai-assistance-compatibility-review",
    "v0.4-ai-assistance-evidence-freeze-package",
    "v0.4-ai-assistance-non-advancement-gate",
    "ai-assistance-deferred-risk-register",
    "ai-assistance-demo-export-draft-display-consistency-audit",
    "ai-assistance-docs-registry-report-index-consistency-audit",
    "v04-ai-assistance-phase-gate-closure-review",
    "v04-ai-assistance-closure-evidence-index",
    "post-closure-reference-integrity-audit",
    "post-closure-evidence-baseline-lock-review",
    "v05-ai-assistance-reopen-rationale",
    "v05-ai-assistance-input-boundary-contract",
    "v05-ai-assistance-output-template-contract",
    "v05-ai-assistance-reviewer-only-fixture-renderer",
    "v05-ai-assistance-safety-regression-matrix",
    "v05-ai-assistance-phase-gate-review",
    "phase2a-readonly-job-runner-framework",
    "phase2a-03-dry-run-job-plan-gate",
    "phase2a-04-plan-evidence-ledger",
    "phase2a-05-dry-run-result-envelope-renderer",
    "phase2a-06-negative-regression-matrix",
    "phase2a-07-vrrp-dry-run-validation-pack",
    "phase2a-08-jobs-catalog-ui-readiness-planning-pack",
    "phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack",
    "phase2a-10-safe-boundary-implementation-readiness-artifact",
    "phase2a-11-phase-closure-final-readiness-review",
    "phase2b-00-authorization-scope-gate-review",
    "phase2b-00a-planning-only-owner-authorization-statement",
    "phase2b-01-planning-scope-design-only",
    "phase2b-02-safety-gate-design-planning-only",
    "phase2b-04-safety-artifact-crosswalk-gap-review",
    "phase2b-06-implementation-entry-gate-and-first-slice-readiness-review",
    "phase2b-07-first-slice-definition-pack",
    "phase2b-08-first-slice-implementation-authorization-gate-planning-only",
    "phase2b-09-first-slice-implementation-plan-pack-planning-only",
    "phase2b-10-day1-day160-reference-mapping-for-future-first-slice-planning-only",
    "phase2b-11-project-consolidation-and-implementation-entry-map-planning-only",
    "phase2b-12-future-implementation-authorization-review-planning-only",
    "phase2b-13-first-slice-final-selection-gate-planning-only",
    "phase2b-14-first-slice-implementation-kickoff-gate",
    "phase2c-01-local-static-job-first-slice",
    "phase2c-02-post-first-slice-acceptance-review",
    "phase2c-03-next-slice-decision-gate-authorization-review",
    "phase2c-04-next-slice-candidate-inventory",
    "phase2c-05-next-slice-safety-delta-review",
    "wireguard-runner",
)


TASK_ALIASES: Dict[str, str] = {
    "broker-review-queue-decision-state": "broker-review-queue",
    "deferred-evidence-collection-log": "reviewer-evidence-intake-outcome-ledger",
}


class UnknownTaskError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedTask:
    requested_name: str
    canonical_name: str
    handler: TaskHandler

    @property
    def is_alias(self) -> bool:
        return self.requested_name != self.canonical_name


def get_cli_task_choices() -> Tuple[str, ...]:
    choices = list(CANONICAL_TASK_NAMES)
    for alias_name in TASK_ALIASES:
        canonical_name = TASK_ALIASES[alias_name]
        try:
            insert_at = choices.index(canonical_name) + 1
        except ValueError:
            insert_at = len(choices)
        choices.insert(insert_at, alias_name)
    return tuple(choices)


def resolve_task_name(task_name: str) -> str:
    if task_name in TASK_ALIASES:
        return TASK_ALIASES[task_name]
    if task_name in CANONICAL_TASK_NAMES:
        return task_name
    raise UnknownTaskError(f"Unknown task: {task_name}")


def resolve_task_handler(task_name: str, handlers: Mapping[str, TaskHandler]) -> ResolvedTask:
    canonical_name = resolve_task_name(task_name)
    handler = handlers.get(canonical_name)
    if handler is None:
        raise UnknownTaskError(f"No handler registered for task: {canonical_name}")
    return ResolvedTask(
        requested_name=task_name,
        canonical_name=canonical_name,
        handler=handler,
    )
