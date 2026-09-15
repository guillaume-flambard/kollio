# Tasks

- [x] `data.py`: models, `DIMENSIONS`, `DIFFERENTIATORS`, `context_memory`,
  fixture loader; `fixtures/initiatives.json` with ~10 marketing initiatives and
  the Faktus memory.
- [x] `arms.py`: `arm_request`, `run_arms`, `run_benchmark` over an injected
  model.
- [x] `blinding.py`: deterministic seeded shuffle, blind document + separate key.
- [x] `scoring.py`: `aggregate` + `judge` verdict with a product-problem flag.
- [x] `__main__.py`: `run` / `sheet` / `score`, live opt-in guarded, replay from
  recorded outputs.
- [x] Offline unit tests: arms differ by memory/tier, blind sheet hides arms and
  is reversible, verdict wins and flags a product problem, fixture loads.
- [x] Docs note in `docs/08-conventions-and-testing.md`.
- [x] `make verify` green.
