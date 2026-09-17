## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the link rule: same workspace accepted; a space from another workspace refused; an option outside the space refused; an option without a space refused; no link accepted.
- [x] 1.2 Implement the pure link rule under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the two nullable columns (`decision_space_id`, `option_id`) to `experiments`, with `ondelete="SET NULL"` and indexes, leaving existing rows untouched.
- [x] 2.2 Extend the adapter: read a space's experiments, read a space's learnings with their experiment, and the lookups the link rule needs.
- [x] 2.3 Register the models with Alembic, run the migration on a disposable database and confirm `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Accept the optional `decision_space_id` and `option_id` on experiment creation, with the refusals as validation errors that store nothing.
- [x] 3.2 Add the two member-scoped reads: a space's experiments and a space's learnings, refusing non-members as not found.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: linked creation, space plus option, unlinked creation unchanged, cross-workspace space refused, foreign option refused, option without space refused, experiments listed per space, learnings listed per space with status, empty list not an error, unknown space, non-member refusal on both reads, unauthenticated 401.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md`.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full suite.

## 5. Vocabulary and docs

- [x] 5.1 Note the link in `apps/api/CONTEXT.md` without redefining the existing loop's vocabulary.
- [x] 5.2 Record the two columns in `docs/05-data-model.md`.
