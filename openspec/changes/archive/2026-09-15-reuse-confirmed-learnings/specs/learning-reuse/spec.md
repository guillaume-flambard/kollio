# Learning reuse

## Embedding a confirmed learning

When a member confirms a learning, it is embedded with the same model and
dimensions as an idea. Its provenance carries the workspace, the idea and
the experiment ids. Embedding failure is logged and does not fail the
confirmation.

## Scoped retrieval

Similarity retrieval takes the viewer's workspace ids and returns only
candidates whose idea belongs to one of those workspaces. An empty set
returns nothing. Confirmed learnings only.

## Launch injection

At launch, the initiative's title and pitch form the query; the nearest
confirmed learnings of the viewer's workspaces are appended to the launch
evidence as `learning:<uuid>` entries, labelled with a synthetic
`kollio://learning/<uuid>` URL. The snapshot records the reused ids. A
missing provider degrades to the caller-supplied evidence.
