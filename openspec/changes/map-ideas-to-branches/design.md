## Context

`docs/00-project-overview.md` §5 preserves current Kollio ideation inside Explore: users create private or shared Branches with notes, AI outputs, URLs, documents, research and artifacts, and "Propose to shared space" converts selected material into Contributions that a human confirms. §20 maps "Current Idea → Branch or Contribution" as step 3. The product decision for this change is Idea → Branch: an Idea's content becomes a Branch's raw material, and Contributions are proposed from it. The word `Branch` is reused for the exploration container; the iteration `branch` string is the legacy line that the mapping reads as raw material.

This design settles only what step 3 needs: the two objects, the mapping rule, the propose flow, and their permissions. What consumes Contributions (Converge, Options, the screens) is designed with its own capability and attaches later.

## Domain model

`Branch` is an exploration container under a Decision Space. Its content is raw material and is never canonical.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the parent Decision Space; never null |
| `title` | text, required | trimmed, non-empty |
| `summary` | text, optional | the frame carried over from a mapped Idea's pitch |
| `source_idea_id` | reference, optional | the mapped Idea; the link that preserves history without duplicating it |
| `visibility` | closed value | `private`, `shared` |
| `created_by` | reference, required | a workspace member |
| `lang` | code, required | the language of the last write, as on spaces and ideas |
| `created_at`, `updated_at` | timestamps | platform convention |

`Contribution` is an atomic canonical unit proposed from Branch material: an idea, a claim, a piece of evidence, an objection or a constraint.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the parent Decision Space; never null |
| `branch_id` | reference, required | the Branch the material was proposed from; provenance, never null |
| `kind` | closed value | `idea`, `claim`, `evidence`, `objection`, `constraint` |
| `title` | text, required | trimmed, non-empty |
| `body` | text, optional | the selected material |
| `author_id` | reference, required | the human who proposed or confirmed |
| `source` | text, optional | URL, document or artifact reference |
| `tool_model` | text, optional | the AI tool and model, when known |
| `transformation_history` | structured, optional | what was selected, trimmed or reframed on the way in |
| `status` | closed value | `suggested` (AI), `confirmed` (human) |
| `lang` | code, required | the language of the last write |
| `created_at`, `updated_at` | timestamps | platform convention |

A human proposing material directly creates a `confirmed` Contribution. An AI suggestion creates a `suggested` one; a human confirming it flips the status to `confirmed` and records themselves as author. Only `confirmed` Contributions are canonical and will be consumed by Converge.

## Mapping rule

For every Idea with a `workspace_id`, the mapping creates one Branch under one Decision Space:

- The parent Space is created for the Idea: its question is the Idea's title, its owner the Idea's owner, its workspace the Idea's workspace, its language the Idea's language.
- The Branch carries the Idea's title, its pitch as summary, and `source_idea_id` pointing at the Idea. The Idea's iteration history is not copied; it stays in the iteration tables and remains reachable through the link.
- The Branch visibility is `shared`: a workspace Idea was already workspace-visible.
- The mapping is idempotent: an Idea with a Branch already pointing at it (`source_idea_id`) is skipped.

Ideas without a workspace (public) are not mapped. A Decision Space is workspace-scoped, so a public Idea has no parent; the public layer is Phase 2.

The Idea read path is untouched by this change. Ideas remain readable exactly as today; the Branch is an additional, pivot-native reading, not a replacement yet. Removing or redirecting the Idea path is a later step once Converge gives Branches a screen.

## Propose flow

"Propose to shared space" takes selected Branch material and a kind, and creates a Contribution:

1. The caller selects material from a Branch they can read and names a kind.
2. A human proposing creates a `confirmed` Contribution with themselves as author and the Branch, source, tool/model and transformation history recorded.
3. An AI suggestion creates a `suggested` Contribution; it becomes canonical only when a human confirms it, at which point the confirmer becomes the author.
4. Proposing from a Branch the caller cannot read is refused as if the Branch did not exist. Proposing an unknown kind or an empty title is a validation error that stores nothing.

## Permissions

- **Branch visibility governs read.** A `private` Branch is readable only by its creator. A `shared` Branch is readable by the Space's readers (workspace members).
- **Write follows the Space.** Adding material context, proposing and confirming follow the Space write rule: owner plus participants. A workspace member who is neither cannot write, and a non-member receives the workspace-not-found treatment.
- **Contributions inherit their Space.** A Contribution is readable by whoever can read its Space, and confirmable by whoever can write to it.

## Boundary

A new vertical module `apps/api/src/modules/branches/` following the platform's lightweight hexagonal seam:

- `domain/` — the pure mapping rule (is this Idea mappable?), the propose rule (is this kind/title valid, who confirms what?), plus `access.py` for the Branch visibility predicate. No I/O, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: create/read/list Branch, map Idea, propose/confirm/list Contribution.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints; schemas are the request/response boundary.

Operation shapes (path nesting under the workspace and space, verb choices, error payload shape) follow the existing modules and are confirmed against `modules/decision_spaces/api/routes.py` during implementation rather than invented here.

## Persistence

One Alembic migration adding two tables:

- `branches` — with required space and creator references, an optional source-idea reference, a non-empty title check, a closed visibility check, and the platform's `lang` and timestamp columns.
- `contributions` — with required space, branch and author references, a closed kind check, a closed status check, a non-empty title check, and the platform's `lang` and timestamp columns.

Facts proved on a disposable PostgreSQL, not in the browser: the mapping preserves every mappable Idea exactly once, a mapped Branch reads back its Idea's title and pitch, proposing stores full provenance, an AI suggestion is not canonical until confirmed, and cross-workspace isolation holds by identifier.

## Deliberately out of scope

- Consuming Contributions (clustering, merge/fork, the Converge map) is step 4.
- Any user interface at all, including the Branch screen and the propose button.
- Removing, redirecting or rewriting the Idea read path and its screens.
- Public Ideas, which have no workspace and therefore no parent Space.
- Re-parenting Outcome and Learning (step 8), which still hang off an initiative.

## Vocabulary

- **`Branch` (exploration container)** is the new entity defined here: a private or shared container of raw material under a Decision Space.
- **`branch` (iteration line)** is the legacy `branch` string on iterations (`main` plus proposal names). It is not renamed by this change; the mapping reads it as the Branch's raw material, and `apps/api/CONTEXT.md` records both senses.
- **`Contribution`** is the canonical atomic unit defined here. It must not be confused with the legacy `Contribution` named in the old Team-and-moat vocabulary (a participation record); that sense is re-pointed by step 8.

## Open questions

- Should mapping create one Space per Idea, or should several Ideas from one workspace share an exploratory Space until a real question emerges? This change creates one Space per Idea (one question per Space, faithful to §3); grouping is revisited if the Space list becomes noise.
- Should the Idea read path redirect to its Branch once Converge lands, or should Ideas remain a separate entry point? Left out on purpose; revisit with the Branch screen.
