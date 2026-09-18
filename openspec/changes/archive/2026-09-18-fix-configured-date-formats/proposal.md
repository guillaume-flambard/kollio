# Use the configured date formats

## Why

`apps/web/i18n/i18n.config.ts` declares `datetimeFormats` (`short`) and `numberFormats` (`decimal`) that nothing calls: `rg` finds no `$d`, `$n`, `d()` or `n()` anywhere in `apps/web/app`, and the two blocks are referenced nowhere else in `apps/web` (the only other `decimal` hits are `inputmode="decimal"` attributes in the experiment screen). Meanwhile nine pages build the same `Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'long', year: 'numeric' })` themselves, and a tenth builds an `Intl.RelativeTimeFormat`, so the format the product shows is not the format the configuration declares. Changing a locale format therefore needs nine edits, and the declared formats can drift untested. The audit recorded this as I18N-3 in `.agents/skills/ux-flow-auditor/evidence/i18n-report.md`.

## What Changes

- `apps/web/i18n/i18n.config.ts` declares the format the product actually shows: a `long` date format (`{ day: 'numeric', month: 'long', year: 'numeric' }`) in French and English. The unused `short` date format and the whole `numberFormats` block go, because nothing formats a number through the catalog and `style: 'decimal'` is the runtime default.
- A new composable `apps/web/app/composables/useFormatters.ts` exposes `formatDate`, built on vue-i18n's `d()`, and `formatRelative`, which keeps the day and hour arithmetic and the `Intl.RelativeTimeFormat` in one place instead of ten.
- Nine pages drop their local formatter and call the composable, keeping their local helper names (`dateLabel`, `deadlineLabel`) so templates and specs do not move.
- `const { t, locale } = useI18n()` becomes `const { t } = useI18n()` in those files, since `locale` was only read to build the formatter.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vocabulary`: add a requirement that visible dates render through the configured locale formats, so one configuration edit moves every date.

## Impact

`apps/web/i18n/i18n.config.ts`, a new `apps/web/app/composables/useFormatters.ts`, and nine pages: `workspace/index.vue`, `workspace/ideas/index.vue`, `workspace/ideas/[ideaId].vue`, `workspace/people/[userId].vue`, `workspace/decision-spaces/index.vue`, `workspace/decision-spaces/[spaceId].vue`, and the `[spaceId]` sections `learning.vue`, `explore.vue` and `decision.vue`. No contract, migration, database, API or dependency change: the rendered date keeps the same shape, so the existing browser assertions on the long form are the equivalence proof.

## Out of Scope

- Changing what a date looks like: the new `long` format renders exactly what the pages render today.
- Formatting numbers through the catalog with `n()`, since no screen shows a number that needs locale grouping; the decimal block is removed rather than left dead.
- Rewording the relative date, and touching the timeline view type, which already takes `formatDate` as a parameter.
