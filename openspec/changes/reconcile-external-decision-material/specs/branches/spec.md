## ADDED Requirements

### Requirement: Source-backed Contributions retain typed provenance
The system SHALL retain a typed source-revision and excerpt reference when a Contribution is promoted from imported material, in addition to its existing provenance fields.

#### Scenario: Typed provenance round-trips
- **WHEN** a writer promotes an excerpt from imported material
- **THEN** a later Contribution read returns its source revision and excerpt reference
- **AND** existing Contributions without imported material remain readable unchanged
