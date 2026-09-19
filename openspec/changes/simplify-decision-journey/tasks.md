# Tasks - simplify-decision-journey

## 1. Name the three moments

- [x] 1.1 Add the three moment labels and their one-line descriptions to `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json`, keeping the two catalogs in parity.

## 2. Group the section navigation

- [x] 2.1 Render the six section links grouped under the three moments in `apps/web/app/pages/workspace/decision-spaces/[spaceId].vue`, keeping every section path, every localized link and the active state.
- [x] 2.2 Mark a moment as active when the current route belongs to it, without changing what the section active state already does.

## 3. Make an empty space read as a path

- [x] 3.1 On `apps/web/app/pages/workspace/decision-spaces/[spaceId]/index.vue`, show for each moment what it will hold and the next action when none of its sections has content, reading only what the space already returns.

## 4. Regress the journey

- [x] 4.1 Add a browser scenario that reads the three moments on a space page and reaches each section through them, in French and English.
- [x] 4.2 Confirm the scenario fails against the previous navigation.

## 5. Close with evidence

- [x] 5.1 Run `pnpm lint`, `pnpm typecheck`, `check_locales`, `check_design_tokens`, `check_ux_coverage` and `pnpm build`.
- [x] 5.2 Run the browser suite.
- [x] 5.3 Write `acceptance.md` with the scenario-to-evidence mapping.
