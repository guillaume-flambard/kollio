# Acceptance evidence — add-experiment-screens

Change: `openspec/changes/add-experiment-screens`
Tickets: GitHub #124 (migration step 7 of `docs/00-project-overview.md` §20, screen half; follows the API slices #115 and #116)
Date: 2026-09-17
Delivered by this change: the Experiment section of a Decision Space. It holds the Space's editable scenario ranges, declares scenario runs on a chosen Option, reads the deterministic sensitivity report, and carries the experiment loop from creation through status changes to the observed outcome. The Learning stays read-only here. No API change.

Status: **implemented and verified.** Every scenario below is bound to a browser spec that exists and runs green.

## Scenario → evidence

| Scenario | Evidence | Status |
| --- | --- | --- |
| The variables of a Space are listed | `tests/browser/space-experiment.spec.ts::EXPERIMENT-02` (two declared ranges, each rendered with its low → high and its base) | passing |
| A variable is added | `tests/browser/space-experiment.spec.ts::EXPERIMENT-03` (POST carries name, unit and the three bounds) | passing |
| A variable is edited | `tests/browser/space-experiment.spec.ts::EXPERIMENT-04` (PATCH carries the edited range, the list rereads it) | passing |
| A variable is deleted | `tests/browser/space-experiment.spec.ts::EXPERIMENT-05` (DELETE, the range leaves the list) | passing |
| A blank name is refused | `tests/browser/space-experiment.spec.ts::EXPERIMENT-06` (no request leaves the browser, the field says why) | passing |
| An unordered range is refused | `tests/browser/space-experiment.spec.ts::EXPERIMENT-07` (90 / 50 / 10 refused locally, nothing sent) | passing |
| Nothing declared yet | `tests/browser/space-experiment.spec.ts::EXPERIMENT-02` (the runs, sensitivity and experiment lists each say they are empty) | passing |
| A run is declared | `tests/browser/space-experiment.spec.ts::EXPERIMENT-08` (POST carries the level, the assumptions and one value per declared variable) | passing |
| A run without assumptions is refused | `tests/browser/space-experiment.spec.ts::EXPERIMENT-09` (refused locally, nothing sent) | passing |
| The runs are read per Option | `tests/browser/space-experiment.spec.ts::EXPERIMENT-08` (the list is fetched for the Option the member chose) | passing |
| A run is deleted | No browser test yet; the control exists (a DELETE per run) — recorded under Known gaps | gap |
| The sensitivity read describes declared points | `tests/browser/space-experiment.spec.ts::EXPERIMENT-10`, `EXPERIMENT-11` | passing |
| The reading criterion is chosen by the member | `tests/browser/space-experiment.spec.ts::EXPERIMENT-10` (changing the direction triggers a new read carrying `direction=below`) | passing |
| Nothing to read yet | `tests/browser/space-experiment.spec.ts::EXPERIMENT-02` (the section says no run is declared) | passing |
| An experiment is created | `tests/browser/space-experiment.spec.ts::EXPERIMENT-12` (POST carries the chosen initiative, the Option, the title, the hypothesis and the success metric) | passing |
| A missing required field is refused | `tests/browser/space-experiment.spec.ts::EXPERIMENT-13` (refused locally, nothing sent) | passing |
| The expected range is set beside the observed outcome | `tests/browser/space-experiment.spec.ts::EXPERIMENT-16` (the expected target is rendered beside the recorded outcome) | passing |
| A proposed experiment is launched | `tests/browser/space-experiment.spec.ts::EXPERIMENT-14` (POST carries `running`, the status follows) | passing |
| A running experiment is completed | `tests/browser/space-experiment.spec.ts::EXPERIMENT-15` (POST carries `completed`, the composed draft Learning appears) | passing |
| A running experiment is abandoned | No browser test yet; the control is asserted present in `EXPERIMENT-14` — recorded under Known gaps | gap |
| Only permitted transitions are offered | `tests/browser/space-experiment.spec.ts::EXPERIMENT-14` (a proposed experiment offers launch, abandon and record-outcome, and nothing else) | passing |
| An outcome is recorded | `tests/browser/space-experiment.spec.ts::EXPERIMENT-16` (POST carries the metric, the value and the unit) | passing |
| A refusal is shown | `tests/browser/space-experiment.spec.ts::EXPERIMENT-17` (a 403 leaves the status unchanged and says so) | passing |
| No forecast anywhere in the section | `tests/browser/space-experiment.spec.ts::EXPERIMENT-18` (no score, rank, rating, forecast, prediction or probability node, and the read states it predicts nothing) | passing |
| A French section | `tests/browser/space-experiment.spec.ts` (the whole `fr` loop of the 19 scenarios) | passing |
| An English section | `tests/browser/space-experiment.spec.ts` (the whole `en` loop of the 19 scenarios) | passing |
| The section could not be read | `tests/browser/space-experiment.spec.ts::EXPERIMENT-19` (a 500 on the Options says so, the section stays framed) | passing |
| Scenarios and experiments stay inside their workspace | `tests/integration/test_scenario_analysis.py`, `tests/integration/test_experiments.py`, `tests/integration/test_experiment_space_links.py` (isolation, write permissions and the link rules are proved against a disposable PostgreSQL, not by mocked browser routes) | passing |

