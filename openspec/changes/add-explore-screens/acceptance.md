# Acceptance evidence — add-explore-screens

Change: `openspec/changes/add-explore-screens`
Tickets: GitHub #120 (migration step 3 of `docs/00-project-overview.md` §20, screen half; follows the API slice #110)
Date: 2026-09-17
Delivered by this change: the Explore section of a Decision Space. A participant creates a Branch with its raw material and its visibility, proposes a Contribution from it, reads what waits for a human apart from what is confirmed, and sees every Contribution's provenance. No API change: the `branches` capability already ships every operation this screen consumes.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A Branch is created and read back | `tests/browser/explore.spec.ts::EXPLORE-02` (a Branch is created with its material and visibility, then listed) | passing |
| A Branch without a name is refused | `::EXPLORE-05` (no request is sent, the form says the name is required) | passing |
| A Branch whose visibility is not private or shared is refused | `::EXPLORE-02` (the form offers only Private and Shared; a request carries one of them) | passing |
| Branches arrive in the order they were explored | `::EXPLORE-03` (the list renders both Branches in the order the API returned) | passing |
| Visibility is stated per Branch | `::EXPLORE-03` (a private and a shared Branch each state their own visibility) | passing |
| A private Branch is not listed for another participant | `::EXPLORE-01` (the rendering only shows what the API returned — a private Branch of another participant is filtered out by `list_branches`, proved in `tests/integration/test_branches.py`) | passing |
| Material says what it is | `::EXPLORE-04` (the material carries the material label, not a shared-reasoning treatment) | passing |
| Promotion starts from the Branch | `::EXPLORE-04` (the only promotion action lives on the Branch, and the confirmed list stays empty) | passing |
| A proposal is recorded from its Branch | `::EXPLORE-06` (the request carries the Branch, the kind, the title and the optional fields) | passing |
| A proposal without a title is refused | `::EXPLORE-07` (no request is sent, the form says the title is required) | passing |
| A proposal with an unknown kind is refused | `::EXPLORE-06` (the form offers exactly the five kinds the API accepts) | passing |
| The two states are listed apart | `::EXPLORE-08` (what waits for a human is listed under its own heading, apart from what is confirmed) | passing |
| Nothing waits for a human yet | `::EXPLORE-01` (the waiting list says it is empty rather than being hidden) | passing |
| A human confirms what waited | `::EXPLORE-09` (confirming moves the Contribution into the confirmed list) | passing |
| Provenance is complete for a Contribution that carries everything | `::EXPLORE-10` (author, Branch, source, tool or model and the date are all rendered) | passing |
| An absent source or tool is said to be absent | `::EXPLORE-11` (an absent source and an absent tool each read as not stated, never as a blank) | passing |
| The absence is in the reader's language | `::EXPLORE-11` (the same key is asserted from both catalogues) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **162 passed**, of which `tests/browser/explore.spec.ts` contributes **24** (12 scenarios × FR/EN).

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove neither authentication, nor workspace isolation, nor the domain rules that decide who may read a Branch or confirm a Contribution, nor persistence. Those are proved on disposable PostgreSQL by `apps/api/tests/integration/test_branches.py` (see the archived API slice `openspec/changes/archive/2026-09-17-map-ideas-to-branches/acceptance.md`).
- **The waiting list is not reachable from production yet.** The HTTP route for proposing a Contribution records a human proposal, so it always arrives `confirmed`; nothing in production creates a `suggested` Contribution until the AI proposer ships. The waiting group is therefore evidenced with mocked responses, which proves the screen renders and settles the state, not that the state occurs today.
- **Branch material is written once.** No HTTP operation updates or deletes a Branch, so the screen creates a Branch and its material in one form; editing Branch material is not offered rather than being faked.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 592 catalog keys cover their usages.` (472 before the screen slices; 120 keys added in both locales across #119 and this change).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean; `pnpm build` completes.
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op for this slice.

## Explicitly deferred (not gaps)

- The AI proposer that creates `suggested` Contributions lands with its own slice; this screen already renders and settles that state.
- Converge (#121), Options (#122), Decision (#123), Experiment (#124) and Learning (#125) fill the remaining sections of the Space shell.
- Space participants are managed in the header by the Members slice (#126), not here.

## Known gaps

- None beyond the boundaries above.
