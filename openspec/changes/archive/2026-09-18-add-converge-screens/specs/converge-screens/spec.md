## ADDED Requirements

### Requirement: The map shows the Space's confirmed reasoning

The system SHALL render every confirmed Contribution of the Space inside one Decision Space, with the kind it carries and the group a human placed it in, and SHALL say when a Contribution is not grouped.

#### Scenario: A member reads the map

- **WHEN** a member opens the Converge section of a Space that holds confirmed Contributions
- **THEN** each Contribution is shown with its kind and the group it belongs to
- **AND** a Contribution in no group says it is not grouped

#### Scenario: A Space with nothing to converge says so

- **WHEN** the Space holds no confirmed Contribution
- **THEN** the section says the Space has no shared reasoning yet
- **AND** it offers a way to reach Explore instead of rendering an empty canvas

#### Scenario: The map could not be read

- **WHEN** the map request fails
- **THEN** the section says the map could not be loaded

### Requirement: A member asserts and removes Relations

The system SHALL let a member assert a Relation between two Contributions, choosing one of the eight kinds, SHALL show every Relation with its kind and its two ends, and SHALL let a member remove one. A Relation never links a Contribution to itself.

#### Scenario: A Relation is asserted

- **WHEN** a member picks two Contributions, chooses a kind and submits the relation form
- **THEN** the Relation is sent to the API with its kind and its two ends
- **AND** the listed Relations carry the new one after the map is read again

#### Scenario: A Relation to itself is refused before the request

- **WHEN** a member picks the same Contribution on both ends
- **THEN** the section refuses it in the reader's language
- **AND** no request is sent

#### Scenario: A Relation is removed

- **WHEN** a member removes a listed Relation
- **THEN** the section asks the API to delete it
- **AND** the Relation is gone from the list after the map is read again

#### Scenario: No Relation is an empty state

- **WHEN** the Space's map carries no Relation
- **THEN** the Relations block says there is none rather than showing nothing

### Requirement: A member groups Contributions into Clusters

The system SHALL let a member create a Cluster, add a Contribution to it, remove one, and delete the Cluster. A Contribution SHALL belong to one Cluster at a time.

#### Scenario: A Cluster is created

- **WHEN** a member submits the cluster form with a title
- **THEN** the Cluster is sent to the API and appears in the list after the map is read again

#### Scenario: A Cluster without a title is refused before the request

- **WHEN** a member submits the cluster form with a blank title
- **THEN** the section refuses it in the reader's language
- **AND** no request is sent

#### Scenario: A Contribution is added and then removed

- **WHEN** a member adds a Contribution to a Cluster
- **THEN** the Cluster lists it after the map is read again
- **AND** removing it takes it out of the Cluster while the Contribution stays on the map

#### Scenario: A Cluster is deleted

- **WHEN** a member deletes a Cluster
- **THEN** the Cluster is gone after the map is read again
- **AND** its Contributions stay on the map, ungrouped

### Requirement: The section answers in the reader's languages

The system SHALL write every label, every kind and every message of the Converge section in the reader's locale, leaving the stored vocabulary values unchanged.

#### Scenario: The kinds are written in French

- **WHEN** a French reader opens the Converge section
- **THEN** the eight relation kinds, the five Contribution kinds and the cluster wording are the French catalog values

#### Scenario: The kinds are written in English

- **WHEN** an English reader opens the Converge section
- **THEN** the same labels come from the English catalog

### Requirement: The section never decides for the reader

The system SHALL show what a human asserted and SHALL NOT infer, rank or score anything about an Option, a Contribution or the Space.

#### Scenario: Nothing names a verdict

- **WHEN** a member reads the Converge section
- **THEN** no verdict, ranking, score or prediction appears in what is rendered
- **AND** the only structure shown is the one a human created through the section
