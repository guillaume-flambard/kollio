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

### Requirement: An experiment can belong to a decision space
The system SHALL accept an optional decision space when an experiment is created, SHALL store the link, and SHALL refuse a link that crosses workspaces or names an option outside that space.

#### Scenario: Experiment created with a space
- **WHEN** a member creates an experiment against an idea and names a decision space of the same workspace
- **THEN** the experiment is stored with that link
- **AND** a later read returns it

#### Scenario: Experiment created with a space and an option
- **WHEN** a member names both a decision space and one of its options
- **THEN** both links are stored
- **AND** the option belongs to that space

#### Scenario: Link omitted
- **WHEN** a member creates an experiment without naming a space
- **THEN** the experiment carries no link
- **AND** the initiative path behaves exactly as before

#### Scenario: Space from another workspace refused
- **WHEN** a member names a decision space that does not belong to the idea's workspace
- **THEN** the system refuses the request as invalid
- **AND** stores no experiment

#### Scenario: Foreign option refused
- **WHEN** a member names an option that does not belong to the named space
- **THEN** the system refuses the request as invalid
- **AND** stores no experiment

#### Scenario: Option without a space refused
- **WHEN** a member names an option without naming a space
- **THEN** the system refuses the request as invalid
- **AND** stores no experiment

#### Scenario: Existing experiments are untouched
- **WHEN** the link is introduced
- **THEN** experiments created earlier keep no space
- **AND** they remain readable on their initiative

### Requirement: A decision space lists its experiments and learnings
The system SHALL expose a decision space's experiments, and the learnings behind them, to authenticated members of the owning workspace, and SHALL disclose nothing to anyone else.

#### Scenario: Experiments listed for a space
- **WHEN** a workspace member asks for a decision space's experiments
- **THEN** the system returns the experiments linked to that space
- **AND** returns only experiments of that space

#### Scenario: Learnings listed for a space
- **WHEN** a workspace member asks for a decision space's learnings
- **THEN** the system returns the learnings whose experiment is linked to that space
- **AND** returns each learning with its status, so a draft is told apart from a confirmed one

#### Scenario: Nothing yet
- **WHEN** the space holds no experiment
- **THEN** the system answers with an empty list rather than an error

#### Scenario: Non-member asks
- **WHEN** an authenticated non-member asks for a space's experiments or its learnings
- **THEN** the system responds as if the space were not found
- **AND** discloses no experiment, outcome or learning content

#### Scenario: Unknown space
- **WHEN** a member asks for the experiments of a space that does not exist
- **THEN** the system responds as if the space were not found

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller asks for a space's experiments or learnings
- **THEN** the system responds unauthorized without touching persistence
