# learning-screens Specification

## Purpose
TBD - created by archiving change add-learning-screens. Update Purpose after archive.

## Requirements

### Requirement: The section lists the Space's lessons with their descent

The `learning` section of a Decision Space SHALL list the lessons the Space holds — those
still waiting for a person and those already confirmed — and SHALL show, for each of them,
the outcome it came from, the experiment that produced it and the initiative it belongs
to. A lesson whose status is `draft` SHALL be told apart from a confirmed one by name, not
by colour alone.

#### Scenario: Nothing confirmed yet

- **WHEN** a member opens the Learning section of a Space that holds no lesson
- **THEN** the section says there is no lesson yet and keeps its heading and intro
- **AND** no group of lessons is rendered

#### Scenario: The lessons of a Space are listed

- **WHEN** a member opens the Learning section of a Space whose experiments produced
  lessons
- **THEN** every lesson is listed with its text and its status told apart in words

#### Scenario: A proposed lesson is told apart from a confirmed one

- **WHEN** the Space holds one proposed lesson and one confirmed lesson
- **THEN** the section renders them in two distinct groups
- **AND** the proposed one offers the actions a proposal needs

#### Scenario: The lessons could not be read

- **WHEN** the lessons of the Space cannot be read
- **THEN** the section says so in an alert role
- **AND** the section's heading and intro are still rendered

### Requirement: A person confirms a proposed lesson

The section SHALL let a member edit a proposed lesson's text and confirm it, and SHALL
show a refusal in the reader's language when the write is rejected. Confirming SHALL NOT be
possible from anywhere else in the section.

#### Scenario: Confirm a lesson

- **WHEN** a member confirms a proposed lesson
- **THEN** the write carries `confirm` as true and the lesson's text
- **AND** the lesson is listed in the confirmed group afterwards

#### Scenario: Edit the text before confirming

- **WHEN** a member rewrites a proposed lesson's text and confirms it
- **THEN** the confirmed lesson carries the rewritten text, not the composed draft

#### Scenario: A refused write is shown

- **WHEN** the write is refused
- **THEN** the section shows the refusal in an alert role
- **AND** the lesson keeps the status it had

### Requirement: A draft without confirmation is kept

The section SHALL let a member save their edit without confirming, and SHALL say that the
lesson stays a kept draft, that nothing is deleted and that only a person confirms a
lesson.

#### Scenario: Save a draft

- **WHEN** a member saves a proposed lesson's text without confirming
- **THEN** the write carries `confirm` as false
- **AND** the lesson is still listed as proposed

#### Scenario: The section says the draft is kept

- **WHEN** a member reads a section that holds a proposed lesson
- **THEN** the section says that an unconfirmed lesson stays as a kept draft and that
  nothing is deleted

### Requirement: The system never confirms a lesson on its own

The section SHALL NOT confirm a lesson, SHALL NOT resolve anything without a person acting,
and SHALL NOT offer a way to delete a lesson.

#### Scenario: Nothing is confirmed without a person

- **WHEN** a member opens the Learning section without acting
- **THEN** no write is sent
- **AND** no lesson changes status

### Requirement: The section never judges the decision

The section SHALL render no score, no ranking and no verdict about the decision, the
Option or the lesson.

#### Scenario: No score, ranking or verdict

- **WHEN** a member reads the Learning section
- **THEN** no element of the section carries a score, a ranking, a rating, a verdict or a
  prediction

### Requirement: The section answers in the reader's languages

Every label, status and message of the section SHALL come from the reader's translation
catalog, so a French reader and an English reader each read the section in their own
language.

#### Scenario: A French section

- **WHEN** a member reads the section in French
- **THEN** every label, status and message is the French one

#### Scenario: An English section

- **WHEN** a member reads the section in English
- **THEN** every label, status and message is the English one
