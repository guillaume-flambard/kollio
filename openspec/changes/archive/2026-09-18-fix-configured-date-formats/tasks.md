# Tasks - fix-configured-date-formats

## 1. Declare the format the product shows

- [x] 1.1 Replace the unused `short` date format and the `numberFormats` block in `apps/web/i18n/i18n.config.ts` with a `long` date format for French and English
- [x] 1.2 Add `apps/web/app/composables/useFormatters.ts` exposing `formatDate` through `d()` and `formatRelative`

## 2. Convert the call sites

- [x] 2.1 `workspace/index.vue`, `workspace/ideas/[ideaId].vue` and `workspace/people/[userId].vue`
- [x] 2.2 `workspace/ideas/index.vue`, which formats a relative date
- [x] 2.3 The decision space screens: `decision-spaces/index.vue`, `decision-spaces/[spaceId].vue` and the `[spaceId]` sections `learning.vue`, `explore.vue` and `decision.vue`
- [x] 2.4 Drop `locale` from the `useI18n()` destructuring where it was only there for a formatter

## 3. Close with evidence

- [x] 3.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens` and `check_ux_coverage`
- [x] 3.2 Run `pnpm build` and the browser suite
- [x] 3.3 Write `acceptance.md` with the scenario to evidence mapping
