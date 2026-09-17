## Context

`docs/00-project-overview.md` §3 makes the Decision Space the central object: one question requiring convergence, owned by a person, worked by participants, and carried through a fixed lifecycle whose end product is a confirmed Learning. §20 sequences the migration and puts this object second, after freezing new generic ideation.

This design settles only what step 2 needs: the object, its lifecycle, its privacy and write rules, and its history. Everything that consumes a Decision Space (Branches, Contributions, Converge, Options, Decision Record, Experiments, Learnings, Decision Inbox) is designed with its own capability and attaches later.

## Domain model

`DecisionSpace` is a workspace-scoped aggregate.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `workspace_id` | reference, required | the privacy boundary; never null |
| `question` | text, required | the one question to converge on; trimmed, non-empty |
| `description` | text, optional | the frame: what is at stake |
| `owner_id` | reference, required | the creator; a workspace member |
| `status` | closed value | `OPEN`, `EXPLORING`, `CONVERGING`, `READY_TO_DECIDE`, `DECIDED`, `TESTING`, `LEARNED`, `REOPENED` |
| `deadline` | date, optional | informational only; see below |
| `lang` | code, required | the language of the last write, as on ideas and iterations |
| `created_at`, `updated_at` | timestamps | platform convention |

`DecisionSpaceParticipant` joins a workspace member to a Space. The owner is always a participant, by construction.

`DecisionSpaceStatusEvent` is the append-only history: `from_status`, `to_status`, `actor_id`, `reason` (optional, required when reopening), `created_at`.

## Lifecycle

The blueprint declares the chain and the reopen escape; it declares nothing else. The accepted transition set is therefore exactly:

| From | To | Rule |
| --- | --- | --- |
| `OPEN` | `EXPLORING` | forward |
| `EXPLORING` | `CONVERGING` | forward |
| `CONVERGING` | `READY_TO_DECIDE` | forward |
| `READY_TO_DECIDE` | `DECIDED` | forward |
| `DECIDED` | `TESTING` | forward |
| `TESTING` | `LEARNED` | forward |
| `DECIDED`, `TESTING`, `LEARNED` | `REOPENED` | reopen, reason required |
| `REOPENED` | `EXPLORING` | work resumes |

Anything else is refused with a validation error and leaves the Space and its history untouched. The current status is the last history entry's `to_status`; the stored `status` column is a projection of that history, written in the same transaction.

Two consequences worth stating plainly, because they are choices and not oversights:

- **No backward step was invented.** Sending a Space back from `READY_TO_DECIDE` to `CONVERGING` is *not* in the declared set. The blueprint expresses going back as reopening a Decision, which only exists once a Decision does. If the product needs a gentler return before that, it is a separate, explicit decision (see Open questions).
- **`deadline` does not gate anything.** No transition is refused, and no state is skipped, because a date passed. Turning deadlines into triggers is part of step 9's Decision Inbox thinking, not of the object.

## Permissions

- **Workspace = privacy boundary.** Any authenticated member of the owning workspace may read and list. Everyone else receives the workspace-not-found treatment, identical to `company-context`, so membership cannot be probed by identifier.
- **Write set = owner plus participants** for status transitions.
- **Participant management = owner only.** A participant who is not the owner cannot add or remove participants, and the owner cannot be removed from their own Space.
- **Participants must be workspace members.** Adding an outsider is a validation error, not a silent no-op.

## Boundary

A new vertical module `apps/api/src/modules/decision_spaces/` following the platform's lightweight hexagonal seam:

- `domain/` — the pure transition rule (is this transition in the declared set?) and the reopen rule (is a reason present?), plus `access.py` for the read/write predicate. No I/O, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: create, read, list, transition, add/remove participant.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints; schemas are the request/response boundary.

Operation shapes (path nesting under the workspace, verb choices, error payload shape) follow the existing modules and are confirmed against `modules/company_context/api/routes.py` and `modules/ideas/api/routes.py` during implementation rather than invented here.

## Persistence

One Alembic migration adding three tables:

- `decision_spaces` — with a required workspace FK, a non-empty question check, a closed status check, and the platform's `lang` and timestamp columns.
- `decision_space_participants` — unique per `(space_id, user_id)`, which is what makes adding the same participant twice idempotent.
- `decision_space_status_events` — append-only; ordered by `created_at` and id; never updated, never deleted.

Facts proved on a disposable PostgreSQL, not in the browser: cross-workspace isolation by identifier, the non-member refusal on every operation, idempotent participant addition, and that a refused transition writes nothing.

## Deliberately out of scope

Each of these is a later step of `docs/00` §20, and naming them here keeps this change from quietly growing:

- Mapping existing Ideas into Branches and Contributions (step 3).
- Converge, the reasoning map (step 4) — and therefore the Decision Space screen, which exists to show it.
- Options and Challenge (step 5); the Decision Record with rationale and revisit triggers (step 6).
- Moving simulation under Options and Experiment (step 7); re-parenting Outcome and Learning, which today hang off an initiative (step 8).
- Home as Decision Inbox (step 9); integrations (step 10).
- Any user interface at all.

## Vocabulary collisions to settle in later slices

Recorded now so they are decisions rather than accidents:

- **`Branch` is taken.** In the current vocabulary a Branch is a line of iterations diverging from `main` (`apps/api/CONTEXT.md`). The blueprint reuses the word for a private or shared exploration under a Decision Space. Step 3 must decide whether exploration Branches reuse that concept or claim the word, and what the iteration branch becomes.
- **`Initiative` is the user-facing name of an Idea.** The blueprint gives the Decision Space its own user-facing identity, and step 3 decides how Ideas read once they are Branches and Contributions inside a Space.
- **`Outcome` and `Learning` already exist**, attached to an initiative through the experiment loop. Step 8 re-parents them to the Decision → Experiment → Outcome → Learning chain without losing the recorded learnings.

## Open questions

- Should `READY_TO_DECIDE` be able to return to `CONVERGING` before the Decision Record exists (step 6), and if so is that a transition or a reopen? Left out on purpose; revisit when the Decision Record lands.
- Should closing a Space (`LEARNED`) be reversible by reopening only, or should a Space be archivable independently of its lifecycle? Archival is not in the blueprint's state list, so it is not modelled here.
