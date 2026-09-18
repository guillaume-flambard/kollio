# Tasks - add-configurable-deployment-identity

## 1. Read the identity from the environment

- [x] 1.1 Declare `resources: []` in `apps/web/nuxt.config.ts` and give the i18n base URL a local fallback
- [x] 1.2 In `apps/web/server/utils/kollio-api.ts`, derive the access-token audience from `runtimeConfig.logto.resources` and fail with a named error when it is empty
- [x] 1.3 Add `ARG NUXT_PUBLIC_SITE_URL` to `apps/web/Dockerfile` and pass it from `NUXT_PUBLIC_SITE_URL` in the build step of the workflow

## 2. Enforce it with the guard

- [x] 2.1 Fail `scripts/check_private_files.py` when tracked content names the operator host or home directory, skipping the script itself

## 3. Supply it to the deployment

- [x] 3.1 Create the `NUXT_PUBLIC_SITE_URL` repository variable before the next build
- [x] 3.2 In the infrastructure repository, supply `NUXT_LOGTO_RESOURCES` to the web service and open a pull request

## 4. Close with evidence

- [x] 4.1 Run `scripts/check_private_files.py --tracked`, `pnpm lint`, `pnpm typecheck`, the locale, token and coverage guards, `pnpm build` and the browser suite
- [ ] 4.2 Verify sign-in, the landing and the canonical URLs in the deployment after the merge
- [x] 4.3 Write `acceptance.md` with the scenario to evidence mapping
