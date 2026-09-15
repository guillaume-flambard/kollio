# Experiment to outcome to learning screen

## Why

The learning loop exists in the API (#67) and nowhere on screen. The pilot's
promise is not "we had an idea" but "we tried it and here is what we
learned"; without a surface, a member cannot walk that loop. This is the P0
of the pilot (#74): the differentiator cannot be shown.

## What changes

- A new **Experiments** section on the initiative detail where a member
  walks the loop: create an experiment, launch it, record results, complete
  or cancel it, then read and confirm the drafted learning.
- Six BFF routes delegate to the generated client: list and create by
  initiative, detail, status, outcomes and learning by experiment.
- Labels in both locales. Vocabulary is Expérience, Résultat, Apprentissage;
  no run, workflow, branch, embedding or vector reaches the screen.

## Out of scope

- The model-drafted learning text: the draft stays the deterministic one
  from #67, which the member edits.
- A cross-initiative list of experiments, or experiments in the explorer.
- The analysis reusing confirmed learnings: already wired server side (#71).
