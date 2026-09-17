## Purpose

Answer "what needs my attention?" across the workspaces a member belongs to, from the state the other capabilities already store. Read-only, and honest about the one question it cannot yet answer.

## ADDED Requirements

### Requirement: The inbox is private to its reader
The system SHALL return an inbox only to the authenticated member who asked for it, covering only the workspaces that member belongs to.

#### Scenario: A member reads their inbox
- **WHEN** an authenticated member requests the inbox
- **THEN** the system returns the sections described below
- **AND** every entry belongs to a workspace that member is a member of

#### Scenario: The inbox never crosses workspaces
- **WHEN** a member belongs to one workspace and another workspace holds waiting work
- **THEN** that other workspace's work does not appear in the member's inbox

#### Scenario: A member with nothing waiting
- **WHEN** a member belongs to a workspace but no Space meets any section's condition
- **THEN** the system returns every section empty
- **AND** does not treat the empty inbox as an error

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests the inbox
- **THEN** the system responds unauthorized without reading state

### Requirement: Spaces that need convergence are surfaced
The system SHALL surface each Space of the reader's workspaces whose status is `CONVERGING`.

#### Scenario: A converging Space appears
- **WHEN** a Space of the reader's workspace stands in `CONVERGING`
- **THEN** it appears in the needs convergence section
- **AND** the entry names its workspace, the Space and the Space question

#### Scenario: A Space elsewhere in the lifecycle does not
- **WHEN** a Space stands in `OPEN`, `EXPLORING`, `READY_TO_DECIDE`, `DECIDED`, `TESTING`, `LEARNED` or `REOPENED`
- **THEN** it does not appear in the needs convergence section

### Requirement: Work waiting on the reader personally is surfaced
The system SHALL surface suggested Contributions and proposed Challenge findings that sit in a Space where the reader is the owner or a participant, and SHALL NOT surface them for a Space where the reader is neither.

#### Scenario: A suggested Contribution waits for a participant
- **WHEN** a Space where the reader is a participant holds a Contribution in `suggested`
- **THEN** it appears in the needs my input section
- **AND** the entry carries the Contribution's identifier and title

#### Scenario: A proposed finding waits for a participant
- **WHEN** a Space where the reader is a participant holds a Challenge finding in `proposed`
- **THEN** it appears in the needs my input section
- **AND** names the finding rather than the Contribution kind

#### Scenario: An uninvolved member is not asked
- **WHEN** a suggested Contribution or a proposed finding sits in a Space where the reader is a workspace member but neither the owner nor a participant
- **THEN** it does not appear in the reader's inbox

#### Scenario: Confirmed work stops waiting
- **WHEN** a Contribution is `confirmed` or a finding is `confirmed` or `dismissed`
- **THEN** it does not appear in the needs my input section

### Requirement: Spaces ready for a Decision are surfaced
The system SHALL surface each Space of the reader's workspaces whose status is `READY_TO_DECIDE` and which holds no committed Decision.

#### Scenario: A prepared Space appears
- **WHEN** a Space of the reader's workspace stands in `READY_TO_DECIDE` with no committed Decision
- **THEN** it appears in the ready to decide section

#### Scenario: A committed Decision stops the prompt
- **WHEN** a Space stands in `READY_TO_DECIDE` and already holds a Decision
- **THEN** it does not appear in the ready to decide section

#### Scenario: A Space elsewhere in the lifecycle does not
- **WHEN** a Space stands in `DECIDED`, `TESTING`, `LEARNED` or `REOPENED`
- **THEN** it does not appear in the ready to decide section

### Requirement: Work needing a learning is surfaced
The system SHALL surface, for the reader's workspaces, completed experiments with no recorded Outcome and Learnings that are still drafts.

#### Scenario: A completed experiment with no outcome
- **WHEN** an experiment of a Space in the reader's workspace is `completed` and holds no Outcome
- **THEN** it appears in the needs learning section
- **AND** the entry carries the experiment's identifier

#### Scenario: A draft Learning awaits confirmation
- **WHEN** a Learning in a Space of the reader's workspace is in `draft`
- **THEN** it appears in the needs learning section
- **AND** the entry carries the Learning's identifier

#### Scenario: An experiment still running does not
- **WHEN** an experiment is `proposed`, `running` or `cancelled`
- **THEN** it does not appear in the needs learning section

#### Scenario: A confirmed Learning is done
- **WHEN** an experiment is `completed` and holds a confirmed Learning
- **THEN** neither the experiment nor that Learning appears in the needs learning section

### Requirement: The inbox is ordered, bounded and honest about its bound
The system SHALL order each section oldest first, SHALL return at most a requested number of entries per section, and SHALL report how many entries each section holds in total.

#### Scenario: The longest wait comes first
- **WHEN** a section holds several entries
- **THEN** the entries are ordered by the age of what waits, oldest first
- **AND** two entries of the same age are ordered deterministically

#### Scenario: The bound is applied per section
- **WHEN** the reader asks for a limit and a section holds more entries than that
- **THEN** the section returns that many entries
- **AND** reports the total it holds so the client can say how many remain

#### Scenario: An out-of-range limit is refused
- **WHEN** the reader asks for a limit below 1 or above the accepted maximum
- **THEN** the system refuses the request as invalid

### Requirement: The inbox does not answer what it cannot
The system SHALL NOT return a relevant prior memory section while no capability surfaces prior confirmed Learnings with their provenance.

#### Scenario: No empty memory section
- **WHEN** an authenticated member reads the inbox
- **THEN** the response carries the four sections this capability computes
- **AND** carries no relevant prior memory section, because an empty one would assert that no relevant memory exists
