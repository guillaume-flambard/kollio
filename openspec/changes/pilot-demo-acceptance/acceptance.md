# Acceptance evidence

## The seed runs

- `tests/integration/test_seed_faktus.py` seeds twice with identical counts and
  resets to empty, against a real Postgres, rolled back.
- Verified by hand on a scratch database: `make seed-faktus` reports
  `workspace 1, members 2, objectives 3, constraints 3, principles 3, metrics 3,
  ideas 1`; a second run is identical; `make reset-faktus` clears it with no
  foreign-key errors.

## Demo path A–I

| Step | Interface action | Evidence |
| --- | --- | --- |
| A | Open the seeded company context | `test_seed_faktus`; settings checks `SETTINGS-01`, `ONBOARD-02` |
| B | Deposit an initiative with a closed type | `tests/integration/test_deposit.py`; browser `initiative-type`, deposit checks |
| C | Launch analysis with context injected | `tests/integration/test_analysis_context.py`; reuse fixture |
| D | Read Known / Assumed / Unknown + contradiction | recorded evals `constraint_analysis.*.json`; browser DEPOSIT-05 |
| E | Second person challenges, owner decides, history kept | `tests/integration/test_iterations.py`; browser `proposal`, `owner-actions`, `timeline` |
| F | Define an experiment | EXPERIMENT-02; `test_the_learning_loop_...` |
| G | Launch and record outcomes | EXPERIMENT-03, EXPERIMENT-04 |
| H | Complete and confirm the learning | EXPERIMENT-05, EXPERIMENT-06; the loop round-trip test |
| I | Later analysis reuses the learning | `test_confirmed_learnings_are_embedded_and_reused_within_the_workspace` |

## §15 acceptance checklist

Reconstructed from the brief's pilot loop (§14) and the #52 user stories; the
verbatim §15 was not in the repository, so this list is a reconstruction and is
labelled as such.

- [x] A workspace-private company context drives every analysis (C).
- [x] Analysis separates Known, Assumed and Unknown and refuses to score an
  unknown (D).
- [x] Analysis contradicts a stated objective or constraint explicitly (D).
- [x] A second person can challenge without overwriting; history is append-only
  (E).
- [x] A decision (accept) is recorded with its author (E).
- [x] The decision becomes a testable experiment with outcomes (F, G).
- [x] A confirmed learning is reusable by a later analysis, scoped to the
  workspace (H, I).
- [x] Team formation is dual-axis (participation and function) and owner-adds
  work without an application (from #57/#66; `test_team`, `test_workspace_members`).
- [x] The whole surface is bilingual FR/EN (`check_locales`; every browser check
  runs in both locales).
- [x] Nothing is visible outside the workspace (outsider-denied integration tests
  across ideas, context, members, experiments).
- [x] Onboarding seeds the context with partial answers, no CLI (ONBOARD-01..06).

## How to reproduce the demo locally

```
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"
export DATABASE_URL="postgresql+asyncpg://memo@localhost/<dev-db>"
export REDIS_URL="redis://localhost:63799/0"
make migrate
make seed-faktus            # stand up Faktus
make up                     # api + web + worker + gateway
# then walk A through I in the browser as the operator.
```

## Gaps and honest limits

- The brief's verbatim §13 Faktus content and §15 checklist are **reconstructed**
  from the committed fixtures and #52 stories, not transcribed from the client
  brief. The operator should overwrite the seed facts with Faktus's real words
  before showing it.
- Steps B, C and D as **live** actions need the configured model provider; their
  observable shape is pinned by the recorded evals, and comparative quality is
  still open (#77).
- The path is demonstrated by existing per-boundary tests plus the operator walk;
  there is no single live end-to-end automated run, by design (see design.md).
- The seeded members have no auth subject: the operator joins their own account
  to the workspace (or points a login at them) before the live demo.
