# b2b-product-landing Specification

## Purpose

Present Kollio to private teams in French and English. The public surface also covers what a visitor reads when a path does not exist, which stays in the reader's locale rather than falling back to the framework.

## ADDED Requirements

### Requirement: An unknown path gets a localized not-found screen (BPL-09)

The public surface SHALL answer an unknown path with a screen in the reader's locale: the Kollio brand, the status code, a heading and a description taken from the catalogs, a primary action back to the landing, and the document language set to that locale. It SHALL NOT render a raw translation key, the framework's default error page, or English copy for a French reader.

#### Scenario: A French reader mistypes a path

- **WHEN** a visitor opens a path without a locale prefix that matches no route
- **THEN** the page shows the French heading and description of the not-found screen
- **AND** the document language is French
- **AND** the primary action points at the landing

#### Scenario: An English reader mistypes a path

- **WHEN** a visitor opens an unknown path under `/en`
- **THEN** the page shows the English heading and description of the not-found screen
- **AND** the document language is English

#### Scenario: A server fault uses the same screen

- **WHEN** an error whose status is not 404 reaches the screen
- **THEN** the page shows the generic heading, description and action instead of the not-found words
- **AND** the reader still gets the brand and a way back to the landing
