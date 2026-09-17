## Context

§4 defines Home as a Decision Inbox with five sections. §20 puts it ninth, after the objects each section reads: Spaces (step 2), Contributions (step 3), the converge map (step 4), Options and Challenge (step 5), the Decision Record (step 6), scenarios (step 7) and the experiment link (step 8). All of those exist, so every section except one can be derived from stored data.

This design settles only the read: what waits on whom, from which rows, and in which order. The Home screen, notifications, digests and the memory retriever belong to their own slices.

## What the inbox is

A read scoped to the asking member, across every workspace they belong to. It stores nothing: every entry is a projection of an existing row, so it cannot drift from the state it reports.

## Sections

| Section | Entry source | Condition | Scope |
| --- | --- | --- | --- |
| `needs_convergence` | Decision Space | `status = 'CONVERGING'` | Spaces of the reader's workspaces |
| `needs_my_input` | Contribution | `status = 'suggested'` | Spaces where the reader is owner or participant |
| `needs_my_input` | Challenge finding | `status = 'proposed'` | Spaces where the reader is owner or participant |
| `ready_to_decide` | Decision Space | `status = 'READY_TO_DECIDE'` **and** no committed Decision | Spaces of the reader's workspaces |
| `needs_learning` | Experiment | `status = 'completed'` **and** no recorded Outcome | Spaces of the reader's workspaces |
| `needs_learning` | Learning | `status = 'draft'` | Spaces of the reader's workspaces |

Two scopes are deliberate and different. Convergence and a Decision are the team's, so workspace membership is the right boundary. A suggested Contribution or a proposed finding is a specific person's decision to confirm or dismiss, so it appears only to the owner and the participants of that Space — the same people the write rule already allows.

`ready_to_decide` excludes a Space that already holds a Decision, because committing one is what moves it to `DECIDED`; the exclusion covers the window where a Space sits in `READY_TO_DECIDE` with its Decision already committed and then reopened. It is a guard against a duplicate prompt, not a second source of truth.

## Shape

One operation, `read_decision_inbox`, at `GET /inbox`, authenticated, with an optional `limit` per section (default 20, bounds 1 to 50, outside which the request is refused as invalid).

Each entry carries the workspace, the Space, the Space question, the Space status, a `kind` naming why it is here, the `subject_id` when the entry is about one row (a Contribution, a finding, an experiment or a Learning), an optional `detail` for the client to render without a second read, and `created_at` — the age of the thing waiting.

Sections are ordered oldest first, tie-broken by id, so the longest wait is at the top. Each section is capped by `limit`, and the read is honest about the cap: it reports the total per section alongside the entries, so a client can say "20 of 43" instead of silently truncating.

`needs_my_input` merges two kinds into one list; the `kind` field tells them apart.

## The section that is not shipped

`relevant_prior_memory` is absent from the response. Its source is the memory retriever that surfaces past confirmed Learnings with provenance (§11), which is not built. Returning an empty list under that key would read as "you have no relevant memory", which is a claim nothing supports today. Leaving the key out says the truth: this slice answers four of the five questions. The retriever adds the fifth with its own spec.

## Boundary

A new read-only module `apps/api/src/modules/inbox/`:

- `domain/sections.py` — the pure predicates (does this status need convergence, does this experiment need an outcome, does this learning wait for confirmation, is this Space the reader's to answer) plus the ordering key. No I/O, under strict Mypy, unit-tested with no database.
- `adapters/postgres.py` — the reads, cross-module and read-only: it selects from the tables the other modules own and flushes nothing.
- `service/inbox.py` — resolves the reader's workspaces and participant Spaces, then assembles the sections.
- `api/routes.py`, `api/schemas.py` — the one authenticated operation and its boundary shapes.

## Persistence

None. No table, no column, no migration. `alembic check` must keep reporting no drift, and that is itself evidence that the slice added no state.

## Deliberately out of scope

- The Home screen, and any other interface. This is the read the screen will consume.
- The memory retriever and therefore `relevant_prior_memory` (§11).
- Notifications, digests, unread badges, email. §4 asks what needs attention, not what is new.
- Writing from the inbox: dismissing an entry, snoozing, assigning. Each would be state, and each belongs with the object it would change.
- Cross-workspace ranking or a single global priority order. The sections are the priority.

## Open questions

- Should `needs_convergence` also cover a Space in `EXPLORING` that has confirmed Contributions but no relation yet — that is, "nothing has been mapped here"? Left out because it would report a Space nobody has declared ready to converge, which is a prompt to start, not a thing waiting.
- Should the reader be able to narrow the inbox to one workspace? The read is cross-workspace because Home is the person's, not a workspace page; a filter is cheap to add when a client needs it.
- Should the cap be reported as a total only, or with a cursor? A total answers "is there more"; a cursor answers "show me the rest", which needs a stable order across pages. The order here is stable, so a cursor is a later, additive change.
