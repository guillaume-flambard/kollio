# Acceptance: landing-locale-coverage

Every scenario in `specs/b2b-product-landing/spec.md` mapped to the evidence that
closed it, plus the gaps that remain open.

## The landing page copy exists in both catalogs

Requirement: the public page SHALL render localized copy, and no `t()` call in
the landing SHALL fall back to a raw key.

### Scenario: the French landing renders copy

Evidence: production build served locally.

```
pnpm --dir apps/web build
cd apps/web && PORT=3111 node .output/server/index.mjs
curl -s http://localhost:3111/ | grep -o 'landing\.[a-zA-Z.]*'
```

Result: no output, so no key reaches the served HTML. The same response contains
`PENSER ENSEMBLE. CONSTRUIRE ENSEMBLE.` and the French hero title.

### Scenario: the English landing renders copy

```
curl -s http://localhost:3111/en | grep -o 'landing\.[a-zA-Z.]*'
```

Result: no output. The response contains `THINK TOGETHER. BUILD TOGETHER.` and
`An initiative deserves more than`.

Both catalogs carry the same 65 `landing.*` keys: `node scripts/check_locales.mjs`
reports `FR/EN translation keys match, and all 468 catalog keys cover their usages.`

## Every navigation entry resolves to the section it names

Requirement: a navigation entry SHALL land on the section that carries its name.

### Scenario: the method entry reaches the ordered steps

Source evidence (`apps/web/app/pages/index.vue`): the navigation entry links to
`#method`, and `id="method"` sits on `section.landing-method`, which holds the
`capture`, `challenge` and `decide` steps in that order.

### Scenario: the teams entry reaches the outcome benefits

Source evidence: the navigation entry links to `#teams`, and `id="teams"` sits on
`section.landing-outcomes`, which holds the three benefit articles.

Before this change the two identifiers were swapped, so both the method entry and
the hero secondary action landed on the benefits section.

## The locale guard rejects a key that no catalog defines

Requirement: the guard SHALL fail when the web app uses a key that neither
catalog defines.

### Scenario: a static key missing from both catalogs

Evidence: `landing.hero.eyebrow` was removed from `fr.json` and `en.json` only,
then `node scripts/check_locales.mjs` was run.

Result: `missing landing.hero.eyebrow (used in apps/web/app/pages/index.vue)`,
exit code 1. Restoring the key returned the guard to exit code 0. Removing the key
from a single catalog fails earlier on the FR/EN parity assertion, which is the
existing behavior.

### Scenario: a dynamic family is accepted

`t('ideas.function.' + request.business_function)` in
`apps/web/app/pages/workspace/ideas/[ideaId].vue` is reduced to its static prefix
`ideas.function.`. The guard accepts it because catalog entries start with that
prefix, without enumerating the runtime values.

### Scenario: the guard passes when every usage is covered

`node scripts/check_locales.mjs` exits 0 with
`FR/EN translation keys match, and all 468 catalog keys cover their usages.`

## Full verification

- `make verify`: green (`PIPESTATUS=0`). API suite `123 passed, 54 skipped,
  2 deselected`; `pnpm lint`, `pnpm typecheck`, the locale guard and the design
  token guard all pass.
- `pnpm --dir apps/web build`: `Build complete!`, total size 4.97 MB (1.3 MB gzip).

## Known gaps

- The 54 skipped API tests need `TEST_DATABASE_URL`; they cover Postgres
  integration and performance, not this change.
- The served-page check ran against a local production preview, not against the
  deployed site. Re-running
  `curl -s https://kollio.memolabs.dev/ | grep -o 'landing\.[a-zA-Z.]*'` after the
  deploy is the last step.
- GitHub branch protection is still not enforced on this repository (HTTP 403,
  GitHub Pro or a public repository required, rechecked on 2026-09-13), so the
  required checks are green but not mandatory.
- The interactive parts of the project's task 6.5 (browser auth, LangGraph resume
  with the preserved locale, multilingual retrieval in production, Langfuse trace
  ingestion) remain outside this change.
