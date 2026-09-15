## Purpose

Keep a launched constraint analysis alive against a thinking model: structured
model calls ask for the JSON they need and wait long enough for it, instead of
failing on a fixed, too-short timeout.

## ADDED Requirements

### Requirement: Structured model calls do not think and do not time out early (LT-01)
Every structured-output chat completion the API issues SHALL carry an explicit
directive that disables model reasoning, and SHALL be bounded by a timeout
read from configuration rather than a fixed constant.

#### Scenario: Structured call disables model reasoning
- **WHEN** the constraint analysis gateway issues a structured-output chat completion
- **THEN** the request body SHALL set the reasoning directive to false
- **AND** SHALL keep the routed model, the strict JSON schema and the token limit unchanged

#### Scenario: Analysis survives provider latency variance
- **WHEN** a single model call takes longer than the previous fixed limit but within the configured timeout
- **THEN** the call SHALL complete and return its validated report
- **AND** the workflow SHALL not fail with a read timeout

#### Scenario: Timeout is configuration
- **WHEN** an operator sets the model request timeout for a deployment
- **THEN** both the constraint analysis gateway and the competition gateway SHALL build their client with that value
