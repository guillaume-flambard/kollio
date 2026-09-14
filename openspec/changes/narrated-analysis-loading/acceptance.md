# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| NL-01 real inputs narrated | `tests/browser/deposit.spec.ts` DEPOSIT-03 asserts the company name, an objective title, a constraint title, a learning text and a source from `analysis.progress` |
| NL-02 omission and "+N more" | DEPOSIT-03 asserts the 4th objective is absent and the `+1 more` overflow shows |
| NL-03 progress from snapshot + evidence | `tests/integration/test_analysis_display.py` `test_running_analysis_carries_real_progress` asserts the running read's `progress` (profile, objectives, constraints, learnings, sources, areas) built from the launch snapshot |
| NL-04 verdict unchanged | DEPOSIT-02 (resolved) and DEPOSIT-04 (abstention) still pass; the narration renders only while `analysis.state === 'running'` |
| NL-05 reduced motion | the component sets every group done under `prefers-reduced-motion: reduce`; content is the real data either way |
| NL-06 FR/EN + tokens | DEPOSIT-03 runs in both locales; `check_locales` parity; `check_design_tokens` passes |

## Gaps

- `progress` is assembled from the frozen snapshot at launch, so it reflects
  what the run started with, not live per-step completion; the pipeline (#76)
  still finishes in one analyze step, so there is no incremental sub-progress to
  surface yet.
- Reused-learning text comes from the effective evidence (populated at launch);
  with no embeddings configured the learnings group is simply absent, which is
  the honest behaviour.
