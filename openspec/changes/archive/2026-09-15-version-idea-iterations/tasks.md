## 1. Deterministic domain

- [x] 1.1 Add failing tests for main-write authorization, proposal lifecycle, stale parents and rollback semantics.
- [x] 1.2 Implement the pure iteration decision rules and make strict Mypy cover the module.

## 2. PostgreSQL persistence

- [x] 2.1 Add the append-only iteration schema with branch, status and uniqueness constraints.
- [x] 2.2 Implement transactional history reads and locked mutations with atomic idea projection updates.
- [x] 2.3 Verify repository behavior and workspace isolation against PostgreSQL.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated list, create, accept, reject and rollback endpoints.
- [x] 3.2 Export OpenAPI, regenerate the TypeScript client and verify no contract drift.

## 4. Quality

- [x] 4.1 Run Ruff, formatting, strict Mypy, unit and integration tests.
- [x] 4.2 Validate the OpenSpec change strictly and record the completed tasks.
