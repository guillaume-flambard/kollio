# Design - use the configured date formats

## Context

`apps/web/i18n/i18n.config.ts` declares `datetimeFormats.short` and `numberFormats.decimal`, and neither is called anywhere in `apps/web`: the only other occurrences of the word `decimal` are `inputmode="decimal"` attributes in `apps/web/app/pages/workspace/decision-spaces/[spaceId]/experiment.vue`. The configuration itself is loaded: `apps/web/nuxt.config.ts` points `vueI18n` at `./i18n.config.ts`, which `@nuxtjs/i18n 10.6.0` resolves to `apps/web/i18n/i18n.config.ts` (the dev module map holds that id, and the dev bundle carries `datetimeFormats` twice). Ten call sites build their own formatter: nine pages with `new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })` (in `workspace/index.vue`, `workspace/ideas/[ideaId].vue`, `workspace/people/[userId].vue`, `workspace/decision-spaces/index.vue`, `workspace/decision-spaces/[spaceId].vue`, and the `[spaceId]` sections `learning.vue`, `explore.vue` and `decision.vue`), plus `workspace/ideas/index.vue`, which adds an `Intl.RelativeTimeFormat`. `apps/web/app/utils/timeline.ts` already takes `formatDate` as a `(iso: string) => string` parameter, so a shared function drops into that seam without a type change.

## Goals / Non-Goals

**Goals:**
- The date format the product shows lives in the i18n configuration and is actually used.
- One place defines the relative wording and the day arithmetic.
- The rendered output does not change, so the existing browser suite proves equivalence without a single assertion edit.
- No dead configuration is left behind.

**Non-Goals:**
- Changing the visible shape of a date.
- Formatting numbers through the catalog.
- Rewording the relative date.
- Touching the timeline types.

## Decisions

### Declare `long`, not `short`

The pages render a long month today, and the specs assert it (`new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'long', year: 'numeric' })`, for instance in `apps/web/tests/browser/profiles.spec.ts`). The new format keeps those options, so the suite stays green with no assertion change and becomes the equivalence proof. Reusing `short` would have moved every visible date, which is not what this change is for.

### Remove the formats nothing calls

`short` and `numberFormats` are declared and never used. Keeping them would repeat the defect this change closes, so they go. If a screen ever needs a number format, it declares one and calls `n()`; a declared format nothing calls is how the drift started.

### One composable, keeping the local helper names

`useFormatters()` returns `formatDate` and `formatRelative`. Pages keep their `dateLabel` and `deadlineLabel` helpers and call the composable inside, so templates and specs do not move and the diff stays about the format. The composable follows the house shape already used by `useDrawer`, `useInitiativeTypeOptions` and `useSourceDisplayName`: a plain `export function`, auto-imported, no explicit Nuxt or Vue imports.

### `d()` for absolute dates, `Intl` for the relative one

vue-i18n formats dates but has no relative formatter, so the relative wording stays on `Intl.RelativeTimeFormat`, centralized in the composable rather than repeated in a page.

## Migration Plan

1. Declare the `long` format and drop the dead blocks; the locale guard and the design token guard still pass.
2. Add `useFormatters.ts`.
3. Convert the ten sites and drop the now unused `locale` from each `useI18n()` destructuring.
4. Run lint, types, the guards, the build and the browser suite.

Rollback: revert the commit. Only rendering moves, and no data, contract or dependency changes.
