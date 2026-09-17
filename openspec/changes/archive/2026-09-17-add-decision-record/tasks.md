## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the revisit trigger shape (metric required and non-blank; `above` and `below` accepted; unknown direction refused; optional threshold and note).
- [x] 1.2 Add failing unit tests for the record fields (rationale required and non-blank; rejected alternatives exclude the selected Option; an unknown side refused).
- [x] 1.3 Add failing unit tests for the access rule (member reads; owner and participant commit; uninvolved member refused; non-member refused).
- [x] 1.4 Implement the pure rules under `decisions/domain` and put them under strict Mypy, including the module in the Makefile list.

## 2. PostgreSQL persistence

- [x] 2.1 Add the schema: `decisions` with a required space FK, unique `(space_id, version)`, non-blank rationale check and closed `lang` check; `decision_rejected_alternatives` with composite key `(decision_id, option_id)`; `decision_arguments` with composite key `(decision_id, contribution_id)` and a closed side check.
- [x] 2.2 Implement the adapter: read the latest record, read one version, list versions with their alternatives and arguments, next version number, create a record with its alternatives and arguments, and the participant snapshot; it is the only flusher.
- [x] 2.3 Register the models with Alembic, run the migration on a disposable database and confirm `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: read the latest record, list versions, commit; non-members get space-not-found.
- [x] 3.2 Refuse a commit outside `READY_TO_DECIDE`, a blank rationale, an Option from another space, the selected Option listed as rejected, an unknown argument side, a suggested or foreign Contribution, and a trigger without a metric — all as validation errors that store nothing.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: commit and read back, minimal record, refusal outside `READY_TO_DECIDE`, space moved to `DECIDED` with the history event, second version after reopening with the first unchanged, blank rationale refused, foreign Option refused, selected Option as rejected refused, argument linking on both sides with refusals, trigger validation, reviewer snapshot frozen across a participation change, versions listed newest first and empty when undecided, no leak across spaces, non-member refusal everywhere, unauthenticated refusal.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md` and note the deferred steps.
- [x] 4.3 Run Ruff, formatting, strict Mypy, the full integration suite and the full verification.

## 5. Vocabulary and docs

- [x] 5.1 Add a Decision Record section to `apps/api/CONTEXT.md` (Decision, Decision version, Decision alternative, Decision argument, Revisit trigger) and mark the Critic as still unbuilt.
- [x] 5.2 Update the transition note to record step 6 as landed.
- [x] 5.3 Add the entity to `docs/05-data-model.md` and link the change to its tracker issue.
