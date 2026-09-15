## Why

Kollio has a resumable LangGraph proof, but users cannot launch, inspect or review an analysis through the product API. The worker is disconnected from the modular monolith and its generic result is not linked to an idea or iteration.

## What Changes

- Add a constraint-analysis vertical module with persistent workflow and result records.
- Let workspace members launch an analysis for the current idea snapshot and inspect its status.
- Let the idea owner approve or reject a paused analysis.
- Dispatch work through a typed task-queue port and a Taskiq Redis adapter.
- Propagate W3C trace context from the API through the worker and LangGraph execution.
- Keep all model traffic behind LiteLLM and validate every model result with Pydantic.
- Record results against the analyzed idea and source iteration without mutating idea history.

## Capabilities

### New Capabilities

- `constraint-analysis-workflows`: Workspace-isolated, durable and reviewable constraint analysis for an idea snapshot.

### Modified Capabilities

- `phase-zero-integrations`: Replace the maintenance-only ARQ queue with an async Taskiq Redis adapter while preserving the existing Redis deployment.

## Impact

The change adds one vertical API module, PostgreSQL tables and migration, a typed LangGraph workflow, Taskiq worker integration, generated OpenAPI types, trace propagation and deterministic tests. It does not add autonomous side effects or frontend behavior.
