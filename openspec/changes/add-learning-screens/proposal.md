# Spec the learning screens

## Why

`docs/00-project-overview.md` §10 ends the Decision Space loop with a Learning: an
experiment runs, outcomes accumulate, and a person confirms the lesson the Space should
keep. The API already holds that loop — a completion drafts a learning, `draft` and
`confirmed` are the only statuses, and a confirmed learning never returns to draft — and
no screen reaches it. The `learning` section of a Decision Space is still a shell that
says what will live there.

## What Changes

- The `learning` section of a Decision Space lists the lessons the Space holds: those
  still waiting for a person, and those already confirmed, each with the outcome it came
  from, the experiment that produced it and the initiative it belongs to.
- A proposed lesson is readable and its text is editable before it is confirmed, because
  the draft the completion composed is a starting point and not a decision.
- A person confirms a lesson, or saves their edit without confirming, and the section says
  plainly that a lesson nobody confirmed stays a kept draft: nothing is deleted, and
  nothing returns a confirmed lesson to draft.
- The section never confirms a lesson on its own, and it never shows a score, a ranking or
  a verdict about the decision the Space made.
- One Nitro proxy is added for the Space's lessons list; the write operation reuses the
  existing experiment learning proxy.

Capabilities: `learning-screens`.

## Impact

- The section reads the Space's experiments and their details, the Space's lessons, the
  workspace members and the workspace ideas, so the descent of a lesson is named rather
  than referenced by identifier.
- No API change: no route, no schema and no migration is touched, so `make contract` is a
  no-op for this slice.
- Honest boundary: the API has no `rejected` status. `LEARNING_STATUSES` is `draft` and
  `confirmed`, so rejecting a lesson is expressed as leaving it as a kept draft, and the
  screen says that instead of inventing a state the API cannot store.
- Out of scope: the Memory Retriever (§11) and the `Relevant prior memory` section of the
  Inbox, which stay unbuilt.

Tickets: GitHub #125 (migration step 8 of `docs/00-project-overview.md` §20, screen half;
follows the API slice #116).
