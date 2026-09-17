## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the option fields rule (title and proposal accepted when usable, refused when blank or whitespace-only).
- [x] 1.2 Add failing unit tests for the evidence side rule (the two declared sides accepted, anything else refused).
- [x] 1.3 Add failing unit tests for the write rule (owner and participant allowed, uninvolved member refused).
- [x] 1.4 Implement the pure rules in `options/domain` under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the options schema and the evidence link table with a Space foreign key, non-blank title and proposal checks, a closed side check, a composite key on the link and cascade deletes.
- [x] 2.2 Implement the adapter: create, read, list by Space, update, delete, link and unlink evidence, all Space-scoped, with the adapter the only place that flushes.
- [x] 2.3 Register the models with Alembic, apply the migration on a disposable database and confirm `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: list, create, read, update, delete, link evidence and unlink evidence; non-members get workspace-not-found, unauthenticated callers get 401.
- [x] 3.2 Refuse blank titles and proposals, unknown sides, unconfirmed Contributions, Contributions from another Space and duplicate links, each as a validation error that stores nothing.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: option round-trip with every field, blank title and proposal refused, update, delete, evidence link on both sides, unconfirmed Contribution refused, foreign Contribution refused, unknown side refused, duplicate link refused, unlink, uninvolved member refused, non-member refused on every operation, cross-Space isolation by identifier, `lang` follows the request locale.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md` and note the deferred Critic slice.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full suite.

## 5. Vocabulary and docs

- [x] 5.1 Add an options section to `apps/api/CONTEXT.md` defining `Option` and `OptionEvidence`, and stating that the Critic and every score are absent by design.
- [x] 5.2 Add the entities to `docs/05-data-model.md` and link the change to its tracker ticket.
