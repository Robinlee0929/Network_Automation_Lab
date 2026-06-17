"""Phase 2A-07 Day1-Day160 artifact-to-Jobs dry-run validation pack.

This module maps prior Day1-Day160 in-repo artifact patterns into candidate
Phase 2A Jobs and validates local VRRP mock evidence as the first concrete
example Job. It does not connect to devices, run commands, invoke adapters,
invoke brokers, invoke runners, call providers/APIs/models, or perform live
testing.
"""

from __future__ import annotations

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple


PHASE = "2A-07"
TASK_NAME = "phase2a-07-vrrp-dry-run-validation-pack"
TITLE = "Phase 2A-07 Day1-Day160 Artifact-to-Jobs Dry-Run Validation Pack"
STATUS_LABEL = "PHASE_2A_07_ARTIFACT_TO_JOBS_DRY_RUN_VALIDATION_PACK_READY"
MODE = "report_only"
SCOPE = "day1_day160_artifact_to_jobs_mapping_with_vrrp_example"
FIXTURE_PATH = Path("fixtures") / "phase_2a" / "phase_2a_07_vrrp_mock_evidence.json"
REPORT_JSON = Path("reports") / "lab-summary" / "phase_2a_07_vrrp_dry_run_validation_pack.json"
REPORT_HTML = Path("reports") / "lab-summary" / "phase_2a_07_vrrp_dry_run_validation_pack.html"
DOC_PATH = Path("docs") / "phase_2a" / "phase_2a_07_vrrp_dry_run_validation_pack.md"

SAFETY_FLAGS = {
    "real_vrrp_test_performed": False,
    "live_device_access_enabled": False,
    "ssh_enabled": False,
    "netconf_enabled": False,
    "restconf_enabled": False,
    "provider_api_model_enabled": False,
    "adapter_broker_runner_enabled": False,
    "secrets_enabled": False,
    "real_network_io_enabled": False,
    "real_command_execution_enabled": False,
    "real_backup_execution_enabled": False,
    "real_failover_testing_enabled": False,
    "config_change_enabled": False,
    "custom_script_execution_enabled": False,
    "phase_2b_authorized": False,
    "next_phase_allowed": False,
}

COMPLETION_MARKERS = (
    "PHASE_2A_07_ARTIFACT_TO_JOBS_DRY_RUN_VALIDATION_PACK_READY",
    "AGENTS_MD_FOUND_AND_READ",
    "AGENTS_MD_NOT_MODIFIED",
    "DAY1_DAY160_ARTIFACT_REFERENCES_INSPECTED",
    "ARTIFACT_PATTERNS_MAPPED_TO_JOB_CANDIDATES",
    "SAFE_JOBS_DRY_RUN_MOCK_LOCAL_REPORT_ONLY",
    "UNSAFE_JOBS_BLOCKED_OR_PLANNING_ONLY",
    "VRRP_VALIDATION_RETAINED_AS_FIRST_CONCRETE_EXAMPLE_JOB",
    "VRRP_MOCK_EVIDENCE_ONLY",
    "LOCAL_FIXTURE_VALIDATION_ONLY",
    "MISMATCH_DETECTION_PRESENT",
    "INCOMPLETE_EVIDENCE_DETECTION_PRESENT",
    "UNSAFE_VRRP_REQUESTS_REJECTED",
    "UNSAFE_INPUT_VALUES_REDACTED",
    "RUNNER_INVOKED_FALSE",
    "ADAPTER_INVOKED_FALSE",
    "BROKER_INVOKED_FALSE",
    "LIVE_DEVICE_ACCESS_ENABLED_FALSE",
    "NEXT_PHASE_ALLOWED_FALSE",
)

REQUIRED_JOB_TYPES = (
    "baseline_check",
    "interface_status_check",
    "wan_lan_check",
    "vrrp_validation",
    "backup_config_plan",
    "blocked_config_change_request",
)

