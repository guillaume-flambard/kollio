# Analysis basis (Known/Assumed/Unknown), explicit contradictions and context injection

## Why

Pilot brief §4: the engine must separate what it knows from what it
assumes and what it does not know, contradict the user explicitly rather
than folding a conflict into a score, and take the company context into
account. Today the analysis scores every factor from 0 to 100, has no
notion of basis, and never receives the workspace's objectives or
constraints.

## What changes

- Every factor carries a basis from `known`, `assumed`, `unknown`. An
  unknown factor carries no score and names the evidence it is missing; a
  known factor must cite at least one supplied evidence id. An unknown
  verdict carries no overall score and requires every factor to be
  unknown.
- The result carries a `contradictions` list; each entry names its target
  (`objective` or `constraint`), the exact referenced id, and the
  conflict in prose. The validator rejects a reference the launch never
  supplied.
- The launch input now snapshots the active company context (profile,
  active objectives, active constraints) with stable ids
  (`objective:<uuid>`, `constraint:<uuid>`), the worker carries it into
  the graph, and the gateway sends it to the model as data.
- The read model exposes each constraint's basis and gap and the
  contradictions, so the surface can show them.

## Out of scope

- Rendering the basis and contradictions in the web app: #61 owns the
  explanation surface.
- Correcting a heuristic mid-flight: a correction is new evidence on a
  new run, which the engine already supports.
