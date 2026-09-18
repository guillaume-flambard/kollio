# Acceptance evidence — workspace-idea-browsing

Landed as PR #6 (`browse-private-ideas`), merged 2026-09-12 as `9f13572`.
Re-verified on `main` 2026-09-15 against an isolated pgvector database.

| Spec scenario | Evidence |
| --- | --- |
| Authenticated member requests workspaces | `test_member_discovers_only_their_workspaces` (integration, Postgres) |
| Unauthenticated user requests workspaces | `test_unauthenticated_idea_request_is_localized` (unit) + JWT claim tests in `test_identity_validates_all_security_claims` |
| Member browses a populated workspace (ordered, paginated) | `test_member_browses_only_their_workspace_ideas` + `test_list_orders_by_recent_activity_with_fallback` + `test_workspace_idea_page_has_constant_query_count_and_latency` |
| Member browses an empty workspace | `test_member_browses_only_their_workspace_ideas` empty-workspace path + EXPLORER browser empty-state cases |
| Non-member browses a workspace (404, no disclosure) | `test_http_workspace_isolation` + `test_member_browses_only_their_workspace_ideas` non-member path |
| Member opens an idea (title, pitch, stage, lang, date) | `test_deposit_creates_private_idea_with_initial_iteration` + `idea-detail-states` UI tests + EXPLORER browser detail navigation |
| Inaccessible idea request (404, no disclosure) | `test_http_workspace_isolation` + `get_idea` non-member 404 path |
| Browsing in French, content unchanged | `check_locales.mjs` FR/EN parity + `EXPLORER-0x` browser suite run in `fr` locale + `test_locale_negotiation` |
| Browsing in English, content unchanged | Same as above, `en` locale branch |

## Verification runs (2026-09-15, isolated `kollio_test` on pgvector)

- Alembic `upgrade head` + `alembic check`: clean, no drift.
- `pytest -m 'not live'`: 170 passed, 2 deselected (live opt-in only).
- Ruff check + format check + strict Mypy (ideas, iterations, constraint_analysis, profiles, company_context domains): clean.
- `pnpm lint`, `pnpm typecheck`: exit 0. `check_locales.mjs`: FR/EN keys match. `check_design_tokens.mjs`: canonical tokens only.
- Vitest UI suite: 9 files, 32 tests passed.
- Contract: `export_openapi` hash unchanged, `generate:client` produces no diff.
- `pnpm build` + `check_web_performance_budgets.mjs`: pass (JS 10.7%, CSS 14.4%, images 0.4%).
- CI `Foundations CI` on `main`: success (runs 34906527316, 34905144487, 34903671578, 34901277882, 34899597676).
- Deployed: `https://kollio.example.com/api/health` returns `{"status":"ok"}`; landing returns HTTP 200. Prod runs merge commit `9f13572`.

## Known boundaries

- Playwright browser specs simulate API responses; they prove UI behavior only, not backend authorization. Authorization is proven by the Postgres integration tests above.
- Authenticated end-to-end browser sign-in against production Logto is a manual smoke check, not part of automated CI.
- Branch protection requiring the `verify` job is not enforceable on this private repository without GitHub Pro (HTTP 403 on 2026-09-13); merge discipline is procedural until then.
