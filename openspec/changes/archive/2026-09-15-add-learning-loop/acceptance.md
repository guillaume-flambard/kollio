# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| Create an experiment from an initiative | `test_the_learning_loop_records_outcomes_and_confirms_a_learning` asserts 201 and `proposed` |
| Illegal transition refused | the same test asserts 422 for `proposed -> completed` |
| Several outcomes on one experiment | the same test records two outcomes and reads both back |
| Outsiders denied | the same test asserts 404 on read and on write for a non-member |
| Completion drafts a learning | the same test asserts the draft text carries the hypothesis and target, with two `outcome_ids` |
| Confirm persists with links | the same test asserts `confirmed` with `confirmed_by_id`, retrievable by experiment and by initiative |
| Rules without a database | `tests/unit/experiments/test_lifecycle.py`, 6 cases |

## Gaps

- The draft text is deterministic, not model-written: the pilot reads a
  template it edits. Provider-backed drafting arrives with the analysis
  engine work.
- No screen yet shows experiments or learnings inside the initiative;
  the API is the deliverable of this slice.
- Experiment and outcome creation do not reference the initiative's
  active company context yet; that arrives with #58, which now also
  carries the context-injection criterion.
