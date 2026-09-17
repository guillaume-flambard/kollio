## Why

Kollio's central object is still an Idea. The blueprint (`docs/00-project-overview.md`, §3 and §20) makes the Decision Space the parent of collective reasoning: one question a workspace must converge on, whose Explore → Converge → Options → Decision → Experiment → Learning loop produces the reusable Learnings that are the moat. No later slice of the pivot has anywhere to attach until that parent exists. Step 1 of the migration sequence (freeze generic ideation) is done; this is step 2.

## What Changes

- Introduce `DecisionSpace` as a first-class, workspace-scoped parent object: the question, its owner, its status, an optional deadline and description, and its participants.
- Enforce the lifecycle the blueprint declares — `OPEN` → `EXPLORING` → `CONVERGING` → `READY_TO_DECIDE` → `DECIDED` → `TESTING` → `LEARNED`, plus `REOPENED` with a recorded reason — and refuse every transition outside that set.
- Version every accepted status change append-only (from, to, actor, reason, timestamp). Committed history is never rewritten.
- Keep the workspace as the privacy boundary: members read, the owner and participants write, everyone else gets the workspace-not-found treatment.
- Record the language of the write on every row, as the platform already does for ideas, iterations and the company context.
- Expose additive HTTP operations (create, read, list, transition, manage participants), regenerate the OpenAPI client, and add one PostgreSQL migration.
- Record the new vocabulary in `apps/api/CONTEXT.md` and name the two collisions the pivot creates (`Branch`, and the Idea/Decision Space overlap during migration).

## Capabilities

### New Capabilities

- `decision-space`: Workspace members open and steer the question their team must decide, with a closed lifecycle, an owner, participants and an append-only status history.

## Impact

Adds a `decision_spaces` vertical module (domain, adapters, service, api), one PostgreSQL migration with three tables, five HTTP operations, regenerated OpenAPI types, vocabulary updates, and deterministic unit plus PostgreSQL integration evidence. No agent call, no screen, and no breaking contract change: operations are added, none removed.

No screen in this slice, deliberately. The blueprint forbids decorative surfaces (docs/00 §21), and a Decision Space screen whose Explore, Converge, Options, Decision, Experiment and Learning tabs are all empty would be exactly that. The screens land with the capabilities that fill them, starting with Converge (step 4).

Tickets: GitHub #109 (this slice is migration step 2 of `docs/00` §20).
