## Why

`docs/00-project-overview.md` §4 makes Home a Decision Inbox that answers "What needs my attention?", and §17 counts convergence completion, time to Decision, Outcome capture and repeat Decision Spaces as the supporting metrics. Today no read answers that question: a person must open each Decision Space to discover that it is waiting on them, so the loop that makes the product worth returning to has no entry point.

## What Changes

- Add a member-scoped inbox read that gathers, across every workspace the reader belongs to, what currently waits on them.
- Sections carried by this slice: needs convergence, needs my input, ready to decide, needs learning.
- Derive every entry from data that already exists: Space status, Space participation, suggested Contributions, proposed Challenge findings, committed Decisions, experiments and Learnings. No new state is stored.
- Order each section oldest first, and bound it with a limit, because an inbox that cannot be skimmed does not get read.
- Keep it read-only: no writes, no migration, no change to any existing operation.
- The fifth §4 section, relevant prior memory, is **not** shipped: its source is the memory retriever, which does not exist yet. The response does not pretend to answer it.

## Capabilities

### New Capabilities

- `decision-inbox`: A member asks what needs their attention and receives the waiting work across their workspaces, sectioned as §4 describes.

## Impact

Adds a read-only `inbox` vertical module (domain rules, one adapter read, one service, one operation). No migration, no table, no write path, and no existing operation changes: one operation is added, none removed. Deterministic unit tests plus PostgreSQL integration tests, and no screen.

Tickets: GitHub #117 (this slice, step 9 of §20).
