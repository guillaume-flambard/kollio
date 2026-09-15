# Faktus onboarding

## Model

The workspace company context SHALL carry two more workspace-private,
lang-stamped lists alongside objectives and constraints: **principles**
(non-negotiables, a title and optional detail) and **key metrics** (a name and
optional value, unit, observed date and source). They are readable in
`GET /workspaces/{workspace_id}/company-context` and created or updated through
`POST`/`PATCH` on `.../company-context/principles` and `.../company-context/metrics`.
A caller outside the workspace is refused everywhere, the same 404 as the rest
of the context.

## The wizard

- **ONB-01** The settings screen opens with a seven-question wizard. With
  nothing filled, all seven questions read as pending.
- **ONB-02** A member answers any subset and saves; every entered answer
  persists in the model (profile PUT plus one POST per new objective,
  constraint, principle and metric). The wizard completes with partial answers.
- **ONB-03** A skipped question stays visibly pending after a save; an answered
  one does not.
- **ONB-04** Saving the same wizard twice does not duplicate a row that is
  already stored (matched by trimmed, case-insensitive title or name).
- **ONB-05** Non-negotiables and key indicators have their own enrichment
  forms, so a question can be completed after startup.

## Access

- **ONB-06** The context, including principles and metrics, is invisible to a
  non-member: read is a 404, and every write is refused.

## FR and EN

- **ONB-07** The wizard behaves identically in French and English; every label
  comes from the catalogs.
