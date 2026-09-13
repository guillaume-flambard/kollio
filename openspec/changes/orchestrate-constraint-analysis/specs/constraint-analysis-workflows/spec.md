## Purpose

Provide workspace-isolated, durable and human-reviewed constraint analysis for a versioned idea snapshot.

## ADDED Requirements

### Requirement: Members can launch one durable analysis
The system SHALL allow an authenticated workspace member to launch a constraint analysis for an accessible idea snapshot.

#### Scenario: Member launches an analysis
- **WHEN** a workspace member requests an analysis and no active workflow exists for the same idempotency key
- **THEN** the system stores a queued workflow containing the idea snapshot, source iteration and requested locale
- **AND** dispatches its workflow identifier to the task queue

#### Scenario: Launch is repeated
- **WHEN** the member repeats a launch with the same idempotency key
- **THEN** the system returns the existing workflow
- **AND** does not dispatch duplicate work

#### Scenario: Non-member launches an analysis
- **WHEN** an authenticated non-member requests an analysis
- **THEN** the system responds as if the idea were not found

### Requirement: Members can inspect workflow status
The system SHALL expose an analysis workflow only to members of its idea workspace.

#### Scenario: Member reads a workflow
- **WHEN** a workspace member requests a workflow
- **THEN** the system returns its lifecycle status, current step, locale, timestamps and validated result when available

### Requirement: Owner controls human review
The system SHALL allow only the idea owner to resolve a workflow awaiting review.

#### Scenario: Owner approves a finding
- **WHEN** the owner approves the current pending review
- **THEN** the system resumes the same LangGraph thread
- **AND** persists one final result linked to the analyzed snapshot

#### Scenario: Owner rejects a finding
- **WHEN** the owner rejects the current pending review
- **THEN** the system resumes the same LangGraph thread
- **AND** marks the workflow rejected without creating a final analysis

#### Scenario: Review is stale
- **WHEN** a review targets a workflow that is no longer awaiting review
- **THEN** the system rejects the transition as a conflict

### Requirement: Model output is validated before storage
The system SHALL validate the full constraint result through a strict Pydantic schema before exposing it for review or persistence.

#### Scenario: Valid result is produced
- **WHEN** the model returns the requested locale, exactly five named factors, bounded scores and only supplied evidence identifiers
- **THEN** the workflow stores the validated draft and enters awaiting review

#### Scenario: Invalid result is produced
- **WHEN** any model field violates the result contract
- **THEN** the workflow enters failed
- **AND** no final analysis is stored

### Requirement: Trace context crosses the queue
The system SHALL propagate W3C trace context from the launch request through task execution, graph nodes and model calls.

#### Scenario: Worker processes a queued workflow
- **WHEN** a Taskiq worker receives a workflow command
- **THEN** its execution span is a descendant of the launch request trace
- **AND** the trace identifies the workflow, idea and requested locale without containing provider secrets

### Requirement: Dispatch failures remain recoverable
The system SHALL retain durable workflow intent when Redis is temporarily unavailable and SHALL
allow the same idempotent request to finish dispatching after the queue recovers.

#### Scenario: Initial dispatch fails
- **WHEN** PostgreSQL commits a workflow but Redis rejects its first dispatch attempt
- **THEN** the API reports temporary unavailability
- **AND** repeating the same idempotent request dispatches the existing workflow without creating another workflow

#### Scenario: Two launches arrive concurrently
- **WHEN** two requests use the same idea and idempotency key at the same time
- **THEN** both requests return the same workflow
- **AND** the system creates and dispatches that workflow exactly once

#### Scenario: Review dispatch fails
- **WHEN** the owner records a review decision but Redis rejects its first dispatch attempt
- **THEN** repeating the same decision dispatches the existing review without changing the decision

### Requirement: Production configuration fails closed
The API and worker SHALL refuse production startup when identity validation, model gateway or
OpenTelemetry export configuration is incomplete.

#### Scenario: Required production setting is missing
- **WHEN** a production process starts without a required identity, model gateway or trace export setting
- **THEN** configuration validation fails before the process accepts work
