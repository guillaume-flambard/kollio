# Acceptance evidence - fix-profile-role-labels

The person profile and the explorer expertise badge resolved role labels through `ideas.role.*`, a seven-key family inherited from the pre-pivot vocabulary (`owner`, `designer`, `dev`, `commercial`, `growth`, `data`, `product`). The API serves the current closed vocabularies instead: a person's craft roles come from `User.roles` (`product`, `strategy`, `design`, `research`, `engineering`, `platform`, `ai`, `data`, `growth`, `sales`, `operations`, `finance`) and a membership carries a business function from `BUSINESS_FUNCTIONS_SQL`. Every value outside the legacy seven therefore rendered as its key path (`ideas.role.engineering`, `ideas.role.platform`). The three call sites now read the families that own their vocabulary, and the browser regression asserts the rendered labels with fixture values the legacy family never covered, so a key path can no longer pass unnoticed.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| PRL-01 A profile renders craft roles the legacy vocabulary does not cover | `apps/web/tests/browser/profiles.spec.ts` PROFILE-01, fr and en: `.profile-roles li` renders `[roleLabels.engineering, roleLabels.platform]` (`['Développement', 'Plateforme']` and `['Engineering', 'Platform']`), and `.profile-roles` never contains `ideas.` | Passing |
| PRL-01 A profile renders a membership's business function | Same file, PROFILE-01: the strong element of the second `.profile-section` renders `functions.finance` (`Finance`) through `ideas.function.*` | Passing |
| PRL-01 An explorer row renders a collaborator's craft role | Same file, PROFILE-02, fr and en: `.explorer-row-topics` contains `roleLabels.platform` (`Plateforme` / `Platform`) and never contains `ideas.` | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:
- Nothing is recorded yet. This change carries its own commit and no deploy has been made, so `kollio.example.com` still serves the pre-fix build. The deploy and a production read of the profile page belong in the delivery comment on the commit, not here.

Local, before deploy:
- `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 1022 catalog keys cover their usages.` (down from 1029 after the seven legacy keys left both catalogs in step).
- `pnpm lint` (`eslint .`) → clean.
- `pnpm typecheck` (`nuxt typecheck`) → clean.
- `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs` → `coverage: ok`
- `pnpm build` → `Σ Total size: 5.6 MB (1.45 MB gzip)`, `Build complete!`
- `pnpm --dir apps/web exec playwright test` → `328 passed (19.4m)`, including PROFILE-01 and PROFILE-02 in fr and en.
- Counter-check for task 2.3: with the three call sites temporarily restored to `ideas.role.*` (the catalogs already stripped of those keys, which is the original defect), `pnpm --dir apps/web exec playwright test profiles.spec.ts` → `4 failed`, and the rendered pages carried the raw key paths again (eight occurrences of `ideas.role` in the run log). The regression fails against the defect and passes against the fix.

## Known boundaries

- The browser suite runs against a development server with simulated API responses, so it proves the rendered UI only: not authentication, not backend authorization, not persistence.
- The label vocabulary is not checked against the API's closed vocabularies in CI. `scripts/check_locales.mjs` verifies that a constructed key's prefix exists in the catalogs, not that every value the API can serve has a label. A new role or function value without a label would surface as a key path again.
- Participation values (`owner`, `decision_maker`, `contributor`, `observer`) still have no label family. Nothing renders them through `t()` today, so nothing is broken; they are noted because this change is the same class of defect already realised once.
- The suite total of 328 includes `apps/web/tests/browser/a11y-audit-tmp.spec.ts`, a temporary file committed earlier by the i18n audit. This change leaves it untouched.
