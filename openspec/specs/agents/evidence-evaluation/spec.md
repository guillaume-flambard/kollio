# agents/evidence-evaluation Specification

## Purpose
Defines repeatable evidence-grounded evaluations that detect regressions in agent judgment while
keeping provider calls structured, bounded, and separate from deterministic domain tests.

## Requirements

### Requirement: Agent decisions use validated structured output
Every competition finding SHALL conform to its schema, use the requested locale, and cite only
evidence identifiers present in the input.

#### Scenario: Provider returns prose instead of the schema
- **WHEN** a provider response cannot be validated as the declared structure
- **THEN** the finding SHALL be rejected and no side effect SHALL be committed

#### Scenario: Finding cites unknown evidence
- **WHEN** a finding cites an identifier absent from its input
- **THEN** the finding SHALL be rejected

### Requirement: Fixed cases measure known judgment failures
The suite SHALL replay reviewed immutable inputs covering named competitors, an observed empty
landscape, competitor-authored content, and failed research. Historical expectations SHALL remain
labeled where Kollio semantics differ.

#### Scenario: Recorded regression suite runs in CI
- **WHEN** CI runs without provider credentials
- **THEN** recorded cases SHALL be evaluated against explicit verdict and grounding criteria

#### Scenario: An expectation changes
- **WHEN** a reviewer changes the product meaning of a recorded case
- **THEN** the change SHALL be reviewed as a specification change rather than a lower threshold

### Requirement: Live evaluations are bounded and explicit
Live evaluations MUST be opt-in, rate limited, budget limited, and executed only in an authorized
context. A live evaluation failure SHALL fail its authorized run.

#### Scenario: Pull request has no provider secrets
- **WHEN** an untrusted pull request runs evaluations
- **THEN** it SHALL use recordings and SHALL make no provider call

#### Scenario: Authorized run exceeds its budget
- **WHEN** the evaluation budget or rate limit is exhausted
- **THEN** the run SHALL stop and report incomplete cases without treating them as passes
