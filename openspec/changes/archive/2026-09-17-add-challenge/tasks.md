## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the closed vocabularies: the six checks, three severities, four run statuses, four origins and statuses, with unknown values refused.
- [x] 1.2 Add failing unit tests for the finding shape: a detail is trimmed and must not be blank, and an origin decides the arriving status (human means confirmed, critic means proposed).
- [x] 1.3 Add failing unit tests for the run lifecycle: `OPEN` to `RUNNING` to `COMPLETED`, `FAILED` from `RUNNING`, terminal states refusing everything, unknown statuses refused.
- [x] 1.4 Add failing unit tests for coverage: covered kinds, dismissed findings not covering, uncovered kinds always listed, and a missing run set reading as nothing covered.
- [x] 1.5 Add failing unit tests for the access rule: a member reads, a non-member does not, and only the owner plus participants write.
- [x] 1.6 Implement the pure rules in `challenge/domain` under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the schema: `challenge_runs` with cascading FKs to the Space and the Option, a closed status check, `lang` and timestamps; `challenge_findings` with a cascading FK to the run, closed checks on kind, severity, origin and status, a non-blank detail check, an optional Contribution FK and a run index.
- [x] 2.2 Implement the adapter: resolve memberships, the Space, the Option and a Contribution; open a run; read a run with its findings; list runs for an Option; record a finding; resolve a finding; complete a run — the adapter is the only place that flushes.
- [x] 2.3 Register the models with Alembic, apply the migration to the disposable database and confirm `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: list an Option's challenges, open a run, read a run, record a finding, resolve a finding (confirm or dismiss), complete a run.
- [x] 3.2 Refuse an unknown check or severity, a blank detail, a foreign Contribution, an undeclared lifecycle transition, a non-member and an uninvolved member, each as a validation, forbidden or not-found response storing nothing.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: run round-trip, one finding of each of the six kinds, unknown kind and severity refused, blank detail refused, Contribution reference round-trip, foreign Contribution refused, a critique-origin finding arriving proposed, confirm and dismiss keeping the record, coverage with and without dismissed findings, an unchallenged Option, a completed run refusing further transitions, the non-member refusal on every operation, the uninvolved-member refusal, cross-workspace isolation by identifier, and the unauthenticated refusal.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md` and note the Critic as deferred rather than a gap.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full suite.

## 5. Vocabulary and docs

- [x] 5.1 Add a Challenge section to `apps/api/CONTEXT.md` defining the run, the finding, the six checks and the coverage read, marking the Critic as not built.
- [x] 5.2 Add the entity to `docs/05-data-model.md` and link the change to its tracker issue.
