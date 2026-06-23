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
  python network_lab.py report-index
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
  python network_lab.py --task project-folder-organization-decision-gate
  python network_lab.py --task project-folder-organization-dry-run-inventory-gate
  python network_lab.py --task docs-only-move-dry-run-evidence-plan
  python network_lab.py --task folder-move-compatibility-gate
  python network_lab.py --task ai-assistance-review-demo-package
  python network_lab.py --task ai-summary-to-dry-run-draft-display-contract
  python network_lab.py --task dry-run-draft-safety-diff-viewer
  python network_lab.py --task v0.4-ai-assistance-compatibility-review
  python network_lab.py --task v0.4-ai-assistance-evidence-freeze-package
  python network_lab.py --task v0.4-ai-assistance-non-advancement-gate
  python network_lab.py --task ai-assistance-deferred-risk-register
  python network_lab.py --task ai-assistance-demo-export-draft-display-consistency-audit
  python network_lab.py --task ai-assistance-docs-registry-report-index-consistency-audit
  python network_lab.py --task v04-ai-assistance-phase-gate-closure-review
  python network_lab.py --task v04-ai-assistance-closure-evidence-index
  python network_lab.py --task post-closure-reference-integrity-audit
  python network_lab.py --task post-closure-evidence-baseline-lock-review
  python network_lab.py --task v05-ai-assistance-reopen-rationale
  python network_lab.py --task v05-ai-assistance-input-boundary-contract
  python network_lab.py --task v05-ai-assistance-output-template-contract
  python network_lab.py --task v05-ai-assistance-reviewer-only-fixture-renderer
  python network_lab.py --task v05-ai-assistance-safety-regression-matrix
  python network_lab.py --task v05-ai-assistance-phase-gate-review
  python network_lab.py --task phase2a-readonly-job-runner-framework
  python network_lab.py --task phase2a-03-dry-run-job-plan-gate
  python network_lab.py --task phase2a-04-plan-evidence-ledger
  python network_lab.py --task phase2a-05-dry-run-result-envelope-renderer
  python network_lab.py --task phase2a-06-negative-regression-matrix
  python network_lab.py --task phase2a-07-vrrp-dry-run-validation-pack
  python network_lab.py --task phase2a-08-jobs-catalog-ui-readiness-planning-pack
  python network_lab.py --task phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack
  python network_lab.py --task phase2a-10-safe-boundary-implementation-readiness-artifact
  python network_lab.py --task phase2a-11-phase-closure-final-readiness-review
  python network_lab.py --task phase2b-00-authorization-scope-gate-review
  python network_lab.py --task phase2b-00a-planning-only-owner-authorization-statement
  python network_lab.py --task phase2b-01-planning-scope-design-only
  python network_lab.py --task phase2b-02-safety-gate-design-planning-only
  python network_lab.py --task phase2b-04-safety-artifact-crosswalk-gap-review
  python network_lab.py --task phase2b-06-implementation-entry-gate-and-first-slice-readiness-review
  python network_lab.py --task phase2b-07-first-slice-definition-pack
  python network_lab.py --task phase2b-08-first-slice-implementation-authorization-gate-planning-only
  python network_lab.py --task phase2b-09-first-slice-implementation-plan-pack-planning-only
  python network_lab.py --task phase2b-10-day1-day160-reference-mapping-for-future-first-slice-planning-only
  python network_lab.py --task phase2b-11-project-consolidation-and-implementation-entry-map-planning-only
  python network_lab.py --task phase2b-12-future-implementation-authorization-review-planning-only
  python network_lab.py --task phase2b-13-first-slice-final-selection-gate-planning-only
  python network_lab.py --task phase2b-14-first-slice-implementation-kickoff-gate
  python network_lab.py --task phase2c-01-local-static-job-first-slice
  python network_lab.py --task phase2c-02-post-first-slice-acceptance-review
  python network_lab.py --task phase2c-03-next-slice-decision-gate-authorization-review
  python network_lab.py --task phase2c-04-next-slice-candidate-inventory
  python network_lab.py --task phase2c-05-next-slice-safety-delta-review
  python network_lab.py --task phase2c-06-next-slice-final-selection-gate
  python network_lab.py --task phase2c-07-next-slice-implementation-kickoff-gate
  python network_lab.py --task phase2c-08-next-slice-implementation
  python network_lab.py --task phase2c-08-artifact-validation-job
  python network_lab.py --task phase2c-09-post-next-slice-acceptance-review
  python network_lab.py --task phase2c-10-next-slice-decision-gate-authorization-review
  python network_lab.py --task phase2c-11-interview-mvp-scope-architecture-gate
  python network_lab.py --task phase2c-12-interview-mvp-implementation-slice-candidate-inventory
  python network_lab.py --task phase2c-13-interview-mvp-implementation-slice-safety-delta-review
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
project-folder-organization-decision-gate writes a Day137 decision-only project folder organization gate; it does not move, delete, rename, rewrite imports, enable execution/provider/API, or implement the deferred AI Assistance Review Demo Package.
project-folder-organization-dry-run-inventory-gate writes a Day138 dry-run-only project folder inventory; it does not move, delete, rename, change import paths, enable execution/provider/API, allow SSH/live commands, invoke adapters/brokers/runners, or unlock the next phase.
docs-only-move-dry-run-evidence-plan writes a Day139 docs-only move dry-run evidence plan based on Day138 docs candidates; it does not move, rename, modify imports, enable execution/provider/API, allow SSH/live commands, invoke adapters/brokers/runners, decide migration is allowed, or implement Day140.
folder-move-compatibility-gate writes a Day140 review-only compatibility gate for entering a future first-batch docs-only move review; it does not move files/folders, modify imports, enable execution/provider/API, allow SSH/NETCONF/RESTCONF/live commands, invoke adapters/brokers/runners, or implement the next-day feature.
ai-assistance-review-demo-package writes a Day141 review-only AI assistance review demo package over existing Day127-Day140 artifacts; it does not execute source, open execution/provider/API, call OpenAI API, call AI providers, make AI decisions, access live devices, use SSH, implement Day142, continue folder moves, clean tmp folders, or unlock the next phase.
ai-summary-to-dry-run-draft-display-contract writes a Day142 display-only contract that maps already-produced AI reviewer summary text/metadata into a dry-run draft display payload without enabling providers, APIs, model invocation, execution, SSH, NETCONF, RESTCONF, live-device access, config write/apply, adapters, or next phase.
dry-run-draft-safety-diff-viewer writes a Day143 review-only/display-only diff over two existing dry-run draft display payload fixtures; it does not redo Day142, implement Day144, call providers/APIs, execute commands, access live devices, use SSH, save/apply drafts, or unlock the next phase.
v0.4-ai-assistance-compatibility-review writes a Day144 review-only compatibility review for existing Day127-Day143 AI assistance artifacts against a future v0.4 review package; it is not Day145, does not open execution/provider/API, does not call OpenAI API or any provider, does not use SSH/NETCONF/RESTCONF/RouterOS/live devices, does not redo folder move compatibility, and keeps next_phase_allowed=false.
v0.4-ai-assistance-evidence-freeze-package writes a Day145 review-only evidence freeze package over Day127-Day144; Day144 remains frozen and untouched, no folders move, no cleanup runs, providers/APIs/models/SSH/live devices remain disabled, and next_phase_allowed=false.
v0.4-ai-assistance-non-advancement-gate writes a Day146 review-only gate over Day127-Day145; Day145 remains frozen and untouched, Day147 and next phase stay blocked, no providers/APIs/models/runtimes/mapped tasks/SSH/live devices/folder moves/cleanup run, and next_phase_allowed=false.
ai-assistance-deferred-risk-register writes a Day147 review-only deferred risk register; Day145 freeze and Day146 non-advancement remain authoritative, provider/API/model/execution/network/live-device paths stay disabled, and next_phase_allowed=false.
ai-assistance-demo-export-draft-display-consistency-audit writes a Day148 review-only consistency audit over Day141 demo, Day136 export package, Day142 dry-run draft, and Day143 diff viewer display wording and safety semantics without enabling execution/provider/API/model/device/adapter/broker/runner paths or next-phase advancement.
ai-assistance-docs-registry-report-index-consistency-audit writes a Day149 review-only/report-only consistency audit over Day145-Day149 AI Assistance docs, task registry, CLI task names, report-index registration, report paths, day labels, and disabled execution/provider/API flags without enabling providers, APIs, model calls, execution paths, live devices, SSH, adapters, brokers, runners, secrets, Day150, or next phase.
v04-ai-assistance-phase-gate-closure-review writes a Day150 review-only/report-only closure review for the v0.4 AI Assistance phase gate; it preserves Day145-Day149 conclusions, keeps README as a status summary only, and keeps execution, provider, API, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, and next phase disabled.
v04-ai-assistance-closure-evidence-index writes a Day151 review-only/report-only closure evidence index over Day145-Day150 artifacts without rerunning source tasks or enabling execution, providers, APIs, model calls, device access, SSH, NETCONF, RESTCONF, secrets, live network I/O, adapters, brokers, runners, or next phase.
post-closure-reference-integrity-audit writes a Day152 review-only/report-only reference integrity audit over README, docs, registry, CLI, task catalog, and report-index references after Day151 merge without redoing Day145-Day151 safety judgments, rerunning source tasks, or enabling execution/provider/API/model/device/SSH/NETCONF/RESTCONF/live paths.
post-closure-evidence-baseline-lock-review writes a Day154 review-only/report-only post-closure evidence baseline lock review plus SDD operating contract draft after Day153 without supplementing Day153, implementing next-day features, or enabling execution/provider/API/model/live-device paths.
v05-ai-assistance-reopen-rationale writes a Day155 docs-only/rationale-only/review-only reopen rationale for v0.5 AI Assistance without enabling providers, APIs, model calls, direct commands, executor unlocks, secrets, live devices, or next phase.
v05-ai-assistance-input-boundary-contract writes a Day156 review-only/report-only input boundary contract without reading secrets, config.json, live devices, providers, APIs, voice input, or next phase.
v05-ai-assistance-output-template-contract writes a Day157 review-only/report-only fixed output template contract without command, executor, provider, secret, approval unlock, or next phase fields.
v05-ai-assistance-reviewer-only-fixture-renderer writes a Day158 deterministic reviewer-only fixture renderer without provider/API/model/runtime/live-device behavior.
v05-ai-assistance-safety-regression-matrix writes a Day159 review-only/report-only safety regression matrix with unsafe capability flags kept false.
v05-ai-assistance-phase-gate-review writes a Day160 phase gate review package only; it is not phase gate approval and keeps next_phase_allowed=false.
phase2a-readonly-job-runner-framework writes the Phase 2A-02 job spec contract validator and negative input matrix evidence with allowlisted schemas as the primary boundary; it does not enable live execution, SSH, NETCONF, RESTCONF, RouterOS, external APIs, AI providers/model calls, backup_config, config changes, arbitrary commands, shell, or script paths.
phase2a-03-dry-run-job-plan-gate writes the Phase 2A-03 request normalization and dry-run plan gate evidence; it creates only non-executable dry-run plans for allowed mock/local/read-only requests and rejects unsafe requests before runner or adapter invocation.
phase2a-04-plan-evidence-ledger writes the Phase 2A-04 report-only traceability ledger binding Phase 2A-03 dry-run plans and rejected unsafe requests to sanitized evidence records; it does not invoke runners, adapters, live execution, provider/API/model calls, Phase 2B, or real execution.
phase2a-05-dry-run-result-envelope-renderer writes the Phase 2A-05 result envelope and renderer over the existing Phase 2A-04 report interface; result_envelope and render_outputs remain separate, and it does not rebuild planner or ledger behavior.
phase2a-06-negative-regression-matrix writes the Phase 2A-06 negative regression matrix only; unsafe inputs remain rejected, redacted, and non-executing, and next-phase authorization remains false.
phase2a-07-vrrp-dry-run-validation-pack writes the Phase 2A-07 Day1-Day160 artifact-to-Jobs dry-run validation pack; it maps local artifact patterns to Jobs, keeps VRRP as the first concrete mock example, rejects live VRRP requests, and keeps live access, execution, and next-phase authorization false.
phase2a-08-jobs-catalog-ui-readiness-planning-pack writes the Phase 2A-08 multi-job catalog/card UI readiness planning pack; it is not executable and keeps runners, adapters, brokers, live access, providers/APIs/models, real backup, real VRRP testing, and next-phase authorization false.
phase2a-09-jobs-ui-display-contract-mock-screen-readiness-pack writes the Phase 2A-09 /network/jobs display contract, badge rules, empty/error states, and mock screen data over the full Phase 2A-08 Jobs Catalog without adding execution or real frontend API integration.
phase2a-10-safe-boundary-implementation-readiness-artifact writes the Phase 2A-10 phase-wide safe-boundary implementation readiness artifact without adding Phase 2B, execution, runners, adapters, brokers, SSH, NETCONF, RESTCONF, live device access, providers/APIs/models, secrets, or weaker safety gates.
phase2a-11-phase-closure-final-readiness-review writes the Phase 2A-11 phase-wide closure and final readiness review over the Phase 2A initial read-only framework through Phase 2A-10; Phase 2B remains unauthorized and no execution, runner, adapter, broker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, approval execution, or safety-gate relaxation is enabled.
phase2b-00-authorization-scope-gate-review writes the Phase 2B-00 review-only authorization/scope gate over Phase 2A closure and next-phase criteria; Phase 2B remains not authorized and no Phase 2B-01, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, or safety-gate relaxation is enabled.
phase2b-00a-planning-only-owner-authorization-statement records a review-only owner authorization for Phase 2B planning-only scope work; it permits documentation/readiness/specification scope design only and still forbids Phase 2B implementation, Phase 2B-01, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, and safety-gate relaxation.
phase2b-01-planning-scope-design-only writes the Phase 2B-01 planning-only scope design artifact; it may discuss conceptual mock runner, local queue, approval gate, dry-run envelope, and read-only result lifecycle boundaries but forbids implementation, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, and safety-gate relaxation.
phase2b-02-safety-gate-design-planning-only writes the Phase 2B-02 safety gate design planning-only artifact; it defines future owner authorization, scope, forbidden capability, no-execution, no-secret, no-live-device, no-provider/API/model, approval design, traceability, validation, and stop-condition gates while forbidding implementation, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, and safety-gate relaxation.
phase2b-04-safety-artifact-crosswalk-gap-review writes the Phase 2B-04 planning-only crosswalk and gap review over existing Day1-Day160, Phase 2A, and Phase 2B safety artifacts; it does not create a new safety matrix or enable implementation, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, or safety-gate relaxation.
phase2b-06-implementation-entry-gate-and-first-slice-readiness-review writes the Phase 2B-06 planning-only implementation entry gate and first-slice readiness review; it may only authorize defining the next first-slice planning artifact and does not implement a slice, create a second safety matrix, or enable implementation, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend API, backup, VRRP execution, approval bypass, or safety-gate relaxation.
phase2b-07-first-slice-definition-pack writes the Phase 2B-07 planning-only first-slice definition pack; it defines a future local static job-definition and evidence-contract boundary and does not re-run Phase 2B-06, re-create safety gates, implement the slice, create a second safety matrix, or enable implementation, execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend integration, backup, validation, command execution, approval bypass, or safety-gate relaxation.
phase2b-08-first-slice-implementation-authorization-gate-planning-only writes the Phase 2B-08 planning-only first-slice implementation authorization gate; it may only authorize moving to Phase 2B-09 planning and does not authorize implementation, re-run Phase 2B-06, rebuild safety gates, create a second safety matrix, or enable execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend integration, backup, validation, command execution, approval bypass, or safety-gate relaxation.
phase2b-09-first-slice-implementation-plan-pack-planning-only writes the Phase 2B-09 planning-only first-slice implementation plan pack; it references the Phase 2B-08 GO_TO_2B_09_PLANNING_ONLY gate verdict as input, does not duplicate the gate, and does not implement the slice, create a second safety matrix, or enable execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend integration, backup, validation, command execution, approval bypass, or safety-gate relaxation.
phase2b-10-day1-day160-reference-mapping-for-future-first-slice-planning-only writes the Phase 2B-10 planning-only Day1-Day160 reference mapping for a future first slice; it references existing Day1-Day160, Phase 2A, and Phase 2B controls without copying, rewriting, replacing, creating a second safety matrix, duplicating Phase 2B-05/06/08/09, authorizing implementation, or enabling execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, frontend integration, backup, validation, command execution, approval bypass, or safety-gate relaxation.
phase2b-11-project-consolidation-and-implementation-entry-map-planning-only writes the Phase 2B-11 planning-only project consolidation and implementation entry map; it adds a review-only future plan and drift check without creating future phases, authorizing implementation, selecting a first slice, replacing Phase 2B-10, rewriting Day1-Day160, creating a second safety matrix, or enabling execution, runner, adapter, broker, scheduler, queue worker, SSH, NETCONF, RESTCONF, live device, provider/API/model, token, credential, secret, backup, validation, command execution, config change, approval bypass, or safety-gate relaxation.
phase2b-12-future-implementation-authorization-review-planning-only writes the Phase 2B-12 planning-only future implementation authorization review; it keeps Phase 2B planning-only, states future implementation is not authorized, treats listed job types as examples only, lists missing authorization conditions and scope drift risks, and does not create a first slice, runner, adapter, broker, scheduler, queue worker, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, validation, command execution, config change, second safety matrix, Day1-Day160 replacement, approval bypass, or safety-gate relaxation.
phase2b-13-first-slice-final-selection-gate-planning-only writes the Phase 2B-13 planning-only first-slice final selection gate; it selects local_static_job_definition_and_evidence_contract_slice as the future first slice, keeps implementation forbidden until a separate Phase 2B-14 authorization gate, and does not touch Phase 2C, runner, adapter, broker, scheduler, queue worker, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, validation, command execution, config change, second safety matrix, Day1-Day160 replacement, approval bypass, or safety-gate relaxation.
phase2b-14-first-slice-implementation-kickoff-gate writes the Phase 2B-14 authorization kickoff gate; it confirms scope in writing, treats job types as examples only, keeps the selected first slice as only the first future target, and does not implement local_static_job or add runner, adapter, broker, scheduler, queue, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, config change, custom command/script execution, second safety matrix, Day1-Day160 replacement, approval bypass, or safety-gate relaxation.
phase2c-01-local-static-job-first-slice writes the Phase 2C-01 local_static_job first-slice report; it implements only a local/static/deterministic data contract and does not add runner, adapter, broker, scheduler, queue, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, shell command, custom script, backup execution, config change execution, Day1-Day160 replacement, or a second safety matrix.
phase2c-02-post-first-slice-acceptance-review writes the Phase 2C-02 post-first-slice acceptance review; it accepts Phase 2C-01 reviewer evidence without rerunning the source task, regenerating the source report, modifying the first-slice implementation, authorizing the next slice, or adding runner, adapter, broker, scheduler, queue, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, shell command, custom script, backup execution, config change execution, Day1-Day160 replacement, or a second safety matrix.
phase2c-03-next-slice-decision-gate-authorization-review writes the Phase 2C-03 planning-only next-slice decision gate; it allows future next-slice planning after reviewing local_static_job and Phase 2C-02 acceptance evidence, while next-slice implementation remains unauthorized and no runner, adapter, broker, scheduler, queue, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, config change, Day1-Day160 replacement, or second safety matrix is opened.
phase2c-04-next-slice-candidate-inventory writes the Phase 2C-04 planning-only next-slice candidate inventory; it lists candidates only and does not select a next slice, authorize Phase 2C-05, implement or scaffold a candidate, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-05-next-slice-safety-delta-review writes the Phase 2C-05 planning-only next-slice safety delta review; it compares Phase 2C-04 candidates against existing safety boundaries only and does not select a next slice, authorize Phase 2C-06/2C-07/2C-08, implement a candidate, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-06-next-slice-final-selection-gate writes the Phase 2C-06 planning-only final selection gate; it selects candidate-02 artifact_validation_job using Phase 2C-04 and Phase 2C-05 safety evidence and does not authorize Phase 2C-07/2C-08, implement the selected slice, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-07-next-slice-implementation-kickoff-gate writes the Phase 2C-07 authorization-only kickoff gate; it authorizes artifact_validation_job for a later separate Phase 2C-08 only and does not start Phase 2C-08, implement the selected slice, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, real command execution, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-08-next-slice-implementation writes the Phase 2C-08 implementation report for the selected artifact_validation_job; it validates fixed local repository artifacts and prior Phase 2C evidence only, without adding runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, real command execution, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-08-artifact-validation-job is an alias for phase2c-08-next-slice-implementation.
phase2c-09-post-next-slice-acceptance-review writes the Phase 2C-09 report-only acceptance review for existing Phase 2C-08 artifact_validation_job evidence; it does not select another slice, start Phase 2C-10, modify the implementation, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, real command execution, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-10-next-slice-decision-gate-authorization-review writes the Phase 2C-10 planning-only next-slice decision gate after Phase 2C-09 acceptance; it allows only entry into Phase 2C-11 planning and does not list candidates, select a slice, authorize implementation, start Phase 2C-11, or add runner, adapter, broker, scheduler, queue, worker, agent loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secret, real command execution, backup, config change, Day1-Day160 replacement, AGENTS.md modification, or second safety matrix.
phase2c-11-interview-mvp-scope-architecture-gate writes the Phase 2C-11 planning-only Interview MVP scope and architecture authorization gate; it authorizes later implementation planning only and does not implement or start runner, adapter, result envelope, report renderer, demo jobs, Phase 2C-12, scheduler, queue, worker, AI agent loop, SSH, NETCONF, RESTCONF, live device, provider/API/model, secrets, backup, config change, production execution, AGENTS.md modification, Phase 2C-10 modification, Day1-Day160 replacement, or second safety matrix.
phase2c-12-interview-mvp-implementation-slice-candidate-inventory writes the Phase 2C-12 planning-only Interview MVP implementation slice candidate inventory; it lists candidates only and does not select a slice, authorize implementation, start implementation, start Phase 2C-13, or add runner, adapter, result envelope, report renderer, demo jobs, scheduler, queue, worker, AI loop, execution path, SSH, NETCONF, RESTCONF, live device, provider/API/model, secrets, backup, config change, production execution, AGENTS.md modification, Day1-Day160 replacement, or second safety matrix.
phase2c-13-interview-mvp-implementation-slice-safety-delta-review writes the Phase 2C-13 planning-only Interview MVP implementation slice safety delta review; it derives candidates only from Phase 2C-12 and does not select a unique slice, authorize implementation, start implementation, start Phase 2C-14, or add runner, adapter, execution path, queue, scheduler, worker, AI loop, SSH, NETCONF, RESTCONF, live device, provider/API/model, secrets, backup, config change, Day1-Day160 replacement, or second safety matrix.
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
    parser.add_argument(
        "positional_task",
        nargs="?",
        choices=get_cli_task_choices(),
        metavar="task",
        help="Compatibility task name. Equivalent to --task when --task is omitted.",
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
        lab.DAY137_PROJECT_FOLDER_ORGANIZATION_DECISION_GATE_TASK_ID: lambda: lab._run_day137_project_folder_organization_decision_gate(root),
        lab.DAY138_PROJECT_FOLDER_ORGANIZATION_DRY_RUN_INVENTORY_GATE_TASK_ID: lambda: lab._run_day138_project_folder_organization_dry_run_inventory_gate(root),
        lab.DAY139_DOCS_ONLY_MOVE_DRY_RUN_EVIDENCE_PLAN_TASK_ID: lambda: lab._run_day139_docs_only_move_dry_run_evidence_plan(root),
        lab.DAY140_FOLDER_MOVE_COMPATIBILITY_GATE_TASK_ID: lambda: lab._run_day140_folder_move_compatibility_gate(root),
        lab.DAY141_AI_ASSISTANCE_REVIEW_DEMO_PACKAGE_TASK_ID: lambda: lab._run_day141_ai_assistance_review_demo_package(root),
        lab.DAY142_AI_SUMMARY_TO_DRY_RUN_DRAFT_DISPLAY_CONTRACT_TASK_ID: lambda: lab._run_day142_ai_summary_to_dry_run_draft_display_contract(root),
        lab.DAY143_DRY_RUN_DRAFT_SAFETY_DIFF_VIEWER_TASK_ID: lambda: lab._run_day143_dry_run_draft_safety_diff_viewer(root),
        lab.DAY144_V04_AI_ASSISTANCE_COMPATIBILITY_REVIEW_TASK_ID: lambda: lab._run_day144_v04_ai_assistance_compatibility_review(root),
        lab.DAY145_V04_AI_ASSISTANCE_EVIDENCE_FREEZE_PACKAGE_TASK_ID: lambda: lab._run_day145_v04_ai_assistance_evidence_freeze_package(root),
        lab.DAY146_V04_AI_ASSISTANCE_NON_ADVANCEMENT_GATE_TASK_ID: lambda: lab._run_day146_v04_ai_assistance_non_advancement_gate(root),
        lab.DAY147_AI_ASSISTANCE_DEFERRED_RISK_REGISTER_TASK_ID: lambda: lab._run_day147_ai_assistance_deferred_risk_register(root),
        lab.DAY148_AI_ASSISTANCE_DISPLAY_CONSISTENCY_AUDIT_TASK_ID: lambda: lab._run_day148_ai_assistance_display_consistency_audit(root),
        lab.DAY149_AI_ASSISTANCE_DOCS_REGISTRY_REPORT_INDEX_CONSISTENCY_AUDIT_TASK_ID: lambda: lab._run_day149_ai_assistance_docs_registry_report_index_consistency_audit(root),
        lab.DAY150_V04_AI_ASSISTANCE_PHASE_GATE_CLOSURE_REVIEW_TASK_ID: lambda: lab._run_day150_v04_ai_assistance_phase_gate_closure_review(root),
        lab.DAY151_V04_AI_ASSISTANCE_CLOSURE_EVIDENCE_INDEX_TASK_ID: lambda: lab._run_day151_v04_ai_assistance_closure_evidence_index(root),
        lab.DAY152_POST_CLOSURE_REFERENCE_INTEGRITY_AUDIT_TASK_ID: lambda: lab._run_day152_post_closure_reference_integrity_audit(root),
        lab.DAY154_POST_CLOSURE_EVIDENCE_BASELINE_LOCK_REVIEW_TASK_ID: lambda: lab._run_day154_post_closure_evidence_baseline_lock_review(root),
        lab.DAY155_V05_AI_ASSISTANCE_REOPEN_RATIONALE_TASK_ID: lambda: lab._run_day155_v05_ai_assistance_reopen_rationale(root),
        lab.DAY156_V05_AI_ASSISTANCE_INPUT_BOUNDARY_CONTRACT_TASK_ID: lambda: lab._run_day156_v05_ai_assistance_input_boundary_contract(root),
        lab.DAY157_V05_AI_ASSISTANCE_OUTPUT_TEMPLATE_CONTRACT_TASK_ID: lambda: lab._run_day157_v05_ai_assistance_output_template_contract(root),
        lab.DAY158_V05_AI_ASSISTANCE_REVIEWER_ONLY_FIXTURE_RENDERER_TASK_ID: lambda: lab._run_day158_v05_ai_assistance_reviewer_only_fixture_renderer(root),
        lab.DAY159_V05_AI_ASSISTANCE_SAFETY_REGRESSION_MATRIX_TASK_ID: lambda: lab._run_day159_v05_ai_assistance_safety_regression_matrix(root),
        lab.DAY160_V05_AI_ASSISTANCE_PHASE_GATE_REVIEW_TASK_ID: lambda: lab._run_day160_v05_ai_assistance_phase_gate_review(root),
        lab.PHASE2A_READONLY_JOB_RUNNER_FRAMEWORK_TASK_ID: lambda: lab._run_phase2a_readonly_job_runner_framework(root),
        lab.PHASE_2A_03_DRY_RUN_JOB_PLAN_GATE_TASK_ID: lambda: lab._run_phase_2a_03_dry_run_job_plan_gate(root),
        lab.PHASE_2A_04_PLAN_EVIDENCE_LEDGER_TASK_ID: lambda: lab._run_phase_2a_04_plan_evidence_ledger(root),
        lab.PHASE_2A_05_DRY_RUN_RESULT_ENVELOPE_RENDERER_TASK_ID: lambda: lab._run_phase_2a_05_dry_run_result_envelope_renderer(root),
        lab.PHASE_2A_06_NEGATIVE_REGRESSION_MATRIX_TASK_ID: lambda: lab._run_phase_2a_06_negative_regression_matrix(root),
        lab.PHASE_2A_07_VRRP_DRY_RUN_VALIDATION_PACK_TASK_ID: lambda: lab._run_phase_2a_07_vrrp_dry_run_validation_pack(root),
        lab.PHASE_2A_08_JOBS_CATALOG_UI_READINESS_PLANNING_PACK_TASK_ID: lambda: lab._run_phase_2a_08_jobs_catalog_ui_readiness_planning_pack(root),
        lab.PHASE_2A_09_JOBS_UI_DISPLAY_CONTRACT_MOCK_SCREEN_READINESS_PACK_TASK_ID: lambda: lab._run_phase_2a_09_jobs_ui_display_contract_mock_screen_readiness_pack(root),
        lab.PHASE_2A_10_SAFE_BOUNDARY_IMPLEMENTATION_READINESS_ARTIFACT_TASK_ID: lambda: lab._run_phase_2a_10_safe_boundary_implementation_readiness_artifact(root),
        lab.PHASE_2A_11_PHASE_CLOSURE_FINAL_READINESS_REVIEW_TASK_ID: lambda: lab._run_phase_2a_11_phase_closure_final_readiness_review(root),
        lab.PHASE_2B_00_AUTHORIZATION_SCOPE_GATE_REVIEW_TASK_ID: lambda: lab._run_phase_2b_00_authorization_scope_gate_review(root),
        lab.PHASE_2B_00A_PLANNING_ONLY_OWNER_AUTHORIZATION_STATEMENT_TASK_ID: lambda: lab._run_phase_2b_00a_planning_only_owner_authorization_statement(root),
        lab.PHASE_2B_01_PLANNING_SCOPE_DESIGN_ONLY_TASK_ID: lambda: lab._run_phase_2b_01_planning_scope_design_only(root),
        lab.PHASE_2B_02_SAFETY_GATE_DESIGN_PLANNING_ONLY_TASK_ID: lambda: lab._run_phase_2b_02_safety_gate_design_planning_only(root),
        lab.PHASE_2B_04_SAFETY_ARTIFACT_CROSSWALK_GAP_REVIEW_TASK_ID: lambda: lab._run_phase_2b_04_safety_artifact_crosswalk_gap_review(root),
        lab.PHASE_2B_06_IMPLEMENTATION_ENTRY_GATE_AND_FIRST_SLICE_READINESS_REVIEW_TASK_ID: lambda: lab._run_phase_2b_06_implementation_entry_gate_and_first_slice_readiness_review(root),
        lab.PHASE_2B_07_FIRST_SLICE_DEFINITION_PACK_TASK_ID: lambda: lab._run_phase_2b_07_first_slice_definition_pack(root),
        lab.PHASE_2B_08_FIRST_SLICE_IMPLEMENTATION_AUTHORIZATION_GATE_TASK_ID: lambda: lab._run_phase_2b_08_first_slice_implementation_authorization_gate(root),
        lab.PHASE_2B_09_FIRST_SLICE_IMPLEMENTATION_PLAN_PACK_TASK_ID: lambda: lab._run_phase_2b_09_first_slice_implementation_plan_pack(root),
        lab.PHASE_2B_10_DAY1_DAY160_REFERENCE_MAPPING_TASK_ID: lambda: lab._run_phase_2b_10_day1_day160_reference_mapping(root),
        lab.PHASE_2B_11_PROJECT_CONSOLIDATION_ENTRY_MAP_TASK_ID: lambda: lab._run_phase_2b_11_project_consolidation_entry_map(root),
        lab.PHASE_2B_12_FUTURE_IMPLEMENTATION_AUTHORIZATION_REVIEW_TASK_ID: lambda: lab._run_phase_2b_12_future_implementation_authorization_review(root),
        lab.PHASE_2B_13_FIRST_SLICE_FINAL_SELECTION_GATE_TASK_ID: lambda: lab._run_phase_2b_13_first_slice_final_selection_gate(root),
        lab.PHASE_2B_14_FIRST_SLICE_IMPLEMENTATION_KICKOFF_GATE_TASK_ID: lambda: lab._run_phase_2b_14_first_slice_implementation_kickoff_gate(root),
        lab.PHASE_2C_01_LOCAL_STATIC_JOB_FIRST_SLICE_TASK_ID: lambda: lab._run_phase_2c_01_local_static_job_first_slice(root),
        lab.PHASE_2C_02_POST_FIRST_SLICE_ACCEPTANCE_REVIEW_TASK_ID: lambda: lab._run_phase_2c_02_post_first_slice_acceptance_review(root),
        lab.PHASE_2C_03_NEXT_SLICE_DECISION_GATE_AUTHORIZATION_REVIEW_TASK_ID: lambda: lab._run_phase_2c_03_next_slice_decision_gate_authorization_review(root),
        lab.PHASE_2C_04_NEXT_SLICE_CANDIDATE_INVENTORY_TASK_ID: lambda: lab._run_phase_2c_04_next_slice_candidate_inventory(root),
        lab.PHASE_2C_05_NEXT_SLICE_SAFETY_DELTA_REVIEW_TASK_ID: lambda: lab._run_phase_2c_05_next_slice_safety_delta_review(root),
        lab.PHASE_2C_06_NEXT_SLICE_FINAL_SELECTION_GATE_TASK_ID: lambda: lab._run_phase_2c_06_next_slice_final_selection_gate(root),
        lab.PHASE_2C_07_NEXT_SLICE_IMPLEMENTATION_KICKOFF_GATE_TASK_ID: lambda: lab._run_phase_2c_07_next_slice_implementation_kickoff_gate(root),
        lab.PHASE_2C_08_NEXT_SLICE_IMPLEMENTATION_TASK_ID: lambda: lab._run_phase_2c_08_next_slice_implementation(root),
        lab.PHASE_2C_09_POST_NEXT_SLICE_ACCEPTANCE_REVIEW_TASK_ID: lambda: lab._run_phase_2c_09_post_next_slice_acceptance_review(root),
        lab.PHASE_2C_10_NEXT_SLICE_DECISION_GATE_AUTHORIZATION_REVIEW_TASK_ID: lambda: lab._run_phase_2c_10_next_slice_decision_gate_authorization_review(root),
        lab.PHASE_2C_11_INTERVIEW_MVP_SCOPE_ARCHITECTURE_GATE_TASK_ID: lambda: lab._run_phase_2c_11_interview_mvp_scope_architecture_gate(root),
        lab.PHASE_2C_12_INTERVIEW_MVP_IMPLEMENTATION_SLICE_CANDIDATE_INVENTORY_TASK_ID: lambda: lab._run_phase_2c_12_interview_mvp_implementation_slice_candidate_inventory(root),
        lab.PHASE_2C_13_INTERVIEW_MVP_IMPLEMENTATION_SLICE_SAFETY_DELTA_REVIEW_TASK_ID: lambda: lab._run_phase_2c_13_interview_mvp_implementation_slice_safety_delta_review(root),
        lab.PHASE_2C_14_INTERVIEW_MVP_IMPLEMENTATION_SLICE_FINAL_SELECTION_GATE_TASK_ID: lambda: lab._run_phase_2c_14_interview_mvp_implementation_slice_final_selection_gate(root),
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
    if args.task and args.positional_task:
        parser.error("use either positional task or --task, not both")
    if args.positional_task:
        args.task = args.positional_task
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

