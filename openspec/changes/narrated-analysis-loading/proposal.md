# Narrated analysis loading

## Why

#78's first item. A member exposed to Linear and Notion reads a bare spinner
during the constraint analysis as "still a prototype". The analysis is the
product's central move, and while it runs the screen says almost nothing about
what is happening. The engine already reads the company context, checks active
objectives and constraints, reuses confirmed learnings and weighs five areas;
the screen should show that building rather than a blank wait.

## What changes

- The deposit page's running state becomes a **narrated build-up**: five steps
  (read context, check objectives and constraints, reuse learnings, weigh the
  five areas, decide and say where it disagrees) appear and settle one by one
  instead of a single "running" line.
- It is decorative and decoupled from completion: the real verdict arrives from
  the existing poll and replaces the narration; the application state never
  depends on the animation finishing. Reduced motion renders all steps settled.

## Out of scope

- The rest of #78 (the confirmation moment, the full empty/loading/error and
  responsive sweep, the vocabulary pass) - this slice is the narrated loading
  only, and #78 stays open.
- Backend per-step progress: the pipeline (#76) runs as one analysis step, so the
  narration reflects the stages Kollio performs, not live sub-step status.
