# Acceptance evidence — link-experiments-to-spaces

Change: `openspec/changes/link-experiments-to-spaces`
Tickets: GitHub #116 (migration step 8 of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: the additive link from an experiment to a Decision Space (and optionally one of its Options), and the two reads that let a space see its experiments and learnings. No screen.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Experiment created with a space | `tests/integration/test_experiment_space_links.py::test_linking_a_space_makes_the_experiment_visible_to_the_space` (201, link echoed, then visible to the space) | passing |
| Experiment created with a space and an option | `::test_linking_an_option_of_the_space` (link echoed with the option) | passing |
| Link omitted | `::test_an_unlinked_experiment_stays_out_of_the_space` (`decision_space_id` null, space read empty, initiative read intact) | passing |
| Space from another workspace refused | `::test_space_of_another_workspace_refused` (422, nothing stored) | passing |
| Foreign option refused | `::test_option_of_another_space_refused` (422) | passing |
| Option without a space refused | `::test_option_without_a_space_refused` (422) | passing |
| Unknown space refused | `::test_unknown_space_refused` (422, nothing stored) | passing |
| Existing experiments are untouched | `::test_an_unlinked_experiment_stays_out_of_the_space` (an unlinked row still lists on its initiative) | passing |
| Experiments listed for a space | `::test_linking_a_space_makes_the_experiment_visible_to_the_space` and `::test_a_member_reads_the_space_experiments` (a workspace member who is not the creator reads it) | passing |
| Learnings listed for a space | `::test_learnings_are_read_through_the_linked_experiment` (reached through the experiment, status returned) | passing |
| Nothing yet | `::test_an_unlinked_experiment_stays_out_of_the_space` (empty list, not an error) | passing |
| Non-member asks | `::test_a_non_member_sees_no_space_experiments` (404 on both reads) | passing |
| No leak across workspaces | `::test_spaces_stay_inside_their_workspaces` (the other workspace's member is refused by id) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| Link rule (unit) | `tests/unit/experiments/test_links.py` (9 cases: no link, same-workspace space, option inside its space, foreign-workspace space, unknown space, option of another space, option without a space, unknown option, public idea) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_experiment_space_links.py tests/unit/experiments -q` → 27 passed (12 integration, 15 unit).
Whole integration suite: `uv run pytest tests/integration -q` → 208 passed (was 196 before this change, so the 12 new tests are additive and nothing regressed, which is itself the proof that the initiative path is untouched).
Full suite: `make verify` with `TEST_DATABASE_URL` exported (so the integration tests actually run) → **682 passed, 2 deselected**, plus Ruff, `ruff format --check`, strict Mypy, `pnpm lint`, `pnpm typecheck`, the FR/EN locale gate (472 keys) and the design-token gate all green.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 2 added (`list_space_experiments`, `list_space_learnings`); 0 paths removed; 84 → 86 operations, 70 paths; 112 schemas, 0 removed.
- Migration `c8a4f1d29e63` applied cleanly on the disposable database; `alembic check` reports no drift.
- Strict Mypy includes `apps/api/src/modules/experiments/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- The pre-existing `tests/integration/test_experiments.py` and `tests/integration/test_learning_reuse.py` still pass unchanged, proving the initiative path and the learning confirmation chain are untouched.
- Vocabulary recorded: `apps/api/CONTEXT.md` (Experiment, ExperimentOutcome, Learning, Experiment space link) and `docs/05-data-model.md`.

## Review findings applied

Three findings were handled during implementation and are worth recording:

- The link error subclasses the module's existing `ExperimentRuleError` on purpose, so the route's existing handler returns the established `{"code": "experiment_rule", "message": …}` 422 shape instead of a second, inconsistent error body. Caught while wiring the route.
- A redundant `outcomes_for_experiment` adapter alias was written and then removed before committing: it duplicated the existing `outcomes`.
- A migration that `ruff format --check` rejected on first pass (two over-long lines) was reformatted; the migration was then re-applied from `downgrade -1` to `upgrade head` and `alembic check` still reports no drift, so the formatting change did not alter the schema.
- The integration seed had to flush in dependency order (users and workspaces, then the idea). A single `add_all` batch raised a `ForeignKeyViolationError` on `ideas_owner_id_fkey` because the idea insert reached the database before its user; splitting the batch into two flushes, as the existing experiment test file already does, is what passes. Recorded because it is reproducible, not because the mechanism was fully established.

## Explicitly deferred (not gaps)

- The Memory Retriever (§11) and the learning embedding's provenance extension belong to the retrieval slice.
- Requiring every experiment to belong to a space is deliberately not done: it would invalidate the existing loop and its spec.
- No screen.
- The Outcome and Learning tables are not denormalised onto the space; the chain is reachable by one join.

## Known gaps

- None. The implementation tasks are complete.
