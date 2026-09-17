# Acceptance evidence — add-options

Change: `openspec/changes/add-options`
Tickets: GitHub #112 (migration step 5 of `docs/00-project-overview.md` §20, human slice of §7)
Date: 2026-09-17
Delivered by this change: structured Options under a Decision Space, with their §7 fields and their evidence linked to confirmed Contributions. No Critic, no score, no screen.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads an option | `tests/integration/test_options.py::test_option_round_trip_with_every_field` (all nine fields, localized) | passing |
| Non-member requests an option | `::test_non_member_is_refused_everywhere` (404 on read, write, evidence link) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| Option created | `::test_option_round_trip_with_every_field` (author and `lang` follow the write) | passing |
| Title and proposal required | `::test_blank_title_and_proposal_refused` (422 on blank and whitespace-only, both fields, nothing stored) | passing |
| Option edited | `::test_option_update` (a later read returns the updated values) | passing |
| Option deleted | `::test_option_delete` (204, later read 404, gone from the list) | passing |
| Uninvolved member cannot write | `::test_uninvolved_member_cannot_write` (403 on create, patch and delete, unchanged) | passing |
| Non-member cannot write | `::test_non_member_is_refused_everywhere` (POST, PATCH and DELETE refused) | passing |
| Confirmed Contribution linked | `::test_evidence_link_round_trip` (both sides recorded) | passing |
| Unconfirmed Contribution refused | `::test_suggested_contribution_cannot_be_linked` (422, no link) | passing |
| Contribution from another Space refused | `::test_foreign_contribution_cannot_be_linked` (422, no link) | passing |
| Unknown side refused | `::test_unknown_side_refused` (422 on `support`) | passing |
| Duplicate link refused | `::test_duplicate_link_refused` (422, exactly one link kept, first side preserved) | passing |
| Evidence unlinked | `::test_evidence_unlink` (link removed, the Contribution still listed) | passing |
| Evidence legible from the option | `::test_evidence_link_round_trip` (side and Contribution id on both sides) | passing |
| Two Spaces with similar options | `::test_list_returns_only_this_space` (each Space lists only its own) | passing |
| No leak across workspaces | `::test_no_leak_across_workspaces` and `::test_options_stay_inside_their_space` (read and mutate by identifier refused) | passing |
| Every declared field is readable | `::test_option_round_trip_with_every_field` | passing |
| Fields left out read as absent | `::test_option_minimal_fields_read_as_absent` | passing |
| No score is exposed | `::test_option_response_carries_no_score` (response keys asserted exactly, no score or rank key) | passing |
| Participant can also write | `::test_participant_can_write` (extra beyond the spec) | passing |
| Fields rule (unit) | `tests/unit/options/test_option_fields.py` (8 cases) | passing |
| Evidence side rule (unit) | `tests/unit/options/test_evidence.py` (7 cases) | passing |
| Write rule (unit) | `tests/unit/options/test_access.py` (7 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_options.py tests/unit/options -q` → 41 passed (19 integration, 22 unit).
Full suite (`make verify`): lint, formatting, strict Mypy on the domain, `pnpm lint`, `pnpm typecheck`, the FR/EN locale gate and the design-token gate all green, with the integration tests skipped where no database URL is set.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 7 added (`list_options`, `create_option`, `get_option`, `update_option`, `delete_option`, `link_option_evidence`, `unlink_option_evidence`); 0 paths removed; 59 → 66 operations.
- Migration `a2c7e5b81f46` applied cleanly on the disposable database; `alembic check` reports no drift on the first check (the step-3 `ondelete` and column-type lessons were applied up front).
- Strict Mypy includes `apps/api/src/modules/options/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (`Option`, `OptionEvidence`, `Critic`) and `docs/05-data-model.md`.

## Review findings applied

No defect was found by the evidence: the 41 tests passed on the first run, and `alembic check` was clean on the first check. Two behaviours are worth naming because they were decisions rather than accidents:

- An explicit `null` for `title` or `proposal` on PATCH is refused (`_RejectsExplicitNulls`), matching the company-context convention, while an explicit `null` on a narrative field clears it.
- Unlinking a Contribution that is not linked returns 422 rather than 404, so a double unlink is a rule violation and not a missing resource.

## Explicitly deferred (not gaps)

- The Critic and its six checks. The next slice of §7, and the first that needs a model.
- Choosing an Option, the Decision Record, rationale and revisit triggers (step 6).
- Scenarios and simulation under Options (step 7).
- No user interface. Options become visible with the Decision Space screen.

## Known gaps

- None. The implementation tasks are complete.
