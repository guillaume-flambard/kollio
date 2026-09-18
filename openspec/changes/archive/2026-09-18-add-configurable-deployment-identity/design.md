# Design - make the deployment identity configurable

## Context

The public release replaced the operator's host everywhere it was only prose, but three values stayed wired because they are read by the running application: the Logto resource list in `apps/web/nuxt.config.ts`, the access-token audience in `apps/web/server/utils/kollio-api.ts`, and the i18n base URL in `apps/web/nuxt.config.ts`. The first two have to hold the same string, because the resource indicator the web app asks the identity provider for is the audience the API verifies, and a mismatch only surfaces as a 401 at sign-in. The third is evaluated while the image is built and feeds canonical URLs and hreflang tags.

The runtime reads of the other Logto settings show the mechanism already in use: the deployment supplies `NUXT_LOGTO_ENDPOINT`, `NUXT_LOGTO_APP_ID`, `NUXT_LOGTO_APP_SECRET`, `NUXT_LOGTO_COOKIE_ENCRYPTION_KEY` and `NUXT_LOGTO_CUSTOM_REDIRECT_BASE_URL`, and Nuxt merges environment overrides into `runtimeConfig` at startup, parsing non primitive values so a JSON string arrives as a list. The base URL does not have that path, because `i18n.baseUrl` is computed in the config at build time; `apps/web/Dockerfile` already takes `ARG NUXT_PUBLIC_AUTH_ENABLED` in the build stage and the workflow passes it, so the same route exists for a site URL.

## Goals / Non-Goals

**Goals:**

- The repository carries no operator host, so a clone runs by supplying its own configuration.
- The resource indicator and the token audience come from one value, and a missing configuration fails with a named error rather than a confusing 401 later.
- The build receives the public site URL so canonical URLs stay correct in the deployment.
- A check fails when tracked content names the operator's host, so the property survives future edits.

**Non-Goals:**

- Making the repository public or moving the continuous integration to hosted runners and a public registry.
- Renaming the identity provider's application or rotating its credentials.
- Changing what the identity provider issues or how the API verifies an audience.
- Making the fallback base URL meaningful in production: it exists so a local build without configuration is obviously local.

## Decisions

### One value instead of two constants kept in step

The web app has to request a resource indicator from the identity provider and the API has to verify that same audience. Reading the audience from `runtimeConfig.logto.resources` removes the second place where the string could be updated, and makes the sign-in configuration the single source. The alternative, a second `NUXT_` variable for the audience, was rejected because two variables that must match are a defect waiting for a busy afternoon.

### Missing configuration fails loudly

When no resource is configured, the server throws an error that names the missing configuration instead of requesting a token with an empty audience. An empty audience would produce a token that the API rejects, and the operator would read a generic authorization failure at the far end of the request. A 500 with a clear message is easier to diagnose and cannot be mistaken for a permissions bug.

### A local fallback for the site URL, fed by the build

The i18n base URL falls back to a local address, and the continuous integration passes the real one as a build argument from a repository variable. The alternative, keeping the deployment host as the fallback, would mean the repository still names it and the new check would fail. The variable has to exist before the next image build, otherwise the deployment publishes local URLs; that ordering is recorded as a boundary rather than enforced, because a missing variable only degrades search metadata and not the product.

### Extend the private file check rather than rely on review

`scripts/check_private_files.py` already rejects secret shaped content and private migration artifacts on every pull request. Adding an infrastructure pattern to the same script keeps one gate with one failure message, and it is the check that a fork or an external contribution actually runs. A reviewer's eye was the only guard before, and that is exactly the guard that failed.

## Migration Plan

1. Read the resource list and the audience from configuration in the web app, with the named error when it is absent.
2. Add the public site URL build argument to the image and pass it from the continuous integration.
3. Extend the private file check with the infrastructure pattern.
4. Supply `NUXT_LOGTO_RESOURCES` from the deployment and create the site URL variable, then deploy.
5. Verify sign-in, the landing and the canonical URLs in the deployment.

Rollback is a revert of the commit: the previous values return together with the constants, and the deployment keeps working because the new environment variables are simply ignored by the older code.

## Risks

- A deployment that forgets `NUXT_LOGTO_RESOURCES` breaks sign-in with a clear server error rather than silently, which is the intended trade.
- A build without the site URL variable publishes local canonical URLs; the check cannot detect that, so the variable is created before the first build after this change.
