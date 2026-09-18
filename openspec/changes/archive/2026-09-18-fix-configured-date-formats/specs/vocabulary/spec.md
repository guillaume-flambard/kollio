# vocabulary Specification

## Purpose

Make the golden path speak the product's vocabulary and acknowledge the moment a result becomes company memory. Dates and numbers belong to that vocabulary: a reader sees the format their locale configures, and changing it is one edit rather than nine.

## ADDED Requirements

### Requirement: Visible dates render through the configured locale format (VOC-06)

The web SHALL render a visible date through the date format declared in the i18n configuration, rather than through a formatter built inside the page, and SHALL keep one place for the relative wording and its day arithmetic. A change to the configured format SHALL move every visible date without a page edit.

#### Scenario: A page shows a date

- **WHEN** a page renders a creation, update or deadline date
- **THEN** the date comes from the configured `long` format for the active locale
- **AND** the rendered text is the same long form the page showed before

#### Scenario: The configured format changes

- **WHEN** the `long` date format is edited in `apps/web/i18n/i18n.config.ts`
- **THEN** every page that shows a date follows it without a page edit

#### Scenario: No dead format is declared

- **WHEN** the configuration declares a date or number format
- **THEN** something calls it
- **AND** a format nothing calls is removed rather than kept
