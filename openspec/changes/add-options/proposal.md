## Why

`docs/00-project-overview.md` §7 makes `READY_TO_DECIDE` arrive with real alternatives. Today a Decision Space can converge (relations, clusters) but carries no structured paths, so a commit would have nothing to choose between. §6's rule that trade-offs stay inspectable, and §21's ban on a universal AI score, both point the same way: Options as explicit, evidence-linked data before any Critic speaks.

## What Changes

- Add Options under a Decision Space: a short label, the proposal, and the fields §7 names (mechanism, upside, cost, risks, critical assumptions, success metrics).
- Make "Evidence For" and "Evidence Against" links to confirmed Contributions rather than free text, so a trade-off is inspectable down to its source.
- Let writers (owner plus participants) build, edit, link evidence on and remove Options; let every Space member read them.
- Refuse silently wrong evidence: an unconfirmed Contribution, one from another Space, or the same link twice.
- No universal score, no ranking, no AI. The Critic (the six checks and "what could make us regret this Decision?") is a later slice, and no screen ships yet.

## Capabilities

### New Capabilities

- `options`: Space members read the alternatives a Decision will choose between, each carrying the §7 fields and its evidence linked to the Contributions that support or contradict it.

## Impact

Adds an `options` vertical module, one migration with two tables, seven HTTP operations, regenerated OpenAPI types, and deterministic unit, PostgreSQL integration and contract evidence. No breaking contract change: seven operations are added, none removed. The Idea path and the converge map are untouched.

Tickets: GitHub #112.
