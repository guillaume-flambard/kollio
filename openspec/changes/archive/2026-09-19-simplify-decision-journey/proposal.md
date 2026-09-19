# Simplify the decision journey into three visible moments

## Why

A decision space exposes six sections named after the mechanics inside it: Explore, Converge, Options, Decision, Experiment and Learning. Somebody arriving on the space page has to learn six module names before starting anything, and the page says nothing about where to begin. The product is simpler than its navigation: a team frames a question, chooses with reasons, and records what happened.

## What Changes

- Group the six section routes under three plain-language moments in the space navigation: the decision to frame, the choice and its reasons, and what happened.
- Keep every section route and every deep link where it is, so a link shared today still lands on the same content.
- Add a label and a one-line description per moment, in French and English, and mark the active moment from the current route.
- Give each moment an empty state that says what it holds and what to do next, so a space with nothing in it still reads as a path.
- Keep the detailed tools available on demand inside their moment instead of promoting each one to the same level as the moments.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `decision-space-screens`: add a requirement that a space is navigated by three plain-language moments, so a newcomer starts without learning six internal module names.

## Impact

`apps/web/app/pages/workspace/decision-spaces/[spaceId].vue` (the space shell and its section navigation), `apps/web/app/pages/workspace/decision-spaces/[spaceId]/index.vue` (the empty states of the moments) and the two locale catalogs. No API, contract, migration or database change: the six section routes keep their paths and their payloads. No new dependency, no secret.

## Out of Scope

- A new AI engine, automatic decisions or automatic convergence.
- An onboarding tour, a terminology tutorial or gamification.
- Renaming the section routes or changing the domain vocabulary.
- Replacing the Living Canvas design system.
