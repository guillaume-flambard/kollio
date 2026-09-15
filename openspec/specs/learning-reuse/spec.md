# learning-reuse Specification

## Purpose

Make a confirmed learning reusable: embed it on confirmation, retrieve it scoped to the viewer's workspaces, and inject the nearest ones into a later analysis launch.

## Requirements

### Requirement: Embedding a confirmed learning
When a member confirms a learning, it SHALL be embedded with the same model and
dimensions as an idea. Its provenance SHALL carry the workspace, the idea and
the experiment ids. Embedding failure SHALL be logged and SHALL NOT fail the
confirmation.

#### Scenario: Confirmation embeds the learning
- **WHEN** a member confirms a learning
- **THEN** it is embedded with the same model and dimensions as an idea
- **AND** its provenance carries the workspace, the idea and the experiment ids

#### Scenario: Embedding fails
- **WHEN** embedding the confirmed learning fails
- **THEN** the failure is logged
- **AND** the confirmation still succeeds

### Requirement: Scoped retrieval
Similarity retrieval SHALL take the viewer's workspace ids and return only
candidates whose idea belongs to one of those workspaces. An empty set SHALL
return nothing. Confirmed learnings only.

#### Scenario: Retrieval scoped to the viewer
- **WHEN** similarity retrieval runs for a viewer
- **THEN** only candidates whose idea belongs to one of the viewer's workspaces are returned
- **AND** only confirmed learnings are returned

#### Scenario: No workspace
- **WHEN** the viewer has no workspace id
- **THEN** retrieval returns nothing

### Requirement: Launch injection
At launch, the initiative's title and pitch SHALL form the query; the nearest
confirmed learnings of the viewer's workspaces SHALL be appended to the launch
evidence as `learning:<uuid>` entries, labelled with a synthetic
`kollio://learning/<uuid>` URL. The snapshot SHALL record the reused ids. A
missing provider SHALL degrade to the caller-supplied evidence.

#### Scenario: Learnings injected at launch
- **WHEN** a member launches an analysis
- **THEN** the initiative's title and pitch form the query
- **AND** the nearest confirmed learnings of the viewer's workspaces are appended to the launch evidence as `learning:<uuid>` entries labelled with a synthetic `kollio://learning/<uuid>` URL
- **AND** the snapshot records the reused ids

#### Scenario: Provider missing
- **WHEN** the embedding provider is missing at launch
- **THEN** the launch degrades to the caller-supplied evidence
