# matching/multilingual-embeddings Specification (delta)

## ADDED Requirements

### Requirement: The active space can be selected from the environment (EM-01)

A deployment SHALL be able to choose the active embedding space through its
environment, supplying the model, the source model and the dimension as text,
and the application SHALL load that configuration without a validation error.
The accepted dimensions SHALL remain exactly 1,536 and 384, and any other value
SHALL fail configuration instead of starting on an unsupported space.

#### Scenario: Deployment selects the 1536-dimension space

- **WHEN** the environment supplies the space's model and source model and the
  dimension as the text `1536`
- **THEN** configuration SHALL load with a dimension of 1536 and the process
  SHALL start

#### Scenario: Unsupported dimension fails closed

- **WHEN** the environment supplies a dimension outside the two supported spaces
- **THEN** configuration SHALL fail naming the field and no process SHALL start

#### Scenario: Existing deployments keep the default

- **WHEN** no dimension is supplied
- **THEN** the local 384-dimension space SHALL remain the active default
