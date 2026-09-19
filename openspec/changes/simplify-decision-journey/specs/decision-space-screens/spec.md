# decision-space-screens Specification

## Purpose

A decision space is read and used as three plain-language moments: the decision to frame, the choice and its reasons, and what happened. The six section routes keep their paths and stay addressable, and the navigation groups them under those moments.

## ADDED Requirements

### Requirement: A decision space is navigated by three plain-language moments (SIMPLE-01)

The space shell SHALL present its section navigation as three named moments, each with a localized label and a one-line description, and SHALL mark the moment that owns the current route. The six section routes SHALL keep their paths, their deep links and their active state. A moment SHALL say what it holds when none of its sections has content, and SHALL name the next action when one is known. No write SHALL be invented, defaulted or auto-confirmed to shorten the journey.

#### Scenario: SIMPLE-01 A newcomer sees the question and the three moments

- **WHEN** a member opens a decision space
- **THEN** the navigation presents three moments with localized labels
- **AND** the question of the space is visible without opening a section
- **AND** words such as Branch, relation or cluster are not required to start

#### Scenario: SIMPLE-02 The minimal supported input is enough to move

- **WHEN** a member provides the minimal information a section supports
- **THEN** the space advances without configuring scenario variables
- **AND** without building the convergence map by hand first

#### Scenario: SIMPLE-03 Optional detail stays discoverable and collapsible

- **WHEN** a member opens the optional detail of a moment
- **THEN** the detail is reachable on demand
- **AND** collapsing it again loses no information that was typed or recorded

#### Scenario: SIMPLE-04 An existing space keeps its data and its section links

- **WHEN** an existing space is opened after this change
- **THEN** its Decisions, Contributions, provenance and history are unchanged
- **AND** a link to a section route reaches that section with its content

#### Scenario: SIMPLE-05 A refused write stays visible and recoverable

- **WHEN** a write is refused or fails
- **THEN** the failure is visible in the moment where it happened
- **AND** the input stays recoverable
- **AND** nothing reports success

#### Scenario: SIMPLE-06 French, English, mobile and keyboard

- **WHEN** the journey is used in French or English on a phone or on a desktop
- **THEN** every moment label and description is localized
- **AND** the navigation and its section links are usable with the keyboard
