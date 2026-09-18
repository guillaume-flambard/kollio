# Tasks - harden the recorded evaluation corpus

## 1. Replay the recordings at the boundary

- [x] 1.1 Validate every gate recording with `GateFinding.model_validate` and `validate_finding`, using the identifiers the recording supplied
- [x] 1.2 Validate every constraint-analysis recording with `ConstraintAnalysisResult.model_validate`
- [x] 1.3 Prove the negative path on a mutated copy of a reviewed recording (swapped locale, unknown identifier, decided verdict without citations)

## 2. Guard the inventory

- [x] 2.1 Fail when a `fixtures/*.json` file is replayed by no test under `apps/api/tests/evals` or `apps/api/tests/unit`

## 3. Close with evidence

- [x] 3.1 Run `uv run ruff check .`, `uv run ruff format --check .` and `uv run pytest -m 'not live'` from `apps/api`
- [x] 3.2 Show that a temporarily mutated recording fails the new suite, then restore the file
- [x] 3.3 Write `acceptance.md` with the scenario to evidence mapping