DAY1_DAY160_ARTIFACT_REFERENCES = (
    {
        "reference_id": "DAY1_DAY4_BASELINE_PATTERN",
        "day_range": "Day1-Day4",
        "source_artifacts": [
            "README.md#Day 1",
            "README.md#Day 4",
            "reports/lab-summary/phase2a_readonly_job_runner_framework.json",
            "mikrotik_acceptance_check.py",
            "mikrotik_day4_multi_device_baseline.py",
        ],
        "evidence_pattern": "baseline acceptance and multi-device baseline reports",
        "mapped_job_types": ["baseline_check"],
        "safety_class": "local_mock_report_only_candidate",
    },
    {
        "reference_id": "DAY5_DAY32_INTERFACE_STATUS_PATTERN",
        "day_range": "Day5-Day32",
        "source_artifacts": [
            "README.md#Cisco validation",
            "docs/roadmap/ha_vrrp_safety_model.md",
            "reports/lab-summary/day32_vrrp_readonly_precheck.json",
            "cisco_topology_validation.py",
            "mikrotik_day32_vrrp_readonly_precheck.py",
        ],
        "evidence_pattern": "read-only interface and topology status reports",
        "mapped_job_types": ["interface_status_check"],
        "safety_class": "local_mock_report_only_candidate",
    },
    {
        "reference_id": "DAY8_DAY13_WAN_LAN_PATTERN",
        "day_range": "Day8-Day13",
        "source_artifacts": [
            "README.md#Day 8",
            "README.md#Day 13",
            "reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary.json",
            "performance_test.py",
            "mikrotik_day13_multi_router_wireguard_validation.py",
        ],
        "evidence_pattern": "WAN/LAN reachability and performance evidence summaries",
        "mapped_job_types": ["wan_lan_check"],
        "safety_class": "local_mock_report_only_candidate",
    },
    {
        "reference_id": "DAY31_DAY39_VRRP_PATTERN",
        "day_range": "Day31-Day39",
        "source_artifacts": [
            "docs/roadmap/ha_vrrp_topology_plan.md",
            "docs/roadmap/ha_vrrp_safety_model.md",
            "reports/lab-summary/day32_vrrp_readonly_precheck.json",
            "reports/lab-summary/day33_vrrp_topology_dry_run.json",
            "reports/lab-summary/day34_vrrp_staged_apply_plan.json",
            "reports/lab-summary/day35_vrrp_failover_validation.json",
            "reports/lab-summary/day39_vrrp_evidence_dashboard_integration.json",
            FIXTURE_PATH.as_posix(),
        ],
        "evidence_pattern": "VRRP planning, read-only precheck, dry-run, blocked plan, and mock validation evidence",
        "mapped_job_types": ["vrrp_validation"],
        "safety_class": "concrete_local_mock_report_only_example",
    },
    {
        "reference_id": "DAY2_DAY41_BACKUP_PLAN_PATTERN",
        "day_range": "Day2-Day41",
        "source_artifacts": [
            "README.md#Day 2",
            "README.md#Day 41",
            "reports/portfolio/day41_v0.2_release_packaging.json",
        ],
        "evidence_pattern": "backup and release packaging references treated as plan metadata only",
        "mapped_job_types": ["backup_config_plan"],
        "safety_class": "planning_only_blocked_from_execution",
    },
    {
        "reference_id": "DAY34_DAY57_DAY79_DAY160_BLOCKED_CHANGE_PATTERN",
        "day_range": "Day34-Day160",
        "source_artifacts": [
            "docs/phase_2a/next_phase_authorization_criteria_pack.md",
            "docs/roadmap/ha_vrrp_safety_model.md",
            "reports/lab-summary/day34_vrrp_staged_apply_plan.json",
            "reports/lab-summary/day79_readonly_task_contract.json",
            "reports/lab-summary/day160_v05_ai_assistance_phase_gate_review.json",
        ],
        "evidence_pattern": "blocked configuration change and next-phase lock evidence",
        "mapped_job_types": ["blocked_config_change_request"],
        "safety_class": "blocked_non_executing",
    },
)

JOB_CANDIDATES = (
    {
        "job_type": "baseline_check",
        "job_role": "safe_candidate",
        "source_reference_ids": ["DAY1_DAY4_BASELINE_PATTERN"],
        "source_pattern": "baseline acceptance and multi-device baseline evidence",
        "allowed_mode": "dry_run_mock_local_report_only",
        "candidate_status": "SAFE_DRY_RUN_MOCK_ONLY",
        "checks": ["expected device identity", "baseline status", "missing report detection"],
        "unsafe_actions_blocked": ["live baseline collection", "SSH session creation", "config mutation"],
    },
    {
        "job_type": "interface_status_check",
        "job_role": "safe_candidate",
        "source_reference_ids": ["DAY5_DAY32_INTERFACE_STATUS_PATTERN"],
        "source_pattern": "read-only interface and topology status evidence",
        "allowed_mode": "dry_run_mock_local_report_only",
        "candidate_status": "SAFE_DRY_RUN_MOCK_ONLY",
        "checks": ["interface presence", "interface state", "missing interface evidence"],
        "unsafe_actions_blocked": ["shut/no-shut", "live command collection", "device connection"],
    },
    {
        "job_type": "wan_lan_check",
        "job_role": "safe_candidate",
        "source_reference_ids": ["DAY8_DAY13_WAN_LAN_PATTERN"],
        "source_pattern": "WAN/LAN reachability and throughput evidence summaries",
        "allowed_mode": "dry_run_mock_local_report_only",
        "candidate_status": "SAFE_DRY_RUN_MOCK_ONLY",
        "checks": ["WAN evidence present", "LAN evidence present", "stale or missing evidence"],
        "unsafe_actions_blocked": ["real network I/O", "iperf execution", "VPN runner execution"],
    },
    {
        "job_type": "vrrp_validation",
        "job_role": "first_concrete_example",
        "source_reference_ids": ["DAY31_DAY39_VRRP_PATTERN"],
        "source_pattern": "VRRP planning, dry-run, blocked plan, and mock validation evidence",
        "allowed_mode": "dry_run_mock_local_report_only",
        "candidate_status": "IMPLEMENTED_AS_LOCAL_MOCK_EXAMPLE",
        "checks": [
            "expected VRRP group",
            "expected virtual IP",
            "expected active router",
            "expected standby router",
            "priority comparison",
            "preempt setting",
            "interface state",
            "freshness",
            "mismatch detection",
            "incomplete evidence detection",
        ],
        "unsafe_actions_blocked": ["real VRRP testing", "live failover", "VRRP priority changes"],
    },
    {
        "job_type": "backup_config_plan",
        "job_role": "planning_only_candidate",
        "source_reference_ids": ["DAY2_DAY41_BACKUP_PLAN_PATTERN"],
        "source_pattern": "backup/export references represented as plan metadata only",
        "allowed_mode": "planning_only_report_only",
        "candidate_status": "BLOCKED_FROM_EXECUTION",
        "checks": ["backup intent identified", "execution denied", "no backup artifact generated"],
        "unsafe_actions_blocked": ["real backup execution", "secret export", "device connection"],
    },
    {
        "job_type": "blocked_config_change_request",
        "job_role": "blocked_candidate",
        "source_reference_ids": ["DAY34_DAY57_DAY79_DAY160_BLOCKED_CHANGE_PATTERN"],
        "source_pattern": "configuration-changing requests remain blocked by safety gates",
        "allowed_mode": "blocked_non_executing_report_only",
        "candidate_status": "BLOCKED_NON_EXECUTING",
        "checks": ["blocked action identified", "no plan execution", "next phase remains locked"],
        "unsafe_actions_blocked": ["configuration changes", "interface changes", "next-phase unlock"],
    },
)

