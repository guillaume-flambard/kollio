## 1. Vocabulary and navigation

- [x] 1.1 Add the Decision spaces message keys (list, form, header, six sections, statuses, transitions) to both locales, referenced by a literal call so the locale gate passes.
- [x] 1.2 Give the workspace navigation three entries — Decision spaces, Initiatives, Company context — with an explicitly computed active state.

## 2. The list and the form

- [x] 2.1 Add failing browser specs for the list: a workspace's Spaces render with question, owner, status and deadline; an empty workspace says so; another workspace's Space is not reachable.
- [x] 2.2 Replace `/workspace` with the Decision Space list and the open form, carrying the browser evidence to green.

## 3. The Space shell and its sections

- [x] 3.1 Add failing browser specs for the shell: the header frames the question and its participants; the six section routes are reachable; each empty section says what will live there.
- [x] 3.2 Build the shell and the six section routes, carrying the browser evidence to green.
- [x] 3.3 Add failing browser spec for the status: the permitted transitions from the current status are offered and the new status is visible after reload; an undeclared transition is not offered.

## 4. Re-home the Explorer

- [x] 4.1 Move the idea Explorer to `/workspace/ideas`, repoint its filter and pagination links, and update its browser spec URLs. Prove it still renders identically.

## 5. Evidence and docs

- [x] 5.1 Record scenario-to-test evidence in `acceptance.md`, naming what browser tests do not prove (authentication, authorization, persistence).
- [x] 5.2 Add the screen vocabulary to `apps/web/CONTEXT.md` and note the new routes in `docs/`.
- [x] 5.3 Run `pnpm lint`, `pnpm typecheck`, the locale gate, the design-token gate, the UX coverage gate, the browser specs and the production build.
