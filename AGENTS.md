# UnrealMate Agent Guide

## Repo Purpose
- UnrealMate is a CLI-first toolkit for Unreal Engine workflows.
- The stable/default CLI surface is the real primary product.
- The repository is in release-hardening / merge-readiness mode.
- `report dashboard` is real, but still experimental and secondary to the CLI.
- `report notify` is local-only. It is not remote delivery.
- UE editor plugin work is direction-only in this repo, not a shipped product surface.

## Product Positioning Rules
- Treat the stable/default CLI surface as the center of the product.
- Do not introduce new product surfaces.
- Do not expand scope into SaaS, desktop app, or editor plugin productization.
- Do not turn `report dashboard` into the center of the product story.
- Do not imply that build generators are production-grade CI/CD automation.
- Do not imply that advisory analysis commands are authoritative runtime truth.

## Canonical Truth Docs And Precedence
Use these in order when deciding what is true:

1. `docs/PROJECT_STATUS.md`
   Status source-of-truth for current repo state, work mode, and remaining risks.
2. `docs/PRODUCT_AND_UX_STATUS.md`
   Product and UX reality snapshot.
3. `docs/COMMAND_SURFACES.md`
   Generated support truth from registry metadata and smoke coverage. Do not hand-edit.
4. `README.md`
   Short top-level entry only. Keep it brief and aligned with the canonical docs above.

If docs and code drift, prefer current code behavior plus test evidence, then update the canonical docs narrowly.

## Language Rules
### Stable
- Stable means default-visible and test-backed.
- Stable does not mean risk-free, production-perfect, or automatically reversible.
- Keep caution language for commands that write or delete local state.

### Experimental
- Say experimental plainly.
- Do not position experimental surfaces as core product value.
- `report dashboard` should stay explicitly experimental.

### Mock / Placeholder
- Say mock, simulated, or placeholder plainly.
- Do not let mock surfaces sound product-real.
- Keep them out of default product framing unless explicitly needed for truth.

### Local-only
- Say local-only plainly.
- Do not imply network, webhook, cloud, or remote delivery if it does not exist.
- `report notify` must remain clearly local-only.

## Preferred Work Style
- Prefer narrow, reviewable PRs.
- Prefer blocker-level hardening, truthfulness, and regression coverage over broad cleanup.
- Prefer small targeted edits over architecture campaigns or broad refactors.
- Keep the CLI-first product direction intact.
- Preserve existing tests and extend them narrowly when behavior changes.

## Verification Commands
Run the smallest relevant set for the files you touch. The common release-hardening baseline is:

```powershell
python -m pytest -q
python -m pytest -q tests/smoke tests/registry
python scripts/sync_docs_from_registry.py --check
python scripts/generate_command_registry_artifact.py --check
python -m ruff check unrealmate tests
```

Notes:
- `docs/COMMAND_SURFACES.md` must stay generated. Regenerate it only through the existing script path.
- `ruff format --check` and `mypy` are currently advisory, not release gates. Do not start broad cleanup campaigns just to satisfy them unless explicitly asked.

## PR Expectations
- Keep PRs narrow, scoped, and easy to review.
- Include focused regression tests for the behavior you change.
- Preserve truthful user-facing wording.
- Call out any remaining risks or intentional deferrals explicitly.
- Do not mix broad cleanup with a narrow hardening change.
- If generated artifacts or generated docs change, regenerate them through the project scripts and mention that clearly.

## Done Means
A change is done when:

- It stays within current product scope.
- The stable/default CLI surface remains the priority.
- User-facing wording is truthful about stable, experimental, mock, local-only, advisory, or starter-template behavior.
- Touched behavior has focused verification.
- Relevant commands/tests pass.
- Generated truth remains in sync.
- The result is merge-ready without needing a broad follow-up cleanup.

## Explicit Do-Not Rules
- Do not introduce new product surfaces.
- Do not start a broad `cli.py` breakup.
- Do not start architecture campaigns.
- Do not start typed-details migration.
- Do not expand docs into new roadmap/spec/tutorial categories.
- Do not broaden scope into SaaS, desktop app, or editor plugin productization.
- Do not oversell `report dashboard`, `report notify`, build generators, or advisory analysis surfaces.
- Do not hand-edit `docs/COMMAND_SURFACES.md`.
- Do not trade truthfulness for polish.
