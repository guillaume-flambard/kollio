## Why

Authenticated users currently return to the marketing page and cannot inspect the private ideas already imported into their workspace. The first product slice must turn the completed identity and data foundations into a useful, workspace-isolated browsing experience.

## What Changes

- Add an authenticated workspace dashboard that summarizes the current private workspace.
- Add a paginated idea list ordered by most recently created, with stage and source-language metadata.
- Add an idea detail page reachable from the list.
- Enforce workspace membership on list and detail access without exposing whether inaccessible records exist.
- Preserve FR/EN UI localization and the original language of idea content.
- Extend the generated OpenAPI client and Nuxt server routes for the new endpoints.

## Capabilities

### New Capabilities

- `workspace-idea-browsing`: Authenticated members can browse and inspect ideas belonging to their private workspace.

### Modified Capabilities

None.

## Impact

The change affects the `ideas` vertical slice, FastAPI routes and schemas, the generated OpenAPI contract and client, Nuxt pages and translation catalogs. It uses the existing PostgreSQL models, Logto identity mapping and design tokens without introducing new infrastructure or dependencies.
