# Design

## Placement

The section lives in the initiative document (the main column), between the
iterations block and the team section, with the id `experiments`. The
companion is too narrow for a five-step loop, and the design system forbids
dense simultaneous panels, so a section extends the existing document
instead of adding a new surface.

## Ownership of state

A dedicated component `KollioExperimentLoop` owns the experiments list, the
open experiment's detail, and the write actions. The page passes only
`idea-id` and `is-member`. The loop has one read plus five writes; keeping
it in the page would grow an already large component and mix concerns.

## Read and write model

- The list comes from `GET /ideas/{id}/experiments`.
- Opening an experiment fetches `GET /experiments/{id}`, which returns the
  experiment, its outcomes and its learning in one response, so the whole
  loop is visible without a second round of calls.
- Every write refreshes the open detail; a status change also refreshes the
  list so the status label moves.
- One experiment is open at a time.

## Membership and authority

`is-member` is true when the session subject is the owner or one of the
collaborators. Read is open to anyone who can see the initiative; create,
launch, cancel, complete, record a result and confirm the learning are
member-only, matching the acceptance criterion "only a member may add
results". The API stays the authority: the UI hides what a member cannot do
and surfaces the refusal otherwise.

## Errors and localization

`POST /experiments/{id}/status` and the learning write can refuse with
`experiment_rule` (422). The BFF forwards the status and the code; the
component maps 422 to a localized message, so an illegal action explains
itself in the member's locale instead of leaking the English rule string.
Status codes (`proposed`, `running`, `completed`, `cancelled`) are rendered
through the catalogs; the raw code never reaches the screen.

## States

- Empty: no experiment yet, one sentence and the create action.
- Loading: a skeleton line while the list or the detail loads.
- Error: a localized message with a retry.
