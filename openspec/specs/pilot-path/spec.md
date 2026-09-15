# pilot-path Specification

## Purpose

Demonstrate the pilot on a seeded Faktus workspace by walking the whole loop through the interface, with every step backed by an executable that already proves it.

## Requirements

### Requirement: The pilot is demonstrated on a seeded Faktus workspace
The pilot SHALL be demonstrated on a seeded Faktus workspace by walking the loop entirely through the interface, and the acceptance checklist SHALL be verified with evidence. Each step below names the interface action and the executable that already proves it.

#### Scenario: A — open the seeded company context
- **WHEN** a member opens the seeded workspace and reads the company context
- **THEN** the profile, objectives, constraints, principles and indicators are present
- **AND** the seed is proven by `test_seed_faktus`, editing by the settings checks

#### Scenario: B — deposit an initiative with a closed type
- **WHEN** a member deposits an initiative with a closed type
- **THEN** the initial iteration lands on the timeline
- **AND** `test_deposit` plus the deposit and initiative-type browser checks prove it

#### Scenario: C — launch an analysis with injected context
- **WHEN** a member launches an analysis
- **THEN** the active company context (objectives, constraints) is injected without any pasting
- **AND** `test_analysis_context` and the reuse fixture prove it

#### Scenario: D — read the verdict
- **WHEN** a member reads the verdict
- **THEN** each factor carries its basis (Known, Assumed, Unknown), unknowns name the missing evidence, and a contradiction block names the objective or constraint it collides with
- **AND** the recorded abstention and contradiction evals plus the explanation browser check DEPOSIT-05 prove it

#### Scenario: E — a second member challenges, the owner decides
- **WHEN** a second member challenges the initiative with a proposal and the owner accepts it
- **THEN** the append-only history keeps both steps
- **AND** `test_iterations` plus the proposal, owner-actions and timeline browser checks prove it

#### Scenario: F — define an experiment
- **WHEN** a member defines an experiment from the initiative with hypothesis, metric, baseline and target
- **THEN** the experiment is created
- **AND** EXPERIMENT-02 proves it

#### Scenario: G — launch it and record real outcomes
- **WHEN** a member launches the experiment and records real outcomes
- **THEN** the outcomes accumulate against it
- **AND** EXPERIMENT-03 and EXPERIMENT-04 prove it

#### Scenario: H — complete it and confirm the drafted learning
- **WHEN** a member completes the experiment and confirms the drafted learning
- **THEN** the learning becomes company memory
- **AND** EXPERIMENT-05, EXPERIMENT-06 and the loop round-trip in `test_the_learning_loop_records_outcomes_and_confirms_a_learning` prove it

#### Scenario: I — reuse the confirmed learning
- **WHEN** a member launches a later analysis
- **THEN** the confirmed learning is reused as evidence, scoped to the workspace
- **AND** `test_confirmed_learnings_are_embedded_and_reused_within_the_workspace` proves it

### Requirement: The demonstration states its boundaries
The pilot SHALL state that interface steps are proven on simulated responses, that authentication, backend authorization and persistence are proven by the named integration tests, and that a live analysis verdict is the operator's demo act whose shape is pinned by the recorded evals and whose quality is tracked by the comparative evals in #77.

#### Scenario: Boundaries are declared
- **WHEN** the pilot acceptance is presented
- **THEN** it declares that interface steps rest on simulated responses
- **AND** it declares that authentication, backend authorization and persistence rest on the named integration tests
- **AND** it declares that a live verdict is the operator's demo act, pinned in shape by the recorded evals and tracked in quality by the comparative evals in #77
