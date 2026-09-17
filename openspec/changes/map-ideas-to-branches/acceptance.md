# Acceptance evidence — map-ideas-to-branches

Change: `openspec/changes/map-ideas-to-branches`
Tickets: GitHub #110 (migration step 3 of `docs/00-project-overview.md` §20)
Date: 2026-09-17
Delivered by this change: exploration Branches under Decision Spaces, the Idea-to-Branch mapping, and human-confirmed Contributions proposed from Branch material. No screen.

Status: **implemented and verified.** Every row below names the real test that proves it.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Shared Branch created and read back | `tests/integration/test_branches.py::test_shared_branch_round_trip` (title, visibility, space, `lang` follows locale) | passing |
| Private Branch visible only to its creator | `::test_private_branch_hidden_from_other_members` (creator 200, other member 404) | passing |
| Branch without a title refused | `::test_blank_branch_title_refused` (422 on `` and on whitespace, nothing stored) | passing |
| Spaces list their Branches | `::test_branches_listed_per_space` (two Spaces, exact titles, empty list not an error covered by the refused test) | passing |
| Workspace Idea mapped | `::test_workspace_idea_mapped_to_branch` (Space plus shared Branch, title and pitch carried, history linked, parent Space question/owner/workspace) | passing |
| Mapping is idempotent | `::test_mapping_skips_already_mapped_idea` (second call returns the same Branch, created False) | passing |
| Public Idea left alone | `::test_public_idea_not_mapped` (MappingNotFoundError, nothing created) | passing |
| Idea read path untouched | `::test_mapped_idea_still_reads_as_before` (`GET /ideas/{id}` identical before and after) | passing |
| Human proposes a Contribution | `::test_human_proposal_confirmed_with_provenance` (status confirmed, author, kind, source, tool/model, transformation history) | passing |
| AI suggestion waits for a human | `::test_ai_suggestion_not_canonical_until_confirmed` (status suggested) | passing |
| Human confirms a suggestion | `::test_confirmation_flips_status_and_author` (participant confirms, status confirmed, author becomes confirmer) | passing |
| Unknown kind refused | `::test_unknown_contribution_kind_refused` (422, nothing stored) | passing |
| Proposing from an unreadable Branch refused | `::test_proposal_from_unreadable_branch_refused` (participant proposes from a private Branch, 404, nothing stored) | passing |
| Non-member sees nothing | `::test_non_member_is_refused_everywhere` (404 on both lists and all three writes, no disclosure) | passing |
| Uninvolved member cannot write | `::test_uninvolved_member_cannot_write` (403, unchanged) | passing |
| No leak across workspaces | `::test_branches_stay_inside_their_workspace` (member of the other workspace refused by id) | passing |
| Provenance round-trips | `::test_contribution_provenance_round_trip` (author, Branch, source, tool/model, history exact) | passing |
| Unauthenticated request | `::test_unauthenticated_request_is_unauthorized` (401, extra beyond the spec) | passing |
| Mapping rule (unit) | `tests/unit/branches/test_mapping.py` (4 cases) | passing |
| Propose rule (unit) | `tests/unit/branches/test_propose.py` (13 cases) | passing |
| Access rule (unit) | `tests/unit/branches/test_access.py` (11 cases) | passing |

Command: `TEST_DATABASE_URL=… uv run pytest tests/integration/test_branches.py tests/unit/branches -q` → 46 passed (18 integration, 28 unit).
Full suite (`make verify`, integration skipped without a database URL): 263 passed, 92 skipped, 2 deselected, plus Ruff, formatting, strict Mypy on the domain, `pnpm lint`, `pnpm typecheck`, the FR/EN locale gate and the design-token gate all green.

## Boundary evidence

- OpenAPI export: `make contract` regenerated `contracts/openapi.json` and the TypeScript client. Diff review: 0 operations removed, 6 added (`list_branches`, `create_branch`, `get_branch`, `propose_contribution`, `list_contributions`, `confirm_contribution`); 0 paths removed, 4 added; 46 → 52 operations.
- Migration `e8b4d6f2a937` applied cleanly on the disposable database; `alembic check` reports no drift (after the two findings below were fixed).
- Strict Mypy includes `apps/api/src/modules/branches/domain` (Makefile + CI).
- Permissions are proved by PostgreSQL integration tests, not browser tests.
- Vocabulary recorded: `apps/api/CONTEXT.md` (exploration `Branch` vs iteration `branch`, canonical `Contribution`, mapping note) and `docs/05-data-model.md`.

## Review findings applied

Two-axis review before commit; both findings were fixed rather than deferred:

- The `Branch.title` and `Contribution.title` columns were `Text()` in the migration but bare `Mapped[str]` (String) in the model; `alembic check` caught the drift and the migration now uses `String()` like the Idea title.
- The `created_by` and `author_id` model FKs were missing `ondelete="CASCADE"` while the migration specified it; the model now declares it, so the ORM and the database agree on delete behavior.

## Known gaps

- None. The implementation tasks are complete; the deferred items in the proposal (Converge consumption, screens, Idea path removal, public Ideas, Outcome/Learning re-parenting) belong to their own steps.
