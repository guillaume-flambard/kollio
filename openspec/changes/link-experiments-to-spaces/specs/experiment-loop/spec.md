## ADDED Requirements

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
