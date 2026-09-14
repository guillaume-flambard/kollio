# Faktus onboarding wizard

## Why

The pilot is judged by whether a real team can fill the company context fast
enough for the first analysis to be relevant. The context existed as three
loose editing forms (profile, objectives, constraints); a new workspace had no
guided path, and the brief's principles and metrics had no model at all.

## What changes

- A **seven-question onboarding wizard** at the top of workspace settings,
  mapped 1:1 onto the decided model: company facts, business model, markets
  and segments (profile), three objectives, constraints, non-negotiables and
  key indicators.
- Two new company-context tables, **principles** and **key metrics**, with the
  same workspace-private create/read/update surface as objectives and
  constraints, so answers entered in the wizard persist.
- Partial answers are the normal case: the wizard finishes with what was
  filled and shows each skipped question as pending.
- Non-negotiables and key indicators get their own enrichment forms so
  "continue after startup" is true for all seven, not just the first five.

## Out of scope

- Injecting principles and metrics into the analysis engine (a follow-up on
  the analysis side; the engine still reads profile, objectives and
  constraints).
- Any CLI or seed path: the wizard is the only onboarding, per #50.
- Progress gating: an empty wizard never blocks a first analysis.
