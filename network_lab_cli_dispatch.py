import argparse
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional

from network_lab_task_registry import (
    UnknownTaskError,
    get_cli_task_choices,
    resolve_task_handler,
)


def _build_parser(lab: ModuleType) -> argparse.ArgumentParser:
    examples = """examples:
  python network_lab.py
  python network_lab.py --interactive
  python network_lab.py --list-tasks
  python network_lab.py --list-tasks --verbose
  python network_lab.py --report-index
  python network_lab.py --portfolio-finalize
  python network_lab.py --task demo-flow
  python network_lab.py --task report-index --dry-run
  python network_lab.py --task report-index
  python network_lab.py --task day4-baseline --dry-run
  python network_lab.py --task day4-baseline
  python network_lab.py --task iperf3-performance --dry-run
  python network_lab.py --task iperf3-performance
  python network_lab.py --task day32-vrrp-precheck
  python network_lab.py --task day33-vrrp-dry-run
  python network_lab.py --task day34-vrrp-staged-plan
  python network_lab.py --task day35-vrrp-failover-validation
  python network_lab.py --task day39-vrrp-evidence-dashboard-integration
  python network_lab.py --task day40-v0.2-demo-readiness-review
  python network_lab.py --task day41-v0.2-release-packaging
  python network_lab.py --task intent-mapping-prototype --intent-text "show me the latest reports"
  python network_lab.py --task intent-safety-review --intent-text "do VRRP failover test"
  python network_lab.py --task intent-policy-matrix
  python network_lab.py --task safety-boundary-regression-matrix
  python network_lab.py --task safety-invariant-helper-review
  python network_lab.py --task thin-cli-regression-gate
  python network_lab.py --task post-refactor-compatibility-evidence-pack
  python network_lab.py --task ai-reviewer-summary-schema-contract
  python network_lab.py --task ai-reviewer-summary-fixture-renderer
  python network_lab.py --task ai-summary-prompt-contract
  python network_lab.py --task ai-summary-redaction-and-no-secret-policy
  python network_lab.py --task ai-summary-audit-trail-binding
  python network_lab.py --task ai-summary-dashboard-card-integration
  python network_lab.py --task disabled-ai-provider-interface-boundary
  python network_lab.py --task disabled-ai-provider-adapter-contract
  python network_lab.py --task ai-provider-disabled-by-default-safety-regression
  python network_lab.py --task ai-reviewer-export-package-integration
  python network_lab.py --task intent-workflow-demo
  python network_lab.py --task offline-mock-runtime
  python network_lab.py --task offline-mock-runtime-contract
  python network_lab.py --task offline-mock-runtime-review
  python network_lab.py --task wireguard-runner --dry-run
  python network_lab.py --task wireguard-runner --wireguard-config Set_WireguardVPN_lab02_config.json --dry-run
  python network_lab.py --task wireguard-runner
  python network_lab.py --task wireguard-runner --wireguard-config Set_WireguardVPN_lab02_config.json --allow-live-wireguard
  python network_lab.py --task report-index --profile topology_profiles/day14_lab_runner_profile.json

report-index and portfolio-finalize read existing report metadata and do not connect to devices.
day4-baseline delegates to the existing live SSH validation script.
iperf3-performance delegates to the existing live iperf3 performance script.
day32-vrrp-precheck runs read-only MikroTik print/export terse commands with a blocking safety guard.
day33-vrrp-dry-run generates local VRRP topology and command previews without SSH or RouterOS execution.
day34-vrrp-staged-plan generates a blocked staged apply plan and safety gate without SSH or RouterOS execution.
day35-vrrp-failover-validation observes manual external VRRP failover with read-only RouterOS commands and source-specific LAN pings.
day39-vrrp-evidence-dashboard-integration scans local VRRP docs/reports only and writes a summary report.
day40-v0.2-demo-readiness-review writes a report-only v0.2 demo readiness scope lock without SSH or live tests.
day41-v0.2-release-packaging writes a report-only v0.2 release packaging summary without SSH, live tests, voice/AI implementation, or tag creation.
intent-mapping-prototype classifies static text and prints a dry-run-only mapping proposal without API, voice, SSH, device access, or runner delegation.
intent-safety-review classifies static text through a dry-run confirmation gate and writes a report-only Day58 safety decision.
intent-policy-matrix writes a reviewer-facing Day59 JSON/HTML safety matrix without API, voice, SSH, device access, config.json, or mapped task execution.
intent-workflow-demo writes a Day60 reviewer walkthrough connecting Day57-Day59 without API, voice, SSH, device access, config.json, live execution, or mapped task execution.
offline-mock-runtime writes a fixed Day66 offline mock runtime skeleton report without API, voice, SSH, device access, config.json, live execution, or mapped task execution.
offline-mock-runtime-contract validates Day66 mock output fields and safety invariants without API, voice, SSH, device access, config.json, live execution, or mapped task execution.
offline-mock-runtime-review reviews Day66-Day67 report quality and evidence traceability without API, voice, SSH, device access, config.json, live execution, or mapped task execution.
mock-ai-decision-pipeline runs deterministic Day73 mock decisions after Day72 validation without AI API, SSH, device access, config.json, live execution, mapped task execution, or dashboard actions.
dry-run-plan-builder converts Day73 mock decisions into deterministic Day74 dry-run plan previews without AI API, SSH, device access, config.json, live execution, mapped task execution, or dashboard actions.
manual-review-approval-envelope wraps Day74 dry-run plans in deterministic Day75 reviewer sign-off envelopes without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, or dashboard actions.
runtime-audit-trail links Day73 decisions, Day74 dry-run plans, and Day75 approval envelopes into deterministic Day76 reviewer audit evidence without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, or dashboard actions.
runtime-safety-gate links Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, and Day76 audit records into deterministic Day77 locked runtime safety gates without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, execution controls, or dashboard actions.
runtime-safety-case links Day72 input validation, Day73 decisions, Day74 dry-run plans, Day75 approval envelopes, Day76 audit records, and Day77 locked gates into deterministic Day78 end-to-end reviewer safety cases without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, execution controls, or dashboard actions.
readonly-task-contract defines deterministic Day79 read-only task candidates, blocked write actions, destructive actions, unknown tasks, and manual classification cases without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, execution controls, or dashboard actions.
readonly-execution-broker defines deterministic Day80 read-only broker request records, contract checks, rejection records, review queue records, and mock execution request data without AI API, SSH, device access, config.json, live execution, mapped task execution, approval unlocks, execution controls, or dashboard actions.
broker-review-queue transforms Day80 broker records into deterministic Day81 reviewer queue and decision state records without AI API, SSH, device access, config.json, live execution, mapped task execution, execution unlocks, dashboard forms, POST routes, or action endpoints.
broker-review-queue-decision-state is a compatibility alias for broker-review-queue.
reviewer-decision-audit-summary summarizes Day81 queue decisions into deterministic Day82 reviewer audit evidence without AI API, AI SDK runtime, SSH, device access, config.json, live execution, mapped task execution, execution unlocks, dashboard forms, POST routes, or action endpoints.
readonly-executor-readiness-gate validates Day79-Day82 safety evidence as deterministic Day83 future-adapter candidate readiness only; it is not an executor and does not enable AI API, AI SDK runtime, SSH, device access, config.json, live execution, mapped task execution, approval/execution unlocks, dashboard forms, POST routes, or action endpoints.
readonly-executor-adapter-contract defines deterministic Day84 future adapter request/response/capability/evidence/validation shapes only; it is not an executor or adapter implementation and does not enable AI API, SSH, device access, live execution, mapped task execution, approval/execution unlocks, dashboard forms, POST routes, or action endpoints.
controlled-runner-harness runs deterministic Day86 runner-level safety regression scenarios over Day85-style adapter compatibility/evidence signals without AI API, SSH, device access, config.json, live command execution, mapped task execution, approval/execution unlocks, dashboard forms, POST routes, or action endpoints.
readonly-executor-phase-gate-review reviews Day83-Day86 safety evidence as deterministic Day87 phase gate evidence only; it may recommend Day88 DESIGN_ONLY but does not design or implement a real adapter, execute mapped tasks, open SSH, connect devices, run live/write commands, call APIs, or add dashboard actions.
readonly-executor-adapter-design defines deterministic Day88 real read-only executor adapter design contracts only; it remains DESIGN_ONLY, does not implement SSH or RouterOS connection, does not support live commands, and does not add dashboard actions.
real-adapter-safety-boundary-spec locks the Day89 pre-implementation safety boundary for any future real adapter; it remains DESIGN_ONLY, does not implement SSH or RouterOS connection, does not execute commands, and does not add dashboard actions.
real-adapter-implementation-plan produces the Day90 implementation-entry decision report; it remains PLANNING_ONLY and does not implement SSH, RouterOS commands, live adapter access, or automatic apply.
real-adapter-safety-scaffold produces the Day91 scaffold-only safety evidence after Day90 CONDITIONAL_GO; dangerous actions are denied, read-only candidates are future-only, and live-read remains blocked.
safety-boundary-regression-matrix writes a Day123 report-only safety regression matrix over mock, review-only, report-only, dry-run-only, fake-adapter-only, locked, disabled, parser-only, and Day120-Day122 refactor boundaries without executing reviewed tasks, SSH, live commands, mutation, unlocks, OpenAI API, voice runtime, or dashboard actions.
safety-invariant-helper-review writes a Day124 review-only helper consolidation report with all OpenAI API, voice input, SSH, live device, live command, runtime unlock, dashboard POST/action endpoint, broker, mapped task, write, and configuration change flags fixed false.
thin-cli-regression-gate writes a Day125 report-only regression gate proving thin CLI, registry, dispatch, report/formatter, safety helper, and smoke task behavior remained stable after Day120-Day124 without live execution, SSH, OpenAI API, or dashboard action endpoints.
post-refactor-compatibility-evidence-pack writes a Day126 report-only compatibility evidence pack for Day120-Day125; Day125 thin CLI evidence is one snapshot only, not a thin CLI budget gate or numeric enforcement mechanism.
ai-reviewer-summary-schema-contract writes a Day127 report-only AI reviewer summary data structure contract with schema validation and an example fixture; it does not implement Day128 renderer, Day129 prompt text, Day130 redaction policy, or execution unlocks.
ai-reviewer-summary-fixture-renderer writes a Day128 report-only fixture renderer for the existing Day127 schema fixture; it does not redefine schema, make AI decisions, define prompt or redaction policy, call OpenAI API, enable providers/APIs, or add execution unlocks.
ai-summary-prompt-contract writes a Day129 report-only prompt contract limited to reviewer summary text only; it does not call OpenAI API, add provider/API config, request tools, enable execution, implement Day130 redaction, implement Day131 audit binding, make AI decisions, or unlock the next phase.
ai-summary-redaction-and-no-secret-policy writes a Day130 deterministic local-only redaction report for reviewer summary text; it does not call OpenAI API, enable providers/APIs, add network calls, execute tools, bind Day131 audit trails, infer reviewer approval, add Day133 mock provider behavior, make AI decisions, or unlock the next phase.
ai-summary-audit-trail-binding writes a Day131 deterministic review-only audit binding over Day127-Day130 AI summary evidence; it does not call providers/APIs, execute AI, make AI decisions, infer reviewer approval, add Day133 mock provider behavior, invoke SSH/device/broker/runner/adapter paths, or unlock the next phase.
ai-summary-dashboard-card-integration writes a Day132 display-only dashboard card over Day127-Day131 AI summary evidence; it does not add Day133 provider boundary work, Day134 adapter contract work, providers/APIs, AI execution, AI decisions, reviewer approval, SSH/device/broker/runner/adapter paths, or next-phase unlocks.
disabled-ai-provider-interface-boundary writes a Day133 disabled AI provider interface boundary only; it is not Day134 adapter contract work and does not enable execution/provider/API, provider adapters, SDKs, external APIs, API keys, secrets, network calls, live AI calls, prompt submission, model selection, async jobs, retry, rate limit, or timeout provider behavior.
disabled-ai-provider-adapter-contract writes a Day134 disabled AI provider adapter contract shape only; it is not the next day's feature and does not enable provider/API/model/network/execution paths, SDK imports, API key handling, environment provider config, HTTP requests, async clients, subprocess providers, broker/runner/adapter execution, live backends, or next-phase unlocks.
ai-provider-disabled-by-default-safety-regression writes a Day135 disabled-by-default safety regression over Day134 evidence; consumer read is one read-only regression case and it does not instantiate providers, call APIs, invoke execution, activate registry/CLI/report paths, implement Day136, or unlock the next phase.
ai-reviewer-export-package-integration writes a Day136 deterministic review-only export package over Day127-Day135 AI reviewer evidence; this is not next-day functionality and execution / provider / API remain disabled.
wireguard-runner is dry-run by default and delegates to the existing WireGuard script only after explicit --allow-live-wireguard."""
    parser = argparse.ArgumentParser(
        description=f"Day14 {lab.DAY14_NAME}.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--list-tasks", action="store_true", help="List available and planned lab tasks.")
    parser.add_argument("--verbose", action="store_true", help="Show detailed task catalog metadata with --list-tasks.")
    parser.add_argument("--report-index", action="store_true", help="Scan local reports and write reports/report_index.html.")
    parser.add_argument(
        "--portfolio-finalize",
        action="store_true",
        help="Write the Day19 portfolio evidence index JSON and HTML without running live workflows.",
    )
    parser.add_argument(
        "--task",
        choices=get_cli_task_choices(),
        help="Task to run.",
    )
    parser.add_argument("--profile", default=str(lab.DEFAULT_PROFILE), help="Path to the Day14 lab runner profile JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Show report-index inputs and outputs without writing reports.")
    parser.add_argument(
        "--intent-text",
        default="",
        help="User text to classify for the Day57 mapping prototype or Day58 safety review dry-run.",
    )
    parser.add_argument("--interactive", action="store_true", help="Show the safe interactive Day14 menu.")
    parser.add_argument("--allow-live-wireguard", action="store_true", help="Allow guarded live WireGuard execution.")
    parser.add_argument(
        "--wireguard-config",
        default=lab.DAY12_WIREGUARD_CONFIG,
        help=f"Config path for the delegated Day12 WireGuard validation script. Default: {lab.DAY12_WIREGUARD_CONFIG}.",
    )
    parser.add_argument(
        "--wireguard-run-iperf",
        "--run-iperf",
        action="store_true",
        dest="run_iperf",
        help="For WireGuard runner live mode, also request iperf3 checks with --expect-connected.",
    )
    return parser


