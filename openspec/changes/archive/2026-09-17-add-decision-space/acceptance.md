# Acceptance evidence — add-decision-space

Change: `openspec/changes/add-decision-space`
Tickets: GitHub #109 (migration step 2 of `docs/00-project-overview.md` §20)
Date: 2026-09-16
Delivered by this change: the Decision Space parent domain — object, lifecycle, history, permissions and HTTP contract. No screen.

Status: **implemented and verified.** Every scenario below is bound to a test that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads a Decision Space | `tests/integration/test_decision_space.py::test_member_reads_space` (question, owner, status, participants, `Content-Language: en`) | passing |
| Non-member requests a Decision Space | `::test_non_member_is_refused_everywhere` (list, create, read, transition, add and remove all 404) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401 + `WWW-Authenticate: Bearer`, session never overridden) | passing |
| A Decision Space never leaks across workspaces | `::test_spaces_stay_inside_their_workspace` (a member of the other workspace holding the real id gets 404) | passing |
| Opened | `::test_open_round_trip` (201, `OPEN`, owner is the first participant, `lang` follows the locale) | passing |
| Question required | `::test_empty_question_refused` (`""` and `"   "` both 422, list stays empty) | passing |
| Optional frame recorded | `::test_open_with_description_and_deadline` | passing |
| Non-member cannot open a Space | `::test_non_member_is_refused_everywhere` (create 404) | passing |
| Forward transition accepted | `::test_declared_chain_walked_end_to_end` | passing |
| Skipping a step refused | `::test_undeclared_transition_refused` (`OPEN`→`DECIDED` 422, history length unchanged) | passing |
| Unknown status refused | `::test_unknown_status_refused` (`ARCHIVED` 422, nothing stored) | passing |
| The declared chain is walkable end to end | `::test_declared_chain_walked_end_to_end` (lands `LEARNED`) | passing |
| A terminal Space cannot resume without reopening | `::test_undeclared_transition_refused` (`LEARNED`→`TESTING` 422) | passing |
| Reopened with a reason | `::test_reopen_requires_reason` (reason lands in history with `from_status`) | passing |
| Reason required | `::test_reopen_requires_reason` (absent and whitespace-only both 422, still `DECIDED`) | passing |
| Work resumes after reopening | `::test_reopened_space_resumes_at_exploring` | passing |
| A Space that was never decided cannot be reopened | `::test_undeclared_transition_refused` (reopen refused from `OPEN`/`EXPLORING`/`CONVERGING`/`READY_TO_DECIDE`) | passing |
| History accumulates in order | `::test_status_history_is_ordered_and_immutable` | passing |
| History is readable | `::test_status_history_is_ordered_and_immutable` (actor and timestamp on every entry) | passing |
| A refused transition leaves no trace | `::test_undeclared_transition_refused` + `::test_uninvolved_member_cannot_write` | passing |
| Opening records the first entry | `::test_open_round_trip` (`from_status: null` → `OPEN`) | passing |
| Participant added | `::test_participant_lifecycle` | passing |
| Adding the same participant twice is idempotent | `::test_participant_lifecycle` (still exactly two) | passing |
| A non-member cannot participate | `::test_participant_must_belong_to_workspace` (422, roster unchanged) | passing |
| The owner cannot be removed | `::test_participant_lifecycle` (422) | passing |
| Participants persist | `::test_participant_lifecycle` (read-back includes the owner) | passing |
| A participant transitions the status | `::test_participant_can_transition_status` | passing |
| An uninvolved member cannot write | `::test_uninvolved_member_cannot_write` (403 for both status and participants, status and history unchanged) | passing |
| Only the owner manages participants | `::test_only_owner_manages_participants` (participant adding a third gets 403) | passing |
| Spaces listed | `::test_list_returns_only_this_workspace` | passing |
| Nothing yet | `::test_list_is_empty_not_an_error` (`{"items": []}`, 200) | passing |
| A non-member lists nothing | `::test_non_member_is_refused_everywhere` (list 404) | passing |
| Access rule (unit) | `tests/unit/decision_spaces/test_access.py` (11 cases) | passing |
| Transition rule (unit) | `tests/unit/decision_spaces/test_transitions.py` (every declared edge accepted, every one of the 54 undeclared pairs refused) | passing |
| Reopen rule (unit) | `tests/unit/decision_spaces/test_transitions.py` (reason required on exactly the three reopening edges) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_decision_space.py tests/unit/decision_spaces -q` → **124 passed**.
Full suite: `make verify` → **309 passed, 2 deselected**, plus Ruff, formatting, strict Mypy, `pnpm lint`, `pnpm typecheck`, the locale gate (472 keys) and the design-token gate.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: **0 operations removed, exactly 6 added** (`list_decision_spaces`, `open_decision_space`, `get_decision_space`, `transition_decision_space`, `add_decision_space_participant`, `remove_decision_space_participant`); no path removed; 40 → 46 operations.
- Migration `c4e9b7a2d815` applied cleanly on the disposable database and `alembic check` reports **"No new upgrade operations detected"** (no drift).
- Strict Mypy includes `apps/api/src/modules/decision_spaces/domain` (Makefile line 33) and passes.
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded in `apps/api/CONTEXT.md` (a **Vocabulary in transition** note plus a **Decision spaces** section) and in `docs/05-data-model.md`.

## Review findings applied

Both were caught by the evidence rather than deferred:

- **History order was not actually guaranteed.** `decision_space_status_events` was ordered by `(created_at, id)`, but Postgres `now()` is the transaction timestamp, so several events written in one transaction tie and the random uuid broke the order. A monotonic `seq` identity column now carries the order and history is read by it; the ordering assertion is a real invariant instead of a timestamp accident.
- **Reading a space back after a transition raised `MissingGreenlet`.** `updated_at` uses a server-side `onupdate`, so the attribute was expired after the flush and Pydantic read it outside the greenlet. The adapter now refreshes the row after flushing, matching the `experiments` adapter.
- The unauthenticated test overrides only `get_session` (never `current_identity`) so the 401 comes from the real bearer dependency rather than a stub.

## Explicitly deferred (not gaps)

- No user interface. The Decision Space screens belong to Converge (step 4), which gives them something real to show.
- Ideas are not yet mapped into Branches and Contributions (step 3), so `Idea` remains the object users see in the product.
- `Outcome` and `Learning` still hang off an initiative; re-parenting them to the Decision → Experiment → Outcome → Learning chain is step 8.
- `READY_TO_DECIDE`→`CONVERGING` is deliberately unmodelled until the Decision Record exists (step 6). See `design.md` Open questions.

## Known gaps

- None. The change is complete for step 2 of the migration sequence.
