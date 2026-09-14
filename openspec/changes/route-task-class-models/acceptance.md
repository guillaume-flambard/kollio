# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| RT-01 class resolves to a model | `tests/unit/test_task_routing.py` `test_visible_classes_resolve_to_the_premium_model` and `test_commodity_classes_do_not` |
| RT-02 analysis is visible, extraction is not | `test_analysis_requests_the_visible_model` captures the outbound payload and asserts the premium model; `test_gateways_declare_a_visible_task_class` |
| RT-03 runs without premium credentials | `test_visible_falls_back_to_the_default_without_premium_credentials`; full `make verify` passes with `LLM_MODEL_VISIBLE` unset and no live calls (2 deselected `live` tests) |
| RT-04 observability | span attributes `kollio.task.class`, `kollio.task.tier`, `gen_ai.request.model` set in `constraint_analysis/adapters/litellm.py`, `platform/llm.py` and `platform/worker.py`; cost stays with LiteLLM/Langfuse, no pricing API in code |

## How to run

```
make verify
cd apps/api && uv run pytest tests/unit/test_task_routing.py -q
```

## Gaps

- No premium deployment is registered in `infra/litellm/config.yaml`: the
  operator points `LLM_MODEL_VISIBLE` at a named premium model when they have a
  key. Until then every class resolves to `kollio-default`, which is exactly the
  current behavior, so this slice is a safe no-op for the running demo.
- `resolve_model` covers the two live chat gateways. The embeddings path keeps
  its own `EMBEDDING` class in the enum for the moment a caller needs it; it is
  not yet routed because embeddings use a separate model today.
