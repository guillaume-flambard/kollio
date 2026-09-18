## Purpose

Members browse the ideas their workspace holds through the explorer at `/workspace/ideas`. The surface must be operable with assistive technology: one main landmark, and a search field whose purpose is announced rather than only hinted at.

## ADDED Requirements

### Requirement: The browsing surface is operable with assistive technology (WIB-01)

The browsing surface at `/workspace/ideas` SHALL expose exactly one main landmark, and SHALL give its search field an accessible name in the active locale, distinct from the placeholder that hints at what can be searched.

#### Scenario: A member reaches the explorer with a screen reader

- **WHEN** a member opens `/workspace/ideas`
- **THEN** the page exposes a single main landmark
- **AND** the search field has an accessible name in the active locale

#### Scenario: The search field is named in French

- **WHEN** the explorer renders with French as the active locale
- **THEN** the search field's accessible name is the French label
- **AND** the placeholder keeps hinting at what can be searched

#### Scenario: The search field is named in English

- **WHEN** the explorer renders with English as the active locale
- **THEN** the search field's accessible name is the English label
- **AND** the placeholder keeps hinting at what can be searched
