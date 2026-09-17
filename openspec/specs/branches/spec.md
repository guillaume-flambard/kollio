# branches Specification

## Purpose
Hold exploration Branches under Decision Spaces, map existing Ideas into them without losing history, and propose canonical Contributions from Branch material with human confirmation.

## Requirements

### Requirement: Members work in Branch containers
The system SHALL expose exploration Branches under a Decision Space, private or shared, holding non-canonical raw material.

#### Scenario: Shared Branch created and read back
- **WHEN** a Space writer creates a shared Branch with a title
- **THEN** the system persists it under that Space
- **AND** a later read returns exactly its title, visibility and language

#### Scenario: Private Branch visible only to its creator
- **WHEN** a member creates a private Branch
- **THEN** the system returns it to its creator
- **AND** responds as if it did not exist to any other member

#### Scenario: Branch without a title refused
- **WHEN** a member creates a Branch with an empty or whitespace title
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Spaces list their Branches
- **WHEN** a member lists the Branches of a Space
- **THEN** the system returns only that Space's Branches
- **AND** returns an empty list, not an error, when there are none

### Requirement: Ideas map to Branches without losing history
The system SHALL map every workspace-scoped Idea to exactly one Branch whose raw material is the Idea's content and whose history stays reachable through an explicit source link.

#### Scenario: Workspace Idea mapped
- **WHEN** a workspace Idea with title, pitch and iterations is mapped
- **THEN** the system creates a Decision Space in the Idea's workspace owned by the Idea's owner
- **AND** creates a shared Branch under it carrying the Idea's title and pitch
- **AND** links the Branch to the Idea so the iteration history remains reachable

#### Scenario: Mapping is idempotent
- **WHEN** an Idea that already has a Branch pointing at it is mapped again
- **THEN** the system creates nothing
- **AND** the Idea still has exactly one Branch

#### Scenario: Public Idea left alone
- **WHEN** an Idea without a workspace is considered for mapping
- **THEN** the system maps nothing
- **AND** leaves the Idea exactly as it is

#### Scenario: Idea read path untouched
- **WHEN** a member reads a mapped Idea through the existing Idea endpoints
- **THEN** the system returns it exactly as before the mapping

### Requirement: Contributions are proposed from Branch material
The system SHALL let Space writers propose canonical Contributions from Branch material, with AI suggestions becoming canonical only on human confirmation.

#### Scenario: Human proposes a Contribution
- **WHEN** a Space writer selects material from a readable Branch and proposes it with a kind
- **THEN** the system persists a `confirmed` Contribution with that writer as author
- **AND** records the Branch, source, tool/model when given, and transformation history

#### Scenario: AI suggestion waits for a human
- **WHEN** an AI suggestion arrives with material and a kind
- **THEN** the system persists it as `suggested`
- **AND** it is not treated as canonical

#### Scenario: Human confirms a suggestion
- **WHEN** a Space writer confirms a `suggested` Contribution
- **THEN** the system flips it to `confirmed`
- **AND** records the confirmer as author

#### Scenario: Unknown kind refused
- **WHEN** a proposal names a kind outside `idea`, `claim`, `evidence`, `objection` and `constraint`
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Proposing from an unreadable Branch refused
- **WHEN** a caller proposes material from a Branch they cannot read
- **THEN** the system responds as if the Branch did not exist
- **AND** stores nothing

### Requirement: Branch and Contribution permissions follow the Space
The system SHALL gate Branch and Contribution reads and writes on Branch visibility and Space membership, never leaking across workspaces.

#### Scenario: Non-member sees nothing
- **WHEN** an authenticated non-member requests a Branch, a Contribution or either list
- **THEN** the system responds as if the workspace were not found
- **AND** discloses no Branch or Contribution content

#### Scenario: Uninvolved member cannot write
- **WHEN** a workspace member who is neither the Space owner nor a participant attempts to propose or confirm
- **THEN** the system refuses the write
- **AND** stores nothing

#### Scenario: No leak across workspaces
- **WHEN** two workspaces each hold Spaces with Branches and Contributions
- **THEN** a member of one workspace cannot read or mutate the other's items, even by identifier

### Requirement: Every Contribution carries its provenance
The system SHALL preserve author, Branch, original source, tool/model when known, timestamp and transformation history on every Contribution, readable back exactly as stored.

#### Scenario: Provenance round-trips
- **WHEN** a Contribution is proposed with source, tool/model and transformation history
- **THEN** a later read returns exactly those values alongside author, Branch and timestamps
