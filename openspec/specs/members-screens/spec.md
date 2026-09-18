# members-screens Specification

## Purpose
TBD - created by archiving change add-members-screens. Update Purpose after archive.

## Requirements

### Requirement: The section lists the workspace's members with their roles

The system SHALL render, inside `/workspace/settings`, a Members section listing every member of the current workspace with the member's display name and role, and SHALL state that the roster could not be read instead of rendering an empty list as if the workspace had no member.

#### Scenario: The members of a workspace are listed

- **WHEN** a member opens `/workspace/settings` for a workspace whose roster holds several people
- **THEN** the section lists each of them with a display name
- **AND** each row states the member's role in words

#### Scenario: A workspace with a single member

- **WHEN** the workspace's roster holds one person
- **THEN** the section lists that person
- **AND** the section does not invent a second row

#### Scenario: The members could not be read

- **WHEN** the roster request fails
- **THEN** the section shows an error with `role="alert"`
- **AND** the section's heading and introduction stay rendered

### Requirement: A member manages the membership of a chosen initiative

Membership in this product belongs to an initiative, and the section SHALL say so: it SHALL let the reader choose which of the workspace's initiatives to manage, and SHALL show that initiative's waiting requests and team, rather than presenting membership as a workspace-level act.

#### Scenario: The section asks which initiative to manage

- **WHEN** a member opens the section for a workspace holding several initiatives
- **THEN** the section offers a way to choose the initiative to manage
- **AND** it reads that initiative's requests and team

#### Scenario: A workspace with no initiative says so

- **WHEN** the workspace holds no initiative
- **THEN** the section says there is no initiative to manage
- **AND** it does not render a chooser with nothing to choose

### Requirement: A waiting join request is visible with who asked

The section SHALL list the join requests of the chosen initiative that still wait for a person, each with the name of the person who asked and the note that person wrote, and SHALL say when nothing is waiting.

#### Scenario: A waiting request is listed

- **WHEN** the chosen initiative carries a request whose status is still waiting
- **THEN** the section lists it with the requester's name
- **AND** the note the requester wrote is readable

#### Scenario: Nothing is waiting

- **WHEN** the chosen initiative carries no waiting request
- **THEN** the section says nothing is waiting
- **AND** a request already resolved is not offered as if it still waited

### Requirement: Accepting a request adds the person to the team

The section SHALL accept a waiting request through the existing operation and SHALL read the initiative back afterwards, so the requester appears in the team without the reader reloading the page.

#### Scenario: A request is accepted

- **WHEN** a member accepts a waiting request
- **THEN** the request leaves the waiting list
- **AND** the person it named appears in the initiative's team
- **AND** the section reflects both without a manual reload

### Requirement: Refusing a request requires a reason

The section SHALL refuse a request only with a reason a person wrote, SHALL refuse a blank reason locally before reaching the API, and SHALL record the reason through the existing operation.

#### Scenario: A refusal without a reason is refused

- **WHEN** a member asks to refuse a request without writing a reason
- **THEN** the section shows a local error with `role="alert"`
- **AND** no refusal request is sent

#### Scenario: A refusal with a reason is recorded

- **WHEN** a member writes a reason and refuses the request
- **THEN** the section sends the refusal carrying that reason
- **AND** the request leaves the waiting list

### Requirement: A member adds a participant and removes one

The section SHALL add a participant to the chosen initiative with a participation and a business function, SHALL remove a member of that initiative's team, and SHALL refuse an add that names nobody locally before reaching the API.

#### Scenario: A participant is added

- **WHEN** a member chooses a workspace member, a participation and a function and submits
- **THEN** the section sends the add with those three values
- **AND** the person appears in the initiative's team
- **AND** the person is no longer offered as a candidate to add

#### Scenario: A member is removed

- **WHEN** a member removes someone from the initiative's team
- **THEN** the section sends the removal for that person
- **AND** the person leaves the team and is offered again as a candidate

#### Scenario: Adding nobody is refused

- **WHEN** a member submits the add form without choosing a workspace member
- **THEN** the section shows a local error with `role="alert"`
- **AND** no add request is sent

### Requirement: The section is refused by the API rather than hidden

The section SHALL render its membership controls for any member of a workspace and SHALL show the refusal the API returns, because the web client knows only the authenticated subject and not the caller's effective rights.

#### Scenario: A refused action is shown

- **WHEN** an action is refused by the API
- **THEN** the section shows an error with `role="alert"`
- **AND** the section keeps its heading and its roster

#### Scenario: The section says what it is not

- **WHEN** a member reads the section
- **THEN** it says that membership is managed per initiative
- **AND** it says that matching between people and initiatives is not surfaced here

### Requirement: The section never ranks people

The section SHALL NOT render a score, a ranking, a rating or a verdict for a person or an initiative.

#### Scenario: No score, ranking or verdict

- **WHEN** a member reads the section
- **THEN** no element carries a score, a ranking, a rating or a verdict

### Requirement: The section answers in the reader's languages

The section SHALL render every label, action and error from the FR and EN catalogues, and SHALL read the same in both.

#### Scenario: A French section

- **WHEN** the reader's locale is French
- **THEN** the section's labels and errors are French

#### Scenario: An English section

- **WHEN** the reader's locale is English
- **THEN** the section's labels and errors are English
- **AND** both locales state the same rules
