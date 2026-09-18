# decision-screens Specification

## Purpose
TBD - created by archiving change add-decision-screens. Update Purpose after archive.

## Requirements

### Requirement: The section challenges an Option

The Decision section SHALL let a member choose one of the Decision Space's Options, open a
challenge on it, and read the runs that Option holds with the model that answered each one,
and SHALL say the Space holds no Option to challenge rather than rendering a broken screen.

#### Scenario: A challenge is opened

- **WHEN** a member chooses an Option and opens a challenge
- **THEN** the section reports the run of that Option
- **AND** the run carries its status and the model that answered

#### Scenario: A Space with no Option

- **WHEN** a member opens the Decision section of a Space that holds no Option
- **THEN** the section says there is no Option to challenge
- **AND** it points at the section where Options are written

#### Scenario: The section could not be read

- **WHEN** the read of the Options, of the record or of the versions fails
- **THEN** the section says it could not be read
- **AND** the section heading stays readable

### Requirement: A finding is a proposal a person settles

The Decision section SHALL list every finding of the current run with its kind, its severity
and its status, SHALL let a member confirm or dismiss a proposed finding, and SHALL never
settle a finding on its own.

#### Scenario: Findings are listed with their kind and severity

- **WHEN** a member reads a run that carries findings
- **THEN** each finding is shown with its kind, its severity and its status
- **AND** a finding that is still proposed offers the actions that settle it

#### Scenario: A member confirms one and dismisses another

- **WHEN** a member confirms one proposed finding and dismisses another
- **THEN** both records carry the chosen status
- **AND** a reload keeps both rows with that status

#### Scenario: Nothing is settled automatically

- **WHEN** a run carries a proposed finding and no member acts
- **THEN** the finding stays proposed
- **AND** the section shows no verdict about the run

### Requirement: A failed run says why and can be retried

The Decision section SHALL show the stored reason of a run that failed with no findings, and
SHALL offer the action that opens a new run on the same Option.

#### Scenario: A failed run shows its reason

- **WHEN** the current run of the challenged Option failed
- **THEN** the section shows the stored reason
- **AND** it lists no finding for that run

#### Scenario: A new run can be opened after a failure

- **WHEN** a member opens a new challenge after a failed run
- **THEN** the section reports the new run of the same Option

### Requirement: A member commits the Decision Record

The Decision section SHALL let a member commit a record from `READY_TO_DECIDE` carrying the
selected Option, a required rationale, the rejected alternatives, the arguments for and
against, the critical assumptions, the unresolved uncertainty, the success criteria and the
revisit triggers, and SHALL refuse the commit form while the Space is not ready to decide.

#### Scenario: The record is committed with its rationale and triggers

- **WHEN** a member commits a record naming a selected Option, a rationale and a revisit trigger
- **THEN** the committed record is the current one
- **AND** a reload shows it with its rationale and its trigger

#### Scenario: The commit form is offered only when the Space is ready

- **WHEN** a member opens the Decision section of a Space that is not `READY_TO_DECIDE`
- **THEN** the section says which status a decision is recorded from
- **AND** it offers no commit form

#### Scenario: A member who is not a participant is refused

- **WHEN** a member who is neither the owner nor a participant of the Space commits a record
- **THEN** the section says only the owner and the participants can decide
- **AND** the section keeps rendering

### Requirement: Committed versions stay readable

The Decision section SHALL list every committed version of the record and SHALL keep an
earlier version readable after a later one is committed.

#### Scenario: Versions are listed

- **WHEN** a member reads a Space that holds several committed versions
- **THEN** each version is listed with its number, its date and its rationale

#### Scenario: A second version keeps the first readable

- **WHEN** a second version is committed
- **THEN** the earlier version is still listed
- **AND** its rationale is unchanged

### Requirement: The section never judges the Option

The Decision section SHALL present the findings the Critic proposed as proposals a person
settles, and SHALL NOT expose a verdict, a score, a ranking or a prediction about any Option.

#### Scenario: No verdict, score or ranking

- **WHEN** a member reads the Decision section
- **THEN** nothing in it exposes a score, a rank or a rating
- **AND** the section states that the Critic proposes and a person decides

### Requirement: The section answers in the reader's languages

The Decision section SHALL render every label from the locale catalogs, SHALL hold its keys in
both French and English, and SHALL answer in the reader's language.

#### Scenario: A French reader

- **WHEN** a French reader opens the Decision section
- **THEN** every control, heading and message is French

#### Scenario: An English reader

- **WHEN** an English reader opens the Decision section
- **THEN** the same section behaves identically in English
