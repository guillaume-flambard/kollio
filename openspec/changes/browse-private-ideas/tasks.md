## 1. Contract and access control

- [x] 1.1 Add a failing HTTP integration test for member workspace discovery and verify it fails before implementation.
- [x] 1.2 Implement workspace discovery with membership roles and verify the new integration test passes.
- [x] 1.3 Add a failing HTTP integration test for paginated workspace idea browsing and non-member isolation, then verify it fails before implementation.
- [x] 1.4 Implement bounded, deterministic workspace idea listing and verify the integration tests pass.

## 2. Generated client and web seam

- [x] 2.1 Export OpenAPI and regenerate the TypeScript client with the locked CLI, then verify the generated drift check is clean.
- [x] 2.2 Add authenticated Nuxt server routes for workspace discovery and idea listing, then verify typecheck succeeds.

## 3. Localized product interface

- [x] 3.1 Add the authenticated workspace dashboard and pagination using existing design tokens, then verify the local page renders the imported ideas.
- [x] 3.2 Add the localized idea detail page and verify navigation from a list item preserves the active locale.
- [x] 3.3 Update the public landing action and navigation for signed-in users, then verify sign-in lands on the workspace experience.
- [x] 3.4 Add matching FR/EN catalog keys and verify ESLint reports no literal UI text or locale-key drift.

## 4. Delivery

- [x] 4.1 Run Ruff, formatting, Mypy, all Pytest suites, ESLint, Nuxt typecheck, OpenSpec strict validation and the production build.
- [x] 4.2 Validate the authenticated local flow in a browser, including list pagination, idea detail and workspace isolation.
- [x] 4.3 Land the change through a reviewed pull request with green CI and verify the deployed health checks.
