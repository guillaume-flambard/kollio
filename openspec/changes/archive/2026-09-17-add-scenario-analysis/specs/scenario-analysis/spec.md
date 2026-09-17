## Purpose

Hold what a decision turns on — the variables and their ranges, the scenarios and their assumptions — and answer, deterministically, what would change the preference. Intervals and rankings, never a predicted number.

## ADDED Requirements

### Requirement: A Decision Space's scenarios are private to its workspace
The system SHALL expose a space's scenario variables and an option's scenario runs only to authenticated members of the owning workspace.

#### Scenario: Member reads the variables
- **WHEN** a workspace member requests the scenario variables of a space in their workspace
- **THEN** the system returns them with their unit and range
- **AND** answers in the request locale

#### Scenario: Member reads an option's runs
- **WHEN** a member requests the scenario runs of an option in their workspace
- **THEN** the system returns each run with its level, assumptions and declared values

#### Scenario: Non-member requests scenarios
- **WHEN** an authenticated non-member requests any scenario resource
- **THEN** the system responds as if the space were not found
- **AND** discloses no variable, run or value

#### Scenario: Unauthenticated request
- **WHEN** an unauthenticated caller requests a scenario resource
- **THEN** the system responds unauthorized without touching persistence

#### Scenario: Nothing leaks across spaces or workspaces
- **WHEN** two spaces each hold variables and runs
- **THEN** a member of one sees only that space's variables and only that space's options' runs
- **AND** cannot read or mutate the other's even by identifier

### Requirement: Members maintain the variables and their editable ranges
The system SHALL let a space's writers create, edit and delete scenario variables, each with a name, an optional unit and a range.

#### Scenario: Variable created
- **WHEN** a writer creates a variable with a name, a unit and a low, base and high value
- **THEN** the system persists it in the space

#### Scenario: Range must be ordered
- **WHEN** a writer submits a range where low is above base, or base above high
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Blank name refused
- **WHEN** a writer submits an empty or whitespace-only name
- **THEN** the system refuses the request as invalid

#### Scenario: A name is unique inside its space
- **WHEN** a writer creates a second variable with a name already used in that space
- **THEN** the system refuses the request as invalid
- **AND** the two spaces may each define the same name without interfering

#### Scenario: Variable edited and deleted
- **WHEN** a writer updates a variable's unit or range, then deletes it
- **THEN** each change round-trips through the API
- **AND** the deleted variable no longer appears in the list

### Requirement: Members declare scenario runs on an option
The system SHALL let a space's writers create, edit and delete scenario runs on an option, each with a declared level, explicit assumptions and a value per variable.

#### Scenario: Run created
- **WHEN** a writer creates a run with a level and assumptions, and declares values for variables of the space
- **THEN** the system persists the run under that option with those values

#### Scenario: Assumptions are required
- **WHEN** a writer submits a run with empty or whitespace-only assumptions
- **THEN** the system refuses the request as invalid
- **AND** stores nothing

#### Scenario: Unknown level refused
- **WHEN** a writer submits a level outside `optimistic`, `base`, `pessimistic` and `failure`
- **THEN** the system refuses the request as invalid

#### Scenario: One base case per option
- **WHEN** a writer creates a second `base` run on the same option
- **THEN** the system refuses the request as invalid
- **AND** accepts repeated `optimistic`, `pessimistic` or `failure` runs

#### Scenario: A value must belong to the space
- **WHEN** a writer declares a value for a variable that is not in the run's space
- **THEN** the system refuses the request as invalid
- **AND** stores neither the run nor the value

#### Scenario: Declaring the same variable twice is refused
- **WHEN** a writer declares two values for the same variable in one run
- **THEN** the system refuses the request as invalid

#### Scenario: Run edited and deleted
- **WHEN** a writer updates a run's assumptions or its declared values, then deletes the run
- **THEN** each change round-trips
- **AND** the deleted run's values are gone with it

### Requirement: The sensitivity read answers what would change the preference
The system SHALL compute, from an option's declared runs and a caller-supplied criterion, what would change the preference, and SHALL NOT return a predicted single value.

#### Scenario: A criterion flips inside a declared range
- **WHEN** a caller asks with a metric, a direction and a threshold, and one variable's declared points straddle the threshold
- **THEN** the system reports that variable with the interval in which the criterion flips
- **AND** reports the interpolated crossing point
- **AND** marks the interval as found in the declared range

#### Scenario: No declared point straddles the threshold
- **WHEN** no adjacent pair of declared points crosses the threshold
- **THEN** the system reports the variable as beyond its declared range
- **AND** reports the direction the metric travels as that variable grows
- **AND** fabricates no crossing

#### Scenario: Too few points
- **WHEN** a variable has fewer than two runs declaring both it and the metric
- **THEN** the system reports that variable as having insufficient points
- **AND** excludes it from the ranking

#### Scenario: Several crossings are surfaced
- **WHEN** more than one adjacent pair of declared points crosses the threshold
- **THEN** the system reports the narrowest interval and how many pairs crossed
- **AND** does not present it as a single clean threshold

#### Scenario: Runs missing the metric are reported, not averaged
- **WHEN** an option's run declares no value for the criterion's metric
- **THEN** the system reports that run as incomplete
- **AND** excludes it from every computation

#### Scenario: Variables are ranked by implied impact
- **WHEN** the read succeeds
- **THEN** the system ranks the variables by the absolute implied slope across the declared points
- **AND** reports each slope as a range over the adjacent pairs

#### Scenario: Evidence is reported without being attributed to a variable
- **WHEN** the read succeeds
- **THEN** the system reports how many confirmed Contributions the option links as evidence for and against
- **AND** states that evidence is not attributed to any variable

#### Scenario: The response carries no forecast
- **WHEN** any sensitivity read succeeds
- **THEN** the response contains intervals, slopes, rankings and counts
- **AND** contains no field carrying a single predicted outcome value

#### Scenario: No runs yet
- **WHEN** an option has no scenario run
- **THEN** the system answers with an empty ranking rather than an error

### Requirement: Members write, everyone else is refused
The system SHALL allow only the space's owner and participants to write scenario variables, runs and values.

#### Scenario: A participant writes
- **WHEN** a participant creates a variable, a run or a value
- **THEN** the system accepts it

#### Scenario: An uninvolved member cannot write
- **WHEN** a workspace member who is neither the owner nor a participant attempts any write
- **THEN** the system refuses it
- **AND** stores nothing

#### Scenario: A refused write leaves no trace
- **WHEN** any create or update is refused
- **THEN** the system stores nothing and no partial change survives
