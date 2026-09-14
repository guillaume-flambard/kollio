# Tasks

- [x] `TaskClass`, commodity set, `intelligence_tier`, `resolve_model` in
  `src/platform/task_class.py`.
- [x] Settings: `llm_model` (commodity) plus `llm_model_visible` (visible,
  defaults to empty).
- [x] Constraint-analysis gateway declares `REASONING`; competition gateway
  declares `CHALLENGE`; both request the resolved model.
- [x] Worker stores the analysis with the resolved model; spans carry task class
  and `gen_ai.request.model`.
- [x] `.env.example` documents both keys.
- [x] Architecture note on the routing.
- [x] Unit pin test: visible vs commodity resolution, the captured analysis
  request, and the no-premium fallback.
- [x] `make verify` green (158 API tests).
