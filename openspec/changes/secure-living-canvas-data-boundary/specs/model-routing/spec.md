## MODIFIED Requirements

### Requirement: Calls declare a task class (RT-01)
Every LLM gateway call SHALL declare a `TaskClass` and SHALL resolve an approved provider and model through workspace policy before transmission.

#### Scenario: A gateway call is made
- **WHEN** a caller invokes the LLM gateway
- **THEN** it SHALL declare a `TaskClass`
- **AND** it SHALL resolve an approved provider and model through workspace policy.

#### Scenario: Provider is not approved
- **WHEN** a call resolves a model whose provider is not approved for the workspace
- **THEN** the gateway SHALL refuse before sending source content.
