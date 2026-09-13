## Purpose

Defines how workspace members understand an idea, follow its active relationships, and choose the next action without being overwhelmed by secondary information.

## ADDED Requirements

### Requirement: Calm idea library
The system SHALL present the idea library as a three-zone explorer with stable filters, readable idea summaries, and a contextual preview on wide viewports.

#### Scenario: Member scans available ideas
- **WHEN** a workspace member opens the idea library on a wide viewport
- **THEN** filters remain in a narrow rail, enriched results remain visible in the center, and the selected idea appears in a persistent preview

#### Scenario: Member selects and opens an idea
- **WHEN** a workspace member activates an idea row
- **THEN** the preview updates without changing the list position and an explicit preview action opens the complete idea page

#### Scenario: Member uses a narrow viewport
- **WHEN** the filter rail and result list no longer fit side by side
- **THEN** stage filters become an in-flow horizontal control and the preview becomes a drawer on tablet or a full-screen surface on mobile

### Requirement: Focused idea canvas
The system SHALL present the idea narrative as the primary content and SHALL reveal detailed constraints, evidence, and history progressively.

#### Scenario: Member opens an idea
- **WHEN** a workspace member opens an idea they can access
- **THEN** the idea title, stage, narrative, collaborators summary, and primary next action are visible without opening another panel

### Requirement: Contextual relationships
The system SHALL allow a selected passage to reveal its related person, open question, or evidence item without displaying all relationships simultaneously.

#### Scenario: Member selects a linked passage
- **WHEN** a member activates a passage that has a relationship
- **THEN** the related item is selected in the companion panel and the relationship is visually expressed

#### Scenario: Member uses a keyboard
- **WHEN** a member focuses and activates a linked passage using the keyboard
- **THEN** the same related item and contextual actions are available

### Requirement: Distinct active states
The system SHALL identify active navigation, content, and companion-panel state without relying on color alone or generic badge shapes.

#### Scenario: Active state is displayed
- **WHEN** navigation or contextual content becomes active
- **THEN** it has a visible text treatment, a felt-tip wash treatment, and an accessible semantic state

### Requirement: Purposeful motion
The system SHALL use motion to explain selection, relationship, panel changes, and action feedback while preserving correct state when animation is interrupted.

#### Scenario: Motion is enabled
- **WHEN** a member changes the active passage or panel
- **THEN** the selection, relationship, and destination transition in spatial order within 300ms

#### Scenario: Reduced motion is requested
- **WHEN** the member prefers reduced motion
- **THEN** the final interface state appears immediately without drawn-line or spatial movement effects

### Requirement: Responsive companion content
The system SHALL keep team, question, and evidence content accessible when the viewport cannot support a persistent side panel.

#### Scenario: Member uses a narrow viewport
- **WHEN** the companion panel cannot remain beside the idea canvas
- **THEN** its active content is available through an explicit in-flow or overlay control with predictable back navigation

### Requirement: Theme-ready semantic colors
The system SHALL express interface colors through semantic roles so future workspace themes can change color values without changing meaning or reducing required contrast.

#### Scenario: Default theme is used
- **WHEN** no workspace theme is configured
- **THEN** the Aubergine palette supplies the semantic colors

### Requirement: Reproducible development collaborators
The system SHALL provide an explicit development seed that creates stable synthetic user profiles and idea memberships without creating authentication credentials.

#### Scenario: Developer seeds collaboration data
- **WHEN** the seed runs against a non-production environment containing imported Prospecteur ideas
- **THEN** each seeded profile and membership is persisted with a stable identifier and rerunning the seed creates no duplicate records

#### Scenario: Member opens a seeded idea
- **WHEN** a workspace member opens an idea with seeded memberships
- **THEN** the API returns its collaborators and the interface displays their names, roles, and distinguishable avatars

#### Scenario: Seed is attempted in production
- **WHEN** the demo seed detects the production environment
- **THEN** it stops before creating or changing any demo record
