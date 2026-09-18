# Acceptance evidence - fix-localized-not-found

The public journey audit recorded JOURNEY-1: an unknown path answered with the framework's
own error page, in English whatever the locale prefix, with no Kollio surface and no way
back. The 2026-09-18 re-measurement showed HTML instead of the raw JSON the audit had
captured, but the finding held: `/nope` and `/en/nope` both rendered a page titled
`404 - Page not found: /nope | Nuxt`. This change adds `apps/web/app/error.vue`, six keys
per catalog (`errors.notFound.*` and `errors.generic.*`, catalogs going from 1007 to 1013
keys), and a browser scenario that fails against the framework page, so a visitor who
mistypes a path is answered in their own language with a way back. The dated audit report
keeps its original finding; this file records what replaced it.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A French reader mistypes a path | `NOT-FOUND-01` in the `fr` locale opens `/no-such-page` and asserts `lang="fr-FR"`, the `h1` equal to `errors.notFound.title`, the visible description and the primary action named `errors.notFound.action` pointing at `/` | Passing |
| An English reader mistypes a path | `NOT-FOUND-01` in the `en` locale opens `/en/no-such-page` with the same assertions in English, the action pointing at `/en` | Passing |
| A server fault uses the same screen | Source-only. `apps/web/app/error.vue` branches on `statusCode === 404` for the heading, description and action, and falls back to `errors.generic.*` for any other status, which no browser scenario reaches | Passing (source-only) |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- `https://kollio.memolabs.dev/`: HTTP 200, 65 945 bytes.
- `https://kollio.memolabs.dev/no-such-page`: HTTP 404, `text/html`, 13 947 bytes, `lang="fr-FR"`,
  title `Cette page n'existe pas · Kollio`, a link back to `/` labelled `Revenir à l'accueil`, and
  no raw key path anywhere in the response.
- `https://kollio.memolabs.dev/en/no-such-page`: HTTP 404, `text/html`, 13 942 bytes, `lang="en-GB"`,
  title `This page does not exist · Kollio`, a link back to `/en` labelled `Back to home`, and no
  raw key path.
- The deploy needed a companion fix in `lab-infra` (PR #83, merged as `8157414`): the `kollio-web`
  health probe allowed 5 s while spawning `node` took about 6 s under memory pressure, so the
  container stayed unhealthy and Traefik dropped its route, which took the whole domain down to the
  default gateway 404 for a few minutes. The probe now allows 30 s, retries 5 and starts after 120 s.

Local, before deploy:

- `pnpm lint`: clean.
- `pnpm typecheck`: clean.
- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1013 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.`
- `node scripts/check_design_tokens.mjs`: `apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: build complete.
- Counter-check (task 2.2): with `apps/web/app/error.vue` temporarily renamed away, `pnpm --dir apps/web exec playwright test not-found.spec.ts` reports `2 failed`, one per locale, so the scenario fails against the framework's error page and passes against the new screen.
- `pnpm --dir apps/web exec playwright test`: `322 passed (13.4m)`, which includes the two NOT-FOUND-01 runs, one per locale.

## Known boundaries

- The full suite runs against simulated API responses on the browser fixture, so it proves what the browser renders for an unknown path, not routing, hosting or cache behaviour behind it.
- The same screen answers every status; a 500 path is exercised only by source, and the acceptance table says so rather than implying a rendered check.
- Contrast, focus order and screen-reader naming of the new screen were not measured in this change; the accessibility audit covered the six product screens and did not include the error screen.
- Nuxt's default error page remains the fallback if `error.vue` is removed or fails to load, which is how the counter-check reproduced the original finding.
