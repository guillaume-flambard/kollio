# Tasks

## 1. Vocabulary and navigation

- [x] 1.1 Add the `workspace.settings.members` keys to both catalogues: the section, the roster, the initiative to manage, the waiting requests and their actions, the team and its removal, the add form, the four participations, the two honest notes and the errors.
- [x] 1.2 Rename the navigation entry: `navigation.settings` reads Settings in English and Réglages in French, while the route stays `/workspace/settings`, and update the browser spec that asserted the old label.

## 2. The Members section

- [x] 2.1 List the workspace's members with their roles, read from the workspace member endpoint, and say so when the roster could not be read.
- [x] 2.2 Let a member choose which initiative to manage, since membership belongs to an initiative, and say so when the workspace holds none.
- [x] 2.3 List the initiative's waiting join requests with the requester's name and note, and say when nothing is waiting.
- [x] 2.4 Accept a request through the existing operation, then read the initiative back so the requester appears in the team without a manual reload.
- [x] 2.5 Refuse a request only with a reason a person wrote, refusing a blank reason locally before reaching the API.
- [x] 2.6 Add a participant with a participation and a function, and remove a member from the team, each through its existing operation, and refuse an add that names nobody.
- [x] 2.7 Render the membership controls for any member and show the refusal the API returns, and state that membership is per initiative and that matching is not surfaced here.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs: the roster with roles, the waiting request with its requester, acceptance, a refusal without a reason, a refusal with a reason, a removal, an add, an add without a member, a failed read and a workspace with no initiative.
- [x] 3.2 Carry them to green while keeping the six-section shell spec and the responsive navigation spec passing.

## 4. Documentation

- [x] 4.1 Record the section's delta as the `members-screens` capability.
- [x] 4.2 Record the scenario-to-test evidence, the boundaries and the deferrals in `acceptance.md`.

## 5. Verification

- [x] 5.1 Run the linter and the type checker.
- [x] 5.2 Run the locale gate, the design-token gate and the UX coverage gate.
- [x] 5.3 Run the whole browser suite and the production build.
- [x] 5.4 Validate the change with the OpenSpec CLI.
