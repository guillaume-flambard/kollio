## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the section predicates (a converging Space needs convergence; a completed experiment without an outcome and a draft Learning need learning; a ready Space without a Decision is ready to decide; a Space is the reader's to answer only when they are its owner or a participant).
- [x] 1.2 Add failing unit tests for the ordering key (oldest first, deterministic on a tie).
- [x] 1.3 Implement the pure predicates and the ordering key in `src/modules/inbox/domain/` under strict Mypy.
- [x] 1.4 Append `apps/api/src/modules/inbox/domain` to the Makefile strict-Mypy list.

## 2. Read-only persistence

- [x] 2.1 Implement the adapter reads: the reader's workspace ids, the reader's participant Space ids, the converging Spaces, the ready Spaces without a Decision, the suggested Contributions, the proposed findings, the completed experiments without an Outcome, and the draft Learnings, each scoped as the spec requires and ordered oldest first.
- [x] 2.2 Prove no state was added: `alembic check` reports no drift and no migration exists.

## 3. Service

- [x] 3.1 Implement the service: resolve the reader, assemble the four sections, apply the limit per section, and compute each section's total.
- [x] 3.2 Implement the not-found and validation paths: an unknown subject, and an out-of-range limit.

## 4. HTTP contract

- [x] 4.1 Add the authenticated operation `read_decision_inbox` at `GET /inbox` with the optional bounded `limit`.
- [x] 4.2 Export OpenAPI, regenerate the TypeScript client, and confirm the diff contains only the one added operation.
- [x] 4.3 Add the locale keys the refusals need.

## 5. Evidence

- [x] 5.1 Integration tests on disposable PostgreSQL: each section's positive and negative cases, the personal scoping of needs my input, the no-cross-workspace guarantee, the empty inbox, the ordering, the per-section bound and total, the out-of-range limit, and the absent memory section.
- [x] 5.2 Record the scenario-to-test evidence in `acceptance.md`.
- [x] 5.3 Run Ruff, formatting, strict Mypy and the full verification with the test database exported.

## 6. Vocabulary and docs

- [x] 6.1 Add the Decision Inbox vocabulary to `apps/api/CONTEXT.md` and note that the fifth §4 section is not built.
- [x] 6.2 Record the read in `docs/05-data-model.md` as a projection with no table of its own.
- [x] 6.3 Link the change to its tracker issue.
