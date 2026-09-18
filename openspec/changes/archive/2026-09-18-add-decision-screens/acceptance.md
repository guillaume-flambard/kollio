# Acceptance evidence — add-decision-screens

Change: `openspec/changes/add-decision-screens`

Tickets: GitHub #123 (migration steps 5 and 6 of `docs/00-project-overview.md` §20, screen half; follows the API slices #113 and #114)

Date: 2026-09-17

Delivered by this change: the Decision section of a Decision Space. A member challenges one of
the Space's Options, reads the runs the Critic executed with their findings, settles each
proposed finding, and commits the Decision Record from `READY_TO_DECIDE` with its rationale,
alternatives, arguments, assumptions, uncertainty, success criteria and revisit triggers. Every
committed version stays readable. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that
exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| A challenge is opened | `tests/browser/decision.spec.ts::DECISION-02` (the POST reaches the Option's challenges and the section reports the new run) | passing |
| A Space with no Option | `tests/browser/decision.spec.ts::DECISION-01` (the section says there is no Option to challenge and points at the Options section) | passing |
| The section could not be read | `tests/browser/decision.spec.ts::DECISION-10` (a failing read says so and the heading stays readable) | passing |
| Findings are listed with their kind and severity | `tests/browser/decision.spec.ts::DECISION-03` (two findings, each with its kind, its severity and its status, plus the model that answered) | passing |
| A member confirms one and dismisses another | `tests/browser/decision.spec.ts::DECISION-04` (both resolutions are POSTed and both rows carry the chosen status) | passing |
| Nothing is settled automatically | `tests/browser/decision.spec.ts::DECISION-03` and `::DECISION-04` (a proposed finding still offers both actions after the read, and a status only changes when a member acts) | passing |
| A failed run shows its reason | `tests/browser/decision.spec.ts::DECISION-05` (the stored reason is rendered, no finding is listed, and a new run can be opened) | passing |
| A new run can be opened after a failure | `tests/browser/decision.spec.ts::DECISION-05` (the retry action POSTs to the same Option and reports the new run) | passing |
| The record is committed with its rationale and triggers | `tests/browser/decision.spec.ts::DECISION-06` (the POST carries the selected Option, the rationale and the trigger, and a reload shows the record) | passing |
| The commit form is offered only when the Space is ready | `tests/browser/decision.spec.ts::DECISION-11` (an `EXPLORING` Space says which status a decision is recorded from and offers no form) | passing |
| A member who is not a participant is refused | `tests/browser/decision.spec.ts::DECISION-09` (a 403 says only the owner and the participants can decide, and the section keeps rendering) | passing |
| Versions are listed | `tests/browser/decision.spec.ts::DECISION-07` (each version carries its number, its date and its rationale) | passing |
| A second version keeps the first readable | `tests/browser/decision.spec.ts::DECISION-07` (after a second commit both versions are listed and the first rationale is unchanged) | passing |
| No verdict, score or ranking | `tests/browser/decision.spec.ts::DECISION-08` (no element of the section carries a score, a rank or a rating marker, and the section states that the Critic proposes and a person decides) | passing |
| A French reader | `tests/browser/decision.spec.ts` describes `fr` (all eleven scenarios run with the French catalog) | passing |
| An English reader | `tests/browser/decision.spec.ts` describes `en` (the same eleven scenarios run with the English catalog) | passing |
| Challenge runs and findings stay inside their Space | `apps/api/tests/integration/test_challenge.py` and `apps/api/tests/integration/test_challenge_execution.py` (isolation, the Critic's origin and status, the refusal of a citation outside the brief) | passing |
| Commits are append-only and refuse a non-ready Space | `apps/api/tests/integration/test_decision_record.py` (version numbering, the `READY_TO_DECIDE` gate, arguments from confirmed Contributions) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **236 passed**, of which
`tests/browser/decision.spec.ts` contributes **22** (11 scenarios × FR/EN). `tests/browser/decision-spaces.spec.ts`
still passes its 22 scenarios.

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove
  neither authentication, nor workspace isolation, nor the lifecycle rules, nor persistence.
  Those are proved by `apps/api/tests/integration/test_challenge.py`,
  `apps/api/tests/integration/test_challenge_execution.py` and
  `apps/api/tests/integration/test_decision_record.py` on disposable PostgreSQL.
- **A record that does not exist yet is not an error.** The `decision` proxy answers `null`
  when the API answers 404, so a Space that has never been decided renders its empty state
  instead of a failure. That is a client-side reading of an absent resource, not a second
  source of truth.
- **Three operations stay unsurfaced**: `record_challenge_finding` (a human finding is not
  part of this slice), `complete_challenge` (the Critic completes runs) and `get_challenge`
  (a reader is served by `list_challenges`, which returns the runs, their findings and the
  coverage). The section states that the Critic proposes and a person decides.
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all
  792 catalog keys cover their usages.` (702 before this slice; 90 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app
  uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean.
- **Build**: `pnpm build` completes with the section's route in the Nitro output.
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json`
  and the generated client are unchanged and `make contract` is a no-op for this slice.

## Explicitly deferred (not gaps)

- Recording a human challenge finding, and completing a run by hand, are not part of this
  slice; the Critic records and completes.
- The Experiment section (#124), the Learning section (#125), Members (#126) and the Decision
  Inbox (#127) stay as they are until their own slices.

## Known gaps

- None beyond the boundaries above.