def _late_interactive_task_names(lab: ModuleType) -> set[str]:
    return {
        "report-index",
        "day4-baseline",
        "iperf3-performance",
        lab.DAY32_VRRP_PRECHECK_TASK_ID,
        lab.DAY33_VRRP_DRY_RUN_TASK_ID,
        lab.DAY34_VRRP_STAGED_PLAN_TASK_ID,
        lab.DAY35_VRRP_FAILOVER_TASK_ID,
        lab.WIREGUARD_RUNNER_TASK_ALIAS,
    }


def _run_profile_backed_cli_task(
    lab: ModuleType,
    project_root: Path,
    args: argparse.Namespace,
    runner: Any,
) -> int:
    profile_path = lab._resolve_project_path(project_root, args.profile)
    try:
        profile = lab.load_lab_runner_profile(profile_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return runner(profile, profile_path)


def _build_task_handlers(args: argparse.Namespace, root: Path, lab: ModuleType) -> Dict[str, Any]:
    return {
        "report-index": lambda: _run_profile_backed_cli_task(
            lab,
            root,
            args,
            lambda profile, profile_path: lab._run_report_index(
                profile,
                root,
                profile_path,
                dry_run=args.dry_run,
            ),
        ),
        "portfolio-finalize": lambda: lab._run_portfolio_finalization(root),
        "demo-flow": lambda: lab._run_day24_demo_flow(root),
        "day4-baseline": lambda: lab._run_day4_baseline(root, dry_run=args.dry_run),
        "iperf3-performance": lambda: lab._run_day8_performance(root, dry_run=args.dry_run),
        lab.DAY32_VRRP_PRECHECK_TASK_ID: lambda: lab._run_day32_vrrp_precheck(root, dry_run=args.dry_run),
        lab.DAY33_VRRP_DRY_RUN_TASK_ID: lambda: lab._run_day33_vrrp_dry_run(root),
        lab.DAY34_VRRP_STAGED_PLAN_TASK_ID: lambda: lab._run_day34_vrrp_staged_plan(root),
        lab.DAY35_VRRP_FAILOVER_TASK_ID: lambda: lab._run_day35_vrrp_failover_validation(root, dry_run=args.dry_run),
        lab.DAY39_VRRP_EVIDENCE_TASK_ID: lambda: lab._run_day39_vrrp_evidence_dashboard_integration(root),
        lab.DAY40_DEMO_READINESS_TASK_ID: lambda: lab._run_day40_demo_readiness_review(root),
        lab.DAY41_RELEASE_PACKAGING_TASK_ID: lambda: lab._run_day41_release_packaging(root),
        lab.DAY57_INTENT_MAPPING_TASK_ID: lambda: lab._run_day57_intent_mapping_prototype(args.intent_text),
        lab.DAY58_INTENT_SAFETY_REVIEW_TASK_ID: lambda: lab._run_day58_intent_safety_review(root, args.intent_text),
        lab.DAY59_INTENT_POLICY_MATRIX_TASK_ID: lambda: lab._run_day59_intent_policy_matrix(root),
        lab.DAY60_INTENT_WORKFLOW_DEMO_TASK_ID: lambda: lab._run_day60_intent_workflow_demo(root),
        lab.DAY66_OFFLINE_MOCK_RUNTIME_TASK_ID: lambda: lab._run_day66_offline_mock_runtime(root),
        lab.DAY67_OFFLINE_MOCK_RUNTIME_CONTRACT_TASK_ID: lambda: lab._run_day67_offline_mock_runtime_contract(root),
        lab.DAY68_OFFLINE_MOCK_RUNTIME_REVIEW_TASK_ID: lambda: lab._run_day68_offline_mock_runtime_review(root),
        lab.DAY73_MOCK_AI_DECISION_PIPELINE_TASK_ID: lambda: lab._run_day73_mock_ai_decision_pipeline(root),
        lab.DAY74_DRY_RUN_PLAN_BUILDER_TASK_ID: lambda: lab._run_day74_dry_run_plan_builder(root),
        lab.DAY75_MANUAL_REVIEW_APPROVAL_ENVELOPE_TASK_ID: lambda: lab._run_day75_manual_review_approval_envelope(root),
        lab.DAY76_RUNTIME_AUDIT_TRAIL_TASK_ID: lambda: lab._run_day76_runtime_audit_trail(root),
        lab.DAY77_RUNTIME_SAFETY_GATE_TASK_ID: lambda: lab._run_day77_runtime_safety_gate(root),
        lab.DAY78_RUNTIME_SAFETY_CASE_TASK_ID: lambda: lab._run_day78_runtime_safety_case(root),
        lab.DAY79_READONLY_TASK_CONTRACT_TASK_ID: lambda: lab._run_day79_readonly_task_contract(root),
        lab.DAY80_READONLY_EXECUTION_BROKER_TASK_ID: lambda: lab._run_day80_readonly_execution_broker(root),
        lab.DAY81_BROKER_REVIEW_QUEUE_TASK_ID: lambda: lab._run_day81_broker_review_queue(root),
        lab.DAY82_REVIEWER_DECISION_AUDIT_TASK_ID: lambda: lab._run_day82_reviewer_decision_audit_summary(root),
        lab.DAY83_READONLY_EXECUTOR_READINESS_GATE_TASK_ID: lambda: lab._run_day83_readonly_executor_readiness_gate(root),
        lab.DAY84_READONLY_EXECUTOR_ADAPTER_CONTRACT_TASK_ID: lambda: lab._run_day84_readonly_executor_adapter_contract(root),
        lab.DAY85_MOCK_ADAPTER_EVIDENCE_BINDING_TASK_ID: lambda: lab._run_day85_mock_adapter_evidence_binding(root),
        lab.DAY86_CONTROLLED_RUNNER_HARNESS_TASK_ID: lambda: lab._run_day86_controlled_runner_harness(root),
        lab.DAY87_READONLY_EXECUTOR_PHASE_GATE_REVIEW_TASK_ID: lambda: lab._run_day87_readonly_executor_phase_gate_review(root),
        lab.DAY88_REAL_READONLY_EXECUTOR_ADAPTER_DESIGN_TASK_ID: lambda: lab._run_day88_real_readonly_executor_adapter_design(root),
        lab.DAY89_REAL_ADAPTER_SAFETY_BOUNDARY_SPEC_TASK_ID: lambda: lab._run_day89_real_adapter_safety_boundary_spec(root),
        lab.DAY90_REAL_ADAPTER_IMPLEMENTATION_PLAN_TASK_ID: lambda: lab._run_day90_real_adapter_implementation_plan(root),
        lab.DAY91_REAL_ADAPTER_SAFETY_SCAFFOLD_TASK_ID: lambda: lab._run_day91_real_adapter_safety_scaffold(root),
        lab.DAY92_REAL_ADAPTER_EXECUTABLE_GUARDS_TASK_ID: lambda: lab._run_day92_real_adapter_executable_guards(root),
        lab.DAY93_GUARDED_FAKE_ADAPTER_CONTRACT_TASK_ID: lambda: lab._run_day93_guarded_fake_adapter_contract(root),
        lab.DAY94_ADAPTER_BOUNDARY_REGRESSION_MATRIX_TASK_ID: lambda: lab._run_day94_adapter_boundary_regression_matrix(root),
        lab.DAY95_ADAPTER_RESULT_NORMALIZATION_TASK_ID: lambda: lab._run_day95_adapter_result_normalization(root),
        lab.DAY96_READONLY_OUTPUT_PARSER_PROTOTYPE_TASK_ID: lambda: lab._run_day96_readonly_output_parser_prototype(root),
        lab.DAY97_PARSER_EVIDENCE_QUALITY_TASK_ID: lambda: lab._run_day97_parser_evidence_quality(root),
        lab.DAY98_PARSER_CLASSIFICATION_MATRIX_TASK_ID: lambda: lab._run_day98_parser_classification_matrix(root),
        lab.DAY99_PARSER_EVIDENCE_COVERAGE_AUDIT_TASK_ID: lambda: lab._run_day99_parser_evidence_coverage_audit(root),
        lab.DAY100_PARSER_PHASE_GATE_REVIEW_TASK_ID: lambda: lab._run_day100_parser_phase_gate_review(root),
        lab.DAY101_PARSER_EVIDENCE_CLOSURE_PLAN_TASK_ID: lambda: lab._run_day101_parser_evidence_closure_plan(root),
        lab.DAY102_PARSER_FIXTURE_EXPANSION_TASK_ID: lambda: lab._run_day102_parser_fixture_expansion(root),
        lab.DAY103_PARSER_EVIDENCE_MATRIX_TASK_ID: lambda: lab._run_day103_parser_evidence_matrix(root),
        lab.DAY104_PARSER_REVIEWER_ACCEPTANCE_GATE_TASK_ID: lambda: lab._run_day104_parser_reviewer_acceptance_gate(root),
        lab.DAY105_PARSER_ACCEPTANCE_CLOSURE_TASK_ID: lambda: lab._run_day105_parser_acceptance_closure(root),
        lab.DAY106_CODEX_AGENTS_INSTRUCTION_AUDIT_TASK_ID: lambda: lab._run_day106_codex_agents_instruction_audit(root),
        lab.DAY107_PARSER_REVIEWER_EVIDENCE_CONTRACT_TASK_ID: lambda: lab._run_day107_parser_reviewer_evidence_contract(root),
        lab.DAY108_PARSER_CONTRACT_CONSUMER_HANDOFF_TASK_ID: lambda: lab._run_day108_parser_contract_consumer_handoff(root),
        lab.DAY109_PARSER_CONSUMER_HANDOFF_READINESS_MATRIX_TASK_ID: lambda: lab._run_day109_parser_consumer_handoff_readiness_matrix(root),
        lab.DAY110_PARSER_CONSUMER_FINAL_GATE_TASK_ID: lambda: lab._run_day110_parser_consumer_final_gate(root),
        lab.DAY111_PARSER_CONSUMER_RELEASE_PACKAGE_TASK_ID: lambda: lab._run_day111_parser_consumer_release_package(root),
        lab.DAY112_PARSER_CONSUMER_RELEASE_REVIEW_INTAKE_TASK_ID: lambda: lab._run_day112_parser_consumer_release_review_intake(root),
        lab.DAY113_PARSER_CONSUMER_REVIEWER_TRIAGE_DECISION_LOG_TASK_ID: lambda: lab._run_day113_parser_consumer_reviewer_triage_decision_log(root),
        lab.DAY114_PARSER_CONSUMER_REVIEWER_TRIAGE_EVIDENCE_TRACEABILITY_TASK_ID: lambda: lab._run_day114_parser_consumer_reviewer_triage_evidence_traceability(root),
        lab.DAY115_PARSER_CONSUMER_REVIEWER_TRIAGE_CLOSURE_SUMMARY_TASK_ID: lambda: lab._run_day115_parser_consumer_reviewer_triage_closure_summary(root),
        lab.DAY116_REVIEWER_DEFERRED_ACTION_REGISTER_TASK_ID: lambda: lab._run_day116_reviewer_deferred_action_register(root),
        lab.DAY117_DEFERRED_ACTION_TRACEABILITY_REVIEW_TASK_ID: lambda: lab._run_day117_deferred_action_traceability_review(root),
        lab.DAY118_DEFERRED_ACTION_REVIEW_SEQUENCE_RUNBOOK_TASK_ID: lambda: lab._run_day118_deferred_action_review_sequence_runbook(root),
        lab.DAY119_REVIEWER_EVIDENCE_INTAKE_OUTCOME_LEDGER_TASK_ID: lambda: lab._run_day119_reviewer_evidence_intake_outcome_ledger(root),
        lab.DAY123_SAFETY_BOUNDARY_REGRESSION_MATRIX_TASK_ID: lambda: lab._run_day123_safety_boundary_regression_matrix(root),
        lab.DAY124_SAFETY_INVARIANT_HELPER_REVIEW_TASK_ID: lambda: lab._run_day124_safety_invariant_helper_review(root),
        lab.DAY125_THIN_CLI_REGRESSION_GATE_TASK_ID: lambda: lab._run_day125_thin_cli_regression_gate(root),
        lab.DAY126_POST_REFACTOR_COMPATIBILITY_EVIDENCE_PACK_TASK_ID: lambda: lab._run_day126_post_refactor_compatibility_evidence_pack(root),
        lab.DAY127_AI_REVIEWER_SUMMARY_SCHEMA_CONTRACT_TASK_ID: lambda: lab._run_day127_ai_reviewer_summary_schema_contract(root),
        lab.DAY128_AI_REVIEWER_SUMMARY_FIXTURE_RENDERER_TASK_ID: lambda: lab._run_day128_ai_reviewer_summary_fixture_renderer(root),
        lab.DAY129_AI_SUMMARY_PROMPT_CONTRACT_TASK_ID: lambda: lab._run_day129_ai_summary_prompt_contract(root),
        lab.DAY130_AI_SUMMARY_REDACTION_POLICY_TASK_ID: lambda: lab._run_day130_ai_summary_redaction_policy(root),
        lab.DAY131_AI_SUMMARY_AUDIT_TRAIL_BINDING_TASK_ID: lambda: lab._run_day131_ai_summary_audit_trail_binding(root),
        lab.DAY132_AI_SUMMARY_DASHBOARD_CARD_INTEGRATION_TASK_ID: lambda: lab._run_day132_ai_summary_dashboard_card_integration(root),
        lab.DAY133_DISABLED_AI_PROVIDER_INTERFACE_BOUNDARY_TASK_ID: lambda: lab._run_day133_disabled_ai_provider_interface_boundary(root),
        lab.DAY134_DISABLED_AI_PROVIDER_ADAPTER_CONTRACT_TASK_ID: lambda: lab._run_day134_disabled_ai_provider_adapter_contract(root),
        lab.DAY135_AI_PROVIDER_DISABLED_BY_DEFAULT_SAFETY_REGRESSION_TASK_ID: lambda: lab._run_day135_ai_provider_disabled_by_default_safety_regression(root),
        lab.DAY136_AI_REVIEWER_EXPORT_PACKAGE_INTEGRATION_TASK_ID: lambda: lab._run_day136_ai_reviewer_export_package_integration(root),
        lab.WIREGUARD_RUNNER_TASK_ALIAS: lambda: lab._run_wireguard_runner(
            root,
            dry_run=args.dry_run,
            allow_live_wireguard=args.allow_live_wireguard,
            config_path=args.wireguard_config,
            run_iperf=args.run_iperf,
        ),
    }


def main(
    argv: Optional[List[str]] = None,
    project_root: Optional[Path] = None,
    lab_module: Optional[ModuleType] = None,
) -> int:
    if lab_module is None:
        import network_lab as lab_module

    parser = _build_parser(lab_module)
    args = parser.parse_args(argv)
    root = Path(project_root or Path.cwd()).resolve()

    if args.list_tasks:
        lab_module._print_task_list(verbose=args.verbose)
        return 0
    if args.report_index:
        return lab_module._run_report_visibility_index(root)
    if args.portfolio_finalize:
        return lab_module._run_portfolio_finalization(root)

    handlers = _build_task_handlers(args, root, lab_module)
    resolved_task = None
    if args.task:
        try:
            resolved_task = resolve_task_handler(args.task, handlers)
        except UnknownTaskError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        if resolved_task.canonical_name not in _late_interactive_task_names(lab_module):
            return resolved_task.handler()

    profile_path = lab_module._resolve_project_path(root, args.profile)
    try:
        profile = lab_module.load_lab_runner_profile(profile_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.interactive or not args.task:
        return lab_module.run_interactive_menu(
            profile,
            root,
            profile_path,
            wireguard_config=args.wireguard_config,
        )

    if resolved_task:
        return resolved_task.handler()

    return 2

