# Comparative evals: Kollio against a bare model

## Why

The pilot sells one claim: better context plus memory plus systematic
contradiction beats a shared ChatGPT fed the same question. #52 opens on exactly
that objection. It must be measured before a prospect sees it, not asserted.

## What changes

- A benchmark harness: about ten marketing initiatives, each run through three
  arms - A a bare model with only the prompt, B the visible model without
  company memory, C full Kollio (memory, active objectives and constraints,
  confirmed learnings, Known/Assumed/Unknown and contradiction).
- A blind scoring sheet: the three answers per initiative are shuffled into
  anonymous positions with a hidden key, so the rater cannot vote for the tool
  that made them.
- A written verdict that de-blinds the returned scores and states whether C
  clearly beats A on the dimensions memory is supposed to win.
- One command to run the arms over the fixture set, live calls opt-in and
  budgeted; the comparison can otherwise replay recorded outputs with no
  provider.

## Out of scope

- The human scoring itself (a rater fills the blind sheet).
- A large curated corpus; the ten initiatives are reconstructed, not client data.
- Changing the shipped analysis engine; the arms only assemble what each is
  given and measure the text.
