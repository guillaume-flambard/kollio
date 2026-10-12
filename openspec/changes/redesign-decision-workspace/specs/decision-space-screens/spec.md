## MODIFIED Requirements

### Requirement: The Space screen frames the question and its loop

The Space screen at `/workspace/decision-spaces/[spaceId]` SHALL carry the question, its owner, its status, its deadline and its participants. It SHALL organise the six addressable section routes into the three visible product moments: frame the decision (Explore and Converge), choose with reasons (Options and Decision), and record reality (Experiment and Learning). Each section SHALL remain a route of its own. A section whose capability has not shipped SHALL say what will live there instead of rendering an empty shell that reads as broken.

#### Scenario: The header frames the Space

- **WHEN** a member opens a Space
- **THEN** the question, owner, status, deadline and participants of that Space are visible
- **AND** every participant is named

#### Scenario: Every section is reachable

- **WHEN** a member opens the Space
- **THEN** the three product moments and their six section routes are offered as navigation
- **AND** each of the six routes renders without an error

#### Scenario: The active section has context

- **WHEN** a member opens one of the six section routes
- **THEN** its parent product moment and its active section are distinguishable in words and not by colour alone
- **AND** the member can reach an adjacent section without leaving the Space

#### Scenario: An empty section says what will live there

- **WHEN** a member opens a section whose capability has not shipped
- **THEN** the section says what will live there
- **AND** it does not present itself as a failure and invents no content

### Requirement: The Space status is readable and only permitted transitions are offered

The status SHALL be stated in words, not as a raw value. Every transition the API permits from the current status SHALL be reachable through one contextual human action, and a transition the API refuses SHALL NOT be offered.

#### Scenario: The status is readable

- **WHEN** a member opens a Space
- **THEN** the status is stated as a word in the reader's language

#### Scenario: A permitted transition is applied

- **WHEN** a member takes a transition the API permits from the current status
- **THEN** the new status is visible on the Space screen
- **AND** it is still the status after the page is reloaded

#### Scenario: A transition the API refuses is not offered

- **WHEN** a member looks at the transitions offered for the current status
- **THEN** no transition that skips a step, and no transition out of the current status that the lifecycle does not declare, is offered

#### Scenario: The transition explains its consequence

- **WHEN** a member opens the contextual transition action
- **THEN** the action states the next lifecycle state in the reader's language
- **AND** a reopening transition still requires its reason before it is sent

### Requirement: Navigation orders Spaces before Initiatives

The workspace navigation SHALL make Inbox and Decision Spaces the primary connected-product destinations, followed by workspace settings. The legacy idea Explorer SHALL remain reachable at `/workspace/ideas` but SHALL not compete with Decision Spaces in the primary navigation. Exactly one entry SHALL be active for the current primary route.

#### Scenario: Three entries with one active

- **WHEN** a member is on a Space screen
- **THEN** Decision Spaces is the active primary navigation entry
- **AND** Inbox and Settings are not marked active

#### Scenario: A member addresses the legacy Explorer

- **WHEN** a member opens `/workspace/ideas`
- **THEN** the Explorer keeps working at that route
- **AND** the primary navigation does not present it as a peer of Inbox and Decision Spaces
