# Acceptance evidence — add-learning-screens

Change: `openspec/changes/add-learning-screens`
Tickets: GitHub #125 (migration step 8 of `docs/00-project-overview.md` §20, screen half; follows the API slice #116)
Date: 2026-09-17
Delivered by this change: the Learning section of a Decision Space. It lists the lessons a Space holds, tells a proposed lesson apart from a confirmed one, and lets a person confirm the draft an experiment composed or save an edit without confirming. Each lesson shows the outcome, the experiment and the initiative it descends from. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| Nothing confirmed yet | `tests/browser/learning.spec.ts::LEARNING-01` (the empty state says there is nothing yet, no group is rendered) | passing |
| The lessons of a Space are listed | `tests/browser/learning.spec.ts::LEARNING-05` (a confirmed lesson is rendered with its text) | passing |
| A proposed lesson is told apart from a confirmed one | `tests/browser/learning.spec.ts::LEARNING-02` and `LEARNING-05` (the status word differs per group, and the proposed group holds only drafts) | passing |
| The lessons could not be read | `tests/browser/learning.spec.ts::LEARNING-08` (an alert says the lessons could not be loaded, the heading and intro stay rendered) | passing |
| Confirm a lesson | `tests/browser/learning.spec.ts::LEARNING-03` (the request carries `confirm: true`, the lesson moves to the confirmed group) | passing |
| Edit the text before confirming | `tests/browser/learning.spec.ts::LEARNING-03` (the edited text is what the request carries and what the confirmed group renders) | passing |
| A refused write is shown | `tests/browser/learning.spec.ts::LEARNING-07` (a 403 becomes an alert and the lesson stays a draft) | passing |
| Save a draft | `tests/browser/learning.spec.ts::LEARNING-04` (the request carries `confirm: false` and the lesson stays a draft) | passing |
| The section says the draft is kept | `tests/browser/learning.spec.ts::LEARNING-04` (both notes are rendered) | passing |
| Nothing is confirmed without a person | `tests/browser/learning.spec.ts::LEARNING-06` (opening the section writes nothing and the confirmed group is empty) | passing |
| No score, ranking or verdict | `tests/browser/learning.spec.ts::LEARNING-09` (no element in the section carries a score, rank, rating, verdict or prediction hook) | passing |
| A French section | `tests/browser/learning.spec.ts` (every scenario runs in the `fr` locale) | passing |
| An English section | `tests/browser/learning.spec.ts` (every scenario runs in the `en` locale) | passing |
| Isolation, permissions and the learning rules | `apps/api/tests/integration/test_experiments.py` (workspace isolation, who may write, and the `draft` → `confirmed` rule are proved against a disposable PostgreSQL, not by a mocked browser test) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **290 passed**, of which `tests/browser/learning.spec.ts` contributes **18** (9 scenarios × FR/EN).

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove neither authentication, nor workspace isolation, nor the learning rules, nor persistence. Those are proved by the API integration suite on a disposable PostgreSQL (`apps/api/tests/integration/test_experiments.py`).
- **The API has no `rejected` status.** `LEARNING_STATUSES` is `{'draft', 'confirmed'}`, so a refusal cannot be stored. The section says this plainly: saving without confirming keeps a draft that is not deleted (`actions.save` + `notes.draftKept`), rather than pretending a rejected state exists.
- **Shipping the last section retired a scenario.** `DECISION-SPACES-06 an unshipped section says what will live there` was removed from `apps/web/tests/browser/decision-spaces.spec.ts` because this slice ships the sixth and final section, so no route renders the placeholder message any more. `KollioSpaceSection` stays as the placeholder a future section would use.
- **Confirmation embeds the lesson for reuse** and that behaviour belongs to the `learning-reuse` capability, not to this screen.
- **The Memory Retriever (§11) is out of scope**, so the section shows a Space's own lessons only, and the Inbox's `Relevant prior memory` section stays absent.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 952 catalog keys cover their usages.` (926 before this slice; 26 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` is clean and `pnpm typecheck` reports no error.
- **Build**: `pnpm build` completes.
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op for this slice.

## Explicitly deferred (not gaps)

- The Memory Retriever (§11) and the Inbox section it feeds — a later slice.
- A `rejected` learning status — the API would need an operation and a column before a screen could offer it.
- The Convergence Engine (§13) proposing lessons — not part of this capability.
- The remaining screen slices: Members (#126) and the Decision Inbox (#127).

## Known gaps

- None beyond the boundaries above.
