# analysis-basis Specification

## Purpose

Make every factor of a verdict state what it rests on — known, assumed or unknown — and surface conflicts with the company's own objectives and constraints rather than folding them into a score.

## Requirements

### Requirement: Each factor carries an epistemic basis
Each of the five factors SHALL carry a basis of `known`, `assumed` or `unknown`. An unknown factor SHALL have no score and a non-empty gap naming the missing evidence, and SHALL cite nothing. A known factor SHALL have a score and SHALL cite at least one supplied evidence id. An assumed factor SHALL have a score and MAY cite nothing. An unknown verdict SHALL have no overall score and every factor SHALL be unknown; any other verdict SHALL have an overall score.

#### Scenario: Unknown factor
- **WHEN** a factor is `unknown`
- **THEN** it has no score
- **AND** it carries a non-empty gap naming the missing evidence
- **AND** it cites nothing

#### Scenario: Known factor
- **WHEN** a factor is `known`
- **THEN** it has a score
- **AND** it cites at least one supplied evidence id

#### Scenario: Assumed factor
- **WHEN** a factor is `assumed`
- **THEN** it has a score
- **AND** it may cite nothing

#### Scenario: Unknown verdict
- **WHEN** the verdict is `unknown`
- **THEN** it has no overall score
- **AND** every factor is unknown

### Requirement: Evidence and context references are validated before persistence
Cited evidence ids SHALL be a subset of the evidence supplied at launch. A non-unknown verdict SHALL require at least one citation. Every contradiction SHALL reference an id supplied in the launch's company context (`objective:<uuid>` or `constraint:<uuid>`); a reference to anything else SHALL be refused before persistence.

#### Scenario: Citation outside the launch evidence
- **WHEN** a result cites an evidence id not supplied at launch
- **THEN** the system refuses the result before persistence

#### Scenario: Contradiction references an unknown target
- **WHEN** a contradiction references an id that is not `objective:<uuid>` or `constraint:<uuid>` from the launch context
- **THEN** the system refuses the result before persistence

### Requirement: The launch snapshots the active company context
The launch SHALL snapshot the workspace's active company context: profile, active objectives (with priority) and active constraints (with detail), each with a namespaced id. The snapshot SHALL travel with the run; the model SHALL receive it as untrusted data and the code SHALL validate against it.

#### Scenario: Context injected at launch
- **WHEN** a member launches an analysis in a workspace with active objectives and constraints
- **THEN** the run carries a snapshot of the profile, the active objectives and the active constraints, each with a namespaced id
- **AND** the code validates the result against that snapshot

### Requirement: Contradictions name their target
A contradiction SHALL name its target, the referenced id and the conflict in the requested language. An initiative that conflicts with a stated objective or constraint SHALL produce at least one contradiction instead of folding the conflict into a score.

#### Scenario: An initiative conflicts with a stated objective
- **WHEN** the analysis finds the initiative in conflict with an active objective or constraint
- **THEN** it produces at least one contradiction naming the target, the referenced id and the conflict in the requested language

### Requirement: Corrections are new evidence on a new run
A correction SHALL be new evidence on a new run. Launching again SHALL create a new workflow and a new analysis row; previously stored results SHALL never be mutated.

#### Scenario: Corrections never overwrite
- **WHEN** a member supplies new evidence and launches again
- **THEN** a new workflow and a new analysis row are created
- **AND** the previously stored result is unchanged
