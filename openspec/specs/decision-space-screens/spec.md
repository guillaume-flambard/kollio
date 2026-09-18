# decision-space-screens Specification

## Purpose
TBD - created by archiving change add-decision-space-screens. Update Purpose after archive.

## Requirements

### Requirement: The workspace shows the Decision Spaces it owns

`/workspace` SHALL be the workspace's Decision Space list rather than the idea Explorer: each Space named by its question, with its owner, status, deadline and participant count. A workspace that owns none SHALL be told so rather than shown a broken list.

#### Scenario: Spaces listed

- **WHEN** a member opens `/workspace` in a workspace that owns Decision Spaces
- **THEN** every Space of that workspace is listed with its question, owner, status and deadline
- **AND** the count of participants is visible for each Space

#### Scenario: Nothing yet

- **WHEN** a member opens `/workspace` in a workspace that owns no Decision Space
- **THEN** the screen says the workspace has none yet and offers the way to open the first one
- **AND** no error state is shown

#### Scenario: A Space from another workspace is not reachable

- **WHEN** a member addresses a Space whose workspace is not theirs
- **THEN** the screen reports that the Space was not found
- **AND** nothing about that Space is rendered

### Requirement: A member opens a Decision Space from the list

A workspace member SHALL open a Space by giving the question the workspace must converge on. The question SHALL be required, and opening SHALL land on the new Space's own screen.

#### Scenario: Opened from the form

- **WHEN** a member submits a non-blank question from the open form
- **THEN** the Space is created and the member lands on that Space's screen
- **AND** the question they typed is the question shown

#### Scenario: A blank question is refused

- **WHEN** a member submits an empty or whitespace-only question
- **THEN** the form reports that the question is required
- **AND** no Space is created

### Requirement: The Space screen frames the question and its loop

The Space screen at `/workspace/decision-spaces/[spaceId]` SHALL carry the question, its owner, its status, its deadline and its participants, and SHALL offer the six sections the blueprint names: Explore, Converge, Options, Decision, Experiment and Learning. Each section SHALL be a route of its own. A section whose capability has not shipped SHALL say what will live there instead of rendering an empty shell that reads as broken.

#### Scenario: The header frames the Space

- **WHEN** a member opens a Space
- **THEN** the question, owner, status, deadline and participants of that Space are visible
- **AND** every participant is named

#### Scenario: Every section is reachable

- **WHEN** a member opens the Space
- **THEN** the six sections are offered as navigation
- **AND** each of the six routes renders without an error

#### Scenario: An empty section says what will live there

- **WHEN** a member opens a section whose capability has not shipped
- **THEN** the section says what will live there
- **AND** it does not present itself as a failure and invents no content

### Requirement: The Space status is readable and only permitted transitions are offered

The status SHALL be stated in words, not as a raw value. Every transition the API permits from the current status SHALL be reachable from the screen, and a transition the API refuses SHALL NOT be offered.

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

### Requirement: Ideas stay reachable at their own route

The idea Explorer SHALL keep working exactly as it did, at `/workspace/ideas`. Nothing of the pre-pivot product SHALL be removed by this slice; it is re-homed.

#### Scenario: The Explorer keeps working

- **WHEN** a member opens `/workspace/ideas`
- **THEN** the Explorer renders its filters, its result rows and its preview panel as before
- **AND** its filters and pagination keep their place in the address

### Requirement: Navigation orders Spaces before Initiatives

The workspace navigation SHALL name the three areas of the product in the order the blueprint reads them: Decision spaces, then Initiatives, then the workspace settings. Exactly one entry SHALL be active for the current route, and `/workspace/ideas` SHALL NOT be read as the Spaces list.

#### Scenario: Three entries with one active

- **WHEN** a member is on a Space screen
- **THEN** Decision spaces is the active entry
- **AND** when they are on the Explorer, Initiatives is the active entry and Decision spaces is not
