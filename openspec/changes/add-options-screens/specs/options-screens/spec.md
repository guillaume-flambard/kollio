# options-screens

## ADDED Requirements

### Requirement: The section lists the Space's Options

The Options section SHALL list the Options the Decision Space holds, each with its title,
its proposal and whether it carries evidence, and SHALL say the list is empty rather than
render a blank page when the Space holds none.

#### Scenario: A Space with no Option

- **WHEN** a member opens the Options section of a Space that holds no Option
- **THEN** the section says there is no Option yet
- **AND** it offers the action that starts one

#### Scenario: The Options of a Space are listed

- **WHEN** a member opens the Options section of a Space that holds two Options
- **THEN** each Option is listed with its title and its proposal
- **AND** each Option says whether it carries evidence

#### Scenario: An Option that carries no evidence says so

- **WHEN** a listed Option has no linked evidence
- **THEN** that Option says it carries no evidence instead of rendering an empty list

#### Scenario: The section could not be read

- **WHEN** the read of the Options fails
- **THEN** the section says it could not be read

### Requirement: A member writes, edits and deletes an Option

The Options section SHALL let a member write an Option from a form, edit it and delete it,
requiring a non-blank title and a non-blank proposal and keeping the six narrative fields
`docs/00` §7 names optional.

#### Scenario: An Option is created with its title and proposal

- **WHEN** a member submits a title and a proposal and leaves the six narrative fields out
- **THEN** the Option is created
- **AND** the new Option is listed with its title and its proposal
- **AND** no narrative field is rendered for it, because an absent field is an absence

#### Scenario: The fields a member does provide are kept

- **WHEN** a member submits an Option with a mechanism and a cost
- **THEN** the Option is listed with those two fields rendered under their labels

#### Scenario: An Option without a title is refused

- **WHEN** a member submits an Option with a blank title
- **THEN** the section says a title is required
- **AND** no Option is created

#### Scenario: An Option without a proposal is refused

- **WHEN** a member submits an Option with a blank proposal
- **THEN** the section says a proposal is required
- **AND** no Option is created

#### Scenario: An Option is edited

- **WHEN** a member edits the mechanism of an Option and saves
- **THEN** the section reads the Option back with the new mechanism

#### Scenario: An Option is deleted

- **WHEN** a member deletes an Option
- **THEN** the Option leaves the list
- **AND** the Space is still readable

### Requirement: Evidence is linked to an Option, not asserted

The Options section SHALL let a member link a confirmed Contribution of the same Space to
an Option on the `for` or the `against` side, SHALL let the member unlink it, and SHALL
offer only confirmed Contributions.

#### Scenario: A confirmed Contribution is linked and read back

- **WHEN** a member links a confirmed Contribution to an Option on the `against` side
- **THEN** the section reads the Option back with that Contribution under the against side

#### Scenario: A linked Contribution is unlinked

- **WHEN** a member unlinks a Contribution from an Option
- **THEN** the section reads the Option back with that Contribution gone from its evidence

#### Scenario: Only confirmed Contributions are offered

- **WHEN** a member opens the linking form of an Option
- **THEN** the Contributions offered are the confirmed ones of the Space
- **AND** a Contribution that is still suggested is not among them

#### Scenario: Nothing to link

- **WHEN** every confirmed Contribution of the Space is already linked to the Option
- **THEN** the linking form says there is no confirmed Contribution to link rather than
  offering an empty choice

### Requirement: The section never scores an Option

The Options section SHALL present Options as paths to compare and SHALL NOT expose a
score, a rank, a rating or a prediction about any Option.

#### Scenario: A member reads the section

- **WHEN** a member reads the Options section of a Space that holds two Options
- **THEN** the section carries no score, no rank, no rating and no prediction
- **AND** no Option is presented as better than another

### Requirement: The section answers in the reader's languages

The Options section SHALL render every label from the locale catalogs, SHALL hold its
keys in both French and English, and SHALL answer in the reader's language.

#### Scenario: A French reader

- **WHEN** a French reader opens the Options section
- **THEN** every control, heading and message is French

#### Scenario: An English reader

- **WHEN** an English reader opens the Options section
- **THEN** the same section behaves identically in English
