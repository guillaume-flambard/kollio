# Tasks — add the Options screens

## 1. Vocabulary and routes

- [x] 1.1 Add the Options keys to both locale catalogs and the Options vocabulary to
      `apps/web/CONTEXT.md`.
- [x] 1.2 Add the seven Nitro proxies under
      `server/api/workspaces/[workspaceId]/decision-spaces/[spaceId]/options…`, rejecting a
      missing or blank required field before it reaches the API.

## 2. The Options section

- [x] 2.1 Read the Options of the Space, each with its title, its proposal and whether it
      carries evidence, and read each Option in detail because the list omits evidence.
- [x] 2.2 Write an Option from a form with a required title and proposal and the six
      optional §7 fields, leaving an omitted field out instead of storing an empty answer.
- [x] 2.3 Edit an Option and keep the change readable after a reload.
- [x] 2.4 Link a confirmed Contribution of the Space as evidence `for` or `against`, unlink
      it, and offer only confirmed Contributions.
- [x] 2.5 Delete an Option so it leaves the list while the Space stays readable.
- [x] 2.6 Say an empty list is empty, with the action that starts one, and say an absent
      field is absent. Score, rank and rate nothing.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs at the mocked-API pattern covering the empty state,
      creation, refusal of a blank title and a blank proposal, edition, linking and
      unlinking evidence, absence of scoring, deletion and a failed read.
- [x] 3.2 Carry them to green in French and English, keeping the two
      `decision-spaces.spec.ts` scenarios that assert the Options section's heading and
      body intact.

## 4. Documentation

- [x] 4.1 Write the `options-screens` spec delta.
- [x] 4.2 Record the scenario-to-test map in `acceptance.md` and name the boundaries and
      the deferred work.

## 5. Verification

- [x] 5.1 Run lint and typecheck.
- [x] 5.2 Run the locale gate, the design-token gate and the UX coverage gate.
- [x] 5.3 Run the full browser suite and the production build.
- [x] 5.4 Run `openspec validate add-options-screens`.
