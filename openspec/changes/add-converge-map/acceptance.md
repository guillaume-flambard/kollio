# Acceptance evidence — add-converge-map

Change: `openspec/changes/add-converge-map`
Tickets: GitHub #111 (migration step 4 of `docs/00-project-overview.md` §20, first slice)
Date: 2026-09-17
Delivered by this change: the human-built reasoning map — explicit relations, explicit Clusters and the map read. No screen, no AI proposer.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Member reads the map | `tests/integration/test_converge_map.py::test_member_reads_map` (confirmed Contributions, one relation, one Cluster, localized) | passing |
| Non-member requests the map | `::test_non_member_is_refused_everywhere` (404 on map, relation create and cluster create, no disclosure) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401) | passing |
| Suggested Contributions stay out | `::test_suggested_contributions_excluded` | passing |
| Relation asserted | `::test_relation_round_trip` (author recorded, map shows it) | passing |
| Unknown relation type refused | `::test_unknown_relation_type_refused` (422, nothing stored) | passing |
| Self-relation refused | `::test_self_relation_refused` (422, nothing stored) | passing |
| Cross-space pair refused | `::test_cross_space_pair_refused` (404, nothing stored or disclosed) | passing |
| Duplicate directed pair refused | `::test_duplicate_pair_refused` (422, existing untouched) | passing |
| Uninvolved member cannot link | `::test_uninvolved_member_cannot_write` (403 on relation and cluster, unchanged) | passing |
| Relation removed | `::test_relation_removed` (204, map clean, Contributions remain) | passing |
| Unknown relation removal refused | `::test_unknown_relation_removal_refused` (404) | passing |
| Cluster created | `::test_cluster_lifecycle` (empty members, map shows it) | passing |
| Blank cluster title refused | `::test_blank_cluster_title_refused` (422 on `` and whitespace, nothing stored) | passing |
| Contribution assigned and moved | `::test_member_assigned_and_moved` (latest Cluster only) | passing |
| Contribution unassigned | `::test_member_unassigned` (unclustered, Contribution untouched) | passing |
| Cluster deleted, members kept | `::test_cluster_deleted_members_kept` (204, unclustered, Contributions remain with null cluster) | passing |
| Foreign Contribution refused | `::test_foreign_member_refused` (404, nothing stored) | passing |
| Spaces do not leak | `::test_maps_stay_inside_their_space` (other workspace refused by identifier) | passing |
| Relation rule (unit) | `tests/unit/converge/test_relations.py` (13 cases: eight types, unknown, self) | passing |
| Cluster and access rules (unit) | `tests/unit/converge/test_access.py` (11 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_converge_map.py tests/unit/converge -q` → 43 passed (19 integration, 24 unit).
Full suite (`make verify`, integration skipped without a database URL): 287 passed, 111 skipped, 2 deselected, plus Ruff, formatting, strict Mypy on the domain, `pnpm lint`, `pnpm typecheck`, the FR/EN locale gate and the design-token gate all green.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 7 added (`get_converge_map`, `create_relation`, `delete_relation`, `create_cluster`, `delete_cluster`, `add_cluster_member`, `remove_cluster_member`); 0 paths removed; 52 → 59 operations.
- Migration `f7d2a9c4e1b8` applied cleanly on the disposable database; `alembic check` reports no drift on the first check (the `ondelete` and type lessons from step 3 were applied up front).
- Strict Mypy includes `apps/api/src/modules/converge/domain` (Makefile + CI).
- Permissions proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (converge-map section) and `docs/05-data-model.md`.

## Review findings applied

Two-axis review before commit; the evidence found no defects — 43/43 on the first run. Pre-emptive alignments (not findings): the ordered-pair unique constraint is named identically in model and migration, and the `contributions.cluster_id` column lives on the branches model so ORM and schema agree.

## Known gaps

- None. The implementation tasks are complete; the AI proposer, Options promotion, merge/split beyond assign/unassign and screens belong to their own slices.