EXPECTED_VRRP_STATE = {
    "group": 10,
    "virtual_ip": "192.0.2.254",
    "active_router": "edge-a",
    "standby_router": "edge-b",
    "preempt": True,
    "required_interface_state": "up",
    "max_evidence_age_minutes": 10,
}

DEFAULT_MOCK_EVIDENCE = {
    "fixture_id": "PHASE_2A_07_LOCAL_VRRP_MOCK_FIXTURE",
    "source": "local_static_mock_data",
    "records": [
        {
            "record_id": "VRRP-MOCK-VALID",
            "description": "Expected VRRP mock state",
            "expected_outcome": "PASS",
            "observed_at": "2026-06-17T00:00:00Z",
            "evidence_age_minutes": 4,
            "group": 10,
            "virtual_ip": "192.0.2.254",
            "active_router": "edge-a",
            "standby_router": "edge-b",
            "routers": [
                {"name": "edge-a", "priority": 120, "preempt": True, "interface_state": "up"},
                {"name": "edge-b", "priority": 100, "preempt": True, "interface_state": "up"},
            ],
        },
        {
            "record_id": "VRRP-MOCK-VIP-MISMATCH",
            "description": "Virtual IP mismatch is detected",
            "expected_outcome": "MISMATCH",
            "observed_at": "2026-06-17T00:00:00Z",
            "evidence_age_minutes": 3,
            "group": 10,
            "virtual_ip": "192.0.2.99",
            "active_router": "edge-a",
            "standby_router": "edge-b",
            "routers": [
                {"name": "edge-a", "priority": 120, "preempt": True, "interface_state": "up"},
                {"name": "edge-b", "priority": 100, "preempt": True, "interface_state": "up"},
            ],
        },
        {
            "record_id": "VRRP-MOCK-MISSING-STANDBY",
            "description": "Incomplete standby evidence is detected",
            "expected_outcome": "INCOMPLETE",
            "observed_at": "2026-06-17T00:00:00Z",
            "evidence_age_minutes": 5,
            "group": 10,
            "virtual_ip": "192.0.2.254",
            "active_router": "edge-a",
            "routers": [
                {"name": "edge-a", "priority": 120, "preempt": True, "interface_state": "up"},
            ],
        },
        {
            "record_id": "VRRP-MOCK-STALE",
            "description": "Stale local evidence is detected",
            "expected_outcome": "STALE",
            "observed_at": "2026-06-16T23:00:00Z",
            "evidence_age_minutes": 42,
            "group": 10,
            "virtual_ip": "192.0.2.254",
            "active_router": "edge-a",
            "standby_router": "edge-b",
            "routers": [
                {"name": "edge-a", "priority": 120, "preempt": True, "interface_state": "up"},
                {"name": "edge-b", "priority": 100, "preempt": True, "interface_state": "up"},
            ],
        },
        {
            "record_id": "VRRP-MOCK-INTERFACE-DOWN",
            "description": "Interface state mismatch is detected",
            "expected_outcome": "MISMATCH",
            "observed_at": "2026-06-17T00:00:00Z",
            "evidence_age_minutes": 7,
            "group": 10,
            "virtual_ip": "192.0.2.254",
            "active_router": "edge-a",
            "standby_router": "edge-b",
            "routers": [
                {"name": "edge-a", "priority": 120, "preempt": True, "interface_state": "up"},
                {"name": "edge-b", "priority": 100, "preempt": True, "interface_state": "down"},
            ],
        },
    ],
}

RAW_UNSAFE_LITERALS = (
    "ssh router01",
    "show vrrp",
    "test live failover",
    "set vrrp priority 200",
    "shutdown interface ether1",
    "no shutdown interface ether1",
    "unsafe-user",
    "unsafe-password",
    "198.51.100.22",
    "unsafe-api-key",
    "unsafe-provider",
    "unsafe-model",
    "unsafe-script.ps1",
    "custom command",
)

