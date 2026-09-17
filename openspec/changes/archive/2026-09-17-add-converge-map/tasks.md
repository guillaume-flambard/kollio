## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the relation rule (eight declared types accepted, unknown types refused, self-relation refused).
- [x] 1.2 Add failing unit tests for the cluster rule (blank title refused) and the access rule (member reads the map, owner and participant write, uninvolved member refused, non-member denied).
- [x] 1.3 Implement the pure rules and put `converge/domain` under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add the schema: `contribution_relations` (Space FK, two Contribution FKs, closed type check, no-self check, unique ordered pair), `clusters` (Space FK, non-blank title check), and `contributions.cluster_id` (nullable FK with `ON DELETE SET NULL`).
- [x] 2.2 Implement the adapter: map read (confirmed Contributions, relations, Clusters with members), create/delete relations, create/delete Clusters, assign/unassign/move members. The adapter is the only place that flushes.
- [x] 2.3 Register the new models with Alembic, run the migration on a disposable database, `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated endpoints: read map, create relation, delete relation, create Cluster, delete Cluster, assign member, unassign member. Non-members get space-not-found; unauthenticated callers get 401.
- [x] 3.2 Refuse unknown relation types, self-relations, cross-space pairs, duplicate ordered pairs, blank cluster titles, foreign members and unknown ids — all as validation errors that store nothing; refuse uninvolved writers as forbidden.
- [x] 3.3 Export OpenAPI, regenerate the TypeScript client, diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: map round-trip with suggested Contributions excluded, relation lifecycle, self/cross-space/duplicate/unknown refusals, cluster lifecycle with move and delete-nulling, non-member refusal on every operation, uninvolved writes refused, cross-workspace isolation by identifier, `lang` follows the request locale.
- [x] 4.2 Record scenario-to-test evidence in `acceptance.md`.
- [x] 4.3 Run Ruff, formatting, strict Mypy and the full suite.

## 5. Vocabulary and docs

- [x] 5.1 Add the converge-map section in `apps/api/CONTEXT.md` (`ContributionRelation`, `Cluster`, the map, one-relation-per-pair).
- [x] 5.2 Add the entities to `docs/05-data-model.md` and link the change to its tracker epic.
