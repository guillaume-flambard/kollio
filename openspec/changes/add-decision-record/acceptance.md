# Acceptance evidence — add-decision-record

Change: `openspec/changes/add-decision-record`
Tickets: GitHub #114 (migration step 6 of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: the versioned, append-only Decision Record — commit from a ready space, rejected alternatives, arguments linked to confirmed Contributions, uncertainty, criteria, structured revisit triggers, frozen reviewer snapshot. No screen, no Critic run.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads the record | `tests/integration/test_decision_record.py::test_member_reads_the_record` (version, locale, selected Option) | passing |
| No record yet | `::test_no_record_yet` (404 on the record, empty version list, no error) | passing |
| Non-member requests the record | `::test_non_member_is_refused_everywhere` (404 on read, versions and commit) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| A record never leaks across spaces or workspaces | `::test_records_stay_inside_their_space` (member of the other workspace refused by id) | passing |
| Committed from a ready space | `::test_commit_from_ready_space_moves_it_to_decided` (space `DECIDED`, history event with its actor) | passing |
| Committed from any other status | `::test_commit_outside_ready_to_decide_refused` (4 statuses, 422, no record, no new history event) | passing |
| A re-decided space takes a new version | `::test_second_version_after_reopening` (reopen, resume, re-commit → version 2; version 1 stored unchanged) | passing |
| Full record committed | `::test_full_record_round_trip` (every field, both argument sides, trigger normalization, reviewer snapshot, `decided_by`) | passing |
| Minimal record committed | `::test_minimal_record_round_trip` (optional fields absent, not failed) | passing |
| Rationale required | `::test_blank_rationale_refused` (422 on `` and on whitespace, nothing stored) | passing |
| Selected Option must belong to the space | `::test_foreign_option_refused` (an Option from another space refused) | passing |
| A rejected alternative cannot be the selected Option | `::test_selected_option_cannot_be_rejected` | passing |
| Arguments reference confirmed Contributions of the space | `::test_argument_linking_rules` (unknown Contribution, `suggested` Contribution, foreign-space Contribution all refused, nothing stored) | passing |
| One Contribution cannot argue both ways | `::test_argument_linking_rules` (the same Contribution on both sides refused) | passing |
| Revisit triggers are structured | `::test_revisit_trigger_validation` (5 refused shapes, a metric-only trigger accepted) | passing |
| Reviewers are snapshotted | `::test_reviewer_snapshot_is_frozen` (removing the participant leaves the stored reviewers unchanged) | passing |
| Versions listed | `::test_second_version_after_reopening` (newest first: `[2, 1]`) and `::test_no_record_yet` (empty list) | passing |
| An earlier version is unchanged | `::test_second_version_after_reopening` (version 1 keeps its rationale and selected Option) | passing |
| Writers commit, members read | `::test_participant_can_commit` (participant recorded as `decided_by`), `::test_uninvolved_member_cannot_commit` (403, nothing stored) | passing |
| Trigger shape (unit) | `tests/unit/decisions/test_triggers.py` (13 cases) | passing |
| Record fields (unit) | `tests/unit/decisions/test_record_fields.py` (12 cases) | passing |
| Access rule (unit) | `tests/unit/decisions/test_access.py` (6 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_decision_record.py tests/unit/decisions -q` → 54 passed.
Full integration suite after this change: `uv run pytest tests/integration -q` → 172 passed.
Full verification: `make verify` → 420 passed, 174 skipped, 2 deselected, plus Ruff, `ruff format --check`, strict Mypy on `decisions/domain`, `pnpm lint`, `pnpm typecheck`, the FR/EN locale gate (472 keys) and the design-token gate all green.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, exactly 3 added (`get_decision_record`, `list_decision_versions`, `commit_decision`); 0 paths removed; 72 → 75 operations.
- Migration `d5a8f2b64c19` applied cleanly on the disposable database; `alembic check` reported no drift on the first check.
- Strict Mypy includes `apps/api/src/modules/decisions/domain` (Makefile + CI).
- Permissions proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (Decision, Decision version, Decision alternative, Decision argument, Revisit trigger) and `docs/05-data-model.md`.

## Review findings applied

Two-axis review before commit; both findings were fixed rather than deferred:

- The argument key was designed as `(decision_id, contribution_id, side)`, which would have let the same Contribution argue both for and against one decision. The key is now `(decision_id, contribution_id)` with `side` as a column, and the service refuses the contradiction with a validation error instead of relying on a database error. `design.md`, `spec.md` and the tests were all updated with it.
- `apps/api/CONTEXT.md` defined **Critic** twice (once in the Challenge section, once misplaced at the end of the Options section, the second calling it "the next slice of step 7"). The duplicate is gone: one definition in the Challenge section, carrying the "nothing ranks or scores an Option while it is absent" note.

## Known gaps

- None for this slice. The deferred items named in the proposal (Critic, simulation, Outcome/Learning, Decision Inbox, integrations, screens) belong to their own steps.