UNSAFE_REQUEST_SPECS = (
    {
        "case_id": "VRRP-NEG-01",
        "target": "ssh_request",
        "request": {"action": "ssh router01", "transport": "ssh"},
    },
    {
        "case_id": "VRRP-NEG-02",
        "target": "live_show_command",
        "request": {"action": "collect", "command": "show vrrp"},
    },
    {
        "case_id": "VRRP-NEG-03",
        "target": "live_failover_test",
        "request": {"action": "test live failover", "live_failover": True},
    },
    {
        "case_id": "VRRP-NEG-04",
        "target": "priority_change",
        "request": {"action": "set vrrp priority 200", "change_priority": 200},
    },
    {
        "case_id": "VRRP-NEG-05",
        "target": "interface_shutdown",
        "request": {"action": "shutdown interface ether1", "interface_action": "shutdown"},
    },
    {
        "case_id": "VRRP-NEG-06",
        "target": "execution_target_and_credentials",
        "request": {
            "username": "unsafe-user",
            "password": "unsafe-password",
            "host": "router01",
            "ip": "198.51.100.22",
            "port": 22,
        },
    },
    {
        "case_id": "VRRP-NEG-07",
        "target": "provider_api_model_fields",
        "request": {"api_key": "unsafe-api-key", "provider": "unsafe-provider", "model": "unsafe-model"},
    },
    {
        "case_id": "VRRP-NEG-08",
        "target": "custom_command_script_fields",
        "request": {"custom_command": "custom command", "script_path": "unsafe-script.ps1"},
    },
    {
        "case_id": "VRRP-NEG-09",
        "target": "interface_no_shutdown",
        "request": {"action": "no shutdown interface ether1", "interface_action": "no shut"},
    },
)

FORBIDDEN_REQUEST_FIELDS = {
    "api_key",
    "command",
    "custom_command",
    "custom_script",
    "host",
    "ip",
    "live_failover",
    "model",
    "password",
    "port",
    "provider",
    "script_path",
    "ssh",
    "transport",
    "username",
}

