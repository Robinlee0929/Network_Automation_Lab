# Day42 - v0.2 Release Tag Preparation

## Purpose

Confirm `main` readiness and create the annotated `v0.2` release tag for the demo-ready Network Automation Platform package.

Day42 is release validation and tag creation only.

## Pre-check Summary

- Branch requirement: `main`.
- Working tree requirement: clean before Day42 edits.
- Remote requirement: `main` up to date with `origin/main`.
- Day41 merge requirement: confirm `eb38e85` is present in recent `main` history.
- Existing tag requirement: confirm `v0.2` does not already exist before creating it.

Recorded pre-check commands:

```powershell
git status --short --branch
git switch main
git pull origin main
git log --oneline --decorate -10
git tag --list
```

Initial Day42 pre-check result:

- `main` was checked out.
- `origin/main` was already up to date.
- Day41 merge commit `eb38e85` was present as the latest `main` commit before Day42 documentation.
- Existing tags listed `v0.1`; `v0.2` was not present before Day42 tag creation.

## Day41 Release Material Verification

Day41 release materials were verified before creating the Day42 documentation:

| Material | Path | Verification |
| --- | --- | --- |
| Release package | `docs/releases/v0.2_release_package.md` | Present and referenced from `README.md` and `network_lab.py`. |
| Artifact checklist | `docs/releases/v0.2_artifact_checklist.md` | Present and referenced from `README.md` and `network_lab.py`. |
| Demo handoff guide | `docs/portfolio/v0.2_demo_handoff_guide.md` | Present and referenced from `README.md` and `network_lab.py`. |

The Day41 package confirms that the v0.2 release is a reviewer-ready HA / VRRP evidence and demo package, while Day42 owns final tag preparation.

## Test Command and Result Placeholder

Required validation command before creating the tag:

```powershell
python -m pytest
```

Result placeholder:

```text
486 passed, 1 existing getpass echo warning in 3.30s.
```

If tests fail, do not create or push the `v0.2` tag.

The existing getpass echo warning is acceptable only if tests pass and the warning already existed.

## Tag Creation Command

Create the annotated tag only after Day42 documentation is committed and pushed to `main`, and after tests pass:

```powershell
git tag -a v0.2 -m "Release v0.2 - Network Automation Platform demo-ready package"
```

Verification command:

```powershell
git show v0.2 --stat
```

## Tag Push Command

Push the tag only after verifying the annotated tag locally:

```powershell
git push origin v0.2
```

Post-push verification commands:

```powershell
git tag --list
git status --short --branch
git log --oneline --decorate -5
```

## Safety Statement

Day42 performs no live test, no SSH, and no MikroTik, Cisco, firewall, NAT, IP, VRRP, or interface changes.

Day42 does not connect to routers, switches, firewalls, WireGuard peers, iperf3 endpoints, or lab devices. It does not run VRRP failover, WireGuard live execution, iperf3 live performance testing, or any real device configuration change.

## Completion Checklist

- [x] Confirmed clean `main` before Day42 documentation edits.
- [x] Confirmed `main` was up to date with `origin/main`.
- [x] Confirmed Day41 merge commit `eb38e85` exists in recent history.
- [x] Confirmed `v0.2` did not already exist before tag creation.
- [x] Verified Day41 release package materials.
- [x] Ran `python -m pytest`.
- [ ] Committed Day42 documentation updates.
- [ ] Pushed Day42 documentation commit to `main`.
- [ ] Created annotated `v0.2` tag.
- [ ] Verified `v0.2` with `git show v0.2 --stat`.
- [ ] Pushed `v0.2` tag to origin.
