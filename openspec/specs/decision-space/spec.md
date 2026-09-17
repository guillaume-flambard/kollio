# decision-space Specification

## Purpose
Hold the durable parent object of collective reasoning: one question a workspace must decide, with its owner, its participants, its lifecycle and its append-only history. Branches, Contributions, Converge, Options and the Decision Record attach to it in later slices.

## Requirements

### Requirement: The workspace is the privacy boundary
The system SHALL expose a Decision Space only to authenticated members of the workspace that owns it, and SHALL treat every other caller as if the Decision Space did not exist.

#### Scenario: Member reads a Decision Space
- **WHEN** a workspace member requests a Decision Space of their workspace
- **THEN** the system returns its question, owner, status, optional deadline and description, and participants
- **AND** answers in the request locale

#### Scenario: Non-member requests a Decision Space
- **WHEN** an authenticated non-member requests a Decision Space of a workspace they do not belong to
- **THEN** the system responds as if it were not found
- **AND** discloses no question, owner, participant or status

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a Decision Space
- **THEN** the system responds unauthorized without touching persistence

#### Scenario: A Decision Space never leaks across workspaces
- **WHEN** two workspaces each hold Decision Spaces
- **THEN** a member of one workspace sees only that workspace's Spaces
- **AND** cannot read, transition or edit the other workspace's Spaces, even by identifier

### Requirement: Members open a Decision Space
The system SHALL let a workspace member open a Decision Space with a question, starting it `OPEN`, with the caller recorded as owner and as a participant.

#### Scenario: Opened
- **WHEN** a member submits a question
- **THEN** the system persists the Space as `OPEN`
- **AND** records the caller as owner and as its first participant
- **AND** records the language of the write

#### Scenario: Question required
- **WHEN** a member submits an empty or whitespace-only question
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Optional frame recorded
- **WHEN** a member submits a question with a description and a deadline
- **THEN** the system persists them with the Space
- **AND** a later read returns exactly those values

#### Scenario: Non-member cannot open a Space
- **WHEN** a non-member attempts to open a Decision Space in a workspace they do not belong to
- **THEN** the system responds as if the workspace were not found
- **AND** stores nothing

### Requirement: The lifecycle is a closed set of transitions
The system SHALL accept a status transition only when it belongs to the declared set, and SHALL refuse every other request without changing the Space or its history.

The declared set is `OPEN` → `EXPLORING` → `CONVERGING` → `READY_TO_DECIDE` → `DECIDED` → `TESTING` → `LEARNED`, plus `DECIDED`, `TESTING` or `LEARNED` → `REOPENED`, plus `REOPENED` → `EXPLORING`.

#### Scenario: Forward transition accepted
- **WHEN** the owner or a participant moves an `OPEN` Space to `EXPLORING`
- **THEN** the system persists the new status

#### Scenario: Skipping a step refused
- **WHEN** a caller moves a Space from `OPEN` straight to `DECIDED`
- **THEN** the system refuses it as invalid
- **AND** the Space keeps its previous status

#### Scenario: Unknown status refused
- **WHEN** a caller requests a status outside the declared set
- **THEN** the system refuses it as invalid
- **AND** stores nothing

#### Scenario: The declared chain is walkable end to end
- **WHEN** a Space is moved `OPEN` → `EXPLORING` → `CONVERGING` → `READY_TO_DECIDE` → `DECIDED` → `TESTING` → `LEARNED`
- **THEN** every step succeeds
- **AND** the Space ends `LEARNED`

#### Scenario: A terminal Space cannot resume without reopening
- **WHEN** a caller moves a `LEARNED` Space directly to `TESTING`
- **THEN** the system refuses it as invalid

### Requirement: A decided Space can be reopened
The system SHALL let a `DECIDED`, `TESTING` or `LEARNED` Space be reopened into `REOPENED` with a recorded reason, and SHALL let a `REOPENED` Space resume at `EXPLORING`.

#### Scenario: Reopened with a reason
- **WHEN** the owner or a participant reopens a `DECIDED` Space with a reason
- **THEN** the Space becomes `REOPENED`
- **AND** the reason is recorded in its history

#### Scenario: Reason required
- **WHEN** a caller reopens a Space without a reason
- **THEN** the system refuses it as invalid
- **AND** the Space keeps its previous status

#### Scenario: Work resumes after reopening
- **WHEN** the owner or a participant moves a `REOPENED` Space to `EXPLORING`
- **THEN** the system accepts it

#### Scenario: A Space that was never decided cannot be reopened
- **WHEN** a caller tries to reopen a Space in `OPEN`, `EXPLORING`, `CONVERGING` or `READY_TO_DECIDE`
- **THEN** the system refuses it as invalid

### Requirement: Status history is append-only
The system SHALL record every accepted status change as an immutable entry carrying the previous status, the new status, the actor, the timestamp and the optional reason, and SHALL read the Space's current status from that history.

#### Scenario: History accumulates in order
- **WHEN** a Space is transitioned twice
- **THEN** its history holds both entries in order
- **AND** the current status is the last entry's target

#### Scenario: History is readable
- **WHEN** a member reads a Space
- **THEN** the system returns its status history in order
- **AND** each entry names its actor and its timestamp

#### Scenario: A refused transition leaves no trace
- **WHEN** a transition is refused
- **THEN** the history gains no entry

#### Scenario: Opening records the first entry
- **WHEN** a Space is opened
- **THEN** its history already holds one entry establishing `OPEN`

### Requirement: Participants are workspace members
The system SHALL let a Decision Space carry participants drawn from the members of its workspace, and SHALL let the owner add and remove them.

#### Scenario: Participant added
- **WHEN** the owner adds a workspace member as a participant
- **THEN** the Space lists that member among its participants

#### Scenario: Adding the same participant twice is idempotent
- **WHEN** the owner adds a member who is already a participant
- **THEN** the Space still lists that member exactly once

#### Scenario: A non-member cannot participate
- **WHEN** the owner tries to add someone who is not a member of the workspace
- **THEN** the system refuses it as invalid
- **AND** stores nothing

#### Scenario: The owner cannot be removed
- **WHEN** a caller tries to remove the owner from the participants
- **THEN** the system refuses it

#### Scenario: Participants persist
- **WHEN** participants are added and the Space is read back
- **THEN** the read returns exactly those participants
- **AND** the owner is among them

### Requirement: Only the owner and participants write
The system SHALL let the owner and the Space's participants change its status, and SHALL refuse any other workspace member; SHALL let only the owner manage participants.

#### Scenario: A participant transitions the status
- **WHEN** a participant who is not the owner moves the Space's status
- **THEN** the system accepts it

#### Scenario: An uninvolved member cannot write
- **WHEN** a workspace member who is neither owner nor participant attempts to change the status
- **THEN** the system refuses it
- **AND** the Space is unchanged

#### Scenario: Only the owner manages participants
- **WHEN** a participant who is not the owner tries to add or remove a participant
- **THEN** the system refuses it
- **AND** stores nothing

### Requirement: Workspace members list their Decision Spaces
The system SHALL list a workspace's Decision Spaces to its members and SHALL return an empty list rather than an error when there are none.

#### Scenario: Spaces listed
- **WHEN** a member lists the Decision Spaces of their workspace
- **THEN** the system returns that workspace's Spaces only

#### Scenario: Nothing yet
- **WHEN** a workspace has no Decision Space
- **THEN** the system returns an empty list

#### Scenario: A non-member lists nothing
- **WHEN** a non-member lists a workspace's Decision Spaces
- **THEN** the system responds as if the workspace were not found
