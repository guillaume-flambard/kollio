# Agentic stack decision, September 2026

## Decision

Kollio uses one agent orchestration runtime and keeps infrastructure responsibilities separate:

| Responsibility | Choice | Reason |
| --- | --- | --- |
| Product API | FastAPI and Pydantic | Async HTTP boundary and strict request, response and model contracts |
| Agent orchestration | LangGraph | Durable checkpoints, streaming primitives and interrupt-based human review |
| Durable state | PostgreSQL and LangGraph PostgreSQL checkpointer | One transactional store for product data, workflow records and graph checkpoints |
| Semantic retrieval | pgvector | Shared relational and vector data until measured scale requires a separate service |
| Background dispatch | Taskiq with Redis Streams | Async-native worker that fits FastAPI and replaces maintenance-only ARQ |
| Model gateway | Self-hosted LiteLLM | Provider aliases, budgets, limits and OpenAI-compatible transport |
| Generation model | `b.ai / qwen3.8-flash` through the `kollio-default` alias | Preserves the audited provider while keeping the application provider-neutral |
| Embeddings | OpenAI `text-embedding-3-large`, 1,536 dimensions | One explicitly versioned FR/EN vector space |
| Observability | OpenTelemetry to Langfuse | Standard cross-process trace context and an agent-focused trace and evaluation UI |
| Evaluation | Deterministic validators, recorded fixtures, DeepEval and Langfuse datasets | Fast contract checks plus reviewed regression data |

## Explicit exclusions

Kollio does not add the OpenAI Agents SDK or a high-level LangChain agent loop. Both would duplicate orchestration, state and tracing already owned by LangGraph. The application may still use an OpenAI-compatible Responses API through LiteLLM when the selected provider supports the required contract.

Temporal remains outside the current architecture. LangGraph checkpoints plus a queue are enough for the present modular monolith. Temporal becomes relevant only if workflows expand beyond the graph into many independently deployed services, long timers or large fan-out that requires a general durable execution platform.

## Operational rules

- PostgreSQL owns workflow status and results. Redis transports commands and never becomes the source of truth.
- Taskiq retries failed jobs at most three times. The PostgreSQL workflow returns to its queued phase before each retry and becomes failed only after the retry budget is exhausted.
- Every queued command contains only a workflow identifier, a review decision when applicable and W3C trace context.
- Every model output is validated with strict Pydantic models before review or persistence.
- Every model and tool side effect is idempotent. Product writes retain a database uniqueness constraint.
- Human review resumes the same LangGraph thread and never starts a second model call.
- Langfuse datasets grow from reviewed production traces. Automated quality gates are calibrated only after enough human labels exist to measure false positives and false negatives.

## Primary references

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- [OpenAI Agents SDK runtime guidance](https://openai.github.io/openai-agents-python/)
- [LiteLLM proxy](https://docs.litellm.ai/)
- [LiteLLM OpenTelemetry integration](https://docs.litellm.ai/docs/observability/opentelemetry_integration)
- [Taskiq state and dependencies](https://taskiq-python.github.io/guide/state-and-deps.html)
- [ARQ repository maintenance status](https://github.com/python-arq/arq)
- [OpenTelemetry Python propagation](https://opentelemetry.io/docs/languages/python/propagation/)
- [Langfuse evaluation overview](https://langfuse.com/docs/evaluation/overview)
- [Langfuse datasets](https://langfuse.com/docs/evaluation/experiments/datasets)
