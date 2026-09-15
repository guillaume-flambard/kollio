# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| EX-01 lists experiments, empty state with the create action | `tests/browser/experiments.spec.ts` EXPERIMENT-01 |
| EX-02 a member creates an experiment (payload asserted) | EXPERIMENT-02 asserts the posted title, hypothesis, metric, baseline and target |
| EX-03 a member launches it to `running` | EXPERIMENT-03 asserts the posted status and the detail's `running` state |
| EX-04 a member records a result (payload asserted) | EXPERIMENT-04 asserts the posted metric, value, unit and nulls, and the listed result |
| EX-05 completing drafts a learning | EXPERIMENT-05 asserts the posted `completed` and the draft textarea |
| EX-06 the member edits and confirms the learning | EXPERIMENT-06 asserts the posted `{ text, confirm: true }` and the confirmed state |
| EX-07 a non-member reads but gets no write form | EXPERIMENT-07 asserts the result and learning are visible with no create, result or confirm control |
| EX-08 a refused action is explained in the locale | EXPERIMENT-08 asserts the localized rule message on a 422 |
| EX-09 empty, loading and error states | empty in EXPERIMENT-01, error and retry in EXPERIMENT-09 |

## How to run

```
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"
pnpm --dir apps/web exec playwright test experiments.spec.ts
make verify
```

## Gaps

- The browser checks run on **simulated API responses**: they prove the UI
  behavior, not authentication, backend authorization or persistence. Those
  boundaries are covered by the API integration test
  `test_the_learning_loop_records_outcomes_and_confirms_a_learning` from #67,
  which is unchanged by this slice.
- The **loading** state is implemented but not asserted: it is transient
  between the mount and the response.
- The draft learning text is the deterministic template from #67, not a
  model-written claim; this slice only surfaces and confirms it.
- One experiment is open at a time; there is no cross-initiative list and no
  pagination.
