# Eval corpus extension for V1 constraint behavior

Research resolution for wayfinder ticket "Constraint eval corpus extension".
Branch: `research/constraint-eval-corpus` (throwaway; merge nothing, cherry-pick cases when the schema lands).

## What exists today

`apps/api/tests/evals/` holds the reviewed corpus:

- `fixtures/no_evidence.{en,fr}.json` → abstention contract: no evidence means verdict `unknown`, no citations, requested locale (strict DeepEval threshold).
- `fixtures/competition.*.json` (4 cases) → competition-gate contract with prospecteur provenance (`source_system`, `source_case_id`, `reviewed_on`, `semantic_note`).
- `test_contract.py` → schema rejection: unstructured output, unapproved fields, unknown evidence ids, wrong locale.
- Opt-in live runs behind `LiveEvaluationGuard` (`KOLLIO_RUN_LIVE_EVALS=1`, budget-capped).

Gap: no `ConstraintAnalysis` schema or code exists yet in `src/` (five scored constraints + realism score). Every case below waits on that schema, decided via the "Constraint killer live behavior" ticket.

## Proposed new cases

1. **Deposit-time analysis** (`deposit.{fr,en}.json`): bare title + pitch, no iteration context. Expect a valid five-constraint analysis in the requested locale, plus an abstention variant for vacuous pitches (mirrors the `no_evidence` contract at deposit time).
2. **Iteration-linked recompute**: same idea across two iterations with a changed payload → analyses differ and each is bound to its `iteration_id`. Negative: an analysis bound to an old iteration must never serve the current one.
3. **Five-constraint coverage**: each of `concurrence`, `cout`, `temps`, `defendabilite`, `acquisition` carries a score and a short note; FR/EN parity per note (extends the existing locale contract to every note).
4. **Score-explanation coupling**: a realism score presented without evidence notes fails. A decorative score is the exact failure the product principles forbid.
5. **Per-constraint abstention**: one dimension with insufficient evidence records `unknown`/neutral while the other four stay scored. Pending the schema shape — confirm in the "Constraint killer live behavior" ticket whether the schema allows it.

## Methodology (reuse, don't reinvent)

- Recorded fixtures with the same provenance block as the competition cases (`source`, `reviewed_on`, `semantic_note`); strict pass/fail like `AbstentionMetric`.
- Live variants opt-in under the existing `LiveEvaluationGuard` budget.
- Land cases 1–4 with the schema; case 5 only after the schema decision confirms per-constraint verdicts exist.

## Handoff

When "Constraint killer live behavior" resolves, convert cases 1–4 into fixtures + tests in `apps/api/tests/evals/` on the delivery branch. This file stays on the throwaway branch as the pointer.
