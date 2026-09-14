## Purpose

Hold the durable company context of a workspace — profile, objectives and constraints — as the reality every analysis reads.

## ADDED Requirements

### Requirement: Workspace-scoped context privacy
The system SHALL expose a workspace's company context only to authenticated members of that workspace.

#### Scenario: Member reads the context
- **WHEN** a workspace member requests the company context of their workspace
- **THEN** the system returns the profile (possibly empty), its objectives and its constraints
- **AND** answers in the request locale

#### Scenario: Non-member requests the context
- **WHEN** an authenticated non-member requests the company context of a workspace they do not belong to
- **THEN** the system responds as if the workspace were not found
- **AND** discloses no profile, objective or constraint content

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a company context
- **THEN** the system responds unauthorized without touching persistence

### Requirement: Members maintain the company profile
The system SHALL let any workspace member create or update the company profile of their workspace.

#### Scenario: Profile created then read back
- **WHEN** a member saves a profile with name, description, business model, products or services, customer segments, markets and structure
- **THEN** the system persists it for that workspace
- **AND** a later read returns exactly those values

#### Scenario: Profile updated in place
- **WHEN** a member saves a profile a second time
- **THEN** the system updates the existing profile rather than duplicating it
- **AND** the workspace still exposes exactly one profile

#### Scenario: Profile untouched on read
- **WHEN** a member reads a workspace that has no profile yet
- **THEN** the system returns an empty profile instead of an error

### Requirement: Members maintain objectives
The system SHALL let any workspace member create, edit, activate, archive and prioritise objectives in their workspace.

#### Scenario: Objective created
- **WHEN** a member creates an objective with a title
- **THEN** the system persists it as active and non-priority by default

#### Scenario: Objective lifecycle edited
- **WHEN** a member updates an objective's title, state or priority
- **THEN** the system persists the change
- **AND** accepts only the states `active` and `archived`

#### Scenario: Unknown objective state refused
- **WHEN** a member submits an objective state outside `active` and `archived`
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

### Requirement: Members maintain constraints
The system SHALL let any workspace member create, edit and archive constraints in their workspace.

#### Scenario: Constraint created
- **WHEN** a member creates a constraint with a title
- **THEN** the system persists it as active

#### Scenario: Constraint edited and archived
- **WHEN** a member updates a constraint's title, detail or state
- **THEN** the system persists the change
- **AND** accepts only the states `active` and `archived`

#### Scenario: Non-member cannot write
- **WHEN** a non-member attempts to create or update any context item
- **THEN** the system responds as if the collection did not exist
- **AND** stores nothing

### Requirement: Context items stay inside their workspace
The system SHALL scope every context read and write to a single workspace and never leak items across workspaces.

#### Scenario: Two workspaces with similar items
- **WHEN** two workspaces each hold a profile, objectives and constraints
- **THEN** a member of one workspace sees only that workspace's items
- **AND** cannot read or mutate the other workspace's items, even by identifier
