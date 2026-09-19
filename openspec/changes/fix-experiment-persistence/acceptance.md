# Acceptance evidence - fix-experiment-persistence

Every mutating route of the experiments module answered with a complete object and stored nothing. `apps/api/src/platform/db.py` yields a session and closes it without committing, so each route that writes owns its commit; `options`, `converge`, `scenarios`, `challenge`, `branches`, `ideas` and `decisions` all do it, and `apps/api/src/modules/experiments/api/routes.py` was the only writer that never did. Each handler performs a `flush`, which is enough to assign the identifier and the timestamps, so the reply looked finished while the transaction was discarded when the session closed. Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| An experiment is created and read back | `apps/api/tests/integration/test_experiments.py::test_a_created_experiment_survives_the_request_that_created_it` fails against the routes without the commit (`1 failed`, `assert None is not None` at `tests/integration/test_experiments.py:226`) and passes after it; in the isolated environment the browser POST stored `fcad78f0-a878-4601-96e2-2fba21214ac9` with its `decision_space_id` and its `option_id` | Passing |
| An outcome is recorded and read back | the same environment stored `b1589505-4333-41e0-8219-0405798eaafa` (`Taux de réponse`, `4.8`, `%`), and the reloaded section renders `Observé` `4.8 %` with its comment | Passing |
| A confirmed learning is read back | the auto-composed draft `ba5cf462-72fe-4a8b-83be-43d5975b6db7` moved to `confirmed` with its author, and the Learning section lists it under its confirmed heading after a full reload | Passing |

## Verification runs (2026-09-19)

Live, in production, after the deploy: not observed. The change is committed on main and reaches the pilot host with the next image built from that commit; the pilot host is not the verification environment, so reading the record on the deployed site belongs to the delivery comment.

Local, before deploy:

- Before the fix: `TEST_DATABASE_URL=… uv run --project apps/api python -m pytest apps/api/tests/integration/test_experiments.py -k survives -q` reports `1 failed, 1 deselected`, the route answering `201` while the row stays absent.
- After the fix: the same file reports `2 passed in 11.31s`.
- `uv run --project apps/api python -m pytest apps/api -m 'not live' -q` against a disposable database reports `2 failed, 795 passed, 2 deselected in 273.40s`. Both failures are environmental: the agentic-runtime end-to-end test leaves its workflow `queued` because the worker it starts never drains (a path this change does not touch), and the ten-thousand-record CPU budget is missed by nine milliseconds under the Docker load while it passes when run alone.
- `uv run --project apps/api ruff check apps/api scripts`: `All checks passed!`.
- `uv run --project apps/api ruff format --check apps/api scripts`: `335 files already formatted`.
- In the isolated verification environment, the browser journey stored and then re-read all four records after the fix.

## Known boundaries

- The regression covers persistence for the create route. The status, outcome and learning routes are proven through the verification environment (a recorded outcome and a confirmed learning read back from the database and from the reloaded page), not by the integration test.
- The committed suite could not see this defect: its harness opens an outer transaction and injects one session per request, so a missing commit becomes a savepoint release and the final rollback hides it. A harness that owns the transaction cannot prove that the code commits.
- Records created before this fix are lost. They were acknowledgements of writes nobody stored, and nothing in the database can reconstruct them.
- The verification result was recorded without an observation date, because the date control refused tool interaction and the API accepts an empty `observed_at`; the stored record keeps a null observation date.
