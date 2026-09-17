# Acceptance evidence — add-decision-space-screens

Change: `openspec/changes/add-decision-space-screens`
Tickets: GitHub #119 (migration step 2 of `docs/00-project-overview.md` §20, screen half; follows the API slice #109)
Date: 2026-09-17
Delivered by this change: the Decision Space list, the form that opens one, the Space screen with its six sections, its status transitions and the workspace navigation, plus the idea Explorer re-homed at `/workspace/ideas`. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Spaces listed | `tests/browser/decision-spaces.spec.ts::DECISION-SPACES-01` (question, owner, deadline and participant count, both locales) | passing |
| Nothing yet | `::DECISION-SPACES-02` | passing |
| A Space from another workspace is not reachable | `::DECISION-SPACES-11` (a 404 renders the not-found state; isolation itself is proved by `tests/integration/test_decision_space.py::test_spaces_stay_inside_their_workspace`) | passing |
| Opened from the form | `::DECISION-SPACES-03` (the POST lands on the new Space's screen and the question is the one typed) | passing |
| A blank question is refused | `::DECISION-SPACES-04` (the form says so and no POST is sent) | passing |
| The header frames the Space | `::DECISION-SPACES-05` (question, status word, owner, participants) | passing |
| Every section is reachable | `::DECISION-SPACES-05` (all six section routes clicked and rendered) | passing |
| An empty section says what will live there | `::DECISION-SPACES-06` (body plus the "lands with its own slice" line) | passing |
| The status is readable | `::DECISION-SPACES-05` (the status renders as a word, not as `READY_TO_DECIDE`) | passing |
| A permitted transition is applied | `::DECISION-SPACES-07` (applied, then survives a reload) | passing |
| A transition the API refuses is not offered | `::DECISION-SPACES-08` (from `OPEN` the select offers exactly `EXPLORING`) | passing |
| The Explorer keeps working | `tests/browser/explorer.spec.ts::EXPLORER-02, EXPLORER-04, EXPLORER-06` (filters, rail and reset control unchanged) and `::DECISION-SPACES-10` | passing |
| Three entries with one active | `::DECISION-SPACES-09` (Decision spaces active on the list, Initiatives active on the Explorer, never both) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **138 passed** (136 before this slice's last scenario; `decision-spaces.spec.ts` contributes 22). The same command with the Explorer specs alone: `playwright test tests/browser/explorer.spec.ts` → 6 passed.

## Boundary evidence

- **Browser tests prove the UI only.** Every route under `/api/**` is mocked in the specs, so they prove what the screen renders and which requests it sends. They do **not** prove authentication, workspace isolation, the lifecycle rules or persistence: those are proved by the API integration suite on disposable PostgreSQL (`tests/integration/test_decision_space.py`, 124 assertions recorded in `openspec/changes/archive/2026-09-17-add-decision-space/acceptance.md`), where a non-member gets 404 on every operation and a skipped transition is refused with nothing stored.
- The client-side permitted-transition table duplicates `apps/api/src/modules/decision_spaces/domain/lifecycle.py` (`DECLARED_TRANSITIONS`). It is a presentation filter, not an authority: the API refuses anything else, and `::DECISION-SPACES-08` asserts the screen offers only the declared edge from `OPEN`.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 536 catalog keys cover their usages.` (472 before this slice; 64 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.` No literal colour and no undefined `var(--…)` in the new pages.
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` clean; `pnpm typecheck` clean.
- **No API change**: no route, schema or migration is touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op for this slice. The OpenAPI export was not run because nothing on the boundary moved.
- The participant roster is read-only on this screen. Adding and removing a Space participant exists in the API (`add_decision_space_participant`, `remove_decision_space_participant`) and is deliberately not surfaced here.

## Explicitly deferred (not gaps)

- The six section bodies. Each names what will live there and says it lands with its own slice; Explore (#120), Converge (#121), Options (#122), Decision (#123), Experiment (#124) and Learning (#125) fill them in that order.
- Space participant management, with the workspace Members slice (#126).
- The Decision Inbox, which takes `/workspace` over at step 9 (#127); the Space list then moves to `/workspace/decision-spaces`.

## Known gaps

- None. The slice is complete for step 2's screen half.
