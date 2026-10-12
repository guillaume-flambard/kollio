## 1. Approve the visual reference

- [x] 1.1 Produce desktop and 375px visual references for the Inbox and Decision Space shell in the quiet decision workbench direction, show them to the product owner, and record the selected reference before implementation begins.
- [x] 1.2 Translate the selected reference into a concise visual acceptance checklist for hierarchy, typography, semantic colour, relationship treatment, and motion; verify every checklist item maps to a token or shared primitive.

## 2. Establish shared workspace foundations

- [ ] 2.1 Consolidate connected-workspace typography, semantic colour, spacing, shape, and motion in canonical tokens; verify no connected route requires an undeclared token.
- [ ] 2.2 Implement shared page frame, page header, action, status, reasoning block, and feedback-state primitives; verify focused component tests cover keyboard focus, disabled state, and empty/error states.
- [ ] 2.3 Add a guard against page-local literal colour, spacing, typography, and unsupported token values; verify it fails on a known invalid fixture and passes the web lint command.
- [ ] 2.4 Replace or remove connected-product uses of display and annotation fonts that conflict with the approved reference; verify the production build loads the selected interface typography without a new font dependency.

## 3. Rebuild workspace navigation and Inbox

- [x] 3.1 Rework the workspace shell and navigation so Inbox and Decision Spaces are primary destinations, Settings remains reachable, and `/workspace/ideas` remains routable but leaves primary navigation; verify active navigation in desktop and mobile browser tests.
- [x] 3.2 Implement a deterministic Inbox next-action selection from the existing four response sections; verify the selected action always links to an existing entry's Space and actionable section in FR and EN browser tests.
- [x] 3.3 Render the Inbox next action, grouped waiting work, empty state, and load failure with the shared primitives; verify the existing Inbox scenarios and new primary-action scenarios pass without changing the API response.
- [x] 3.4 Add 375px and 768px Inbox coverage for no overflow, reachable primary action, and reachable grouped work; verify the responsive browser scenarios pass in both locales.

## 4. Rebuild the Decision Space shell

- [ ] 4.1 Replace the six-peer-section presentation with three visible product moments while preserving every existing section URL and active route; verify all six sections remain addressable in FR and EN browser tests.
- [ ] 4.2 Rebuild the Space header around question, owner, deadline, participants, readable status, and current moment; verify the data remains visible for populated, empty, and not-found states.
- [x] 4.3 Replace the raw lifecycle select with a contextual transition action backed by the existing permitted-transition table; verify permitted transitions persist after reload and reopening still refuses a blank reason.
- [x] 4.4 Add 375px and 768px Decision Space coverage for no overflow, readable status, active moment, reachable routes, and transition action; verify the responsive scenarios pass in FR and EN.

## 4A. Extend the approved workspace language through the six sections

- [ ] 4.5 Rework Explore around a private raw-material intake, visible source provenance, and a clear promotion boundary; preserve branch creation, visibility, and all existing URLs, then verify FR/EN browser scenarios.
- [ ] 4.6 Rework Converge as a readable reasoning canvas: agreements, open disagreements, alternatives, and source lineage are distinguishable without relying on colour alone; preserve all existing finding and resolution behaviour, then verify FR/EN browser scenarios.
- [ ] 4.7 Rework Options and Decision with the shared page frame, reasoning blocks, one primary action, and explicit retained or rejected rationale; preserve decision-record permissions and lifecycle behaviour, then verify FR/EN browser scenarios.
- [ ] 4.8 Rework Experiment and Learning with the shared page frame, expected-versus-observed relationship treatment, and confirmed-learning boundary; preserve existing outcome and confirmation behaviour, then verify FR/EN browser scenarios.
- [ ] 4.9 Audit all six section routes at 375px, 768px and desktop for canonical tokens, owned icons, one readable current action, empty/error states, and active-moment context; record route-by-route visual evidence.

## 5. Capture evidence and protect the pilot

- [ ] 5.1 Capture approved desktop and phone screenshots for the Inbox and Decision Space in French and English, and link them to the UX evidence record with non-empty paths.
- [ ] 5.2 Run `pnpm lint`, `pnpm typecheck`, `pnpm --dir apps/web test:ui`, the affected Playwright browser specs, and `pnpm build`; record results and any simulated-boundary limitation in `acceptance.md`.
- [ ] 5.3 Verify the redesign does not alter the scope or evidence of `verify-pilot-journey`; confirm the two changes can be tested independently before merge.
