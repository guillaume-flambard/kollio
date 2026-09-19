# Design - fix experiment persistence

## Context

`apps/api/src/platform/db.py` yields a request session and closes it without committing, so each route that writes owns its commit. The convention is visible across the API: `options` commits in five places, `converge` in six, `scenarios` in six, `challenge` in four, `branches` in three, `ideas` in ten and `decisions` in one. `apps/api/src/modules/experiments/api/routes.py` has four mutating routes and none of them commits: `POST /ideas/{idea_id}/experiments`, `POST /experiments/{experiment_id}/status`, `POST /experiments/{experiment_id}/outcomes` and `POST /experiments/{experiment_id}/learnings`.

Each of the four answers after a flush, which assigns the identifier and the timestamps, so the response body is complete and the client has no way to tell that nothing was stored.

The existing integration test cannot catch this. Its harness opens one connection, begins an outer transaction and injects that single session into the application, so the missing commit is replaced by a savepoint release and the final rollback hides it.

## Goals / Non-Goals

**Goals:**

- An experiment, an outcome and a confirmed learning written through the API are readable from a session opened after the request that wrote them.
- The regression fails against the routes that do not commit.
- Nothing else changes: same responses, same errors, same authorization.

**Non-Goals:**

- Recovering records that were never stored.
- Adding commits to modules that only read, or moving commit responsibility into the adapters.
- Changing the read-only role of the space experiment routes.

## Decisions

### Commit in the route, before the response

The commit goes where the other modules put it: after the service call and before the response is built. Committing inside the adapter would move transaction ownership into the persistence layer, which this codebase deliberately keeps in the routes, and it would commit boundaries the callers do not expect.

### Regress with a real session factory

The harness that hides the defect is the one that must not be reused. The regression builds the application with `async_sessionmaker(engine, expire_on_commit=False)` and yields a fresh session per request, seeds and commits in its own session, writes the experiment through the API, then reads it back from a new session. That is the smallest test that proves a write survived its request.

### Clean up explicitly

The verification database is shared, so the regression deletes, in order, the experiments of the seeded idea, the idea, its memberships, its users and its workspace.

## Migration Plan

1. Add the four commits.
2. Add the regression and watch it fail against the unfixed routes.
3. Run the API checks: `ruff check`, `ruff format --check`, the experiments integration file with `TEST_DATABASE_URL`, and the suite without the live marker.
4. Replay the experiment in the verification environment and read the row back from the database.

Rollback: revert the commit. There is no migration, no contract and no data to repair.

## Risks

- The four routes now commit before the response is built, so a failure while building the response would leave the write durable. That is already the behaviour of every other module and the correct one here: the record exists because the user asked for it.
- Experiments created before this fix were never stored. A user who believes they recorded one will not find it, and the issue says so rather than pretending the data is somewhere.
