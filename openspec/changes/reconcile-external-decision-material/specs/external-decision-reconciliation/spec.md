## Purpose

Preserve external decision material and reconcile competing proposals without losing who said what, in which version, or why a person chose one direction over another.

## ADDED Requirements

### Requirement: Members import immutable source material
The system SHALL let a Space writer manually import text material with a title, body, stated author, origin label, original language, and visibility. It SHALL preserve every imported revision and SHALL never overwrite its body.

#### Scenario: A member imports a ChatGPT-derived note
- **WHEN** a Space writer imports a non-blank note with its stated author and origin label
- **THEN** the Space lists the material with its provenance and first revision
- **AND** a later read returns its original body unchanged

#### Scenario: A later revision is added
- **WHEN** a writer adds a revision to imported material
- **THEN** the new revision is listed after the original
- **AND** the original revision remains readable

#### Scenario: A non-member imports material
- **WHEN** a non-member imports or reads material for a Space
- **THEN** the system responds as if the Space were not found
- **AND** stores and discloses nothing

### Requirement: Source excerpts remain addressable
The system SHALL let a Space writer select a non-empty excerpt from one source revision and promote it to a Contribution while retaining the source revision and exact excerpt. Raw material SHALL not be presented as shared reasoning until that promotion is confirmed.

#### Scenario: A source excerpt becomes shared reasoning
- **WHEN** a writer promotes an excerpt with a known Contribution kind
- **THEN** the Contribution retains its source revision and excerpt
- **AND** the Space can read the Contribution separately from raw material

#### Scenario: A member reads an imported claim
- **WHEN** a member opens a source-backed Contribution
- **THEN** the member can reach its cited source revision and excerpt
- **AND** the source author and origin label remain visible

### Requirement: A reconciliation preserves disagreement
The system SHALL let Space writers compare selected source-backed Contributions and record each as combined, retained, rejected, or open with a human rationale. Reconciliation SHALL not alter any source revision or automatically change a Contribution's confirmation state.

#### Scenario: Diverging material is reconciled
- **WHEN** a writer compares Jean-Pierre's and Corinne's source-backed Contributions and records one as retained and one as rejected
- **THEN** both Contributions remain readable with their source lineage
- **AND** the recorded resolutions and rationale are visible

#### Scenario: A disagreement stays open
- **WHEN** a writer records a comparison as open
- **THEN** neither source is presented as the team's settled position

### Requirement: The Companion proposes a cited reconciliation only
The Companion SHALL produce a reconciliation proposal only from selected source excerpts and confirmed Contributions. Each proposed statement SHALL cite one or more supplied sources, and no Companion output SHALL alter source material, Contributions, resolutions, or a Decision Record without a human action.

#### Scenario: The Companion proposes a grounded brief
- **WHEN** a writer asks the Companion to reconcile selected material
- **THEN** every proposed statement cites supplied material or a confirmed Contribution
- **AND** the proposal is visibly distinguished from a human resolution

#### Scenario: A source cannot support the proposal
- **WHEN** the Companion cannot ground a proposed statement in supplied material
- **THEN** it omits the statement or states the uncertainty
- **AND** it does not invent a citation
