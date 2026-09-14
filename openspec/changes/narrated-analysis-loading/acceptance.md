# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| NL-01 five narrated steps while running, one current | `tests/browser/deposit.spec.ts` DEPOSIT-03 asserts the five localized step labels, `.narration-step` count 5 and one `[data-current="true"]`, and no resolved heading |
| NL-02 verdict replaces it unchanged | DEPOSIT-02 (resolved) and DEPOSIT-04 (abstention) still pass; the narration only renders while `analysisState === 'running'` |
| NL-03 reduced motion settles all steps | component sets `stage` to the last index under `prefers-reduced-motion: reduce` (no animation dependency for state) |
| NL-04 FR/EN parity, no jargon | DEPOSIT-03 runs in both locales; `check_locales` parity |
| NL-05 canonical tokens only | `check_design_tokens` passes (no literal colour, no unknown token) |

## Gaps

- This is the first item of #78 only. The confirmation moment, the full
  empty/loading/error and responsive sweep, and the vocabulary pass across the
  other golden-path screens are not here; #78 stays open.
- The narration timing is client-side and reflects the stages Kollio runs, not a
  live per-step signal from the pipeline. The pipeline (#76) completes in one
  analysis step today, so there is no real sub-progress to show.
