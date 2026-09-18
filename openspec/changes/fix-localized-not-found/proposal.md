# Localize the not-found screen

## Why

A visitor who mistypes a path never meets Kollio. On 2026-09-18, `https://kollio.memolabs.dev/nope` returned **HTTP 404 with 16,639 bytes of `text/html`**, and `/en/nope` returned **16,674 bytes**, both under a plain `Accept: */*` and under a browser `Accept` header. The body is Nuxt's default error page: its title reads `404 - Page not found: /nope | Nuxt`, it carries no Kollio brand, no navigation and no way back, and **its text is English whichever locale prefix the reader used**, so a French reader and an English reader see the same English screen.

This is the JOURNEY-1 finding of the production journey audit (`.agents/skills/ux-flow-auditor/evidence/journey-report.md`), the only public dead end that audit reached. The audit captured a raw JSON body at the time; the re-measurement above shows the deployed build answers with the framework's HTML error page instead, so that one detail of the finding has moved, but the finding itself stands: the product is bilingual by contract, the landing promises a private space that looks cared for, and a stranger who lands on a wrong path gets none of it.

## What Changes

- Add `apps/web/app/error.vue`, a standalone error screen that carries the Kollio brand, the status code, a localized heading, a localized description, a primary action back to the landing and the existing language switch. The public layout is not reused because it awaits `/api/session` before it renders, which is a risk to take while something has already gone wrong.
- Add six keys to each catalog, `errors.notFound.title/description/action` and `errors.generic.title/description/action`, so a 404 and any other status read differently and neither ever renders a translation path.
- Set the document language on the error screen itself. `app.vue` carries the `useLocaleHead` that sets `htmlAttrs.lang`, and the error screen replaces the application render, so without this the page would ship without a language.
- Add a browser regression that opens an unknown path in both locales and asserts the localized heading, the way back and the document language, so the screen cannot quietly regress to the framework default.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `b2b-product-landing`: add a requirement that a visitor who reaches an unknown path gets a localized not-found screen with a way back, so the public surface never ends in a framework page.

## Impact

- `apps/web/app/error.vue`: new file.
- `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`: six keys each, kept at parity.
- `apps/web/tests/browser/not-found.spec.ts`: new browser scenario.

No contract, migration, database or API change. Adds no dependency and no secret. The dated audit report keeps its finding; the change's `acceptance.md` records what this work replaces.

## Out of Scope

- Suggesting a close match or redirecting an unknown path onto a real screen.
- Reworking server-fault handling beyond the same shell and its generic keys.
- Editing the dated audit reports or adding a coverage row for a surface the journey audit already reached.
- The advisory accessibility findings: the two navigation landmarks that share a name, the settings save confirmation that is not announced, and the profile page that carries no first-level heading.
