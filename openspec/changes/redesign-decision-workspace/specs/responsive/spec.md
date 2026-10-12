## ADDED Requirements

### Requirement: The decision workspace hierarchy fits narrow viewports (RS-05)
The Inbox and Decision Space shell SHALL render at 375 and 768 without horizontal overflow. Their current primary action, status, and active product moment SHALL remain reachable without relying on hover or a desktop-only side panel.

#### Scenario: Inbox at phone width
- **WHEN** the Inbox renders at 375px with a primary next action and additional waiting work
- **THEN** there is no horizontal overflow
- **AND** the next action and every populated section remain reachable

#### Scenario: Decision Space at phone and tablet widths
- **WHEN** a Decision Space renders at 375px or 768px
- **THEN** the question, readable status, active product moment, and contextual transition are reachable
- **AND** the six section routes remain reachable without horizontal overflow