Command: `pnpm --dir apps/web exec playwright test` → **274 passed**, of which `tests/browser/space-experiment.spec.ts` contributes **38** (19 scenarios × FR/EN). The 22 tests of `tests/browser/decision-spaces.spec.ts` stay green, including the one that walks the six sections.

## Boundary evidence

- **Browser tests prove the UI only.** Every `/api/**` route is mocked, so these specs prove neither authentication, nor workspace isolation, nor the scenario and experiment rules, nor persistence. Those are proved by the API integration suites named in the last row above.
- **The section renders the controls and lets the API refuse.** The web has no space-scoped permission of its own, so a non-participant sees the same controls and a 403 is rendered as a readable refusal (`EXPERIMENT-17`). The authority is the API.
- **The API's experiment body is narrower than the ticket.** `ExperimentCreateBody` carries a title, a hypothesis, a success metric, a baseline and a target. The §10 fields *owner*, *budget*, *duration*, *guardrails* and *stop condition* do not exist in the API, so they are not drawn: inventing them in the screen would assert something nothing stores.
- **An experiment is created against an initiative.** `create_experiment` lives under `/ideas/{idea_id}/experiments`, so the form asks the member to choose the initiative that carries it and links the Space on the way. The Space has no stored initiative of its own, and guessing one would be a lie.
- **The Learning is read-only here.** Completing an experiment makes the API compose a draft Learning; the section shows it with its explanation and offers no confirmation. Confirming belongs to the Learning slice (#125).
- **Locale gate**: `node scripts/check_locales.mjs` → `FR/EN translation keys match, and all 926 catalog keys cover their usages.` (792 before this slice; 134 keys added in both locales).
- **Design-token gate**: `node scripts/check_design_tokens.mjs` → `Design tokens: apps/web/app uses only canonical tokens.`
- **UX coverage gate**: `node scripts/check_ux_coverage.mjs` → `coverage: ok`.
- **Lint and types**: `pnpm lint` and `pnpm typecheck` are clean.
- **Build**: `pnpm build` completes.
- **No API change**: no route, schema or migration was touched, so `contracts/openapi.json` and the generated client are unchanged and `make contract` is a no-op for this slice.
- **One operation is deliberately not surfaced**: `update_scenario_run` (editing a declared run) is not part of the ticket's acceptance, so the section offers creation and deletion only.

## Explicitly deferred (not gaps)

- Editing a declared scenario run (`update_scenario_run`) — the section offers creation and deletion; editing would need its own control.
- The §10 fields the API does not hold (owner, budget, duration, guardrails, stop condition) — they belong to an API slice before any screen draws them.
- Confirming the Learning composed at completion — #125.
- The Convergence Engine proposing variables, runs or experiments — `docs/00-project-overview.md` §13.
- Members and join requests — #126; the Decision Inbox — #127.

## Known gaps

- No browser test deletes a scenario run; the control exists and the API operation is proved in `tests/integration/test_scenario_analysis.py`.
- No browser test abandons a running experiment; `EXPERIMENT-14` asserts the control is offered, and the transition rule is proved in `tests/integration/test_experiments.py`.
