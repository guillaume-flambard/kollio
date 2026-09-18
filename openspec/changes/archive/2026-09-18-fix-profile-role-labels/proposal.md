# Fix profile role labels

## Why

The person profile at `/workspace/people/[userId]` resolves every role label through `ideas.role.*`, a seven-key family inherited from the pre-pivot vocabulary (`owner`, `designer`, `dev`, `commercial`, `growth`, `data`, `product`). The API serves newer closed vocabularies instead: a person's craft roles come from `User.roles` (`product`, `strategy`, `design`, `research`, `engineering`, `platform`, `ai`, `data`, `growth`, `sales`, `operations`, `finance`) and a membership carries one business function from `BUSINESS_FUNCTIONS_SQL`. A value outside the seven legacy keys has no label, so the page prints the key path itself: the rendered profile reads `ideas.role.engineering` and `ideas.role.platform` where it should read the role labels. The same lookup feeds the expertise badge of the explorer row in `apps/web/app/pages/workspace/ideas/index.vue`, so the defect reaches a second screen.

Both families the correct vocabulary needs already exist in the catalogues: `ideas.detail.roles.*` holds exactly the thirteen values a person's roles can take, and `ideas.function.*` holds exactly the twelve business functions. `IdeaPreviewPanel.vue:47` and `workspace/index.vue:146` already resolve these values through them. No translation is missing; three call sites point at the wrong family.

The browser suite missed it because its fixture uses `dev`, one of the seven legacy keys, and asserts no label at all.

## What Changes

- Repoint the profile's craft-role list to `ideas.detail.roles.*`, the family that covers every seeded role value.
- Repoint the profile's membership line to `ideas.function.*`, the family of the business-function axis the membership carries.
- Repoint the explorer row's expertise badge to `ideas.detail.roles.*`, the family the idea detail panel already uses for a person's roles.
- Use fixture values outside the legacy seven and assert the rendered labels in the browser regression, so a raw key path fails the test.
- Remove the now-unused `ideas.role.*` family from both catalogues once no call site remains.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `participant-axes`: add a requirement that the web renders every participant axis value through the label family that owns its vocabulary, so a closed vocabulary value can never surface as a key path.

## Impact

- `apps/web/app/pages/workspace/people/[userId].vue`
- `apps/web/app/pages/workspace/ideas/index.vue`
- `apps/web/i18n/locales/fr.json` and `apps/web/i18n/locales/en.json` (removal of seven unused keys per catalogue)
- `apps/web/tests/browser/profiles.spec.ts`

No contract, migration, database or API change: the vocabularies served today are already the target ones. Adds no dependency and no secret.

## Out of Scope

- Changing the closed vocabularies themselves.
- Adding a value-level check to `scripts/check_locales.mjs`, which would catch this class of defect before review.
- Formatting the profile's dates and numbers through the configured i18n formats instead of a page-local `Intl.DateTimeFormat`.
