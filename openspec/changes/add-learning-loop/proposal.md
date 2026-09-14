# Add the learning loop (experiments, outcomes, learnings)

## Why

The pilot's promise is not "we had an idea" but "we tried it and here is
what we learned". Decision #47 fixed the shape: an experiment records a
hypothesis and a success metric, outcomes are observed facts any
reader-member may add, and completing the experiment produces a learning
a member confirms or edits, linked to its experiment, outcomes and idea.

## What changes

- A new `experiments` slice: create an experiment from an initiative,
  move it through `proposed -> running -> completed | cancelled`, record
  outcomes, and write or confirm the learning.
- Completing an experiment drafts a learning from the hypothesis, the
  metric and the recorded outcomes, so the member edits rather than
  writes from nothing.
- Learnings are retrievable by experiment and by initiative.

## Out of scope

- The model-drafted learning text: the draft is deterministic here; a
  provider-backed suggestion is a refinement of the analysis engine.
- The screen that shows experiments and learnings inside the initiative.
