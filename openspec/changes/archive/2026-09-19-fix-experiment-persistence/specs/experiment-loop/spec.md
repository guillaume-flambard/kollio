# experiment-loop Specification

## Purpose

Carry the experiment loop on the initiative detail: create, launch, record results, complete or cancel, and confirm the learning, in the product's own vocabulary. A record the API acknowledges has to be there afterwards.

## ADDED Requirements

### Requirement: A recorded experiment survives the request that created it (EP-01)

The API SHALL persist the records it acknowledges. An experiment, an outcome and a confirmed learning written through the experiment routes SHALL be readable from a session opened after the request that wrote them.

#### Scenario: An experiment is created and read back

- **WHEN** a member creates an experiment through the API and the response carries its identifier
- **THEN** an experiment with that identifier exists in the database
- **AND** a session opened after the request reads it

#### Scenario: An outcome is recorded and read back

- **WHEN** a member records an outcome on an experiment
- **THEN** the outcome is readable from a session opened after the request

#### Scenario: A confirmed learning is read back

- **WHEN** a member confirms the learning of a completed experiment
- **THEN** the learning is readable from a session opened after the request, with its confirmation
