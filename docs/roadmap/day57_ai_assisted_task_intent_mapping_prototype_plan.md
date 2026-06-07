# Day57 - AI-assisted Task Intent Mapping Prototype Plan

## Goal

Day57 continues the conservative v0.3 planning line from Day56 by defining a safe text intent mapping layer.

The Day57 flow is:

```text
User text input
-> classify intent
-> map to an allowlisted runner task proposal
-> show safety level
-> require human confirmation where needed
-> produce prototype plan or dry-run mapping only
```

Day57 adds a deterministic local prototype so the shape of the future Voice + AI assistant can be reviewed without adding AI API calls, voice control, SSH, live runner execution, or device access.

## Non-Goals

Day57 does not:

- Connect to OpenAI, local LLMs, RAG, vector stores, or any external AI API.
- Implement speech recognition, audio capture, wake words, text-to-speech, or real voice control.
- Implement an autonomous AI Agent.
- Execute mapped runner tasks.
- Run live network tests, SSH, WireGuard validation, VRRP failover, iperf3, or device checks.
- Read or modify `config.json`.
- Add credentials or secrets.
- Modify NAT, IP, VRRP, WireGuard, firewall, route, interface, or device configuration.
- Create a release tag.
- Start v0.3 runtime implementation beyond this safe prototype mapping layer.

## Safety Boundaries

Day57 treats every natural-language request as a proposal, not a command.

Required boundaries:

- Unknown or ambiguous user text maps to manual review.
- Guarded-live candidate requests still produce dry-run mapping only.
- Human confirmation is recorded as required for future live-capable paths.
- Mapped tasks are never executed by the intent prototype.
- The prototype does not call `subprocess.run` for mapped actions.
- The prototype does not open SSH, connect to devices, or access lab credentials.
- The prototype is deterministic and based on static rules.

## Intent Mapping Flow

1. Normalize the input text.
2. Match it against deterministic prototype rules.
3. Select a reviewed intent label.
4. Map to a known runner task proposal or to manual review.
5. Attach a safety level.
6. Attach confirmation requirements.
7. Return `execution_mode: dry_run_only` and `mapped_task_executed: false`.

## Allowlisted Task Mapping Examples

| User input | Intent | Mapped runner task | Safety level | Confirmation | Day57 behavior |
| --- | --- | --- | --- | --- | --- |
| Show me the latest reports | `view_reports` | `report-index` | `report_only` | Not required or low-risk confirmation only | Dry-run mapping only |
| Run the WireGuard check | `wireguard_status_or_validation_request` | `wireguard-runner` | `guarded_dry_run` | Required before any future live-capable path | Dry-run mapping only |
| Do VRRP failover test | `vrrp_failover_test_request` | `day35-vrrp-failover-validation` as blocked/future guarded candidate | `guarded_live_candidate` | Mandatory | Blocked in Day57; dry-run mapping only |
| Open dashboard | `open_dashboard_or_report_view` | Dashboard / report viewer | `local_ui_only` | Not required | Dry-run mapping only |
| Make everything better | `unknown_or_ambiguous` | None | `needs_manual_review` | Manual review required | No task mapped; dry-run only |

## Human Confirmation Requirement

Human confirmation remains mandatory before any future live-capable path.

Day57 records confirmation policy only:

- Report-only or local UI requests may be marked as not requiring confirmation.
- WireGuard validation requests require confirmation before any future live-capable path.
- VRRP failover requests require mandatory confirmation and remain blocked in Day57.
- Unknown requests require manual review and do not map to a runner task.

## Dry-Run-Only Behavior

The Day57 CLI prototype is:

```powershell
python network_lab.py --task intent-mapping-prototype --intent-text "show me the latest reports"
```

It prints a structured mapping object with:

- Normalized user input.
- Detected intent.
- Mapped allowlisted task proposal.
- Safety level.
- Confirmation requirement.
- `execution_mode: dry_run_only`.
- `mapped_task_executed: false`.
- Blocked actions.

It never executes `report-index`, `wireguard-runner`, VRRP validation, SSH, iperf3, or any live network task.

## Static Prototype Artifact

The reviewer-facing prototype artifact is:

```text
docs/ai/day57_intent_mapping_prototype.md
```

It documents the reviewed mapping examples and the shape of the future intent object.

## Future Path Toward v0.3

Day57 prepares, but does not implement, the future v0.3 Voice + AI assistant direction.

Recommended future order:

1. Expand static intent taxonomy and safety labels.
2. Add fixture-based evidence explanation for existing local reports.
3. Add a reviewed intent object schema.
4. Add dashboard mock view for the reviewed intent object.
5. Add offline-only assistant demo using committed fixtures.
6. Propose allowlist integration while keeping execution disabled.
7. Review safety model again before any API, voice, or live-capable implementation.

Voice should remain a wrapper around reviewed text intent only after the text layer is stable.

## Validation Results

Commands planned for Day57 validation:

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-mapping-prototype --intent-text "Do VRRP failover test"
```

Observed Day57 results:

- `python -m pytest`: `492 passed, 1 warning in 2.54s`.
- `python network_lab.py --task report-index`: overall `WARN`, counts `total=12 pass=10 fail=0 warn=0 missing=2 unknown=0`.
- Missing optional generated local reports:
  - `reports/Hex-s-2025-lab02/day8_iperf3_performance_report.json`
  - `reports/lab-summary/day6_lab_topology_summary.json`
- `python network_lab.py --task intent-mapping-prototype --intent-text "Do VRRP failover test"`: returned `vrrp_failover_test_request`, mapped to `day35-vrrp-failover-validation (blocked in Day57)`, `execution_mode: dry_run_only`, `mapped_task_executed: false`.

The `report-index` WARN is acceptable for Day57 because `fail=0` and the missing items are optional generated local reports.

## Final Status

Day57 status: READY WITH NOTES.

Expected final safety confirmation:

- No OpenAI API.
- No voice control.
- No live network tests.
- No SSH.
- No device connections.
- No `config.json` changes.
- No NAT/IP/VRRP/WireGuard/firewall/interface/route/device configuration changes.
- No release tag.
- No v0.3 runtime implementation beyond the dry-run intent mapping prototype.
