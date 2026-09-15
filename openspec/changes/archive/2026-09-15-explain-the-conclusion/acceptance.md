# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| The basis is shown per factor | `tests/browser/deposit.spec.ts` DEPOSIT-05 asserts both labels render, in fr and en |
| An unknown factor shows its gap | the same test asserts the gap prose renders |
| Contradictions are shown with their target | the same test asserts the heading and the prose |
| Abstention still shows no fake score | DEPOSIT-04 unchanged and green |
| Vocabulary is translated | the keys live in both locale files and the parity check passes |

## Gaps

- Only the deposit verdict panel explains the conclusion; the idea detail
  and the timeline show a label only.
- The evidence cited by a known factor is not shown: the analysis response
  exposes source ids inside the factor, not the evidence texts, so the
  surface cannot list them without another API field.
- Browser checks use simulated analysis responses; the real shapes come
  from the API tests and the recorded eval fixtures.
