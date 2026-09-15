## Purpose

Describe the people around an initiative by two axes — participation and business function — and let the owner add a colleague without an application.

## ADDED Requirements

### Requirement: Membership carries two axes
The system SHALL describe every participant by a participation from `owner`, `decision_maker`, `contributor`, `observer` and a business function from the closed twelve-value list.

#### Scenario: The owner adds a workspace member
- **WHEN** the owner adds a workspace member with participation `decision_maker` and function `finance`
- **THEN** the membership exists immediately
- **AND** reads return both axes

#### Scenario: Unknown function refused
- **WHEN** the owner adds a member with a function outside the closed list
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Non-owner cannot add
- **WHEN** a workspace member who is not the owner tries to add someone
- **THEN** the system refuses as forbidden

#### Scenario: The owner participation is never granted
- **WHEN** anyone tries to grant the `owner` participation
- **THEN** the system refuses it

### Requirement: The application names a function
The system SHALL keep the self-nomination application, with the applicant naming the business function they bring.

#### Scenario: A member applies
- **WHEN** a workspace member applies with a function and a note
- **THEN** the request is pending with that function
- **AND** accepting it creates a contributor membership with the same function

### Requirement: Legacy roles migrate onto the function axis
The system SHALL map every existing craft role and every existing sought value onto the business function axis during the migration, without data loss.

#### Scenario: Existing memberships
- **WHEN** the migration runs on rows carrying `designer`, `dev`, `commercial`, `growth`, `data`, `product` or `owner`
- **THEN** each becomes a business function and a participation (`owner` only for the owner row)
- **AND** no row is dropped
