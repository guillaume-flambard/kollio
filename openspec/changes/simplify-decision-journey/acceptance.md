# Acceptance evidence - simplify-decision-journey

A decision space exposed six sections named after internal mechanics (Explore, Converge, Options, Decision, Experiment, Learning), so a person arriving had to learn six module names before starting, and the space index silently redirected to Explore. This change reads a space as three moments in plain language, groups the six routes under them, keeps every route and every deep link where it was, and turns the index into a static orientation page instead of a redirect.

Status: complete.

| Spec scenario | Evidence | State |
| --- | --- | --- |
| SIMPLE-01 A newcomer sees the question and the three moments | `DECISION-SPACES-12 reads the space as three moments` in `apps/web/tests/browser/decision-spaces.spec.ts` asserts the three moment labels in order above the section links, each moment holding exactly its two sections, and the orientation heading with its three blocks on the space index. | Passing |
| SIMPLE-02 The minimal supported input is enough to move | The moment actions point at the first section of each moment, and no required field was added: the space header, the status transition form and the section controls are unchanged, so a reader still moves with the same minimal input. | Passing (source) |
| SIMPLE-03 Optional detail stays discoverable and collapsible | Every section route, its localized link and the detailed controls inside the sections are untouched; the moments only group the links, and `DECISION-SPACES-05` still walks all six sections. | Passing |
| SIMPLE-04 An existing space keeps its data and its section links | `DECISION-SPACES-05` unchanged and green: question, status, owner, deadline, participants and every section link still resolve; `DECISION-SPACES-11` still reports a missing space; no request payload changed. | Passing |
| SIMPLE-05 A refused write stays visible and recoverable | The transition failure path (`decisionSpaces.transition.failed` in an alert) is untouched, and `DECISION-SPACES-07` and `-08` were green in the targeted run. | Passing |
| SIMPLE-06 French, English, mobile and keyboard | `DECISION-SPACES-12` runs once per locale; the styles keep 42px link targets, a single-column moment list under 760px and the existing focus outlines. | Passing |

## Verification runs (2026-09-19)

Live, in production, after the deploy: not observed. The change is committed and no deployment has been made, so the deployed pilot still shows the six-section navigation. Reading the three moments on the live pilot belongs to the delivery comment.

Local, before deploy:

- `node scripts/check_locales.mjs`: `FR/EN catalogs match (1026 web keys): every key the code uses exists, and every catalog key is reachable from apps/web or packages/ui/src.` (1013 keys before this change, plus the 13 moment keys).
- `node scripts/check_design_tokens.mjs`: `Design tokens: apps/web/app uses only canonical tokens.`
- `pnpm lint`: clean. One unused constant (`sections` in the space shell) had to be removed, the navigation now being built from the moments.
- `pnpm typecheck`: clean.
- `node scripts/check_ux_coverage.mjs`: `coverage: ok`.
- `pnpm build`: complete.
- Targeted run: `pnpm --dir apps/web exec playwright test decision-spaces.spec.ts` reports `22 passed`, with `DECISION-SPACES-12` green in French and English.
- Counter-check: with the two `.vue` files stashed and the catalogs kept, the same file reports `4 failed, 18 passed`. The four are `DECISION-SPACES-12` in both locales plus `DECISION-SPACES-03` in both, the latter because its updated assertion targets the orientation page that the previous navigation does not have. The new scenario is therefore not complacent.
- `pnpm --dir apps/web exec playwright test`: `324 passed (11.1m)`, which includes the two DECISION-SPACES-12 runs, one per locale.

## Known boundaries

- Before this change the space index redirected to Explore; it now renders the orientation page, so `DECISION-SPACES-03` was updated to assert that page. The redirect is gone by design, not by accident.
- The orientation page reads no data, so it cannot say whether a moment is empty: the line it shows comes from the `empty` keys and is phrased as guidance rather than as a claim about the current space.
- Browser tests run against simulated API responses. They prove what the browser renders for the new navigation, not authentication, workspace isolation, persistence or provider behaviour.
- One load-related failure was observed once on `DECISION-SPACES-04` in English and did not reproduce: the file was green on the next two runs.
