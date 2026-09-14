# Adversarial reasoning behind one analysis

## Why

A one-shot chat answer flatters the author. The pilot's claim is that Kollio's
conclusion is stronger than a bare model because it argues, attacks, judges the
evidence and checks company fit before it commits. #75 gave each step a task
class; this slice runs the reasoning through that routing as a real pipeline,
behind the single analysis the member already sees.

## What changes

- The constraint-analysis step is now five ordered calls: analyst (case in
  favour, commodity tier), challenger (why it fails at this company, visible),
  evidence critic (fact versus speculation, visible), company fit (against the
  active objectives and constraints, visible), and a decision synthesizer
  (visible) that reads the challenger and the evidence critic and writes the
  one `ConstraintAnalysisResult`.
- A conclusion cannot silently drop the adversarial or evidentiary step: if the
  challenger or the evidence critic produced nothing, the run fails and nothing
  is published.
- Every step is persisted per run so a conclusion can be replayed and audited.
- A compact decision brief carries only the relevant context, never the whole
  history.

## Out of scope

- The member's surface: still one analysis with the same response shape, no
  visible agents.
- Live quality measurement: that is the comparative benchmark (#77).
- A premium model registered in the deployment: with `LLM_MODEL_VISIBLE` unset
  every step still runs, on the default model.
