# initiative-framing Specification

## Purpose

Let a workspace say what kind of initiative it is depositing, and speak of Initiatives in the B2B surface while the data model keeps calling them Ideas.

## Requirements

### Requirement: Every initiative carries a closed kind
The system SHALL record exactly one initiative type per idea, taken from a closed list, and SHALL refuse any other value.

#### Scenario: Deposit chooses a kind
- **WHEN** a member deposits an initiative with the `campaign` kind
- **THEN** the system stores `campaign`
- **AND** returns it in the deposit response, the idea read, and the workspace list

#### Scenario: Deposit omits the kind
- **WHEN** a member deposits an initiative without a kind
- **THEN** the system stores the default `idea` kind

#### Scenario: Unknown kind refused
- **WHEN** a caller submits a kind outside the closed list
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

### Requirement: The owner may change the kind
The system SHALL let only the idea owner change an initiative's kind after deposit.

#### Scenario: Owner re-classifies
- **WHEN** the owner updates the kind to `pricing`
- **THEN** the system stores it and later reads return `pricing`

#### Scenario: Non-owner refused
- **WHEN** a workspace member who is not the owner attempts the update
- **THEN** the system refuses as forbidden
- **AND** stores nothing

#### Scenario: Non-member gets nothing
- **WHEN** a caller outside the workspace attempts the update
- **THEN** the system responds as if the initiative were not found

### Requirement: Existing initiatives keep working
The system SHALL keep every idea readable when no kind was ever chosen.

#### Scenario: Rows predating the field
- **WHEN** an idea created before this change is read or listed
- **THEN** its kind is the default `idea`
- **AND** no read fails

### Requirement: The B2B surface says Initiative
The system SHALL present the workspace surfaces — explorer, deposit, detail, profiles, settings and navigation — as Initiatives in French and English, while code, database and API keep saying Idea.

#### Scenario: French workspace copy
- **WHEN** a French member browses the workspace area
- **THEN** no user-facing label calls the object an idée
- **AND** the kind selector offers the ten kinds in French

#### Scenario: English workspace copy
- **WHEN** an English member browses the workspace area
- **THEN** no user-facing label calls the object an idea
- **AND** the kind selector offers the ten kinds in English
