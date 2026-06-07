# Day58 - Intent Mapping Safety Review / Confirmation Gate Design

## Scope

Day58 implements a dry-run/report-only safety review layer for the Day57 intent mapping prototype. The new `intent-safety-review` task classifies user intent, reports whether confirmation is required, blocks live-capable actions by default, and writes local JSON/HTML evidence.

Out of scope: OpenAI API integration, voice control, live execution, SSH, device access, `config.json` changes, network/device configuration changes, release tags, and Day9-Day15 behavior changes.

## Files Changed

- `network_lab.py`
- `tests/test_network_lab_runner.py`
- `docs/ai/day58_intent_mapping_safety_review_confirmation_gate.md`
- `docs/roadmap/day58_intent_mapping_safety_review_confirmation_gate.md`
- `README.md`

Generated local reports:

- `reports/portfolio/day58_intent_mapping_safety_review.json`
- `reports/portfolio/day58_intent_mapping_safety_review.html`

The `reports/` directory is ignored and generated reports are not intended to be committed unless project convention changes.

## Validation Commands

```powershell
python -m pytest
python network_lab.py --task report-index
python network_lab.py --task intent-safety-review --intent-text "show latest reports"
python network_lab.py --task intent-safety-review --intent-text "do VRRP failover test"
```

## Expected Result

- `python -m pytest` passes.
- `report-index` may return WARN when optional local generated reports are missing, with `fail=0`.
- `show latest reports` is classified as `report_only` and allowed.
- `do VRRP failover test` is classified as `blocked_live_capable` and blocked by default.
- Day58 writes a local dry-run safety report.
- No live execution occurs.

## Safety Confirmation

Day58 does not connect to OpenAI APIs, use voice control, execute mapped tasks, run live tests, use SSH, connect to routers/switches/firewalls/VPNs/devices, read or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration.

## Next-day Recommendation

Day59 should keep the same conservative boundary and focus on additional review-only artifacts, such as richer example coverage or a human-readable intent preview checklist. Do not add live execution, API integration, or voice control until the confirmation gate model has independent tests and explicit human approval requirements.
