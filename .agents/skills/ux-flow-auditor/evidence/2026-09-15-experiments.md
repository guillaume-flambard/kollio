# Evidence record - Experiments / companion loop audit (2026-09-15)

## Identifiers

- `IdeaDetail.Experiments.Loop.Create` - locales fr, en - scenarios
  EXPERIMENT-01, EXPERIMENT-02
- `IdeaDetail.Experiments.Loop.Run` - locales fr, en - scenarios
  EXPERIMENT-03, EXPERIMENT-04, EXPERIMENT-05
- `IdeaDetail.Experiments.Loop.ConfirmLearning` - locales fr, en - scenarios EXPERIMENT-06
- `IdeaDetail.Experiments.Loop.HideFromNonMember` - locales fr, en - scenarios EXPERIMENT-07
- `IdeaDetail.Experiments.Loop.SurfaceRefusal` - locales fr, en - scenarios
  EXPERIMENT-08, EXPERIMENT-09

## Scenario result

`apps/web/tests/browser/experiments.spec.ts`: **18 passed (27.1s)**, single
clean run, one worker. EXPERIMENT-01 through EXPERIMENT-09 in fr + en. Raw
output: `evidence/2026-09-15-experiments.spec-output.txt` (non-empty).

- EXPERIMENT-02: create POST payload is exactly title/hypothesis/metric/baseline/
  target, and the row lands in `data-status="proposed"`.
- EXPERIMENT-04: the outcome POST payload carries metric/value/unit and nulls.
- EXPERIMENT-06: the learning POST sends `{ text, confirm: true }`.
- EXPERIMENT-07: a non-member sees no write form and no confirm control.
- EXPERIMENT-08/09: refused status action and list failure both surface
  `role="alert"`.

## Grounding checks

- **Locale:** `ideas.experiments.title`, `.empty`, `.newAction`, `.loadError`,
  `.retry`, `.ruleError`, `.status.*`, `.create.*`, `.actions.*`, `.outcomes.*`,
  `.learning.*` all resolve in fr and en.
- **Tokens:** `--ui-error` on every alert, `--ui-success` on completed status,
  `--kollio-active-ink` on running status, `--kollio-action` on the primary
  action.

## Findings

1. **Touch target below convention.** `.experiment-action`
   (`ExperimentLoop.vue:435`) sets `min-height: 40px`, under the 44px mobile
   convention used by the rail (`index.vue:267`). At 375px the experiment
   actions are the primary controls of the panel and are 4px short. RESP-375
   checks reachability only, not target size.
2. **Detail failure reuses the list error copy.** The detail error branch
   (`ExperimentLoop.vue:276`) shows `ideas.experiments.loadError` ("Experiments
   could not be loaded") for a single-experiment detail failure. The copy
   misdescribes the failing surface; there is no dedicated
   `ideas.experiments.detailLoadError` key.

## Verdict

All five experiment-loop flows AUDITED for fr and en.
