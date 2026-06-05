# v0.2 Portfolio Demo Checklist

This checklist prepares the Day40 v0.2 HA / VRRP portfolio demo. It is documentation and report-only guidance. It does not require SSH, live tests, or device configuration changes.

## Pre-Demo Checks

- Confirm the working branch contains Day40 documentation and runner metadata.
- Generate the Day40 report with the report-only demo navigation command: `python network_lab.py --task day40-v0.2-demo-readiness-review`.
- Generate the report index with the report-only demo navigation command: `python network_lab.py --task report-index`.
- Confirm no real credentials, `.conf` files, exported configs, or local `config.json` content are part of the demo.
- Confirm generated `reports/` output is treated as local evidence unless intentionally exported for screenshots.

## Dashboard Walkthrough Checks

- Start the dashboard only for local evidence browsing.
- Open `/reports`.
- Confirm HA / VRRP evidence cards are visible.
- Confirm missing generated reports are shown as missing or not generated instead of crashing.
- Confirm JSON preview remains redacted and readable.
- Confirm no dashboard action is used to run live tests, SSH, failover, iperf3, reboot, reset, or configuration changes.

## Report Index Checks

- Open `reports/report_index.html`.
- Confirm Day39 and Day40 rows appear after their reports are generated.
- Confirm Day40 is labeled as report-only demo readiness.
- Confirm missing optional reports remain visible as missing rather than hidden.
- Confirm report links point to local evidence paths.

## Latest Lab Overview Checks

- Confirm the latest overview can surface HA / VRRP evidence metadata.
- Confirm Day40 docs and generated reports are discoverable through the shared evidence catalog.
- Confirm overview generation remains local and report-only.

## VRRP Evidence Traceability Checks

- Day31 topology plan is available.
- Day31 safety model is available.
- Day32 read-only precheck path is explained.
- Day33 dry-run command preview path is explained.
- Day34 staged apply safety gate path is explained.
- Day35 controlled failover observation path is explained.
- Day36 report hardening note is available.
- Day37 regression and evidence policy note is available.
- Day38 v0.2 scope planning note is available.
- Day39 dashboard integration report is available or clearly marked not generated.
- Day40 demo readiness report is available.

## Safety Explanation Checks

- Explain that Day40 does not run live tests.
- Explain that Day40 does not use SSH.
- Explain that Day40 does not change MikroTik, Cisco, firewall, NAT, IP, VRRP, or interface settings.
- Explain the difference between report-only, read-only, dry-run, guarded-live, and controlled failover observation.
- Explain that the v0.2 demo can be presented from local evidence without touching live device configuration.

## Portfolio Explanation Points

- The project turns network validation into repeatable JSON and HTML evidence.
- v0.1 established the runner, dashboard, report index, WireGuard safety, and portfolio evidence story.
- v0.2 extends the story into HA / VRRP with explicit safety boundaries.
- Day31-Day39 form a traceable HA / VRRP milestone from planning through dashboard visibility.
- Day40 locks the demo scope before release packaging so the demo stays safe and focused.

## Known Limitations

- Day35 failover evidence depends on a manual external physical trigger.
- Fresh clones may not have every generated `reports/` artifact until the relevant report-only or guarded workflow is run.
- The v0.2 demo is not a production NMS or a claim of continuous HA monitoring.
- CLI tab completion, command tree improvements, and AI report assistant are future work.

## Out-of-Scope Items

- New live VRRP tests.
- New SSH operations.
- New MikroTik, Cisco, firewall, NAT, IP, VRRP, or interface configuration commands.
- Automated failure injection.
- Router reboot, reset, disable, enable, add, set, or remove operations.
- New live WireGuard or iperf3 runs.
- Changes to Day31-Day39 evidence semantics.

## Final Go / No-Go Criteria

Go if:

- Day40 JSON and HTML reports generate successfully.
- Day40 safety flags say `live_test: false`, `ssh_used: false`, and `device_config_changed: false`.
- Dashboard and report index paths can be shown from local evidence.
- The presenter can explain included and excluded v0.2 scope clearly.

No-go if:

- Any demo step requires SSH or live lab reachability.
- Any demo step changes device configuration.
- Day40 report generation fails.
- The safety boundary cannot be explained without ambiguity.
