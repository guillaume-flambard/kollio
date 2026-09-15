# Tasks

- [x] `domain/pipeline.py`: `StepName`, `STEP_ORDER`, `STEP_TASK_CLASS`,
  `PipelineStep`, `AnalysisRun`, `ordered_steps`, `require_synthesis_inputs`,
  `PipelineIncompleteError`.
- [x] Report schemas (Analyst, Challenger, Evidence, CompanyFit) in the domain.
- [x] `agent/pipeline.py`: `build_decision_brief` and `run_constraint_pipeline`
  with locale guard and enforcement.
- [x] `ConstraintReasoningGateway` protocol; the LiteLLM gateway implements the
  five task-class-routed calls and validates the synthesized result.
- [x] Graph analyze node runs the pipeline; state carries `steps`; worker
  persists `steps` / `draft_steps` and fails a non-retryable
  `PipelineIncompleteError`.
- [x] Migration `b6d24e8f1a07`.
- [x] Unit tests (order, tiers, one result, skip enforcement, routing) and the
  agentic E2E driving the real worker and gateway.
- [x] Docs (data model, architecture) and `make verify` green (160 API tests).
