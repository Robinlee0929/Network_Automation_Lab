# Public Reviewer Walkthrough

## Conclusion

Network Automation Lab is ready for a local Stage-0 portfolio review through
committed documentation, tests, screenshots, report evidence, and the canonical
Flask dashboard. The walkthrough is display- and report-oriented: it does not
require or authorize live devices, SSH, configuration changes, provider/model
calls, secrets, or command execution from the dashboard.

## One-Sentence Project Positioning

Network Automation Lab is a safety-first Python portfolio project that turns
MikroTik, Cisco, WireGuard, VRRP, and performance-validation work into
repeatable test logic, structured evidence, reports, and local reviewer
interfaces.

## What Problem This Project Solves

Network checks are often proved with ad hoc terminal sessions, screenshots, and
copied output. This project shows how those checks can instead be organized like
a QA platform:

- deterministic code and tests define expected behavior;
- reports use readable PASS, FAIL, WARN, and unavailable states;
- dashboard pages make bounded local evidence easier to review;
- dry-run, mock, report-only, historical, and gated capabilities remain
  distinguishable;
- public review can happen without contacting a lab device.

Historical records include workflows that had separate read-only or guarded
boundaries. Those records do not change the current Stage-0 public review path.

## Suggested Reading Order

1. `README.md`
2. `AGENTS.md`
3. `docs/portfolio/public_reviewer_walkthrough.md`
4. `docs/phase_2n/phase_2n_01_canonical_quick_start_and_demo_runbook_documentation_only.md`
5. `docs/phase_2n/phase_2n_05_final_user_facing_acceptance_review_phase_closure_review_only.md`
6. `docs/demo/offline_interview_demo_kit/README.md`

For a shorter review, read the release status and safety sections in
`README.md`, then follow the dashboard sequence below.

## Start the Canonical Local Dashboard

From the repository root, create and activate a Python environment, then install
the committed requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the canonical Flask dashboard:

```powershell
python dashboard_app.py
```

Open:

```text
http://127.0.0.1:5000/
```

Stop the server with `Ctrl+C` after the walkthrough.

If the local environment cannot start Flask, use only the current-suitable
screenshots identified under Offline Demo Materials:

```text
docs/demo/day52_offline_demo_package/screenshots/
```

The retained `dashboard_commands.png` is historical, superseded evidence of the
pre-display-only command UI. It is not a fallback for the current `/commands`
surface.

The Next.js application is a secondary Stage-0 evidence interface. It is not
required for this canonical walkthrough and does not displace the Flask entry
point.

## Dashboard Pages to Review

| Route | What to review | Current interaction boundary |
| --- | --- | --- |
| `/` | Project positioning, Stage-0 status, evidence health, proof points, and navigation | Local display surface |
| `/reports` | Evidence summaries, status filters, missing states, safe JSON previews, and bounded artifact links | GET-oriented evidence browsing |
| `/commands` | Registered command descriptions and historical execution records | **Display-only; no Run or POST control is rendered** |
| `/ai-checklist` | Static AI and safety checklist evidence | Display-only |
| `/ai-intent-reviewer` | Static intent examples, mock-runtime evidence, readiness gates, and safety boundaries | Display-only; no mapped-task execution |

The `/commands` page documents registry entries and historical records for
review. It does not expose a selectable execution workflow, does not grant
command authority, and must not be described or demonstrated as a live command
console.

The AI checklist and intent reviewer are also evidence surfaces. They do not
invoke a model, submit a provider request, create a job, execute a mapped task,
or contact a device.

## Recommended Walkthrough

1. Open `/` and explain that Flask is the canonical reviewer interface.
2. Identify the Stage-0 status and the distinction between evidence availability
   and validation quality.
3. Open `/reports` and review the summary counts and status filters.
4. Open one available safe JSON or HTML detail, if present.
5. Show an empty, missing, unavailable, or blocked state when local evidence is
   absent; do not trigger live collection to fill the gap.
