# Design

- `src/platform/task_class.py` owns the `TaskClass` StrEnum, the commodity set,
  `intelligence_tier` and `resolve_model(settings, task_class)`. It imports
  `Settings` only under `TYPE_CHECKING`, so config and platform stay acyclic.
- Two settings: `llm_model` (commodity) and `llm_model_visible` (visible).
  `resolve_model` returns the visible model for visible classes and falls back
  to `llm_model` when `llm_model_visible` is empty. Defaults are equal, so
  nothing requires a premium credential to run the loop locally or in CI.
- Each gateway declares a `ClassVar task_class`. The constraint-analysis
  `analyze` uses `REASONING` and the competition `assess` uses `CHALLENGE`, both
  visible tier; the model in the outbound payload comes from `resolve_model`,
  never from `settings.llm_model` directly. The worker stores the analysis with
  the same resolved model so the record matches the call.
- Observability: the model span sets `kollio.task.class`, `kollio.task.tier` and
  `gen_ai.request.model`; the worker span mirrors them. Cost per model stays
  with LiteLLM and Langfuse; no vendor pricing API is called from application
  code.
- The pin lives in a unit test that sets two distinct model names and asserts
  visible classes resolve to the premium one and commodity ones do not, plus a
  captured-request test that the analysis payload actually carries the visible
  model, and a fallback test that with no premium configured the whole thing
  still runs on the default.
