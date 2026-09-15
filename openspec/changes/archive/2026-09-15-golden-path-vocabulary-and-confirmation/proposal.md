# Golden-path vocabulary and confirmation moment

## Why

Part of #78. A member fluent in Linear and Notion reads dev-speak on screen as
"still a prototype". Two concrete fixes: the analysis vocabulary is supposed to
be Evolution, Proposal, Alternative, Analysis, Result, Learning - but the
timeline still said "Branch", "Merged" and "Analysis running"; and confirming a
learning, the moment a result becomes company memory, ended with no visible
acknowledgement.

## What changes

- Vocabulary pass over the visible strings: the proposal line is an
  **Alternative**, an accepted proposal is **Accepted** (not git "Merged"), the
  in-flight analysis reads **"Analysis in progress"**, and the proposal hint and
  change-message label drop "branch"/"iteration". FR and EN together.
- A **confirmation moment** when a learning is confirmed: the confirmed learning
  shows "Added to the company memory" with a discrete, reduced-motion-safe
  transition.

## Out of scope

- The full empty/loading/error and responsive sweep across every golden-path
  screen: the last item of #78, tracked separately; #78 stays open for it.
- Any backend or contract change; this is copy and one CSS state.
