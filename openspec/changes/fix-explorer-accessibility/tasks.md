# Tasks - fix-explorer-accessibility

## 1. Name the search field

- [x] 1.1 Add `ideas.explorer.searchLabel` to `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`
- [x] 1.2 Apply the key as `aria-label` on the search input in `apps/web/app/pages/workspace/ideas/index.vue`

## 2. Restore a single main landmark

- [x] 2.1 Turn the page's `<main class="ideas-results">` into `<div class="ideas-results">`, with its closing tag

## 3. Regress the two defects

- [x] 3.1 Add the EXPLORER-08 scenario to `apps/web/tests/browser/explorer.spec.ts`, for both locales
- [x] 3.2 Confirm the scenario fails against the previous markup

## 4. Close with evidence

- [x] 4.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens` and `check_ux_coverage`
- [x] 4.2 Run `pnpm build` and the browser suite
- [x] 4.3 Write `acceptance.md` with the scenario-to-evidence mapping
