## Context

`docs/00-project-overview.md` §8 lists what a Decision Record contains, §3 fixes its lifecycle meaning (a committed choice, versioned and append-only, reopenable by new evidence, outcomes or predefined triggers), and §20 puts it sixth, after Options and Challenge and before simulation, Outcome/Learning and the Decision Inbox.

The space lifecycle already exists (`add-decision-space`, step 2): `READY_TO_DECIDE` → `DECIDED` is a declared forward edge, and reopening (`DECIDED` → `REOPENED`, reason required) is the declared way back. Options (`add-options`, step 5) and Challenge runs (`add-challenge`, step 5) already exist and are read by this design.

## Domain model

`Decision` is a versioned, append-only record belonging to a Decision Space.

| Field | Kind | Notes |
| --- | --- | --- |
| `id` | identity | server-generated |
| `space_id` | reference, required | the space it commits |
| `version` | integer, required | starts at 1 and increments per space; unique per `(space_id, version)` |
| `selected_option_id` | reference, required | an Option of the same space |
| `rationale` | text, required | why this option; trimmed, non-blank |
| `critical_assumptions` | text, optional | what must stay true |
| `uncertainty` | text, optional | what remains unresolved, stated rather than hidden |
| `success_criteria` | text, optional | what would count as working |
| `revisit_triggers` | jsonb list, optional | structured triggers, see below |
| `reviewer_ids` | jsonb list, required | snapshot of the space participants at commit time |
| `decided_by` | reference, required | the actor who committed |
| `lang` | code, required | the language of the write, as everywhere else |
| `created_at` | timestamp | platform convention |

`DecisionRejectedAlternative` joins a record to the Options it did not take: `(decision_id, option_id)`.

`DecisionArgument` joins a record to the confirmed Contributions it rests on: key `(decision_id, contribution_id)`, with `side` as a required column carrying `for` or `against`. The side is deliberately not part of the key: one Contribution arguing both for and against the same decision is a contradiction, not a nuance, so the model refuses it rather than storing it twice.

## Revisit triggers

A trigger is an object, not prose: `metric` (required, non-blank), `direction` (optional, `above` or `below`), `threshold` (optional, non-blank when present), `note` (optional). A trigger may carry a metric alone — that is a reminder to look, and it is honest about being one. §9's useful output is "B becomes preferable if CTR exceeds X", and §17 counts decisions that carry triggers, so a paragraph would satisfy neither.

## Lifecycle coupling

Committing is the only way a space reaches `DECIDED`, and it does so through the existing declared edge:

- `commit_decision` requires the space to be `READY_TO_DECIDE`. Any other status refuses with a validation error and writes nothing — no record, no status event.
- On success, one transaction writes the record and appends the `READY_TO_DECIDE` → `DECIDED` status event through the existing decision-space adapter, so the space history stays the single account of who moved it and when.
- Reopening stays where it is: `transition_decision_space` to `REOPENED` with a reason. A re-decided space then takes a new record version.

This answers the open question left in `add-decision-space`'s design ("should `READY_TO_DECIDE` return to `CONVERGING` before the Decision Record exists?"): **no.** The declared return path is reopening, and now that a record carries revisit triggers, a team that wants to keep converging has a recorded reason to reopen rather than a silent backward step.

Option status (`draft`/`viable`/`rejected`) stays absent for the same reason it was deferred: rejection is recorded per decision in `decision_rejected_alternatives`, and an Option-level status would be a second, weaker account of the same fact.

## Self-containment

§8's test is that the record makes sense six months later. Two consequences are deliberate:

- **Arguments are links, not text.** "Strongest arguments for/against" references confirmed Contributions of the same space. Rewriting them as prose would let a record assert support that no Contribution carries, which is exactly the failure the Option design refused for evidence.
- **Reviewers are a snapshot.** The participants at commit time are copied onto the record instead of joined live, because a live join would silently rewrite who reviewed a past decision when membership changes. The alternative (a join table) was rejected: the list is frozen at write time and never queried across records.

## Boundary

A new vertical module `apps/api/src/modules/decisions/` following the platform's lightweight hexagonal seam:

- `domain/` — pure rules: trigger shape, record field validation, access predicates. No I/O, under strict Mypy, unit-tested without a database.
- `adapters/postgres.py` — the only place that touches the ORM or flushes.
- `service/` — orchestration: read the current record, list versions, commit.
- `api/routes.py`, `api/schemas.py` — localized, authenticated endpoints.

## Persistence

One Alembic migration adding three tables:

- `decisions` — required space FK, unique `(space_id, version)`, non-blank `rationale` check, closed `lang` check.
- `decision_rejected_alternatives` — composite primary key `(decision_id, option_id)`.
- `decision_arguments` — composite primary key `(decision_id, contribution_id)`, required `side` with a closed `for`/`against` check, cascades from the record and the Contribution.

Append-only is enforced by omission: no update and no delete operation exists in the adapter.

## Deliberately out of scope

- The Critic's model slice. `add-challenge` shipped the checks as data with a declared port and no implementation; commitment today does not require a Critic run, and the record says nothing it cannot support. Revisit when the Critic lands, at which point the record's coverage line becomes meaningful.
- Simulation under Options and Experiment (§20 step 7): §9 stays untouched.
- Outcome and Learning (§20 step 8), and therefore any link from a record to what actually happened.
- Home as Decision Inbox (§20 step 9) and integrations (§20 step 10).
- Any user interface. The Decision Record screen belongs with the screens slice.

## Open questions

- Should a record be immutable forever, or should a later slice allow annotating a version with its Outcome without editing it? Left open on purpose: §20 step 8 owns that link.
- Should `reviewer_ids` be constrained to workspace members at read time (a stale id is not an error today)? Left open: the snapshot is a record of the past, so filtering it would falsify it.
