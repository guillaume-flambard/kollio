# Pilot demo acceptance (seed Faktus and the end-to-end path)

## Why

Everything the loop needs is built (context, framing, teams, analysis with
Known/Assumed/Unknown and contradictions, the experiment-to-learning screen,
learning reuse, the onboarding wizard), but the pilot has never been shown to
run start to finish on a seeded Faktus workspace, and the brief's acceptance
checklist (§15) has never been recorded with evidence. This is the closing
slice of #52: it turns a set of verified capabilities into one demonstrable
path.

## What changes

- A deterministic, idempotent **Faktus seed** (`seed_faktus`, `make
  seed-faktus`) that stands up the workspace, two members, the full company
  context (profile, three objectives, three constraints, three non-negotiables,
  three indicators) and one deposited initiative with its first iteration.
- A **recorded demo path** (steps A–I) that maps each loop step to the exact
  interface action and the test that already proves that step, so the run can be
  repeated and checked without a terminal.
- The **§15 acceptance checklist**, verified item by item with evidence links.

## Out of scope

- Re-proving each capability: this slice references existing tests, it does not
  duplicate them.
- A live-provider run: the analysis verdict quality is pinned by recorded evals;
  running it against a live model is the operator's demo act, noted as such.
- Anything in the brief's §11 (world model, connectors, investors, BI).
