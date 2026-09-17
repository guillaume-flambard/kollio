## Why

Converge is the flagship differentiator (`docs/00` §6) and the MVP P0 explicitly requires the map — agreements, conflicts, alternatives, unknowns, assumptions, duplicates — plus human correction of convergence. Contributions exist as canonical units, but there is no map: no explicit relationships, no groupings, nothing to correct. This change makes the map real as human-built data. The AI proposer, which will suggest relations for humans to confirm, is a separate next slice; this one stays deterministic with no model calls, so every behavior below is unit-testable without evals.

## What Changes

- Add explicit `ContributionRelation` links between two Contributions of one Space, typed by the closed blueprint set: `SUPPORTS`, `CONTRADICTS`, `DUPLICATES`, `ALTERNATIVE_TO`, `DERIVED_FROM`, `SUPERSEDES`, `EVIDENCE_FOR`, `EVIDENCE_AGAINST`.
- Add `Cluster` groupings of Contributions inside one Space; a Contribution sits in at most one Cluster, and deleting a Cluster ungroups its members without deleting them.
- Expose the full map (Contributions with their relations and Clusters) as read data for one Space.
- Writers (owner plus participants) assert and remove relations and manage Clusters; workspace members read; everyone else gets the space-not-found treatment.
- No screen. The map ships as data; screens that render it come once real maps exist.

## Capabilities

### New Capabilities

- `converge-map`: Workspace members read a Decision Space's reasoning map — its confirmed Contributions, their explicit relationships and their Clusters — and the Space's writers build and correct that map by hand.

## Impact

Adds a `converge` vertical module (domain, adapters, service, api), one PostgreSQL migration with two tables plus one nullable column on `contributions`, seven HTTP operations, regenerated OpenAPI types, and deterministic unit, PostgreSQL integration and contract evidence. No agent call and no breaking contract change: seven operations are added, none removed.

Tickets: GitHub #111 (this slice).
