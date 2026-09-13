## Decision

See `docs/decisions/0001-scenario-led-delivery.md`. Extend the real Nuxt app from an
isolated browser fixture with SSR disabled. Simulate only application API URLs;
asset/module requests must reach the dev server. Reuse existing Playwright and
Vitest dependencies. Keep PostgreSQL integration tests as access-control evidence.

## Verification

Run lint, types, component tests, browser scenarios, backend tests/evaluations and
build. Inspect GitHub branch protection separately. Report limits explicitly.
