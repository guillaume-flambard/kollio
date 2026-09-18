# Acceptance evidence - add-public-release

The repository was a private pilot: it had no license, so nobody could legally reuse it, and it had no way for a reader to learn how to run it, propose a change or report a problem. A handful of tracked files also named the operator's infrastructure, which reads badly in a public project and tells a stranger nothing useful. This change carries the license and the community files, orients a newcomer from the README, and replaces the operator's own names with placeholders wherever they are not wired into the deployment.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A reader looks for the license | `LICENSE` holds the Apache-2.0 text (202 lines, header `Apache License, Version 2.0, January 2004`, trailer `END OF TERMS AND CONDITIONS`), and `README.md` states the license in its `## Contribuer` section with a link to `LICENSE`. | Passing |
| A newcomer wants to propose a change | `CONTRIBUTING.md` carries `## Run it locally` (runtimes from `.nvmrc` and `.python-version`, `cp .env.example .env`, generating the two local secrets, `make install`, `services`, `migrate`, `build`, `up`, `make verify`, Chromium for the browser suite, `TEST_DATABASE_URL`, `KOLLIO_RUN_LIVE_EVALS=1`), `## The shape of a change`, `## Commits and sign off` (conventional one-line subjects and the DCO sign-off), `## Reporting` and `## License`; `CODE_OF_CONDUCT.md` carries the Contributor Covenant 2.1 with `g.flambard@gmail.com` as the reporting contact; `SECURITY.md` carries the private disclosure path; `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md` and `.github/PULL_REQUEST_TEMPLATE.md` exist. | Passing |
| A reader opens the example environment | `.env.example` holds only `example.com` hosts (`NUXT_LOGTO_ENDPOINT=https://auth.example.com/`, `LOGTO_ISSUER=https://auth.example.com/oidc`, `LOGTO_JWKS_URL=https://auth.example.com/oidc/jwks`, `LOGTO_AUDIENCE=https://kollio.example.com/api`) and the placeholder `your-logto-app-id`; `rg` over the tree finds no operator host, no server address and no personal home path; the only remaining mentions of the pilot host are the three runtime values left for the separate deployment change (`apps/web/nuxt.config.ts` lines 17 and 28, `apps/web/server/utils/kollio-api.ts` line 4). | Passing |
| An archived record stays readable | In the seven archived `acceptance.md` files, the archived `proposal.md` and the journey audit, only host names changed: status codes, byte counts and commands are untouched, and the journey report carries a note at its head saying the host names became examples while the measurements are the observed ones. | Passing |
| A newcomer opens the repository | `README.md` leads with the product paragraph, keeps `## Ordre de lecture`, states a current `## Statut` (pilot screens delivered, 322 browser tests and 557 API tests green, FR and EN catalogs at parity on 1013 keys, measured 2026-09-18), keeps `## Principe directeur`, adds `## Contribuer` and keeps `## Local foundations`. | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- Not applicable. This change only touches tracked text, a license and community files; it carries no runtime behaviour and deploys nothing, so there is nothing to read on the pilot. The three runtime values that could affect the deployed sign-in flow were deliberately left alone and are named under Known boundaries.

Local, before deploy:

- `rg` for the operator host, the server address, the personal home path, the ssh alias and the identity provider application id over the tracked tree: the pilot host survives only in `apps/web/nuxt.config.ts` and `apps/web/server/utils/kollio-api.ts` (the deployment change), and no server address, home directory path or application id remains anywhere.
- `pnpm lint`: clean.
- `pnpm typecheck`: clean.
- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1013 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.`
- `node scripts/check_design_tokens.mjs`: `apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: build complete.
- `pnpm --dir apps/web exec playwright test`: `322 passed (18.6m)`, which includes the two EXPLORER-08 runs, one per locale.

## Known boundaries

- Three values are wired into the running deployment and were left with the operator's host on purpose: the Logto resource in `apps/web/nuxt.config.ts`, the i18n `baseUrl` fallback in the same file and the API audience in `apps/web/server/utils/kollio-api.ts`. Replacing them here would break the deployed sign-in or the canonical URLs, so they belong to the change that first gives the web app a Logto resource and a public site URL through its environment.
- `scripts/check_private_files.py` still knows nothing about host names. It is extended together with those three values, because it can only go green once the tree is genuinely free of the operator's names.
- Both points above are now closed by the follow-up change, archived under `openspec/changes/archive/2026-09-18-add-configurable-deployment-identity`: it reads the three values from the environment and extends that guard to reject tracked content naming the operator's host or home directory.
- The repository is not public yet and the CI still runs on the self-hosted runner with the local registry; making the repository public and moving the pipeline to hosted runners and a public registry is a separate change.
