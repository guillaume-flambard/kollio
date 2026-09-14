# Adversarial analysis pipeline

Behind the single constraint analysis the member reads, the engine SHALL run an
ordered set of reasoning steps whose conclusion cannot silently skip the
adversarial or evidentiary work.

- **AP-01** One analysis runs, in order, analyst, challenger, evidence critic,
  company fit and synthesizer, and returns exactly one `ConstraintAnalysisResult`.
- **AP-02** The synthesizer receives the challenger and the evidence critic; if
  either produced nothing, the run fails and publishes no conclusion.
- **AP-03** The case-building step runs on the commodity model tier; the
  challenge, evidence judgment, company fit and synthesis run on the visible
  model tier, routed by task class.
- **AP-04** Every step is persisted per run (name, tier, model, output) so the
  conclusion can be replayed and audited.
- **AP-05** The member's response shape is unchanged: still one analysis with the
  Known/Assumed/Unknown factors and contradictions from #58.
- **AP-06** Local development and CI exercise the whole pipeline with no live
  provider call (scripted gateway, recorded fake server), and with
  `LLM_MODEL_VISIBLE` unset every step still runs.
