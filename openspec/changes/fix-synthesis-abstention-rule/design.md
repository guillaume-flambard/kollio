# Design

## Context

`ConstraintAnalysisResult` carries cross-field rules that a JSON schema cannot
express, so they are enforced after the call by Pydantic validators in
`apps/api/src/modules/constraint_analysis/domain/models.py`:

- `require_all_factors` requires exactly the five known factors, and requires an
  unknown verdict to carry no overall score with every factor unknown.
- `require_the_basis_shape` requires an unknown factor to carry no score, a gap
  and no source ids, and a known factor to carry a score and at least one source
  id.
- `validate_analysis_result` requires every cited id to belong to the supplied
  evidence set and requires at least one cited id for a non-unknown verdict.

The synthesizer prompt restated most of this but omitted the cross-field rule
linking an unknown verdict to all five factors. Model output was therefore
rejected at the boundary, the workflow ended `failed` with
`error_code = "ValidationError"`, and no analysis was stored.

## Goals / Non-Goals

**Goals:**

- A synthesis call with no supplied evidence yields a result the domain accepts.
- The prompt states the rule the validator enforces, in the same terms.

**Non-Goals:**

- Weakening the domain contract.
- Programme-level repair of a model reply.
- Changing which inputs become evidence.

## Decisions

### State the cross-field rule in the prompt

The rule is enforced in code and must be knowable by the caller. The prompt is
the only channel that reaches the model, so the rule is written there in the same
words the validator uses. The alternative, letting the schema carry the rule, is
impossible: strict JSON schema cannot express a conditional requirement across
five array items plus a sibling enum.

### Add a prompt regression test

A reply shape cannot be unit-tested without a provider, but the fix itself is
prompt text. A focused assertion keeps the rule from being silently dropped
again, which is exactly how this defect appeared. The heavier instrument,
recorded evaluations, stays responsible for verdict quality.

### Keep failing closed

An inconsistent abstention still fails the workflow. Silently repairing the
model's reply would hide a contract violation and store a result the engine did
not produce.

## Migration Plan

The change is a prompt constant plus a test. Deploy follows the normal path: push
to `main`, the `publish` job rebuilds the API and worker images, the autodeploy
timer restarts the stack. Rollback restores the previous prompt text. No data
migration.
