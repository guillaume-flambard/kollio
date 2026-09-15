# benchmark Specification

## Purpose

Measure whether full Kollio beats a bare model, blind, and reproducibly without a provider.

## Requirements

### Requirement: Three arms run over the fixture set from one command (BM-01)
Three arms SHALL run over the fixture set from one command: A bare model on the prompt alone, B visible model without company memory, C full Kollio with memory, active objectives and constraints, confirmed learnings and Known/Assumed/Unknown.

#### Scenario: One command runs all arms
- **WHEN** the benchmark harness runs over the fixture set
- **THEN** arm A runs the bare model on the prompt alone
- **AND** arm B runs the visible model without company memory
- **AND** arm C runs full Kollio with memory, active objectives and constraints, confirmed learnings and Known/Assumed/Unknown

### Requirement: Company memory is the only substantive difference (BM-02)
A and B SHALL be given no company memory; only C SHALL be, and that SHALL be the only substantive difference across the arms.

#### Scenario: Memory isolation
- **WHEN** arms A, B and C are compared
- **THEN** no arm but C receives company memory
- **AND** no other substantive difference separates the arms

### Requirement: The scoring sheet is anonymous (BM-03)
The scoring sheet SHALL be anonymous: the rater-facing document SHALL have no arm labels, and the position-to-arm key SHALL be kept apart from it.

#### Scenario: Rater document de-blinded only by the key
- **WHEN** a rater receives the scoring sheet
- **THEN** it carries no arm label
- **AND** the position-to-arm key is stored separately from it

### Requirement: Runs can be recorded and replayed (BM-04)
Runs SHALL be recordable and replayable so a later model or prompt change is compared with no live call.

#### Scenario: Recorded run replayed
- **WHEN** a recorded run is replayed after a model or prompt change
- **THEN** the comparison needs no live call

### Requirement: Live provider calls are opt-in and budgeted (BM-05)
Live provider calls SHALL be opt-in and budgeted; the default path and CI SHALL make none.

#### Scenario: CI makes no live call
- **WHEN** the benchmark runs in CI
- **THEN** no live provider call is made

### Requirement: The verdict de-blinds ratings and names a product problem (BM-06)
The verdict SHALL de-blind ratings and state whether C clearly beats A; if it does not, it SHALL report a product problem, not a scoring accident.

#### Scenario: C does not clearly beat A
- **WHEN** the de-blinded verdict shows C not clearly ahead of A
- **THEN** the harness reports a product problem
- **AND** does not present it as a scoring accident
