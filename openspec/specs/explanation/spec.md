# explanation Specification

## Purpose

Make the verdict inspectable: each factor shows its basis, contradictions name what they collide with, and the engine's prose is shown in the language it was requested in.

## Requirements

### Requirement: Each factor shows its basis
Each factor in the verdict SHALL show its basis. An unknown factor SHALL show, in its place of score, the missing evidence the engine named.

#### Scenario: Unknown factor shows the gap
- **WHEN** the verdict carries an unknown factor
- **THEN** the factor shows, where the score would be, the missing evidence the engine named

#### Scenario: Scored factor shows its basis
- **WHEN** the verdict carries a known or assumed factor
- **THEN** the factor shows its basis next to its score

### Requirement: Contradictions are listed with a translated label
When the analysis contradicts a stated objective or constraint, the panel SHALL list each entry with a translated target label and the engine's prose.

#### Scenario: Contradiction rendered
- **WHEN** the analysis reports a contradiction
- **THEN** the panel lists it with a translated target label and the engine's prose

### Requirement: Labels are localized, engine prose is shown as returned
All labels SHALL come from the translation catalogs; the engine's prose SHALL be shown as returned, in the locale the analysis was requested in.

#### Scenario: French analysis
- **WHEN** the analysis was requested in French
- **THEN** the labels are French
- **AND** the engine's prose is shown as returned

#### Scenario: English analysis
- **WHEN** the analysis was requested in English
- **THEN** the labels are English
- **AND** the engine's prose is shown as returned
