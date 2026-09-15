# Acceptance evidence

| Scenario | Evidence |
| --- | --- |
| VOC-01 Alternative, not branch | `ideas.iterations.branch` is "Alternative {name}" in FR and EN; `timeline.spec.ts` and `proposal.spec.ts` render it through the catalog and pass |
| VOC-02 Accepted / in progress | `ideas.iterations.accepted` = "Accepted"/"Acceptée" and `analysisRunning` = "Analysis in progress"; the owner-actions and timeline checks read these values and pass |
| VOC-03 confirmation moment | `tests/browser/experiments.spec.ts` EXPERIMENT-06 asserts "Added to the company memory" appears after confirming |
| VOC-04 no jargon | the FR/EN app catalogs contain no "branch"/"Branche"/"Merged"/"Fusionnée"/"commit"/"workflow"/"repo"/"embedding"/"vector" in visible strings; `check_locales` parity and `check_design_tokens` pass |

## Gaps

- VOC-01/02 are pinned by catalog values read through the localized specs rather
  than by asserting the literal word on screen; a wording regression that keeps
  the key would not fail a browser check. The catalog grep above is the guard.
- The full empty/loading/error and responsive sweep across every golden-path
  screen is not in this slice; #78 stays open for it.
