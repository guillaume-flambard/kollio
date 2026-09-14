# Comparative benchmark

The harness SHALL measure whether full Kollio beats a bare model, blind, and
reproducible without a provider.

- **BM-01** Three arms run over the fixture set from one command: A bare model
  on the prompt alone, B visible model without company memory, C full Kollio with
  memory, active objectives and constraints, confirmed learnings and
  Known/Assumed/Unknown.
- **BM-02** A and B are given no company memory; only C is, and that is the only
  substantive difference across the arms.
- **BM-03** The scoring sheet is anonymous: the rater-facing document has no arm
  labels, and the position-to-arm key is kept apart from it.
- **BM-04** Runs can be recorded and replayed so a later model or prompt change
  is compared with no live call.
- **BM-05** Live provider calls are opt-in and budgeted; the default path and CI
  make none.
- **BM-06** The verdict de-blinds ratings and states whether C clearly beats A;
  if it does not, it reports a product problem, not a scoring accident.
