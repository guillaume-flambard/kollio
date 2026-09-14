# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| RS-01 detail + experiments on phone/tablet | `tests/browser/responsive.spec.ts` RESP-375/768 idea detail: heading + one experiment row visible, `scrollWidth <= clientWidth` |
| RS-02 wizard, no phone overflow | RESP-375/768 onboarding: wizard heading visible, no overflow (was +203px before the `min-width: 0` and stacked-form fix) |
| RS-03 deposit + running narration on phone | RESP-375 deposit; RESP-narration asserts "Lecture du contexte de Faktus" and no overflow at 375 |
| RS-04 states intact | unchanged from earlier slices: explorer/settings/experiments empty states, idea-detail skeleton + error surface, deposit narration while running |

## Note

This is the overflow-and-reachability floor for #78. The remaining
"would a screenshot go on the homepage" call is a human visual pass, not a
green check; it is left to the operator's eyes, not claimed as automated.
