## Purpose

Defines a shared multilingual vector space for comparing French and English content while
retaining enough provenance to prevent incompatible vectors from being mixed.

## ADDED Requirements

### Requirement: Embeddings use the approved shared vector space
The system SHALL create idea and profile embeddings with `text-embedding-3-large` at exactly
1,536 dimensions for both French and English content.

#### Scenario: French idea and English profile are embedded
- **WHEN** French and English content are submitted for embedding
- **THEN** both vectors SHALL have 1,536 dimensions and identify the same source model

#### Scenario: Provider returns an incompatible vector
- **WHEN** the provider returns an unexpected count, index, or dimension
- **THEN** the system SHALL reject the operation without storing partial vectors

### Requirement: Stored vectors retain compatibility metadata
Each stored embedding MUST retain its source model, dimension, original language, source record,
and update provenance. Retrieval SHALL exclude vectors from incompatible spaces.

#### Scenario: Vector space changes
- **WHEN** a stored vector uses another model or dimension
- **THEN** it SHALL not participate in matching against the approved shared space

### Requirement: Real output verifies multilingual retrieval
Phase 0 SHALL use real provider output to prove that a reviewed French and English semantic pair
can be stored and retrieved across languages.

#### Scenario: Cross-language semantic retrieval
- **WHEN** a reviewed French query is compared with a reviewed English candidate set
- **THEN** the expected counterpart SHALL rank ahead of unrelated candidates

#### Scenario: Provider credential is absent
- **WHEN** verification has no approved embedding credential
- **THEN** it SHALL report the criterion as unverified and SHALL not substitute fake vectors
