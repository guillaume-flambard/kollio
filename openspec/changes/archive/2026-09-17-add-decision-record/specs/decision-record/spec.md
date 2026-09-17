## Purpose

Hold the committed choice of a Decision Space as a versioned, append-only record that stands on its own: what was chosen, what was rejected, which confirmed Contributions support and oppose it, what remains uncertain, what would count as success and what would bring the team back.

## ADDED Requirements

### Requirement: Workspace-scoped record privacy
The system SHALL expose a Decision Record only to authenticated members of the workspace owning its Decision Space.

#### Scenario: Member reads the record
- **WHEN** a workspace member requests the decision record of a space in their workspace
- **THEN** the system returns the latest version with its selected Option, rejected alternatives, arguments and narrative fields
- **AND** answers in the request locale

#### Scenario: No record yet
- **WHEN** a member requests the decision record of a space that has not been decided
- **THEN** the system responds as if no record existed for that space, without disclosing anything

#### Scenario: Non-member requests the record
- **WHEN** an authenticated non-member requests a decision record of a workspace they do not belong to
- **THEN** the system responds as if the space were not found
- **AND** discloses no decision content

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a decision record
- **THEN** the system responds unauthorized without touching persistence

#### Scenario: A record never leaks across spaces or workspaces
- **WHEN** two spaces in two workspaces each hold a decision record
- **THEN** a member of one workspace can read only their own space's record, even by identifier

### Requirement: Committing is the only way to decide
The system SHALL accept a decision commit only for a space in `READY_TO_DECIDE`, and record the resulting status change in the space history.

#### Scenario: Committed from a ready space
- **WHEN** a writer commits a decision for a space in `READY_TO_DECIDE`
- **THEN** the system stores the record and moves the space to `DECIDED`
- **AND** appends the status change to the space history with its actor

#### Scenario: Committed from any other status
- **WHEN** a writer commits a decision for a space whose status is `OPEN`, `EXPLORING`, `CONVERGING`, `DECIDED`, `TESTING`, `LEARNED` or `REOPENED`
- **THEN** the system refuses the request as invalid
- **AND** stores no record and appends no status event

#### Scenario: A re-decided space takes a new version
- **WHEN** a space that already holds a record is reopened, brought back to `READY_TO_DECIDE` and committed again
- **THEN** the system stores the commit as the next version
- **AND** leaves the earlier version untouched

### Requirement: The record stands on its own
The system SHALL store a record whose selected Option, rejected alternatives, supporting and opposing arguments, uncertainty, criteria and triggers are all explicit.

#### Scenario: Full record committed
- **WHEN** a writer commits a record naming a selected Option, rejected Options, arguments for and against, critical assumptions, uncertainty, success criteria and revisit triggers
- **THEN** the system persists all of them against that version
- **AND** a later read returns exactly those values

#### Scenario: Minimal record committed
- **WHEN** a writer commits a record with only a selected Option and a rationale
- **THEN** the system persists it
- **AND** a later read reports the optional fields as absent rather than failed

#### Scenario: Rationale required
- **WHEN** a writer commits a record with an empty or whitespace-only rationale
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Selected Option must belong to the space
- **WHEN** a writer commits a record selecting an Option that does not exist in that space
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: A rejected alternative cannot be the selected Option
- **WHEN** a writer lists the selected Option among the rejected alternatives
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Arguments reference confirmed Contributions of the space
- **WHEN** a writer links an argument to a Contribution
- **THEN** the system accepts it only if that Contribution is confirmed and belongs to the same space
- **AND** records whether it argues for or against
- **AND** refuses an unknown side, an unknown Contribution, a suggested Contribution or a Contribution from another space without storing anything

#### Scenario: One Contribution cannot argue both ways
- **WHEN** a writer links the same Contribution as both an argument for and an argument against the same decision
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Revisit triggers are structured
- **WHEN** a writer supplies a revisit trigger
- **THEN** the system requires a non-blank metric
- **AND** accepts only `above` or `below` as a direction, with an optional non-blank threshold and an optional note
- **AND** refuses a trigger without a metric and a trigger with an unknown direction, storing nothing

#### Scenario: Reviewers are snapshotted
- **WHEN** a writer commits a record
- **THEN** the system stores the participants of the space at that moment as the record's reviewers
- **AND** a later change to participation leaves the stored reviewers unchanged

### Requirement: Versions are append-only
The system SHALL keep every committed version readable and never modify or delete a stored record.

#### Scenario: Versions listed
- **WHEN** a member lists the decision versions of a space
- **THEN** the system returns every version, newest first, each with its own alternatives and arguments
- **AND** returns an empty list, not an error, when the space has never been decided

#### Scenario: An earlier version is unchanged
- **WHEN** a later version exists
- **THEN** reading the earlier version still returns its original selected Option, rationale and arguments

### Requirement: Writers commit, members read
The system SHALL let the space owner and its participants commit a decision, and let any workspace member read records.

#### Scenario: Participant commits
- **WHEN** a participant of the space commits a decision
- **THEN** the system stores it and records them as the decision maker

#### Scenario: Uninvolved member cannot commit
- **WHEN** a workspace member who is neither the owner nor a participant attempts to commit
- **THEN** the system refuses the request and stores nothing

#### Scenario: Non-member sees nothing
- **WHEN** a non-member attempts to read or commit any decision record
- **THEN** the system responds as if the space were not found
- **AND** stores nothing
