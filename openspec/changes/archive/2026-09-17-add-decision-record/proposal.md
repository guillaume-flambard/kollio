## Why

`docs/00-project-overview.md` §8 defines the Decision Record, and §3 states that a Decision is a committed choice with rationale, uncertainty and revisit triggers, versioned and append-only. Today a workspace can converge, build Options and challenge them, but nothing lets it commit — and nothing survives that commitment as a record.

This is step 6 of the §20 migration sequence. It is also the first step whose artifact must stand alone: §8 requires that a Decision Record make sense six months later without reopening the original AI chats, so the record carries its own alternatives, arguments, assumptions, criteria and triggers rather than pointing at live state.

## What Changes

- Add a versioned, append-only Decision Record per Decision Space: selected Option, rejected alternatives, strongest arguments for and against, critical assumptions, unresolved uncertainty, owner and reviewers, success criteria and revisit triggers.
- Committing a record requires the space to be `READY_TO_DECIDE` and moves it to `DECIDED` inside the same transaction, so the existing space history records who decided and when.
- Link arguments for and against to confirmed Contributions rather than free text, as Options already do for evidence, so a record cannot assert support nothing backs.
- Record rejected alternatives explicitly, which is what makes the record readable without the Option list of the day.
- Snapshot the reviewers at commit time so the record keeps its meaning when membership later changes.
- Validate revisit triggers as structured values (a metric, an optional direction and threshold, an optional note) so a later step can act on them; a paragraph would not be actionable.
- Leave the Critic to its own slice: Challenge coverage stays informational and gates no commitment, and the record states that plainly.

## Capabilities

### New Capabilities

- `decision-record`: A workspace commits a versioned, self-contained record of what it decided, why, with what uncertainty and what would bring them back.

## Impact

Adds a `decisions` vertical module (domain, adapters, service, api), one PostgreSQL migration with three tables, three HTTP operations, regenerated OpenAPI types, and deterministic unit, PostgreSQL integration and scenario evidence. No breaking contract change: three operations are added, none removed. No screen.

Tickets: GitHub #114 (this slice), #109 (parent epic).
