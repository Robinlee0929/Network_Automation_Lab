# Day37 - VRRP Report Regression and Evidence Snapshot Policy

## Purpose

Day37 protects the Day35 and Day36 VRRP evidence chain without creating new live lab evidence.

- Day35 validated live VRRP failover behavior with a manual external lab01 LAN disconnect and reconnect.
- Day36 hardened the Day35 evidence summary, report rendering, report-index visibility, and portfolio traceability.
- Day37 adds offline regression guards and defines when evidence snapshots may be committed.

Day37 does not perform live VRRP testing, does not run failover, does not unplug cables, does not connect to MikroTik routers for new validation, and does not change MikroTik configuration.

## Runtime Report Policy

Runtime reports under `reports/` are normally not committed. They are generated local evidence, can contain lab-specific paths or raw device output, and may become noisy when regenerated.

Full live evidence reports should stay local unless a reviewer intentionally selects a small sanitized snapshot for a milestone. The default source-control representation for Day35 and Day36 is documentation plus offline regression fixtures, not full runtime report dumps.

A snapshot may be committed only when it is:

- Small enough to review without hiding code or documentation changes.
- Sanitized of local secrets, credentials, device passwords, private keys, exported WireGuard configs, and raw sensitive outputs.
- Reviewer-useful because it demonstrates a specific schema, summary format, or milestone result.
- Tied to a clear milestone, release note, test fixture, or documentation path.

Secrets, private keys, credentials, device passwords, exported WireGuard configs, raw RouterOS outputs with sensitive values, local config files, backups, and environment-specific private data must never be committed.

## Commit Guidance

| Category | Examples | Policy |
| --- | --- | --- |
| Do not commit | Full `reports/` dumps, raw live evidence exports, local configs, backups, WireGuard `.conf` files, secrets, private keys, device passwords, raw sensitive outputs | Keep local and ignored. Redact or summarize before sharing. |
| May commit as sanitized snapshot | Small milestone JSON/HTML excerpt, sanitized report sample, compact reviewer screenshot, schema-focused evidence slice | Commit only when intentionally selected, sanitized, small, and linked to a milestone or review purpose. |
| Should commit as documentation or sample fixture | Roadmap notes, README updates, portfolio evidence notes, unit-test fixtures, schema regression samples | Prefer these for durable portfolio evidence and regression protection. |

## Day35-Day37 Reviewer Note

Day35 produced live VRRP failover evidence. Day36 improved how that evidence is summarized and indexed. Day37 intentionally avoids creating another live validation run and instead protects the report/index contract with offline regression tests.

For review, Day35 and Day36 evidence is represented in source control by documentation and regression fixtures rather than full runtime report dumps. This keeps the repository clean, avoids committing lab-specific raw output, and still preserves the important reviewer contract: the Day35 summary must continue to expose overall status, device role/status summaries, evidence metadata, and failover/recovery result fields.

## Day37 Boundaries

- No new live VRRP validation evidence is created.
- No MikroTik device settings are modified.
- No failover is triggered.
- No cables are unplugged.
- No live SSH operations are added.
- No generated `reports/` tree is committed.
- Regression tests use fixture/sample JSON and temporary pytest files only.
