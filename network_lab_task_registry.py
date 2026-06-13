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
