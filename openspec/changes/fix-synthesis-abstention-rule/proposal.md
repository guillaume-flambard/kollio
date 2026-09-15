# Fix the synthesis abstention rule

## Why

The timeout fix shipped in the previous change worked: the production analysis
reached the final synthesis step instead of failing on the first one. It then
failed there with a domain validation error.

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for ConstraintAnalysisResult
  Value error, An unknown verdict requires every factor to be unknown
```

The synthesizer returned `verdict = "unknown"` together with factors whose basis
was `known` and `assumed`. The domain model rejects that shape:

- `ConstraintAnalysisResult.require_all_factors` enforces that an unknown verdict
  carries no overall score and that every factor is unknown.
- `ConstraintFactor.require_the_basis_shape` allows a scored factor only for a
  `known` or `assumed` basis.
- `validate_analysis_result` requires at least one cited evidence id for any
  non-unknown verdict.

`SYNTHESIZER_PROMPT` said that insufficient evidence requires an unknown verdict
but never said that an unknown verdict forces every factor to be unknown. That
cross-field rule lives only in the Pydantic validator, which a JSON schema cannot
express, so the model had no way to learn it. With no supplied evidence the only
legal result is a total abstention, and the prompt did not say so.

Reproduced offline against the live gateway, holding everything else constant:

| variant | result |
| --- | --- |
| previous prompt, reasoning on | transport timeout at 123s |
| previous prompt, reasoning off | invalid: verdict `unknown` with bases `assumed, known, known, unknown, unknown` |
| fixed prompt, reasoning on | valid total abstention, 35.2s |
| fixed prompt, reasoning off | valid total abstention, 10.8s |

The defect is the prompt, not the reasoning setting: with reasoning off the old
prompt still produced the rejected shape, and with reasoning on the fixed prompt
passed.

## What Changes

State the cross-field abstention rule in `SYNTHESIZER_PROMPT` so the model can
satisfy the domain contract it is graded against.

The rule is now explicit: when no supplied evidence supports a factor, that
factor is unknown, no factor carries a score, the overall score stays empty, and
the contradictions list is empty.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `constraint-analysis-workflows`: an abstention result must satisfy the domain
  contract, and the synthesizer prompt must state the rule the validator enforces.

## Impact

- `apps/api/src/modules/constraint_analysis/adapters/litellm.py`, the
  `SYNTHESIZER_PROMPT` constant only.
- `apps/api/tests/unit/constraint_analysis/test_gateway.py`, a prompt regression
  test.
- No API contract change, no migration, no database change, no frontend change.
- The domain validators are not relaxed. A model that still returns an
  inconsistent abstention continues to fail closed.

## Out of Scope

- Relaxing `require_all_factors`, `require_the_basis_shape` or
  `validate_analysis_result`.
- Retrying or repairing an invalid synthesis automatically.
- Supplying evidence on behalf of the user. Evidence stays an operator input.
- Re-prompting the model with the validator error.
