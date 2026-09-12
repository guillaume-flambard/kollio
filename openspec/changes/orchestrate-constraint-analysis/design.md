## Context

The current graph proves PostgreSQL checkpoint resume and Pydantic validation, but its prompt, state and persistence dependencies point across generic `agents` and `platform` packages. The product needs an explicit workflow lifecycle before adding more tools, streaming or additional agents.

## Goals / Non-Goals

**Goals:**

- Make an analysis a workspace-scoped product resource with an explicit lifecycle.
- Preserve the exact idea snapshot, source iteration and locale used for a run.
- Resume human review after process restarts through the PostgreSQL checkpointer.
- Keep queue, model and persistence implementations replaceable at narrow boundaries.
- Preserve one distributed trace across API, queue, graph and model calls.

**Non-Goals:**

- Autonomous writes to an idea or its iteration history.
- Token streaming or WebSockets.
- Multi-agent handoffs or a second orchestration framework.
- Calibrated quality thresholds before enough human-reviewed examples exist.

## Decisions

### Keep LangGraph as the only agent runtime

LangGraph already provides durable checkpoints and interrupt-based human review. Adding another agent runtime would create two competing state and tracing models. Product-specific graph code moves into the constraint-analysis module; shared infrastructure remains under `platform`.

### Replace ARQ with Taskiq behind a queue port

ARQ is in maintenance-only mode. Taskiq supports native async tasks, FastAPI integration and Redis-backed brokers. The application service depends on a minimal `AnalysisQueue` protocol, so the product lifecycle is independent of Taskiq and can migrate again without changing domain behavior.

### Persist workflow state outside the queue

Redis transports commands only. PostgreSQL stores workflow status, immutable input snapshots, source iteration, review metadata, failures and final results. A queue retry therefore observes the same durable product record and cannot create a second workflow.

### Use explicit lifecycle transitions

The lifecycle is `queued`, `running`, `awaiting_review`, `completed`, `rejected` or `failed`. Pure transition rules reject stale or repeated review decisions. The worker updates state transactionally around graph execution.

### Propagate standard trace context

The API injects W3C trace context into the queued command. The worker extracts it before opening its span. LangGraph nodes and LiteLLM calls remain children of that context, allowing Langfuse to display one end-to-end trace through its OpenTelemetry ingestion.

### Treat model output as an untrusted boundary

The model returns a strict Pydantic schema containing an overall score, a verdict and five named constraint factors. Validation rejects unknown sources, wrong locales, missing factors and scores outside the accepted range before a result can be reviewed or stored.

## Migration Plan

1. Add workflow and analysis tables without changing existing idea rows.
2. Deploy the Taskiq worker and API launch, status and review endpoints.
3. Remove the ARQ runtime after the Taskiq worker passes the same checkpoint-resume test.
4. Rollback restores the previous worker image and removes the new endpoints and tables; idea and iteration data remain unchanged.
