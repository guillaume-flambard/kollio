## Purpose

Give the private decision workspace one calm, legible interaction language so members can identify the next human action and read shared reasoning without learning the product's internal model first.

## ADDED Requirements

### Requirement: The connected workspace uses a shared decision language
The connected workspace SHALL use one shared visual language for its page frame, headings, actions, status, reasoning blocks, empty states, and errors. It SHALL use the canonical semantic tokens and SHALL reserve relationship treatment for the active section, selected reasoning, or a visible relationship between two records.

#### Scenario: Two workspace routes share the same primitives
- **WHEN** a member opens the Inbox and then a Decision Space
- **THEN** their page hierarchy, primary action, status, feedback, and focus treatment are recognisably the same system
- **AND** the relationship treatment does not decorate unrelated controls

#### Scenario: A keyboard reader encounters a shared control
- **WHEN** a member reaches an interactive control by keyboard
- **THEN** the control has visible focus and a target of at least 44px
- **AND** its meaning is not conveyed by colour or texture alone

### Requirement: The workspace makes the current human action primary
Each connected workspace screen SHALL state its purpose and present at most one primary action for the member's current decision context. Secondary or destructive actions SHALL remain available without competing with the primary action.

#### Scenario: A member opens a screen with actionable work
- **WHEN** the Inbox or a Decision Space has work the member can perform
- **THEN** the screen names the next action in the reader's language
- **AND** offers one visually primary control that leads to or performs that action

#### Scenario: A member opens an empty screen
- **WHEN** the Inbox or a Decision Space section has no actionable work
- **THEN** the screen explains the empty state in the reader's language
- **AND** does not render a decorative primary action with no valid outcome

### Requirement: The workspace is evidenced across locales and widths
The connected workspace SHALL retain its hierarchy, action reachability, and readable states in French and English at desktop and phone widths. The implementation SHALL record browser evidence for those reference states.

#### Scenario: A French member uses the phone layout
- **WHEN** a French member opens the Inbox or a Decision Space at 375px
- **THEN** there is no horizontal overflow
- **AND** the current primary action and the active section remain reachable and readable

#### Scenario: An English member uses the desktop layout
- **WHEN** an English member opens the same reference route at desktop width
- **THEN** all interface labels are English
- **AND** the visual hierarchy and next action match the French route's behaviour