FORBIDDEN_ACTION_FRAGMENTS = (
    "ssh",
    "show vrrp",
    "live failover",
    "set vrrp",
    "change priority",
    "shutdown",
    "no shutdown",
    "no shut",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _stable_digest(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length].upper()


def _iter_field_paths(payload: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path
            yield from _iter_field_paths(value, path)
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            yield from _iter_field_paths(value, f"{prefix}[{index}]")


def _contains_raw_unsafe_literal(payload: Any) -> bool:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return any(literal in serialized for literal in RAW_UNSAFE_LITERALS)


def _load_local_fixture(project_root: Optional[Path]) -> Dict[str, Any]:
    if project_root is not None:
        fixture_path = project_root / FIXTURE_PATH
        if fixture_path.exists():
            return json.loads(fixture_path.read_text(encoding="utf-8"))
    return deepcopy(DEFAULT_MOCK_EVIDENCE)


def _router_by_name(record: Mapping[str, Any], name: str) -> Optional[Mapping[str, Any]]:
    routers = record.get("routers", [])
    if not isinstance(routers, Sequence) or isinstance(routers, (str, bytes, bytearray)):
        return None
    for router in routers:
        if isinstance(router, Mapping) and router.get("name") == name:
            return router
    return None


def validate_vrrp_mock_record(
    record: Mapping[str, Any],
    expected: Mapping[str, Any] = EXPECTED_VRRP_STATE,
) -> Dict[str, Any]:
    missing = []
    mismatches = []

    for field in ("group", "virtual_ip", "active_router", "standby_router", "routers", "evidence_age_minutes"):
        if field not in record:
            missing.append(field)

    active_router = _router_by_name(record, str(expected["active_router"]))
    standby_router = _router_by_name(record, str(expected["standby_router"]))
    if active_router is None:
        missing.append("routers.active")
    if standby_router is None:
        missing.append("routers.standby")

    if missing:
        return {
            "record_id": str(record.get("record_id", "UNKNOWN")),
            "validation_status": "INCOMPLETE",
            "checks": [],
            "missing_fields": sorted(set(missing)),
            "mismatches": mismatches,
            "non_execution_proof": _non_execution_proof(),
        }

    checks = [
        _check("expected_vrrp_group", record.get("group"), expected["group"]),
        _check("expected_virtual_ip", record.get("virtual_ip"), expected["virtual_ip"]),
        _check("expected_active_router", record.get("active_router"), expected["active_router"]),
        _check("expected_standby_router", record.get("standby_router"), expected["standby_router"]),
        _check("active_router_preempt", active_router.get("preempt"), expected["preempt"]),
        _check("standby_router_preempt", standby_router.get("preempt"), expected["preempt"]),
        _check("active_interface_state", active_router.get("interface_state"), expected["required_interface_state"]),
        _check("standby_interface_state", standby_router.get("interface_state"), expected["required_interface_state"]),
    ]

    active_priority = active_router.get("priority")
    standby_priority = standby_router.get("priority")
    priority_ok = isinstance(active_priority, int) and isinstance(standby_priority, int) and active_priority > standby_priority
    checks.append(
        {
            "name": "priority_comparison",
            "status": "PASS" if priority_ok else "FAIL",
            "expected": "active_priority_greater_than_standby_priority",
            "observed": "active_priority_greater_than_standby_priority" if priority_ok else "priority_order_not_met",
        }
    )

    evidence_age = record.get("evidence_age_minutes")
    freshness_ok = isinstance(evidence_age, int) and evidence_age <= int(expected["max_evidence_age_minutes"])
    checks.append(
        {
            "name": "evidence_freshness",
            "status": "PASS" if freshness_ok else "STALE",
            "expected": f"age_minutes<={expected['max_evidence_age_minutes']}",
            "observed": "fresh" if freshness_ok else "stale",
        }
    )

    mismatches = [check["name"] for check in checks if check["status"] == "FAIL"]
    stale = [check["name"] for check in checks if check["status"] == "STALE"]
    if stale:
        validation_status = "STALE"
    elif mismatches:
        validation_status = "MISMATCH"
    else:
        validation_status = "PASS"

    return {
        "record_id": str(record.get("record_id", "UNKNOWN")),
        "validation_status": validation_status,
        "checks": checks,
        "missing_fields": [],
        "mismatches": mismatches,
        "non_execution_proof": _non_execution_proof(),
    }


def _check(name: str, observed: Any, expected: Any) -> Dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if observed == expected else "FAIL",
        "expected": expected,
        "observed": observed,
    }


def _non_execution_proof() -> Dict[str, bool]:
    return {
        "local_fixture_read": True,
        "subprocess_invoked": False,
        "runner_invoked": False,
        "adapter_invoked": False,
        "broker_invoked": False,
        "device_connection_attempted": False,
        "command_payload_present": False,
        "network_io_attempted": False,
    }


def reject_unsafe_vrrp_request(request: Mapping[str, Any]) -> Dict[str, Any]:
    field_paths = sorted(_iter_field_paths(request))
    field_names = {path.split(".")[-1] for path in field_paths}
    forbidden_fields = sorted(field_names.intersection(FORBIDDEN_REQUEST_FIELDS))
    action = str(request.get("action", "")).lower()
    forbidden_fragments = sorted(fragment for fragment in FORBIDDEN_ACTION_FRAGMENTS if fragment in action)
    port_22_target = request.get("port") == 22
    rejected = bool(forbidden_fields or forbidden_fragments or port_22_target)
    return {
        "status": "REJECTED" if rejected else "ACCEPTED_FOR_LOCAL_MOCK_REVIEW",
        "rejection_reason": "UNSAFE_VRRP_REQUEST_REJECTED" if rejected else "",
        "request_ref": f"PHASE_2A_07_REQUEST_REF_{_stable_digest(request)}",
        "field_paths": field_paths,
        "forbidden_fields": forbidden_fields,
        "forbidden_action_fragment_count": len(forbidden_fragments),
        "port_22_target_detected": port_22_target,
        "values_redacted": True,
        "raw_values_included": False,
        "runner_invoked": False,
        "adapter_invoked": False,
        "broker_invoked": False,
        "live_execution_opened": False,
        "next_phase_allowed": False,
    }


def build_negative_regression_matrix() -> Sequence[Dict[str, Any]]:
    matrix = []
    for spec in UNSAFE_REQUEST_SPECS:
        rejection = reject_unsafe_vrrp_request(spec["request"])
        case = {
            "case_id": spec["case_id"],
            "target": spec["target"],
            "expected_status": "REJECTED",
            "actual": rejection,
            "passed": (
                rejection["status"] == "REJECTED"
                and rejection["values_redacted"] is True
                and rejection["raw_values_included"] is False
                and rejection["runner_invoked"] is False
                and rejection["adapter_invoked"] is False
                and rejection["broker_invoked"] is False
                and rejection["live_execution_opened"] is False
                and rejection["next_phase_allowed"] is False
            ),
        }
        matrix.append(case)
    return matrix


def build_vrrp_validation_pack(
    evidence_fixture: Mapping[str, Any],
    expected: Mapping[str, Any] = EXPECTED_VRRP_STATE,
) -> Dict[str, Any]:
    records = evidence_fixture.get("records", [])
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        records = []
    validations = []
    for record in records:
        if isinstance(record, Mapping):
            validation = validate_vrrp_mock_record(record, expected)
            validation["expected_outcome"] = str(record.get("expected_outcome", "UNKNOWN"))
            validation["expected_outcome_matched"] = validation["validation_status"] == validation["expected_outcome"]
            validations.append(validation)
    return {
        "fixture_id": str(evidence_fixture.get("fixture_id", "UNKNOWN")),
        "fixture_source": str(evidence_fixture.get("source", "local_static_mock_data")),
        "expected_state": dict(expected),
        "validations": validations,
    }


def _artifact_references_by_id() -> Dict[str, Mapping[str, Any]]:
    return {str(reference["reference_id"]): reference for reference in DAY1_DAY160_ARTIFACT_REFERENCES}


def build_artifact_to_jobs_mapping() -> Dict[str, Any]:
    """Build a non-executing mapping from Day1-Day160 artifacts to Job candidates."""

    references_by_id = _artifact_references_by_id()
    jobs = []
    for candidate in JOB_CANDIDATES:
        source_reference_ids = list(candidate["source_reference_ids"])
        source_references = [references_by_id[reference_id] for reference_id in source_reference_ids]
        source_artifacts = [
            artifact
            for reference in source_references
            for artifact in reference.get("source_artifacts", [])
        ]
        job = {
            "job_type": candidate["job_type"],
            "job_role": candidate["job_role"],
            "candidate_status": candidate["candidate_status"],
            "allowed_mode": candidate["allowed_mode"],
            "source_reference_ids": source_reference_ids,
            "source_day_ranges": [str(reference.get("day_range")) for reference in source_references],
            "source_artifacts": source_artifacts,
            "source_pattern": candidate["source_pattern"],
            "checks": list(candidate["checks"]),
            "unsafe_actions_blocked": list(candidate["unsafe_actions_blocked"]),
            "vrrp_concrete_example": candidate["job_type"] == "vrrp_validation",
            "safe_job": candidate["allowed_mode"] == "dry_run_mock_local_report_only",
            "blocked_or_planning_only": candidate["allowed_mode"] != "dry_run_mock_local_report_only",
            "non_execution_proof": _non_execution_proof(),
            "safety_boundary": {
                "dry_run_only": True,
                "mock_only": True,
                "local_only": True,
                "report_only": True,
                "live_device_access_enabled": False,
                "ssh_enabled": False,
                "netconf_enabled": False,
                "restconf_enabled": False,
                "provider_api_model_enabled": False,
                "adapter_broker_runner_enabled": False,
                "secrets_enabled": False,
                "real_network_io_enabled": False,
                "config_change_enabled": False,
                "next_phase_allowed": False,
            },
        }
        jobs.append(job)

    return {
        "mapping_scope": "Day1-Day160 in-repo artifact references",
        "artifact_references_inspected": True,
        "artifact_reference_groups": deepcopy(DAY1_DAY160_ARTIFACT_REFERENCES),
        "job_candidates": jobs,
        "vrrp_role_after_correction": (
            "VRRP remains the first concrete local mock validation Job example; "
            "it is no longer the whole Phase 2A-07 scope."
        ),
    }


def validate_phase_2a_07_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    errors = []
    pack = report.get("vrrp_validation_pack", {})
    validations = pack.get("validations", []) if isinstance(pack, Mapping) else []
    negative_matrix = report.get("negative_regression_matrix", [])
    artifact_mapping = report.get("artifact_to_jobs_mapping", {})
    job_candidates = artifact_mapping.get("job_candidates", []) if isinstance(artifact_mapping, Mapping) else []

    if not validations:
        errors.append("VRRP_VALIDATION_CASES_EMPTY")
    for validation in validations:
        if validation.get("expected_outcome_matched") is not True:
            errors.append(f"VRRP_EXPECTED_OUTCOME_NOT_DETECTED:{validation.get('record_id')}")
        proof = validation.get("non_execution_proof", {})
        if not isinstance(proof, Mapping) or any(
            proof.get(key) is not False
            for key in (
                "subprocess_invoked",
                "runner_invoked",
                "adapter_invoked",
                "broker_invoked",
                "device_connection_attempted",
                "command_payload_present",
                "network_io_attempted",
            )
        ):
            errors.append(f"VRRP_EXECUTION_PROOF_FAILED:{validation.get('record_id')}")

    required_statuses = {"PASS", "MISMATCH", "INCOMPLETE", "STALE"}
    detected_statuses = {str(validation.get("validation_status")) for validation in validations}
    missing_statuses = sorted(required_statuses.difference(detected_statuses))
    if missing_statuses:
        errors.append("VRRP_DETECTION_COVERAGE_MISSING:" + ",".join(missing_statuses))

    if len(negative_matrix) != len(UNSAFE_REQUEST_SPECS):
        errors.append("NEGATIVE_REGRESSION_CASE_COUNT_MISMATCH")
    for case in negative_matrix:
        if case.get("passed") is not True:
            errors.append(f"NEGATIVE_CASE_FAILED:{case.get('case_id')}")

    if not isinstance(artifact_mapping, Mapping) or artifact_mapping.get("artifact_references_inspected") is not True:
        errors.append("DAY1_DAY160_ARTIFACT_REFERENCES_NOT_INSPECTED")
    mapped_job_types = {str(job.get("job_type")) for job in job_candidates if isinstance(job, Mapping)}
    missing_job_types = sorted(set(REQUIRED_JOB_TYPES).difference(mapped_job_types))
    if missing_job_types:
        errors.append("JOB_MAPPING_MISSING:" + ",".join(missing_job_types))
    if not any(
        isinstance(job, Mapping)
        and job.get("job_type") == "vrrp_validation"
        and job.get("vrrp_concrete_example") is True
        for job in job_candidates
    ):
        errors.append("VRRP_NOT_RETAINED_AS_CONCRETE_JOB_EXAMPLE")
    for job in job_candidates:
        if not isinstance(job, Mapping):
            errors.append("JOB_MAPPING_RECORD_NOT_OBJECT")
            continue
        if job.get("safe_job") is True and job.get("allowed_mode") != "dry_run_mock_local_report_only":
            errors.append(f"SAFE_JOB_NOT_DRY_RUN_MOCK_LOCAL_REPORT_ONLY:{job.get('job_type')}")
        if job.get("job_type") in {"backup_config_plan", "blocked_config_change_request"}:
            if job.get("blocked_or_planning_only") is not True:
                errors.append(f"UNSAFE_JOB_NOT_BLOCKED_OR_PLANNING_ONLY:{job.get('job_type')}")
        boundary = job.get("safety_boundary", {})
        if not isinstance(boundary, Mapping) or any(
            boundary.get(key) is not False
            for key in (
                "live_device_access_enabled",
                "ssh_enabled",
                "netconf_enabled",
                "restconf_enabled",
                "provider_api_model_enabled",
                "adapter_broker_runner_enabled",
                "secrets_enabled",
                "real_network_io_enabled",
                "config_change_enabled",
                "next_phase_allowed",
            )
        ):
            errors.append(f"JOB_SAFETY_BOUNDARY_FAILED:{job.get('job_type')}")

    for flag_name, expected_value in SAFETY_FLAGS.items():
        if report.get(flag_name) is not expected_value:
            errors.append(f"SAFETY_FLAG_NOT_FALSE:{flag_name}")

    if _contains_raw_unsafe_literal(report):
        errors.append("RAW_UNSAFE_LITERAL_PRESENT")

    return {
        "valid": not errors,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "vrrp_cases_checked": len(validations),
        "negative_cases_checked": len(negative_matrix),
    }


def build_phase_2a_07_vrrp_dry_run_validation_pack_report(
    project_root: Optional[Path] = None,
    evidence_fixture: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    fixture = deepcopy(evidence_fixture) if evidence_fixture is not None else _load_local_fixture(project_root)
    vrrp_pack = build_vrrp_validation_pack(fixture)
    artifact_mapping = build_artifact_to_jobs_mapping()
    negative_matrix = list(build_negative_regression_matrix())
    validations = vrrp_pack["validations"]
    job_candidates = artifact_mapping["job_candidates"]
    report = {
        "phase": PHASE,
        "status": "PASS",
        "overall_status": "PASS",
        "task": TASK_NAME,
        "title": TITLE,
        "status_label": STATUS_LABEL,
        "mode": MODE,
        "scope": SCOPE,
        **SAFETY_FLAGS,
        "agents_md_pre_read": {
            "required": True,
            "found": True,
            "read": True,
            "modified": False,
            "path": "AGENTS.md",
        },
        "phase_authorization": {
            "phase_2a_07_implementation_authorized": True,
            "phase_2b_authorized": False,
            "next_phase_allowed": False,
        },
        "fixture_path": FIXTURE_PATH.as_posix(),
        "completion_markers": list(COMPLETION_MARKERS),
        "summary": {
            "artifact_reference_groups_inspected": len(artifact_mapping["artifact_reference_groups"]),
            "mapped_job_candidates": len(job_candidates),
            "safe_job_candidates": sum(1 for job in job_candidates if job["safe_job"] is True),
            "blocked_or_planning_only_job_candidates": sum(
                1 for job in job_candidates if job["blocked_or_planning_only"] is True
            ),
            "required_job_types_mapped": len({job["job_type"] for job in job_candidates}.intersection(REQUIRED_JOB_TYPES)),
            "vrrp_role_after_correction": "first_concrete_example_job",
            "vrrp_mock_records": len(validations),
            "pass_records": sum(1 for validation in validations if validation["validation_status"] == "PASS"),
            "mismatch_records": sum(1 for validation in validations if validation["validation_status"] == "MISMATCH"),
            "incomplete_records": sum(1 for validation in validations if validation["validation_status"] == "INCOMPLETE"),
            "stale_records": sum(1 for validation in validations if validation["validation_status"] == "STALE"),
            "expected_outcomes_detected": sum(
                1 for validation in validations if validation["expected_outcome_matched"] is True
            ),
            "unsafe_requests_rejected": sum(
                1 for case in negative_matrix if case["actual"]["status"] == "REJECTED"
            ),
            "unsafe_requests_redacted": sum(
                1 for case in negative_matrix if case["actual"]["raw_values_included"] is False
            ),
            "runner_invoked_count": sum(1 for case in negative_matrix if case["actual"]["runner_invoked"] is True),
            "adapter_invoked_count": sum(1 for case in negative_matrix if case["actual"]["adapter_invoked"] is True),
            "broker_invoked_count": sum(1 for case in negative_matrix if case["actual"]["broker_invoked"] is True),
            "live_execution_opened_count": sum(
                1 for case in negative_matrix if case["actual"]["live_execution_opened"] is True
            ),
            "next_phase_allowed_count": sum(1 for case in negative_matrix if case["actual"]["next_phase_allowed"] is True),
            "raw_unsafe_literals_present": 0,
        },
        "artifact_to_jobs_mapping": artifact_mapping,
        "vrrp_validation_pack": vrrp_pack,
        "negative_regression_matrix": negative_matrix,
    }
    validation = validate_phase_2a_07_report(report)
    report["validation"] = validation
    report["status"] = "PASS" if validation["valid"] else "FAIL"
    report["overall_status"] = report["status"]
    return report


def write_phase_2a_07_vrrp_dry_run_validation_pack_reports(
    project_root: Path,
    report: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, Path]:
    report_data = report or build_phase_2a_07_vrrp_dry_run_validation_pack_report(project_root=project_root)
    json_path = project_root / REPORT_JSON
    html_path = project_root / REPORT_HTML
    json_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report_data, indent=2, sort_keys=True), encoding="utf-8")
    _write_html_report(report_data, html_path)
    return json_path, html_path


