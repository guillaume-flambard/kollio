## ADDED Requirements

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
