# Reuse confirmed learnings in the next analysis

## Why

The loop only pays when what one initiative learned reaches the next
one. Until now a confirmed learning was stored and never read back, no
content was ever embedded (the embedding table had no production writer),
and the similarity retrieval could read across workspaces because it
filtered on nothing but the model and the dimensions.

## What changes

- A confirmed learning is embedded with the same model and dimensions as
  an idea, its provenance carrying the workspace, the idea and the
  experiment ids.
- Retrieval is workspace-scoped: `similar_idea_ids` gains the viewer's
  workspace ids and filters through `ideas.workspace_id`, closing the
  cross-workspace leak.
- At analysis launch the nearest confirmed learnings of the viewer's
  workspaces enter the input as evidence entries (`learning:<uuid>`), and
  the snapshot records which ids were reused.
- Both hooks are best effort: a missing embedding provider degrades to
  the caller-supplied evidence instead of failing the run.

## Out of scope

- Embedding ideas in production: nothing writes idea embeddings yet, so
  the similar-ideas path is scoped and tested but still uncontributed.
- Ranking quality tuning (thresholds, reranking).