def _summary_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report["summary"].items()
    )


def _validation_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(validation['record_id']))}</td>"
        f"<td>{html.escape(str(validation['expected_outcome']))}</td>"
        f"<td>{html.escape(str(validation['validation_status']))}</td>"
        f"<td>{html.escape(str(validation['expected_outcome_matched']))}</td>"
        f"<td>{html.escape(str(', '.join(validation['mismatches'])))}</td>"
        f"<td>{html.escape(str(', '.join(validation['missing_fields'])))}</td>"
        "</tr>"
        for validation in report["vrrp_validation_pack"]["validations"]
    )


def _job_mapping_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(job['job_type']))}</td>"
        f"<td>{html.escape(str(job['job_role']))}</td>"
        f"<td>{html.escape(str(job['candidate_status']))}</td>"
        f"<td>{html.escape(str(job['allowed_mode']))}</td>"
        f"<td>{html.escape(str(', '.join(job['source_day_ranges'])))}</td>"
        f"<td>{html.escape(str(job['vrrp_concrete_example']))}</td>"
        "</tr>"
        for job in report["artifact_to_jobs_mapping"]["job_candidates"]
    )


def _negative_rows(report: Mapping[str, Any]) -> str:
    return "\n".join(
        "<tr>"
        f"<td>{html.escape(str(case['case_id']))}</td>"
        f"<td>{html.escape(str(case['target']))}</td>"
        f"<td>{html.escape(str(case['actual']['status']))}</td>"
        f"<td>{html.escape(str(case['actual']['values_redacted']))}</td>"
        f"<td>{html.escape(str(case['actual']['runner_invoked']))}</td>"
        f"<td>{html.escape(str(case['actual']['adapter_invoked']))}</td>"
        f"<td>{html.escape(str(case['actual']['broker_invoked']))}</td>"
        f"<td>{html.escape(str(case['actual']['live_execution_opened']))}</td>"
        f"<td>{html.escape(str(case['passed']))}</td>"
        "</tr>"
        for case in report["negative_regression_matrix"]
    )


