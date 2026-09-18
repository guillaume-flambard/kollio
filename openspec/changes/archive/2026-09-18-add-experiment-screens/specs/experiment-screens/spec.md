# experiment-screens

## ADDED Requirements

### Requirement: The section holds the Space's scenario ranges

The section at `/workspace/decision-spaces/[spaceId]/experiment` SHALL list the scenario
variables the Space declares, each with its name, its unit when it has one, and its low, base
and high values. It SHALL let a member add a variable, edit one and delete one.

#### Scenario: The variables of a Space are listed

- **WHEN** a member opens the section of a Space that declares variables
- **THEN** each variable is rendered with its name and its declared range
- **AND** a variable that carries a unit renders it beside its name

#### Scenario: A variable is added

- **WHEN** a member fills the variable form with a name and an ordered range and submits it
- **THEN** the variable is sent to the API with its name, its unit and its three values
- **AND** it is listed once the section refreshes

#### Scenario: A variable is edited

- **WHEN** a member opens a listed variable for editing, changes a value and saves
- **THEN** the update is sent for that variable and the refreshed list shows the new range

#### Scenario: A variable is deleted

- **WHEN** a member deletes a listed variable
- **THEN** the deletion is sent for that variable and it disappears from the refreshed list

#### Scenario: A blank name is refused

- **WHEN** a member submits the variable form without a name
- **THEN** the section states that a name is required and sends nothing

#### Scenario: An unordered range is refused

- **WHEN** a member submits a range whose low, base and high are not ordered, or one of them is
  not a number
- **THEN** the section states that the range must stay ordered and sends nothing

#### Scenario: Nothing declared yet

- **WHEN** a Space declares no variable
- **THEN** the section says so instead of rendering an empty list

### Requirement: A member declares scenario runs on an Option

The section SHALL let a member declare a scenario run on a chosen Option: a level among
`optimistic`, `base`, `pessimistic` and `failure`, the assumptions the point rests on, and one
value per declared variable. It SHALL list the runs of the chosen Option.

#### Scenario: A run is declared

- **WHEN** a member picks an Option, picks a level, states the assumptions and fills the value of
  at least one declared variable
- **THEN** the run is sent for that Option with its level, its assumptions and its values
- **AND** it is listed once the section refreshes

#### Scenario: A run without assumptions is refused

- **WHEN** a member submits the run form without stating the assumptions
- **THEN** the section states that a run states its assumptions and sends nothing

#### Scenario: The runs are read per Option

- **WHEN** a member chooses an Option in the run block
- **THEN** only the runs of that Option are listed
- **AND** each run renders its level, its assumptions and the values it declares

#### Scenario: A run is deleted

- **WHEN** a member deletes a listed run
- **THEN** the deletion is sent for that run and it disappears from the refreshed list

#### Scenario: Nothing declared yet

- **WHEN** the chosen Option carries no run
- **THEN** the section says so instead of rendering an empty list

### Requirement: The sensitivity read describes declared points

For a named result variable, a criterion direction and a threshold, the section SHALL render what
the API reports: the status of every other declared variable, the interval a flip falls in when
one is found, how the result travels over the declared range otherwise, how many flips were
found, the runs that carry no result, and the evidence counts of the Option. It SHALL state that
the read describes declared points and predicts nothing.

#### Scenario: A flip is reported

- **WHEN** the declared runs of an Option straddle the threshold inside a variable's range
- **THEN** that variable is rendered with the flip status and the interval the flip falls in

#### Scenario: No flip inside the declared range

- **WHEN** no declared point changes the side of the criterion
- **THEN** the variable is rendered with the status that says so
- **AND** how the result travels over the range is rendered

#### Scenario: Too few points

- **WHEN** fewer than two declared runs carry both the variable and the result variable
- **THEN** the variable is rendered with the status that says the points are insufficient

#### Scenario: Runs that carry no result are reported

