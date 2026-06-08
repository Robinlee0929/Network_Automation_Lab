"""Day71 static controlled entry design for a future AI runtime.

This module defines reviewer-facing contract data only. It does not execute,
delegate, connect, read config, or start any runtime behavior.
"""

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ContractField:
    name: str
    requirement: str


@dataclass(frozen=True)
class SafetyGate:
    order: int
    name: str
    day71_status: str


@dataclass(frozen=True)
class EvidenceReference:
    day: str
    artifact: str
    reviewer_value: str


INPUT_CONTRACT: List[ContractField] = [
    ContractField("user_intent_text", "Natural-language text to classify for review."),
    ContractField("requested_operation_type", "Declared request type such as report, dry-run, or live-capable."),
    ContractField("target_scope", "Declared local report, lab area, or blocked target scope."),
    ContractField("safety_level", "Reviewer-visible safety label before any future action is considered."),
    ContractField("evidence_required", "Evidence paths or proof required before the next step."),
    ContractField("reviewer_required", "Human review requirement for the proposed operation."),
    ContractField("execution_allowed", "Always false for Day71."),
]

OUTPUT_CONTRACT: List[ContractField] = [
    ContractField("normalized_intent", "Reviewer-readable normalized intent label."),
    ContractField("mapped_category", "Mapped policy category, not a delegated task."),
    ContractField("risk_level", "Reviewer-visible risk level."),
    ContractField("required_evidence", "Evidence required before approval can be considered."),
    ContractField("reviewer_decision_required", "Whether a human decision is required."),
    ContractField("blocked_reason", "Reason the request remains blocked when applicable."),
    ContractField("next_safe_step", "Report-only or review-only next step."),
]

SAFETY_GATE_SEQUENCE: List[SafetyGate] = [
    SafetyGate(1, "intent normalization", "DESIGNED_ONLY"),
    SafetyGate(2, "task classification", "DESIGNED_ONLY"),
    SafetyGate(3, "blocked-action screening", "DESIGNED_ONLY"),
    SafetyGate(4, "evidence requirement mapping", "DESIGNED_ONLY"),
    SafetyGate(5, "offline mock validation", "DESIGNED_ONLY"),
    SafetyGate(6, "reviewer approval", "DESIGNED_ONLY"),
    SafetyGate(7, "dry-run report generation", "DESIGNED_ONLY"),
    SafetyGate(8, "explicit human confirmation", "DESIGNED_ONLY"),
    SafetyGate(9, "future controlled execution consideration", "STOPPED_BEFORE_EXECUTION"),
]

REVIEWER_EVIDENCE_MAP: List[EvidenceReference] = [
    EvidenceReference("Day57", "intent mapping prototype", "Shows static text-to-task proposal boundaries."),
    EvidenceReference("Day58", "safety review gate", "Blocks live-capable and unknown intents by default."),
    EvidenceReference("Day59", "policy matrix", "Explains allowed, dry-run, blocked, and clarification decisions."),
    EvidenceReference("Day60", "reviewer walkthrough", "Shows the report-only workflow path."),
    EvidenceReference("Day61", "dashboard entry", "Places review evidence in the static dashboard."),
    EvidenceReference("Day62", "scenario pack", "Gives sample intents and expected reviewer decisions."),
    EvidenceReference("Day63", "traceability map", "Connects reviewer concepts to source evidence."),
    EvidenceReference("Day64", "acceptance runbook", "Defines reviewer acceptance steps."),
    EvidenceReference("Day65", "sign-off package", "Records accepted, deferred, and rejected scope."),
    EvidenceReference("Day66", "offline mock runtime skeleton", "Models future runtime-shaped records offline."),
    EvidenceReference("Day67", "runtime contract validation", "Validates mock output and safety invariants."),
    EvidenceReference("Day68", "reviewer report quality", "Checks readability and evidence traceability."),
    EvidenceReference("Day69", "dashboard evidence drilldown", "Shows scenario evidence on a read-only page."),
    EvidenceReference("Day70", "AI readiness gate", "Confirms readiness to design, not implement, a prototype."),
]


def get_day71_controlled_entry_design() -> Dict[str, object]:
    """Return the deterministic Day71 design contract summary."""
    return {
        "day": 71,
        "label": "Day71",
        "title": "Controlled AI Runtime Prototype Entry Design",
        "safety_stage": "design_only",
        "proposed_future_entry_point": "ai_intent_reviewer_controlled_runtime_entry",
        "execution_allowed": False,
        "api_integration_allowed": False,
        "voice_allowed": False,
        "device_access_allowed": False,
        "dashboard_action_surface_allowed": False,
        "mapped_task_execution_allowed": False,
        "live_execution_allowed": False,
        "required_reviewer_gate": True,
        "input_contract": [asdict(item) for item in INPUT_CONTRACT],
        "output_contract": [asdict(item) for item in OUTPUT_CONTRACT],
        "safety_gate_sequence": [asdict(item) for item in SAFETY_GATE_SEQUENCE],
        "reviewer_evidence_map": [asdict(item) for item in REVIEWER_EVIDENCE_MAP],
        "blocked_at_day71": [
            "model invocation",
            "voice input or output",
            "device access",
            "live execution",
            "mapped task execution",
            "configuration changes",
            "dashboard submission surfaces",
            "secret handling",
            "release tagging",
        ],
        "acceptance_criteria": [
            "Static documentation exists.",
            "Dashboard exposes Day71 design as read-only content.",
            "Tests confirm no dashboard submission or command surface.",
            "Tests confirm static contract booleans keep execution disabled.",
            "Existing report-only runner tasks still pass.",
        ],
    }
