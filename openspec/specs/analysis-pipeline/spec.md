# analysis-pipeline Specification

## Purpose

Behind the single constraint analysis the member reads, run an ordered set of reasoning steps whose conclusion cannot silently skip the adversarial or evidentiary work.

## Requirements

### Requirement: One analysis runs an ordered adversarial pipeline (AP-01)
One analysis SHALL run, in order, analyst, challenger, evidence critic, company fit and synthesizer, and SHALL return exactly one `ConstraintAnalysisResult`.

#### Scenario: The pipeline runs in order
- **WHEN** a member launches a constraint analysis
- **THEN** the engine runs analyst, then challenger, then evidence critic, then company fit, then synthesizer, in that order
- **AND** returns exactly one `ConstraintAnalysisResult`

### Requirement: The conclusion cannot skip the challenge or the evidence (AP-02)
The synthesizer SHALL receive the challenger and the evidence critic; if either produced nothing, the run SHALL fail and publish no conclusion.

#### Scenario: A step produced nothing
- **WHEN** the challenger or the evidence critic produces no output
- **THEN** the run fails
- **AND** no conclusion is published

### Requirement: The pipeline routes by task class (AP-03)
The case-building step SHALL run on the commodity model tier; the challenge, evidence judgment, company fit and synthesis SHALL run on the visible model tier, routed by task class.

#### Scenario: Case building uses the commodity tier
- **WHEN** the analyst step runs
- **THEN** it requests the commodity model tier by task class

#### Scenario: Judgment steps use the visible tier
- **WHEN** the challenger, evidence critic, company fit and synthesizer steps run
- **THEN** each requests the visible model tier by task class

### Requirement: Every step is persisted per run (AP-04)
The system SHALL persist every step per run (name, tier, model, output) so the conclusion can be replayed and audited.

#### Scenario: A run is audited
- **WHEN** a completed run is inspected
- **THEN** each step's name, tier, model and output are available for replay

### Requirement: The member response shape is unchanged (AP-05)
The member's response shape SHALL remain one analysis with the Known/Assumed/Unknown factors and contradictions from #58.

#### Scenario: The member reads one analysis
- **WHEN** the pipeline completes
- **THEN** the member reads a single analysis carrying the Known/Assumed/Unknown factors and contradictions

### Requirement: The pipeline is provable without a live provider (AP-06)
Local development and CI SHALL exercise the whole pipeline with no live provider call (scripted gateway, recorded fake server), and with `LLM_MODEL_VISIBLE` unset every step SHALL still run.

#### Scenario: CI runs the full pipeline offline
- **WHEN** CI runs the constraint analysis pipeline with a scripted gateway
- **THEN** every step runs with no live provider call

#### Scenario: The visible model is unset
- **WHEN** `LLM_MODEL_VISIBLE` is unset
- **THEN** every step still runs
