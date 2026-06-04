# Day29 v0.1 Release Tag Preparation

This document records the Day29 v0.1 release tag preparation result for Network Automation Lab. It is documentation-only evidence for preparing the repository to be tagged or shared as the v0.1 portfolio release.

Day29 confirms that the Day28 portfolio evidence package has a clear final review path, explicit safety posture, and a repeatable validation command before creating a Git release tag.

## Preparation Scope

- Confirm README scope describes the v0.1 package through Day29 tag preparation.
- Confirm release notes and portfolio checklist point reviewers to the final validation command.
- Keep generated `reports/`, `exports/`, caches, real configs, credentials, passwords, private keys, WireGuard `.conf` files, and environment-specific files out of committed evidence.
- Keep Day29 documentation-only, without adding runner behavior, dashboard behavior, live VPN behavior, SSH execution behavior, generated reports, or release package artifacts.
- Record the intended tag target as the clean repository state after Day29 documentation and validation are complete.

## Recommended Tag Checklist

Before creating the v0.1 tag:

1. Run the full local regression suite.
2. Confirm `git status --short` contains only intentional Day29 documentation changes, then is clean after commit.
3. Review `docs/portfolio_evidence/v0.1_release_notes.md`.
4. Review `docs/portfolio_evidence/v0.1_portfolio_checklist.md`.
5. Create the release tag only after the Day29 documentation commit is complete.

Recommended tag commands after committing Day29:

```powershell
git tag -a v0.1 -m "Network Automation Lab v0.1"
git push origin v0.1
```

Do not tag local generated evidence, real configs, exports, caches, or secrets.

## Safety Result

Day29 does not connect to routers, switches, WireGuard clients, or iperf3 endpoints. It does not execute live validation, start VPN clients, apply router configuration, reset or reboot devices, read local secrets, or generate report artifacts.

## Validation

Recorded validation command:

```powershell
python -m pytest --basetemp=.pytest-tmp-day29-tag
```

Local execution used the Codex bundled Python runtime because the system `python` and `py` launchers were not available in this shell.

Recorded result:

```text
401 passed in 2.03s
```

## Tag Readiness Verdict

The v0.1 release tag is ready to create after the Day29 documentation commit is complete.
