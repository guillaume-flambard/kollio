# Tasks

- [x] Migration `3d9a1f4c7b20`: `learning_embeddings`, plus the JSON to JSONB alignment on `learnings.outcome_ids` that `alembic check` flagged.
- [x] Embeddings: learning record, model, store, and workspace-scoped retrieval for both learnings and ideas.
- [x] Experiments: embed on confirmation with workspace/idea/experiment provenance.
- [x] Launch: retrieve the nearest learnings of the viewer's workspaces and inject them as evidence.
- [x] Tests: confirmation writes a provenance-carrying vector; retrieval never crosses a workspace; the launch injects and records the reused ids.
- [x] Recorded eval fixture for reuse, offline.
