# Acceptance evidence — add-initiative-framing

Change: `openspec/changes/add-initiative-framing`
Tickets: GitHub #56 (parent spec #52)
Date: 2026-09-14
Delivered by this change: the backend field, the owner-only update and the B2B copy switch.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Deposit chooses a kind | `tests/integration/test_initiative_type.py::test_deposit_stores_the_chosen_type_and_exposes_it` (response, read and list) | passing |
| Deposit omits the kind | `::test_deposit_defaults_to_the_idea_type` | passing |
| Unknown kind refused | `::test_deposit_refuses_an_unknown_type` (422) | passing |
| Owner re-classifies | `::test_owner_changes_the_type` (also proves an unknown kind on update is refused) | passing |
| Non-owner refused | `::test_only_the_owner_changes_the_type` (member 403) | passing |
| Non-member gets nothing | `::test_only_the_owner_changes_the_type` (outsider 404) | passing |
| Existing initiatives keep working | the column is `NOT NULL DEFAULT 'idea'` in the migration, so pre-existing rows read as `idea` without a data backfill; the integration seed creates a row through the ORM (model default) and `test_member_browses_only_their_workspace_ideas` asserts the kind in the response. The DDL `server_default` itself is not exercised by a test (gap, low risk: the migration is the only writer of pre-existing rows) | passing |
| French workspace copy | `apps/web/tests/browser/initiative-type.spec.ts` (FR) and, for the whole surface, `apps/web/tests/ui/initiative-copy.spec.ts` asserting zero forbidden words across `ideas.*`, `workspace.*` and the navigation values | passing |
| English workspace copy | the same Vitest spec in EN | passing |
| Closed list (unit) | `tests/unit/ideas/test_initiative_type_rules.py`: the ten kinds, known accepted, unknown and blank refused, **plus drift tests** asserting the Pydantic literal, the adapter check constraint and the migration all equal the domain constant | passing |

Targeted commands: `uv run pytest tests/unit/ideas tests/integration/test_initiative_type.py -q` → 12 passed; `pnpm --dir apps/web exec playwright test tests/browser/initiative-type.spec.ts` → 6 passed; `pnpm --dir apps/web test:ui` → 32 passed.

## Boundary evidence

- Migration `7b1f0c2e9a55` applied and reverted cleanly; `alembic check` reports no drift.
- Contract regenerated: `update_idea` added, `initiative_type` added to the deposit request and to the idea responses. No operation removed.
- Strict Mypy covers the new domain module (`apps/api/src/modules/ideas/domain` was already listed).

## Review findings applied

A two-axis review ran before the pull request and its findings were applied:

- The closed list existed in four unlinked copies while `design.md` claimed a mismatch would fail a test: the drift tests now enforce the domain constant, the Pydantic literal, the adapter constraint and the migration as one list, and the domain validator is called by the service (it was dead code).
- The deposit BFF silently coerced an unknown kind to the default while the ticket requires refusal: a shared `server/utils/initiative.ts` guard now refuses it with 422, and both BFF handlers use the one list.
- A failed type change rendered an unrelated iterations message and never reset: the detail screen has its own error flag and message next to the selector.
- The derived `typeOptions` was duplicated on two pages (now one composable), `canManageIterations` duplicated `isOwner`, and the update route re-fetched after commit with an `assert` (now returns the service result, like the deposit route).

## Boundaries and known gaps

- Browser checks use simulated responses: they prove the UI (selector presence, request payload, read-only view), not authorization or persistence. Those are proved by the PostgreSQL integration tests.
- CI runs Vitest but not Playwright, so the six browser checks are local evidence.
- The kind is not yet used for filtering, ranking or analysis prompting; those belong to later slices (#58 analysis context, #61 explanation surface).
- Imported legacy content keeps its original wording; only the product's own labels changed.
