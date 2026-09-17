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

### Requirement: The Critic executes a challenge run
The system SHALL execute an opened challenge run by calling the Critic, recording what it returns as findings, and completing the run.

#### Scenario: Opening a challenge dispatches the run
- **WHEN** a writer opens a challenge on an Option
- **THEN** the system creates the run and asks the queue to execute it
- **AND** the run is returned to the caller as running

#### Scenario: The Critic writes findings into the run
- **WHEN** the Critic returns candidate findings for a running challenge
- **THEN** the system records them against that run with the `critic` origin
- **AND** marks the run complete

#### Scenario: The run records the model that produced its findings
- **WHEN** a run completes with findings the Critic produced
- **THEN** the run reports the model that was called
- **AND** a run executed before this capability reads as having no model

#### Scenario: A completed run keeps its findings
- **WHEN** a member reads a completed challenge
- **THEN** the findings the Critic wrote are still there with their kinds, severities and statuses

### Requirement: The Critic reads only what the space already holds
The system SHALL assemble the Critic's brief from the Option and the confirmed Contributions linked to it as evidence, and from nothing else.

#### Scenario: The brief carries the Option
- **WHEN** the Critic is called for an Option
- **THEN** the brief carries the space question and the Option's title and proposal
- **AND** carries each of the Option's narrative fields that is present
- **AND** omits a narrative field the Option does not carry

#### Scenario: The brief carries the linked evidence
- **WHEN** an Option links confirmed Contributions as evidence for and against
- **THEN** the brief carries each one with its identifier, title and body
- **AND** distinguishes the side it was linked on

#### Scenario: A suggested Contribution is not evidence
- **WHEN** an Option's space holds a Contribution that is still a suggestion
- **THEN** the brief does not carry it
- **AND** the Critic cannot cite it

#### Scenario: Raw branch material is never sent
- **WHEN** a Space holds Branch content that was never promoted to a Contribution
- **THEN** the brief does not carry it

#### Scenario: A citation outside the brief is refused
- **WHEN** the Critic returns a finding citing a Contribution that was not in the brief
- **THEN** the system refuses that finding
- **AND** stores no finding for that run

#### Scenario: The brief never leaves the workspace boundary
- **WHEN** the Critic is called for a Space
- **THEN** every part of the brief belongs to that Space's workspace

### Requirement: A failed run says why and stores nothing
The system SHALL end a run that could not be executed as failed, record the reason, and store no findings.

#### Scenario: The Critic fails
- **WHEN** the Critic call raises an error
- **THEN** the run becomes failed with a reason
- **AND** the run holds no findings

#### Scenario: The Critic returns something unusable
- **WHEN** the Critic returns a response that cannot be read as findings
- **THEN** the run becomes failed with a reason
- **AND** the run holds no findings

#### Scenario: The Critic finds nothing
- **WHEN** the Critic returns no findings for a run
- **THEN** the run becomes failed with a reason
- **AND** the run holds no findings
- **AND** nothing presents the Option as having been cleared

#### Scenario: Part of the result is invalid
- **WHEN** the Critic returns several findings and one of them breaks a rule
- **THEN** the system stores none of them
- **AND** the run becomes failed with a reason

#### Scenario: The queue cannot take the run
- **WHEN** a challenge is opened but the run cannot be queued
- **THEN** the run becomes failed with a reason
- **AND** no run is left running with nothing to execute it

#### Scenario: A failed run can be tried again
- **WHEN** a writer opens a new challenge on the same Option after a failed run
- **THEN** the system creates a new run
- **AND** the failed run and its reason are still readable

### Requirement: Machine findings stay proposals a human settles
The system SHALL record every Critic finding as a proposal and never resolve one itself.

#### Scenario: A Critic finding arrives as a proposal
- **WHEN** the Critic returns a finding
- **THEN** the system stores it as proposed rather than confirmed

#### Scenario: A human confirms a Critic finding
- **WHEN** a writer confirms a proposed finding the Critic wrote
- **THEN** the finding becomes confirmed
- **AND** the run is not otherwise changed

#### Scenario: A human dismisses a Critic finding
- **WHEN** a writer dismisses a proposed finding the Critic wrote
- **THEN** the finding becomes dismissed
- **AND** its row is kept as convergence data

#### Scenario: The Critic never resolves its own findings
- **WHEN** a Critic finding is stored
- **THEN** its status is proposed and no resolution is applied by the system

### Requirement: The Critic invents nothing to look certain
The system SHALL reject any finding that is not expressed in the vocabulary the space can read, and SHALL never present a verdict or a score for the Option.

#### Scenario: An unknown check is refused
- **WHEN** the Critic returns a finding whose kind is outside the six checks
- **THEN** the system refuses it and stores nothing for that run

#### Scenario: An unknown severity is refused
- **WHEN** the Critic returns a finding whose severity is outside the declared set
- **THEN** the system refuses it and stores nothing for that run

#### Scenario: A finding with no statement is refused
- **WHEN** the Critic returns a finding with a blank statement
- **THEN** the system refuses it and stores nothing for that run

#### Scenario: No verdict about the Option
- **WHEN** a member reads a challenge run
- **THEN** the response carries findings and their coverage
- **AND** carries no verdict, ranking or score for the Option

#### Scenario: Coverage still gates nothing
- **WHEN** a run completes with findings for some of the six checks
- **THEN** the Option is neither blocked nor ranked by that coverage

### Requirement: The Critic answers in the reader's languages
The system SHALL produce findings in the language of the run, in French and English alike.

#### Scenario: French run
- **WHEN** a challenge is opened from a French request
- **THEN** the findings are written in French
- **AND** every stored vocabulary value is unchanged

#### Scenario: English run
- **WHEN** a challenge is opened from an English request
- **THEN** the findings are written in English
- **AND** the rules behave identically
