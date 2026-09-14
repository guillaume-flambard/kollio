# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| BM-01 three arms, one command | `tests/unit/benchmark/test_comparative.py` `test_arms_differ_by_memory_and_tier`; the `benchmark run` command |
| BM-02 only C gets memory | `test_arms_differ_by_memory_and_tier` asserts "Five pilots" absent from A and B, present in C; `test_arm_request_marks_memory_usage` |
| BM-03 blind sheet | `test_blind_sheet_hides_arms_and_is_reversible` (no `arm` key in the document; key covers A/B/C; deterministic per seed); CLI smoke shows zero `arm` labels in the sheet document |
| BM-04 recorded replay, no provider | `run` reads recorded outputs without `--live`; offline smoke (`run`→`sheet`→`score`) produced the verdict with no provider call |
| BM-05 live opt-in and bounded | `GuardedBenchmarkModel` spends `LiveEvaluationGuard` before each call; `--live` only; CI never passes it |
| BM-06 verdict or product problem | `test_verdict_wins_when_memory_pays_off` (exit 0) and `test_verdict_flags_a_product_problem_when_memory_does_not_help` (summary "Product problem", exit 1); `test_missing_ratings_cannot_claim_a_win` |

## How to run (offline)

```
cd apps/api
uv run python -m src.platform.benchmark sheet --outputs <recorded> --sheet sheet.json
uv run python -m src.platform.benchmark score --sheet sheet.json --ratings <human-scores>
# or regenerate live, budgeted:
LLM_API_KEY=... uv run python -m src.platform.benchmark run --live
```

## Gaps

- The verdict needs human ratings; this ships the harness, not the filled
  scorecard. The ~10 initiatives are reconstructed for the benchmark, not a
  curated client corpus.
- C uses the memory block, not the full #76 five-step gateway, so this measures
  what a model produces from Kollio's context versus a bare prompt, not the
  pipeline's internal reasoning cost. A pipeline-vs-bare arm is a follow-up.
- Recording is a JSON file on disk; there is no CI job that stores it (it is an
  operator artifact once someone runs `--live`).
