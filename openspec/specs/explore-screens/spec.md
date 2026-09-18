# explore-screens Specification

## Purpose
TBD - created by archiving change add-explore-screens. Update Purpose after archive.

## Requirements

### Requirement: A participant works in their own Branch

The system SHALL let a writer of a Decision Space create a Branch inside it, carrying a name and the raw material that Branch explores, and SHALL list the Branches the participant may read.

#### Scenario: A Branch is created and read back

- **WHEN** a writer creates a Branch with a name, some raw material and a visibility
- **THEN** the Space lists that Branch with its name, its material, who created it and when

#### Scenario: A Branch without a name is refused

- **WHEN** a writer submits a Branch with a blank name
- **THEN** the screen refuses it, says a Branch needs a name, and no Branch is created

#### Scenario: A Branch whose visibility is not private or shared is refused

- **WHEN** a writer submits a Branch whose visibility is neither private nor shared
- **THEN** the screen refuses it and no Branch is created

#### Scenario: Branches arrive in the order they were explored

- **WHEN** a Space holds several Branches
- **THEN** the screen lists them oldest first, each with its own raw material

### Requirement: A Branch states whether it is private or shared

The system SHALL state each Branch's visibility in words on the screen, and SHALL NOT show a Branch to anyone who may not read it.

#### Scenario: Visibility is stated per Branch

- **WHEN** a Space holds a private Branch and a shared Branch
- **THEN** the screen names each one's visibility, in the reader's language, on the Branch itself

#### Scenario: A private Branch is not listed for another participant

- **WHEN** a Space holds a Branch whose creator is someone else and whose visibility is private
- **THEN** that Branch is not listed for this participant, and their own private Branch still is

### Requirement: Raw Branch material is not the Space's reasoning

The system SHALL present Branch material as material, never as the Space's reasoning, and SHALL make the promotion step explicit: material only joins the shared reasoning by being proposed as a Contribution and confirmed by a human.

#### Scenario: Material says what it is

- **WHEN** the screen lists a Branch that holds raw material
- **THEN** that material is labelled as the Branch's material, and nothing on the screen presents it as a confirmed Contribution

#### Scenario: Promotion starts from the Branch

- **WHEN** a participant proposes a Contribution
- **THEN** the proposal names the Branch it comes from, and the screen states which Branch the proposal is for before it is sent

### Requirement: A Contribution is proposed from a Branch and waits or is confirmed

The system SHALL let a writer propose a Contribution from a readable Branch, with a known kind, a title, and optional body, source and tool or model, and SHALL show what is confirmed apart from what still waits for a human.

#### Scenario: A proposal is recorded from its Branch

- **WHEN** a writer proposes a Contribution from a Branch with a kind and a title
- **THEN** the Contribution is listed for the Space, tied to that Branch

#### Scenario: A proposal without a title is refused

- **WHEN** a writer submits a proposal with a blank title
- **THEN** the screen refuses it, says a proposal needs a title, and no Contribution is created

#### Scenario: A proposal with an unknown kind is refused

- **WHEN** a writer submits a proposal whose kind is outside the known kinds
- **THEN** the screen refuses it and no Contribution is created

#### Scenario: The two states are listed apart

- **WHEN** the Space holds a Contribution awaiting a human and a confirmed Contribution
- **THEN** the screen lists the awaiting one under what waits for a human and the confirmed one under what is confirmed

#### Scenario: Nothing waits for a human yet

- **WHEN** every Contribution of the Space is confirmed
- **THEN** the awaiting list says it is empty instead of disappearing or showing an error

#### Scenario: A human confirms what waited

- **WHEN** a participant confirms a Contribution that was awaiting a human
- **THEN** it moves to the confirmed list and the screen no longer offers to confirm it

### Requirement: Every Contribution shows its provenance

The system SHALL show every Contribution's provenance: its author, its Branch, its source, its tool or model, and when it was added, stating an absence rather than leaving a blank or inventing a value.

#### Scenario: Provenance is complete for a Contribution that carries everything

- **WHEN** the screen lists a Contribution proposed with a source and a tool or model
- **THEN** it shows the author, the Branch, the source, the tool or model and the date it was added

#### Scenario: An absent source or tool is said to be absent

- **WHEN** the screen lists a Contribution proposed without a source and without a tool or model
- **THEN** the source and the tool or model are each stated as absent rather than left blank

#### Scenario: The absence is in the reader's language

- **WHEN** the same Contribution is read in each locale
- **THEN** every provenance label and the stated absence are in that locale while the stored values themselves are unchanged
