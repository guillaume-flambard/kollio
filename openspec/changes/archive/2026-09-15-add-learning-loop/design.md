# Design

## Decisions

- Lifecycle and learning rules live in `experiments/domain/lifecycle.py`
  as pure functions (`decide_transition`, `decide_learning_status`,
  `compose_learning_draft`) so they are unit-tested without a database.
- Authorization is the reader-membership rule already used by the team
  slice: any member who can read the initiative may record an outcome or
  move the lifecycle; an outsider sees not-found, never a distinction
  between "exists" and "forbidden".
- One learning per experiment (`unique(experiment_id)`), with
  `idea_id` denormalised for the initiative-level read and `outcome_ids`
  pinned at write time so a confirmed learning keeps the evidence it was
  confirmed against.
- Terminal statuses (`completed`, `cancelled`) never move again; the
  draft is (re)composed when the experiment completes and is left alone
  once a member has written their own text.
