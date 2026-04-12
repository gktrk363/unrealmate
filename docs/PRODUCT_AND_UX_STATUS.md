<!-- ═══════════════════════════════════════════════════════════════════ -->
<!-- UnrealMate - PRODUCT_AND_UX_STATUS -->
<!-- Author: G & E ZYNTH -->
<!-- © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers -->
<!-- ═══════════════════════════════════════════════════════════════════ -->

# Product and UX Status

## 1. Executive Product Read
- UnrealMate currently feels like a capable CLI product, not an equal-weight multi-client product.
- The default user experience is much more truthful than before: default help is quieter, local-only/experimental/mock surfaces are clearer, and stable risky commands keep stronger caution language.
- Version, root help, and post-command result surfaces were recently refreshed for a more premium, consistently styled terminal experience.
- The strongest user-facing value is still the stable CLI surface: `doctor`, `config`, `git`, `asset`, `performance`, `plugin`, `report html`, and `report json`.
- `report dashboard` is now more trustworthy operationally, but it still reads as an experimental CLI-launched secondary surface.
- `report notify` is clearly local-only and should not be sold as real remote notification delivery.
- UE editor plugin remains future/direction-only in this repo.

## 2. What Users Actually Experience Today

### CLI
- Users get a broad, practical CLI with real project utility and strong regression coverage.
- Help and discovery are more truthful now because default help follows registry visibility more closely and keeps weaker surfaces out of the default menu.
- Install, first-run, and project-entry guidance are clearer now, including a more explicit “run from project root or pass the project path” story.
- Broader discoverability now has an explicit opt-in path via `--help-all`, which keeps the default help surface stable-first while still making weaker surfaces reviewable on purpose.
- Warning/error wording is more consistent across several high-visibility commands.

### report html / report json
- These commands are reliable local export flows.
- They now read correctly as point-in-time local snapshots, not live editor or runtime state.
- For current product reality, this is a good fit for the CLI-first model.

### report dashboard
- The dashboard has a stronger lifecycle path than before: readiness, shutdown, no-browser mode, and port/runtime failure messaging are all more operationally useful.
- Even so, it still feels experimental because it is a long-running local web surface launched from the CLI, not a fully mature second client.

### plugin flows
- `plugin install`, `enable`, `disable`, and `remove` are more predictable now because they explain whether they touch `Plugins/`, `.uproject`, or both.
- They are still safety-sensitive local mutation commands, not low-risk convenience actions.

### build / config / git / asset
- These are the highest-value day-to-day CLI workflows today.
- Their safety language is more consistent than before, especially around overwrite, force, manual recovery, and partial/starter behavior.

## 3. UX Reality By Surface

| Surface | Current reality |
|---|---|
| CLI core | Strong and clearly primary. |
| Default help / discoverability | Better and more truthful, but still broad for first-time users. |
| report html / json | Reliable local export surface. |
| report dashboard | Real but experimental secondary surface. |
| report notify | Local-only utility, not a remote notification product. |
| plugin commands | Useful, stable, and still safety-sensitive. |
| build commands | Helpful starter generators, not production-grade automation. |
| editor plugin | Not product-real in this repo. |

## 4. UX Quality Assessment

| Area | Rating | Why |
|---|---|---|
| command discoverability | good but still broad | Registry-driven help now reduces false confidence, but the CLI surface is still large. |
| help surface truthfulness | good | Experimental/mock/opt-in surfaces are less likely to leak into default help, and labels are clearer. |
| warning/error clarity | good | High-visibility commands now use more consistent refusal, failure, and advisory wording. |
| destructive safety communication | good but safety-sensitive | Mutation risk is clearer, though many commands still rely on manual recovery rather than rollback. |
| report UX | good for CLI export | `html/json` are solid; dashboard remains a weaker secondary surface. |
| dashboard UX | acceptable but experimental | Much better operationally, still not equal to the CLI in trust. |
| Windows / legacy-terminal robustness | acceptable and improving | ASCII fallback is better on important paths, but not every rich surface is fully normalized. |
| onboarding | clearer but still CLI-heavy | README stays short, install/first-run/project-path guidance is better, and deeper understanding still depends on command help plus canonical docs. |

## 5. What Should Not Be Overstated
- Dashboard maturity should not be described as fully production-polished.
- `report notify` should not be described as remote notification delivery.
- Build generators should not be described as turnkey CI/CD automation.
- Advisory analysis commands should not be described as authoritative runtime truth.
- Editor plugin work should not be described as a current product surface.

## 6. Remaining Product / UX Gaps
- First-run command selection is better than before, but the breadth of the CLI still creates real onboarding load.
- Dashboard remains the weakest user-trust area among visible product surfaces.
- Stable destructive commands are much clearer now, but users still need to treat them as real local mutations.
- Legacy Windows terminal degradation is reduced, not eliminated.

## 7. Lean UI / UX Roadmap

### Wave 1 - First-run / Onboarding UX
- Focus on helping new users find the primary stable CLI surface faster.
- Prioritize clearer recommended/common flows, tighter first-run command selection, and less confusion from CLI breadth.
- This matters most because UnrealMate already has real CLI value, but first-time orientation still costs users time.

### Wave 2 - Dashboard / Secondary Surface UX
- Focus on making `report dashboard` feel more intentional as a CLI-launched secondary client.
- Prioritize clearer relationships between CLI-generated report artifacts and what the dashboard is showing.
- This matters because dashboard trust is improving, but it should stay positioned as an operational secondary surface, not a co-equal product client.

### Wave 3 - Product UX Polish
- Focus on broader consistency, visual cleanup, and lower-priority interaction polish only after release-hardening work is complete.
- Prioritize cross-command consistency and lower-value cleanup rather than new capability.
- This matters because the current product gap is trust and clarity, not missing feature breadth.

## 8. Recommended Work Mode
- Keep the product in release decision mode.
- Reopen engineering only for real blockers discovered in human review.
- If UI/UX work resumes after release, start with Wave 1 before broader polish.
- Do not reopen architecture or capability expansion work.

## 9. Verification Snapshot (2026-04-12)
- `python -m pytest -q` -> `347 passed, 11 skipped`
- `python -m pytest -q tests/smoke tests/registry` -> `56 passed, 1 skipped`
- `python scripts/sync_docs_from_registry.py --check` -> `Docs are already up to date.`
- `python scripts/generate_command_registry_artifact.py --check` -> `Command registry artifacts are already up to date.`
