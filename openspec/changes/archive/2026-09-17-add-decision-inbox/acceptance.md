# Acceptance evidence — add-decision-inbox

Change: `openspec/changes/add-decision-inbox`
Tickets: GitHub #117 (migration step 9 of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: the Decision Inbox read — what waits on a member across their workspaces. No screen, no stored state.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A member reads their inbox | `tests/integration/test_decision_inbox.py::test_converging_spaces_appear_oldest_first_with_their_total` (an owner reads their own inbox) | passing |
| The inbox never crosses workspaces | `::test_the_inbox_never_leaks_across_workspaces` | passing |
| A member with nothing waiting | `::test_an_empty_inbox_is_an_empty_answer_not_an_error` (a quiet workspace, the exact four section keys, every section empty) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| A converging Space appears | `::test_converging_spaces_appear_oldest_first_with_their_total` | passing |
| A Space elsewhere in the lifecycle does not | `::test_an_exploring_space_is_quoted_by_no_section`, `tests/unit/inbox/test_sections.py::test_no_other_status_needs_convergence` (parametrized over the other seven statuses) | passing |
| A suggested Contribution waits for a participant | `::test_suggested_contributions_await_my_input` | passing |
| A proposed finding waits for a participant | `::test_suggested_contributions_await_my_input` (the finding branch) | passing |
| An uninvolved member is not asked | `::test_needs_my_input_is_personal_to_owner_and_participants`, `tests/unit/inbox/test_sections.py::test_an_uninvolved_member_does_not_answer_for_a_space` | passing |
| Confirmed work stops waiting | `::test_suggested_contributions_await_my_input` (a confirmed contribution and a confirmed finding are asserted absent) | passing |
| A prepared Space appears | `::test_a_ready_space_awaits_commitment` | passing |
| A committed Decision stops the prompt | `::test_a_space_that_already_holds_a_decision_is_not_prompted` | passing |
| A Space elsewhere in the lifecycle does not (ready) | `::test_an_exploring_space_is_quoted_by_no_section`, `tests/unit/inbox/test_sections.py::test_no_other_status_is_ready_to_decide` (parametrized) | passing |
| A completed experiment with no outcome | `::test_a_completed_experiment_without_an_outcome_awaits_learning` | passing |
| A draft Learning awaits confirmation | `::test_a_draft_learning_awaits_confirmation_and_a_confirmed_one_does_not` | passing |
| An experiment still running does not | `::test_a_completed_experiment_without_an_outcome_awaits_learning` (a running and an already-answered experiment are asserted absent), `tests/unit/inbox/test_sections.py::test_an_unfinished_experiment_does_not_need_an_outcome` | passing |
| A confirmed Learning is done | `::test_a_draft_learning_awaits_confirmation_and_a_confirmed_one_does_not` | passing |
| The longest wait comes first | `::test_converging_spaces_appear_oldest_first_with_their_total` (three converging Spaces with explicit ages), `tests/unit/inbox/test_sections.py::test_order_puts_the_longest_wait_first` | passing |
| The bound is applied per section | `::test_the_limit_bounds_each_section_and_the_total_still_speaks` (limit 2 of 3, `total == 3`) | passing |
| An out-of-range limit is refused | `::test_an_out_of_range_limit_is_refused` (parametrized `0`, `51`, `-1` → 422) | passing |
| No empty memory section | `::test_the_memory_section_is_absent_because_it_cannot_be_answered` (exact key set) | passing |
| Section predicates (unit) | `tests/unit/inbox/test_sections.py` (16 functions, 28 cases) | passing |
| Ordering key (unit) | `tests/unit/inbox/test_sections.py::test_order_is_deterministic_on_an_identical_age` | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_decision_inbox.py tests/unit/inbox -q` → 44 passed (16 integration test instances, 28 unit cases).
Whole integration suite: `uv run pytest tests/integration -q` → 224 passed (was 208 after step 8).

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: exactly **1 operation added** (`read_decision_inbox`), 1 path added (`/inbox`), **0 operations removed, 0 paths removed, 0 schemas removed**, 0 canonical lines removed; 86 → 87 operations.
- **No migration and no table**: `alembic check` reports no drift and no migration was written, which is the evidence that this slice added no state. The inbox is a projection over rows the other capabilities own.
- Strict Mypy includes `apps/api/src/modules/inbox/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded in `apps/api/CONTEXT.md` (DecisionInbox, Inbox section, Inbox entry, Relevant prior memory) and `docs/05-data-model.md`.

## Review findings applied

Three real defects were found by the evidence and fixed in the implementation rather than worked around in the tests:

- `InboxEntryResponse` had no `model_config = ConfigDict(from_attributes=True)`, so validating an adapter `InboxRow` dataclass raised a Pydantic `ValidationError` instead of building the response.
- `PostgresInbox.spaces_answered_by` anchored its `User` join on `DecisionSpace.owner_id`, so it only ever matched the owner; a participant's `needs_my_input` section was always empty. The reader is now resolved from the subject first and matched as owner **or** participant, and an owner-only Space (no participant row) stays visible.
- `PostgresInbox.draft_learnings` returned no detail while the sibling experiment branch returned the experiment title, so a Learning awaiting confirmation had nothing for a client to show. It now returns the Learning text.

Two test-side corrections were also made, where the implementation was right: `subject_id` is legitimately absent for a space-level entry (the design says it carries the row id only when the entry is about one row), so the ready-to-decide assertions were switched to the space id; and an unused import was removed.

## Explicitly deferred (not gaps)

- No screen. The Home screen consumes this read and belongs to its own slice.
- `relevant_prior_memory` is not returned: its source is the memory retriever (§11), which is not built. An empty section would assert that no relevant memory exists, which nothing supports today.
- Notifications, digests, unread badges and writing from the inbox (dismiss, snooze, assign) are each state and belong with the object they would change.

## Known gaps

- None. The implementation tasks are complete.
