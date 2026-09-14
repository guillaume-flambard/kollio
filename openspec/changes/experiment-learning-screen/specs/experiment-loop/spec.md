# Experiment learning loop on the initiative detail

The initiative detail SHALL carry an Experiments section where a member walks
the loop the API already supports: create, launch, record results, complete
or cancel, and confirm the learning. The section MUST read through BFF routes
that delegate to the generated client, and MUST show no technical vocabulary
(no run, workflow, branch, embedding or vector).

## Listing and empty state

- **EX-01** The section lists the initiative's experiments with their
  localized status. When there is none, it SHALL show an empty state with the
  create action instead of a blank area.

## The loop

- **EX-02** A member SHALL create an experiment with a title, a hypothesis, a
  success metric and optional baseline and target. The new experiment starts
  `proposed` and opens its detail.
- **EX-03** A member SHALL launch a proposed experiment, moving it to
  `running`.
- **EX-04** A member SHALL record a result on an experiment: metric, value,
  optional unit, observed date, comment and a qualitative note. Several
  results SHALL accumulate and be listed.
- **EX-05** A member SHALL complete a running experiment, moving it to
  `completed`; completing SHALL surface the drafted learning. A member MAY
  cancel a proposed or running experiment instead.
- **EX-06** A member SHALL edit and confirm the learning. A confirmed learning
  SHALL be shown as read-only and MUST NOT offer to return to draft.

## Access

- **EX-07** A non-member SHALL read the experiments, their results and the
  learning, but MUST NOT be offered any write form.

## Refusal and states

- **EX-08** An action the API refuses with `experiment_rule` (422) SHALL be
  explained in the member's locale, not shown as a raw server string.
- **EX-09** Each step SHALL have empty, loading and error states.
