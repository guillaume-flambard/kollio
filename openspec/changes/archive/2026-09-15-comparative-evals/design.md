# Design

## Shape

`src/platform/benchmark/` is pure data plus four small modules so the whole
thing is testable without a provider:

- `data.py`: `Initiative`, `CompanyContext`, `ArmOutput`, `DIMENSIONS` (the
  seven blind criteria), `DIFFERENTIATORS` (company_knowledge,
  willingness_to_challenge, trust), a fixture loader, and `context_memory` that
  renders the company facts, active objectives and constraints and confirmed
  learnings into one block.
- `arms.py`: `arm_request` builds the exact (system, user, uses_memory) each arm
  gets, differing only in memory and instructions; `run_benchmark` calls an
  injected model that exposes `bare_model`, `visible_model` and `complete`. A is
  the bare model on the raw prompt, B the visible model with no memory, C the
  visible model with memory and the K/A/U + contradict instruction.
- `blinding.py`: shuffles each initiative's three answers into positions with
  `random.Random(seed*1_000_003 + index)`, returns the sheet and the separate
  key. The rater-facing document carries positions and text only, never the arm.
- `scoring.py`: de-blinds ratings by the key, averages per arm and dimension,
  and `judge` returns the verdict. C wins only if it clears A by `min_margin`
  overall and on every differentiator; otherwise the summary says "Product
  problem".

## Live is opt-in and bounded

The CLI's `LiteLLMBenchmarkModel` reaches the gateway only under `--live`, wrapped
in `GuardedBenchmarkModel` which spends the same `LiveEvaluationGuard` budget the
evals use before each call. Without `--live` the command reads recorded outputs,
so the comparison replays offline. CI never passes `--live`; every test uses a
scripted model.

## Model tiers reuse #75

`resolve_model(REASONING)` names the visible model, and A is pinned to the bare
`llm_model`, so the arms line up with the routing that ships the reasoning.
