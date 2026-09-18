# Make the deployment identity configurable

## Why

The public release left three values that name the operator's host wired into the application: the Logto resource list in `apps/web/nuxt.config.ts`, the same string as an API audience constant in `apps/web/server/utils/kollio-api.ts`, and the i18n base URL in `apps/web/nuxt.config.ts`. A check that fails on the operator's host in tracked content would fail on them, and nobody can run the web app from a clone without either inheriting that host or editing source.

Two of the three are runtime values: `@logto/nuxt` reads the resource list when it asks for an access token, and the audience the server requests has to equal that same resource indicator, which is why keeping them as two separate strings invites a 401 that only appears at sign-in. The third, the i18n base URL, is evaluated while the image is built, so it feeds canonical URLs and hreflang tags and has to arrive through the build.

## What Changes

- Declare `resources: []` in `apps/web/nuxt.config.ts` and read the list from `NUXT_LOGTO_RESOURCES` at runtime.
- Derive the access-token audience in `apps/web/server/utils/kollio-api.ts` from `runtimeConfig.logto.resources`, and fail with a named server error when no resource is configured, so the requested resource and the audience cannot diverge.
- Pass the public site URL into the image build: `ARG NUXT_PUBLIC_SITE_URL` in `apps/web/Dockerfile`, fed by the `NUXT_PUBLIC_SITE_URL` GitHub Actions variable in the build step, with a local fallback so a build without it stays obviously local.
- Extend `scripts/check_private_files.py` to fail when tracked content names the operator's host or home directory, so the property is enforced on every pull request instead of remembered.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `operations/public-release`: add a requirement that the deployment identity comes from the environment rather than from the repository, so a clone runs without the operator's host in its source.

## Impact

Touches `apps/web/nuxt.config.ts`, `apps/web/server/utils/kollio-api.ts`, `apps/web/Dockerfile`, `.github/workflows/ci.yml` and `scripts/check_private_files.py`. No contract, migration or database change, no dependency and no secret. The deployment that supplies `NUXT_LOGTO_RESOURCES` lives in the private infrastructure repository, and the `NUXT_PUBLIC_SITE_URL` variable must exist before the next image build.

## Out of Scope

- Making the repository public and moving the CI to hosted runners and a public registry.
- Renaming the Logto application or rotating its credentials.
- Changing what the identity provider issues, what the API accepts as an audience, or the sign-in experience.
