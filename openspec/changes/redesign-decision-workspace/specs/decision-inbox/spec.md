## ADDED Requirements

### Requirement: The Inbox names one next action without hiding waiting work
The Inbox SHALL derive one primary next action from the entries already returned by its four sections. It SHALL show that action before the grouped sections, state why it needs attention, and link to the same Space and section as the underlying entry. The four sections, their bounds, their ordering, and their empty states SHALL remain readable below it.

#### Scenario: The oldest actionable entry becomes the next action
- **WHEN** the Inbox holds at least one entry
- **THEN** it renders one primary next action that points to an existing entry
- **AND** the entry's kind, Space question, detail when present, and destination remain visible or reachable

#### Scenario: A reader still sees work outside the primary action
- **WHEN** the Inbox contains entries in more than one section
- **THEN** every populated section remains visible after the next action
- **AND** the primary action does not remove, merge, or misrepresent the other entries

#### Scenario: The Inbox is empty
- **WHEN** all four Inbox sections are empty
- **THEN** it renders no next-action control
- **AND** it explains that no work currently awaits the reader without treating the state as an error
