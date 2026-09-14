# Design

## Model

Principles and key metrics reuse the objective/constraint pattern exactly, so
the module stays one shape:

- `CompanyPrinciple(id, workspace_id, title, detail?, state(active|archived),
  lang, created_at, updated_at)`: a stated intent or an explicitly refused
  item, the "non-negotiables" of the brief.
- `CompanyMetric(id, workspace_id, name, value?, unit?, observed_at?, source?,
  state, lang, created_at, updated_at)`: a simple tracked number, the
  "metric names" of the brief. `value`, `unit`, `observed_at` and `source` are
  optional so the wizard can persist a bare name.

Both are keyed by `workspace_id`, visible and editable only inside the
workspace, and carry `lang` like every other company-context row. The read
`CompanyContextResponse` grows `principles` and `metrics`; the analysis engine
still consumes profile, objectives and constraints untouched.

## Wizard placement and state

The wizard is the first section of workspace settings, above the existing
editing forms. It holds only local form state seeded from the context; there
is no draft persisted per step. The seven steps are:

| Step | Writes |
| --- | --- |
| Company facts | profile `name`, `description` |
| Business model | profile `business_model`, `products_services` |
| Markets and segments | profile `markets`, `customer_segments` |
| Three objectives | new `company_objectives` rows |
| Constraints | new `company_constraints` rows |
| Non-negotiables | new `company_principles` rows |
| Key indicators | new `company_metrics` rows |

Saving is one action: a profile PUT plus one POST per filled list row that is
not already stored (compared by trimmed, case-insensitive title or name). That
makes the wizard idempotent: running it twice does not duplicate an objective,
and it never overwrites a list the user did not touch.

## Pending is the persisted state

A step's answered/pending marker is computed from what is stored, not from the
live inputs. A question stays pending until its answer is in the model, which
is exactly the acceptance ("skipped questions stay visibly pending"). During a
save the form inputs are snapshotted before the first await, so the context
watch that re-seeds the form cannot clobber rows that are mid-write.

## BFF

Four new routes mirror the constraint ones: `principles` create and update,
`metrics` create and update. `optionalText` normalises blank fields to null so
a partial metric stores only what was typed.
