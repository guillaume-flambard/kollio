## MODIFIED Requirements

### Requirement: Raw Branch material is not the Space's reasoning
The system SHALL present Branch material as material and SHALL send only policy-authorized selected excerpts to an AI workflow without asking ordinary members to choose or confirm a provider.

#### Scenario: Material says what it is
- **WHEN** the screen lists a Branch that holds raw material
- **THEN** that material SHALL be labelled as the Branch's material
- **AND** nothing on the screen SHALL present it as a confirmed Contribution.

#### Scenario: Promotion starts from the Branch
- **WHEN** a participant proposes a Contribution
- **THEN** the proposal SHALL name the Branch it comes from
- **AND** the screen SHALL state which Branch the proposal is for before it is sent.

#### Scenario: A member invokes reconciliation
- **WHEN** a writer invokes the Companion from imported material
- **THEN** the screen SHALL not ask them to choose or confirm a provider
- **AND** the server SHALL apply the approved-provider and excerpt policy before transmission.
