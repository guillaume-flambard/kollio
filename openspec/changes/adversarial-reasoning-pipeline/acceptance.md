# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| AP-01 five ordered steps, one result | `tests/unit/constraint_analysis/test_pipeline.py` `test_pipeline_runs_the_steps_in_order_and_returns_one_result`; agentic E2E `test_api_worker_graph_and_checkpoint_complete_one_reviewed_analysis` |
| AP-02 cannot skip challenger or critic | `test_a_conclusion_cannot_drop_the_challenger_or_the_evidence_critic`; worker `except (UnsupportedLocaleError, PipelineIncompleteError)` records a non-retryable failure |
| AP-03 tier routing by task class | `test_pipeline_runs_the_steps_in_order...` asserts tiers `commodity, visible, visible, visible, visible`; `tests/unit/test_task_routing.py` `test_pipeline_routes_analyst_cheap_and_the_rest_premium` captures the outbound models |
| AP-04 steps persisted | agentic E2E runs the real worker through to review with the persisted `steps`; graph state returns `steps` and worker writes `constraint_analyses.steps` / `analysis_workflows.draft_steps` (migration `b6d24e8f1a07`) |
| AP-05 response shape unchanged | the synthesis path still returns `ConstraintAnalysisResult` validated by `validate_analysis_result`; the existing display and context integration tests pass unchanged |
| AP-06 no live provider | all of the above run offline (scripted gateway, fake OpenAI server, `LLM_MODEL_VISIBLE` unset path in `test_visible_falls_back_to_the_default_without_premium_credentials`); the two live evals stay deselected |

## How to run

```
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"
export TEST_DATABASE_URL=... REDIS_URL=...    # for the agentic E2E
make verify
cd apps/api && uv run pytest tests/unit/constraint_analysis/test_pipeline.py -q
```

## Gaps

- The synthesizer still receives the intermediate steps as data in one prompt;
  the adversarial value comes from the separate challenge and evidence passes,
  not from a debate loop. A fuller back-and-forth is #77's benchmark question,
  out of scope here.
- The per-step model names are recorded on each `PipelineStep`, but cost is
  accounted by LiteLLM/Langfuse at the model level; there is no per-step spend
  rollup in the app yet.
- No UI exposes the steps; they are audit data for now, matching "the member
  sees one analysis, never five agents".
