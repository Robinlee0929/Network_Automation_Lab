# Day46 - v0.2.1 Release Candidate Decision and Post-Fix Release Strategy

## Purpose

Decide whether the project should create a `v0.2.1` tag after the Day44 hermetic test fix and the Day45 post-fix fresh checkout verification.

Day46 is a release decision record only. It documents the recommended version strategy before any new release tag is created, so the project does not mix patch verification work with feature-release versioning.

## Background

The `v0.2` tag already exists at commit:

```text
f4fd4d5a33d6847d40baac87ae4ed285e56dea6a
```

Day43 verified the `v0.2` tag as a portfolio demo baseline and found one pytest failure from a fresh checkout:

```text
tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode
```

The root cause was a non-hermetic test dependency. The test could pass in a developer working tree when ignored local `config.json` supplied router host and username values, but it failed from a fresh checkout where `config.json` is intentionally absent.

Day44 fixed the hidden config dependency in `tests/test_day12_wireguard_vpn_automation.py` by making the Day12 test path self-contained with explicit fake non-live values and by guarding against unexpected write commands.

Day44 validation:

```powershell
python -m pytest tests/test_day12_wireguard_vpn_automation.py -q
python -m pytest
```

Result:

```text
50 passed
487 passed, 1 warning
```

Day45 completed post-Day44 fresh checkout verification and was merged to `main`. The latest `main` after the Day45 merge is:

```text
49cf68f
```

Day44 and Day45 are patch/release-verification work. They do not add a new feature scope.

## Options Considered

### Do Not Create v0.2.1 Now

This option keeps current `main` as the portfolio demo baseline and defers the patch tag unless a formal corrected release artifact is required.

This is the recommended option because Day44 fixed the hermetic test issue and Day45 verified the corrected state from a fresh checkout. A new tag is useful only if the project needs to formally publish a fresh-checkout-corrected replacement for the `v0.2` verification result.

### Create v0.2.1

This option creates a corrected patch release tag after Day44 and Day45.

This is conditional. It is useful if the release process requires an immutable tag that explicitly says the `v0.2` fresh-checkout issue has been corrected. It is not required for normal portfolio demo use because `main` is already suitable as the corrected baseline.

### Move Directly to v0.3

This option skips a patch tag and treats the post-Day44 state as the next minor release.

This is not recommended. Day44 and Day45 fixed and verified a test hermeticity issue. They are patch-level release quality work, not feature-level scope that would justify `v0.3`.

## Decision Table

| Option | Recommendation | Reason |
| --- | --- | --- |
| Do not create `v0.2.1` now | Recommended | `main` is already usable for demo; avoids unnecessary patch release unless a formal release is required |
| Create `v0.2.1` | Conditional | Useful if a clean fresh-checkout patch tag is needed |
| Move directly to `v0.3` | Not recommended | Day44 and Day45 are patch fixes, not new feature scope |

## Recommendation

Day46 decision: Defer `v0.2.1` tag creation.

Keep current `main` as the portfolio demo baseline. Create `v0.2.1` later only if the project needs a formal corrected patch release that clearly communicates the fresh-checkout Day12 issue found after `v0.2` has been fixed.

Do not move directly to `v0.3` from this work. Day44 and Day45 improve release correctness and verification confidence, but they do not introduce a new feature milestone.

## Risk Analysis

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Creating `v0.2.1` immediately may imply a formal release process that has not been explicitly planned | Version history becomes noisy or confusing | Document the decision first and create the tag only when a formal corrected patch release is required |
| Not creating `v0.2.1` may leave `v0.2` with a known fresh-checkout test failure | Reviewers may need context if they inspect the old tag directly | Use current `main` as the demo baseline and point to Day43-Day46 notes for the release verification chain |
| Moving to `v0.3` after patch-only work may overstate the project scope | Minor-version meaning becomes unclear | Reserve `v0.3` for a future feature-level milestone |
| Relying on local ignored config files can hide future hermeticity problems | Fresh checkout confidence can drift | Keep non-live tests self-contained and verify important release candidates from clean checkouts |

## Version Strategy

- `v0.2` remains the existing HA / VRRP demo-ready release tag at `f4fd4d5`.
- Current `main` after Day45 is the corrected portfolio demo baseline.
- `v0.2.1` should be created only if a formal patch release is needed to publish a clean fresh-checkout-corrected tag.
- `v0.3` should wait for a feature-level milestone, not a patch verification chain.
- Release notes should distinguish immutable historical tags from the current corrected branch state.

## Safety Statement

Day46 is documentation-only release strategy work.

Day46 does not create a tag, create a GitHub release, run live network tests, use SSH, connect to routers, switches, firewalls, VPN devices, WireGuard peers, or iperf3 endpoints, create or modify `config.json`, or change NAT, IP, VRRP, WireGuard, firewall, route, interface, or device configuration.

## Validation Command and Results

Day46 validation command:

```powershell
python -m pytest
```

Result:

```text
487 passed, 1 warning
```

The warning is the existing non-live `getpass` terminal echo warning observed in recent full-suite verification. It does not indicate a live device connection or a failed test.

## Next Step Recommendation for Day47

Day47 should start the next clearly scoped work item without changing release tags by default.

Recommended Day47 direction: define the next feature-level `v0.3` candidate scope separately from the Day44-Day46 patch/release-verification chain. If a formal corrected patch release becomes necessary, create a dedicated `v0.2.1` release-preparation task with explicit tag and release-note steps.

## Final Conclusion

Day46 decision: Defer `v0.2.1` tag creation.

Current `main` is suitable as the portfolio demo baseline. `v0.2.1` should be created only if the project needs to formally announce that the `v0.2` fresh-checkout test issue has been corrected. Day44 and Day45 are patch-level fixes and verification work, so they do not justify moving directly to `v0.3`.
