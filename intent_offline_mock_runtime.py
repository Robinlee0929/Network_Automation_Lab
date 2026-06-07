"""Day66 offline mock runtime skeleton for the AI Intent Reviewer flow.

This module is intentionally deterministic and offline-only. It models the
shape of a future runtime review record without calling APIs, executing tasks,
opening SSH, reading configuration files, or touching devices.
"""

from copy import deepcopy
from typing import Any, Dict, List


EXECUTION_MODE = "offline_mock"
LIVE_EXECUTION_ALLOWED = False

EVIDENCE_DOC_REFS = [
    "docs/ai/day57_intent_mapping_prototype.md",
    "docs/ai/day58_intent_mapping_safety_review_confirmation_gate.md",
    "docs/ai/day59_intent_policy_matrix_reviewer_safety_explanation.md",
    "docs/ai/day60_ai_intent_workflow_demo_reviewer_walkthrough.md",
    "docs/ai/intent_reviewer_scenario_pack.md",
    "docs/ai/intent_reviewer_traceability_evidence_map.md",
    "docs/ai/intent_reviewer_acceptance_runbook.md",
    "docs/ai/intent_reviewer_acceptance_signoff_package.md",
    "docs/ai/intent_offline_mock_runtime_skeleton.md",
    "docs/roadmap/day66_offline_mock_runtime_skeleton.md",
]

SAMPLE_MOCK_INTENTS = [
    {
        "id": "documentation-only-runbook",
        "input_text": "Explain the AI intent reviewer acceptance runbook",
        "normalized_intent": "explain_acceptance_runbook",
        "safety_category": "documentation_only",
        "mock_plan": [
            "Normalize the request as a documentation lookup.",
            "Point the reviewer to the Day64 and Day65 evidence documents.",
            "Record a documentation-only mock execution record.",
        ],
        "reviewer_note": "Documentation lookup only. No runner task is proposed or executed.",
    },
    {
        "id": "report-only-latest",
        "input_text": "Show the latest AI intent reviewer reports",
        "normalized_intent": "show_latest_reviewer_reports",
        "safety_category": "report_only",
        "mock_plan": [
            "Normalize the request as local report review.",
            "Reference existing report-index and Day60 reviewer walkthrough evidence.",
            "Record a report-only mock execution record.",
        ],
        "reviewer_note": "Report-only review path. This skeleton does not open files or run report-index.",
    },
    {
        "id": "blocked-vrrp-live",
        "input_text": "Run the VRRP failover test from the AI reviewer",
        "normalized_intent": "request_vrrp_failover_live_action",
        "safety_category": "blocked_live_action",
        "mock_plan": [
            "Normalize the request as a live-capable HA action.",
            "Block the request before any runner task can be delegated.",
            "Record blocked evidence for human review.",
        ],
        "reviewer_note": "Blocked live-capable action. VRRP failover cannot run from intent review.",
    },
    {
        "id": "blocked-ssh-device",
        "input_text": "SSH to the router and change the firewall rule",
        "normalized_intent": "request_ssh_device_configuration_change",
        "safety_category": "blocked_live_action",
        "mock_plan": [
            "Normalize the request as direct device access and configuration change.",
            "Block SSH, shell, and device-changing behavior.",
            "Record blocked evidence for human review.",
        ],
        "reviewer_note": "Blocked live action. SSH and device configuration changes are outside Day66 scope.",
    },
    {
        "id": "manual-review-ambiguous",
        "input_text": "Make the network better automatically",
        "normalized_intent": "ambiguous_network_automation_request",
        "safety_category": "needs_manual_review",
        "mock_plan": [
            "Normalize the request as ambiguous automation intent.",
            "Stop before task proposal because the request is underspecified.",
            "Record manual-review evidence.",
        ],
        "reviewer_note": "Needs manual review. Ambiguous intent must not become automatic execution.",
    },
]


def _mock_execution_record(sample: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mock_record_created": True,
        "mock_record_type": "reviewer_evidence_only",
        "real_command_executed": False,
        "mapped_task_executed": False,
        "ssh_used": False,
        "device_access_used": False,
        "network_change_made": False,
        "source_sample_id": sample["id"],
    }


def review_mock_intent(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Return one deterministic offline mock reviewer record."""
    return {
        "input_text": sample["input_text"],
        "normalized_intent": sample["normalized_intent"],
        "safety_category": sample["safety_category"],
        "mock_plan": list(sample["mock_plan"]),
        "execution_mode": EXECUTION_MODE,
        "live_execution_allowed": LIVE_EXECUTION_ALLOWED,
        "reviewer_note": sample["reviewer_note"],
        "evidence_links_or_doc_refs": list(EVIDENCE_DOC_REFS),
        "mock_execution_record": _mock_execution_record(sample),
    }


def run_mock_runtime() -> List[Dict[str, Any]]:
    """Return all committed Day66 sample intent records."""
    return [review_mock_intent(deepcopy(sample)) for sample in SAMPLE_MOCK_INTENTS]


def build_mock_runtime_report() -> Dict[str, Any]:
    """Build the Day66 fixed mock report payload."""
    scenarios = run_mock_runtime()
    blocked = [
        item for item in scenarios if item["safety_category"] == "blocked_live_action"
    ]
    manual_review = [
        item for item in scenarios if item["safety_category"] == "needs_manual_review"
    ]
    return {
        "day": "Day66",
        "title": "Offline Mock Runtime Skeleton",
        "overall_status": "PASS",
        "reviewer_status": "REVIEW_READY",
        "execution_mode": EXECUTION_MODE,
        "live_execution_allowed": LIVE_EXECUTION_ALLOWED,
        "no_live_execution_occurred": True,
        "no_device_access_occurred": True,
        "no_network_change_occurred": True,
        "openai_api_used": False,
        "voice_integration_used": False,
        "ssh_used": False,
        "config_json_read": False,
        "mapped_task_executed": False,
        "summary": {
            "mock_scenarios": len(scenarios),
            "blocked_live_action_scenarios": len(blocked),
            "manual_review_scenarios": len(manual_review),
            "execution_modes": sorted({item["execution_mode"] for item in scenarios}),
            "all_live_execution_allowed_values": sorted(
                {item["live_execution_allowed"] for item in scenarios}
            ),
        },
        "runtime_stages": [
            "user_request_input",
            "intent_normalization",
            "safety_classification",
            "mock_plan_generation",
            "mock_execution_record",
            "reviewer_evidence_output",
            "final_dry_run_summary",
        ],
        "mock_scenarios": scenarios,
        "evidence_links_or_doc_refs": list(EVIDENCE_DOC_REFS),
        "final_safety_statement": (
            "Day66 created an offline mock runtime skeleton only. No live execution, "
            "AI API, voice integration, SSH, device access, or network change occurred."
        ),
    }
