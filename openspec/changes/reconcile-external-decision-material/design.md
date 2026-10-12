## Context

See `proposal.md`. Branches already hold raw material and Contributions already preserve string provenance, but neither records immutable document versions nor a typed citation to an exact excerpt. The current Converge map is intentionally human-built.

## Goals / Non-Goals

**Goals:** preserve imported text and its versions; make promoted claims traceable; let humans reconcile divergence; constrain Companion synthesis to cited supplied material.

**Non-Goals:** SaaS connectors, uploads or parsing for arbitrary files, cross-workspace reuse, automatic merging, autonomous resolution, and replacing the human-built Converge map.

## Decisions

### Model sources separately from Branches

Introduce immutable `SourceMaterial` and ordered `SourceRevision` records, scoped to one Space. A Branch remains a container for exploration; a source revision can feed a Branch or a Contribution without pretending that an imported document is already shared reasoning. This avoids stretching the Branch summary into a version-control system.

### Cite excerpts by stored snapshot, not character offset alone

Store the excerpt text with its source revision and offsets when available. Offsets support highlighting, while stored excerpt text keeps citations stable if rendering changes.

### Human resolution is append-only

Use reconciliation resolutions as appended records with a human actor and rationale. Never mutate source revisions or quietly replace a prior resolution; a new resolution supersedes the earlier one visibly.

### Companion output is structured and non-canonical

Use Pydantic output containing proposed statements, source references, conflicts and uncertainty. Validate every citation against the supplied set before persistence. The proposal is a review artefact, not a Decision or a Contribution.

## Risks / Trade-offs

- [Imported text contains sensitive information] -> Keep every read and write inside existing Space membership and do not transmit material to a model until a writer explicitly invokes the Companion.
- [A synthesis hides dissent] -> Require cited statements and keep open, rejected and retained source claims visible.
- [Version lineage becomes confusing] -> Treat every revision as immutable and show a stable ordered timeline.
- [The scope becomes an integration platform] -> Accept manual text only; connectors and file parsing require a separate change.

## Migration Plan

Add isolated tables and routes, then generated client types, followed by Explore and Converge surfaces. Existing Branches and Contributions receive nullable typed source references and require no backfill. Revert safely by removing the new surfaces; imported rows remain isolated and no existing decision record is changed.
