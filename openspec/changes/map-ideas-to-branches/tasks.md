## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the mapping rule: a workspace Idea is mappable, a public Idea is not, an already-mapped Idea is skipped.
- [x] 1.2 Add failing unit tests for the propose rule: a valid kind and title are accepted, an unknown kind is refused, an empty title is refused, a human proposal is `confirmed` while an AI suggestion stays `suggested` until confirmed.
- [x] 1.3 Add failing unit tests for the access rule: a private Branch reads only for its creator, a shared Branch reads for Space readers, a writer proposes and confirms, an uninvolved member is refused everywhere.
- [x] 1.4 Implement the pure rules and put `branches/domain` under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the Branch and Contribution schema: `branches` (space, creator and optional source-idea references, non-empty title check, closed visibility check, `lang`, timestamps), `contributions` (space, branch and author references, closed kind and status checks, non-empty title check, `lang`, timestamps).
- [x] 2.2 Implement the adapter: create, read and list Branches; map an Idea (create its Space and Branch, skip when already mapped); propose, confirm and list Contributions. The adapter is the only place that flushes.
- [x] 2.3 Register the new models with Alembic and verify no schema drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: create, list and read Branches; propose, list and confirm Contributions. Non-members get workspace-not-found; unauthenticated callers get 401.
- [x] 3.2 Refuse an empty title, an unknown kind, a proposal from an unreadable Branch, a confirmation by an uninvolved member, and the mapping of a public Idea — all as validation errors that store nothing.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only the new operations.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: Branch create/read round-trip and private visibility, Space Branch listing, Idea mapping (Space plus Branch created, title and pitch carried, history reachable, idempotent, public skipped, Idea path untouched), human proposal confirmed with provenance, AI suggestion waiting, confirmation flipping author and status, unknown kind refused, unreadable Branch refused, non-member refusal on every operation, cross-workspace isolation by identifier, `lang` follows the request locale.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md`.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full test suite.

## 5. Vocabulary and docs

- [x] 5.1 Record both Branch senses and the Contribution in `apps/api/CONTEXT.md`, with the mapping note that the iteration `branch` string is read as raw material.
- [x] 5.2 Add the Branch and Contribution entities to `docs/05-data-model.md` and link the change to its tracker epic.
