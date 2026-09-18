# agents/evidence-evaluation Specification

## Purpose

Defines repeatable evidence-grounded evaluations that detect regressions in agent judgment while keeping provider calls structured, bounded, and separate from deterministic domain tests. The recorded corpus is the part that runs without credentials, so it has to be replayed through the same validation the runtime applies.

## ADDED Requirements

### Requirement: Reviewed recordings are replayed at the runtime boundary (AEE-04)

Every reviewed recording SHALL be replayed through the validation the runtime applies, so that a recording which no longer matches that boundary fails the suite instead of passing beside it. A recorded gate finding SHALL be accepted only if it conforms to the declared structure, names the requested locale, and cites only identifiers that the recording supplied. A recorded constraint analysis SHALL conform to the declared structure, including its refusal of fields the structure does not declare. A recording that no test replays SHALL be treated as a failure.

#### Scenario: A recorded gate finding is replayed

- **WHEN** the suite runs without provider credentials
- **THEN** each recorded gate finding SHALL be validated as the declared structure
- **AND** it SHALL be accepted only if its locale matches the request and every cited identifier was supplied in the input

#### Scenario: A recorded constraint analysis is replayed

- **WHEN** the suite runs
- **THEN** each recorded constraint analysis SHALL be validated as the declared structure
- **AND** a field the structure does not declare SHALL be refused

#### Scenario: A recording drifts from the boundary

- **WHEN** a reviewed recording is altered so that its locale, one of its citations, or its evidence rule no longer holds
- **THEN** the suite SHALL fail

#### Scenario: A recording is added and never replayed

- **WHEN** a fixture file exists that no test replays
- **THEN** the suite SHALL fail
