# Analysis basis and contradictions

## Basis

Each of the five factors carries a basis: `known`, `assumed` or `unknown`.
An unknown factor has no score and a non-empty gap naming the missing
evidence, and cites nothing. A known factor has a score and cites at least
one supplied evidence id. An assumed factor has a score and may cite
nothing. An unknown verdict has no overall score and every factor is
unknown; any other verdict has an overall score.

## Evidence and context validation

Cited evidence ids must be a subset of the evidence supplied at launch. A
non-unknown verdict requires at least one citation. Every contradiction
must reference an id supplied in the launch's company context
(`objective:<uuid>` or `constraint:<uuid>`); a reference to anything else
is refused before persistence.

## Context injection

The launch snapshots the workspace's active company context: profile,
active objectives (with priority) and active constraints (with detail),
each with a namespaced id. The snapshot travels with the run; the model
receives it as untrusted data and the code validates against it.

## Contradictions

A contradiction names its target, the referenced id and the conflict in
the requested language. An initiative that conflicts with a stated
objective or constraint produces at least one contradiction instead of
folding the conflict into a score.

## Corrections

A correction is new evidence on a new run. Launching again creates a new
workflow and a new analysis row; previously stored results are never
mutated.
