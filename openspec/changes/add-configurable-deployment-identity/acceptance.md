# Acceptance evidence - add-configurable-deployment-identity

The public release left three values that name the operator's host inside the application: the Logto resource list and the i18n base URL in `apps/web/nuxt.config.ts`, and the same resource indicator as an API audience constant in `apps/web/server/utils/kollio-api.ts`. A check that rejects the operator's host in tracked content fails on them, and a clone cannot run the web app without inheriting that host or editing source. Two of the three are read at runtime and must agree, or the mismatch only shows up as a 401 at sign-in; the third is evaluated at image build time and feeds canonical URLs and hreflang tags. This change reads all three from the environment, derives the audiences from the single configured resource, and makes the check enforce the property instead of relying on review. The deployment that supplies the resource lives in the private infrastructure repository, which is why the hosting values stay out of this one.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| A clone runs without the operator's host | `apps/web/nuxt.config.ts` declares `resources: []` and falls back to `http://localhost:3000` for the site URL; `apps/web/server/utils/kollio-api.ts` reads the audience from `runtimeConfig.logto.resources`; `python3 scripts/check_private_files.py --tracked` exits 0 over the whole tracked tree, so no tracked file names the operator's host or home directory. | Passing |
| The resource and the audience agree | The server takes the resource indicator from `runtimeConfig.logto.resources` and passes that same value to `getAccessToken`; there is no second constant to keep in step. | Passing |
| The resource is missing | With no resource configured the server throws `createError({ statusCode: 500, statusMessage: 'No API resource is configured' })` instead of requesting a token for an empty audience. | Passing |
| The guard catches a quoted host | `scripts/check_private_files.py` scans tracked and staged content for the operator's host and home directory, skipping itself, and exits non-zero naming the offending file. Covered by the guard run below. | Passing |

## Verification runs (2026-09-18)

Live, in production, after the deploy:

- The infrastructure half is deployed and observed: `guillaume-flambard/lab-infra` pull request #85 (squash-merged, merge commit `36212d7292d69e8ebc7c832e80e01082e88924c2`) provides `NUXT_LOGTO_RESOURCES=["https://kollio.memolabs.dev/api"]` to the `kollio-web` service, applied with `make deploy-stack app=kollio force=1` (`ok=14 changed=3 failed=0`). The running container reports the variable, is healthy, `https://kollio.memolabs.dev/` answers 200, and `/sign-in` redirects to the identity provider with `resource=https://kollio.memolabs.dev/api`.
- The code half of this change reaches production with the image built from this commit, so at the time of writing the container still runs the previous image, which carries the operator's host in its own bundle and ignores the resource variable. Reading the named resource and the canonical URLs back from the deployed site belongs to the delivery comment; the local evidence below already exercises the same code paths.

Local, before deploy:

- `python3 scripts/check_private_files.py --tracked`: exit 0 (`GUARD=0`).
- `pnpm lint`: clean (`LINT=0`).
- `pnpm typecheck`: clean (`TC=0`).
- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1013 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.`
- `node scripts/check_design_tokens.mjs`: `Design tokens: apps/web/app uses only canonical tokens.`
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: build complete (`BUILD=0`), run without `NUXT_PUBLIC_SITE_URL` so the site URL took its local fallback, which is the intended behaviour for a build that is not production.
- `pnpm --dir apps/web exec playwright test`: `322 passed (18.3m)`.

## Known boundaries

- The resource that makes the deployment work is supplied by the private infrastructure repository, so this repository proves the code reads the configuration and fails loudly without it, not that any particular deployment is configured.
- The `NUXT_PUBLIC_SITE_URL` variable must exist in the build environment before the next image is built; the check cannot detect a missing site URL, it can only detect a host left in the source. The variable was created before the first build that uses it.
- The check reads tracked and staged content, not git history. The history was audited separately and holds no host, secret or personal path.
- The three resource values are asserted through the code and the deployed container, not through an end-to-end sign-in, which needs an interactive identity provider session.
