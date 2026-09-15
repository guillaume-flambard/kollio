# Tasks

## 1. State the abstention rule where the model can read it

- [x] 1.1 Write a failing prompt regression test asserting that `SYNTHESIZER_PROMPT` states an unknown verdict requires every factor to be unknown, and that no factor carries a score in that case.
- [x] 1.2 Extend the closing sentence of `SYNTHESIZER_PROMPT` in `apps/api/src/modules/constraint_analysis/adapters/litellm.py` with the cross-field abstention rule, matching the wording the domain validator uses.

## 2. Prove the contract holds at the boundary

- [x] 2.1 Run the synthesizer four times against the live gateway with no supplied evidence, comparing the previous and the fixed prompt with reasoning on and off, and confirm the fixed prompt produces a total abstention the domain validator accepts while the previous prompt does not.
- [x] 2.2 Keep `enable_thinking` false and the strict JSON schema unchanged: the comparison confirms reasoning off is faster and that it was not the cause of the rejection.

## 3. Verify the change

- [x] 3.1 Run Ruff, Ruff format check, strict Mypy on the five domain packages and the API unit suite with `make verify`.
- [x] 3.2 Run the full API suite against a migrated disposable Postgres with `TEST_DATABASE_URL`, and confirm the contract drift check reports no change.

## 4. Deploy and observe

- [ ] 4.1 Deploy the API and worker through the published image path (push to `main`, `verify` then `publish`, autodeploy restarts the stack).
- [ ] 4.2 Re-run the pilot loop in production and confirm the analysis reaches a stored result instead of `failed` with `error_code` `ValidationError`.
- [ ] 4.3 Write `acceptance.md` mapping each scenario to its evidence and naming the remaining gaps.
