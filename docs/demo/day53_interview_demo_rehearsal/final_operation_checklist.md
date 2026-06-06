# Day53 Final Operation Checklist

## Pre-rehearsal Gate

- [ ] Repository is on latest `main` before creating Day53 branch.
- [ ] Day52 is merged into `main`.
- [ ] Working tree is clean before Day53 documentation edits.
- [ ] Day53 branch is `day53-interview-demo-final-rehearsal-operation-checklist`.

## Safety Gate

- [ ] No live network dependency.
- [ ] No SSH.
- [ ] No router, switch, firewall, VPN, WireGuard peer, or lab device connection.
- [ ] No NAT, IP, VRRP, WireGuard, firewall, interface, route, or device configuration change.
- [ ] No `config.json` creation or modification.
- [ ] No release tag creation.
- [ ] No `v0.3` work.

## Local Validation

- [ ] `python -m pytest` reviewed.
- [ ] `python network_lab.py --task report-index` reviewed.
- [ ] `report-index` has `fail=0` if it returns `WARN`.
- [ ] Any missing reports are optional generated local reports.

## Demo Materials

- [ ] Demo opening script reviewed.
- [ ] 3-5 minute operation sequence reviewed.
- [ ] Common Q&A reviewed.
- [ ] Safety statement ready.
- [ ] Screenshots/package location known:

```text
docs/demo/day52_offline_demo_package/
```

## Dashboard Path

- [ ] Dashboard can be started locally if needed:

```powershell
python dashboard_app.py
```

- [ ] Dashboard home page reachable locally:

```text
http://127.0.0.1:5000/
```

- [ ] Reports page reachable locally:

```text
http://127.0.0.1:5000/reports
```

- [ ] Commands and safety page reachable locally:

```text
http://127.0.0.1:5000/commands
```

- [ ] AI checklist reachable locally:

```text
http://127.0.0.1:5000/ai-checklist
```

## Backup Plan

- [ ] If dashboard cannot open, use Day52 screenshots.
- [ ] If `report-index` returns `WARN`, explain optional missing local reports and confirm `fail=0`.
- [ ] If asked for live VRRP/WireGuard/device changes, explain that those require a separate guarded live lab plan.
- [ ] If asked about AI, explain that AI is future roadmap and must stay behind safety controls.

## Close-out

- [ ] Working tree checked after documentation edits.
- [ ] Validation results recorded in Day53 roadmap.
- [ ] Commit created with message:

```text
Document Day53 interview demo rehearsal checklist
```

- [ ] No push performed unless explicitly instructed.
