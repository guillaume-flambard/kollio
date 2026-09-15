# matching/multilingual-embeddings Specification

## Purpose

Extend the shared multilingual vector space with a self-hosted alternative so
matching is provable without a vendor embedding credential, while keeping
spaces isolated by model and dimensions.

## Requirements

### Requirement: Embeddings use an explicitly versioned shared vector space
The system SHALL create idea and profile embeddings in exactly one active
space at a time: either `text-embedding-3-large` at 1,536 dimensions or
`intfloat/multilingual-e5-small` at 384 dimensions, for both French and
English content. The active space is fixed per deployment by configuration.

#### Scenario: French idea and English profile are embedded in the local space
- **WHEN** French and English content are submitted for embedding with the
  local space active
- **THEN** both vectors SHALL have 384 dimensions and identify
  `intfloat/multilingual-e5-small` as the source model

#### Scenario: Provider returns an incompatible vector
- **WHEN** the provider returns an unexpected count, index, or dimension
- **THEN** the system SHALL reject the operation without storing partial vectors

### Requirement: Stored vectors retain compatibility metadata
Each stored embedding MUST retain its source model, dimension, original
language, source record, and update provenance. Retrieval SHALL exclude
vectors from incompatible spaces, including OpenAI rows when the local space
is active and local rows when the OpenAI space is active.

#### Scenario: Active space changes
- **WHEN** a stored vector uses another model or dimension than the active space
- **THEN** it SHALL not participate in matching

### Requirement: Local embedding traffic needs no credential
The local embedding path SHALL require no API key at any layer (server,
gateway, application). A missing `OPENAI_API_KEY` SHALL NOT disable local
embedding or retrieval.

#### Scenario: OpenAI credential is absent with local space active
- **WHEN** embedding or retrieval runs without any OpenAI credential configured
- **THEN** it SHALL succeed through the local server and gateway alias

### Requirement: Recorded output verifies local multilingual retrieval
The suite SHALL prove, from one recorded real local-server output, that a
reviewed French query ranks its expected English semantic counterpart ahead
of unrelated candidates in the 384-dimensional space.

#### Scenario: Cross-language semantic retrieval in the local space
- **WHEN** a reviewed French query is compared with a reviewed English
  candidate set from the recording
- **THEN** the expected counterpart SHALL rank ahead of unrelated candidates

#### Scenario: Recording is replayed without the server
- **WHEN** CI runs without the local embedding server reachable
- **THEN** the recorded case SHALL evaluate without network calls
