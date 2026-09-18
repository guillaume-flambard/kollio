# Design - fix-profile-role-labels

## Context

Three call sites resolve a person's role or a membership's function through `ideas.role.*`:

- `apps/web/app/pages/workspace/people/[userId].vue:43` renders `profile.roles` as `{{ t(`ideas.role.${role}`) }}`.
- `apps/web/app/pages/workspace/people/[userId].vue:62` renders `{{ t(`ideas.role.${membership.role}`) }}` in the membership line.
- `apps/web/app/pages/workspace/ideas/index.vue:169` builds the explorer row's `expertise-label` from `idea.collaborators[0].roles[0]`.

`ideas.role.*` holds seven keys. The API serves `User.roles` from a thirteen-value vocabulary and membership functions from a twelve-value one. The catalogues already label both: `ideas.detail.roles.*` (thirteen keys) and `ideas.function.*` (twelve keys, matching `BUSINESS_FUNCTIONS_SQL`).

Neighbouring screens resolve these values correctly today: `IdeaPreviewPanel.vue:47` uses `ideas.detail.roles.*` for a person's roles, and `workspace/index.vue:146`, `settings.vue:688`, `ideas/index.vue:170` and `[ideaId].vue:588` use `ideas.function.*` for the function axis.

## Goals / Non-Goals

**Goals:**

- Every role and function value the API can serve renders as a localized label in French and English, on both screens.
- A regression test fails if a call site falls back to a key path.

**Non-Goals:**

- Changing the closed vocabularies, the API, the contract or the database.
- Extending `scripts/check_locales.mjs` with a value-level check.
- Touching the profile's localized date or number formatting.

## Decisions

### Point at the families the values belong to, rather than widening the legacy one

Adding the six missing values to `ideas.role.*` would make the page render, but it would keep two overlapping role vocabularies alive and leave the next added role value broken in the same way. `ideas.detail.roles.*` and `ideas.function.*` already cover the served values exactly and the neighbouring components use them, so three call sites move instead of seven keys being duplicated.

### Remove the legacy family in the same change

`rg 'ideas\.role\.'` over the repository finds exactly the three call sites above and nothing else, so the family becomes dead once they move. A dead family that shadows a live one is the trap that produced this defect: the next author finds `ideas.role.*`, uses it and reproduces the bug. Removing seven keys per catalogue is mechanical, and `scripts/check_locales.mjs` compares the two catalogues key by key, so they cannot drift.

### Assert the label, not just the presence of a value

The browser regression asserts the exact localized label for each fixture value. Asserting a non-empty string would pass on a key path, which is exactly how the defect survived the suite.

## Migration Plan

1. Move the three call sites to their correct families.
2. Update the browser regression fixture and add label assertions.
3. Remove `ideas.role.*` from both catalogues.
4. Run the delivery gates: `pnpm lint`, `pnpm typecheck`, `scripts/check_locales.mjs`, `scripts/check_design_tokens.mjs`, `scripts/check_ux_coverage.mjs`, `pnpm build` and the browser suite.

Rollback: revert the commit. No data, no contract and no runtime state is involved.
