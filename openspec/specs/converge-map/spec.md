# converge-map Specification

## Purpose
Hold a Decision Space's reasoning map as human-built data — its confirmed Contributions, their explicit relationships and their Clusters — so Converge exists before any AI proposes to it.

## Requirements

### Requirement: Readers see the map
The system SHALL expose one Space's confirmed Contributions with their relations and Clusters to authenticated members of its workspace, and to nobody else.

#### Scenario: Member reads the map
- **WHEN** a workspace member requests a Space's map
- **THEN** the system returns its confirmed Contributions, every relation between them and every Cluster with its member ids
- **AND** answers in the request locale

#### Scenario: Non-member requests the map
- **WHEN** an authenticated non-member requests a Space's map
- **THEN** the system responds as if the Space were not found
- **AND** discloses no Contribution, relation or Cluster

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a map
- **THEN** the system responds unauthorized without touching persistence

#### Scenario: Suggested Contributions stay out
- **WHEN** a Space holds suggested and confirmed Contributions
- **THEN** the map lists only the confirmed ones
- **AND** no relation touches a suggested Contribution

### Requirement: Writers assert relations
The system SHALL let the Space's writers link two confirmed Contributions of that Space with one of the eight declared relation types.

#### Scenario: Relation asserted
- **WHEN** a writer links two confirmed Contributions of the Space with a declared type
- **THEN** the system stores it with its author
- **AND** the map shows it

#### Scenario: Unknown relation type refused
- **WHEN** a writer submits a type outside the closed set
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Self-relation refused
- **WHEN** a writer links a Contribution to itself
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Cross-space pair refused
- **WHEN** a writer links two Contributions that do not both belong to the path's Space
- **THEN** the system responds as if the pair did not exist
- **AND** stores nothing and discloses nothing about the other Space

#### Scenario: Duplicate directed pair refused
- **WHEN** a writer links an ordered pair that already carries a relation
- **THEN** the system refuses the request as invalid
- **AND** keeps the existing relation untouched

#### Scenario: Uninvolved member cannot link
- **WHEN** a workspace member who is neither owner nor participant asserts a relation
- **THEN** the system refuses the request as forbidden
- **AND** stores nothing

### Requirement: Writers remove relations
The system SHALL let the Space's writers delete a relation, leaving both Contributions in place.

#### Scenario: Relation removed
- **WHEN** a writer deletes a relation of the Space
- **THEN** the system removes it
- **AND** the map no longer shows it while both Contributions remain

#### Scenario: Unknown relation removal refused
- **WHEN** a writer deletes a relation id that is not in the path's Space
- **THEN** the system responds as if it did not exist

### Requirement: Writers group Contributions into Clusters
The system SHALL let the Space's writers create titled Clusters, assign Contributions to them, move them between Clusters, unassign them and delete Clusters without deleting Contributions.

#### Scenario: Cluster created
- **WHEN** a writer creates a Cluster with a title
- **THEN** the system stores it empty for that Space

#### Scenario: Blank cluster title refused
- **WHEN** a writer submits an empty or whitespace cluster title
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Contribution assigned and moved
- **WHEN** a writer assigns a same-Space Contribution to a Cluster, then to another
- **THEN** the map shows it in the latest Cluster only

#### Scenario: Contribution unassigned
- **WHEN** a writer removes a Contribution from its Cluster
- **THEN** the map shows it unclustered
- **AND** the Contribution itself is untouched

#### Scenario: Cluster deleted, members kept
- **WHEN** a writer deletes a Cluster
- **THEN** the system removes the Cluster
- **AND** its former members become unclustered while their Contributions remain

#### Scenario: Foreign Contribution refused
- **WHEN** a writer assigns a Contribution that does not belong to the path's Space
- **THEN** the system responds as if it did not exist
- **AND** stores nothing

### Requirement: Spaces do not leak into each other
The system SHALL scope every map read and write to a single Space and never expose one Space's map through another's identifiers.

#### Scenario: Two Spaces with similar maps
- **WHEN** two Spaces each hold Contributions, relations and Clusters
- **THEN** a member of the workspace sees each Space's map only through that Space's identifiers
- **AND** cannot read or mutate one Space's map through the other's, even by identifier
