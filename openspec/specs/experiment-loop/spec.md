# experiment-loop Specification

## Purpose

Carry the experiment loop on the initiative detail: create, launch, record results, complete or cancel, and confirm the learning, in the product's own vocabulary.

## Requirements

### Requirement: The section lists experiments and offers the create action (EX-01)
The initiative detail's Experiments section SHALL list the initiative's experiments with their localized status, and when there is none SHALL show an empty state with the create action instead of a blank area.

#### Scenario: Experiments listed
- **WHEN** a member opens the initiative detail
- **THEN** the section lists the experiments with their localized status

#### Scenario: No experiment yet
- **WHEN** the initiative has no experiment
- **THEN** the section shows an empty state with the create action

### Requirement: A member creates an experiment (EX-02)
A member SHALL create an experiment with a title, a hypothesis, a success metric and optional baseline and target; the new experiment SHALL start `proposed` and open its detail.

#### Scenario: Create an experiment
- **WHEN** a member submits a title, a hypothesis and a success metric
- **THEN** the experiment starts `proposed`
- **AND** its detail opens

### Requirement: A member launches a proposed experiment (EX-03)
A member SHALL launch a proposed experiment, moving it to `running`.

#### Scenario: Launch
- **WHEN** a member launches a proposed experiment
- **THEN** it moves to `running`

### Requirement: A member records results (EX-04)
A member SHALL record a result on an experiment: metric, value, optional unit, observed date, comment and a qualitative note. Several results SHALL accumulate and be listed.

#### Scenario: Results accumulate
- **WHEN** a member records a result, then another
- **THEN** both results are listed against the experiment

### Requirement: A member completes or cancels (EX-05)
A member SHALL complete a running experiment, moving it to `completed`; completing SHALL surface the drafted learning. A member MAY cancel a proposed or running experiment instead.

#### Scenario: Complete surfaces the learning
- **WHEN** a member completes a running experiment
- **THEN** the experiment moves to `completed`
- **AND** the drafted learning is surfaced

#### Scenario: Cancel
- **WHEN** a member cancels a proposed or running experiment
- **THEN** the experiment moves to `cancelled`

### Requirement: A member confirms the learning (EX-06)
A member SHALL edit and confirm the learning. A confirmed learning SHALL be shown as read-only and MUST NOT offer to return to draft.

#### Scenario: Confirmed learning is read-only
- **WHEN** a member confirms the learning
- **THEN** it is shown read-only
- **AND** no control offers to return it to draft

### Requirement: A non-member reads but cannot write (EX-07)
A non-member SHALL read the experiments, their results and the learning, but MUST NOT be offered any write form.

#### Scenario: Non-member reads the loop
- **WHEN** a non-member opens the initiative detail
- **THEN** the experiments, their results and the learning are readable
- **AND** no write form is offered

### Requirement: Refusals are explained in the member's locale (EX-08)
An action the API refuses with `experiment_rule` (422) SHALL be explained in the member's locale, not shown as a raw server string.

#### Scenario: Rule refusal
- **WHEN** the API refuses an action with `experiment_rule`
- **THEN** the interface explains it in the member's locale

### Requirement: Every step has its states (EX-09)
Each step SHALL have empty, loading and error states.

#### Scenario: Loading and error
- **WHEN** a step is in flight or fails
- **THEN** the interface shows its loading or error state