- **WHEN** some runs of the Option do not declare the result variable
- **THEN** the count of those runs is rendered
- **AND** they are not averaged into the read

#### Scenario: The evidence of the Option is reported

- **WHEN** the read is rendered
- **THEN** the number of Contributions linked to the Option for and against is rendered
- **AND** that count is not attributed to any variable

#### Scenario: The reading criterion is chosen by the member

- **WHEN** a member names the result variable, the direction and the threshold
- **THEN** the read is taken for that criterion

#### Scenario: Nothing to read yet

- **WHEN** the chosen Option carries no run
- **THEN** the section says what to declare before a read is possible

### Requirement: A member turns the Space's reasoning into an experiment

The section SHALL let a member create an experiment for the Space: choose the initiative that
carries it, write a title, a hypothesis and a success metric, and add a baseline and an expected
range. It SHALL list the Space's experiments with what was expected set beside what was observed.

#### Scenario: An experiment is created

- **WHEN** a member picks an initiative, writes a title, a hypothesis and a success metric and
  submits the form
- **THEN** the experiment is created for that initiative, linked to the Space and to the chosen
  Option when one was picked
- **AND** it is listed once the section refreshes

#### Scenario: A missing required field is refused

- **WHEN** a member submits the form without an initiative, a title, a hypothesis or a success
  metric
- **THEN** the section states which field it is waiting for and sends nothing

#### Scenario: The expected range is set beside the observed outcome

- **WHEN** an experiment carries an expected range and an outcome has been recorded
- **THEN** the experiment renders what was expected and what was observed in the same block
- **AND** an absent baseline, an absent expected range or an absent outcome is said to be absent

### Requirement: The experiment loop is reachable from the section

The section SHALL offer only the status transitions the API permits from the current status, and
SHALL surface a refusal instead of hiding it. It SHALL render the learning a completion drafts,
read-only.

#### Scenario: A proposed experiment is launched

- **WHEN** a member launches a proposed experiment
- **THEN** the status change is sent with the target status the transition allows
- **AND** the refreshed experiment renders its new status

#### Scenario: A running experiment is completed

- **WHEN** a member completes a running experiment
- **THEN** the status change is sent
- **AND** the draft learning the API composed is rendered read-only
- **AND** the section states that a person confirms it in the Learning section

#### Scenario: A running experiment is abandoned

- **WHEN** a member abandons a running experiment
- **THEN** the status change is sent and the refreshed experiment renders its new status

#### Scenario: Only permitted transitions are offered

- **WHEN** an experiment is completed or abandoned
- **THEN** no further transition is offered for it

#### Scenario: An outcome is recorded

- **WHEN** a member records an outcome with a metric and a value
- **THEN** the outcome is sent for that experiment and rendered once the section refreshes
- **AND** a missing metric or a missing value is refused before anything is sent

#### Scenario: A refusal is shown

- **WHEN** the API refuses a write, for instance because the member does not participate in the
  Space
- **THEN** the section renders the refusal instead of failing silently

### Requirement: The section never forecasts

The section SHALL render no probability, no prediction, no ranking of Options and no score.

#### Scenario: No forecast anywhere in the section

- **WHEN** the section is rendered with variables, runs, a sensitivity read and experiments
- **THEN** no rendered text carries a probability, a prediction or a score

### Requirement: The section answers in the reader's languages

The section SHALL render in the locale of the request, and every value it reads from the API
SHALL stay unchanged by translation.

#### Scenario: A French section

- **WHEN** the section is opened in French
- **THEN** its labels are French and every status, level and side read from the API is rendered
  through the French catalog

#### Scenario: An English section

- **WHEN** the section is opened in English
- **THEN** its labels are English and every status, level and side read from the API is rendered
  through the English catalog

#### Scenario: The section could not be read

- **WHEN** the section's data cannot be loaded
- **THEN** it says so in the reader's language instead of rendering a broken screen
