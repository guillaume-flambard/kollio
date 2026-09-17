# challenge Specification

## Purpose
Let a workspace challenge an Option against the six checks of `docs/00-project-overview.md` §7, record findings a human confirms, and read what has been challenged and what remains uncovered.

## Requirements

### Requirement: A challenge stays inside its workspace

The system SHALL expose a challenge run and its findings only to authenticated members of the workspace that owns the parent Decision Space.

#### Scenario: Member reads a challenge
- **WHEN** a workspace member requests the challenges of an Option in their workspace
- **THEN** the system returns the runs and their findings
- **AND** answers in the request locale

#### Scenario: Non-member requests a challenge
- **WHEN** an authenticated non-member requests, opens or resolves anything under a Space they do not belong to
- **THEN** the system responds as if the Space were not found
- **AND** discloses no run, finding or Option content

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a challenge
- **THEN** the system responds unauthorized without touching persistence

#### Scenario: A run never leaks across workspaces or Options
- **WHEN** a member of another workspace, or a member of the same workspace naming a different Option, requests a run by identifier
- **THEN** the system responds as if the run were not found
- **AND** discloses nothing

### Requirement: Writers open and complete a challenge run

The system SHALL let the Option owner and the Space participants open a challenge run on an Option and complete it, and SHALL refuse everyone else.

#### Scenario: Run opened
- **WHEN** a writer opens a challenge on an Option
- **THEN** the system creates a run in `RUNNING` owned by that writer
- **AND** records the write language
- **AND** the run starts with no findings

#### Scenario: Uninvolved member cannot write
- **WHEN** a workspace member who is neither the owner nor a participant opens a run, records a finding, resolves one or completes a run
- **THEN** the system refuses the request as forbidden
- **AND** stores nothing

#### Scenario: Lifecycle is a closed set
- **WHEN** a writer completes a run in `RUNNING`
- **THEN** the system records it as `COMPLETED`
- **AND** refuses any further transition on that run, accepting only `OPEN`, `RUNNING`, `COMPLETED` and `FAILED` as statuses

#### Scenario: A completed run keeps its findings
- **WHEN** a run is completed
- **THEN** its findings remain readable unchanged

### Requirement: Findings cover the six checks

The system SHALL let a writer record a finding on a run, each carrying exactly one of the six declared checks, a severity and a non-blank detail statement.

#### Scenario: Each kind recorded
- **WHEN** a writer records a finding of each of `unsupported_assumption`, `contradictory_evidence`, `hidden_dependency`, `failure_mode`, `causal_claim` and `missing_success_criteria`
- **THEN** the system persists each with its kind, severity and detail
- **AND** a later read returns exactly those findings

#### Scenario: Unknown check refused
- **WHEN** a writer records a finding with a kind outside the six, or a severity outside the three
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Detail required
- **WHEN** a writer records a finding with an empty or whitespace-only detail
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: A finding about a Contribution keeps the reference
- **WHEN** a writer records a finding naming a Contribution of the same Space
- **THEN** the system persists the reference
- **AND** a read returns it

#### Scenario: A finding cannot name a foreign Contribution
- **WHEN** a writer records a finding naming a Contribution that does not belong to the same Space
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

### Requirement: Machine findings wait for a human

The system SHALL treat a human finding as confirmed on arrival and a machine finding as proposed until a human confirms or dismisses it.

#### Scenario: Human finding is canonical
- **WHEN** a writer records a finding
- **THEN** the system stores it as `confirmed`
- **AND** records its origin as `human`

#### Scenario: Machine finding is not canonical
- **WHEN** the Critic records a finding
- **THEN** the system stores it as `proposed`
- **AND** records its origin as `critic`

#### Scenario: Human confirms a proposal
- **WHEN** a writer confirms a proposed finding
- **THEN** the system stores it as `confirmed`
- **AND** a later read returns it as confirmed

#### Scenario: Human dismisses a proposal
- **WHEN** a writer dismisses a proposed or confirmed finding
- **THEN** the system stores it as `dismissed`
- **AND** keeps the finding readable rather than deleting it

#### Scenario: Resolving is a writer action
- **WHEN** an uninvolved member confirms or dismisses a finding
- **THEN** the system refuses the request as forbidden
- **AND** leaves the finding unchanged

### Requirement: A member reads what was challenged and what is not

The system SHALL report, for each Option, its runs, its findings and which of the six checks carry at least one non-dismissed finding.

#### Scenario: Coverage reported
- **WHEN** a member reads a challenged Option whose findings cover some of the six kinds
- **THEN** the system reports the covered kinds
- **AND** reports the uncovered kinds
- **AND** reports no score

#### Scenario: Dismissed findings do not cover
- **WHEN** the only finding of a kind has been dismissed
- **THEN** the system reports that kind as uncovered
- **AND** still returns the dismissed finding

#### Scenario: Unchallenged Option
- **WHEN** a member reads an Option that has never been challenged
- **THEN** the system returns no runs and reports every kind as uncovered
- **AND** does not treat that as an error

#### Scenario: Coverage gates nothing
- **WHEN** an Option has uncovered checks
- **THEN** the system still allows opening a new run, recording findings and completing the existing run
- **AND** refuses no request because of it

#### Scenario: French and English behave identically
- **WHEN** the same challenge journey runs in French and in English
- **THEN** every message the API returns is localized
- **AND** behavior is identical
