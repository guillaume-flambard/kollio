# Tasks

## 1. Vocabulary and proxies

- [x] 1.1 Add the `experiment` keys to both locales and the section's vocabulary to
  `apps/web/CONTEXT.md`.
- [x] 1.2 Add the Nitro proxies: the scenario variables, the scenario runs of an Option, the
  sensitivity read (repeating the three query parameters) and the Space's experiment list.
- [x] 1.3 Add the creation proxy at the Space level, which resolves the initiative the API
  requires in the path and forces the Space of the current route.

## 2. The Experiment section

- [x] 2.1 List the Space's scenario variables with their range and their base, and let a member
  add, edit and delete one, refusing a blank name and an unordered range before the API does.
- [x] 2.2 Let a member declare a scenario run on a chosen Option: a level, the assumptions and
  one value per declared variable, listed per Option with the Option named only by its title.
- [x] 2.3 Read the sensitivity of a named result variable against a criterion: the ranking, the
  status of each variable, the interval a flip falls in, how the result travels otherwise, the
  runs that carry no result, and the evidence counts of the Option.
- [x] 2.4 Turn a decision into an experiment from the Space: choose the initiative, write the
  title, the hypothesis and the success metric, add a baseline and an expected range, and list
  the experiment with what was expected beside what was observed.
- [x] 2.5 Reach the lifecycle the API permits and show the draft learning read-only, with the
  states a member can reach named and nothing shown when there is nothing yet.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs for the section: the empty state, a variable written and
  edited, a run declared, the sensitivity read, an experiment created, its status moved, an
  outcome recorded, a refusal shown, and the absence of any forecast.
- [x] 3.2 Carry them to green while keeping the six-section shell test intact, which asserts the
  section title of every section.

## 4. Documentation

- [x] 4.1 Write the `experiment-screens` spec delta.
- [x] 4.2 Record the scenario-to-test mapping in `acceptance.md`, name the boundaries and list
  what is deferred.

## 5. Verification

- [x] 5.1 Run lint and typecheck.
- [x] 5.2 Run the locale gate, the design-token gate and the coverage gate.
- [x] 5.3 Run the browser specs and the production build.
- [x] 5.4 Run `openspec validate add-experiment-screens`.
