## Why

Kollio can display imported ideas and collaborators, but the product cannot yet record how an idea changes. Versioned iterations are the deterministic core of the product and must exist before agent analysis or richer collaboration can safely mutate an idea.

## What Changes

- Add append-only idea iterations with immutable snapshots, parent links, branches, short hashes, authors and timestamps.
- Let workspace members inspect iteration history.
- Let the idea owner append directly to the main branch.
- Let other workspace members create pending proposals on named branches.
- Let the owner accept or reject pending proposals.
- Let the owner restore an earlier snapshot by creating a new main-branch iteration.
- Protect concurrent writes with an expected-parent precondition.

## Capabilities

### New Capabilities

- `idea-iterations`: Workspace members can inspect and evolve an idea through an append-only version history.

## Impact

The change adds an `iterations` vertical module, one PostgreSQL migration, authenticated FastAPI endpoints, generated OpenAPI types and deterministic domain tests. It does not add an agent call or frontend behavior.
