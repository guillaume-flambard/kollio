## Context

Phase 0 provides Logto authentication, PostgreSQL workspace memberships, 446 imported ideas and one protected idea-detail endpoint. The Nuxt application still renders only the public landing page after sign-in. See `proposal.md` for the product motivation and the capability spec for observable behavior.

## Goals / Non-Goals

**Goals:**

- Deliver one end-to-end vertical slice from authenticated Nuxt pages through generated OpenAPI types to PostgreSQL.
- Keep workspace isolation at the API boundary and preserve the existing indistinguishable not-found behavior.
- Provide stable offset pagination suitable for the current 446-record dataset.
- Reuse the existing design tokens and FR/EN locale routing.

**Non-Goals:**

- Creating, editing, translating, scoring or embedding ideas.
- Iterations, branches, proposals, teams, matching or public exploration.
- A reusable component library or a generic repository abstraction.

## Decisions

### Expose workspace discovery separately from idea listing

`GET /workspaces` returns the authenticated user's memberships. `GET /workspaces/{workspace_id}/ideas` lists ideas within an explicitly selected workspace. This keeps future multi-workspace navigation possible without inventing a global current-workspace preference. Returning an arbitrary current workspace was rejected because it would make selection unstable when a user joins a second workspace.

### Keep simple workspace behavior inside a small vertical module

A `workspaces` module will contain only its PostgreSQL adapter, response schemas and route. It will not receive domain or service layers until workspace behavior requires them. Idea listing remains in the existing `ideas` module. This follows the modular-monolith convention without adding four empty layers.

### Use bounded offset pagination

The list accepts `limit` from 1 to 100 and a non-negative `offset`, returning `total`, `limit` and `offset`. Ordering uses `created_at DESC, id DESC` for deterministic pages. Cursor pagination was rejected for this first 446-record private dataset because it adds contract and UI complexity without a measured need.

### Use Nuxt server routes as the authenticated backend-for-frontend seam

Nuxt server routes obtain the Logto access token and call the generated client-facing API contract. Pages call only same-origin Nuxt endpoints, which keeps tokens out of browser code and preserves SSR. Direct browser calls to FastAPI were rejected because they would expose access-token handling and require separate CORS policy.

### Render dedicated workspace routes

Authenticated users enter `/workspace`; idea details live at `/workspace/ideas/:ideaId`. The marketing page remains public and its primary action routes signed-in users to the workspace. This provides a stable product shell without introducing a full navigation system before more modules exist.

## Risks / Trade-offs

- [Offset pagination can drift when rows are inserted between requests] → Deterministic ordering limits surprises; move to cursors when data size or activity makes drift visible.
- [A user with no memberships has no product destination] → Render a localized empty state with a clear explanation; workspace creation is a later slice.
- [Imported records can contain long pitches] → Truncate summaries visually in the list and show complete content on detail pages.
- [Local Logto identity may not yet map to the imported workspace] → Use the existing idempotent identity-mapping command for local development and keep mapping outside request-time behavior.

## Migration Plan

1. Add the read-only endpoints and tests without changing the database schema.
2. Export OpenAPI and regenerate the TypeScript client with the locked generator.
3. Add Nuxt server routes, localized pages and navigation.
4. Validate with the isolated integration database, production build and an authenticated local browser session.
5. Deploy through the existing GitHub Actions and Make/Ansible path. Rollback requires only reverting the application image because no schema migration is introduced.
