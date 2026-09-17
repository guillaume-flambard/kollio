## 1. Deterministic domain

- [x] 1.1 Add failing unit tests for the candidate-finding rules: known kind, known severity, non-blank statement, citation membership.
- [x] 1.2 Implement the pure validation of a candidate finding and put it under strict Mypy.

## 2. Persistence

- [x] 2.1 Add the nullable `failure_reason` column to `challenge_runs` with its migration; keep existing rows readable.
- [x] 2.2 Add the adapter methods the worker path needs: load a run by id, fail a run with a reason, record the model on a run. Keep the adapter the only flusher.
- [x] 2.3 Run the migration on the disposable database and confirm `alembic check` reports no drift.

## 3. The Critic adapter and the queue

- [x] 3.1 Implement the declared `ChallengeGateway` against the model gateway: brief in, candidate findings out, one call per run, visible tier, structured output, OTel span, untrusted-content and locale clauses in the prompt.
- [x] 3.2 Implement the declared `ChallengeQueue` over Taskiq, mirroring the analysis queue adapter.
- [x] 3.3 Add the `challenge.execute` worker task, mirroring the analysis task's failure handling so a retrying failure is distinguished from a terminal one.

## 4. Execution

- [x] 4.1 Add failing tests for the execution path with a fake gateway: findings recorded as proposals with the critic origin, the model recorded, the run completed.
- [x] 4.2 Implement `execute_run` so validation happens before any write and a failure ends the run with a reason.
- [x] 4.3 Wire the route: opening a challenge dispatches the run, and a dispatch that cannot be queued fails the run.
- [x] 4.4 Register the challenge queue on the app state and provide the dependency the route injects.

## 5. Evidence and docs

- [x] 5.1 Integration tests on disposable PostgreSQL: dispatch on open, execution through a fake gateway end to end, a failed Critic leaving no findings and a readable reason, invalid results storing nothing, citations outside the brief refused, a human settling a Critic finding, no verdict in the read.
- [x] 5.2 Update the existing challenge tests with a queue override so they do not reach Redis, and keep their scenarios passing.
- [x] 5.3 Record scenario-to-test evidence in `acceptance.md` and name the recorded-fixture eval debt.
- [x] 5.4 Run Ruff, formatting, strict Mypy and the full suite.
- [x] 5.5 Record the vocabulary in `apps/api/CONTEXT.md` and note the execution path in `docs/05-data-model.md`.
