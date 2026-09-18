# Harden the recorded evaluation corpus

## Why

The recorded corpus under `apps/api/tests/evals/fixtures/` is the only evaluation that runs without provider credentials, so it is the regression net for agent judgment: thirteen reviewed recordings, replayed by three test files.

Today the suite checks its own rules by hand. `test_recorded_findings.py` re-implements the evidence rule (`set(finding.source_ids).issubset({item["id"] for item in fixture["input"]["evidence"]})`) and `test_constraint_analysis_recordings.py` drives DeepEval metrics over the recorded outputs. Meanwhile the code that will actually accept a provider answer in production is `validate_finding` (`apps/api/src/platform/llm.py:23`) for gate findings, and the strict domain model `ConstraintAnalysisResult` (`apps/api/src/modules/constraint_analysis/domain/models.py:75`) for constraint analysis. Neither boundary is exercised by the recordings.

So a recording can drift from the boundary it stands for and still pass: if the schema gained a required field, if the locale rule changed, or if the model stopped forbidding undeclared fields, the recorded suite would keep reporting green while the live path would reject every answer. Nothing in the suite states that every file in the folder is replayed at all.

## What Changes

- Replay every recorded gate finding (the four `competition.*` and the two `no_evidence.*` recordings) through `GateFinding.model_validate` and then the real `validate_finding`, with the evidence identifiers the recording was given, so each reviewed case proves it would cross the production boundary.
- Replay every recorded constraint analysis (the six `constraint_analysis.*` recordings) through `ConstraintAnalysisResult.model_validate`, which carries `extra="forbid"`, `strict=True`, the five-factor rule and the unknown-verdict rule.
- Prove the negative path on a mutated copy of a reviewed recording rather than on a synthetic object: a recording whose locale is swapped is refused with `wrong locale`, one citing an identifier that was never sent is refused with `unknown evidence`, and one whose verdict is decided without citations is refused with `A decision requires evidence`.
- Fail when a `fixtures/*.json` file is replayed by no test under `apps/api/tests/evals` or `apps/api/tests/unit`, so a recording cannot be added and forgotten.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agents/evidence-evaluation`: add a requirement that every reviewed recording is replayed through the same validation the runtime applies, so a recording cannot pass while drifting from the contract it represents.

## Impact

- One new test file under `apps/api/tests/evals/`. No fixture content changes, no production code touched, no contract, migration, database or dependency change.
- No provider call is added: the value of this corpus is that it runs without credentials, and the live path with `LiveEvaluationGuard` stays untouched.
- Running the suite today is itself evidence: if a recording already fails one of the two boundaries, that is a finding about the recording or the boundary, and it is reported rather than worked around.

## Out of Scope

- Recording new judgment cases. A reviewed recording needs a provider run that a human reads and accepts, which is the budgeted live path (`KOLLIO_LIVE_EVAL_*`) and not something a test change can fabricate honestly.
- Extending the DeepEval metrics of the existing competition suite.
- The pivot surfaces (challenge, converge, options, decisions, scenarios, learning), which have no recorded corpus at all.
- Any web behavior, and the API catalogs.
