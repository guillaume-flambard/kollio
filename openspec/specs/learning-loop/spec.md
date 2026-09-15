# learning-loop Specification

## Purpose

Turn a completed experiment into company memory: an experiment runs, outcomes accumulate, and a confirmed learning never returns to draft.

## Requirements

### Requirement: Experiment lifecycle
The system SHALL create an experiment from an initiative with a title, a hypothesis, a success metric and optional baseline and target, starting `proposed`, and SHALL move it through `running` to `completed` or `cancelled`, where `completed` and `cancelled` are terminal.

#### Scenario: Experiment created
- **WHEN** a member creates an experiment with a title, a hypothesis and a success metric
- **THEN** the system stores it as `proposed`

#### Scenario: Illegal transition refused
- **WHEN** an unknown or illegal target state is requested
- **THEN** the system refuses it with a 422 carrying the rule message

### Requirement: Outcomes accumulate
The system SHALL let any member who can read the initiative record an outcome against a running or completed experiment, with metric, value, optional unit, observed date, comment and a qualitative note, and SHALL accumulate several outcomes on one experiment.

#### Scenario: Several outcomes recorded
- **WHEN** a member records an outcome against a running experiment, then another
- **THEN** both outcomes are stored against that experiment

#### Scenario: Outsider sees nothing
- **WHEN** a caller outside the workspace attempts to record an outcome
- **THEN** the system responds 404

### Requirement: Completing drafts a learning
The system SHALL draft a learning on completion from the hypothesis, the metric, the target and the recorded outcomes, with the outcome ids pinned.

#### Scenario: Learning drafted
- **WHEN** a running experiment is completed
- **THEN** the system drafts a learning pinned to the recorded outcome ids

### Requirement: A confirmed learning is final
The system SHALL let a member edit the drafted text and confirm it, recording who confirmed it and moving it from `draft` to `confirmed`, and a confirmed learning SHALL never return to draft.

#### Scenario: Learning confirmed
- **WHEN** a member edits and confirms the drafted learning
- **THEN** the learning is `confirmed` and records who confirmed it

#### Scenario: Confirmed learning stays confirmed
- **WHEN** any caller attempts to move a confirmed learning back to draft
- **THEN** the system refuses it

### Requirement: A learning is reachable from its experiment and its initiative
The system SHALL make a learning readable by its experiment and by its initiative.

#### Scenario: Learning read by initiative
- **WHEN** a member reads the initiative that owns the experiment
- **THEN** the confirmed learning is reachable from it
