## ADDED Requirements

### Requirement: Model transmission is explicitly authorised
The system SHALL transmit workspace material to a model only when a permitted actor selects the excerpts and the workspace has approved that provider.

#### Scenario: Unapproved provider is configured
- **WHEN** a workflow resolves a provider not approved for its workspace
- **THEN** the invocation SHALL be refused
- **AND** no source content SHALL leave Kollio.

### Requirement: Every transmission is auditable
The system SHALL record the actor, provider, model, selected excerpt identifiers, outcome and time for each model transmission without duplicating source bodies in the audit record.

#### Scenario: A model call completes
- **WHEN** an approved model call succeeds or fails
- **THEN** its audit record SHALL identify the actor, provider, model and selected excerpts
- **AND** it SHALL NOT contain a second copy of the source body.

### Requirement: Customer controls data lifecycle
The system SHALL let a workspace administrator export its data, request deletion, and read configured retention and deletion timing.

#### Scenario: An administrator requests their workspace data
- **WHEN** a workspace administrator opens data controls
- **THEN** they SHALL be able to request export or deletion
- **AND** the configured retention and deletion timing SHALL be visible.
