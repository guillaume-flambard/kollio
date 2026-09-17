## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the variable rules: a name is required and trimmed, a range must be ordered `low <= base <= high`, and a duplicate name inside a space is refused by the adapter contract.
- [x] 1.2 Add failing unit tests for the run rules: the level is a closed set, assumptions are required and trimmed, and at most one `base` run exists per option.
- [x] 1.3 Add failing unit tests for the sensitivity computation: a flip inside a declared range interpolates exactly, no crossing reports `beyond_declared_range` with the travel direction, fewer than two points reports `insufficient_points`, several crossings report the narrowest interval and the count, runs missing the metric are excluded, variables rank by absolute slope, and no result path produces a single predicted value.
- [x] 1.4 Implement the pure rules and the computation with decimal arithmetic, under strict Mypy.

## 2. PostgreSQL persistence

- [x] 2.1 Add `scenario_variables` with a cascade from the space, a unique `(space_id, name)`, the ordered-range check and the closed `lang`.
- [x] 2.2 Add `scenario_runs` with a cascade from the option, the closed level, the `btrim` assumptions check and the partial unique index for one `base` run per option.
- [x] 2.3 Add `scenario_run_values` with a unique `(run_id, variable_id)` and cascades from run and variable.
- [x] 2.4 Implement the adapter: variables CRUD scoped to a space, runs scoped to an option, values written and replaced with the run, and the reads the sensitivity needs — the adapter is the only place that flushes.
- [x] 2.5 Register the models with Alembic, migrate a disposable database and confirm `alembic check` reports no drift.

## 3. HTTP contract

- [x] 3.1 Add localized authenticated operations for the variables: list, create, update, delete.
- [x] 3.2 Add localized authenticated operations for the runs: list by option, create with its values, read, delete.
- [x] 3.3 Add the sensitivity read, taking the metric, the direction and the threshold, returning intervals, slopes, ranking, incomplete runs and evidence counts.
- [x] 3.4 Refuse unknown or foreign variables, an unknown level, a blank name or assumptions, an unordered range, a duplicate name, a second base run and a duplicate value, all as validation errors that store nothing.
- [x] 3.5 Export OpenAPI, regenerate the TypeScript client and confirm the diff contains only additions.

## 4. Evidence

- [x] 4.1 Integration tests on disposable PostgreSQL: variable round-trip and every refusal, run round-trip with values, the one-base rule, a foreign variable refused, the deleted run taking its values, and the non-member, uninvolved and unauthenticated refusals.
- [x] 4.2 Integration tests for the sensitivity read itself: a straddling variable with its interval and interpolation, a non-straddling variable, a variable with one point, several crossings, an incomplete run excluded, the ranking order, the evidence counts, an option with no run, and an exact assertion that the response has no forecast field.
- [x] 4.3 Record scenario-to-test evidence in `acceptance.md` and mark anything deferred.
- [x] 4.4 Run Ruff, formatting, strict Mypy and the full suite.

## 5. Vocabulary and docs

- [x] 5.1 Add a Scenario analysis section to `apps/api/CONTEXT.md`: `ScenarioVariable`, `ScenarioRun`, `Scenario run level`, `Sensitivity read`, and the explicit statement that no model is fitted and no forecast is produced.
- [x] 5.2 Add the entity to `docs/05-data-model.md` and link the change to its tracker issue.
