## Why

`docs/00-project-overview.md` §10 makes the loop Decision → Experiment → Outcome → Learning the source of every reusable Learning, and §20 step 8 attaches it to the Decision Space. Today the loop hangs off an initiative alone: an experiment is created against an Idea and its learning is confirmed against that Idea, so a Decision Space cannot reach the Outcomes and Learnings that its own decision produced. Without that reach, §11's organizational memory has nothing to retrieve and §17's north-star metric (a Learning reused by another Decision Space) cannot be observed.

## What Changes

- Let an experiment belong to a Decision Space, and optionally to one of that space's Options, through nullable links. Existing experiments keep no link and are untouched: **no backfill, no rewrite, nothing removed**.
- Refuse a link that crosses workspaces: the space must belong to the idea's workspace, and the option to that space.
- Let a workspace member list a Decision Space's experiments and its learnings, learning included whether it is `draft` or `confirmed`.
- Keep the initiative path exactly as it is: the existing routes, payloads and specs continue to work unchanged.

## Capabilities

### Modified Capabilities

- `experiment-loop`: an experiment may additionally belong to a Decision Space and to one of its Options, and a Decision Space exposes its experiments and learnings to workspace members.

## Impact

Adds two nullable columns to `experiments` (one PostgreSQL migration, no data change), two optional fields on the create payload, two read operations and no changed operation: 2 added, 0 removed. No agent call, no screen, no vocabulary change to the existing loop. The Critic, the Memory Retriever and the Outcome/Learning re-parenting of the *idea* path remain later slices.

Tickets: GitHub #116 (migration step 8 of `docs/00-project-overview.md` §20).
