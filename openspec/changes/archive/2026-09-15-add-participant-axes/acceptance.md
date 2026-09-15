# Acceptance evidence — add-participant-axes

Change: `openspec/changes/add-participant-axes`
Tickets: GitHub #54 (parent spec #52, decision #48)
Date: 2026-09-14

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Owner adds a workspace member with both axes | `tests/integration/test_team.py::test_owner_adds_a_workspace_member_directly` | passing |
| Unknown function refused | same test (422 on `wizardry`) and `tests/unit/ideas/test_team_rules.py::test_an_unknown_function_is_refused` | passing |
| Non-owner cannot add | `test_team_rules.py::test_only_the_owner_adds_a_participant` | passing |
| The owner participation is never granted | `test_team_rules.py::test_the_owner_participation_cannot_be_granted` | passing |
| Member applies with a function | `test_team.py::test_join_handshake_full_loop` (applies with `engineering`, gets a contributor membership with that function) | passing |
| Legacy roles migrate onto the function axis | `test_team_rules.py::test_the_legacy_craft_roles_map_onto_the_function_axis` pins the mapping; the migration imports the same constant and `alembic check` reports no drift | passing (mapping pinned; see gap) |
| Both axes on the surface | `apps/web/tests/browser/team.spec.ts`, `timeline.spec.ts` and `initiative-type.spec.ts` run against the new payload shapes; FR/EN labels in `ideas.function.*` and `ideas.participation.*` | passing |
| Explorer filters on functions | `apps/web/tests/browser/explorer.spec.ts` (selects a function) and `tests/integration/test_explorer_list.py::test_list_filters_by_sought_role_and_realism` | passing |

Commands: `uv run pytest -m 'not live' -q` → 127 passed; `pnpm --dir apps/web exec playwright test` → 57 passed; `pnpm --dir apps/web test:ui` → 32 passed; `make verify` green.

## Boundaries and known gaps

- The migration's data mapping is pinned by a unit test on the shared constant and by `alembic check` for the schema, but no test executes the migration against rows holding legacy roles (the test database is migrated from scratch). Recorded as a gap.
- The `participation` granted on acceptance defaults to `contributor`; the owner can adjust through the add operation, which updates an existing membership. The accept endpoint accepts an optional participation but the UI does not offer it yet.
- Browser checks use simulated responses (UI only); authorization and persistence are proved by the PostgreSQL integration tests.
- CI runs Vitest but not Playwright: the browser checks are local evidence.
- The member-picker UI for direct addition is not in this slice: it needs a workspace-members endpoint. Tracked as a follow-up ticket.
- `ideas.sought_roles` keeps its column and API name while its values moved to the function axis (decision recorded in the design doc); renaming it would ripple through the contract for no pilot value.
