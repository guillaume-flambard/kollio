## ADDED Requirements

### Requirement: The public page addresses private teams

The landing page SHALL describe Kollio as a private workspace where a team evaluates ideas and documents decisions.

#### Scenario: A visitor reads the first viewport

- **WHEN** an unauthenticated visitor opens the localized home page
- **THEN** the page presents a team-oriented value proposition
- **AND** it exposes a primary action to create or enter a workspace
- **AND** it communicates privacy, permissions, and analysis traceability

### Requirement: The product workflow is understandable without interaction

The landing page SHALL present the initiative workflow in Signal, Validation, and Decision order.

#### Scenario: The preview is rendered

- **WHEN** the product preview is visible
- **THEN** its three stages use semantic headings
- **AND** evidence, an open question, ownership, and the documented decision remain associated through text and grouping

### Requirement: The visual relationship language is reusable and anchored

The landing page SHALL render relationship connectors, hand-drawn annotation arrows, and felt-tip emphasis through dedicated visual components.

#### Scenario: The desktop workflow is rendered

- **WHEN** the product preview displays its horizontal three-stage layout
- **THEN** each relationship connector starts and ends at explicit card anchor coordinates
- **AND** connector endpoints remain visually attached to the related cards
- **AND** active text uses the shared felt-tip mark instead of a page-specific pseudo-element

#### Scenario: The viewport is narrow

- **WHEN** the workflow changes to its sequential layout
- **THEN** relationship connectors and annotation arrows are hidden
- **AND** the semantic order and labels preserve the relationship meaning

### Requirement: The landing remains usable across input and display preferences

The landing page SHALL preserve content and actions across supported breakpoints and reduced-motion preferences.

#### Scenario: The viewport is narrow

- **WHEN** the viewport cannot display the horizontal workflow
- **THEN** the stages stack in their original order
- **AND** decorative connectors are hidden
- **AND** the page does not require horizontal scrolling

### Requirement: Outcome benefits use Kollio-owned artwork

The landing page SHALL use original Kollio artwork for the shared context, explainable decisions, and controlled AI outcomes.

#### Scenario: Outcome benefits are rendered

- **WHEN** a visitor reaches the outcome benefits below the product workflow
- **THEN** each benefit displays its dedicated Kollio-owned SVG illustration
- **AND** no generic icon substitutes for the illustration
- **AND** decorative artwork is hidden from assistive technology because the adjacent heading and description carry its meaning

### Requirement: Narrative landing sections share one artwork system

The landing page SHALL use the same reusable Kollio artwork component for outcome benefits, the decision-memory method, and team alignment.

#### Scenario: A visitor continues below the product workflow

- **WHEN** the visitor reaches the method and final call-to-action sections
- **THEN** each section uses dedicated Kollio-owned SVG artwork
- **AND** the artwork preserves its native aspect ratio
- **AND** it does not replace or duplicate the section's semantic text
