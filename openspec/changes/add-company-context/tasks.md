## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the context access rule (member allowed, non-member denied).
- [x] 1.2 Implement the pure access rule and put it under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the company context schema (profile, objectives, constraints) with workspace foreign keys, unique single profile per workspace and closed state checks.
- [x] 2.2 Implement the adapter: read context, upsert profile, create/update objectives, create/update constraints, all workspace-scoped.
- [x] 2.3 Register the new models with Alembic and verify no schema drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: read context, save profile, create/update objectives, create/update constraints; non-members get not-found.
- [x] 3.2 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only the new operations.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: profile round-trip and upsert, objective create/lifecycle, constraint create/update/archive, non-member refusal, cross-workspace isolation.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md` and note the UI slice as pending.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full test suite.

## 5. Settings UI

- [x] 5.1 Add the workspace settings screen with profile fields, objectives list (create, priority, archive) and constraints list (create, archive).
- [x] 5.2 Add BFF endpoints forwarding to the generated company-context client operations.
- [x] 5.3 Add FR/EN catalog keys and a settings entry point in the workspace navigation.
- [x] 5.4 Browser acceptance in FR and EN: load, save profile, create and archive objective, create and archive constraint, failure feedback.
- [x] 5.5 Record the UI scenario evidence in `acceptance.md` and rerun the full verification.
