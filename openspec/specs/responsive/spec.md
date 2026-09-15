# responsive Specification

## Purpose

Hold the golden path at the widths a member actually uses, with no horizontal overflow and the primary control reachable.

## Requirements

### Requirement: The initiative detail fits narrow viewports (RS-01)
The initiative detail with its Experiments loop SHALL render at 375 and 768 without horizontal overflow and with the experiment rows reachable.

#### Scenario: Initiative detail at 375 and 768
- **WHEN** the initiative detail is rendered at 375 or 768
- **THEN** there is no horizontal overflow
- **AND** the experiment rows are reachable

### Requirement: The onboarding wizard and enrichment forms fit narrow viewports (RS-02)
The workspace onboarding wizard and its enrichment forms SHALL render at 375 and 768 without horizontal overflow (the phone-width overflow of the two-column create forms is fixed).

#### Scenario: Wizard at 375 and 768
- **WHEN** the workspace onboarding wizard renders at 375 or 768
- **THEN** there is no horizontal overflow

#### Scenario: Enrichment forms at 375 and 768
- **WHEN** a two-column create form renders at 375 or 768
- **THEN** there is no horizontal overflow

### Requirement: The deposit form and narration fit a phone width (RS-03)
The deposit form and its running analysis narration SHALL fit a phone width with no overflow.

#### Scenario: Deposit and narration on a phone
- **WHEN** the deposit form and its running analysis narration render at a phone width
- **THEN** there is no overflow

### Requirement: States survive the responsive guard (RS-04)
Every golden-path screen SHALL keep its empty, loading and error states; the responsive guard SHALL not replace them.

#### Scenario: States preserved
- **WHEN** a golden-path screen renders
- **THEN** its empty, loading and error states remain available
- **AND** the responsive guard did not replace them
