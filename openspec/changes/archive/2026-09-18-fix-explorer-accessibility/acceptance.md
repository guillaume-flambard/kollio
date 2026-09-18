# Acceptance evidence - fix-explorer-accessibility

The idea explorer at `/workspace/ideas` failed two accessibility checks recorded in `.agents/skills/ux-flow-auditor/evidence/a11y-report.md`: the search field had no accessible name (A11Y-1, WCAG 4.1.2 level A) and the page rendered a second `<main>` inside the layout's `<main>` (A11Y-2, WCAG 1.3.1 level A). This change names the field through a dedicated catalog key and turns the results container into a `div`, with a browser scenario that fails against the previous markup. The dated audit report stays as the record of what was found.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A member reaches the explorer with a screen reader | `EXPLORER-08` in `apps/web/tests/browser/explorer.spec.ts` asserts a single `main` landmark on `/workspace/ideas`; the audit probe recorded the nested pair before the fix (`mains: [{id: "main", nested: false}, {id: "", cls: "ideas-results", nested: true}]`) | Passing |
| The search field is named in French | `EXPLORER-08` in the `fr` locale resolves `getByRole('searchbox', { name: 'Rechercher une initiative' })` from the catalog key `ideas.explorer.searchLabel` | Passing |
| The search field is named in English | `EXPLORER-08` in the `en` locale resolves `getByRole('searchbox', { name: 'Search for an initiative' })` from the same key | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- Deployed and observed. The `3c358e0` build reached production on 2026-09-18: the `kollio-web` container was recreated at 15:29:47Z, started at 15:30:38Z and reported healthy, and `grep -rl ideas.explorer.searchLabel /app/.output/public/_nuxt` inside the running container returned `_nuxt/COM01a2j.js`, so the served bundle carries the named search field. The single main landmark follows from the same source change, whose rendered effect was measured locally.

Local, before deploy:

- `pnpm lint`: clean.
- `pnpm typecheck`: clean.
- `node scripts/check_locales.mjs`: `FR/EN translation keys match, and all 1023 catalog keys cover their usages.`
- `node scripts/check_design_tokens.mjs`: `apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: build complete.
- Counter-check (task 3.2): with `apps/web/app/pages/workspace/ideas/index.vue` stashed and the two catalogs kept, `pnpm --dir apps/web exec playwright test explorer.spec.ts` reports `2 failed, 6 passed`. Both failures are EXPLORER-08, one per locale, on the accessible name of the field. The landmark assertion is not reached because the name assertion fails first; the defect it targets was measured directly by the audit probe.
- `pnpm --dir apps/web exec playwright test`: `330 passed (14.3m)`, which includes the two EXPLORER-08 runs, one per locale.

## Known boundaries

- The browser suite runs against simulated API responses, so it proves what the browser renders, not authentication, authorization or persistence.
- The two locale scenarios differ only by the catalog and the URL prefix; the component behaviour is shared.
- A11Y-3 and A11Y-5 of the audit report stay open on purpose: the adversarial review records them as advisory rather than conformance failures.
- The audit report and the coverage register keep their original dates; this change does not rewrite them.
