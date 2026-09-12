## 1. Visual foundation

- [x] 1.1 Replace shared color, radius, shadow, focus, selection, and browser-surface tokens with the approved Aubergine semantic roles; verify contrast and run the web typecheck.
- [ ] 1.2 Add reusable felt-tip wash and split-action primitives with hover, focus, pressed, disabled, and reduced-motion states; verify them in French and English at 375px and 1440px.

## 2. Existing product surfaces

- [ ] 2.1 Rebuild the authenticated workspace shell with slim responsive navigation and verify sign-in, locale switching, navigation, and sign-out still work.
- [ ] 2.2 Redesign the idea list around purposeful rows and progressive metadata; verify loading, error, empty, pagination, and populated states.
- [ ] 2.3 Redesign idea detail as a Living Canvas using only fields from the generated API contract; verify private-workspace access and not-found behavior remain unchanged.

## 3. Contextual interaction

- [ ] 3.1 Add the accessible relationship-selection state and companion-panel contract without fabricated records; verify mouse and keyboard activation produce the same state.
- [ ] 3.2 Add replaceable selection, line-drawing, panel, and button motion; verify interrupted transitions settle correctly and reduced motion is immediate.
- [ ] 3.3 Define the narrow-screen companion flow with predictable back behavior; verify it at 320px, 375px, and 768px without horizontal scrolling.

## 4. Quality and delivery

- [ ] 4.1 Add meaningful UI tests for semantic active state, keyboard relationships, and reduced motion; verify the focused test suite passes.
- [x] 4.2 Run ESLint, Nuxt typecheck, production build, and OpenSpec strict validation; record the commands and results.
- [ ] 4.3 Perform a visual review against the approved Aubergine reference using real French and English content, then correct hierarchy, overflow, contrast, and motion defects.
