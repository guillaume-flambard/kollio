# Tasks — add-explore-screens

## 1. Vocabulary and routes

- [x] 1.1 Add the Explore vocabulary to the catalogues in both locales (Branches, visibility, the proposal form, the two Contribution states, provenance, the stated absences) and record Branch, Contribution and Explore in `apps/web/CONTEXT.md`.
- [x] 1.2 Add the five Nitro proxy routes the screen consumes: list Branches, create a Branch, list Contributions, propose a Contribution, confirm a Contribution. Each one refuses a missing or blank required field with a readable message before it reaches the API.

## 2. The Explore section

- [x] 2.1 Make the Explore section body real: create a Branch with its name, its raw material and its visibility, and list every readable Branch with its material, its creator and its date.
- [x] 2.2 State each Branch's visibility in words on the Branch itself, and label the material as the Branch's material rather than as the Space's reasoning.
- [x] 2.3 Add the proposal: choose the Branch, the kind, the title and the optional body, source and tool or model, then record it against that Branch.
- [x] 2.4 List the two Contribution states apart, with the awaiting list carrying the action that confirms, and an empty awaiting list said to be empty.
- [x] 2.5 Show every Contribution's provenance — author, Branch, source, tool or model and the date added — stating an absent source or tool as absent.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs for the section: create a Branch, refuse a blank name, state visibility per Branch, keep a private Branch out of another participant's list, refuse a blank or unknown proposal, list a confirmed Contribution with its provenance, list an awaiting Contribution apart with its confirmation action, and an empty awaiting list.
- [x] 3.2 Carry the specs to green, keeping the two tests of `decision-spaces.spec.ts` that assert the Explore section header and body intact.

## 4. Documentation

- [x] 4.1 Write the `explore-screens` capability spec with the observable scenarios of the section.
- [x] 4.2 Record the scenario-to-test mapping in `acceptance.md`, name the boundary that no production route creates a Contribution awaiting a human yet, and list what is deferred.

## 5. Verification

- [x] 5.1 Run `pnpm lint` and `pnpm typecheck`.
- [x] 5.2 Run the locale gate, the design-token gate and the UX coverage gate.
- [x] 5.3 Run the browser specs and the production build.
- [x] 5.4 Validate the change with `openspec validate add-explore-screens`.