6. Open `/commands` and explain that it is display-only and contains no Run
   or POST control.
7. Open `/ai-checklist` and `/ai-intent-reviewer` to show the explicit
   safety and no-execution boundary.
8. Optionally run the report-only index or repository tests.
9. Stop Flask with `Ctrl+C`.

## Validate the Local Evidence

Run the Python regression suite when a full local code check is appropriate:

```powershell
python -m pytest
```

Run the report index as a local report-only evidence scan:

```powershell
python network_lab.py --task report-index
```

`report-index` reads local metadata and evidence paths. It does not connect
to routers, switches, VPN peers, SSH, WireGuard, VRRP, or iperf3 endpoints.

It may return `WARN` when optional generated reports are missing from
`reports/`. That is acceptable only when:

- `fail=0`;
- every missing item is optional generated evidence;
- the output still provides a usable evidence inventory.

A required-evidence failure or any non-zero failure count is not an acceptable
optional-artifact warning.

## How to Interpret Reports

Reports are evidence artifacts, not unbounded terminal dumps.

| Status | Meaning |
| --- | --- |
| `PASS` | The checked condition passed |
| `FAIL` | A required condition failed or required evidence is invalid |
| `WARN` | A non-blocking issue or documented optional-evidence gap |
| `MISSING` | An expected local generated artifact is absent |
| `UNKNOWN` | Evidence exists but exposes no supported result field |
| `UNAVAILABLE` | The evidence source or bounded projection cannot be used |
| `ERROR` | Evidence could not be processed safely |
| `BLOCKED` | A safety or authorization gate prevented the action |

Start with the overall result, then review failures and warnings. Inspect
expected/actual detail only when deeper troubleshooting is needed. Availability
alone is not a PASS.

## Offline Demo Materials

Start with:

```text
docs/demo/offline_interview_demo_kit/README.md
```

Supporting files include:

```text
docs/demo/offline_interview_demo_kit/demo_checklist.md
docs/demo/offline_interview_demo_kit/demo_commands.md
docs/demo/offline_interview_demo_kit/interview_talk_track_3_to_5_min.md
docs/demo/offline_interview_demo_kit/no_live_dependency_statement.md
docs/demo/offline_interview_demo_kit/troubleshooting_guide.md
```

The directory name is historical and remains unchanged so existing evidence
references continue to work.

Current-suitable fallback screenshot order:

1. `dashboard_home.png`
2. `dashboard_reports.png`
3. `dashboard_ai_checklist.png`

`dashboard_commands.png` remains in the package for historical traceability.
It shows the superseded pre-display-only interface and is not current or
recommended `/commands` evidence.

## What Can Be Reviewed Without Live Lab Access

A reviewer can inspect:

- Python and TypeScript source organization;
- unit, regression, safety, and presentation tests;
- architecture, safety, Phase, and roadmap documents;
- dashboard structure and the current-suitable committed screenshots identified
  above;
- report-index behavior and report interpretation;
- committed summaries and any available local report evidence;
- dry-run and mock reviewer-evidence chains.

No router, switch, VPN, VRRP, WireGuard, SSH, NETCONF, RESTCONF, iperf3,
firewall, provider/model service, secret, or private lab configuration is
required for this path.

## Safety Boundaries

The August release remains Stage 0. For this public review:

- do not run live network tests;
- do not use SSH, NETCONF, or RESTCONF;
- do not connect to or configure a device;
- do not change router, switch, firewall, VPN, WireGuard, VRRP, NAT, IP,
  interface, or route state;
- do not run a live iperf3 scenario;
- do not use provider/API/model calls or secrets;
- do not treat display metadata as execution authorization;
- do not submit or simulate unavailable dashboard action controls.

Use committed documentation, tests, the current-suitable screenshots identified
above, summaries, and local report-only/dashboard views. Any future read-only
or live integration requires a separate Stage gate and task-specific user
approval.
