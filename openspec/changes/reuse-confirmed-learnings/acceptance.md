# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| A confirmed learning is embedded with workspace provenance | `tests/integration/test_learning_reuse.py`: the stored vector carries workspace, idea and experiment ids |
| Retrieval returns only the viewer's workspaces | the same test: the viewer's workspace returns its learning only, the other workspace returns its own, an empty set returns nothing |
| No cross-workspace leakage on the idea path | `tests/integration/test_foundations.py`: `similar_idea_ids` with an unrelated workspace set returns nothing |
| Launch injects the top learnings as evidence | the same reuse test: the workflow evidence carries `learning:<uuid>` and the snapshot records the reused id |
| An outsider cannot launch on another workspace's idea | the same test: not-found |
| Reuse pinned offline | `tests/evals/test_constraint_analysis_recordings.py`, `constraint_analysis.reuse.*`, no provider calls |

## Gaps

- The provider call is best effort and swallowed with a warning; the
  integration tests exercise the degraded path (no provider) except the
  reuse test, which stubs `embed`. A live run would confirm the real
  embedding quality.
- No production writer embeds ideas, so `similar_idea_ids` remains
  uncontributed outside tests; it is scoped and proven, not used.
- A learning from the same initiative is not excluded from its own
  launch, and no similarity threshold is applied: the top few are always
  injected when they exist.
- Ranking quality (thresholds, reranking, mixing weights with company
  context) is untuned.
