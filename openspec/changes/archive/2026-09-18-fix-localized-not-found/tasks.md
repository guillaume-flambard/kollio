# Tasks - fix-localized-not-found

## 1. Add the localized screen

- [x] 1.1 Add `errors.notFound.title/description/action` and `errors.generic.title/description/action` to `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`, keeping parity
- [x] 1.2 Add `apps/web/app/error.vue` rendering the brand, the status code, the localized heading and description, the primary action back to the landing and the language switch
- [x] 1.3 Set the document language from the locale configuration on the error screen

## 2. Regress it

- [x] 2.1 Add the browser scenario for an unknown path in both locales
- [x] 2.2 Confirm the scenario fails against the framework error page

## 3. Close with evidence

- [x] 3.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens` and `check_ux_coverage`
- [x] 3.2 Run `pnpm build` and the browser suite
- [x] 3.3 Write `acceptance.md` with the scenario to evidence mapping
