# Fix experiment persistence

## Why

Every mutating route of the experiments module answers with a complete object and stores nothing. `POST /ideas/{idea_id}/experiments` returns `201 Created`, `POST /experiments/{experiment_id}/status` returns `200`, and the outcome and learning routes do the same, but the row never reaches the database.

The cause is a single omission. `apps/api/src/platform/db.py` yields a session and closes it without committing, so every writing route owns its own commit: `options` commits in five places, `converge` in six, `scenarios` in six, `challenge` in four, `branches` in three, `ideas` in ten and `decisions` in one. `apps/api/src/modules/experiments/api/routes.py` is the only writing module with none. Each handler flushes, which is enough to assign the identifier and the timestamps, so the response looks finished while the transaction is rolled back when the session closes.

The pilot journey found it. A member created an experiment from the Expérience section of a decision space, the API answered `201 Created` with `{"id":"199dc901-870d-4201-8cc9-34ea8d4a46f0","decision_space_id":"7a50c0b2-151a-4319-8ecb-e77ca2a425f7","option_id":"fae705c2-2ddc-4587-8b15-f5672c4f979b","created_at":"2026-09-19T12:58:24.899328Z"}`, and `select count(*) from experiments` returned zero, checked both through `psql` and through the connection the API itself uses. The section therefore kept saying that no experiment existed for the space.

The integration suite could not see it. Its harness opens one connection, begins an outer transaction and injects that single session into the application, so a missing commit becomes a savepoint release and the rollback at the end of the test hides exactly this defect. The lesson is worth keeping: a harness that owns the transaction cannot prove that the code commits.

Until this is fixed, an experiment, an observed outcome and a confirmed learning cannot be recorded at all, which blocks the pilot verification the milestone depends on.

## What Changes

- Commit before the response in each of the four mutating experiment routes, as the other modules do.
- Add a regression that writes an experiment through the API and reads it back from a session opened afterwards, so the defect cannot return unnoticed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `experiment-loop`: add a requirement that a recorded experiment, outcome and learning survive the request that created them, so the API cannot acknowledge a record nobody stored.

## Impact

- `apps/api/src/modules/experiments/api/routes.py` and `apps/api/tests/integration/test_experiments.py`.
- No contract, migration, database or frontend change. No dependency and no secret.
- Records that were never stored are gone and cannot be reconstructed; the feature never persisted anything, so there is nothing to reconcile.

## Out of Scope

- Rebuilding the experiments a user believed they had recorded.
- Adding commits to modules that only read.
- Changing response shapes, error codes or the read-only role of the space experiment routes.
