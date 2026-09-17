## Context

`docs/00-project-overview.md` §6 defines Converge as a live map of collective reasoning that never collapses meaningful disagreement, and §18 requires relationships stored explicitly (not only embeddings), with human corrections as durable data. §20 sequences the migration and puts Converge fourth, first. Steps 2 and 3 delivered the parent Space, the exploration Branches and the confirmed Contributions this map reads.

This design settles only the human-built map: explicit relations, explicit clusters, and the map read. The AI proposer (candidate relations from embeddings and classification, confirmed by humans) attaches later as its own capability and never bypasses human confirmation.

## Domain model

`ContributionRelation` links two Contributions of one Space. Directed: `(from, to)` and `(to, from)` are distinct pairs.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the Space whose map this belongs to; never null |
| `from_contribution_id` | reference, required | one end of the link |
| `to_contribution_id` | reference, required | the other end; must differ from `from` |
| `relation_type` | closed value | `SUPPORTS`, `CONTRADICTS`, `DUPLICATES`, `ALTERNATIVE_TO`, `DERIVED_FROM`, `SUPERSEDES`, `EVIDENCE_FOR`, `EVIDENCE_AGAINST` |
| `created_by` | reference, required | the writer who asserted it |
| `created_at` | timestamp | platform convention |

One relation per ordered pair: `(from, to)` is unique. Changing a relation's meaning is delete plus create, so the map never holds two competing claims about the same directed pair.

`Cluster` groups Contributions of one Space for the map.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the Space whose map this belongs to |
| `title` | text, required | trimmed, non-empty |
| `created_by` | reference, required | the writer who grouped them |
| `created_at` | timestamp | platform convention |

Membership rides on a nullable `cluster_id` on `contributions`: a Contribution sits in at most one Cluster. Assigning moves (even from another Cluster). Deleting a Cluster nulls its members through `ON DELETE SET NULL`; Contributions are never deleted with it.

## Rules

- Both ends of a relation must be Contributions of the same Space named in the path; a cross-space pair is refused as not found, never leaked.
- No self-relation. Unknown relation types are refused.
- The map read returns the Space's confirmed Contributions (suggested ones are not canonical and stay out), every relation, and every Cluster with its member ids.
- Readers (workspace members) read the map. Writers (owner plus participants, the Space rule) assert/remove relations and manage Clusters. Non-members get the space-not-found treatment on every operation; unauthenticated callers get 401.

## Boundary

A new vertical module `apps/api/src/modules/converge/` following the platform's lightweight hexagonal seam:

- `domain/` — the pure relation rule (closed type set, no-self) and the access predicate. No I/O, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: map read, relation create/delete, cluster create/delete/assign/unassign.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints; schemas are the request/response boundary.

Operation shapes (path nesting under the Space, verb choices, error payload shape) follow the existing modules.

## Persistence

One Alembic migration adding two tables and one column:

- `contribution_relations` — with Space and Contribution FKs, the closed type check, a no-self check, and a unique constraint on `(from_contribution_id, to_contribution_id)`.
- `clusters` — with a Space FK and a non-blank title check.
- `contributions.cluster_id` — nullable FK to `clusters.id` with `ON DELETE SET NULL`.

Facts proved on a disposable PostgreSQL, not in the browser: the map round-trip, self/cross-space/duplicate/unknown refusals writing nothing, cluster move and delete-nulling, the non-member refusal on every operation, cross-workspace isolation by identifier.

## Deliberately out of scope

- The AI proposer (embedding candidates, relationship classification, incremental clustering). It will create `suggested` relations for humans to confirm and never writes canonical data directly.
- Promoting Alternatives into Options (step 5), merge/split operations beyond assign/unassign, and any screen rendering the map.
- Re-parenting Outcome and Learning (step 8).

## Open questions

- Should a directed pair ever carry two relation types at once (e.g. `DERIVED_FROM` plus `SUPERSEDES`)? Decided no for this slice: one claim per pair keeps the map readable; revisit if Converge practice demands it.
- Should Clusters carry a kind (agreement/conflict/alternative) or stay untyped groupings? Left untyped; typing is the proposer's job when it suggests groupings.
