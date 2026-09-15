# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| Unknown factor: no score, gap named | `tests/unit/constraint_analysis/test_basis_rules.py` (unknown with a score or without a gap is refused) |
| Known factor without cited evidence rejected | the same file, `test_a_known_factor_without_cited_evidence_is_refused` |
| Abstention carries no score | `test_an_abstention_carries_no_overall_score_and_no_scored_factor`, plus the recorded abstention fixtures |
| Contradiction references a supplied objective/constraint id | `test_a_contradiction_must_reference_a_supplied_context_item` |
| Context injected at launch | `tests/integration/test_analysis_context.py`: the snapshot carries the active objective and constraint ids and not the archived one |
| Correcting fills an unknown on a new run; previous rows untouched | the same test: two launches, distinct workflows, the first stored result byte-identical |
| Recorded fixtures pin abstention and contradiction | `tests/evals/test_constraint_analysis_recordings.py`, `constraint_analysis.no_evidence.*` and `constraint_analysis.contradiction.*`, no provider calls |

## Gaps

- Only the API exposes the basis, the gap and the contradictions; the web
  surface that shows them is #61.
- The `assumed` basis is accepted without a citation by construction
  (reasoning, not a source). The prompt asks for it explicitly, but no
  eval yet measures how often the model picks `assumed` over `known`; the
  live eval harness covers that when it runs.
- Contradiction ids resolved at launch are not re-validated against later
  context edits: a contradiction keeps meaning what it meant when the run
  was launched.
