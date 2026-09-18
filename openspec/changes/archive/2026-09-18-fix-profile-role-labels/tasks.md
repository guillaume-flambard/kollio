# Tasks - fix-profile-role-labels

## 1. Repoint the call sites

- [x] 1.1 `people/[userId].vue`: render `profile.roles` through `ideas.detail.roles.*`
- [x] 1.2 `people/[userId].vue`: render the membership function through `ideas.function.*`
- [x] 1.3 `ideas/index.vue`: render the explorer expertise badge through `ideas.detail.roles.*`

## 2. Regress the defect

- [x] 2.1 Use a fixture role and a fixture function outside the legacy seven keys
- [x] 2.2 Assert the rendered craft-role labels and the membership function label, in FR and EN
- [x] 2.3 Confirm the assertions fail against the previous call sites

## 3. Retire the legacy family

- [x] 3.1 Confirm no call site references `ideas.role.*`
- [x] 3.2 Remove the seven keys from `fr.json` and `en.json`

## 4. Close with evidence

- [x] 4.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens`, `check_ux_coverage` and `pnpm build`
- [x] 4.2 Run the browser suite
- [x] 4.3 Write `acceptance.md` with the scenario-to-evidence mapping
