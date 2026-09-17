## Why

Kollio's shipped product still treats the Idea as the central object: users read Ideas, and iterations hang off them. `docs/00-project-overview.md` §5 moves ideation into exploration Branches whose raw material is not canonical, and §3 makes the Contribution the atomic canonical unit. §20 sequences this mapping third, after the Decision Space parent. Step 2 is done; this is step 3.

## What Changes

- Add a `Branch` exploration container under a Decision Space, private or shared, holding non-canonical raw material with full provenance.
- Map every workspace-scoped Idea to a Branch: the Idea's title, pitch and iteration history become the Branch's raw material, reachable through an explicit source link rather than duplicated.
- Add a `Contribution` canonical unit proposed from Branch material; AI may suggest, a human confirms, and the provenance (author, Branch, source, tool/model, timestamp, transformation history) is preserved.
- Disambiguate the two Branches: the iteration `branch` string (a legacy version-control line) and the exploration `Branch` entity (a container). The legacy line is not renamed here; it is read as the Branch's raw material.
- Public Ideas without a workspace have no parent Space and are explicitly out of scope; they belong to the Phase-2 public layer.

## Capabilities

### New Capabilities

- `branches`: Space members explore in private or shared Branches, map existing Ideas into them without losing history, and propose canonical Contributions from Branch material with human confirmation.

## Impact

Adds a `branches` vertical module (domain, adapters, service, api), one PostgreSQL migration with two tables, six HTTP operations, regenerated OpenAPI types, deterministic unit, PostgreSQL integration and no browser evidence (no screen ships with this change). No agent call and no breaking contract change: six operations are added, none removed, and the Idea read path is untouched.

Tickets: GitHub #110 (this slice).
