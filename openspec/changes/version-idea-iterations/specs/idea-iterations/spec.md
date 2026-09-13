## Purpose

Provide a safe, workspace-isolated, append-only history for evolving ideas.

## ADDED Requirements

### Requirement: Members can inspect iteration history
The system SHALL return an idea's iterations only to authenticated members of its workspace, ordered from newest to oldest.

#### Scenario: Member reads history
- **WHEN** a workspace member requests an idea's iterations
- **THEN** the system returns snapshots, parent links, revisions, authors, branches, proposal statuses, original message languages and timestamps

#### Scenario: Non-member requests history
- **WHEN** an authenticated non-member requests an idea's iterations
- **THEN** the system responds as if the idea were not found
- **AND** discloses no iteration content

### Requirement: Main history is owner controlled
The system SHALL allow only the idea owner to append a snapshot directly to the main branch.

#### Scenario: Owner advances the idea
- **WHEN** the owner submits a valid snapshot with the current main head as expected parent
- **THEN** the system appends a main iteration
- **AND** updates the idea projection to that snapshot

#### Scenario: Concurrent main update wins first
- **WHEN** the expected parent no longer matches the current main head
- **THEN** the system rejects the write as a conflict
- **AND** stores no iteration or partial projection update

### Requirement: Members can propose changes
The system SHALL allow a workspace member to append a pending snapshot to a named proposal branch.

#### Scenario: Member creates a proposal
- **WHEN** a member submits a valid snapshot on a non-main branch
- **THEN** the system appends a pending proposal without changing the idea projection

### Requirement: Owner resolves proposals
The system SHALL allow only the idea owner to accept or reject a pending proposal.

#### Scenario: Owner accepts a proposal
- **WHEN** the owner accepts a pending proposal against the current main head
- **THEN** the proposal becomes accepted
- **AND** a new main iteration copies its snapshot
- **AND** the idea projection changes atomically

#### Scenario: Owner rejects a proposal
- **WHEN** the owner rejects a pending proposal
- **THEN** the proposal becomes rejected
- **AND** the main history and idea projection remain unchanged

### Requirement: Rollback preserves history
The system SHALL implement rollback by appending a new main iteration from an earlier snapshot.

#### Scenario: Owner restores an earlier version
- **WHEN** the owner selects an earlier iteration and supplies the current main head
- **THEN** the system appends a new main iteration containing the selected snapshot
- **AND** no existing iteration is modified or deleted
