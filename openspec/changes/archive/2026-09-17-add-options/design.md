## Context

`docs/00-project-overview.md` §7 defines an Option by what it contains, and forbids summarizing alternatives in one AI score. §20 puts Options at step 5, after the converge map: a Space that can name its agreements, conflicts and assumptions can then name the paths it might take.

This design settles the Option as data and leaves the Critic to its own slice. §6's human-first precedent applies: structure first, machine critique after.

## Domain model

`Option` is a workspace-scoped row, reachable only through its Decision Space.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the parent Space; never null |
| `title` | text, required | the short label a list shows |
| `proposal` | text, required | the proposal itself, per §7 |
| `mechanism` | text, optional | how it would work |
| `upside` | text, optional | what we gain |
| `cost` | text, optional | what it costs |
| `risks` | text, optional | what could go wrong |
| `critical_assumptions` | text, optional | what must be true |
| `success_metrics` | text, optional | how we would know |
| `created_by` | reference, required | a Space writer |
| `lang` | code, required | language of the last write, as elsewhere |
| `created_at`, `updated_at` | timestamps | platform convention |

`OptionEvidence` links an Option to a confirmed Contribution on one side.

| Field | Kind | Notes |
| --- | --- | --- |
| `option_id` | reference, required | part of the primary key |
| `contribution_id` | reference, required | part of the primary key |
| `side` | closed value | `for` or `against` |
| `created_at` | timestamp | platform convention |

The composite primary key is what makes the same link twice impossible.

## Why evidence is a link and not a paragraph

§7 lists "Evidence For" and "Evidence Against" among the things an Option contains, and §21 asks that provenance beat polished prose. A paragraph would let an Option assert support that no Contribution backs, which is exactly the failure mode Converge exists to prevent. Linking to `confirmed` Contributions keeps the chain intact: Branch → Contribution → Option → Decision, each hop a real row.

Consequences worth stating:

- Only `confirmed` Contributions are linkable, so an AI suggestion cannot reach an Option without a human.
- `suggested` Contributions are invisible here, matching the map rule from step 4.
- A Contribution may support one Option and contradict another; the link carries the side, not the Contribution.

## Permissions

- **Read = any authenticated member of the owning workspace.** Everyone else gets the workspace-not-found treatment, as on every other object, so membership cannot be probed by identifier.
- **Write = owner plus participants**, for creating, editing, deleting, and for linking or unlinking evidence.

## Boundary

A new vertical module `apps/api/src/modules/options/` on the platform's lightweight hexagonal seam:

- `domain/` — the pure rules: is a side one of the two declared values, is a title or proposal usable, may this actor write. No I/O, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: list, read, create, update, delete, link evidence, unlink evidence.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints; schemas are the request/response boundary.

Operation shapes follow `modules/converge` and `modules/branches`: path nesting under the workspace and the Space, localized 404 keys, 422 for rule violations, 403 for a member who is neither owner nor participant.

## Persistence

One Alembic migration adding two tables:

- `options` — required Space FK, non-blank title and proposal checks, a closed `lang` check, the platform timestamps.
- `option_evidence` — composite primary key on `(option_id, contribution_id)`, a closed `side` check, cascade from both parents.

Facts proved on a disposable PostgreSQL, not in the browser: cross-Space isolation by identifier, the non-member refusal on every operation, that an unconfirmed or foreign Contribution cannot be linked, and that a duplicate link is refused and stores nothing.

## Deliberately out of scope

- The Critic and its six checks (unsupported assumptions, contradictory evidence, hidden dependencies, failure modes, causal claims, missing success criteria) — the next slice of §7, and the first one that needs a model.
- Any universal score or ranking, which §7 and §21 forbid outright.
- Choosing an Option, the Decision Record, rationale and revisit triggers (§20 step 6).
- Scenarios and simulation attached to Options (§20 step 7).
- Any user interface.

## Open questions

- Should an Option carry a status (`draft`, `viable`, `rejected`) before the Decision Record exists? Left out: `rejected` is a Decision outcome, and inventing a private status now would pre-empt step 6.
- Should the six Critic checks later attach as first-class rows with findings, or as one critique record per Option? Decide with the Critic slice, when the shape of a finding is known.
