## Context

Ideas currently store only their latest title, pitch and stage. The data model already defines an iteration as an append-only snapshot with a parent, author, branch and proposal status. This change implements that model without introducing a generic event store.

## Goals / Non-Goals

**Goals:**

- Preserve every accepted and proposed idea snapshot.
- Keep the current `ideas` row as a query-efficient projection of the main branch head.
- Make concurrent edits explicit instead of silently overwriting a newer head.
- Keep authorization decisions deterministic and independently testable.

**Non-Goals:**

- Arbitrary merge conflict resolution.
- Multiple active proposals on the same branch.
- Agent analysis, comments, questions, evidence or notifications.
- Editing or deleting an existing iteration snapshot.

## Decisions

### Store complete snapshots

Each iteration stores the title, pitch and stage needed to reconstruct the idea at that point, plus the original language of its user-authored message. A monotonically increasing revision unique within the idea gives branch-head and history queries a deterministic order even when writes share a database timestamp. Complete snapshots make rollback deterministic and keep the first implementation understandable. Diff storage was rejected because it complicates reconstruction and migration without a measured storage problem.

### Use optimistic parent checks

Mutation requests provide the parent they observed. The service locks the idea, resolves the current branch head and rejects a stale parent with a conflict. This prevents lost updates without holding a transaction open across user interaction.

### Keep main writes owner-controlled

The owner may append to `main`. Other workspace members create a pending proposal on a named branch. The owner accepts a proposal by creating a new main iteration from its snapshot, or rejects it by changing only the proposal lifecycle status.

### Represent rollback as a new iteration

Rollback copies an earlier snapshot into a new main iteration whose parent is the current main head. No historical record is updated or removed.

## Migration Plan

1. Add the iterations table and constraints without fabricating history for imported ideas.
2. Deploy the API endpoints and generated contract.
3. Existing ideas begin history with their first product-authored iteration.
4. Rollback removes the new endpoints and table; existing idea projections remain valid.
