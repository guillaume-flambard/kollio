# Design

## Decisions

- `learning_embeddings` mirrors `idea_embeddings` (composite primary key
  on the subject, the model and the dimensions; provenance JSONB) rather
  than generalising one table, so the existing shape, its migration and
  its test stay untouched.
- Retrieval takes the viewer's workspace ids explicitly instead of a
  subject: the scoping decision is made by the caller, which already
  resolved the identity, and the query stays a plain equi-join.
- Both the confirmation hook and the launch hook swallow provider
  failures with a warning: reuse is an enhancement, and a launch must not
  fail because an embedding endpoint is down. The snapshot records
  `reused_learning_ids`, so the skip is observable from the run.
- The launch embeds the initiative's title and pitch as the query text;
  ideas are not embedded in production yet, so this is the honest way to
  rank learnings for a new initiative today.
- Evidence entries carry `id=learning:<uuid>` and a synthetic
  `kollio://learning/<uuid>` URL, since a learning has no public URL; the
  model only ever cites the id, which the validator checks.
