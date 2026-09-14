# Narrated analysis loading

## Why

#78's first item. A member exposed to Linear and Notion reads a bare spinner
during the constraint analysis as "still a prototype". The analysis is the
product's central move, and while it runs the screen says almost nothing about
what is happening. The engine already reads the company context, checks active
objectives and constraints, reuses confirmed learnings and weighs five areas;
the screen should show that building rather than a blank wait.

## What changes

- The deposit page's running state narrates the **real inputs** the analysis is
  weighing, not generic stages: the company name, the active objective titles,
  the active constraint titles, the reused learning texts and the evidence
  sources, each under a count-aware localized sentence. A group with no data is
  omitted and long lists are capped with "+N more".
- The running `analysis` read gains a `progress` field assembled from the frozen
  launch snapshot and the effective evidence, so the narration is honest and
  dynamic rather than decorative.
- It stays decoupled from completion: the real verdict still arrives from the
  poll and replaces it; reduced motion settles every group at once.

## Out of scope

- The rest of #78 (the confirmation moment, the full empty/loading/error and
  responsive sweep, the vocabulary pass) - this slice is the narrated loading
  only, and #78 stays open.
- Backend per-step progress: the pipeline (#76) runs as one analysis step, so the
  narration reflects the stages Kollio performs, not live sub-step status.
