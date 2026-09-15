# vocabulary Specification

## Purpose

Make the golden path speak the product's vocabulary and acknowledge the moment a result becomes company memory.

## Requirements

### Requirement: A proposal line is an "Alternative" (VOC-01)
A proposal line SHALL be called an "Alternative", never a "branch", in the timeline and the proposal hint, in FR and EN.

#### Scenario: Timeline and hint
- **WHEN** a member reads the timeline or the proposal hint in FR or EN
- **THEN** a proposal line is called an "Alternative"
- **AND** it is never called a "branch"

### Requirement: Accepted reads "Accepted", in-flight reads "Analysis in progress" (VOC-02)
An accepted proposal SHALL read "Accepted", not "Merged"; the in-flight analysis SHALL read "Analysis in progress", not "running".

#### Scenario: Accepted proposal
- **WHEN** a member reads an accepted proposal
- **THEN** it reads "Accepted"
- **AND** it does not read "Merged"

#### Scenario: In-flight analysis
- **WHEN** a member reads an in-flight analysis
- **THEN** it reads "Analysis in progress"
- **AND** it does not read "running"

### Requirement: Confirming a learning is acknowledged (VOC-03)
Confirming a learning SHALL show "Added to the company memory" as a discrete, reduced-motion-safe state on the confirmed learning, not a silent swap.

#### Scenario: Learning confirmed
- **WHEN** a member confirms a learning
- **THEN** "Added to the company memory" appears as a discrete state on the confirmed learning
- **AND** the state is reduced-motion-safe

### Requirement: No technical jargon in the visible golden path (VOC-04)
No technical jargon (branch, merged, commit, run, workflow, repo, embedding, vector) SHALL appear in the visible golden-path strings; the design guard for tokens SHALL still pass.

#### Scenario: Golden-path strings
- **WHEN** the visible golden-path strings are read
- **THEN** no technical jargon appears
- **AND** the design guard for tokens still passes
