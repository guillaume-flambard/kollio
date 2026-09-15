# constraint-analysis-workflows Specification (delta)

## ADDED Requirements

### Requirement: An abstention satisfies the domain contract (SA-01)

The system SHALL state, in the synthesizer prompt, every cross-field rule that
the domain validators enforce and that a JSON schema cannot express. The system
SHALL keep the domain validators themselves unchanged, so an inconsistent model
reply still fails closed rather than being stored.

#### Scenario: Abstention rule is stated where the model can read it
- **WHEN** the synthesizer prompt is loaded
- **THEN** it states that an unknown verdict requires every factor to be unknown, that no factor carries a score in that case, that the overall score stays empty, and that the contradictions list is empty

#### Scenario: No evidence yields a result the domain accepts
- **WHEN** a synthesis call runs with no supplied evidence
- **THEN** the result carries the unknown verdict, no overall score, five factors whose basis is unknown with no source ids and a named gap each, and an empty contradictions list
- **AND** the domain validator accepts that result

#### Scenario: The boundary still fails closed
- **WHEN** a synthesis reply pairs an unknown verdict with a scored or known factor
- **THEN** validation rejects it and the workflow records the failure
