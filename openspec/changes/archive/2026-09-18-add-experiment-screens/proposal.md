# Why

`docs/00-project-overview.md` §9 replaces prediction with scenario analysis, and §10 closes
the loop from an Option to an Outcome. Both halves are implemented in the API and neither is
reachable in the product: the `scenarios` module holds the editable ranges, the runs and the
deterministic sensitivity read, and the `experiments` module already holds the experiment, its
outcome and the learning a completion drafts. The `experiment` section of a Decision Space is
still an empty shell that only announces what will live there.

This is the screen half of migration step 7 (and, with it, the outcome half of step 8).

# What Changes

- The `experiment` section of a Decision Space becomes real. It shows the Space's scenario
  variables with their low, base and high values, and lets a member add, edit and delete one.
- It lets a member declare scenario runs on a chosen Option: a level among optimistic, base,
  pessimistic and failure, the assumptions the point rests on, and one value per declared
  variable.
- It reads the sensitivity of a criterion: the member names the result variable, the direction
  (above or below) and the threshold, and the section reports, for each other variable, whether
  a flip is found inside the declared interval and where, how the result travels otherwise, and
  which runs carry no result instead of averaging them. The report describes declared points and
  says so; it carries no forecast, no probability and no score.
- It turns the Space's reasoning into an experiment: a member picks the initiative that carries
  it, writes the title, the hypothesis and the success metric, and may add a baseline and the
  expected range. The created experiment is then listed with what was expected set beside what
  was observed once an outcome is recorded.
- It reaches the lifecycle the API permits — propose, launch, complete, abandon — and shows the
  draft learning a completion produces, read-only, because confirming a learning belongs to its
  own slice.

# Capabilities

### New Capabilities

- `experiment-screens`: the `experiment` section of a Decision Space renders the scenario
  ranges, the scenario runs and the sensitivity read, and drives the experiment loop from the
  Space without hiding a refusal.

# Impact

Five Nitro proxies are added for the scenario operations and the Space's experiment list, plus
one for creation that carries the initiative the API requires. The two experiment proxies the
initiative screen already uses for status and outcome are reused as they are. No API change, no
migration, no agent call.

Two boundaries are worth naming now. The section renders the writing controls and lets the API
refuse a non-participant, because the web has no identity of its own beyond the auth subject;
the refusal is surfaced with the same message the decision section uses. And the API's
`ExperimentCreateBody` carries only title, hypothesis, success metric, baseline and target:
`owner`, `budget`, `duration`, `guardrails` and the stop condition that §10 names are not in the
contract, so they are deferred behind an API operation rather than invented in the screen.

Tickets: GitHub #124 (migration step 7 of `docs/00-project-overview.md` §20, screen half;
follows the API slices #115 and #116).
