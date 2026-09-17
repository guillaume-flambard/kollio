## Context

`docs/00` §10 makes the loop Decision → Experiment → Outcome → Learning the only path that produces a reusable Learning, and §20 step 8 attaches that loop to the Decision Space. The loop already exists and works: `apps/api/src/modules/experiments/` carries `proposed` → `running` → `completed`/`cancelled`, accumulates `ExperimentOutcome` rows and drafts one `Learning` per experiment which a human confirms. What is missing is the link: today `experiments.idea_id` is the only parent, so nothing connects a Decision Space to the Outcomes and Learnings of the decision it recorded.

The user decision for this slice is explicit: **additive link, nothing broken**.

## Domain model

No new entity. Two nullable columns on `experiments`:

| Field | Kind | Notes |
| --- | --- | --- |
| `decision_space_id` | reference, optional | the space the experiment validates; null for every existing row |
| `option_id` | reference, optional | the Option under test, when the experiment tests one; null otherwise |

Both are `ondelete="SET NULL"`: a space or option that disappears must not destroy experiment history. No Decision Space delete operation exists today; the choice is made now so a later one cannot silently erase outcomes.

`ExperimentOutcome` and `Learning` are **not** changed. Their parent is the experiment, and the experiment now carries the space, so the whole chain is reachable from a Decision Space by one join. Denormalising the space onto outcomes and learnings would create two places to keep in agreement for no query that needs it today.

## Rules

- **Same workspace.** The space must belong to the workspace of the experiment's idea. A space from another workspace is refused as a validation error and stores nothing, so the link can never become a cross-tenant read.
- **Option belongs to the space.** `option_id` is only accepted together with a `decision_space_id`, and the option must belong to that space.
- **No link, no change.** Creating an experiment without the new fields behaves exactly as before, and the initiative routes keep serving it.
- **No backfill.** Existing experiments keep `decision_space_id` null. Inferring a space for them would invent a decision nobody made.

## Permissions

- **Writing a link** follows the existing experiment rule: whoever may create the experiment today may create it with a link.
- **Reading a space's experiments and learnings** follows the space rule: any authenticated member of the owning workspace, and nobody else. A non-member receives the same workspace-not-found treatment as every other space route so membership cannot be probed.

## Boundary

Extends the existing `experiments` module rather than adding a new one: two columns and their verification, two service reads, two HTTP operations. The read routes live under the decision-space path (`/workspaces/{wid}/decision-spaces/{sid}/experiments` and `.../learnings`) because that is where the caller stands, and they go through the same workspace-membership gate as the rest of the module.

## Deliberately out of scope

- The Memory Retriever (§11): nothing yet surfaces a past Learning with its why and provenance.
- Extending the learning embedding's provenance with the space id. It is one small change but it belongs with the retrieval slice, which decides what the retriever actually queries.
- Requiring every experiment to belong to a space. That would invalidate the existing loop and its spec.
- Any screen.
- Re-parenting the initiative-facing narrative: the product still shows the loop on the initiative detail.

## Open questions

- Should an experiment that validates a Decision eventually be *required* to name one, once the Decision Space screens exist? Left open until the screens show whether a space-less experiment still has a place.
- Should `Outcome` carry the space directly for a future "all outcomes of this space" query without a join? Revisit only if such a query appears.
