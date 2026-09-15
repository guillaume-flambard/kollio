## ADDED Requirements

### Requirement: The landing page copy exists in both catalogs

Every `landing.*` key the public landing reads SHALL exist in `apps/web/i18n/locales/fr.json` and
`apps/web/i18n/locales/en.json`, so the rendered page never shows a raw key.

#### Scenario: A visitor loads the landing in French

- **WHEN** a visitor requests the root page with the French locale
- **THEN** the served HTML contains no `landing.` key
- **AND** it renders the French copy for the hero, the navigation, the outcome benefits, the method steps, the preview and the final call to action

#### Scenario: A visitor loads the landing in English

- **WHEN** a visitor requests the root page with the English locale
- **THEN** the served HTML contains no `landing.` key
- **AND** it renders the English copy for the same sections

### Requirement: Every navigation entry resolves to the section it names

Each landing navigation entry SHALL target the identifier of the section whose content it
announces.

#### Scenario: A visitor follows the method entry

- **WHEN** a visitor activates the navigation entry named after the method
- **THEN** the browser reaches the section holding the three ordered steps

#### Scenario: A visitor follows the teams entry

- **WHEN** a visitor activates the navigation entry named after the teams
- **THEN** the browser reaches the section holding the outcome benefits

### Requirement: The locale guard rejects a key that no catalog defines

`scripts/check_locales.mjs` SHALL fail when a key used by `apps/web/app` is absent from the
catalogs, in addition to asserting FR and EN parity.

#### Scenario: A key is used in the web app but missing from both catalogs

- **WHEN** a component calls `t('landing.hero.eyebrow')` and neither catalog defines it
- **THEN** the guard reports the key with the file that uses it
- **AND** the guard exits non-zero

#### Scenario: A dynamic key family exists in the catalogs

- **WHEN** a component builds a key from a template or a concatenation
- **THEN** the guard requires at least one catalog entry to start with the static prefix
- **AND** the guard passes while that family exists

#### Scenario: The catalogs and their usages agree

- **WHEN** every static key used in the web app exists in the catalogs and FR and EN expose the same keys
- **THEN** the guard exits zero
