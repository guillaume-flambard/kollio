# Private idea browsing acceptance

This is the first delivery-workflow pilot. Scenario names below refer to
`specs/workspace-idea-browsing/spec.md`. IDs identify the executable browser checks.

| Scenario | Evidence |
| --- | --- |
| Authenticated member requests workspaces | `apps/api/tests/integration/test_foundations.py::test_member_discovers_only_their_workspaces` |
| Member browses a populated workspace | Same file: `test_member_browses_only_their_workspace_ideas`; browser BROWSE-02 |
| Non-member browses a workspace | Same integration test checks membership isolation |
| Member opens an idea | Browser BROWSE-01 |
| Member browses an empty workspace | Browser BROWSE-03 |
| Member requests an inaccessible idea | Browser BROWSE-04 checks presentation; `test_http_workspace_isolation` checks access control |
| User browses in French / English | BROWSE-01 through BROWSE-04 each run in both locales |
| Unauthenticated user requests workspaces | `apps/api/tests/unit/test_http.py::test_unauthenticated_idea_request_is_localized` (includes workspace endpoints) |

Browser file: `apps/web/tests/browser/workspace-browsing.spec.ts`.
Run `pnpm test:browser`. Run `pnpm test:ui` for the existing component suite.

## Scope of proof

The browser fixture extends the real Nuxt app, disables SSR and supplies simulated
API responses. It tests navigation, pagination, empty/error outcomes and locale
preservation, without credentials or live data. It does not validate Logto,
server-side rendering, Nuxt-to-FastAPI authentication or PostgreSQL persistence.
Backend integration tests must pass separately on a disposable database. A real
authenticated smoke check remains required before claiming the entire deployed
journey is verified. Delivery task 4.3 remains open until review, merge and deployed
health verification actually occur.

## Pilot run

On 2026-09-13, all 8 browser checks passed in Chromium. BROWSE-02 first failed
in both locales because Previous retained page=2; clearing that query parameter
fixed the behavior. All 54 non-live backend tests passed, including PostgreSQL
integration checks. See `../enforce-delivery-workflow/acceptance.md` for commands,
verification limits and the GitHub merge-enforcement limitation.
