# Design

## Decisions

- Basis rules live on `ConstraintFactor` and the verdict/score coupling on
  `ConstraintAnalysisResult`, so a malformed model answer never reaches
  persistence. Evidence-subset and contradiction-reference checks stay in
  `validate_analysis_result`, which sees the supplied evidence and context.
- Fields are required-but-nullable (`score: int | None` with no default)
  so the generated JSON schema keeps every property in `required`, which
  OpenAI strict structured output demands.
- The context is snapshotted at launch, not read at execution: the run
  stays explainable from its own record, and a later context edit cannot
  silently change what the model saw.
- Contradiction ids are namespaced (`objective:`, `constraint:`) so a
  reference is unambiguous across the two tables and stable in prose.
- No migration: the result and the snapshot are JSONB.
