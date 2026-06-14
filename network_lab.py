import argparse
import html
import json
import os
import re
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from intent_dry_run_plan_builder import build_dry_run_plan_builder_report
from intent_manual_review_approval_envelope import (
    build_manual_review_approval_envelope_report,
)
from intent_mock_ai_decision_pipeline import build_mock_ai_decision_pipeline_report
from intent_offline_mock_runtime import build_mock_runtime_report
from intent_reviewer_report_quality import build_reviewer_quality_report
from intent_runtime_contract import validate_runtime_results
from intent_runtime_audit_trail import build_runtime_audit_trail_report
from intent_readonly_task_contract import (
    build_readonly_task_contract_report,
    write_readonly_task_contract_reports,
)
from intent_readonly_execution_broker import (
    build_readonly_execution_broker_report,
    write_readonly_execution_broker_reports,
)
from intent_broker_review_queue import (
    build_broker_review_queue_report,
    write_broker_review_queue_reports,
)
from intent_reviewer_decision_audit_summary import (
    build_reviewer_decision_audit_summary_report,
    write_reviewer_decision_audit_summary_reports,
)
from intent_readonly_executor_readiness_gate import (
    build_readonly_executor_readiness_gate_report,
    write_readonly_executor_readiness_gate_reports,
)
from intent_readonly_executor_adapter_contract import (
    build_readonly_executor_adapter_contract_report,
    write_readonly_executor_adapter_contract_reports,
)
from intent_mock_adapter_evidence_binding import (
    build_mock_adapter_evidence_binding_report,
    write_mock_adapter_evidence_binding_reports,
)
from intent_controlled_runner_harness import (
    build_controlled_runner_harness_report,
    write_controlled_runner_harness_reports,
)
from intent_readonly_executor_phase_gate_review import (
    build_readonly_executor_phase_gate_review,
    write_readonly_executor_phase_gate_review_reports,
)
from intent_real_readonly_executor_adapter_design import (
    build_real_readonly_executor_adapter_design_report,
    write_real_readonly_executor_adapter_design_reports,
)
from intent_real_adapter_safety_boundary_spec import (
    build_real_adapter_safety_boundary_spec_report,
    write_real_adapter_safety_boundary_spec_reports,
)
from intent_real_adapter_implementation_plan import (
    build_real_adapter_implementation_plan_report,
    write_real_adapter_implementation_plan_reports,
)
from intent_real_adapter_safety_scaffold import (
    build_day91_real_adapter_safety_scaffold,
    write_day91_real_adapter_safety_scaffold_reports,
)
from intent_executable_guards import (
    build_day92_real_adapter_executable_guards_report,
    write_day92_real_adapter_executable_guards_reports,
)
from intent_guarded_fake_adapter_contract import (
    run_guarded_fake_adapter_contract,
    write_guarded_fake_adapter_contract_reports,
)
from intent_adapter_boundary_regression_matrix import (
    run_adapter_boundary_regression_matrix,
    write_adapter_boundary_regression_matrix_reports,
)
from intent_adapter_result_normalization import (
    run_adapter_result_normalization,
    write_adapter_result_normalization_reports,
)
from intent_readonly_output_parser_prototype import (
    build_day96_parser_report,
    write_day96_parser_reports,
)
from intent_parser_evidence_quality import (
    build_day97_parser_evidence_quality_report,
    write_day97_parser_evidence_quality_reports,
)
from intent_parser_classification_matrix import (
    build_parser_classification_matrix,
    write_parser_classification_matrix_reports,
)
from intent_parser_evidence_coverage_audit import (
    build_parser_evidence_coverage_audit_report,
    write_parser_evidence_coverage_audit_reports,
)
from intent_parser_phase_gate_review import (
    build_parser_phase_gate_review_report,
    write_parser_phase_gate_review_reports,
)
from intent_parser_evidence_closure_plan import (
    build_parser_evidence_closure_plan_report,
    write_parser_evidence_closure_plan_reports,
)
from intent_parser_fixture_expansion import (
    build_parser_fixture_expansion_report,
    write_parser_fixture_expansion_reports,
)
from intent_parser_evidence_matrix import (
    build_parser_evidence_matrix_report,
    write_parser_evidence_matrix_reports,
)
from intent_parser_reviewer_acceptance_gate import (
    build_parser_reviewer_acceptance_gate_report,
    write_parser_reviewer_acceptance_gate_reports,
)
from intent_parser_acceptance_closure import (
    build_parser_acceptance_closure_report,
    write_parser_acceptance_closure_reports,
)
from intent_parser_reviewer_evidence_contract import (
    build_parser_reviewer_evidence_contract_report,
    write_parser_reviewer_evidence_contract_reports,
)
from intent_parser_contract_consumer_handoff import (
    build_parser_contract_consumer_handoff_report,
    write_parser_contract_consumer_handoff_reports,
)
from intent_parser_consumer_handoff_readiness_matrix import (
    build_parser_consumer_handoff_readiness_matrix_report,
    write_parser_consumer_handoff_readiness_matrix_reports,
)
from intent_parser_consumer_final_gate import (
    build_parser_consumer_final_gate_report,
    write_parser_consumer_final_gate_reports,
)
from intent_parser_consumer_release_package import (
    build_parser_consumer_release_package_report,
    write_parser_consumer_release_package_reports,
)
from intent_parser_consumer_release_review_intake import (
    build_parser_consumer_release_review_intake_report,
    write_parser_consumer_release_review_intake_reports,
)
from intent_parser_consumer_reviewer_triage_decision_log import (
    build_parser_consumer_reviewer_triage_decision_log_report,
    write_parser_consumer_reviewer_triage_decision_log_reports,
)
from intent_parser_consumer_reviewer_triage_evidence_traceability import (
    build_parser_consumer_reviewer_triage_evidence_traceability_report,
    write_parser_consumer_reviewer_triage_evidence_traceability_reports,
)
from intent_parser_consumer_reviewer_triage_closure_summary import (
    build_parser_consumer_reviewer_triage_closure_summary_report,
    write_parser_consumer_reviewer_triage_closure_summary_reports,
)
from intent_reviewer_deferred_action_register import (
    build_reviewer_deferred_action_register_report,
    write_reviewer_deferred_action_register_reports,
)
from intent_deferred_action_traceability_review import (
    build_deferred_action_traceability_review_report,
    write_deferred_action_traceability_review_reports,
)
from intent_deferred_action_review_sequence_runbook import (
    build_deferred_action_review_sequence_runbook_report,
    write_deferred_action_review_sequence_runbook_reports,
)
from intent_reviewer_evidence_intake_outcome_ledger import (
    build_reviewer_evidence_intake_outcome_ledger_report,
    write_reviewer_evidence_intake_outcome_ledger_reports,
)
from intent_safety_boundary_regression_matrix import (
    build_safety_boundary_regression_matrix_report,
    write_safety_boundary_regression_matrix_reports,
)
from intent_safety_invariant_helpers import (
    build_safety_invariant_helper_review,
    write_safety_invariant_helper_review_reports,
)
from intent_thin_cli_regression_gate import run_thin_cli_regression_gate
from intent_post_refactor_compatibility_evidence_pack import (
    run_post_refactor_compatibility_evidence_pack,
)
from intent_ai_reviewer_summary_schema_contract import (
    run_ai_reviewer_summary_schema_contract,
)
from intent_ai_reviewer_summary_fixture_renderer import (
    run_ai_reviewer_summary_fixture_renderer,
)
from intent_ai_summary_prompt_contract import (
    run_ai_summary_prompt_contract,
)
from intent_ai_summary_redaction_policy import (
    run_ai_summary_redaction_policy,
)
from intent_ai_summary_audit_trail_binding import (
    run_ai_summary_audit_trail_binding,
)
from intent_codex_agents_instruction_audit import (
    build_codex_agents_instruction_audit_report,
    write_codex_agents_instruction_audit_reports,
)
from intent_runtime_safety_case import build_runtime_safety_case_report
from intent_runtime_safety_gate import build_runtime_safety_gate_report
DAY14_NAME = "Unified Lab Runner and Report Index"
DEFAULT_PROFILE = Path("topology_profiles") / "day14_lab_runner_profile.json"
DAY4_BASELINE_SCRIPT = "mikrotik_day4_multi_device_baseline.py"
DAY4_BASELINE_DISPLAY_COMMAND = f"python {DAY4_BASELINE_SCRIPT}"
DAY8_PERFORMANCE_SCRIPT = "performance_test.py"
DAY8_PERFORMANCE_PROFILE = Path("topology_profiles") / "day8_iperf3_router_performance.json"
DAY12_WIREGUARD_SCRIPT = "mikrotik_day12_wireguard_vpn_automation.py"
DAY12_WIREGUARD_CONFIG = "Set_WireguardVPN_config.json"
DAY12_WIREGUARD_TIMEOUT_SECONDS = 900
DAY32_VRRP_PRECHECK_SCRIPT = "mikrotik_day32_vrrp_readonly_precheck.py"
DAY32_VRRP_PRECHECK_TASK_ID = "day32-vrrp-precheck"
DAY32_VRRP_PRECHECK_JSON = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.json"
DAY32_VRRP_PRECHECK_HTML = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.html"
DAY32_VRRP_PRECHECK_TXT = Path("reports") / "lab-summary" / "day32_vrrp_readonly_precheck.txt"
DAY33_VRRP_DRY_RUN_SCRIPT = "mikrotik_day33_vrrp_topology_dry_run.py"
DAY33_VRRP_DRY_RUN_TASK_ID = "day33-vrrp-dry-run"
DAY33_VRRP_DRY_RUN_JSON = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.json"
DAY33_VRRP_DRY_RUN_HTML = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.html"
DAY33_VRRP_DRY_RUN_TXT = Path("reports") / "lab-summary" / "day33_vrrp_topology_dry_run.txt"
DAY34_VRRP_STAGED_PLAN_SCRIPT = "mikrotik_day34_vrrp_staged_apply_plan.py"
DAY34_VRRP_STAGED_PLAN_TASK_ID = "day34-vrrp-staged-plan"
DAY34_VRRP_STAGED_PLAN_JSON = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.json"
DAY34_VRRP_STAGED_PLAN_HTML = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.html"
DAY34_VRRP_STAGED_PLAN_TXT = Path("reports") / "lab-summary" / "day34_vrrp_staged_apply_plan.txt"
DAY35_VRRP_FAILOVER_SCRIPT = "mikrotik_day35_vrrp_failover_validation.py"
DAY35_VRRP_FAILOVER_TASK_ID = "day35-vrrp-failover-validation"
DAY35_VRRP_FAILOVER_JSON = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.json"
DAY35_VRRP_FAILOVER_HTML = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.html"
DAY35_VRRP_FAILOVER_TXT = Path("reports") / "lab-summary" / "day35_vrrp_failover_validation.txt"
DAY39_VRRP_EVIDENCE_TASK_ID = "day39-vrrp-evidence-dashboard-integration"
DAY39_VRRP_EVIDENCE_JSON = Path("reports") / "lab-summary" / "day39_vrrp_evidence_dashboard_integration.json"
DAY39_VRRP_EVIDENCE_HTML = Path("reports") / "lab-summary" / "day39_vrrp_evidence_dashboard_integration.html"
DAY40_DEMO_READINESS_TASK_ID = "day40-v0.2-demo-readiness-review"
DAY40_DEMO_READINESS_JSON = Path("reports") / "portfolio" / "day40_v0.2_demo_readiness_review.json"
DAY40_DEMO_READINESS_HTML = Path("reports") / "portfolio" / "day40_v0.2_demo_readiness_review.html"
DAY41_RELEASE_PACKAGING_TASK_ID = "day41-v0.2-release-packaging"
DAY41_RELEASE_PACKAGE_DOC = Path("docs") / "releases" / "v0.2_release_package.md"
DAY41_ARTIFACT_CHECKLIST_DOC = Path("docs") / "releases" / "v0.2_artifact_checklist.md"
DAY41_DEMO_HANDOFF_DOC = Path("docs") / "portfolio" / "v0.2_demo_handoff_guide.md"
DAY41_RELEASE_PACKAGING_JSON = Path("reports") / "portfolio" / "day41_v0.2_release_packaging.json"
DAY41_RELEASE_PACKAGING_HTML = Path("reports") / "portfolio" / "day41_v0.2_release_packaging.html"
DAY57_INTENT_MAPPING_TASK_ID = "intent-mapping-prototype"
DAY57_INTENT_MAPPING_DOC = Path("docs") / "ai" / "day57_intent_mapping_prototype.md"
DAY58_INTENT_SAFETY_REVIEW_TASK_ID = "intent-safety-review"
DAY58_INTENT_SAFETY_REVIEW_DOC = Path("docs") / "ai" / "day58_intent_mapping_safety_review_confirmation_gate.md"
DAY58_INTENT_SAFETY_REVIEW_ROADMAP = Path("docs") / "roadmap" / "day58_intent_mapping_safety_review_confirmation_gate.md"
DAY58_INTENT_SAFETY_REVIEW_JSON = Path("reports") / "portfolio" / "day58_intent_mapping_safety_review.json"
DAY58_INTENT_SAFETY_REVIEW_HTML = Path("reports") / "portfolio" / "day58_intent_mapping_safety_review.html"
DAY59_INTENT_POLICY_MATRIX_TASK_ID = "intent-policy-matrix"
DAY59_INTENT_POLICY_MATRIX_DOC = Path("docs") / "ai" / "day59_intent_policy_matrix_reviewer_safety_explanation.md"
DAY59_INTENT_POLICY_MATRIX_ROADMAP = (
    Path("docs") / "roadmap" / "day59_intent_policy_matrix_reviewer_safety_explanation.md"
)
DAY59_INTENT_POLICY_MATRIX_JSON = Path("reports") / "portfolio" / "day59_intent_policy_matrix.json"
DAY59_INTENT_POLICY_MATRIX_HTML = Path("reports") / "portfolio" / "day59_intent_policy_matrix.html"
DAY60_INTENT_WORKFLOW_DEMO_TASK_ID = "intent-workflow-demo"
DAY60_INTENT_WORKFLOW_DEMO_DOC = (
    Path("docs") / "ai" / "day60_ai_intent_workflow_demo_reviewer_walkthrough.md"
)
DAY60_INTENT_WORKFLOW_DEMO_ROADMAP = (
    Path("docs") / "roadmap" / "day60_ai_intent_workflow_demo_reviewer_walkthrough.md"
)
DAY60_INTENT_WORKFLOW_DEMO_JSON = Path("reports") / "portfolio" / "day60_intent_workflow_demo.json"
DAY60_INTENT_WORKFLOW_DEMO_HTML = Path("reports") / "portfolio" / "day60_intent_workflow_demo.html"
DAY66_OFFLINE_MOCK_RUNTIME_TASK_ID = "offline-mock-runtime"
DAY66_OFFLINE_MOCK_RUNTIME_DOC = Path("docs") / "ai" / "intent_offline_mock_runtime_skeleton.md"
DAY66_OFFLINE_MOCK_RUNTIME_ROADMAP = Path("docs") / "roadmap" / "day66_offline_mock_runtime_skeleton.md"
DAY66_OFFLINE_MOCK_RUNTIME_JSON = Path("reports") / "portfolio" / "day66_offline_mock_runtime_skeleton.json"
DAY66_OFFLINE_MOCK_RUNTIME_HTML = Path("reports") / "portfolio" / "day66_offline_mock_runtime_skeleton.html"
DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_TASK_ID = "offline-mock-runtime-contract"
DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_DOC = Path("docs") / "ai" / "intent_offline_mock_runtime_contract.md"
DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_ROADMAP = (
    Path("docs") / "roadmap" / "day67_offline_mock_runtime_contract_safety_invariants.md"
)
DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_JSON = (
    Path("reports") / "portfolio" / "day67_offline_mock_runtime_contract.json"
)
DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_HTML = (
    Path("reports") / "portfolio" / "day67_offline_mock_runtime_contract.html"
)
DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_TASK_ID = "offline-mock-runtime-review"
DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_DOC = (
    Path("docs") / "ai" / "intent_offline_mock_runtime_reviewer_report_quality.md"
)
DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_ROADMAP = (
    Path("docs") / "roadmap" / "day68_offline_mock_runtime_reviewer_report_quality.md"
)
DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_JSON = (
    Path("reports") / "lab-summary" / "day68_offline_mock_runtime_reviewer_report_quality.json"
)
DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_HTML = (
    Path("reports") / "lab-summary" / "day68_offline_mock_runtime_reviewer_report_quality.html"
)
DAY73_MOCK_AI_DECISION_PIPELINE_TASK_ID = "mock-ai-decision-pipeline"
DAY73_MOCK_AI_DECISION_PIPELINE_DOC = Path("docs") / "ai" / "intent_mock_ai_decision_pipeline.md"
DAY73_MOCK_AI_DECISION_PIPELINE_ROADMAP = Path("docs") / "roadmap" / "day73_mock_ai_decision_pipeline.md"
DAY73_MOCK_AI_DECISION_PIPELINE_JSON = Path("reports") / "lab-summary" / "day73_mock_ai_decision_pipeline.json"
DAY73_MOCK_AI_DECISION_PIPELINE_HTML = Path("reports") / "lab-summary" / "day73_mock_ai_decision_pipeline.html"
DAY74_DRY_RUN_PLAN_BUILDER_TASK_ID = "dry-run-plan-builder"
DAY74_DRY_RUN_PLAN_BUILDER_DOC = Path("docs") / "ai" / "intent_dry_run_plan_builder.md"
DAY74_DRY_RUN_PLAN_BUILDER_ROADMAP = Path("docs") / "roadmap" / "day74_dry_run_plan_builder.md"
DAY74_DRY_RUN_PLAN_BUILDER_JSON = Path("reports") / "lab-summary" / "day74_dry_run_plan_builder.json"
DAY74_DRY_RUN_PLAN_BUILDER_HTML = Path("reports") / "lab-summary" / "day74_dry_run_plan_builder.html"
DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_TASK_ID = "manual-review-approval-envelope"
DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_DOC = (
    Path("docs") / "ai" / "intent_manual_review_approval_envelope.md"
)
DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_ROADMAP = (
    Path("docs") / "roadmap" / "day75_manual_review_approval_envelope.md"
)
DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_JSON = (
    Path("reports") / "lab-summary" / "day75_manual_review_approval_envelope.json"
)
DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_HTML = (
    Path("reports") / "lab-summary" / "day75_manual_review_approval_envelope.html"
)
DAY76_RUNTIME_AUDIT_TRAIL_TASK_ID = "runtime-audit-trail"
DAY76_RUNTIME_AUDIT_TRAIL_DOC = Path("docs") / "ai" / "intent_runtime_audit_trail.md"
DAY76_RUNTIME_AUDIT_TRAIL_ROADMAP = Path("docs") / "roadmap" / "day76_runtime_audit_trail.md"
DAY76_RUNTIME_AUDIT_TRAIL_JSON = Path("reports") / "lab-summary" / "day76_runtime_audit_trail.json"
DAY76_RUNTIME_AUDIT_TRAIL_HTML = Path("reports") / "lab-summary" / "day76_runtime_audit_trail.html"
DAY77_RUNTIME_SAFETY_GATE_TASK_ID = "runtime-safety-gate"
DAY77_RUNTIME_SAFETY_GATE_DOC = Path("docs") / "ai" / "intent_runtime_safety_gate.md"
DAY77_RUNTIME_SAFETY_GATE_ROADMAP = Path("docs") / "roadmap" / "day77_runtime_safety_gate.md"
DAY77_RUNTIME_SAFETY_GATE_JSON = Path("reports") / "lab-summary" / "day77_runtime_safety_gate.json"
DAY77_RUNTIME_SAFETY_GATE_HTML = Path("reports") / "lab-summary" / "day77_runtime_safety_gate.html"
DAY78_RUNTIME_SAFETY_CASE_TASK_ID = "runtime-safety-case"
DAY78_RUNTIME_SAFETY_CASE_DOC = Path("docs") / "ai" / "intent_runtime_safety_case.md"
DAY78_RUNTIME_SAFETY_CASE_ROADMAP = Path("docs") / "roadmap" / "day78_runtime_safety_case.md"
DAY78_RUNTIME_SAFETY_CASE_JSON = Path("reports") / "lab-summary" / "day78_runtime_safety_case.json"
DAY78_RUNTIME_SAFETY_CASE_HTML = Path("reports") / "lab-summary" / "day78_runtime_safety_case.html"
DAY79_READONLY_TASK_CONTRACT_TASK_ID = "readonly-task-contract"
DAY79_READONLY_TASK_CONTRACT_DOC = Path("docs") / "ai" / "intent_readonly_task_contract.md"
DAY79_READONLY_TASK_CONTRACT_ROADMAP = Path("docs") / "roadmap" / "day79_readonly_task_contract.md"
DAY79_READONLY_TASK_CONTRACT_JSON = Path("reports") / "lab-summary" / "day79_readonly_task_contract.json"
DAY79_READONLY_TASK_CONTRACT_HTML = Path("reports") / "lab-summary" / "day79_readonly_task_contract.html"
DAY80_READONLY_EXECUTION_BROKER_TASK_ID = "readonly-execution-broker"
DAY80_READONLY_EXECUTION_BROKER_DOC = Path("docs") / "ai" / "intent_readonly_execution_broker.md"
DAY80_READONLY_EXECUTION_BROKER_ROADMAP = (
    Path("docs") / "roadmap" / "day80_readonly_execution_broker_skeleton.md"
)
DAY80_READONLY_EXECUTION_BROKER_JSON = Path("reports") / "lab-summary" / "day80_readonly_execution_broker.json"
DAY80_READONLY_EXECUTION_BROKER_HTML = Path("reports") / "lab-summary" / "day80_readonly_execution_broker.html"
DAY81_BROKER_REVIEW_QUEUE_TASK_ID = "broker-review-queue"
DAY81_BROKER_REVIEW_QUEUE_DOC = Path("docs") / "ai" / "intent_broker_review_queue.md"
DAY81_BROKER_REVIEW_QUEUE_ROADMAP = Path("docs") / "roadmap" / "day81_broker_review_queue.md"
DAY81_BROKER_REVIEW_QUEUE_JSON = Path("reports") / "lab-summary" / "day81_broker_review_queue.json"
DAY81_BROKER_REVIEW_QUEUE_HTML = Path("reports") / "lab-summary" / "day81_broker_review_queue.html"
DAY82_REVIEWER_DECISION_AUDIT_TASK_ID = "reviewer-decision-audit-summary"
DAY82_REVIEWER_DECISION_AUDIT_DOC = Path("docs") / "ai" / "intent_reviewer_decision_audit_summary.md"
DAY82_REVIEWER_DECISION_AUDIT_ROADMAP = (
    Path("docs") / "roadmap" / "day82_reviewer_decision_audit_summary.md"
)
DAY82_REVIEWER_DECISION_AUDIT_JSON = (
    Path("reports") / "lab-summary" / "day82_reviewer_decision_audit_summary.json"
)
DAY82_REVIEWER_DECISION_AUDIT_HTML = (
    Path("reports") / "lab-summary" / "day82_reviewer_decision_audit_summary.html"
)
DAY83_READONLY_EXECUTOR_READINESS_GATE_TASK_ID = "readonly-executor-readiness-gate"
DAY83_READONLY_EXECUTOR_READINESS_GATE_DOC = (
    Path("docs") / "ai" / "readonly_executor_readiness_gate.md"
)
DAY83_READONLY_EXECUTOR_READINESS_GATE_ROADMAP = (
    Path("docs") / "roadmap" / "day83_readonly_executor_readiness_gate.md"
)
DAY83_READONLY_EXECUTOR_READINESS_GATE_JSON = (
    Path("reports") / "lab-summary" / "day83_readonly_executor_readiness_gate.json"
)
DAY83_READONLY_EXECUTOR_READINESS_GATE_HTML = (
    Path("reports") / "lab-summary" / "day83_readonly_executor_readiness_gate.html"
)
DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_TASK_ID = "readonly-executor-adapter-contract"
DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_DOC = (
    Path("docs") / "ai" / "intent_readonly_executor_adapter_contract.md"
)
DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_ROADMAP = (
    Path("docs") / "roadmap" / "day84_readonly_executor_adapter_interface_contract.md"
)
DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_JSON = (
    Path("reports") / "lab-summary" / "day84_readonly_executor_adapter_contract.json"
)
DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_HTML = (
    Path("reports") / "lab-summary" / "day84_readonly_executor_adapter_contract.html"
)
DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_TASK_ID = "mock-adapter-evidence-binding"
DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_DOC = (
    Path("docs") / "ai" / "intent_mock_adapter_evidence_binding.md"
)
DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_ROADMAP = (
    Path("docs") / "roadmap" / "day85_mock_adapter_evidence_binding.md"
)
DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_JSON = (
    Path("reports") / "lab-summary" / "day85_mock_adapter_evidence_binding.json"
)
DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_HTML = (
    Path("reports") / "lab-summary" / "day85_mock_adapter_evidence_binding.html"
)
DAY86_CONTROLLED_RUNNER_HARNESS_TASK_ID = "controlled-runner-harness"
DAY86_CONTROLLED_RUNNER_HARNESS_DOC = (
    Path("docs") / "ai" / "intent_controlled_runner_harness.md"
)
DAY86_CONTROLLED_RUNNER_HARNESS_ROADMAP = (
    Path("docs") / "roadmap" / "day86_controlled_runner_harness_safety_regression.md"
)
DAY86_CONTROLLED_RUNNER_HARNESS_JSON = (
    Path("reports") / "lab-summary" / "day86_controlled_runner_harness.json"
)
DAY86_CONTROLLED_RUNNER_HARNESS_HTML = (
    Path("reports") / "lab-summary" / "day86_controlled_runner_harness.html"
)
DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_TASK_ID = "readonly-executor-phase-gate-review"
DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_DOC = (
    Path("docs") / "ai" / "intent_readonly_executor_phase_gate_review.md"
)
DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_ROADMAP = (
    Path("docs") / "roadmap" / "day87_readonly_executor_phase_gate_review.md"
)
DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_JSON = (
    Path("reports") / "lab-summary" / "day87_readonly_executor_phase_gate_review.json"
)
DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_HTML = (
    Path("reports") / "lab-summary" / "day87_readonly_executor_phase_gate_review.html"
)
DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_TASK_ID = "readonly-executor-adapter-design"
DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_DOC = (
    Path("docs") / "ai" / "intent_real_readonly_executor_adapter_design.md"
)
DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_ROADMAP = (
    Path("docs") / "roadmap" / "day88_real_readonly_executor_adapter_design.md"
)
DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_JSON = (
    Path("reports") / "lab-summary" / "day88_real_readonly_executor_adapter_design.json"
)
DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_HTML = (
    Path("reports") / "lab-summary" / "day88_real_readonly_executor_adapter_design.html"
)
DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_TASK_ID = "real-adapter-safety-boundary-spec"
DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_DOC = (
    Path("docs") / "ai" / "real_adapter_safety_boundary_spec.md"
)
DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_ROADMAP = (
    Path("docs") / "roadmap" / "day89_real_adapter_safety_boundary_spec.md"
)
DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_JSON = (
    Path("reports") / "lab-summary" / "day89_real_adapter_safety_boundary_spec.json"
)
DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_HTML = (
    Path("reports") / "lab-summary" / "day89_real_adapter_safety_boundary_spec.html"
)
DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_TASK_ID = "real-adapter-implementation-plan"
DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_DOC = (
    Path("docs") / "ai" / "intent_real_adapter_implementation_plan.md"
)
DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_ROADMAP = (
    Path("docs") / "roadmap" / "day90_real_adapter_implementation_plan.md"
)
DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_JSON = (
    Path("reports") / "lab-summary" / "day90_real_adapter_implementation_plan.json"
)
DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_HTML = (
    Path("reports") / "lab-summary" / "day90_real_adapter_implementation_plan.html"
)
DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_TASK_ID = "real-adapter-safety-scaffold"
DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_DOC = (
    Path("docs") / "ai" / "intent_real_adapter_safety_scaffold.md"
)
DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_ROADMAP = (
    Path("docs") / "roadmap" / "day91_real_adapter_safety_scaffold.md"
)
DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_JSON = (
    Path("reports") / "lab-summary" / "day91_real_adapter_safety_scaffold.json"
)
DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_HTML = (
    Path("reports") / "lab-summary" / "day91_real_adapter_safety_scaffold.html"
)
DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_TASK_ID = "real-adapter-executable-guards"
DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_DOC = (
    Path("docs") / "ai" / "intent_executable_guards.md"
)
DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_ROADMAP = (
    Path("docs") / "roadmap" / "day92_real_adapter_executable_guards.md"
)
DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_JSON = (
    Path("reports") / "lab-summary" / "day92_real_adapter_executable_guards_report.json"
)
DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_HTML = (
    Path("reports") / "lab-summary" / "day92_real_adapter_executable_guards_report.html"
)
DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_TASK_ID = "guarded-fake-adapter-contract"
DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_DOC = (
    Path("docs") / "ai" / "intent_guarded_fake_adapter_contract.md"
)
DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_ROADMAP = (
    Path("docs") / "roadmap" / "day93_guarded_fake_adapter_contract.md"
)
DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_JSON = (
    Path("reports") / "lab-summary" / "day93_guarded_fake_adapter_contract.json"
)
DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_HTML = (
    Path("reports") / "lab-summary" / "day93_guarded_fake_adapter_contract.html"
)
DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_TASK_ID = "adapter-boundary-regression-matrix"
DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_DOC = (
    Path("docs") / "ai" / "intent_adapter_boundary_regression_matrix.md"
)
DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_ROADMAP = (
    Path("docs") / "roadmap" / "day94_adapter_boundary_regression_matrix.md"
)
DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_JSON = (
    Path("reports") / "lab-summary" / "day94_adapter_boundary_regression_matrix.json"
)
DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_HTML = (
    Path("reports") / "lab-summary" / "day94_adapter_boundary_regression_matrix.html"
)
DAY95_ADAPTER_RESULT_NORMALIZATION_TASK_ID = "adapter-result-normalization"
DAY95_ADAPTER_RESULT_NORMALIZATION_DOC = (
    Path("docs") / "ai" / "intent_adapter_result_normalization.md"
)
DAY95_ADAPTER_RESULT_NORMALIZATION_ROADMAP = (
    Path("docs") / "roadmap" / "day95_adapter_result_normalization.md"
)
DAY95_ADAPTER_RESULT_NORMALIZATION_JSON = (
    Path("reports") / "lab-summary" / "day95_adapter_result_normalization.json"
)
DAY95_ADAPTER_RESULT_NORMALIZATION_HTML = (
    Path("reports") / "lab-summary" / "day95_adapter_result_normalization.html"
)
DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_TASK_ID = "readonly-output-parser-prototype"
DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_DOC = (
    Path("docs") / "ai" / "readonly_output_parser_prototype.md"
)
DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_ROADMAP = (
    Path("docs") / "roadmap" / "day96_readonly_output_parser_prototype.md"
)
DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_JSON = (
    Path("reports") / "lab-summary" / "day96_readonly_output_parser_prototype.json"
)
DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_HTML = (
    Path("reports") / "lab-summary" / "day96_readonly_output_parser_prototype.html"
)
DAY97_PARSER_EVIDENCE_QUALITY_TASK_ID = "parser-evidence-quality"
DAY97_PARSER_EVIDENCE_QUALITY_DOC = (
    Path("docs") / "ai" / "intent_parser_evidence_quality.md"
)
DAY97_PARSER_EVIDENCE_QUALITY_ROADMAP = (
    Path("docs") / "roadmap" / "day97_parser_evidence_quality_unsupported_output_case_hardening.md"
)
DAY97_PARSER_EVIDENCE_QUALITY_JSON = (
    Path("reports") / "ai" / "day97_parser_evidence_quality_report.json"
)
DAY97_PARSER_EVIDENCE_QUALITY_HTML = (
    Path("reports") / "ai" / "day97_parser_evidence_quality_report.html"
)
DAY98_PARSER_CLASSIFICATION_MATRIX_TASK_ID = "parser-classification-matrix"
DAY98_PARSER_CLASSIFICATION_MATRIX_DOC = (
    Path("docs") / "ai-intent" / "day98_parser_classification_matrix.md"
)
DAY98_PARSER_CLASSIFICATION_MATRIX_JSON = (
    Path("reports") / "ai" / "day98_parser_classification_matrix.json"
)
DAY98_PARSER_CLASSIFICATION_MATRIX_HTML = (
    Path("reports") / "ai" / "day98_parser_classification_matrix.html"
)
DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_TASK_ID = "parser-evidence-coverage-audit"
DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_DOC = (
    Path("docs") / "ai-intent" / "day99_parser_evidence_coverage_audit.md"
)
DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_ROADMAP = (
    Path("docs") / "roadmap" / "day99_parser_evidence_coverage_sample_gap_audit.md"
)
DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_JSON = (
    Path("reports") / "ai" / "day99_parser_evidence_coverage_audit.json"
)
DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_HTML = (
    Path("reports") / "ai" / "day99_parser_evidence_coverage_audit.html"
)
DAY100_PARSER_PHASE_GATE_REVIEW_TASK_ID = "parser-phase-gate-review"
DAY100_PARSER_PHASE_GATE_REVIEW_DOC = (
    Path("docs") / "ai-intent" / "day100_parser_phase_gate_review.md"
)
DAY100_PARSER_PHASE_GATE_REVIEW_ROADMAP = (
    Path("docs") / "roadmap" / "day100_parser_phase_gate_review_readiness_decision.md"
)
DAY100_PARSER_PHASE_GATE_REVIEW_JSON = (
    Path("reports") / "ai" / "day100_parser_phase_gate_review.json"
)
DAY100_PARSER_PHASE_GATE_REVIEW_HTML = (
    Path("reports") / "ai" / "day100_parser_phase_gate_review.html"
)
DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_TASK_ID = "parser-evidence-closure-plan"
DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_DOC = (
    Path("docs") / "ai-intent" / "day101_parser_evidence_closure_plan.md"
)
DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_ROADMAP = (
    Path("docs") / "roadmap" / "day101_parser_evidence_closure_plan.md"
)
DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_JSON = (
    Path("reports") / "ai" / "day101_parser_evidence_closure_plan.json"
)
DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_HTML = (
    Path("reports") / "ai" / "day101_parser_evidence_closure_plan.html"
)
DAY102_PARSER_FIXTURE_EXPANSION_TASK_ID = "parser-fixture-expansion"
DAY102_PARSER_FIXTURE_EXPANSION_DOC = (
    Path("docs") / "ai-intent" / "day102_parser_fixture_expansion.md"
)
DAY102_PARSER_FIXTURE_EXPANSION_ROADMAP = (
    Path("docs") / "roadmap" / "day102_parser_fixture_expansion.md"
)
DAY102_PARSER_FIXTURE_EXPANSION_JSON = (
    Path("reports") / "ai" / "day102_parser_fixture_expansion.json"
)
DAY102_PARSER_FIXTURE_EXPANSION_HTML = (
    Path("reports") / "ai" / "day102_parser_fixture_expansion.html"
)
DAY103_PARSER_EVIDENCE_MATRIX_TASK_ID = "parser-evidence-matrix-gap-traceability"
DAY103_PARSER_EVIDENCE_MATRIX_DOC = (
    Path("docs") / "ai-intent" / "day103_parser_evidence_matrix_gap_traceability.md"
)
DAY103_PARSER_EVIDENCE_MATRIX_ROADMAP = (
    Path("docs") / "roadmap" / "day103_parser_evidence_matrix_gap_traceability.md"
)
DAY103_PARSER_EVIDENCE_MATRIX_JSON = (
    Path("reports") / "ai" / "day103_parser_evidence_matrix_gap_traceability.json"
)
DAY103_PARSER_EVIDENCE_MATRIX_HTML = (
    Path("reports") / "ai" / "day103_parser_evidence_matrix_gap_traceability.html"
)
DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_TASK_ID = "parser-reviewer-acceptance-gate"
DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_DOC = (
    Path("docs") / "ai-intent" / "day104_parser_reviewer_acceptance_gate.md"
)
DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_ROADMAP = (
    Path("docs") / "roadmap" / "day104_parser_reviewer_acceptance_gate.md"
)
DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_JSON = (
    Path("reports") / "lab-summary" / "day104_parser_reviewer_acceptance_gate.json"
)
DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_HTML = (
    Path("reports") / "lab-summary" / "day104_parser_reviewer_acceptance_gate.html"
)
DAY105_PARSER_ACCEPTANCE_CLOSURE_TASK_ID = "parser-acceptance-closure"
DAY105_PARSER_ACCEPTANCE_CLOSURE_DOC = (
    Path("docs") / "ai-intent" / "day105_parser_acceptance_closure.md"
)
DAY105_PARSER_ACCEPTANCE_CLOSURE_REVIEWER_DOC = (
    Path("docs") / "reviewer" / "day105_parser_acceptance_closure.md"
)
DAY105_PARSER_ACCEPTANCE_CLOSURE_ROADMAP = (
    Path("docs") / "roadmap" / "day105_parser_acceptance_closure.md"
)
DAY105_PARSER_ACCEPTANCE_CLOSURE_JSON = (
    Path("reports") / "lab-summary" / "day105_parser_acceptance_closure.json"
)
DAY105_PARSER_ACCEPTANCE_CLOSURE_HTML = (
    Path("reports") / "lab-summary" / "day105_parser_acceptance_closure.html"
)
DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_TASK_ID = "codex-agents-instruction-audit"
DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_DOC = (
    Path("docs") / "ai-intent" / "day106_codex_agents_instruction_compliance_audit.md"
)
DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_ROADMAP = (
    Path("docs") / "roadmap" / "day106_codex_agents_instruction_compliance_audit.md"
)
DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_JSON = (
    Path("reports") / "ai" / "day106_codex_agents_instruction_compliance_audit.json"
)
DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_HTML = (
    Path("reports") / "ai" / "day106_codex_agents_instruction_compliance_audit.html"
)
DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_TASK_ID = "parser-reviewer-evidence-contract"
DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_DOC = (
    Path("docs") / "ai-intent" / "day107_parser_reviewer_evidence_contract.md"
)
DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_ROADMAP = (
    Path("docs") / "roadmap" / "day107_parser_reviewer_evidence_contract.md"
)
DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_JSON = (
    Path("reports") / "lab-summary" / "day107_parser_reviewer_evidence_contract.json"
)
DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_HTML = (
    Path("reports") / "lab-summary" / "day107_parser_reviewer_evidence_contract.html"
)
DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_TASK_ID = "parser-contract-consumer-handoff"
DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_DOC = (
    Path("docs") / "ai-intent" / "day108_parser_contract_consumer_handoff.md"
)
DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_ROADMAP = (
    Path("docs") / "roadmap" / "day108_parser_contract_consumer_handoff.md"
)
DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_JSON = (
    Path("reports") / "lab-summary" / "day108_parser_contract_consumer_handoff.json"
)
DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_HTML = (
    Path("reports") / "lab-summary" / "day108_parser_contract_consumer_handoff.html"
)
DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_TASK_ID = (
    "parser-consumer-handoff-readiness-matrix"
)
DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_DOC = (
    Path("docs") / "ai-intent" / "day109_parser_consumer_handoff_readiness_matrix.md"
)
DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_JSON = (
    Path("reports") / "lab-summary" / "day109_parser_consumer_handoff_readiness_matrix.json"
)
DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_HTML = (
    Path("reports") / "lab-summary" / "day109_parser_consumer_handoff_readiness_matrix.html"
)
DAY110_PARSER_CONSUMER_FINAL_GATE_TASK_ID = "parser-consumer-final-gate"
DAY110_PARSER_CONSUMER_FINAL_GATE_DOC = (
    Path("docs") / "ai-intent" / "day110_parser_consumer_final_gate.md"
)
DAY110_PARSER_CONSUMER_FINAL_GATE_JSON = (
    Path("reports") / "lab-summary" / "day110_parser_consumer_final_gate.json"
)
DAY110_PARSER_CONSUMER_FINAL_GATE_HTML = (
    Path("reports") / "lab-summary" / "day110_parser_consumer_final_gate.html"
)
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_TASK_ID = "parser-consumer-release-package"
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_DOC = (
    Path("docs") / "ai-intent" / "day111_parser_consumer_release_package.md"
)
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_REVIEWER_DOC = (
    Path("docs") / "ai-intent" / "reviewer" / "day111_parser_consumer_release_package.md"
)
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day111_parser_consumer_release_package.md"
)
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_JSON = (
    Path("reports") / "lab-summary" / "day111_parser_consumer_release_package.json"
)
DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_HTML = (
    Path("reports") / "lab-summary" / "day111_parser_consumer_release_package.html"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_TASK_ID = (
    "parser-consumer-release-review-intake"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_DOC = (
    Path("docs") / "ai-intent" / "day112_parser_consumer_release_review_intake.md"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_REVIEWER_DOC = (
    Path("docs") / "ai-intent" / "reviewer" / "day112_parser_consumer_release_review_intake.md"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day112_parser_consumer_release_review_intake.md"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_JSON = (
    Path("reports") / "lab-summary" / "day112_parser_consumer_release_review_intake.json"
)
DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_HTML = (
    Path("reports") / "lab-summary" / "day112_parser_consumer_release_review_intake.html"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_TASK_ID = (
    "parser-consumer-reviewer-triage-decision-log"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_DOC = (
    Path("docs") / "ai-intent" / "day113_parser_consumer_reviewer_triage_decision_log.md"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_REVIEWER_DOC = (
    Path("docs") / "ai-intent" / "reviewer" / "day113_parser_consumer_reviewer_triage_decision_log.md"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day113_parser_consumer_reviewer_triage_decision_log.md"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_JSON = (
    Path("reports") / "lab-summary" / "day113_parser_consumer_reviewer_triage_decision_log.json"
)
DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_HTML = (
    Path("reports") / "lab-summary" / "day113_parser_consumer_reviewer_triage_decision_log.html"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_TASK_ID = (
    "parser-consumer-reviewer-triage-evidence-traceability"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_DOC = (
    Path("docs") / "ai-intent" / "day114_parser_consumer_reviewer_triage_evidence_traceability.md"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_REVIEWER_DOC = (
    Path("docs") / "ai-intent" / "reviewer" / "day114_parser_consumer_reviewer_triage_evidence_traceability.md"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day114_parser_consumer_reviewer_triage_evidence_traceability.md"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_JSON = (
    Path("reports") / "lab-summary" / "day114_parser_consumer_reviewer_triage_evidence_traceability.json"
)
DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_HTML = (
    Path("reports") / "lab-summary" / "day114_parser_consumer_reviewer_triage_evidence_traceability.html"
)
DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_TASK_ID = (
    "parser-consumer-reviewer-triage-closure-summary"
)
DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_DOC = (
    Path("docs") / "ai-intent" / "day115_parser_consumer_reviewer_triage_closure_summary.md"
)
DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day115_parser_consumer_reviewer_triage_closure_summary.md"
)
DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_JSON = (
    Path("reports") / "lab-summary" / "day115_parser_consumer_reviewer_triage_closure_summary.json"
)
DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_HTML = (
    Path("reports") / "lab-summary" / "day115_parser_consumer_reviewer_triage_closure_summary.html"
)
DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_TASK_ID = "reviewer-deferred-action-register"
DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_DOC = (
    Path("docs") / "ai-intent" / "day116_reviewer_deferred_action_register.md"
)
DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day116_reviewer_deferred_action_register.md"
)
DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_JSON = (
    Path("reports") / "lab-summary" / "day116_reviewer_deferred_action_register.json"
)
DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_HTML = (
    Path("reports") / "lab-summary" / "day116_reviewer_deferred_action_register.html"
)
DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_TASK_ID = "deferred-action-traceability-review"
DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_DOC = (
    Path("docs") / "ai-intent" / "day117_deferred_action_traceability_review.md"
)
DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day117_deferred_action_traceability_review.md"
)
DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_JSON = (
    Path("reports") / "lab-summary" / "day117_deferred_action_traceability_review.json"
)
DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_HTML = (
    Path("reports") / "lab-summary" / "day117_deferred_action_traceability_review.html"
)
DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_TASK_ID = "deferred-action-review-sequence-runbook"
DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_DOC = (
    Path("docs") / "ai-intent" / "day118_deferred_action_review_sequence_runbook.md"
)
DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day118_deferred_action_review_sequence_runbook.md"
)
DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_JSON = (
    Path("reports") / "lab-summary" / "day118_deferred_action_review_sequence_runbook.json"
)
DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_HTML = (
    Path("reports") / "lab-summary" / "day118_deferred_action_review_sequence_runbook.html"
)
DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_TASK_ID = "reviewer-evidence-intake-outcome-ledger"
DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_DOC = (
    Path("docs") / "ai-intent" / "day119_reviewer_evidence_intake_outcome_ledger.md"
)
DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day119_reviewer_evidence_intake_outcome_ledger.md"
)
DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_JSON = (
    Path("reports") / "lab-summary" / "day119_reviewer_evidence_intake_outcome_ledger.json"
)
DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_HTML = (
    Path("reports") / "lab-summary" / "day119_reviewer_evidence_intake_outcome_ledger.html"
)
DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_TASK_ID = "safety-boundary-regression-matrix"
DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_DOC = (
    Path("docs") / "ai-intent" / "day123_safety_boundary_regression_matrix.md"
)
DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day123_safety_boundary_regression_matrix.md"
)
DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_JSON = (
    Path("reports") / "lab-summary" / "day123_safety_boundary_regression_matrix.json"
)
DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_HTML = (
    Path("reports") / "lab-summary" / "day123_safety_boundary_regression_matrix.html"
)
DAY124_SAFETY_INVARIANT_HELPER_REVIEW_TASK_ID = "safety-invariant-helper-review"
DAY124_SAFETY_INVARIANT_HELPER_REVIEW_DOC = (
    Path("docs") / "ai-intent" / "day124_safety_invariant_helper_consolidation.md"
)
DAY124_SAFETY_INVARIANT_HELPER_REVIEW_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day124_safety_invariant_helper_consolidation.md"
)
DAY124_SAFETY_INVARIANT_HELPER_REVIEW_JSON = (
    Path("reports") / "lab-summary" / "day124_safety_invariant_helper_review.json"
)
DAY124_SAFETY_INVARIANT_HELPER_REVIEW_HTML = (
    Path("reports") / "lab-summary" / "day124_safety_invariant_helper_review.html"
)
DAY125_THIN_CLI_REGRESSION_GATE_TASK_ID = "thin-cli-regression-gate"
DAY125_THIN_CLI_REGRESSION_GATE_DOC = (
    Path("docs") / "ai-intent" / "day125_thin_cli_regression_gate.md"
)
DAY125_THIN_CLI_REGRESSION_GATE_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day125_thin_cli_regression_gate.md"
)
DAY125_THIN_CLI_REGRESSION_GATE_JSON = (
    Path("reports") / "lab-summary" / "day125_thin_cli_regression_gate.json"
)
DAY125_THIN_CLI_REGRESSION_GATE_HTML = (
    Path("reports") / "lab-summary" / "day125_thin_cli_regression_gate.html"
)
DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_TASK_ID = (
    "post-refactor-compatibility-evidence-pack"
)
DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_DOC = (
    Path("docs") / "ai-intent" / "day126_post_refactor_compatibility_evidence_pack.md"
)
DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day126_post_refactor_compatibility_evidence_pack.md"
)
DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_JSON = (
    Path("reports") / "lab-summary" / "day126_post_refactor_compatibility_evidence_pack.json"
)
DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_HTML = (
    Path("reports") / "lab-summary" / "day126_post_refactor_compatibility_evidence_pack.html"
)
DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_TASK_ID = "ai-reviewer-summary-schema-contract"
DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_DOC = (
    Path("docs") / "ai-intent" / "day127_ai_reviewer_summary_schema_contract.md"
)
DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day127_ai_reviewer_summary_schema_contract.md"
)
DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_JSON = (
    Path("reports") / "lab-summary" / "day127_ai_reviewer_summary_schema_contract.json"
)
DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_HTML = (
    Path("reports") / "lab-summary" / "day127_ai_reviewer_summary_schema_contract.html"
)
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TASK_ID = "ai-reviewer-summary-fixture-renderer"
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_DOC = (
    Path("docs") / "ai-intent" / "day128_ai_reviewer_summary_fixture_renderer.md"
)
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day128_ai_reviewer_summary_fixture_renderer.md"
)
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_JSON = (
    Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.json"
)
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_HTML = (
    Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.html"
)
DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TXT = (
    Path("reports") / "lab-summary" / "day128_ai_reviewer_summary_fixture_renderer.txt"
)
DAY129_AI_SUMMARY_PROMPT_CONTRACT_TASK_ID = "ai-summary-prompt-contract"
DAY129_AI_SUMMARY_PROMPT_CONTRACT_DOC = (
    Path("docs") / "ai-intent" / "day129_ai_summary_prompt_contract.md"
)
DAY129_AI_SUMMARY_PROMPT_CONTRACT_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day129_ai_summary_prompt_contract.md"
)
DAY129_AI_SUMMARY_PROMPT_CONTRACT_JSON = (
    Path("reports") / "lab-summary" / "day129_ai_summary_prompt_contract.json"
)
DAY129_AI_SUMMARY_PROMPT_CONTRACT_HTML = (
    Path("reports") / "lab-summary" / "day129_ai_summary_prompt_contract.html"
)
DAY130_AI_SUMMARY_REDACTION_POLICY_TASK_ID = "ai-summary-redaction-and-no-secret-policy"
DAY130_AI_SUMMARY_REDACTION_POLICY_DOC = (
    Path("docs") / "ai-intent" / "day130_ai_summary_redaction_and_no_secret_policy.md"
)
DAY130_AI_SUMMARY_REDACTION_POLICY_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day130_ai_summary_redaction_and_no_secret_policy.md"
)
DAY130_AI_SUMMARY_REDACTION_POLICY_FIXTURE = (
    Path("fixtures") / "day130_ai_summary_redaction_policy.example.json"
)
DAY130_AI_SUMMARY_REDACTION_POLICY_JSON = (
    Path("reports") / "lab-summary" / "day130_ai_summary_redaction_and_no_secret_policy.json"
)
DAY130_AI_SUMMARY_REDACTION_POLICY_HTML = (
    Path("reports") / "lab-summary" / "day130_ai_summary_redaction_and_no_secret_policy.html"
)
DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_TASK_ID = "ai-summary-audit-trail-binding"
DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_DOC = (
    Path("docs") / "ai-intent" / "day131_ai_summary_audit_trail_binding.md"
)
DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_ROADMAP_DOC = (
    Path("docs") / "roadmap" / "day131_ai_summary_audit_trail_binding.md"
)
DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_JSON = (
    Path("reports") / "lab-summary" / "day131_ai_summary_audit_trail_binding.json"
)
DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_HTML = (
    Path("reports") / "lab-summary" / "day131_ai_summary_audit_trail_binding.html"
)
WIREGUARD_RUNNER_TASK_ALIAS = "wireguard-runner"
WIREGUARD_RUNNER_TASK_ID = "wireguard_runner_safety_layer"
WIREGUARD_RUNNER_DISPLAY_NAME = "WireGuard Runner Safety Layer"
WIREGUARD_RUNNER_REPORT_JSON = Path("reports") / "lab-summary" / "wireguard_runner_safety_layer.json"
WIREGUARD_RUNNER_REPORT_HTML = Path("reports") / "lab-summary" / "wireguard_runner_safety_layer.html"
DAY12_WIREGUARD_REPORT_JSON_NAME = "day12_wireguard_vpn_automation_report.json"
DAY12_WIREGUARD_REPORT_HTML_NAME = "day12_wireguard_vpn_automation_report.html"
SECRET_FIELD_MARKERS = ("secret", "password", "private_key", "preshared_key", "token", "key")
DAY17_REPORT_INDEX_HTML = Path("reports") / "report_index.html"
DAY19_EVIDENCE_INDEX_JSON = Path("reports") / "portfolio" / "day19_runner_evidence_index.json"
DAY19_EVIDENCE_INDEX_HTML = Path("reports") / "portfolio" / "day19_runner_evidence_index.html"
DAY24_DEMO_FLOW_JSON = Path("reports") / "portfolio" / "day24_rc_demo_flow.json"
DAY24_DEMO_FLOW_HTML = Path("reports") / "portfolio" / "day24_rc_demo_flow.html"
RESULTS = {"PASS", "FAIL", "WARN", "MISSING", "INCOMPLETE", "UNKNOWN", "SKIP", "NOT_RUN", "NOT_GENERATED"}
INTERACTIVE_ACTION_COMPLETE = (
    "Action complete. Returning to menu. Choose another option or enter 0 to exit."
)
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_COLORS = {
    "cyan": "\033[36m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "gray": "\033[90m",
}
STATUS_COLORS = {
    "PASS": "green",
    "FAIL": "red",
    "WARN": "yellow",
    "MISSING": "gray",
    "INCOMPLETE": "yellow",
    "UNKNOWN": "magenta",
    "SKIP": "blue",
    "NOT_RUN": "blue",
    "NOT_GENERATED": "yellow",
}
LIVE_WORKFLOW_RECOMMENDATIONS = {
    "day4": {
        "title": "Day4 multi-device baseline",
        "command": "python mikrotik_day4_multi_device_baseline.py",
        "reminder": "This is a live SSH validation workflow. Review config first and run it manually.",
    },
    "day8": {
        "title": "Day8 iperf3 performance workflow",
        "command": "python performance_test.py --profile topology_profiles/day8_iperf3_router_performance.json",
        "reminder": "This workflow depends on lab reachability and iperf3 readiness. Run it manually with the correct direction/profile.",
    },
    "wireguard_runner": {
        "title": WIREGUARD_RUNNER_DISPLAY_NAME,
        "command": "python network_lab.py --task wireguard-runner --dry-run",
        "reminder": "This may validate live WireGuard and iperf3 state. Confirm the client, LAN host, and secrets stay local before running.",
    },
    "day13": {
        "title": "Day13 multi-router WireGuard summary",
        "command": "Run the Day13 multi-router WireGuard summary workflow, then run: python network_lab.py --task report-index",
        "reminder": "Day13 live or summary generation is not executed by Day14 Phase 2. Use the Day13 workflow manually first.",
    },
}

SAFETY_LEVELS = {
    "report-only": "Local report viewing, summary generation, dry-run output, or existing report indexing.",
    "read-only": "Live device checks that read state without changing configuration.",
    "guarded-live": "Live validation delegated only after explicit runner action, confirmation, or guard flag.",
    "controlled_failover_observation": "Live read-only HA observation where the failure trigger is manual and external.",
    "dry-run": "Planned-action preview that does not connect to devices or start live checks.",
    "disabled": "Placeholder or blocked workflow that is intentionally not available from the runner.",
    "safety-review": "Dry-run/report-only intent safety classification with blocked-by-default confirmation gate design.",
}

DAY58_SAFETY_BOUNDARIES = [
    "No OpenAI API connection.",
    "No voice control or speech API.",
    "No mapped task execution.",
    "No live network tests.",
    "No SSH sessions.",
    "No MikroTik, Cisco, router, switch, firewall, VPN, or real device connections.",
    "No config.json read, create, or modify action.",
    "No NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration changes.",
    "No release tag creation.",
]

DAY58_BLOCKED_LIVE_CAPABLE_ACTIONS = [
    "VRRP failover execution",
    "interface disable/enable",
    "firewall rule add/remove/change",
    "NAT change",
    "IP address change",
    "route change",
    "WireGuard peer add/remove/recreate",
    "router reboot/reset",
    "SSH command execution",
    "arbitrary shell command execution",
    "direct device configuration apply",
]

DAY58_CONFIRMATION_GATE_RULES = [
    "Report-only tasks may run without confirmation.",
    "Read-only tasks may require an explicit flag or human review depending on risk.",
    "Dry-run tasks may run only when they do not touch devices.",
    "Live-capable tasks must never execute directly from intent mapping.",
    "Any task capable of changing device or network state is blocked by default.",
    "Future live-capable execution requires explicit user confirmation, visible task preview, safety classification, blocked action check, non-default live flag, and a human-readable warning.",
    "Unknown intent is blocked.",
]

DAY59_INTENT_POLICY_MATRIX_ROWS = [
    {
        "intent_category": "Open dashboard / latest reports",
        "example_user_phrase": "Open the dashboard and show the latest reports",
        "mapped_task_type": "local UI / report-only",
        "candidate_task": "dashboard/report viewer or report-index",
        "safety_classification": "report_only",
        "default_decision": "allowed",
        "requires_confirmation": False,
        "allowed_to_execute_automatically": True,
        "mapped_task_execution_allowed": True,
        "reviewer_explanation": (
            "Opening local dashboard or report views reads existing local artifacts and does not touch live devices."
        ),
        "evidence_report_output": "Dashboard /reports page, reports/report_index.html, local report JSON/HTML files",
    },
    {
        "intent_category": "Show task catalog",
        "example_user_phrase": "Show me the available runner tasks",
        "mapped_task_type": "local metadata / report-only",
        "candidate_task": "--list-tasks",
        "safety_classification": "report_only",
        "default_decision": "allowed",
        "requires_confirmation": False,
        "allowed_to_execute_automatically": True,
        "mapped_task_execution_allowed": True,
        "reviewer_explanation": "Listing the task catalog prints committed runner metadata only.",
        "evidence_report_output": "network_lab.py --list-tasks output and task catalog metadata",
    },
    {
        "intent_category": "Generate report index",
        "example_user_phrase": "Generate the report index",
        "mapped_task_type": "report-only",
        "candidate_task": "report-index",
        "safety_classification": "report_only",
        "default_decision": "allowed",
        "requires_confirmation": False,
        "allowed_to_execute_automatically": True,
        "mapped_task_execution_allowed": True,
        "reviewer_explanation": "Report index generation scans local report metadata and writes summary JSON/HTML.",
        "evidence_report_output": "reports/report_index.json and reports/report_index.html",
    },
    {
        "intent_category": "Dry-run intent mapping",
        "example_user_phrase": "Map this request to a runner task, but dry-run only",
        "mapped_task_type": "dry-run proposal",
        "candidate_task": DAY57_INTENT_MAPPING_TASK_ID,
        "safety_classification": "dry_run",
        "default_decision": "allowed_dry_run_only",
        "requires_confirmation": False,
        "allowed_to_execute_automatically": True,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": (
            "Day57 may classify intent and propose an allowlisted task, but the proposed task is never executed."
        ),
        "evidence_report_output": "Day57 CLI JSON output and docs/ai/day57_intent_mapping_prototype.md",
    },
    {
        "intent_category": "Read-only safety review",
        "example_user_phrase": "Review whether this intent is safe",
        "mapped_task_type": "report-only safety explanation",
        "candidate_task": DAY58_INTENT_SAFETY_REVIEW_TASK_ID,
        "safety_classification": "report_only",
        "default_decision": "allowed",
        "requires_confirmation": False,
        "allowed_to_execute_automatically": True,
        "mapped_task_execution_allowed": True,
        "reviewer_explanation": "Day58 writes a local safety decision report and does not delegate to mapped tasks.",
        "evidence_report_output": DAY58_INTENT_SAFETY_REVIEW_JSON.as_posix(),
    },
    {
        "intent_category": "VRRP failover request",
        "example_user_phrase": "Do the VRRP failover test",
        "mapped_task_type": "live-capable network test",
        "candidate_task": DAY35_VRRP_FAILOVER_TASK_ID,
        "safety_classification": "blocked_live_capable",
        "default_decision": "blocked_by_default",
        "requires_confirmation": True,
        "allowed_to_execute_automatically": False,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": (
            "VRRP failover can affect network availability, so intent mapping may only identify it as a candidate."
        ),
        "evidence_report_output": "Day58 blocked policy match: VRRP failover execution",
    },
    {
        "intent_category": "WireGuard live validation request",
        "example_user_phrase": "Run the WireGuard validation",
        "mapped_task_type": "guarded-live capable validation",
        "candidate_task": WIREGUARD_RUNNER_TASK_ALIAS,
        "safety_classification": "blocked_live_capable",
        "default_decision": "blocked_by_default",
        "requires_confirmation": True,
        "allowed_to_execute_automatically": False,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": (
            "WireGuard validation may touch live VPN state or test endpoints, so it must not run from intent alone."
        ),
        "evidence_report_output": "Day57/Day58 dry-run mapping and safety review output",
    },
    {
        "intent_category": "SSH command request",
        "example_user_phrase": "SSH to the router and run this command",
        "mapped_task_type": "direct device access",
        "candidate_task": "blocked-live-capable-action",
        "safety_classification": "blocked_live_capable",
        "default_decision": "blocked_by_default",
        "requires_confirmation": True,
        "allowed_to_execute_automatically": False,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": "SSH and RouterOS command execution are outside Day59 scope and blocked by default.",
        "evidence_report_output": "Day58 blocked policy match: SSH command execution",
    },
    {
        "intent_category": "Router / switch configuration change request",
        "example_user_phrase": "Apply this router configuration change",
        "mapped_task_type": "device-changing action",
        "candidate_task": "blocked-live-capable-action",
        "safety_classification": "blocked_live_capable",
        "default_decision": "blocked_by_default",
        "requires_confirmation": True,
        "allowed_to_execute_automatically": False,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": (
            "Router, switch, firewall, VPN, NAT, IP, VRRP, WireGuard, interface, and route changes are blocked."
        ),
        "evidence_report_output": "Day58 blocked live-capable action policy",
    },
    {
        "intent_category": "Unknown or ambiguous request",
        "example_user_phrase": "Make everything better",
        "mapped_task_type": "no safe task mapped",
        "candidate_task": None,
        "safety_classification": "unknown_blocked",
        "default_decision": "blocked_or_requires_clarification",
        "requires_confirmation": True,
        "allowed_to_execute_automatically": False,
        "mapped_task_execution_allowed": False,
        "reviewer_explanation": "Ambiguous requests must stop for human clarification and must not execute any task.",
        "evidence_report_output": "Day57 unknown_or_ambiguous / Day58 unknown_blocked output",
    },
]

DAY59_REVIEWER_EXPLANATION = [
    "The system separates understanding intent from executing a task.",
    "Intent mapping is not permission to run the mapped task.",
    "Safety review happens before any future execution path.",
    "Report-only and documentation-only tasks may be allowed because they only read or write local evidence.",
    "Live-capable tasks require explicit human confirmation in future design and are blocked by default now.",
    "Voice input, OpenAI API calls, SSH, live device access, and device control are intentionally out of scope.",
]

DAY60_NO_EXECUTION_STATEMENT = (
    "No mapped task was executed. This is a dry-run reviewer walkthrough only."
)

DAY60_WORKFLOW_STEPS = [
    {
        "step": 1,
        "name": "Input intent text",
        "reviewer_view": "Reviewer reads a static example phrase. No microphone, speech API, or AI API is used.",
    },
    {
        "step": 2,
        "name": "Day57-style dry-run intent mapping",
        "reviewer_view": "The phrase is mapped to a proposed task or blocked category as report data only.",
    },
    {
        "step": 3,
        "name": "Day58-style safety review",
        "reviewer_view": "The mapped proposal is classified before any future execution path can exist.",
    },
    {
        "step": 4,
        "name": "Day59-style policy explanation",
        "reviewer_view": "The reviewer sees why report-only examples are allowed and live/configuration examples are blocked.",
    },
    {
        "step": 5,
        "name": "Reviewer decision",
        "reviewer_view": "The report records allowed or blocked as a human-readable decision.",
    },
    {
        "step": 6,
        "name": "No execution performed",
        "reviewer_view": DAY60_NO_EXECUTION_STATEMENT,
    },
]

DAY60_INTENT_WORKFLOW_DEMO_EXAMPLES = [
    {
        "input_intent_text": "show latest reports",
        "expected_classification": "report-only",
        "candidate_task": "report-index",
        "reviewer_decision": "allowed",
        "blocked": False,
        "policy_explanation": "Local report browsing or report index generation reads/writes local evidence only.",
    },
    {
        "input_intent_text": "explain available runner tasks",
        "expected_classification": "documentation/report-only",
        "candidate_task": "--list-tasks",
        "reviewer_decision": "allowed",
        "blocked": False,
        "policy_explanation": "Task catalog explanation uses committed runner metadata and documentation only.",
    },
    {
        "input_intent_text": "do VRRP failover test",
        "expected_classification": "live-capable",
        "candidate_task": DAY35_VRRP_FAILOVER_TASK_ID,
        "reviewer_decision": "blocked by default",
        "blocked": True,
        "policy_explanation": "VRRP failover can affect network availability and must not run from intent alone.",
    },
    {
        "input_intent_text": "change router firewall rule",
        "expected_classification": "configuration-changing",
        "candidate_task": "blocked-live-capable-action",
        "reviewer_decision": "blocked",
        "blocked": True,
        "policy_explanation": "Firewall and router configuration changes are blocked in the intent workflow.",
    },
    {
        "input_intent_text": "run WireGuard throughput test",
        "expected_classification": "live-capable",
        "candidate_task": WIREGUARD_RUNNER_TASK_ALIAS,
        "reviewer_decision": "blocked unless future guarded-live flow exists",
        "blocked": True,
        "policy_explanation": "WireGuard throughput validation may touch live VPN/test endpoints and requires a future explicit guarded-live flow.",
    },
]

REPORT_CATALOG = [
    {
        "day": "Day2",
        "title": "Day2 Auto Setup",
        "report_type": "Automation validation report",
        "safety_label": "live config evidence",
        "description": "Evidence from MikroTik setup automation; report index only reads generated JSON/HTML.",
        "json_globs": ["reports/**/day2*.json", "reports/**/*day2*auto*setup*.json"],
        "html_globs": ["reports/**/day2*.html", "reports/**/*day2*auto*setup*.html"],
    },
    {
        "day": "Day4",
        "title": "Day4 Baseline Validation",
        "report_type": "Multi-device baseline report",
        "safety_label": "live read-only evidence",
        "description": "RouterOS baseline checks gathered from existing reports; report index does not connect to devices.",
        "json_globs": ["reports/**/day4_baseline_validation.json", "reports/**/*day4*baseline*.json"],
        "html_globs": ["reports/**/day4_baseline_validation.html", "reports/**/*day4*baseline*.html"],
    },
    {
        "day": "Day5",
        "title": "Day5 Cisco Switch Topology",
        "report_type": "Topology validation report",
        "safety_label": "read-only evidence",
        "description": "Cisco switch topology validation evidence when local reports are available.",
        "json_globs": ["reports/**/*day5*cisco*.json", "reports/**/*cisco*topology*.json"],
        "html_globs": ["reports/**/*day5*cisco*.html", "reports/**/*cisco*topology*.html"],
        "missing_note": "Expected Cisco switch report was not found in local reports folder.",
    },
    {
        "day": "Day6",
        "title": "Day6 Lab Topology Summary",
        "report_type": "Lab topology summary",
        "safety_label": "report-only evidence",
        "description": "Local topology summary evidence for portfolio review.",
        "json_globs": ["reports/**/*day6*topology*.json", "summary/**/*day6*topology*.json"],
        "html_globs": ["reports/**/*day6*topology*.html", "summary/**/*day6*topology*.html"],
    },
    {
        "day": "Day8",
        "title": "Day8 iperf3 Performance",
        "report_type": "Day8 performance report",
        "safety_label": "guarded-live performance evidence",
        "description": "Day8 iperf3 throughput evidence; report visibility reads existing files and does not generate traffic.",
        "json_globs": ["reports/**/day8_iperf3_*_report.json", "reports/**/*iperf3*performance*.json"],
        "html_globs": ["reports/**/day8_iperf3_*_report.html", "reports/**/*iperf3*performance*.html"],
    },
    {
        "day": "Day12",
        "title": "Day12 WireGuard Validation",
        "report_type": "Day12 WireGuard report / documentation relationship",
        "safety_label": "guarded-live evidence",
        "description": "Detailed WireGuard client-to-site validation evidence; Day18 links to these reports when guarded delegation runs.",
        "json_globs": ["reports/**/day12_wireguard_vpn_automation_report.json"],
        "html_globs": ["reports/**/day12_wireguard_vpn_automation_report.html"],
    },
    {
        "day": "Day13",
        "title": "Day13 WireGuard Summary",
        "report_type": "Day13 multi-router WireGuard validation report",
        "safety_label": "report-only evidence",
        "description": "Multi-router WireGuard validation summary evidence; Day12 remains the detailed source of truth for per-router live validation.",
        "json_globs": ["summary/**/*day13*wireguard*.json", "reports/**/*day13*wireguard*.json"],
        "html_globs": ["summary/**/*day13*wireguard*.html", "reports/**/*day13*wireguard*.html"],
    },
    {
        "day": "Day18",
        "title": WIREGUARD_RUNNER_DISPLAY_NAME,
        "report_type": "Day18 WireGuard runner result",
        "safety_label": "guarded-live / dry-run default",
        "description": "Safety-layer result for delegated Day12 WireGuard validation; unsafe Day12 write flags are not delegated.",
        "json_globs": [WIREGUARD_RUNNER_REPORT_JSON.as_posix()],
        "html_globs": [WIREGUARD_RUNNER_REPORT_HTML.as_posix()],
        "missing_note": f"Expected report path: {WIREGUARD_RUNNER_REPORT_JSON.as_posix()}",
    },
    {
        "day": "Day14-Day16",
        "title": "Runner Overview Reports",
        "report_type": "Day21 report viewer / evidence viewer relationship",
        "safety_label": "local report index",
        "description": "Unified runner overview and report index generated from local files for the dashboard /reports evidence viewer.",
        "json_globs": ["reports/lab-summary/latest_lab_overview.json"],
        "html_globs": ["reports/lab-summary/latest_lab_overview.html", "reports/report_index.html"],
    },
    {
        "day": "Day24",
        "title": "Day24 RC Demo Flow",
        "report_type": "RC demo walkthrough",
        "safety_label": "report-only demo guidance",
        "description": "Local reviewer walkthrough for RC demo and portfolio presentation; generated without live execution.",
        "json_globs": [DAY24_DEMO_FLOW_JSON.as_posix()],
        "html_globs": [DAY24_DEMO_FLOW_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task demo-flow",
    },
    {
        "day": "Day32",
        "title": "VRRP Read-only Precheck Runner",
        "report_type": "HA / VRRP read-only precheck report",
        "safety_label": "read-only evidence",
        "description": "MikroTik HA/VRRP readiness evidence gathered with read-only print/export terse commands only.",
        "json_globs": [DAY32_VRRP_PRECHECK_JSON.as_posix()],
        "html_globs": [DAY32_VRRP_PRECHECK_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY32_VRRP_PRECHECK_TASK_ID}",
    },
    {
        "day": "Day33",
        "title": "VRRP Topology Design + Dry-run Command Preview",
        "report_type": "HA / VRRP dry-run topology design report",
        "safety_label": "dry-run preview",
        "description": "MikroTik HA/VRRP v0.2 topology design and command preview generated from local dry-run profile data only.",
        "json_globs": [DAY33_VRRP_DRY_RUN_JSON.as_posix()],
        "html_globs": [DAY33_VRRP_DRY_RUN_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY33_VRRP_DRY_RUN_TASK_ID}",
    },
    {
        "day": "Day34",
        "title": "VRRP Staged Apply Plan and Safety Gate",
        "report_type": "HA / VRRP staged apply plan report",
        "safety_label": "blocked plan-only safety gate",
        "description": "MikroTik HA/VRRP staged apply plan that checks Day32/Day33 evidence and blocks live execution.",
        "json_globs": [DAY34_VRRP_STAGED_PLAN_JSON.as_posix()],
        "html_globs": [DAY34_VRRP_STAGED_PLAN_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY34_VRRP_STAGED_PLAN_TASK_ID}",
    },
    {
        "day": "Day35",
        "title": "VRRP Failover Validation",
        "report_type": "HA / VRRP controlled failover validation report",
        "safety_label": "controlled_failover_observation",
        "description": "MikroTik HA/VRRP failover evidence gathered after a manual external lab01 LAN disconnect/reconnect; automation only observes and reports.",
        "json_globs": [DAY35_VRRP_FAILOVER_JSON.as_posix()],
        "html_globs": [DAY35_VRRP_FAILOVER_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY35_VRRP_FAILOVER_TASK_ID}",
    },
    {
        "day": "Day39",
        "title": "VRRP Evidence Dashboard Integration",
        "report_type": "HA / VRRP evidence dashboard summary",
        "safety_label": "report-only evidence",
        "description": "Report-only Day39 summary that inventories Day31-Day38 HA/VRRP docs, diagrams, reports, and dashboard/index readiness.",
        "json_globs": [DAY39_VRRP_EVIDENCE_JSON.as_posix()],
        "html_globs": [DAY39_VRRP_EVIDENCE_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY39_VRRP_EVIDENCE_TASK_ID}",
    },
    {
        "day": "Day40",
        "title": "v0.2 Demo Readiness Review and Scope Lock",
        "report_type": "Portfolio demo readiness report",
        "safety_label": "report-only demo readiness",
        "description": "Report-only Day40 scope lock and demo checklist for v0.2; generated without SSH, live tests, or device configuration changes.",
        "json_globs": [DAY40_DEMO_READINESS_JSON.as_posix()],
        "html_globs": [DAY40_DEMO_READINESS_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY40_DEMO_READINESS_TASK_ID}",
    },
    {
        "day": "Day41",
        "title": "v0.2 Release Packaging",
        "report_type": "Release packaging report",
        "safety_label": "report-only release packaging",
        "description": "Report-only Day41 package for v0.2 docs, checklist, demo handoff, known limitations, and Day42 tag handoff.",
        "json_globs": [DAY41_RELEASE_PACKAGING_JSON.as_posix()],
        "html_globs": [DAY41_RELEASE_PACKAGING_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY41_RELEASE_PACKAGING_TASK_ID}",
    },
    {
        "day": "Day59",
        "title": "Intent Policy Matrix",
        "report_type": "Reviewer-facing safety matrix",
        "safety_label": "report-only AI planning evidence",
        "description": "Day59 policy matrix explaining Day57/Day58 intent mapping safety decisions without live behavior.",
        "json_globs": [DAY59_INTENT_POLICY_MATRIX_JSON.as_posix()],
        "html_globs": [DAY59_INTENT_POLICY_MATRIX_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY59_INTENT_POLICY_MATRIX_TASK_ID}",
    },
    {
        "day": "Day60",
        "title": "AI Intent Workflow Demo",
        "report_type": "Reviewer walkthrough report",
        "safety_label": "report-only AI planning evidence",
        "description": "Day60 reviewer walkthrough connecting Day57 mapping, Day58 safety review, and Day59 policy explanation without live behavior.",
        "json_globs": [DAY60_INTENT_WORKFLOW_DEMO_JSON.as_posix()],
        "html_globs": [DAY60_INTENT_WORKFLOW_DEMO_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY60_INTENT_WORKFLOW_DEMO_TASK_ID}",
    },
    {
        "day": "Day66",
        "title": "Offline Mock Runtime Skeleton",
        "report_type": "Reviewer mock runtime report",
        "safety_label": "offline mock / dry-run-only AI planning evidence",
        "description": "Day66 fixed mock runtime skeleton report for AI Intent Reviewer architecture shape without live behavior.",
        "json_globs": [DAY66_OFFLINE_MOCK_RUNTIME_JSON.as_posix()],
        "html_globs": [DAY66_OFFLINE_MOCK_RUNTIME_HTML.as_posix()],
        "missing_note": f"Generate with: python network_lab.py --task {DAY66_OFFLINE_MOCK_RUNTIME_TASK_ID}",
    },
    {
        "day": "Day67",
        "title": "Offline Mock Runtime Contract",
        "report_type": "Reviewer contract validation report",
        "safety_label": "offline mock contract / safety invariant validation",
        "description": "Day67 validates Day66 mock runtime output contracts and safety invariants without live behavior.",
        "json_globs": [DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day68",
        "title": "Offline Mock Runtime Reviewer Report Quality",
        "report_type": "Reviewer quality and evidence trace report",
        "safety_label": "offline mock reviewer quality / evidence trace review",
        "description": "Day68 reviews Day66-Day67 report quality, evidence traceability, and no-execution proof without live behavior.",
        "json_globs": [DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_JSON.as_posix()],
        "html_globs": [DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_TASK_ID}"
        ),
    },
    {
        "day": "Day73",
        "title": "Mock AI Decision Pipeline",
        "report_type": "Reviewer mock AI decision pipeline report",
        "safety_label": "mock-only / report-only AI planning evidence",
        "description": "Day73 runs deterministic mock decisions after Day72 validation without AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY73_MOCK_AI_DECISION_PIPELINE_JSON.as_posix()],
        "html_globs": [DAY73_MOCK_AI_DECISION_PIPELINE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY73_MOCK_AI_DECISION_PIPELINE_TASK_ID}"
        ),
    },
    {
        "day": "Day74",
        "title": "Controlled Dry-run Plan Builder",
        "report_type": "Reviewer dry-run plan builder report",
        "safety_label": "mock-only / dry-run-only AI planning evidence",
        "description": "Day74 converts deterministic Day73 mock decisions into reviewer dry-run plan previews without AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY74_DRY_RUN_PLAN_BUILDER_JSON.as_posix()],
        "html_globs": [DAY74_DRY_RUN_PLAN_BUILDER_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY74_DRY_RUN_PLAN_BUILDER_TASK_ID}"
        ),
    },
    {
        "day": "Day75",
        "title": "Manual Review Approval Envelope",
        "report_type": "Reviewer sign-off envelope simulation report",
        "safety_label": "mock-only / dry-run-only reviewer sign-off evidence",
        "description": "Day75 wraps deterministic Day74 dry-run plans in reviewer approval envelope records without approval unlocks, AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_JSON.as_posix()],
        "html_globs": [DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_TASK_ID}"
        ),
    },
    {
        "day": "Day76",
        "title": "Controlled Runtime Audit Trail",
        "report_type": "Reviewer decision evidence package",
        "safety_label": "mock-only / dry-run-only runtime audit evidence",
        "description": "Day76 links Day73 decisions, Day74 plans, and Day75 approval envelopes into reviewer audit records without execution unlocks, AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY76_RUNTIME_AUDIT_TRAIL_JSON.as_posix()],
        "html_globs": [DAY76_RUNTIME_AUDIT_TRAIL_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY76_RUNTIME_AUDIT_TRAIL_TASK_ID}"
        ),
    },
    {
        "day": "Day77",
        "title": "Runtime Safety Gate / No-Execution Enforcement Report",
        "report_type": "Runtime safety gate enforcement report",
        "safety_label": "deterministic mock-only / dry-run-only no-execution gate",
        "description": "Day77 links Day73 decisions, Day74 plans, Day75 approval envelopes, and Day76 audit records into locked runtime safety gate records without execution unlocks, AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY77_RUNTIME_SAFETY_GATE_JSON.as_posix()],
        "html_globs": [DAY77_RUNTIME_SAFETY_GATE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY77_RUNTIME_SAFETY_GATE_TASK_ID}"
        ),
    },
    {
        "day": "Day78",
        "title": "Controlled Runtime Safety Case / End-to-End Reviewer Package",
        "report_type": "Runtime safety case reviewer package",
        "safety_label": "deterministic mock-only / dry-run-only reviewer package",
        "description": "Day78 links Day72 input validation, Day73 decisions, Day74 plans, Day75 approval envelopes, Day76 audit records, and Day77 locked safety gates into deterministic safety case records without execution unlocks, AI API, SSH, device access, live execution, or mapped task execution.",
        "json_globs": [DAY78_RUNTIME_SAFETY_CASE_JSON.as_posix()],
        "html_globs": [DAY78_RUNTIME_SAFETY_CASE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY78_RUNTIME_SAFETY_CASE_TASK_ID}"
        ),
    },
    {
        "day": "Day79",
        "title": "Controlled Read-only Task Contract & Allowlist",
        "report_type": "Read-only task contract allowlist",
        "safety_label": "deterministic mock-only / dry-run-only task eligibility contract",
        "description": "Day79 defines future read-only task candidates, blocked write actions, destructive actions, and manual classification cases while preserving no execution unlock, no SSH, no device access, no mapped task execution, and no network change.",
        "json_globs": [DAY79_READONLY_TASK_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY79_READONLY_TASK_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY79_READONLY_TASK_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day80",
        "title": "Read-only Execution Broker Skeleton",
        "report_type": "Read-only broker skeleton",
        "safety_label": "deterministic mock-only / dry-run-only broker evidence",
        "description": "Day80 receives fixed mock read-only task requests, checks them against the Day79 contract, rejects unsafe requests, queues review-only requests, or prepares mock execution request data while preserving no execution unlock, no SSH, no device access, no live command execution, and no network change.",
        "json_globs": [DAY80_READONLY_EXECUTION_BROKER_JSON.as_posix()],
        "html_globs": [DAY80_READONLY_EXECUTION_BROKER_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY80_READONLY_EXECUTION_BROKER_TASK_ID}"
        ),
    },
    {
        "day": "Day81",
        "title": "Read-only Broker Review Queue & Decision State Report",
        "report_type": "Broker review queue decision state report",
        "safety_label": "deterministic mock-only / dry-run-only review queue evidence",
        "description": "Day81 transforms Day80 broker records into reviewer-facing queue and decision state records while preserving no execution unlock, no SSH, no device access, no live command execution, no mapped task execution, and no dashboard action endpoint.",
        "json_globs": [DAY81_BROKER_REVIEW_QUEUE_JSON.as_posix()],
        "html_globs": [DAY81_BROKER_REVIEW_QUEUE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY81_BROKER_REVIEW_QUEUE_TASK_ID}"
        ),
    },
    {
        "day": "Day82",
        "title": "Reviewer Decision Audit Summary / Queue Evidence Export",
        "report_type": "Reviewer decision audit summary",
        "safety_label": "deterministic mock-only / dry-run-only audit evidence export",
        "description": "Day82 summarizes Day81 broker review queue decisions and exports reviewer evidence while preserving no execution unlock, no SSH, no device access, no live command execution, no AI runtime, no mapped task execution, and no dashboard action endpoint.",
        "json_globs": [DAY82_REVIEWER_DECISION_AUDIT_JSON.as_posix()],
        "html_globs": [DAY82_REVIEWER_DECISION_AUDIT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY82_REVIEWER_DECISION_AUDIT_TASK_ID}"
        ),
    },
    {
        "day": "Day83",
        "title": "Read-only Executor Readiness Gate / Controlled Runner Preflight",
        "report_type": "Read-only executor readiness gate",
        "safety_label": "deterministic offline review-only readiness gate",
        "description": "Day83 validates the Day79-Day82 safety evidence chain as sufficient for future read-only executor adapter design review while preserving executor_allowed=false, no live execution, no SSH, no device access, no AI runtime, no mapped task execution, no approval/execution unlock, and no dashboard action endpoint.",
        "json_globs": [DAY83_READONLY_EXECUTOR_READINESS_GATE_JSON.as_posix()],
        "html_globs": [DAY83_READONLY_EXECUTOR_READINESS_GATE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY83_READONLY_EXECUTOR_READINESS_GATE_TASK_ID}"
        ),
    },
    {
        "day": "Day84",
        "title": "Read-only Executor Adapter Interface Contract",
        "report_type": "Read-only executor adapter interface contract",
        "safety_label": "deterministic contract-only adapter boundary",
        "description": "Day84 defines future read-only executor adapter request, response, capability, evidence, safety flag, and validation result shapes while preserving no executor implementation, no SSH, no device access, no live command execution, no AI API, no approval/execution unlock, and no dashboard action endpoint.",
        "json_globs": [DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day85",
        "title": "Mock Adapter + Evidence Binding",
        "report_type": "Mock adapter evidence binding",
        "safety_label": "deterministic mock-only evidence-bound adapter fixture",
        "description": "Day85 binds deterministic mock adapter responses to Day84 contract references and reviewer evidence while preserving no SSH, no device access, no live command execution, no AI API, no approval/execution unlock, and no dashboard action endpoint. Compatibility Matrix remains internal validation evidence only.",
        "json_globs": [DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_JSON.as_posix()],
        "html_globs": [DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_TASK_ID}"
        ),
    },
    {
        "day": "Day86",
        "title": "Controlled Runner Harness + Safety Regression",
        "report_type": "Controlled runner harness safety regression",
        "safety_label": "deterministic runner-level dry-run safety regression",
        "description": "Day86 consumes Day85-style adapter compatibility and evidence signals at the runner layer while preserving allowed_to_execute=false, ssh_allowed=false, live_command_allowed=false, mapped_task_executed=false, no approval/execution unlock, and no dashboard action endpoint.",
        "json_globs": [DAY86_CONTROLLED_RUNNER_HARNESS_JSON.as_posix()],
        "html_globs": [DAY86_CONTROLLED_RUNNER_HARNESS_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY86_CONTROLLED_RUNNER_HARNESS_TASK_ID}"
        ),
    },
    {
        "day": "Day87",
        "title": "Read-only Executor Phase Gate Review",
        "report_type": "Read-only executor phase gate review",
        "safety_label": "deterministic phase gate review; design-only recommendation",
        "description": "Day87 reviews Day83-Day86 safety and readiness evidence to decide whether Day88 may start the Real Read-only Executor Adapter Design Draft while preserving execution_allowed=false, ssh_allowed=false, live_command_allowed=false, write_command_allowed=false, device_connection_allowed=false, real_adapter_implementation_allowed=false, and real_adapter_design_allowed=true.",
        "json_globs": [DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_JSON.as_posix()],
        "html_globs": [DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_TASK_ID}"
        ),
    },
    {
        "day": "Day88",
        "title": "Real Read-only Executor Adapter Design Draft",
        "report_type": "Real read-only executor adapter design draft",
        "safety_label": "deterministic design-only adapter draft; no execution unlock",
        "description": "Day88 defines the future real read-only executor adapter architecture, positive command allowlist, evidence/error/timeout contracts, and safety boundary while keeping execution_supported=false, ssh_supported=false, routeros_connection_supported=false, live_command_supported=false, and dashboard action surfaces disabled.",
        "json_globs": [DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_JSON.as_posix()],
        "html_globs": [DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_TASK_ID}"
        ),
    },
    {
        "day": "Day89",
        "title": "Real Adapter Safety Boundary Spec",
        "report_type": "Real adapter pre-implementation safety boundary spec",
        "safety_label": "deterministic design-only boundary lock; no live adapter",
        "description": "Day89 locks the safety boundary before any real adapter implementation while keeping implementation_allowed=false, live_device_access_allowed=false, ssh_allowed=false, config_change_allowed=false, command_execution_allowed=false, and safety_boundary_locked=true.",
        "json_globs": [DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_JSON.as_posix()],
        "html_globs": [DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_TASK_ID}"
        ),
    },
    {
        "day": "Day90",
        "title": "Real Adapter Implementation Plan",
        "report_type": "Real adapter implementation-entry decision plan",
        "safety_label": "deterministic planning-only decision; no adapter implementation",
        "description": "Day90 decides GO, CONDITIONAL_GO, or NO_GO from repository evidence while keeping scope=planning_only, adapter_implementation_allowed=false, live_device_access_allowed=false, ssh_allowed=false, and routeros_command_execution_allowed=false.",
        "json_globs": [DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_JSON.as_posix()],
        "html_globs": [DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_TASK_ID}"
        ),
    },
    {
        "day": "Day91",
        "title": "Real Adapter Safety Scaffold",
        "report_type": "Real adapter scaffold-only safety evidence",
        "safety_label": "deterministic scaffold-only evidence; no live-read",
        "description": "Day91 is scaffold-only with no live-read and follows Day90 CONDITIONAL_GO by proving dangerous actions are denied before any real adapter, transport, SSH, RouterOS API, socket, subprocess device operation, credential use, or live-read path exists.",
        "json_globs": [DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_JSON.as_posix()],
        "html_globs": [DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_TASK_ID}"
        ),
    },
    {
        "day": "Day92",
        "title": "Real Adapter Executable Guards",
        "report_type": "Real adapter executable guard evidence",
        "safety_label": "offline deterministic guard; no adapter implementation",
        "description": "Day92 turns the Day91 static safety scaffold into executable request guards with no adapter implementation: safe simulated read-only requests may pass to a fake executor, dangerous/unknown/sensitive requests are rejected before executor invocation, and rejected_adapter_invocations remains 0.",
        "json_globs": [DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_JSON.as_posix()],
        "html_globs": [DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_TASK_ID}"
        ),
    },
    {
        "day": "Day93",
        "title": "Guarded Fake Adapter Contract",
        "report_type": "Guarded fake adapter boundary audit evidence",
        "safety_label": "fake adapter only; no live execution",
        "description": "Day93 proves guard-first ordering at the fake adapter boundary: allowed read-only scenarios enter only the fake adapter, rejected scenarios never enter any adapter boundary, and real_adapter_invocations remains 0.",
        "json_globs": [DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day94",
        "title": "Adapter Boundary Regression Matrix",
        "report_type": "Adapter boundary regression matrix evidence",
        "safety_label": "fake-adapter-only matrix; no live execution",
        "description": "Day94 expands Day93 guard-first proof into a matrix: rejected rows never invoke the fake adapter, real_adapter_invocations remains 0, live_execution_invocations remains 0, and allowed fake-adapter rows are evidence-only.",
        "json_globs": [DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_JSON.as_posix()],
        "html_globs": [DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_TASK_ID}"
        ),
    },
    {
        "day": "Day95",
        "title": "Adapter Result Normalization",
        "report_type": "Normalized fake adapter result evidence",
        "safety_label": "fake-only result normalization; no live execution",
        "description": "Day95 normalizes only deterministic fake adapter results after the Day93/Day94 fake boundary evidence chain: rejected scenarios produce no adapter result, real_adapter_result_count remains 0, and live_execution_result_count remains 0.",
        "json_globs": [DAY95_ADAPTER_RESULT_NORMALIZATION_JSON.as_posix()],
        "html_globs": [DAY95_ADAPTER_RESULT_NORMALIZATION_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY95_ADAPTER_RESULT_NORMALIZATION_TASK_ID}"
        ),
    },
    {
        "day": "Day96",
        "title": "Read-only Output Parser Prototype",
        "report_type": "Parser-only fake adapter simulated output evidence",
        "safety_label": "parser-only; no live-read, SSH, RouterOS, or device access",
        "description": "Day96 parses only Day95 normalized fake adapter simulated output into structured records. Unsupported or malformed inputs return REVIEW_NEEDED or UNSUPPORTED without adapter fallback, runner live path, SSH, RouterOS, config.json, or dashboard action.",
        "json_globs": [DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_JSON.as_posix()],
        "html_globs": [DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_TASK_ID}"
        ),
    },
    {
        "day": "Day97",
        "title": "Parser Evidence Quality",
        "report_type": "Parser-only unsupported output evidence quality",
        "safety_label": "static fake parser cases; no execution, SSH, live-read, write, or unlock path",
        "description": "Day97 hardens Day96 parser evidence handling for empty, malformed, incomplete, ambiguous, unsupported, and degraded static fake outputs. Unsupported output remains parser evidence, not an execution-failure result, and all execution-related safety flags remain false.",
        "json_globs": [DAY97_PARSER_EVIDENCE_QUALITY_JSON.as_posix()],
        "html_globs": [DAY97_PARSER_EVIDENCE_QUALITY_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY97_PARSER_EVIDENCE_QUALITY_TASK_ID}"
        ),
    },
    {
        "day": "Day98",
        "title": "Parser Classification Matrix",
        "report_type": "Parser-only reviewer traceability matrix",
        "safety_label": "static Day96/Day97 samples; executable_allowed is always false",
        "description": "Day98 connects Day96 parser prototype outcomes and Day97 unsupported-output hardening into a reviewer-facing traceability matrix: input sample, parser classification, parsed fields or unsupported reason, reviewer action, and safety invariant.",
        "json_globs": [DAY98_PARSER_CLASSIFICATION_MATRIX_JSON.as_posix()],
        "html_globs": [DAY98_PARSER_CLASSIFICATION_MATRIX_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY98_PARSER_CLASSIFICATION_MATRIX_TASK_ID}"
        ),
    },
    {
        "day": "Day99",
        "title": "Parser Evidence Coverage / Sample Gap Audit",
        "report_type": "Report-only parser evidence coverage audit",
        "safety_label": "static Day96-Day98 report audit; UNDER_COVERED gaps are allowed",
        "description": "Day99 audits Day96-Day98 parser samples and evidence coverage before Day100. It records under-covered categories as non-blocking sample gaps while keeping execution, adapter, broker, SSH, live device, config, dashboard action, OpenAI API, and voice paths disabled.",
        "json_globs": [DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_JSON.as_posix()],
        "html_globs": [DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_TASK_ID}"
        ),
    },
    {
        "day": "Day100",
        "title": "Parser Phase Gate Review / Readiness Decision",
        "report_type": "Report-only parser phase gate readiness decision",
        "safety_label": "static Day96-Day99 review; broker/executor/adapter/SSH/live access disabled",
        "description": "Day100 grades Day96-Day99 parser evidence into ADVANCE_READY, REVIEW_ONLY, UNDER_COVERED, and BLOCKED decisions. Parser output remains reviewer evidence only: broker_boundary_allowed, execution_allowed, adapter_invocation_allowed, ssh_allowed, and live_access_allowed are always false.",
        "json_globs": [DAY100_PARSER_PHASE_GATE_REVIEW_JSON.as_posix()],
        "html_globs": [DAY100_PARSER_PHASE_GATE_REVIEW_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY100_PARSER_PHASE_GATE_REVIEW_TASK_ID}"
        ),
    },
    {
        "day": "Day101",
        "title": "Parser Evidence Closure Plan",
        "report_type": "Report-only parser evidence closure roadmap",
        "safety_label": "Day100 closure planning; broker handoff blocked; execution/SSH/live access disabled",
        "description": "Day101 converts Day100 UNDER_COVERED and REVIEW_ONLY parser findings into a Day102-Day105 evidence closure plan. parser_ready_for_broker and broker_handoff_allowed remain false, and phase_gate_rerun_required remains true.",
        "json_globs": [DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_JSON.as_posix()],
        "html_globs": [DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_TASK_ID}"
        ),
    },
    {
        "day": "Day102",
        "title": "Parser Fixture Expansion",
        "report_type": "Report-only static parser fixture expansion",
        "safety_label": "static fixture evidence only; parser capability/broker/adapter/SSH/live access disabled",
        "description": "Day102 expands parser evidence fixtures across positive, negative, malformed, ambiguous, and unsafe categories. It proves legal read-only/report-only inputs are not rejected, unsupported and malformed inputs have reasons, ambiguous inputs are not silently accepted, and live/mutating/SSH/config-change intents are blocked.",
        "json_globs": [DAY102_PARSER_FIXTURE_EXPANSION_JSON.as_posix()],
        "html_globs": [DAY102_PARSER_FIXTURE_EXPANSION_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY102_PARSER_FIXTURE_EXPANSION_TASK_ID}"
        ),
    },
    {
        "day": "Day103",
        "title": "Parser Evidence Matrix / Gap Traceability",
        "report_type": "Report-only parser evidence matrix and gap traceability",
        "safety_label": "static Day96-Day102 evidence integration; execution/broker/adapter/SSH/live access disabled",
        "description": "Day103 integrates Day96-Day102 parser evidence into a reviewer-facing gap traceability matrix: gap, fixture or evidence, expected decision, actual result, report path, and safety boundary. It does not add parser capability, execution, broker handoff, adapter invocation, SSH, live device access, config changes, dashboard actions, OpenAI API usage, voice runtime, or external integrations.",
        "json_globs": [DAY103_PARSER_EVIDENCE_MATRIX_JSON.as_posix()],
        "html_globs": [DAY103_PARSER_EVIDENCE_MATRIX_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY103_PARSER_EVIDENCE_MATRIX_TASK_ID}"
        ),
    },
    {
        "day": "Day104",
        "title": "Parser Reviewer Acceptance Gate / Matrix Decision Review",
        "report_type": "Report-only parser reviewer acceptance gate",
        "safety_label": "Day103 matrix decision review only; parser expansion/execution/broker/adapter/SSH/live access disabled",
        "description": "Day104 converts Day103 matrix trace states into a reviewer acceptance decision. TRACE_COMPLETE can pass only when all required rows are complete; REVIEW_REQUIRED prevents full acceptance; KNOWN_GAP and BLOCKED_BY_SAFETY_BOUNDARY block next-stage readiness, with safety boundary blocks dominating known gaps.",
        "json_globs": [DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_JSON.as_posix()],
        "html_globs": [DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_TASK_ID}"
        ),
    },
    {
        "day": "Day105",
        "title": "Parser Acceptance Closure / Safety-Blocked Exit Summary",
        "report_type": "Report-only parser acceptance closure package",
        "safety_label": "Day96-Day104 closure only; next phase remains blocked and no execution unlock is granted",
        "description": "Day105 packages Day96-Day104 parser evidence for reviewer inspection. It is SUMMARY_ONLY, keeps final_recommendation=SAFETY_BLOCKED_REVIEW_ONLY, and does not add parser capability, adapter execution, SSH, live access, mapped task execution, OpenAI API, voice input, or configuration change permission.",
        "json_globs": [DAY105_PARSER_ACCEPTANCE_CLOSURE_JSON.as_posix()],
        "html_globs": [DAY105_PARSER_ACCEPTANCE_CLOSURE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY105_PARSER_ACCEPTANCE_CLOSURE_TASK_ID}"
        ),
    },
    {
        "day": "Day106",
        "title": "Codex AGENTS.md Instruction Compliance Audit",
        "report_type": "Report-only Codex instruction compliance audit",
        "safety_label": "AGENTS.md governance audit only; may read/audit/report, must not modify/stage/commit AGENTS.md",
        "description": "Day106 evaluates the repository-level AGENTS.md as a durable Codex instruction contract. Codex may read AGENTS.md, audit AGENTS.md, and report findings with proposed wording, but must not modify, stage, or commit AGENTS.md during the governance audit.",
        "json_globs": [DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_JSON.as_posix()],
        "html_globs": [DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_TASK_ID}"
        ),
    },
    {
        "day": "Day107",
        "title": "Parser Reviewer Evidence Contract Consolidation",
        "report_type": "Report-only parser reviewer evidence contract",
        "safety_label": "Day96-Day105 parser evidence contract only; live execution, SSH, device access, adapter invocation, OpenAI API, voice runtime, rejected-intent execution, and config mutation remain locked",
        "description": "Day107 consolidates Day96-Day105 parser evidence into one deterministic reviewer contract. It accepts review-only continuation only when all required evidence stages are represented and all safety boundaries remain locked, with final_recommendation=PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION on the PASS path.",
        "json_globs": [DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day108",
        "title": "Parser Contract Consumer / Reviewer Decision Handoff",
        "report_type": "Report-only parser contract consumer handoff",
        "safety_label": "Consumes the Day107 source contract shape only; live execution, SSH, device access, command execution, approval unlock, mapped task execution, OpenAI API, voice input, and write/config change remain locked",
        "description": "Day108 consumes Day107-style reviewer evidence contract records and emits deterministic reviewer decision handoff records. Unsafe flags block handoff, degraded evidence requires reviewer clarification, and ready records remain report-only with reviewer_decision=READY_FOR_REVIEW_HANDOFF and reviewer_handoff_status=CONSUMER_HANDOFF_READY_REPORT_ONLY.",
        "json_globs": [DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_JSON.as_posix()],
        "html_globs": [DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_TASK_ID}"
        ),
    },
    {
        "day": "Day109",
        "title": "Parser Consumer Handoff Readiness Matrix",
        "report_type": "Report-only parser consumer handoff readiness matrix",
        "safety_label": "Consumes Day108 handoff records only; REVIEW_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE, with command and mapped task execution blocked",
        "description": "Day109 converts Day108 consumer handoff records into deterministic READY, NEEDS_CLARIFICATION, and BLOCKED reviewer-facing rows. Unsafe, live, SSH, write, command execution, and mapped task execution flags remain blocking conditions and are never rewritten as ready.",
        "json_globs": [DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_JSON.as_posix()],
        "html_globs": [DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_TASK_ID}"
        ),
    },
    {
        "day": "Day110",
        "title": "Parser Consumer Final Gate / Reviewer Decision Summary",
        "report_type": "Report-only parser consumer final gate",
        "safety_label": "Consumes Day109 readiness evidence only; includes AGENTS.md pre-read result; REVIEW_ONLY / REPORT_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE",
        "description": "Day110 summarizes Day109 parser consumer readiness into a final reviewer decision gate. Blocked or clarification rows keep next_phase_allowed=false, AGENTS.md pre-read evidence is displayed, and no adapter, broker, runner, live device, SSH, write/config change, OpenAI API, external API, or mapped task execution path is added.",
        "json_globs": [DAY110_PARSER_CONSUMER_FINAL_GATE_JSON.as_posix()],
        "html_globs": [DAY110_PARSER_CONSUMER_FINAL_GATE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY110_PARSER_CONSUMER_FINAL_GATE_TASK_ID}"
        ),
    },
    {
        "day": "Day111",
        "title": "Parser Consumer Evidence Freeze / Release Package",
        "report_type": "Report-only parser consumer release package",
        "safety_label": "Freezes Day107-Day110 evidence; RELEASE_PACKAGE_READY_REVIEW_ONLY / FROZEN / NO_LIVE_EXECUTION / NO_SSH / NO_MAPPED_TASK_EXECUTION",
        "description": "Day111 freezes Day107-Day110 parser consumer reviewer evidence into one deterministic release package. The package is ready for reviewer release, but Day109 blocked records and the Day110 locked final gate keep next_phase_allowed=false. It adds no live device access, SSH, mapped task execution, adapter, broker, cloud, OpenAI API, voice, approval unlock, or dashboard execution control.",
        "json_globs": [DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_JSON.as_posix()],
        "html_globs": [DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_TASK_ID}"
        ),
    },
    {
        "day": "Day112",
        "title": "Parser Consumer Release Review Intake / Reviewer Triage Checklist",
        "report_type": "Report-only parser consumer reviewer intake checklist",
        "safety_label": "Consumes Day111 frozen release package for reviewer intake only; REVIEW_INTAKE_READY_NON_EXECUTABLE / BLOCKED_CONDITIONS_PRESERVED / NEXT_PHASE_ALLOWED_FALSE",
        "description": "Day112 receives the Day111 frozen parser consumer release package into reviewer intake. It provides the 10 required checklist items and exact reviewer routes, while approval unlock, execution readiness, mapped task execution, adapter/broker/runner invocation, live device access, SSH, OpenAI API, cloud, voice, and next-phase enablement remain disallowed.",
        "json_globs": [DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_JSON.as_posix()],
        "html_globs": [DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_TASK_ID}"
        ),
    },
    {
        "day": "Day113",
        "title": "Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit",
        "report_type": "Report-only parser consumer reviewer triage outcome log",
        "safety_label": "Records Day112 intake outcome for reviewer audit only; TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE / HOLD_FOR_BLOCKED_RECORDS / NEXT_PHASE_ALLOWED_FALSE",
        "description": "Day113 records the reviewer triage outcome for the Day112 intake package. It logs the HOLD_FOR_BLOCKED_RECORDS outcome and audits intake result preservation while approval unlock, execution readiness, mapped task execution, adapter/broker/runner invocation, live device access, SSH, OpenAI API, cloud, voice, and next-phase enablement remain disallowed.",
        "json_globs": [DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_JSON.as_posix()],
        "html_globs": [DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_TASK_ID}"
        ),
    },
    {
        "day": "Day114",
        "title": "Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit",
        "report_type": "Audit-only parser consumer reviewer traceability map",
        "safety_label": "Links Day112 intake and Day113 triage evidence only; TRACEABILITY_AUDITED_NON_EXECUTABLE / BLOCKED_RECORDS_PRESERVED / NO_NEXT_PHASE_UNLOCK",
        "description": "Day114 verifies that all Day112 intake records and Day113 triage outcomes remain traceable, blocked records are preserved, no downgrade occurred, and no execution readiness or next phase unlock is inferred. It keeps approval unlock, execution readiness, mapped task execution, adapter/broker/runner invocation, live device access, SSH, OpenAI API, cloud, voice, and next-phase enablement disallowed.",
        "json_globs": [DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_JSON.as_posix()],
        "html_globs": [DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_TASK_ID}"
        ),
    },
    {
        "day": "Day115",
        "title": "Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit",
        "report_type": "Report-only parser consumer reviewer triage closure summary",
        "safety_label": "Closes Day112-Day114 reviewer triage chain only; TRIAGE_CLOSURE_AUDITED_NON_ADVANCING / DO_NOT_ADVANCE / NO_NEXT_PHASE_UNLOCK",
        "description": "Day115 closes the reviewer triage chain from Day112 to Day114 while preserving the non-advancement decision. It keeps blocked records blocked, does not infer execution readiness, and does not enable broker handoff, runner execution, adapter access, SSH, live access, mapped task execution, approval unlock, or next-phase advancement.",
        "json_globs": [DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_JSON.as_posix()],
        "html_globs": [DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_TASK_ID}"
        ),
    },
    {
        "day": "Day116",
        "title": "Reviewer Deferred Action Register / Blocked Follow-up Queue",
        "report_type": "Reviewer-only deferred action register",
        "safety_label": "Records Day112-Day115 deferred follow-up queue only; DEFERRED_ACTION_REGISTER_RECORDED / FOLLOW_UP_QUEUE_RECORDED / NO_EXECUTION_UNLOCK",
        "description": "Day116 consolidates blocked, held, and do-not-advance records from Day112-Day115 into a reviewer-only follow-up queue. It does not resolve items, advance execution, generate readiness, or enter broker, runner, adapter, SSH, or live access paths.",
        "json_globs": [DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_JSON.as_posix()],
        "html_globs": [DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_TASK_ID}"
        ),
    },
    {
        "day": "Day117",
        "title": "Deferred Action Traceability Review / Follow-up Ownership Matrix",
        "report_type": "Reviewer-only deferred action traceability matrix",
        "safety_label": "Adds Day116 follow-up ownership traceability only; DEFERRED_ACTION_TRACEABILITY_REVIEW_READY / REVIEW_ONLY_NON_ADVANCING / NO_EXECUTION_UNLOCK",
        "description": "Day117 tracks owner roles, follow-up types, blocking reasons, review sequence, and evidence requirements for the seven Day116 deferred items. It does not resolve items, advance execution, generate readiness, or enter broker, runner, adapter, SSH, or live access paths.",
        "json_globs": [DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_JSON.as_posix()],
        "html_globs": [DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_TASK_ID}"
        ),
    },
    {
        "day": "Day118",
        "title": "Deferred Action Review Sequence Runbook / Evidence Intake Checklist",
        "report_type": "Reviewer-only deferred action evidence intake checklist",
        "safety_label": "Converts Day117 ownership matrix into intake questions only; INTAKE_CHECKLIST_READY_REVIEW_ONLY / REVIEW_ONLY_NON_ADVANCING / NO_EXECUTION_UNLOCK",
        "description": "Day118 turns the seven Day117 deferred ownership matrix records into a reviewer sequence runbook and evidence intake checklist. It does not change deferred conclusions, generate readiness, advance next stage, unlock execution, or enter broker, runner, adapter, SSH, live access, mapped task, OpenAI API, or voice runtime paths.",
        "json_globs": [DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_JSON.as_posix()],
        "html_globs": [DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_TASK_ID}"
        ),
    },
    {
        "day": "Day119",
        "title": "Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log",
        "report_type": "Reviewer-only evidence intake outcome ledger",
        "safety_label": "Records Day118 evidence intake outcomes only; INTAKE_LEDGER_READY / REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION / NO_ACCEPTANCE / NO_EXECUTION_UNLOCK",
        "description": "Day119 records received, partial, missing, deferred, rejected, and clarification-needed intake outcomes for the seven Day118 expected evidence items. It does not judge acceptance, produce sign-off, release safety boundaries, unlock execution, invoke broker or adapter paths, change parser capability, use SSH, or contact live devices.",
        "json_globs": [DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_JSON.as_posix()],
        "html_globs": [DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_TASK_ID}"
        ),
    },
    {
        "day": "Day123",
        "title": "Safety Boundary Regression Matrix",
        "report_type": "Report-only safety boundary regression matrix",
        "safety_label": "REPORT_ONLY_SAFETY_BOUNDARY_REGRESSION; no execution, SSH, live commands, mutation, unlock, adapter/broker/runner invocation, OpenAI API, voice runtime, or dashboard POST actions",
        "description": "Day123 verifies that safety-critical mock, review-only, report-only, dry-run-only, fake-adapter-only, locked, disabled, and Day120-Day122 refactor-boundary surfaces remain non-executing after the registry, CLI dispatch, and report-index responsibility splits.",
        "json_globs": [DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_JSON.as_posix()],
        "html_globs": [DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_TASK_ID}"
        ),
    },
    {
        "day": "Day124",
        "title": "Safety Invariant Helper Consolidation",
        "report_type": "Review-only safety invariant helper consolidation",
        "safety_label": "REVIEW_ONLY; execution_allowed=false; OpenAI API, voice input, SSH, live device, live command, runtime unlock, dashboard POST/action, broker, mapped task, write, and configuration change flags remain false",
        "description": "Day124 consolidates common deterministic safety invariant helpers for AI intent, reviewer, provider, dry-run, and report-only tasks without adding execution capability.",
        "json_globs": [DAY124_SAFETY_INVARIANT_HELPER_REVIEW_JSON.as_posix()],
        "html_globs": [DAY124_SAFETY_INVARIANT_HELPER_REVIEW_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY124_SAFETY_INVARIANT_HELPER_REVIEW_TASK_ID}"
        ),
    },
    {
        "day": "Day125",
        "title": "Thin CLI Regression Gate",
        "report_type": "Report-only thin CLI regression gate",
        "safety_label": "REPORT_ONLY; allowed_to_execute=false; SSH, live command, OpenAI API, dashboard action endpoint, and next phase unlock remain false",
        "description": "Day125 verifies that registry, dispatch, report visibility, formatter, and safety helper behavior did not regress after Day120-Day124 while keeping network_lab.py as a thin CLI entrypoint wrapper.",
        "json_globs": [DAY125_THIN_CLI_REGRESSION_GATE_JSON.as_posix()],
        "html_globs": [DAY125_THIN_CLI_REGRESSION_GATE_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY125_THIN_CLI_REGRESSION_GATE_TASK_ID}"
        ),
    },
    {
        "day": "Day126",
        "title": "Post-Refactor Compatibility Evidence Pack",
        "report_type": "Report-only post-refactor compatibility evidence pack",
        "safety_label": "REPORT_ONLY; REVIEWER_ONLY; Day125 thin CLI is snapshot-only; no budget gate, SSH, live command, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or next phase unlock",
        "description": "Day126 packages compatibility evidence for Day120-Day125 responsibility-split work while keeping the Day125 thin CLI regression gate represented only as one snapshot, not a budget gate or numeric enforcement mechanism.",
        "json_globs": [DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_JSON.as_posix()],
        "html_globs": [DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_TASK_ID}"
        ),
    },
    {
        "day": "Day127",
        "title": "AI Reviewer Summary Schema Contract Integration",
        "report_type": "Report-only AI reviewer summary data structure contract",
        "safety_label": "REPORT_ONLY; REVIEWER_ONLY; schema/validation/fixture only; no Day128 renderer, Day129 prompt text, Day130 redaction policy, SSH, live command, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or execution unlock",
        "description": "Day127 integrates the AI reviewer summary data structure contract with validation, an example fixture, CLI task evidence, tests, and documentation while explicitly leaving renderer, prompt text, and redaction policy work for later days.",
        "json_globs": [DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day128",
        "title": "AI Reviewer Summary Fixture Renderer",
        "report_type": "Report-only Day127 schema fixture renderer",
        "safety_label": "REPORT_ONLY; FIXTURE_ONLY; NON_EXECUTABLE; renders Day127 schema fixture only; no AI decision, prompt contract, redaction policy, SSH, live command, OpenAI API, provider, API enablement, execution unlock, next-day feature, or next-phase approval",
        "description": "Day128 renders the existing Day127 AI reviewer summary schema fixture into deterministic reviewer-facing text/HTML/JSON evidence without redefining schema or advancing Day129-Day131 scope.",
        "json_globs": [DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_JSON.as_posix()],
        "html_globs": [DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TASK_ID}"
        ),
    },
    {
        "day": "Day129",
        "title": "AI Summary Prompt Contract for Reviewer Text Only",
        "report_type": "Report-only reviewer-text-only prompt contract",
        "safety_label": "REPORT_ONLY; PROMPT_CONTRACT_ONLY; REVIEWER_TEXT_ONLY; no execution, provider/API access, tool calls, secrets, redaction policy, audit trail binding, AI approval, pass/fail decision, next phase unlock, or OpenAI API call",
        "description": "Day129 defines the deterministic prompt contract for future AI reviewer summary text only, referencing Day127 schema and Day128 renderer expectations without advancing Day130-Day133 scope.",
        "json_globs": [DAY129_AI_SUMMARY_PROMPT_CONTRACT_JSON.as_posix()],
        "html_globs": [DAY129_AI_SUMMARY_PROMPT_CONTRACT_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY129_AI_SUMMARY_PROMPT_CONTRACT_TASK_ID}"
        ),
    },
    {
        "day": "Day130",
        "title": "AI Summary Redaction and No-Secret Policy",
        "report_type": "Report-only deterministic local redaction policy",
        "safety_label": "REPORT_ONLY; REVIEW_ONLY; LOCAL_ONLY; deterministic redaction/no-secret policy; no execution, provider/API access, OpenAI API call, network calls, AI decision, reviewer approval inference, audit trail binding, mock provider behavior, or next phase unlock",
        "description": "Day130 checks and redacts obvious secret-like reviewer summary text before any future AI audit, approval, or provider flow exists, without advancing Day131-Day133 scope.",
        "json_globs": [DAY130_AI_SUMMARY_REDACTION_POLICY_JSON.as_posix()],
        "html_globs": [DAY130_AI_SUMMARY_REDACTION_POLICY_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY130_AI_SUMMARY_REDACTION_POLICY_TASK_ID}"
        ),
    },
    {
        "day": "Day131",
        "title": "AI Summary Audit Trail Binding",
        "report_type": "Report-only deterministic audit trail binding",
        "safety_label": "REPORT_ONLY; REVIEW_ONLY; NON_ADVANCING; binds Day127-Day130 evidence only; no provider/API, AI execution, AI decision, reviewer approval gate, mock provider boundary, SSH, device, broker, runner, adapter, live execution, or next phase unlock",
        "description": "Day131 binds existing Day127-Day130 AI summary schema, fixture renderer, prompt contract, and redaction/no-secret policy references into deterministic reviewer-visible audit records without advancing Day132-Day133 scope.",
        "json_globs": [DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_JSON.as_posix()],
        "html_globs": [DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_HTML.as_posix()],
        "missing_note": (
            "Generate with: python network_lab.py --task "
            f"{DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_TASK_ID}"
        ),
    },
]


VRRP_EVIDENCE_CATALOG = [
    {
        "group": "Topology and planning",
        "day": "Day31",
        "title": "HA / VRRP topology plan",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/ha_vrrp_topology_plan.md",
        "description": "v0.2 HA/VRRP topology intent, router roles, VIP, VRID, and lab relationship.",
        "safety_level": "documentation_only",
        "demo_relevance": "Introduces the HA/VRRP story before showing generated evidence.",
    },
    {
        "group": "Safety model",
        "day": "Day31",
        "title": "HA / VRRP safety model",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/ha_vrrp_safety_model.md",
        "description": "Safety vocabulary and boundaries for documentation-only, read-only, dry-run, and guarded workflows.",
        "safety_level": "documentation_only",
        "demo_relevance": "Explains why Day39 does not run SSH or change device state.",
    },
    {
        "group": "Topology and planning",
        "day": "Day31",
        "title": "MikroTik + Cisco lab topology v0.2 diagram",
        "artifact_type": "Diagram",
        "path": "docs/assets/mikrotik-cisco-lab-topology-v0.2.png",
        "description": "Portfolio diagram for the planned MikroTik + Cisco v0.2 HA topology.",
        "safety_level": "documentation_only",
        "demo_relevance": "Gives reviewers a visual anchor for VRRP evidence.",
    },
    {
        "group": "Topology and planning",
        "day": "Day36",
        "title": "MikroTik + Cisco lab topology v0.2 final diagram",
        "artifact_type": "Diagram",
        "path": "docs/assets/mikrotik-cisco-lab-topology-v0.2-final.png",
        "description": "Final topology diagram used by the post-failover evidence narrative.",
        "safety_level": "documentation_only",
        "demo_relevance": "Supports the final v0.2 topology presentation.",
    },
    {
        "group": "Read-only precheck",
        "day": "Day32",
        "title": "VRRP read-only precheck JSON",
        "artifact_type": "JSON report",
        "path": DAY32_VRRP_PRECHECK_JSON.as_posix(),
        "description": "Read-only RouterOS state collection summary for HA/VRRP readiness.",
        "safety_level": "read-only",
        "demo_relevance": "Shows pre-failover state evidence without configuration changes.",
    },
    {
        "group": "Read-only precheck",
        "day": "Day32",
        "title": "VRRP read-only precheck HTML",
        "artifact_type": "HTML report",
        "path": DAY32_VRRP_PRECHECK_HTML.as_posix(),
        "description": "Human-readable Day32 readiness report.",
        "safety_level": "read-only",
        "demo_relevance": "Primary reviewer-facing Day32 report.",
    },
    {
        "group": "Read-only precheck",
        "day": "Day32",
        "title": "VRRP read-only precheck TXT",
        "artifact_type": "TXT report",
        "path": DAY32_VRRP_PRECHECK_TXT.as_posix(),
        "description": "Plain-text Day32 report companion.",
        "safety_level": "read-only",
        "demo_relevance": "Useful fallback evidence for console-style review.",
    },
    {
        "group": "Topology and planning",
        "day": "Day33",
        "title": "VRRP topology dry-run profile",
        "artifact_type": "Profile",
        "path": "topology_profiles/day33_vrrp_topology_dry_run.json",
        "description": "Local profile that defines the intended VRRP topology and command preview inputs.",
        "safety_level": "dry-run",
        "demo_relevance": "Shows dry-run inputs without touching devices.",
    },
    {
        "group": "Topology and planning",
        "day": "Day33",
        "title": "VRRP topology dry-run JSON",
        "artifact_type": "JSON report",
        "path": DAY33_VRRP_DRY_RUN_JSON.as_posix(),
        "description": "Generated local dry-run evidence for VRRP topology design and command previews.",
        "safety_level": "dry-run",
        "demo_relevance": "Demonstrates planned commands as text only.",
    },
    {
        "group": "Topology and planning",
        "day": "Day33",
        "title": "VRRP topology dry-run HTML",
        "artifact_type": "HTML report",
        "path": DAY33_VRRP_DRY_RUN_HTML.as_posix(),
        "description": "Human-readable Day33 dry-run topology report.",
        "safety_level": "dry-run",
        "demo_relevance": "Primary reviewer-facing Day33 report.",
    },
    {
        "group": "Topology and planning",
        "day": "Day33",
        "title": "VRRP topology dry-run TXT",
        "artifact_type": "TXT report",
        "path": DAY33_VRRP_DRY_RUN_TXT.as_posix(),
        "description": "Plain-text Day33 dry-run report companion.",
        "safety_level": "dry-run",
        "demo_relevance": "Useful fallback evidence for command preview review.",
    },
    {
        "group": "Topology and planning",
        "day": "Day34",
        "title": "VRRP staged apply plan profile",
        "artifact_type": "Profile",
        "path": "topology_profiles/day34_vrrp_staged_apply_plan.json",
        "description": "Local profile for staged backup-then-primary apply planning.",
        "safety_level": "dry-run",
        "demo_relevance": "Shows staged planning inputs without live execution.",
    },
    {
        "group": "Topology and planning",
        "day": "Day34",
        "title": "VRRP staged apply plan JSON",
        "artifact_type": "JSON report",
        "path": DAY34_VRRP_STAGED_PLAN_JSON.as_posix(),
        "description": "Generated Day34 blocked plan-only safety gate report.",
        "safety_level": "dry-run",
        "demo_relevance": "Shows the safety gate and blocked live execution boundary.",
    },
    {
        "group": "Topology and planning",
        "day": "Day34",
        "title": "VRRP staged apply plan HTML",
        "artifact_type": "HTML report",
        "path": DAY34_VRRP_STAGED_PLAN_HTML.as_posix(),
        "description": "Human-readable Day34 staged apply plan report.",
        "safety_level": "dry-run",
        "demo_relevance": "Primary reviewer-facing Day34 report.",
    },
    {
        "group": "Topology and planning",
        "day": "Day34",
        "title": "VRRP staged apply plan TXT",
        "artifact_type": "TXT report",
        "path": DAY34_VRRP_STAGED_PLAN_TXT.as_posix(),
        "description": "Plain-text Day34 report companion.",
        "safety_level": "dry-run",
        "demo_relevance": "Useful fallback evidence for staged plan review.",
    },
    {
        "group": "Live validation evidence",
        "day": "Day35",
        "title": "VRRP failover validation plan",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day35_vrrp_failover_validation_plan.md",
        "description": "Plan for controlled manual external VRRP failover observation.",
        "safety_level": "controlled_failover_observation",
        "demo_relevance": "Explains the human-in-the-loop failover evidence flow.",
    },
    {
        "group": "Live validation evidence",
        "day": "Day35",
        "title": "VRRP failover validation safety note",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day35_vrrp_failover_validation_safety.md",
        "description": "Safety boundary for Day35 controlled failover observation.",
        "safety_level": "controlled_failover_observation",
        "demo_relevance": "Shows that automation observed only and did not trigger destructive changes.",
    },
    {
        "group": "Live validation evidence",
        "day": "Day35",
        "title": "VRRP failover validation JSON",
        "artifact_type": "JSON report",
        "path": DAY35_VRRP_FAILOVER_JSON.as_posix(),
        "description": "Structured Day35 failover and recovery evidence.",
        "safety_level": "controlled_failover_observation",
        "demo_relevance": "Core proof point for the v0.2 HA/VRRP milestone.",
    },
    {
        "group": "Live validation evidence",
        "day": "Day35",
        "title": "VRRP failover validation HTML",
        "artifact_type": "HTML report",
        "path": DAY35_VRRP_FAILOVER_HTML.as_posix(),
        "description": "Human-readable Day35 failover evidence report.",
        "safety_level": "controlled_failover_observation",
        "demo_relevance": "Primary reviewer-facing Day35 report.",
    },
    {
        "group": "Live validation evidence",
        "day": "Day35",
        "title": "VRRP failover validation TXT",
        "artifact_type": "TXT report",
        "path": DAY35_VRRP_FAILOVER_TXT.as_posix(),
        "description": "Plain-text Day35 report companion.",
        "safety_level": "controlled_failover_observation",
        "demo_relevance": "Useful fallback evidence for failover review.",
    },
    {
        "group": "Evidence hardening / regression policy",
        "day": "Day36",
        "title": "VRRP evidence review and report hardening",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day36_vrrp_failover_evidence_review_report_hardening.md",
        "description": "Documents the Day35 evidence review, report summary hardening, and report-index visibility.",
        "safety_level": "report-only",
        "demo_relevance": "Shows the evidence chain was reviewed after the live milestone.",
    },
    {
        "group": "Evidence hardening / regression policy",
        "day": "Day37",
        "title": "VRRP report regression and evidence snapshot policy",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day37_vrrp_report_regression_evidence_policy.md",
        "description": "Offline regression guard and generated evidence snapshot policy.",
        "safety_level": "report-only",
        "demo_relevance": "Explains why full runtime reports stay local while contracts are tested.",
    },
    {
        "group": "Evidence hardening / regression policy",
        "day": "Day38",
        "title": "Post-VRRP milestone review and v0.2 scope planning",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day38_post_vrrp_milestone_review_and_v0_2_scope_planning.md",
        "description": "Milestone review and conservative next-scope planning after Day31-Day37.",
        "safety_level": "report-only",
        "demo_relevance": "Frames Day39 dashboard integration as the next safe v0.2 step.",
    },
    {
        "group": "Dashboard integration status",
        "day": "Day39",
        "title": "VRRP evidence dashboard integration note",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day39_vrrp_evidence_dashboard_integration.md",
        "description": "Documents Day39 report-only scope, safety boundary, outputs, and v0.2 demo relevance.",
        "safety_level": "report-only",
        "demo_relevance": "Gives reviewers a concise Day39 scope and safety handoff.",
    },
    {
        "group": "Dashboard integration status",
        "day": "Day39",
        "title": "VRRP evidence dashboard integration JSON",
        "artifact_type": "JSON report",
        "path": DAY39_VRRP_EVIDENCE_JSON.as_posix(),
        "description": "Day39 summary generated from local Day31-Day38 evidence only.",
        "safety_level": "report-only",
        "demo_relevance": "Provides a single machine-readable VRRP evidence inventory for the dashboard and report index.",
    },
    {
        "group": "Dashboard integration status",
        "day": "Day39",
        "title": "VRRP evidence dashboard integration HTML",
        "artifact_type": "HTML report",
        "path": DAY39_VRRP_EVIDENCE_HTML.as_posix(),
        "description": "Day39 reviewer-facing VRRP evidence inventory.",
        "safety_level": "report-only",
        "demo_relevance": "Provides a single HTML handoff for the HA/VRRP evidence chain.",
    },
    {
        "group": "v0.2 demo readiness",
        "day": "Day40",
        "title": "v0.2 demo readiness review",
        "artifact_type": "Documentation",
        "path": "docs/roadmap/day40_v0.2_demo_readiness_review.md",
        "description": "Locks the v0.2 demo scope and records Day40 as report-only.",
        "safety_level": "report-only",
        "demo_relevance": "Gives reviewers the v0.2 scope boundary before release packaging.",
    },
    {
        "group": "v0.2 demo readiness",
        "day": "Day40",
        "title": "v0.2 portfolio demo checklist",
        "artifact_type": "Documentation",
        "path": "docs/portfolio_v0.2_demo_checklist.md",
        "description": "Pre-demo, dashboard, report-index, evidence traceability, safety, and go/no-go checklist.",
        "safety_level": "report-only",
        "demo_relevance": "Provides the operator checklist for a safe portfolio walkthrough.",
    },
    {
        "group": "v0.2 demo readiness",
        "day": "Day40",
        "title": "v0.2 demo readiness JSON",
        "artifact_type": "JSON report",
        "path": DAY40_DEMO_READINESS_JSON.as_posix(),
        "description": "Machine-readable Day40 demo readiness and scope-lock report.",
        "safety_level": "report-only",
        "demo_relevance": "Lets report index and dashboard discovery surface the Day40 scope lock.",
    },
    {
        "group": "v0.2 demo readiness",
        "day": "Day40",
        "title": "v0.2 demo readiness HTML",
        "artifact_type": "HTML report",
        "path": DAY40_DEMO_READINESS_HTML.as_posix(),
        "description": "Reviewer-facing Day40 demo readiness and scope-lock report.",
        "safety_level": "report-only",
        "demo_relevance": "Acts as the final human-readable handoff before v0.2 packaging.",
    },
    {
        "group": "v0.2 release packaging",
        "day": "Day41",
        "title": "v0.2 release package document",
        "artifact_type": "Markdown doc",
        "path": DAY41_RELEASE_PACKAGE_DOC.as_posix(),
        "description": "Packages the Day31-Day40 HA/VRRP milestone, safety model, dashboard/report integration, limitations, Day42 next step, and v3.0 roadmap note.",
        "safety_level": "report-only",
        "demo_relevance": "Gives reviewers one canonical v0.2 package summary before tag preparation.",
    },
    {
        "group": "v0.2 release packaging",
        "day": "Day41",
        "title": "v0.2 artifact checklist",
        "artifact_type": "Markdown doc",
        "path": DAY41_ARTIFACT_CHECKLIST_DOC.as_posix(),
        "description": "Tracks required, optional, ignored generated, Day42-deferred, and v3.0-deferred release artifacts.",
        "safety_level": "report-only",
        "demo_relevance": "Shows release readiness and intentionally deferred work without implying a completed tag.",
    },
    {
        "group": "v0.2 release packaging",
        "day": "Day41",
        "title": "v0.2 demo handoff guide",
        "artifact_type": "Markdown doc",
        "path": DAY41_DEMO_HANDOFF_DOC.as_posix(),
        "description": "Defines the interview/demo order and safety-level explanation for the v0.2 portfolio handoff.",
        "safety_level": "report-only",
        "demo_relevance": "Provides the recommended reviewer path through README, topology, catalog, dashboard, reports, and roadmap.",
    },
    {
        "group": "v0.2 release packaging",
        "day": "Day41",
        "title": "v0.2 release packaging JSON",
        "artifact_type": "JSON report",
        "path": DAY41_RELEASE_PACKAGING_JSON.as_posix(),
        "description": "Machine-readable Day41 release packaging status and safety summary.",
        "safety_level": "report-only",
        "demo_relevance": "Lets report index and dashboard discovery surface the Day41 package handoff.",
    },
    {
        "group": "v0.2 release packaging",
        "day": "Day41",
        "title": "v0.2 release packaging HTML",
        "artifact_type": "HTML report",
        "path": DAY41_RELEASE_PACKAGING_HTML.as_posix(),
        "description": "Reviewer-facing Day41 release packaging status and safety summary.",
        "safety_level": "report-only",
        "demo_relevance": "Closes the v0.2 package story while leaving tag creation for Day42.",
    },
]


def load_lab_runner_profile(profile_path: Path) -> Dict[str, Any]:
    path = Path(profile_path)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Profile was not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Profile is not valid JSON: {path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Profile must contain a JSON object.")
    if not isinstance(profile.get("overview_output"), dict):
        raise ValueError("Profile must define overview_output.")
    return profile


def iter_report_items(profile: Dict[str, Any]) -> Iterator[Tuple[str, Optional[Dict[str, Any]], Dict[str, Any]]]:
    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        for report in device.get("reports", []):
            if isinstance(report, dict):
                yield "device", device, report

    for report in profile.get("lab_summary_reports", []):
        if isinstance(report, dict):
            yield "lab_summary", None, report


def normalize_result(value: Any) -> str:
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if value is None:
        return "UNKNOWN"

    normalized = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "OK": "PASS",
        "SUCCESS": "PASS",
        "SUCCEEDED": "PASS",
        "PASSED": "PASS",
        "TRUE": "PASS",
        "ERROR": "FAIL",
        "FAILED": "FAIL",
        "FALSE": "FAIL",
        "WARNING": "WARN",
        "WARNINGS": "WARN",
        "PARTIAL": "WARN",
        "MISSING": "MISSING",
        "INCOMPLETE": "INCOMPLETE",
        "UNKNOWN": "UNKNOWN",
        "SKIPPED": "SKIP",
        "SKIP": "SKIP",
        "N_A": "SKIP",
        "NA": "SKIP",
        "NOT_RUN": "NOT_RUN",
        "NOTRUN": "NOT_RUN",
        "NOT_GENERATED": "NOT_GENERATED",
        "NOTGENERATED": "NOT_GENERATED",
    }
    return aliases.get(normalized, normalized if normalized in RESULTS else "UNKNOWN")


def infer_report_result(json_data: Any) -> str:
    if not isinstance(json_data, dict):
        return "UNKNOWN"

    for key in (
        "overall_result",
        "overall_status",
        "result",
        "overall_decision",
        "status",
        "passed",
        "validation_result",
    ):
        if key in json_data:
            return normalize_result(json_data.get(key))

    for container_key in ("summary", "aggregate", "day13", "Day13 summary"):
        nested = json_data.get(container_key)
        if isinstance(nested, dict):
            for key in (
                "overall_result",
                "overall_status",
                "result",
                "overall_decision",
                "status",
                "passed",
                "validation_result",
            ):
                if key in nested:
                    return normalize_result(nested.get(key))

    return "UNKNOWN"


def check_report_file(report_item: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    root = Path(project_root)
    json_path = root / str(report_item.get("json", ""))
    html_path = root / str(report_item.get("html", ""))
    record = {
        "name": report_item.get("name", "Unnamed Report"),
        "json": str(report_item.get("json", "")),
        "html": str(report_item.get("html", "")),
        "required": bool(report_item.get("required", False)),
        "status": "MISSING",
        "exists": json_path.exists(),
        "html_exists": html_path.exists(),
        "message": "",
    }

    if not record["exists"]:
        record["message"] = "JSON report is missing."
        return record

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        record["status"] = "UNKNOWN"
        record["message"] = f"Invalid JSON: {exc.msg}"
        return record
    except OSError as exc:
        record["status"] = "UNKNOWN"
        record["message"] = f"Could not read JSON report: {exc}"
        return record

    record["status"] = infer_report_result(data)
    if record["status"] == "UNKNOWN":
        record["message"] = "Could not infer result from supported report fields."
    return record


def compute_overall_result(report_records: List[Dict[str, Any]]) -> str:
    if not report_records or not any(record.get("exists") for record in report_records):
        return "INCOMPLETE"

    statuses = [record.get("status", "UNKNOWN") for record in report_records]
    if "FAIL" in statuses:
        return "FAIL"
    if any(record.get("required") and record.get("status") == "MISSING" for record in report_records):
        return "INCOMPLETE"
    if any(status in {"MISSING", "UNKNOWN", "WARN", "SKIP", "NOT_RUN", "INCOMPLETE"} for status in statuses):
        return "WARN"
    return "PASS"


def _empty_counts() -> Dict[str, int]:
    return {
        "total": 0,
        "pass": 0,
        "fail": 0,
        "warn": 0,
        "missing": 0,
        "unknown": 0,
        "skip": 0,
        "not_run": 0,
    }


def _update_counts(counts: Dict[str, int], status: str) -> None:
    counts["total"] += 1
    key = status.lower()
    if key in counts:
        counts[key] += 1


def _vrrp_artifact_status(project_root: Path, relative_path: str) -> str:
    path = Path(project_root) / relative_path
    if path.exists():
        return "FOUND"
    if relative_path.startswith("reports/"):
        return "NOT_GENERATED"
    return "MISSING"


def _vrrp_artifact_modified_at(project_root: Path, relative_path: str) -> str:
    path = Path(project_root) / relative_path
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime).replace(microsecond=0).isoformat(sep=" ")


def discover_vrrp_evidence(project_root: Path) -> List[Dict[str, Any]]:
    entries = []
    for item in VRRP_EVIDENCE_CATALOG:
        relative_path = str(item["path"])
        status = _vrrp_artifact_status(project_root, relative_path)
        entries.append(
            {
                "group": item["group"],
                "day": item["day"],
                "title": item["title"],
                "artifact_type": item["artifact_type"],
                "path": relative_path,
                "status": status,
                "exists": status == "FOUND",
                "description": item["description"],
                "safety_level": item["safety_level"],
                "demo_relevance": item["demo_relevance"],
                "modified_at": _vrrp_artifact_modified_at(project_root, relative_path),
            }
        )
    return entries


def summarize_vrrp_evidence(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {"total": 0, "found": 0, "missing": 0, "not_generated": 0}
    by_group: Dict[str, Dict[str, int]] = {}
    for entry in entries:
        status = str(entry.get("status", "MISSING"))
        group = str(entry.get("group", "Ungrouped"))
        counts["total"] += 1
        if status == "FOUND":
            counts["found"] += 1
        elif status == "NOT_GENERATED":
            counts["not_generated"] += 1
        else:
            counts["missing"] += 1
        group_counts = by_group.setdefault(group, {"total": 0, "found": 0, "missing": 0, "not_generated": 0})
        group_counts["total"] += 1
        if status == "FOUND":
            group_counts["found"] += 1
        elif status == "NOT_GENERATED":
            group_counts["not_generated"] += 1
        else:
            group_counts["missing"] += 1
    return {"counts": counts, "groups": by_group}


def build_day39_vrrp_evidence_report(project_root: Path) -> Dict[str, Any]:
    entries = discover_vrrp_evidence(project_root)
    summary = summarize_vrrp_evidence(entries)
    missing_count = summary["counts"]["missing"] + summary["counts"]["not_generated"]
    readiness_status = "READY" if missing_count == 0 else "NEEDS_REVIEW"
    overall_status = "PASS" if missing_count == 0 else "WARN"
    return {
        "day": "Day39",
        "title": "VRRP Evidence Dashboard Integration",
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "overall_status": overall_status,
        "readiness_status": readiness_status,
        "purpose": "Integrate Day31-Day38 HA/VRRP evidence into dashboard and report-index visibility.",
        "safety_scope": {
            "live_tests_executed": False,
            "ssh_connections_opened": False,
            "router_configuration_changed": False,
            "notes": "Day39 scans local documentation, diagrams, profiles, and generated reports only.",
        },
        "outputs": {
            "json": DAY39_VRRP_EVIDENCE_JSON.as_posix(),
            "html": DAY39_VRRP_EVIDENCE_HTML.as_posix(),
        },
        "summary": summary,
        "evidence": entries,
        "missing_optional_artifacts": [
            entry for entry in entries if entry["status"] in {"MISSING", "NOT_GENERATED"}
        ],
    }


def build_day40_demo_readiness_report(project_root: Path) -> Dict[str, Any]:
    evidence_entries = [
        entry
        for entry in discover_vrrp_evidence(project_root)
        if str(entry.get("day", "")) in {f"Day{day}" for day in range(31, 40)}
    ]
    traceability = [
        {
            "day": entry.get("day", ""),
            "artifact": entry.get("title", ""),
            "artifact_type": entry.get("artifact_type", ""),
            "path": entry.get("path", ""),
            "status": entry.get("status", "MISSING"),
            "safety_level": entry.get("safety_level", ""),
            "demo_relevance": entry.get("demo_relevance", ""),
        }
        for entry in evidence_entries
    ]
    demo_checklist = [
        {"category": "Pre-demo", "item": "README opens with v0.2 HA / VRRP context visible.", "status": "PASS"},
        {"category": "Dashboard", "item": "Dashboard /reports can show local evidence cards without running live workflows.", "status": "PASS"},
        {"category": "Report Index", "item": "Report index discovers generated JSON/HTML evidence when present.", "status": "PASS"},
        {"category": "Latest Lab Overview", "item": "Latest overview includes HA / VRRP evidence metadata through local discovery.", "status": "PASS"},
        {"category": "Safety", "item": "Demo story explicitly separates report-only review from read-only or guarded live tasks.", "status": "PASS"},
        {"category": "Scope Lock", "item": "v0.2 demo excludes new live tests, SSH, and device configuration changes.", "status": "PASS"},
    ]
    return mask_secret_values(
        {
            "day": 40,
            "task_name": DAY40_DEMO_READINESS_TASK_ID,
            "title": "v0.2 Demo Readiness Review and Scope Lock",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "overall_status": "PASS",
            "demo_readiness_status": "READY_WITH_LIMITATIONS",
            "task_type": "report-only",
            "safety_level": "report_only",
            "live_test": False,
            "ssh_used": False,
            "device_config_changed": False,
            "safety_statement": (
                "Day40 is report-only. It does not run live tests, does not use SSH, "
                "and does not change MikroTik, Cisco, firewall, NAT, IP, VRRP, or interface settings."
            ),
            "scope_included": [
                "Day31-Day39 HA / VRRP milestone summary.",
                "v0.2 demo scope lock for portfolio review.",
                "Dashboard, report index, latest overview, and evidence traceability checks.",
                "Generated JSON and HTML portfolio readiness reports.",
                "Known limitations and next-step planning for v0.2 release packaging.",
            ],
            "scope_excluded": [
                "New live VRRP tests or failover injection.",
                "Any SSH operation or credential access.",
                "MikroTik, Cisco, firewall, NAT, IP, VRRP, or interface configuration changes.",
                "New scripts that perform live network changes.",
                "Changes to Day31-Day39 evidence semantics.",
                "CLI tab completion, command tree, and AI report assistant implementation.",
            ],
            "day31_to_day39_summary": [
                {"day": "Day31", "summary": "Created HA / VRRP topology and safety planning docs.", "status": "Complete"},
                {"day": "Day32", "summary": "Added VRRP read-only precheck with safety guard and reports.", "status": "Complete"},
                {"day": "Day33", "summary": "Added VRRP topology dry-run and command preview without SSH.", "status": "Complete"},
                {"day": "Day34", "summary": "Added staged apply plan and safety gate while blocking live execution.", "status": "Complete"},
                {"day": "Day35", "summary": "Captured controlled failover observation with manual external trigger and read-only evidence.", "status": "Complete"},
                {"day": "Day36", "summary": "Hardened Day35 evidence readability, report-index visibility, and portfolio traceability.", "status": "Complete"},
                {"day": "Day37", "summary": "Recorded regression guards and evidence snapshot policy for VRRP reports.", "status": "Complete"},
                {"day": "Day38", "summary": "Reviewed the post-VRRP milestone and proposed conservative v0.2 scope.", "status": "Complete"},
                {"day": "Day39", "summary": "Integrated HA / VRRP evidence into dashboard and report-index visibility.", "status": "Complete"},
            ],
            "demo_checklist": demo_checklist,
            "evidence_traceability": traceability,
            "dashboard_walkthrough": [
                {"step": 1, "surface": "README", "check": "Confirm v0.2 HA / VRRP project context and safety posture."},
                {"step": 2, "surface": "Task Catalog", "check": "Run demo navigation command `python network_lab.py --list-tasks --verbose` and point out safety levels."},
                {"step": 3, "surface": "Report Index", "check": "Run demo navigation command `python network_lab.py --task report-index` and open `reports/report_index.html`."},
                {"step": 4, "surface": "Dashboard", "check": "Open `/reports` and review HA / VRRP evidence cards without starting live workflows."},
                {"step": 5, "surface": "Portfolio Reports", "check": "Open Day39 and Day40 HTML reports to close the v0.2 story."},
            ],
            "known_limitations": [
                "The Day35 failover trigger remains manual and physical.",
                "The v0.2 demo relies on local generated reports being present when screenshots are needed.",
                "Topology variants beyond the two-router MikroTik HA lab remain future work.",
                "AI summaries and CLI command tree improvements are intentionally out of Day40 scope.",
            ],
            "next_steps": [
                {"day": "Day41", "item": "v0.2 release package."},
                {"day": "Day42", "item": "v0.2 tag / release note."},
                {"day": "Day43 or later", "item": "CLI tab completion / command tree."},
                {"day": "Day43 or later", "item": "AI report assistant."},
            ],
            "outputs": {
                "json": DAY40_DEMO_READINESS_JSON.as_posix(),
                "html": DAY40_DEMO_READINESS_HTML.as_posix(),
            },
        }
    )


def build_day41_release_packaging_report(project_root: Path) -> Dict[str, Any]:
    package_docs = [
        DAY41_RELEASE_PACKAGE_DOC,
        DAY41_ARTIFACT_CHECKLIST_DOC,
        DAY41_DEMO_HANDOFF_DOC,
    ]
    docs_status = [
        {
            "path": doc.as_posix(),
            "status": "FOUND" if (project_root / doc).exists() else "MISSING",
            "required": True,
        }
        for doc in package_docs
    ]
    return mask_secret_values(
        {
            "day": 41,
            "task_name": DAY41_RELEASE_PACKAGING_TASK_ID,
            "title": "Day41 v0.2 Release Packaging",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "overall_status": "PASS" if all(item["status"] == "FOUND" for item in docs_status) else "WARN",
            "task_type": "report-only",
            "safety_level": "report_only",
            "live_test": False,
            "ssh_used": False,
            "device_config_changed": False,
            "v0_2_tag_created": False,
            "voice_ai_implemented": False,
            "purpose": "Package Day31-Day40 into a v0.2 release documentation, artifact checklist, demo handoff, and optional local report.",
            "included_release_scope": [
                "Day31 HA / VRRP topology and safety model.",
                "Day32 VRRP read-only precheck.",
                "Day33 VRRP design and dry-run preview.",
                "Day34 topology diagrams, staged plan, and demo preparation.",
                "Day35 controlled VRRP failover validation evidence.",
                "Day36 final topology and evidence hardening.",
                "Day37 VRRP report regression and evidence policy.",
                "Day38 post-milestone v0.2 scope planning.",
                "Day39 dashboard/report-index evidence integration.",
                "Day40 demo readiness review and scope lock.",
            ],
            "created_or_updated_docs": docs_status,
            "safety_status": {
                "live_execution": False,
                "ssh_required": False,
                "device_config_change": False,
                "generated_reports_allowed": True,
                "notes": "Day41 reads local metadata and documentation only, then writes local package reports under reports/portfolio.",
            },
            "known_limitations": [
                "Some optional reports may be missing.",
                "Generated reports under reports/ may be ignored by .gitignore.",
                "Day41 does not create a v0.2 tag.",
                "Day41 does not prove new live behavior.",
                "Day41 only packages existing Day31-Day40 evidence.",
                "Voice + AI is future roadmap only, not implemented in v0.2.",
            ],
            "day42_next_action": "Day42: prepare the v0.2 tag and release note after final review; Day41 intentionally leaves the tag uncreated.",
            "v3_0_roadmap_note": "Voice + AI Network Test Assistant / AI-assisted Network Test Orchestration remains roadmap-only.",
            "outputs": {
                "json": DAY41_RELEASE_PACKAGING_JSON.as_posix(),
                "html": DAY41_RELEASE_PACKAGING_HTML.as_posix(),
            },
        }
    )


def build_latest_lab_overview(profile: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    counts = _empty_counts()
    all_records: List[Dict[str, Any]] = []
    devices = []

    for device in profile.get("devices", []):
        if not isinstance(device, dict):
            continue
        device_reports = []
        for report in device.get("reports", []):
            if not isinstance(report, dict):
                continue
            record = check_report_file(report, project_root)
            device_reports.append(record)
            all_records.append(record)
            _update_counts(counts, record["status"])
        devices.append(
            {
                "name": device.get("name", "Unnamed Device"),
                "type": device.get("type", "unknown"),
                "required": bool(device.get("required", False)),
                "reports": device_reports,
            }
        )

    lab_summary_reports = []
    for report in profile.get("lab_summary_reports", []):
        if not isinstance(report, dict):
            continue
        record = check_report_file(report, project_root)
        lab_summary_reports.append(record)
        all_records.append(record)
        _update_counts(counts, record["status"])

    return {
        "day": "Day14",
        "name": DAY14_NAME,
        "lab_name": profile.get("lab_name", "Network Automation Lab"),
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "overall_result": compute_overall_result(all_records),
        "counts": counts,
        "devices": devices,
        "lab_summary_reports": lab_summary_reports,
        "ha_vrrp_evidence": discover_vrrp_evidence(project_root),
    }


def write_json_report(data: Dict[str, Any], output_path: Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mask_secret_values(data), indent=2), encoding="utf-8")


def mask_secret_values(value: Any) -> Any:
    if isinstance(value, dict):
        masked = {}
        for key, item in value.items():
            key_text = str(key)
            if any(marker in key_text.lower() for marker in SECRET_FIELD_MARKERS):
                masked[key] = "[REDACTED]"
            else:
                masked[key] = mask_secret_values(item)
        return masked
    if isinstance(value, list):
        return [mask_secret_values(item) for item in value]
    return value


def supports_color(stream: Any = sys.stdout) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return bool(getattr(stream, "isatty", lambda: False)())


def color_text(text: str, color: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
    if not supports_color():
        return text

    parts = []
    if bold:
        parts.append(ANSI_BOLD)
    if dim:
        parts.append(ANSI_DIM)
    if color:
        parts.append(ANSI_COLORS.get(color, ""))
    parts.append(text)
    parts.append(ANSI_RESET)
    return "".join(parts)


def format_status(status: str) -> str:
    normalized = normalize_result(status)
    return color_text(f"[{normalized}]", STATUS_COLORS.get(normalized), bold=True)


def format_heading(text: str) -> str:
    return color_text(text, "cyan", bold=True)


def build_relative_link(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(Path(to_path).resolve(), Path(from_path).resolve().parent)).as_posix()


def _status_badge(status: str) -> str:
    return f'<span class="badge badge-{html.escape(status.lower())}">{html.escape(status)}</span>'


def _html_report_link(output_path: Path, report: Dict[str, Any], project_root: Path) -> str:
    if not report.get("html_exists"):
        return "MISSING"
    href = build_relative_link(output_path, project_root / report.get("html", ""))
    return f'<a href="{html.escape(href)}">{html.escape(report.get("html", ""))}</a>'


def _render_device_rows(data: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    rows = []
    for device in data.get("devices", []):
        for report in device.get("reports", []):
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(device.get('name', '')))}</td>"
                f"<td>{html.escape(str(device.get('type', '')))}</td>"
                f"<td>{html.escape(str(report.get('name', '')))}</td>"
                f"<td>{'Yes' if report.get('required') else 'No'}</td>"
                f"<td>{_status_badge(str(report.get('status', 'UNKNOWN')))}</td>"
                f"<td>{html.escape(str(report.get('json', '')) if report.get('exists') else 'MISSING')}</td>"
                f"<td>{_html_report_link(output_path, report, project_root)}</td>"
                "</tr>"
            )
    return "\n".join(rows) or '<tr><td colspan="7">No device reports configured.</td></tr>'


def _render_summary_rows(data: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    rows = []
    for report in data.get("lab_summary_reports", []):
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(report.get('name', '')))}</td>"
            f"<td>{'Yes' if report.get('required') else 'No'}</td>"
            f"<td>{_status_badge(str(report.get('status', 'UNKNOWN')))}</td>"
            f"<td>{html.escape(str(report.get('json', '')) if report.get('exists') else 'MISSING')}</td>"
            f"<td>{_html_report_link(output_path, report, project_root)}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="5">No lab summary reports configured.</td></tr>'


def _html_artifact_link_or_text(output_path: Path, project_root: Path, value: str) -> str:
    if not value or value == "MISSING":
        return html.escape(value or "")
    target = project_root / value
    if target.exists():
        href = build_relative_link(output_path, target)
        return f'<a href="{html.escape(href)}">{html.escape(value)}</a>'
    return html.escape(value)


def _render_vrrp_evidence_rows(entries: List[Dict[str, Any]], output_path: Path, project_root: Path) -> str:
    rows = []
    for entry in entries:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(entry.get('group', '')))}</td>"
            f"<td>{html.escape(str(entry.get('day', '')))}</td>"
            f"<td>{html.escape(str(entry.get('title', '')))}</td>"
            f"<td>{html.escape(str(entry.get('artifact_type', '')))}</td>"
            f"<td>{_status_badge(str(entry.get('status', 'MISSING')))}</td>"
            f"<td>{html.escape(str(entry.get('safety_level', '')))}</td>"
            f"<td>{_html_artifact_link_or_text(output_path, project_root, str(entry.get('path', '')))}</td>"
            f"<td>{html.escape(str(entry.get('demo_relevance', '')))}</td>"
            "</tr>"
        )
    return "\n".join(rows) or '<tr><td colspan="8">No HA / VRRP evidence entries configured.</td></tr>'


def write_html_overview(data: Dict[str, Any], output_path: Path, project_root: Optional[Path] = None) -> None:
    path = Path(output_path)
    root = Path(project_root or Path.cwd())
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = data.get("counts", {})
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Latest Lab Overview</title>
  <style>
    :root {{ --bg: #f5f7fb; --ink: #172033; --muted: #617089; --line: #d8e0ec; --panel: #ffffff; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); }}
    header {{ padding: 34px 38px 24px; background: #233044; color: white; }}
    main {{ padding: 28px 38px 46px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .meta {{ color: #dbe5f3; }}
    .summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; }}
    .metric {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; min-width: 112px; }}
    .metric .label {{ color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric .value {{ margin-top: 5px; font-size: 22px; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    a {{ color: #155bb5; font-weight: 700; text-decoration: none; }}
    .badge {{ display: inline-block; min-width: 74px; padding: 4px 8px; border-radius: 999px; font-weight: 800; font-size: 12px; text-align: center; }}
    .badge-pass, .badge-found {{ background: #dff7e8; color: #136b35; }}
    .badge-fail {{ background: #ffe1e1; color: #9c1d1d; }}
    .badge-warn, .badge-skip, .badge-not_run, .badge-not_generated {{ background: #fff3cc; color: #856100; }}
    .badge-missing, .badge-incomplete {{ background: #eceff5; color: #4d596b; }}
    .badge-unknown {{ background: #e5e7ff; color: #393a8a; }}
  </style>
</head>
<body>
  <header>
    <h1>Latest Lab Overview</h1>
    <div class="meta">{html.escape(str(data.get("lab_name", "")))} · Generated {html.escape(str(data.get("generated_at", "")))}</div>
    <p>Overall {_status_badge(str(data.get("overall_result", "UNKNOWN")))}</p>
  </header>
  <main>
    <section class="summary">
      <div class="metric"><div class="label">Total</div><div class="value">{counts.get("total", 0)}</div></div>
      <div class="metric"><div class="label">PASS</div><div class="value">{counts.get("pass", 0)}</div></div>
      <div class="metric"><div class="label">FAIL</div><div class="value">{counts.get("fail", 0)}</div></div>
      <div class="metric"><div class="label">WARN</div><div class="value">{counts.get("warn", 0)}</div></div>
      <div class="metric"><div class="label">MISSING</div><div class="value">{counts.get("missing", 0)}</div></div>
      <div class="metric"><div class="label">UNKNOWN</div><div class="value">{counts.get("unknown", 0)}</div></div>
    </section>

    <h2>Device Reports</h2>
    <table>
      <thead><tr><th>Device</th><th>Type</th><th>Report</th><th>Required</th><th>Status</th><th>JSON</th><th>HTML</th></tr></thead>
      <tbody>{_render_device_rows(data, path, root)}</tbody>
    </table>

    <h2>Lab Summary Reports</h2>
    <table>
      <thead><tr><th>Report</th><th>Required</th><th>Status</th><th>JSON</th><th>HTML</th></tr></thead>
      <tbody>{_render_summary_rows(data, path, root)}</tbody>
    </table>

    <h2>HA / VRRP Evidence</h2>
    <table>
      <thead><tr><th>Group</th><th>Day</th><th>Artifact</th><th>Type</th><th>Status</th><th>Safety</th><th>Path</th><th>Demo relevance</th></tr></thead>
      <tbody>{_render_vrrp_evidence_rows(data.get("ha_vrrp_evidence", []), path, root)}</tbody>
    </table>
  </main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def list_tasks() -> List[Dict[str, Any]]:
    return [
        {
            "id": "report-index",
            "task_id": "report_index",
            "display_name": "Report Index",
            "user_display_name": "Report Index",
            "day": "Day14-Day19",
            "category": "reports",
            "description": "Read local reports and build lab overview or visibility indexes.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/lab-summary/latest_lab_overview.json",
                "reports/lab-summary/latest_lab_overview.html",
                "reports/report_index.html",
                DAY19_EVIDENCE_INDEX_JSON.as_posix(),
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day14 latest lab overview JSON/HTML",
                "Day17-Day21 report viewer visibility index",
                "Day19 portfolio evidence index JSON/HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Reads local report paths only and does not connect to devices or read config.json.",
        },
        {
            "id": "portfolio-finalize",
            "task_id": "day19_runner_evidence_index",
            "display_name": "Day19 Runner Evidence Index",
            "user_display_name": "Portfolio Evidence Index",
            "day": "Day19",
            "category": "portfolio",
            "description": "Build a portfolio-ready evidence index from the task catalog and local report visibility.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY19_EVIDENCE_INDEX_JSON.as_posix(),
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day19 runner evidence index JSON",
                "Day19 runner evidence index HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Day19 finalization reads local report metadata only; generated output is safe for screenshots and portfolio review.",
        },
        {
            "id": "demo-flow",
            "task_id": "day24_rc_demo_flow",
            "display_name": "Day24 RC Demo Flow",
            "user_display_name": "RC Demo Flow",
            "day": "Day24",
            "category": "portfolio",
            "description": "Build a reviewer-friendly RC demo flow and portfolio walkthrough from local task/report metadata.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY24_DEMO_FLOW_JSON.as_posix(),
                DAY24_DEMO_FLOW_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day24 RC demo flow JSON",
                "Day24 RC demo flow HTML",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only task. Day24 demo flow reads task/report metadata only and gives reviewers a safe click-through order for RC walkthroughs.",
        },
        {
            "id": "day4-baseline",
            "task_id": "day4_baseline_validation",
            "display_name": "Day4 Multi-device Baseline Validation",
            "user_display_name": "Multi-device Baseline Validation",
            "day": "Day4",
            "category": "baseline",
            "description": "Existing Day4 multi-device RouterOS baseline validation.",
            "safety_level": "read-only",
            "execution_mode": "guarded-live",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day4_baseline_validation.json",
                "reports/<device>/day4_baseline_validation.html",
            ],
            "report_outputs": [
                "Day4 per-device baseline validation JSON/HTML",
            ],
            "related_script": DAY4_BASELINE_SCRIPT,
            "notes": "Read-only live SSH validation. Uses the existing Day4 script; interactive runner asks before delegation.",
        },
        {
            "id": "iperf3-performance",
            "task_id": "day8_iperf3_performance",
            "display_name": "Day8 iperf3 Performance",
            "user_display_name": "iperf3 Performance Test",
            "day": "Day8",
            "category": "performance",
            "description": "Existing Day8 iperf3 performance workflow.",
            "safety_level": "guarded-live",
            "execution_mode": "guarded-live",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "reports/<device>/day8_iperf3_performance_report.json",
                "reports/<device>/day8_iperf3_performance_report.html",
            ],
            "report_outputs": [
                "Day8 iperf3 performance report JSON/HTML",
            ],
            "related_script": DAY8_PERFORMANCE_SCRIPT,
            "notes": "Guarded-live performance task. Generates iperf3 traffic only after confirmation and does not modify router configuration.",
        },
        {
            "id": DAY32_VRRP_PRECHECK_TASK_ID,
            "task_id": "day32_vrrp_readonly_precheck",
            "display_name": "Day32 VRRP Read-only Precheck",
            "user_display_name": "VRRP Read-only Precheck",
            "day": "Day32",
            "category": "ha_vrrp",
            "description": "Collect HA/VRRP readiness state from MikroTik routers using read-only RouterOS commands only.",
            "safety_level": "read-only",
            "execution_mode": "read-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                DAY32_VRRP_PRECHECK_JSON.as_posix(),
                DAY32_VRRP_PRECHECK_HTML.as_posix(),
                DAY32_VRRP_PRECHECK_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day32 VRRP read-only precheck JSON",
                "Day32 VRRP read-only precheck HTML",
                "Day32 VRRP read-only precheck TXT",
            ],
            "related_script": DAY32_VRRP_PRECHECK_SCRIPT,
            "notes": "Live SSH read-only precheck. The Day32 script blocks add, set, remove, disable, enable, reboot, and reset-configuration before any MikroTik command is sent.",
        },
        {
            "id": DAY33_VRRP_DRY_RUN_TASK_ID,
            "task_id": "day33_vrrp_topology_dry_run",
            "display_name": "Day33 VRRP Topology Dry-run",
            "user_display_name": "VRRP Topology Dry-run",
            "day": "Day33",
            "category": "ha_vrrp",
            "description": "Render HA/VRRP v0.2 topology design and RouterOS command previews without connecting to devices.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY33_VRRP_DRY_RUN_JSON.as_posix(),
                DAY33_VRRP_DRY_RUN_HTML.as_posix(),
                DAY33_VRRP_DRY_RUN_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day33 VRRP topology dry-run JSON",
                "Day33 VRRP topology dry-run HTML",
                "Day33 VRRP topology dry-run TXT",
            ],
            "related_script": DAY33_VRRP_DRY_RUN_SCRIPT,
            "notes": "Safe dry-run only. The Day33 script validates the v0.2 VRRP contract, renders RouterOS command previews, and never opens SSH or executes commands.",
        },
        {
            "id": DAY34_VRRP_STAGED_PLAN_TASK_ID,
            "task_id": "day34_vrrp_staged_apply_plan",
            "display_name": "Day34 VRRP Staged Apply Plan",
            "user_display_name": "VRRP Staged Apply Plan",
            "day": "Day34",
            "category": "ha_vrrp",
            "description": "Render a staged VRRP apply plan and safety gate; live execution remains blocked.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY34_VRRP_STAGED_PLAN_JSON.as_posix(),
                DAY34_VRRP_STAGED_PLAN_HTML.as_posix(),
                DAY34_VRRP_STAGED_PLAN_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day34 VRRP staged apply plan JSON",
                "Day34 VRRP staged apply plan HTML",
                "Day34 VRRP staged apply plan TXT",
            ],
            "related_script": DAY34_VRRP_STAGED_PLAN_SCRIPT,
            "notes": "Plan-only safety gate. Day34 requires Day32/Day33 evidence for review readiness, keeps manual confirmation blocked, and never opens SSH or executes RouterOS commands.",
        },
        {
            "id": DAY35_VRRP_FAILOVER_TASK_ID,
            "task_id": "day35_vrrp_failover_validation",
            "display_name": "Day35 VRRP Failover Validation",
            "user_display_name": "VRRP Failover Validation",
            "day": "Day35",
            "category": "ha_vrrp",
            "description": "Validate that lab02 takes over the VRRP VIP after a manual external lab01 LAN failure.",
            "safety_level": "controlled_failover_observation",
            "execution_mode": "controlled_failover_observation",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_paths": [
                DAY35_VRRP_FAILOVER_JSON.as_posix(),
                DAY35_VRRP_FAILOVER_HTML.as_posix(),
                DAY35_VRRP_FAILOVER_TXT.as_posix(),
            ],
            "report_outputs": [
                "Day35 VRRP failover validation JSON",
                "Day35 VRRP failover validation HTML",
                "Day35 VRRP failover validation TXT",
            ],
            "related_script": DAY35_VRRP_FAILOVER_SCRIPT,
            "notes": "Controlled live observation. Day35 prompts the operator to disconnect/reconnect lab01 LAN externally, uses source-specific ping, sends only read-only RouterOS print commands, and blocks interface, firewall/NAT, IP, VRRP, reboot, and reset changes.",
        },
        {
            "id": DAY39_VRRP_EVIDENCE_TASK_ID,
            "task_id": "day39_vrrp_evidence_dashboard_integration",
            "display_name": "Day39 VRRP Evidence Dashboard Integration",
            "user_display_name": "VRRP Evidence Dashboard Integration",
            "day": "Day39",
            "category": "ha_vrrp",
            "description": "Generate a report-only HA/VRRP evidence inventory for dashboard and report-index visibility.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_output_path": DAY39_VRRP_EVIDENCE_JSON.as_posix(),
            "report_paths": [
                DAY39_VRRP_EVIDENCE_JSON.as_posix(),
                DAY39_VRRP_EVIDENCE_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day39 VRRP evidence integration JSON",
                "Day39 VRRP evidence integration HTML",
                "Dashboard/report-index HA / VRRP Evidence visibility",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only local scan of Day31-Day38 docs, diagrams, profiles, and generated report paths. It does not run SSH, live tests, iperf3, failover, or RouterOS/Cisco configuration changes.",
        },
        {
            "id": DAY40_DEMO_READINESS_TASK_ID,
            "task_id": "day40_v0.2_demo_readiness_review",
            "display_name": "Day40 v0.2 Demo Readiness Review",
            "user_display_name": "v0.2 Demo Readiness Review",
            "day": "Day40",
            "category": "portfolio",
            "description": "Generate a report-only v0.2 demo readiness review, scope lock, checklist, and evidence traceability report.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_output_path": DAY40_DEMO_READINESS_JSON.as_posix(),
            "report_paths": [
                DAY40_DEMO_READINESS_JSON.as_posix(),
                DAY40_DEMO_READINESS_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day40 v0.2 demo readiness JSON",
                "Day40 v0.2 demo readiness HTML",
                "Dashboard/report-index portfolio visibility",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only scope lock. Day40 does not run SSH, live tests, iperf3, failover, or MikroTik/Cisco/firewall/NAT/IP/VRRP/interface configuration changes.",
        },
        {
            "id": DAY41_RELEASE_PACKAGING_TASK_ID,
            "task_id": "day41_v0.2_release_packaging",
            "display_name": "Day41 v0.2 Release Packaging",
            "user_display_name": "v0.2 Release Packaging",
            "day": "Day41",
            "category": "portfolio",
            "description": "Generate a report-only v0.2 release package status report and point to release package, artifact checklist, and demo handoff docs.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_output_path": DAY41_RELEASE_PACKAGING_JSON.as_posix(),
            "report_paths": [
                DAY41_RELEASE_PACKAGING_JSON.as_posix(),
                DAY41_RELEASE_PACKAGING_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day41 v0.2 release packaging JSON",
                "Day41 v0.2 release packaging HTML",
                "Release package docs, artifact checklist, and demo handoff guide references",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only release packaging and documentation handoff. Day41 does not run SSH, live tests, iperf3, failover, voice, AI assistant features, v0.2 tag creation, or MikroTik/Cisco/firewall/NAT/IP/VRRP/interface configuration changes.",
        },
        {
            "id": WIREGUARD_RUNNER_TASK_ALIAS,
            "task_id": WIREGUARD_RUNNER_TASK_ID,
            "display_name": WIREGUARD_RUNNER_DISPLAY_NAME,
            "user_display_name": "WireGuard VPN Validation",
            "day": "Day18",
            "category": "vpn",
            "description": "Feature-named WireGuard runner integration for dry-run safety reporting and manually guarded live validation.",
            "safety_level": "guarded-live",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": True,
            "requires_password": True,
            "produces_report": True,
            "report_output_path": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
            "report_paths": [
                WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
                WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
            ],
            "report_outputs": [
                "Day18 WireGuard runner safety-layer result JSON/HTML",
                "Related Day12 WireGuard validation report paths when delegated evidence exists",
                "Day22 WireGuard documentation relationship for safety review",
            ],
            "related_script": DAY12_WIREGUARD_SCRIPT,
            "notes": "Dry-run is the default runner posture. Guarded live validation requires manual --allow-live-wireguard authorization and omits firewall apply, peer recreation, reset, reboot, and VPN activation logic.",
        },
        {
            "id": "day13-wireguard-summary",
            "task_id": "day13_wireguard_summary_only",
            "display_name": "Day13 WireGuard Summary Only",
            "user_display_name": "WireGuard Summary Only",
            "day": "Day13",
            "category": "vpn",
            "description": "Report-only or placeholder visibility for Day13 WireGuard summaries.",
            "safety_level": "disabled",
            "execution_mode": "report-only",
            "enabled": False,
            "status": "planned",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.json",
                "summary/day13_multi_router_wireguard_client_to_site_summary_*.html",
            ],
            "report_outputs": [
                "Day13 multi-router WireGuard validation summary JSON/HTML when generated outside the runner",
            ],
            "related_script": "mikrotik_day13_multi_router_wireguard_validation.py",
            "notes": "Disabled live runner task. Day13 summary remains report-only until its own live safety layer is implemented.",
        },
        {
            "id": DAY57_INTENT_MAPPING_TASK_ID,
            "task_id": "day57_ai_assisted_task_intent_mapping_prototype",
            "display_name": "Day57 AI-assisted Task Intent Mapping Prototype",
            "user_display_name": "Intent Mapping Prototype",
            "day": "Day57",
            "category": "ai_planning",
            "description": "Deterministic text intent classification prototype that maps user requests to allowlisted runner task proposals.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "prototype",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": False,
            "report_paths": [
                DAY57_INTENT_MAPPING_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day57 static intent mapping prototype documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Dry-run mapping only. Does not call OpenAI APIs, speech APIs, SSH, live runners, devices, config.json, or mapped task execution.",
        },
        {
            "id": DAY58_INTENT_SAFETY_REVIEW_TASK_ID,
            "task_id": "day58_intent_mapping_safety_review_confirmation_gate",
            "display_name": "Day58 Intent Mapping Safety Review and Confirmation Gate",
            "user_display_name": "Intent Safety Review",
            "day": "Day58",
            "category": "ai_planning",
            "description": "Dry-run safety classification and confirmation gate review for mapped intent proposals.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY58_INTENT_SAFETY_REVIEW_JSON.as_posix(),
                DAY58_INTENT_SAFETY_REVIEW_HTML.as_posix(),
                DAY58_INTENT_SAFETY_REVIEW_DOC.as_posix(),
                DAY58_INTENT_SAFETY_REVIEW_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day58 dry-run JSON/HTML safety review report",
                "Day58 confirmation gate design documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only confirmation gate design. Blocks live-capable and unknown intents by default and never executes mapped tasks.",
        },
        {
            "id": DAY59_INTENT_POLICY_MATRIX_TASK_ID,
            "task_id": "day59_intent_policy_matrix_reviewer_safety_explanation",
            "display_name": "Day59 Intent Policy Matrix and Reviewer Safety Explanation",
            "user_display_name": "Intent Policy Matrix",
            "day": "Day59",
            "category": "ai_planning",
            "description": "Reviewer-facing policy matrix for Day57/Day58 intent mapping and safety decisions.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY59_INTENT_POLICY_MATRIX_JSON.as_posix(),
                DAY59_INTENT_POLICY_MATRIX_HTML.as_posix(),
                DAY59_INTENT_POLICY_MATRIX_DOC.as_posix(),
                DAY59_INTENT_POLICY_MATRIX_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day59 reviewer-facing JSON/HTML intent policy matrix",
                "Day59 policy matrix and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only matrix generation. Does not call APIs, use voice, execute mapped tasks, open SSH, read config.json, or connect to devices.",
        },
        {
            "id": DAY60_INTENT_WORKFLOW_DEMO_TASK_ID,
            "task_id": "day60_ai_intent_workflow_demo_reviewer_walkthrough",
            "display_name": "Day60 AI Intent Workflow Demo Reviewer Walkthrough",
            "user_display_name": "Intent Workflow Demo",
            "day": "Day60",
            "category": "ai_planning",
            "description": "Reviewer-facing walkthrough connecting Day57 intent mapping, Day58 safety review, and Day59 policy explanation.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY60_INTENT_WORKFLOW_DEMO_JSON.as_posix(),
                DAY60_INTENT_WORKFLOW_DEMO_HTML.as_posix(),
                DAY60_INTENT_WORKFLOW_DEMO_DOC.as_posix(),
                DAY60_INTENT_WORKFLOW_DEMO_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day60 reviewer-facing JSON/HTML intent workflow demo",
                "Day60 AI intent workflow walkthrough documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only walkthrough. Does not call APIs, use voice, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, or modify network/device configuration.",
        },
        {
            "id": DAY66_OFFLINE_MOCK_RUNTIME_TASK_ID,
            "task_id": "day66_offline_mock_runtime_skeleton",
            "display_name": "Day66 Offline Mock Runtime Skeleton",
            "user_display_name": "Offline Mock Runtime",
            "day": "Day66",
            "category": "ai_planning",
            "description": "Fixed offline mock runtime skeleton report for AI Intent Reviewer architecture shape.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY66_OFFLINE_MOCK_RUNTIME_JSON.as_posix(),
                DAY66_OFFLINE_MOCK_RUNTIME_HTML.as_posix(),
                DAY66_OFFLINE_MOCK_RUNTIME_DOC.as_posix(),
                DAY66_OFFLINE_MOCK_RUNTIME_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day66 fixed JSON/HTML offline mock runtime report",
                "Day66 offline mock runtime skeleton documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Fixed mock report only. Does not call APIs, use voice, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, or modify network/device configuration.",
        },
        {
            "id": DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_TASK_ID,
            "task_id": "day67_offline_mock_runtime_contract",
            "display_name": "Day67 Offline Mock Runtime Contract & Safety Invariants",
            "user_display_name": "Offline Mock Runtime Contract",
            "day": "Day67",
            "category": "ai_planning",
            "description": "Validates the Day66 offline mock runtime output contract and safety invariants.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_JSON.as_posix(),
                DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_HTML.as_posix(),
                DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_DOC.as_posix(),
                DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day67 JSON/HTML offline mock runtime contract validation report",
                "Day67 offline mock runtime contract documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Contract validation report only. Validates in-memory mock results and does not call APIs, use voice, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, or modify network/device configuration.",
        },
        {
            "id": DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_TASK_ID,
            "task_id": "day68_offline_mock_runtime_reviewer_report_quality",
            "display_name": "Day68 Offline Mock Runtime Reviewer Report Quality & Evidence Trace Review",
            "user_display_name": "Offline Mock Runtime Review",
            "day": "Day68",
            "category": "ai_planning",
            "description": "Reviews Day66-Day67 offline mock runtime report quality, evidence traceability, and no-execution proof.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_JSON.as_posix(),
                DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_HTML.as_posix(),
                DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_DOC.as_posix(),
                DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day68 JSON/HTML reviewer quality and evidence trace report",
                "Day68 offline mock runtime reviewer quality documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Reviewer quality report only. Reviews deterministic mock data and Day67 validation evidence without APIs, voice, mapped task execution, live tests, SSH, config.json, device access, or network/device configuration changes.",
        },
        {
            "id": DAY73_MOCK_AI_DECISION_PIPELINE_TASK_ID,
            "task_id": "day73_mock_ai_decision_pipeline",
            "display_name": "Day73 Mock AI Decision Pipeline",
            "user_display_name": "Mock AI Decision Pipeline",
            "day": "Day73",
            "category": "ai_planning",
            "description": "Runs deterministic mock AI decision records after Day72 input validation.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY73_MOCK_AI_DECISION_PIPELINE_JSON.as_posix(),
                DAY73_MOCK_AI_DECISION_PIPELINE_HTML.as_posix(),
                DAY73_MOCK_AI_DECISION_PIPELINE_DOC.as_posix(),
                DAY73_MOCK_AI_DECISION_PIPELINE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day73 JSON/HTML mock AI decision pipeline report",
                "Day73 mock AI decision pipeline documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Mock-only report generation. Uses Day72 validation output but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard action surfaces, or modify network/device configuration.",
        },
        {
            "id": DAY74_DRY_RUN_PLAN_BUILDER_TASK_ID,
            "task_id": "day74_dry_run_plan_builder",
            "display_name": "Day74 Controlled Dry-run Plan Builder",
            "user_display_name": "Controlled Dry-run Plan Builder",
            "day": "Day74",
            "category": "ai_planning",
            "description": "Converts Day73 mock decision records into deterministic reviewer dry-run plan previews.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY74_DRY_RUN_PLAN_BUILDER_JSON.as_posix(),
                DAY74_DRY_RUN_PLAN_BUILDER_HTML.as_posix(),
                DAY74_DRY_RUN_PLAN_BUILDER_DOC.as_posix(),
                DAY74_DRY_RUN_PLAN_BUILDER_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day74 JSON/HTML controlled dry-run plan report",
                "Day74 controlled dry-run plan builder documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Dry-run-only report generation. Uses Day73 mock decisions but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard action surfaces, approval unlocks, or modify network/device configuration.",
        },
        {
            "id": DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_TASK_ID,
            "task_id": "day75_manual_review_approval_envelope",
            "display_name": "Day75 Manual Review Approval Envelope",
            "user_display_name": "Manual Review Approval Envelope",
            "day": "Day75",
            "category": "ai_planning",
            "description": "Wraps Day74 dry-run plans in deterministic reviewer sign-off envelope records.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_JSON.as_posix(),
                DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_HTML.as_posix(),
                DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_DOC.as_posix(),
                DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day75 JSON/HTML manual review approval envelope report",
                "Day75 manual review approval envelope documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Mock-only dry-run sign-off simulation. Uses Day74 dry-run plans but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, approval unlocks, or modify network/device configuration.",
        },
        {
            "id": DAY76_RUNTIME_AUDIT_TRAIL_TASK_ID,
            "task_id": "day76_runtime_audit_trail",
            "display_name": "Day76 Controlled Runtime Audit Trail",
            "user_display_name": "Controlled Runtime Audit Trail",
            "day": "Day76",
            "category": "ai_planning",
            "description": "Links Day73 decisions, Day74 dry-run plans, and Day75 approval envelopes into deterministic reviewer evidence packages.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY76_RUNTIME_AUDIT_TRAIL_JSON.as_posix(),
                DAY76_RUNTIME_AUDIT_TRAIL_HTML.as_posix(),
                DAY76_RUNTIME_AUDIT_TRAIL_DOC.as_posix(),
                DAY76_RUNTIME_AUDIT_TRAIL_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day76 JSON/HTML controlled runtime audit trail report",
                "Day76 controlled runtime audit trail documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Mock-only dry-run audit evidence. Uses Day73, Day74, and Day75 deterministic records but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, execution unlocks, or modify network/device configuration.",
        },
        {
            "id": DAY77_RUNTIME_SAFETY_GATE_TASK_ID,
            "task_id": "day77_runtime_safety_gate",
            "display_name": "Day77 Runtime Safety Gate",
            "user_display_name": "Runtime Safety Gate",
            "day": "Day77",
            "category": "ai_planning",
            "description": "Links Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, and Day76 audit records into deterministic locked runtime safety gate records.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY77_RUNTIME_SAFETY_GATE_JSON.as_posix(),
                DAY77_RUNTIME_SAFETY_GATE_HTML.as_posix(),
                DAY77_RUNTIME_SAFETY_GATE_DOC.as_posix(),
                DAY77_RUNTIME_SAFETY_GATE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day77 JSON/HTML runtime safety gate report",
                "Day77 runtime safety gate documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run no-execution gate. Uses Day73, Day74, Day75, and Day76 deterministic records but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY78_RUNTIME_SAFETY_CASE_TASK_ID,
            "task_id": "day78_runtime_safety_case",
            "display_name": "Day78 Controlled Runtime Safety Case",
            "user_display_name": "Controlled Runtime Safety Case",
            "day": "Day78",
            "category": "ai_planning",
            "description": "Links Day72 input validation, Day73 mock decisions, Day74 dry-run plans, Day75 approval envelopes, Day76 audit records, and Day77 locked gates into deterministic end-to-end reviewer safety case records.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY78_RUNTIME_SAFETY_CASE_JSON.as_posix(),
                DAY78_RUNTIME_SAFETY_CASE_HTML.as_posix(),
                DAY78_RUNTIME_SAFETY_CASE_DOC.as_posix(),
                DAY78_RUNTIME_SAFETY_CASE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day78 JSON/HTML controlled runtime safety case package",
                "Day78 controlled runtime safety case documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run reviewer safety case. Uses Day72, Day73, Day74, Day75, Day76, and Day77 deterministic records but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY79_READONLY_TASK_CONTRACT_TASK_ID,
            "task_id": "day79_readonly_task_contract",
            "display_name": "Day79 Controlled Read-only Task Contract & Allowlist",
            "user_display_name": "Controlled Read-only Task Contract & Allowlist",
            "day": "Day79",
            "category": "ai_planning",
            "description": "Defines deterministic future read-only task candidates, blocked write actions, destructive actions, unknown tasks, and manual classification cases without unlocking execution.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY79_READONLY_TASK_CONTRACT_JSON.as_posix(),
                DAY79_READONLY_TASK_CONTRACT_HTML.as_posix(),
                DAY79_READONLY_TASK_CONTRACT_DOC.as_posix(),
                DAY79_READONLY_TASK_CONTRACT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day79 JSON/HTML controlled read-only task contract",
                "Day79 read-only task contract documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run task contract. It classifies read-only candidates, blocked write actions, destructive actions, unknown tasks, and manual classification cases but does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY80_READONLY_EXECUTION_BROKER_TASK_ID,
            "task_id": "day80_readonly_execution_broker",
            "display_name": "Day80 Read-only Execution Broker Skeleton",
            "user_display_name": "Read-only Execution Broker Skeleton",
            "day": "Day80",
            "category": "ai_planning",
            "description": "Defines deterministic future read-only broker request handling: received, rejected, queued for review, or prepared as mock execution request data without executing anything.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY80_READONLY_EXECUTION_BROKER_JSON.as_posix(),
                DAY80_READONLY_EXECUTION_BROKER_HTML.as_posix(),
                DAY80_READONLY_EXECUTION_BROKER_DOC.as_posix(),
                DAY80_READONLY_EXECUTION_BROKER_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day80 JSON/HTML read-only execution broker skeleton",
                "Day80 read-only broker skeleton documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run broker skeleton. It reuses the Day79 read-only task contract, records broker decisions, rejects unsafe requests, queues manual-review requests, and prepares mock execution request data only; it does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, approve/execute action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY81_BROKER_REVIEW_QUEUE_TASK_ID,
            "task_id": "day81_broker_review_queue",
            "display_name": "Day81 Read-only Broker Review Queue & Decision State Report",
            "user_display_name": "Read-only Broker Review Queue & Decision State Report",
            "day": "Day81",
            "category": "ai_planning",
            "description": "Transforms Day80 broker records into deterministic reviewer queue records with review states and decision states, without executing anything.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY81_BROKER_REVIEW_QUEUE_JSON.as_posix(),
                DAY81_BROKER_REVIEW_QUEUE_HTML.as_posix(),
                DAY81_BROKER_REVIEW_QUEUE_DOC.as_posix(),
                DAY81_BROKER_REVIEW_QUEUE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day81 JSON/HTML broker review queue decision state report",
                "Day81 broker review queue documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run broker review queue. It transforms Day80 broker records into review and decision state records only; it does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY82_REVIEWER_DECISION_AUDIT_TASK_ID,
            "task_id": "day82_reviewer_decision_audit_summary",
            "display_name": "Day82 Reviewer Decision Audit Summary / Queue Evidence Export",
            "user_display_name": "Reviewer Decision Audit Summary / Queue Evidence Export",
            "day": "Day82",
            "category": "ai_planning",
            "description": "Summarizes Day81 broker review queue decisions and exports deterministic reviewer evidence without executing anything.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY82_REVIEWER_DECISION_AUDIT_JSON.as_posix(),
                DAY82_REVIEWER_DECISION_AUDIT_HTML.as_posix(),
                DAY82_REVIEWER_DECISION_AUDIT_DOC.as_posix(),
                DAY82_REVIEWER_DECISION_AUDIT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day82 JSON/HTML reviewer decision audit summary",
                "Day82 queue evidence export documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only dry-run reviewer decision audit summary. It summarizes and exports Day81 queue evidence only; it does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY83_READONLY_EXECUTOR_READINESS_GATE_TASK_ID,
            "task_id": "day83_readonly_executor_readiness_gate",
            "display_name": "Day83 Read-only Executor Readiness Gate / Controlled Runner Preflight",
            "user_display_name": "Read-only Executor Readiness Gate / Controlled Runner Preflight",
            "day": "Day83",
            "category": "ai_planning",
            "description": "Validates whether Day79-Day82 safety evidence is sufficient to mark a request as a future read-only executor candidate without executing anything.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY83_READONLY_EXECUTOR_READINESS_GATE_JSON.as_posix(),
                DAY83_READONLY_EXECUTOR_READINESS_GATE_HTML.as_posix(),
                DAY83_READONLY_EXECUTOR_READINESS_GATE_DOC.as_posix(),
                DAY83_READONLY_EXECUTOR_READINESS_GATE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day83 JSON/HTML read-only executor readiness gate",
                "Day83 controlled runner preflight documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic offline review-only readiness gate. It marks future adapter design candidacy only; it is not the read-only executor and does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, approval unlocks, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_TASK_ID,
            "task_id": "day84_readonly_executor_adapter_contract",
            "display_name": "Day84 Read-only Executor Adapter Interface Contract",
            "user_display_name": "Read-only Executor Adapter Interface Contract",
            "day": "Day84",
            "category": "ai_planning",
            "description": "Defines the future read-only executor adapter input/output contract without implementing an executor or adapter.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_JSON.as_posix(),
                DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_HTML.as_posix(),
                DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_DOC.as_posix(),
                DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day84 JSON/HTML read-only executor adapter contract",
                "Day84 contract-only adapter boundary documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic contract-only adapter boundary. It defines future request, response, capability, evidence, safety flag, and validation result shapes only; it is not an executor or adapter implementation and does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, approval unlocks, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_TASK_ID,
            "task_id": "day85_mock_adapter_evidence_binding",
            "display_name": "Day85 Mock Adapter + Evidence Binding",
            "user_display_name": "Mock Adapter + Evidence Binding",
            "day": "Day85",
            "category": "ai_planning",
            "description": "Creates deterministic mock adapter fixtures that conform to the Day84 adapter interface contract and binds every response to reviewer evidence.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_JSON.as_posix(),
                DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_HTML.as_posix(),
                DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_DOC.as_posix(),
                DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day85 JSON/HTML mock adapter evidence binding",
                "Day85 mock-only adapter fixture documentation",
                "Compatibility Matrix internal validation evidence",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic mock-only evidence-bound adapter fixture. It conforms to the Day84 contract, binds every mock response to request, adapter, contract, evidence, and reviewer decision fields, and keeps Compatibility Matrix as internal validation only; it is not a standalone topic and does not call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, approval unlocks, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY86_CONTROLLED_RUNNER_HARNESS_TASK_ID,
            "task_id": "day86_controlled_runner_harness",
            "display_name": "Day86 Controlled Runner Harness + Safety Regression",
            "user_display_name": "Controlled Runner Harness",
            "day": "Day86",
            "category": "ai_planning",
            "description": "Runs deterministic runner-level safety regression scenarios over Day85-style adapter compatibility and evidence signals.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY86_CONTROLLED_RUNNER_HARNESS_JSON.as_posix(),
                DAY86_CONTROLLED_RUNNER_HARNESS_HTML.as_posix(),
                DAY86_CONTROLLED_RUNNER_HARNESS_DOC.as_posix(),
                DAY86_CONTROLLED_RUNNER_HARNESS_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day86 JSON/HTML controlled runner harness safety regression",
                "Day86 runner-level review-only safety documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic runner-level safety regression. It consumes Day85-style adapter compatibility, blocked adapter, and evidence binding signals, but allowed_to_execute remains false, ssh_allowed remains false, live_command_allowed remains false, mapped_task_executed remains false, final recommendation remains REVIEW_ONLY, and it does not add adapter functionality, call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, approval unlocks, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_TASK_ID,
            "task_id": "day87_readonly_executor_phase_gate_review",
            "display_name": "Day87 Read-only Executor Phase Gate Review",
            "user_display_name": "Read-only Executor Phase Gate Review",
            "day": "Day87",
            "category": "ai_planning",
            "description": "Reviews Day83-Day86 readiness and safety evidence to decide whether Day88 may start a real read-only executor adapter design draft.",
            "safety_level": "dry-run",
            "execution_mode": "dry-run",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_JSON.as_posix(),
                DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_HTML.as_posix(),
                DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_DOC.as_posix(),
                DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day87 JSON/HTML read-only executor phase gate review",
                "Day87 design-only phase gate documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic phase gate review only. It aggregates Day83-Day86 evidence and may recommend DESIGN_ONLY for Day88, but execution_allowed remains false, ssh_allowed remains false, live_command_allowed remains false, write_command_allowed remains false, device_connection_allowed remains false, real_adapter_implementation_allowed remains false, and it does not design or implement a real adapter, call APIs, use AI SDKs, execute mapped tasks, run live tests, open SSH, read config.json, connect to devices, add dashboard forms, POST routes, action endpoints, approval unlocks, execution unlocks, arbitrary command execution, or modify network/device configuration.",
        },
        {
            "id": DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_TASK_ID,
            "task_id": "day88_real_readonly_executor_adapter_design",
            "display_name": "Day88 Real Read-only Executor Adapter Design Draft",
            "user_display_name": "Real Read-only Executor Adapter Design Draft",
            "day": "Day88",
            "category": "ai_planning",
            "description": "Defines the future real read-only executor adapter design draft and safety contracts without implementing transport or command execution.",
            "safety_level": "design-only",
            "execution_mode": "design-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_JSON.as_posix(),
                DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_HTML.as_posix(),
                DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_DOC.as_posix(),
                DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day88 JSON/HTML real read-only executor adapter design draft",
                "Day88 design-only adapter contract documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic design-only draft. It defines future adapter architecture, positive allowlist, evidence contract, error contract, timeout contract, and safety boundary only; execution_supported remains false, ssh_supported remains false, routeros_connection_supported remains false, live_command_supported remains false, execution_unlock_supported remains false, dashboard action surfaces remain disabled, Day87 is not redone, and no SSH, RouterOS connection, live command, subprocess, mapped task execution, approval unlock, or real adapter implementation is added.",
        },
        {
            "id": DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_TASK_ID,
            "task_id": "day89_real_adapter_safety_boundary_spec",
            "display_name": "Day89 Real Adapter Safety Boundary Spec",
            "user_display_name": "Real Adapter Safety Boundary Spec",
            "day": "Day89",
            "category": "ai_planning",
            "description": "Locks the pre-implementation safety boundary before any future real adapter implementation.",
            "safety_level": "design-only",
            "execution_mode": "design-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_JSON.as_posix(),
                DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_HTML.as_posix(),
                DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_DOC.as_posix(),
                DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day89 JSON/HTML real adapter safety boundary spec",
                "Day89 pre-implementation safety boundary documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic design-only boundary lock. It allows only spec-level classification, allowlist metadata validation, evidence-only reporting, deterministic output, and no network side effects; implementation_allowed remains false, live_device_access_allowed remains false, ssh_allowed remains false, config_change_allowed remains false, command_execution_allowed remains false, and no SSH, RouterOS connection, live command, arbitrary executor, dashboard action, file upload, shell escape, or device change is added.",
        },
        {
            "id": DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_TASK_ID,
            "task_id": "day90_real_adapter_implementation_plan",
            "display_name": "Day90 Real Adapter Implementation Plan",
            "user_display_name": "Real Adapter Implementation Plan",
            "day": "Day90",
            "category": "ai_planning",
            "description": "Decides whether repository evidence is ready for a later minimal real read-only adapter prototype.",
            "safety_level": "planning-only",
            "execution_mode": "planning-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_JSON.as_posix(),
                DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_HTML.as_posix(),
                DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_DOC.as_posix(),
                DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day90 JSON/HTML real adapter implementation-entry decision report",
                "Day90 planning-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic planning-only decision. It may produce GO, CONDITIONAL_GO, or NO_GO from repository evidence, but scope remains planning_only; adapter_implementation_allowed remains false, live_device_access_allowed remains false, ssh_allowed remains false, routeros_command_execution_allowed remains false, and no SSH client, RouterOS command runner, real device credentials, adapter connection logic, automatic apply, dashboard action, subprocess, network command, or configuration mutation is added.",
        },
        {
            "id": DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_TASK_ID,
            "task_id": "day91_real_adapter_safety_scaffold",
            "display_name": "Day91 Real Adapter Safety Scaffold",
            "user_display_name": "Real Adapter Safety Scaffold",
            "day": "Day91",
            "category": "ai_planning",
            "description": "Creates scaffold-only evidence after Day90 CONDITIONAL_GO that dangerous live/device-modifying actions are structurally denied before any read-only execution path exists.",
            "safety_level": "scaffold-only",
            "execution_mode": "scaffold-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_JSON.as_posix(),
                DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_HTML.as_posix(),
                DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_DOC.as_posix(),
                DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day91 JSON/HTML real adapter safety scaffold",
                "Day91 scaffold-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic scaffold-only evidence. Day90 was CONDITIONAL_GO only; Day91 denies dangerous actions, marks read-only candidates future-only, keeps live_read_allowed false, write_allowed false, raw_command_allowed false, credential_required false, transport_required false, real_device_contact_allowed false, and adds no SSH, RouterOS API, socket, subprocess device operation, credential use, real adapter, executable guard, dashboard action, command input, or live-read path.",
        },
        {
            "id": DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_TASK_ID,
            "task_id": "day92_real_adapter_executable_guards",
            "display_name": "Day92 Real Adapter Executable Guards",
            "user_display_name": "Real Adapter Executable Guards",
            "day": "Day92",
            "category": "ai_planning",
            "description": "Converts the Day91 static scaffold into executable guards that allow safe simulated read-only requests and reject dangerous, sensitive, ambiguous, or unknown requests before any executor can be reached.",
            "safety_level": "offline-deterministic-guard",
            "execution_mode": "guard-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_JSON.as_posix(),
                DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_HTML.as_posix(),
                DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_DOC.as_posix(),
                DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day92 JSON/HTML executable guard evidence",
                "Day92 guard-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic executable guard layer only. Safe read-only requests are simulated and offline; dangerous, sensitive, ambiguous, or unknown requests fail closed with reason_code, matched_rule_name, blocked_action_category, and evidence. rejected_adapter_invocations remains 0, adapter_implementation_added remains false, and Day92 adds no real adapter, SSH, RouterOS API, socket, subprocess device operation, credential use, dashboard action, command input, live-read path, or device contact.",
        },
        {
            "id": DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_TASK_ID,
            "task_id": "day93_guarded_fake_adapter_contract",
            "display_name": "Day93 Guarded Fake Adapter Contract",
            "user_display_name": "Guarded Fake Adapter Contract",
            "day": "Day93",
            "category": "ai_planning",
            "description": "Audits guard-first ordering for a fake read-only adapter boundary: allowed scenarios invoke only the fake adapter, while rejected scenarios never enter the adapter boundary.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "guarded-fake-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_JSON.as_posix(),
                DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_HTML.as_posix(),
                DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_DOC.as_posix(),
                DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day93 JSON/HTML guarded fake adapter boundary evidence",
                "Day93 fake-adapter-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic fake adapter boundary audit only. Guard evaluation happens before adapter invocation; rejected scenarios keep adapter_invocation_attempted false, adapter_boundary_entered false, and fake_adapter_invoked false; allowed scenarios use adapter_type fake only. real_adapter_invocations remains 0, ssh_allowed remains false, device_access_allowed remains false, live_command_allowed remains false, no config.json is read, and Day93 adds no real adapter, SSH, RouterOS API, socket, subprocess device operation, dashboard action, command input, execution unlock, or device contact.",
        },
        {
            "id": DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_TASK_ID,
            "task_id": "day94_adapter_boundary_regression_matrix",
            "display_name": "Day94 Adapter Boundary Regression Matrix",
            "user_display_name": "Adapter Boundary Regression Matrix",
            "day": "Day94",
            "category": "ai_planning",
            "description": "Expands the Day93 fake adapter boundary proof into a deterministic regression matrix covering allowed, rejected, fake-target, real-target-blocked, live-capable, mutation, and unknown intent classes.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "guarded-fake-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_JSON.as_posix(),
                DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_HTML.as_posix(),
                DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_DOC.as_posix(),
                DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day94 JSON/HTML adapter boundary regression matrix evidence",
                "Day94 fake-adapter-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic matrix evidence only. Rejected rows never invoke the fake adapter; allowed fake-adapter rows may invoke only fake boundary evidence. real_adapter_invocations remains 0, live_execution_invocations remains 0, adapter_invoked_for_rejected remains 0, no config.json is read, and Day94 adds no real adapter, SSH, RouterOS API, socket, subprocess device operation, dashboard action, command input, execution unlock, or device contact.",
        },
        {
            "id": DAY95_ADAPTER_RESULT_NORMALIZATION_TASK_ID,
            "task_id": "day95_adapter_result_normalization",
            "display_name": "Day95 Adapter Result Normalization",
            "user_display_name": "Adapter Result Normalization",
            "day": "Day95",
            "category": "ai_planning",
            "description": "Normalizes deterministic fake adapter boundary results into a fixed parser-ready schema while rejected scenarios produce no adapter result.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "guarded-fake-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY95_ADAPTER_RESULT_NORMALIZATION_JSON.as_posix(),
                DAY95_ADAPTER_RESULT_NORMALIZATION_HTML.as_posix(),
                DAY95_ADAPTER_RESULT_NORMALIZATION_DOC.as_posix(),
                DAY95_ADAPTER_RESULT_NORMALIZATION_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day95 JSON/HTML normalized fake adapter result evidence",
                "Day95 fake-adapter-only AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Deterministic fake result normalization only. Allowed scenarios produce schema_version day95.adapter_result.v1 normalized_fake_adapter_result records from the deterministic fake boundary; rejected scenarios keep adapter_result None. real_adapter_result_count remains 0, live_execution_result_count remains 0, result_status_source remains deterministic_fake_boundary, and Day95 adds no real adapter, SSH, RouterOS API, socket, subprocess device operation, dashboard action, POST route, command input, execution unlock, or device contact.",
        },
        {
            "id": DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_TASK_ID,
            "task_id": "day96_readonly_output_parser_prototype",
            "display_name": "Day96 Read-only Output Parser Prototype",
            "user_display_name": "Read-only Output Parser Prototype",
            "day": "Day96",
            "category": "ai_planning",
            "description": "Parses only Day95 normalized fake adapter simulated output into structured parser records with explicit no-live safety metadata.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_JSON.as_posix(),
                DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_HTML.as_posix(),
                DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_DOC.as_posix(),
                DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day96 JSON/HTML parser-only fake output evidence",
                "Day96 parser boundary AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Parser-only prototype. Input is Day95 normalized fake adapter simulated_output only; unsupported or malformed inputs return REVIEW_NEEDED or UNSUPPORTED. live_read_enabled remains false, ssh_enabled remains false, routeros_enabled remains false, device_access_enabled remains false, adapter fallback remains false, runner live path remains false, no config.json is read, and Day96 adds no RouterOS connection, SSH, live command, real device command parser, dashboard action, POST route, command input, execution unlock, or device contact.",
        },
        {
            "id": DAY97_PARSER_EVIDENCE_QUALITY_TASK_ID,
            "task_id": "day97_parser_evidence_quality",
            "display_name": "Day97 Parser Evidence Quality",
            "user_display_name": "Parser Evidence Quality",
            "day": "Day97",
            "category": "ai_planning",
            "description": "Hardens Day96 parser evidence handling for unsupported, incomplete, malformed, ambiguous, empty, and degraded static fake output cases.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY97_PARSER_EVIDENCE_QUALITY_JSON.as_posix(),
                DAY97_PARSER_EVIDENCE_QUALITY_HTML.as_posix(),
                DAY97_PARSER_EVIDENCE_QUALITY_DOC.as_posix(),
                DAY97_PARSER_EVIDENCE_QUALITY_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day97 JSON/HTML parser evidence quality report",
                "Day97 parser unsupported-output hardening AI reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Parser-only static fake cases. Unsupported output is classified as UNSUPPORTED_OUTPUT, INCOMPLETE_OUTPUT, MALFORMED_INPUT, EMPTY_OUTPUT, or AMBIGUOUS_OUTPUT, not an execution-failure result. live_read_allowed remains false, ssh_allowed remains false, write_allowed remains false, command_execution_allowed remains false, raw_command_allowed remains false, device_contact_allowed remains false, approval_unlock_supported remains false, mapped_task_execution_allowed remains false, no config.json is read, and Day97 adds no RouterOS execution, SSH, live-read, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, or device contact.",
        },
        {
            "id": DAY98_PARSER_CLASSIFICATION_MATRIX_TASK_ID,
            "task_id": "day98_parser_classification_matrix",
            "display_name": "Day98 Parser Classification Matrix",
            "user_display_name": "Parser Classification Matrix",
            "day": "Day98",
            "category": "ai_planning",
            "description": "Builds a reviewer-facing traceability matrix across Day96 parser prototype cases and Day97 unsupported-output hardening cases.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY98_PARSER_CLASSIFICATION_MATRIX_JSON.as_posix(),
                DAY98_PARSER_CLASSIFICATION_MATRIX_HTML.as_posix(),
                DAY98_PARSER_CLASSIFICATION_MATRIX_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day98 JSON/HTML parser classification traceability matrix",
                "Day98 reviewer traceability documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only static Day96/Day97 sample matrix. Every row has parser_classification, parsed_fields or unsupported_reason, reviewer_action, safety_invariant, evidence_required, and trace_status. executable_allowed remains false, live_read_allowed remains false, ssh_allowed remains false, routeros_execution_allowed remains false, command_execution_allowed remains false, device_contact_allowed remains false, approval_unlock_supported remains false, no config.json is read, and Day98 adds no RouterOS execution, SSH, live-read, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, or external service call.",
        },
        {
            "id": DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_TASK_ID,
            "task_id": "day99_parser_evidence_coverage_audit",
            "display_name": "Day99 Parser Evidence Coverage / Sample Gap Audit",
            "user_display_name": "Parser Evidence Coverage / Sample Gap Audit",
            "day": "Day99",
            "category": "ai_planning",
            "description": "Audits Day96-Day98 parser sample coverage and records non-blocking sample gaps before the Day100 parser phase-gate readiness decision.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_JSON.as_posix(),
                DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_HTML.as_posix(),
                DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_DOC.as_posix(),
                DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day99 JSON/HTML parser evidence coverage and sample gap audit",
                "Day99 coverage audit reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day96-Day98 parser evidence coverage audit. UNDER_COVERED categories are allowed and become Day100 review inputs, not Day99 failures. execution_allowed remains false, adapter_path_allowed remains false, broker_path_allowed remains false, ssh_allowed remains false, live_device_path_allowed remains false, routeros_execution_allowed remains false, command_execution_allowed remains false, no config.json is read, and Day99 adds no parser capability, adapter execution, broker execution, SSH, live device path, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, or external service call.",
        },
        {
            "id": DAY100_PARSER_PHASE_GATE_REVIEW_TASK_ID,
            "task_id": "day100_parser_phase_gate_review",
            "display_name": "Day100 Parser Phase Gate Review / Readiness Decision",
            "user_display_name": "Parser Phase Gate Review / Readiness Decision",
            "day": "Day100",
            "category": "ai_planning",
            "description": "Grades Day96-Day99 parser evidence into ADVANCE_READY, REVIEW_ONLY, UNDER_COVERED, and BLOCKED readiness decisions without opening broker, executor, adapter, SSH, or live-access paths.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY100_PARSER_PHASE_GATE_REVIEW_JSON.as_posix(),
                DAY100_PARSER_PHASE_GATE_REVIEW_HTML.as_posix(),
                DAY100_PARSER_PHASE_GATE_REVIEW_DOC.as_posix(),
                DAY100_PARSER_PHASE_GATE_REVIEW_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day100 JSON/HTML parser phase-gate readiness decision",
                "Day100 phase-gate reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day96-Day99 parser phase-gate review. It formally classifies parser evidence as ADVANCE_READY, REVIEW_ONLY, UNDER_COVERED, or BLOCKED. Parser output is review data only, not execution authorization. broker_boundary_allowed remains false, execution_allowed remains false, adapter_invocation_allowed remains false, executor_invocation_allowed remains false, ssh_allowed remains false, live_access_allowed remains false, no config.json is read, and Day100 opens no broker, executor, adapter invocation, SSH, live access, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, or external service call.",
        },
        {
            "id": DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_TASK_ID,
            "task_id": "day101_parser_evidence_closure_plan",
            "display_name": "Day101 Parser Evidence Closure Plan",
            "user_display_name": "Parser Evidence Closure Plan",
            "day": "Day101",
            "category": "ai_planning",
            "description": "Converts Day100 UNDER_COVERED and REVIEW_ONLY parser findings into a Day102-Day105 evidence closure roadmap without approving broker handoff or parser advancement.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_JSON.as_posix(),
                DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_HTML.as_posix(),
                DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_DOC.as_posix(),
                DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day101 JSON/HTML parser evidence closure plan",
                "Day101 closure plan reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day100 parser evidence closure plan. It lists UNDER_COVERED and REVIEW_ONLY categories, closure items, and the Day102-Day105 sequence. parser_ready_for_broker remains false, broker_handoff_allowed remains false, execution_allowed remains false, live_device_access_allowed remains false, ssh_allowed remains false, openai_api_allowed remains false, and phase_gate_rerun_required remains true. Day101 opens no broker, executor, adapter invocation, SSH, live access, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, or external service call.",
        },
        {
            "id": DAY102_PARSER_FIXTURE_EXPANSION_TASK_ID,
            "task_id": "day102_parser_fixture_expansion",
            "display_name": "Day102 Parser Fixture Expansion",
            "user_display_name": "Parser Fixture Expansion",
            "day": "Day102",
            "category": "ai_planning",
            "description": "Adds static parser fixture evidence for positive, negative, malformed, ambiguous, and unsafe inputs without adding parser capability or opening broker, adapter, SSH, or live-device paths.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY102_PARSER_FIXTURE_EXPANSION_JSON.as_posix(),
                DAY102_PARSER_FIXTURE_EXPANSION_HTML.as_posix(),
                DAY102_PARSER_FIXTURE_EXPANSION_DOC.as_posix(),
                DAY102_PARSER_FIXTURE_EXPANSION_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day102 JSON/HTML parser fixture expansion evidence",
                "Day102 fixture expansion reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day102 parser fixture expansion. It adds positive, negative, malformed, ambiguous, and unsafe static fixtures as evidence only. parser_capability_added remains false, parser_ready_for_broker remains false, broker_handoff_allowed remains false, execution_allowed remains false, live_device_access_allowed remains false, ssh_allowed remains false, config_change_allowed remains false, and adapter_invocation_allowed remains false. Day102 opens no broker, executor, adapter invocation, SSH, live access, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, external service call, or device contact.",
        },
        {
            "id": DAY103_PARSER_EVIDENCE_MATRIX_TASK_ID,
            "task_id": "day103_parser_evidence_matrix_gap_traceability",
            "display_name": "Day103 Parser Evidence Matrix / Gap Traceability",
            "user_display_name": "Parser Evidence Matrix / Gap Traceability",
            "day": "Day103",
            "category": "ai_planning",
            "description": "Integrates Day96-Day102 parser evidence into a static reviewer-facing gap traceability matrix without adding parser capability or opening broker, adapter, SSH, or live-device paths.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY103_PARSER_EVIDENCE_MATRIX_JSON.as_posix(),
                DAY103_PARSER_EVIDENCE_MATRIX_HTML.as_posix(),
                DAY103_PARSER_EVIDENCE_MATRIX_DOC.as_posix(),
                DAY103_PARSER_EVIDENCE_MATRIX_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day103 JSON/HTML parser evidence matrix and gap traceability report",
                "Day103 matrix reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day103 parser evidence matrix. It links Day96-Day102 gap, fixture/evidence, expected decision, actual result, report paths, and safety boundary in one traceability table. parser_capability_added remains false, broker_handoff_allowed remains false, execution_allowed remains false, adapter_invocation_allowed remains false, live_access_allowed remains false, and ssh_allowed remains false. Day103 opens no broker, executor, adapter invocation, SSH, live access, dashboard action, POST route, command input, execution unlock, OpenAI API, voice runtime, external service call, or device contact.",
        },
        {
            "id": DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_TASK_ID,
            "task_id": "day104_parser_reviewer_acceptance_gate",
            "display_name": "Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review",
            "user_display_name": "Parser Reviewer Acceptance Gate / Matrix Decision Review",
            "day": "Day104",
            "category": "ai_planning",
            "description": "Converts Day103 matrix trace states into a reviewer acceptance decision without adding parser capability or opening broker, adapter, SSH, live-device, or execution paths.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_JSON.as_posix(),
                DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_HTML.as_posix(),
                DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_DOC.as_posix(),
                DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day104 JSON/HTML parser reviewer acceptance gate report",
                "Day104 reviewer gate and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "Report-only Day104 reviewer gate. It maps Day103 TRACE_COMPLETE, REVIEW_REQUIRED, KNOWN_GAP, and BLOCKED_BY_SAFETY_BOUNDARY states to acceptance decisions. Safety boundary blocks dominate acceptance, known gaps prevent next-stage readiness, REVIEW_REQUIRED prevents full acceptance, and all parser capability, execution, broker handoff, adapter, SSH, live access, command, config change, OpenAI API, and voice runtime flags remain false.",
        },
        {
            "id": DAY105_PARSER_ACCEPTANCE_CLOSURE_TASK_ID,
            "task_id": "day105_parser_acceptance_closure",
            "display_name": "Day105 Parser Acceptance Closure / Safety-Blocked Exit Summary",
            "user_display_name": "Parser Acceptance Closure / Safety-Blocked Exit Summary",
            "day": "Day105",
            "category": "ai_planning",
            "description": "Packages Day96-Day104 parser evidence into a reviewer-facing closure summary while keeping live execution and next-phase entry safety-blocked.",
            "safety_level": "fake-adapter-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY105_PARSER_ACCEPTANCE_CLOSURE_JSON.as_posix(),
                DAY105_PARSER_ACCEPTANCE_CLOSURE_HTML.as_posix(),
                DAY105_PARSER_ACCEPTANCE_CLOSURE_DOC.as_posix(),
                DAY105_PARSER_ACCEPTANCE_CLOSURE_REVIEWER_DOC.as_posix(),
                DAY105_PARSER_ACCEPTANCE_CLOSURE_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day105 JSON/HTML parser acceptance closure package",
                "Day105 reviewer and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "SUMMARY_ONLY Day105 closure package for Day96-Day104. final_recommendation remains SAFETY_BLOCKED_REVIEW_ONLY; next_phase_allowed, execution_allowed, live_device_access_allowed, ssh_allowed, config_change_allowed, mapped_task_execution_allowed, openai_api_allowed, voice_input_allowed, and parser_capability_added remain false. A separate branch and separate phase gate are required before any future live-capable discussion.",
        },
        {
            "id": DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_TASK_ID,
            "task_id": "day106_codex_agents_instruction_compliance_audit",
            "display_name": "Day106 Codex AGENTS.md Instruction Compliance Audit",
            "user_display_name": "Codex AGENTS.md Instruction Compliance Audit",
            "day": "Day106",
            "category": "ai_planning",
            "description": "Audits the repository-level AGENTS.md as a Codex instruction contract while preserving report-only safety boundaries.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_JSON.as_posix(),
                DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_HTML.as_posix(),
                DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_DOC.as_posix(),
                DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day106 JSON/HTML Codex AGENTS.md instruction compliance audit",
                "Day106 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day106 AGENTS.md governance audit. Codex may read AGENTS.md, audit AGENTS.md, and report findings with proposed wording, but codex_must_not_modify_agents_md, codex_must_not_stage_agents_md, and codex_must_not_commit_agents_md remain true. live_execution_allowed, ssh_allowed, device_connection_allowed, config_mutation_allowed, openai_api_allowed, voice_runtime_allowed, push_allowed_without_user_approval, merge_allowed_without_user_approval, and tag_allowed_without_user_approval remain false. The task reads local AGENTS.md only and does not invoke adapters, brokers, subprocess execution paths, devices, SSH, APIs, voice runtime, push, merge, tag, or deployment.",
        },
        {
            "id": DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_TASK_ID,
            "task_id": "day107_parser_reviewer_evidence_contract",
            "display_name": "Day107 Parser Reviewer Evidence Contract Consolidation",
            "user_display_name": "Parser Reviewer Evidence Contract Consolidation",
            "day": "Day107",
            "category": "ai_planning",
            "description": "Consolidates Day96-Day105 parser evidence into one deterministic reviewer evidence contract while keeping all live-capable boundaries locked.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_JSON.as_posix(),
                DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_HTML.as_posix(),
                DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_DOC.as_posix(),
                DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day107 JSON/HTML parser reviewer evidence contract",
                "Day107 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day107 parser reviewer evidence contract for Day96-Day105. accepted_for_review_only_continuation can pass only when every required evidence stage is represented and safety boundaries remain locked. accepted_for_live_execution, live_execution_allowed, ssh_allowed, device_connection_allowed, config_mutation_allowed, openai_api_allowed, voice_runtime_allowed, adapter_invocation_allowed, and rejected_intent_execution_allowed remain false. No adapter, broker, runner execution path, live device, SSH, external AI runtime, voice runtime, or configuration mutation is introduced.",
        },
        {
            "id": DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_TASK_ID,
            "task_id": "day108_parser_contract_consumer_handoff",
            "display_name": "Day108 Parser Contract Consumer / Reviewer Decision Handoff",
            "user_display_name": "Parser Contract Consumer / Reviewer Decision Handoff",
            "day": "Day108",
            "category": "ai_planning",
            "description": "Consumes Day107-style reviewer evidence contract records and emits deterministic reviewer decision handoff records while blocking unsafe or unsupported consumer transitions.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_JSON.as_posix(),
                DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_HTML.as_posix(),
                DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_DOC.as_posix(),
                DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_ROADMAP.as_posix(),
            ],
            "report_outputs": [
                "Day108 JSON/HTML parser contract consumer handoff",
                "Day108 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day108 consumer handoff for the Day107 source contract shape. Handoff records include source_contract, source_contract_version, consumer_schema_version, reviewer_decision, evidence_status, safety_flags, and next_stage_recommendation. live_execution_allowed, ssh_allowed, device_connection_allowed, command_execution_allowed, write_or_config_change_allowed, approval_unlock_supported, mapped_task_execution_allowed, openai_api_used, and voice_input_used remain false. Unsafe flags block handoff and no live device, SSH, adapter, broker, runner, OpenAI API, voice input, approval unlock, mapped task execution, or write/config change path is introduced.",
        },
        {
            "id": DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_TASK_ID,
            "task_id": "day109_parser_consumer_handoff_readiness_matrix",
            "display_name": "Day109 Parser Consumer Handoff Readiness Matrix",
            "user_display_name": "Parser Consumer Handoff Readiness Matrix",
            "day": "Day109",
            "category": "ai_planning",
            "description": "Converts Day108 handoff records into deterministic reviewer-facing READY, NEEDS_CLARIFICATION, and BLOCKED readiness rows while preserving unsafe and execution-capable flags as blocking conditions.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_JSON.as_posix(),
                DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_HTML.as_posix(),
                DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day109 JSON/HTML parser consumer handoff readiness matrix",
                "Day109 AI intent documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day109 readiness matrix for Day108 consumer handoff records. Rows include consumer_name, source_day, handoff_status, readiness_status, blocking_reasons, clarification_items, required_consumer_actions, unsafe/live/SSH/write/command/mapped-task flags, and evidence_refs. REVIEW_ONLY, NO_LIVE_EXECUTION, NO_SSH, NO_WRITE, no command execution, no mapped task execution, no OpenAI API, and no external API boundaries remain locked.",
        },
        {
            "id": DAY110_PARSER_CONSUMER_FINAL_GATE_TASK_ID,
            "task_id": "day110_parser_consumer_final_gate",
            "display_name": "Day110 Parser Consumer Final Gate / Reviewer Decision Summary",
            "user_display_name": "Parser Consumer Final Gate / Reviewer Decision Summary",
            "day": "Day110",
            "category": "ai_planning",
            "description": "Summarizes Day109 parser consumer readiness into a final reviewer decision gate and displays whether AGENTS.md was read before Day110 work.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY110_PARSER_CONSUMER_FINAL_GATE_JSON.as_posix(),
                DAY110_PARSER_CONSUMER_FINAL_GATE_HTML.as_posix(),
                DAY110_PARSER_CONSUMER_FINAL_GATE_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day110 JSON/HTML parser consumer final gate",
                "Day110 AI intent documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day110 final gate for Day109 parser consumer readiness. Includes agents_md_pre_read_result and agents_md_read_before_day110_work reviewer evidence. Blocked or clarification rows keep next_phase_allowed=false. REVIEW_ONLY, NO_LIVE_EXECUTION, NO_SSH, NO_WRITE, no command execution, no mapped task execution, no adapter, no broker, no runner execution, no OpenAI API, and no external API boundaries remain locked.",
        },
        {
            "id": DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_TASK_ID,
            "task_id": "day111_parser_consumer_release_package",
            "display_name": "Day111 Parser Consumer Evidence Freeze / Release Package",
            "user_display_name": "Parser Consumer Evidence Freeze / Release Package",
            "day": "Day111",
            "category": "ai_planning",
            "description": "Freezes Day107-Day110 parser consumer reviewer evidence into a deterministic release package while preserving the Day109 blocked condition and Day110 final-gate lock.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_JSON.as_posix(),
                DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_HTML.as_posix(),
                DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_DOC.as_posix(),
                DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_REVIEWER_DOC.as_posix(),
                DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day111 JSON/HTML parser consumer release package",
                "Day111 AI intent and reviewer documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day111 release package freezes Day107-Day110 evidence. Includes agents_md_read_before_day111_work, agents_md_pre_read_result, agents_md_modified=false, source_day_count=4, frozen_evidence_count=4, blocked_condition_preserved=true, next_phase_allowed=false. RELEASE_PACKAGE_READY_REVIEW_ONLY / FROZEN; no SSH, no live device access, no network command execution, no config mutation, no mapped task execution, no execution broker unlock, no approval unlock, no OpenAI API, no voice runtime, no cloud runtime, and no next-phase execution.",
        },
        {
            "id": DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_TASK_ID,
            "task_id": "day112_parser_consumer_release_review_intake",
            "display_name": "Day112 Parser Consumer Release Review Intake / Reviewer Triage Checklist",
            "user_display_name": "Parser Consumer Release Review Intake / Reviewer Triage Checklist",
            "day": "Day112",
            "category": "ai_planning",
            "description": "Receives the Day111 frozen parser consumer release package into reviewer intake without enabling approval unlock, execution readiness, or next phase advancement.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_JSON.as_posix(),
                DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_HTML.as_posix(),
                DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_DOC.as_posix(),
                DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_REVIEWER_DOC.as_posix(),
                DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day112 JSON/HTML parser consumer reviewer intake checklist",
                "Day112 AI intent and reviewer documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day112 intake consumes the Day111 frozen package for reviewer intake only. Includes agents_md_read_before_day112_work, reviewer_status=REVIEW_INTAKE_READY_NON_EXECUTABLE, intake_status=ACCEPTED_FOR_REVIEW, triage_status=BLOCKED_CONDITIONS_PRESERVED, blocked_condition_status=PRESERVED, checklist_pass_count=10, checklist_total_count=10, allowed_reviewer_route_count=4, forbidden_reviewer_route_count=1, approve_next_phase_execution_supported=false, approval_unlock_allowed=false, execution_readiness_allowed=false, next_phase_allowed=false. No SSH, live device access, network command execution, config mutation, mapped task execution, execution broker unlock, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, approval unlock, or next-phase execution.",
        },
        {
            "id": DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_TASK_ID,
            "task_id": "day113_parser_consumer_reviewer_triage_decision_log",
            "display_name": "Day113 Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit",
            "user_display_name": "Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit",
            "day": "Day113",
            "category": "ai_planning",
            "description": "Records the reviewer triage outcome for the Day112 intake package without enabling approval unlock, execution readiness, or next phase advancement.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_JSON.as_posix(),
                DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_HTML.as_posix(),
                DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_DOC.as_posix(),
                DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_REVIEWER_DOC.as_posix(),
                DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day113 JSON/HTML parser consumer reviewer triage outcome log",
                "Day113 AI intent and reviewer documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day113 records the reviewer triage outcome for the Day112 intake package. Includes agents_md_read_before_day113_work, reviewer_status=TRIAGE_OUTCOME_RECORDED_NON_EXECUTABLE, outcome_audit_status=INTAKE_OUTCOME_AUDITED, triage_outcome_status=HOLD_LOGGED_BLOCKED_CONDITIONS_PRESERVED, selected_reviewer_outcome=HOLD_FOR_BLOCKED_RECORDS, outcome_log_entry_count=5, audit_check_pass_count=9, audit_check_total_count=9, failed_check_count=0, approve_next_phase_execution_supported=false, approval_unlock_allowed=false, execution_readiness_allowed=false, next_phase_allowed=false. No SSH, live device access, network command execution, config mutation, mapped task execution, execution broker unlock, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, approval unlock, or next-phase execution.",
        },
        {
            "id": DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_TASK_ID,
            "task_id": "day114_parser_consumer_reviewer_triage_evidence_traceability",
            "display_name": "Day114 Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit",
            "user_display_name": "Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit",
            "day": "Day114",
            "category": "ai_planning",
            "description": "Links Day112 intake records, Day113 triage outcomes, blocked records, and final recommendation into a non-executable traceability audit.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_JSON.as_posix(),
                DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_HTML.as_posix(),
                DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_DOC.as_posix(),
                DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_REVIEWER_DOC.as_posix(),
                DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day114 JSON/HTML parser consumer reviewer traceability audit",
                "Day114 AI intent and reviewer documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "AUDIT_ONLY REPORT_ONLY Day114 links Day112 intake records to Day113 triage outcome records. Includes agents_md_read_before_day114_work, reviewer_status=TRACEABILITY_AUDITED_NON_EXECUTABLE, source_day112_intake_linked=true, source_day113_triage_linked=true, blocked_records_preserved=true, missing_trace_count=0, downgrade_detected_count=0, execution_readiness_inferred_count=0, next_phase_allowed_count=0, unsafe_flag_count=0, NO_EXECUTION_READINESS_INFERRED, NO_NEXT_PHASE_UNLOCK, BLOCKED_RECORDS_PRESERVED. No SSH, live device access, network command execution, config mutation, mapped task execution, execution broker unlock, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, approval unlock, or next-phase execution.",
        },
        {
            "id": DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_TASK_ID,
            "task_id": "day115_parser_consumer_reviewer_triage_closure_summary",
            "display_name": "Day115 Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit",
            "user_display_name": "Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit",
            "day": "Day115",
            "category": "ai_planning",
            "description": "Closes the Day112-Day114 reviewer triage chain while explicitly preserving DO_NOT_ADVANCE and all execution locks.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_JSON.as_posix(),
                DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_HTML.as_posix(),
                DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_DOC.as_posix(),
                DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day115 JSON/HTML parser consumer reviewer triage closure summary",
                "Day115 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day115 closes the Day112-Day114 reviewer triage chain without advancing parser consumer work. Includes agents_md_read_before_day115_work, reviewer_status=TRIAGE_CLOSURE_AUDITED_NON_ADVANCING, closure_status=CLOSED_WITH_BLOCKED_RECORDS_PRESERVED, final_recommendation=DO_NOT_ADVANCE, next_phase_allowed=false, execution_readiness_inferred=false, blocked_records_preserved=true, blocked_records_not_downgraded=true, TRIAGE_CHAIN_CLOSED_NON_ADVANCING, NO_EXECUTION_READINESS_INFERRED, NO_NEXT_PHASE_UNLOCK, NO_BROKER_HANDOFF, NO_RUNNER_EXECUTION, NO_ADAPTER_ACCESS, NO_SSH_ACCESS, NO_LIVE_ACCESS, NO_COMMAND_EXECUTION, NO_MAPPED_TASK_EXECUTION, NO_APPROVAL_UNLOCK. No readiness, broker, runner, adapter, SSH, live access, command execution, mapped task execution, approval unlock, parser capability change, or next-phase advancement.",
        },
        {
            "id": DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_TASK_ID,
            "task_id": "day116_reviewer_deferred_action_register",
            "display_name": "Day116 Reviewer Deferred Action Register / Blocked Follow-up Queue",
            "user_display_name": "Reviewer Deferred Action Register / Blocked Follow-up Queue",
            "day": "Day116",
            "category": "ai_planning",
            "description": "Records a reviewer-only deferred follow-up queue for blocked, held, and do-not-advance items from Day112-Day115.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_JSON.as_posix(),
                DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_HTML.as_posix(),
                DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_DOC.as_posix(),
                DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day116 JSON/HTML reviewer deferred action register",
                "Day116 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REVIEWER_ONLY REPORT_ONLY Day116 records a deferred follow-up queue only. Includes agents_md_read_before_day116_work, status=DEFERRED_ACTION_REGISTER_RECORDED, follow_up_queue_status=FOLLOW_UP_QUEUE_RECORDED, day_range=Day112-Day115, register_scope=REVIEWER_DEFERRED_ACTIONS_ONLY, execution_allowed=false, broker_allowed=false, runner_allowed=false, adapter_allowed=false, ssh_allowed=false, live_access_allowed=false, readiness_generated=false, next_stage_allowed=false, readiness_generated_count=0, execution_unlock_count=0, broker_handoff_count=0, runner_handoff_count=0, adapter_handoff_count=0, ssh_access_count=0, live_access_count=0. No item is resolved, approved, released, advanced, handed off, or executed.",
        },
        {
            "id": DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_TASK_ID,
            "task_id": "day117_deferred_action_traceability_review",
            "display_name": "Day117 Deferred Action Traceability Review / Follow-up Ownership Matrix",
            "user_display_name": "Deferred Action Traceability Review / Follow-up Ownership Matrix",
            "day": "Day117",
            "category": "ai_planning",
            "description": "Adds reviewer-only owner, follow-up type, blocking reason, review sequence, and evidence requirements to the seven Day116 deferred items.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_JSON.as_posix(),
                DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_HTML.as_posix(),
                DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_DOC.as_posix(),
                DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day117 JSON/HTML deferred action traceability review matrix",
                "Day117 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REVIEWER_ONLY REPORT_ONLY NON_ADVANCING Day117 follows the seven Day116 deferred items only. Includes status=DEFERRED_ACTION_TRACEABILITY_REVIEW_READY, final_recommendation=REVIEW_ONLY_NON_ADVANCING, ownership_matrix_status=RECORDED, traceability_status=TRACEABLE_TO_DAY116, total_deferred_items_reviewed=7, review_sequence_count=7, unsafe_flag_count=0, execution_allowed=false, broker_allowed=false, runner_allowed=false, adapter_allowed=false, ssh_allowed=false, live_access_allowed=false, readiness_generated=false, next_stage_allowed=false. No item is resolved, approved, released, advanced, handed off, or executed.",
        },
        {
            "id": DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_TASK_ID,
            "task_id": "day118_deferred_action_review_sequence_runbook",
            "display_name": "Day118 Deferred Action Review Sequence Runbook / Evidence Intake Checklist",
            "user_display_name": "Deferred Action Review Sequence Runbook / Evidence Intake Checklist",
            "day": "Day118",
            "category": "ai_planning",
            "description": "Converts the seven Day117 deferred ownership matrix records into reviewer evidence intake questions and a sequence runbook.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_JSON.as_posix(),
                DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_HTML.as_posix(),
                DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_DOC.as_posix(),
                DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day118 JSON/HTML deferred action evidence intake checklist",
                "Day118 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REVIEW_ONLY REPORT_ONLY NON_ADVANCING Day118 follows the seven Day117 deferred ownership matrix records only. Includes reviewer_status=INTAKE_CHECKLIST_READY_REVIEW_ONLY, final_recommendation=REVIEW_ONLY_NON_ADVANCING, source_record_count=7, checklist_record_count=7, review_sequence=1..7, execution_unlock_supported=false, next_stage_allowed=false, readiness_transition_allowed=false, broker_allowed=false, runner_allowed=false, adapter_allowed=false, ssh_allowed=false, live_access_allowed=false, mapped_task_execution_allowed=false, openai_api_allowed=false, voice_runtime_allowed=false, device_access_allowed=false. No item is made READY, advanced, approved, released, handed off, or executed.",
        },
        {
            "id": DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_TASK_ID,
            "task_id": "day119_reviewer_evidence_intake_outcome_ledger",
            "display_name": "Day119 Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log",
            "user_display_name": "Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log",
            "day": "Day119",
            "category": "ai_planning",
            "description": "Records intake outcomes and remaining gaps for each Day118 expected evidence item without acceptance, sign-off, safety release, or execution unlock.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_JSON.as_posix(),
                DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_HTML.as_posix(),
                DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_DOC.as_posix(),
                DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day119 JSON/HTML reviewer evidence intake outcome ledger",
                "Day119 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REVIEW_ONLY REPORT_ONLY Day119 follows the seven Day118 expected evidence items only. Includes overall_status=INTAKE_LEDGER_READY, final_recommendation=REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION, source_record_count=7, ledger_record_count=7, intake statuses RECEIVED/PARTIAL/MISSING/DEFERRED/REJECTED/NEEDS_CLARIFICATION, gap statuses NO_GAP/OPEN_GAP/DEFERRED_GAP/SAFETY_BLOCKED_GAP/CLARIFICATION_REQUIRED, acceptance_decision_made=false, reviewer_signoff_made=false, safety_boundary_released=false, allowed_to_execute=false, ssh_allowed=false, live_command_allowed=false, adapter_invocation_allowed=false, broker_handoff_allowed=false, parser_capability_changed=false. No item is accepted, signed off, released, handed off, executed, or used to expand parser capability.",
        },
        {
            "id": DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_TASK_ID,
            "task_id": "day123_safety_boundary_regression_matrix",
            "display_name": "Day123 Safety Boundary Regression Matrix",
            "user_display_name": "Safety Boundary Regression Matrix",
            "day": "Day123",
            "category": "ai_planning",
            "description": "Builds a report-only regression matrix proving safety-critical task families and Day120-Day122 refactor seams remain non-executing.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_JSON.as_posix(),
                DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_HTML.as_posix(),
                DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_DOC.as_posix(),
                DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day123 JSON/HTML safety boundary regression matrix",
                "Day123 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REPORT_ONLY Day123 reviews mock-only, review-only, report-only, dry-run-only, fake-adapter-only, locked, disabled, parser-only, design-only, planning-only, scaffold-only, registry, CLI dispatch, and report-index boundaries. Includes overall_status=PASS, final_recommendation=KEEP_BOUNDARIES_LOCKED, execution_allowed=false, ssh_allowed=false, live_command_allowed=false, mutation_allowed=false, unlock_supported=false, adapter_invocation_allowed=false, broker_invocation_allowed=false, runner_invocation_allowed=false, openai_api_allowed=false, voice_runtime_allowed=false, dashboard_post_action_allowed=false. No reviewed task is executed.",
        },
        {
            "id": DAY124_SAFETY_INVARIANT_HELPER_REVIEW_TASK_ID,
            "task_id": "day124_safety_invariant_helper_review",
            "display_name": "Day124 Safety Invariant Helper Consolidation",
            "user_display_name": "Safety Invariant Helper Consolidation",
            "day": "Day124",
            "category": "ai_planning",
            "description": "Builds a review-only report proving shared safety invariant helpers keep dangerous execution capability flags false.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY124_SAFETY_INVARIANT_HELPER_REVIEW_JSON.as_posix(),
                DAY124_SAFETY_INVARIANT_HELPER_REVIEW_HTML.as_posix(),
                DAY124_SAFETY_INVARIANT_HELPER_REVIEW_DOC.as_posix(),
                DAY124_SAFETY_INVARIANT_HELPER_REVIEW_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day124 JSON/HTML safety invariant helper review",
                "Day124 AI intent and roadmap documentation",
            ],
            "related_script": "network_lab.py",
            "notes": "REVIEW_ONLY REPORT_ONLY Day124 consolidates deterministic safety invariant helpers. Includes overall_status=PASS, mode=REVIEW_ONLY, execution_allowed=false, final_recommendation=KEEP_REVIEW_ONLY_SAFETY_INVARIANTS, openai_api_allowed=false, voice_input_allowed=false, ssh_allowed=false, live_device_allowed=false, live_command_allowed=false, runtime_unlock_supported=false, dashboard_post_allowed=false, broker_execution_allowed=false, mapped_task_execution_allowed=false, write_operation_allowed=false, configuration_change_allowed=false. No runtime, provider, dashboard POST/action, broker, mapped task, SSH, live execution, or configuration-changing path is added.",
        },
        {
            "id": DAY125_THIN_CLI_REGRESSION_GATE_TASK_ID,
            "task_id": "day125_thin_cli_regression_gate",
            "display_name": "Day125 Thin CLI Regression Gate",
            "user_display_name": "Thin CLI Regression Gate",
            "day": "Day125",
            "category": "ai_planning",
            "description": "Builds a report-only regression gate proving the Day120-Day124 registry, dispatch, report, formatter, and safety helper splits remain stable.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY125_THIN_CLI_REGRESSION_GATE_JSON.as_posix(),
                DAY125_THIN_CLI_REGRESSION_GATE_HTML.as_posix(),
                DAY125_THIN_CLI_REGRESSION_GATE_DOC.as_posix(),
                DAY125_THIN_CLI_REGRESSION_GATE_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day125 JSON/HTML thin CLI regression gate",
                "Day125 AI intent and roadmap documentation",
            ],
            "related_script": "intent_thin_cli_regression_gate.py",
            "notes": "REPORT_ONLY Day125 verifies AGENTS.md pre-read evidence, thin CLI delegation, registry resolution, dispatch wiring, report-index readability, Day124 safety helper invariants, and representative smoke tasks. It keeps allowed_to_execute=false, ssh_allowed=false, live_command_allowed=false, next_phase_allowed=false, live_execution_added=false, ssh_added=false, openai_api_added=false, and dashboard_execution_endpoint_added=false.",
        },
        {
            "id": DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_TASK_ID,
            "task_id": "day126_post_refactor_compatibility_evidence_pack",
            "display_name": "Day126 Post-Refactor Compatibility Evidence Pack",
            "user_display_name": "Post-Refactor Compatibility Evidence Pack",
            "day": "Day126",
            "category": "ai_planning",
            "description": "Builds a report-only compatibility evidence pack for Day120-Day125 responsibility-split work with the Day125 thin CLI gate represented as one snapshot only.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_JSON.as_posix(),
                DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_HTML.as_posix(),
                DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_DOC.as_posix(),
                DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day126 JSON/HTML post-refactor compatibility evidence pack",
                "Day126 AI intent and roadmap documentation",
            ],
            "related_script": "intent_post_refactor_compatibility_evidence_pack.py",
            "notes": "REPORT_ONLY REVIEWER_ONLY Day126 verifies Day120 task registry, Day121 CLI dispatch, Day122 report-index/report registry, Day123 formatter/output, Day124 safety helper, and a single Day125 thin CLI snapshot. It does not add a thin CLI budget gate, numeric budget thresholds, budget enforcement, live execution, SSH, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or execution unlock.",
        },
        {
            "id": DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_TASK_ID,
            "task_id": "day127_ai_reviewer_summary_schema_contract",
            "display_name": "Day127 AI Reviewer Summary Schema Contract Integration",
            "user_display_name": "AI Reviewer Summary Schema Contract",
            "day": "Day127",
            "category": "ai_planning",
            "description": "Builds a report-only AI reviewer summary data structure contract with schema validation and a static example fixture.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_JSON.as_posix(),
                DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_HTML.as_posix(),
                DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_DOC.as_posix(),
                DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_ROADMAP_DOC.as_posix(),
                "fixtures/day127_ai_reviewer_summary.example.json",
            ],
            "report_outputs": [
                "Day127 JSON/HTML AI reviewer summary schema contract",
                "Day127 AI intent and roadmap documentation",
                "Day127 static example fixture",
            ],
            "related_script": "intent_ai_reviewer_summary_schema_contract.py",
            "notes": "REPORT_ONLY REVIEWER_ONLY Day127 integrates schema, validation, example fixture, CLI task, tests, and documentation evidence for the AI reviewer summary data contract. It does not implement Day128 renderer, Day129 prompt text contract, Day130 redaction policy, live execution, SSH, OpenAI API, voice runtime, mapped task execution, dashboard action endpoint, or execution unlock.",
        },
        {
            "id": DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TASK_ID,
            "task_id": "day128_ai_reviewer_summary_fixture_renderer",
            "display_name": "Day128 AI Reviewer Summary Fixture Renderer",
            "user_display_name": "AI Reviewer Summary Fixture Renderer",
            "day": "Day128",
            "category": "ai_planning",
            "description": "Renders the existing Day127 AI reviewer summary schema fixture into deterministic reviewer-facing evidence.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_JSON.as_posix(),
                DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_HTML.as_posix(),
                DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TXT.as_posix(),
                DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_DOC.as_posix(),
                DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_ROADMAP_DOC.as_posix(),
                "fixtures/day127_ai_reviewer_summary.example.json",
            ],
            "report_outputs": [
                "Day128 JSON/HTML/text AI reviewer summary fixture render",
                "Day128 AI intent and roadmap documentation",
                "Day127 static example fixture reused as source",
            ],
            "related_script": "intent_ai_reviewer_summary_fixture_renderer.py",
            "notes": "REPORT_ONLY FIXTURE_ONLY NON_EXECUTABLE Day128 renders only the existing Day127 schema fixture. It does not redefine schema, make an AI decision, add a prompt contract, add redaction policy, call OpenAI API, enable a provider/API, add live execution, SSH, mapped execution, execution unlock, next-day feature, or next-phase approval.",
        },
        {
            "id": DAY129_AI_SUMMARY_PROMPT_CONTRACT_TASK_ID,
            "task_id": "day129_ai_summary_prompt_contract",
            "display_name": "Day129 AI Summary Prompt Contract for Reviewer Text Only",
            "user_display_name": "AI Summary Prompt Contract",
            "day": "Day129",
            "category": "ai_planning",
            "description": "Defines a deterministic prompt contract limited to reviewer summary text only.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY129_AI_SUMMARY_PROMPT_CONTRACT_JSON.as_posix(),
                DAY129_AI_SUMMARY_PROMPT_CONTRACT_HTML.as_posix(),
                DAY129_AI_SUMMARY_PROMPT_CONTRACT_DOC.as_posix(),
                DAY129_AI_SUMMARY_PROMPT_CONTRACT_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day129 JSON/HTML AI summary prompt contract",
                "Day129 AI intent and roadmap documentation",
            ],
            "related_script": "intent_ai_summary_prompt_contract.py",
            "notes": "REPORT_ONLY PROMPT_CONTRACT_ONLY REVIEWER_TEXT_ONLY Day129 defines what a future prompt may ask for. It does not implement Day130 redaction policy, Day131 audit trail binding, Day132 reviewer approval gate, Day133 mock provider boundary, OpenAI API calls, provider/API configuration, tool calling, execution, AI decisions, pass/fail decisions, next-phase approval, or execution unlock.",
        },
        {
            "id": DAY130_AI_SUMMARY_REDACTION_POLICY_TASK_ID,
            "task_id": "day130_ai_summary_redaction_and_no_secret_policy",
            "display_name": "Day130 AI Summary Redaction and No-Secret Policy",
            "user_display_name": "AI Summary Redaction Policy",
            "day": "Day130",
            "category": "ai_planning",
            "description": "Applies deterministic local redaction checks to reviewer summary text and reports no-secret policy evidence.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY130_AI_SUMMARY_REDACTION_POLICY_JSON.as_posix(),
                DAY130_AI_SUMMARY_REDACTION_POLICY_HTML.as_posix(),
                DAY130_AI_SUMMARY_REDACTION_POLICY_DOC.as_posix(),
                DAY130_AI_SUMMARY_REDACTION_POLICY_ROADMAP_DOC.as_posix(),
                DAY130_AI_SUMMARY_REDACTION_POLICY_FIXTURE.as_posix(),
            ],
            "report_outputs": [
                "Day130 JSON/HTML AI summary redaction policy",
                "Day130 AI intent and roadmap documentation",
                "Day130 fake local redaction fixtures",
            ],
            "related_script": "intent_ai_summary_redaction_policy.py",
            "notes": "REPORT_ONLY REVIEW_ONLY LOCAL_ONLY Day130 enforces deterministic redaction and no-secret policy evidence for reviewer summary text. It is not Day131 audit trail binding, Day132 reviewer approval gate, or Day133 mock provider boundary, and does not enable execution, provider/API configuration, OpenAI API calls, network calls, AI decisions, reviewer approval inference, SSH, live device access, real adapter/broker/runner execution behavior, next-phase approval, or execution unlock.",
        },
        {
            "id": DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_TASK_ID,
            "task_id": "day131_ai_summary_audit_trail_binding",
            "display_name": "Day131 AI Summary Audit Trail Binding",
            "user_display_name": "AI Summary Audit Trail Binding",
            "day": "Day131",
            "category": "ai_planning",
            "description": "Binds Day127-Day130 AI summary artifacts into deterministic reviewer-visible audit records.",
            "safety_level": "report-only",
            "execution_mode": "report-only",
            "enabled": True,
            "status": "implemented",
            "requires_live_device": False,
            "requires_password": False,
            "produces_report": True,
            "report_paths": [
                DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_JSON.as_posix(),
                DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_HTML.as_posix(),
                DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_DOC.as_posix(),
                DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_ROADMAP_DOC.as_posix(),
            ],
            "report_outputs": [
                "Day131 JSON/HTML AI summary audit trail binding",
                "Day131 AI intent and roadmap documentation",
            ],
            "related_script": "intent_ai_summary_audit_trail_binding.py",
            "notes": "REPORT_ONLY REVIEW_ONLY NON_ADVANCING Day131 binds Day127 schema, Day128 fixture renderer, Day129 prompt contract, and Day130 redaction/no-secret policy evidence into deterministic audit records. It is not Day132 reviewer approval gate or Day133 mock provider boundary, and does not enable provider/API configuration, OpenAI API calls, AI execution, AI decisions, reviewer approval, mock provider behavior, SSH, live device access, broker/runner/adapter invocation, next-phase approval, or execution unlock.",
        },
    ]


def _build_parser() -> argparse.ArgumentParser:
    from network_lab_cli_dispatch import _build_parser as build_cli_parser

    return build_cli_parser(sys.modules[__name__])


def _resolve_project_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _task_enabled_label(task: Dict[str, Any]) -> str:
    return "enabled" if task.get("enabled") else "planned"


def _print_compact_task_list() -> None:
    print(format_heading("Task Catalog"))
    print("Use: python network_lab.py --task <task-name>")
    print("For full metadata, run: python network_lab.py --list-tasks --verbose")
    print()
    print(f"{'Task':<24} {'Name':<38} {'Safety':<18} Status")
    print(f"{'-' * 24} {'-' * 38} {'-' * 18} {'-' * 10}")
    for task in list_tasks():
        print(
            f"{task['id']:<24} "
            f"{str(task.get('user_display_name', task['display_name']))[:38]:<38} "
            f"{task['safety_level']:<18} "
            f"{_task_enabled_label(task)}"
        )


def _print_verbose_task_list() -> None:
    print(format_heading("Task Catalog"))
    for task in list_tasks():
        print()
        print(f"[{task['task_id']}]")
        print(f"CLI task: {task['id']}")
        print(f"Day: {task['day']}")
        print(f"Display name: {task['display_name']}")
        print(f"User-facing name: {task.get('user_display_name', task['display_name'])}")
        print(f"Category: {task['category']}")
        print(f"Safety: {task['safety_level']}")
        print(f"Enabled: {'yes' if task['enabled'] else 'no'}")
        print(f"Execution mode: {task['execution_mode']}")
        print(f"Live device required: {'yes' if task['requires_live_device'] else 'no'}")
        print(f"Password required: {'yes' if task['requires_password'] else 'no'}")
        print(f"Related script: {task['related_script']}")
        print("Reports:")
        for report_path in task.get("report_paths", []):
            print(f"  - {report_path}")
        print(f"Notes: {task['notes']}")


def _print_task_list(verbose: bool = False) -> None:
    if verbose:
        _print_verbose_task_list()
        return
    _print_compact_task_list()


def _normalize_intent_text(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _text_contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def build_day57_intent_mapping(user_input: str) -> Dict[str, Any]:
    normalized = _normalize_intent_text(user_input)
    base_mapping: Dict[str, Any] = {
        "day": "Day57",
        "prototype": "AI-assisted Task Intent Mapping Prototype",
        "normalized_user_input": normalized,
        "execution_mode": "dry_run_only",
        "mapped_task_executed": False,
        "openai_api_used": False,
        "voice_control_used": False,
        "ssh_used": False,
        "device_connection_used": False,
        "config_json_read": False,
        "blocked_actions": [
            "OpenAI API calls",
            "speech or voice control",
            "SSH sessions",
            "live runner delegation",
            "MikroTik/Cisco/router/switch/firewall/VPN/device connections",
            "NAT/IP/VRRP/WireGuard/firewall/interface/route/device configuration changes",
        ],
    }

    if _text_contains_any(normalized, ["vrrp", "failover", "fail over"]) and _text_contains_any(
        normalized,
        ["run", "do", "test", "start", "trigger", "validate", "check"],
    ):
        base_mapping.update(
            {
                "detected_intent": "vrrp_failover_test_request",
                "mapped_allowlisted_task": f"{DAY35_VRRP_FAILOVER_TASK_ID} (blocked in Day57)",
                "safety_level": "guarded_live_candidate",
                "confirmation_requirement": "mandatory_before_any_future_live_capable_path",
                "day57_result": "blocked_in_day57_dry_run_mapping_only",
                "human_review_required": True,
                "rationale": "VRRP failover can affect lab availability, so Day57 only records the proposed mapping and blocks execution.",
            }
        )
        return base_mapping

    if _text_contains_any(normalized, ["wireguard", "wire guard", "wg"]) and _text_contains_any(
        normalized,
        ["run", "check", "validate", "validation", "status", "test"],
    ):
        base_mapping.update(
            {
                "detected_intent": "wireguard_status_or_validation_request",
                "mapped_allowlisted_task": WIREGUARD_RUNNER_TASK_ALIAS,
                "safety_level": "guarded_dry_run",
                "confirmation_requirement": "required_before_any_future_live_capable_path",
                "day57_result": "dry_run_mapping_only",
                "human_review_required": True,
                "rationale": "WireGuard validation may become guarded-live later, but Day57 never delegates to the runner.",
            }
        )
        return base_mapping

    if _text_contains_any(normalized, ["dashboard", "open dashboard", "dashboard page"]):
        base_mapping.update(
            {
                "detected_intent": "open_dashboard_or_report_view",
                "mapped_allowlisted_task": "dashboard / report viewer",
                "safety_level": "local_ui_only",
                "confirmation_requirement": "not_required",
                "day57_result": "dry_run_mapping_only",
                "human_review_required": False,
                "rationale": "Opening local UI/report views is low risk, but Day57 still returns only the mapping proposal.",
            }
        )
        return base_mapping

    if _text_contains_any(normalized, ["report", "reports", "latest report", "latest reports", "evidence"]):
        base_mapping.update(
            {
                "detected_intent": "view_reports",
                "mapped_allowlisted_task": "report-index",
                "safety_level": "report_only",
                "confirmation_requirement": "not_required_or_low_risk_confirmation_only",
                "day57_result": "dry_run_mapping_only",
                "human_review_required": False,
                "rationale": "Report viewing maps to the local report index path, but Day57 does not execute report-index.",
            }
        )
        return base_mapping

    base_mapping.update(
        {
            "detected_intent": "unknown_or_ambiguous",
            "mapped_allowlisted_task": None,
            "safety_level": "needs_manual_review",
            "confirmation_requirement": "manual_review_required",
            "day57_result": "no_task_mapped_dry_run_only",
            "human_review_required": True,
            "rationale": "Unknown or ambiguous requests must not map to execution.",
        }
    )
    return base_mapping


def _run_day57_intent_mapping_prototype(intent_text: str) -> int:
    mapping = build_day57_intent_mapping(intent_text)
    print(format_heading("Day57 AI-assisted Task Intent Mapping Prototype"))
    print(json.dumps(mapping, indent=2, sort_keys=True))
    print()
    print(f"{format_status('PASS')} Dry-run mapping only. No mapped task was executed.")
    return 0


def _redact_intent_text_for_report(intent_text: str) -> str:
    redacted = str(intent_text or "")
    secret_patterns = [
        r"(?i)\b(password|secret|token|api[_ -]?key|private[_ -]?key|preshared[_ -]?key)\s*[:=]\s*[^\s,;]+",
        r"(?i)\b(password|secret|token|api[_ -]?key|private[_ -]?key|preshared[_ -]?key)\s+[^\s,;]+",
    ]
    for pattern in secret_patterns:
        redacted = re.sub(pattern, lambda match: f"{match.group(1)} [REDACTED]", redacted)
    return redacted


def _day58_blocked_policy_match(normalized: str) -> Optional[Tuple[str, str]]:
    if _text_contains_any(normalized, ["vrrp failover", "failover", "fail over"]) and "vrrp" in normalized:
        return ("VRRP failover execution", "VRRP failover can affect network availability and is blocked by default.")
    if "interface" in normalized and _text_contains_any(normalized, ["disable", "enable", "shutdown", "no shutdown"]):
        return ("interface disable/enable", "Interface state changes can interrupt connectivity and are blocked by default.")
    if "firewall" in normalized and _text_contains_any(normalized, ["add", "remove", "delete", "change", "modify", "set", "rule"]):
        return ("firewall rule add/remove/change", "Firewall rule changes alter traffic policy and are blocked by default.")
    if "nat" in normalized and _text_contains_any(normalized, ["add", "remove", "delete", "change", "modify", "set"]):
        return ("NAT change", "NAT changes alter traffic forwarding behavior and are blocked by default.")
    if _text_contains_any(normalized, ["ip address", "address change", "change ip", "set ip", "add ip", "remove ip"]):
        return ("IP address change", "IP address changes can disrupt management and lab reachability and are blocked by default.")
    if "route" in normalized and _text_contains_any(normalized, ["add", "remove", "delete", "change", "modify", "set"]):
        return ("route change", "Route changes alter packet forwarding and are blocked by default.")
    if _text_contains_any(normalized, ["wireguard peer", "wg peer"]) and _text_contains_any(
        normalized,
        ["add", "remove", "delete", "recreate", "change", "modify", "set"],
    ):
        return ("WireGuard peer add/remove/recreate", "WireGuard peer changes alter VPN state and are blocked by default.")
    if _text_contains_any(normalized, ["reboot", "reset", "restart router", "factory reset"]):
        return ("router reboot/reset", "Router reboot or reset actions are blocked by default.")
    if _text_contains_any(normalized, ["ssh", "routeros command", "ros command"]):
        return ("SSH command execution", "SSH or RouterOS command execution is outside Day58 scope and is blocked.")
    if _text_contains_any(normalized, ["shell command", "powershell", "cmd.exe", "bash", "run command"]):
        return ("arbitrary shell command execution", "Arbitrary shell command execution is outside Day58 scope and is blocked.")
    if _text_contains_any(normalized, ["apply config", "apply configuration", "configure device", "device config", "push config"]):
        return ("direct device configuration apply", "Direct device configuration apply is blocked by default.")
    return None


def build_day58_intent_safety_review(user_input: str) -> Dict[str, Any]:
    normalized = _normalize_intent_text(user_input)
    redacted_intent = _redact_intent_text_for_report(user_input)
    day57_mapping = build_day57_intent_mapping(user_input)
    day57_mapping["normalized_user_input"] = _normalize_intent_text(redacted_intent)

    mapped_task = day57_mapping.get("mapped_allowlisted_task")
    safety_classification = "unknown_blocked"
    action_capability = "unknown"
    confirmation_gate_required = True
    blocked = True
    blocked_policy_match: Optional[str] = None
    blocked_action_decision = "blocked_unknown_intent"
    rationale = "Unknown or ambiguous intent is blocked until a human reviews it."

    policy_match = _day58_blocked_policy_match(normalized)
    if policy_match:
        blocked_policy_match, rationale = policy_match
        mapped_task = mapped_task or "blocked-live-capable-action"
        safety_classification = "blocked_live_capable"
        action_capability = "live_capable"
        confirmation_gate_required = True
        blocked = True
        blocked_action_decision = "blocked_by_default_policy"
    elif day57_mapping.get("detected_intent") in {"view_reports", "open_dashboard_or_report_view"} or _text_contains_any(
        normalized,
        ["show latest reports", "latest reports", "run report index", "report index", "open dashboard", "view reports"],
    ):
        mapped_task = "report-index" if "dashboard" not in normalized else "dashboard/report viewer"
        safety_classification = "report_only"
        action_capability = "report_only"
        confirmation_gate_required = False
        blocked = False
        blocked_action_decision = "allowed_report_only"
        rationale = "Report and dashboard review reads local generated artifacts only and does not touch devices."
    elif _text_contains_any(normalized, ["dry run", "dry-run", "preview", "plan only", "staged plan"]):
        safety_classification = "dry_run"
        action_capability = "dry_run"
        confirmation_gate_required = False
        blocked = False
        blocked_action_decision = "allowed_dry_run_only"
        rationale = "Dry-run preview is allowed only because Day58 does not execute mapped tasks or connect to devices."
    elif _text_contains_any(normalized, ["read only", "read-only", "precheck", "status check", "show status"]):
        safety_classification = "read_only"
        action_capability = "read_only"
        confirmation_gate_required = True
        blocked = False
        blocked_action_decision = "allowed_with_review_or_explicit_flag"
        rationale = "Read-only requests may be low risk but still require review when they imply live device access."
    elif mapped_task:
        safety_classification = "live_capable_requires_confirmation"
        action_capability = "live_capable"
        confirmation_gate_required = True
        blocked = True
        blocked_action_decision = "blocked_pending_future_confirmation_gate"
        rationale = "Mapped live-capable runner proposals must never execute directly from intent mapping."

    return {
        "day": "Day58",
        "task_name": DAY58_INTENT_SAFETY_REVIEW_TASK_ID,
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "intent_text": redacted_intent,
        "normalized_intent_text": _normalize_intent_text(redacted_intent),
        "detected_intent": day57_mapping.get("detected_intent"),
        "mapped_task": mapped_task,
        "mapped_task_executed": False,
        "day57_mapping_reference": day57_mapping,
        "safety_categories_supported": [
            "report_only",
            "read_only",
            "dry_run",
            "live_capable_requires_confirmation",
            "blocked_live_capable",
            "unknown_blocked",
        ],
        "safety_classification": safety_classification,
        "action_capability": action_capability,
        "confirmation_gate_required": confirmation_gate_required,
        "blocked": blocked,
        "blocked_action_decision": blocked_action_decision,
        "blocked_policy_match": blocked_policy_match,
        "rationale": rationale,
        "confirmation_gate_model": DAY58_CONFIRMATION_GATE_RULES,
        "blocked_live_capable_action_policy": DAY58_BLOCKED_LIVE_CAPABLE_ACTIONS,
        "safety_boundaries": DAY58_SAFETY_BOUNDARIES,
        "final_status": "PASS",
        "no_live_execution_occurred": True,
        "openai_api_used": False,
        "voice_control_used": False,
        "ssh_used": False,
        "device_connection_used": False,
        "config_json_read": False,
        "config_json_modified": False,
        "device_configuration_changed": False,
    }


def write_day58_intent_safety_review_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = "\n".join(
        f"<tr><td>{html.escape(label)}</td><td>{html.escape(str(value))}</td></tr>"
        for label, value in [
            ("Day", report.get("day", "")),
            ("Task name", report.get("task_name", "")),
            ("Intent text", report.get("intent_text", "")),
            ("Detected intent", report.get("detected_intent", "")),
            ("Mapped task", report.get("mapped_task", "")),
            ("Safety classification", report.get("safety_classification", "")),
            ("Confirmation gate required", report.get("confirmation_gate_required", "")),
            ("Blocked", report.get("blocked", "")),
            ("Blocked action decision", report.get("blocked_action_decision", "")),
            ("Blocked policy match", report.get("blocked_policy_match", "")),
            ("Final status", report.get("final_status", "")),
            ("No live execution occurred", report.get("no_live_execution_occurred", "")),
        ]
    )
    categories = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_categories_supported", []))
    gate_rules = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("confirmation_gate_model", []))
    blocked_policy = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("blocked_live_capable_action_policy", []))
    boundaries = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundaries", []))
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day58 Intent Mapping Safety Review</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; background: #f6f8fb; }}
    main {{ max-width: 1040px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 26px 0 10px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d8e0ec; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .notice {{ background: #fff4d8; border: 1px solid #f0c66a; padding: 12px 14px; margin: 16px 0; color: #765200; }}
    .panel {{ background: #fff; border: 1px solid #d8e0ec; padding: 12px 18px; }}
  </style>
</head>
<body>
  <main>
    <h1>Day58 Intent Mapping Safety Review</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))}</div>
    <div class="notice">Report-only confirmation gate review. No mapped task was executed, no SSH was used, and no device or network configuration was changed.</div>
    <h2>Safety Decision</h2>
    <table><tbody>{summary_rows}</tbody></table>
    <h2>Rationale</h2>
    <div class="panel">{html.escape(str(report.get("rationale", "")))}</div>
    <h2>Supported Safety Categories</h2>
    <ul class="panel">{categories}</ul>
    <h2>Confirmation Gate Model</h2>
    <ul class="panel">{gate_rules}</ul>
    <h2>Blocked Live-capable Action Policy</h2>
    <ul class="panel">{blocked_policy}</ul>
    <h2>Safety Boundaries</h2>
    <ul class="panel">{boundaries}</ul>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day58_intent_safety_review(project_root: Path, intent_text: str) -> int:
    report = build_day58_intent_safety_review(intent_text)
    json_path = project_root / DAY58_INTENT_SAFETY_REVIEW_JSON
    html_path = project_root / DAY58_INTENT_SAFETY_REVIEW_HTML
    write_json_report(report, json_path)
    write_day58_intent_safety_review_html(mask_secret_values(report), html_path)

    print(format_heading("Day58 Intent Mapping Safety Review and Confirmation Gate"))
    print(f"Intent text: {report.get('intent_text') or '<empty>'}")
    print(f"Mapped task: {report.get('mapped_task') or '<none>'}")
    print(f"Safety classification: {report.get('safety_classification')}")
    print(f"Confirmation gate required: {report.get('confirmation_gate_required')}")
    print(f"Blocked: {report.get('blocked')}")
    print(f"Rationale: {report.get('rationale')}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day58 safety review completed. No live execution occurred.")
    return 0


def build_day59_intent_policy_matrix() -> Dict[str, Any]:
    matrix_rows = [dict(row) for row in DAY59_INTENT_POLICY_MATRIX_ROWS]
    allowed_rows = [
        row
        for row in matrix_rows
        if str(row.get("default_decision", "")).startswith("allowed")
        and row.get("allowed_to_execute_automatically") is True
    ]
    blocked_rows = [
        row
        for row in matrix_rows
        if str(row.get("default_decision", "")).startswith("blocked")
        or row.get("allowed_to_execute_automatically") is False
    ]
    return {
        "day": "Day59",
        "task_name": DAY59_INTENT_POLICY_MATRIX_TASK_ID,
        "task_id": "day59_intent_policy_matrix_reviewer_safety_explanation",
        "task_type": "report-only",
        "safety_level": "report_only",
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "final_status": "PASS",
        "matrix_columns": [
            "intent_category",
            "example_user_phrase",
            "mapped_task_type",
            "safety_classification",
            "default_decision",
            "requires_confirmation",
            "allowed_to_execute_automatically",
            "reviewer_explanation",
            "evidence_report_output",
        ],
        "policy_matrix": matrix_rows,
        "summary": {
            "total_categories": len(matrix_rows),
            "allowed_category_count": len(allowed_rows),
            "blocked_category_count": len(blocked_rows),
            "mapped_task_execution_from_intent_allowed": False,
        },
        "reviewer_facing_explanation": DAY59_REVIEWER_EXPLANATION,
        "safety_scope": {
            "documentation_only": True,
            "report_only": True,
            "explanation_only": True,
            "mapped_tasks_executed": False,
            "live_tests_executed": False,
            "openai_api_used": False,
            "voice_control_used": False,
            "ssh_connections_opened": False,
            "device_connections_opened": False,
            "config_json_read": False,
            "config_json_modified": False,
            "router_switch_firewall_vpn_configuration_changed": False,
            "nat_ip_vrrp_wireguard_interface_route_changed": False,
            "release_tag_created": False,
        },
        "safety_boundaries": DAY58_SAFETY_BOUNDARIES,
        "confirmation_gate_model": DAY58_CONFIRMATION_GATE_RULES,
        "blocked_live_capable_action_policy": DAY58_BLOCKED_LIVE_CAPABLE_ACTIONS,
        "report_paths": {
            "json": DAY59_INTENT_POLICY_MATRIX_JSON.as_posix(),
            "html": DAY59_INTENT_POLICY_MATRIX_HTML.as_posix(),
        },
        "openai_api_used": False,
        "voice_control_used": False,
        "ssh_used": False,
        "device_connection_used": False,
        "config_json_read": False,
        "mapped_task_executed": False,
        "device_configuration_changed": False,
        "no_live_execution_occurred": True,
    }


def write_day59_intent_policy_matrix_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(row.get('intent_category', '')))}</td>"
        f"<td>{html.escape(str(row.get('example_user_phrase', '')))}</td>"
        f"<td>{html.escape(str(row.get('mapped_task_type', '')))}</td>"
        f"<td>{html.escape(str(row.get('safety_classification', '')))}</td>"
        f"<td>{html.escape(str(row.get('default_decision', '')))}</td>"
        f"<td>{html.escape(str(row.get('requires_confirmation', '')))}</td>"
        f"<td>{html.escape(str(row.get('allowed_to_execute_automatically', '')))}</td>"
        f"<td>{html.escape(str(row.get('reviewer_explanation', '')))}</td>"
        f"<td>{html.escape(str(row.get('evidence_report_output', '')))}</td>"
        "</tr>"
        for row in report.get("policy_matrix", [])
    )
    explanation = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("reviewer_facing_explanation", [])
    )
    scope_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report.get("safety_scope", {}).items()
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day59 Intent Policy Matrix</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; background: #f6f8fb; }}
    main {{ max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 26px 0 10px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d8e0ec; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .notice {{ background: #e9f7ef; border: 1px solid #8bd3a8; padding: 12px 14px; margin: 16px 0; color: #245b38; }}
    .panel {{ background: #fff; border: 1px solid #d8e0ec; padding: 12px 18px; }}
    .matrix {{ font-size: 13px; }}
  </style>
</head>
<body>
  <main>
    <h1>Day59 Intent Policy Matrix</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))}</div>
    <div class="notice">Safety: report-only. This report explains policy decisions only; it does not call APIs, use voice, open SSH, connect to devices, read config.json, or execute mapped tasks.</div>
    <h2>Reviewer Explanation</h2>
    <ul class="panel">{explanation}</ul>
    <h2>Policy Matrix</h2>
    <table class="matrix">
      <thead>
        <tr>
          <th>Intent category</th>
          <th>Example user phrase</th>
          <th>Mapped task type</th>
          <th>Safety classification</th>
          <th>Default decision</th>
          <th>Requires confirmation?</th>
          <th>Allowed to execute automatically?</th>
          <th>Reviewer explanation</th>
          <th>Evidence / report output</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <h2>Safety Scope</h2>
    <table><tbody>{scope_rows}</tbody></table>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day59_intent_policy_matrix(project_root: Path) -> int:
    report = build_day59_intent_policy_matrix()
    json_path = project_root / DAY59_INTENT_POLICY_MATRIX_JSON
    html_path = project_root / DAY59_INTENT_POLICY_MATRIX_HTML
    write_json_report(report, json_path)
    write_day59_intent_policy_matrix_html(mask_secret_values(report), html_path)

    print(format_heading("Day59 Intent Policy Matrix and Reviewer Safety Explanation"))
    print("Safety: report-only")
    print(f"Policy categories: {report['summary']['total_categories']}")
    print(f"Allowed categories: {report['summary']['allowed_category_count']}")
    print(f"Blocked categories: {report['summary']['blocked_category_count']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day59 policy matrix generated. No mapped task was executed.")
    return 0


def _build_day60_demo_example(example: Dict[str, Any]) -> Dict[str, Any]:
    intent_text = str(example["input_intent_text"])
    day57_mapping = build_day57_intent_mapping(intent_text)
    candidate_task = example.get("candidate_task")
    mapped_task = candidate_task if candidate_task is not None else day57_mapping.get("mapped_allowlisted_task")
    blocked = bool(example["blocked"])
    return {
        "input_intent_text": intent_text,
        "workflow": [
            {
                "step": 1,
                "name": "Input intent text",
                "result": intent_text,
            },
            {
                "step": 2,
                "name": "Day57-style dry-run intent mapping",
                "result": {
                    "detected_intent": day57_mapping.get("detected_intent"),
                    "mapped_task": mapped_task,
                    "mapped_task_executed": False,
                },
            },
            {
                "step": 3,
                "name": "Day58-style safety review",
                "result": {
                    "safety_classification": example["expected_classification"],
                    "blocked": blocked,
                    "confirmation_required_for_live_or_config_actions": blocked,
                },
            },
            {
                "step": 4,
                "name": "Day59-style policy explanation",
                "result": example["policy_explanation"],
            },
            {
                "step": 5,
                "name": "Reviewer decision",
                "result": example["reviewer_decision"],
            },
            {
                "step": 6,
                "name": "No execution performed",
                "result": DAY60_NO_EXECUTION_STATEMENT,
            },
        ],
        "expected_classification": example["expected_classification"],
        "candidate_task": mapped_task,
        "reviewer_decision": example["reviewer_decision"],
        "blocked": blocked,
        "mapped_task_executed": False,
        "no_execution_statement": DAY60_NO_EXECUTION_STATEMENT,
    }


def build_day60_intent_workflow_demo() -> Dict[str, Any]:
    examples = [_build_day60_demo_example(example) for example in DAY60_INTENT_WORKFLOW_DEMO_EXAMPLES]
    allowed_examples = [example for example in examples if example["blocked"] is False]
    blocked_examples = [example for example in examples if example["blocked"] is True]
    return {
        "day": "Day60",
        "task_name": DAY60_INTENT_WORKFLOW_DEMO_TASK_ID,
        "task_id": "day60_ai_intent_workflow_demo_reviewer_walkthrough",
        "task_type": "report-only",
        "safety_level": "report_only",
        "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
        "final_status": "PASS",
        "purpose": (
            "Connect Day57, Day58, and Day59 into a reviewer-facing local walkthrough "
            "for the AI intent workflow without real AI, voice, SSH, devices, or live execution."
        ),
        "relationship_to_previous_days": [
            "Day57 provides deterministic dry-run intent mapping.",
            "Day58 provides safety review and confirmation gate design.",
            "Day59 provides the reviewer-facing policy matrix and safety explanation.",
            "Day60 connects those pieces into one local walkthrough report.",
        ],
        "workflow_steps": DAY60_WORKFLOW_STEPS,
        "example_intents": examples,
        "summary": {
            "total_examples": len(examples),
            "allowed_examples": len(allowed_examples),
            "blocked_examples": len(blocked_examples),
            "mapped_task_execution_from_intent_allowed": False,
            "mapped_tasks_executed": False,
        },
        "safety_scope": {
            "documentation_only": True,
            "report_only": True,
            "reviewer_walkthrough_only": True,
            "openai_api_used": False,
            "voice_control_used": False,
            "mapped_tasks_executed": False,
            "live_tests_executed": False,
            "ssh_connections_opened": False,
            "device_connections_opened": False,
            "config_json_read": False,
            "config_json_required": False,
            "config_json_modified": False,
            "router_switch_firewall_vpn_configuration_changed": False,
            "nat_ip_vrrp_wireguard_interface_route_changed": False,
            "release_tag_created": False,
            "v0_3_runtime_started": False,
        },
        "safety_boundaries": DAY58_SAFETY_BOUNDARIES
        + [
            "No real AI intent runtime implementation.",
            "No reviewer decision triggers mapped task execution.",
        ],
        "intentionally_not_implemented": [
            "OpenAI API integration",
            "voice input or speech recognition",
            "mapped task execution",
            "live network testing",
            "SSH or device access",
            "config.json dependency",
            "NAT/IP/VRRP/WireGuard/firewall/interface/route/device configuration changes",
            "release tag creation",
            "v0.3 runtime implementation",
        ],
        "report_paths": {
            "json": DAY60_INTENT_WORKFLOW_DEMO_JSON.as_posix(),
            "html": DAY60_INTENT_WORKFLOW_DEMO_HTML.as_posix(),
        },
        "openai_api_used": False,
        "voice_control_used": False,
        "ssh_used": False,
        "device_connection_used": False,
        "config_json_read": False,
        "config_json_required": False,
        "mapped_task_executed": False,
        "device_configuration_changed": False,
        "no_live_execution_occurred": True,
        "final_safety_statement": DAY60_NO_EXECUTION_STATEMENT,
    }


def write_day60_intent_workflow_demo_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    steps = "".join(
        "<tr>"
        f"<td>{html.escape(str(step.get('step', '')))}</td>"
        f"<td>{html.escape(str(step.get('name', '')))}</td>"
        f"<td>{html.escape(str(step.get('reviewer_view', '')))}</td>"
        "</tr>"
        for step in report.get("workflow_steps", [])
    )
    examples = "".join(
        "<tr>"
        f"<td>{html.escape(str(example.get('input_intent_text', '')))}</td>"
        f"<td>{html.escape(str(example.get('candidate_task', '')))}</td>"
        f"<td>{html.escape(str(example.get('expected_classification', '')))}</td>"
        f"<td>{html.escape(str(example.get('reviewer_decision', '')))}</td>"
        f"<td>{html.escape(str(example.get('mapped_task_executed', '')))}</td>"
        f"<td>{html.escape(str(example.get('no_execution_statement', '')))}</td>"
        "</tr>"
        for example in report.get("example_intents", [])
    )
    scope_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in report.get("safety_scope", {}).items()
    )
    boundaries = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundaries", []))
    not_implemented = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("intentionally_not_implemented", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day60 AI Intent Workflow Demo</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; background: #f6f8fb; }}
    main {{ max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 26px 0 10px; font-size: 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d8e0ec; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .notice {{ background: #fff4d8; border: 1px solid #f0c66a; padding: 12px 14px; margin: 16px 0; color: #765200; font-weight: 700; }}
    .panel {{ background: #fff; border: 1px solid #d8e0ec; padding: 12px 18px; }}
    .examples {{ font-size: 13px; }}
  </style>
</head>
<body>
  <main>
    <h1>Day60 AI Intent Workflow Demo</h1>
    <div>Generated {html.escape(str(report.get("generated_at", "")))}</div>
    <div class="notice">{html.escape(str(report.get("final_safety_statement", "")))}</div>
    <h2>Purpose</h2>
    <div class="panel">{html.escape(str(report.get("purpose", "")))}</div>
    <h2>Walkthrough Steps</h2>
    <table>
      <thead><tr><th>Step</th><th>Name</th><th>Reviewer view</th></tr></thead>
      <tbody>{steps}</tbody>
    </table>
    <h2>Example Intents</h2>
    <table class="examples">
      <thead>
        <tr><th>Intent</th><th>Candidate task</th><th>Classification</th><th>Reviewer decision</th><th>Mapped task executed?</th><th>Execution statement</th></tr>
      </thead>
      <tbody>{examples}</tbody>
    </table>
    <h2>Safety Scope</h2>
    <table><tbody>{scope_rows}</tbody></table>
    <h2>Safety Boundaries</h2>
    <ul class="panel">{boundaries}</ul>
    <h2>Intentionally Not Implemented</h2>
    <ul class="panel">{not_implemented}</ul>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day60_intent_workflow_demo(project_root: Path) -> int:
    report = build_day60_intent_workflow_demo()
    json_path = project_root / DAY60_INTENT_WORKFLOW_DEMO_JSON
    html_path = project_root / DAY60_INTENT_WORKFLOW_DEMO_HTML
    write_json_report(report, json_path)
    write_day60_intent_workflow_demo_html(mask_secret_values(report), html_path)

    print(format_heading("Day60 AI Intent Workflow Demo Reviewer Walkthrough"))
    print("Safety: report-only reviewer walkthrough")
    print(f"Workflow steps: {len(report['workflow_steps'])}")
    print(f"Example intents: {report['summary']['total_examples']}")
    print(f"Allowed examples: {report['summary']['allowed_examples']}")
    print(f"Blocked examples: {report['summary']['blocked_examples']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} {DAY60_NO_EXECUTION_STATEMENT}")
    return 0


def write_day66_offline_mock_runtime_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenarios = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('input_text', '')))}</td>"
        f"<td>{html.escape(str(item.get('normalized_intent', '')))}</td>"
        f"<td>{html.escape(str(item.get('safety_category', '')))}</td>"
        f"<td>{html.escape(str(item.get('execution_mode', '')))}</td>"
        f"<td>{html.escape(str(item.get('live_execution_allowed', '')))}</td>"
        f"<td>{html.escape(str(item.get('reviewer_note', '')))}</td>"
        "</tr>"
        for item in report.get("mock_scenarios", [])
    )
    scope_rows = "".join(
        "<tr>"
        f"<th>{html.escape(label)}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("Overall status", report.get("overall_status")),
            ("Reviewer status", report.get("reviewer_status")),
            ("Execution mode", report.get("execution_mode")),
            ("Live execution allowed", report.get("live_execution_allowed")),
            ("OpenAI API used", report.get("openai_api_used")),
            ("Voice integration used", report.get("voice_integration_used")),
            ("SSH used", report.get("ssh_used")),
            ("Device access occurred", not bool(report.get("no_device_access_occurred"))),
            ("Network change occurred", not bool(report.get("no_network_change_occurred"))),
            ("config.json read", report.get("config_json_read")),
            ("Mapped task executed", report.get("mapped_task_executed")),
        ]
    )
    stages = "".join(
        f"<li>{html.escape(str(stage))}</li>" for stage in report.get("runtime_stages", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(ref))}</code></li>"
        for ref in report.get("evidence_links_or_doc_refs", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day66 Offline Mock Runtime Skeleton</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day66 Offline Mock Runtime Skeleton</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{scope_rows}</tbody></table>
  <h2>Runtime Stages</h2>
  <ol>{stages}</ol>
  <h2>Mock Scenarios</h2>
  <table>
    <thead>
      <tr><th>Input text</th><th>Normalized intent</th><th>Safety category</th><th>Execution mode</th><th>Live execution allowed?</th><th>Reviewer note</th></tr>
    </thead>
    <tbody>{scenarios}</tbody>
  </table>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day66_offline_mock_runtime(project_root: Path) -> int:
    report = build_mock_runtime_report()
    json_path = project_root / DAY66_OFFLINE_MOCK_RUNTIME_JSON
    html_path = project_root / DAY66_OFFLINE_MOCK_RUNTIME_HTML
    write_json_report(report, json_path)
    write_day66_offline_mock_runtime_html(mask_secret_values(report), html_path)

    print(format_heading("Day66 Offline Mock Runtime Skeleton"))
    print("Safety: offline mock / dry-run-only report")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Mock scenarios: {report['summary']['mock_scenarios']}")
    print(f"Blocked live-action scenarios: {report['summary']['blocked_live_action_scenarios']}")
    print(f"Execution mode: {report['execution_mode']}")
    print(f"Live execution allowed: {report['live_execution_allowed']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} No live execution, API, voice, SSH, device access, or network change occurred.")
    return 0


def build_day67_offline_mock_runtime_contract_report() -> Dict[str, Any]:
    day66_report = build_mock_runtime_report()
    scenarios = day66_report.get("mock_scenarios", [])
    validation_errors = validate_runtime_results(scenarios)
    scenario_validations = []
    for scenario in scenarios:
        scenario_errors = validate_runtime_results([scenario])
        scenario_validations.append(
            {
                "scenario_id": scenario.get("scenario_id"),
                "scenario_name": scenario.get("scenario_name"),
                "safety_category": scenario.get("safety_category"),
                "decision": scenario.get("decision"),
                "contract_status": "PASS" if not scenario_errors else "FAIL",
                "errors": scenario_errors,
            }
        )

    overall_status = "PASS" if not validation_errors else "FAIL"
    return {
        "day": "Day67",
        "title": "Offline Mock Runtime Contract & Safety Invariant Validation",
        "task_name": DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_TASK_ID,
        "overall_status": overall_status,
        "reviewer_status": "REVIEW_READY" if overall_status == "PASS" else "REVIEW_REQUIRED",
        "source_runtime_day": day66_report.get("day"),
        "source_runtime_title": day66_report.get("title"),
        "validated_scenarios": len(scenarios),
        "validation_errors": validation_errors,
        "scenario_validations": scenario_validations,
        "allowed_execution_modes": ["dry_run_only", "offline_mock"],
        "allowed_safety_categories": [
            "blocked_live_action",
            "documentation_only",
            "needs_manual_review",
            "report_only",
        ],
        "safety_invariants": {
            "live_execution_allowed_always_false": all(
                scenario.get("live_execution_allowed") is False for scenario in scenarios
            ),
            "mapped_task_executed_always_false": all(
                scenario.get("mapped_task_executed") is False for scenario in scenarios
            ),
            "blocked_live_actions_have_warning_and_evidence": all(
                scenario.get("blocked") is True
                and isinstance(scenario.get("reviewer_warning"), str)
                and bool(scenario.get("reviewer_warning", "").strip())
                and isinstance(scenario.get("evidence_references"), list)
                and bool(scenario.get("evidence_references"))
                for scenario in scenarios
                if scenario.get("safety_category") == "blocked_live_action"
            ),
        },
        "safety_boundary": [
            "No OpenAI API.",
            "No voice integration.",
            "No SSH.",
            "No device access.",
            "No live execution.",
            "No mapped task execution.",
            "No arbitrary command execution.",
            "No config.json dependency.",
            "No router, switch, firewall, VPN, VRRP, or network configuration changes.",
            "No release tag.",
        ],
        "report_only_statement": (
            "Day67 validates in-memory Day66 mock runtime dictionaries only. "
            "It does not enable AI, voice, SSH, device access, live execution, "
            "mapped task execution, or network configuration changes."
        ),
    }


def write_day67_offline_mock_runtime_contract_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('safety_category', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision', '')))}</td>"
        f"<td>{html.escape(str(item.get('contract_status', '')))}</td>"
        f"<td>{html.escape('; '.join(str(error) for error in item.get('errors', [])))}</td>"
        "</tr>"
        for item in report.get("scenario_validations", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    error_items = "".join(
        f"<li>{html.escape(str(error))}</li>" for error in report.get("validation_errors", [])
    ) or "<li>None</li>"
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day67 Offline Mock Runtime Contract</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day67 Offline Mock Runtime Contract &amp; Safety Invariant Validation</h1>
  <p class="safe">{html.escape(str(report.get("report_only_statement", "")))}</p>
  <h2>Summary</h2>
  <table>
    <tbody>
      <tr><th>Overall status</th><td>{html.escape(str(report.get("overall_status", "")))}</td></tr>
      <tr><th>Reviewer status</th><td>{html.escape(str(report.get("reviewer_status", "")))}</td></tr>
      <tr><th>Validated scenarios</th><td>{html.escape(str(report.get("validated_scenarios", "")))}</td></tr>
      <tr><th>Source runtime</th><td>{html.escape(str(report.get("source_runtime_title", "")))}</td></tr>
    </tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Scenario Contract Results</h2>
  <table>
    <thead><tr><th>Scenario ID</th><th>Safety category</th><th>Decision</th><th>Status</th><th>Errors</th></tr></thead>
    <tbody>{scenario_rows}</tbody>
  </table>
  <h2>Validation Errors</h2>
  <ul>{error_items}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day67_offline_mock_runtime_contract(project_root: Path) -> int:
    report = build_day67_offline_mock_runtime_contract_report()
    json_path = project_root / DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_JSON
    html_path = project_root / DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_HTML
    write_json_report(report, json_path)
    write_day67_offline_mock_runtime_contract_html(mask_secret_values(report), html_path)

    print(format_heading("Day67 Offline Mock Runtime Contract & Safety Invariant Validation"))
    print("Safety: offline mock contract validation / report-only")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Validated scenarios: {report['validated_scenarios']}")
    print(f"Validation errors: {len(report['validation_errors'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS":
        print(f"{format_status('PASS')} REVIEW_READY")
        print("No live execution, API, voice, SSH, device access, mapped task execution, or network change occurred.")
        return 0

    print(f"{format_status('FAIL')} REVIEW_REQUIRED")
    return 2


def write_day68_offline_mock_runtime_review_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('input_intent_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_result_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('safety_classification_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('blocked_reason_present_when_applicable', '')))}</td>"
        f"<td>{html.escape(str(item.get('evidence_reference_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('contract_validation_status', '')))}</td>"
        f"<td>{html.escape(str(item.get('no_live_execution_evidence_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('no_mapped_task_execution_evidence_present', '')))}</td>"
        f"<td>{html.escape(str(item.get('no_device_network_change_evidence_present', '')))}</td>"
        f"<td>{html.escape('; '.join(str(missing) for missing in item.get('missing_evidence', []))) or 'None'}</td>"
        f"<td>{html.escape(str(item.get('reviewer_verdict', '')))}</td>"
        "</tr>"
        for item in report.get("scenario_reviews", [])
    )
    quality = report.get("quality_gate_summary", {})
    quality_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("scenario_count", report.get("scenario_count")),
            ("review_status", report.get("review_status")),
            ("review_ready_count", quality.get("review_ready_count")),
            ("needs_review_count", quality.get("needs_review_count")),
            ("all_scenarios_review_ready", quality.get("all_scenarios_review_ready")),
        ]
    )
    non_execution_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("non_execution_evidence", {}).items()
    )
    contract = report.get("contract_validation_evidence", {})
    contract_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("validator", contract.get("validator")),
            ("validation_performed", contract.get("validation_performed")),
            ("contract_status", contract.get("contract_status")),
            ("validated_scenario_count", contract.get("validated_scenario_count")),
            ("validation_errors", "; ".join(str(error) for error in contract.get("validation_errors", [])) or "None"),
        ]
    )
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    note_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("validation_notes", [])
    )
    missing_items = [
        f"{item.get('scenario_id')}: {', '.join(str(missing) for missing in item.get('missing_evidence', []))}"
        for item in report.get("scenario_reviews", [])
        if item.get("missing_evidence")
    ]
    missing_list = "".join(f"<li>{html.escape(item)}</li>" for item in missing_items) or "<li>None</li>"
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day68 Offline Mock Runtime Reviewer Report Quality</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ background: #fff4d8; border: 1px solid #f0c66a; color: #765200; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day68 Offline Mock Runtime Reviewer Report Quality &amp; Evidence Trace Review</h1>
  <p class="safe">Day68 is offline mock/report-only. It reviews Day66-Day67 evidence quality and does not execute live actions, mapped tasks, APIs, voice, SSH, device access, or network configuration changes.</p>
  <h2>Overall Review Result</h2>
  <table><tbody>{quality_rows}</tbody></table>
  <h2>Scenario Evidence Trace Table</h2>
  <table>
    <thead>
      <tr>
        <th>Scenario ID</th><th>Input intent</th><th>Decision</th><th>Safety</th><th>Blocked reason</th>
        <th>Evidence ref</th><th>Contract</th><th>No live action</th><th>No mapped task</th>
        <th>No device/network change</th><th>Missing evidence</th><th>Verdict</th>
      </tr>
    </thead>
    <tbody>{scenario_rows}</tbody>
  </table>
  <h2>Missing Evidence</h2>
  <ul class="warn">{missing_list}</ul>
  <h2>Non-Execution Evidence</h2>
  <table><tbody>{non_execution_rows}</tbody></table>
  <h2>Contract Validation Confirmation</h2>
  <table><tbody>{contract_rows}</tbody></table>
  <h2>Safety Boundary Confirmation</h2>
  <ul>{boundary_items}</ul>
  <h2>Validation Notes</h2>
  <ul>{note_items}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day68_offline_mock_runtime_review(project_root: Path) -> int:
    report = build_reviewer_quality_report()
    json_path = project_root / DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_JSON
    html_path = project_root / DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_HTML
    write_json_report(report, json_path)
    write_day68_offline_mock_runtime_review_html(mask_secret_values(report), html_path)

    print(format_heading("Day68 Offline Mock Runtime Reviewer Report Quality & Evidence Trace Review"))
    print("Safety: offline mock reviewer quality / report-only")
    print(f"Review status: {report['overall_status']} / {report['review_status']}")
    print(f"Reviewed scenarios: {report['scenario_count']}")
    print(f"Reviewer-ready scenarios: {report['quality_gate_summary']['review_ready_count']}")
    print(f"Needs-review scenarios: {report['quality_gate_summary']['needs_review_count']}")
    print(f"Contract validation: {report['contract_validation_evidence']['contract_status']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["review_status"] == "REVIEW_READY":
        print(f"{format_status('PASS')} REVIEW_READY")
        print("No live action, mapped task execution, API, voice, SSH, device access, or network configuration change occurred.")
        return 0

    print(f"{format_status('WARN')} NEEDS_REVIEW")
    return 1


def write_day73_mock_ai_decision_pipeline_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    decision_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('validator_status', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_label', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('requires_manual_review', '')))}</td>"
        f"<td>{html.escape(str(item.get('blocked_reason', '')) or 'None')}</td>"
        f"<td>{html.escape(str(item.get('next_reviewer_action', '')))}</td>"
        "</tr>"
        for item in report.get("decision_records", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("Overall status", report.get("overall_status")),
            ("Reviewer status", report.get("reviewer_status")),
            ("Execution mode", report.get("execution_mode")),
            ("Scenario count", report.get("summary", {}).get("scenario_count")),
            ("Allowed to execute values", report.get("summary", {}).get("allowed_to_execute_values")),
        ]
    )
    label_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).get("decision_label_counts", {}).items()
    )
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(ref))}</code></li>"
        for ref in report.get("evidence_links_or_doc_refs", [])
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(error))}</li>" for error in report.get("validation_errors", [])
    ) or "<li>None</li>"
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day73 Mock AI Decision Pipeline</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ background: #fff4d8; border: 1px solid #f0c66a; color: #765200; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day73 Mock AI Decision Pipeline</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Decision Label Counts</h2>
  <table><tbody>{label_rows}</tbody></table>
  <h2>Mock Decision Records</h2>
  <table>
    <thead>
      <tr>
        <th>Scenario ID</th><th>Day72 validator status</th><th>Decision label</th>
        <th>Allowed to execute?</th><th>Manual review?</th><th>Blocked reason</th>
        <th>Next reviewer action</th>
      </tr>
    </thead>
    <tbody>{decision_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day73_mock_ai_decision_pipeline(project_root: Path) -> int:
    report = build_mock_ai_decision_pipeline_report()
    json_path = project_root / DAY73_MOCK_AI_DECISION_PIPELINE_JSON
    html_path = project_root / DAY73_MOCK_AI_DECISION_PIPELINE_HTML
    write_json_report(report, json_path)
    write_day73_mock_ai_decision_pipeline_html(mask_secret_values(report), html_path)

    print(format_heading("Day73 Mock AI Decision Pipeline"))
    print("Safety: deterministic mock-only decision report")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Decision records: {report['summary']['scenario_count']}")
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS":
        print(f"{format_status('PASS')} No AI API, SSH, device access, live execution, mapped task execution, config.json dependency, or network change occurred.")
        return 0

    print(f"{format_status('FAIL')} Day73 safety invariants failed.")
    return 1


def write_day74_dry_run_plan_builder_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plan_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('plan_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('source_scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_label', '')))}</td>"
        f"<td>{html.escape(str(item.get('plan_status', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_only', '')))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('planned_steps', [])))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('blocked_steps', [])))}</td>"
        f"<td>{html.escape(str(item.get('next_reviewer_action', '')))}</td>"
        "</tr>"
        for item in report.get("dry_run_plans", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("Overall status", report.get("overall_status")),
            ("Reviewer status", report.get("reviewer_status")),
            ("Execution mode", report.get("execution_mode")),
            ("Plan count", report.get("summary", {}).get("plan_count")),
            ("Allowed to execute values", report.get("summary", {}).get("allowed_to_execute_values")),
            ("Dry-run-only values", report.get("summary", {}).get("dry_run_only_values")),
        ]
    )
    status_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(count))}</td>"
        "</tr>"
        for label, count in report.get("summary", {}).get("plan_status_counts", {}).items()
    )
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(ref))}</code></li>"
        for ref in report.get("evidence_links_or_doc_refs", [])
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(error))}</li>" for error in report.get("validation_errors", [])
    ) or "<li>None</li>"
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day74 Controlled Dry-run Plan Builder</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ background: #fff4d8; border: 1px solid #f0c66a; color: #765200; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day74 Controlled Dry-run Plan Builder</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Plan Status Counts</h2>
  <table><tbody>{status_rows}</tbody></table>
  <h2>Dry-run Plans</h2>
  <table>
    <thead>
      <tr>
        <th>Plan ID</th><th>Source scenario</th><th>Decision label</th><th>Plan status</th>
        <th>Allowed to execute?</th><th>Dry-run only?</th><th>Planned preview steps</th>
        <th>Blocked steps</th><th>Next reviewer action</th>
      </tr>
    </thead>
    <tbody>{plan_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day74_dry_run_plan_builder(project_root: Path) -> int:
    report = build_dry_run_plan_builder_report()
    json_path = project_root / DAY74_DRY_RUN_PLAN_BUILDER_JSON
    html_path = project_root / DAY74_DRY_RUN_PLAN_BUILDER_HTML
    write_json_report(report, json_path)
    write_day74_dry_run_plan_builder_html(mask_secret_values(report), html_path)

    print(format_heading("Day74 Controlled Dry-run Plan Builder"))
    print("Safety: deterministic mock-only / dry-run-only plan report")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Dry-run plans: {report['summary']['plan_count']}")
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS":
        print(f"{format_status('PASS')} No AI API, SSH, device access, live execution, mapped task execution, config.json dependency, approval unlock, or network change occurred.")
        return 0

    print(f"{format_status('FAIL')} Day74 safety invariants failed.")
    return 1


def write_day75_manual_review_approval_envelope_html(
    report: Dict[str, Any], output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('envelope_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_plan_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('reviewer_signoff_state', '')))}</td>"
        f"<td>{html.escape(str(item.get('reviewer_decision', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_only', '')))}</td>"
        f"<td>{html.escape(str(item.get('execution_unlock_supported', '')))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('required_review_items', [])))}</td>"
        "</tr>"
        for item in report.get("approval_envelopes", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in [
            ("Overall status", report.get("overall_status")),
            ("Reviewer status", report.get("reviewer_status")),
            ("Execution mode", report.get("execution_mode")),
            (
                "Approval envelope count",
                report.get("summary", {}).get("approval_envelope_count"),
            ),
            (
                "Allowed to execute values",
                report.get("summary", {}).get("allowed_to_execute_values"),
            ),
            ("Dry-run-only values", report.get("summary", {}).get("dry_run_only_values")),
            (
                "Execution unlock supported values",
                report.get("summary", {}).get("execution_unlock_supported_values"),
            ),
        ]
    )
    decision_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(count))}</td>"
        "</tr>"
        for label, count in report.get("summary", {}).get("reviewer_decision_counts", {}).items()
    )
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(ref))}</code></li>"
        for ref in report.get("evidence_links_or_doc_refs", [])
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(error))}</li>" for error in report.get("validation_errors", [])
    ) or "<li>None</li>"
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day75 Manual Review Approval Envelope</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ background: #fff4d8; border: 1px solid #f0c66a; color: #765200; padding: 12px; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day75 Manual Review Approval Envelope</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Reviewer Decision Counts</h2>
  <table><tbody>{decision_rows}</tbody></table>
  <h2>Approval Envelopes</h2>
  <table>
    <thead>
      <tr>
        <th>Envelope ID</th><th>Scenario</th><th>Dry-run plan</th><th>Sign-off state</th>
        <th>Reviewer decision</th><th>Allowed to execute?</th><th>Dry-run only?</th>
        <th>Execution unlock supported?</th><th>Required review items</th>
      </tr>
    </thead>
    <tbody>{envelope_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day75_manual_review_approval_envelope(project_root: Path) -> int:
    report = build_manual_review_approval_envelope_report()
    json_path = project_root / DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_JSON
    html_path = project_root / DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_HTML
    write_json_report(report, json_path)
    write_day75_manual_review_approval_envelope_html(mask_secret_values(report), html_path)

    print(format_heading("Day75 Manual Review Approval Envelope"))
    print("Safety: deterministic mock-only / dry-run-only reviewer sign-off simulation")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Approval envelopes: {report['summary']['approval_envelope_count']}")
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS":
        print(
            f"{format_status('PASS')} No AI API, SSH, device access, live execution, "
            "mapped task execution, config.json dependency, approval unlock, dashboard "
            "action surface, or network change occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day75 safety invariants failed.")
    return 1


def write_day76_runtime_audit_trail_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('audit_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_plan_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('approval_envelope_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('evidence_chain_complete', '')))}</td>"
        f"<td>{html.escape(str(item.get('audit_result', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_only', '')))}</td>"
        f"<td>{html.escape(str(item.get('execution_unlock_supported', '')))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('reviewer_trace', [])))}</td>"
        "</tr>"
        for item in report.get("audit_records", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).items()
    )
    result_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).get("audit_result_counts", {}).items()
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("validation_errors", [])
    ) or "<li>None</li>"
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(item))}</code></li>"
        for item in report.get("evidence_links_or_doc_refs", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day76 Controlled Runtime Audit Trail</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ color: #7a4d00; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day76 Controlled Runtime Audit Trail</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Audit Result Counts</h2>
  <table><tbody>{result_rows}</tbody></table>
  <h2>Reviewer Decision Evidence Packages</h2>
  <table>
    <thead>
      <tr>
        <th>Audit ID</th><th>Scenario</th><th>Decision ID</th><th>Dry-run plan</th>
        <th>Approval envelope</th><th>Evidence chain complete?</th><th>Audit result</th>
        <th>Allowed to execute?</th><th>Dry-run only?</th><th>Execution unlock supported?</th>
        <th>Reviewer trace</th>
      </tr>
    </thead>
    <tbody>{audit_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day76_runtime_audit_trail(project_root: Path) -> int:
    report = build_runtime_audit_trail_report()
    json_path = project_root / DAY76_RUNTIME_AUDIT_TRAIL_JSON
    html_path = project_root / DAY76_RUNTIME_AUDIT_TRAIL_HTML
    write_json_report(report, json_path)
    write_day76_runtime_audit_trail_html(mask_secret_values(report), html_path)

    print(format_heading("Day76 Controlled Runtime Audit Trail"))
    print("Safety: deterministic mock-only / dry-run-only reviewer audit evidence")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Audit records: {report['summary']['audit_record_count']}")
    print(
        "Evidence chain complete values: "
        f"{report['summary']['evidence_chain_complete_values']}"
    )
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. No AI API, SSH, device access, "
            "live execution, mapped task execution, config.json dependency, approval "
            "unlock, dashboard action surface, or network change occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day76 safety invariants failed.")
    return 1


def write_day77_runtime_safety_gate_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gate_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('gate_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_plan_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('approval_envelope_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('audit_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('evidence_chain_complete', '')))}</td>"
        f"<td>{html.escape(str(item.get('runtime_gate_state', '')))}</td>"
        f"<td>{html.escape(str(item.get('gate_result', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_only', '')))}</td>"
        f"<td>{html.escape(str(item.get('execution_unlock_supported', '')))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('blocked_conditions', [])))}</td>"
        "</tr>"
        for item in report.get("safety_gate_records", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).items()
    )
    result_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).get("gate_result_counts", {}).items()
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("validation_errors", [])
    ) or "<li>None</li>"
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(item))}</code></li>"
        for item in report.get("evidence_links_or_doc_refs", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day77 Runtime Safety Gate</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ color: #7a4d00; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day77 Runtime Safety Gate</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Gate Result Counts</h2>
  <table><tbody>{result_rows}</tbody></table>
  <h2>No-Execution Gate Records</h2>
  <table>
    <thead>
      <tr>
        <th>Gate ID</th><th>Scenario</th><th>Decision ID</th><th>Dry-run plan</th>
        <th>Approval envelope</th><th>Audit ID</th><th>Evidence chain complete?</th>
        <th>Runtime gate state</th><th>Gate result</th><th>Allowed to execute?</th>
        <th>Dry-run only?</th><th>Execution unlock supported?</th><th>Blocked conditions</th>
      </tr>
    </thead>
    <tbody>{gate_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day77_runtime_safety_gate(project_root: Path) -> int:
    report = build_runtime_safety_gate_report()
    json_path = project_root / DAY77_RUNTIME_SAFETY_GATE_JSON
    html_path = project_root / DAY77_RUNTIME_SAFETY_GATE_HTML
    write_json_report(report, json_path)
    write_day77_runtime_safety_gate_html(mask_secret_values(report), html_path)

    print(format_heading("Day77 Runtime Safety Gate"))
    print("Safety: deterministic mock-only / no-execution enforcement report")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Gate records: {report['summary']['gate_record_count']}")
    print(f"Runtime gate state values: {report['summary']['runtime_gate_state_values']}")
    print(
        "Evidence chain complete values: "
        f"{report['summary']['evidence_chain_complete_values']}"
    )
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Runtime gate remains LOCKED; no AI API, "
            "SSH, device access, live execution, mapped task execution, config.json "
            "dependency, approval unlock, dashboard action surface, or network change occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day77 safety invariants failed.")
    return 1


def write_day78_runtime_safety_case_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    case_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('case_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('scenario_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('input_validation_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('decision_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_plan_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('approval_envelope_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('audit_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('gate_id', '')))}</td>"
        f"<td>{html.escape(str(item.get('evidence_chain_complete', '')))}</td>"
        f"<td>{html.escape(str(item.get('runtime_gate_state', '')))}</td>"
        f"<td>{html.escape(str(item.get('final_recommendation', '')))}</td>"
        f"<td>{html.escape(str(item.get('safety_case_result', '')))}</td>"
        f"<td>{html.escape(str(item.get('allowed_to_execute', '')))}</td>"
        f"<td>{html.escape(str(item.get('dry_run_only', '')))}</td>"
        f"<td>{html.escape(str(item.get('execution_unlock_supported', '')))}</td>"
        f"<td>{html.escape('; '.join(str(step) for step in item.get('reviewer_findings', [])))}</td>"
        "</tr>"
        for item in report.get("safety_case_records", [])
    )
    invariant_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label).replace('_', ' ').title())}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("safety_invariants", {}).items()
    )
    summary_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).items()
    )
    result_rows = "".join(
        "<tr>"
        f"<th>{html.escape(str(label))}</th>"
        f"<td>{html.escape(str(value))}</td>"
        "</tr>"
        for label, value in report.get("summary", {}).get("safety_case_result_counts", {}).items()
    )
    validation_errors = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("validation_errors", [])
    ) or "<li>None</li>"
    boundary_items = "".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("safety_boundary", [])
    )
    refs = "".join(
        f"<li><code>{html.escape(str(item))}</code></li>"
        for item in report.get("evidence_links_or_doc_refs", [])
    )
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day78 Controlled Runtime Safety Case</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
    .safe {{ background: #ecfdf3; border: 1px solid #abefc6; color: #05603a; padding: 12px; }}
    .warn {{ color: #7a4d00; }}
    code {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <h1>Day78 Controlled Runtime Safety Case</h1>
  <p class="safe">{html.escape(str(report.get("final_safety_statement", "")))}</p>
  <h2>Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Safety Case Result Counts</h2>
  <table><tbody>{result_rows}</tbody></table>
  <h2>End-to-End Reviewer Safety Case Records</h2>
  <table>
    <thead>
      <tr>
        <th>Case ID</th><th>Scenario</th><th>Input validation</th><th>Decision ID</th>
        <th>Dry-run plan</th><th>Approval envelope</th><th>Audit ID</th><th>Gate ID</th>
        <th>Evidence chain complete?</th><th>Runtime gate state</th>
        <th>Final recommendation</th><th>Safety case result</th>
        <th>Allowed to execute?</th><th>Dry-run only?</th>
        <th>Execution unlock supported?</th><th>Reviewer findings</th>
      </tr>
    </thead>
    <tbody>{case_rows}</tbody>
  </table>
  <h2>Safety Invariants</h2>
  <table><tbody>{invariant_rows}</tbody></table>
  <h2>Validation Errors</h2>
  <ul class="warn">{validation_errors}</ul>
  <h2>Safety Boundary</h2>
  <ul>{boundary_items}</ul>
  <h2>Evidence References</h2>
  <ul>{refs}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day78_runtime_safety_case(project_root: Path) -> int:
    report = build_runtime_safety_case_report()
    json_path = project_root / DAY78_RUNTIME_SAFETY_CASE_JSON
    html_path = project_root / DAY78_RUNTIME_SAFETY_CASE_HTML
    write_json_report(report, json_path)
    write_day78_runtime_safety_case_html(mask_secret_values(report), html_path)

    print(format_heading("Day78 Controlled Runtime Safety Case"))
    print("Safety: deterministic mock-only / end-to-end reviewer package")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Safety case records: {report['summary']['safety_case_record_count']}")
    print(f"Runtime gate state values: {report['summary']['runtime_gate_state_values']}")
    print(
        "Evidence chain complete values: "
        f"{report['summary']['evidence_chain_complete_values']}"
    )
    print(
        "Final recommendation values: "
        f"{report['summary']['final_recommendation_values']}"
    )
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Runtime safety case remains REVIEW_ONLY "
            "with gate state LOCKED; no AI API, SSH, device access, live execution, "
            "mapped task execution, config.json dependency, approval unlock, "
            "dashboard action surface, or network change occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day78 safety case invariants failed.")
    return 1


def _run_day79_readonly_task_contract(project_root: Path) -> int:
    report = build_readonly_task_contract_report()
    json_path, html_path = write_readonly_task_contract_reports(project_root, report)

    print(format_heading("Day79 Controlled Read-only Task Contract & Allowlist"))
    print("Safety: deterministic mock-only / dry-run-only task eligibility contract")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Contract records: {report['summary']['contract_record_count']}")
    print(
        "Read-only eligible values: "
        f"{report['summary']['readonly_eligible_values']}"
    )
    print(
        "Execution candidate values: "
        f"{report['summary']['execution_candidate_values']}"
    )
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Read-only task contract is defined; "
            "no SSH, device access, live execution, mapped task execution, approval "
            "unlock, or network change occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day79 read-only task contract invariants failed.")
    return 1


def _run_day80_readonly_execution_broker(project_root: Path) -> int:
    report = build_readonly_execution_broker_report()
    json_path, html_path = write_readonly_execution_broker_reports(project_root, report)

    print(format_heading("Day80 Read-only Execution Broker Skeleton"))
    print("Safety: deterministic mock-only / dry-run-only broker skeleton")
    print(f"Overall status: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Broker records: {report['summary']['broker_record_count']}")
    print(f"Broker statuses: {report['summary']['broker_statuses']}")
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(
        "Device connection allowed values: "
        f"{report['summary']['device_connection_allowed_values']}"
    )
    print(f"SSH allowed values: {report['summary']['ssh_allowed_values']}")
    print(f"Live command allowed values: {report['summary']['live_command_allowed_values']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Read-only broker skeleton is "
            "defined; no live command was executed, no mapped task was executed, "
            "no device was accessed, and no execution unlock occurred."
        )
        return 0

    print(f"{format_status('FAIL')} Day80 read-only execution broker invariants failed.")
    return 1


def _run_day81_broker_review_queue(project_root: Path) -> int:
    report = build_broker_review_queue_report()
    json_path, html_path = write_broker_review_queue_reports(project_root, report)

    print(format_heading("Day81 Read-only Broker Review Queue & Decision State Report"))
    print("Task name: broker-review-queue")
    print("Safety: deterministic mock-only / dry-run-only broker review queue")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Queue records count: {report['summary']['queue_record_count']}")
    print(f"Review states list: {report['summary']['review_states']}")
    print(f"Decision states list: {report['summary']['decision_states']}")
    print(f"Allowed to execute values: {report['summary']['allowed_to_execute_values']}")
    print(f"Dry-run-only values: {report['summary']['dry_run_only_values']}")
    print(
        "Execution unlock supported values: "
        f"{report['summary']['execution_unlock_supported_values']}"
    )
    print(
        "Device connection allowed values: "
        f"{report['summary']['device_connection_allowed_values']}"
    )
    print(f"SSH allowed values: {report['summary']['ssh_allowed_values']}")
    print(f"Live command allowed values: {report['summary']['live_command_allowed_values']}")
    print(
        "Mapped task execution allowed values: "
        f"{report['summary']['mapped_task_execution_allowed_values']}"
    )
    print(
        "Dashboard action allowed values: "
        f"{report['summary']['dashboard_action_allowed_values']}"
    )
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Broker review queue is "
            "report-only; no request is allowed to execute, no mapped task was "
            "executed, no device was accessed, and no dashboard action endpoint "
            "was added."
        )
        return 0

    print(f"{format_status('FAIL')} Day81 broker review queue invariants failed.")
    return 1


def _run_day82_reviewer_decision_audit_summary(project_root: Path) -> int:
    report = build_reviewer_decision_audit_summary_report()
    json_path, html_path = write_reviewer_decision_audit_summary_reports(project_root, report)
    summary = report["decision_summary"]

    print(format_heading("Day82 Reviewer Decision Audit Summary / Queue Evidence Export"))
    print("Task name: reviewer-decision-audit-summary")
    print("Safety: deterministic mock-only / dry-run-only reviewer audit evidence export")
    print(f"Result: {report['overall_status']} / {report['status']}")
    print(f"Queue records summarized: {summary['queue_record_count']}")
    print(f"Evidence exports count: {summary['evidence_export_count']}")
    print(f"Review state counts: {summary['review_state_counts']}")
    print(f"Decision state counts: {summary['decision_state_counts']}")
    print(f"allowed_to_execute: {summary['allowed_to_execute_values']}")
    print(f"dry_run_only: {summary['dry_run_only_values']}")
    print(f"execution_unlock_supported: {summary['execution_unlock_supported_values']}")
    print(f"device_connection_allowed: {summary['device_connection_allowed_values']}")
    print(f"ssh_allowed: {summary['ssh_allowed_values']}")
    print(f"live_command_allowed: {summary['live_command_allowed_values']}")
    print(f"network_change_allowed: {summary['network_change_allowed_values']}")
    print(f"ai_runtime_allowed: {summary['ai_runtime_allowed_values']}")
    print(f"dashboard_action_allowed: {summary['dashboard_action_allowed_values']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Reviewer decision audit summary "
            "is review-only; no live execution, no SSH, no device access, no AI "
            "runtime, no mapped task execution, and no dashboard action endpoint "
            "was added."
        )
        return 0

    print(f"{format_status('FAIL')} Day82 reviewer decision audit summary invariants failed.")
    return 1


def _run_day83_readonly_executor_readiness_gate(project_root: Path) -> int:
    report = build_readonly_executor_readiness_gate_report()
    json_path, html_path = write_readonly_executor_readiness_gate_reports(project_root, report)
    summary = report["summary"]

    def flag(name: str) -> str:
        return json.dumps(report[name])

    print(format_heading("Day83 Read-only Executor Readiness Gate / Controlled Runner Preflight"))
    print("Task name: readonly-executor-readiness-gate")
    print("Safety: deterministic offline / review-only readiness gate; this is not an executor")
    print(f"Result: {report['overall_status']} / {report['readiness_state']}")
    print(f"Readiness checks: {summary['readiness_checks_passed']} / {summary['readiness_check_count']}")
    print(f"Day79 contract records: {summary['day79_contract_records']}")
    print(f"Day80 broker records: {summary['day80_broker_records']}")
    print(f"Day81 queue records: {summary['day81_queue_records']}")
    print(f"Day82 evidence exports: {summary['day82_evidence_exports']}")
    print(f"Executor allowed: {flag('executor_allowed')}")
    print(f"Read-only executor candidate: {flag('readonly_executor_candidate')}")
    print(f"Live execution allowed: {flag('live_execution_allowed')}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"Device access allowed: {flag('device_access_allowed')}")
    print(f"AI runtime allowed: {flag('ai_runtime_allowed')}")
    print(f"Dashboard action allowed: {flag('dashboard_action_allowed')}")
    print(f"Mapped task execution allowed: {flag('mapped_task_execution_allowed')}")
    print(f"Approval unlock allowed: {flag('approval_unlock_allowed')}")
    print(f"Execution unlock supported: {flag('execution_unlock_supported')}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["readiness_state"] == "READINESS_REVIEW_READY":
        print(
            f"{format_status('PASS')} READINESS_REVIEW_READY. Read-only executor "
            "candidate status is review-only; no executor, live execution, SSH, "
            "device access, AI runtime, mapped task execution, dashboard action, "
            "approval unlock, or execution unlock was added."
        )
        return 0

    print(f"{format_status('FAIL')} Day83 read-only executor readiness gate invariants failed.")
    return 1


def _run_day84_readonly_executor_adapter_contract(project_root: Path) -> int:
    report = build_readonly_executor_adapter_contract_report()
    json_path, html_path = write_readonly_executor_adapter_contract_reports(project_root, report)
    summary = report["summary"]

    def flag(name: str) -> str:
        return json.dumps(report["adapter_safety_flags"][name])

    print(format_heading("Day84 Read-only Executor Adapter Interface Contract"))
    print("Task name: readonly-executor-adapter-contract")
    print("Safety: deterministic contract-only adapter boundary; this is not an executor")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Contract state: {report['contract_state']}")
    print(f"Request shapes: {summary['request_shape_count']}")
    print(f"Response shapes: {summary['response_shape_count']}")
    print(f"Capability declarations: {summary['capability_declaration_count']}")
    print(f"Evidence references: {summary['evidence_reference_count']}")
    print(f"Read-only only: {flag('read_only_only')}")
    print(f"Dry-run only: {flag('dry_run_only')}")
    print(f"Allowed to execute: {flag('allowed_to_execute')}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"Device access allowed: {flag('device_access_allowed')}")
    print(f"Live command allowed: {flag('live_command_allowed')}")
    print(f"Approval unlock supported: {flag('approval_unlock_supported')}")
    print(f"Execution unlock supported: {flag('execution_unlock_supported')}")
    print(f"AI API allowed: {flag('ai_api_allowed')}")
    print(f"Adapter implementation present: {flag('adapter_implementation_present')}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["reviewer_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Read-only executor adapter "
            "contract is locked as review-only; no executor implementation, SSH, "
            "device access, live command, AI API, approval unlock, or execution "
            "unlock was added."
        )
        return 0

    print(f"{format_status('FAIL')} Day84 read-only executor adapter contract invariants failed.")
    return 1


def _run_day85_mock_adapter_evidence_binding(project_root: Path) -> int:
    report = build_mock_adapter_evidence_binding_report()
    json_path, html_path = write_mock_adapter_evidence_binding_reports(project_root, report)
    summary = report["traceability_summary"]
    flags = report["safety_invariants"]

    def flag(name: str) -> str:
        return json.dumps(flags[name])

    print(format_heading("Day85 Mock Adapter + Evidence Binding"))
    print("Task name: mock-adapter-evidence-binding")
    print("Safety: deterministic mock-only adapter fixture; evidence-bound and non-executing")
    print(f"Result: {report['overall_status']} / {report['review_status']}")
    print(f"Final recommendation: {report['final_recommendation']}")
    print(f"Adapter records: {summary['adapter_record_count']}")
    print(f"Evidence bindings: {summary['evidence_binding_count']}")
    print(f"Compatible adapters: {summary['compatible_adapter_count']}")
    print(f"Blocked adapters: {summary['blocked_adapter_count']}")
    print("Compatibility Matrix: internal Day85/Day86 validation only")
    print(f"Allowed to execute: {flag('allowed_to_execute')}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"Device access allowed: {flag('device_access_allowed')}")
    print(f"Live command allowed: {flag('live_command_allowed')}")
    print(f"Approval unlock supported: {flag('approval_unlock_supported')}")
    print(f"Execution unlock supported: {flag('execution_unlock_supported')}")
    print(f"AI API allowed: {flag('ai_api_allowed')}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and report["review_status"] == "REVIEW_READY":
        print(
            f"{format_status('PASS')} REVIEW_READY. Mock adapter evidence binding "
            "is review-only; Compatibility Matrix stayed internal validation, "
            "and no SSH, device, live command, AI API, approval unlock, or "
            "execution unlock path was added."
        )
        return 0

    print(f"{format_status('FAIL')} Day85 mock adapter evidence binding invariants failed.")
    return 1


def _run_day86_controlled_runner_harness(project_root: Path) -> int:
    report = build_controlled_runner_harness_report()
    json_path, html_path = write_controlled_runner_harness_reports(project_root, report)
    summary = report["summary"]
    flags = report["safety_invariants"]

    def flag(name: str) -> str:
        return json.dumps(flags[name])

    print(format_heading("Day86 Controlled Runner Harness + Safety Regression"))
    print("Task name: controlled-runner-harness")
    print("Safety: deterministic runner-level safety regression; dry-run/review-only")
    print(f"Result: {report['overall_status']} / {report['review_status']}")
    print(f"Runner mode: {report['runner_mode']}")
    print(f"Final recommendation: {report['final_recommendation']}")
    print(f"Total scenarios: {summary['total_scenarios']}")
    print(f"Failed scenarios: {summary['failed_scenarios']}")
    print(f"allowed_to_execute={flag('allowed_to_execute')}")
    print(f"ssh_allowed={flag('ssh_allowed')}")
    print(f"live_command_allowed={flag('live_command_allowed')}")
    print(f"mapped_task_executed={flag('mapped_task_executed')}")
    print(f"Execution unlock supported: {flag('execution_unlock_supported')}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["review_status"] == "REVIEW_ONLY"
        and report["final_recommendation"] == "REVIEW_ONLY"
    ):
        print(
            f"{format_status('PASS')} REVIEW_ONLY. Controlled runner harness "
            "is dry-run-only; adapter compatibility and report generation did "
            "not enable SSH, live command execution, mapped task execution, or "
            "execution unlock."
        )
        return 0

    print(f"{format_status('FAIL')} Day86 controlled runner harness safety regression failed.")
    return 1


def _run_day87_readonly_executor_phase_gate_review(project_root: Path) -> int:
    report = build_readonly_executor_phase_gate_review()
    json_path, html_path = write_readonly_executor_phase_gate_review_reports(project_root, report)

    def flag(name: str) -> str:
        return json.dumps(report[name])

    passed_checks = sum(1 for check in report["gate_checks"] if check["status"] == "PASS")
    print(format_heading("Day87 Read-only Executor Phase Gate Review"))
    print("Task name: readonly-executor-phase-gate-review")
    print("Safety: deterministic phase gate review only; no real adapter design or implementation")
    print(f"Result: {report['phase_gate_status']} / {report['phase_gate_recommendation']}")
    print(f"Reviewed days: {', '.join(report['reviewed_days'])}")
    print(f"Gate checks: {passed_checks} / {len(report['gate_checks'])}")
    print(f"Execution allowed: {flag('execution_allowed')}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"Live command allowed: {flag('live_command_allowed')}")
    print(f"Write command allowed: {flag('write_command_allowed')}")
    print(f"Device connection allowed: {flag('device_connection_allowed')}")
    print(f"Real adapter design allowed: {flag('real_adapter_design_allowed')}")
    print(f"Real adapter implementation allowed: {flag('real_adapter_implementation_allowed')}")
    print(f"Next phase: Day88 {report['allowed_next_step']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["phase_gate_status"] == "PASS"
        and report["phase_gate_recommendation"] == "DESIGN_ONLY"
        and report["execution_allowed"] is False
        and report["real_adapter_design_allowed"] is True
        and report["real_adapter_implementation_allowed"] is False
    ):
        print(
            f"{format_status('PASS')} DESIGN_ONLY. Reviewed Day83, Day84, Day85, "
            "and Day86; Day88 may start the design draft only, while execution "
            "and real adapter implementation remain blocked."
        )
        return 0

    print(f"{format_status('FAIL')} Day87 read-only executor phase gate review failed.")
    return 1


def _run_day88_real_readonly_executor_adapter_design(project_root: Path) -> int:
    report = build_real_readonly_executor_adapter_design_report()
    json_path, html_path = write_real_readonly_executor_adapter_design_reports(project_root, report)

    def flag(name: str) -> str:
        return json.dumps(report[name])

    allowlist = report["command_allowlist_design"]
    print(format_heading("Day88 Real Read-only Executor Adapter Design Draft"))
    print("Task name: readonly-executor-adapter-design")
    print("Safety: deterministic design-only adapter draft; no real adapter implementation")
    print(f"Result: {report['overall_status']} / {report['phase_state']}")
    print(f"Allowlist policy: {allowlist['policy_type']}")
    print(f"Allowlisted command examples: {len(allowlist['commands'])}")
    print(f"Forbidden mutation tokens: {len(report['forbidden_command_policy']['tokens'])}")
    print(f"Execution supported: {flag('execution_supported')}")
    print(f"SSH supported: {flag('ssh_supported')}")
    print(f"RouterOS connection supported: {flag('routeros_connection_supported')}")
    print(f"Live command supported: {flag('live_command_supported')}")
    print(f"Execution unlock supported: {flag('execution_unlock_supported')}")
    print(f"Dashboard action button supported: {flag('dashboard_execute_button_supported')}")
    print(f"Current adapter state: {report['error_contract']['day88_current_error_code']}")
    print(f"Timeout retry supported: {json.dumps(report['timeout_contract']['retry_supported'])}")
    print(f"Day89 handoff: {report['day89_handoff']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["phase_state"] == "DESIGN_ONLY"
        and report["execution_supported"] is False
        and report["ssh_supported"] is False
        and report["routeros_connection_supported"] is False
        and report["live_command_supported"] is False
        and report["execution_unlock_supported"] is False
        and report["dashboard_execute_button_supported"] is False
    ):
        print(
            f"{format_status('PASS')} DESIGN_ONLY. Day88 defines the future adapter "
            "contract and safety boundary only; real execution remains locked."
        )
        return 0

    print(f"{format_status('FAIL')} Day88 real read-only executor adapter design failed.")
    return 1


def _run_day89_real_adapter_safety_boundary_spec(project_root: Path) -> int:
    report = build_real_adapter_safety_boundary_spec_report()
    json_path, html_path = write_real_adapter_safety_boundary_spec_reports(project_root, report)

    def flag(name: str) -> str:
        return json.dumps(report[name])

    print(format_heading("Day89 Real Adapter Safety Boundary Spec"))
    print("Task name: real-adapter-safety-boundary-spec")
    print("Safety: deterministic design-only boundary lock; no real adapter implementation")
    print(f"Result: {report['status']} / {report['phase']}")
    print(f"safety_boundary_locked={report['safety_boundary_locked']}")
    print(f"implementation_allowed={report['implementation_allowed']}")
    print(f"live_device_access_allowed={report['live_device_access_allowed']}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"Config change allowed: {flag('config_change_allowed')}")
    print(f"Command execution allowed: {flag('command_execution_allowed')}")
    print(f"Reviewer decision required: {flag('reviewer_decision_required')}")
    print(f"Blocked capabilities: {len(report['blocked_capabilities'])}")
    print(f"Allowed spec-level capabilities: {len(report['allowed_capabilities'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["status"] == "PASS"
        and report["phase"] == "DESIGN_ONLY"
        and report["safety_boundary_locked"] is True
        and report["implementation_allowed"] is False
        and report["live_device_access_allowed"] is False
        and report["ssh_allowed"] is False
        and report["config_change_allowed"] is False
        and report["command_execution_allowed"] is False
    ):
        print(
            f"{format_status('PASS')} DESIGN_ONLY. Day89 locks the safety boundary "
            "before any real adapter implementation; live access and command "
            "execution remain blocked."
        )
        return 0

    print(f"{format_status('FAIL')} Day89 real adapter safety boundary spec failed.")
    return 1


def _run_day90_real_adapter_implementation_plan(project_root: Path) -> int:
    report = build_real_adapter_implementation_plan_report(project_root)
    json_path, html_path = write_real_adapter_implementation_plan_reports(project_root, report)

    def flag(name: str) -> str:
        return json.dumps(report[name])

    print(format_heading("Day90 Real Adapter Implementation Plan"))
    print("Task name: real-adapter-implementation-plan")
    print("Safety: deterministic planning-only decision; no real adapter implementation")
    print("Scope: PLANNING_ONLY")
    print(f"Result: {report['status']} / {report['readiness_level']}")
    print(f"Decision: {report['decision']}")
    print(f"Decision reason: {report['decision_reason']}")
    print(f"Adapter implementation allowed: {flag('adapter_implementation_allowed')}")
    print(f"Live device access allowed: {flag('live_device_access_allowed')}")
    print(f"SSH allowed: {flag('ssh_allowed')}")
    print(f"RouterOS command execution allowed: {flag('routeros_command_execution_allowed')}")
    print(f"Non-GO blockers: {len(report['non_go_blockers'])}")
    print(f"Evidence chain items: {len(report['evidence_chain'])}")
    print(f"Recommended Day91 positioning: {report['recommended_day91_positioning']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["status"] == "PASS"
        and report["scope"] == "planning_only"
        and report["decision"] in {"GO", "CONDITIONAL_GO", "NO_GO"}
        and report["adapter_implementation_allowed"] is False
        and report["live_device_access_allowed"] is False
        and report["ssh_allowed"] is False
        and report["routeros_command_execution_allowed"] is False
    ):
        print(
            f"{format_status('PASS')} PLANNING_ONLY. Day90 produced an "
            "implementation-entry decision without live adapter behavior."
        )
        return 0

    print(f"{format_status('FAIL')} Day90 real adapter implementation plan failed validation.")
    return 1


def _run_day91_real_adapter_safety_scaffold(project_root: Path) -> int:
    report = build_day91_real_adapter_safety_scaffold()
    json_path, html_path = write_day91_real_adapter_safety_scaffold_reports(project_root, report)
    invariants = report["invariants"]

    def flag(name: str) -> str:
        return json.dumps(invariants[name])

    print(format_heading("Day91 Real Adapter Safety Scaffold"))
    print("Task name: real-adapter-safety-scaffold")
    print("Safety: deterministic scaffold-only evidence; no real adapter or live-read")
    print(f"Result: {report['overall_decision']} / {report['status']}")
    print(f"Day90 gate: {report['day90_gate']['decision']} only")
    print(f"Dangerous actions denied: {len(report['dangerous_actions'])}")
    print(f"Read-only candidates future-only: {len(report['read_only_candidates'])}")
    print(f"fail_closed_default: {flag('fail_closed_default')}")
    print(f"live_read_allowed: {flag('live_read_allowed')}")
    print(f"write_allowed: {flag('write_allowed')}")
    print(f"raw_command_allowed: {flag('raw_command_allowed')}")
    print(f"credential_required: {flag('credential_required')}")
    print(f"transport_required: {flag('transport_required')}")
    print(f"real_device_contact_allowed: {flag('real_device_contact_allowed')}")
    print(f"Next required days: {', '.join(item['day'] for item in report['next_required_days'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_decision"] == "PASS"
        and report["status"] == "SCAFFOLD_ONLY"
        and report["day90_gate"]["decision"] == "CONDITIONAL_GO"
        and all(item["decision"] == "DENY" and item["allowed"] is False for item in report["dangerous_actions"])
        and all(
            item["execution_state"] == "NOT_EXECUTABLE"
            and item["guard_state"] == "PENDING_GUARD"
            and item["scope_state"] == "FUTURE_ONLY"
            for item in report["read_only_candidates"]
        )
        and invariants["live_read_allowed"] is False
        and invariants["write_allowed"] is False
        and invariants["raw_command_allowed"] is False
        and invariants["credential_required"] is False
        and invariants["transport_required"] is False
        and invariants["real_device_contact_allowed"] is False
    ):
        print(
            f"{format_status('PASS')} SCAFFOLD_ONLY. Day91 denied dangerous "
            "actions, kept read-only candidates future-only, and left live-read blocked."
        )
        return 0

    print(f"{format_status('FAIL')} Day91 real adapter safety scaffold failed validation.")
    return 1


def _run_day92_real_adapter_executable_guards(project_root: Path) -> int:
    report = build_day92_real_adapter_executable_guards_report()
    json_path, html_path = write_day92_real_adapter_executable_guards_reports(project_root, report)

    print(format_heading("Day92 Real Adapter Executable Guards"))
    print("Task name: real-adapter-executable-guards")
    print("Safety: offline deterministic executable guard; no real adapter, SSH, socket, or subprocess")
    print(f"Result: {report['status']} / {report['phase']}")
    print(f"Total scenarios: {report['total_scenarios']}")
    print(f"Allowed count: {report['allowed_scenarios']}")
    print(f"Rejected count: {report['rejected_scenarios']}")
    print(f"adapter_invoked_for_rejected = {report['adapter_invoked_for_rejected']}")
    print(f"Evidence report JSON: {_relative_to_project(project_root, json_path)}")
    print(f"Evidence report HTML: {_relative_to_project(project_root, html_path)}")

    if (
        report["status"] == "PASS"
        and report["phase"] == "GUARD_ENFORCED"
        and report["no_real_device_access"] is True
        and report["no_ssh"] is True
        and report["no_subprocess"] is True
        and report["no_socket"] is True
        and report["no_real_adapter"] is True
        and report["adapter_implementation_added"] is False
        and report["rejected_adapter_invocations"] == 0
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} GUARD_ENFORCED. Day92 rejected unsafe "
            "requests before executor invocation and allowed only simulated read-only cases."
        )
        return 0

    print(f"{format_status('FAIL')} Day92 real adapter executable guards failed validation.")
    return 1


def _run_day93_guarded_fake_adapter_contract(project_root: Path) -> int:
    report = run_guarded_fake_adapter_contract()
    json_path, html_path = write_guarded_fake_adapter_contract_reports(project_root, report)

    print(format_heading("Day93 Guarded Fake Adapter Contract"))
    print("Task name: guarded-fake-adapter-contract")
    print("Mode: FAKE_ADAPTER_ONLY")
    print("Safety: fake adapter only; no real device access, SSH, config.json read, or live execution")
    print(f"Result: {report['overall_status']} / {report['mode']}")
    print(f"Total scenarios: {report['total_scenarios']}")
    print(f"Allowed count: {report['allowed_count']}")
    print(f"Rejected count: {report['rejected_count']}")
    print(f"Fake adapter invocations: {report['fake_adapter_invocations']}")
    print(f"Rejected adapter invocations = {report['rejected_adapter_invocations']}")
    print(f"Real adapter invocations = {report['real_adapter_invocations']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["mode"] == "FAKE_ADAPTER_ONLY"
        and report["allowed_count"] > 0
        and report["rejected_count"] > 0
        and report["fake_adapter_invocations"] == report["allowed_count"]
        and report["rejected_adapter_invocations"] == 0
        and report["real_adapter_invocations"] == 0
        and report["guard_ordering_violations"] == 0
        and report["safety_violations"] == 0
        and report["audit_chain_complete"] is True
        and report["adapter_boundary_verified"] is True
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} FAKE_ADAPTER_ONLY. Day93 verified guard-first "
            "ordering and fake-adapter-only boundary invocation evidence."
        )
        return 0

    print(f"{format_status('FAIL')} Day93 guarded fake adapter contract failed validation.")
    return 1


def _run_day94_adapter_boundary_regression_matrix(project_root: Path) -> int:
    report = run_adapter_boundary_regression_matrix()
    json_path, html_path = write_adapter_boundary_regression_matrix_reports(project_root, report)
    summary = report["summary"]

    print(format_heading("Day94 Adapter Boundary Regression Matrix"))
    print("Task name: adapter-boundary-regression-matrix")
    print("Mode: FAKE_ADAPTER_BOUNDARY_EVIDENCE_ONLY")
    print("Safety: fake-adapter-only; no real device access, SSH, real adapter, or live execution")
    print(f"Result: {report['overall_status']} / {report['mode']}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Allowed rows: {summary['allowed_rows']}")
    print(f"Rejected rows: {summary['rejected_rows']}")
    print(f"Fake adapter invocations: {summary['fake_adapter_invocations']}")
    print(f"adapter_invoked_for_rejected = {summary['adapter_invoked_for_rejected']}")
    print(f"real_adapter_invocations = {summary['real_adapter_invocations']}")
    print(f"live_execution_invocations = {summary['live_execution_invocations']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and summary["total_rows"] >= 12
        and summary["failed_rows"] == 0
        and summary["adapter_invoked_for_rejected"] == 0
        and summary["real_adapter_invocations"] == 0
        and summary["live_execution_invocations"] == 0
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} FAKE_ADAPTER_BOUNDARY_EVIDENCE_ONLY. "
            "Day94 regression matrix preserved adapter boundary invariants."
        )
        return 0

    print(f"{format_status('FAIL')} Day94 adapter boundary regression matrix failed validation.")
    return 1


def _run_day95_adapter_result_normalization(project_root: Path) -> int:
    report = run_adapter_result_normalization()
    json_path, html_path = write_adapter_result_normalization_reports(project_root, report)
    summary = report["summary"]

    print(format_heading("Day95 Adapter Result Normalization"))
    print("Task name: adapter-result-normalization")
    print("Phase: FAKE_ONLY_EVIDENCE_HARDENING")
    print("Safety: fake-only; read-only report evidence; no SSH, real adapter, device access, or live execution")
    print(f"Result: {report['overall_status']} / {report['phase']}")
    print(f"Total scenarios: {summary['total_scenarios']}")
    print(f"Allowed count: {summary['allowed_count']}")
    print(f"Rejected count: {summary['rejected_count']}")
    print(f"Normalized result count: {summary['normalized_result_count']}")
    print(f"Fake adapter result count: {summary['fake_adapter_result_count']}")
    print(f"real_adapter_result_count = {summary['real_adapter_result_count']}")
    print(f"live_execution_result_count = {summary['live_execution_result_count']}")
    print(f"result_status_source = {summary['result_status_source']}")
    print(f"evidence_chain_complete = {json.dumps(summary['evidence_chain_complete'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and summary["total_scenarios"] == 5
        and summary["allowed_count"] == 2
        and summary["rejected_count"] == 3
        and summary["normalized_result_count"] == summary["allowed_count"]
        and summary["fake_adapter_result_count"] == summary["allowed_count"]
        and summary["real_adapter_result_count"] == 0
        and summary["live_execution_result_count"] == 0
        and summary["rejected_with_adapter_result"] == 0
        and summary["result_status_source"] == "deterministic_fake_boundary"
        and summary["evidence_chain_complete"] is True
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} FAKE_ONLY_EVIDENCE_HARDENING. "
            "Day95 normalized deterministic fake adapter results and kept rejected scenarios result-free."
        )
        return 0

    print(f"{format_status('FAIL')} Day95 adapter result normalization failed validation.")
    return 1


def _run_day96_readonly_output_parser_prototype(project_root: Path) -> int:
    report = build_day96_parser_report()
    json_path, html_path = write_day96_parser_reports(project_root, report)
    summary = report["parsed_records_summary"]

    print(format_heading("Day96 Read-only Output Parser Prototype"))
    print("Task name: readonly-output-parser-prototype")
    print("Phase: PARSER_PROTOTYPE_READY")
    print("Safety: parser-only over Day95 normalized fake adapter simulated output; no RouterOS, SSH, device access, live-read, adapter fallback, or runner live path")
    print(f"Result: {report['overall_status']} / {report['phase']}")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Parsed cases: {summary['parsed_case_count']}")
    print(f"Review-needed cases: {summary['review_needed_case_count']}")
    print(f"Unsupported cases: {summary['unsupported_case_count']}")
    print(f"Parsed records: {summary['parsed_record_count']}")
    print(f"live_fallback_attempts = {summary['live_fallback_attempts']}")
    print(f"adapter_fallback_attempts = {summary['adapter_fallback_attempts']}")
    print(f"device_access_attempts = {summary['device_access_attempts']}")
    print(f"live_read_enabled = {json.dumps(report['safety_boundary']['live_read_enabled'])}")
    print(f"ssh_enabled = {json.dumps(report['safety_boundary']['ssh_enabled'])}")
    print(f"routeros_enabled = {json.dumps(report['safety_boundary']['routeros_enabled'])}")
    print(f"device_access_enabled = {json.dumps(report['safety_boundary']['device_access_enabled'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and summary["parsed_case_count"] >= 2
        and summary["review_needed_case_count"] >= 2
        and summary["unsupported_case_count"] >= 1
        and summary["live_fallback_attempts"] == 0
        and summary["adapter_fallback_attempts"] == 0
        and summary["device_access_attempts"] == 0
        and report["safety_boundary"]["live_read_enabled"] is False
        and report["safety_boundary"]["ssh_enabled"] is False
        and report["safety_boundary"]["routeros_enabled"] is False
        and report["safety_boundary"]["device_access_enabled"] is False
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} PARSER_PROTOTYPE_READY. "
            "Day96 parsed fake simulated output without live-read or fallback."
        )
        return 0

    print(f"{format_status('FAIL')} Day96 read-only output parser prototype failed validation.")
    return 1


def _run_day97_parser_evidence_quality(project_root: Path) -> int:
    report = build_day97_parser_evidence_quality_report()
    json_path, html_path = write_day97_parser_evidence_quality_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day97 Parser Evidence Quality"))
    print("Task name: parser-evidence-quality")
    print("Phase: HARDENED")
    print("Safety: parser-only static fake cases; no SSH, live-read, RouterOS execution, writes, mapped task execution, approval unlock, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Parser-supported count: {summary['parser_supported_count']}")
    print(f"Unsupported/degraded count: {summary['unsupported_degraded_count']}")
    print(f"Unsafe flag count: {summary['unsafe_flag_count']}")
    print(f"overall_status = {summary['overall_status']}")
    print(f"reviewer_status = {summary['reviewer_status']}")
    print(f"failed_execution_count = {summary['failed_execution_count']}")
    print(f"live_read_allowed = {json.dumps(invariants['live_read_allowed'])}")
    print(f"ssh_allowed = {json.dumps(invariants['ssh_allowed'])}")
    print(f"write_allowed = {json.dumps(invariants['write_allowed'])}")
    print(f"command_execution_allowed = {json.dumps(invariants['command_execution_allowed'])}")
    print(f"approval_unlock_supported = {json.dumps(invariants['approval_unlock_supported'])}")
    print(f"mapped_task_execution_allowed = {json.dumps(invariants['mapped_task_execution_allowed'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] in {"REVIEW_READY", "HARDENED"}
        and summary["total_cases"] >= 14
        and summary["unsupported_degraded_count"] >= 13
        and summary["unsafe_flag_count"] == 0
        and summary["failed_execution_count"] == 0
        and all(invariants[flag] is False for flag in (
            "live_read_allowed",
            "ssh_allowed",
            "write_allowed",
            "command_execution_allowed",
            "raw_command_allowed",
            "device_contact_allowed",
            "approval_unlock_supported",
            "mapped_task_execution_allowed",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} {report['reviewer_status']}. "
            "Day97 hardened parser evidence quality without execution or live fallback."
        )
        return 0

    print(f"{format_status('FAIL')} Day97 parser evidence quality hardening failed validation.")
    return 1


def _run_day98_parser_classification_matrix(project_root: Path) -> int:
    report = build_parser_classification_matrix()
    json_path, html_path = write_parser_classification_matrix_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day98 Parser Classification Matrix"))
    print("Task name: parser-classification-matrix")
    print("Phase: TRACEABILITY_HARDENED")
    print("Safety: parser-only static Day96/Day97 samples; no SSH, live-read, RouterOS execution, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Classifications: {', '.join(summary['classification_values'])}")
    print(f"Trace complete count: {summary['trace_complete_count']}")
    print(f"Trace review required count: {summary['trace_review_required_count']}")
    print(f"Unsupported reasons complete: {json.dumps(summary['unsupported_reasons_complete'])}")
    print(f"executable_allowed_count = {summary['executable_allowed_count']}")
    print(f"reviewer_action_missing_count = {summary['reviewer_action_missing_count']}")
    print(f"safety_invariant_missing_count = {summary['safety_invariant_missing_count']}")
    print(f"external_runtime_dependency_count = {summary['external_runtime_dependency_count']}")
    print(f"executable_allowed = {json.dumps(invariants['executable_allowed'])}")
    print(f"live_read_allowed = {json.dumps(invariants['live_read_allowed'])}")
    print(f"ssh_allowed = {json.dumps(invariants['ssh_allowed'])}")
    print(f"routeros_execution_allowed = {json.dumps(invariants['routeros_execution_allowed'])}")
    print(f"command_execution_allowed = {json.dumps(invariants['command_execution_allowed'])}")
    print(f"approval_unlock_supported = {json.dumps(invariants['approval_unlock_supported'])}")
    print(f"dashboard_action_allowed = {json.dumps(invariants['dashboard_action_allowed'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "TRACEABILITY_READY"
        and summary["total_rows"] >= 7
        and summary["required_categories_present"] is True
        and summary["all_trace_statuses_valid"] is True
        and summary["unsupported_reasons_complete"] is True
        and summary["executable_allowed_count"] == 0
        and summary["reviewer_action_missing_count"] == 0
        and summary["safety_invariant_missing_count"] == 0
        and summary["external_runtime_dependency_count"] == 0
        and all(invariants[flag] is False for flag in (
            "executable_allowed",
            "live_read_allowed",
            "ssh_allowed",
            "routeros_execution_allowed",
            "device_contact_allowed",
            "command_execution_allowed",
            "approval_unlock_supported",
            "dashboard_action_allowed",
            "external_runtime_state_required",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} TRACEABILITY_READY. "
            "Day98 linked parser classifications to reviewer actions without execution or live fallback."
        )
        return 0

    print(f"{format_status('FAIL')} Day98 parser classification matrix failed validation.")
    return 1


def _run_day99_parser_evidence_coverage_audit(project_root: Path) -> int:
    report = build_parser_evidence_coverage_audit_report()
    json_path, html_path = write_parser_evidence_coverage_audit_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day99 Parser Evidence Coverage / Sample Gap Audit"))
    print("Task name: parser-evidence-coverage-audit")
    print("Phase: COVERAGE_AUDIT_READY")
    print("Safety: report-only Day96-Day98 coverage audit; no parser expansion, adapter path, broker path, SSH, live device path, RouterOS execution, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Total coverage rows: {summary['total_coverage_rows']}")
    print(f"Covered count: {summary['covered_count']}")
    print(f"Under-covered count: {summary['under_covered_count']}")
    print(f"under_covered_allowed = {json.dumps(summary['under_covered_allowed'])}")
    print(f"blocking_gap_count = {summary['blocking_gap_count']}")
    print(f"source_report_fail_count = {summary['source_report_fail_count']}")
    print(f"runtime_violation_count = {summary['runtime_violation_count']}")
    print(f"ready_for_day100_review = {json.dumps(summary['ready_for_day100_review'])}")
    print(f"execution_allowed = {json.dumps(invariants['execution_allowed'])}")
    print(f"adapter_path_allowed = {json.dumps(invariants['adapter_path_allowed'])}")
    print(f"broker_path_allowed = {json.dumps(invariants['broker_path_allowed'])}")
    print(f"ssh_allowed = {json.dumps(invariants['ssh_allowed'])}")
    print(f"live_device_path_allowed = {json.dumps(invariants['live_device_path_allowed'])}")
    print(f"routeros_execution_allowed = {json.dumps(invariants['routeros_execution_allowed'])}")
    print(f"command_execution_allowed = {json.dumps(invariants['command_execution_allowed'])}")
    print(f"dashboard_action_allowed = {json.dumps(invariants['dashboard_action_allowed'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "COVERAGE_REVIEW_READY"
        and summary["required_coverage_areas_present"] is True
        and summary["under_covered_allowed"] is True
        and summary["blocking_gap_count"] == 0
        and summary["source_report_fail_count"] == 0
        and summary["runtime_violation_count"] == 0
        and summary["ready_for_day100_review"] is True
        and all(invariants[flag] is False for flag in (
            "execution_allowed",
            "adapter_path_allowed",
            "broker_path_allowed",
            "ssh_allowed",
            "live_device_path_allowed",
            "routeros_execution_allowed",
            "command_execution_allowed",
            "dashboard_action_allowed",
            "approval_unlock_supported",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} COVERAGE_REVIEW_READY. "
            "Day99 audited parser evidence coverage and sample gaps without execution or parser expansion."
        )
        return 0

    print(f"{format_status('FAIL')} Day99 parser evidence coverage audit failed validation.")
    return 1


def _run_day100_parser_phase_gate_review(project_root: Path) -> int:
    report = build_parser_phase_gate_review_report()
    json_path, html_path = write_parser_phase_gate_review_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day100 Parser Phase Gate Review / Readiness Decision"))
    print("Task name: parser-phase-gate-review")
    print("Phase: PARSER_PHASE_GATE_REVIEW")
    print("Safety: report-only Day96-Day99 parser evidence grading; no broker, executor, adapter invocation, SSH, live access, RouterOS execution, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Final readiness decision: {summary['final_readiness_decision']}")
    print(f"Total decision rows: {summary['total_decision_rows']}")
    print(f"ADVANCE_READY count: {summary['advance_ready_count']}")
    print(f"REVIEW_ONLY count: {summary['review_only_count']}")
    print(f"UNDER_COVERED count: {summary['under_covered_count']}")
    print(f"BLOCKED count: {summary['blocked_count']}")
    print(f"source_report_fail_count = {summary['source_report_fail_count']}")
    print(f"source_runtime_violation_count = {summary['source_runtime_violation_count']}")
    print(f"safety_violation_count = {summary['safety_violation_count']}")
    print(f"broker_boundary_allowed = {json.dumps(invariants['broker_boundary_allowed'])}")
    print(f"execution_allowed = {json.dumps(invariants['execution_allowed'])}")
    print(f"adapter_invocation_allowed = {json.dumps(invariants['adapter_invocation_allowed'])}")
    print(f"executor_invocation_allowed = {json.dumps(invariants['executor_invocation_allowed'])}")
    print(f"ssh_allowed = {json.dumps(invariants['ssh_allowed'])}")
    print(f"live_access_allowed = {json.dumps(invariants['live_access_allowed'])}")
    print(f"parser_outputs_are_review_data_only = {json.dumps(summary['parser_outputs_are_review_data_only'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "PHASE_GATE_REVIEW_READY"
        and summary["total_decision_rows"] > 0
        and summary["blocked_count"] == 0
        and summary["source_report_fail_count"] == 0
        and summary["source_runtime_violation_count"] == 0
        and summary["safety_violation_count"] == 0
        and summary["parser_outputs_are_review_data_only"] is True
        and all(invariants[flag] is False for flag in (
            "broker_boundary_allowed",
            "execution_allowed",
            "adapter_invocation_allowed",
            "executor_invocation_allowed",
            "ssh_allowed",
            "live_access_allowed",
            "routeros_execution_allowed",
            "command_execution_allowed",
            "dashboard_action_allowed",
            "approval_unlock_supported",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} PHASE_GATE_REVIEW_READY. "
            "Day100 graded parser evidence without broker, executor, adapter, SSH, or live access."
        )
        return 0

    print(f"{format_status('FAIL')} Day100 parser phase gate review failed validation.")
    return 1


def _run_day101_parser_evidence_closure_plan(project_root: Path) -> int:
    report = build_parser_evidence_closure_plan_report()
    json_path, html_path = write_parser_evidence_closure_plan_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day101 Parser Evidence Closure Plan"))
    print("Task name: parser-evidence-closure-plan")
    print("Phase: PARSER_EVIDENCE_CLOSURE_PLANNING")
    print("Safety: report-only Day100 parser evidence closure planning; no broker handoff, parser gate release, executor, adapter invocation, SSH, live access, RouterOS execution, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Closure item count: {summary['closure_item_count']}")
    print(f"Blocked category count: {summary['blocked_category_count']}")
    print(f"UNDER_COVERED category count: {summary['under_covered_category_count']}")
    print(f"REVIEW_ONLY category count: {summary['review_only_category_count']}")
    print(f"Recommended next action count: {summary['recommended_next_action_count']}")
    print(f"Recommended sequence: {' -> '.join(summary['recommended_next_days'])}")
    print(f"Next phase gate: {report['next_phase_gate']}")
    print(f"parser_ready_for_broker = {json.dumps(report['parser_ready_for_broker'])}")
    print(f"broker_handoff_allowed = {json.dumps(report['broker_handoff_allowed'])}")
    print(f"execution_allowed = {json.dumps(report['execution_allowed'])}")
    print(f"live_device_access_allowed = {json.dumps(report['live_device_access_allowed'])}")
    print(f"ssh_allowed = {json.dumps(report['ssh_allowed'])}")
    print(f"openai_api_allowed = {json.dumps(report['openai_api_allowed'])}")
    print(f"evidence_closure_required = {json.dumps(report['evidence_closure_required'])}")
    print(f"phase_gate_rerun_required = {json.dumps(report['phase_gate_rerun_required'])}")
    print(f"broker_boundary_opened = {json.dumps(invariants['broker_boundary_opened'])}")
    print(f"broker_connection_attempted = {json.dumps(invariants['broker_connection_attempted'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "EVIDENCE_CLOSURE_PLAN_READY"
        and summary["closure_item_count"] > 0
        and summary["blocked_category_count"] == summary["closure_item_count"]
        and summary["under_covered_category_count"] > 0
        and summary["review_only_category_count"] > 0
        and summary["recommended_next_days"] == ["Day102", "Day103", "Day104", "Day105"]
        and report["parser_ready_for_broker"] is False
        and report["broker_handoff_allowed"] is False
        and report["execution_allowed"] is False
        and report["live_device_access_allowed"] is False
        and report["ssh_allowed"] is False
        and report["openai_api_allowed"] is False
        and report["evidence_closure_required"] is True
        and report["phase_gate_rerun_required"] is True
        and all(invariants[flag] is False for flag in (
            "parser_ready_for_broker",
            "broker_handoff_allowed",
            "execution_allowed",
            "adapter_invocation_allowed",
            "executor_invocation_allowed",
            "ssh_allowed",
            "live_device_access_allowed",
            "live_access_allowed",
            "routeros_execution_allowed",
            "command_execution_allowed",
            "dashboard_action_allowed",
            "approval_unlock_supported",
            "openai_api_allowed",
            "voice_runtime_allowed",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} EVIDENCE_CLOSURE_PLAN_READY. "
            "Day101 planned parser evidence closure without broker handoff, execution, SSH, or live access."
        )
        return 0

    print(f"{format_status('FAIL')} Day101 parser evidence closure plan failed validation.")
    return 1


def _run_day102_parser_fixture_expansion(project_root: Path) -> int:
    report = build_parser_fixture_expansion_report()
    json_path, html_path = write_parser_fixture_expansion_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]
    counts = summary["category_counts"]

    print(format_heading("Day102 Parser Fixture Expansion"))
    print("Task name: parser-fixture-expansion")
    print("Phase: PARSER_FIXTURE_EXPANSION")
    print("Safety: report-only static parser fixture expansion; no parser capability, broker handoff, executor, adapter invocation, SSH, live access, RouterOS execution, config change, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Total fixtures: {summary['total_fixtures']}")
    print(f"positive fixtures: {counts['positive']}")
    print(f"negative fixtures: {counts['negative']}")
    print(f"malformed fixtures: {counts['malformed']}")
    print(f"ambiguous fixtures: {counts['ambiguous']}")
    print(f"unsafe fixtures: {counts['unsafe']}")
    print(f"accepted_count = {summary['accepted_count']}")
    print(f"rejected_count = {summary['rejected_count']}")
    print(f"positive_not_rejected_count = {summary['positive_not_rejected_count']}")
    print(f"unsupported_clear_rejection_count = {summary['unsupported_clear_rejection_count']}")
    print(f"malformed_no_crash_count = {summary['malformed_no_crash_count']}")
    print(f"ambiguous_rejected_count = {summary['ambiguous_rejected_count']}")
    print(f"unsafe_blocked_count = {summary['unsafe_blocked_count']}")
    print(f"reason_missing_count = {summary['reason_missing_count']}")
    print(f"runtime_violation_count = {summary['runtime_violation_count']}")
    print(f"success_criteria_met = {json.dumps(summary['success_criteria_met'])}")
    print(f"parser_capability_added = {json.dumps(report['parser_capability_added'])}")
    print(f"parser_ready_for_broker = {json.dumps(report['parser_ready_for_broker'])}")
    print(f"broker_handoff_allowed = {json.dumps(report['broker_handoff_allowed'])}")
    print(f"execution_allowed = {json.dumps(report['execution_allowed'])}")
    print(f"adapter_invocation_allowed = {json.dumps(report['adapter_invocation_allowed'])}")
    print(f"live_device_access_allowed = {json.dumps(report['live_device_access_allowed'])}")
    print(f"ssh_allowed = {json.dumps(report['ssh_allowed'])}")
    print(f"config_change_allowed = {json.dumps(report['config_change_allowed'])}")
    print(f"fixture_expansion_only = {json.dumps(invariants['fixture_expansion_only'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "FIXTURE_EXPANSION_READY"
        and summary["total_fixtures"] >= 15
        and all(counts[category] >= 3 for category in ("positive", "negative", "malformed", "ambiguous", "unsafe"))
        and summary["success_criteria_met"] is True
        and summary["reason_missing_count"] == 0
        and summary["runtime_violation_count"] == 0
        and report["parser_capability_added"] is False
        and report["parser_ready_for_broker"] is False
        and report["broker_handoff_allowed"] is False
        and report["execution_allowed"] is False
        and report["adapter_invocation_allowed"] is False
        and report["live_device_access_allowed"] is False
        and report["ssh_allowed"] is False
        and report["config_change_allowed"] is False
        and all(invariants[flag] is False for flag in (
            "parser_capability_added",
            "parser_ready_for_broker",
            "broker_handoff_allowed",
            "execution_allowed",
            "adapter_invocation_allowed",
            "executor_invocation_allowed",
            "ssh_allowed",
            "live_device_access_allowed",
            "live_access_allowed",
            "routeros_execution_allowed",
            "command_execution_allowed",
            "raw_command_allowed",
            "config_change_allowed",
            "auth_material_required",
            "device_contact_allowed",
            "dashboard_action_allowed",
            "approval_unlock_supported",
            "openai_api_allowed",
            "voice_runtime_allowed",
        ))
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} FIXTURE_EXPANSION_READY. "
            "Day102 expanded parser fixtures without parser capability, broker handoff, execution, SSH, or live access."
        )
        return 0

    print(f"{format_status('FAIL')} Day102 parser fixture expansion failed validation.")
    return 1


def _run_day103_parser_evidence_matrix(project_root: Path) -> int:
    report = build_parser_evidence_matrix_report()
    json_path, html_path = write_parser_evidence_matrix_reports(project_root, report)
    summary = report["summary"]
    invariants = report["safety_invariants"]

    print(format_heading("Day103 Parser Evidence Matrix / Gap Traceability"))
    print("Task name: parser-evidence-matrix-gap-traceability")
    print("Phase: PARSER_EVIDENCE_MATRIX_READY")
    print("Safety: report-only static Day96-Day102 evidence integration; no parser capability, broker handoff, executor, adapter invocation, SSH, live access, RouterOS execution, config change, config.json, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Total days covered: {summary['total_days_covered']}")
    print(f"trace_complete_count = {summary['trace_complete_count']}")
    print(f"review_required_count = {summary['review_required_count']}")
    print(f"known_gap_count = {summary['known_gap_count']}")
    print(f"blocked_by_safety_boundary_count = {summary['blocked_by_safety_boundary_count']}")
    print(f"execution_allowed_count = {summary['execution_allowed_count']}")
    print(f"adapter_invocation_allowed_count = {summary['adapter_invocation_allowed_count']}")
    print(f"broker_handoff_allowed_count = {summary['broker_handoff_allowed_count']}")
    print(f"live_access_allowed_count = {summary['live_access_allowed_count']}")
    print(f"parser_capability_added_count = {summary['parser_capability_added_count']}")
    print(f"read_only_evidence_integration = {json.dumps(invariants['read_only_evidence_integration'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "MATRIX_READY"
        and summary["days_covered"] == ["Day96", "Day97", "Day98", "Day99", "Day100", "Day101", "Day102"]
        and summary["total_rows"] >= 7
        and summary["trace_complete_count"] >= 1
        and summary["review_required_count"] + summary["known_gap_count"] >= 1
        and summary["execution_allowed_count"] == 0
        and summary["adapter_invocation_allowed_count"] == 0
        and summary["broker_handoff_allowed_count"] == 0
        and summary["live_access_allowed_count"] == 0
        and summary["parser_capability_added_count"] == 0
        and report["parser_capability_added"] is False
        and report["execution_allowed"] is False
        and report["adapter_invocation_allowed"] is False
        and report["broker_handoff_allowed"] is False
        and report["live_access_allowed"] is False
        and report["ssh_allowed"] is False
        and all(
            invariants[flag] is False
            for flag in (
                "parser_capability_added",
                "execution_allowed",
                "adapter_invocation_allowed",
                "broker_handoff_allowed",
                "live_access_allowed",
                "ssh_allowed",
                "executor_invocation_allowed",
                "routeros_execution_allowed",
                "config_mutation_allowed",
                "external_integration_allowed",
                "execution_unlock_supported",
            )
        )
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} MATRIX_READY. "
            "Day103 linked parser evidence gaps without parser capability, broker handoff, execution, SSH, or live access."
        )
        return 0

    print(f"{format_status('FAIL')} Day103 parser evidence matrix failed validation.")
    return 1


def _run_day104_parser_reviewer_acceptance_gate(project_root: Path) -> int:
    report = build_parser_reviewer_acceptance_gate_report()
    json_path, html_path = write_parser_reviewer_acceptance_gate_reports(project_root, report)
    summary = report["summary"]
    flags = report["safety_flags"]

    print(format_heading("Day104 Parser Reviewer Acceptance Gate / Matrix Decision Review"))
    print("Task name: parser-reviewer-acceptance-gate")
    print("Phase: PARSER_REVIEWER_ACCEPTANCE_GATE")
    print("Mode: REVIEW_GATE_ONLY / ACCEPTANCE_DECISION_ONLY")
    print("Safety: report-only Day103 matrix decision review; no parser expansion, parser fallback, broker handoff, adapter binding, SSH, live device access, live command, config change, dashboard action, OpenAI API, voice runtime, or device contact")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Acceptance decision: {report['acceptance_decision']}")
    print(f"Acceptance reason: {report['acceptance_reason']}")
    print(f"next_stage_allowed = {json.dumps(report['next_stage_allowed'])}")
    print(f"Total rows: {summary['total_rows']}")
    print(f"Required rows: {summary['required_rows']}")
    print(f"trace_complete_count = {summary['trace_complete_count']}")
    print(f"review_required_count = {summary['review_required_count']}")
    print(f"known_gap_count = {summary['known_gap_count']}")
    print(f"blocked_by_safety_boundary_count = {summary['blocked_by_safety_boundary_count']}")
    print(f"blocking_finding_count = {summary['blocking_finding_count']}")
    print(f"parser_capability_added = {json.dumps(report['parser_capability_added'])}")
    print(f"execution_unlocked = {json.dumps(report['execution_unlocked'])}")
    print(f"broker_handoff_enabled = {json.dumps(report['broker_handoff_enabled'])}")
    print(f"adapter_connected = {json.dumps(report['adapter_connected'])}")
    print(f"ssh_allowed = {json.dumps(report['ssh_allowed'])}")
    print(f"live_device_access_allowed = {json.dumps(report['live_device_access_allowed'])}")
    print(f"live_command_allowed = {json.dumps(report['live_command_allowed'])}")
    print(f"config_change_allowed = {json.dumps(report['config_change_allowed'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "REVIEW_GATE_READY"
        and report["mode"] == "REVIEW_GATE_ONLY"
        and report["decision_mode"] == "ACCEPTANCE_DECISION_ONLY"
        and report["acceptance_decision"]
        in {
            "ACCEPTABLE_FOR_NEXT_STAGE",
            "ACCEPTABLE_WITH_REVIEW_NOTES",
            "NOT_ACCEPTABLE_KNOWN_GAPS",
            "NOT_ACCEPTABLE_SAFETY_BLOCKED",
            "REVIEW_REQUIRED",
        }
        and all(value is False for value in flags.values())
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} REVIEW_GATE_READY. "
            "Day104 converted Day103 matrix decisions without parser capability, broker handoff, execution, SSH, or live access."
        )
        return 0

    print(f"{format_status('FAIL')} Day104 parser reviewer acceptance gate failed validation.")
    return 1


def _run_day105_parser_acceptance_closure(project_root: Path) -> int:
    report = build_parser_acceptance_closure_report()
    json_path, html_path = write_parser_acceptance_closure_reports(project_root, report)
    flags = report["execution_flags"]

    print(format_heading("Day105 Parser Acceptance Closure / Safety-Blocked Exit Summary"))
    print("Task name: parser-acceptance-closure")
    print("Phase: Parser Acceptance Closure / Safety-Blocked Exit Summary")
    print("Closure type: SUMMARY_ONLY")
    print("Safety: report-only Day96-Day104 parser evidence closure; no parser expansion, adapter execution, SSH, live device access, mapped task execution, config change, OpenAI API, voice input, or next-phase unlock")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"Final recommendation: {report['final_recommendation']}")
    print(f"Covered days: {report['covered_days']}")
    print(f"safety_blocked = {json.dumps(report['safety_blocked'])}")
    print(f"next_phase_allowed = {json.dumps(report['next_phase_allowed'])}")
    print(f"parser_capability_added = {json.dumps(report['parser_capability_added'])}")
    print(f"capability_added = {json.dumps(report['capability_added'])}")
    for flag_name in (
        "execution_allowed",
        "live_device_access_allowed",
        "ssh_allowed",
        "config_change_allowed",
        "mapped_task_execution_allowed",
        "openai_api_allowed",
        "voice_input_allowed",
    ):
        print(f"{flag_name} = {json.dumps(flags[flag_name])}")
    print(f"Safety-blocking reasons: {len(report['safety_blocking_reasons'])}")
    print(f"Next-phase entry conditions: {len(report['next_phase_entry_conditions'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "CLOSURE_READY_REVIEW_ONLY"
        and report["closure_type"] == "SUMMARY_ONLY"
        and report["covered_days"] == [96, 97, 98, 99, 100, 101, 102, 103, 104]
        and report["final_recommendation"] == "SAFETY_BLOCKED_REVIEW_ONLY"
        and report["safety_blocked"] is True
        and report["next_phase_allowed"] is False
        and report["parser_capability_added"] is False
        and report["capability_added"] is False
        and all(value is False for value in flags.values())
        and report["safety_blocking_reasons"]
        and report["next_phase_entry_conditions"]
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} CLOSURE_READY_REVIEW_ONLY. "
            "Day105 packaged parser evidence for review without unlocking live execution."
        )
        return 0

    print(f"{format_status('FAIL')} Day105 parser acceptance closure failed validation.")
    return 1


def _run_day106_codex_agents_instruction_audit(project_root: Path) -> int:
    report = build_codex_agents_instruction_audit_report(project_root)
    json_path, html_path = write_codex_agents_instruction_audit_reports(project_root, report)

    print(format_heading("Day106 Codex AGENTS.md Instruction Compliance Audit"))
    print("Task name: codex-agents-instruction-audit")
    print("Phase: Codex AGENTS.md Instruction Compliance Audit")
    print("Audit type: REPORT_ONLY")
    print("Safety: reads local AGENTS.md and writes reviewer evidence only; no live device, SSH, config mutation, OpenAI API, voice runtime, push, merge, tag, deploy, or publish")
    print("AGENTS.md governance: Codex may read AGENTS.md, audit AGENTS.md, and report findings with proposed wording; Codex must not modify, stage, or commit AGENTS.md during this audit")
    print(f"Result: {report['overall_status']} / {report['reviewer_status']}")
    print(f"AGENTS.md found: {json.dumps(report['agents_file_found'])}")
    print(f"Instruction contract status: {report['instruction_contract_status']}")
    print(f"Safety boundary status: {report['safety_boundary_status']}")
    print(f"Secrets exposure status: {report['secrets_exposure_status']}")
    print(f"Repo guidance status: {report['repo_guidance_status']}")
    print(f"Validation guidance status: {report['validation_guidance_status']}")
    print(f"Done criteria status: {report['done_criteria_status']}")
    for flag_name in (
        "live_execution_allowed",
        "ssh_allowed",
        "device_connection_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "push_allowed_without_user_approval",
        "merge_allowed_without_user_approval",
        "tag_allowed_without_user_approval",
    ):
        print(f"{flag_name} = {json.dumps(report[flag_name])}")
    for flag_name in (
        "codex_may_read_agents_md",
        "codex_may_audit_agents_md",
        "codex_may_report_findings_and_proposed_changes",
        "codex_must_not_modify_agents_md",
        "codex_must_not_stage_agents_md",
        "codex_must_not_commit_agents_md",
        "audit_modifies_agents_md",
        "audit_stages_agents_md",
        "audit_commits_agents_md",
    ):
        print(f"{flag_name} = {json.dumps(report[flag_name])}")
    print(f"Final recommendation: {report['final_recommendation']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["final_recommendation"]
        == "AGENTS_INSTRUCTION_CONTRACT_ACCEPTABLE_FOR_REVIEW_ONLY_CODEX_WORK"
        and report["agents_file_found"] is True
        and report["validation_errors"] == []
        and all(report[flag_name] is False for flag_name in (
            "live_execution_allowed",
            "ssh_allowed",
            "device_connection_allowed",
            "config_mutation_allowed",
            "openai_api_allowed",
            "voice_runtime_allowed",
            "push_allowed_without_user_approval",
            "merge_allowed_without_user_approval",
            "tag_allowed_without_user_approval",
        ))
        and all(report[flag_name] is True for flag_name in (
            "codex_may_read_agents_md",
            "codex_may_audit_agents_md",
            "codex_may_report_findings_and_proposed_changes",
            "codex_must_not_modify_agents_md",
            "codex_must_not_stage_agents_md",
            "codex_must_not_commit_agents_md",
        ))
        and all(report[flag_name] is False for flag_name in (
            "audit_modifies_agents_md",
            "audit_stages_agents_md",
            "audit_commits_agents_md",
        ))
    ):
        print(f"{format_status('PASS')} AGENTS_INSTRUCTION_CONTRACT_ACCEPTABLE_FOR_REVIEW_ONLY_CODEX_WORK")
        return 0

    if report["overall_status"] == "WARN":
        print(f"{format_status('WARN')} AGENTS.md needs hardening before reuse as the durable instruction contract.")
        return 0

    print(f"{format_status('FAIL')} Day106 Codex AGENTS.md instruction compliance audit failed.")
    return 1


def _run_day107_parser_reviewer_evidence_contract(project_root: Path) -> int:
    report = build_parser_reviewer_evidence_contract_report()
    json_path, html_path = write_parser_reviewer_evidence_contract_reports(project_root, report)

    print(format_heading("Day107 Parser Reviewer Evidence Contract Consolidation"))
    print("Task name: parser-reviewer-evidence-contract")
    print("Phase: Parser Reviewer Evidence Contract Consolidation")
    print("Audit type: REPORT_ONLY")
    print("Evidence scope: Day96-Day105")
    print("Safety: deterministic report-only parser reviewer evidence contract; no live execution, SSH, device connection, adapter invocation, OpenAI API, voice runtime, rejected-intent execution, or config mutation")
    print(f"Result: {report['overall_status']} / {report['reviewer_contract_status']}")
    print(f"Final recommendation: {report['final_recommendation']}")
    print(f"evidence_chain_complete = {json.dumps(report['evidence_chain_complete'])}")
    print(f"accepted_for_review_only_continuation = {json.dumps(report['accepted_for_review_only_continuation'])}")
    print(f"accepted_for_live_execution = {json.dumps(report['accepted_for_live_execution'])}")
    for flag_name in (
        "live_execution_allowed",
        "ssh_allowed",
        "device_connection_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "adapter_invocation_allowed",
        "rejected_intent_execution_allowed",
    ):
        print(f"{flag_name} = {json.dumps(report[flag_name])}")
    print(f"Missing evidence days: {report['missing_evidence_days']}")
    print(f"Safety violation fields: {report['safety_violation_fields']}")
    print(f"JSON report: {json_path.relative_to(project_root).as_posix()}")
    print(f"HTML report: {html_path.relative_to(project_root).as_posix()}")

    if (
        report["overall_status"] == "PASS"
        and report["final_recommendation"]
        == "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION"
        and report["evidence_chain_complete"] is True
        and report["accepted_for_review_only_continuation"] is True
        and all(report[flag_name] is False for flag_name in (
            "accepted_for_live_execution",
            "live_execution_allowed",
            "ssh_allowed",
            "device_connection_allowed",
            "config_mutation_allowed",
            "openai_api_allowed",
            "voice_runtime_allowed",
            "adapter_invocation_allowed",
            "rejected_intent_execution_allowed",
        ))
        and not report["safety_violation_fields"]
        and not report["validation_errors"]
    ):
        print(
            f"{format_status('PASS')} "
            "PARSER_REVIEWER_EVIDENCE_CONTRACT_ACCEPTED_FOR_REVIEW_ONLY_CONTINUATION"
        )
        return 0

    if report["overall_status"] == "WARN":
        print(f"{format_status('WARN')} Day107 parser reviewer evidence contract needs gap review.")
        return 0

    print(f"{format_status('FAIL')} Day107 parser reviewer evidence contract failed validation.")
    return 1


def _run_day108_parser_contract_consumer_handoff(project_root: Path) -> int:
    report = build_parser_contract_consumer_handoff_report()
    json_path, html_path = write_parser_contract_consumer_handoff_reports(project_root, report)
    summary = report["summary"]
    source = report["source_contract"]
    invariants = report["safety_invariants"]

    print(format_heading("Day108 Parser Contract Consumer / Reviewer Decision Handoff"))
    print("Task name: parser-contract-consumer-handoff")
    print("Phase: Parser Contract Consumer / Reviewer Decision Handoff")
    print("Audit type: REPORT_ONLY")
    print("Safety: deterministic report-only consumer handoff; no live execution, SSH, device connection, command execution, approval unlock, mapped task execution, OpenAI API, voice input, or write/config change")
    print(f"Source contract: {source['source_contract']}")
    print(f"source_contract_version = {source['source_contract_version']}")
    print(f"consumer_schema_version = {report['consumer_schema_version']}")
    print(f"Result: {report['overall_status']} / {report['reviewer_handoff_status']}")
    print(f"handoff_record_count = {summary['handoff_record_count']}")
    print(f"handoff_ready_count = {summary['handoff_ready_count']}")
    print(f"clarification_required_count = {summary['clarification_required_count']}")
    print(f"blocked_count = {summary['blocked_count']}")
    print(f"unsafe_flags_block_handoff = {json.dumps(summary['unsafe_flags_block_handoff'])}")
    for flag_name in (
        "report_only",
        "dry_run_only",
        "live_execution_allowed",
        "ssh_allowed",
        "device_connection_allowed",
        "command_execution_allowed",
        "write_or_config_change_allowed",
        "approval_unlock_supported",
        "mapped_task_execution_allowed",
        "openai_api_used",
        "voice_input_used",
    ):
        print(f"{flag_name} = {json.dumps(invariants[flag_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_handoff_status"] == "CONSUMER_HANDOFF_READY_REPORT_ONLY"
        and source["source_contract"] == "day107.parser_reviewer_evidence_contract"
        and source["source_contract_version"] == "day107.parser_reviewer_evidence_contract.v1"
        and summary["handoff_ready_count"] >= 1
        and summary["unsafe_flags_block_handoff"] is True
        and invariants["report_only"] is True
        and invariants["dry_run_only"] is True
        and all(invariants[flag_name] is False for flag_name in (
            "live_execution_allowed",
            "ssh_allowed",
            "device_connection_allowed",
            "command_execution_allowed",
            "write_or_config_change_allowed",
            "approval_unlock_supported",
            "mapped_task_execution_allowed",
            "openai_api_used",
            "voice_input_used",
        ))
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} CONSUMER_HANDOFF_READY_REPORT_ONLY")
        return 0

    print(f"{format_status('FAIL')} Day108 parser contract consumer handoff failed validation.")
    return 1


def _run_day109_parser_consumer_handoff_readiness_matrix(project_root: Path) -> int:
    report = build_parser_consumer_handoff_readiness_matrix_report()
    json_path, html_path = write_parser_consumer_handoff_readiness_matrix_reports(project_root, report)
    safety_summary = report["safety_summary"]

    print(format_heading("Day109 Parser Consumer Handoff Readiness Matrix"))
    print("Task name: parser-consumer-handoff-readiness-matrix")
    print("Phase: Parser Consumer Handoff Readiness Matrix")
    print("Audit type: REPORT_ONLY")
    print("Safety: REVIEW_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE; no command execution, mapped task execution, OpenAI API, external API, adapter, broker, or live device access")
    print(f"Source day: {report['source_day']}")
    print(f"Source task: {report['source_task']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"total_records: {report['total_records']}")
    print(f"ready_count: {report['ready_count']}")
    print(f"needs_clarification_count: {report['needs_clarification_count']}")
    print(f"blocked_count: {report['blocked_count']}")
    for field_name in (
        "unsafe_flag_count",
        "live_flag_count",
        "ssh_flag_count",
        "write_flag_count",
        "command_execution_flag_count",
        "mapped_task_execution_flag_count",
        "blocking_condition_preserved",
    ):
        print(f"{field_name}: {json.dumps(safety_summary[field_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if report["overall_status"] == "PASS" and safety_summary["blocking_condition_preserved"] is True:
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day109 parser consumer handoff readiness matrix failed validation.")
    return 1


def _run_day110_parser_consumer_final_gate(project_root: Path) -> int:
    report = build_parser_consumer_final_gate_report(project_root=project_root, agents_md_pre_read=True)
    json_path, html_path = write_parser_consumer_final_gate_reports(project_root, report)
    summary = report["reviewer_decision_summary"]
    agents_evidence = report["agents_md_pre_read_evidence"]

    print(format_heading("Day110 Parser Consumer Final Gate / Reviewer Decision Summary"))
    print("Task name: parser-consumer-final-gate")
    print("Phase: Parser Consumer Final Gate / Reviewer Decision Summary")
    print("Audit type: REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / NO_LIVE_EXECUTION / NO_SSH / NO_WRITE; no command execution, mapped task execution, OpenAI API, external API, adapter, broker, runner execution, or live device access")
    print(f"Source day: {report['source_day']}")
    print(f"Source task: {report['source_task']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"final_gate_status: {report['final_gate_status']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"source_total_records: {summary['source_total_records']}")
    print(f"ready_count: {summary['ready_count']}")
    print(f"needs_clarification_count: {summary['needs_clarification_count']}")
    print(f"blocked_count: {summary['blocked_count']}")
    print(f"agents_md_read_before_day110_work: {json.dumps(agents_evidence['agents_md_read_before_day110_work'])}")
    print(f"agents_md_pre_read_result: {agents_evidence['agents_md_pre_read_result']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["next_phase_allowed"] is False
        and agents_evidence["agents_md_pre_read_result"] == "PASS"
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['final_gate_status']}")
        return 0

    print(f"{format_status('FAIL')} Day110 parser consumer final gate failed validation.")
    return 1


def _run_day111_parser_consumer_release_package(project_root: Path) -> int:
    report = build_parser_consumer_release_package_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_parser_consumer_release_package_reports(project_root, report)
    manifest = report["release_manifest"]
    blocked = report["blocked_condition_summary"]
    traceability = report["traceability_summary"]
    safety = report["safety_invariants"]

    print(format_heading("Day111 Parser Consumer Evidence Freeze / Release Package"))
    print("Task name: parser-consumer-release-package")
    print("Phase: Parser Consumer Evidence Freeze / Release Package")
    print("Audit type: REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / FROZEN; no SSH, live device access, network command execution, config mutation, mapped task execution, execution broker unlock, approval unlock, OpenAI API, voice runtime, cloud runtime, dashboard execution control, or next-phase execution")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"release_package_status: {report['release_package_status']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day111_work: {json.dumps(report['agents_md_read_before_day111_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    print(f"source_day_count: {manifest['source_day_count']}")
    print(f"frozen_evidence_count: {manifest['frozen_evidence_count']}")
    print(f"blocked_condition_preserved: {json.dumps(blocked['blocked_condition_preserved'])}")
    print(f"safety_invariant_result: {traceability['safety_invariant_result']}")
    for field_name in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "approval_unlock_supported",
        "mapped_task_execution_allowed",
        "execution_broker_unlock_allowed",
        "next_phase_execution_allowed",
    ):
        print(f"{field_name}: {json.dumps(safety[field_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["next_phase_allowed"] is False
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day111_work"] is True
        and report["agents_md_modified"] is False
        and blocked["blocked_condition_preserved"] is True
        and traceability["safety_invariant_result"] == "PASS"
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day111 parser consumer release package failed validation.")
    return 1


def _run_day112_parser_consumer_release_review_intake(project_root: Path) -> int:
    report = build_parser_consumer_release_review_intake_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_parser_consumer_release_review_intake_reports(project_root, report)
    summary = report["triage_summary"]
    safety = report["safety_invariants"]

    print(format_heading("Day112 Parser Consumer Release Review Intake / Reviewer Triage Checklist"))
    print("Task name: parser-consumer-release-review-intake")
    print("Phase: Parser Consumer Release Review Intake / Reviewer Triage Checklist")
    print("Audit type: REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / TRIAGE_ONLY; no approval unlock, execution readiness, SSH, live device access, network command execution, config mutation, mapped task execution, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, dashboard execution control, or next-phase execution")
    print(f"Source day: {report['source_day']}")
    print(f"Source task: {report['source_task']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"intake_status: {report['intake_status']}")
    print(f"triage_status: {report['triage_status']}")
    print(f"blocked_condition_status: {report['blocked_condition_status']}")
    print(f"decision_route: {report['decision_route']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"approval_unlock_allowed: {json.dumps(report['approval_unlock_allowed'])}")
    print(f"execution_readiness_allowed: {json.dumps(report['execution_readiness_allowed'])}")
    print(f"approve_next_phase_execution_supported: {json.dumps(report['approve_next_phase_execution_supported'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day112_work: {json.dumps(report['agents_md_read_before_day112_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    print(f"source_release_package_status: {summary['source_release_package_status']}")
    print(f"source_blocked_condition_preserved: {json.dumps(summary['source_blocked_condition_preserved'])}")
    print(f"checklist_pass_count: {summary['checklist_pass_count']}")
    print(f"checklist_total_count: {summary['checklist_total_count']}")
    print(f"allowed_reviewer_route_count: {summary['allowed_reviewer_route_count']}")
    print(f"forbidden_reviewer_route_count: {summary['forbidden_reviewer_route_count']}")
    print(f"failed_check_count: {summary['failed_check_count']}")
    for field_name in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "approval_unlock_supported",
        "approve_next_phase_execution_supported",
        "execution_readiness_supported",
        "mapped_task_execution_allowed",
        "adapter_invocation_allowed",
        "broker_invocation_allowed",
        "execution_broker_unlock_allowed",
        "runner_invocation_allowed",
        "next_phase_execution_allowed",
    ):
        print(f"{field_name}: {json.dumps(safety[field_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["next_phase_allowed"] is False
        and report["approval_unlock_allowed"] is False
        and report["execution_readiness_allowed"] is False
        and report["approve_next_phase_execution_supported"] is False
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day112_work"] is True
        and report["agents_md_modified"] is False
        and report["blocked_condition_status"] == "PRESERVED"
        and summary["source_blocked_condition_preserved"] is True
        and summary["checklist_pass_count"] == 10
        and summary["checklist_total_count"] == 10
        and summary["allowed_reviewer_route_count"] == 4
        and summary["forbidden_reviewer_route_count"] == 1
        and summary["failed_check_count"] == 0
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day112 parser consumer release review intake failed validation.")
    return 1


def _run_day113_parser_consumer_reviewer_triage_decision_log(project_root: Path) -> int:
    report = build_parser_consumer_reviewer_triage_decision_log_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_parser_consumer_reviewer_triage_decision_log_reports(project_root, report)
    summary = report["outcome_summary"]
    safety = report["safety_invariants"]

    print(format_heading("Day113 Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit"))
    print("Task name: parser-consumer-reviewer-triage-decision-log")
    print("Phase: Parser Consumer Reviewer Triage Decision Log / Intake Outcome Audit")
    print("Audit type: REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / OUTCOME_AUDIT_ONLY; no approval unlock, execution readiness, SSH, live device access, network command execution, config mutation, mapped task execution, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, dashboard execution control, or next-phase execution")
    print(f"Source day: {report['source_day']}")
    print(f"Source task: {report['source_task']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"outcome_audit_status: {report['outcome_audit_status']}")
    print(f"triage_outcome_status: {report['triage_outcome_status']}")
    print(f"selected_reviewer_outcome: {report['selected_reviewer_outcome']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"approval_unlock_allowed: {json.dumps(report['approval_unlock_allowed'])}")
    print(f"execution_readiness_allowed: {json.dumps(report['execution_readiness_allowed'])}")
    print(f"approve_next_phase_execution_supported: {json.dumps(report['approve_next_phase_execution_supported'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day113_work: {json.dumps(report['agents_md_read_before_day113_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    print(f"source_reviewer_status: {summary['source_reviewer_status']}")
    print(f"source_intake_status: {summary['source_intake_status']}")
    print(f"source_triage_status: {summary['source_triage_status']}")
    print(f"source_blocked_condition_status: {summary['source_blocked_condition_status']}")
    print(f"source_next_phase_allowed: {json.dumps(summary['source_next_phase_allowed'])}")
    print(f"outcome_log_entry_count: {summary['outcome_log_entry_count']}")
    print(f"audit_check_pass_count: {summary['audit_check_pass_count']}")
    print(f"audit_check_total_count: {summary['audit_check_total_count']}")
    print(f"failed_check_count: {summary['failed_check_count']}")
    for field_name in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "approval_unlock_supported",
        "execution_readiness_supported",
        "approve_next_phase_execution_supported",
        "mapped_task_execution_allowed",
        "adapter_invocation_allowed",
        "broker_invocation_allowed",
        "execution_broker_unlock_allowed",
        "runner_invocation_allowed",
        "next_phase_execution_allowed",
    ):
        print(f"{field_name}: {json.dumps(safety[field_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["next_phase_allowed"] is False
        and report["approval_unlock_allowed"] is False
        and report["execution_readiness_allowed"] is False
        and report["approve_next_phase_execution_supported"] is False
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day113_work"] is True
        and report["agents_md_modified"] is False
        and report["selected_reviewer_outcome"] == "HOLD_FOR_BLOCKED_RECORDS"
        and summary["source_next_phase_allowed"] is False
        and summary["source_blocked_condition_status"] == "PRESERVED"
        and summary["outcome_log_entry_count"] == 5
        and summary["audit_check_pass_count"] == 9
        and summary["audit_check_total_count"] == 9
        and summary["failed_check_count"] == 0
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day113 parser consumer reviewer triage decision log failed validation.")
    return 1


def _run_day114_parser_consumer_reviewer_triage_evidence_traceability(project_root: Path) -> int:
    report = build_parser_consumer_reviewer_triage_evidence_traceability_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_parser_consumer_reviewer_triage_evidence_traceability_reports(
        project_root, report
    )
    summary = report["traceability_summary"]
    safety = report["safety_invariants"]

    print(format_heading("Day114 Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit"))
    print("Task name: parser-consumer-reviewer-triage-evidence-traceability")
    print("Phase: Parser Consumer Reviewer Triage Evidence Traceability / Blocked Record Preservation Audit")
    print("Audit type: AUDIT_ONLY / REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / TRACEABILITY_AUDIT_ONLY; no approval unlock, execution readiness, SSH, live device access, network command execution, config mutation, mapped task execution, adapter invocation, broker invocation, runner invocation, OpenAI API, voice runtime, cloud runtime, dashboard execution control, or next-phase execution")
    print(f"Source Day112 task: {report['source_tasks']['day112']}")
    print(f"Source Day113 task: {report['source_tasks']['day113']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"traceability_status: {report['traceability_status']}")
    print(f"blocked_record_status: {report['blocked_record_status']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"source_day112_intake_linked: {json.dumps(report['source_day112_intake_linked'])}")
    print(f"source_day113_triage_linked: {json.dumps(report['source_day113_triage_linked'])}")
    print(f"blocked_records_preserved: {json.dumps(report['blocked_records_preserved'])}")
    print(f"total_trace_records: {summary['total_trace_records']}")
    print(f"source_intake_record_count: {summary['source_intake_record_count']}")
    print(f"linked_day113_outcome_count: {summary['linked_day113_outcome_count']}")
    print(f"blocked_condition_count: {summary['blocked_condition_count']}")
    print(f"preserved_blocked_record_count: {summary['preserved_blocked_record_count']}")
    print(f"missing_trace_count: {summary['missing_trace_count']}")
    print(f"downgrade_detected_count: {summary['downgrade_detected_count']}")
    print(f"execution_readiness_inferred_count: {summary['execution_readiness_inferred_count']}")
    print(f"next_phase_allowed_count: {summary['next_phase_allowed_count']}")
    print(f"unsafe_flag_count: {summary['unsafe_flag_count']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"approval_unlock_allowed: {json.dumps(report['approval_unlock_allowed'])}")
    print(f"execution_readiness_allowed: {json.dumps(report['execution_readiness_allowed'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day114_work: {json.dumps(report['agents_md_read_before_day114_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    for field_name in (
        "ssh_allowed",
        "live_device_access_allowed",
        "network_command_execution_allowed",
        "config_mutation_allowed",
        "adapter_invocation_allowed",
        "broker_invocation_allowed",
        "runner_invocation_allowed",
        "approval_unlock_supported",
        "execution_readiness_supported",
        "next_phase_allowed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "cloud_runtime_allowed",
        "mapped_task_execution_allowed",
    ):
        print(f"{field_name}: {json.dumps(safety[field_name])}")
    print("NO_EXECUTION_READINESS_INFERRED")
    print("NO_NEXT_PHASE_UNLOCK")
    print("BLOCKED_RECORDS_PRESERVED")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "TRACEABILITY_AUDITED_NON_EXECUTABLE"
        and report["source_day112_intake_linked"] is True
        and report["source_day113_triage_linked"] is True
        and report["blocked_records_preserved"] is True
        and report["next_phase_allowed"] is False
        and report["approval_unlock_allowed"] is False
        and report["execution_readiness_allowed"] is False
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day114_work"] is True
        and report["agents_md_modified"] is False
        and summary["missing_trace_count"] == 0
        and summary["downgrade_detected_count"] == 0
        and summary["execution_readiness_inferred_count"] == 0
        and summary["next_phase_allowed_count"] == 0
        and summary["unsafe_flag_count"] == 0
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day114 parser consumer reviewer triage evidence traceability failed validation.")
    return 1


def _run_day115_parser_consumer_reviewer_triage_closure_summary(project_root: Path) -> int:
    report = build_parser_consumer_reviewer_triage_closure_summary_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_parser_consumer_reviewer_triage_closure_summary_reports(
        project_root, report
    )
    summary = report["closure_summary"]
    safety = report["safety_invariants"]

    print(format_heading("Day115 Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit"))
    print("Task name: parser-consumer-reviewer-triage-closure-summary")
    print("Phase: Parser Consumer Reviewer Triage Closure Summary / Non-Advancement Decision Audit")
    print("Audit type: CLOSURE_SUMMARY / REPORT_ONLY")
    print("Safety: REVIEW_ONLY / REPORT_ONLY / NON_ADVANCING_CLOSURE; no readiness inference, broker handoff, runner execution, adapter access, SSH, live access, command execution, mapped task execution, approval unlock, parser capability change, or next-phase advancement")
    print(f"Source Day112 task: {report['source_tasks']['day112']}")
    print(f"Source Day113 task: {report['source_tasks']['day113']}")
    print(f"Source Day114 task: {report['source_tasks']['day114']}")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"closure_status: {report['closure_status']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"triage_chain_conclusion: {report['triage_chain_conclusion']}")
    print(f"day112_included: {json.dumps(summary['day112_included'])}")
    print(f"day113_included: {json.dumps(summary['day113_included'])}")
    print(f"day114_included: {json.dumps(summary['day114_included'])}")
    print(f"blocked_record_count: {summary['blocked_record_count']}")
    print(f"blocked_records_preserved: {json.dumps(summary['blocked_records_preserved'])}")
    print(f"blocked_records_not_downgraded: {json.dumps(summary['blocked_records_not_downgraded'])}")
    print(f"downgraded_to_pass_count: {summary['downgraded_to_pass_count']}")
    print(f"unsafe_flag_count: {summary['unsafe_flag_count']}")
    print(f"next_phase_allowed: {json.dumps(report['next_phase_allowed'])}")
    print(f"execution_readiness_inferred: {json.dumps(report['execution_readiness_inferred'])}")
    print(f"readiness_inferred: {json.dumps(report['readiness_inferred'])}")
    print(f"broker_handoff_allowed: {json.dumps(report['broker_handoff_allowed'])}")
    print(f"runner_execution_allowed: {json.dumps(report['runner_execution_allowed'])}")
    print(f"adapter_access_allowed: {json.dumps(report['adapter_access_allowed'])}")
    print(f"ssh_allowed: {json.dumps(report['ssh_allowed'])}")
    print(f"live_access_allowed: {json.dumps(report['live_access_allowed'])}")
    print(f"command_execution_allowed: {json.dumps(report['command_execution_allowed'])}")
    print(f"mapped_task_execution_allowed: {json.dumps(report['mapped_task_execution_allowed'])}")
    print(f"approval_unlock_allowed: {json.dumps(report['approval_unlock_allowed'])}")
    print(f"parser_capability_changed: {json.dumps(report['parser_capability_changed'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day115_work: {json.dumps(report['agents_md_read_before_day115_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    for field_name in (
        "next_phase_allowed",
        "execution_readiness_inferred",
        "readiness_inferred",
        "broker_handoff_allowed",
        "runner_execution_allowed",
        "adapter_access_allowed",
        "ssh_allowed",
        "live_access_allowed",
        "command_execution_allowed",
        "mapped_task_execution_allowed",
        "approval_unlock_allowed",
        "parser_capability_changed",
    ):
        print(f"safety_invariants.{field_name}: {json.dumps(safety[field_name])}")
    for marker in report["evidence_markers"]:
        print(marker)
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "TRIAGE_CLOSURE_AUDITED_NON_ADVANCING"
        and report["closure_status"] == "CLOSED_WITH_BLOCKED_RECORDS_PRESERVED"
        and report["final_recommendation"] == "DO_NOT_ADVANCE"
        and report["next_phase_allowed"] is False
        and report["execution_readiness_inferred"] is False
        and summary["day112_included"] is True
        and summary["day113_included"] is True
        and summary["day114_included"] is True
        and summary["blocked_records_preserved"] is True
        and summary["blocked_records_not_downgraded"] is True
        and summary["downgraded_to_pass_count"] == 0
        and summary["unsafe_flag_count"] == 0
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day115_work"] is True
        and report["agents_md_modified"] is False
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day115 parser consumer reviewer triage closure summary failed validation.")
    return 1


def _run_day116_reviewer_deferred_action_register(project_root: Path) -> int:
    report = build_reviewer_deferred_action_register_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_reviewer_deferred_action_register_reports(project_root, report)
    summary = report["register_summary"]

    print(format_heading("Day116 Reviewer Deferred Action Register / Blocked Follow-up Queue"))
    print("Task name: reviewer-deferred-action-register")
    print("Phase: Reviewer Deferred Action Register / Blocked Follow-up Queue")
    print("Audit type: REVIEWER_ONLY / REPORT_ONLY")
    print("Safety: REVIEWER_DEFERRED_ACTIONS_ONLY; no item resolution, approval, release, advancement, broker handoff, runner handoff, adapter handoff, SSH access, live access, command execution, or execution unlock")
    print(f"overall_status: {report['overall_status']}")
    print(f"status: {report['status']}")
    print(f"follow_up_queue_status: {report['follow_up_queue_status']}")
    print(f"day_range: {report['day_range']}")
    print(f"register_scope: {report['register_scope']}")
    print(f"source_days_reviewed: {summary['source_days_reviewed']}")
    print(f"source_artifacts_reviewed: {summary['source_artifacts_reviewed']}")
    print(f"deferred_item_count: {summary['deferred_item_count']}")
    print(f"blocked_count: {summary['blocked_count']}")
    print(f"hold_count: {summary['hold_count']}")
    print(f"do_not_advance_count: {summary['do_not_advance_count']}")
    print(f"readiness_generated_count: {summary['readiness_generated_count']}")
    print(f"execution_unlock_count: {summary['execution_unlock_count']}")
    print(f"broker_handoff_count: {summary['broker_handoff_count']}")
    print(f"runner_handoff_count: {summary['runner_handoff_count']}")
    print(f"adapter_handoff_count: {summary['adapter_handoff_count']}")
    print(f"ssh_access_count: {summary['ssh_access_count']}")
    print(f"live_access_count: {summary['live_access_count']}")
    print(f"execution_allowed: {json.dumps(report['execution_allowed'])}")
    print(f"broker_allowed: {json.dumps(report['broker_allowed'])}")
    print(f"runner_allowed: {json.dumps(report['runner_allowed'])}")
    print(f"adapter_allowed: {json.dumps(report['adapter_allowed'])}")
    print(f"ssh_allowed: {json.dumps(report['ssh_allowed'])}")
    print(f"live_access_allowed: {json.dumps(report['live_access_allowed'])}")
    print(f"readiness_generated: {json.dumps(report['readiness_generated'])}")
    print(f"next_stage_allowed: {json.dumps(report['next_stage_allowed'])}")
    print(f"agents_md_pre_read_result: {report['agents_md_pre_read_result']}")
    print(f"agents_md_read_before_day116_work: {json.dumps(report['agents_md_read_before_day116_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["status"] == "DEFERRED_ACTION_REGISTER_RECORDED"
        and report["day_range"] == "Day112-Day115"
        and report["register_scope"] == "REVIEWER_DEFERRED_ACTIONS_ONLY"
        and report["execution_allowed"] is False
        and report["broker_allowed"] is False
        and report["runner_allowed"] is False
        and report["adapter_allowed"] is False
        and report["ssh_allowed"] is False
        and report["live_access_allowed"] is False
        and report["readiness_generated"] is False
        and report["next_stage_allowed"] is False
        and summary["source_days_reviewed"] == 4
        and summary["readiness_generated_count"] == 0
        and summary["execution_unlock_count"] == 0
        and summary["broker_handoff_count"] == 0
        and summary["runner_handoff_count"] == 0
        and summary["adapter_handoff_count"] == 0
        and summary["ssh_access_count"] == 0
        and summary["live_access_count"] == 0
        and report["agents_md_pre_read_result"] == "PASS"
        and report["agents_md_read_before_day116_work"] is True
        and report["agents_md_modified"] is False
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['status']}")
        return 0

    print(f"{format_status('FAIL')} Day116 reviewer deferred action register failed validation.")
    return 1


def _run_day117_deferred_action_traceability_review(project_root: Path) -> int:
    report = build_deferred_action_traceability_review_report(
        project_root=project_root,
        agents_md_pre_read=True,
        agents_md_modified=False,
    )
    json_path, html_path = write_deferred_action_traceability_review_reports(project_root, report)
    summary = report["matrix_summary"]

    print(format_heading("Day117 Deferred Action Traceability Review / Follow-up Ownership Matrix"))
    print("Task name: deferred-action-traceability-review")
    print("Phase: Deferred Action Traceability Review / Follow-up Ownership Matrix")
    print("Audit type: REVIEWER_ONLY / REPORT_ONLY / NON_ADVANCING")
    print("Safety: DAY116_DEFERRED_ACTION_TRACEABILITY_ONLY; no item resolution, approval, release, advancement, readiness generation, broker handoff, runner handoff, adapter handoff, SSH access, live access, command execution, or execution unlock")
    print(f"overall_status: {report['overall_status']}")
    print(f"status: {report['status']}")
    print(f"ownership_matrix_status: {summary['ownership_matrix_status']}")
    print(f"traceability_status: {summary['traceability_status']}")
    print(f"total_deferred_items_reviewed: {summary['total_deferred_items_reviewed']}")
    print(f"expected_deferred_item_count: {summary['expected_deferred_item_count']}")
    print(f"review_sequence_count: {summary['review_sequence_count']}")
    print(f"unsafe_flag_count: {summary['unsafe_flag_count']}")
    print(f"execution_allowed: {json.dumps(report['execution_allowed'])}")
    print(f"broker_allowed: {json.dumps(report['broker_allowed'])}")
    print(f"runner_allowed: {json.dumps(report['runner_allowed'])}")
    print(f"adapter_allowed: {json.dumps(report['adapter_allowed'])}")
    print(f"ssh_allowed: {json.dumps(report['ssh_allowed'])}")
    print(f"live_access_allowed: {json.dumps(report['live_access_allowed'])}")
    print(f"readiness_generated: {json.dumps(report['readiness_generated'])}")
    print(f"next_stage_allowed: {json.dumps(report['next_stage_allowed'])}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"agents_md_read_before_day117_work: {json.dumps(report['agents_md_read_before_day117_work'])}")
    print(f"agents_md_modified: {json.dumps(report['agents_md_modified'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["status"] == "DEFERRED_ACTION_TRACEABILITY_REVIEW_READY"
        and summary["total_deferred_items_reviewed"] == 7
        and summary["ownership_matrix_status"] == "RECORDED"
        and summary["traceability_status"] == "TRACEABLE_TO_DAY116"
        and summary["review_sequence_count"] == 7
        and summary["unsafe_flag_count"] == 0
        and report["execution_allowed"] is False
        and report["broker_allowed"] is False
        and report["runner_allowed"] is False
        and report["adapter_allowed"] is False
        and report["ssh_allowed"] is False
        and report["live_access_allowed"] is False
        and report["readiness_generated"] is False
        and report["next_stage_allowed"] is False
        and report["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
        and report["agents_md_read_before_day117_work"] is True
        and report["agents_md_modified"] is False
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['status']}")
        return 0

    print(f"{format_status('FAIL')} Day117 deferred action traceability review failed validation.")
    return 1


def _run_day118_deferred_action_review_sequence_runbook(project_root: Path) -> int:
    report = build_deferred_action_review_sequence_runbook_report(project_root=project_root)
    json_path, html_path = write_deferred_action_review_sequence_runbook_reports(project_root, report)
    summary = report["reviewer_status_summary"]

    print(format_heading("Day118 Deferred Action Review Sequence Runbook / Evidence Intake Checklist"))
    print("Task name: deferred-action-review-sequence-runbook")
    print("Phase: Deferred Action Review Sequence Runbook / Evidence Intake Checklist")
    print("Audit type: REVIEW_ONLY / REPORT_ONLY / NON_ADVANCING")
    print("Safety: Day117 evidence intake checklist only; no readiness transition, next-stage advancement, broker, runner, adapter, SSH, live access, mapped task execution, OpenAI API, voice runtime, or execution unlock")
    print(f"overall_status: {report['overall_status']}")
    print(f"status: {report['status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"source_day: {report['source_day']}")
    print(f"source_record_count: {report['source_record_count']}")
    print(f"checklist_record_count: {report['checklist_record_count']}")
    print(f"review_sequence: {summary['review_sequence']}")
    print(f"completion_state_values: {summary['completion_state_values']}")
    print(f"review_only: {json.dumps(report['review_only'])}")
    print(f"non_advancing: {json.dumps(report['non_advancing'])}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"execution_unlock_supported: {json.dumps(report['execution_unlock_supported'])}")
    print(f"next_stage_allowed: {json.dumps(report['next_stage_allowed'])}")
    print(f"readiness_transition_allowed: {json.dumps(report['readiness_transition_allowed'])}")
    print(f"broker_allowed: {json.dumps(report['broker_allowed'])}")
    print(f"runner_allowed: {json.dumps(report['runner_allowed'])}")
    print(f"adapter_allowed: {json.dumps(report['adapter_allowed'])}")
    print(f"ssh_allowed: {json.dumps(report['ssh_allowed'])}")
    print(f"live_access_allowed: {json.dumps(report['live_access_allowed'])}")
    print(f"mapped_task_execution_allowed: {json.dumps(report['mapped_task_execution_allowed'])}")
    print(f"openai_api_allowed: {json.dumps(report['openai_api_allowed'])}")
    print(f"voice_runtime_allowed: {json.dumps(report['voice_runtime_allowed'])}")
    print(f"device_access_allowed: {json.dumps(report['device_access_allowed'])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["reviewer_status"] == "INTAKE_CHECKLIST_READY_REVIEW_ONLY"
        and report["source_day"] == 117
        and report["source_record_count"] == 7
        and report["checklist_record_count"] == 7
        and summary["review_sequence"] == list(range(1, 8))
        and report["review_only"] is True
        and report["non_advancing"] is True
        and report["final_recommendation"] == "REVIEW_ONLY_NON_ADVANCING"
        and report["execution_unlock_supported"] is False
        and report["next_stage_allowed"] is False
        and report["readiness_transition_allowed"] is False
        and report["broker_allowed"] is False
        and report["runner_allowed"] is False
        and report["adapter_allowed"] is False
        and report["ssh_allowed"] is False
        and report["live_access_allowed"] is False
        and report["mapped_task_execution_allowed"] is False
        and report["openai_api_allowed"] is False
        and report["voice_runtime_allowed"] is False
        and report["device_access_allowed"] is False
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['reviewer_status']}")
        return 0

    print(f"{format_status('FAIL')} Day118 deferred action review sequence runbook failed validation.")
    return 1


def _run_day119_reviewer_evidence_intake_outcome_ledger(project_root: Path) -> int:
    report = build_reviewer_evidence_intake_outcome_ledger_report(project_root=project_root)
    json_path, html_path = write_reviewer_evidence_intake_outcome_ledger_reports(project_root, report)

    print(format_heading("Day119 Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log"))
    print("Task name: reviewer-evidence-intake-outcome-ledger")
    print("Alias: deferred-evidence-collection-log")
    print("Phase: Reviewer Evidence Intake Outcome Ledger / Deferred Evidence Collection Log")
    print("Audit type: REVIEW_ONLY / REPORT_ONLY / EVIDENCE_INTAKE_LOG_ONLY")
    print("Safety: Day118 evidence intake outcome logging only; no acceptance decision, reviewer sign-off, safety boundary release, execution, SSH, live command, adapter invocation, broker handoff, OpenAI API, voice runtime, or parser capability change")
    print(f"overall_status: {report['overall_status']}")
    print(f"status: {report['status']}")
    print(f"source_day: {report['source_day']}")
    print(f"source_record_count: {report['source_record_count']}")
    print(f"ledger_record_count: {report['ledger_record_count']}")
    print(f"intake_status_counts: {report['intake_status_counts']}")
    print(f"gap_status_counts: {report['gap_status_counts']}")
    print(f"open_or_deferred_gap_count: {report['open_or_deferred_gap_count']}")
    print(f"safety_blocked_gap_count: {report['safety_blocked_gap_count']}")
    print(f"received_no_gap_count: {report['received_no_gap_count']}")
    print(f"final_recommendation: {report['final_recommendation']}")
    for flag_name in (
        "acceptance_decision_made",
        "reviewer_signoff_made",
        "safety_boundary_released",
        "allowed_to_execute",
        "ssh_allowed",
        "live_command_allowed",
        "adapter_invocation_allowed",
        "broker_handoff_allowed",
        "parser_capability_changed",
        "openai_api_allowed",
        "voice_runtime_allowed",
        "live_device_access_allowed",
        "config_mutation_allowed",
    ):
        print(f"{flag_name}: {json.dumps(report[flag_name])}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "INTAKE_LEDGER_READY"
        and report["status"] == "INTAKE_LEDGER_READY"
        and report["source_day"] == 118
        and report["source_record_count"] == 7
        and report["ledger_record_count"] == 7
        and report["open_or_deferred_gap_count"] >= 1
        and report["safety_blocked_gap_count"] >= 1
        and report["final_recommendation"] == "REVIEW_ONLY_DEFERRED_EVIDENCE_COLLECTION"
        and all(report[flag_name] is False for flag_name in (
            "acceptance_decision_made",
            "reviewer_signoff_made",
            "safety_boundary_released",
            "allowed_to_execute",
            "ssh_allowed",
            "live_command_allowed",
            "adapter_invocation_allowed",
            "broker_handoff_allowed",
            "parser_capability_changed",
            "openai_api_allowed",
            "voice_runtime_allowed",
            "live_device_access_allowed",
            "config_mutation_allowed",
        ))
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} {report['overall_status']}")
        return 0

    print(f"{format_status('FAIL')} Day119 reviewer evidence intake outcome ledger failed validation.")
    return 1


def _run_day123_safety_boundary_regression_matrix(project_root: Path) -> int:
    report = build_safety_boundary_regression_matrix_report(task_catalog=list_tasks())
    json_path, html_path = write_safety_boundary_regression_matrix_reports(project_root, report)
    summary = report["summary"]

    print(format_heading("Day123 Safety Boundary Regression Matrix"))
    print("Task name: safety-boundary-regression-matrix")
    print("Mode: REPORT_ONLY_SAFETY_BOUNDARY_REGRESSION")
    print("Safety: report-only; no reviewed task execution, SSH, live commands, mutation, unlock, adapter/broker/runner invocation, OpenAI API, voice runtime, or dashboard POST action")
    print(f"overall_status: {report['overall_status']}")
    print(f"status: {report['status']}")
    print(f"total_rows: {summary['total_rows']}")
    print(f"passed_rows: {summary['passed_rows']}")
    print(f"failed_rows: {summary['failed_rows']}")
    print(f"missing_catalog_rows: {summary['missing_catalog_rows']}")
    for count_name in (
        "execution_allowed_count",
        "ssh_allowed_count",
        "live_command_allowed_count",
        "mutation_allowed_count",
        "unlock_supported_count",
        "adapter_invocation_allowed_count",
        "broker_invocation_allowed_count",
        "runner_invocation_allowed_count",
        "openai_api_allowed_count",
        "voice_runtime_allowed_count",
        "dashboard_post_action_allowed_count",
    ):
        print(f"{count_name}: {summary[count_name]}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["status"] == "PASS"
        and summary["total_rows"] >= 24
        and summary["failed_rows"] == 0
        and summary["missing_catalog_rows"] == 0
        and all(
            summary[count_name] == 0
            for count_name in (
                "execution_allowed_count",
                "ssh_allowed_count",
                "live_command_allowed_count",
                "mutation_allowed_count",
                "unlock_supported_count",
                "adapter_invocation_allowed_count",
                "broker_invocation_allowed_count",
                "runner_invocation_allowed_count",
                "openai_api_allowed_count",
                "voice_runtime_allowed_count",
                "dashboard_post_action_allowed_count",
            )
        )
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} SAFETY_BOUNDARY_REGRESSION_MATRIX_READY")
        return 0

    print(f"{format_status('FAIL')} Day123 safety boundary regression matrix blocked by a safety regression.")
    return 1


def _run_day124_safety_invariant_helper_review(project_root: Path) -> int:
    report = build_safety_invariant_helper_review()
    json_path, html_path = write_safety_invariant_helper_review_reports(project_root, report)
    summary = report["dangerous_flag_summary"]

    print(format_heading("Day124 Safety Invariant Helper Consolidation"))
    print("Task name: safety-invariant-helper-review")
    print("Mode: REVIEW_ONLY")
    print("Safety: review-only; no OpenAI API, voice input, SSH, live device, live command, runtime unlock, dashboard POST/action endpoint, broker execution, mapped task execution, write operation, or configuration change")
    print(f"overall_status: {report['overall_status']}")
    print(f"reviewer_status: {report['reviewer_status']}")
    print(f"mode: {report['mode']}")
    print(f"execution_allowed: {str(report['execution_allowed']).lower()}")
    print(f"final_recommendation: {report['final_recommendation']}")
    print(f"dangerous_flags_false: {summary['false_flags']}/{summary['total_flags']}")
    print(f"unsafe_true_flags: {summary['unsafe_true_flags']}")
    print(f"unblocked_capabilities: {summary['unblocked_capabilities']}")
    for flag, value in report["safety_invariants"].items():
        print(f"{flag}: {str(value).lower()}")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")

    if (
        report["overall_status"] == "PASS"
        and report["mode"] == "REVIEW_ONLY"
        and report["execution_allowed"] is False
        and report["final_recommendation"] == "KEEP_REVIEW_ONLY_SAFETY_INVARIANTS"
        and summary["unsafe_true_flags"] == 0
        and summary["unblocked_capabilities"] == 0
        and not report["validation_errors"]
    ):
        print(f"{format_status('PASS')} SAFETY_INVARIANT_HELPER_CONSOLIDATED")
        return 0

    print(f"{format_status('FAIL')} Day124 safety invariant helper review blocked by an unsafe flag.")
    return 1


def _run_day125_thin_cli_regression_gate(project_root: Path) -> int:
    return run_thin_cli_regression_gate(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day126_post_refactor_compatibility_evidence_pack(project_root: Path) -> int:
    return run_post_refactor_compatibility_evidence_pack(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day127_ai_reviewer_summary_schema_contract(project_root: Path) -> int:
    return run_ai_reviewer_summary_schema_contract(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day128_ai_reviewer_summary_fixture_renderer(project_root: Path) -> int:
    return run_ai_reviewer_summary_fixture_renderer(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day129_ai_summary_prompt_contract(project_root: Path) -> int:
    return run_ai_summary_prompt_contract(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day130_ai_summary_redaction_policy(project_root: Path) -> int:
    return run_ai_summary_redaction_policy(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _run_day131_ai_summary_audit_trail_binding(project_root: Path) -> int:
    return run_ai_summary_audit_trail_binding(
        project_root,
        format_heading_func=format_heading,
        format_status_func=format_status,
        relative_to_project_func=_relative_to_project,
    )


def _relative_to_project(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _collect_report_paths(project_root: Path, patterns: List[str]) -> List[Path]:
    paths: List[Path] = []
    seen = set()
    for pattern in patterns:
        for path in sorted(project_root.glob(pattern)):
            if path.is_file() and path.name.lower() != "config.json":
                resolved = path.resolve()
                if resolved not in seen:
                    paths.append(path)
                    seen.add(resolved)
    return paths


def _report_device_label(path: Optional[Path], report_title: str) -> str:
    if path is None:
        return "Summary report" if "summary" in report_title.lower() else "Expected report"
    parent = path.parent.name
    if parent in {"reports", "summary", "lab-summary"}:
        return "Summary report"
    return parent


def _scan_report_catalog_item(project_root: Path, report_type: Dict[str, Any]) -> Dict[str, List[Path]]:
    return {
        "json_paths": _collect_report_paths(project_root, report_type["json_globs"]),
        "html_paths": _collect_report_paths(project_root, report_type["html_globs"]),
    }


def _missing_report_visibility_row(report_type: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "day": report_type["day"],
        "title": report_type["title"],
        "report_type": report_type.get("report_type", "Report evidence"),
        "device": _report_device_label(None, report_type["title"]),
        "status": "MISSING",
        "safety": report_type.get("safety_label", "report-only evidence"),
        "description": report_type.get("description", ""),
        "json": "",
        "html": "",
        "notes": report_type.get("missing_note", "Expected report was not found."),
    }


def _found_report_visibility_row(
    project_root: Path,
    report_type: Dict[str, Any],
    json_path: Optional[Path],
    html_path: Optional[Path],
) -> Dict[str, Any]:
    label_path = json_path or html_path
    return {
        "day": report_type["day"],
        "title": report_type["title"],
        "report_type": report_type.get("report_type", "Report evidence"),
        "device": _report_device_label(label_path, report_type["title"]),
        "status": "FOUND" if json_path or html_path else "MISSING",
        "safety": report_type.get("safety_label", "report-only evidence"),
        "description": report_type.get("description", ""),
        "json": _relative_to_project(project_root, json_path) if json_path else "MISSING",
        "html": _relative_to_project(project_root, html_path) if html_path else "MISSING",
        "notes": "",
    }


def _normalize_report_visibility_rows(
    project_root: Path,
    report_type: Dict[str, Any],
    scanned_paths: Dict[str, List[Path]],
) -> List[Dict[str, Any]]:
    json_paths = scanned_paths["json_paths"]
    html_paths = scanned_paths["html_paths"]
    if not json_paths and not html_paths:
        return [_missing_report_visibility_row(report_type)]

    rows: List[Dict[str, Any]] = []
    max_count = max(len(json_paths), len(html_paths))
    for index in range(max_count):
        json_path = json_paths[index] if index < len(json_paths) else None
        html_path = html_paths[index] if index < len(html_paths) else None
        rows.append(_found_report_visibility_row(project_root, report_type, json_path, html_path))
    return rows


def _attach_day18_runner_evidence(rows: List[Dict[str, Any]], project_root: Path) -> None:
    day18_evidence = build_day18_runner_evidence(project_root)
    for row in rows:
        if row.get("day") == "Day18" and row.get("title") == WIREGUARD_RUNNER_DISPLAY_NAME:
            row["day18_evidence"] = day18_evidence
            row["notes"] = _format_day18_console_note(day18_evidence)


def _disabled_day13_live_execution_row() -> Dict[str, Any]:
    return {
        "day": "Day13",
        "title": "Day13 WireGuard Live Execution",
        "report_type": "Disabled live workflow",
        "device": "Runner guardrail",
        "status": "DISABLED FOR DAY18",
        "safety": "disabled guardrail",
        "description": "Day13 live execution is intentionally not exposed through the Day18 runner safety layer.",
        "json": "",
        "html": "",
        "notes": "Day13 live WireGuard execution remains disabled until its own runner safety layer is implemented.",
    }


def discover_report_visibility(project_root: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for report_type in REPORT_CATALOG:
        scanned_paths = _scan_report_catalog_item(project_root, report_type)
        rows.extend(_normalize_report_visibility_rows(project_root, report_type, scanned_paths))

    _attach_day18_runner_evidence(rows, project_root)
    rows.append(_disabled_day13_live_execution_row())
    return rows


def _safe_nested_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_day18_runner_evidence(project_root: Path) -> Dict[str, Any]:
    json_path = project_root / WIREGUARD_RUNNER_REPORT_JSON
    html_path = project_root / WIREGUARD_RUNNER_REPORT_HTML
    evidence: Dict[str, Any] = {
        "runner_json": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
        "runner_html": WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
        "runner_json_exists": json_path.exists(),
        "runner_html_exists": html_path.exists(),
        "selected_config_path": "Not available",
        "delegated_day12_json": "Not available",
        "delegated_day12_html": "Not available",
        "final_vpn_connectivity": "Not available",
        "iperf_forward_mbps": "Not available",
        "iperf_reverse_mbps": "Not available",
        "runner_safety_guardrail_status": {},
        "parse_warning": "",
    }
    if not json_path.exists():
        return evidence

    try:
        report = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        evidence["parse_warning"] = f"Could not parse Day18 runner report: {exc}"
        return evidence

    delegated_report = _safe_nested_dict(report.get("delegated_report"))
    delegated_summary = _safe_nested_dict(report.get("delegated_result_summary"))
    guardrails = _safe_nested_dict(report.get("safety_guardrail_status"))
    evidence.update(
        mask_secret_values(
            {
                "selected_config_path": report.get("selected_config_path") or "Not available",
                "delegated_day12_json": delegated_report.get("json") or "Not available",
                "delegated_day12_html": delegated_report.get("html") or "Not available",
                "final_vpn_connectivity": delegated_summary.get("final_vpn_connectivity") or "Not available",
                "iperf_forward_mbps": delegated_summary.get("iperf_forward_mbps", "Not available"),
                "iperf_reverse_mbps": delegated_summary.get("iperf_reverse_mbps", "Not available"),
                "runner_safety_guardrail_status": guardrails,
            }
        )
    )
    return evidence


def _format_day18_console_note(evidence: Dict[str, Any]) -> str:
    if not evidence.get("runner_json_exists"):
        return f"Expected Day18 runner report: {evidence['runner_json']}"
    return (
        f"config={evidence.get('selected_config_path')}; "
        f"vpn={evidence.get('final_vpn_connectivity')}; "
        f"iperf={evidence.get('iperf_forward_mbps')}/{evidence.get('iperf_reverse_mbps')} Mbps"
    )


def _compact_guardrail_status(guardrails: Dict[str, Any]) -> str:
    if not guardrails:
        return "Not available"
    return ", ".join(f"{key}={value}" for key, value in guardrails.items())


def _print_report_visibility(rows: List[Dict[str, Any]], output_path: str = "reports/report_index.html") -> None:
    print(format_heading("Report Index"))
    counts = _count_report_statuses(rows)
    status_width = max(22, max(len(str(row.get("status", ""))) + 2 for row in rows))
    print(
        "Summary: "
        f"found={color_text(str(counts['found']), 'green', bold=True)} "
        f"missing={color_text(str(counts['missing']), 'yellow', bold=True)} "
        f"disabled={color_text(str(counts['disabled']), 'blue', bold=True)}"
    )
    print(f"Output: {output_path}")

    current_key: Optional[Tuple[str, str]] = None
    group_rows: List[Dict[str, Any]] = []

    def flush_group() -> None:
        if not group_rows:
            return
        first = group_rows[0]
        print()
        print(format_heading(f"{first['title']} ({first['day']})"))
        print(f"  {'Status':<{status_width}} {'Device':<24} {'Safety':<28} Report paths")
        print(f"  {'-' * status_width} {'-' * 24} {'-' * 28} {'-' * 42}")
        visible_rows, hidden_count = _compact_console_report_rows(group_rows)
        for visible_row in visible_rows:
            _print_report_visibility_row(visible_row, status_width)
        if hidden_count:
            print(
                f"  ... {hidden_count} more reports hidden in console; "
                f"open {output_path} for full list"
            )

    for row in rows:
        key = (str(row["day"]), str(row["title"]))
        if current_key is None:
            current_key = key
        if key != current_key:
            flush_group()
            group_rows = []
            current_key = key
        group_rows.append(row)
    flush_group()


def _compact_console_report_rows(
    rows: List[Dict[str, Any]],
    max_default_rows: int = 3,
) -> Tuple[List[Dict[str, Any]], int]:
    special_rows = [
        row
        for row in rows
        if str(row.get("status", "")).upper() == "MISSING"
        or "DISABLED" in str(row.get("status", "")).upper()
    ]
    visible_ids = {id(row) for row in special_rows}
    remaining_slots = max(0, max_default_rows - len(special_rows))
    for row in rows:
        if id(row) in visible_ids:
            continue
        if remaining_slots <= 0:
            break
        special_rows.append(row)
        visible_ids.add(id(row))
        remaining_slots -= 1
    hidden_count = len(rows) - len(visible_ids)
    return special_rows, hidden_count


def _print_report_visibility_row(row: Dict[str, Any], status_width: int) -> None:
    status = _format_report_visibility_status(str(row["status"]))
    safety = str(row.get("safety", ""))[:28]
    print(f"  {status:<{status_width}} {str(row['device'])[:24]:<24} {safety:<28} JSON: {row.get('json') or '-'}")
    if row.get("html"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} HTML: {row['html']}")
    if row.get("notes"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} Notes: {row['notes']}")
    evidence = row.get("day18_evidence")
    if isinstance(evidence, dict) and evidence.get("runner_json_exists"):
        print(f"  {'':<{status_width}} {'':<24} {'':<28} Day12 JSON: {evidence.get('delegated_day12_json')}")
        print(
            f"  {'':<{status_width}} {'':<24} {'':<28} Guardrails: "
            f"{_compact_guardrail_status(_safe_nested_dict(evidence.get('runner_safety_guardrail_status')))}"
        )


def _count_report_statuses(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"found": 0, "missing": 0, "disabled": 0}
    for row in rows:
        status = str(row.get("status", "")).upper()
        if status == "FOUND":
            counts["found"] += 1
        elif status == "MISSING":
            counts["missing"] += 1
        elif "DISABLED" in status:
            counts["disabled"] += 1
    return counts


def _format_report_visibility_status(status: str) -> str:
    normalized = status.upper()
    if normalized == "FOUND":
        return color_text("[FOUND]", "green", bold=True)
    if normalized == "MISSING":
        return color_text("[MISSING]", "yellow", bold=True)
    if "DISABLED" in normalized:
        return color_text(f"[{normalized}]", "blue", bold=True)
    return color_text(f"[{normalized}]", "gray", bold=True)


def _html_link_or_text(output_path: Path, project_root: Path, value: str) -> str:
    if not value or value == "MISSING":
        return html.escape(value or "")
    target = project_root / value
    if target.suffix.lower() == ".html" and target.exists():
        href = build_relative_link(output_path, target)
        return f'<a href="{html.escape(href)}">{html.escape(value)}</a>'
    return html.escape(value)


def _css_token(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def _day18_evidence_for_html(report_rows: List[Dict[str, Any]], project_root: Path) -> Dict[str, Any]:
    for row in report_rows:
        evidence = row.get("day18_evidence")
        if isinstance(evidence, dict):
            return evidence
    return build_day18_runner_evidence(project_root)


def _render_day18_evidence_html(evidence: Dict[str, Any], output_path: Path, project_root: Path) -> str:
    guardrails = _safe_nested_dict(evidence.get("runner_safety_guardrail_status"))
    guardrail_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in guardrails.items()
    ) or "<tr><td colspan=\"2\">Not available</td></tr>"
    detail_rows = [
        ("Day18 runner JSON", _html_link_or_text(output_path, project_root, str(evidence.get("runner_json", "")))),
        ("Day18 runner HTML", _html_link_or_text(output_path, project_root, str(evidence.get("runner_html", "")))),
        ("Delegated Day12 JSON", _html_link_or_text(output_path, project_root, str(evidence.get("delegated_day12_json", "")))),
        ("Delegated Day12 HTML", _html_link_or_text(output_path, project_root, str(evidence.get("delegated_day12_html", "")))),
        ("Selected WireGuard config", html.escape(str(evidence.get("selected_config_path", "Not available")))),
        ("Final VPN connectivity", html.escape(str(evidence.get("final_vpn_connectivity", "Not available")))),
        ("iperf forward Mbps", html.escape(str(evidence.get("iperf_forward_mbps", "Not available")))),
        ("iperf reverse Mbps", html.escape(str(evidence.get("iperf_reverse_mbps", "Not available")))),
    ]
    if evidence.get("parse_warning"):
        detail_rows.append(("Parse warning", html.escape(str(evidence["parse_warning"]))))
    rows = "\n".join(f"<tr><td>{html.escape(label)}</td><td>{value}</td></tr>" for label, value in detail_rows)
    return f"""
    <h2>Day18 WireGuard Runner Evidence</h2>
    <div class="warning">Day18 runner evidence is summarized from the runner report. Day12 remains the detailed source of truth for WireGuard validation.</div>
    <table>
      <thead><tr><th>Field</th><th>Value</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <h2>Day18 Runner Guardrails</h2>
    <table>
      <thead><tr><th>Guardrail</th><th>Status</th></tr></thead>
      <tbody>{guardrail_rows}</tbody>
    </table>
"""


def _render_vrrp_evidence_index_html(entries: List[Dict[str, Any]], output_path: Path, project_root: Path) -> str:
    summary = summarize_vrrp_evidence(entries)
    counts = summary["counts"]
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(entry.get('group', '')))}</td>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(entry.get('day', '')))}</span></td>"
        f"<td>{html.escape(str(entry.get('title', '')))}</td>"
        f"<td>{html.escape(str(entry.get('artifact_type', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(entry.get('status', 'MISSING')))}\">{html.escape(str(entry.get('status', 'MISSING')))}</span></td>"
        f"<td><span class=\"pill safety-{_css_token(str(entry.get('safety_level', 'report-only')))}\">{html.escape(str(entry.get('safety_level', 'report-only')))}</span></td>"
        f"<td>{_html_artifact_link_or_text(output_path, project_root, str(entry.get('path', '')))}</td>"
        f"<td>{html.escape(str(entry.get('demo_relevance', '')))}</td>"
        "</tr>"
        for entry in entries
    ) or "<tr><td colspan=\"8\">No HA / VRRP evidence entries configured.</td></tr>"
    return f"""
    <h2>HA / VRRP Evidence</h2>
    <div class="warning">Day39 evidence integration is report-only: it reads Day31-Day38 local docs, diagrams, profiles, and generated reports without SSH, live tests, or configuration changes.</div>
    <section class="summary light-summary">
      <div class="metric"><div class="metric-label">VRRP Artifacts</div><div class="metric-value">{counts['total']}</div></div>
      <div class="metric"><div class="metric-label">Found</div><div class="metric-value">{counts['found']}</div></div>
      <div class="metric"><div class="metric-label">Missing</div><div class="metric-value">{counts['missing']}</div></div>
      <div class="metric"><div class="metric-label">Not Generated</div><div class="metric-value">{counts['not_generated']}</div></div>
    </section>
    <table>
      <thead><tr><th>Group</th><th>Day</th><th>Artifact</th><th>Type</th><th>Status</th><th>Safety</th><th>Path</th><th>Demo relevance</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
"""


def write_report_index_html(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
    output_path: Path,
    project_root: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().replace(microsecond=0).isoformat(sep=" ")
    counts = _count_report_statuses(report_rows)
    task_rows = "\n".join(
        "<tr>"
        f"<td><code>{html.escape(str(task['task_id']))}</code></td>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(task['day']))}</span></td>"
        f"<td>{html.escape(str(task['display_name']))}</td>"
        f"<td>{html.escape(str(task['category']))}</td>"
        f"<td><span class=\"pill safety-{_css_token(str(task['safety_level']))}\">{html.escape(str(task['safety_level']))}</span></td>"
        f"<td><span class=\"pill {'enabled' if task['enabled'] else 'disabled'}\">{'yes' if task['enabled'] else 'no'}</span></td>"
        f"<td>{html.escape(str(task['execution_mode']))}</td>"
        f"<td>{'yes' if task['requires_live_device'] else 'no'}</td>"
        "</tr>"
        for task in task_catalog
    )
    report_table_rows = "\n".join(
        "<tr>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(row['day']))}</span></td>"
        f"<td>{html.escape(str(row['title']))}</td>"
        f"<td>{html.escape(str(row.get('report_type', 'Report evidence')))}</td>"
        f"<td>{html.escape(str(row['device']))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(row['status']))}\">{html.escape(str(row['status']))}</span></td>"
        f"<td><span class=\"pill safety-{_css_token(str(row.get('safety', 'report-only')))}\">{html.escape(str(row.get('safety', 'report-only')))}</span></td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('json', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(row.get('html', '')))}</td>"
        f"<td>{html.escape(str(row.get('description', '')))}</td>"
        f"<td>{html.escape(str(row.get('notes', '')))}</td>"
        "</tr>"
        for row in report_rows
    )
    safety_rows = "\n".join(
        f"<tr><td><span class=\"pill safety-{_css_token(level)}\">{html.escape(level)}</span></td><td>{html.escape(description)}</td></tr>"
        for level, description in SAFETY_LEVELS.items()
    )
    day18_evidence_html = _render_day18_evidence_html(
        _day18_evidence_for_html(report_rows, project_root),
        output_path,
        project_root,
    )
    vrrp_evidence_html = _render_vrrp_evidence_index_html(
        discover_vrrp_evidence(project_root),
        output_path,
        project_root,
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Network Automation Lab Report Index</title>
  <style>
    :root {{
      --bg: #f4f7fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #27364a;
      --blue: #155bb5;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
      --red-bg: #fdecec;
      --red: #b42318;
      --blue-bg: #e6f0ff;
      --blue-ink: #1849a9;
      --gray-bg: #eef2f6;
      --gray: #475467;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); box-shadow: 0 10px 24px rgba(16, 24, 40, .06); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    tr:nth-child(even) td {{ background: #fafcff; }}
    code {{ font-family: Consolas, "Courier New", monospace; overflow-wrap: anywhere; }}
    a {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .meta {{ color: #dbe5f3; }}
    .warning {{ background: var(--yellow-bg); border: 1px solid #f0c66a; border-radius: 8px; padding: 12px 14px; margin: 18px 0 20px; color: var(--yellow); }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .light-summary {{ margin-bottom: 14px; }}
    .light-summary .metric {{ background: var(--panel); border-color: var(--line); }}
    .light-summary .metric-label {{ color: var(--muted); }}
    .light-summary .metric-value {{ color: var(--ink); }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .pill-day {{ background: var(--gray-bg); color: var(--gray); }}
    .enabled, .status-found {{ background: var(--green-bg); color: var(--green); }}
    .disabled, .status-disabled-for-day18, .safety-future-reserved {{ background: var(--blue-bg); color: var(--blue-ink); }}
    .status-missing, .status-not-generated {{ background: var(--yellow-bg); color: var(--yellow); }}
    .safety-safe-read-only {{ background: var(--green-bg); color: var(--green); }}
    .safety-live-read-only {{ background: #e7f0fb; color: #175cd3; }}
    .safety-live-performance {{ background: #f3e8ff; color: #6941c6; }}
    .safety-live-config-change {{ background: var(--red-bg); color: var(--red); }}
    .safety-guarded-live {{ background: #ecfdf3; color: #067647; }}
    @media (max-width: 820px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Network Automation Lab Report Index</h1>
    <div class="meta">Generated {html.escape(generated_at)}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Tasks</div><div class="metric-value">{len(task_catalog)}</div></div>
      <div class="metric"><div class="metric-label">Reports Found</div><div class="metric-value">{counts['found']}</div></div>
      <div class="metric"><div class="metric-label">Missing</div><div class="metric-value">{counts['missing']}</div></div>
      <div class="metric"><div class="metric-label">Disabled</div><div class="metric-value">{counts['disabled']}</div></div>
    </section>
  </header>
  <main>
    <div class="warning">Day18 WireGuard runner integration uses a safety layer: dry-run by default, explicit live confirmation, fixed argv execution, and no peer/firewall write flags.</div>
    {day18_evidence_html}
    {vrrp_evidence_html}
    <h2>Task Catalog Summary</h2>
    <table>
      <thead><tr><th>Task ID</th><th>Day</th><th>Name</th><th>Category</th><th>Safety</th><th>Enabled</th><th>Mode</th><th>Live Device</th></tr></thead>
      <tbody>{task_rows}</tbody>
    </table>
    <h2>Report Visibility</h2>
    <table>
      <thead><tr><th>Day</th><th>Task Name</th><th>Report Type</th><th>Device</th><th>Status</th><th>Safety</th><th>JSON</th><th>HTML</th><th>Description</th><th>Notes</th></tr></thead>
      <tbody>{report_table_rows}</tbody>
    </table>
    <h2>Safety Level Legend</h2>
    <table>
      <thead><tr><th>Safety Level</th><th>Description</th></tr></thead>
      <tbody>{safety_rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def write_day39_vrrp_evidence_html(report: Dict[str, Any], output_path: Path, project_root: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = report.get("summary", {})
    counts = summary.get("counts", {}) if isinstance(summary, dict) else {}
    rows = _render_vrrp_evidence_rows(report.get("evidence", []), output_path, project_root)
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day39 VRRP Evidence Dashboard Integration</title>
  <style>
    :root {{ --bg: #f5f7fb; --ink: #172033; --muted: #617089; --line: #d8e0ec; --panel: #ffffff; --head: #27364a; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ padding: 34px 38px 24px; background: var(--head); color: white; }}
    main {{ padding: 28px 38px 46px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .meta {{ color: #dbe5f3; }}
    .notice {{ background: #fff4d8; border: 1px solid #f0c66a; border-radius: 8px; padding: 12px 14px; margin: 18px 0 20px; color: #8a6100; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin: 20px 0; }}
    .metric {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }}
    .metric .label {{ color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric .value {{ margin-top: 5px; font-size: 22px; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    a {{ color: #155bb5; font-weight: 700; text-decoration: none; }}
    .badge {{ display: inline-block; min-width: 92px; padding: 4px 8px; border-radius: 999px; font-weight: 800; font-size: 12px; text-align: center; }}
    .badge-found, .badge-pass {{ background: #dff7e8; color: #136b35; }}
    .badge-missing, .badge-not_generated, .badge-warn {{ background: #fff3cc; color: #856100; }}
    .badge-unknown {{ background: #e5e7ff; color: #393a8a; }}
    @media (max-width: 820px) {{ header, main {{ padding-left: 16px; padding-right: 16px; }} .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} table {{ display: block; overflow-x: auto; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Day39 VRRP Evidence Dashboard Integration</h1>
    <div class="meta">Generated {html.escape(str(report.get("generated_at", "")))} · Overall {_status_badge(str(report.get("overall_status", "UNKNOWN")))}</div>
  </header>
  <main>
    <div class="notice">Report-only integration. Day39 did not run live tests, open SSH, change RouterOS/Cisco/firewall/NAT/IP/VRRP settings, or require lab connectivity.</div>
    <section class="summary">
      <div class="metric"><div class="label">Artifacts</div><div class="value">{counts.get("total", 0)}</div></div>
      <div class="metric"><div class="label">Found</div><div class="value">{counts.get("found", 0)}</div></div>
      <div class="metric"><div class="label">Missing</div><div class="value">{counts.get("missing", 0)}</div></div>
      <div class="metric"><div class="label">Not Generated</div><div class="value">{counts.get("not_generated", 0)}</div></div>
    </section>
    <h2>HA / VRRP Evidence</h2>
    <table>
      <thead><tr><th>Group</th><th>Day</th><th>Artifact</th><th>Type</th><th>Status</th><th>Safety</th><th>Path</th><th>Demo relevance</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def write_day40_demo_readiness_html(report: Dict[str, Any], output_path: Path, project_root: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    included = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("scope_included", []))
    excluded = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("scope_excluded", []))
    checklist_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('category', '')))}</td>"
        f"<td>{html.escape(str(item.get('item', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(item.get('status', '')))}\">{html.escape(str(item.get('status', '')))}</span></td>"
        "</tr>"
        for item in report.get("demo_checklist", [])
    )
    milestone_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('day', '')))}</td>"
        f"<td>{html.escape(str(item.get('summary', '')))}</td>"
        f"<td>{html.escape(str(item.get('status', '')))}</td>"
        "</tr>"
        for item in report.get("day31_to_day39_summary", [])
    )
    traceability_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('day', '')))}</td>"
        f"<td>{html.escape(str(item.get('artifact', '')))}</td>"
        f"<td>{html.escape(str(item.get('artifact_type', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(item.get('status', '')))}\">{html.escape(str(item.get('status', '')))}</span></td>"
        f"<td>{html.escape(str(item.get('safety_level', '')))}</td>"
        f"<td>{_html_artifact_link_or_text(output_path, project_root, str(item.get('path', '')))}</td>"
        f"<td>{html.escape(str(item.get('demo_relevance', '')))}</td>"
        "</tr>"
        for item in report.get("evidence_traceability", [])
    )
    walkthrough_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('step', '')))}</td>"
        f"<td>{html.escape(str(item.get('surface', '')))}</td>"
        f"<td>{html.escape(str(item.get('check', '')))}</td>"
        "</tr>"
        for item in report.get("dashboard_walkthrough", [])
    )
    limitations = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("known_limitations", []))
    next_steps = "".join(
        f"<li><strong>{html.escape(str(item.get('day', '')))}</strong>: {html.escape(str(item.get('item', '')))}</li>"
        for item in report.get("next_steps", [])
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day40 v0.2 Demo Readiness Review</title>
  <style>
    :root {{ --bg: #f6f8fb; --ink: #182230; --muted: #667085; --line: #d8e0ec; --panel: #ffffff; --head: #243447; --green-bg: #e7f7ee; --green: #147a3d; --yellow-bg: #fff4d8; --yellow: #8a6100; --blue-bg: #e8f1ff; --blue: #175cd3; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 34px 38px 24px; }}
    main {{ padding: 28px 38px 46px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .meta {{ color: #dbe5f3; }}
    .notice {{ background: var(--yellow-bg); border: 1px solid #f0c66a; border-radius: 8px; padding: 12px 14px; margin: 18px 0 20px; color: var(--yellow); }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .split {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    a {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .status-pass, .status-found {{ background: var(--green-bg); color: var(--green); }}
    .status-missing, .status-not-generated {{ background: var(--yellow-bg); color: var(--yellow); }}
    .status-not-generated {{ background: var(--blue-bg); color: var(--blue); }}
    @media (max-width: 900px) {{ header, main {{ padding-left: 16px; padding-right: 16px; }} .summary, .split {{ grid-template-columns: 1fr; }} table {{ display: block; overflow-x: auto; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Day40 v0.2 Demo Readiness Review and Scope Lock</h1>
    <div class="meta">Generated {html.escape(str(report.get("generated_at", "")))} · Overall {html.escape(str(report.get("overall_status", "")))}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Task Type</div><div class="metric-value">{html.escape(str(report.get("task_type", "")))}</div></div>
      <div class="metric"><div class="metric-label">Readiness</div><div class="metric-value">{html.escape(str(report.get("demo_readiness_status", "")))}</div></div>
      <div class="metric"><div class="metric-label">Live Test</div><div class="metric-value">{html.escape(str(report.get("live_test", "")))}</div></div>
      <div class="metric"><div class="metric-label">SSH Used</div><div class="metric-value">{html.escape(str(report.get("ssh_used", "")))}</div></div>
    </section>
  </header>
  <main>
    <div class="notice">{html.escape(str(report.get("safety_statement", "")))}</div>
    <section class="split">
      <div class="panel"><h2>Included Scope</h2><ul>{included}</ul></div>
      <div class="panel"><h2>Excluded Scope</h2><ul>{excluded}</ul></div>
    </section>
    <h2>Day31-Day39 Milestone Summary</h2>
    <table><thead><tr><th>Day</th><th>Summary</th><th>Status</th></tr></thead><tbody>{milestone_rows}</tbody></table>
    <h2>Demo Readiness Checklist</h2>
    <table><thead><tr><th>Category</th><th>Check</th><th>Status</th></tr></thead><tbody>{checklist_rows}</tbody></table>
    <h2>Evidence Traceability</h2>
    <table><thead><tr><th>Day</th><th>Artifact</th><th>Type</th><th>Status</th><th>Safety</th><th>Path</th><th>Demo relevance</th></tr></thead><tbody>{traceability_rows}</tbody></table>
    <h2>Dashboard Walkthrough Checks</h2>
    <table><thead><tr><th>Step</th><th>Surface</th><th>Check</th></tr></thead><tbody>{walkthrough_rows}</tbody></table>
    <section class="split">
      <div class="panel"><h2>Known Limitations</h2><ul>{limitations}</ul></div>
      <div class="panel"><h2>Recommended Next Steps</h2><ul>{next_steps}</ul></div>
    </section>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def write_day41_release_packaging_html(report: Dict[str, Any], output_path: Path, project_root: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scope_rows = "\n".join(
        f"<li>{html.escape(str(item))}</li>" for item in report.get("included_release_scope", [])
    )
    doc_rows = "\n".join(
        "<tr>"
        f"<td>{_html_artifact_link_or_text(output_path, project_root, str(item.get('path', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(item.get('status', '')))}\">{html.escape(str(item.get('status', '')))}</span></td>"
        f"<td>{'yes' if item.get('required') else 'no'}</td>"
        "</tr>"
        for item in report.get("created_or_updated_docs", [])
    )
    limitations = "".join(f"<li>{html.escape(str(item))}</li>" for item in report.get("known_limitations", []))
    safety = report.get("safety_status", {})
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day41 v0.2 Release Packaging</title>
  <style>
    :root {{ --bg: #f6f8fb; --ink: #182230; --muted: #667085; --line: #d8e0ec; --panel: #ffffff; --head: #263447; --green-bg: #e7f7ee; --green: #147a3d; --yellow-bg: #fff4d8; --yellow: #8a6100; --blue: #175cd3; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 34px 38px 24px; }}
    main {{ padding: 28px 38px 46px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin-top: 30px; font-size: 20px; }}
    .meta {{ color: #dbe5f3; }}
    .notice {{ background: var(--yellow-bg); border: 1px solid #f0c66a; border-radius: 8px; padding: 12px 14px; margin: 18px 0 20px; color: var(--yellow); }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; font-size: 12px; text-transform: uppercase; color: #435066; }}
    a {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .status-pass, .status-found {{ background: var(--green-bg); color: var(--green); }}
    .status-missing, .status-warn {{ background: var(--yellow-bg); color: var(--yellow); }}
    @media (max-width: 900px) {{ header, main {{ padding-left: 16px; padding-right: 16px; }} .summary {{ grid-template-columns: 1fr; }} table {{ display: block; overflow-x: auto; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Day41 v0.2 Release Packaging</h1>
    <div class="meta">Generated {html.escape(str(report.get("generated_at", "")))} · Overall {html.escape(str(report.get("overall_status", "")))}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Task Type</div><div class="metric-value">{html.escape(str(report.get("task_type", "")))}</div></div>
      <div class="metric"><div class="metric-label">Live Test</div><div class="metric-value">{html.escape(str(report.get("live_test", "")))}</div></div>
      <div class="metric"><div class="metric-label">SSH Used</div><div class="metric-value">{html.escape(str(report.get("ssh_used", "")))}</div></div>
      <div class="metric"><div class="metric-label">v0.2 Tag</div><div class="metric-value">{html.escape(str(report.get("v0_2_tag_created", "")))}</div></div>
    </section>
  </header>
  <main>
    <div class="notice">Report-only release packaging. Day41 did not run live tests, open SSH, change device configuration, implement voice/AI features, or create a v0.2 tag.</div>
    <div class="panel"><h2>Purpose</h2><p>{html.escape(str(report.get("purpose", "")))}</p></div>
    <h2>Included Day31-Day40 Scope</h2>
    <div class="panel"><ul>{scope_rows}</ul></div>
    <h2>Package Documents</h2>
    <table><thead><tr><th>Path</th><th>Status</th><th>Required</th></tr></thead><tbody>{doc_rows}</tbody></table>
    <h2>Safety Status</h2>
    <table><thead><tr><th>Control</th><th>Value</th></tr></thead><tbody>
      <tr><td>Live execution</td><td>{html.escape(str(safety.get("live_execution", "")))}</td></tr>
      <tr><td>SSH required</td><td>{html.escape(str(safety.get("ssh_required", "")))}</td></tr>
      <tr><td>Device config change</td><td>{html.escape(str(safety.get("device_config_change", "")))}</td></tr>
      <tr><td>Generated reports allowed</td><td>{html.escape(str(safety.get("generated_reports_allowed", "")))}</td></tr>
    </tbody></table>
    <h2>Known Limitations</h2>
    <div class="panel"><ul>{limitations}</ul></div>
    <h2>Next Steps</h2>
    <div class="panel"><p><strong>Day42:</strong> {html.escape(str(report.get("day42_next_action", "")))}</p><p><strong>v3.0 roadmap:</strong> {html.escape(str(report.get("v3_0_roadmap_note", "")))}</p></div>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def _portfolio_evidence_area(row: Dict[str, Any]) -> str:
    title = str(row.get("title", "")).lower()
    day = str(row.get("day", ""))
    if "wireguard" in title:
        return "VPN validation"
    if "iperf" in title or "performance" in title:
        return "Performance"
    if "topology" in title:
        return "Topology"
    if "baseline" in title or "auto setup" in title:
        return "Baseline"
    if "runner" in title or "overview" in title:
        return "Runner"
    return day or "Evidence"


def _portfolio_evidence_quality(row: Dict[str, Any]) -> str:
    status = str(row.get("status", "")).upper()
    json_path = str(row.get("json", ""))
    html_path = str(row.get("html", ""))
    if status == "FOUND" and json_path != "MISSING" and html_path != "MISSING":
        return "READY"
    if status == "FOUND":
        return "PARTIAL"
    if "DISABLED" in status:
        return "GUARDED"
    return "MISSING"


def build_portfolio_evidence_index(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    counts = _count_report_statuses(report_rows)
    evidence_items = [
        {
            "day": row.get("day", ""),
            "area": _portfolio_evidence_area(row),
            "title": row.get("title", ""),
            "report_type": row.get("report_type", ""),
            "device": row.get("device", ""),
            "quality": _portfolio_evidence_quality(row),
            "source_status": row.get("status", ""),
            "safety": row.get("safety", ""),
            "json": row.get("json", ""),
            "html": row.get("html", ""),
            "description": row.get("description", ""),
            "notes": row.get("notes", ""),
        }
        for row in report_rows
    ]
    local_only_tasks = [
        task
        for task in task_catalog
        if not task.get("requires_live_device") and task.get("safety_level") == "report-only"
    ]
    live_guarded_tasks = [
        task
        for task in task_catalog
        if task.get("requires_live_device") or "live" in str(task.get("safety_level", "")).lower()
    ]
    readiness = "READY_WITH_GAPS" if counts["found"] else "NEEDS_LOCAL_REPORTS"
    if counts["found"] and not counts["missing"]:
        readiness = "READY"

    return mask_secret_values(
        {
            "day": "Day19",
            "name": "Runner Evidence Index and Portfolio Finalization",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "portfolio_readiness": readiness,
            "summary": {
                "tasks": len(task_catalog),
                "local_only_tasks": len(local_only_tasks),
                "live_or_guarded_tasks": len(live_guarded_tasks),
                "reports_found": counts["found"],
                "reports_missing": counts["missing"],
                "disabled_guardrails": counts["disabled"],
            },
            "portfolio_highlights": [
                "Unified runner lists safe local tasks separately from guarded live workflows.",
                "Evidence index links JSON and HTML reports without reading config.json or exported WireGuard configs.",
                "WireGuard runner remains dry-run by default and requires explicit live authorization.",
                "Generated Day19 output is suitable for portfolio screenshots and final review.",
            ],
            "evidence_items": evidence_items,
        }
    )


def write_portfolio_evidence_html(
    evidence: Dict[str, Any],
    output_path: Path,
    project_root: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary = evidence.get("summary", {})
    evidence_rows = "\n".join(
        "<tr>"
        f"<td><span class=\"pill pill-day\">{html.escape(str(item.get('day', '')))}</span></td>"
        f"<td>{html.escape(str(item.get('area', '')))}</td>"
        f"<td>{html.escape(str(item.get('title', '')))}</td>"
        f"<td>{html.escape(str(item.get('report_type', '')))}</td>"
        f"<td>{html.escape(str(item.get('device', '')))}</td>"
        f"<td><span class=\"pill quality-{_css_token(str(item.get('quality', '')))}\">{html.escape(str(item.get('quality', '')))}</span></td>"
        f"<td>{html.escape(str(item.get('safety', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(item.get('json', '')))}</td>"
        f"<td>{_html_link_or_text(output_path, project_root, str(item.get('html', '')))}</td>"
        f"<td>{html.escape(str(item.get('description', '')))}</td>"
        f"<td>{html.escape(str(item.get('notes', '')))}</td>"
        "</tr>"
        for item in evidence.get("evidence_items", [])
    )
    highlights = "".join(
        f"<li>{html.escape(str(item))}</li>"
        for item in evidence.get("portfolio_highlights", [])
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day19 Runner Evidence Index</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #243447;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
      --blue-bg: #e6f0ff;
      --blue: #1849a9;
      --gray-bg: #eef2f6;
      --gray: #475467;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    a {{ color: #155bb5; font-weight: 700; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .meta {{ color: #dbe5f3; }}
    .summary {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; margin-top: 18px; }}
    .metric {{ background: rgba(255, 255, 255, .10); border: 1px solid rgba(255, 255, 255, .20); border-radius: 8px; padding: 13px 14px; }}
    .metric-label {{ color: #dbe5f3; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .metric-value {{ margin-top: 4px; font-size: 24px; font-weight: 800; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .pill-day, .quality-missing {{ background: var(--gray-bg); color: var(--gray); }}
    .quality-ready {{ background: var(--green-bg); color: var(--green); }}
    .quality-partial {{ background: var(--yellow-bg); color: var(--yellow); }}
    .quality-guarded {{ background: var(--blue-bg); color: var(--blue); }}
    .highlights {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Day19 Runner Evidence Index</h1>
    <div class="meta">{html.escape(str(evidence.get("name", "")))} · Generated {html.escape(str(evidence.get("generated_at", "")))}</div>
    <section class="summary">
      <div class="metric"><div class="metric-label">Readiness</div><div class="metric-value">{html.escape(str(evidence.get("portfolio_readiness", "")))}</div></div>
      <div class="metric"><div class="metric-label">Tasks</div><div class="metric-value">{summary.get("tasks", 0)}</div></div>
      <div class="metric"><div class="metric-label">Found</div><div class="metric-value">{summary.get("reports_found", 0)}</div></div>
      <div class="metric"><div class="metric-label">Missing</div><div class="metric-value">{summary.get("reports_missing", 0)}</div></div>
      <div class="metric"><div class="metric-label">Guardrails</div><div class="metric-value">{summary.get("disabled_guardrails", 0)}</div></div>
    </section>
  </header>
  <main>
    <h2>Portfolio Highlights</h2>
    <ul class="highlights">{highlights}</ul>
    <h2>Evidence Items</h2>
    <table>
      <thead><tr><th>Day</th><th>Area</th><th>Evidence</th><th>Report Type</th><th>Device</th><th>Quality</th><th>Safety</th><th>JSON</th><th>HTML</th><th>Description</th><th>Notes</th></tr></thead>
      <tbody>{evidence_rows}</tbody>
    </table>
  </main>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def build_day24_demo_flow(
    task_catalog: List[Dict[str, Any]],
    report_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    task_ids = {str(task.get("id", "")) for task in task_catalog}
    available_titles = {
        str(row.get("title", ""))
        for row in report_rows
        if str(row.get("status", "")).upper() != "MISSING"
    }
    walkthrough_steps = [
        {
            "order": 1,
            "section": "Scope",
            "demo_action": "Open the README and explain the lab goal, supported devices, and current Day1-Day24 scope.",
            "command_or_location": "README.md",
            "talk_track": "This is a QA/SDET network automation lab focused on repeatable validation and readable evidence, not one-off screenshots.",
            "evidence": "Project overview, progress table, and safety sections.",
        },
        {
            "order": 2,
            "section": "Runner Safety",
            "demo_action": "Show the task catalog with verbose metadata.",
            "command_or_location": "python network_lab.py --list-tasks --verbose",
            "talk_track": "The runner separates report-only, read-only, dry-run, guarded-live, and disabled workflows before anyone can trigger live lab behavior.",
            "evidence": "Task IDs, safety levels, execution modes, report paths, and notes.",
        },
        {
            "order": 3,
            "section": "Evidence Index",
            "demo_action": "Generate or open the local report visibility index.",
            "command_or_location": "python network_lab.py --report-index",
            "talk_track": "Report visibility reads existing JSON/HTML files, marks missing evidence clearly, and does not connect to routers, switches, VPN clients, or iperf3 endpoints.",
            "evidence": DAY17_REPORT_INDEX_HTML.as_posix(),
        },
        {
            "order": 4,
            "section": "Dashboard Walkthrough",
            "demo_action": "Start the dashboard and open the read-only report viewer.",
            "command_or_location": "python dashboard_app.py -> http://127.0.0.1:5000/reports",
            "talk_track": "The dashboard is the human review surface: grouped evidence cards, redacted JSON preview, and safe links to already-generated HTML reports.",
            "evidence": "Day21 dashboard /reports viewer.",
        },
        {
            "order": 5,
            "section": "WireGuard Safety Boundary",
            "demo_action": "Run or show the WireGuard runner dry-run.",
            "command_or_location": "python network_lab.py --task wireguard-runner --dry-run",
            "talk_track": "WireGuard validation is intentionally dry-run by default, with guarded live delegation only after explicit authorization and without unsafe write flags.",
            "evidence": WIREGUARD_RUNNER_REPORT_HTML.as_posix(),
        },
        {
            "order": 6,
            "section": "Portfolio Close",
            "demo_action": "Open the Day19 portfolio index, then this Day24 walkthrough artifact.",
            "command_or_location": "python network_lab.py --portfolio-finalize; python network_lab.py --task demo-flow",
            "talk_track": "The portfolio view ties together evidence quality, missing gaps, guardrails, and the recommended reviewer path for the RC.",
            "evidence": f"{DAY19_EVIDENCE_INDEX_HTML.as_posix()} and {DAY24_DEMO_FLOW_HTML.as_posix()}",
        },
    ]
    checklist = [
        {
            "item": "Task catalog includes report-only demo flow",
            "status": "PASS" if "demo-flow" in task_ids else "MISSING",
        },
        {
            "item": "Report visibility has at least one local evidence row",
            "status": "PASS" if available_titles else "MISSING",
        },
        {
            "item": "WireGuard runner remains guarded or dry-run",
            "status": "PASS"
            if any(task.get("id") == WIREGUARD_RUNNER_TASK_ALIAS and task.get("execution_mode") == "dry-run" for task in task_catalog)
            else "MISSING",
        },
        {
            "item": "Day13 live runner path remains disabled",
            "status": "PASS"
            if any(task.get("id") == "day13-wireguard-summary" and not task.get("enabled") for task in task_catalog)
            else "MISSING",
        },
        {
            "item": "Portfolio index task remains local-only",
            "status": "PASS"
            if any(task.get("id") == "portfolio-finalize" and not task.get("requires_live_device") for task in task_catalog)
            else "MISSING",
        },
    ]
    return mask_secret_values(
        {
            "day": "Day24",
            "name": "RC Demo Flow and Portfolio Walkthrough",
            "generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            "mode": "report-only",
            "result": "READY" if all(item["status"] == "PASS" for item in checklist) else "READY_WITH_GAPS",
            "safety_summary": [
                "No live workflows are executed by this demo-flow task.",
                "No config.json, WireGuard .conf files, SSH passwords, or private keys are read.",
                "Live validation remains behind existing guarded runner paths.",
            ],
            "walkthrough_steps": walkthrough_steps,
            "rc_checklist": checklist,
            "recommended_open_order": [
                "README.md",
                "docs/portfolio_evidence.md",
                DAY17_REPORT_INDEX_HTML.as_posix(),
                "http://127.0.0.1:5000/reports",
                DAY19_EVIDENCE_INDEX_HTML.as_posix(),
                DAY24_DEMO_FLOW_HTML.as_posix(),
            ],
        }
    )


def write_day24_demo_flow_html(
    demo_flow: Dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    steps = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(step.get('order', '')))}</td>"
        f"<td>{html.escape(str(step.get('section', '')))}</td>"
        f"<td>{html.escape(str(step.get('demo_action', '')))}</td>"
        f"<td><code>{html.escape(str(step.get('command_or_location', '')))}</code></td>"
        f"<td>{html.escape(str(step.get('talk_track', '')))}</td>"
        f"<td>{html.escape(str(step.get('evidence', '')))}</td>"
        "</tr>"
        for step in demo_flow.get("walkthrough_steps", [])
    )
    checklist = "\n".join(
        "<tr>"
        f"<td>{html.escape(str(item.get('item', '')))}</td>"
        f"<td><span class=\"pill status-{_css_token(str(item.get('status', '')))}\">{html.escape(str(item.get('status', '')))}</span></td>"
        "</tr>"
        for item in demo_flow.get("rc_checklist", [])
    )
    safety = "".join(f"<li>{html.escape(str(item))}</li>" for item in demo_flow.get("safety_summary", []))
    open_order = "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in demo_flow.get("recommended_open_order", []))
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Day24 RC Demo Flow</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d8e0ec;
      --head: #243447;
      --green-bg: #e7f7ee;
      --green: #147a3d;
      --yellow-bg: #fff4d8;
      --yellow: #8a6100;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--ink); font-size: 14px; }}
    header {{ background: var(--head); color: white; padding: 30px 38px 26px; }}
    main {{ padding: 26px 38px 48px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin: 28px 0 12px; font-size: 19px; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; color: #435066; font-size: 12px; text-transform: uppercase; }}
    code {{ background: #eef2f6; padding: 2px 5px; border-radius: 4px; }}
    .meta {{ color: #dbe5f3; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .status-pass, .status-ready {{ background: var(--green-bg); color: var(--green); }}
    .status-missing, .status-ready-with-gaps {{ background: var(--yellow-bg); color: var(--yellow); }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      table {{ display: block; overflow-x: auto; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Day24 RC Demo Flow</h1>
    <div class="meta">{html.escape(str(demo_flow.get("name", "")))} · Generated {html.escape(str(demo_flow.get("generated_at", "")))} · Result {html.escape(str(demo_flow.get("result", "")))}</div>
  </header>
  <main>
    <h2>Walkthrough Steps</h2>
    <table>
      <thead><tr><th>#</th><th>Section</th><th>Demo Action</th><th>Command / Location</th><th>Talk Track</th><th>Evidence</th></tr></thead>
      <tbody>{steps}</tbody>
    </table>
    <h2>RC Checklist</h2>
    <table>
      <thead><tr><th>Item</th><th>Status</th></tr></thead>
      <tbody>{checklist}</tbody>
    </table>
    <h2>Safety Summary</h2>
    <ul class="panel">{safety}</ul>
    <h2>Recommended Open Order</h2>
    <ol class="panel">{open_order}</ol>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def _run_day24_demo_flow(project_root: Path) -> int:
    task_catalog = list_tasks()
    report_rows = discover_report_visibility(project_root)
    demo_flow = build_day24_demo_flow(task_catalog, report_rows)
    json_path = project_root / DAY24_DEMO_FLOW_JSON
    html_path = project_root / DAY24_DEMO_FLOW_HTML
    write_json_report(demo_flow, json_path)
    write_day24_demo_flow_html(demo_flow, html_path)
    print(format_heading("Day24 RC Demo Flow"))
    print(f"Result: {demo_flow['result']}")
    print(f"Walkthrough steps: {len(demo_flow['walkthrough_steps'])}")
    print(f"JSON demo flow: {_relative_to_project(project_root, json_path)}")
    print(f"HTML demo flow: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day24 demo flow completed without live execution.")
    return 0


def _run_portfolio_finalization(project_root: Path) -> int:
    task_catalog = list_tasks()
    report_rows = discover_report_visibility(project_root)
    evidence = build_portfolio_evidence_index(task_catalog, report_rows)
    json_path = project_root / DAY19_EVIDENCE_INDEX_JSON
    html_path = project_root / DAY19_EVIDENCE_INDEX_HTML
    write_json_report(evidence, json_path)
    write_portfolio_evidence_html(evidence, html_path, project_root)
    print(format_heading("Day19 Runner Evidence Index"))
    print(f"Portfolio readiness: {evidence['portfolio_readiness']}")
    print(
        "Summary: "
        f"tasks={evidence['summary']['tasks']} "
        f"found={evidence['summary']['reports_found']} "
        f"missing={evidence['summary']['reports_missing']} "
        f"guardrails={evidence['summary']['disabled_guardrails']}"
    )
    print(f"JSON evidence index: {_relative_to_project(project_root, json_path)}")
    print(f"HTML evidence index: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} Day19 portfolio finalization completed without live execution.")
    return 0


def _render_report_visibility_index(
    rows: List[Dict[str, Any]],
    project_root: Path,
    output_path: Path,
) -> None:
    output_path_text = _relative_to_project(project_root, output_path)
    _print_report_visibility(rows, output_path_text)
    write_report_index_html(list_tasks(), rows, output_path, project_root)
    print()
    print(f"{format_status('PASS')} HTML report index: {output_path_text}")
    print("Day18 WireGuard runner integration uses dry-run and explicit confirmation guardrails.")


def _run_report_visibility_index(project_root: Path) -> int:
    rows = discover_report_visibility(project_root)
    output_path = project_root / DAY17_REPORT_INDEX_HTML
    _render_report_visibility_index(rows, project_root, output_path)
    return 0


def _run_day39_vrrp_evidence_dashboard_integration(project_root: Path) -> int:
    report = build_day39_vrrp_evidence_report(project_root)
    json_path = project_root / DAY39_VRRP_EVIDENCE_JSON
    html_path = project_root / DAY39_VRRP_EVIDENCE_HTML
    write_json_report(report, json_path)
    report = build_day39_vrrp_evidence_report(project_root)
    write_json_report(report, json_path)
    write_day39_vrrp_evidence_html(report, html_path, project_root)
    report = build_day39_vrrp_evidence_report(project_root)
    write_json_report(report, json_path)
    write_day39_vrrp_evidence_html(report, html_path, project_root)
    counts = report["summary"]["counts"]
    print(format_heading("Day39 VRRP Evidence Dashboard Integration"))
    print(f"Overall status: {format_status(str(report.get('overall_status', 'UNKNOWN')))}")
    print(
        "Summary: "
        f"total={counts.get('total', 0)} "
        f"found={color_text(str(counts.get('found', 0)), 'green')} "
        f"missing={color_text(str(counts.get('missing', 0)), 'yellow')} "
        f"not_generated={color_text(str(counts.get('not_generated', 0)), 'yellow')}"
    )
    missing = report.get("missing_optional_artifacts", [])
    if missing:
        print()
        print(format_heading("Missing optional VRRP artifacts"))
        for entry in missing:
            print(
                f"  {format_status(str(entry.get('status', 'MISSING')))} "
                f"{entry.get('day')} / {entry.get('title')} -> {entry.get('path')}"
            )
    print()
    print("Safety: report-only; no live tests, SSH, credentials, or configuration changes.")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    return 0


def _run_day40_demo_readiness_review(project_root: Path) -> int:
    report = build_day40_demo_readiness_report(project_root)
    json_path = project_root / DAY40_DEMO_READINESS_JSON
    html_path = project_root / DAY40_DEMO_READINESS_HTML
    write_json_report(report, json_path)
    write_day40_demo_readiness_html(report, html_path, project_root)
    print(format_heading("Day40 v0.2 Demo Readiness Review and Scope Lock"))
    print(f"Overall status: {format_status(str(report.get('overall_status', 'UNKNOWN')))}")
    print(f"Readiness: {report.get('demo_readiness_status')}")
    print(
        "Safety flags: "
        f"live_test={report.get('live_test')} "
        f"ssh_used={report.get('ssh_used')} "
        f"device_config_changed={report.get('device_config_changed')}"
    )
    print("Safety: report-only; no live tests, SSH, credentials, or configuration changes.")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    return 0


def _run_day41_release_packaging(project_root: Path) -> int:
    report = build_day41_release_packaging_report(project_root)
    json_path = project_root / DAY41_RELEASE_PACKAGING_JSON
    html_path = project_root / DAY41_RELEASE_PACKAGING_HTML
    write_json_report(report, json_path)
    write_day41_release_packaging_html(report, html_path, project_root)
    print(format_heading("Day41 v0.2 Release Packaging"))
    print(f"Overall status: {format_status(str(report.get('overall_status', 'UNKNOWN')))}")
    print(
        "Safety flags: "
        f"live_test={report.get('live_test')} "
        f"ssh_used={report.get('ssh_used')} "
        f"device_config_changed={report.get('device_config_changed')} "
        f"v0_2_tag_created={report.get('v0_2_tag_created')}"
    )
    print("Safety: report-only; no live tests, SSH, credentials, configuration changes, voice/AI implementation, or tag creation.")
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    return 0


def _print_dry_run(profile: Dict[str, Any], profile_path: Path) -> None:
    output = profile["overview_output"]
    print(format_heading(f"Day14 {DAY14_NAME}"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Profile path: {color_text(str(profile_path), 'gray')}")
    print()
    print(format_heading("Overview output paths"))
    print(f"  JSON overview : {output.get('json')}")
    print(f"  HTML overview : {output.get('html')}")
    print()
    print(format_heading("Report files that would be checked"))
    for _section, device, report in iter_report_items(profile):
        label = f"{device.get('name')} / {report.get('name')}" if device else str(report.get("name"))
        required = "required" if report.get("required") else "optional"
        print(
            f"  {format_status('NOT_RUN')} "
            f"{color_text(label, 'cyan')} "
            f"{color_text('[' + required + ']', 'yellow' if report.get('required') else 'gray')} "
            f"-> {report.get('json')}"
        )
    print()
    print(f"{format_status('PASS')} No reports were written")


def _format_required_label(required: bool) -> str:
    label = "required" if required else "optional"
    return color_text(f"[{label}]", "yellow" if required else "gray")


def _print_report_record(label: str, record: Dict[str, Any]) -> None:
    message = f" - {record.get('message')}" if record.get("message") else ""
    print(
        f"  {format_status(str(record.get('status', 'UNKNOWN')))} "
        f"{color_text(label, 'cyan')} "
        f"{_format_required_label(bool(record.get('required')))} "
        f"-> {record.get('json')}{message}"
    )


def _print_report_records(overview: Dict[str, Any]) -> None:
    print()
    print(format_heading("Device report results"))
    for device in overview.get("devices", []):
        device_label = f"{device.get('name')} / {device.get('type')}"
        print(f"  {color_text(str(device_label), 'gray', bold=True)}")
        reports = device.get("reports", [])
        if not reports:
            print(f"    {format_status('UNKNOWN')} No reports configured")
            continue
        for report in reports:
            _print_report_record(f"{device.get('name')} / {report.get('name')}", report)

    print()
    print(format_heading("Lab summary report results"))
    lab_summary_reports = overview.get("lab_summary_reports", [])
    if not lab_summary_reports:
        print(f"  {format_status('UNKNOWN')} No lab summary reports configured")
        return
    for report in lab_summary_reports:
        _print_report_record(str(report.get("name")), report)


def _print_run_summary(overview: Dict[str, Any], profile: Dict[str, Any]) -> None:
    counts = overview.get("counts", {})
    print(format_heading(f"Day14 {DAY14_NAME}"))
    print(f"Overall result: {format_status(str(overview.get('overall_result', 'UNKNOWN')))}")
    print(
        "Counts: "
        f"total={counts.get('total', 0)} "
        f"pass={color_text(str(counts.get('pass', 0)), 'green')} "
        f"fail={color_text(str(counts.get('fail', 0)), 'red')} "
        f"warn={color_text(str(counts.get('warn', 0)), 'yellow')} "
        f"missing={color_text(str(counts.get('missing', 0)), 'gray')} "
        f"unknown={color_text(str(counts.get('unknown', 0)), 'magenta')}"
    )
    _print_report_records(overview)
    print()
    print(f"JSON overview: {profile['overview_output']['json']}")
    print(f"HTML overview: {profile['overview_output']['html']}")


def _run_report_index(
    profile: Dict[str, Any],
    project_root: Path,
    profile_path: Path,
    dry_run: bool = False,
) -> int:
    if dry_run:
        _print_dry_run(profile, profile_path)
        return 0

    overview = build_latest_lab_overview(profile, project_root)
    json_output = _resolve_project_path(project_root, profile["overview_output"]["json"])
    html_output = _resolve_project_path(project_root, profile["overview_output"]["html"])
    write_json_report(overview, json_output)
    write_html_overview(overview, html_output, project_root)
    _print_run_summary(overview, profile)
    return 0 if overview["overall_result"] in {"PASS", "WARN"} else 1


def _build_day4_baseline_command() -> List[str]:
    return [sys.executable, DAY4_BASELINE_SCRIPT]


def _print_day4_baseline_dry_run() -> None:
    print(format_heading("Day4 multi-device baseline"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Command that would be executed: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    print()
    print(format_heading("Safety notes"))
    print("  This is a live SSH validation workflow.")
    print("  Dry-run does not connect to devices.")
    print(f"  Dry-run does not execute {DAY4_BASELINE_SCRIPT}.")
    print("  Dry-run does not write reports.")
    print()
    print(f"{format_status('PASS')} No live workflow was executed.")


def _print_day4_baseline_follow_up() -> None:
    print()
    print("Day4 baseline finished. To refresh the lab overview, run:")
    print("python network_lab.py --task report-index")


def _run_day4_baseline(project_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        _print_day4_baseline_dry_run()
        return 0

    print(format_heading("Day4 multi-device baseline"))
    print("Live SSH validation workflow.")
    print(f"Executing command: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    result = subprocess.run(_build_day4_baseline_command(), cwd=project_root)
    _print_day4_baseline_follow_up()
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day4 baseline completed successfully.")
        return 0

    print(f"{format_status('FAIL')} Day4 baseline failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_day4_baseline(project_root: Path, input_func: Any) -> int:
    print(format_heading("Day4 multi-device baseline"))
    print("This is a live SSH validation workflow.")
    print(f"Command to execute: {color_text(DAY4_BASELINE_DISPLAY_COMMAND, 'cyan', bold=True)}")
    try:
        confirmation = input_func("Confirm live Day4 baseline run? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation not in {"y", "yes"}:
        print(f"{format_status('NOT_RUN')} Day4 baseline cancelled. No live workflow was executed.")
        return 0

    return _run_day4_baseline(project_root, dry_run=False)


def _load_day8_performance_profile(project_root: Path) -> Dict[str, Any]:
    profile_path = project_root / DAY8_PERFORMANCE_PROFILE
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Day8 performance profile was not found: {profile_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Day8 performance profile is not valid JSON: {profile_path}") from exc

    if not isinstance(profile, dict):
        raise ValueError("Day8 performance profile must contain a JSON object.")
    return profile


def _required_day8_profile_value(profile: Dict[str, Any], key: str) -> str:
    value = profile.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Day8 performance profile must define {key}.")
    return str(value)


def _build_day8_performance_command(project_root: Path, executable: str = sys.executable) -> List[str]:
    profile = _load_day8_performance_profile(project_root)
    return [
        executable,
        DAY8_PERFORMANCE_SCRIPT,
        "--lan-server-ip",
        _required_day8_profile_value(profile, "default_lan_server_ip"),
        "--duration",
        _required_day8_profile_value(profile, "default_duration_sec"),
        "--omit",
        _required_day8_profile_value(profile, "default_omit_sec"),
        "--parallel",
        _required_day8_profile_value(profile, "default_parallel_streams"),
        "--threshold-mbps",
        _required_day8_profile_value(profile, "default_threshold_mbps"),
        "--warn-threshold-mbps",
        _required_day8_profile_value(profile, "default_warn_threshold_mbps"),
    ]


def _format_display_command(command: List[str]) -> str:
    display_parts = ["python" if index == 0 and part == sys.executable else part for index, part in enumerate(command)]
    return " ".join(display_parts)


def _print_day8_performance_dry_run(project_root: Path) -> int:
    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Command that would be executed: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    print()
    print(format_heading("Safety notes"))
    print("  This is a live iperf3 performance workflow.")
    print("  Dry-run does not connect to devices.")
    print("  Dry-run does not require real iperf3.")
    print(f"  Dry-run does not execute {DAY8_PERFORMANCE_SCRIPT}.")
    print("  Dry-run does not write reports.")
    print()
    print(f"{format_status('PASS')} No live workflow was executed.")
    return 0


def _run_day8_performance(project_root: Path, dry_run: bool = False) -> int:
    if dry_run:
        return _print_day8_performance_dry_run(project_root)

    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print("Live iperf3 performance workflow.")
    print(f"Executing command: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day8 iperf3 performance completed successfully.")
        return 0

    print(f"{format_status('FAIL')} Day8 iperf3 performance failed with exit code {result.returncode}.")
    return result.returncode


def _run_day32_vrrp_precheck(project_root: Path, dry_run: bool = False) -> int:
    command = [sys.executable, DAY32_VRRP_PRECHECK_SCRIPT]
    display_command = _format_display_command(command)
    if dry_run:
        print(format_heading("Day32 VRRP Read-only Precheck"))
        print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
        print(f"Command that would be executed: {color_text(display_command, 'cyan', bold=True)}")
        print()
        print(format_heading("Safety notes"))
        print("  This is a live SSH read-only precheck workflow.")
        print("  The Day32 script validates every MikroTik command before sending it.")
        print("  Allowed operations are print, /export terse, and local report generation.")
        print("  Blocked keywords are add, set, remove, disable, enable, reboot, and reset-configuration.")
        print("  Dry-run does not connect to devices and does not write reports.")
        print()
        print(f"{format_status('PASS')} No live workflow was executed.")
        return 0

    print(format_heading("Day32 VRRP Read-only Precheck"))
    print("Live SSH read-only precheck workflow.")
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day32 VRRP read-only precheck completed.")
        return 0

    print(f"{format_status('FAIL')} Day32 VRRP read-only precheck failed with exit code {result.returncode}.")
    return result.returncode


def _run_day33_vrrp_dry_run(project_root: Path) -> int:
    command = [sys.executable, DAY33_VRRP_DRY_RUN_SCRIPT]
    display_command = _format_display_command(command)
    print(format_heading("Day33 VRRP Topology Dry-run"))
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    print("Safety guard: DRY-RUN ONLY and NOT EXECUTED; no SSH connection or RouterOS execution is performed.")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day33 VRRP topology dry-run completed.")
        print(f"JSON report: {DAY33_VRRP_DRY_RUN_JSON.as_posix()}")
        print(f"HTML report: {DAY33_VRRP_DRY_RUN_HTML.as_posix()}")
        print(f"TXT report: {DAY33_VRRP_DRY_RUN_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day33 VRRP topology dry-run failed with exit code {result.returncode}.")
    return result.returncode


def _run_day34_vrrp_staged_plan(project_root: Path) -> int:
    command = [sys.executable, DAY34_VRRP_STAGED_PLAN_SCRIPT]
    display_command = _format_display_command(command)
    print(format_heading("Day34 VRRP Staged Apply Plan"))
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    print("Safety gate: BLOCKED PLAN ONLY and NOT EXECUTED; no SSH connection or RouterOS execution is performed.")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day34 VRRP staged apply plan completed.")
        print(f"JSON report: {DAY34_VRRP_STAGED_PLAN_JSON.as_posix()}")
        print(f"HTML report: {DAY34_VRRP_STAGED_PLAN_HTML.as_posix()}")
        print(f"TXT report: {DAY34_VRRP_STAGED_PLAN_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day34 VRRP staged apply plan failed with exit code {result.returncode}.")
    return result.returncode


def _run_day35_vrrp_failover_validation(project_root: Path, dry_run: bool = False) -> int:
    command = [sys.executable, DAY35_VRRP_FAILOVER_SCRIPT]
    display_command = _format_display_command(command)
    if dry_run:
        print(format_heading("Day35 VRRP Failover Validation"))
        print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
        print(f"Command that would be executed: {color_text(display_command, 'cyan', bold=True)}")
        print()
        print(format_heading("Safety notes"))
        print("  This is a controlled live observation workflow.")
        print("  The operator manually disconnects/reconnects lab01 LAN from the switch.")
        print("  Automation uses ping -S 192.168.88.100 <target> and read-only RouterOS print commands.")
        print("  Blocked actions include interface enable/disable, firewall/NAT changes, IP changes, VRRP changes, reboot, and reset.")
        print("  Dry-run does not prompt for cable actions, wait, connect to devices, run pings, or write reports.")
        print()
        print(f"{format_status('PASS')} No live workflow was executed.")
        return 0

    print(format_heading("Day35 VRRP Failover Validation"))
    print("Controlled live observation workflow.")
    print("Manual trigger: disconnect/reconnect lab01 LAN cable only when prompted.")
    print(f"Executing command: {color_text(display_command, 'cyan', bold=True)}")
    sys.stdout.flush()
    result = subprocess.run(command, cwd=project_root)
    if result.returncode == 0:
        print(f"{format_status('PASS')} Day35 VRRP failover validation completed.")
        print(f"JSON report: {DAY35_VRRP_FAILOVER_JSON.as_posix()}")
        print(f"HTML report: {DAY35_VRRP_FAILOVER_HTML.as_posix()}")
        print(f"TXT report: {DAY35_VRRP_FAILOVER_TXT.as_posix()}")
        return 0
    print(f"{format_status('FAIL')} Day35 VRRP failover validation failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_day8_performance(project_root: Path, input_func: Any) -> int:
    try:
        command = _build_day8_performance_command(project_root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading("Day8 iperf3 performance"))
    print("This is a live iperf3 performance workflow.")
    print(f"Command to execute: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    try:
        confirmation = input_func("Confirm live Day8 iperf3 performance run? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation != "y":
        print(f"{format_status('NOT_RUN')} Day8 iperf3 performance cancelled. No live workflow was executed.")
        return 0

    return _run_day8_performance(project_root, dry_run=False)


def _wireguard_runner_report_path(project_root: Path, html_report: bool = False) -> Path:
    return project_root / (WIREGUARD_RUNNER_REPORT_HTML if html_report else WIREGUARD_RUNNER_REPORT_JSON)


def _wireguard_runner_planned_steps(run_iperf: bool = False) -> List[str]:
    steps = [
        "Validate WireGuard runner config file path.",
        "Validate required non-secret config fields before guarded execution.",
        "Delegate to the existing WireGuard validation script only when live guard is explicit.",
        "Keep peer recreation and firewall fix flags disabled in the runner.",
        "Write local runner safety report with secrets masked.",
    ]
    if run_iperf:
        steps.append("Request iperf3 checks only in guarded live mode.")
    return steps


def _wireguard_config_path(project_root: Path, config_path: str) -> Path:
    path = Path(config_path)
    return path if path.is_absolute() else project_root / path


def _wireguard_config_display_path(project_root: Path, config_path: str) -> str:
    return _relative_to_project(project_root, _wireguard_config_path(project_root, config_path))


def _wireguard_runner_config_validation(project_root: Path, config_path: str = DAY12_WIREGUARD_CONFIG) -> Dict[str, Any]:
    selected_path = _wireguard_config_path(project_root, config_path)
    selected_display_path = _wireguard_config_display_path(project_root, config_path)
    required_fields = ["device_name", "router_host", "router_username", "wg_interface", "peer_name"]
    optional_fields = ["lan_gateway_ip", "lan_host_ip", "iperf_server_ip", "client_address"]
    validation: Dict[str, Any] = {
        "config_path": selected_display_path,
        "status": "PASS",
        "missing_required_fields": [],
        "missing_optional_fields": [],
        "warnings": [],
    }
    try:
        data = json.loads(selected_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation["status"] = "WARN"
        validation["missing_required_fields"] = ["config_file"]
        validation["warnings"] = [f"Config file was not found: {selected_display_path}"]
        return validation
    except json.JSONDecodeError as exc:
        validation["status"] = "FAIL"
        validation["missing_required_fields"] = ["valid_json_config"]
        validation["warnings"] = [f"Config file is not valid JSON: {exc.msg}"]
        return validation

    if not isinstance(data, dict):
        validation["status"] = "FAIL"
        validation["missing_required_fields"] = ["json_object_config"]
        validation["warnings"] = ["Config file must contain a JSON object."]
        return validation

    missing_required = [field for field in required_fields if str(data.get(field, "")).strip() == ""]
    missing_optional = [field for field in optional_fields if str(data.get(field, "")).strip() == ""]
    validation["missing_required_fields"] = missing_required
    validation["missing_optional_fields"] = missing_optional
    validation["status"] = "PASS" if not missing_required else "FAIL"
    if missing_optional:
        validation["warnings"] = [f"Optional fields missing: {', '.join(missing_optional)}"]
    return validation


def _is_safe_report_device_segment(value: str) -> bool:
    text = str(value).strip()
    return bool(text) and Path(text).name == text and "/" not in text and "\\" not in text


def _count_check_statuses(checks: Dict[str, Any]) -> Dict[str, int]:
    return {
        "pass_count": sum(1 for status in checks.values() if status == "PASS"),
        "warn_count": sum(1 for status in checks.values() if status == "WARN"),
        "fail_count": sum(1 for status in checks.values() if status == "FAIL"),
        "skip_count": sum(1 for status in checks.values() if status == "SKIP"),
    }


def _build_delegated_day12_summary(project_root: Path, config_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "delegated_report": {},
        "delegated_result_summary": {},
    }
    try:
        config_data = json.loads(_wireguard_config_path(project_root, config_path).read_text(encoding="utf-8"))
        device_name = str(config_data.get("device_name", "")).strip() if isinstance(config_data, dict) else ""
    except (OSError, json.JSONDecodeError) as exc:
        result["delegated_report_parse_warning"] = f"Could not read selected WireGuard config for delegated report discovery: {exc}"
        return result

    if not _is_safe_report_device_segment(device_name):
        result["delegated_report_parse_warning"] = "Selected WireGuard config does not contain a safe device_name for report discovery."
        return result

    json_path = project_root / "reports" / device_name / DAY12_WIREGUARD_REPORT_JSON_NAME
    html_path = project_root / "reports" / device_name / DAY12_WIREGUARD_REPORT_HTML_NAME
    result["delegated_report"] = {
        "json": _relative_to_project(project_root, json_path),
        "html": _relative_to_project(project_root, html_path),
    }

    try:
        report_data = json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        result["delegated_report_parse_warning"] = (
            "Delegated Day12 report JSON was not found after runner completion: "
            + _relative_to_project(project_root, json_path)
        )
        return result
    except (OSError, json.JSONDecodeError) as exc:
        result["delegated_report_parse_warning"] = f"Could not parse delegated Day12 report JSON: {exc}"
        return result

    if not isinstance(report_data, dict):
        result["delegated_report_parse_warning"] = "Delegated Day12 report JSON did not contain an object."
        return result

    checks = report_data.get("checks", {})
    if not isinstance(checks, dict):
        checks = {}
    iperf_summary = report_data.get("iperf_summary", {})
    if not isinstance(iperf_summary, dict):
        iperf_summary = {}

    summary: Dict[str, Any] = {
        "result": report_data.get("overall_result", report_data.get("result", "UNKNOWN")),
        **_count_check_statuses(checks),
    }
    for source_key, output_key in (
        ("final_vpn_connectivity", "final_vpn_connectivity"),
        ("initial_handshake_seen", "initial_handshake_seen"),
        ("post_connectivity_handshake_seen", "post_connectivity_handshake_seen"),
    ):
        if source_key in checks:
            summary[output_key] = checks[source_key]
    for source_key, output_key in (
        ("forward_mbps", "iperf_forward_mbps"),
        ("reverse_mbps", "iperf_reverse_mbps"),
    ):
        if source_key in iperf_summary:
            summary[output_key] = iperf_summary[source_key]

    result["delegated_result_summary"] = summary
    return result


def _build_wireguard_runner_report(
    mode: str,
    result: str,
    project_root: Path,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
    message: str = "",
    delegated_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    validation = _wireguard_runner_config_validation(project_root, config_path)
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    delegated_summary = delegated_summary or {}
    warnings = list(validation["warnings"])
    if delegated_summary.get("delegated_report_parse_warning"):
        warnings.append(str(delegated_summary["delegated_report_parse_warning"]))
    live_guard_status = {
        "dry-run": "DRY-RUN: no live execution",
        "blocked": "BLOCKED: missing explicit --allow-live-wireguard",
        "guarded-live": "PASS: explicit --allow-live-wireguard provided",
    }.get(mode, "UNKNOWN")
    guardrails = {
        "dry_run_default": "PASS",
        "requires_allow_live_wireguard": "PASS",
        "subprocess_shell_false": "PASS",
        "forbidden_write_flags_blocked": "PASS",
        "secrets_masked": "PASS",
        "live_device_execution": "ENABLED" if mode == "guarded-live" else "BLOCKED",
    }
    return mask_secret_values(
        {
            "task_id": WIREGUARD_RUNNER_TASK_ID,
            "display_name": WIREGUARD_RUNNER_DISPLAY_NAME,
            "day": "Day18",
            "category": "vpn",
            "mode": mode,
            "result": result,
            "selected_config_path": selected_config_path,
            "live_guard_status": live_guard_status,
            "delegated_command_summary": _format_display_command(command),
            "validation_status": validation["status"],
            "safety_guardrail_status": guardrails,
            "missing_required_fields": validation["missing_required_fields"],
            "missing_optional_fields": validation["missing_optional_fields"],
            "warnings": warnings,
            "planned_steps": _wireguard_runner_planned_steps(run_iperf=run_iperf),
            "report_output_path": WIREGUARD_RUNNER_REPORT_JSON.as_posix(),
            "message": message,
            "timestamp": datetime.now().replace(microsecond=0).isoformat(sep=" "),
            **delegated_summary,
        }
    )


def _write_wireguard_runner_html(report: Dict[str, Any], output_path: Path) -> None:
    safe_report = mask_secret_values(report)
    rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in safe_report.items()
        if key not in {
            "safety_guardrail_status",
            "planned_steps",
            "warnings",
            "delegated_report",
            "delegated_result_summary",
        }
    )
    guardrail_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in safe_report.get("safety_guardrail_status", {}).items()
    )
    planned_steps = "".join(f"<li>{html.escape(str(step))}</li>" for step in safe_report.get("planned_steps", []))
    warnings = "".join(f"<li>{html.escape(str(item))}</li>" for item in safe_report.get("warnings", [])) or "<li>None</li>"
    delegated_report = safe_report.get("delegated_report", {})
    if not isinstance(delegated_report, dict):
        delegated_report = {}
    delegated_summary = safe_report.get("delegated_result_summary", {})
    if not isinstance(delegated_summary, dict):
        delegated_summary = {}
    delegated_report_rows = "\n".join(
        f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>"
        for key, value in delegated_report.items()
    ) or "<tr><td colspan='2'>Not available</td></tr>"
    delegated_summary_keys = [
        "result",
        "final_vpn_connectivity",
        "initial_handshake_seen",
        "post_connectivity_handshake_seen",
        "iperf_forward_mbps",
        "iperf_reverse_mbps",
    ]
    delegated_summary_rows = "\n".join(
        f"<tr><td>{html.escape(key)}</td><td>{html.escape(str(delegated_summary[key]))}</td></tr>"
        for key in delegated_summary_keys
        if key in delegated_summary
    ) or "<tr><td colspan='2'>Not available</td></tr>"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(WIREGUARD_RUNNER_DISPLAY_NAME)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #182230; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    td, th {{ border: 1px solid #d8e0ec; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #edf2f8; }}
  </style>
</head>
<body>
  <h1>{html.escape(WIREGUARD_RUNNER_DISPLAY_NAME)}</h1>
  <table><tbody>{rows}</tbody></table>
  <h2>Delegated Day12 Reports</h2>
  <table><tbody>{delegated_report_rows}</tbody></table>
  <h2>Delegated Day12 Summary</h2>
  <table><tbody>{delegated_summary_rows}</tbody></table>
  <h2>Safety Guardrails</h2>
  <table><tbody>{guardrail_rows}</tbody></table>
  <h2>Planned Steps</h2>
  <ol>{planned_steps}</ol>
  <h2>Warnings</h2>
  <ul>{warnings}</ul>
</body>
</html>
""",
        encoding="utf-8",
    )


def _write_wireguard_runner_report(project_root: Path, report: Dict[str, Any]) -> Tuple[Path, Path]:
    json_path = _wireguard_runner_report_path(project_root)
    html_path = _wireguard_runner_report_path(project_root, html_report=True)
    write_json_report(report, json_path)
    _write_wireguard_runner_html(report, html_path)
    return json_path, html_path


def _build_wireguard_runner_command(
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
    executable: str = sys.executable,
) -> List[str]:
    command = [
        executable,
        DAY12_WIREGUARD_SCRIPT,
        "--config",
        str(config_path),
    ]
    if run_iperf:
        command.extend(["--run-iperf", "--expect-connected"])
    command.append("--non-interactive")
    return command


def _validate_wireguard_runner_command(command: List[str], config_path: str = DAY12_WIREGUARD_CONFIG) -> None:
    forbidden_flags = {"--recreate-peer", "--apply-firewall-fixes"}
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        raise ValueError("WireGuard runner command must be a list of string arguments.")
    present_forbidden_flags = sorted(forbidden_flags.intersection(command))
    if present_forbidden_flags:
        raise ValueError(
            "WireGuard runner command contains forbidden live write flags: "
            + ", ".join(present_forbidden_flags)
        )
    required_parts = {DAY12_WIREGUARD_SCRIPT, "--config", str(config_path), "--non-interactive"}
    missing_parts = sorted(part for part in required_parts if part not in command)
    if missing_parts:
        raise ValueError("WireGuard runner command is missing required safety args: " + ", ".join(missing_parts))


def _print_wireguard_runner_dry_run(
    project_root: Path,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
) -> int:
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    _validate_wireguard_runner_command(command, config_path=config_path)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    report = _build_wireguard_runner_report("dry-run", "DRY-RUN", project_root, config_path=config_path, run_iperf=run_iperf)
    json_path, html_path = _write_wireguard_runner_report(project_root, report)
    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print(f"Mode: {color_text('Dry run', 'yellow', bold=True)}")
    print(f"Primary command: {color_text('python network_lab.py --task wireguard-runner --dry-run', 'cyan', bold=True)}")
    print(f"Selected WireGuard config: {selected_config_path}")
    print()
    print(format_heading("Planned validation steps"))
    for step in report["planned_steps"]:
        print(f"  - {step}")
    print()
    print(format_heading("Safety guardrails"))
    print("  This is a live WireGuard validation workflow.")
    print("  Dry-run does not connect to devices.")
    print("  Dry-run does not start WireGuard, ping, iperf, or device config changes.")
    print("  Runner command is non-interactive and does not include --recreate-peer or --apply-firewall-fixes.")
    print("  Live execution requires explicit --allow-live-wireguard. Interactive menu execution also requires explicit confirmation.")
    print()
    print(f"JSON report: {_relative_to_project(project_root, json_path)}")
    print(f"HTML report: {_relative_to_project(project_root, html_path)}")
    print(f"{format_status('PASS')} No live workflow was executed.")
    return 0


def _run_wireguard_runner(
    project_root: Path,
    dry_run: bool = False,
    allow_live_wireguard: bool = False,
    config_path: str = DAY12_WIREGUARD_CONFIG,
    run_iperf: bool = False,
) -> int:
    if dry_run:
        return _print_wireguard_runner_dry_run(project_root, config_path=config_path, run_iperf=run_iperf)
    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    if not allow_live_wireguard:
        message = "WireGuard live execution requires explicit --allow-live-wireguard"
        report = _build_wireguard_runner_report(
            "blocked",
            "BLOCKED",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            message=message,
        )
        _write_wireguard_runner_report(project_root, report)
        print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
        print(f"Selected WireGuard config: {selected_config_path}")
        print(message)
        return 0

    validation = _wireguard_runner_config_validation(project_root, config_path)
    if validation["status"] == "FAIL":
        message = "WireGuard runner config validation failed before live execution."
        report = _build_wireguard_runner_report(
            "blocked",
            "BLOCKED",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            message=message,
        )
        _write_wireguard_runner_report(project_root, report)
        print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
        print(f"Selected WireGuard config: {selected_config_path}")
        print(message)
        return 2

    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=run_iperf)
    try:
        _validate_wireguard_runner_command(command, config_path=config_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print("Live WireGuard validation workflow.")
    print(f"Selected WireGuard config: {selected_config_path}")
    print(f"Executing command: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            shell=False,
            timeout=DAY12_WIREGUARD_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            f"{format_status('FAIL')} WireGuard runner timed out after "
            f"{DAY12_WIREGUARD_TIMEOUT_SECONDS} seconds."
        )
        return 124
    delegated_summary = _build_delegated_day12_summary(project_root, config_path)
    if result.returncode == 0:
        report = _build_wireguard_runner_report(
            "guarded-live",
            "PASS",
            project_root,
            config_path=config_path,
            run_iperf=run_iperf,
            delegated_summary=delegated_summary,
        )
        _write_wireguard_runner_report(project_root, report)
        print(f"{format_status('PASS')} WireGuard runner completed successfully.")
        return 0

    report = _build_wireguard_runner_report(
        "guarded-live",
        "FAIL",
        project_root,
        config_path=config_path,
        run_iperf=run_iperf,
        delegated_summary=delegated_summary,
    )
    _write_wireguard_runner_report(project_root, report)
    print(f"{format_status('FAIL')} WireGuard runner failed with exit code {result.returncode}.")
    return result.returncode


def _confirm_and_run_wireguard_runner(
    project_root: Path,
    input_func: Any,
    config_path: str = DAY12_WIREGUARD_CONFIG,
) -> int:
    command = _build_wireguard_runner_command(config_path=config_path, run_iperf=False)
    try:
        _validate_wireguard_runner_command(command, config_path=config_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    selected_config_path = _wireguard_config_display_path(project_root, config_path)
    print(format_heading(WIREGUARD_RUNNER_DISPLAY_NAME))
    print("This is a live WireGuard validation workflow.")
    print(f"Selected WireGuard config: {selected_config_path}")
    print(f"Command to execute: {color_text(_format_display_command(command), 'cyan', bold=True)}")
    print("Runner safety layer omits --recreate-peer and --apply-firewall-fixes.")
    try:
        confirmation = input_func("Confirm live WireGuard runner execution? [y/N]: ").strip().lower()
    except EOFError:
        confirmation = ""

    if confirmation != "y":
        print(f"{format_status('NOT_RUN')} WireGuard runner cancelled. No live workflow was executed.")
        return 0

    return _run_wireguard_runner(project_root, allow_live_wireguard=True, config_path=config_path, run_iperf=False)


def _wireguard_config_suggestions(project_root: Path) -> List[str]:
    suggestions = []
    seen = set()
    for path in sorted(project_root.glob("Set_WireguardVPN*_config.json")):
        if not path.is_file():
            continue
        name = path.name
        if name in seen:
            continue
        suggestions.append(name)
        seen.add(name)
    return sorted(suggestions, key=lambda name: (name == DAY12_WIREGUARD_CONFIG, name.lower()))


def _prompt_for_wireguard_config(
    project_root: Path,
    input_func: Any,
) -> Optional[str]:
    suggestions = _wireguard_config_suggestions(project_root)
    print(format_heading("WireGuard VPN validation"))
    print("Select a WireGuard config file for this run.")
    if suggestions:
        print("Suggestions:")
        for index, suggestion in enumerate(suggestions, start=1):
            print(f"  {index}. {suggestion}")
    else:
        print("No Set_WireguardVPN*_config.json files were found. Type a config path to continue.")

    try:
        selection = input_func("WireGuard config path or number [blank to cancel]: ").strip()
    except EOFError:
        selection = ""

    if not selection:
        print(f"{format_status('NOT_RUN')} WireGuard runner cancelled. No config was selected.")
        return None

    if selection.isdigit() and suggestions:
        selected_index = int(selection)
        if 1 <= selected_index <= len(suggestions):
            return suggestions[selected_index - 1]
        print(f"{format_status('UNKNOWN')} Invalid WireGuard config selection: {selection}")
        return None

    return selection


def _print_recommended_live_command(workflow_id: str) -> None:
    recommendation = LIVE_WORKFLOW_RECOMMENDATIONS[workflow_id]
    print(format_heading(recommendation["title"]))
    print(f"Recommended command: {color_text(recommendation['command'], 'cyan', bold=True)}")
    print(f"Safety reminder: {color_text(recommendation['reminder'], 'yellow')}")
    print(f"{format_status('NOT_RUN')} Day14 Phase 2 printed guidance only; no live workflow was executed.")


def _open_latest_overview_html(profile: Dict[str, Any], project_root: Path) -> bool:
    html_output = _resolve_project_path(project_root, profile["overview_output"]["html"])
    if not html_output.exists():
        print(f"{format_status('MISSING')} Latest overview HTML was not found: {html_output}")
        print("Run report-index first to generate it.")
        return False

    print(f"{format_status('PASS')} Opening latest overview HTML: {html_output}")
    try:
        if hasattr(os, "startfile"):
            os.startfile(str(html_output))  # type: ignore[attr-defined]
        else:
            webbrowser.open(html_output.resolve().as_uri())
    except OSError as exc:
        print(f"{format_status('UNKNOWN')} Could not open HTML file: {exc}")
        return False
    return True


def _print_interactive_menu() -> None:
    print()
    print(format_heading("Network Lab Runner"))
    print("Select an option by number:")
    print("  1. List available tasks")
    print("  2. Generate report index")
    print("  3. Dry-run report index")
    print("  4. Open latest overview HTML if it exists")
    print("  5. Run multi-device baseline validation")
    print("  6. Run iperf3 performance test")
    print("  7. Run WireGuard VPN validation")
    print("  8. Show WireGuard summary command")
    print("  0. Exit")


def _print_interactive_action_complete() -> None:
    print()
    print(color_text(INTERACTIVE_ACTION_COMPLETE, "green", bold=True))


def run_interactive_menu(
    profile: Dict[str, Any],
    project_root: Path,
    profile_path: Path,
    wireguard_config: str = DAY12_WIREGUARD_CONFIG,
    input_func: Optional[Any] = None,
) -> int:
    read_input = input_func or input
    while True:
        _print_interactive_menu()
        try:
            choice = read_input("Choice: ").strip().lower()
        except EOFError:
            print()
            print("Input closed. Exiting.")
            return 0

        if choice in {"0", "q", "quit", "exit"}:
            print("Exiting Network Lab Runner.")
            return 0
        if choice == "1":
            _print_task_list()
            _print_interactive_action_complete()
        elif choice == "2":
            _run_report_index(profile, project_root, profile_path, dry_run=False)
            _print_interactive_action_complete()
        elif choice == "3":
            _run_report_index(profile, project_root, profile_path, dry_run=True)
            _print_interactive_action_complete()
        elif choice == "4":
            _open_latest_overview_html(profile, project_root)
            _print_interactive_action_complete()
        elif choice == "5":
            day4_exit_code = _confirm_and_run_day4_baseline(project_root, read_input)
            _print_interactive_action_complete()
            if day4_exit_code != 0:
                return day4_exit_code
        elif choice == "6":
            day8_exit_code = _confirm_and_run_day8_performance(project_root, read_input)
            _print_interactive_action_complete()
            if day8_exit_code != 0:
                return day8_exit_code
        elif choice == "7":
            selected_wireguard_config = _prompt_for_wireguard_config(project_root, read_input)
            if selected_wireguard_config is None:
                _print_interactive_action_complete()
                continue
            wireguard_exit_code = _confirm_and_run_wireguard_runner(
                project_root,
                read_input,
                config_path=selected_wireguard_config,
            )
            _print_interactive_action_complete()
            if wireguard_exit_code != 0:
                return wireguard_exit_code
        elif choice == "8":
            _print_recommended_live_command("day13")
            _print_interactive_action_complete()
        else:
            print(f"{format_status('UNKNOWN')} Invalid menu choice: {choice or '<empty>'}")
            print("Please enter a number from 0 to 8.")


def _run_profile_backed_cli_task(project_root: Path, args: argparse.Namespace, runner: Any) -> int:
    from network_lab_cli_dispatch import _run_profile_backed_cli_task as run_profile_backed_cli_task

    return run_profile_backed_cli_task(sys.modules[__name__], project_root, args, runner)


def _build_task_handlers(args: argparse.Namespace, root: Path) -> Dict[str, Any]:
    from network_lab_cli_dispatch import _build_task_handlers as build_cli_task_handlers

    return build_cli_task_handlers(args, root, sys.modules[__name__])


def main(argv: Optional[List[str]] = None, project_root: Optional[Path] = None) -> int:
    from network_lab_cli_dispatch import main as cli_dispatch_main

    return cli_dispatch_main(argv=argv, project_root=project_root, lab_module=sys.modules[__name__])


if __name__ == "__main__":
    raise SystemExit(main())
