# options Specification

## Purpose
Hold the alternatives a Decision Space may choose between, each carrying the fields `docs/00` §7 names and linking its supporting and contradicting evidence to real Contributions, so a trade-off is inspectable rather than summarized.

## Requirements

### Requirement: Space members read the options
The system SHALL expose a Decision Space's options, with their fields and evidence links, only to authenticated members of the owning workspace.

#### Scenario: Member reads an option
- **WHEN** a workspace member requests an option of a Space in their workspace
- **THEN** the system returns its title, proposal, mechanism, upside, cost, risks, critical assumptions and success metrics
- **AND** returns its evidence links with the side and the linked Contribution identifier
- **AND** answers in the request locale

#### Scenario: Non-member requests an option
- **WHEN** an authenticated non-member requests an option of a Space they do not belong to
- **THEN** the system responds as if the workspace were not found
- **AND** discloses no option content

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests an option
- **THEN** the system responds unauthorized without touching persistence

### Requirement: Writers build options
The system SHALL let the Space owner and its participants create, edit and delete options, and SHALL refuse a member who is neither.

#### Scenario: Option created
- **WHEN** a writer creates an option with a title and a proposal
- **THEN** the system persists it under that Space
- **AND** records the language of the write and the author

#### Scenario: Title and proposal required
- **WHEN** a writer submits an option without a title, or with a blank or whitespace-only title or proposal
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Option edited
- **WHEN** a writer updates any of the option's fields
- **THEN** the system persists the change
- **AND** a later read returns the updated values

#### Scenario: Option deleted
- **WHEN** a writer deletes an option
- **THEN** the system removes it and its evidence links
- **AND** a later read reports it as not found

#### Scenario: Uninvolved member cannot write
- **WHEN** a workspace member who is neither the owner nor a participant creates, edits or deletes an option
- **THEN** the system refuses the write
- **AND** leaves the option unchanged

#### Scenario: Non-member cannot write
- **WHEN** a non-member attempts any option write
- **THEN** the system responds as if the collection did not exist
- **AND** stores nothing

### Requirement: Evidence is linked, not asserted
The system SHALL attach evidence to an option only by linking a confirmed Contribution of the same Space, with a declared side.

#### Scenario: Confirmed Contribution linked
- **WHEN** a writer links a confirmed Contribution to an option on the `for` or `against` side
- **THEN** the system records the link and returns it on the option

#### Scenario: Unconfirmed Contribution refused
- **WHEN** a writer links a Contribution that is still `suggested`
- **THEN** the system refuses the request as invalid
- **AND** stores no link

#### Scenario: Contribution from another Space refused
- **WHEN** a writer links a Contribution that belongs to a different Space
- **THEN** the system refuses the request as invalid
- **AND** stores no link

#### Scenario: Unknown side refused
- **WHEN** a writer declares a side other than `for` and `against`
- **THEN** the system refuses the request as invalid
- **AND** stores no link

#### Scenario: Duplicate link refused
- **WHEN** a writer links a Contribution the option already carries
- **THEN** the system refuses the request as invalid
- **AND** keeps exactly one link

#### Scenario: Evidence unlinked
- **WHEN** a writer unlinks a Contribution from an option
- **THEN** the system removes the link
- **AND** leaves the Contribution itself untouched

#### Scenario: Evidence legible from the option
- **WHEN** a member reads an option carrying links on both sides
- **THEN** the system returns each link's side and Contribution identifier
- **AND** distinguishes support from contradiction

### Requirement: Options stay inside their space
The system SHALL scope every option read and write to a single Decision Space and never expose an option through another Space or workspace.

#### Scenario: Two Spaces with similar options
- **WHEN** two Spaces in the same workspace each hold options
- **THEN** a member listing one Space sees only that Space's options
- **AND** cannot read or mutate the other Space's options, even by identifier

#### Scenario: No leak across workspaces
- **WHEN** a member of another workspace requests an option by identifier
- **THEN** the system responds as if the workspace were not found

### Requirement: Trade-offs are inspectable and unscored
The system SHALL expose every option's fields as written and SHALL NOT compute a score, a rank or a universal verdict for an option.

#### Scenario: Every declared field is readable
- **WHEN** an option is created with all of mechanism, upside, cost, risks, critical assumptions and success metrics
- **THEN** a later read returns each one exactly as written

#### Scenario: Fields left out read as absent
- **WHEN** an option is created with only a title and a proposal
- **THEN** the other fields read as absent rather than as invented content

#### Scenario: No score is exposed
- **WHEN** any option is read
- **THEN** the response carries no score, rank or computed verdict
