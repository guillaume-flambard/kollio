# Tasks - fix experiment persistence

## 1. Commit the writes

- [x] 1.1 `POST /ideas/{idea_id}/experiments` commits before its response
- [x] 1.2 `POST /experiments/{experiment_id}/status` commits before its response
- [x] 1.3 `POST /experiments/{experiment_id}/outcomes` commits before its response
- [x] 1.4 `POST /experiments/{experiment_id}/learnings` commits before its response

## 2. Regress it

- [x] 2.1 A test writes an experiment through the API and reads it back from a new session
- [x] 2.2 The test fails against the routes that do not commit

## 3. Close with evidence

- [x] 3.1 Run ruff, the experiments integration file and the API suite without the live marker
- [x] 3.2 Replay the experiment in the verification environment and read the row back
- [x] 3.3 Write `acceptance.md` with the scenario to evidence mapping
