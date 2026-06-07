# Day59 - Intent Policy Matrix / Reviewer Safety Explanation

## Scope

Day59 adds a reviewer-facing policy matrix for the Day57 intent mapping prototype and Day58 safety review gate. It documents the allowed, blocked, and clarification-required decisions for common intent categories, then adds an optional `intent-policy-matrix` report-only runner task that writes local JSON/HTML evidence.

Out of scope: OpenAI API integration, voice control, live execution, SSH, device access, `config.json` dependency, network/device configuration changes, release tags, and v0.3 runtime implementation beyond the existing dry-run/report-only safety explanation behavior.

## Files Changed

- `network_lab.py`
- `tests/test_network_lab_runner.py`
- `docs/ai/day59_intent_policy_matrix_reviewer_safety_explanation.md`
- `docs/roadmap/day59_intent_policy_matrix_reviewer_safety_explanation.md`
- `README.md`

Generated local reports:

- `reports/portfolio/day59_intent_policy_matrix.json`
- `reports/portfolio/day59_intent_policy_matrix.html`

The `reports/` directory is ignored. Generated reports are local evidence and are not intended to be committed unless repository convention changes.

## Policy Decisions

- Report-only and documentation-only intents are allowed.
- Dry-run intent mapping is allowed only when the mapped task is not executed.
- Read-only safety explanation reports are allowed.
- Live-capable network tests are blocked by default.
- SSH and direct device access are blocked by default.
- Configuration changes are blocked by default.
- Unknown or ambiguous intent is blocked or requires clarification before any action.

## Runner Task

```powershell
python network_lab.py --task intent-policy-matrix
```

Expected behavior:

- Writes Day59 JSON and HTML reports.
- Includes blocked examples for VRRP failover, WireGuard live validation, SSH, configuration changes, and unknown intent.
- Includes allowed examples for dashboard/report viewing, task catalog review, report index generation, dry-run mapping, and safety review reports.
- Does not execute any mapped task.
- Does not call APIs, use voice, open SSH, connect to devices, or read `config.json`.

## Validation Commands

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-policy-matrix
```

## Expected Result

- `python -m pytest` passes.
- `report-index` may return WARN when optional generated local reports are missing, with `fail=0`.
- `intent-policy-matrix` returns PASS and writes local JSON/HTML reports.
- Day59 docs clearly explain the policy matrix and safety decisions.
- No live network behavior is introduced.

## Safety Confirmation

Day59 does not connect to OpenAI APIs, use voice control, execute mapped tasks, run live tests, use SSH, connect to routers/switches/firewalls/VPNs/devices, read or modify `config.json`, create release tags, or change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.
