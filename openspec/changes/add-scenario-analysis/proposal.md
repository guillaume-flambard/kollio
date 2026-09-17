## Why

`docs/00-project-overview.md` §9 makes scenario analysis the initial promise and then forbids the obvious cheat: it is scenario analysis, NOT prediction. Nothing in Kollio currently holds the variables a decision turns on, the four scenarios a team reasons with, or the assumptions behind them, so the question §9 says the product should answer — "what would change our mind?" — has no home. §20 step 7 moves simulation under Options.

## What Changes

- Add scenario variables scoped to a Decision Space: a named quantity with a unit and an editable low/base/high range (§9 Level 2).
- Add scenario runs scoped to an Option: a declared level (`optimistic`, `base`, `pessimistic`, `failure`), required explicit assumptions, and a declared value per variable (§9 Level 1, applied at Level 2).
- Add a deterministic sensitivity read: given a criterion (a metric variable, a direction and a threshold), it reports, per other variable, the interval in which the criterion flips, how they rank by implied impact, and how much Evidence the Option carries. It never returns a point forecast.
- Keep everything under the Option, behind the existing Space permissions: members read, owner and participants write.

## Capabilities

### New Capabilities

- `scenario-analysis`: A team records what a decision turns on, states scenarios and their assumptions, and reads back what would change the preference — as intervals and rankings, never as a predicted number.

## Impact

Adds a `scenarios` vertical module (domain, adapters, service, api), one PostgreSQL migration with three tables, nine HTTP operations, regenerated OpenAPI types, and deterministic unit, PostgreSQL integration and evidence. No agent call: the Critic and the Scenario Analyst stay declared debts, and §9's "later only" list (probabilistic models, Monte Carlo, workspace priors, validated narrow predictive models) stays out.

Adds nine operations, removes none.

Tickets: GitHub #115 (this slice), step 7 of the `docs/00` §20 sequence.
