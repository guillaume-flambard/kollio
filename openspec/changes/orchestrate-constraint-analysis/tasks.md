## 1. Architecture decision

- [x] 1.1 Review the 2026 official documentation for LangGraph, OpenAI, LiteLLM, Langfuse, OpenTelemetry and async job queues.
- [x] 1.2 Record one orchestration runtime, one model gateway, one telemetry path and one queue boundary.

## 2. Deterministic workflow lifecycle

- [x] 2.1 Add failing tests for launch authorization, lifecycle transitions, stale review and idempotent dispatch.
- [x] 2.2 Implement strict domain models and typed ports without framework dependencies.

## 3. PostgreSQL persistence

- [x] 3.1 Add workflow and constraint-analysis tables linked to idea, source iteration and requester.
- [x] 3.2 Implement workspace-isolated workflow reads and transactional state changes.
- [x] 3.3 Verify retries do not duplicate workflows or final results.

## 4. Agent and queue runtime

- [x] 4.1 Move the constraint prompt, schemas and graph into the vertical module.
- [x] 4.2 Replace ARQ with a Taskiq Redis adapter and update the worker image command.
- [x] 4.3 Propagate W3C trace context from API enqueue through worker execution.
- [x] 4.4 Verify PostgreSQL checkpoint pause and resume with the requested locale.

## 5. HTTP contract

- [x] 5.1 Add authenticated launch, status and owner review endpoints.
- [x] 5.2 Export OpenAPI, regenerate the TypeScript client and verify no contract drift.

## 6. Evaluation and quality

- [x] 6.1 Extend recorded fixtures for the full five-factor schema and deterministic validators.
- [x] 6.2 Run Ruff, strict Mypy, unit and PostgreSQL integration tests.
- [x] 6.3 Validate the OpenSpec change strictly and document remaining live-provider evidence.

## 7. Failure simulation and regression coverage

- [x] 7.1 Reject incomplete production identity, model gateway and telemetry configuration at startup.
- [x] 7.2 Simulate queue dispatch outages and prove idempotent launch and review recovery.
- [x] 7.3 Exercise API, Redis Streams, Taskiq, LangGraph and PostgreSQL through one provider-free E2E scenario.
- [x] 7.4 Run deterministic web behavior tests in the required CI job.

## 8. Performance regression gates

- [x] 8.1 Guard workspace idea pagination against N+1 queries and excessive local latency.
- [x] 8.2 Enforce compressed JavaScript, compressed CSS and static image budgets after the production web build.
- [x] 8.3 Guard strict agent-result validation throughput on the CPU hot path.
