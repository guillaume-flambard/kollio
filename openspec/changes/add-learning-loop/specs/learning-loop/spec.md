# Learning loop

## Experiment lifecycle

An experiment is created from an initiative with a title, a hypothesis, a
success metric and optional baseline and target, and starts `proposed`.
It moves to `running`, then to `completed` or `cancelled`; `completed` and
`cancelled` are terminal. An unknown or illegal target is refused with a
422 carrying the rule message.

## Outcomes

Any member who can read the initiative records an outcome against a
running or completed experiment: metric, value, optional unit, observed
date, comment and a qualitative note. Several outcomes accumulate on one
experiment. An outsider sees 404.

## Learning

Completing an experiment drafts a learning from the hypothesis, the
metric, the target and the recorded outcomes, with the outcome ids pinned.
A member edits the text and confirms it, which records who confirmed it
and moves it from `draft` to `confirmed`; a confirmed learning never
returns to draft. A learning is readable by its experiment and by its
initiative.