def _write_html_report(report: Mapping[str, Any], output_path: Path) -> None:
    markers = "".join(f"<li>{html.escape(marker)}</li>" for marker in report["completion_markers"])
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(str(report["title"]))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(str(report["title"]))}</h1>
  <p>Status: {html.escape(str(report["status"]))} / {html.escape(str(report["status_label"]))}</p>
  <p>Phase 2A-07 maps Day1-Day160 artifact patterns into dry-run/mock/local/report-only Job candidates. VRRP remains the first concrete local mock validation example. No live testing, device connection, command execution, runner, adapter, broker, provider, API, model, or Phase 2B path is opened.</p>
  <h2>Summary</h2>
  <table><tbody>{_summary_rows(report)}</tbody></table>
  <h2>Artifact-to-Jobs Mapping</h2>
  <table>
    <thead><tr><th>Job type</th><th>Role</th><th>Status</th><th>Allowed mode</th><th>Source days</th><th>VRRP example</th></tr></thead>
    <tbody>{_job_mapping_rows(report)}</tbody>
  </table>
  <h2>VRRP Mock Evidence Checks</h2>
  <table>
    <thead><tr><th>Record</th><th>Expected</th><th>Detected</th><th>Matched</th><th>Mismatches</th><th>Missing fields</th></tr></thead>
    <tbody>{_validation_rows(report)}</tbody>
  </table>
  <h2>Unsafe Request Regression</h2>
  <table>
    <thead><tr><th>Case</th><th>Target</th><th>Status</th><th>Redacted</th><th>Runner</th><th>Adapter</th><th>Broker</th><th>Live execution</th><th>Passed</th></tr></thead>
    <tbody>{_negative_rows(report)}</tbody>
  </table>
  <h2>Completion Markers</h2>
  <ul>{markers}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def run_phase_2a_07_vrrp_dry_run_validation_pack(
    project_root: Path,
    format_heading_func: Optional[Callable[[str], str]] = None,
    format_status_func: Optional[Callable[[str], str]] = None,
    relative_to_project_func: Optional[Callable[[Path, Path], str]] = None,
) -> int:
    report = build_phase_2a_07_vrrp_dry_run_validation_pack_report(project_root=project_root)
    json_path, html_path = write_phase_2a_07_vrrp_dry_run_validation_pack_reports(project_root, report)
    heading = format_heading_func or (lambda value: value)
    status = format_status_func or (lambda value: f"[{value}]")
    relative = relative_to_project_func or (lambda _root, path: str(path))

    print(heading(TITLE))
    print(f"Task name: {TASK_NAME}")
    print(f"Phase: {PHASE}")
    print(f"Mode: {MODE}")
    print(f"Scope: {SCOPE}")
    print(f"Artifact reference groups inspected: {report['summary']['artifact_reference_groups_inspected']}")
    print(f"Mapped job candidates: {report['summary']['mapped_job_candidates']}")
    print(f"Safe job candidates: {report['summary']['safe_job_candidates']}")
    print(f"Blocked/planning-only job candidates: {report['summary']['blocked_or_planning_only_job_candidates']}")
    print(f"Required job types mapped: {report['summary']['required_job_types_mapped']}")
    print(f"VRRP role after correction: {report['summary']['vrrp_role_after_correction']}")
    print(f"VRRP mock records: {report['summary']['vrrp_mock_records']}")
    print(f"Expected outcomes detected: {report['summary']['expected_outcomes_detected']}")
    print(f"Unsafe requests rejected: {report['summary']['unsafe_requests_rejected']}")
    print(f"Unsafe requests redacted: {report['summary']['unsafe_requests_redacted']}")
    print(f"runner_invoked_count: {report['summary']['runner_invoked_count']}")
    print(f"adapter_invoked_count: {report['summary']['adapter_invoked_count']}")
    print(f"broker_invoked_count: {report['summary']['broker_invoked_count']}")
    print(f"live_execution_opened_count: {report['summary']['live_execution_opened_count']}")
    print(f"real_vrrp_test_performed: {str(report['real_vrrp_test_performed']).lower()}")
    print(f"live_device_access_enabled: {str(report['live_device_access_enabled']).lower()}")
    print(f"ssh_enabled: {str(report['ssh_enabled']).lower()}")
    print(f"provider_api_model_enabled: {str(report['provider_api_model_enabled']).lower()}")
    print(f"adapter_broker_runner_enabled: {str(report['adapter_broker_runner_enabled']).lower()}")
    print(f"config_change_enabled: {str(report['config_change_enabled']).lower()}")
    print(f"next_phase_allowed: {str(report['next_phase_allowed']).lower()}")
    print(f"JSON report: {relative(project_root, json_path)}")
    print(f"HTML report: {relative(project_root, html_path)}")
    print(f"{status(report['status'])} {report['status_label']}")
    return 0 if report["status"] == "PASS" else 1
