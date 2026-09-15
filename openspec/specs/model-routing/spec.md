# model-routing Specification

## Purpose

Route every gateway call by named task class rather than by call-site model names, so the tier a call runs on is declared, observable and reproducible offline.

## Requirements

### Requirement: Calls declare a task class (RT-01)
Every LLM gateway call SHALL declare a `TaskClass`; each class SHALL map to a configured model through `resolve_model`.

#### Scenario: A gateway call is made
- **WHEN** a caller invokes the LLM gateway
- **THEN** it declares a `TaskClass`
- **AND** the class maps to a configured model through `resolve_model`

### Requirement: Visible intelligence is distinguished from commodity work (RT-02)
The constraint analysis SHALL be a visible-intelligence class and SHALL request the visible model; a commodity class such as extraction SHALL not.

#### Scenario: Constraint analysis requests the visible model
- **WHEN** the constraint analysis calls the gateway
- **THEN** it declares the visible-intelligence class
- **AND** requests the visible model

#### Scenario: Extraction requests the commodity model
- **WHEN** a commodity class such as extraction calls the gateway
- **THEN** it does not request the visible model

### Requirement: Local development and CI run without premium credentials (RT-03)
Local development and CI SHALL run the full loop without premium credentials: an unset `LLM_MODEL_VISIBLE` SHALL fall back to `LLM_MODEL`, and no live provider call SHALL be made in CI (recorded fixtures).

#### Scenario: Visible model unset
- **WHEN** `LLM_MODEL_VISIBLE` is unset
- **THEN** the visible tier falls back to `LLM_MODEL`

#### Scenario: CI
- **WHEN** the loop runs in CI
- **THEN** no live provider call is made and recorded fixtures are used

### Requirement: The routing decision is observable (RT-04)
The task class and the resolved model SHALL be visible per run in the existing OpenTelemetry attributes; no vendor pricing API SHALL be called in code.

#### Scenario: A run is traced
- **WHEN** a run is traced
- **THEN** the task class and the resolved model appear in the OpenTelemetry attributes
- **AND** no vendor pricing API is called in code
