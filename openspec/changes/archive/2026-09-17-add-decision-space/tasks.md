## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the transition rule: every declared edge accepted, every undeclared edge refused (`OPEN`→`DECIDED`, `LEARNED`→`TESTING`, unknown values).
- [x] 1.2 Add failing unit tests for the reopen rule: reopen refused without a reason, refused from `OPEN`/`EXPLORING`/`CONVERGING`/`READY_TO_DECIDE`, accepted from `DECIDED`/`TESTING`/`LEARNED`.
- [x] 1.3 Add failing unit tests for the access rule: member reads, owner and participant write status, uninvolved member refused, owner-only participant management.
- [x] 1.4 Implement the pure rules and put `decision_spaces/domain` under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the schema: `decision_spaces` (workspace FK, non-empty question check, closed status check, `lang`, timestamps), `decision_space_participants` (unique per space and user), `decision_space_status_events` (append-only, ordered).
- [x] 2.2 Implement the adapter: create with its first status event, read with participants and history, list by workspace, append a status event, add and remove participants. The adapter is the only place that flushes.
- [x] 2.3 Register the models with Alembic, run the migration on a disposable database, and verify `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: list, create, read, transition status, add participant, remove participant. Non-members receive the workspace-not-found treatment; unauthenticated callers receive 401.
- [x] 3.2 Refuse an empty question, an unknown or undeclared status, a reopen without a reason, a participant who is not a workspace member, and removal of the owner — all as validation errors that store nothing.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only the new operations.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: create/read round-trip, the full declared chain walked end to end, a skipped step refused, an unknown status refused, reopen with and without a reason, resume from `REOPENED`, history order and immutability, participant add idempotence, owner-not-removable, non-member refusal on every operation, cross-workspace isolation by identifier, `lang` follows the request locale.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md`, marking the deferred steps explicitly.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full test suite.

## 5. Vocabulary and docs

- [x] 5.1 Add a Decision Space section to `apps/api/CONTEXT.md`: `DecisionSpace`, `DecisionSpaceParticipant`, `DecisionSpaceStatusEvent`, and the status value names.
- [x] 5.2 Note in `apps/api/CONTEXT.md` that the Idea, RealismScore and matching vocabulary is being re-pointed by steps 3 to 8 of the migration, so the two vocabularies are not read as coexisting targets.
- [x] 5.3 Add the entity to `docs/05-data-model.md` and link the change to its tracker epic.
