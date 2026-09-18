# ux-flow-auditor Specification

## Purpose
TBD - created by archiving change add-ux-flow-auditor. Update Purpose after archive.

## Requirements

### Requirement: Stable flow identifiers

The auditor SHALL address every audit target with a stable identifier of the
form `FEATURE.FLOW.SCREEN.ACTION[.STATE]`, where each segment uses the project
domain vocabulary (`apps/web/CONTEXT.md`), and SHALL NOT use generic prefixes
such as `PROJ-`.

#### Scenario: Identifier resolves to one screen and action

- **WHEN** an audit record names `Explorer.Filter.Toolbar.ApplyRole`
- **THEN** a reader can locate the exact screen and control without additional
  explanation, using the domain vocabulary and the linked evidence.

### Requirement: AUDITED only with evidence

The auditor SHALL mark a flow AUDITED only when the audit record links at
least one non-empty evidence file (Playwright scenario run, screenshot, or
trace stub) by path, and the coverage gate SHALL fail otherwise.

#### Scenario: Claim without evidence fails the gate

- **WHEN** the coverage registry lists a flow as AUDITED with a missing or
  empty evidence path
- **THEN** `scripts/check_ux_coverage.mjs` exits non-zero naming the offending
  row.

### Requirement: Living Canvas and locale grounding

The auditor SHALL evaluate screens against the semantic tokens in
`packages/ui/src/tokens.css` (never hex literals) and SHALL audit FR and EN
separately using locale message keys, following the existing browser spec
pattern (`apps/web/tests/browser/explorer.spec.ts`).

#### Scenario: Audit references tokens and locale

- **WHEN** an audit reports a color, spacing, radius, or type observation
- **THEN** the observation cites the semantic token name and the locale it was
  observed in.
