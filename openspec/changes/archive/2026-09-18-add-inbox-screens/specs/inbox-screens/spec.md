# inbox-screens

## ADDED Requirements

### Requirement: The inbox lists what waits on the reader

The system SHALL render `/workspace` as the Decision Inbox, reading the four sections the API answers: spaces to converge, work waiting on the reader, spaces ready for a decision, and work needing a learning.

#### Scenario: A member reads the inbox

- **WHEN** a member opens `/workspace`
- **THEN** the screen shows the inbox title and its description
- **AND** it shows one section per question the API answers, each with the heading of its own question

#### Scenario: The four sections are filled from the answer

- **WHEN** the API answers entries in each of the four sections
- **THEN** every entry appears under the section its kind belongs to
- **AND** each entry says what waits on the reader

#### Scenario: Nothing waits

- **WHEN** every section is empty
- **THEN** the screen says there is nothing to attend to rather than showing four empty lists
- **AND** it shows no fabricated task

### Requirement: Every entry names what waits and leads where it can be acted on

The system SHALL make every entry name the work that waits and link to the space and the section where that work can be acted on.

#### Scenario: An entry leads to its space and section

- **WHEN** an entry of any kind is listed
- **THEN** its link points to the space of the entry and to the section of that space where the work is done
- **AND** the workspace of the entry travels with the link

#### Scenario: Work waiting on the reader is told apart

- **WHEN** a contribution waits for a confirmation and a finding waits for a resolution
- **THEN** each entry says which of the two it is
- **AND** the detail the API carries, when there is one, is shown

#### Scenario: A bounded section reports what it does not show

- **WHEN** a section holds fewer entries than its total
- **THEN** the screen says how many entries remain beyond the ones shown

### Requirement: A section that is empty says so

The system SHALL say a section is empty when that section holds no entry, instead of leaving it blank.

#### Scenario: An empty section is named as empty

- **WHEN** a section holds no entry
- **THEN** the section still renders its heading and its intro
- **AND** it says that nothing waits in it

### Requirement: The inbox does not answer what it cannot

The system SHALL NOT present a section for relevant prior memory, because the capability that would surface prior confirmed Learnings with their provenance does not exist, and an empty list under that question would assert that no relevant memory exists, which nothing supports.

#### Scenario: The unanswered question is named

- **WHEN** a member reads the inbox
- **THEN** the screen says that relevant prior memory is not answered yet
- **AND** it says why

#### Scenario: No empty memory list

- **WHEN** a member reads the inbox
- **THEN** no list and no empty state is rendered under the memory question

### Requirement: The space list lives at its own route

The system SHALL serve the decision spaces list at `/workspace/decision-spaces`, unchanged, so the inbox can answer alone at `/workspace`.

#### Scenario: The list is reached at its new route

- **WHEN** a member opens `/workspace/decision-spaces`
- **THEN** the list of the workspace's decision spaces is shown
- **AND** it lists and opens each space as it did before

#### Scenario: The inbox points at the list

- **WHEN** a member reads the inbox
- **THEN** a link leads to the decision spaces list

### Requirement: The navigation makes the inbox the home

The system SHALL show four navigation entries: the inbox at `/workspace`, the decision spaces at `/workspace/decision-spaces`, the initiatives, and the settings, each marking whether it is the area being read.

#### Scenario: Four entries, one active

- **WHEN** a member reads the inbox
- **THEN** the inbox entry is marked active
- **AND** the decision spaces entry is not

#### Scenario: The spaces entry is active on the list

- **WHEN** a member reads the decision spaces list
- **THEN** the decision spaces entry is marked active
- **AND** the inbox entry is not

### Requirement: A failed read is shown

The system SHALL keep the frame of the inbox and report a failed read as an alert, instead of leaving the screen silent or blank.

#### Scenario: The inbox could not be read

- **WHEN** the read of the inbox fails
- **THEN** the title and the description stay rendered
- **AND** the failure is shown in an alert

### Requirement: The inbox answers in the reader's languages

The system SHALL render every text of the inbox in the reader's locale, French and English both, with the values the API stores left unchanged.

#### Scenario: A French inbox

- **WHEN** the reader's locale is French
- **THEN** the inbox is written in French

#### Scenario: An English inbox

- **WHEN** the reader's locale is English
- **THEN** the inbox is written in English

### Requirement: The inbox never ranks the work

The system SHALL NOT score, rank, rate or predict anything on this screen; it lists what is provably open.

#### Scenario: No score, no ranking

- **WHEN** a member reads the inbox
- **THEN** no score, ranking or prediction appears anywhere on the screen
