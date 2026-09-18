# Design - localize the not-found screen

## Context

`apps/web/app` has no `error.vue` and `apps/web/nuxt.config.ts` sets no error handling, so the application ships the framework's default error page. Two mechanical facts shape the fix.

The browser suite runs the fixture at `apps/web/tests/browser/fixture`, whose configuration is `extends: ['../../../']` with `srcDir` pointing at the real `apps/web/app`. A screen added there is served by the suite with no fixture change.

While an error is rendered the application render is replaced, so `app.vue` and the `useLocaleHead` it carries do not run. The document language has to be set by the error screen itself, or the page ships without one. This is the same class of defect the accessibility audit raised elsewhere, where a rendered page advertised the wrong language.

The public layout (`apps/web/app/layouts/default.vue`) is the style reference: brand link, `--ui-bg` and `--ui-text` shell, language switch through `switchLocalePath`, focus ring on `--kollio-connector`, 44 pixel targets. It is not reused because it awaits `useFetch('/api/session')` before rendering, which is a poor dependency for a screen shown when something already failed.

## Goals / Non-Goals

**Goals:**

- A visitor on an unknown path reads an actionable screen in their own locale, with the brand, the status code and a way back to the landing.
- Any other status reuses the same shell with its own words, so a not-found sentence never appears on a server fault.
- The document language is the reader's locale.
- A browser scenario fails if the screen regresses to the framework default.

**Non-Goals:**

- Redirecting, or suggesting a close path.
- Replacing the framework's error plumbing with a Nitro handler.
- Reworking the authenticated screens or their error states.
- Closing the advisory accessibility findings.

## Decisions

### Let the framework render the screen rather than a server handler

`app/error.vue` catches both server-rendered failures and client-side navigation failures, and it is the supported seam, so the fix stays one file. A Nitro route would re-implement what the framework already does and would miss errors raised while the router moves between pages.

### One screen, two key families

The 404 reads `errors.notFound.*` and everything else reads `errors.generic.*`. A single family with an interpolated status would force one sentence to serve both, and a reader whose request failed should not be told the page does not exist. The cost is three keys per locale.

### Set the document language here, from the locale configuration

The screen calls `useLocaleHead({ seo: true })` exactly as `app.vue` does, so the language comes from the locale entries in `nuxt.config.ts` rather than a second hardcoded pair. A hand-written language map would drift the day a locale is added.

### Assert the rendered screen, not the status code

A 404 was already a 404 while the screen was the framework's, so asserting the status would have passed against the defect. The regression asserts what the reader sees: heading, document language and the target of the action.

## Migration Plan

1. Add the six keys to both catalogs, before the `language` block, keeping parity.
2. Add `apps/web/app/error.vue`.
3. Add the browser scenario, then confirm it fails against the framework page by temporarily renaming `error.vue`.
4. Run the gates, the build and the browser suite, then read the deployed screen after the push.

Rollback is a revert of the commit. No data, contract or runtime state is involved.
