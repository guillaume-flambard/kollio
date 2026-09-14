# Acceptance evidence — add-company-context

Change: `openspec/changes/add-company-context`
Tickets: GitHub #53 (backend slice of #52)
Date: 2026-09-14
Delivered by this change: the backend capability only.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads the context | `tests/integration/test_company_context.py::test_member_reads_empty_context`, `::test_profile_round_trip_and_upsert` | passing |
| Non-member requests the context | `::test_non_member_is_refused_everywhere` (404, localized FR) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| Profile created then read back | `::test_profile_round_trip_and_upsert` | passing |
| Profile updated in place (single row) | `::test_profile_round_trip_and_upsert` (second PUT replaces; omitted fields become empty) | passing |
| Profile untouched on read | `::test_member_reads_empty_context` (empty profile, no error) | passing |
| Objective created (active, non-priority) | `::test_objective_lifecycle` | passing |
| Objective lifecycle edited | `::test_objective_lifecycle` | passing |
| Unknown objective state refused | `::test_objective_lifecycle` (422 on `paused`) | passing |
| Explicit null refused instead of failing late | `::test_update_refuses_explicit_nulls` (422, not a 500 on flush) | passing |
| Constraint created | `::test_constraint_lifecycle` | passing |
| Constraint edited and archived | `::test_constraint_lifecycle` | passing |
| Non-member cannot write (including PATCH) | `::test_non_member_is_refused_everywhere` (PUT, POST and PATCH refused) | passing |
| Two workspaces do not leak, including by identifier | `::test_context_items_stay_inside_their_workspace` (a member of the other workspace PATCHing this workspace's objective id gets 404 while authorization passes — the refusal can only come from id scoping) | passing |
| Access rule (unit) | `tests/unit/company_context/test_access.py` (3 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_company_context.py tests/unit/company_context -q` → 11 passed.
Full suite: 116 passed, 2 deselected.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 6 added (`get_company_context`, `save_company_profile`, `create_company_objective`, `update_company_objective`, `create_company_constraint`, `update_company_constraint`); 20 → 26 operations.
- Migration `5a7c1e9d3b48` applied cleanly on the disposable database; `alembic check` reports no drift.
- Strict Mypy includes `apps/api/src/modules/company_context/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (CompanyContext, CompanyProfile, Objective, CompanyConstraint; `Constraint` disambiguated to the analysis dimensions) and `docs/05-data-model.md`.

## Review findings applied

Two-axis review before commit; both findings were fixed rather than deferred:

- PATCH with an explicit `null` for a non-nullable field returned 500 on flush; now validated to 422.
- The "as if the workspace were not found" path reused the idea `not_found` message; a dedicated localized `not_found_workspace` key now says workspace.
- The cross-workspace test passed for the wrong reason (authorization refused before id scoping was reached); it now uses a member of the other workspace.
- Service read/wrote ORM entities and called `session.flush()` (leaky seam); updates now live in the adapter.
- Profile write/response models duplicated seven fields; both derive from one base.

## Known gaps

- The settings UI is a separate ticket (#59); until it lands, the capability is reachable through the API only and no browser/journey evidence exists.
- Principles/strategy and key metrics sub-objects are deliberately out of this slice (decision #45: slice 1 ships profile + objectives + constraints).
- Origin language (`lang`) is not stored for context items. Rationale recorded: they are short labels and descriptions, and the existing `User.bio`/`display_name` precedent treats profile-like meta text as exempt. If Faktus asks for translated company text, this needs a decision, not a silent column.
- The workspace-membership query exists in several adapters (ideas, profiles, company_context, constraint_analysis) as a two-line read on purpose, to keep modules autonomous; extracting a shared kernel is not part of this change.
