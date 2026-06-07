# AI Intent Reviewer Acceptance Runbook

## Purpose

Day64 is a reviewer operation guide for accepting the AI Intent Reviewer documentation and static dashboard chain.

This runbook tells a reviewer how to inspect the Day57-Day63 artifacts, run the local validation commands, confirm the safety boundary, and record the acceptance result.

This is report-only/static documentation. It is not a runtime feature, not an AI integration, not a voice workflow, and not a live automation path.

## Acceptance Flow

### Step 1 - Review Dashboard Entry

Open the local dashboard route:

```text
/ai-intent-reviewer
```

Confirm the page explains the AI Intent Reviewer flow as a static reviewer entry point.

Expected reviewer evidence:

- The page returns HTTP 200 when the dashboard app is available.
- The page links to committed AI reviewer documents.
- The page states that no action is executed from the page.
- The page has no form, POST action, action endpoint, or task runner.

### Step 2 - Review Scenario Pack

Open:

```text
docs/ai/intent_reviewer_scenario_pack.md
```

Confirm the sample cases are reviewer examples only. They should explain report-only, dry-run, blocked, and clarification-required intent outcomes without adding new intent rules or execution behavior.

### Step 3 - Review Traceability Evidence Map

Open:

```text
docs/ai/intent_reviewer_traceability_evidence_map.md
```

Confirm the Day63 map connects each AI intent review concept back to the Day57-Day62 source evidence.

Expected reviewer evidence:

- Day57 intent mapping prototype is traceable.
- Day58 safety review gate is traceable.
- Day59 policy matrix is traceable.
- Day60 reviewer walkthrough is traceable.
- Day61 dashboard entry is traceable.
- Day62 scenario pack is traceable.

### Step 4 - Run Pytest

Run:

```powershell
python -m pytest
```

Expected result:

- Tests pass.
- `/ai-intent-reviewer` remains reachable when Flask is installed.
- Static dashboard safety assertions pass.

### Step 5 - Run Report-Index

Run:

```powershell
python network_lab.py --task report-index
```

Expected result:

- `fail=0`.
- WARN is acceptable only when optional local reports are missing.
- No live network validation is started.

### Step 6 - Run Intent-Workflow-Demo

Run:

```powershell
python network_lab.py --task intent-workflow-demo
```

Expected result:

- The command completes successfully.
- Output confirms no mapped task was executed.
- Generated evidence remains a local reviewer walkthrough only.

### Step 7 - Confirm No Execution Surface Exists

Inspect the dashboard page and related code for execution surfaces.

Acceptance checks:

- No OpenAI API is connected.
- No voice input is connected.
- No live execution is performed.
- No SSH is used.
- No device access is performed.
- No router, switch, firewall, VPN, or VRRP configuration is changed.
- No form is added.
- No POST action is added.
- No action endpoint is added.
- No task runner is added.
- No unsafe intent wording is presented as an executable operation.

### Step 8 - Record Acceptance Result

Record the reviewer outcome in the Day64 roadmap note or external review notes.

Acceptance result should include:

- Date and branch under review.
- Validation commands run.
- Any WARN-only report-index notes.
- Confirmation that the dashboard remained static/report-only.
- Confirmation that the expected result is reviewer acceptance evidence, not runtime execution.

## Safety Boundary

No OpenAI API is connected.
No voice input is connected.
No live execution is performed.
No SSH is used.
No device access is performed.
No router configuration is changed.
No switch configuration is changed.
No firewall configuration is changed.
No VPN configuration is changed.
No VRRP configuration is changed.
No form, POST action, action endpoint, or task runner is added.
No release tag is created.

Day64 passes when the reviewer can follow this runbook to inspect, validate, and record acceptance of the AI Intent Reviewer artifacts while preserving a documentation/static-dashboard/report-only boundary.
