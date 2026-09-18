# Acceptance evidence - fix-configured-date-formats

`apps/web/i18n/i18n.config.ts` declared `datetimeFormats.short` and `numberFormats.decimal`, and nothing called either of them: there is no `$d`, `$n`, `d()` or `n()` anywhere in `apps/web/app`, and the two blocks were referenced nowhere else in `apps/web`. Meanwhile nine pages built the same `Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })` and a tenth built an `Intl.RelativeTimeFormat`, so changing a locale format meant nine edits and the declared formats could drift without a single test. This change declares the format the product actually shows (a `long` date format for each locale), removes the formats nothing calls, adds `apps/web/app/composables/useFormatters.ts` (`formatDate` through the `d()` of vue-i18n, `formatRelative` holding the relative arithmetic and the formatter in one place), and converts the ten call sites to it.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A page shows a date | The nine pages now render creation, update and deadline dates through the composable's `formatDate`, which resolves `d(value, 'long')`. The browser suite keeps its long-form assertions unchanged, for example `apps/web/tests/browser/profiles.spec.ts` compares the rendered time to `new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'long', year: 'numeric' })`, and `pnpm --dir apps/web exec playwright test` is green. | Passing |
| The configured format changes | The format lives once per locale in `apps/web/i18n/i18n.config.ts`, and `rg -n 'Intl\.' apps/web/app` returns a single hit, inside `apps/web/app/composables/useFormatters.ts`, so no page holds its own date format any more. | Passing |
| No dead format is declared | The `short` format and the whole `numberFormats` block were removed, and the only declared format, `long`, is the one `formatDate` reads. | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- Not observed yet. The change is committed locally only, the deployed build predates it, and the rendered date form is unchanged by design, so the deployed read belongs to the delivery comment.

Local, before deploy:

- `pnpm lint`: clean.
- `pnpm typecheck`: clean.
- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1013 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.`
- `node scripts/check_design_tokens.mjs`: `apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: build complete.
- `pnpm --dir apps/web exec playwright test`: `322 passed (15.2m)`, which includes the two EXPLORER-08 runs, one per locale. It covers the ten converted call sites and the existing long-form date assertions.

## Known boundaries

- The browser suite runs against the fixture app with simulated API responses, so it proves what the browser renders for those payloads, not the API, the authorization or the persistence.
- The rendered text is deliberately unchanged: the declared `long` options are identical to the ones the pages used, so the equivalence evidence is the options themselves plus the untouched long-form assertions, not a new golden-file comparison.
- The relative formatter moved unmodified, including its day and hour rounding, and no scenario asserts the exact text of a relative label.
- Numbers keep no catalog format: `numberFormats` was removed rather than exercised, so introducing a numeric format later is a new decision rather than a leftover.
